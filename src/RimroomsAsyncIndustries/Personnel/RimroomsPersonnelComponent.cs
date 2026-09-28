using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Personnel
{
    /// <summary>RR-STA: only this holder deep-saves unspawned candidates; the company owns money and employees.</summary>
    public sealed partial class RimroomsPersonnelComponent : GameComponent, IThingHolder
    {
        public const int CurrentSchemaVersion = 1;
        private int schemaVersion = CurrentSchemaVersion;
        private string branchId;
        private int sequence;
        private int nextRequestTick;
        private int archivedOfferCount;
        private List<ApplicantRecord> offers = new List<ApplicantRecord>();
        private ThingOwner<Pawn> held;
        private string faultKey;
        private bool busy;
        public RimroomsPersonnelComponent(Game game) { held = new ThingOwner<Pawn>(this); }
        public IThingHolder ParentHolder { get { return null; } }
        public ThingOwner GetDirectlyHeldThings() { return held; }
        public void GetChildHolders(List<IThingHolder> outChildren) { ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, held); }
        public IReadOnlyList<ApplicantRecord> Offers { get { return offers; } }
        public int NextRequestTick { get { return nextRequestTick; } }
        public string FaultKey { get { return faultKey; } }
        public int HeldCount { get { return held.Count; } }
        public int ArchivedOfferCount { get { return archivedOfferCount; } }
        public HiringPolicyDef CurrentPolicy { get { return DefDatabase<HiringPolicyDef>.GetNamedSilentFail("RR_OrdinaryApplicants"); } }
        private RimroomsCampaignComponent Campaign { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }
        private static int Now { get { return Find.TickManager.TicksGame; } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_personnelSchema", 1, true);
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_Values.Look(ref sequence, "rr_sequence");
            Scribe_Values.Look(ref nextRequestTick, "rr_nextRequestTick");
            Scribe_Values.Look(ref archivedOfferCount, "rr_archivedOfferCount");
            Scribe_Collections.Look(ref offers, "rr_applicants", LookMode.Deep);
            Scribe_Deep.Look(ref held, "rr_applicantHolder", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                offers = offers ?? new List<ApplicantRecord>();
                held = held ?? new ThingOwner<Pawn>(this);
                ValidateState();
            }
        }

        private void ValidateState()
        {
            faultKey = null;
            if (schemaVersion != CurrentSchemaVersion) { faultKey = "RR_Personnel_UnsupportedSchema"; return; }
            if (sequence < 0 || nextRequestTick < 0 || archivedOfferCount < 0 || (offers.Count > 0 && string.IsNullOrEmpty(branchId)) ||
                offers.Any(o => o == null || string.IsNullOrEmpty(o.id)) ||
                offers.Select(o => o.id).Distinct(StringComparer.Ordinal).Count() != offers.Count)
            { faultKey = "RR_Personnel_InvalidSave"; return; }
            foreach (ApplicantRecord offer in offers)
            {
                if (!offer.id.StartsWith(branchId + ":applicant:", StringComparison.Ordinal) ||
                    offer.onboardingUsd <= 0 || offer.dailyWageUsd <= 0 || offer.createdTick < 0 || offer.expiresTick < offer.createdTick ||
                    !Enum.IsDefined(typeof(ApplicantStatus), offer.status) || !Enum.IsDefined(typeof(ApplicantRelease), offer.release) ||
                    (offer.pawn != null && offer.pawn.GetUniqueLoadID() != offer.pawnId) ||
                    (offer.status == ApplicantStatus.Hiring && !PersonnelRoles.Valid(offer.selectedRole)) ||
                    (offer.registered && (!offer.charged || offer.refunded)) || (offer.refunded && !offer.charged) ||
                    (offer.arrivalFailedOffsite && (offer.everArrived || offer.recruitStarted || offer.registered)) ||
                    (offer.status == ApplicantStatus.Dismissed && (offer.pawn != null || string.IsNullOrEmpty(offer.pawnId) ||
                        string.IsNullOrEmpty(offer.name) || offer.charged || offer.refunded || offer.arrivalAttempted ||
                        offer.everArrived || offer.recruitStarted || offer.recruited || offer.registered)))
                { faultKey = "RR_Personnel_InvalidSave"; return; }
            }
            List<string> activeIds = offers.Where(o => o.pawn != null).Select(o => o.pawnId).ToList();
            if (activeIds.Count != activeIds.Distinct(StringComparer.Ordinal).Count() ||
                held.Cast<Pawn>().Any(p => !offers.Any(o => o.pawn == p && o.status != ApplicantStatus.Hired)))
            { faultKey = "RR_Personnel_InvalidSave"; }
        }

        private CompanyActionResult CheckActive()
        {
            if (faultKey != null) { return Refuse(faultKey); }
            if (schemaVersion != CurrentSchemaVersion) { return Refuse("RR_Personnel_UnsupportedSchema"); }
            RimroomsCampaignComponent campaign = Campaign;
            if (campaign == null || !campaign.CanOperate || (!string.IsNullOrEmpty(branchId) && branchId != campaign.BranchId))
            { return Refuse("RR_Personnel_BranchUnavailable"); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult RequestApplicants()
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            if (Now < nextRequestTick) { return Refuse("RR_Personnel_RequestCooldown"); }
            if (offers.Any(o => o.IsOpen) || held.Count > 0) { return Refuse("RR_Personnel_FinishOffers"); }
            HiringPolicyDef policy = CurrentPolicy;
            if (policy == null || !policy.Valid) { return Refuse("RR_Personnel_PolicyMissing"); }
            if (!LiveHeadquarters(Campaign.Headquarters)) { return Refuse("RR_Personnel_MapUnavailable"); }
            if (sequence > int.MaxValue - policy.maxOffers) { return Refuse("RR_Personnel_InvalidSave"); }
            TrimTerminalHistory();
            branchId = Campaign.BranchId;
            nextRequestTick = AddTicks(Now, policy.refreshTicks);
            for (int i = 0; i < policy.maxOffers; i++)
            {
                string id = branchId + ":applicant:" + (++sequence);
                if (offers.Any(o => o.id == id)) { faultKey = "RR_Personnel_InvalidSave"; return Refuse(faultKey); }
                offers.Add(new ApplicantRecord { id = id, createdTick = Now, expiresTick = AddTicks(Now, policy.offerTicks),
                    kindDefName = policy.candidateKind.defName, policyDefName = policy.defName, onboardingUsd = policy.onboardingUsd,
                    dailyWageUsd = policy.dailyWageUsd, status = ApplicantStatus.Queued });
            }
            return CompanyActionResult.Applied();
        }

        public override void GameComponentTick()
        {
            if (busy || Current.ProgramState != ProgramState.Playing || !CheckActive().Success) { return; }
            ApplicantRecord queued = offers.FirstOrDefault(o => o.status == ApplicantStatus.Queued);
            if (queued != null)
            {
                busy = true;
                try { GenerateOne(queued); }
                finally { busy = false; }
                return;
            }
            if (Now % 250 != 0) { return; }
            ApplicantRecord expired = offers.FirstOrDefault(o => o.status == ApplicantStatus.Offered && Now >= o.expiresTick);
            if (expired != null) { StartRelease(expired, ApplicantRelease.Expired); }
            TrimTerminalHistory();
        }

        private void GenerateOne(ApplicantRecord offer)
        {
            // Persist the attempt before entering native generation. A failed call is never rerolled every tick.
            offer.status = ApplicantStatus.GenerationFailed;
            offer.failureKey = "RR_Personnel_GenerationFailed";
            try
            {
                PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(offer.kindDefName);
                if (kind == null || kind.race == null || kind.race.race == null || !kind.race.race.Humanlike) { return; }
                Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction: null,
                    context: PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, allowDead: false, allowDowned: false,
                    canGeneratePawnRelations: false, allowFood: false, developmentalStages: DevelopmentalStage.Adult, dontGiveWeapon: true));
                if (pawn == null) { return; }
                offer.pawn = pawn;
                offer.pawnId = pawn.GetUniqueLoadID();
                offer.name = pawn.LabelShortCap.ToString();
                if (pawn.Spawned || pawn.holdingOwner != null || Find.WorldPawns.Contains(pawn))
                { offer.status = ApplicantStatus.Unavailable; offer.failureKey = "RR_Personnel_CustodyChanged"; return; }
                if (!held.TryAdd(pawn, false)) { faultKey = "RR_Personnel_InvalidSave"; return; }
                if (pawn.Dead || pawn.Destroyed || pawn.Downed || !pawn.RaceProps.Humanlike || !pawn.DevelopmentalStage.Adult() ||
                    pawn.Faction != null || pawn.skills == null || pawn.story == null || pawn.health == null ||
                    pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger())
                { StartRelease(offer, ApplicantRelease.InvalidCandidate); return; }
                offer.suggestedRole = PersonnelRoles.Recommend(pawn);
                offer.status = ApplicantStatus.Offered;
                offer.failureKey = null;
            }
            catch (Exception exception)
            {
                PreserveDetachedPawn(offer);
                offer.failureKey = "RR_Personnel_GenerationFailed";
                // Keep a returned but interrupted candidate recoverable through explicit release.
                if (offer.pawn != null) { offer.status = ApplicantStatus.Releasing; offer.release = ApplicantRelease.InvalidCandidate; }
                Log.Warning("[Rimrooms][Personnel] Applicant generation interrupted for " + offer.id + ": " + exception.GetType().Name);
            }
        }

        public CompanyActionResult DeclineApplicant(string applicantId)
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            ApplicantRecord offer = FindOffer(applicantId);
            if (offer == null) { return Refuse("RR_Personnel_InvalidOffer"); }
            if (offer.status == ApplicantStatus.Declined || offer.status == ApplicantStatus.Expired) { return CompanyActionResult.Existing(); }
            if (offer.status != ApplicantStatus.Offered) { return Refuse("RR_Personnel_InvalidOffer"); }
            return StartRelease(offer, Now >= offer.expiresTick ? ApplicantRelease.Expired : ApplicantRelease.Declined);
        }

        public CompanyActionResult RetryRelease(string applicantId)
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            ApplicantRecord offer = FindOffer(applicantId);
            if (offer == null || offer.status != ApplicantStatus.Releasing || offer.release == ApplicantRelease.None)
            { return Refuse("RR_Personnel_InvalidOffer"); }
            return FinishRelease(offer);
        }

        public CompanyActionResult DismissUnavailableApplicant(string applicantId)
        {
            CompanyActionResult check = CheckActive();
            if (!check.Success) { return check; }
            if (busy) { return Refuse("RR_Personnel_Busy"); }
            busy = true;
            try
            {
                if (string.IsNullOrEmpty(branchId) || Campaign == null || branchId != Campaign.BranchId)
                { return Refuse("RR_Personnel_BranchUnavailable"); }
                ApplicantRecord offer = FindOffer(applicantId);
                if (offer == null || offer.status != ApplicantStatus.Unavailable ||
                    !offer.id.StartsWith(branchId + ":applicant:", StringComparison.Ordinal))
                { return Refuse("RR_Personnel_InvalidOffer"); }
                if (offer.charged || offer.refunded || offer.arrivalAttempted || offer.everArrived || offer.recruitStarted ||
                    offer.recruited || offer.registered || offer.release != ApplicantRelease.None ||
                    Campaign.Staff.Any(s => s.pawnLoadId == offer.pawnId) ||
                    Campaign.Ledger.Any(e => e.operationId == offer.ChargeId || e.operationId == offer.RefundId))
                { return Refuse("RR_Personnel_CannotRelease"); }

                Pawn pawn = offer.pawn;
                if (pawn == null || pawn.GetUniqueLoadID() != offer.pawnId || pawn.holdingOwner == held)
                { return Refuse("RR_Personnel_CustodyUnconfirmed"); }
                bool knownOutsideCustody = pawn.Spawned || pawn.Destroyed || pawn.Discarded ||
                    (pawn.holdingOwner != null && pawn.holdingOwner != held) || Find.WorldPawns.Contains(pawn);
                if (!knownOutsideCustody) { return Refuse("RR_Personnel_CustodyUnconfirmed"); }

                if (string.IsNullOrEmpty(offer.name)) { offer.name = pawn.LabelShortCap.ToString(); }
                // Keep the stable identity and failure reason. This only drops our journal reference;
                // it never de-spawns, transfers, discards, releases, or otherwise mutates the pawn.
                offer.pawn = null;
                offer.status = ApplicantStatus.Dismissed;
                return CompanyActionResult.Applied();
            }
            finally { busy = false; }
        }

        private CompanyActionResult StartRelease(ApplicantRecord offer, ApplicantRelease reason)
        {
            if (busy && offer.status != ApplicantStatus.GenerationFailed) { return Fail(offer, "RR_Personnel_Busy"); }
            offer.release = reason;
            offer.status = ApplicantStatus.Releasing;
            return FinishRelease(offer);
        }

        private CompanyActionResult FinishRelease(ApplicantRecord offer)
        {
            Pawn pawn = offer.pawn;
            if ((offer.arrivalAttempted && !offer.arrivalFailedOffsite) || offer.everArrived || offer.recruitStarted || offer.registered ||
                (offer.charged && !offer.refunded)) { return Fail(offer, "RR_Personnel_CannotRelease"); }
            if (pawn == null) { return Fail(offer, "RR_Personnel_PawnMissing"); }
            if (pawn.Spawned || pawn.Faction != null || (pawn.holdingOwner != null && pawn.holdingOwner != held))
            { return Fail(offer, "RR_Personnel_CustodyChanged"); }
            bool previousBusy = busy;
            busy = true;
            try
            {
                if (!Find.WorldPawns.Contains(pawn))
                {
                    if (pawn.holdingOwner != held && !offer.worldReleaseStarted) { return Fail(offer, "RR_Personnel_CustodyChanged"); }
                    offer.worldReleaseStarted = true;
                    if (pawn.holdingOwner == held) { held.Remove(pawn); }
                    Find.WorldPawns.PassToWorld(pawn, PawnDiscardDecideMode.Decide);
                }
                if (!Find.WorldPawns.Contains(pawn) && !pawn.Discarded)
                { PreserveDetachedPawn(offer); return Fail(offer, "RR_Personnel_ReleaseInterrupted"); }
                offer.status = offer.release == ApplicantRelease.Declined ? ApplicantStatus.Declined :
                    offer.release == ApplicantRelease.Expired ? ApplicantStatus.Expired :
                    offer.release == ApplicantRelease.Cancelled ? ApplicantStatus.Cancelled : ApplicantStatus.GenerationFailed;
                // Native world ownership/GC takes over. History retains the saved identity, not a second deep pawn.
                offer.pawn = null;
                offer.failureKey = offer.release == ApplicantRelease.InvalidCandidate ? "RR_Personnel_GenerationFailed" : null;
                return CompanyActionResult.Applied();
            }
            catch (Exception exception)
            {
                PreserveDetachedPawn(offer);
                Log.Warning("[Rimrooms][Personnel] Applicant release interrupted for " + offer.id + ": " + exception.GetType().Name);
                return Fail(offer, "RR_Personnel_ReleaseInterrupted");
            }
            finally { busy = previousBusy; }
        }

        private void PreserveDetachedPawn(ApplicantRecord offer)
        {
            Pawn pawn = offer.pawn;
            try
            {
                if (pawn != null && pawn.Spawned && offer.status == ApplicantStatus.Hiring)
                { offer.everArrived = true; offer.arrivalFailedOffsite = false; }
                if (pawn != null && !pawn.Spawned && !pawn.Discarded && pawn.holdingOwner == null && !Find.WorldPawns.Contains(pawn))
                { if (!held.TryAdd(pawn, false)) { faultKey = "RR_Personnel_InvalidSave"; } }
                if (offer.status == ApplicantStatus.Hiring && offer.arrivalAttempted && !offer.everArrived && !offer.recruitStarted &&
                    !offer.registered && pawn != null && !pawn.Spawned && pawn.Faction == null && pawn.holdingOwner == held)
                { offer.arrivalFailedOffsite = true; }
            }
            catch (Exception exception)
            {
                faultKey = "RR_Personnel_InvalidSave";
                Log.Error("[Rimrooms][Personnel] Could not reconcile the original applicant holder: " + exception.GetType().Name);
            }
        }
        private void TrimTerminalHistory()
        {
            // Only compact record-only history: never destroy, move, refund or regenerate any pawn here.
            List<ApplicantRecord> terminal = offers.Where(o =>
                ((o.status == ApplicantStatus.Declined || o.status == ApplicantStatus.Expired || o.status == ApplicantStatus.Cancelled ||
                  o.status == ApplicantStatus.GenerationFailed || o.status == ApplicantStatus.Dismissed) && o.pawn == null) ||
                (o.status == ApplicantStatus.Hired && o.registered && (o.pawn == null || o.pawn.holdingOwner != held) &&
                    Campaign.Staff.Any(s => s.Id == o.StaffId))).ToList();
            foreach (ApplicantRecord old in terminal.Take(Math.Max(0, terminal.Count - 64)))
            {
                offers.Remove(old);
                if (archivedOfferCount < int.MaxValue) { archivedOfferCount++; }
            }
        }
        private ApplicantRecord FindOffer(string id) { return offers.FirstOrDefault(o => o.id == id); }
        private static bool LiveHeadquarters(Map map) { return map != null && Find.Maps.Contains(map) && map.IsPlayerHome; }
        private static int AddTicks(int tick, int delta) { return tick <= int.MaxValue - delta ? tick + delta : int.MaxValue; }
        private static CompanyActionResult Refuse(string key) { return CompanyActionResult.Refused(key); }
        private static CompanyActionResult Fail(ApplicantRecord offer, string key) { offer.failureKey = key; return Refuse(key); }
    }
}
