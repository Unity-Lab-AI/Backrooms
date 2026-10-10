# -*- coding: utf-8 -*-
"""The grand yellow hall is the SPAWN ROOM, and everything past it is maze.

Two owner directions looked like they contradicted each other, and the proof caught it:

    earlier: *"making the 0 level rooms be grand large spaces and leas than 60-100 romms"*
    now:     *"not enough rooms"*, *"it needs to be more maze liek and scary inducing"*

**The owner resolved it themselves in the same message**, and the proof failing is what made me
go back and read it properly:

    *"lets try and fix this so the normal yellow backrooms look isnt the whole floor but the main
     spanw room and going deeping in can mean the numner of branch hallways and rooms distancing
     from the main portal spawn in the back rooms continuw on into the map"*

So it was never *every room is grand*. It is **the main spawn room is grand and yellow, and the
maze starts the moment you leave it.** Grand rooms everywhere is what produced a nine-room
warehouse; small rooms everywhere would lose the arrival.

THE THRESHOLD ROOM NOW TAKES TWO SLOTS. At depth 1 that is roughly **eighty cells across** -- the
same grand span the whole level used to have -- while every other room is about thirty-four and
the grid is six slots per axis instead of three.

**Two slots, not four, and that is deliberate.** The chain is a serpentine precisely so
consecutive rooms are always grid neighbours and connecting them needs no pathfinding. Consuming
the first two entries keeps that true: the next chain room is a neighbour of the second slot, and
the hall's bounds already contain that slot's centre, so the corridor meets it exactly as it
would have. A 2x2 hall would have broken the adjacency the whole layout rests on.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")

OLD = u'''            var rooms = new List<RoomRecord>();
            var taken = new HashSet<IntVec2>();
            for (int index = 0; index < chainLength; index++)
            {
                IntVec2 slot = order[index];
                taken.Add(slot);
                string family = ChainFamilyFor(index, chainLength, seed);
                rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,
                    VariedRoomSpan(spacing, slot, seed, depth), seed, fallback, depth));
            }
            for (int index = 1; index < chainLength; index++) { Link(rooms, index - 1, index); }'''

NEW = u'''            var rooms = new List<RoomRecord>();
            var taken = new HashSet<IntVec2>();

            // **THE GRAND HALL YOU ARRIVE IN, AND THEN THE MAZE.** Owner: *"the normal yellow
            // backrooms look isnt the whole floor but the main spanw room"*. The threshold takes
            // the first TWO slots, so at depth 1 it is about eighty cells across -- the span the
            // entire level used to have -- while everything past it is a third of that.
            //
            // Two and not four: the chain is a serpentine so consecutive rooms are always grid
            // neighbours and linking needs no pathfinding. Consuming two keeps that true, because
            // the next room neighbours the second slot and the hall already contains that slot's
            // centre. A 2x2 hall breaks the adjacency the whole layout rests on.
            int consumed = 0;
            if (!fallback && order.Count >= 2)
            {
                rooms.Add(MakeHall(coordinate, order[0], order[1], spacing, seed, depth));
                taken.Add(order[0]);
                taken.Add(order[1]);
                consumed = 2;
            }

            for (int index = consumed; index < order.Count && rooms.Count < chainLength; index++)
            {
                IntVec2 slot = order[index];
                if (taken.Contains(slot)) { continue; }
                taken.Add(slot);
                string family = ChainFamilyFor(rooms.Count, chainLength, seed);
                rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,
                    VariedRoomSpan(spacing, slot, seed, depth), seed, fallback, depth));
            }
            int chainRooms = rooms.Count;
            for (int index = 1; index < chainRooms; index++) { Link(rooms, index - 1, index); }'''

text = io.open(PLANNER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("CHAIN ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)

# The spur pass measured against `chainLength`; it has to measure against what was built.
SPUR_OLD = u"                    int host = ChainNeighbourOf(rooms, chainLength, slot, slots, spacing);"
SPUR_NEW = u"                    int host = ChainNeighbourOf(rooms, chainRooms, slot, slots, spacing);"
if text.count(SPUR_OLD) != 1:
    print("SPUR ANCHOR PROBLEM: %d" % text.count(SPUR_OLD))
    raise SystemExit(1)
text = text.replace(SPUR_OLD, SPUR_NEW, 1)

# The hall itself, beside MakeRoom so the two are read together.
HALL_ANCHOR = u"        private static RoomRecord MakeRoom(CoordinateRecord coordinate, int index, string family,"
HALL = u'''        /// <summary>
        /// The room you arrive in: one grand space across two slots, and the only one.
        ///
        /// Owner: *"the normal yellow backrooms look isnt the whole floor but the main spanw
        /// room"*, and earlier *"making the 0 level rooms be grand large spaces"*. Both are true
        /// of this room and neither is true of the rest of the level.
        ///
        /// Centred between the two slot centres and spanning both, so the corridor from the next
        /// chain room meets it exactly where it would have met a one-slot room -- the second
        /// slot's centre is inside these bounds.
        ///
        /// No `Derange`, no span variation: this is the one room that is meant to read as built,
        /// so that everything beyond it reads as not.
        /// </summary>
        private static RoomRecord MakeHall(CoordinateRecord coordinate, IntVec2 first,
            IntVec2 second, int spacing, int seed, int depth)
        {
            int centerX = (SlotCenter(first.x, spacing) + SlotCenter(second.x, spacing)) / 2;
            int centerZ = (SlotCenter(first.z, spacing) + SlotCenter(second.z, spacing)) / 2;
            bool horizontal = first.z == second.z;
            int longSpan = Even(spacing * 2 - SlotGap, spacing * 2);
            int shortSpan = Even(SlotRoomSpan(spacing), spacing);
            return new RoomRecord
            {
                Index = 0,
                Family = UniqueFamilies[0],
                Bounds = CellRect.CenteredOn(new IntVec3(centerX, 0, centerZ),
                    (horizontal ? longSpan : shortSpan) / 2,
                    (horizontal ? shortSpan : longSpan) / 2),
                Links = new List<int>(),
            };
        }

        private static RoomRecord MakeRoom(CoordinateRecord coordinate, int index, string family,'''

if text.count(HALL_ANCHOR) != 1:
    print("HALL ANCHOR PROBLEM: %d" % text.count(HALL_ANCHOR))
    raise SystemExit(1)
text = text.replace(HALL_ANCHOR, HALL, 1)

io.open(PLANNER, "w", encoding="utf-8", newline="").write(text)
print("the threshold is a two-slot hall; the rest is maze")
