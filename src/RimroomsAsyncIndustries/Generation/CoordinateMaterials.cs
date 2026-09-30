using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// What a coordinate's furniture is **made of**.
    ///
    /// ## The defect this closes
    ///
    /// Row 1005: *"material variety per coordinate — archetype fixtures take their default stuff
    /// today."* The reality was worse than the row said. `RoomContentBuilder.Place` read:
    ///
    /// <code>
    /// ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.WoodLog : null);
    /// </code>
    ///
    /// **Every stuffable fixture on every coordinate in the game was wooden.** Not the def's
    /// default — a single hardcoded material. Every table, chair, shelf, stool and lamp in every
    /// room of every space the player will ever walk into, identical. That is the opposite of the
    /// *"variation seeded"* the generation rows ask for, and it is the sort of thing that reads as
    /// deliberate right up until the second coordinate.
    ///
    /// ## A coordinate has a palette, not a random material per item
    ///
    /// The distinction matters and it is the whole design. Rolling a material per fixture would
    /// produce a jumble: a steel table beside a wooden chair beside a granite stool, in one small
    /// room, which reads as noise rather than as a place. **A coordinate gets a short ordered
    /// palette instead**, and every fixture takes the first entry in it that the fixture can
    /// actually be made of.
    ///
    /// So a coordinate looks like somewhere — one that was fitted out in steel, one in wood, one
    /// in slate — and two coordinates look different from each other. The palette is small
    /// (<see cref="PaletteSize"/>) because a place with four materials in it is a place with no
    /// character.
    ///
    /// ## Deterministic from the coordinate's own seed, which is not optional
    ///
    /// A coordinate is **regenerated from its seed**, and two players on the same seed must see
    /// the same thing. That rule already governs `GateIncursion`'s candidate ordering and the
    /// between-visit displacement at 0.10.3-dev. So the palette is derived with
    /// <see cref="DestinationService.StableHash"/> from the coordinate's seed and id — the same
    /// helper `RoomContentBuilder` already uses for its own layout choices — and the candidate
    /// material list is **sorted by defName** before anything indexes into it.
    ///
    /// That sort is the load-bearing line. `GenStuff.AllowedStuffsFor` returns defs in database
    /// order, which depends on **which mods are installed and in what order**. Indexing into it
    /// unsorted would give two players with different mod lists different materials from the same
    /// seed, and would change a coordinate's appearance when the player installs an unrelated mod.
    /// Sorting by name makes the choice a function of the seed and the available material set
    /// alone.
    ///
    /// **No `Rand` call here at all**, deliberately, even though the caller has pushed a seeded
    /// state: a pure function of the seed cannot be perturbed by how many `Rand` calls happened
    /// earlier in generation, and the room-content pass already changed shape once.
    ///
    /// ## Existing content only
    ///
    /// Every material is one Core or the installed profile already ships.
    /// `GenStuff.AllowedStuffsFor(def)` is Core's own answer to *"what may this be made of"*, so a
    /// mod that adds a stuffable material is used automatically, and a mod that restricts one is
    /// obeyed. **Nothing here names a material.** There is no list to fall out of date, and no
    /// `ThingDef` was added.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py family materials` — **one of the seven families the register retro sweep
    /// has not reached** (rows 206, 302), so its rows were read directly. **97 Gemstones** is
    /// *"optional resource/trade content; keep Rimrooms currency and research independent"* and
    /// *"use native item behavior only; do not require gems or reuse content"*. Honoured exactly:
    /// gems become eligible fixture material only if Core's own `AllowedStuffsFor` says they are,
    /// nothing here requires them, and no gem is named. The same holds for every stone, metal and
    /// fabric mod in the profile — they widen the palette without being known about.
    ///
    /// The one thing worth stating: a profile that adds many materials makes coordinates *more*
    /// varied rather than less, because the palette is drawn from whatever is allowed. That is the
    /// intended direction.
    /// </summary>
    internal static class CoordinateMaterials
    {
        /// <summary>
        /// How many materials one coordinate may be fitted out in. Three, so a coordinate has a
        /// character and a fixture that cannot take the first choice still has somewhere to go.
        /// </summary>
        private const int PaletteSize = 3;

        /// <summary>Bumped when the derivation changes, so a palette cannot silently shift.</summary>
        private const int MaterialVersion = 1;

        /// <summary>
        /// The palette for one coordinate, cached per coordinate id for the duration of a
        /// generation pass. Rebuilt rather than saved: it is a pure function of the seed, so
        /// storing it would be a second copy that could disagree with the derivation.
        /// </summary>
        private static readonly Dictionary<string, List<ThingDef>> cache =
            new Dictionary<string, List<ThingDef>>(StringComparer.Ordinal);

        private static int cachedGeneration = -1;

        /// <summary>
        /// What this fixture should be made of on this coordinate, or null when the fixture takes
        /// no material at all.
        ///
        /// Returns Core's own default rather than null when the palette has nothing this fixture
        /// can be made of, because a fixture with no material cannot be built and a generation
        /// pass must not fail over a furnishing choice.
        /// </summary>
        internal static ThingDef StuffFor(ThingDef definition, CoordinateRecord coordinate)
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
        }

        /// <summary>
        /// Whether Core would let this fixture be made of this material. Asked through the def's
        /// own stuff categories rather than through `AllowedStuffsFor`, because this runs once per
        /// fixture and the category test is a list comparison rather than a database walk.
        /// </summary>
        private static bool Allowed(ThingDef definition, ThingDef stuff)
        {
            if (stuff == null || stuff.stuffProps == null ||
                stuff.stuffProps.categories == null) { return false; }
            List<StuffCategoryDef> wanted = definition.stuffCategories;
            if (wanted == null) { return false; }
            for (int index = 0; index < wanted.Count; index++)
            {
                if (stuff.stuffProps.categories.Contains(wanted[index])) { return true; }
            }
            return false;
        }

        /// <summary>
        /// The ordered palette for a coordinate. Derived, never stored.
        /// </summary>
        private static List<ThingDef> PaletteFor(CoordinateRecord coordinate)
        {
            // The cache is scoped to one game. A reload produces a new game and must not inherit
            // a palette built against a previous def database, which a mod change could alter.
            int generation = Current.Game == null ? -1 : Current.Game.GetHashCode();
            if (generation != cachedGeneration)
            {
                cachedGeneration = generation;
                cache.Clear();
            }

            string key = coordinate == null ? "" : coordinate.Id ?? "";
            List<ThingDef> palette;
            if (cache.TryGetValue(key, out palette)) { return palette; }

            palette = Build(coordinate);
            cache[key] = palette;
            return palette;
        }

        private static List<ThingDef> Build(CoordinateRecord coordinate)
        {
            // Sorted by name, which is the line that makes this reproducible: the database order
            // AllowedStuffs returns depends on the installed mod list, and a coordinate must not
            // change appearance because the player installed something unrelated.
            List<ThingDef> available = DefDatabase<ThingDef>.AllDefsListForReading
                .Where(Usable)
                .OrderBy(definition => definition.defName, StringComparer.Ordinal)
                .ToList();
            var chosen = new List<ThingDef>();
            if (available.Count == 0) { return chosen; }

            int seed = coordinate == null
                ? MaterialVersion
                : DestinationService.StableHash(coordinate.Seed,
                    (coordinate.Id ?? "") + ":materials", MaterialVersion);

            // Walk with a stride rather than taking consecutive entries, so a coordinate's three
            // materials are spread across the sorted list instead of being three neighbours with
            // near-identical names -- and so a profile that adds a family of similar stones does
            // not produce a coordinate fitted out in three shades of the same thing.
            int stride = 1 + Math.Abs(seed / 7) % Math.Max(1, available.Count);
            int position = Math.Abs(seed) % available.Count;
            for (int step = 0; step < PaletteSize && chosen.Count < available.Count; step++)
            {
                for (int probe = 0; probe < available.Count; probe++)
                {
                    ThingDef candidate = available[(position + probe) % available.Count];
                    if (!chosen.Contains(candidate)) { chosen.Add(candidate); break; }
                }
                position = (position + stride) % available.Count;
            }
            return chosen;
        }

        /// <summary>
        /// A material this generator may furnish with: something Core considers stuff, that is not
        /// itself a piece of this mod's content, and that a player could plausibly find fitted
        /// into a room.
        ///
        /// The `allowedInStuffGeneration` flag is Core's own opt-out, and honouring it is why no
        /// exclusion list is needed here: Core already marks the materials that should not turn up
        /// in generated content.
        /// </summary>
        private static bool Usable(ThingDef definition)
        {
            if (definition == null || definition.stuffProps == null) { return false; }
            if (definition.stuffProps.categories == null ||
                definition.stuffProps.categories.Count == 0) { return false; }
            if (!definition.stuffProps.allowedInStuffGeneration) { return false; }
            // This mod authors no material, and this is the guard that keeps it true even if one
            // is ever added: a coordinate is furnished out of the world's materials, not ours.
            return definition.defName == null || !definition.defName.StartsWith("RR_",
                StringComparison.Ordinal);
        }
    }
}
