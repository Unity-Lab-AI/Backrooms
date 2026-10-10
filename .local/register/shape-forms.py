# -*- coding: utf-8 -*-
"""Seven room forms instead of one rounded square.

Owner: *"they were all just square rooms again..wtf dont u know any other compbinations"*, and
earlier *"triangle, octangones, rombones, all the geomentry and mixetrues"*.

**The probe says the shaping was running the whole time**: 89% of depth-1 rooms carried rock and
it was 7% of their interior. So the amount was never the problem and increasing the reach -- which
was the obvious guess -- would only have produced rounder squares. **There was exactly one form**:
a quarter-ellipse nibbled out of each corner. A room with four rounded corners reads as a square
room, and the owner looked at twenty-eight of them.

So the vocabulary grows instead. Seven forms, chosen per room from its own seed:

  0  CORNERS     the quarter-ellipses, which do give trapezoid / rhombus / octagon by mask
  1  ELL         one whole quadrant is rock
  2  TEE         two quadrants on one side, so the room is a T or a U
  3  CROSS       all four quadrants, leaving the route cross and the perimeter walk: a plus
  4  WEDGE       a diagonal triangle in one quadrant, which is an actual triangle
  5  PARTITION   a stub wall in from one side, stopping short of the cross: narrows and an alcove
  6  BAYS        alternating blocks along one wall, which reads as a row of alcoves

**The two invariants that make every one of them safe are unchanged**, and they are the reason
this can be generous: rock lives only inside the inset-2 interior, so the one-cell ring just
inside the perimeter is always a complete walkable loop around the room; and the centre cross is
inviolable, so the walk from any doorway to any other is always clear. Any pattern obeying those
two cannot disconnect anything -- which is why `CandidateIsSafe` can keep proving walkability
against the same function without knowing which form was drawn.

The hall is excluded. It is the one room meant to read as built -- the same reason `FalseOpening`
excludes it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation", "RoomLayoutPlanner.cs")

OLD_START = u"        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)"
OLD_END = u"""        /// <summary>
        /// Half the width of the corridor between two rooms, so hallways are not all one size."""

