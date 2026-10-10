"""Re-aim the seven proof claims the corridor/degree/fill work moved.

Every one keeps its claim and points it at the rule in its new shape. Two of
them are strengthened rather than merely moved, because the new shape gave the
claim something better to assert; none is weakened. A claim relaxed to pass is
a claim that reports a guarantee nobody is holding.
"""
import io
import sys

NL = chr(10)
LAYOUT = ".local/register/proof-coordinate-layout.py"
BATCH = ".local/register/proof-generation-batch.py"

EDITS = [
    # ------------------------------------------------------- the ceiling that now admits diagonals
    (LAYOUT,
     '      and "private const int MaximumUndirectedEdgesPerRoom = 2;" in service' + NL
     + '      and "directedEdges > 2 * rooms.Count" not in service_code,' + NL
     + '      "-- **the old ceiling allowed a tree plus exactly ONE edge**, which is one loop in the whole "' + NL
     + '      "level at every depth. The line with alcoves was not a choice the generator made, it was "' + NL
     + '      "the only shape `ValidateRooms` would accept: every braided candidate was refused and the "' + NL
     + '      "fallback serpentine caught every seed. The floor is untouched, and it is the half of that "' + NL
     + '      "check that was always doing the work")',
     '      and "private const int MaximumUndirectedEdgesPerRoom = 4;" in service' + NL
     + '      and "private const int MaximumUndirectedEdgesPerRoom = 2;" not in service' + NL
     + '      and "directedEdges > 2 * rooms.Count" not in service_code,' + NL
     + '      "-- **the old ceiling allowed a tree plus exactly ONE edge**, which is one loop in the whole "' + NL
     + '      "level at every depth. The line with alcoves was not a choice the generator made, it was "' + NL
     + '      "the only shape `ValidateRooms` would accept: every braided candidate was refused and the "' + NL
     + '      "fallback serpentine caught every seed. **And TWO per room was the same clause again** -- "' + NL
     + '      "a slot has four orthogonal neighbours plus the four diagonals `BentLegs` can route to, so "' + NL
     + '      "at two it refused every maze that used the links the bend had just made possible. Four is "' + NL
     + '      "the grid geometry stated, not a preference. The floor is untouched, and it is the half of "' + NL
     + '      "that check that was always doing the work")'),

    # ----------------------------------------------------------- the third VariedRoomSpan call site
    (LAYOUT,
     '      and planner.count("VariedRoomSpan(spacing, next, seed, depth)") == 1' + NL
     + '      and planner.count("VariedRoomSpan(spacing, slot, seed, depth)") == 1,' + NL
     + '      "-- defined and called at BOTH room-making sites. A plant swapped the calls back to the "' + NL
     + '      "flat span and left the function sitting there, and every claim about variation still held")',
     '      and planner.count("VariedRoomSpan(spacing, next, seed, depth)") == 1' + NL
     + '      and planner.count("VariedRoomSpan(spacing, slot, seed, depth)") == 2,' + NL
     + '      "-- defined and called at ALL THREE room-making sites: the maze walk, the fallback "' + NL
     + '      "serpentine, and the sealed vaults added after every link is made. A plant swapped the "' + NL
     + '      "calls back to the flat span and left the function sitting there, and every claim about "' + NL
     + '      "variation still held. **The count is the point** -- it was two and a third site appeared "' + NL
     + '      "with the vaults, so a claim that only counted the old two would have let an unvaried "' + NL
     + '      "vault through")'),

    # ------------------------------------------------------ the doorway, now read off the corridor
    (LAYOUT,
     '      "SharedDoorCell" not in planner_code' + NL
     + '      and "other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX" in planner,' + NL
     + '      "-- an abutting neighbour\'s near edge is `maxX + 1`, which IS strictly beyond `maxX`, so "' + NL
     + '      "`DoorOpening`\'s existing rule already opens each room\'s own wall midpoint -- and "' + NL
     + '      "`AreGridNeighbors` guarantees linked centres share that axis, so the two midpoints are "' + NL
     + '      "the same cell on it and the openings meet. The deleted `SharedDoorCell` was a second rule "' + NL
     + '      "deciding one doorway")',
     '      "SharedDoorCell" not in planner_code' + NL
     + '      and "other.Bounds.minX > bounds.maxX && cell.x == bounds.maxX" in planner' + NL
     + '      and "if (TryStraightCorridor(room, other, out alongX, out line))" in planner,' + NL
     + '      "-- an abutting neighbour\'s near edge is `maxX + 1`, which IS strictly beyond `maxX`, so "' + NL
     + '      "`DoorOpening`\'s existing rule already opens each room\'s own wall. **What makes the two "' + NL
     + '      "openings the same cell is that both rooms ask `TryStraightCorridor` for the line, not an "' + NL
     + '      "assumption about their centres** -- since the straight run was generalised the two "' + NL
     + '      "centres need not share an axis at all, and the old reasoning here would have been a "' + NL
     + '      "guarantee resting on something no longer true. The deleted `SharedDoorCell` was a second "' + NL
     + '      "rule deciding one doorway")'),

    # ------------------------------------------- the carver collects legs before it cuts anything
    (LAYOUT,
     '      and "foreach (RoomLayoutPlanner.CorridorLeg leg in RoomLayoutPlanner.CorridorLegs(" in genstep,' + NL
     + '      "-- carving between two touching centres cuts a five-cell hole through the shared wall and "' + NL
     + '      "makes them one room")',
     '      and "List<RoomLayoutPlanner.CorridorLeg> legs = RoomLayoutPlanner.CorridorLegs(" in genstep' + NL
     + '      and "if (legs.Count == 0) { continue; }" in genstep,' + NL
     + '      "-- carving between two touching centres cuts a five-cell hole through the shared wall and "' + NL
     + '      "makes them one room. The carver now collects every leg of every pair before it cuts, "' + NL
     + '      "because a bend puts one leg\'s wall line inside the next leg\'s floor, so the empty list "' + NL
     + '      "is skipped where it is collected rather than where it is carved")'),

    # ------------------------------------- adjacency: the validator asks rather than re-deriving it
    (LAYOUT,
     '      "if (first.Bounds.Overlaps(second.Bounds)) { return false; }" in service' + NL
     + '      and "if (a.x == b.x) { return a.z != b.z; }" in service,' + NL
     + '      "-- what BuildCorridors actually needs: a shared row or column and a straight run of rock "' + NL
     + '      "between them")',
     '      "return RoomLayoutPlanner.AreNeighbourRooms(first, second);" in service' + NL
     + '      and "if (first.Bounds.Overlaps(second.Bounds)) { return false; }" in planner' + NL
     + '      and "internal static bool TryStraightCorridor(RoomRecord first, RoomRecord second," in planner' + NL
     + '      and "if (a.x == b.x) { return a.z != b.z; }" not in service_code,' + NL
     + '      "-- what `BuildCorridors` actually needs, asked of the one function that knows: a straight "' + NL
     + '      "run of rock between them, or a bend through the lane. **The validator held a SECOND COPY "' + NL
     + '      "of this arithmetic** and the copy was live -- the planner\'s half had to grow to admit "' + NL
     + '      "bent and generalised-straight corridors, and the copy would have refused every graph the "' + NL
     + '      "planner had just learned to build, on load, for every saved coordinate")'),

    # -------------------------------------------- the model and the build read the same authority
    (LAYOUT,
     '      and "floor[cell.x, cell.z] = true;" in planner' + NL
     + '      and "foreach (RoomLayoutPlanner.CorridorLeg leg in RoomLayoutPlanner.CorridorLegs(" in genstep,' + NL
     + '      "-- a model with a different width than the build is a model of a different map")',
     '      and "floor[cell.x, cell.z] = true;" in planner' + NL
     + '      and "List<RoomLayoutPlanner.CorridorLeg> legs = RoomLayoutPlanner.CorridorLegs(" in genstep' + NL
     + '      and "RoomLayoutPlanner.ShapeDepthOf(rooms, other, depth))," in genstep,' + NL
     + '      "-- a model with a different width than the build is a model of a different map, and a "' + NL
     + '      "model with a different SHAPE is worse: a bend the validator did not know about is an "' + NL
     + '      "unproved route. Both readers pass the pair\'s own shaping depth and the room list to the "' + NL
     + '      "same function and take back the same legs")'),

    # ------------------------------------------- the side cells, now a property of the whole route
    (BATCH,
     '      and "internal static IEnumerable<IntVec3> CorridorSideCells(CorridorLeg leg)" in _PL' + NL
     + '      and _PL.count("yield return new IntVec3(x, 0, floor.minZ);") == 1' + NL
     + '      and _PL.count("yield return new IntVec3(floor.minX, 0, z);") == 1' + NL
     + '      and "if (floor.Height < 3) { yield break; }" in _PL' + NL
     + '      and "if (floor.Width < 3) { yield break; }" in _PL' + NL
     + '      and "foreach (IntVec3 cell in RoomLayoutPlanner.CorridorSideCells(leg))" in genstep',
     '      and "internal static IEnumerable<IntVec3> CorridorSideCells(List<CorridorLeg> legs)" in _PL' + NL
     + '      and _PL.count("? new IntVec3(along, 0, floor.minZ) : new IntVec3(floor.minX, 0, along);") == 1' + NL
     + '      and _PL.count("? new IntVec3(along, 0, floor.maxZ) : new IntVec3(floor.maxX, 0, along);") == 1' + NL
     + '      and "if (leg.AlongX ? floor.Height < 3 : floor.Width < 3) { continue; }" in _PL' + NL
     # **THE WHOLE ROUTE, not a leg at a time.** At a bend one leg's outermost floor row IS the
     # next leg's centre line, so a per-leg reading of this rule hands the dressing a cell in the
     # middle of the corridor -- the exact fault the rule exists to prevent, arriving by the
     # feature that was supposed to be safe.
     + '      and "if (!OnAnotherLegFloor(legs, index, low)) { yield return low; }" in _PL' + NL
     + '      and "foreach (IntVec3 cell in RoomLayoutPlanner.CorridorSideCells(legs))" in genstep'),
]

problems = 0
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8").read()
    found = text.count(old)
    if found != 1:
        print("NOT UNIQUE (%d) in %s: %s" % (found, path, old.splitlines()[0][:80]))
        problems += 1
        continue
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new))
    print("re-aimed in %s: %s" % (path.split("/")[-1], old.splitlines()[0][:80]))

if problems:
    print("%d claim edit(s) did not apply" % problems)
    sys.exit(1)
print("all seven re-aimed")
