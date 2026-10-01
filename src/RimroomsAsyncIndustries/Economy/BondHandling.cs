using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// Putting a bond back in, and combining several into fewer.
    ///
    /// **Owner direction, 2026-10-01, verbatim:** *"the bonds i pull out i dont sdeem to be able
    /// to put them back in and and to combine them"*.
    ///
    /// ## Why they could not be put back in
    ///
    /// `RimroomsCampaignComponent.RedeemBondsInRadius` exists, works, and is idempotent — and it
    /// had **exactly one caller**: `CompRimroomsCreditBeacon`. A player who had not built a
    /// credit beacon, or had not connected the withdrawal to the idea of one, had **no action
    /// anywhere** that put paper back into the account. The money was not lost, it was
    /// unreachable, which is the same defect shape as `Discover` having no callers and
    /// `IsLiveGate` needing a mark nobody could set.
    ///
    /// So the action lives on the bond. Select the paper, press the button. The beacon still
    /// works and still redeems a whole radius at once, which is what it is for.
    ///
    /// ## Combining
    ///
    /// *"and to combine them"*. Bonds are issued largest-first, so a stack of small paper only
    /// happens when a player has been paid in pieces or has split a withdrawal. Combining
    /// gathers every bond within a short reach, totals the face value, destroys the paper and
    /// issues the **fewest possible bonds, largest first** — the same `CreditDenominations`
    /// decomposition every other payout uses, so one route cannot drift from another.
    ///
    /// **Value is conserved exactly or nothing happens.** The total is computed, the replacement
    /// is planned against that total, and the paper is only destroyed once the plan accounts for
    /// every credit. Anything that cannot be represented as paper is **returned to the account**
    /// rather than rounded away, which is the rule `IssueBonds` already follows.
    /// </summary>
    public static class BondHandling
    {
        /// <summary>How far a combine reaches. Touching distance, not a warehouse sweep.</summary>
        public const float CombineRadius = 3.9f;

        /// <summary>
        /// Deposits one bond, or one stack of them, into the company account and destroys the
        /// paper.
        ///
        /// The transaction is keyed on the thing's own load id, so a reload between the credit
        /// and the destroy cannot pay twice — the same property `RedeemBondsInRadius` relies on.
        /// </summary>
        public static CompanyActionResult Deposit(Thing bond)
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Bond_NoCompany"); }
            if (bond == null || bond.Destroyed || !bond.Spawned)
            { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }
            long value = BondService.FaceValueOf(bond);
            if (value <= 0L) { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }
            return campaign.DepositBondPaper(new List<Thing> { bond }, value,
                "rr.bond.deposit." + bond.GetUniqueLoadID());
        }

        /// <summary>
        /// Combines every bond within <see cref="CombineRadius"/> of this one into the fewest
        /// possible bonds, largest first.
        ///
        /// Refuses when there is nothing to gain — one bond, or paper that is already the
        /// shortest representation of its total — rather than destroying and recreating the same
        /// pile and calling it work.
        /// </summary>
        public static CompanyActionResult Combine(Thing anchor)
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Bond_NoCompany"); }
            if (anchor == null || anchor.Destroyed || !anchor.Spawned || anchor.Map == null)
            { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }

            long total;
            List<Thing> paper = BondService.BondsInRadius(anchor.Map, anchor.Position,
                CombineRadius, out total);
            if (paper.Count <= 1 || total <= 0L)
            { return CompanyActionResult.Refused("RR_Bond_NothingToCombine"); }

            long remainder;
            List<KeyValuePair<long, int>> plan = CreditDenominations.Decompose(total, out remainder);
            int wanted = plan.Sum(step => step.Value);
            // Already the shortest form. Saying so beats shredding the pile and handing back the
            // same pile.
            if (wanted >= paper.Count && remainder <= 0L)
            { return CompanyActionResult.Refused("RR_Bond_AlreadyCombined"); }

            return campaign.CombineBondPaper(paper, total, anchor.Position, anchor.Map,
                "rr.bond.combine." + anchor.GetUniqueLoadID());
        }
    }
}
