using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Decides which found objects carry a tell, and makes them able to carry one at all.
    ///
    /// ## Why the comp is attached in code rather than by a patch, which is the interesting part
    ///
    /// Every other comp this mod puts on existing content goes on by XML in
    /// `Patches/RR_NativeGateProviders.xml`, and that file records the limit that forced this:
    ///
    /// > *"A race-condition xpath looks like the right answer and is not: patches run on the raw
    /// > XML BEFORE def inheritance is resolved, so `ThingDef[race/intelligence="Animal"]` matches
    /// > only the few defs that state it themselves and silently misses the rest."*
    ///
    /// The animal case had a usable workaround — `AnimalThingBase` is a single abstract parent, so
    /// patching it carried the comp by inheritance, at the cost of a stated gap for mod animals
    /// that do not inherit it. **There is no equivalent parent here.** The objects this has to
    /// reach are whatever answers <see cref="RoomArchetypeService.Placeable"/>: work tables, seats,
    /// shelves, lamps and haulable items, across Core, every DLC and all 294 profile mods. Those
    /// descend from a dozen unrelated abstract bases, and `BuildingBase` — the only parent broad
    /// enough to catch the furniture — would attach this to **every building in every colony in
    /// the game**, walls and doors and turrets included, to reach the handful that can be dressed
    /// into a Backrooms room.
    ///
    /// So the attachment is made here, at <c>StaticConstructorOnStartup</c>, which runs **after
    /// inheritance has resolved and after every mod's defs are loaded**. That is strictly more
    /// precise than any xpath could be: the question asked is the same question the generator
    /// asks when it places things, so the set that can carry a tell is exactly the set that can
    /// be placed. Nothing wider, and no gap to record.
    ///
    /// **One rule, one place.** The eligibility test is `RoomArchetypeService.Placeable` itself
    /// rather than a copy of it — *"two derivations of one rule is the defect this project keeps
    /// meeting"*, as `RoomContentBuilder.FixtureCell` puts it. If the generator stops being able
    /// to place something, it stops being able to carry a tell, in the same edit.
    ///
    /// ## Still existing content only, and still no new ThingDef
    ///
    /// Nothing here authors, renames or replaces a definition. A comp is added to definitions the
    /// loaded game already shipped, it is inert on every instance nobody marked, and the tell text
    /// is this mod's own keyed string. No Core or mod asset is copied or redistributed.
    /// </summary>
    [StaticConstructorOnStartup]
    internal static class FixtureTellService
    {
        /// <summary>
        /// How many of the objects placed in a qualifying room carry a tell, as a percentage.
        ///
        /// **Deliberately a small minority, and this is the design rather than a dial.**
        /// `CoordinatePressureLadder.IsQuietRoom` already establishes the rule: *"quiet stretches
        /// are required content"*. A coordinate where every stool and steel stack has a sentence
        /// on it is a museum with too many placards, and worse, it buries the inhabitant and event
        /// tells that carry the sharper beats. The first one a player finds should be the only one
        /// in the room.
        /// </summary>
        internal const int TellPercent = 12;

        /// <summary>Bumped when the derivation changes, so a tell cannot silently move.</summary>
        private const int TellVersion = 1;

        /// <summary>
        /// Attaches the tell comp to every definition the generator is capable of placing.
        ///
        /// Runs once, at startup, after every mod's defs are loaded and resolved.
        /// </summary>
        static FixtureTellService()
        {
            int attached = 0;
            int skippedPlainThing = 0;
            List<ThingDef> all = DefDatabase<ThingDef>.AllDefsListForReading;
            for (int index = 0; index < all.Count; index++)
            {
                ThingDef definition = all[index];
                if (definition == null || !RoomArchetypeService.Placeable(definition)) { continue; }

                // **A comp on a plain `Thing` does nothing at all, silently.** Only
                // `ThingWithComps` reads `def.comps` and builds the comp list; a def whose
                // thingClass is `Thing` would accept the entry and never instantiate it, so the
                // mark would be made against a null comp and the tell would simply not exist.
                // Counted rather than ignored, so the log says how much was out of reach.
                if (definition.thingClass == null
                    || !typeof(ThingWithComps).IsAssignableFrom(definition.thingClass))
                { skippedPlainThing++; continue; }

                if (definition.HasComp(typeof(CompRimroomsFixtureTell))) { continue; }
                definition.comps = definition.comps ?? new List<CompProperties>();
                definition.comps.Add(new CompProperties_RimroomsFixtureTell());
                attached++;
            }
            // One line, once, at startup. The owner reads the first `[Rimrooms]` line of a launch
            // log as a matter of routine, and a count here is the difference between "the tells
            // are not showing" being a mystery and being an answer.
            Log.Message("[Rimrooms][Generation] Fixture tells attached to " + attached
                        + " definitions; " + skippedPlainThing
                        + " placeable definitions cannot carry comps and read their tell in the"
                        + " room record instead.");
        }

        /// <summary>
        /// Marks an object with one exact wrong fact, or leaves it alone.
        ///
        /// Silent and total: anything that does not qualify — a shallow room, an object outside
        /// the derived minority, a definition no tell applies to, a def that cannot carry the comp
        /// — is simply an ordinary object. **A furnishing decision may never fail a generation
        /// pass**, which is the rule `RoomContentBuilder.DressRoom` states and the reason a
        /// landmark placement once cost the owner a whole level.
        /// </summary>
        internal static void Mark(Thing thing, CoordinateRecord coordinate, RoomRecord room,
            int variant)
        {
            if (thing == null || coordinate == null) { return; }
            CompRimroomsFixtureTell comp = thing.TryGetComp<CompRimroomsFixtureTell>();
            if (comp == null || comp.Marked) { return; }

            // Measured the same way the dressing is, so a room a dozen links out on a first level
            // qualifies and the hall it leads back to does not. Owner: *"the normal yellow
            // backrooms look isnt the whole floor but the main spanw room"*.
            int depth = RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth);

            // **Derived, never `Rand`.** A coordinate is regenerated from its seed and two players
            // on the same seed must find the same wrong bench. `Rand` would also let a reload
            // reseat which object was odd, which is a save-scum on the one thing the player is
            // supposed to be able to go back and re-read.
            string key = (coordinate.Id ?? "") + ":tell:" + (room == null ? -1 : room.Index)
                + ":" + variant + ":" + (thing.def == null ? "" : thing.def.defName);
            int roll = DestinationService.StableHash(coordinate.Seed, key, TellVersion);
            if (roll < 0) { roll = ~roll; }
            if (roll % 100 >= TellPercent) { return; }

            RimroomsFixtureTellDef chosen = Choose(thing.def, depth, roll);
            if (chosen == null) { return; }
            comp.Mark(chosen);
        }

        /// <summary>
        /// The tell for this object, weighted among those legal for its kind and depth.
        ///
        /// Sorted by defName before anything indexes into it, because `AllDefsListForReading`
        /// returns database order and that depends on the installed mod list — the same reason
        /// <see cref="CoordinateMaterials"/> sorts its material candidates and
        /// <see cref="RoomArchetypeService"/> sorts its archetypes. A coordinate must not change
        /// what it says because the player installed something unrelated.
        /// </summary>
        private static RimroomsFixtureTellDef Choose(ThingDef definition, int depth, int roll)
        {
            var legal = new List<RimroomsFixtureTellDef>();
            List<RimroomsFixtureTellDef> all =
                DefDatabase<RimroomsFixtureTellDef>.AllDefsListForReading;
            for (int index = 0; index < all.Count; index++)
            {
                RimroomsFixtureTellDef candidate = all[index];
                if (candidate == null) { continue; }
                if (candidate.minDepth > depth) { continue; }
                if (candidate.maxDepth > 0 && candidate.maxDepth < depth) { continue; }
                if (!Fits(candidate.appliesTo, definition)) { continue; }
                legal.Add(candidate);
            }
            if (legal.Count == 0) { return null; }
            legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));

            float total = 0f;
            for (int index = 0; index < legal.Count; index++)
            { total += Math.Max(0.0001f, legal[index].weight); }
            float pick = (roll / 100 % 100000) / 100000f * total;
            for (int index = 0; index < legal.Count; index++)
            {
                pick -= Math.Max(0.0001f, legal[index].weight);
                if (pick <= 0f) { return legal[index]; }
            }
            return legal[legal.Count - 1];
        }

        /// <summary>
        /// Whether a tell for this class of object is true of this definition.
        ///
        /// Asked of the definition through Core's own properties, which is the same discipline
        /// <see cref="RoomArchetypeService"/> uses to answer a capability slot: a bench from a mod
        /// installed tomorrow is a bench today, with nothing here naming it.
        /// </summary>
        private static bool Fits(FixtureClass wanted, ThingDef definition)
        {
            if (definition == null) { return false; }
            switch (wanted)
            {
                case FixtureClass.Any:
                    return true;
                case FixtureClass.Bench:
                    return definition.IsWorkTable;
                case FixtureClass.Seat:
                    return definition.building != null && definition.building.isSittable;
                case FixtureClass.Table:
                    return definition.IsTable;
                case FixtureClass.Bed:
                    return definition.building != null && definition.building.bed_humanlike
                        && definition.IsBed;
                case FixtureClass.Storage:
                    return definition.building != null
                        && definition.building.fixedStorageSettings != null;
                case FixtureClass.Light:
                    return definition.HasComp(typeof(CompGlower));
                case FixtureClass.Equipment:
                    return definition.IsApparel || definition.IsWeapon;
                case FixtureClass.Item:
                    // Equipment is excluded so an equipment tell and an item tell cannot both be
                    // true of a rifle; the narrower class is the one that says something.
                    return definition.category == ThingCategory.Item
                        && !definition.IsApparel && !definition.IsWeapon;
                default:
                    return false;
            }
        }
    }
}
