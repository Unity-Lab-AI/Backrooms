"""Re-aim the five plant anchors the corridor/degree/fill work moved.

Each replacement keeps the SAME claim and points it at the same rule in its new
shape. A plant that is weakened to find its anchor is worse than a broken one,
because it reports a pass it never earned.
"""
import io
import sys

NL = chr(10)
EDITS = [
    # ---------------------------------------------------------------- plant-coordinate-layout.py
    (".local/register/plant-coordinate-layout.py",
     '     "internal const int Margin = 14;", "internal const int Margin = -60;"),',
     '     "internal const int Margin = 6;", "internal const int Margin = -60;"),'),

    # The braid rarity gained a junction escape, so the line the plant removes is longer. Same
    # fault planted: no adjacent pair the walk left alone is ever linked back.
    (".local/register/plant-coordinate-layout.py",
     '     "                    if (roll % BraidRarity != 0) { continue; }",' + NL
     + '     "                    if (true) { continue; }"),',
     '     "                    if (!SlotIsJunction(seed, slot, depth) && roll % BraidRarity != 0) '
     '{ continue; }",' + NL
     + '     "                    if (true) { continue; }"),'),

    # `AreGridNeighbors` stopped carrying its own arithmetic and now asks the planner, which is
    # what this plant was always protecting: the validator must not re-derive the geometry. So the
    # fault is planted by giving it arithmetic again, with the literal back in it.
    (".local/register/plant-coordinate-layout.py",
     '    ("THE FIXED 19-CELL SPACING COMES BACK INTO THE VALIDATOR", SERVICE,' + NL
     + '     "            if (a.x == b.x) { return a.z != b.z; }",' + NL
     + '     "            if (a.x == b.x) { return Math.Abs(a.z - b.z) == 19; }"),',
     '    ("THE FIXED 19-CELL SPACING COMES BACK INTO THE VALIDATOR", SERVICE,' + NL
     + '     "            return RoomLayoutPlanner.AreNeighbourRooms(first, second);",' + NL
     + '     "            IntVec3 a = first.Bounds.CenterCell;" + NL' + NL
     + '     + "            IntVec3 b = second.Bounds.CenterCell;" + NL' + NL
     + '     + "            return Math.Abs(a.x - b.x) == 19 || Math.Abs(a.z - b.z) == 19;"),'),

    # The carver now hands the room list to the corridor authority as well as the shaping depth.
    # Same fault: the generator asking for a corridor at the coordinate's own depth rather than
    # the pair's, so it carves a different corridor than the validator proved.
    (".local/register/plant-coordinate-layout.py",
     '     "                        Math.Max(RoomLayoutPlanner.ShapeDepthOf(rooms, room, depth)," + NL' + NL
     + '     + "                            RoomLayoutPlanner.ShapeDepthOf(rooms, other, depth))))",' + NL
     + '     "                        depth))"),',
     '     "                        Math.Max(RoomLayoutPlanner.ShapeDepthOf(rooms, room, depth)," + NL' + NL
     + '     + "                            RoomLayoutPlanner.ShapeDepthOf(rooms, other, depth))," + NL' + NL
     + '     + "                        rooms);",' + NL
     + '     "                        depth," + NL + "                        rooms);"),'),

    # ---------------------------------------------------------------------- plant-generation.py
    # `CorridorSideCells` takes the whole route now, because at a bend one leg's outermost floor
    # row is the next leg's centre line. Same fault planted: it reports the centre line.
    (".local/register/plant-generation.py",
     '     "                    yield return new IntVec3(x, 0, floor.minZ);",' + NL
     + '     "                    yield return new IntVec3(x, 0, floor.CenterCell.z);"),',
     '     "                    IntVec3 low = leg.AlongX" + NL' + NL
     + '     + "                        ? new IntVec3(along, 0, floor.minZ) : '
     'new IntVec3(floor.minX, 0, along);",' + NL
     + '     "                    IntVec3 low = leg.AlongX" + NL' + NL
     + '     + "                        ? new IntVec3(along, 0, floor.CenterCell.z) : '
     'new IntVec3(floor.CenterCell.x, 0, along);"),'),
]

problems = 0
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8").read()
    found = text.count(old)
    if found != 1:
        print("NOT UNIQUE (%d): %s" % (found, old.splitlines()[0][:90]))
        problems += 1
        continue
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new))
    print("re-aimed: %s" % old.splitlines()[0][:90])

if problems:
    print("%d anchor edit(s) did not apply" % problems)
    sys.exit(1)
print("all five re-aimed")
