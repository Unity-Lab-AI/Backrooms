using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Facilities;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private readonly FacilityReport facilityReport = new FacilityReport();
        private string facilityCategory;
        private int facilityPage;

        private void DrawFacilities(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            if (!FacilityReport.Available(campaign.Headquarters))
            { listing.Label("RR_Company_MapUnavailable".Translate()); return; }
            facilityReport.RefreshIfNeeded(campaign);
            listing.Label("RR_Fac_Explanation".Translate());
            if (listing.ButtonText("RR_Fac_Refresh".Translate())) { facilityReport.RefreshIfNeeded(campaign, true); }
            listing.Label("RR_Fac_SummaryAge".Translate(Math.Max(0, Find.TickManager.TicksGame - facilityReport.CapturedTick)));
            listing.Label("RR_Fac_BedSummary".Translate(facilityReport.OrdinaryBedSlots,
                facilityReport.OrdinaryBedOwners, facilityReport.OrdinaryBedOccupants));
            listing.Label("RR_Fac_OtherBeds".Translate(facilityReport.MedicalSlots, facilityReport.OtherBedSlots));
            listing.Label("RR_Fac_BedLimit".Translate());
            if (facilityReport.StaffWithoutOwnedBeds.Count > 0)
            { listing.Label("RR_Fac_UnassignedStaff".Translate(string.Join(", ", facilityReport.StaffWithoutOwnedBeds.ToArray()))); }
            if (facilityReport.StaffNeedingCare.Count > 0)
            { listing.Label("RR_Fac_CareStaff".Translate(string.Join(", ", facilityReport.StaffNeedingCare.ToArray()))); }
            if (facilityReport.RefreshErrors > 0) { listing.Label("RR_Fac_ObservationErrors".Translate(facilityReport.RefreshErrors)); }
            if (listing.ButtonText("RR_Fac_OpenAssignments".Translate()))
            { OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign")); }
            listing.GapLine();

            string filter = facilityCategory == null ? "RR_Fac_All".Translate().ToString() :
                facilityCategory == "" ? "RR_Fac_Unclassified".Translate().ToString() :
                DefDatabase<RimroomsFacilityCategoryDef>.GetNamedSilentFail(facilityCategory)?.LabelCap.ToString() ?? facilityCategory;
            if (listing.ButtonText("RR_Fac_Filter".Translate(filter)))
            {
                var options = new List<FloatMenuOption> { new FloatMenuOption("RR_Fac_All".Translate(), () => SetFacilityFilter(null)) };
                foreach (RimroomsFacilityCategoryDef definition in DefDatabase<RimroomsFacilityCategoryDef>.AllDefsListForReading.OrderBy(d => d.displayOrder))
                {
                    string id = definition.defName;
                    int count = facilityReport.Buildings.Count(b => b.CategoryId == id);
                    options.Add(new FloatMenuOption(definition.LabelCap + " (" + count + ")", () => SetFacilityFilter(id)));
                }
                options.Add(new FloatMenuOption("RR_Fac_Unclassified".Translate(), () => SetFacilityFilter("")));
                Find.WindowStack.Add(new FloatMenu(options));
            }
            List<FacilityBuildingObservation> rows = facilityReport.Buildings.Where(b => facilityCategory == null ||
                (b.CategoryId ?? "") == facilityCategory).ToList();
            const int pageSize = 12;
            int pages = Math.Max(1, (rows.Count + pageSize - 1) / pageSize);
            facilityPage = Math.Max(0, Math.Min(facilityPage, pages - 1));
            listing.Label("RR_Fac_Page".Translate(facilityPage + 1, pages, rows.Count));
            if (facilityPage > 0 && listing.ButtonText("RR_Fac_Previous".Translate())) { facilityPage--; }
            if (facilityPage + 1 < pages && listing.ButtonText("RR_Fac_Next".Translate())) { facilityPage++; }
            if (rows.Count == 0) { listing.Label("RR_Fac_None".Translate()); }
            foreach (FacilityBuildingObservation row in rows.Skip(facilityPage * pageSize).Take(pageSize))
            {
                listing.GapLine();
                listing.Label(row.Label);
                listing.Label("RR_Fac_Condition".Translate(row.HitPoints, row.MaxHitPoints));
                if (row.HasRoom)
                {
                    string temperature = float.IsNaN(row.Temperature) || float.IsInfinity(row.Temperature)
                        ? "RR_Fac_Unavailable".Translate().ToString() : row.Temperature.ToString("F1") + " °C";
                    listing.Label("RR_Fac_Room".Translate(row.RoomLabel, row.RoomCells, row.UnroofedCells, temperature));
                    if (row.Outdoors) { listing.Label("RR_Fac_OutdoorTemperature".Translate()); }
                }
                else { listing.Label("RR_Fac_NoRoom".Translate()); }
                if (row.PowerOn.HasValue)
                { listing.Label((row.PowerOn.Value ? "RR_Fac_Powered" : "RR_Fac_Unpowered").Translate()); }
                if (row.InteractionCellClear.HasValue)
                { listing.Label((row.InteractionCellClear.Value ? "RR_Fac_InteractionClear" : "RR_Fac_InteractionBlocked").Translate()); }
                if (row.BedTypeKey != null)
                { listing.Label("RR_Fac_BedRow".Translate(row.BedTypeKey.Translate(), row.BedSlots, row.BedOwners, row.BedOccupants)); }
                Building target = row.Building;
                if (listing.ButtonText("RR_Fac_Inspect".Translate(row.Label)))
                {
                    if (FacilityReport.Inspectable(target, campaign.Headquarters)) { CameraJumper.TryJumpAndSelect(target); }
                    else { Messages.Message("RR_Fac_TargetUnavailable".Translate(), MessageTypeDefOf.RejectInput, false); }
                }
                if (FacilityReport.Inspectable(target, campaign.Headquarters) && target.TryGetComp<CompRimroomsGate>()?.IsDesignated == true &&
                    listing.ButtonText("RR_Fac_OpenMachine".Translate())) { selectedPane = 7; scrollPosition = UnityEngine.Vector2.zero; }
            }
        }

        private void SetFacilityFilter(string id)
        { facilityCategory = id; facilityPage = 0; scrollPosition = UnityEngine.Vector2.zero; }
    }
}
