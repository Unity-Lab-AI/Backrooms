# -*- coding: utf-8 -*-
"""Honour the player's chosen map size, and offset the layout onto it.

Owner, 2026-09-30: *"the map size is selected on world seteup before world generation by the
player and they select the tile they appear in so the store gets genreeate in that selected
tiles map"*.

Every consumer of an authored cell has to apply the same offset or the facility tears apart.
The complete list, which is why this is one scripted change rather than several edits:

    ScenPart_RimroomsStart   stop forcing GameInitData.mapSize
    RequireStart             stop requiring an exact size; require the layout FITS
    GenStep_...Terrain       PlayerStartSpot, rootsToUnfog, UsedRects
    HeadquartersBuilder      rooms, doors, buildings, conduits, arrival, stock
    RimroomsStartDef         ConfigErrors no longer bounds mapSize as the map
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario")

GEN = os.path.join(SCEN, "GenStep_Headquarters.cs")
PART = os.path.join(SCEN, "ScenPart_RimroomsStart.cs")

GEN_EDITS = [
    # ---------------------------------------------------------------- the terrain step
    (u"""            RimroomsStartDef start = HeadquartersBuilder.RequireStart(map);
            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }
            MapGenerator.PlayerStartSpot = start.arrivalCell;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell);
            foreach (RimroomsRoomPlan room in start.rooms)
            { MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects").Add(room.Rect); }""",
     u"""            RimroomsStartDef start = HeadquartersBuilder.RequireStart(map);
            // The layout is authored in its own coordinates and offset onto whatever map the
            // player chose; see HeadquartersLayout. Before 0.12.45-dev the mod forced its own
            // map size instead, which is why a 50x50 site read as a cage.
            IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);
            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }
            MapGenerator.PlayerStartSpot = start.arrivalCell + offset;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell + offset);
            foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))
            { MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects").Add(rect); }"""),

    # ---------------------------------------------------------------- the guard
    (u"""                map.Size.x != part.startDef.mapSize || map.Size.z != part.startDef.mapSize ||
                map.Tile != Find.GameInitData.startingTile ||""",
     u"""                map.Tile != Find.GameInitData.startingTile ||
                // The map no longer has to BE the authored size -- it has to be able to hold the
                // layout. The player picks the size at world setup and the tile they arrive on,
                // and the facility is generated onto that map.
                !HeadquartersLayout.Fits(part.startDef, map.Size) ||"""),

    # ---------------------------------------------------------------- the builder
    (u"""            if (!start.arrivalCell.InBounds(map) || !start.stockCell.InBounds(map))
            { throw new InvalidOperationException("Headquarters arrival or receiving position is outside the map."); }
            foreach (RimroomsRoomPlan room in start.rooms)
            {
                CellRect rect = room.Rect;""",
     u"""            IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);
            if (!(start.arrivalCell + offset).InBounds(map) || !(start.stockCell + offset).InBounds(map))
            { throw new InvalidOperationException("Headquarters arrival or receiving position is outside the map."); }
            foreach (RimroomsRoomPlan room in start.rooms)
            {
                CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));"""),

    (u"""            foreach (IntVec3 cell in start.doors)
            {
                Building wall = cell.GetEdifice(map);""",
     u"""            foreach (IntVec3 authored in start.doors)
            {
                IntVec3 cell = authored + offset;
                Building wall = cell.GetEdifice(map);"""),

    (u"""                Rot4 rotation = new Rot4(plan.rotation);
                foreach (IntVec3 cell in GenAdj.OccupiedRect(plan.cell, rotation, plan.thing.size).Cells)""",
     u"""                Rot4 rotation = new Rot4(plan.rotation);
                IntVec3 where = plan.cell + offset;
                foreach (IntVec3 cell in GenAdj.OccupiedRect(where, rotation, plan.thing.size).Cells)"""),

    (u"""                GenSpawn.Spawn(building, plan.cell, map, rotation);""",
     u"""                GenSpawn.Spawn(building, where, map, rotation);"""),

    (u"""                    IntVec3 cell = line.start + new IntVec3(line.alongX ? offset : 0, 0, line.alongX ? 0 : offset);""",
     u"""                    IntVec3 cell = line.start + offset
                        + new IntVec3(line.alongX ? step : 0, 0, line.alongX ? 0 : step);"""),

    (u"""                for (int offset = 0; offset < line.length; offset++)""",
     u"""                for (int step = 0; step < line.length; step++)"""),

    (u"""            if (!start.arrivalCell.Standable(map))
            { throw new InvalidOperationException("Headquarters arrival position is not walkable."); }
            MapGenerator.PlayerStartSpot = start.arrivalCell;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell);
            foreach (IntVec3 door in start.doors) { MapGenerator.rootsToUnfog.Add(door); }""",
     u"""            if (!(start.arrivalCell + offset).Standable(map))
            { throw new InvalidOperationException("Headquarters arrival position is not walkable."); }
            MapGenerator.PlayerStartSpot = start.arrivalCell + offset;
            MapGenerator.rootsToUnfog.Add(start.arrivalCell + offset);
            foreach (IntVec3 door in start.doors) { MapGenerator.rootsToUnfog.Add(door + offset); }"""),
]

PART_EDITS = [
    (u"            Find.GameInitData.mapSize = startDef.mapSize;",
     u"""            // The map size is the PLAYER'S choice, made at world setup, and the tile they
            // pick is where this facility is generated. Forcing it here is what produced the
            // owner's 2026-09-30 report: *"not the map i chose ... a super micro blocked in
            // area"*. The layout is offset onto their map instead; see HeadquartersLayout."""),
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


patch(GEN, GEN_EDITS, "GenStep_Headquarters.cs")
patch(PART, PART_EDITS, "ScenPart_RimroomsStart.cs")
print("map size is the player's choice; layout offsets onto it")
