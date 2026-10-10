# -*- coding: utf-8 -*-
"""Every type of material, for all things, randomly -- and level 0 stays the yellow rooms.

Owner correction, 2026-09-30, verbatim:

    "this is wrong we want every type of wall and material for all things randomly"
    "but depth 0 in the backrroms is the standard yellow style"
    "ive already lkayed this out"

They had. It is in their own words, quoted inside `BackroomsPalette` already:

    "we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main
     backrooms look"
    "andf remmebr thats just the main backrooms looks further in it gets very varied and weird"

So the specification is two-part and this file implements exactly that split:

  * **Level 0 is the standard yellow style.** Monotonous on purpose, coherent, yellow wood walls
    and yellow carpet. A narrow shared palette is RIGHT there.
  * **Deeper is every type, for all things, randomly.** Not a palette at all: each thing draws
    from the full set of materials Core allows for that particular def.

WHAT WAS WRONG WITH WHAT THIS REPLACES. A per-coordinate palette of two to six materials, with
every fixture taking the first entry it could use, means a deep level still reads as "fitted out
in three materials" -- a table and a wall in the same place tend to match. The palette's own doc
argued FOR that, calling per-item choice "a jumble ... which reads as noise rather than as a
place". **That argument is mine and the owner has overruled it**, twice, and for the deep bands
they are right: *"very varied and weird"* is the brief, and coherence is the thing being left
behind as you go inward.
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


# ---------------------------------------------------------------- the selector
edit(os.path.join(SRC, "Generation", "CoordinateMaterials.cs"), [
    ("""        /// <summary>
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
        private const int MaterialVersion = 2;""",
     """        /// <summary>
        /// The shallowest band a coordinate can have, which is the one that stays coherent.
        ///
        /// **Owner direction, 2026-09-30, verbatim:** *"but depth 0 in the backrroms is the
        /// standard yellow style"*, and earlier, *"we can use the floor lights i guess for the
        /// yellow carpet and yellow wood walls for the main backrooms look"* followed
        /// immediately by *"andf remmebr thats just the main backrooms looks further in it gets
        /// very varied and weird"*.
        ///
        /// At or below this depth a coordinate shares one narrow palette, which is what makes the
        /// yellow rooms read as a place. Above it, see <see cref="StuffFor"/>: every thing draws
        /// its own material from everything Core allows for it.
        /// </summary>
        internal const int CoherentDepth = 1;

        /// <summary>Bumped when the derivation changes, so a material cannot silently shift.</summary>
        private const int MaterialVersion = 3;"""),

    ("""        internal static ThingDef StuffFor(ThingDef definition, CoordinateRecord coordinate)
        {
            if (definition == null || !definition.MadeFromStuff) { return null; }
            List<ThingDef> palette = PaletteFor(coordinate);
            for (int index = 0; index < palette.Count; index++)
            {
                ThingDef candidate = palette[index];
                if (Allowed(definition, candidate)) { return candidate; }
            }
            // Core's own answer, which is always buildable for a stuffable def.
            return GenStuff.DefaultStuffFor(definition);
        }""",
     """        internal static ThingDef StuffFor(ThingDef definition, CoordinateRecord coordinate)
        { return StuffFor(definition, coordinate, 0); }

        /// <summary>
        /// What this particular fixture is made of on this coordinate.
        ///
        /// ## Two behaviours, and the split is the owner's specification
        ///
        /// **At <see cref="CoherentDepth"/> and below: one narrow shared palette.** The yellow
        /// rooms are monotonous on purpose, and a level where the table, the shelf and the walls
        /// are the same material is what makes them read as a place rather than a warehouse of
        /// samples.
        ///
        /// **Deeper: every type, for all things, randomly.** Owner correction, verbatim: *"this is
        /// wrong we want every type of wall and material for all things randomly"*. So there is no
        /// palette down there at all — this fixture draws from **the full set of materials Core
        /// allows for its own def**, indexed by its own <paramref name="variant"/>. Two tables in
        /// one room can be different woods, different metals, or one of each.
        ///
        /// ## Still deterministic, and that is not negotiable
        ///
        /// A coordinate is regenerated from its seed, so the choice is a pure function of the
        /// coordinate's seed and id, the fixture's def name, and the variant the caller passes.
        /// **No `Rand` call**, and the candidate list is sorted by defName before anything indexes
        /// into it — because `AllowedStuffsFor` returns database order, which depends on the
        /// installed mod list, and a coordinate must not change appearance because the player
        /// installed something unrelated.
        ///
        /// ## Still existing content only
        ///
        /// `GenStuff.AllowedStuffsFor` is Core's own answer to *"what may this be made of"*, so a
        /// mod that adds a material widens this automatically and a mod that restricts one is
        /// obeyed. **Nothing here names a material.**
        /// </summary>
        internal static ThingDef StuffFor(ThingDef definition, CoordinateRecord coordinate, int variant)
        {
            if (definition == null || !definition.MadeFromStuff) { return null; }
            int depth = coordinate == null ? 1 : coordinate.Depth;
            if (depth > CoherentDepth)
            {
                ThingDef wild = WildStuffFor(definition, coordinate, variant);
                if (wild != null) { return wild; }
            }
            List<ThingDef> palette = PaletteFor(coordinate);
            for (int index = 0; index < palette.Count; index++)
            {
                ThingDef candidate = palette[index];
                if (Allowed(definition, candidate)) { return candidate; }
            }
            // Core's own answer, which is always buildable for a stuffable def.
            return GenStuff.DefaultStuffFor(definition);
        }

        /// <summary>
        /// One material out of everything this def may be made of, chosen per fixture.
        ///
        /// Asked through <c>GenStuff.AllowedStuffsFor</c> rather than through the eligibility test
        /// this file uses for its palette, because that is Core's complete answer for this
        /// particular def and the point of this path is to leave nothing out.
        ///
        /// Returns null when Core allows nothing, so the caller falls through to the palette and
        /// then to Core's default. A generation pass must never fail over a furnishing choice.
        /// </summary>
        private static ThingDef WildStuffFor(ThingDef definition, CoordinateRecord coordinate, int variant)
        {
            List<ThingDef> allowed = GenStuff.AllowedStuffsFor(definition)
                .Where(candidate => candidate != null && candidate.stuffProps != null &&
                    candidate.stuffProps.allowedInStuffGeneration)
                .OrderBy(candidate => candidate.defName, StringComparer.Ordinal)
                .ToList();
            if (allowed.Count == 0) { return null; }
            int seed = coordinate == null
                ? MaterialVersion
                : DestinationService.StableHash(coordinate.Seed,
                    (coordinate.Id ?? "") + ":wild:" + definition.defName + ":" + variant,
                    MaterialVersion);
            return allowed[Math.Abs(seed) % allowed.Count];
        }"""),

    ("""            int wanted = PaletteSizeFor(coordinate == null ? 1 : coordinate.Depth);
            for (int step = 0; step < wanted && chosen.Count < available.Count; step++)""",
     """            for (int step = 0; step < ShallowPaletteSize && chosen.Count < available.Count; step++)"""),
])


# ---------------------------------------------------------------- the fixtures pass a variant
edit(os.path.join(SRC, "Generation", "RoomContentBuilder.cs"), [
    ("""                thing = ThingMaker.MakeThing(definition,
                    CoordinateMaterials.StuffFor(definition, coordinate));""",
     """                // The variant is what lets two identical fixtures in one room be different
                // materials deeper in. Built from the slot and the placement seed, both of which
                // are already deterministic per coordinate.
                thing = ThingMaker.MakeThing(definition,
                    CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));"""),

    ("""            Thing thing = ThingMaker.MakeThing(definition,
                CoordinateMaterials.StuffFor(definition, coordinate));""",
     """            Thing thing = ThingMaker.MakeThing(definition,
                CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));"""),
])


# ---------------------------------------------------------------- walls, per room, deeper in
edit(os.path.join(SRC, "Generation", "GenStep_BackroomsDestination.cs"), [
    ("""                ThingDef bandWallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff
                    ?? ThingDefOf.Steel;
                ThingDef wallStuff = coordinate.Depth <= 1 ? bandWallStuff
                    : (CoordinateMaterials.StuffFor(wallDef, coordinate) ?? bandWallStuff);""",
     """                // The band's own choice, which at level 0 IS the answer: owner direction,
                // *"depth 0 in the backrroms is the standard yellow style"*, and the yellow rooms
                // are wood-walled. It stays the fallback everywhere.
                ThingDef bandWallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff
                    ?? ThingDefOf.Steel;"""),

    ("                BuildRoomWalls(room, coordinate.Rooms, map, wallDef, wallStuff);",
     """                // **Walls are chosen PER ROOM deeper in.** Owner correction: *"we want every
                // type of wall and material for all things randomly"*. One material for the whole
                // level was the thing being corrected -- and per ROOM rather than per CELL because
                // a wall whose every cell is a different stone is a patchwork rather than a wall,
                // and BuildRoomWalls places one room's ring at a time, so the room is the unit
                // the geometry already has.
                //
                // At level 0 every room takes the band's wood, unchanged.
                ThingDef roomWallStuff = coordinate.Depth <= CoordinateMaterials.CoherentDepth
                    ? bandWallStuff
                    : (CoordinateMaterials.StuffFor(wallDef, coordinate, room.Index) ?? bandWallStuff);
                BuildRoomWalls(room, coordinate.Rooms, map, wallDef, roomWallStuff);"""),
])

print("stage six-b applied")
