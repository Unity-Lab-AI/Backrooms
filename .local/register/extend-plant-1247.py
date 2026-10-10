# -*- coding: utf-8 -*-
"""Retarget the stale terrain plant and add the 0.12.47-dev plants.

Written as a file, not a heredoc, per the rule in docs/NOW.md -- bash mangled `\\n` and
apostrophes in five separate scripts during the 0.12.46-dev batch.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

text = io.open(PLANT, encoding="utf-8").read()

# ---------------------------------------------------------------------------- retarget
# The terrain step no longer loops room rects setting terrain, so the old anchor is gone.
STALE = '''    ("THE TERRAIN STEP FLATTENS THE WHOLE MAP AGAIN", GEN,
     "            foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))" + CHR_NL + "            {" + CHR_NL + "                foreach (IntVec3 cell in rect.Cells)",
     "            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }" + CHR_NL
     + "            foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))" + CHR_NL + "            {" + CHR_NL
     + "                foreach (IntVec3 cell in rect.Cells)",
     PROOF),'''

FRESH = '''    ("THE TERRAIN STEP FLATTENS THE WHOLE MAP AGAIN", GEN,
     "            MapGenFloatGrid elevation = MapGenerator.Elevation;",
     "            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }" + CHR_NL
     + "            MapGenFloatGrid elevation = MapGenerator.Elevation;",
     PROOF),'''

# ---------------------------------------------------------------------------- new plants
TAIL_ANCHOR = '''    ("a layout grows past the smallest map RimWorld offers", STARTS,'''

NEW = '''    # ------------------------------------------------- 0.12.47-dev: burn into place
    ("THE TERRAIN STEP RUNS BEFORE THE ELEVATION GRID EXISTS AGAIN", SCENARIOS,
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>100</order>",
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>5</order>", PROOF),

    ("the terrain step runs after Core has already spawned the rock", SCENARIOS,
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>100</order>",
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>300</order>", PROOF),

    ("THE SITE ELEVATION RISES BACK ABOVE CORE'S ROCK THRESHOLD", GEN,
     "private const float BuildableElevation = 0.55f;",
     "private const float BuildableElevation = 0.95f;", PROOF),

    ("the elevation is read but never lowered", GEN,
     "if (elevation[cell] > BuildableElevation) { elevation[cell] = BuildableElevation; }",
     "if (elevation[cell] > BuildableElevation) { }", PROOF),

    ("THE BURN IS DEFINED BUT NEVER CALLED", GEN,
     "            BurnIntoPlace(start, map, offset);" + CHR_NL, "", PROOF),

    ("THE BURN RUNS AFTER THE WALLS ARE ALREADY UP", GEN,
     "            BurnIntoPlace(start, map, offset);" + CHR_NL
     + "            foreach (RimroomsRoomPlan room in start.rooms)" + CHR_NL + "            {" + CHR_NL
     + "                CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));",
     "            foreach (RimroomsRoomPlan room in start.rooms)" + CHR_NL + "            {" + CHR_NL
     + "                BurnIntoPlace(start, map, offset);" + CHR_NL
     + "                CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));", PROOF),

    ("the burn stops carving anything out", GEN,
     "                    thing.Destroy(DestroyMode.Vanish);", "                    continue;", PROOF),

    ("the burn stops copying the cell's thing list before mutating it", GEN,
     "new List<Thing>(cell.GetThingList(map))", "cell.GetThingList(map)", PROOF),

    ("THE NATURAL ROCK ROOF IS LEFT HANGING OVER THE FACILITY", GEN,
     "                if (roof != null && roof.isNatural) { map.roofGrid.SetRoof(cell, null); }",
     "                if (roof != null) { }", PROOF),

    ("WATER IS NO LONGER FILLED IN WITH SOIL", GEN,
     "if (terrain.IsWater || terrain.passability == Traversability.Impassable)",
     "if (false)", PROOF),

    ("impassable terrain stops being filled", GEN,
     "terrain.passability == Traversability.Impassable", "terrain.IsWater", PROOF),

    ("THE BURN STARTS KILLING LIVING THINGS", GEN,
     "if (thing.def.category == ThingCategory.Pawn || !thing.def.destroyable) { continue; }",
     "if (!thing.def.destroyable) { continue; }", PROOF),

    ("another mod's structure is cleared silently", GEN,
     "if (thing.def.category == ThingCategory.Building && thing.Faction != null)",
     "if (false)", PROOF),

    ("THE WALL REFUSES GROUND CORE GENERATED AGAIN", GEN,
     "                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);",
     "                        if (cell.GetEdifice(map) != null) { throw new InvalidOperationException("
     + "\\"Headquarters wall intersects generated structure at \\" + cell); }" + CHR_NL
     + "                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);", PROOF),

    ("A FAILED FACILITY RE-THROWS INSTEAD OF HANDING THE SPOT BACK", GEN,
     "                MapGenerator.PlayerStartSpot = IntVec3.Invalid;",
     "                MapGenerator.PlayerStartSpot = IntVec3.Invalid;" + CHR_NL + "                throw;", PROOF),

    ("a failed facility leaves the player standing inside a building that does not exist", GEN,
     "                MapGenerator.PlayerStartSpot = IntVec3.Invalid;", "", PROOF),

    # ------------------------------------------------- 0.12.47-dev: the colonists survive us
    ("THE ARRIVAL THROWS OUT OF CORE'S SCENARIO STEP AGAIN", ARRIVAL,
     '                Log.Error("[Rimrooms][Scenario] Headquarters receipt incomplete at arrival; " +',
     '                throw new InvalidOperationException("[Rimrooms] Native arrival requires the '
     'prepared headquarters receipt.");' + CHR_NL
     + '                Log.Error("[Rimrooms][Scenario] Headquarters receipt incomplete at arrival; " +', PROOF),

    ("AN INCOMPLETE RECEIPT STOPS DELIVERING CORE'S OWN ARRIVAL", ARRIVAL,
     "                try { base.GenerateIntoMap(map); }", "                try { }", PROOF),

    ("the incomplete-receipt branch disappears", ARRIVAL,
     "            if (receipt == null || receipt.receiptVersion != 2 || !receipt.setupComplete)",
     "            if (false)", PROOF),

    ("the fallback stops recording that stock was granted once", ARRIVAL,
     "                    receipt.arrivalStarted = true;" + CHR_NL, "", PROOF),

    ("the fallback stops guarding against a second grant", ARRIVAL,
     "                    if (receipt.arrivalStarted) { return; }" + CHR_NL, "", PROOF),

'''

NAMES_ANCHOR = 'PROOF = ".local/register/proof-startplacement.py"'
NAMES_NEW = ('SCENARIOS = "Mod/Rimrooms - Async Industries/1.6/Defs/ScenarioDefs/RR_Scenarios.xml"\n'
             'ARRIVAL = SCEN + "/ScenPart_RimroomsArrival.cs"\n'
             'PROOF = ".local/register/proof-startplacement.py"')

problems = []
for anchor in (STALE, TAIL_ANCHOR, NAMES_ANCHOR):
    if text.count(anchor) != 1:
        problems.append("%d occurrence(s) of %r" % (text.count(anchor), anchor[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(NAMES_ANCHOR, NAMES_NEW, 1)
text = text.replace(STALE, FRESH, 1)
text = text.replace(TAIL_ANCHOR, NEW + TAIL_ANCHOR, 1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(text)
print("plant suite retargeted and extended")
