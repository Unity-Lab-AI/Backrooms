using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private static void DrawEvidenceDetails(Listing_Standard listing, EvidenceRecord record)
        {
            EvidenceAnalysisReport report = record.AnalysisReport;
            if (report != null)
            {
                listing.Label("RR_UI_AnalysisReportHeader".Translate(report.AnalystName, Day(report.CompletedTick)));
                listing.Label("RR_UI_AnalysisSnapshotNote".Translate());
                // **The review workflow's readout.** A sign-off nobody can see is a sign-off
                // that may as well not have happened -- which is what became of every second
                // crew account until 0.12.25-dev.
                if (record.Reviewed)
                {
                    listing.Label((record.ReviewEndorsed
                        ? "RR_UI_ReviewEndorsed" : "RR_UI_ReviewReturned").Translate(
                            record.Reviewer == null
                                ? "RR_UI_ReviewerUnknown".Translate().ToString()
                                : record.Reviewer.LabelShortCap.ToString(),
                            Day(record.ReviewedTick)));
                }
                else { DrawReview(listing, record); }
                if (report.DetailsUnavailable)
                {
                    listing.Label((report.LegacyDetailsUnavailable ? "RR_UI_LegacyReportUnavailable" : "RR_UI_ReportUnavailable").Translate());
                    return;
                }
            }
            else { listing.Label("RR_UI_FieldLogHeader".Translate()); }

            var observations = report == null ? record.Observations : report.Observations;
            if (observations.Count == 0) { listing.Label("RR_UI_NoFieldObservations".Translate()); }
            foreach (EvidenceObservationRecord observation in observations)
            {
                listing.Label(("RR_Observation_" + observation.Kind).Translate(observation.RoomIndex + 1,
                    observation.ReferencedRoomIndex + 1, observation.MarkerNumber));
                listing.Label("RR_UI_ObservationWitness".Translate(observation.WitnessName,
                    Day(observation.Tick), observation.RecorderCarrierName));

                // Corroborating and disputing accounts, each named. A dispute the company records
                // but never shows anybody is a dispute that may as well have been discarded, which
                // is what happened to every second crew account until 0.12.25-dev.
                IReadOnlyList<WitnessAccountRecord> accounts = observation.Accounts;
                if (accounts != null)
                {
                    foreach (WitnessAccountRecord account in accounts)
                    {
                        if (account == null) { continue; }
                        listing.Label((account.Agrees ? "RR_UI_AccountAgrees" : "RR_UI_AccountDisagrees")
                            .Translate(account.WitnessName, Day(account.Tick),
                                account.ReferencedRoomIndex + 1, account.MarkerNumber));
                    }
                }
                DrawInterview(listing, record, observation);
                listing.Gap(4f);
            }

            // **Outside the report block on purpose.** A secured record the branch has not
            // analysed is still a thing sitting on a shelf that somebody has to decide about, so
            // the disposition cannot be gated on there being a report. It draws nothing at all
            // for a record the branch does not hold yet.
            DrawDisposition(listing, record);
        }

        /// <summary>
        /// The sign-off, and the button that performs it.
        ///
        /// **Review is the fourth of the owner's four workflows** -- *"Add
        /// analyze/interview/compare/review workflows"* -- and the last to ship. Analyse, compare
        /// and interview were already here.
        ///
        /// Every refusal `ReviewAnalysis` can return is a named key the player is shown, because
        /// a control that refuses in silence is how somebody concludes a button is broken. That
        /// cost the owner an afternoon on the gate at 0.12.73-dev.
        /// </summary>
        private static void DrawReview(Listing_Standard listing, EvidenceRecord record)
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return; }
            if (!campaign.AwaitsReview(record)) { return; }

            // **THE COUNT IS THE BRANCH'S, NOT THIS RECORD'S**, which is what makes it worth
            // showing: a player looking at one report learns how many others are also waiting,
            // and that is the question `RecordsAwaitingReview` was written to answer. It rides
            // the heading that was already here, so the pane gains a number and not a line.
            DrawHeading(listing,
                heading: "RR_UI_ReviewAwaitingBrief".Translate(campaign.AwaitingReviewCount()),
                detail: "RR_UI_ReviewAwaiting".Translate());

            // An outstanding dispute is two of the branch's own people contradicting each other
            // on the record. The interview is what clears it, and saying so is more use than a
            // greyed-out button: it names the step that unblocks this one.
            int disputes = campaign.UnsettledDisputes(record).Count();
            if (disputes > 0)
            {
                // **THE SIGN-OFF BUTTON APPEARS, DISABLED, SAYING WHY.** It used to be a
                // paragraph and then nothing, so the player could not tell whether sign-off
                // was blocked or simply unimplemented.
                DrawAction(listing, label: "RR_UI_SignOffReport".Translate(),
                    refusal: "RR_Review_DisputesOutstanding".Translate(disputes));
                return;
            }

            Pawn reviewer = campaign.ReviewerFor(record);
            if (reviewer == null)
            {
                DrawAction(listing, label: "RR_UI_SignOffReport".Translate(),
                    refusal: "RR_Review_NoReviewer".Translate(
                        RimroomsCampaignComponent.MinimumReviewerIntellectual));
                return;
            }

            listing.Label("RR_UI_ReviewPrompt".Translate(reviewer.LabelShortCap));
            if (listing.ButtonText("RR_UI_SignOffReport".Translate()))
            { ShowResult(campaign.ReviewAnalysis(record, reviewer)); }
        }

        /// <summary>
        /// What the branch is going to do with the thing: contain it, put it back, or hand it to
        /// the corporation.
        ///
        /// **Owner direction, verbatim:** *"Make sale/study/use/contain/release/recruit/detain/
        /// transfer choices visible with financial, staff, faction, legal-in-world, trust, and
        /// security consequences"*. Sale, study and recruit already had surfaces. These three
        /// did not exist at all, and `detain` is on the person rather than the record.
        ///
        /// **The three sit together on purpose.** They are mutually exclusive and one-way, so
        /// showing them as one choice is the honest presentation — and the price is on the
        /// transfer button, because a player deciding between keeping a thing and handing it over
        /// needs the number in front of them rather than in a tooltip.
        /// </summary>
        private static void DrawDisposition(Listing_Standard listing, EvidenceRecord record)
        {
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || record == null) { return; }

            // Already decided: say what was decided and stop. A one-way choice that still shows
            // its buttons reads as something the player can change.
            if (record.Disposition != EvidenceDisposition.None)
            {
                listing.Label(("RR_UI_Disposition_" + record.Disposition).Translate());
                // **The one way out of containment.** A charge that runs every day forever needs
                // one, or a player who contained something before they understood the cost is
                // paying for it permanently. It pays nothing, so it cannot launder a contained
                // record into money.
                if (record.Disposition == EvidenceDisposition.Contained
                    && DrawAction(listing, label: "RR_UI_Destroy".Translate(),
                        refusal: TaggedString.Empty,
                        detail: "RR_UI_DestroyContainedDesc".Translate()))
                { ShowResult(campaign.DestroyFromContainment(record)); }
                return;
            }

            string refusal = campaign.DispositionFailureKey(record);
            // **Nothing is drawn at all when the branch does not hold the thing yet.** A record
            // still out in a coordinate is not a decision anybody can make, and offering three
            // greyed buttons on every located record would be the text wall the owner asked to
            // be rid of.
            if (refusal == "RR_Disposition_NotRecovered") { return; }

            // **Confidence, where the decision is made.** It is derived from the record's own
            // observations, disputes and sign-off, and it moves what the corporation will pay --
            // so the player seeing it beside the transfer price is the point rather than a
            // decoration. The band names which fact to go and fix.
            DrawHeading(listing,
                heading: "RR_UI_DispositionBrief".Translate(
                    ("RR_UI_Confidence_" + campaign.ConfidenceOf(record)).Translate()),
                detail: "RR_UI_Disposition".Translate());

            TaggedString blocked = refusal == null
                ? TaggedString.Empty : refusal.Translate();
            if (DrawAction(listing, label: "RR_UI_Contain".Translate(), refusal: blocked,
                detail: "RR_UI_ContainDesc".Translate(campaign.DailyContainmentUsd.ToString("N0"))))
            { ShowResult(campaign.ContainRecord(record)); }

            if (DrawAction(listing, label: "RR_UI_Release".Translate(), refusal: blocked,
                detail: "RR_UI_ReleaseDesc".Translate()))
            { ShowResult(campaign.ReleaseRecord(record)); }

            // The corporation half carries its own extra refusal: there is nobody to hand it to
            // while the branch is out of contact, and that is worth saying rather than hiding.
            TaggedString transferBlocked = blocked;
            if (transferBlocked.NullOrEmpty() && !campaign.CorporationContact)
            { transferBlocked = "RR_Disposition_NoContact".Translate(); }
            if (DrawAction(listing,
                label: "RR_UI_Transfer".Translate(campaign.TransferValueOf(record).ToString("N0")),
                refusal: transferBlocked,
                detail: "RR_UI_TransferDesc".Translate()))
            { ShowResult(campaign.TransferRecord(record)); }

            // **The one that needs nothing.** Containment needs money, transfer needs the
            // corporation on the line, release needs somewhere to put it back. A branch out of
            // options still has this, which is why the owner's row names it separately.
            if (DrawAction(listing, label: "RR_UI_Destroy".Translate(), refusal: blocked,
                detail: "RR_UI_DestroyDesc".Translate()))
            { ShowResult(campaign.DestroyRecord(record)); }
        }

        /// <summary>
        /// The interview: which of two accounts the company files.
        ///
        /// Only drawn for a fact two crew actually disagree about. The player chooses the account;
        /// the interviewer is whoever the company would send, named on the button so the choice is
        /// not made blind. A refusal is shown in place rather than the button being hidden, because
        /// *"nobody on staff can take a statement"* is information and a missing button is not.
        /// </summary>
        private static void DrawInterview(Listing_Standard listing, EvidenceRecord record,
            EvidenceObservationRecord observation)
        {
            if (observation == null || !observation.Disputed) { return; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return; }

            if (observation.Settled)
            {
                listing.Label("RR_UI_AccountFiled".Translate(
                    observation.NameForAccount(observation.FiledWitnessLoadId),
                    observation.InterviewerName, Day(observation.InterviewTick)));
                return;
            }

            Pawn interviewer = campaign.InterviewerFor(observation);
            if (interviewer == null)
            {
                // Same shape: the thing a player wants is "take the statements", so that is
                // what they see, off, with the Social floor on it.
                DrawAction(listing, label: "RR_UI_TakeStatements".Translate(),
                    refusal: "RR_Interview_NoInterviewer".Translate(
                        campaign.InterviewerSocialFloor));
                return;
            }

            // Who can take the statements is the line; what filing one of them means to the
            // company record is the consequence, and it only matters as you reach for it.
            DrawHeading(listing,
                heading: "RR_UI_InterviewBrief".Translate(interviewer.LabelShortCap),
                detail: "RR_UI_InterviewPrompt".Translate(interviewer.LabelShortCap));
            foreach (string loadId in observation.WitnessLoadIds.ToList())
            {
                string name = observation.NameForAccount(loadId);
                if (string.IsNullOrEmpty(name)) { continue; }
                if (listing.ButtonText("RR_UI_FileAccount".Translate(name)))
                { ShowResult(campaign.SettleDisputedAccount(record, observation, loadId, interviewer)); }
            }
        }

        private static void DrawKnownRoomClues(Listing_Standard listing, CoordinateRecord coordinate)
        {
            RoomContentMapComponent content = coordinate.Site?.Map?.GetComponent<RoomContentMapComponent>();
            if (content == null) { return; }
            foreach (RoomClueRecord clue in content.Clues.Where(c => c.Observed))
            {
                listing.Label(clue.Label);
                listing.Label(clue.Description);
                if (clue.Landmark != null && clue.Landmark.Spawned && clue.Landmark.Map == coordinate.Site.Map &&
                    !clue.Landmark.Position.Fogged(coordinate.Site.Map) && listing.ButtonText("RR_UI_LocateClue".Translate()))
                { CameraJumper.TryJumpAndSelect(clue.Landmark); }
                listing.Gap(6f);
            }
        }

        private static void DrawSalvageRecovery(Listing_Standard listing, Pawn worker)
        {
            RoomContentMapComponent content = worker.Map.GetComponent<RoomContentMapComponent>();
            if (content == null) { return; }
            foreach (RoomClueRecord clue in content.Clues.Where(c => c.Observed && c.Salvage))
            {
                Thing item = clue.Landmark;
                if (item == null || item.Destroyed || !item.Spawned || item.Map != worker.Map || item.Position.Fogged(worker.Map)) { continue; }
                if (listing.ButtonText("RR_UI_CollectSalvage".Translate(worker.LabelShortCap, item.LabelCap)))
                { ShowResult(ExpeditionCargo.QueuePickup(worker, item, item.stackCount)); }
            }
        }
    }
}
