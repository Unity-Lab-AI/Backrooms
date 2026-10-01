using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The company account's side of bearer bonds: paying for one to be printed, taking one
    /// back in, and refunding a print that could not be placed.
    ///
    /// Kept on the campaign component rather than in <see cref="BondService"/> because **this
    /// is the only thing allowed to move the company balance**. Its transactions are idempotent
    /// by operation id, which is what stops a reload mid-action from paying or charging twice,
    /// and a second path to the same money would be a weaker one.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Takes the face value of a bond out of the account so one can be printed.
        /// Fails — and prints nothing — if the balance will not cover it.
        /// </summary>
        internal CompanyActionResult WithdrawForBond(string operationId, long faceValue)
        {
            if (faceValue <= 0L) { return CompanyActionResult.Refused("RR_Bond_InvalidDenomination"); }
            if (BalanceUsd < faceValue) { return CompanyActionResult.Refused("RR_Bond_PrintUnfunded"); }
            return PostTransaction(operationId, -faceValue, "RR_Ledger_BondPrinted", operationId);
        }

        /// <summary>Puts the money back when a printed bond could not be placed.</summary>
        internal CompanyActionResult RefundBond(string operationId, long faceValue)
        {
            if (faceValue <= 0L) { return CompanyActionResult.Refused("RR_Bond_InvalidDenomination"); }
            return PostTransaction(operationId, faceValue, "RR_Ledger_BondRefunded", operationId);
        }

        /// <summary>
        /// Redeems every bond in a radius: destroys the paper and credits the account once for
        /// the total.
        ///
        /// **Counted before anything is destroyed, then destroyed, then posted** — and posted as
        /// a single transaction rather than one per bond, so a reload in the middle cannot
        /// credit a subset twice. The paper is gone in the same operation that pays for it,
        /// which is the owner's *"without leaveing a dead item"*.
        /// </summary>
        internal CompanyActionResult RedeemBondsInRadius(Map map, IntVec3 centre, float radius,
            out long credited, out int consumed)
        {
            credited = 0L;
            consumed = 0;
            if (map == null) { return CompanyActionResult.Refused("RR_Bond_NoMap"); }

            long available;
            List<Thing> bonds = BondService.BondsInRadius(map, centre, radius, out available);
            if (bonds.Count == 0 || available <= 0L)
            { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }

            string operationId = "rr.bond.redeem." + map.uniqueID + "." + centre.x + "." + centre.z +
                "." + (Find.TickManager == null ? 0 : Find.TickManager.TicksGame);

            long destroyed = BondService.ConsumeBonds(bonds);
            if (destroyed <= 0L) { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }

            CompanyActionResult result = PostTransaction(operationId, destroyed,
                "RR_Ledger_BondRedeemed", operationId);
            if (!result.Success) { return result; }

            credited = destroyed;
            consumed = bonds.Count;
            RecordEvent("RR_Event_BondsRedeemed", operationId,
                consumed.ToString("N0"), credited.ToString("N0"));
            return result;
        }

        /// <summary>
        /// Puts named paper back into the account and destroys it.
        ///
        /// **Owner direction, 2026-10-01, verbatim:** *"the bonds i pull out i dont sdeem to be
        /// able to put them back in"*. `RedeemBondsInRadius` already did this for a whole radius
        /// and had exactly one caller — a credit beacon — so a player without one had no route
        /// at all. This is the same operation for a named list, which is what a button on the
        /// paper itself can offer.
        ///
        /// **Destroyed first, then posted**, and posted once for the total under a caller-stable
        /// operation id: a reload between the two cannot credit the same paper twice, and paper
        /// that failed to destroy is never paid for.
        /// </summary>
        internal CompanyActionResult DepositBondPaper(List<Thing> paper, long expected, string operationId)
        {
            if (paper == null || paper.Count == 0 || expected <= 0L)
            { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }
            if (string.IsNullOrWhiteSpace(operationId))
            { return CompanyActionResult.Refused("RR_Bond_InvalidAmount"); }

            long destroyed = BondService.ConsumeBonds(paper);
            if (destroyed <= 0L) { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }

            CompanyActionResult result = PostTransaction(operationId, destroyed,
                "RR_Ledger_BondRedeemed", operationId);
            if (!result.Success) { return result; }
            RecordEvent("RR_Event_BondsRedeemed", operationId,
                paper.Count.ToString("N0"), destroyed.ToString("N0"));
            return result;
        }

        /// <summary>
        /// Replaces a pile of paper with the fewest possible bonds of the same total value.
        ///
        /// **Owner direction, 2026-10-01, verbatim:** *"and and to combine them"*.
        ///
        /// ## Value is conserved, and the ledger is how
        ///
        /// The paper is destroyed and its total **credited**, then the replacement is issued and
        /// its total **debited** — two halves of one operation id. So the account is square at
        /// the end, and if the second half cannot place every bond the unplaced remainder simply
        /// stays credited rather than evaporating between the ledger and the floor. That is the
        /// rule <see cref="IssueBonds"/> already follows and the reason this goes through the
        /// ledger at all instead of swapping objects: the ledger is the only thing in this mod
        /// that cannot lose a credit.
        ///
        /// Credits below the smallest denomination cannot be held as paper, so they stay in the
        /// account. A player's money is never rounded away.
        /// </summary>
        internal CompanyActionResult CombineBondPaper(List<Thing> paper, long expected,
            IntVec3 cell, Map map, string operationId)
        {
            if (paper == null || paper.Count == 0 || expected <= 0L || map == null)
            { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }
            if (string.IsNullOrWhiteSpace(operationId))
            { return CompanyActionResult.Refused("RR_Bond_InvalidAmount"); }

            long destroyed = BondService.ConsumeBonds(paper);
            if (destroyed <= 0L) { return CompanyActionResult.Refused("RR_Bond_NoneInRange"); }

            CompanyActionResult credited = PostTransaction(operationId + ".in", destroyed,
                "RR_Ledger_BondRedeemed", operationId);
            if (!credited.Success) { return credited; }

            long remainder;
            List<KeyValuePair<long, int>> plan = CreditDenominations.Decompose(destroyed, out remainder);
            long payable = CreditDenominations.TotalOf(plan);
            if (payable <= 0L)
            {
                // Everything fell below the smallest denomination. It is already back in the
                // account, which is where it should stay.
                RecordEvent("RR_Event_BondsRedeemed", operationId,
                    paper.Count.ToString("N0"), destroyed.ToString("N0"));
                return credited;
            }

            CompanyActionResult paid = PostTransaction(operationId + ".out", -payable,
                "RR_Ledger_BondIssued", operationId);
            if (!paid.Success) { return paid; }

            long unplaced;
            int issued = BondService.IssueTo(map, cell, payable, out unplaced);
            if (unplaced > 0L)
            {
                PostTransaction(operationId + ".unplaced", unplaced, "RR_Ledger_BondRefunded", operationId);
            }
            RecordEvent("RR_Event_BondsCombined", operationId,
                paper.Count.ToString("N0"), issued.ToString("N0"),
                (payable - unplaced).ToString("N0"));
            return paid;
        }

        /// <summary>
        /// Issues an amount from the account as the fewest possible bonds, largest first, at a
        /// cell — the owner's *"u are always payed in the highest values with least amount of
        /// bonds"*.
        ///
        /// Anything below the smallest denomination **stays in the account** rather than being
        /// rounded away. A player's money is never quietly lost to the shape of the ladder.
        /// </summary>
        internal CompanyActionResult IssueBonds(Map map, IntVec3 cell, long amount,
            out int issued, out long keptInAccount)
        {
            issued = 0;
            keptInAccount = 0L;
            if (map == null) { return CompanyActionResult.Refused("RR_Bond_NoMap"); }
            if (amount <= 0L) { return CompanyActionResult.Refused("RR_Bond_InvalidAmount"); }
            if (amount > BalanceUsd) { return CompanyActionResult.Refused("RR_Bond_Unfunded"); }

            long remainder;
            List<KeyValuePair<long, int>> plan = CreditDenominations.Decompose(amount, out remainder);
            long payable = CreditDenominations.TotalOf(plan);
            keptInAccount = remainder;
            if (payable <= 0L) { return CompanyActionResult.Refused("RR_Bond_BelowSmallest"); }

            string operationId = "rr.bond.issue." + map.uniqueID + "." + cell.x + "." + cell.z +
                "." + (Find.TickManager == null ? 0 : Find.TickManager.TicksGame);
            CompanyActionResult paid = PostTransaction(operationId, -payable,
                "RR_Ledger_BondIssued", operationId);
            if (!paid.Success) { return paid; }

            long unplaced;
            issued = BondService.IssueTo(map, cell, payable, out unplaced);
            if (unplaced > 0L)
            {
                // Some paper could not be placed. Return exactly that much rather than letting
                // the difference disappear between the ledger and the floor.
                PostTransaction(operationId + ".unplaced", unplaced, "RR_Ledger_BondRefunded", operationId);
                keptInAccount += unplaced;
            }
            RecordEvent("RR_Event_BondsIssued", operationId,
                issued.ToString("N0"), (payable - unplaced).ToString("N0"));
            return paid;
        }
    }
}
