# -*- coding: utf-8 -*-
"""Four claims described the serpentine. It is gone, so they describe the maze.

Each refusal was correct: they pinned the chain length, the spur rate, the push call and the
room-making sites of a spine that no longer exists. None of them is relaxed -- each is rewritten
to assert what now guarantees the same property, and four new ones cover the maze itself.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

EDITS = [
    # 1. The chain length is gone; the maze is bounded by the room cap.
    (u'''check("the chain still takes two thirds of the grid",''',
     u'''check("THE SPINE IS A BRAIDED MAZE, NOT A LINE THAT SNAKES",
      "private static List<RoomRecord> BuildMaze(" in planner
      and "return BuildMaze(coordinate, slots, spacing, seed, depth);" in planner
      and "var stack = new List<IntVec2> { hallSecond };" in planner
      and 'int turn = DestinationService.StableHash(seed,' in planner
      and "if (!advanced) { stack.RemoveAt(stack.Count - 1); }" in planner,
      "-- owner: *\\"all the backrooms so far are just one lone strain of perals arangement that "
      "snakes back and forth across the map like one series line... i want them to be mazes like "
      "xcrazy\\"*. **That was a description of the code**: the slot grid walked row-major with "
      "alternating direction, room N linked to N-1. A randomised depth-first walk whose turn "
      "order comes from each slot's own hash branches instead of sweeping")

check("and it is BRAIDED, so there is more than one way through",
      "internal const int BraidRarity = 3;" in planner
      and "roll % BraidRarity != 0" in planner
      and "if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }" in planner,
      "-- a spanning tree has exactly one route between any two rooms: walk it wrong and you "
      "backtrack. Linking back one in three of the adjacent pairs the walk left alone gives "
      "loops, junctions that lie and corridors that rejoin somewhere unexpected. Checked against "
      "the SAME predicate the validator uses, so a braid it would refuse is never made")

check("and the graph ceiling admits a maze at all",
      "directedEdges > 2 * MaximumUndirectedEdgesPerRoom * rooms.Count" in service
      and "private const int MaximumUndirectedEdgesPerRoom = 2;" in service
      and "directedEdges > 2 * rooms.Count" not in service_code,
      "-- **the old ceiling allowed a tree plus exactly ONE edge**, which is one loop in the whole "
      "level at every depth. The line with alcoves was not a choice the generator made, it was "
      "the only shape `ValidateRooms` would accept: every braided candidate was refused and the "
      "fallback serpentine caught every seed. The floor is untouched, and it is the half of that "
      "check that was always doing the work")

check("and the walk declines a step the validator would refuse",
      "if (!AreNeighbourRooms(rooms[parent], room)) { continue; }" in planner,
      "-- the hall spans two slots so its centre sits BETWEEN them, matching no slot's centre, and "
      "a step from it in any direction but along its own row produces a link `AreGridNeighbors` "
      "refuses. **That one link made every maze candidate illegal.** Declined rather than forced: "
      "the slot is reached later from another parent, which a maze can do and a line cannot")

check("the fallback candidate is still the simple serpentine",'''),

    # 2. Both room-making sites: the maze and the fallback.
    (u'''check("AND ROOM SIZES ARE ACTUALLY VARIED, not merely variable",''',
     u'''check("AND ROOM SIZES ARE ACTUALLY VARIED, not merely variable",'''),

    # 3. The push is on a dead end, found by its link count.
    (u'''check("and only a spur is ever pushed, never a chain room",
      "PushAgainst(rooms, rooms[rooms.Count - 1], rooms[host]);" in planner
      and "private static void PushAgainst(List<RoomRecord> rooms, RoomRecord mover," in planner,
      "-- a spur has exactly one connection, so moving it can only affect that pair and can "
      "never re-route the spine")''',
     u'''check("and only a DEAD END is ever pushed, found by its link count",
      "if (rooms[index].links.Count != 1) { continue; }" in planner
      and "PushAgainst(rooms, rooms[index], rooms[host]);" in planner
      and "private static void PushAgainst(List<RoomRecord> rooms, RoomRecord mover," in planner,
      "-- a room with one connection cannot re-route anything by moving, and in a braided maze a "
      "dead end is found by asking rather than by knowing which rooms were added last. The old "
      "claim pinned `rooms[rooms.Count - 1]`, which was the spur loop's last-added room")'''),

    # 4. Branching is the maze itself, not a leftover-slot draw.
    (u'''check("MOST LEFTOVER SLOTS BECOME BRANCHES, which is what makes it a maze",
      "% 4 == 3)" in planner,''',
     u'''check("BRANCHING IS THE MAZE ITSELF, not a draw over leftover slots",
      "% 4 == 3)" not in planner_code
      and "private static void AssignMazeFamilies(" in planner
      and "if (rooms[index].links.Count == 1)" in planner,'''),
]

text = io.open(PROOF, encoding="utf-8").read()
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
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("four claims rewritten to the maze, four added for it")
