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
