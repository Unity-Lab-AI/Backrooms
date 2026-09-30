using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

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
                listing.Label("RR_Interview_NoInterviewer".Translate(
                    RimroomsCampaignComponent.MinimumInterviewerSocial));
                return;
            }

            listing.Label("RR_UI_InterviewPrompt".Translate(interviewer.LabelShortCap));
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
