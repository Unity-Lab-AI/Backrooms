using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// A consignment mission: odd goods, **and** a space actually worked to get them.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"have quests and missions and contracts and
    /// stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd)"*, and the
    /// reason for all of it, also verbatim: *"that can give reason for the players to have to
    /// advance and excplore and haul and use the spaces iin the backrooms"*.
    ///
    /// The contract third of that shipped at 0.7.3-dev. This is the mission third, and the whole
    /// question was what makes a mission **distinct from a contract** rather than a contract with
    /// a different title.
    ///
    /// ## Four verbs, and the contract only paid for one
    ///
    /// The owner's reason names four things a demand should make a player do: **advance**,
    /// **explore**, **haul**, and **use the spaces**. An odd-supply contract pays for *haul* and
    /// nothing else — it draws from the union of everything every coordinate ever produced, and
    /// it settles the moment the goods are sitting at headquarters. A branch with a shelf of odd
    /// cotton can fill one without opening a connection at all.
    ///
    /// A mission pays for the other three. It names **one coordinate**, it wants goods **that
    /// coordinate** produced, and it does not settle until a space **at that depth** has been
    /// surveyed further than it had been when the mission was offered. You cannot fill it out of
    /// stock, and you cannot fill it without going deeper and looking around.
    ///
    /// ## What the code would not let the mission be, and why that is recorded here
    ///
    /// The obvious design is *"bring back odd goods from coordinate AI-04"*, verified at
    /// settlement. **It cannot be built.** `ThingOrigin` has three values — Outside, Backrooms,
    /// Unknown — and carries no coordinate at all; and `CompRimroomsOddOrigin.AllowStackWith`
    /// lets odd stacks merge, so a per-coordinate tag would either break stacking or be lost the
    /// first time two stacks met. So the mission names a coordinate in its *demand* — which
    /// definition it wants, drawn from what that place held — and verifies its field condition
    /// against **recorded survey state**, which is real, saved, and cannot be faked by hauling.
    ///
    /// ## No deadline, and that is not an omission
    ///
    /// `check-campaign-absolutes.py` refuses to let this package ship an expiry, and the absolute
    /// applies here exactly as it does to a request: the company waits as long as it takes. A
    /// mission is harder than a contract because of **what** it asks, never because of a clock.
    ///
    /// ## Settlement is the contract's settlement
    ///
    /// Deliberately. `SettleSupplyContracts` gained one call to
    /// <see cref="FieldConditionMet"/> rather than growing a second settlement path, because two
    /// paths that both consume goods and both pay money will eventually disagree about one of
    /// them. A record with no field condition — every contract written before this — reports
    /// true and behaves exactly as it always did.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How many consignment missions may stand open at once. One, against the contracts'
        /// three: a mission asks for a trip rather than a delivery, and three simultaneous
        /// demands for deeper survey work would read as a backlog rather than as a direction.
        /// </summary>
        private const int MaxOpenConsignments = 1;

        /// <summary>
        /// Ticks between considering a mission. Three days against the contracts' one, for the
        /// same reason the cap is lower.
        /// </summary>
        private const int ConsignmentOfferInterval = 180000;

        /// <summary>
        /// How many further rooms a mission asks to have surveyed. Two: enough that it cannot be
        /// satisfied by survey work already done, small enough to be one trip rather than a
        /// campaign.
        /// </summary>
        private const int ConsignmentSurveyStep = 2;

        /// <summary>
        /// On top of <c>OddValueMultiplier</c>. A mission is paid double a contract for the same
        /// goods because it also buys the survey work, and the survey work is the part the
        /// corporation actually wanted.
        /// </summary>
        private const float ConsignmentPremium = 2f;

        /// <summary>Saved. Counts missions offered, so the sequence is stable across reloads.</summary>
        private int consignmentOfferIndex;

        /// <summary>Saved. The tick a mission was last considered.</summary>
        private int lastConsignmentOfferTick = -1;

        internal void ExposeConsignmentMissions()
        {
            Scribe_Values.Look(ref consignmentOfferIndex, "rr_consignmentOfferIndex", 0);
            Scribe_Values.Look(ref lastConsignmentOfferTick, "rr_lastConsignmentOfferTick", -1);
        }

        /// <summary>
        /// Offers a mission when one is due and there is room for it. Settlement is the
        /// contracts' settlement, so there is nothing to call for it here.
        /// </summary>
        internal void UpdateOddConsignmentMissions()
        {
            int now = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
            if (lastConsignmentOfferTick < 0) { lastConsignmentOfferTick = now; }
            if (now - lastConsignmentOfferTick < ConsignmentOfferInterval) { return; }
            lastConsignmentOfferTick = now;
            TryOfferConsignmentMission(now);
        }

        private int OpenConsignmentCount()
        {
            return contracts.Count(c => c != null && c.IsOddConsignment &&
                c.status == ContractStatus.Accepted);
        }

        /// <summary>
        /// The deepest coordinate the branch can still explore further, or null.
        ///
        /// Deepest, because the mission exists to pull a branch downward. Ordinal tie-break on
        /// the id, never list order, because two coordinates at one depth must resolve the same
        /// way on every load — invariant 26.
        /// </summary>
        private CoordinateRecord DeepestExplorableCoordinate()
        {
            CoordinateRecord best = null;
            foreach (CoordinateRecord coordinate in coordinates
                .Where(c => c != null && c.Status != CoordinateStatus.Unavailable)
                .OrderBy(c => c.Id, StringComparer.Ordinal))
            {
                if (coordinate.Rooms == null || coordinate.Rooms.Count == 0) { continue; }
                // Nothing left to ask for here: every room is already surveyed, so a mission
                // demanding more would be unanswerable. That is the failure the contract
                // generator avoids by drawing only from goods a coordinate really produced, and
                // it is the same mistake in a different shape.
                if (coordinate.Rooms.All(room => room.Surveyed)) { continue; }
                if (coordinate.oddGoodsDefNames == null ||
                    coordinate.oddGoodsDefNames.Count == 0) { continue; }
                if (best == null || coordinate.Depth > best.Depth) { best = coordinate; }
            }
            return best;
        }

        private void TryOfferConsignmentMission(int now)
        {
            if (OpenConsignmentCount() >= MaxOpenConsignments) { return; }
            CoordinateRecord target = DeepestExplorableCoordinate();
            if (target == null) { return; }

            // This coordinate's own goods, sorted ordinally. Not the union every contract draws
            // from: the point of a mission is that it is about a place.
            List<string> pool = target.oddGoodsDefNames
                .Where(name => !string.IsNullOrEmpty(name))
                .Distinct(StringComparer.Ordinal)
                .OrderBy(name => name, StringComparer.Ordinal)
                .ToList();
            if (pool.Count == 0) { return; }

            // Deterministic from the branch and the mission counter -- never Rand, so reloading
            // cannot reroll a hard mission into an easy one.
            int roll = Gen.HashCombineInt(campaignSeed, ~consignmentOfferIndex);
            if (roll < 0) { roll = ~roll; }

            string defName = pool[roll % pool.Count];
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (definition == null)
            {
                // Gone with an uninstalled mod. Advance the counter so the branch does not
                // retry the same missing thing forever, and offer nothing this time.
                consignmentOfferIndex++;
                return;
            }

            int surveyed = target.Rooms.Count(room => room.Surveyed);
            int required = Math.Min(target.Rooms.Count, surveyed + ConsignmentSurveyStep);
            if (required <= surveyed) { consignmentOfferIndex++; return; }

            int count = DemandCount(definition, roll);
            long payment = (long)Math.Min(1000000000d,
                DemandPayment(definition, count) * (double)ConsignmentPremium);
            if (count < 1 || payment < 1) { consignmentOfferIndex++; return; }

            var mission = new ContractRecord
            {
                id = "rr.consignment." + (branchId ?? "branch") + "."
                    + consignmentOfferIndex.ToString(),
                templateId = "rr.mission.oddconsignment.v1",
                titleKey = "RR_Contract_OddConsignment_Title",
                coordinateId = target.Id,
                status = ContractStatus.Accepted,
                basePaymentUsd = payment,
                bonusUsd = 0,
                acceptedTick = now,
                requiredThingDefName = defName,
                requiredCount = count,
                deliveredCount = 0,
                requiredDepth = target.Depth,
                requiredSurveyedRooms = required,
            };
            if (contracts.Any(c => c != null && c.id == mission.id))
            { consignmentOfferIndex++; return; }
            contracts.Add(mission);
            consignmentOfferIndex++;
            RecordEvent("RR_Event_OddConsignmentOffered", mission.id,
                count.ToString("N0"), definition.LabelCap.ToString(), target.Label,
                required.ToString("N0"), payment.ToString("N0"));
        }

        /// <summary>
        /// Whether a record's field condition is met, if it has one.
        ///
        /// **A record with no condition reports true**, which is every contract written before
        /// 0.12.41-dev and every plain supply contract written after it. That is what lets one
        /// settlement path serve both kinds.
        ///
        /// Checked against **any** coordinate deep enough rather than against the named one on
        /// purpose. The coordinate a mission names can fail generation and go
        /// <see cref="CoordinateStatus.Unavailable"/> through no fault of the player, and a
        /// mission that becomes permanently unsatisfiable is worse than one that is satisfied
        /// somewhere else at the same depth. What the corporation is buying is that the branch
        /// has worked a space that deep -- not which one.
        /// </summary>
        internal bool FieldConditionMet(ContractRecord contract)
        {
            if (contract == null) { return false; }
            if (contract.requiredSurveyedRooms <= 0) { return true; }
            int depth = contract.requiredDepth < 1 ? 1 : contract.requiredDepth;
            foreach (CoordinateRecord coordinate in coordinates)
            {
                if (coordinate == null || coordinate.Rooms == null) { continue; }
                if (coordinate.Depth < depth) { continue; }
                if (coordinate.Rooms.Count(room => room.Surveyed)
                    >= contract.requiredSurveyedRooms) { return true; }
            }
            return false;
        }

        /// <summary>
        /// How far along a record's field condition is, for the pane. Returns the best surveyed
        /// count at or below the required depth, so a player can see progress rather than only
        /// a yes or a no.
        /// </summary>
        public int FieldConditionProgress(ContractRecord contract)
        {
            if (contract == null || contract.requiredSurveyedRooms <= 0) { return 0; }
            int depth = contract.requiredDepth < 1 ? 1 : contract.requiredDepth;
            int best = 0;
            foreach (CoordinateRecord coordinate in coordinates)
            {
                if (coordinate == null || coordinate.Rooms == null) { continue; }
                if (coordinate.Depth < depth) { continue; }
                int surveyed = coordinate.Rooms.Count(room => room.Surveyed);
                if (surveyed > best) { best = surveyed; }
            }
            return best;
        }
    }
}
