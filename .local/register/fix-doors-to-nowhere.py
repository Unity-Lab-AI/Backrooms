# -*- coding: utf-8 -*-
"""Doors to nowhere: an opening in a wall that nothing is behind.

Owner, verbatim: *"odd contructions of doors walls corners deadends doors to now where not just
doors on 4 cosides of nothing but square rooms"*.

`DoorOpening` was literally that complaint written as code:

    foreach (int index in room.links)
        if (other is east  && cell.x == maxX && cell.z == CenterCell.z) return true;
        if (other is west  && cell.x == minX && cell.z == CenterCell.z) return true;
        ... north, south

**An opening exists only at the midpoint of a wall that faces a room this one is linked to.** Four
walls, four possible doors, each dead centre. Every room in the place was a box with up to four
doors in the middle of its sides, and the owner could see it.

So a wall with **no** link behind it may now open anyway -- offset from the centre, onto solid
rock. A one-cell alcove with a doorway and nothing past it.

**It cannot disconnect anything**, which is why it is safe to add here rather than somewhere that
needs its own proof: the cell it opens is on the room's own perimeter and the cell beyond is
rock, so it adds a dead end and removes no route. `CandidateIsSafe` and the generator both call
this one function, so the wall the validator proved and the wall that gets built are the same
wall -- the rule this file already lives by.

**Never on the threshold hall.** That is where a player arrives, and it is the one room that is
meant to read as built. The maze starts after it, which is the owner's own shape for the level.

Seeded from the room and the wall, so a coordinate is the same place on every visit.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")

OLD = u'''        internal static bool DoorOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                if (other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.maxX < room.Bounds.minX && cell.x == room.Bounds.minX && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.minZ > room.Bounds.maxZ && cell.z == room.Bounds.maxZ && cell.x == room.Bounds.CenterCell.x) { return true; }
                if (other.Bounds.maxZ < room.Bounds.minZ && cell.z == room.Bounds.minZ && cell.x == room.Bounds.CenterCell.x) { return true; }
            }
            return false;
        }'''

NEW = u'''        internal static bool DoorOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                if (other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.maxX < room.Bounds.minX && cell.x == room.Bounds.minX && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.minZ > room.Bounds.maxZ && cell.z == room.Bounds.maxZ && cell.x == room.Bounds.CenterCell.x) { return true; }
                if (other.Bounds.maxZ < room.Bounds.minZ && cell.z == room.Bounds.minZ && cell.x == room.Bounds.CenterCell.x) { return true; }
            }
            return FalseOpening(room, rooms, cell);
        }

        /// <summary>One wall in this many with nothing behind it opens anyway.</summary>
        internal const int FalseOpeningRarity = 3;

        /// <summary>
        /// A doorway onto solid rock.
        ///
        /// Owner: *"odd contructions of doors walls corners deadends doors to now where not just
        /// doors on 4 cosides of nothing but square rooms"*. The rule above IS that complaint
        /// written as code -- an opening exists only at the midpoint of a wall facing a linked
        /// room, so every room was a box with up to four doors dead centre.
        ///
        /// **A wall with no link behind it may open anyway**, offset from the centre so it does
        /// not read as another corridor that failed to arrive. Beyond it is rock.
        ///
        /// ## Why this is safe to decide here
        ///
        /// It **adds a dead end and removes no route**. The cell is on the room's own perimeter
        /// and the cell past it is rock, so reachability is untouched -- which is the only thing
        /// `CandidateIsSafe` is proving. And both the validator and the generator reach it
        /// through `DoorOpening`, so the wall that is proved is the wall that is built. A second
        /// derivation of one rule is the defect that cost thirty-nine checkpoints.
        ///
        /// **Never on the threshold hall.** That is where a player arrives and the one room meant
        /// to read as built; the maze starts after it.
        ///
        /// Offset by a third of the wall rather than any cell, so it still looks like somebody
        /// put a door there, which is what makes it unsettling rather than merely broken.
        /// </summary>
        internal static bool FalseOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            if (room == null || room.index == 0) { return false; }
            CellRect bounds = room.Bounds;
            // Corners are structure, never openings.
            bool onEastWall = cell.x == bounds.maxX;
            bool onWestWall = cell.x == bounds.minX;
            bool onNorthWall = cell.z == bounds.maxZ;
            bool onSouthWall = cell.z == bounds.minZ;
            int walls = (onEastWall ? 1 : 0) + (onWestWall ? 1 : 0)
                + (onNorthWall ? 1 : 0) + (onSouthWall ? 1 : 0);
            if (walls != 1) { return false; }

            int side = onEastWall ? 0 : onWestWall ? 1 : onNorthWall ? 2 : 3;
            // A wall that already carries a real doorway is left alone: two openings in one wall
            // reads as a mistake rather than as a door that goes nowhere.
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                if (side == 0 && other.Bounds.minX > bounds.maxX) { return false; }
                if (side == 1 && other.Bounds.maxX < bounds.minX) { return false; }
                if (side == 2 && other.Bounds.minZ > bounds.maxZ) { return false; }
                if (side == 3 && other.Bounds.maxZ < bounds.minZ) { return false; }
            }

            int roll = DestinationService.StableHash(room.index * 17 + side,
                (room.familyId ?? "") + ":falsedoor", side);
            if (roll < 0) { roll = ~roll; }
            if (roll % FalseOpeningRarity != 0) { return false; }

            // A third along the wall, not the middle: the middle is where a real door goes.
            bool horizontal = side >= 2;
            int low = horizontal ? bounds.minX : bounds.minZ;
            int high = horizontal ? bounds.maxX : bounds.maxZ;
            if (high - low < 4) { return false; }
            int at = low + (high - low) / 3;
            return horizontal ? cell.x == at : cell.z == at;
        }'''

text = io.open(PLANNER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("doors to nowhere, decided in the one place both readers ask")
