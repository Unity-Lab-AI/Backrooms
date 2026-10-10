# -*- coding: utf-8 -*-
"""Four plants targeted the serpentine. They target the maze, and four more cover it.

The suite refused to run rather than matching nothing, which is the behaviour that matters.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

EDITS = [
    (u'''    ("THE GRAND THRESHOLD HALL IS LOST", PLANNER,
     "rooms.Add(MakeHall(coordinate, order[0], order[1], spacing, seed, depth));", ""),''',
     u'''    ("THE GRAND THRESHOLD HALL IS LOST", PLANNER,
     "rooms.Add(MakeHall(coordinate, hallFirst, hallSecond, spacing, seed, depth));", ""),'''),

    (u'''    ("the hall grows to four slots and breaks the chain's adjacency", PLANNER,
     "                consumed = 2;", "                consumed = 4;"),''',
     u'''    ("the maze starts inside the hall instead of beside it", PLANNER,
     "            var stack = new List<IntVec2> { hallSecond };",
     "            var stack = new List<IntVec2> { hallFirst };"),

    # ------------------------------------------------------- the maze itself
    # Owner: *"all the backrooms so far are just one lone strain of perals arangement that snakes
    # back and forth across the map like one series line... i want them to be mazes like xcrazy"*.
    ("THE SPINE GOES BACK TO BEING A LINE THAT SNAKES", PLANNER,
     "            return BuildMaze(coordinate, slots, spacing, seed, depth);",
     "            return BuildSerpentine(coordinate, order, spacing, seed, depth);"),

    ("the walk sweeps instead of turning, so it is a line again", PLANNER,
     "                int turn = DestinationService.StableHash(seed," + chr(10)
     + '                    "maze:" + current.x + "," + current.z, depth);',
     "                int turn = 0;" + chr(10)
     + '                string unusedMazeKey = "maze:" + current.x + "," + current.z;'),

    ("THE BRAID IS GONE, so the maze is a tree with one route through it", PLANNER,
     "                    if (roll % BraidRarity != 0) { continue; }",
     "                    if (true) { continue; }"),

    ("the graph ceiling goes back to allowing a tree plus one loop", SERVICE,
     "                directedEdges > 2 * MaximumUndirectedEdgesPerRoom * rooms.Count)",
     "                directedEdges > 2 * rooms.Count)"),

    ("the walk stops declining a step the validator would refuse", PLANNER,
     "                    if (!AreNeighbourRooms(rooms[parent], room)) { continue; }" + chr(10), ""),

    ("a braid is made that the validator would refuse", PLANNER,
     "                    if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }" + chr(10), ""),'''),

    (u'''     "% 4 == 3)", "% 3 != 0)"),''',
     u'''     "if (rooms[index].links.Count != 1) { continue; }",
     "if (rooms[index].links.Count < 1) { continue; }"),'''),

    (u'''     "                    { PushAgainst(rooms, rooms[rooms.Count - 1], rooms[host]); }", ""),''',
     u'''     "                PushAgainst(rooms, rooms[index], rooms[host]);" + chr(10), ""),'''),
]

text = io.open(SUITE, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:62]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)

# The suite needs the validator as a target.
T_ANCHOR = u'SERVICE = SRC + "/Generation/DestinationService.cs"'
if T_ANCHOR not in text:
    print("NOTE: adding the SERVICE target")
    text = text.replace(u'PLANNER = SRC + "/Generation/RoomLayoutPlanner.cs"',
                        u'PLANNER = SRC + "/Generation/RoomLayoutPlanner.cs"\n' + T_ANCHOR, 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text)
print("four plants retargeted, six added for the maze and the ceiling")
