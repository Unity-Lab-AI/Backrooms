using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Personnel;
using RimWorld;
using UnityEngine;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private int personnelStaffPage;

        private void DrawPersonnel(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            // **THE EXPLANATION BELONGS ON THE BUTTON IT IS ABOUT.** Seventeen words saying that
            // company roles are assignments and that skills, needs, beds and priorities stay
            // RimWorld's — drawn above the button that opens RimWorld's own Assign tab. No new
            // string: the paragraph is the button's hover now.
            if (DrawAction(listing, label: "RR_Personnel_OpenAssignments".Translate(),
                    refusal: TaggedString.Empty,
                    detail: "RR_Personnel_NativeExplanation".Translate()))
            { OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign")); }
            const int staffPageSize = 12;
            int staffPages = Math.Max(1, (campaign.Staff.Count + staffPageSize - 1) / staffPageSize);
            personnelStaffPage = Math.Max(0, Math.Min(personnelStaffPage, staffPages - 1));
            listing.Label("RR_Personnel_StaffPage".Translate(personnelStaffPage + 1, staffPages, campaign.Staff.Count));
            if (personnelStaffPage > 0 && listing.ButtonText("RR_Personnel_PreviousStaff".Translate()))
            { personnelStaffPage--; scrollPosition = Vector2.zero; }
            if (personnelStaffPage + 1 < staffPages && listing.ButtonText("RR_Personnel_NextStaff".Translate()))
            { personnelStaffPage++; scrollPosition = Vector2.zero; }
            foreach (StaffRecord member in campaign.Staff.Skip(personnelStaffPage * staffPageSize).Take(staffPageSize).ToList())
            {
                listing.GapLine();
                listing.Label("RR_UI_StaffRow".Translate(member.Name, ("RR_Role_" + member.Role).Translate(), Money(member.DailyWageUsd)));
                Pawn pawn = member.Pawn;
                listing.Label(PersonnelView.PawnCondition(pawn));
                if (pawn != null)
                {
                    listing.Label(PersonnelView.NeedsSummary(pawn));
                    listing.Label("RR_Personnel_Bed".Translate(pawn.ownership != null && pawn.ownership.OwnedBed != null
                        ? pawn.ownership.OwnedBed.LabelCap.ToString() : "RR_Personnel_NoBed".Translate().ToString()));
                    if (listing.ButtonText("RR_Personnel_Inspect".Translate(member.Name)))
                    { Find.WindowStack.Add(new Dialog_PersonnelDossier(pawn)); }
                    if (pawn.Spawned && listing.ButtonText("RR_UI_ViewPawn".Translate(member.Name))) { CameraJumper.TryJumpAndSelect(pawn); }
                }
                if (listing.ButtonText("RR_Personnel_ChangeRole".Translate()))
                {
                    string staffId = member.Id;
                    Find.WindowStack.Add(new FloatMenu(PersonnelRoles.Ids.Select(role => new FloatMenuOption(
                        ("RR_Role_" + role).Translate(), () => ShowResult(campaign.AssignCompanyRole(staffId, role)))).ToList()));
                }
            }
            listing.GapLine();
            listing.Label("RR_Personnel_ApplicantHeading".Translate());
            RimroomsPersonnelComponent personnel = Current.Game.GetComponent<RimroomsPersonnelComponent>();
            if (personnel == null) { listing.Label("RR_Personnel_BranchUnavailable".Translate()); return; }
            if (personnel.FaultKey != null)
            { listing.Label(personnel.FaultKey.Translate()); listing.Label("RR_Personnel_HeldCount".Translate(personnel.HeldCount)); return; }
            HiringPolicyDef policy = personnel.CurrentPolicy;
            if (policy != null && policy.Valid)
            {
                DrawHeading(listing,
                    heading: "RR_Personnel_BoardBrief".Translate(policy.maxOffers,
                        ((float)policy.refreshTicks / GenDate.TicksPerDay).ToString("0.##")),
                    detail: "RR_Personnel_BoardExplanation".Translate(policy.maxOffers,
                        ((float)policy.refreshTicks / GenDate.TicksPerDay).ToString("0.##")));
            }
            // **THE MISSING-POLICY CASE STAYS A PARAGRAPH ON SCREEN.** It is a fault, not an
            // explanation: the package is damaged and no applicant can be requested at all. A
            // fault a player has to hover to find is a fault they will report as silence.
            else { listing.Label("RR_Personnel_PolicyMissing".Translate()); }
            listing.Label("RR_Personnel_RequestAt".Translate(Day(personnel.NextRequestTick)));
            if (listing.ButtonText("RR_Personnel_Request".Translate())) { ShowResult(personnel.RequestApplicants()); }
            foreach (ApplicantRecord offer in personnel.Offers.Where(o => o.IsOpen || o.Status == ApplicantStatus.Unavailable).ToList())
            {
                listing.GapLine();
                listing.Label("RR_Personnel_OfferRow".Translate(offer.Name, ("RR_Applicant_" + offer.Status).Translate()));
                listing.Label("RR_Personnel_Quote".Translate(Money(offer.OnboardingUsd), Money(offer.DailyWageUsd)));
                listing.Label("RR_Personnel_Expiry".Translate(Day(offer.ExpiresTick)));
                if (!string.IsNullOrEmpty(offer.FailureKey)) { listing.Label(offer.FailureKey.Translate()); }
                if (offer.Pawn != null && listing.ButtonText("RR_Personnel_Inspect".Translate(offer.Name)))
                { Find.WindowStack.Add(new Dialog_PersonnelDossier(offer.Pawn)); }
                if (offer.Pawn != null && offer.Pawn.Spawned && listing.ButtonText("RR_UI_ViewPawn".Translate(offer.Name)))
                { CameraJumper.TryJumpAndSelect(offer.Pawn); }
                if (offer.Status == ApplicantStatus.Offered)
                {
                    if (listing.ButtonText("RR_Personnel_ReviewHire".Translate())) { Find.WindowStack.Add(new Dialog_ConfirmApplicantHire(offer)); }
                    if (listing.ButtonText("RR_Personnel_Decline".Translate())) { ShowResult(personnel.DeclineApplicant(offer.Id)); }
                }
                else if (offer.Status == ApplicantStatus.Hiring)
                {
                    listing.Label("RR_Personnel_HireProgress".Translate(PersonnelView.YesNo(offer.Charged),
                        PersonnelView.YesNo(offer.ArrivalAttempted), PersonnelView.YesNo(offer.Registered)));
                    if (listing.ButtonText("RR_Personnel_RetryHire".Translate())) { ShowResult(personnel.RetryHire(offer.Id)); }
                    if (offer.CanCancelBeforeArrival && listing.ButtonText("RR_Personnel_CancelHire".Translate()))
                    { ShowResult(personnel.CancelUnarrivedHire(offer.Id)); }
                }
                else if (offer.Status == ApplicantStatus.Releasing && listing.ButtonText("RR_Personnel_RetryRelease".Translate()))
                { ShowResult(personnel.RetryRelease(offer.Id)); }
                else if (offer.Status == ApplicantStatus.Unavailable)
                {
                    // Twenty-six words on exactly what dismissal does and does not touch — the
                    // terms of this one button, on this one button.
                    if (DrawAction(listing, label: "RR_Personnel_DismissUnavailable".Translate(),
                            refusal: TaggedString.Empty,
                            detail: "RR_Personnel_UnavailableDisposition".Translate()))
                    { ShowResult(personnel.DismissUnavailableApplicant(offer.Id)); }
                }
            }
            listing.GapLine();
            listing.Label("RR_Personnel_History".Translate());
            if (personnel.ArchivedOfferCount > 0) { listing.Label("RR_Personnel_Archived".Translate(personnel.ArchivedOfferCount)); }
            foreach (ApplicantRecord offer in personnel.Offers.Where(o => !o.IsOpen && o.Status != ApplicantStatus.Unavailable).Reverse().Take(12))
            {
                listing.Label("RR_Personnel_OfferRow".Translate(offer.Name, ("RR_Applicant_" + offer.Status).Translate()));
                listing.Label("RR_Personnel_HistoryIdentity".Translate(offer.Id, offer.PawnId ?? "RR_Personnel_NotGenerated".Translate().ToString()));
                if (!string.IsNullOrEmpty(offer.FailureKey)) { listing.Label(offer.FailureKey.Translate()); }
            }
        }
    }

    internal static class PersonnelView
    {
        internal static string YesNo(bool value) { return (value ? "RR_Personnel_Yes" : "RR_Personnel_No").Translate().ToString(); }
        internal static string PawnCondition(Pawn pawn)
        {
            if (pawn == null || pawn.Destroyed) { return "RR_Personnel_Missing".Translate().ToString(); }
            if (pawn.Dead) { return "RR_Personnel_Dead".Translate().ToString(); }
            if (pawn.IsPrisoner || pawn.IsSlave) { return "RR_Personnel_Custody".Translate().ToString(); }
            if (pawn.Downed) { return "RR_Personnel_Downed".Translate().ToString(); }
            if (pawn.InMentalState) { return "RR_Personnel_MentalState".Translate().ToString(); }
            return (pawn.Spawned ? "RR_Personnel_OnMap" : "RR_Personnel_OffMap").Translate().ToString();
        }
        internal static string NeedsSummary(Pawn pawn)
        {
            if (pawn.needs == null) { return "RR_Personnel_NeedsUnavailable".Translate().ToString(); }
            return "RR_Personnel_Needs".Translate(NeedLevel(pawn.needs.food), NeedLevel(pawn.needs.rest),
                NeedLevel(pawn.needs.joy), NeedLevel(pawn.needs.mood)).ToString();
        }
        private static string NeedLevel(Need need)
        {
            if (need == null) { return "RR_Personnel_NotApplicable".Translate().ToString(); }
            float value = need.CurLevelPercentage;
            return float.IsNaN(value) || float.IsInfinity(value) ? "RR_Personnel_NotApplicable".Translate().ToString() :
                value.ToString("P0", CultureInfo.CurrentCulture);
        }
        internal static void DrawDetails(Listing_Standard listing, Pawn pawn)
        {
            if (pawn == null || pawn.Destroyed) { listing.Label("RR_Personnel_Missing".Translate()); return; }
            // **THE NOTE HANGS OFF THE NAME.** Twenty-four words about an off-site applicant
            // keeping its offered profile, and what arrival does and does not enable. It is about
            // this person, so it lives on this person's own line rather than as a paragraph under
            // their needs — and it needed no new string to get there.
            DrawHeading(listing, heading: pawn.LabelCap,
                detail: "RR_Personnel_OffsiteNote".Translate());
            // **THE PAWN DEEP LINK.** Owner: *"Make each screen deep-link to the relevant pawn,
            // building, map, quest, item, research project..."*. This screen holds the single
            // richest readout of a person anywhere in the package and had no way to go and look
            // at them -- the player had to close Operations and find them by hand.
            //
            // Refused by name rather than hidden, because the commonest reason it cannot work is
            // interesting: an off-site applicant is a real person with a real profile who is not
            // standing anywhere yet, and that is worth saying out loud.
            if (DrawAction(listing,
                label: "RR_Personnel_ShowPawn".Translate(pawn.LabelShortCap),
                refusal: OperationsLinks.CanReach(pawn)
                    ? TaggedString.Empty
                    : "RR_Personnel_ShowPawnUnreachable".Translate(pawn.LabelShortCap),
                detail: "RR_Personnel_ShowPawnDesc".Translate(pawn.LabelShortCap)))
            { OperationsLinks.Show(pawn); }
            listing.Label(PawnCondition(pawn));
            if (pawn.ageTracker != null) { listing.Label("RR_Personnel_Age".Translate(pawn.ageTracker.AgeBiologicalYears)); }
            listing.Label(NeedsSummary(pawn));
            listing.GapLine();
            listing.Label("RR_Personnel_Traits".Translate());
            if (pawn.story != null && pawn.story.traits != null)
            { foreach (Trait trait in pawn.story.traits.allTraits) { listing.Label(trait.LabelCap); } }
            listing.Label("RR_Personnel_Health".Translate());
            if (pawn.health != null && pawn.health.hediffSet != null)
            {
                if (pawn.health.hediffSet.hediffs.Count == 0) { listing.Label("RR_Personnel_NoConditions".Translate()); }
                foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
                { listing.Label(hediff.LabelCap); }
            }
            listing.GapLine();
            listing.Label("RR_Personnel_Skills".Translate());
            if (pawn.skills != null)
            {
                foreach (SkillRecord skill in pawn.skills.skills.Where(s => s.def != null))
                { listing.Label("RR_Personnel_SkillRow".Translate(skill.def.LabelCap, skill.Level,
                    ("RR_Personnel_Passion_" + skill.passion).Translate(), skill.TotallyDisabled ? "RR_Personnel_Disabled".Translate().ToString() : "")); }
            }
            listing.GapLine();
            listing.Label("RR_Personnel_Work".Translate());
            foreach (WorkTypeDef work in DefDatabase<WorkTypeDef>.AllDefsListForReading)
            {
                if (pawn.WorkTypeIsDisabled(work))
                { listing.Label("RR_Personnel_WorkDisabled".Translate(work.labelShort, string.Join("; ", pawn.GetReasonsForDisabledWorkType(work).ToArray()))); }
                else if (pawn.workSettings != null && pawn.workSettings.Initialized)
                { listing.Label("RR_Personnel_WorkPriority".Translate(work.labelShort, pawn.workSettings.GetPriority(work))); }
                else { listing.Label("RR_Personnel_WorkAvailable".Translate(work.labelShort)); }
            }
            if (pawn.Spawned && pawn.timetable != null)
            { listing.Label("RR_Personnel_Schedule".Translate(pawn.timetable.CurrentAssignment.LabelCap)); }
            listing.GapLine();
            listing.Label("RR_Personnel_Equipment".Translate());
            var possessions = new List<Thing>();
            if (pawn.apparel != null) { possessions.AddRange(pawn.apparel.WornApparel.Cast<Thing>()); }
            if (pawn.equipment != null) { possessions.AddRange(pawn.equipment.AllEquipmentListForReading.Cast<Thing>()); }
            if (pawn.inventory != null) { possessions.AddRange(pawn.inventory.innerContainer.Cast<Thing>()); }
            if (possessions.Count == 0) { listing.Label("RR_Personnel_NoEquipment".Translate()); }
            foreach (Thing item in possessions) { listing.Label(item.LabelCap); }
        }
    }

    public sealed class Dialog_PersonnelDossier : Window
    {
        private readonly Pawn pawn;
        private Vector2 scroll;
        private float height = 600f;
        public override Vector2 InitialSize { get { return new Vector2(700f, 700f); } }
        public Dialog_PersonnelDossier(Pawn pawn)
        { this.pawn = pawn; forcePause = true; absorbInputAroundWindow = true; doCloseX = true; doCloseButton = true; }
        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawDossier(inRect); }
        }

        private void DrawDossier(Rect inRect)
        {
            inRect.yMax -= 40f;
            var content = new Rect(0f, 0f, inRect.width - 20f, height);
            Widgets.BeginScrollView(inRect, ref scroll, content);
            var listing = new Listing_Standard(); listing.maxOneColumn = true;
            listing.Begin(content);
            try { PersonnelView.DrawDetails(listing, pawn); height = Mathf.Max(600f, listing.CurHeight + 20f); }
            finally { listing.End(); Widgets.EndScrollView(); }
        }
    }

    public sealed class Dialog_ConfirmApplicantHire : Window
    {
        private readonly string applicantId;
        private string role;
        private Vector2 scroll;
        private float contentHeight = 520f;
        public override Vector2 InitialSize { get { return new Vector2(640f, 560f); } }
        public Dialog_ConfirmApplicantHire(ApplicantRecord offer)
        {
            applicantId = offer.Id; role = PersonnelRoles.Valid(offer.SuggestedRole) ? offer.SuggestedRole : "operations";
            forcePause = true; absorbInputAroundWindow = true; doCloseX = true;
        }
        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawConfirmation(inRect); }
        }

        private void DrawConfirmation(Rect inRect)
        {
            RimroomsPersonnelComponent personnel = Current.Game == null ? null : Current.Game.GetComponent<RimroomsPersonnelComponent>();
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            ApplicantRecord offer = personnel == null ? null : personnel.Offers.FirstOrDefault(o => o.Id == applicantId);
            var content = new Rect(0f, 0f, inRect.width - 20f, contentHeight);
            Widgets.BeginScrollView(inRect, ref scroll, content);
            var listing = new Listing_Standard(); listing.maxOneColumn = true;
            listing.Begin(content);
            try
            {
                if (offer == null || campaign == null) { listing.Label("RR_Personnel_InvalidOffer".Translate()); return; }
                listing.Label("RR_Personnel_HireTitle".Translate(offer.Name));
                // **THE QUOTE IS THE DECISION; THE TERMS ARE THE SMALL PRINT.** Sixty-five words
                // of payroll boundary and arrival method were drawn under an eight-word quote, so
                // the one number a player is actually agreeing to was the smallest thing on the
                // dialog. Built inline rather than into a local, because a local would hide all
                // three strings from the density measurement.
                int nextPayroll = campaign.NextPayrollTick;
                DrawHeading(listing,
                    heading: "RR_Personnel_Quote".Translate(offer.OnboardingUsd.ToString("N0"),
                        offer.DailyWageUsd.ToString("N0")),
                    detail: (nextPayroll >= 0
                            ? "RR_Personnel_PayrollTerms".Translate(nextPayroll / GenDate.TicksPerDay + 1)
                            : "RR_Personnel_PayrollLimit".Translate())
                        + "\n\n" + "RR_Personnel_ArrivalTerms".Translate());
                listing.GapLine();
                if (DrawAction(listing,
                        label: "RR_Personnel_RoleChoice".Translate(("RR_Role_" + role).Translate()),
                        refusal: TaggedString.Empty,
                        detail: "RR_Personnel_RoleTerms".Translate()))
                {
                    Find.WindowStack.Add(new FloatMenu(PersonnelRoles.Ids.Select(id => new FloatMenuOption(
                        ("RR_Role_" + id).Translate(), () => role = id)).ToList()));
                }
                if (listing.ButtonText("RR_Personnel_ConfirmHire".Translate()))
                {
                    CompanyActionResult result = personnel.HireApplicant(applicantId, role);
                    if (result.Success) { Close(); }
                    else { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
                }
                if (listing.ButtonText("Cancel".Translate())) { Close(); }
            }
            finally { contentHeight = Mathf.Max(520f, listing.CurHeight + 20f); listing.End(); Widgets.EndScrollView(); }
        }
    }
}
