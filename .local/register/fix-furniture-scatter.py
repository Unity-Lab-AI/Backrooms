# -*- coding: utf-8 -*-
"""Furniture went to the four corners because the code aimed it at the four corners.

Owner, after walking the level: *"its currently really nice but the furnature is only in the four
corners of the rooms that nots very random"*.

**They were describing the code.** Both placement paths did this:

    int quadrant = (seed % 4 + slot) % 4;
    IntVec3 preferred = new IntVec3(quadrant % 2 == 0 ? room.x + 2 : room.Bounds.maxX - 2, 0,
        quadrant < 2 ? room.z + 2 : room.Bounds.maxZ - 2);

`preferred` is **one of exactly four cells** -- each corner inset by two -- and every candidate
cell is then sorted by distance to it. So the first free cell is always hard against a corner,
and with four slots cycling through four quadrants a room fills its corners and leaves the middle
empty. Not random; a pattern, and the owner could see it from the map.

Now the anchor is **any cell in the room**, drawn from the same seed and slot so it stays
deterministic -- a coordinate must be the same place on every visit. Rotation is drawn too, over
all four facings rather than alternating north and south, because a row of furniture all facing
the same way reads as placed by a planner.

**The fallback is unchanged and still exhaustive:** the sort only decides where the search
*starts*. Every cell in the room is still tried, so a cramped room places exactly what it placed
before -- this changes where things prefer to land, never whether they can.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILDER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "RoomContentBuilder.cs")

OLD = u'''            int quadrant = (seed % 4 + slot) % 4;
            IntVec3 preferred = new IntVec3(quadrant % 2 == 0 ? room.x + 2 : room.Bounds.maxX - 2, 0,
                quadrant < 2 ? room.z + 2 : room.Bounds.maxZ - 2);'''

NEW = u'''            IntVec3 preferred = ScatterAnchor(room, seed, slot);'''

text = io.open(BUILDER, encoding="utf-8").read()
if text.count(OLD) != 2:
    print("ANCHOR PROBLEM: %d (want 2)" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW)

# Rotation over all four facings, in both paths.
ROT_OLD = u"            Rot4 rotation = slot % 2 == 0 ? Rot4.North : Rot4.South;"
ROT_NEW = u'''            // All four facings, not two. A room where everything faces north or south reads
            // as arranged; the Backrooms are not arranged.
            Rot4 rotation = new Rot4(Scatter(seed, slot, "facing", 4));'''
rot_count = text.count(ROT_OLD)
if rot_count < 1:
    print("ROTATION ANCHOR PROBLEM: %d" % rot_count)
    raise SystemExit(1)
text = text.replace(ROT_OLD, ROT_NEW)

HELPER_ANCHOR = u"        private static Thing TryPlace(Map map, RoomRecord room, CoordinateRecord coordinate,"
HELPER = u'''        /// <summary>
        /// Where a fixture would like to stand: anywhere in the room, not a corner.
        ///
        /// Owner, after walking the first level: *"the furnature is only in the four corners of
        /// the rooms that nots very random"*. **They were reading the code off the screen.** The
        /// anchor used to be one of exactly four cells -- each corner inset by two -- and every
        /// candidate cell was sorted by distance to it, so four slots cycling four quadrants
        /// filled the corners and left the middle bare.
        ///
        /// Deterministic, because a coordinate has to be the same place on every visit: drawn
        /// from the same seed and slot the rest of the placement already uses.
        ///
        /// **This only moves where the search starts.** The caller still walks every cell in the
        /// room, so a cramped room places exactly what it placed before.
        /// </summary>
        private static IntVec3 ScatterAnchor(RoomRecord room, int seed, int slot)
        {
            CellRect inner = room.Bounds.ContractedBy(2);
            if (inner.Width < 1 || inner.Height < 1) { inner = room.Bounds.ContractedBy(1); }
            if (inner.Width < 1 || inner.Height < 1) { return room.Bounds.CenterCell; }
            return new IntVec3(inner.minX + Scatter(seed, slot, "x", inner.Width), 0,
                inner.minZ + Scatter(seed, slot, "z", inner.Height));
        }

        /// <summary>A stable non-negative draw below <paramref name="bound"/>.</summary>
        private static int Scatter(int seed, int slot, string key, int bound)
        {
            if (bound < 1) { return 0; }
            int derived = Company.CampaignSeed.Derive(seed, key + ":" + slot, 1);
            if (derived < 0) { derived = -derived; }
            return derived % bound;
        }

        private static Thing TryPlace(Map map, RoomRecord room, CoordinateRecord coordinate,'''

if text.count(HELPER_ANCHOR) != 1:
    print("HELPER ANCHOR PROBLEM: %d" % text.count(HELPER_ANCHOR))
    raise SystemExit(1)
text = text.replace(HELPER_ANCHOR, HELPER, 1)

io.open(BUILDER, "w", encoding="utf-8", newline="").write(text)
print("furniture scatters through the room, and faces any way")
