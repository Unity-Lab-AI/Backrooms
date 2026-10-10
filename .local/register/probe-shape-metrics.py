# -*- coding: utf-8 -*-
"""Make the probe report how square the rooms actually are.

Owner, twice: *"the hall ways are just rectangles"* and *"they were all just square rooms
again..wtf dont u know any other compbinations"*.

`RockIntrusionCells` is the only thing that makes a room not a rectangle, and its reach is
`min((depth - 1) * 2, span / 3)`. `ShapeDepthOf` gives a depth-1 room `1 + hops / 3`, capped at
four bands -- so a room within two links of the hall gets reach **zero** and a room three links
out gets reach **two**. Two cells of rock in the corner of a thirty-four-cell room is **0.3% of
its interior**, which is a rectangle with a chipped corner.

So the probe measures it: what share of rooms have any rock at all, and what share of the interior
that rock is. **Those two numbers are the owner's complaint, and they are measurable at the desk.**

Written to a file because the format string is full of braces and a heredoc has mangled an escape
eleven times in this project.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = os.path.join(REPO, ".local", "harness", "PlannerProbe", "Program.cs")

EDITS = [
    (u"        private static MethodInfo rockCells;",
     u"        private static MethodInfo rockIntrusionCells;"),

    (u'rockCells = planner.GetMethod("RockIntrusionCells", Statics);',
     u'rockIntrusionCells = planner.GetMethod("RockIntrusionCells", Statics);'),

    (u"                int tightest = int.MaxValue;\n                int starved = 0;",
     u"                int tightest = int.MaxValue;\n"
     u"                int starved = 0;\n"
     u"                int shapedRooms = 0;\n"
     u"                int totalRooms = 0;\n"
     u"                long rockTotal = 0;\n"
     u"                long interiorTotal = 0;"),

    (u"                        int margined = MarginedCells(layout, room, depth);",
     u"                        // **HOW SQUARE IS IT, REALLY.** The owner's complaint, as a number.\n"
     u"                        totalRooms++;\n"
     u"                        int roomShapeDepth = (int)shapeDepthOf.Invoke(\n"
     u"                            null, new object[] { layout, room, depth });\n"
     u"                        int rock = 0;\n"
     u"                        foreach (Verse.IntVec3 rockCell in (IEnumerable<Verse.IntVec3>)\n"
     u"                            rockIntrusionCells.Invoke(null, new object[] { room, roomShapeDepth }))\n"
     u"                        { rock++; }\n"
     u"                        if (rock > 0) { shapedRooms++; }\n"
     u"                        rockTotal += rock;\n"
     u"                        var roomBounds = (Verse.CellRect)roomType.GetProperty(\"Bounds\")\n"
     u"                            .GetValue(room, null);\n"
     u"                        interiorTotal += roomBounds.ContractedBy(1).Area;\n"
     u"                        int margined = MarginedCells(layout, room, depth);"),

    (u'                    "{0} depth {1,-2}  refused {2,3}/{3}  avg rooms {4,5:0.0}  widest {5,3}  pairs {6,4}  tightest margin {7,3}  starved rooms {8,5}",\n'
     u"                    verdict, depth, refused, Seeds, refused == Seeds ? 0.0 : (double)rooms / (Seeds - refused),\n"
     u"                    widest, backToBack, tightest == int.MaxValue ? -1 : tightest, starved));",
     u'                    "{0} depth {1,-2} refused {2,3}/{3} rooms {4,4:0.0} widest {5,3} '
     u'pairs {6,4} margin {7,3} starved {8,4} shaped {9,5:0.0}% rock {10,4:0.0}%",\n'
     u"                    verdict, depth, refused, Seeds, refused == Seeds ? 0.0 : (double)rooms / (Seeds - refused),\n"
     u"                    widest, backToBack, tightest == int.MaxValue ? -1 : tightest, starved,\n"
     u"                    totalRooms == 0 ? 0.0 : 100.0 * shapedRooms / totalRooms,\n"
     u"                    interiorTotal == 0 ? 0.0 : 100.0 * rockTotal / interiorTotal));"),
]

text = io.open(PROBE, encoding="utf-8").read()
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
text = text.replace(u"rockCells.Invoke(", u"rockIntrusionCells.Invoke(")
io.open(PROBE, "w", encoding="utf-8", newline="").write(text)
print("probe reports shaped-room share and rock share of interior")
