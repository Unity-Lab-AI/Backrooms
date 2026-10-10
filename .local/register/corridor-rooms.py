# -*- coding: utf-8 -*-
"""A hallway is a room. Owner: *"rooms as halways with the exact shit thats in the rooms"*.

Two hardcoded values made every corridor in every coordinate a grey steel service tunnel between
themed rooms, which is exactly *"the hall ways are just rectangles and arnt correctly the themed
color and materials"* and most of why the floor read as *"a string of pears"*:

  * the floor was the raw carve terrain -- `concrete`, the thing rock becomes when you clear it --
    while `PaintRoom` gave every room the band's palette floor with accent stripes;
  * the walls were `PlaceWall(..., ThingDefOf.Wall, ThingDefOf.Steel)`. **Literally steel**, while
    rooms draw their walls from the coordinate's own materials and tint them with the band colour.

So a corridor is painted by the same palette call `PaintRoom` uses, walled in the same stuff the
rooms are walled in, tinted the same colour, lit like a room, and dressed with the same fixtures
the rooms carry.

**The centre line is never touched.** A corridor is the route between two rooms, so furniture goes
only against its walls, and only in a corridor wide enough to have a side -- the same discipline as
the reserved route cross inside a room.

`docs/UNIVERSE_ADAPTATION.md` already said this: a coordinate is *"made of rooms and routes"* and
the instruction is to *"reuse recognizable room categories, materials, fluorescent lighting,
service infrastructure, and furniture as the baseline"*. A route with none of those is not part of
the same building.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

# ---------------------------------------------------------------- the call site
CALL_OLD = u"""            BuildCorridors(coordinate.Rooms, map, concrete, coordinateDepth);"""
CALL_NEW = u"""            // **A HALLWAY IS A ROOM.** Owner: *"rooms as halways with the exact shit thats
            // in the rooms"*. The palette and the wall material go in with the carve, so a
            // corridor is part of the same building rather than a service tunnel between rooms.
            List<IntVec3> corridorSides = BuildCorridors(coordinate.Rooms, map, coordinate,
                wallDef, wallStuff, coordinateDepth);"""

# ------------------------------------------------------------- the method itself
SIG_OLD = u"""        private static void BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map, TerrainDef floor,
            int depth)
        {
            foreach (RoomRecord room in rooms)"""
SIG_NEW = u"""        /// <summary>
        /// Carve the routes between rooms, **as rooms**, and report the cells along their walls
        /// that can hold something.
        ///
        /// Owner: *"the hall ways are just rectangles and arnt correctly the themed color and
        /// materials"*, and *"i see the whole map is almost like a string of pears. when it
        /// should just be basicly \\"rooms\\" as halways with the exact shit thats in the rooms"*.
        ///
        /// **Two hardcoded values were the whole of it.** The floor was the raw carve terrain --
        /// `concrete`, what rock becomes when you clear it -- while every room got the band's
        /// palette floor with accent stripes from `PaintRoom`. And the walls were
        /// `ThingDefOf.Steel`, literally, while a room's walls come from the coordinate's own
        /// materials and carry the band's colour. So a themed yellow room opened onto a grey
        /// steel tunnel, on every link, at every depth.
        ///
        /// The palette comes from `BackroomsPalette.SetFloor`, which is the same call `PaintRoom`
        /// makes, so a corridor cannot drift from the rooms it joins.
        ///
        /// Returns the cells one in from each corridor wall, for the lamps and the dressing. The
        /// **centre line is never included**: a corridor is a route, and the same reasoning that
        /// reserves a room's route cross applies to the whole of a corridor's length.
        /// </summary>
        private static List<IntVec3> BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map,
            CoordinateRecord coordinate, ThingDef wallDef, ThingDef wallStuff, int depth)
        {
            var sides = new List<IntVec3>();
            BackroomsPalette.Look look = BackroomsPalette.For(depth,
                DestinationService.StableHash(coordinate.Seed, coordinate.Id + ":corridors", 1));
            foreach (RoomRecord room in rooms)"""

BODY_OLD = u"""                        for (int x = fromX; x <= toX; x++)
                        {
                            for (int offset = -halfWidth + 1; offset <= halfWidth - 1; offset++)
                            {
                                SetWalkableRoofedCell(map, new IntVec3(x, 0, centerZ + offset), floor);
                            }
                            PlaceWall(map, new IntVec3(x, 0, centerZ - halfWidth), ThingDefOf.Wall, ThingDefOf.Steel);
                            PlaceWall(map, new IntVec3(x, 0, centerZ + halfWidth), ThingDefOf.Wall, ThingDefOf.Steel);
                        }"""
BODY_NEW = u"""                        for (int x = fromX; x <= toX; x++)
                        {
                            for (int offset = -halfWidth + 1; offset <= halfWidth - 1; offset++)
                            {
                                IntVec3 cell = new IntVec3(x, 0, centerZ + offset);
                                SetWalkableRoofedCell(map, cell, look.floor);
                                PaintCorridorCell(map, cell, look, x);
                                // One in from the wall, and never the centre line.
                                if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))
                                { sides.Add(cell); }
                            }
                            PlaceCorridorWall(map, new IntVec3(x, 0, centerZ - halfWidth), wallDef, wallStuff, look);
                            PlaceCorridorWall(map, new IntVec3(x, 0, centerZ + halfWidth), wallDef, wallStuff, look);
                        }"""

BODY2_OLD = u"""                        for (int z = fromZ; z <= toZ; z++)
                        {
                            for (int offset = -halfWidth + 1; offset <= halfWidth - 1; offset++)
                            {
                                SetWalkableRoofedCell(map, new IntVec3(centerX + offset, 0, z), floor);
                            }
                            PlaceWall(map, new IntVec3(centerX - halfWidth, 0, z), ThingDefOf.Wall, ThingDefOf.Steel);
                            PlaceWall(map, new IntVec3(centerX + halfWidth, 0, z), ThingDefOf.Wall, ThingDefOf.Steel);
                        }"""
BODY2_NEW = u"""                        for (int z = fromZ; z <= toZ; z++)
                        {
                            for (int offset = -halfWidth + 1; offset <= halfWidth - 1; offset++)
                            {
                                IntVec3 cell = new IntVec3(centerX + offset, 0, z);
                                SetWalkableRoofedCell(map, cell, look.floor);
                                PaintCorridorCell(map, cell, look, z);
                                if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))
                                { sides.Add(cell); }
                            }
                            PlaceCorridorWall(map, new IntVec3(centerX - halfWidth, 0, z), wallDef, wallStuff, look);
                            PlaceCorridorWall(map, new IntVec3(centerX + halfWidth, 0, z), wallDef, wallStuff, look);
                        }"""

TAIL_OLD = u"""                    else
                    {
                        throw new InvalidOperationException("RR_Generation_NonAdjacentRooms");
                    }
                }
            }
        }"""
TAIL_NEW = u"""                    else
                    {
                        throw new InvalidOperationException("RR_Generation_NonAdjacentRooms");
                    }
                }
            }
            return sides;
        }

        /// <summary>
        /// A corridor cell takes the band's floor, with the same accent stripe a room gets.
        ///
        /// `BackroomsPalette.SetFloor` is the call `PaintRoom` makes, so a corridor and the rooms
        /// it joins cannot read as different buildings -- which is what *"arnt correctly the
        /// themed color and materials"* was describing.
        /// </summary>
        private static void PaintCorridorCell(Map map, IntVec3 cell, BackroomsPalette.Look look,
            int along)
        {
            if (look.floor == null) { return; }
            TerrainDef terrain = look.accent != null && along % 4 == 0 ? look.accent : look.floor;
            BackroomsPalette.SetFloor(map, cell, terrain, look.floorColor);
        }

        /// <summary>
        /// A corridor wall is the coordinate's wall in the coordinate's material, in the band's
        /// colour.
        ///
        /// It was `ThingDefOf.Steel`, hardcoded, on every corridor of every coordinate at every
        /// depth -- so the owner's *"every type of wall and material for all things randomly"*
        /// was honoured for rooms and contradicted one cell outside them.
        /// </summary>
        private static void PlaceCorridorWall(Map map, IntVec3 cell, ThingDef wallDef,
            ThingDef wallStuff, BackroomsPalette.Look look)
        {
            PlaceWall(map, cell, wallDef, wallStuff);
            Thing wall = cell.InBounds(map) ? cell.GetEdifice(map) : null;
            if (wall != null && wall.def == wallDef)
            { wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor); }
        }"""

EDITS = [
    (CALL_OLD, CALL_NEW),
    (SIG_OLD, SIG_NEW),
    (BODY_OLD, BODY_NEW),
    (BODY2_OLD, BODY2_NEW),
    (TAIL_OLD, TAIL_NEW),
]

text = io.open(GEN, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(GEN, "w", encoding="utf-8", newline="").write(text)
print("corridors are rooms: palette floor, coordinate walls, band colour, side cells reported")
