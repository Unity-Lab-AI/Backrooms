# -*- coding: utf-8 -*-
"""Four shape claims pinned the exact old call text, and all four refused the change correctly.

They each asserted that the generator passes `coordinateDepth` and the validator passes `depth`
-- a faithful description of the code when it was written, and **exactly the thing that switched
every shape system off at depth 1**, which is the level the owner walked and called *"nothing but
what it currently is"*.

Retargeted at the property that actually matters, which is stronger than what they said before:
**both readers pass the SAME per-room shaping depth.** It was never really about which variable
name appeared; it was about the generator and the validator agreeing. A room shaped one way and
proved walkable another is the defect that cost thirty-nine checkpoints, and these claims now say
so directly rather than by naming a parameter.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

EDITS = [
    (u'''check("ROCK IS LEFT STANDING INSIDE A ROOM, SO IT IS NOT A RECTANGLE",
      "internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)" in planner
      and "RoomLayoutPlanner.RockIntrusionCells(room, coordinateDepth)" in genstep,''',
     u'''check("ROCK IS LEFT STANDING INSIDE A ROOM, SO IT IS NOT A RECTANGLE",
      "internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)" in planner
      and "RoomLayoutPlanner.RockIntrusionCells(room," in genstep
      and "RoomLayoutPlanner.ShapeDepthOf(coordinate.Rooms, room, coordinateDepth)" in genstep,'''),

    (u'''check("the shape is decided in one place, like the pillars",
      planner.count("internal static IEnumerable<IntVec3> RockIntrusionCells") == 1
      and "foreach (IntVec3 rock in RockIntrusionCells(room, depth))" in planner
      and genstep.count("RoomLayoutPlanner.RockIntrusionCells(room, coordinateDepth)") == 1,''',
     u'''# **BOTH READERS PASS THE SAME SHAPING DEPTH.** This used to assert that the generator passed
# `coordinateDepth` and the validator passed `depth` -- which is precisely what kept every shape
# system off at depth 1. The property was never the parameter name; it was that the room the
# validator proves walkable is the room that gets built.
check("the shape is decided in one place, like the pillars",
      planner.count("internal static IEnumerable<IntVec3> RockIntrusionCells") == 1
      and "foreach (IntVec3 rock in RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth)))"
      in planner
      and genstep.count("RoomLayoutPlanner.RockIntrusionCells(room,") == 1
      and planner.count("internal static int ShapeDepthOf(") == 1,'''),

    (u'''check("HALLWAYS ARE NOT ALL ONE WIDTH",
      "internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)"
      in planner
      and "RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth)" in genstep
      and "private const int CorridorHalfWidth" not in genstep,''',
     u'''check("HALLWAYS ARE NOT ALL ONE WIDTH",
      "internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)"
      in planner
      and "RoomLayoutPlanner.CorridorHalfWidthBetween(room, other," in genstep
      and "RoomLayoutPlanner.ShapeDepthOf(rooms, room, depth)" in genstep
      and "private const int CorridorHalfWidth" not in genstep,'''),

    (u'''check("the planner models the same corridor width the generator carves",
      "int reach = CorridorHalfWidthBetween(room, other, depth) - 1;" in planner
      and "for (int dz = -reach; dz <= reach; dz++)" in planner,''',
     u'''check("the planner models the same corridor width the generator carves",
      "int reach = CorridorHalfWidthBetween(room, other," in planner
      and "ShapeDepthOf(rooms, room, depth)" in planner
      and "for (int dz = -reach; dz <= reach; dz++)" in planner,'''),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)

# And the new property itself gets a claim, because nothing asserted it.
A = u'check("MOST LEFTOVER SLOTS BECOME BRANCHES, which is what makes it a maze",'
B = u'''# **SHAPE REACHES THE FIRST LEVEL AT ALL.** Owner: *"you can have back to back roomes and mazes
# of halways of varied widtchs and lengs ... triangle, octangones, rombones, all the geomentry ...
# not just doors on 4 cosides of nothing but square rooms"*. Three shape systems each opened with
# `depth <= 1` and refused to run, so every room on the level the owner walked was a rectangle
# joined by identical corridors. Distance from the spawn hall is depth now.
check("SHAPE AND WIDTH ARE MEASURED FROM THE SPAWN HALL, NOT FROM THE COORDINATE",
      "internal static int ShapeDepthOf(" in planner
      and "int band = hops / LinksPerShapeBand;" in planner,
      "-- the hall and its neighbours stay square, which is the arrival reading as the one built "
      "thing, and everything past it comes apart")

''' + A
if text.count(A) != 1:
    print("MAZE ANCHOR PROBLEM: %d" % text.count(A))
    raise SystemExit(1)
text = text.replace(A, B, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("four claims retargeted at agreement, one added for reach")
