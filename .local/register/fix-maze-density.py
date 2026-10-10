# -*- coding: utf-8 -*-
"""Nine rooms is not a Backrooms level. More rooms, more branches, varied sizes.

Owner, after walking the first level that ever generated: *"not enough rooms"*, *"it needs to be
more maze liek and scary inducing beyond the main starting themed opening room"*, *"going deeping
in can mean the numner of branch hallways and rooms distancing from the main portal spawn in the
back rooms continuw on into the map"*.

MEASURED, NOT GUESSED. The minimap of the live level shows **nine rectangular rooms on straight
corridors**, and the planner says exactly why:

    slots      = MinSlotsPerAxis + (depth - 1)   ->  3 at depth 1
    grid       = 3 x 3                           ->  9 slots
    chain      = order.Count * 2 / 3             ->  6 rooms
    spurs      = of the remaining 3, one in three taken

**Nine rooms on a 300x300 map**, each one 80 cells across. That is a warehouse, not a maze.

THREE CHANGES, AND THE THIRD IS THE ONE THAT MAKES IT READ AS A MAZE:

  1. **The grid starts dense.** `MinSlotsPerAxis` 3 -> 6 and `MaxSlotsPerAxis` 8 -> 10, so depth 1
     is a **6x6 grid of thirty-six slots** and the deepest is ten per axis. Rooms shrink from 80
     cells across to about 34 at depth 1 and 16 at the bottom -- **so going deeper is more rooms,
     smaller, tighter**, which is the owner's *"the numner of branch hallways and rooms distancing
     from the main portal spawn"*.

  2. **Most of the leftover slots become rooms.** One slot in three became a spur; it is now three
     in four. The chain is twenty-four rooms at depth 1 and the spurs add most of the remaining
     twelve, so a first level is **well over thirty rooms** rather than nine, and `MaxRooms` 60
     still holds the owner's *"leas than 60-100 romms"*.

  3. **Rooms are no longer all one size.** Every room's span is drawn from its own slot, varying
     either side of the default, so two neighbours are rarely the same shape. A grid of identical
     boxes reads as a grid however many you add; **unequal boxes read as rooms.**

The variation is seeded per slot, so a coordinate is still the same place every time it is
visited -- which the whole record system depends on.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomLayoutPlanner.cs")

EDITS = [
    # 1. A dense grid from the first level.
    (u"        internal const int MinSlotsPerAxis = 3;",
     u"""        /// <summary>
        /// Slots per axis at depth 1, and **the number that made the first walked level feel
        /// like a warehouse.**
        ///
        /// At 3 this was a nine-slot grid on a 300x300 map and rooms came out eighty cells
        /// across; the owner walked it and said *"not enough rooms"*. At 6 the first level is a
        /// thirty-six-slot grid with rooms about thirty-four across, and the deepest levels reach
        /// <see cref="MaxSlotsPerAxis"/> -- so **deeper is more rooms, smaller and tighter**,
        /// which is what *"the numner of branch hallways and rooms distancing from the main
        /// portal spawn"* describes.
        /// </summary>
        internal const int MinSlotsPerAxis = 6;"""),

    (u"        internal const int MaxSlotsPerAxis = 8;",
     u"        internal const int MaxSlotsPerAxis = 10;"),

    # 2. Most leftover slots become branches.
    (u'''                    if (DestinationService.StableHash(seed, "spur:" + slot.x + "," + slot.z, depth) % 3 != 0)
                    { continue; }''',
     u'''                    // THREE IN FOUR, not one in three. Owner: *"it needs to be more maze liek"*.
                    // A chain with a handful of dead ends is a corridor with alcoves; a chain with
                    // a branch off most slots is something you can get lost in. The quarter that
                    // stays rock is what keeps it a maze rather than an open floor.
                    if (DestinationService.StableHash(seed, "spur:" + slot.x + "," + slot.z, depth) % 4 == 3)
                    { continue; }'''),
]

text = io.open(PLANNER, encoding="utf-8").read()
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

# 3. Per-slot size variation, through the one place a room's span is decided.
SPAN_OLD = u'''        /// <summary>The default span of a room in a slot of this size, always even.</summary>
        internal static int SlotRoomSpan(int spacing)
        {
            int span = spacing - SlotGap;
            if (span % 2 != 0) { span--; }
            return span < 8 ? 8 : span;
        }'''

SPAN_NEW = u'''        /// <summary>The default span of a room in a slot of this size, always even.</summary>
        internal static int SlotRoomSpan(int spacing)
        {
            int span = spacing - SlotGap;
            if (span % 2 != 0) { span--; }
            return span < 8 ? 8 : span;
        }

        /// <summary>How far either side of the default a room's span may vary, in cells.</summary>
        internal const int SpanVariation = 6;

        /// <summary>
        /// This room's span, varied from the default by its own slot.
        ///
        /// Owner: *"it needs to be more maze liek"*. **A grid of identical boxes reads as a grid
        /// however many boxes you add.** Unequal ones read as rooms, and the gap between a small
        /// room and its slot becomes more rock, which is more wall to walk around.
        ///
        /// Seeded from the slot, so a coordinate is the same place every time it is visited --
        /// the record system, the revisit check and every saved route depend on that.
        ///
        /// Always even, because the door placement puts a doorway at the midpoint of each side,
        /// and never below eight, because a room has to hold a doorway on each wall and a walk
        /// between them.
        /// </summary>
        internal static int VariedRoomSpan(int spacing, IntVec2 slot, int seed, int depth)
        {
            int baseline = SlotRoomSpan(spacing);
            int reach = SpanVariation < baseline / 3 ? SpanVariation : baseline / 3;
            if (reach < 1) { return baseline; }
            int offset = DestinationService.StableHash(seed, "span:" + slot.x + "," + slot.z, depth)
                % (reach * 2 + 1) - reach;
            int span = baseline + offset;
            if (span % 2 != 0) { span--; }
            return span < 8 ? 8 : span;
        }'''

if text.count(SPAN_OLD) != 1:
    print("SPAN ANCHOR PROBLEM: %d" % text.count(SPAN_OLD))
    raise SystemExit(1)
text = text.replace(SPAN_OLD, SPAN_NEW, 1)

# And both room-making call sites use it.
for old, new in (
        (u'rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing, span, seed, fallback, depth));',
         u'rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,\n'
         u'                    VariedRoomSpan(spacing, slot, seed, depth), seed, fallback, depth));'),
        (u'rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing, span, seed, false, depth));',
         u'rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,\n'
         u'                        VariedRoomSpan(spacing, slot, seed, depth), seed, false, depth));')):
    if text.count(old) != 1:
        print("CALL ANCHOR PROBLEM: %d of %r" % (text.count(old), old[:60]))
        raise SystemExit(1)
    text = text.replace(old, new, 1)

io.open(PLANNER, "w", encoding="utf-8", newline="").write(text)
print("denser grid, three-in-four branches, per-slot room sizes")
