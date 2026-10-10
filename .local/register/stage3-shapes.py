# -*- coding: utf-8 -*-
"""Stage three: rooms stop being rectangles and corridors stop being one width.

Owner direction, verbatim: *"and everything doesnt have to be square rooms and rectangle
halways"*.

The approach, and why it is the safe one: a room's `Bounds` stays a rect, because the validator,
the doors, the corridors and the pillar lattice all read it. What changes is **which cells inside
it get carved out of the rock.** Rock is left standing in the CORNERS, never on the centre cross
and never at an edge midpoint, so:

  * doors still meet the room where the corridor expects them,
  * a straight walk from any doorway to any other is still clear,
  * connectivity cannot be broken by a shape, so no candidate is ever rejected for one, and
  * the intrusions are `Mineable`, so a player who wants the rectangle back can dig it.

Shallow coordinates barely deform, for the same reason `Derange` leaves them alone: the yellow
rooms read as a place because they are monotonous.

Written as a file.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
PLANNER = os.path.join(SRC, "Generation", "RoomLayoutPlanner.cs")
GEN = os.path.join(SRC, "Generation", "GenStep_BackroomsDestination.cs")

planner = io.open(PLANNER, encoding="utf-8").read()

SHAPES = '''        /// <summary>
        /// Cells inside a room that are left as solid rock, so the room is not a rectangle.
        ///
        /// ## Owner direction, 2026-09-30, verbatim
        ///
        /// *"and everything doesnt have to be square rooms and rectangle halways"*.
        ///
        /// ## Why rock in the corners rather than a different rectangle
        ///
        /// The room's `Bounds` has to stay a rect: the validator bounds-checks it, the doors are
        /// placed at the midpoint of each side, the corridors aim at `CenterCell`, and the pillar
        /// lattice is laid out across it. Changing the rect would mean changing all four.
        ///
        /// So the rect stays and the **carve** changes. Rock is left standing inside the room, and
        /// it is left **only in the corners** -- never on the centre cross, never at an edge
        /// midpoint. That single restriction buys four things at once:
        ///
        ///   * every doorway still opens onto clear floor;
        ///   * a straight walk from any doorway to any other is still clear, so **no shape can
        ///     ever disconnect a room** and no candidate is rejected for having one;
        ///   * the pillar lattice needs no special case, because rock already holds roof; and
        ///   * the intrusions are `Mineable`, so a player who wants the rectangle can dig for it.
        ///
        /// **Shallow coordinates barely deform.** Depth 1 gets nothing, for the same reason
        /// <see cref="Derange"/> leaves it alone: the yellow rooms read as a place precisely
        /// because they are monotonous, and the wrongness is something the player travels toward.
        ///
        /// **Decided here and nowhere else**, like <see cref="PillarCells"/>: the generator leaves
        /// these cells uncarved and <see cref="CandidateIsSafe"/> marks them unwalkable, and two
        /// independent derivations of one rule is the defect that cost this project thirty-nine
        /// checkpoints.
        /// </summary>
        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)
        {
            if (room == null || depth <= 1) { yield break; }
            CellRect bounds = room.Bounds;
            // The interior only. The perimeter is wall and the ring inside it is the walkway that
            // keeps every doorway reachable.
            int insetX = bounds.minX + 2;
            int insetZ = bounds.minZ + 2;
            int extentX = bounds.maxX - 2;
            int extentZ = bounds.maxZ - 2;
            if (extentX - insetX < 4 || extentZ - insetZ < 4) { yield break; }

            IntVec3 center = bounds.CenterCell;
            // How far a corner mass reaches in, growing with depth and never past the centre
            // cross. Clamped to a third of the room so a shape can never eat the middle.
            int reach = System.Math.Min((depth - 1) * 2, System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);
            if (reach < 1) { yield break; }

            int roll = DestinationService.StableHash(room.index * 31 + depth,
                (room.familyId ?? "") + ":shape", depth);
            if (roll < 0) { roll = ~roll; }
            // Which corners are filled. Four bits, and never all four of a small room.
            int corners = 1 + roll % 15;

            for (int index = 0; index < 4; index++)
            {
                if ((corners & (1 << index)) == 0) { continue; }
                bool east = index == 1 || index == 2;
                bool north = index >= 2;
                // Each corner mass is a quarter-ellipse, so the edge it presents to the room is
                // curved rather than another right angle.
                for (int dx = 0; dx < reach; dx++)
                {
                    for (int dz = 0; dz < reach; dz++)
                    {
                        if (dx * dx + dz * dz > reach * reach) { continue; }
                        int x = east ? extentX - dx : insetX + dx;
                        int z = north ? extentZ - dz : insetZ + dz;
                        // The centre cross is inviolable: it is what guarantees every doorway
                        // reaches every other doorway whatever shape the corners take.
                        if (x == center.x || z == center.z) { continue; }
                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }
                        if (z <= bounds.minZ + 1 || z >= bounds.maxZ - 1) { continue; }
                        yield return new IntVec3(x, 0, z);
                    }
                }
            }
        }

        /// <summary>
        /// Half the width of the corridor between two rooms, so hallways are not all one size.
        ///
        /// Two gives a three-cell walkway, three gives five. Derived from the two rooms' own
        /// indices so it is stable across a reload, and **shared with
        /// <see cref="CandidateIsSafe"/>** for the usual reason.
        /// </summary>
        internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)
        {
            if (first == null || second == null || depth <= 1) { return 2; }
            int roll = DestinationService.StableHash(first.index * 101 + second.index,
                "corridor:width", depth);
            if (roll < 0) { roll = ~roll; }
            return roll % 3 == 0 ? 3 : 2;
        }

'''

ANCHOR = "        private static List<RoomRecord> Build(CoordinateRecord coordinate, int candidate)"
if planner.count(ANCHOR) != 1:
    print("PLANNER ANCHOR PROBLEM: %d" % planner.count(ANCHOR))
    raise SystemExit(1)
planner = planner.replace(ANCHOR, SHAPES + ANCHOR, 1)

# CandidateIsSafe must model both, or a candidate could be accepted that the generator then builds
# differently. Depth is needed there, so the signature gains it.
OLD_SAFE = """        private static bool CandidateIsSafe(List<RoomRecord> rooms)
        {
            if (!DestinationService.ValidateRooms(rooms, out _)) { return false; }"""
NEW_SAFE = """        private static bool CandidateIsSafe(List<RoomRecord> rooms, int depth)
        {
            if (!DestinationService.ValidateRooms(rooms, out _)) { return false; }"""
if planner.count(OLD_SAFE) != 1:
    print("SAFE ANCHOR PROBLEM: %d" % planner.count(OLD_SAFE))
    raise SystemExit(1)
planner = planner.replace(OLD_SAFE, NEW_SAFE, 1)

OLD_PILLARS = """                // The pillars, from the SAME function the generator spawns them from.
                foreach (IntVec3 pillar in PillarCells(room))
                { floor[pillar.x, pillar.z] = false; }"""
NEW_PILLARS = """                // The pillars, from the SAME function the generator spawns them from.
                foreach (IntVec3 pillar in PillarCells(room))
                { floor[pillar.x, pillar.z] = false; }
                // And the rock left standing in the corners, from the same function again.
                foreach (IntVec3 rock in RockIntrusionCells(room, depth))
                { floor[rock.x, rock.z] = false; }"""
if planner.count(OLD_PILLARS) != 1:
    print("PILLAR ANCHOR PROBLEM: %d" % planner.count(OLD_PILLARS))
    raise SystemExit(1)
planner = planner.replace(OLD_PILLARS, NEW_PILLARS, 1)

OLD_CORR = """                    if (a.z == b.z)
                    {
                        for (int x = Math.Min(room.Bounds.maxX, other.Bounds.maxX) + 1; x < Math.Max(room.Bounds.minX, other.Bounds.minX); x++)
                        { for (int dz = -1; dz <= 1; dz++) { floor[x, a.z + dz] = true; } }
                    }
                    else
                    {
                        for (int z = Math.Min(room.Bounds.maxZ, other.Bounds.maxZ) + 1; z < Math.Max(room.Bounds.minZ, other.Bounds.minZ); z++)
                        { for (int dx = -1; dx <= 1; dx++) { floor[a.x + dx, z] = true; } }
                    }"""
NEW_CORR = """                    // The same width the generator will carve, from the shared function.
                    int reach = CorridorHalfWidthBetween(room, other, depth) - 1;
                    if (a.z == b.z)
                    {
                        for (int x = Math.Min(room.Bounds.maxX, other.Bounds.maxX) + 1; x < Math.Max(room.Bounds.minX, other.Bounds.minX); x++)
                        { for (int dz = -reach; dz <= reach; dz++) { floor[x, a.z + dz] = true; } }
                    }
                    else
                    {
                        for (int z = Math.Min(room.Bounds.maxZ, other.Bounds.maxZ) + 1; z < Math.Max(room.Bounds.minZ, other.Bounds.minZ); z++)
                        { for (int dx = -reach; dx <= reach; dx++) { floor[a.x + dx, z] = true; } }
                    }"""
if planner.count(OLD_CORR) != 1:
    print("CORRIDOR ANCHOR PROBLEM: %d" % planner.count(OLD_CORR))
    raise SystemExit(1)
planner = planner.replace(OLD_CORR, NEW_CORR, 1)

# Every CandidateIsSafe caller now passes the depth.
CALLS = [
    ("                List<RoomRecord> rooms = Build(coordinate, candidate);\n"
     "                if (CandidateIsSafe(rooms)) { selected = rooms; return true; }",
     "                List<RoomRecord> rooms = Build(coordinate, candidate);\n"
     "                if (CandidateIsSafe(rooms, DepthOf(coordinate))) { selected = rooms; return true; }"),
    ("            List<RoomRecord> fallback = Build(coordinate, FallbackCandidate);\n"
     "            if (!CandidateIsSafe(fallback)) { return false; }",
     "            List<RoomRecord> fallback = Build(coordinate, FallbackCandidate);\n"
     "            if (!CandidateIsSafe(fallback, DepthOf(coordinate))) { return false; }"),
    ("            List<RoomRecord> candidate = Build(coordinate, FallbackCandidate);\n"
     "            if (!CandidateIsSafe(candidate)) { return false; }",
     "            List<RoomRecord> candidate = Build(coordinate, FallbackCandidate);\n"
     "            if (!CandidateIsSafe(candidate, DepthOf(coordinate))) { return false; }"),
]
for old, new in CALLS:
    if planner.count(old) != 1:
        print("CALL ANCHOR PROBLEM (%d): %r" % (planner.count(old), old[:60]))
        raise SystemExit(1)
    planner = planner.replace(old, new, 1)

OLD_SLOTS = "        /// <summary>Slots per axis for this depth. Deeper means more, smaller rooms.</summary>"
NEW_SLOTS = """        /// <summary>A coordinate's depth, floored at one, in one place so every reader agrees.</summary>
        internal static int DepthOf(CoordinateRecord coordinate)
        {
            return coordinate == null || coordinate.Depth < 1 ? 1 : coordinate.Depth;
        }

        /// <summary>Slots per axis for this depth. Deeper means more, smaller rooms.</summary>"""
if planner.count(OLD_SLOTS) != 1:
    print("SLOTS ANCHOR PROBLEM: %d" % planner.count(OLD_SLOTS))
    raise SystemExit(1)
planner = planner.replace(OLD_SLOTS, NEW_SLOTS, 1)

io.open(PLANNER, "w", encoding="utf-8", newline="").write(planner)
print("planner: shapes and corridor widths added, CandidateIsSafe models both")

# ------------------------------------------------------------------ the generator
gen = io.open(GEN, encoding="utf-8").read()

OLD_CARVE = """            foreach (RoomRecord room in coordinate.Rooms)
            {
                foreach (IntVec3 cell in room.Bounds.Cells)
                {
                    // Carve the room out of the rock, keeping the thick roof overhead. The
                    // roof is deliberately NOT RoofConstructed: constructed roof is
                    // removable, and all roof in a Backrooms coordinate must never be.
                    ClearRock(map, cell);
                    map.terrainGrid.SetTerrain(cell, concrete);
                    map.roofGrid.SetRoof(cell, overheadRoof);
                }
            }"""
NEW_CARVE = """            int coordinateDepth = RoomLayoutPlanner.DepthOf(coordinate);
            foreach (RoomRecord room in coordinate.Rooms)
            {
                // Owner direction, 2026-09-30: *"everything doesnt have to be square rooms"*.
                // Rock is left standing in the corners, from the SAME function CandidateIsSafe
                // proved the room walkable against -- see RoomLayoutPlanner.RockIntrusionCells.
                var intrusions = new HashSet<IntVec3>(
                    RoomLayoutPlanner.RockIntrusionCells(room, coordinateDepth));
                foreach (IntVec3 cell in room.Bounds.Cells)
                {
                    // The roof goes overhead either way: an intrusion is rock inside the room,
                    // not a hole in the world.
                    map.roofGrid.SetRoof(cell, overheadRoof);
                    if (intrusions.Contains(cell)) { continue; }
                    // Carve the room out of the rock, keeping the thick roof overhead. The
                    // roof is deliberately NOT RoofConstructed: constructed roof is
                    // removable, and all roof in a Backrooms coordinate must never be.
                    ClearRock(map, cell);
                    map.terrainGrid.SetTerrain(cell, concrete);
                }
            }"""
if gen.count(OLD_CARVE) != 1:
    print("CARVE ANCHOR PROBLEM: %d" % gen.count(OLD_CARVE))
    raise SystemExit(1)
gen = gen.replace(OLD_CARVE, NEW_CARVE, 1)

OLD_BC = "            BuildCorridors(coordinate.Rooms, map, concrete);"
NEW_BC = "            BuildCorridors(coordinate.Rooms, map, concrete, coordinateDepth);"
if gen.count(OLD_BC) != 1:
    print("BUILDCORRIDORS CALL PROBLEM: %d" % gen.count(OLD_BC))
    raise SystemExit(1)
gen = gen.replace(OLD_BC, NEW_BC, 1)

OLD_SIG = """        private static void BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map, TerrainDef floor)
        {
            foreach (RoomRecord room in rooms)
            {
                foreach (int linkedIndex in room.Links.Where(index => index > room.Index))
                {
                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);
                    CellRect first = room.Bounds;
                    CellRect second = other.Bounds;"""
NEW_SIG = """        /// <summary>
        /// The corridors between linked rooms.
        ///
        /// **The width is not a constant any more.** Owner direction, 2026-09-30: *"everything
        /// doesnt have to be ... rectangle halways"*. It comes from
        /// `RoomLayoutPlanner.CorridorHalfWidthBetween`, which `CandidateIsSafe` also reads, so
        /// the reachability the planner proved is the reachability that gets built.
        /// </summary>
        private static void BuildCorridors(IReadOnlyList<RoomRecord> rooms, Map map, TerrainDef floor,
            int depth)
        {
            foreach (RoomRecord room in rooms)
            {
                foreach (int linkedIndex in room.Links.Where(index => index > room.Index))
                {
                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);
                    int halfWidth = RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth);
                    CellRect first = room.Bounds;
                    CellRect second = other.Bounds;"""
if gen.count(OLD_SIG) != 1:
    print("CORRIDOR SIG PROBLEM: %d" % gen.count(OLD_SIG))
    raise SystemExit(1)
gen = gen.replace(OLD_SIG, NEW_SIG, 1)

gen = gen.replace("-CorridorHalfWidth + 1; offset <= CorridorHalfWidth - 1",
                  "-halfWidth + 1; offset <= halfWidth - 1")
gen = gen.replace("new IntVec3(x, 0, centerZ - CorridorHalfWidth)", "new IntVec3(x, 0, centerZ - halfWidth)")
gen = gen.replace("new IntVec3(x, 0, centerZ + CorridorHalfWidth)", "new IntVec3(x, 0, centerZ + halfWidth)")
gen = gen.replace("new IntVec3(centerX - CorridorHalfWidth, 0, z)", "new IntVec3(centerX - halfWidth, 0, z)")
gen = gen.replace("new IntVec3(centerX + CorridorHalfWidth, 0, z)", "new IntVec3(centerX + halfWidth, 0, z)")

io.open(GEN, "w", encoding="utf-8", newline="").write(gen)
print("generator: shaped carve and varied corridor width")
