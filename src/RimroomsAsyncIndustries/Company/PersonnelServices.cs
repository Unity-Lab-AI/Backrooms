using System.Linq;
using RimroomsAsyncIndustries.Personnel;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed partial class RimroomsCampaignComponent
    {
        // A quote must not expose an overdue cutoff as a new employee's first bill.
        // Projection is read-only: the normal company tick still owns catch-up billing.
        public int NextPayrollTick
        {
            get
            {
                long now = Find.TickManager == null ? 0L : Find.TickManager.TicksGame;
                long next = nextOperatingCostTick;
                if (next <= now)
                { next += ((now - next) / GenDate.TicksPerDay + 1L) * GenDate.TicksPerDay; }
                // The company uses int.MaxValue as its stopped-at-tick-limit sentinel.
                return next >= int.MaxValue ? -1 : (int)next;
            }
        }

        internal CompanyActionResult RegisterHiredStaff(ApplicantRecord offer)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Personnel_BranchUnavailable"); }
            if (offer == null || !offer.charged || offer.refunded || offer.dailyWageUsd <= 0 || !PersonnelRoles.Valid(offer.selectedRole))
            { return CompanyActionResult.Refused("RR_Personnel_InvalidOffer"); }
            StaffRecord existing = staff.FirstOrDefault(s => s.id == offer.StaffId);
            if (existing != null)
            {
                return existing.pawnLoadId == offer.pawnId && existing.dailyWageUsd == offer.dailyWageUsd
                    ? CompanyActionResult.Existing() : CompanyActionResult.Refused("RR_Company_ReceiptMismatch");
            }
            Pawn pawn = offer.pawn;
            if (pawn == null || pawn.Dead || pawn.Destroyed || !pawn.Spawned || pawn.Map != headquarters ||
                pawn.Faction != Faction.OfPlayer || pawn.IsPrisoner || pawn.IsSlave || pawn.GetUniqueLoadID() != offer.pawnId ||
                staff.Any(s => s.pawnLoadId == offer.pawnId))
            { return CompanyActionResult.Refused("RR_Personnel_RegistrationBlocked"); }
            LedgerEntry charge = ledger.FirstOrDefault(e => e.operationId == offer.ChargeId);
            if (charge == null || charge.amountUsd != -offer.onboardingUsd || charge.relatedId != offer.id ||
                charge.reasonKey != "RR_Ledger_HiringOnboarding" || ledger.Any(e => e.operationId == offer.RefundId))
            { return CompanyActionResult.Refused("RR_Company_ReceiptMismatch"); }
            staff.Add(new StaffRecord { id = offer.StaffId, pawn = pawn, pawnLoadId = offer.pawnId, nameAtHire = pawn.LabelShortCap.ToString(),
                role = offer.selectedRole, dailyWageUsd = offer.dailyWageUsd, hiredTick = Find.TickManager.TicksGame, employed = true });
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult AssignCompanyRole(string staffId, string roleId)
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Personnel_BranchUnavailable"); }
            if (!PersonnelRoles.Valid(roleId)) { return CompanyActionResult.Refused("RR_Personnel_InvalidRole"); }
            StaffRecord member = staff.FirstOrDefault(s => s.id == staffId);
            Pawn pawn = member == null ? null : member.pawn;
            if (member == null || !member.employed || pawn == null || pawn.Dead || pawn.Destroyed || !pawn.Spawned ||
                pawn.Faction != Faction.OfPlayer || pawn.IsPrisoner || pawn.IsSlave || pawn.Downed || pawn.InMentalState)
            { return CompanyActionResult.Refused("RR_Personnel_PawnUnavailable"); }
            if (member.role == roleId) { return CompanyActionResult.Existing(); }
            member.role = roleId;
            return CompanyActionResult.Applied();
        }
    }
}
