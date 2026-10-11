using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Selling physical valuables to the parent corporation for credits, and drawing credits
    /// back out as paper.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"a way to turn gold silver gems ingots maybe
    /// needs to exchange for cradits with the company"*, and on the rate, *"above market for
    /// (odd) resources"*.
    ///
    /// ## The rate is the whole design
    ///
    /// | What | Rate | Why |
    /// |---|---|---|
    /// | Odd goods | **×1.5** | The owner's answer. The corporation cannot get these anywhere else, and the player paid for them in gate time, power and risk rather than silver. |
    /// | Ordinary valuables | **×0.85** | Instant, no trader, no caravan, no travel — and the company takes a cut for that. |
    ///
    /// **Traders stay the better price for ordinary goods if you are willing to wait for one.**
    /// That is deliberate: a company that always paid full market would make every trader who
    /// buys valuables pointless, and the convenience would cost nothing. Paying *above* market
    /// for odd goods and *below* for ordinary ones is what makes the two economies pull in
    /// different directions instead of one swallowing the other.
    ///
    /// ## Everything in range, like a trade beacon
    ///
    /// The exchange works on a designated credit beacon's radius, and it takes **everything
    /// tradeable inside it**. That is the same contract a Core orbital trade beacon already
    /// has — what is in the circle is what is on the table — so it borrows a mental model the
    /// player already has rather than inventing selection rules. The radius is the control.
    ///
    /// Bonds are excluded, because a bond is already credits and banking it is a different
    /// action with a different meaning. Pawns and corpses are excluded outright.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>What the company pays for goods that came out of a coordinate.</summary>
        public const float OddExchangeRate = 1.5f;

        /// <summary>What it pays for ordinary valuables. Below market; convenience has a price.</summary>
        public const float OrdinaryExchangeRate = 0.85f;

        /// <summary>
        /// The ordinary rate for a branch that has learned the market. Still below 1, because the
        /// company is a buyer of last resort and never a generous one.
        /// </summary>
        public const float OpenMarketOrdinaryRate = 0.95f;

        /// <summary>
        /// What the company would pay for everything currently in range, split by origin so the
        /// player can see the premium before committing.
        /// </summary>
        public void QuoteExchange(Map map, IntVec3 centre, float radius,
            out long oddValue, out long ordinaryValue, out int itemCount)
        {
            oddValue = 0L;
            ordinaryValue = 0L;
            itemCount = 0;
            if (map == null) { return; }

            foreach (Thing thing in ExchangeableIn(map, centre, radius))
            {
                long value = ValueOf(thing);
                if (value <= 0L) { continue; }
                itemCount++;
                if (OddOriginService.IsOdd(thing)) { oddValue += value; }
                else { ordinaryValue += value; }
            }
        }

        /// <summary>
        /// Sells everything tradeable in range and credits the account once for the lot.
        ///
        /// **Valued first, then destroyed, then posted as a single transaction**, so a reload in
        /// the middle cannot credit a subset twice — the same shape the bond banking uses, for
        /// the same reason.
        /// </summary>
        internal CompanyActionResult ExchangeValuables(Map map, IntVec3 centre, float radius,
            out long credited, out int sold)
        {
            credited = 0L;
            sold = 0;
            if (map == null) { return CompanyActionResult.Refused("RR_Exchange_NoMap"); }

            var taking = new List<Thing>(ExchangeableIn(map, centre, radius));
            long total = 0L;
            for (int index = 0; index < taking.Count; index++)
            {
                total += ValueOf(taking[index]);
            }
            if (total <= 0L) { return CompanyActionResult.Refused("RR_Exchange_NothingInRange"); }

            // Its own id, and the credit checked before anything is destroyed: a refused or
            // duplicate post discovered after the goods are gone pays the player nothing for them.
            string operationId = FreshOperationId("rr.exchange." + map.uniqueID + "." + centre.x + "." +
                centre.z + "." + (Find.TickManager == null ? 0 : Find.TickManager.TicksGame));
            string refusal = CreditRefusal(operationId, total);
            if (refusal != null) { return CompanyActionResult.Refused(refusal); }

            for (int index = 0; index < taking.Count; index++)
            {
                Thing thing = taking[index];
                if (thing != null && !thing.Destroyed) { thing.Destroy(DestroyMode.Vanish); sold++; }
            }

            CompanyActionResult result = PostTransaction(operationId, total,
                "RR_Ledger_ValuablesExchanged", operationId);
            if (!result.Success) { return result; }

            credited = total;
            RecordEvent("RR_Event_ValuablesExchanged", operationId,
                sold.ToString("N0"), credited.ToString("N0"));
            return result;
        }

        /// <summary>
        /// What the company pays for one thing, at the rate its origin earns.
        /// Uses the thing's own market value, so it tracks the game's economy and any mod that
        /// changes a price rather than a table this mod would have to maintain.
        /// </summary>
        private static long ValueOf(Thing thing)
        {
            if (thing == null || thing.Destroyed || thing.def == null) { return 0L; }
            float unit = thing.MarketValue;
            if (float.IsNaN(unit) || float.IsInfinity(unit) || unit <= 0f) { return 0L; }
            // **RR_Cap_OpenMarket** (Commerce, tier 4) improves what the company pays for
            // ORDINARY goods only. The odd rate is the premium the whole economy is built on and
            // is deliberately untouched: a branch learns to stop being fleeced on scrap, it does
            // not learn to make the Backrooms pay better.
            // **READ FROM SETTINGS, NOT FROM THE CONSTANT.** Owner, 2026-10-05, on how to resolve
            // the two balance rows: *"Make them player-visible settings"*. The constants are now
            // the DEFAULTS rather than the values -- so a player who never opens the settings gets
            // exactly what shipped, and anyone who wants a different economy does not need a
            // rebuild to try one.
            //
            // Asked at use time rather than cached, for the same reason everything else here is:
            // a rate read once at startup would ignore the player changing it mid-game, and
            // `RimroomsMod.Settings` is null-guarded because settings can be absent while the mod
            // list is still being resolved.
            Core.RimroomsSettings tuning = Core.RimroomsMod.Settings;
            float ordinary = tuning == null
                ? OrdinaryExchangeRate : tuning.EffectiveOrdinaryExchangeRate;
            RimroomsCampaignComponent marketCampaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (marketCampaign != null && marketCampaign.HasCapability("RR_Cap_OpenMarket"))
            {
                ordinary = tuning == null
                    ? OpenMarketOrdinaryRate : tuning.EffectiveOpenMarketOrdinaryRate;
            }
            float odd = tuning == null ? OddExchangeRate : tuning.EffectiveOddExchangeRate;
            float rate = OddOriginService.IsOdd(thing) ? odd : ordinary;
            double total = (double)unit * Math.Max(1, thing.stackCount) * rate;
            if (total < 0d) { total = 0d; }
            if (total > 1e15d) { total = 1e15d; }
            return (long)Math.Round(total);
        }

        /// <summary>
        /// Items held in containment: their records keep billing for them every day.
        /// </summary>
        private HashSet<Thing> BoundEvidenceItems()
        {
            var bound = new HashSet<Thing>();
            for (int index = 0; index < evidence.Count; index++)
            {
                EvidenceRecord record = evidence[index];
                if (record == null || record.Disposition != EvidenceDisposition.Contained) { continue; }
                Thing item = record.Item;
                if (item != null && !item.Destroyed) { bound.Add(item); }
            }
            return bound;
        }

        /// <summary>
        /// Everything in range the company will take.
        ///
        /// Bonds are skipped because a bond is already credits — banking one is a different
        /// action with a different meaning, and quietly selling a million-credit bond at 0.85
        /// would be a way to destroy a player's money by accident.
        ///
        /// Contained evidence is skipped too. Containment is the choice that keeps a thing off the
        /// market, and selling it out from under the record would leave the branch paying a daily
        /// charge for something that is gone. Destroying it from containment is the way out.
        /// </summary>
        private IEnumerable<Thing> ExchangeableIn(Map map, IntVec3 centre, float radius)
        {
            HashSet<Thing> bound = BoundEvidenceItems();
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(centre, radius, true))
            {
                if (!cell.InBounds(map)) { continue; }
                List<Thing> things = cell.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    Thing thing = things[index];
                    if (thing == null || thing.Destroyed) { continue; }
                    if (thing is Pawn || thing is Corpse) { continue; }
                    if (thing.def == null || thing.def.category != ThingCategory.Item) { continue; }
                    if (thing.def.tradeability == Tradeability.None) { continue; }
                    if (BondService.FaceValueOf(thing) > 0L) { continue; }
                    if (thing.IsBurning()) { continue; }
                    if (bound.Contains(thing)) { continue; }
                    yield return thing;
                }
            }
        }
    }
}
