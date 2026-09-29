using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// Attaches the odd-origin marker to the game's own things, and marks a coordinate's
    /// contents once, at the moment generation finishes.
    ///
    /// ## Why the comp is attached in code rather than by a patch
    ///
    /// The owner's direction is explicitly open-ended — *"for all things materials and
    /// resources ect ect"* — so the marker has to reach every carryable thing in the loaded
    /// game, including ones from the other 274 mods. A `PatchOperationAdd` can only append to a
    /// <c>comps</c> node that already exists, and most item defs have none, so an XML patch
    /// would apply to an arbitrary subset and **fail silently on the rest**. Appending to
    /// <see cref="ThingDef.comps"/> at startup reaches all of them and is still purely additive:
    /// no def is replaced, nothing is removed, and no other mod's files are touched. It is the
    /// same rule as everywhere else in this mod — add definitions, never redistribute or rewrite
    /// somebody else's.
    ///
    /// Two filters keep it honest:
    ///
    /// * **The def must actually instantiate comps.** A <see cref="ThingDef"/> whose
    ///   <c>thingClass</c> is not a <see cref="ThingWithComps"/> never builds its comp list, so
    ///   adding one there would be dead weight that looks like it works. Checked, not assumed.
    /// * **The thing must be something a colonist can carry out.** That means it has
    ///   <c>thingCategories</c> (it is an item) or a <c>minifiedDef</c> (it is a building that
    ///   can be uninstalled and carried, which is the owner's own stove example).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class OddOriginService
    {
        /// <summary>How many defs received the marker. Reported in the log line below.</summary>
        private static int attached;

        static OddOriginService()
        {
            try
            {
                Attach();
            }
            catch (Exception error)
            {
                // A failure here must never stop the game loading. The economy degrades to
                // "nothing is odd", which is visibly wrong rather than quietly wrong.
                Log.Error("[Rimrooms] odd-origin markers could not be attached: " + error);
            }
        }

        private static void Attach()
        {
            List<ThingDef> definitions = DefDatabase<ThingDef>.AllDefsListForReading;
            if (definitions == null) { return; }
            for (int index = 0; index < definitions.Count; index++)
            {
                ThingDef definition = definitions[index];
                if (!CanCarryMarker(definition)) { continue; }
                if (definition.comps == null) { definition.comps = new List<CompProperties>(); }
                if (definition.HasComp(typeof(CompRimroomsOddOrigin))) { continue; }
                definition.comps.Add(new CompProperties_RimroomsOddOrigin());
                attached++;
            }
            Log.Message("[Rimrooms] odd-origin marker attached to " + attached + " thing definitions.");
        }

        /// <summary>
        /// Whether this definition is a thing a colonist could carry out of a coordinate, and
        /// one whose class will actually build the comp.
        /// </summary>
        private static bool CanCarryMarker(ThingDef definition)
        {
            if (definition == null || definition.thingClass == null) { return false; }
            if (!typeof(ThingWithComps).IsAssignableFrom(definition.thingClass)) { return false; }
            bool item = definition.thingCategories != null && definition.thingCategories.Count > 0;
            bool uninstallable = definition.minifiedDef != null;
            return item || uninstallable;
        }

        /// <summary>
        /// Reads the mark, looking through a minified wrapper. Uninstalling a building produces
        /// a <see cref="MinifiedThing"/> whose <c>InnerThing</c> is the original, so asking the
        /// wrapper directly would report every uninstalled stove as ordinary — which is exactly
        /// the case the owner named.
        /// </summary>
        public static bool IsOdd(Thing thing)
        {
            Thing subject = Resolve(thing);
            if (subject == null) { return false; }
            CompRimroomsOddOrigin marker = subject.TryGetComp<CompRimroomsOddOrigin>();
            return marker != null && marker.IsOdd;
        }

        /// <summary>
        /// Marks one thing, looking through a minified wrapper. Returns whether a mark was
        /// actually applied, so callers can count honestly rather than estimate.
        /// </summary>
        public static bool Mark(Thing thing)
        {
            Thing subject = Resolve(thing);
            if (subject == null) { return false; }
            CompRimroomsOddOrigin marker = subject.TryGetComp<CompRimroomsOddOrigin>();
            // Already stamped either way -- odd, or proven to have come from outside --
            // means there is nothing to do and nothing was changed. Reporting otherwise
            // would make the generation pass overcount what it marked.
            if (marker == null || marker.Origin != ThingOrigin.Unknown) { return false; }
            marker.MarkOdd();
            return true;
        }

        /// <summary>
        /// The recorded origin of a thing, looking through a minified wrapper. Distinguishes
        /// "proven to have come from outside" from "never stamped", which the boolean
        /// <see cref="IsOdd"/> cannot: shelter scoring needs the former and must not count the
        /// latter, or an unstamped Backrooms fixture would read as comfort from home.
        /// </summary>
        public static ThingOrigin OriginOf(Thing thing)
        {
            Thing subject = Resolve(thing);
            if (subject == null) { return ThingOrigin.Unknown; }
            CompRimroomsOddOrigin marker = subject.TryGetComp<CompRimroomsOddOrigin>();
            return marker == null ? ThingOrigin.Unknown : marker.Origin;
        }

        /// <summary>
        /// Whether this map is a Backrooms coordinate that has finished generating.
        ///
        /// Readiness matters rather than being pedantry: a map still being built is not yet a
        /// place a thing can be said to have come *from*, and the generation pass marks its
        /// contents explicitly anyway.
        /// </summary>
        public static bool IsBackroomsMap(Map map)
        {
            if (map == null) { return false; }
            var site = map.Parent as Generation.RimroomsDestinationMapParent;
            return site != null && site.LayoutReady;
        }

        private static Thing Resolve(Thing thing)
        {
            MinifiedThing minified = thing as MinifiedThing;
            return minified != null ? minified.InnerThing : thing;
        }

        /// <summary>
        /// Marks everything a freshly generated coordinate contains, in one pass.
        ///
        /// **This is the only place a mark is ever applied, and that is deliberate.** The
        /// obvious alternative — mark anything that spawns on a Backrooms map — is an open
        /// laundering route: a player could haul a thousand ordinary cotton in, drop it, pick it
        /// up and walk out with a thousand *odd* cotton, which defeats the entire point of the
        /// contracts. Marking only at generation means the mark can only ever be earned by
        /// going in and taking what was already there.
        ///
        /// Called at the end of generation, before the map is ever reachable, so nothing the
        /// player owns can be present to be marked by accident.
        /// </summary>
        /// <returns>
        /// The distinct definition names actually marked, sorted, so the coordinate can record
        /// what it really produced. Supply contracts are drawn from that record rather than
        /// from the whole def database: a demand for a thousand odd cotton is worthless if no
        /// space the branch has ever opened contained cotton.
        /// </returns>
        public static List<string> MarkGeneratedContents(Map map)
        {
            var produced = new List<string>();
            if (map == null || map.listerThings == null) { return produced; }
            List<Thing> things = map.listerThings.AllThings;
            if (things == null) { return produced; }
            var seen = new HashSet<string>(StringComparer.Ordinal);
            // A copy, because marking is read-only against the lister but callers should not
            // depend on that staying true if this ever grows.
            var snapshot = new List<Thing>(things);
            for (int index = 0; index < snapshot.Count; index++)
            {
                Thing thing = snapshot[index];
                // Pawns are not goods. A generated inhabitant is not a thing to be sold by
                // origin, and the traversal rule already governs what may leave a coordinate.
                if (thing == null || thing is Pawn) { continue; }
                if (!Mark(thing)) { continue; }
                Thing subject = Resolve(thing);
                if (subject == null || subject.def == null) { continue; }
                if (seen.Add(subject.def.defName)) { produced.Add(subject.def.defName); }
            }
            produced.Sort(StringComparer.Ordinal);
            return produced;
        }
    }
}
