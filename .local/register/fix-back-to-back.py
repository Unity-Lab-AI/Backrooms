# -*- coding: utf-8 -*-
"""Back-to-back rooms: two rooms sharing a wall, with a door in it and no corridor between.

Owner, verbatim: *"and you can have back to back roomes"*.

Every room in a coordinate sits at the centre of its own slot with a ten-cell gap to its
neighbour, and every link between two rooms is a carved corridor. **Nothing ever touched
anything.** A level made entirely of islands joined by tubes reads as a diagram; rooms that share
a wall read as a building.

## The shape of the change

A **spur** -- a dead end hanging off the chain by a single link -- may be pushed against its host
until their walls meet. Spurs and not chain rooms, because a spur has exactly one connection, so
moving it can only affect the one pair and can never re-route the spine.

Three readers have to agree about it, and they all ask the same function:

  * `DoorOpening` puts the doorway in the shared wall. Its four tests require the other room to
    be strictly beyond this one's edge, which is false when the edges are equal -- so a touching
    pair would have been sealed, with no way in at all.
  * `BuildCorridors` skips the pair. Carving a corridor between the centres of two rooms that
    already touch would cut a five-cell hole through the shared wall and make them one room.
  * `CandidateIsSafe` proves the route through the shared doorway instead of through a corridor.

**`SharesWall` is the single place that decides it**, for the same reason `PillarCells` is the
single place the pillar lattice is decided: two readers deriving one rule independently is the
defect that stopped every coordinate generating for thirty-nine checkpoints.

Never the threshold hall, which keeps its corridors and its clean walls, and never at the hall's
own distance -- a back-to-back pair is a thing the maze does, not a thing the arrival does.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

planner = io.open(PLANNER, encoding="utf-8").read()

# ----------------------------------------------------------------- the shared predicate
PRED_ANCHOR = u"        internal static bool DoorOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)"
PRED = u'''        /// <summary>
        /// Whether these two rooms share a wall, so there is no corridor between them.
        ///
        /// Owner: *"and you can have back to back roomes"*. Every room used to sit at the centre
        /// of its own slot with a ten-cell gap to its neighbour and every link was a carved
        /// corridor, so nothing ever touched anything -- a level of islands joined by tubes.
        ///
        /// **THE SINGLE PLACE THIS IS DECIDED.** `DoorOpening` puts the doorway in the shared
        /// wall, `BuildCorridors` skips the pair, and `CandidateIsSafe` proves the route through
        /// the doorway rather than through a corridor. Three readers, one rule -- the same reason
        /// `PillarCells` exists, and the same defect avoided.
        ///
        /// Edges equal, overlap along the shared axis, so a pair that merely passes close does
        /// not count.
        /// </summary>
        internal static bool SharesWall(RoomRecord first, RoomRecord second)
        {
            if (first == null || second == null) { return false; }
            CellRect a = first.Bounds;
            CellRect b = second.Bounds;
            bool verticalOverlap = a.minZ <= b.maxZ && b.minZ <= a.maxZ;
            bool horizontalOverlap = a.minX <= b.maxX && b.minX <= a.maxX;
            if ((a.maxX == b.minX || b.maxX == a.minX) && verticalOverlap) { return true; }
            if ((a.maxZ == b.minZ || b.maxZ == a.minZ) && horizontalOverlap) { return true; }
            return false;
        }

''' + PRED_ANCHOR

if planner.count(PRED_ANCHOR) != 1:
    print("PRED ANCHOR PROBLEM: %d" % planner.count(PRED_ANCHOR))
    raise SystemExit(1)
planner = planner.replace(PRED_ANCHOR, PRED, 1)

# ------------------------------------------------------- the doorway in the shared wall
DOOR_OLD = u'''            return FalseOpening(room, rooms, cell);'''
DOOR_NEW = u'''            // **A SHARED WALL NEEDS A DOORWAY TOO.** The four tests above all require the other
            // room to be strictly beyond this one's edge, which is false when the edges are
            // equal -- so a back-to-back pair would be sealed, with no way in at all.
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                if (!SharesWall(room, other)) { continue; }
                if (other.Bounds.minX == room.Bounds.maxX && cell.x == room.Bounds.maxX
                    && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.maxX == room.Bounds.minX && cell.x == room.Bounds.minX
                    && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.minZ == room.Bounds.maxZ && cell.z == room.Bounds.maxZ
                    && cell.x == room.Bounds.CenterCell.x) { return true; }
                if (other.Bounds.maxZ == room.Bounds.minZ && cell.z == room.Bounds.minZ
                    && cell.x == room.Bounds.CenterCell.x) { return true; }
            }
            return FalseOpening(room, rooms, cell);'''
if planner.count(DOOR_OLD) != 1:
    print("DOOR ANCHOR PROBLEM: %d" % planner.count(DOOR_OLD))
    raise SystemExit(1)
planner = planner.replace(DOOR_OLD, DOOR_NEW, 1)

# ------------------------------------------------- the validator routes through the wall
SAFE_OLD = u'''                    int reach = CorridorHalfWidthBetween(room, other,'''
SAFE_NEW = u'''                    // A back-to-back pair has no corridor to model: the doorway in the
                    // shared wall is the route, and the floor grid already carries it.
                    if (SharesWall(room, other)) { continue; }
                    int reach = CorridorHalfWidthBetween(room, other,'''
if planner.count(SAFE_OLD) != 1:
    print("SAFE ANCHOR PROBLEM: %d" % planner.count(SAFE_OLD))
    raise SystemExit(1)
planner = planner.replace(SAFE_OLD, SAFE_NEW, 1)

# ------------------------------------------------------------- push the spur against its host
SPUR_OLD = u'''                    taken.Add(slot);
                    string family = SpurFamilies[rooms.Count % SpurFamilies.Length];
                    rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,
                        VariedRoomSpan(spacing, slot, seed, depth), seed, false, depth));
                    Link(rooms, rooms.Count - 1, host);'''
SPUR_NEW = u'''                    taken.Add(slot);
                    string family = SpurFamilies[rooms.Count % SpurFamilies.Length];
                    rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,
                        VariedRoomSpan(spacing, slot, seed, depth), seed, false, depth));
                    Link(rooms, rooms.Count - 1, host);
                    // **BACK TO BACK.** Owner: *"and you can have back to back roomes"*. A spur
                    // has exactly one connection, so pushing it against its host can only affect
                    // that one pair and can never re-route the spine -- which is why this is done
                    // to spurs and not to chain rooms.
                    if (host > 0 && DestinationService.StableHash(seed,
                        "backtoback:" + slot.x + "," + slot.z, depth) % 3 == 0)
                    { PushAgainst(rooms[rooms.Count - 1], rooms[host]); }'''
if planner.count(SPUR_OLD) != 1:
    print("SPUR ANCHOR PROBLEM: %d" % planner.count(SPUR_OLD))
    raise SystemExit(1)
planner = planner.replace(SPUR_OLD, SPUR_NEW, 1)

PUSH_ANCHOR = u"        internal static bool SharesWall(RoomRecord first, RoomRecord second)"
PUSH = u'''        /// <summary>
        /// Slide this room until its wall meets the other's, along whichever axis they are
        /// already separated on.
        ///
        /// Only moved, never resized, so every property the planner already proved about the
        /// room -- its span is even, its doorways sit at its wall midpoints, its pillar lattice
        /// clears the centre cross -- survives the move untouched.
        ///
        /// Refuses a diagonal pair, because two rooms offset on both axes have no wall to share.
        /// </summary>
        private static void PushAgainst(RoomRecord mover, RoomRecord anchorRoom)
        {
            if (mover == null || anchorRoom == null) { return; }
            CellRect a = mover.Bounds;
            CellRect b = anchorRoom.Bounds;
            bool verticalOverlap = a.minZ <= b.maxZ && b.minZ <= a.maxZ;
            bool horizontalOverlap = a.minX <= b.maxX && b.minX <= a.maxX;
            if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX; return; }
            if (verticalOverlap && a.maxX < b.minX) { mover.x = b.minX - a.Width; return; }
            if (horizontalOverlap && a.minZ > b.maxZ) { mover.z = b.maxZ; return; }
            if (horizontalOverlap && a.maxZ < b.minZ) { mover.z = b.minZ - a.Height; return; }
        }

''' + PUSH_ANCHOR
planner = planner.replace(PUSH_ANCHOR, PUSH, 1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(planner)
print("planner: SharesWall, the shared doorway, the validator skip, and the push")

# --------------------------------------------------------- the generator skips the corridor
gen = io.open(GEN, encoding="utf-8").read()
GEN_OLD = u'''                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);'''
GEN_NEW = u'''                    RoomRecord other = rooms.First(candidate => candidate.Index == linkedIndex);
                    // A back-to-back pair is joined by the doorway in the wall they share.
                    // Carving between their centres would cut a five-cell hole through that wall
                    // and make them one room. The SAME predicate CandidateIsSafe used.
                    if (RoomLayoutPlanner.SharesWall(room, other)) { continue; }'''
if gen.count(GEN_OLD) != 1:
    print("GEN ANCHOR PROBLEM: %d" % gen.count(GEN_OLD))
    raise SystemExit(1)
io.open(GEN, "w", encoding="utf-8", newline="").write(gen.replace(GEN_OLD, GEN_NEW, 1))
print("generator: no corridor where a wall is shared")
