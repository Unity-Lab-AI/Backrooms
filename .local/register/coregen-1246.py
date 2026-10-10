# -*- coding: utf-8 -*-
"""The map generator is not ours. Core generates the tile; we place the facility onto it.

Owner direction, 2026-09-30, verbatim: **"the map generator is not our mod"**, after reporting
*"its not the tilemap i chose the land features are all barren to just bare dirt not even
vegitation"*, using **Map Preview** (`m00nl1ght.MapPreview`, installed) to view and reroll tiles
before selecting.

## What was wrong

`ScenPart_RimroomsStart` did `Find.GameInitData.mapGeneratorDef = startDef.mapGenerator`, which
replaced Core's `Base_Player` with our `RR_Headquarters`. Core's player generator inherits
`MapCommonBase` and runs the whole chain -- elevation, fertility, biome terrain, caves, rocks
from grid, plants, animals, ruins, rivers, roads, plus the DLC steps. **Ours had four steps:** our
terrain pass, our facility, `ScenParts`, `Fog`.

So the map was flat `Soil` with a building on it. No rock, no plants, no water, no biome character
at all -- *"bare dirt not even vegitation"*, exactly. And **Map Preview simulates the real
generator**, so the preview a player rerolled against was a picture of a map the mod then threw
away. The preview was right and the game was wrong.

## What this changes

1. **The override is gone.** Core generates the map for the chosen tile at the chosen size.
2. **Our two gen steps are added to `Base_Player`** by an additive patch, so the facility is built
   onto the real map instead of instead of it.
3. **The steps return quietly when it is not the initial company start.** They currently *throw*,
   and a step that throws inside `Base_Player` would break **every** later colony map -- a
   second settlement, a quest site, anything. This is the load-bearing half of the change.
4. **The terrain step stops overwriting the whole map.** It only floors the facility footprint
   now; the rest of the tile is whatever Core generated, which is the entire point.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario")
PART = os.path.join(SCEN, "ScenPart_RimroomsStart.cs")
GEN = os.path.join(SCEN, "GenStep_Headquarters.cs")

PART_EDITS = [
    (u"            Find.GameInitData.mapGeneratorDef = startDef.mapGenerator;",
     u"""            // **The map generator is not ours.** Owner direction, 2026-09-30, after
            // reporting bare dirt and no vegetation on a tile chosen with Map Preview.
            //
            // This line used to read:
            //     Find.GameInitData.mapGeneratorDef = startDef.mapGenerator;
            // and it replaced Core's `Base_Player` -- elevation, fertility, biome terrain,
            // caves, rocks, plants, animals, ruins, rivers, roads and the DLC steps -- with a
            // four-step generator of ours. The result was flat Soil with a building on it, and
            // **Map Preview simulates the real generator**, so the preview a player rerolled
            // against was a picture of a map this mod then discarded.
            //
            // Core generates the tile now, at the size the player picked, and the facility is
            // added onto it by two gen steps patched into `Base_Player`."""),
]

GEN_EDITS = [
    # ------------------------------------------------------------------ a quiet guard
    (u"""        internal static RimroomsStartDef RequireStart(Map map)
        {
            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;
            if (part == null || part.startDef == null || Find.GameInitData == null ||
                map.Tile != Find.GameInitData.startingTile ||
                // The map no longer has to BE the authored size -- it has to be able to hold the
                // layout. The player picks the size at world setup and the tile they arrive on,
                // and the facility is generated onto that map.
                !HeadquartersLayout.Fits(part.startDef, map.Size) ||
                Current.Game.GetComponent<RimroomsCampaignComponent>().HasBranch)
            { throw new InvalidOperationException("[Rimrooms] Headquarters generator used outside the initial company start."); }
            return part.startDef;
        }""",
     u"""        /// <summary>
        /// The start this map belongs to, or **null** when this map is not the initial company
        /// start.
        ///
        /// **Null rather than a throw, and that is the load-bearing detail of 0.12.46-dev.**
        /// These gen steps now live in Core's `Base_Player`, which runs for **every** player map
        /// a game ever generates -- a second settlement, a quest site, a reloaded world. A step
        /// that threw there would break all of them. It used to throw because it only ever ran
        /// inside a generator this mod owned and nothing else could reach it.
        /// </summary>
        internal static RimroomsStartDef StartForMap(Map map)
        {
            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;
            if (part == null || part.startDef == null || Find.GameInitData == null) { return null; }
            if (map.Tile != Find.GameInitData.startingTile) { return null; }
            if (Current.Game.GetComponent<RimroomsCampaignComponent>().HasBranch) { return null; }
            // The map does not have to BE the authored size -- it has to be able to hold the
            // layout. The player picks the size at world setup and the tile they arrive on.
            if (!HeadquartersLayout.Fits(part.startDef, map.Size)) { return null; }
            return part.startDef;
        }"""),

    # ------------------------------------------------------------------ terrain step
    (u"""            RimroomsStartDef start = HeadquartersBuilder.RequireStart(map);
            // The layout is authored in its own coordinates and offset onto whatever map the
            // player chose; see HeadquartersLayout. Before 0.12.45-dev the mod forced its own
            // map size instead, which is why a 50x50 site read as a cage.
            IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);
            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }
            MapGenerator.PlayerStartSpot = start.arrivalCell + offset;""",
     u"""            RimroomsStartDef start = HeadquartersBuilder.StartForMap(map);
            if (start == null) { return; }
            // The layout is authored in its own coordinates and offset onto whatever map the
            // player chose; see HeadquartersLayout.
            IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);
            // **The rest of the tile is left exactly as Core generated it.** This used to be
            //     foreach (IntVec3 cell in map.AllCells) SetTerrain(cell, start.outdoorTerrain);
            // which flattened the entire map to one terrain -- the *"bare dirt not even
            // vegitation"* the owner reported. Only the footprint is prepared, and the room
            // loop in HeadquartersBuilder floors the interiors.
            foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))
            {
                foreach (IntVec3 cell in rect.Cells)
                {
                    if (cell.InBounds(map))
                    { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }
                }
            }
            MapGenerator.PlayerStartSpot = start.arrivalCell + offset;"""),

    # ------------------------------------------------------------------ facility step
    (u"""            RimroomsStartDef start = HeadquartersBuilder.RequireStart(map);
            HeadquartersSetupComponent receipt = map.GetComponent<HeadquartersSetupComponent>();
            if (receipt.setupStarted) { return; }""",
     u"""            RimroomsStartDef start = HeadquartersBuilder.StartForMap(map);
            if (start == null) { return; }
            HeadquartersSetupComponent receipt = map.GetComponent<HeadquartersSetupComponent>();
            if (receipt == null || receipt.setupStarted) { return; }"""),
]


def patch(path, edits, label):
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%d of %r" % (text.count(old), old[:64]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM in %s: %s" % (label, problem))
        raise SystemExit(1)
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("  %s: %d edit(s)" % (label, len(edits)))


patch(PART, PART_EDITS, "ScenPart_RimroomsStart.cs")
patch(GEN, GEN_EDITS, "GenStep_Headquarters.cs")
print("Core generates the tile; the facility is placed onto it")
