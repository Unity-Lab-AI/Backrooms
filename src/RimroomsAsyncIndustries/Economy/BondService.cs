using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// Minting, reading and redeeming company bearer bonds.
    ///
    /// Everything here is deliberately arithmetic plus spawning, with the **ledger transaction
    /// owned by the caller**. The campaign component is the only thing allowed to move the
    /// company balance, because its transactions are idempotent by operation id and that
    /// property is what stops a reload from paying twice. Duplicating that here would create a
    /// second, weaker path to the same money.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class BondService
    {
        /// <summary>The Core def repurposed as the bond. A printed document.</summary>
        public const string BondDefName = "Novel";

        static BondService()
        {
            try
            {
                ThingDef bond = DefDatabase<ThingDef>.GetNamedSilentFail(BondDefName);
                if (bond == null)
                {
                    Log.Warning("[Rimrooms] bond carrier '" + BondDefName +
                                "' is missing; company bonds are unavailable this session.");
                    return;
                }
                if (bond.comps == null) { bond.comps = new List<CompProperties>(); }
                if (!bond.HasComp(typeof(CompRimroomsBond)))
                { bond.comps.Add(new CompProperties_RimroomsBond()); }
                // **AND THE CLASS, for the same reason and by the same mechanism.** `Verse.Book`
                // overrides `LabelNoCount` and never walks comps, so `TransformLabel` could never
                // name a bond -- every one of them showed a random novel title and its quality.
                // Owner: *"now the books as bonds just say noprmal the quality which is normal"*.
                //
                // A Def field, which is the boundary `check-compliance.py` states: behaviour
                // through *"Core's own ThingComp, GameComponent, WorkGiver, JobDriver and Def
                // extension points"*. The first attempt wrote Book's private `title` by
                // reflection and that checker refused it, correctly.
                //
                // **An ordinary novel is unaffected**: every member of the subclass defers to
                // base unless the thing carries a stamped face value, and it still satisfies
                // every `is Book` test in the game.
                if (bond.thingClass == typeof(Book) || bond.thingClass == null)
                { bond.thingClass = typeof(Book_RimroomsBond); }
                // The value, by the one mechanism that can read a per-instance face value. See
                // StatPart_RimroomsBondValue; `MarketValue`'s own parts are untouched.
                StatDef market = StatDefOf.MarketValue;
                if (market != null)
                {
                    if (market.parts == null) { market.parts = new List<StatPart>(); }
                    if (!market.parts.Any(part => part is StatPart_RimroomsBondValue))
                    {
                        var valuePart = new StatPart_RimroomsBondValue { parentStat = market };
                        market.parts.Add(valuePart);
                    }
                }
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms] company bonds could not be prepared: " + error);
            }
        }

        /// <summary>
        /// Face value of a thing, looking through a minified wrapper for consistency with the
        /// rest of this layer. Zero for anything that is not a bond.
        /// </summary>
        public static long FaceValueOf(Thing thing)
        {
            MinifiedThing minified = thing as MinifiedThing;
            Thing subject = minified != null ? minified.InnerThing : thing;
            if (subject == null) { return 0L; }
            CompRimroomsBond bond = subject.TryGetComp<CompRimroomsBond>();
            if (bond == null || !bond.IsBond) { return 0L; }
            return bond.FaceValue * Math.Max(1, subject.stackCount);
        }

        /// <summary>
        /// Makes one bond of a given denomination, unspawned. Returns null if the denomination
        /// is not on the ladder or the carrier def is missing, rather than minting something
        /// with a value nobody can make change for.
        /// </summary>
        public static Thing MakeBond(long denomination)
        {
            if (!CreditDenominations.IsDenomination(denomination)) { return null; }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(BondDefName);
            if (def == null) { return null; }
            Thing thing = ThingMaker.MakeThing(def);
            CompRimroomsBond comp = thing == null ? null : thing.TryGetComp<CompRimroomsBond>();
            if (comp == null) { return null; }
            comp.Issue(denomination);
            // A bond is issued, not found. Nothing about it came out of a coordinate, and
            // stamping it explicitly keeps it from ever being sold as odd goods.
            CompRimroomsOddOrigin marker = thing.TryGetComp<CompRimroomsOddOrigin>();
            if (marker != null) { marker.StampOrigin(ThingOrigin.Outside); }
            return thing;
        }

        /// <summary>
        /// Issues an amount as the **fewest possible bonds, largest first**, and drops them near
        /// a cell — the owner's *"u are always payed in the highest values with least amount of
        /// bonds"*.
        /// </summary>
        /// <param name="remainder">
        /// Credits below the smallest denomination, which cannot be represented as paper. The
        /// caller must keep this in the ledger rather than discard it; money is never rounded
        /// away from a player here.
        /// </param>
        /// <returns>How many bonds were actually placed.</returns>
        public static int IssueTo(Map map, IntVec3 cell, long amount, out long remainder)
        {
            remainder = 0L;
            if (map == null || amount <= 0L) { remainder = Math.Max(0L, amount); return 0; }

            List<KeyValuePair<long, int>> plan = CreditDenominations.Decompose(amount, out remainder);
            int placed = 0;
            for (int index = 0; index < plan.Count; index++)
            {
                for (int made = 0; made < plan[index].Value; made++)
                {
                    Thing bond = MakeBond(plan[index].Key);
                    if (bond == null)
                    {
                        // Could not mint. Give the credits back to the caller rather than
                        // vaporising them.
                        remainder += plan[index].Key;
                        continue;
                    }
                    if (GenPlace.TryPlaceThing(bond, cell, map, ThingPlaceMode.Near))
                    { placed++; }
                    else
                    {
                        bond.Destroy(DestroyMode.Vanish);
                        remainder += plan[index].Key;
                    }
                }
            }
            return placed;
        }

        /// <summary>
        /// Every bond within a radius of a cell, with their total face value. Used by the credit
        /// beacon, which is the owner's own idea: *"like orbital beacons to beable to show that
        /// available credits"*.
        /// </summary>
        public static List<Thing> BondsInRadius(Map map, IntVec3 centre, float radius, out long total)
        {
            var found = new List<Thing>();
            total = 0L;
            if (map == null) { return found; }
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(centre, radius, true))
            {
                if (!cell.InBounds(map)) { continue; }
                List<Thing> things = cell.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    Thing thing = things[index];
                    long value = FaceValueOf(thing);
                    if (value <= 0L) { continue; }
                    found.Add(thing);
                    total += value;
                }
            }
            return found;
        }

        /// <summary>
        /// Destroys a set of bonds and reports their total face value, so the caller can post
        /// one ledger transaction for the lot.
        ///
        /// **Redeeming destroys the paper outright** — the owner's *"without leaveing a dead
        /// item or thing u are using"*. There is no spent certificate left behind to be hauled
        /// somewhere and no zero-value object cluttering a stockpile.
        /// </summary>
        public static long ConsumeBonds(IEnumerable<Thing> bonds)
        {
            long total = 0L;
            if (bonds == null) { return total; }
            var snapshot = new List<Thing>(bonds);
            for (int index = 0; index < snapshot.Count; index++)
            {
                Thing thing = snapshot[index];
                if (thing == null || thing.Destroyed) { continue; }
                long value = FaceValueOf(thing);
                if (value <= 0L) { continue; }
                total += value;
                thing.Destroy(DestroyMode.Vanish);
            }
            return total;
        }
    }
}
