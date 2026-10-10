# -*- coding: utf-8 -*-
"""Stage six: the wild variation of materials, deeper in.

Owner direction, verbatim: *"with the wild variatiosn of material typeds in all items equaipment
walls floors lights furnature and benches that are found everywher deeper in with wild random
events and layouts and spawns to find and loot!!!!!!"*

WHAT WAS ALREADY THERE, measured before writing anything:

  * `CoordinateMaterials` already derives a per-coordinate palette from the seed, sorted by
    defName so a mod list cannot change a coordinate's appearance, and drawn from
    `GenStuff.AllowedStuffsFor` so **any** stuffable material the profile adds widens it
    automatically. Nothing names a material. That part needed no work at all.
  * `RoomArchetypeService` already gates WHICH defs appear by depth -- `minDepth`, `maxDepth`, a
    tech ceiling and an anomalous weight factor. The variety of *things* already grows inward.

WHAT WAS MISSING, and all three are the same shape -- a material chosen somewhere the palette
could not reach:

  1. **The palette never grew.** `PaletteSize` was a flat 3 at every depth, so the deepest
     coordinate was fitted out in exactly as few materials as the shallowest. That is the whole
     of *"wild variatiosn ... deeper in"* and it was a constant.
  2. **The dressing path did not consult the palette at all.** `TryPlace` used
     `GenStuff.DefaultStuffFor`, and `TryPlace` is the path that places the depth-scaled
     archetype dressing -- so precisely the content the owner wants varied was the content
     taking Core's default.
  3. **Walls were one of two named defs.** `BackroomsPalette` sets `wallStuff` to `WoodLog` or
     `Steel` across five bands, which is a hard-coded pair where everything else is drawn from
     what the profile offers.

NOT CHANGED, deliberately: `ColonistEcho.CopyApparel`. It copies one of the player's OWN
colonists, so the source pawn's material is the right one, and `DefaultStuffFor` there is only a
fallback for a piece that had none. An echo should mirror the colonist, not the coordinate.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")


def edit(path, pairs):
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in pairs:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:64]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in pairs:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("%s: %d edit(s)" % (os.path.basename(path), len(pairs)))


# ------------------------------------------------------------------ 1. the palette grows inward
edit(os.path.join(SRC, "Generation", "CoordinateMaterials.cs"), [
    ("""        /// <summary>
        /// How many materials one coordinate may be fitted out in. Three, so a coordinate has a
        /// character and a fixture that cannot take the first choice still has somewhere to go.
        /// </summary>
        private const int PaletteSize = 3;

        /// <summary>Bumped when the derivation changes, so a palette cannot silently shift.</summary>
        private const int MaterialVersion = 1;""",
     """        /// <summary>
        /// How many materials the **shallowest** coordinate is fitted out in.
        ///
        /// Two, and deliberately fewer than the three this used to be at every depth. The yellow
        /// rooms read as a place because they are monotonous, which is the same reason `Derange`
        /// and `RockIntrusionCells` leave depth 1 alone. A coordinate needs at least two, so a
        /// fixture that cannot take the first choice still has somewhere to go.
        /// </summary>
        private const int ShallowPaletteSize = 2;

        /// <summary>
        /// The most materials any coordinate is fitted out in.
        ///
        /// **Owner direction, 2026-09-30, verbatim:** *"with the wild variatiosn of material
        /// typeds in all items equaipment walls floors lights furnature and benches that are
        /// found everywher deeper in"*.
        ///
        /// Six rather than unbounded because a palette is walked in order and the first entry a
        /// fixture can take wins — past six the later entries are chosen for almost nothing, so
        /// the number would grow without the place looking any wilder.
        /// </summary>
        private const int DeepPaletteSize = 6;

        /// <summary>
        /// How many materials this depth is fitted out in: two at the surface band, one more per
        /// step inward, never more than <see cref="DeepPaletteSize"/>.
        ///
        /// This was a flat constant at every depth, which meant the deepest coordinate in the
        /// game was fitted out in exactly as few materials as the shallowest — the whole of the
        /// owner's direction, sitting as a `const int`.
        /// </summary>
        internal static int PaletteSizeFor(int depth)
        {
            int size = ShallowPaletteSize + (depth < 1 ? 0 : depth - 1);
            if (size < ShallowPaletteSize) { return ShallowPaletteSize; }
            return size > DeepPaletteSize ? DeepPaletteSize : size;
        }

        /// <summary>Bumped when the derivation changes, so a palette cannot silently shift.</summary>
        private const int MaterialVersion = 2;"""),

    ("""            string key = coordinate == null ? "" : coordinate.Id ?? "";""",
     """            // Keyed by id AND depth. The id alone was enough while the palette was the same
            // size everywhere; it is not now, and a cache that ignored depth would hand a deep
            // coordinate a shallow palette for the rest of the session.
            string key = coordinate == null ? "" : (coordinate.Id ?? "") + ":" + coordinate.Depth;"""),

    ("""            int stride = 1 + Math.Abs(seed / 7) % Math.Max(1, available.Count);
            int position = Math.Abs(seed) % available.Count;
            for (int step = 0; step < PaletteSize && chosen.Count < available.Count; step++)""",
     """            int stride = 1 + Math.Abs(seed / 7) % Math.Max(1, available.Count);
            int position = Math.Abs(seed) % available.Count;
            int wanted = PaletteSizeFor(coordinate == null ? 1 : coordinate.Depth);
            for (int step = 0; step < wanted && chosen.Count < available.Count; step++)"""),
])


# ------------------------------------------------------------------ 2. the dressing path
edit(os.path.join(SRC, "Generation", "RoomContentBuilder.cs"), [
    ("""                thing = ThingMaker.MakeThing(definition,
                    definition.MadeFromStuff ? GenStuff.DefaultStuffFor(definition) : null);""",
     """                // **The palette reaches the dressing now, and this was the worst of the three
                // gaps.** This path places the depth-scaled archetype dressing -- the benches,
                // the equipment, the loot, everything the owner means by *"found everywher deeper
                // in"* -- and it was taking Core's default material while the family fixtures a
                // few lines below took the coordinate's palette. So the content that was supposed
                // to vary was the one content that could not.
                //
                // StuffFor falls back to GenStuff.DefaultStuffFor when the palette has nothing
                // this fixture can be made of, so this is strictly wider than what it replaces.
                thing = ThingMaker.MakeThing(definition,
                    CoordinateMaterials.StuffFor(definition, coordinate));"""),
])


# ------------------------------------------------------------------ 3. the walls
edit(os.path.join(SRC, "Generation", "GenStep_BackroomsDestination.cs"), [
    ("""                ThingDef wallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff
                    ?? ThingDefOf.Steel;""",
     """                // The band's own choice is the fallback, and at depth 1 it is the answer: the
                // yellow rooms are wood-walled and stay that way, for the same reason nothing
                // else deforms at the surface band.
                //
                // **Deeper, the walls come from the coordinate's palette.** Owner direction:
                // *"wild variatiosn of material typeds in all items equaipment walls floors ..."*.
                // `BackroomsPalette` names exactly two wall materials -- WoodLog or Steel --
                // across five bands, which is a hard-coded pair where every other material in
                // the place is drawn from whatever the profile offers. Asking
                // CoordinateMaterials means a profile that adds stone or metal widens the walls
                // exactly as it already widens the furniture, and nothing here names a material.
                ThingDef bandWallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff
                    ?? ThingDefOf.Steel;
                ThingDef wallStuff = coordinate.Depth <= 1 ? bandWallStuff
                    : (CoordinateMaterials.StuffFor(wallDef, coordinate) ?? bandWallStuff);"""),
])

print("stage six applied")
