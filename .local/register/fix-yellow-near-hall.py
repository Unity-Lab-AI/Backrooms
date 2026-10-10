# -*- coding: utf-8 -*-
"""The yellow look is the hall and what surrounds it, not the whole floor.

Owner, verbatim: *"lets try and fix this so the normal yellow backrooms look isnt the whole floor
but the main spanw room"*, and *"cant have a whole backrooms be nothing but what it currently is
... it needs to be more maze liek and scary inducing beyond the main starting themed opening
room"*.

**`StuffFor` decides on the coordinate's own depth**, so at depth 1 -- `CoherentDepth` -- every
wall and every fixture on the entire level is drawn from one narrow shared palette. That is the
yellow look, and it is correct for the room you arrive in and wrong for the far side of a maze.

So the wall material asks the same question the dressing and the inhabitants now ask: **how far
from the spawn hall is this room?** Near it, the coherent palette, exactly as now. Further out,
the wild per-item draw that used to need a second level to reach.

**This does not overrule the earlier direction, it locates it.** Owner, 0.12.52-dev: *"but depth
0 in the backrroms is the standard yellow style"* -- and that is still true where a player
arrives and for the rooms around it. What changed is that it stopped being true of rooms twelve
doors away, which the owner has now walked and called *"nothing but what it currently is"*.

Only the WALLS take the room-aware route here. A fixture's material is drawn per item from the
same palette logic and already varies; the walls are what make a corridor read as the same
corridor for three hundred cells.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MATERIALS = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                         "CoordinateMaterials.cs")
GENSTEP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                       "GenStep_BackroomsDestination.cs")

MAT_ANCHOR = u"        internal static ThingDef StuffFor(ThingDef definition, CoordinateRecord coordinate, int variant)"

MAT_NEW = u'''        /// <summary>
        /// The same choice, but asked for a particular room rather than for the whole level.
        ///
        /// Owner: *"the normal yellow backrooms look isnt the whole floor but the main spanw
        /// room"*. `StuffFor` decides on the coordinate's depth, so at `CoherentDepth` every wall
        /// on a three-hundred-cell map comes from one narrow palette -- right for the hall you
        /// arrive in, wrong for the far side of a maze.
        ///
        /// **This locates the earlier direction rather than overruling it.** *"depth 0 in the
        /// backrroms is the standard yellow style"* still holds where a player arrives and for
        /// the rooms around it; it stopped holding twelve doors out, and that is what the owner
        /// walked.
        /// </summary>
        internal static ThingDef StuffForRoom(ThingDef definition, CoordinateRecord coordinate,
            RoomRecord room, int variant)
        {
            if (definition == null || !definition.MadeFromStuff) { return null; }
            int depth = coordinate == null ? 1 : coordinate.Depth;
            int effective = RoomArchetypeService.EffectiveDepth(coordinate, room, depth);
            if (effective > CoherentDepth)
            {
                ThingDef wild = WildStuffFor(definition, coordinate, variant);
                if (wild != null) { return wild; }
            }
            return StuffFor(definition, coordinate, variant);
        }

'''

text = io.open(MATERIALS, encoding="utf-8").read()
if text.count(MAT_ANCHOR) != 1:
    print("MATERIALS ANCHOR PROBLEM: %d" % text.count(MAT_ANCHOR))
    raise SystemExit(1)
text = text.replace(MAT_ANCHOR, MAT_NEW + MAT_ANCHOR, 1)
io.open(MATERIALS, "w", encoding="utf-8", newline="").write(text)
print("StuffForRoom added")

GEN_OLD = u"                    : (CoordinateMaterials.StuffFor(wallDef, coordinate, room.Index) ?? wallStuff);"
GEN_NEW = u"                    : (CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index) ?? wallStuff);"
gen = io.open(GENSTEP, encoding="utf-8").read()
if gen.count(GEN_OLD) != 1:
    print("GENSTEP ANCHOR PROBLEM: %d" % gen.count(GEN_OLD))
    raise SystemExit(1)
io.open(GENSTEP, "w", encoding="utf-8", newline="").write(gen.replace(GEN_OLD, GEN_NEW, 1))
print("walls ask per room, so the yellow stops at the hall")
