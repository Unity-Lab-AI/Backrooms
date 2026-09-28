using System;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Personnel
{
    public sealed partial class RimroomsPersonnelComponent
    {
        public CompanyActionResult HireApplicant(string applicantId, string roleId)
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            ApplicantRecord offer = FindOffer(applicantId);
            if (offer == null) { return Refuse("RR_Personnel_InvalidOffer"); }
            if (offer.status == ApplicantStatus.Hired) { return CompanyActionResult.Existing(); }
            if (offer.status != ApplicantStatus.Offered || Now >= offer.expiresTick) { return Refuse("RR_Personnel_OfferClosed"); }
            if (!PersonnelRoles.Valid(roleId)) { return Refuse("RR_Personnel_InvalidRole"); }
            if (offers.Any(o => o != offer && (o.status == ApplicantStatus.Hiring || o.status == ApplicantStatus.Releasing)))
            { return Refuse("RR_Personnel_FinishHire"); }
            if (!EligibleHeldApplicant(offer)) { return Fail(offer, "RR_Personnel_CustodyChanged"); }
            if (Campaign.BalanceUsd < offer.onboardingUsd) { return Refuse("RR_Company_InsufficientFunds"); }
            Map map = Campaign.Headquarters;
            IntVec3 cell;
            if (!LiveHeadquarters(map)) { return Refuse("RR_Personnel_MapUnavailable"); }
            if (!TryEntry(offer.pawn, map, out cell)) { return Refuse("RR_Personnel_ArrivalBlocked"); }
            offer.selectedRole = roleId;
            offer.hiringMap = map;
            offer.arrivalCell = cell;
            offer.acceptedTick = Now;
            offer.status = ApplicantStatus.Hiring;
            return ContinueHire(offer);
        }

        public CompanyActionResult RetryHire(string applicantId)
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            ApplicantRecord offer = FindOffer(applicantId);
            if (offer == null) { return Refuse("RR_Personnel_InvalidOffer"); }
            if (offer.status == ApplicantStatus.Hired) { return CompanyActionResult.Existing(); }
            if (offer.status != ApplicantStatus.Hiring || offer.refunded) { return Refuse("RR_Personnel_OfferClosed"); }
            return ContinueHire(offer);
        }

        private CompanyActionResult ContinueHire(ApplicantRecord offer)
        {
            busy = true;
            try
            {
                CompanyActionResult receipts = ReconcileMoney(offer);
                if (!receipts.Success) { return receipts; }
                if (offer.refunded) { return Fail(offer, "RR_Personnel_OfferClosed"); }
                Pawn pawn = offer.pawn;
                if (pawn == null || pawn.GetUniqueLoadID() != offer.pawnId || pawn.Dead || pawn.Destroyed || pawn.Discarded)
                { return Fail(offer, "RR_Personnel_PawnMissing"); }
                if (!LiveHeadquarters(offer.hiringMap) || offer.hiringMap != Campaign.Headquarters)
                { return Fail(offer, "RR_Personnel_MapUnavailable"); }
                if (Find.WorldPawns.Contains(pawn) || (pawn.holdingOwner != null && pawn.holdingOwner != held) ||
                    pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger() ||
                    (pawn.Faction != null && pawn.Faction != Faction.OfPlayer) ||
                    (pawn.Faction == Faction.OfPlayer && !offer.recruitStarted))
                { return Fail(offer, "RR_Personnel_CustodyChanged"); }

                StaffRecord staff = Campaign.Staff.FirstOrDefault(s => s.Id == offer.StaffId);
                if (staff != null)
                {
                    if (staff.Pawn != pawn || staff.DailyWageUsd != offer.dailyWageUsd || !offer.charged)
                    { return Fail(offer, "RR_Company_ReceiptMismatch"); }
                    offer.registered = true;
                    offer.status = ApplicantStatus.Hired;
                    offer.failureKey = null;
                    return CompanyActionResult.Existing();
                }
                if (Campaign.Staff.Any(s => s.Pawn == pawn)) { return Fail(offer, "RR_Personnel_CustodyChanged"); }
                if (!pawn.Spawned)
                {
                    if (pawn.holdingOwner != held || offer.everArrived || offer.recruitStarted)
                    { return Fail(offer, "RR_Personnel_CustodyChanged"); }
                    if (!EntryIsClear(pawn, offer.hiringMap, offer.arrivalCell) &&
                        !TryEntry(pawn, offer.hiringMap, out offer.arrivalCell))
                    { return Fail(offer, "RR_Personnel_ArrivalBlocked"); }
                }
                else if (pawn.Map != offer.hiringMap)
                { return Fail(offer, "RR_Personnel_CustodyChanged"); }

                CompanyActionResult charge = Campaign.PostTransaction(offer.ChargeId, -offer.onboardingUsd,
                    "RR_Ledger_HiringOnboarding", offer.id);
                if (!charge.Success) { return Fail(offer, charge.MessageKey); }
                offer.charged = true;
                if (!pawn.Spawned)
                {
                    // The journal owns the strong reference before GenSpawn removes the holder.
                    offer.arrivalAttempted = true;
                    offer.arrivalFailedOffsite = false;
                    GenSpawn.Spawn(pawn, offer.arrivalCell, offer.hiringMap, Rot4.South, WipeMode.VanishOrMoveAside);
                    if (!pawn.Spawned || pawn.Map != offer.hiringMap)
                    { PreserveDetachedPawn(offer); return Fail(offer, "RR_Personnel_ArrivalInterrupted"); }
                }
                offer.everArrived = true;
                offer.arrivalFailedOffsite = false;
                if (!offer.recruited)
                {
                    offer.recruitStarted = true;
                    if (pawn.Faction != Faction.OfPlayer) { RecruitUtility.Recruit(pawn, Faction.OfPlayer); }
                    // A prior native call may have changed faction before throwing. Never replay its population/priority reset.
                    if (pawn.Faction != Faction.OfPlayer || pawn.workSettings == null || !pawn.workSettings.Initialized ||
                        pawn.playerSettings == null || pawn.needs == null || pawn.IsPrisoner || pawn.IsSlave)
                    { return Fail(offer, "RR_Personnel_RecruitInterrupted"); }
                    offer.recruited = true;
                }
                CompanyActionResult registered = Campaign.RegisterHiredStaff(offer);
                if (!registered.Success) { return Fail(offer, registered.MessageKey); }
                offer.registered = true;
                offer.status = ApplicantStatus.Hired;
                offer.failureKey = null;
                return CompanyActionResult.Applied();
            }
            catch (Exception exception)
            {
                PreserveDetachedPawn(offer);
                Log.Warning("[Rimrooms][Personnel] Hire interrupted for " + offer.id + ": " + exception.GetType().Name);
                return Fail(offer, "RR_Personnel_HireInterrupted");
            }
            finally { busy = false; }
        }

        public CompanyActionResult CancelUnarrivedHire(string applicantId)
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            ApplicantRecord offer = FindOffer(applicantId);
            if (offer == null) { return Refuse("RR_Personnel_InvalidOffer"); }
            if (offer.status == ApplicantStatus.Cancelled) { return CompanyActionResult.Existing(); }
            if (offer.status != ApplicantStatus.Hiring || (offer.arrivalAttempted && !offer.arrivalFailedOffsite) || offer.everArrived || offer.recruitStarted ||
                offer.registered || !EligibleHeldApplicant(offer) || Campaign.Staff.Any(s => s.Pawn == offer.pawn))
            { return Refuse("RR_Personnel_CannotCancel"); }
            CompanyActionResult receipt = ReconcileMoney(offer);
            if (!receipt.Success) { return receipt; }
            if (offer.charged && !offer.refunded)
            {
                CompanyActionResult refund = Campaign.PostTransaction(offer.RefundId, offer.onboardingUsd,
                    "RR_Ledger_HiringRefund", offer.id);
                if (!refund.Success) { return Fail(offer, refund.MessageKey); }
                offer.refunded = true;
            }
            return StartRelease(offer, ApplicantRelease.Cancelled);
        }

        private CompanyActionResult ReconcileMoney(ApplicantRecord offer)
        {
            LedgerEntry charge = Campaign.Ledger.FirstOrDefault(e => e.OperationId == offer.ChargeId);
            LedgerEntry refund = Campaign.Ledger.FirstOrDefault(e => e.OperationId == offer.RefundId);
            if ((charge != null && (charge.AmountUsd != -offer.onboardingUsd || charge.relatedId != offer.id || charge.ReasonKey != "RR_Ledger_HiringOnboarding")) ||
                (refund != null && (refund.AmountUsd != offer.onboardingUsd || refund.relatedId != offer.id || refund.ReasonKey != "RR_Ledger_HiringRefund")) ||
                (offer.charged && charge == null) || (offer.refunded && refund == null) || (refund != null && charge == null))
            { return Fail(offer, "RR_Company_ReceiptMismatch"); }
            offer.charged = charge != null;
            offer.refunded = refund != null;
            return CompanyActionResult.Applied();
        }

        private bool EligibleHeldApplicant(ApplicantRecord offer)
        {
            Pawn pawn = offer.pawn;
            return pawn != null && !pawn.Dead && !pawn.Destroyed && !pawn.Discarded && !pawn.Downed && !pawn.Spawned &&
                pawn.holdingOwner == held && pawn.GetUniqueLoadID() == offer.pawnId && pawn.Faction == null &&
                !Find.WorldPawns.Contains(pawn) && !pawn.IsPrisoner && !pawn.IsSlave && !pawn.IsQuestLodger();
        }
        private static bool TryEntry(Pawn pawn, Map map, out IntVec3 cell)
        {
            return RCellFinder.TryFindRandomPawnEntryCell(out cell, map, 0f, false, c => EntryIsClear(pawn, map, c));
        }
        private static bool EntryIsClear(Pawn pawn, Map map, IntVec3 cell)
        {
            if (map == null || !cell.IsValid || !cell.InBounds(map) || !cell.Standable(map) || cell.Fogged(map) ||
                !GenSpawn.CanSpawnAt(pawn.def, cell, map, Rot4.South, false) || !map.reachability.CanReachColony(cell)) { return false; }
            return cell.GetThingList(map).All(t => !(t is Pawn) && !(t is Corpse) && t.def.category != ThingCategory.Building &&
                t.def.category != ThingCategory.Item && !GenSpawn.SpawningWipes(pawn.def, t.def));
        }
    }
}
