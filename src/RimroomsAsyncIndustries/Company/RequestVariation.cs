using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The four things the generator was not reading about the branch it is generating for.
    ///
    /// **Owner direction, verbatim:** *"Generate bounded story variations from client/faction,
    /// coordinate, staffing, discovered rules, company tier, previous outcomes, opening duration,
    /// and available equipment"*.
    ///
    /// Coordinate, staffing, discovered rules and available equipment all reached generation at
    /// 0.12.12-dev through `CanTakeRoute`. **Client/faction identity, company tier, previous
    /// outcome and opening duration did not**, and that is what this adds.
    ///
    /// ## Bias, never a filter, and the distinction is load-bearing
    ///
    /// `FamilyEligible` already decides what is *answerable*: two takeable routes of two
    /// different kinds, so no dead card can ever be offered. Nothing here touches that. **Adding
    /// a fifth hard condition is how a branch ends up with nothing on the table at all** — the
    /// same trap `CoordinateMotif` names for room themes, where the theme is a weight rather than
    /// a filter so a coordinate can never run out of legal archetypes.
    ///
    /// So this weights the choice the generator was already making arbitrarily. `TimesAsked`
    /// least-first stays exactly as it is, because that is the fairness rule that stops the
    /// company repeating its cheapest request forever; the weighting applies **inside the tie**,
    /// which is precisely where `roll % freshest.Count` was choosing at random.
    ///
    /// ## Nothing new is stored, and no def field was added
    ///
    /// Every input is read off state the branch already keeps:
    ///
    /// | Input | Read from |
    /// |---|---|
    /// | **Company tier** | how many supply tiers the branch has opened, against the family's `paymentUsd` |
    /// | **Previous outcome** | `RequestStatus.Cancelled` counts in the branch's own request history |
    /// | **Opening duration** | `PortalWindowTier` on the branch's gates, against the family's `arc` |
    /// | **Client/faction identity** | how many factions in this world are hostile to the player |
    ///
    /// A `faction` field on the def was the obvious alternative and was refused: there is no
    /// authored content behind it, so it would have been a field nothing filled — the hollow
    /// unlock this package keeps refusing elsewhere. What a player's **world** looks like is real
    /// data that varies between campaigns, which is what the row is asking for.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How strongly each input may pull. Deliberately small and bounded.
        ///
        /// **Every factor stays inside [1/Pull, Pull]**, so four of them compounding can at worst
        /// make one family a few times likelier than another — never certain and never
        /// impossible. The owner's word is *"bounded"* and this is the bound: a variation system
        /// that can drive a weight to zero is a filter wearing a weight's clothes, and it would
        /// reintroduce the empty-table risk `FamilyEligible` exists to prevent.
        /// </summary>
        private const float MaximumPull = 1.6f;

        private static float Clamped(float factor)
        {
            if (float.IsNaN(factor) || float.IsInfinity(factor)) { return 1f; }
            return Mathf.Clamp(factor, 1f / MaximumPull, MaximumPull);
        }

        /// <summary>How many supply tiers this branch has opened. The company tier, plainly.</summary>
        public int CompanyTier
        {
            get { return unlockedSupplyTiers == null ? 0 : unlockedSupplyTiers.Count; }
        }

        /// <summary>
        /// The longest window any of this branch's gates can hold, as a tier.
        ///
        /// The **best** gate rather than an average: a branch with one well-researched gate can
        /// do long-field work, and averaging would let a second rough gate hide that.
        /// </summary>
        public int BestOpeningTier
        {
            get
            {
                int best = 0;
                if (headquarters == null || headquarters.listerBuildings == null) { return best; }
                foreach (Building building in headquarters.listerBuildings.allBuildingsColonist)
                {
                    Gate.CompRimroomsGate gate = building.TryGetComp<Gate.CompRimroomsGate>();
                    if (gate == null || !gate.IsDesignated) { continue; }
                    if (gate.PortalWindowTier > best) { best = gate.PortalWindowTier; }
                }
                return best;
            }
        }

        /// <summary>How many times the branch has turned this family down.</summary>
        private int TimesCancelled(string defName)
        {
            int count = 0;
            for (int index = 0; index < requests.Count; index++)
            {
                RequestRecord record = requests[index];
                if (record != null && record.requestDefName == defName
                    && record.status == RequestStatus.Cancelled)
                { count++; }
            }
            return count;
        }

        /// <summary>
        /// Factions in this world that are hostile to the player.
        ///
        /// **The client/faction input, read off the world the player actually generated.** Asked
        /// of Core's own faction manager and its own hostility test, so every faction any mod
        /// adds counts and nothing here keeps a list.
        /// </summary>
        public int HostileFactionCount
        {
            get
            {
                if (Find.FactionManager == null || Faction.OfPlayer == null) { return 0; }
                int count = 0;
                foreach (Faction faction in Find.FactionManager.AllFactionsListForReading)
                {
                    if (faction == null || faction.IsPlayer || faction.defeated) { continue; }
                    if (faction.HostileTo(Faction.OfPlayer)) { count++; }
                }
                return count;
            }
        }

        /// <summary>
        /// How much this branch's situation favours being asked for this family.
        ///
        /// One multiplied by four bounded factors, each one a fact about the branch that the
        /// generator could not see before.
        /// </summary>
        internal float GeneratedFamilyWeight(RimroomsRequestDef definition)
        {
            if (definition == null) { return 0f; }
            float weight = 1f;

            // **COMPANY TIER against what the family pays.** A tier-five branch being asked for a
            // two-hundred-credit errand is the company not noticing it grew, and a brand new one
            // being asked for the most lucrative job on the books is the opposite mistake.
            // Expressed as the distance between where the branch sits on the tier ladder and
            // where the family sits on the payment ladder.
            int tiers = Math.Max(1, RimroomsCampaignComponent.AllSupplyTiers().Count);
            float branchStanding = CompanyTier / (float)tiers;
            float familyStanding = PaymentStanding(definition);
            weight *= Clamped(1f + (0.8f - Math.Abs(branchStanding - familyStanding)));

            // **PREVIOUS OUTCOME.** A family the branch has turned down repeatedly is one the
            // company stops leading with. Damping rather than exclusion: *"the player may
            // cancel, the corporation may not"* cuts both ways -- the corporation is allowed to
            // keep asking, it just reads the room.
            weight *= Clamped(1f / (1f + 0.25f * TimesCancelled(definition.defName)));

            // **OPENING DURATION against how deep the family's arc is.** Arc numbers rise with
            // how far into the Backrooms the work goes, and work that goes deep needs a window
            // that stays open. A branch still on the base window is led toward near work.
            float windowReach = Mathf.Clamp01(BestOpeningTier / 4f);
            float arcDepth = Mathf.Clamp01((definition.arc - 1) / 5f);
            weight *= Clamped(1f + (0.7f - Math.Abs(windowReach - arcDepth)));

            // **CLIENT AND FACTION IDENTITY, read as what the world around the branch is like.**
            // A branch with hostile neighbours is a branch whose corporation has other things on
            // its mind than the early errands, so the later arcs gain and the first ones ease
            // off. Small on purpose: this is the input with the least authored content behind it.
            float pressure = Mathf.Clamp01(HostileFactionCount / 5f);
            weight *= Clamped(1f + 0.3f * (arcDepth - 0.5f) * pressure * 2f);

            return weight <= 0f ? 0.0001f : weight;
        }

        /// <summary>
        /// Where a family sits on the payment ladder, from zero to one.
        ///
        /// Measured against the **other generated families** rather than against a constant, so a
        /// rebalance of the catalogue cannot silently make every family read as cheap. Returns a
        /// half when there is nothing to compare against, which weights nothing either way.
        /// </summary>
        private static float PaymentStanding(RimroomsRequestDef definition)
        {
            List<RimroomsRequestDef> all = RimroomsRequestDef.AllInOrder()
                .Where(candidate => candidate != null && !candidate.tutorial).ToList();
            if (all.Count == 0) { return 0.5f; }
            long highest = all.Max(candidate => candidate.paymentUsd);
            if (highest <= 0L) { return 0.5f; }
            return Mathf.Clamp01(definition.paymentUsd / (float)highest);
        }

        /// <summary>
        /// A weighted draw over the tied families, derived and never `Rand`.
        ///
        /// **Sorted before anything indexes it** -- invariant 26, and the same reason the
        /// materials, the archetypes, the fixture tells and the certifications all sort first.
        /// The caller has already sorted ordinally; this keeps that order and walks it, so the
        /// same branch asked at the same point gets the same request and a save reloaded twice
        /// does not produce two different campaigns.
        /// </summary>
        internal RimroomsRequestDef DrawWeightedFamily(List<RimroomsRequestDef> freshest, int roll)
        {
            if (freshest == null || freshest.Count == 0) { return null; }
            float total = 0f;
            for (int index = 0; index < freshest.Count; index++)
            { total += GeneratedFamilyWeight(freshest[index]); }
            if (total <= 0f) { return freshest[Math.Abs(roll) % freshest.Count]; }

            float pick = (Math.Abs(roll) % 100000) / 100000f * total;
            for (int index = 0; index < freshest.Count; index++)
            {
                pick -= GeneratedFamilyWeight(freshest[index]);
                if (pick <= 0f) { return freshest[index]; }
            }
            return freshest[freshest.Count - 1];
        }
    }
}
