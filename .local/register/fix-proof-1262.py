# -*- coding: utf-8 -*-
"""The two claims that guarded the geometry guarded the wrong thing.

0.12.61-dev shipped a planner that could not produce a single valid layout, and these two claims
passed the whole time. They were faithful readings of the design as written -- and the design as
written was wrong:

  * `SharedDoorCell` computed a doorway in a wall column shared by both rooms' bounds. Two rooms
    whose bounds share a column **overlap**, by `CellRect.Overlaps`, which is inclusive on both
    edges -- and `ValidateRooms` has refused overlapping rooms since the first layout. So the
    claim proved the arithmetic of a geometry the validator would never accept.
  * `PushAgainst(rooms[rooms.Count - 1], rooms[host])` was pinned as literal call text, so the
    claim held while two of that method's four branches produced the illegal overlap and the other
    two produced an abutment the old `SharesWall` did not recognise.

**And no claim anywhere asserted the thing that actually broke it**: `DestinationService`
carried its own copy of the widest span the planner can produce -- `SlotRoomSpan(SlotSpacing(
MinSlotsPerAxis))`, which is 34 -- while the planner's grand hall is 80. Every candidate refused,
`TrySelect` false, and the player got a letter with nothing in the log.

So the claims are rewritten to the new geometry, and **three new ones are added for the ceiling**:
that the validator asks the planner rather than recomputing, that the planner's answer accounts
for both the hall and the span variation, and that the spine never takes the whole room budget.

A claim that pins call text proves a call happened. **It cannot prove the call was legal**, and
the thing that catches that is running the planner.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

DOOR_OLD = u'''check("THE SHARED DOORWAY IS COMPUTED FROM THE OVERLAP, NOT FROM EITHER ROOM'S CENTRE",
      "internal static IntVec3 SharedDoorCell(" in planner
      and "int low = Math.Max(a.minZ, b.minZ) + 1;" in planner
      and "if (cell == SharedDoorCell(room, other)) { return true; }" in planner,
      "-- the shared column belongs to BOTH rooms' bounds and the floor grid is written room by "
      "room. Each opening its own centre would name different cells and the second write would "
      "seal the first: a back-to-back pair would have been a SEALED pair")'''

DOOR_NEW = u'''check("A BACK-TO-BACK PAIR ABUTS, IT DOES NOT OVERLAP",
      "a.maxX + 1 == b.minX || b.maxX + 1 == a.minX" in planner
      and "a.maxZ + 1 == b.minZ || b.maxZ + 1 == a.minZ" in planner
      and "a.maxX == b.minX" not in planner
      and "SharedDoorCell" not in planner,
      "-- `CellRect.Overlaps` is INCLUSIVE on both edges, so two rooms sharing a wall column "
      "overlap by RimWorld's own reckoning, and `ValidateRooms` has refused overlapping rooms "
      "since the first layout. The first draft tested for equal edges, so EVERY back-to-back "
      "pair made the whole candidate illegal and no coordinate would generate. Each room keeps "
      "its own wall, one cell apart")

check("and the doorway in it needs no second rule, so there is not one",
      "if (cell == SharedDoorCell" not in planner
      and "other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX" in planner,
      "-- an abutting neighbour's near edge is `maxX + 1`, which IS strictly beyond `maxX`, so "
      "`DoorOpening`'s existing rule already opens each room's own wall midpoint -- and "
      "`AreGridNeighbors` guarantees linked centres share that axis, so the two midpoints are "
      "the same cell on it and the openings meet. The deleted `SharedDoorCell` was a second rule "
      "deciding one doorway")'''

PUSH_OLD = u'''check("and only a spur is ever pushed, never a chain room",
      "PushAgainst(rooms[rooms.Count - 1], rooms[host]);" in planner
      and "private static void PushAgainst(" in planner,
      "-- a spur has exactly one connection, so moving it can only affect that pair and can "
      "never re-route the spine")'''

PUSH_NEW = u'''check("and only a spur is ever pushed, never a chain room",
      "PushAgainst(rooms, rooms[rooms.Count - 1], rooms[host]);" in planner
      and "private static void PushAgainst(List<RoomRecord> rooms, RoomRecord mover," in planner,
      "-- a spur has exactly one connection, so moving it can only affect that pair and can "
      "never re-route the spine")

check("AND THE PUSH IS PUT BACK IF IT LANDED ON SOMEBODY",
      "bool collides = rooms.Any(other => other != mover && mover.Bounds.Overlaps(other.Bounds));"
      in planner
      and "if (onMap && !collides && SharesWall(mover, anchorRoom)) { return; }" in planner
      and "mover.x = originalX;" in planner,
      "-- the slot a spur leaves is not the slot it arrives in, and the arrival may belong to a "
      "third room. All three conditions are checked -- on the map, no collision, and `SharesWall` "
      "agrees -- because a pair the pushing code thinks is back to back and the doorway code "
      "does not is a sealed room")'''

CEILING_ANCHOR = u'''check("MOST LEFTOVER SLOTS BECOME BRANCHES, which is what makes it a maze",'''

CEILING_NEW = u'''# --------------------------------------------- the ceiling the hall has to pass
# **THIS IS THE ONE NOBODY WROTE, AND IT IS THE ONE THAT BROKE THE GAME.** `ValidateRooms` refuses
# any room wider than `MaxRoomSpan`, and that property recomputed the span of a room filling one
# slot -- 34 at depth 1 -- while the planner's grand hall takes two slots and is 80. Candidates 0,
# 1 and 2 were refused every time; the fallback was refused whenever any room's span varied upward,
# which over twenty-odd rooms is every time. Four refusals, `TrySelect` false, and the player got
# *"No safe first-site layout was found within the bounded attempt limit"* with a clean log.
#
# The number is a statement about the planner, so the planner states it, and the validator asks.
check("THE VALIDATOR ASKS THE PLANNER HOW WIDE A ROOM CAN BE, AND DOES NOT RECOMPUTE IT",
      "get { return RoomLayoutPlanner.WidestRoomSpan; }" in service
      and "SlotRoomSpan(\\n                    RoomLayoutPlanner.SlotSpacing" not in service,
      "-- a validator carrying its own copy of a number the planner decides is the same defect as "
      "the literal 19 this file already removed once, and as the light count that stopped "
      "generation for thirty-nine checkpoints")

check("and the planner's answer counts BOTH the two-slot hall and the span variation",
      "internal static int WidestRoomSpan" in planner
      and "int hall = spacing * 2 - SlotGap;" in planner
      and "int varied = SlotRoomSpan(spacing) + SpanVariation;" in planner
      and "return hall > varied ? hall : varied;" in planner,
      "-- the hall is the widest thing the planner builds and the variation is the widest an "
      "ordinary room gets. Either one alone is a ceiling the other walks straight through")

check("THE SPINE NEVER TAKES THE WHOLE ROOM BUDGET",
      "if (chainLength > MaxRooms * 2 / 3) { chainLength = MaxRooms * 2 / 3; }" in planner,
      "-- the cap was `MaxRooms`, so from depth 5 the serpentine alone reached sixty rooms and "
      "the spur loop, which runs while `rooms.Count < MaxRooms`, never executed once. The "
      "deepest levels had NO dead ends, NO branches and NO back-to-back pairs -- the opposite of "
      "*\\"it needs to be more maze liek\\"*. A sixty-room chain with no branches is a corridor")

''' + CEILING_ANCHOR

EDITS = [(DOOR_OLD, DOOR_NEW), (PUSH_OLD, PUSH_NEW), (CEILING_ANCHOR, CEILING_NEW)]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("proof rewritten: abutment, the reverted push, and the ceiling that was never claimed")
