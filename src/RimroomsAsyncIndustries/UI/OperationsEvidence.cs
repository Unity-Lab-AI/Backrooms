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
                listing.Gap(4f);
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
