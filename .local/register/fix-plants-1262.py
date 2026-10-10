# -*- coding: utf-8 -*-
"""The plants for a geometry that could not be built.

Three plants in `plant-coordinate-layout.py` named code that is gone, because the design they
tested was the one that stopped every coordinate generating: a doorway in a wall column shared by
both rooms' bounds, which `CellRect.Overlaps` counts as an overlap and `ValidateRooms` refuses.
The suite stopped at setup rather than mutating anything, which is the behaviour that matters --
a plant that silently finds no match proves nothing while claiming to.

They are replaced with plants for the abutting geometry, and **four new ones are added for the
defect that actually shipped**: the validator's ceiling, the planner's statement of it, the push
that has to be reverted when it lands on a third room, and the spine that must not eat the whole
room budget. Each one breaks something no existing plant could reach.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

OLD = u'''    ("BACK-TO-BACK ROOMS ARE SEALED: each side opens its own centre", PLANNER,
     "                if (cell == SharedDoorCell(room, other)) { return true; }",
     "                if (cell.z == room.Bounds.CenterCell.z) { return true; }"),

    ("the shared doorway is never opened at all", PLANNER,
     "                if (cell == SharedDoorCell(room, other)) { return true; }", ""),

    ("a corridor is carved through the shared wall, merging the two rooms", GEN,
     "                    if (RoomLayoutPlanner.SharesWall(room, other)) { continue; }", ""),

    ("the validator still models a corridor the generator will not carve", PLANNER,
     "                    if (SharesWall(room, other)) { continue; }", ""),

    ("rooms stop being pushed together at all", PLANNER,
     "                    { PushAgainst(rooms[rooms.Count - 1], rooms[host]); }", ""),'''

NEW = u'''    # **THE SHAPE OF THE DEFECT THAT SHIPPED.** A back-to-back pair whose bounds share a wall
    # column OVERLAPS, because `CellRect.Overlaps` is inclusive on both edges, and
    # `ValidateRooms` has refused overlapping rooms since the first layout. Every pair made the
    # whole candidate illegal, all four candidates were refused, and the player got a letter
    # saying no safe layout was found with nothing in the log.
    ("BACK-TO-BACK ROOMS OVERLAP INSTEAD OF ABUTTING, so no candidate is ever legal", PLANNER,
     "            if ((a.maxX + 1 == b.minX || b.maxX + 1 == a.minX) && verticalOverlap)",
     "            if ((a.maxX == b.minX || b.maxX == a.minX) && verticalOverlap)"),

    ("the push puts the room on its host's wall column rather than beside it", PLANNER,
     "            if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX + 1; }",
     "            if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX; }"),

    ("THE PUSH IS NEVER PUT BACK, so a spur lands on top of a third room", PLANNER,
     "            if (onMap && !collides && SharesWall(mover, anchorRoom)) { return; }" + NL
     + "            mover.x = originalX;" + NL
     + "            mover.z = originalZ;" + NL,
     "            return;" + NL),

    ("the collision test is dropped and only the map bound is checked", PLANNER,
     "            bool collides = rooms.Any(other => other != mover && mover.Bounds.Overlaps(other.Bounds));",
     "            bool collides = false;"),

    ("a corridor is carved through the shared wall, merging the two rooms", GEN,
     "                    if (RoomLayoutPlanner.SharesWall(room, other)) { continue; }", ""),

    ("the validator still models a corridor the generator will not carve", PLANNER,
     "                    if (SharesWall(room, other)) { continue; }", ""),

    ("rooms stop being pushed together at all", PLANNER,
     "                    { PushAgainst(rooms, rooms[rooms.Count - 1], rooms[host]); }", ""),

    # -------------------------------------------- the ceiling the hall has to pass
    # **NOTHING COULD REACH THIS BEFORE.** `MaxRoomSpan` recomputed the span of a room filling
    # one slot -- 34 at depth 1 -- while the grand hall spans two slots and is 80.
    ("THE VALIDATOR RECOMPUTES THE WIDEST SPAN INSTEAD OF ASKING THE PLANNER", SERVICE,
     "            get { return RoomLayoutPlanner.WidestRoomSpan; }",
     "            get { return RoomLayoutPlanner.SlotRoomSpan("
     + "RoomLayoutPlanner.SlotSpacing(RoomLayoutPlanner.MinSlotsPerAxis)); }"),

    ("the planner's ceiling forgets the two-slot hall", PLANNER,
     "                return hall > varied ? hall : varied;",
     "                return varied;"),

    ("and it forgets that a span may vary upward", PLANNER,
     "                int varied = SlotRoomSpan(spacing) + SpanVariation;",
     "                int varied = SlotRoomSpan(spacing);"),

    ("THE SPINE EATS THE WHOLE ROOM BUDGET AND THE DEEP LEVELS LOSE EVERY BRANCH", PLANNER,
     "            if (chainLength > MaxRooms * 2 / 3) { chainLength = MaxRooms * 2 / 3; }",
     "            if (chainLength > MaxRooms) { chainLength = MaxRooms; }"),'''

text = io.open(SUITE, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("plant suite rewritten: abutment, the reverted push, and four for the ceiling")
