using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Contracts that demand goods which came out of a Backrooms coordinate, and will not take
    /// the ordinary equivalent.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"have quests and missions and contracts and
    /// stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd) and the such
    /// for all things materials and resources ect ect that can give reason for the players to
    /// have to advance and excplore and haul and use the spaces iin the backrooms"*
    ///
    /// The marker built in 0.7.2-dev is the substrate; this is the thing that reads it. Without
    /// a buyer, "(odd)" is a label nobody cares about.
    ///
    /// ## Demands are drawn from what coordinates actually held
    ///
    /// The tempting implementation is to pick any thing definition in the game and ask for a
    /// pile of it. That produces demands a player **cannot possibly meet** — a thousand odd
    /// cotton is unanswerable if no space the branch has ever opened contained cotton, and the
    /// player would spend hours looking for something that was never down there.
    ///
    /// So every coordinate records the distinct definitions it really produced, at generation,
    /// and a demand is only ever drawn from the union of those records. That also gives the
    /// loop its shape: open a space, see what it holds, and buyers appear who want it.
    ///
    /// ## Bounded, deterministic, and saved
    ///
    /// At most <see cref="MaxOpenSupplyContracts"/> stand open at once, so a long campaign
    /// cannot accumulate an unbounded backlog. The choice of definition, quantity and price is
    /// derived from the branch seed and a saved counter rather than from `Rand`, so the same
    /// branch offers the same sequence and reloading a save cannot reroll a demand into an
    /// easier one.
    ///
    /// ## Payment
    ///
    /// Settlement goes through the same idempotent <c>PostTransaction</c> every other contract
    /// uses, keyed by operation id, so a delivery cannot be paid twice — including across a
    /// save/reload in the middle of one.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>How many odd-supply contracts may stand open at once.</summary>
        private const int MaxOpenSupplyContracts = 3;

        /// <summary>Ticks between offers. Roughly a day, so demand arrives at a readable pace.</summary>
        private const int SupplyOfferInterval = 60000;

        /// <summary>
        /// Multiplier on the goods' market value. Odd goods are worth materially more than the
        /// ordinary kind because the buyer cannot source them anywhere else, and because the
        /// player paid for them in gate time, power and risk rather than in silver.
        /// </summary>
        private const float OddValueMultiplier = 6f;

        /// <summary>Saved. Counts offers made, so the sequence is stable across reloads.</summary>
        private int supplyOfferIndex;

        /// <summary>Saved. The tick an offer was last considered.</summary>
        private int lastSupplyOfferTick = -1;

        internal void ExposeSupplyContracts()
        {
            Scribe_Values.Look(ref supplyOfferIndex, "rr_supplyOfferIndex", 0);
            Scribe_Values.Look(ref lastSupplyOfferTick, "rr_lastSupplyOfferTick", -1);
        }

        /// <summary>
        /// Offers a new demand when one is due and there is room for it, then settles any
        /// demand the branch can now meet. Called on the same cadence as the other contract
        /// work.
        /// </summary>
        internal void UpdateOddSupplyContracts()
        {
            int now = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
            if (lastSupplyOfferTick < 0) { lastSupplyOfferTick = now; }
            if (now - lastSupplyOfferTick >= SupplyOfferInterval)
            {
                lastSupplyOfferTick = now;
                TryOfferSupplyContract(now);
            }
            SettleSupplyContracts();
        }

        private int OpenSupplyContractCount()
        {
            return contracts.Count(c => c.IsOddSupply && c.status == ContractStatus.Accepted);
        }

        /// <summary>
        /// Every definition any discovered coordinate actually produced, in a stable order.
        /// Sorted rather than enumerated in discovery order so the deterministic pick below
        /// does not silently change when coordinates are discovered in a different sequence.
        /// </summary>
        private List<string> KnownOddGoods()
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (CoordinateRecord coordinate in coordinates)
            {
                if (coordinate == null || coordinate.oddGoodsDefNames == null) { continue; }
                foreach (string name in coordinate.oddGoodsDefNames)
                {
                    if (!string.IsNullOrEmpty(name)) { names.Add(name); }
                }
            }
            var ordered = names.ToList();
            ordered.Sort(StringComparer.Ordinal);
            return ordered;
        }

        private void TryOfferSupplyContract(int now)
        {
            if (OpenSupplyContractCount() >= MaxOpenSupplyContracts) { return; }
            List<string> pool = KnownOddGoods();
            if (pool.Count == 0) { return; }

            // Deterministic from the branch and the offer counter -- never Rand, so a reload
            // cannot reroll a hard demand into an easy one.
            int roll = Gen.HashCombineInt(campaignSeed, supplyOfferIndex);
            if (roll < 0) { roll = ~roll; }

            string defName = pool[roll % pool.Count];
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (definition == null)
            {
                // The definition is gone -- an uninstalled mod, most likely. Skip this offer
                // rather than inventing a substitute; the counter still advances so the branch
                // does not retry the same missing thing forever.
                supplyOfferIndex++;
                return;
            }

            int count = DemandCount(definition, roll);
            long payment = DemandPayment(definition, count);
            if (count < 1 || payment < 1) { supplyOfferIndex++; return; }

            var contract = new ContractRecord
            {
                id = "rr.supply." + (branchId ?? "branch") + "." + supplyOfferIndex.ToString(),
                templateId = "rr.supply.odd.v1",
                titleKey = "RR_Contract_OddSupply_Title",
                coordinateId = null,
                status = ContractStatus.Accepted,
                basePaymentUsd = payment,
                bonusUsd = 0,
                acceptedTick = now,
                requiredThingDefName = defName,
                requiredCount = count,
                deliveredCount = 0,
            };
            if (contracts.Any(c => c.id == contract.id)) { supplyOfferIndex++; return; }
            contracts.Add(contract);
            supplyOfferIndex++;
            RecordEvent("RR_Event_OddSupplyOffered", contract.id,
                count.ToString("N0"), definition.LabelCap.ToString(), payment.ToString("N0"));
        }

        /// <summary>
        /// How many the buyer wants. Scaled by the thing's own stack limit so a demand is
        /// expressed in the units the game already uses -- a few stacks of a stackable
        /// resource, a handful of a piece of furniture -- rather than a flat number that would
        /// be trivial for one and impossible for another.
        /// </summary>
        private static int DemandCount(ThingDef definition, int roll)
        {
            int limit = Math.Max(1, definition.stackLimit);
            if (limit == 1)
            {
                // Furniture and other unstackables: the owner's "10 uninstalled electic stoves".
                return 2 + (roll / 7) % 9;
            }
            int stacks = 1 + (roll / 7) % 4;
            return Math.Min(limit * stacks, limit * 4);
        }

        /// <summary>
        /// What the buyer pays. Built from the thing's own market value so it tracks the game's
        /// economy and any mod that changes it, rather than from a table this mod would have to
        /// maintain against 294 other mods.
        /// </summary>
        private static long DemandPayment(ThingDef definition, int count)
        {
            float unit = definition.BaseMarketValue;
            if (float.IsNaN(unit) || float.IsInfinity(unit) || unit <= 0f) { unit = 1f; }
            double total = (double)unit * count * OddValueMultiplier;
            if (total < 1d) { total = 1d; }
            if (total > 1000000000d) { total = 1000000000d; }
            return (long)Math.Round(total);
        }

        /// <summary>
        /// Pays out every open demand the branch can now meet, and consumes the goods.
        ///
        /// Only odd goods count, and only ones actually at headquarters. The check runs through
        /// <see cref="OddOriginService.IsOdd"/> so an uninstalled building held in a minified
        /// wrapper is read correctly -- which is the owner's own example and the case that
        /// would silently never settle if the wrapper were asked directly.
        /// </summary>
        private void SettleSupplyContracts()
        {
            if (headquarters == null) { return; }
            foreach (ContractRecord contract in contracts)
            {
                if (contract == null || !contract.IsOddSupply) { continue; }
                if (contract.status != ContractStatus.Accepted) { continue; }
                // A consignment mission wants the space worked as well as the goods delivered.
                // A record with no field condition -- every plain contract -- reports true, so
                // this is one settlement path rather than two that could disagree about paying.
                if (!FieldConditionMet(contract)) { continue; }

                List<Thing> matching = MatchingOddGoods(contract.requiredThingDefName);
                int available = 0;
                for (int index = 0; index < matching.Count; index++)
                { available += Math.Max(1, matching[index].stackCount); }
                if (available < contract.requiredCount) { continue; }

                // Payment first, because it is the idempotent step. If the transaction has
                // already been applied under this operation id -- a save reloaded mid-delivery,
                // say -- it reports that rather than paying twice, and the goods are consumed
                // exactly once either way.
                string operationId = contract.id + ":odd-supply-payment";
                CompanyActionResult result = PostTransaction(operationId, contract.basePaymentUsd,
                    "RR_Ledger_OddSupplyPayment", contract.id);
                if (!result.Success) { continue; }

                int remaining = contract.requiredCount;
                for (int index = 0; index < matching.Count && remaining > 0; index++)
                {
                    Thing thing = matching[index];
                    if (thing == null || thing.Destroyed) { continue; }
                    int take = Math.Min(remaining, Math.Max(1, thing.stackCount));
                    thing.SplitOff(take).Destroy(DestroyMode.Vanish);
                    remaining -= take;
                }
                contract.deliveredCount = contract.requiredCount - Math.Max(0, remaining);
                contract.settlementOperationId = operationId;
                contract.completedTick = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
                contract.status = ContractStatus.Completed;
                RecordEvent("RR_Event_OddSupplySettled", contract.id,
                    contract.basePaymentUsd.ToString("N0"));
            }
        }

        /// <summary>
        /// Odd goods of one definition held at headquarters. Reserved and burning things are
        /// excluded for the same reason any Core delivery excludes them: taking something a
        /// colonist is standing over is how a job faults.
        /// </summary>
        private List<Thing> MatchingOddGoods(string defName)
        {
            var found = new List<Thing>();
            if (headquarters == null || headquarters.listerThings == null) { return found; }
            List<Thing> all = headquarters.listerThings.AllThings;
            if (all == null) { return found; }
            for (int index = 0; index < all.Count; index++)
            {
                Thing thing = all[index];
                if (thing == null || thing.Destroyed || thing is Pawn || !thing.Spawned) { continue; }
                // Delivered goods only: loose items, or furniture uninstalled into its crate. An
                // installed stove or bench of the right kind is the branch's working equipment,
                // and an order for "uninstalled stoves" must never take one off the floor.
                if (thing.def == null || thing.def.category != ThingCategory.Item) { continue; }
                // Something a colonist has claimed for a job is not on the table either; taking
                // it out from under the job is how the job faults.
                if (thing.Map != null && thing.Map.reservationManager != null &&
                    thing.Map.reservationManager.IsReservedByAnyoneOf(thing, Faction.OfPlayer)) { continue; }
                Thing subject = thing is MinifiedThing ? ((MinifiedThing)thing).InnerThing : thing;
                if (subject == null || subject.def == null) { continue; }
                if (!string.Equals(subject.def.defName, defName, StringComparison.Ordinal)) { continue; }
                if (!OddOriginService.IsOdd(thing)) { continue; }
                if (thing.IsBurning()) { continue; }
                found.Add(thing);
            }
            return found;
        }
    }
}
