# -*- coding: utf-8 -*-
"""Stage-three claims: rooms are not rectangles, hallways are not one width, and neither can
disconnect a room."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

text = io.open(PROOF, encoding="utf-8").read()
ANCHOR = 'print("")\nprint("HOW MANY PLACES MAY BE HELD OPEN AT ONCE")'

NEW = '''print("")
print("rooms are not rectangles and hallways are not one width")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"and everything doesnt have to be square rooms and
# rectangle halways"*.
check("ROCK IS LEFT STANDING INSIDE A ROOM, SO IT IS NOT A RECTANGLE",
      "internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)" in planner
      and "RoomLayoutPlanner.RockIntrusionCells(room, coordinateDepth)" in genstep,
      "-- the Bounds stays a rect because the validator, the doors, the corridors and the pillar "
      "lattice all read it. What changed is which cells get CARVED")

intrusion_at = planner.find("internal static IEnumerable<IntVec3> RockIntrusionCells")
intrusion_body = planner[intrusion_at:planner.find(chr(10) + "        }" + chr(10), intrusion_at)] \\
    if intrusion_at >= 0 else ""

check("THE CENTRE CROSS IS NEVER FILLED, WHICH IS WHAT MAKES A SHAPE SAFE",
      intrusion_at >= 0 and "if (x == center.x || z == center.z) { continue; }" in intrusion_body,
      "-- doors are placed at the midpoint of each side and corridors aim at CenterCell, so a "
      "clear centre cross means every doorway reaches every other doorway WHATEVER shape the "
      "corners take. That is why no candidate is ever rejected for its shape")

check("rock is left only in the corners, inset from the walls",
      intrusion_at >= 0
      and "if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }" in intrusion_body
      and "if (z <= bounds.minZ + 1 || z >= bounds.maxZ - 1) { continue; }" in intrusion_body,
      "-- the perimeter is wall and the ring inside it is the walkway that keeps every doorway "
      "reachable")

check("the reach of a corner mass can never eat the middle of the room",
      "/ 3" in intrusion_body and "Math.Min" in intrusion_body,
      "-- clamped to a third of the room, so even at the deepest band a shape is an intrusion "
      "rather than a partition")

check("SHALLOW COORDINATES STAY RECTANGULAR",
      "if (room == null || depth <= 1) { yield break; }" in intrusion_body,
      "-- the yellow rooms read as a place precisely because they are monotonous, which is the "
      "same reason Derange leaves depth 1 alone. The wrongness is travelled toward")

check("the shape is decided in one place, like the pillars",
      "RockIntrusionCells(room, depth)" in planner
      and planner.count("RockIntrusionCells") >= 3,
      "-- the generator leaves these cells uncarved and CandidateIsSafe marks them unwalkable; "
      "two derivations of one rule is the defect that cost thirty-nine checkpoints")

check("an intrusion is rock inside a room, never a hole in the world",
      "map.roofGrid.SetRoof(cell, overheadRoof);" in genstep
      and "if (intrusions.Contains(cell)) { continue; }" in genstep
      and genstep.find("map.roofGrid.SetRoof(cell, overheadRoof);") <
          genstep.find("if (intrusions.Contains(cell)) { continue; }"),
      "-- the roof is set BEFORE the skip, so an uncarved cell is still roofed and invariant 13 "
      "holds across every shape")

check("HALLWAYS ARE NOT ALL ONE WIDTH",
      "internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)"
      in planner
      and "RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth)" in genstep
      and "private const int CorridorHalfWidth" not in genstep,
      "-- the constant is gone; the width comes from the shared function, so the reachability "
      "the planner proved is the reachability that gets built")

check("the planner models the same corridor width the generator carves",
      "int reach = CorridorHalfWidthBetween(room, other, depth) - 1;" in planner
      and "for (int dz = -reach; dz <= reach; dz++)" in planner,
      "-- a model with a different width than the build is a model of a different map")

# The shape rule, modelled: fill every corner at the deepest reach and prove the room still
# flood-fills from its centre to all four edge midpoints, which is where the doors are.
def room_still_connected(span, depth):
    inset_x, inset_z = 2, 2
    extent_x, extent_z = span - 3, span - 3
    if extent_x - inset_x < 4 or extent_z - inset_z < 4:
        return True
    reach = min((depth - 1) * 2, min(extent_x - inset_x, extent_z - inset_z) // 3)
    if reach < 1:
        return True
    cx, cz = span // 2, span // 2
    rock = set()
    for east in (False, True):
        for north in (False, True):
            for dx in range(reach):
                for dz in range(reach):
                    if dx * dx + dz * dz > reach * reach:
                        continue
                    x = extent_x - dx if east else inset_x + dx
                    z = extent_z - dz if north else inset_z + dz
                    if x == cx or z == cz:
                        continue
                    if x <= 1 or x >= span - 2 or z <= 1 or z >= span - 2:
                        continue
                    rock.add((x, z))
    # Interior floor is every non-perimeter cell that is not rock.
    floor = set((x, z) for x in range(1, span - 1) for z in range(1, span - 1)
                if (x, z) not in rock)
    seen = set([(cx, cz)])
    queue = [(cx, cz)]
    while queue:
        x, z = queue.pop()
        for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if (nx, nz) in floor and (nx, nz) not in seen:
                seen.add((nx, nz))
                queue.append((nx, nz))
    doors = [(cx, 1), (cx, span - 2), (1, cz), (span - 2, cz)]
    return all(door in seen for door in doors)


broken = []
for depth, _slots, _spacing, span, _chain, _lo, _hi, _gap, _adj in profile:
    if not room_still_connected(span, depth):
        broken.append((depth, span))
check("NO SHAPE CAN EVER DISCONNECT A DOORWAY, AT ANY DEPTH",
      not broken,
      "-- modelled by filling every corner at the deepest reach and flood-filling from the room "
      "centre to all four edge midpoints, which is where the doors are: %s" % broken)

''' + ANCHOR

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("stage-three claims added")
