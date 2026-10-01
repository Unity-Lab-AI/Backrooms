using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Every Backrooms level has a way out to the world and a way further in. Always. Two
    /// doorways per coordinate, chosen when it is first asked about and the same ones ever after.
    ///
    /// ## Owner direction, verbatim
    ///
    /// *"every backrooms instance need a protal to the world map and a deeper in portal"*, and
    /// the report that produced it: *"i explored it all and there were zero weird events or
    /// people, there were zero portals to be discovered"*, *"have more natural portals
    /// guaranteeed so the backrooms never ends persay"*.
    ///
    /// ## Why there were none to find
    ///
    /// Ways onward were **entirely probabilistic**. Every doorway in a coordinate is a candidate,
    /// and `Evaluate` ends with
    ///
    ///     if (draw % origin.Rarity != 0) { return "RR_Frontier_LeadsNowhere"; }
    ///
    /// with `FrontierRarity = 12`. **One doorway in twelve.** A level is allowed four to six ways
    /// onward, but *allowed* is not *has* -- a whole level can roll none, and the owner walked one
    /// that did. A Backrooms with no way deeper and no way out is a dead end, and the dead end is
    /// invisible: nothing tells the player the dice simply did not come up.
    ///
    /// ## What a guarantee is, and what it is not
    ///
    /// It is **not** a third kind of portal and **not** a bypass of the rules. The two chosen
    /// doorways are ordinary frontier candidates that skip the rarity draw and have their kind
    /// decided rather than drawn. Everything else still applies: the threshold is still checked
    /// for obstruction, the way home is still never a frontier, a door already carrying an edge
    /// is still refused, and depth is still capped by `MaximumNaturalDepth`.
    ///
    /// They also **do not count against the cap**, because a cap that can starve the guarantee
    /// would make it conditional -- and the owner's word was *guaranteed*.
    ///
    /// ## Chosen, not marked
    ///
    /// Nothing is written into the coordinate record, so this works for every level already
    /// generated in an existing save rather than only for new ones. The pair is derived from the
    /// coordinate's own seed over its doorways sorted by position, which is the same derivation
    /// every other generated property uses: **stable across saves, reloads and revisits.**
    ///
    /// Re-derived if either door stops existing, because a guarantee that a deconstructed door
    /// used to satisfy is not a guarantee.
    /// </summary>
    internal static class GuaranteedFrontiers
    {
        /// <summary>The pair chosen for one coordinate.</summary>
        private sealed class Pair
        {
            internal Thing Deeper;
            internal Thing Out;
            internal bool Valid
            {
                get
                {
                    return Deeper != null && Deeper.Spawned && !Deeper.Destroyed
                        && Out != null && Out.Spawned && !Out.Destroyed;
                }
            }
        }

        private static readonly Dictionary<string, Pair> chosen = new Dictionary<string, Pair>();

        /// <summary>This coordinate's guaranteed way further in, or null.</summary>
        internal static Thing DeeperDoorOn(CoordinateRecord coordinate, Map map)
        {
            Pair pair = PairFor(coordinate, map);
            return pair == null ? null : pair.Deeper;
        }

        /// <summary>This coordinate's guaranteed way out to the world map, or null.</summary>
        internal static Thing WorldDoorOn(CoordinateRecord coordinate, Map map)
        {
            Pair pair = PairFor(coordinate, map);
            return pair == null ? null : pair.Out;
        }

        /// <summary>Whether this doorway is one of the two, and which.</summary>
        internal static bool IsGuaranteed(Thing door, CoordinateRecord coordinate, out bool leadsOut)
        {
            leadsOut = false;
            if (door == null || coordinate == null) { return false; }
            Pair pair = PairFor(coordinate, door.Map);
            if (pair == null) { return false; }
            if (pair.Out == door) { leadsOut = true; return true; }
            return pair.Deeper == door;
        }

        /// <summary>
        /// The pair for this coordinate, chosen once.
        ///
        /// **Sorted by position, not by load id.** A load id depends on spawn order, which is not
        /// guaranteed stable across a save and reload; a position is fixed for the life of the
        /// map. The same reasoning the frontier draw itself already uses.
        /// </summary>
        private static Pair PairFor(CoordinateRecord coordinate, Map map)
        {
            if (coordinate == null || map == null || string.IsNullOrEmpty(coordinate.Id))
            { return null; }

            Pair cached;
            if (chosen.TryGetValue(coordinate.Id, out cached) && cached != null && cached.Valid)
            { return cached; }

            var doors = new List<Building_Door>();
            List<Thing> all = map.listerThings == null
                ? null : map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            if (all == null) { return null; }
            RimroomsDestinationMapParent site = map.Parent as RimroomsDestinationMapParent;
            for (int index = 0; index < all.Count; index++)
            {
                var door = all[index] as Building_Door;
                if (door == null || !door.Spawned || door.Destroyed) { continue; }
                // The way home is never a frontier, so it can never be one of the two either.
                if (site != null && door == site.ReturnAnchor) { continue; }
                doors.Add(door);
            }
            // Two distinct doorways, so a level with one door has no guarantee to give -- which
            // is honest. Every generated layout has far more than two.
            if (doors.Count < 2) { return null; }

            doors.Sort(delegate (Building_Door left, Building_Door right)
            {
                if (left.Position.z != right.Position.z) { return left.Position.z - right.Position.z; }
                return left.Position.x - right.Position.x;
            });

            int deeperIndex = Index(coordinate.Seed, "guaranteed:deeper", doors.Count);
            int outIndex = Index(coordinate.Seed, "guaranteed:out", doors.Count);
            // Never the same doorway twice: a level whose way out and way deeper were the same
            // door would have one portal, not two, and the owner asked for both.
            if (outIndex == deeperIndex) { outIndex = (outIndex + 1) % doors.Count; }

            var pair = new Pair { Deeper = doors[deeperIndex], Out = doors[outIndex] };
            chosen[coordinate.Id] = pair;
            return pair;
        }

        private static int Index(int seed, string key, int count)
        {
            int derived = CampaignSeed.Derive(seed, key, 1);
            if (derived < 0) { derived = -derived; }
            return count <= 0 ? 0 : derived % count;
        }

        /// <summary>
        /// Forget everything. Called when a game is loaded or a branch is reset, because the
        /// cache holds `Thing` references that belong to maps the previous game owned.
        /// </summary>
        internal static void Clear() { chosen.Clear(); }
    }
}
