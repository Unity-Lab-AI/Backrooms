using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;

using static RimroomsAsyncIndustries.UI.OperationsControls;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private void DrawEvidenceCreationRecovery(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            RimroomsEvidenceCreationComponent creation = Current.Game.GetComponent<RimroomsEvidenceCreationComponent>();
            if (creation == null) { listing.Label("RR_Evidence_InvalidRecord".Translate()); return; }
            if (creation.FaultKey != null) { listing.Label(creation.FaultKey.Translate()); }
            var pending = creation.Attempts.Where(a => a != null && !a.Registered).ToList();
            if (pending.Count == 0 && creation.HeldCount == 0) { return; }
            DrawHeading(listing, heading: "RR_EvidenceRecovery_Title".Translate(),
                detail: "RR_EvidenceRecovery_Explanation".Translate());
            listing.Label("RR_EvidenceRecovery_Held".Translate(creation.HeldCount));
            foreach (EvidenceCreationAttempt attempt in pending)
            {
                string id = attempt.CoordinateId;
                CoordinateRecord coordinate = campaign.Coordinates.FirstOrDefault(c => c.Id == id);
                listing.Label("RR_EvidenceRecovery_Identity".Translate(
                    coordinate == null ? id : coordinate.AddressCode,
                    attempt.ItemLoadId ?? "RR_EvidenceRecovery_NoOriginal".Translate().ToString()));
                if (!string.IsNullOrEmpty(attempt.FailureKey)) { listing.Label(attempt.FailureKey.Translate()); }
                Thing original = attempt.Item;
                if (original != null && !original.Destroyed && original.Spawned &&
                    original.Map != null && !original.Map.Disposed && Find.Maps.Contains(original.Map) &&
                    !original.Position.Fogged(original.Map) && listing.ButtonText("RR_EvidenceRecovery_Locate".Translate()))
                { CameraJumper.TryJumpAndSelect(original); }
                if (coordinate != null && creation.Readiness().Success && listing.ButtonText("RR_EvidenceRecovery_Retry".Translate()))
                { ShowResult(campaign.EnsureRouteRecording(coordinate)); }
                listing.Gap(8f);
            }
            listing.GapLine();
        }
    }
}