NEW = u'''        /// <summary>How many distinct forms a room can take.</summary>
        internal const int ShapeForms = 7;

        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)
        {
            // **Never the grand hall.** It is the room the player arrives in and the one meant to
            // read as built, which is the same reason `FalseOpening` leaves it alone.
            if (room == null || room.index == 0 || depth <= 1) { yield break; }
            CellRect bounds = room.Bounds;
            // The interior only. The perimeter is wall and the ring inside it is the walkway that
            // keeps every doorway reachable -- **and that ring is why every form below is safe**:
            // it is a complete loop around the room whatever the middle does.
            int insetX = bounds.minX + 2;
            int insetZ = bounds.minZ + 2;
            int extentX = bounds.maxX - 2;
            int extentZ = bounds.maxZ - 2;
            if (extentX - insetX < 4 || extentZ - insetZ < 4) { yield break; }

            IntVec3 center = bounds.CenterCell;
            int roll = DestinationService.StableHash(room.index * 31 + depth,
                (room.familyId ?? "") + ":shape", depth);
            if (roll < 0) { roll = ~roll; }

            // How far a mass reaches in, growing with depth and never past the centre cross.
            int reach = System.Math.Min((depth - 1) * 2,
                System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);
            if (reach < 1) { yield break; }

            // The quadrants, which stop one clear cell short of the cross on both axes. A form
            // that fills whole quadrants therefore cannot touch the cross, so it needs no
            // per-cell check of its own.
            int westTo = center.x - 2;
            int eastFrom = center.x + 2;
            int southTo = center.z - 2;
            int northFrom = center.z + 2;
            bool roomy = westTo - insetX >= 3 && extentX - eastFrom >= 3
                && southTo - insetZ >= 3 && extentZ - northFrom >= 3;

            // A plain room is a form too. Owner: *"all the geomentry and mixetrues"* -- a floor
            // where every room is deranged is as uniform as one where none is.
            int form = roll % ShapeForms;
            if (!roomy && form != 0) { form = 0; }

            bool east = (roll / 7) % 2 == 0;
            bool north = (roll / 11) % 2 == 0;

            if (form == 1 || form == 2 || form == 3)
            {
                // ELL: one quadrant. TEE: two on one side. CROSS: all four.
                for (int quadrant = 0; quadrant < 4; quadrant++)
                {
                    bool quadrantEast = quadrant == 1 || quadrant == 2;
                    bool quadrantNorth = quadrant >= 2;
                    if (form == 1 && (quadrantEast != east || quadrantNorth != north)) { continue; }
                    if (form == 2 && quadrantNorth != north) { continue; }
                    int fromX = quadrantEast ? eastFrom : insetX;
                    int toX = quadrantEast ? extentX : westTo;
                    int fromZ = quadrantNorth ? northFrom : insetZ;
                    int toZ = quadrantNorth ? extentZ : southTo;
                    for (int x = fromX; x <= toX; x++)
                    {
                        for (int z = fromZ; z <= toZ; z++) { yield return new IntVec3(x, 0, z); }
                    }
                }
                yield break;
            }

            if (form == 4)
            {
                // WEDGE: a right triangle in one quadrant, hypotenuse facing the middle. The
                // owner asked for triangles; this is one.
                int fromX = east ? eastFrom : insetX;
                int toX = east ? extentX : westTo;
                int fromZ = north ? northFrom : insetZ;
                int toZ = north ? extentZ : southTo;
                int width = toX - fromX;
                int height = toZ - fromZ;
                for (int dx = 0; dx <= width; dx++)
                {
                    for (int dz = 0; dz <= height; dz++)
                    {
                        // Measured from the corner of the room, so the solid part is the corner
                        // and the diagonal face looks into the room.
                        if (dx * height + dz * width > width * height) { continue; }
                        int x = east ? extentX - dx : insetX + dx;
                        int z = north ? extentZ - dz : insetZ + dz;
                        yield return new IntVec3(x, 0, z);
                    }
                }
                yield break;
            }

            if (form == 5)
            {
                // PARTITION: a stub wall in from one side, stopping two clear cells short of the
                // cross. Narrows and a dead-end alcove inside a single room.
                bool alongX = (roll / 13) % 2 == 0;
                int thickness = reach > 2 ? 2 : 1;
                if (alongX)
                {
                    int at = north ? northFrom + (extentZ - northFrom) / 2
                        : insetZ + (southTo - insetZ) / 2;
                    int fromX = east ? eastFrom : insetX;
                    int toX = east ? extentX : westTo;
                    for (int z = at; z < at + thickness && z <= extentZ; z++)
                    {
                        for (int x = fromX; x <= toX; x++) { yield return new IntVec3(x, 0, z); }
                    }
                }
                else
                {
                    int at = east ? eastFrom + (extentX - eastFrom) / 2
                        : insetX + (westTo - insetX) / 2;
                    int fromZ = north ? northFrom : insetZ;
                    int toZ = north ? extentZ : southTo;
                    for (int x = at; x < at + thickness && x <= extentX; x++)
                    {
                        for (int z = fromZ; z <= toZ; z++) { yield return new IntVec3(x, 0, z); }
                    }
                }
                yield break;
            }

            if (form == 6)
            {
                // BAYS: alternating blocks along one wall, which reads as a row of alcoves rather
                // than as damage.
                bool alongX = (roll / 17) % 2 == 0;
                int period = reach + 2;
                if (alongX)
                {
                    int fromZ = north ? northFrom : insetZ;
                    int toZ = System.Math.Min(north ? extentZ : southTo, fromZ + reach - 1);
                    for (int x = insetX; x <= extentX; x++)
                    {
                        if (x == center.x || (x - insetX) % period >= period / 2) { continue; }
                        for (int z = fromZ; z <= toZ; z++)
                        {
                            if (z == center.z) { continue; }
                            yield return new IntVec3(x, 0, z);
                        }
                    }
                }
                else
                {
                    int fromX = east ? eastFrom : insetX;
                    int toX = System.Math.Min(east ? extentX : westTo, fromX + reach - 1);
                    for (int z = insetZ; z <= extentZ; z++)
                    {
                        if (z == center.z || (z - insetZ) % period >= period / 2) { continue; }
                        for (int x = fromX; x <= toX; x++)
                        {
                            if (x == center.x) { continue; }
                            yield return new IntVec3(x, 0, z);
                        }
                    }
                }
                yield break;
            }

            // CORNERS, the original form, and still a good one: which corners are filled decides
            // between a trapezoid, a rhombus and an octagon.
            int corners = 1 + roll % 15;
            for (int index = 0; index < 4; index++)
            {
                if ((corners & (1 << index)) == 0) { continue; }
                bool cornerEast = index == 1 || index == 2;
                bool cornerNorth = index >= 2;
                // Each corner mass is a quarter-ellipse, so the edge it presents to the room is
                // curved rather than another right angle.
                for (int dx = 0; dx < reach; dx++)
                {
                    for (int dz = 0; dz < reach; dz++)
                    {
                        if (dx * dx + dz * dz > reach * reach) { continue; }
                        int x = cornerEast ? extentX - dx : insetX + dx;
                        int z = cornerNorth ? extentZ - dz : insetZ + dz;
                        // The centre cross is inviolable: it is what guarantees every doorway
                        // reaches every other doorway whatever shape the corners take.
                        if (x == center.x || z == center.z) { continue; }
                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }
                        if (z <= bounds.minZ + 1 || z >= bounds.maxZ - 1) { continue; }
                        yield return new IntVec3(x, 0, z);
                    }
                }
            }
        }

'''

text = io.open(PLANNER, encoding="utf-8").read()
start = text.index(OLD_START)
end = text.index(OLD_END)
old = text[start:end]
if u"int corners = 1 + roll % 15;" not in old:
    print("REPLACED REGION LOOKS WRONG: %r" % old[:120])
    raise SystemExit(1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(text[:start] + NEW + text[end:])
print("seven forms written, replacing %d lines" % old.count("\n"))
