using System;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private int laboratoryBenchPage;

        private void DrawLaboratoryBinding(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Lab_Heading".Translate());
            listing.Label("RR_Lab_Explanation".Translate());
            RimroomsLaboratoryComponent laboratory = Current.Game == null ? null : Current.Game.GetComponent<RimroomsLaboratoryComponent>();
            if (laboratory == null || campaign == null) { listing.Label("RR_Lab_BranchUnavailable".Translate()); return; }
            if (laboratory.FaultKey != null) { listing.Label(laboratory.FaultKey.Translate()); return; }
            if (laboratory.HasDesignation)
            {
                listing.Label("RR_Lab_Designation".Translate(laboratory.LabelAtDesignation ?? laboratory.BenchDefName,
                    laboratory.BenchLoadId, laboratory.Revision));
                listing.Label("RR_Lab_Provider".Translate(laboratory.ProviderPackageId, laboratory.BenchDefName));
                Building_ResearchBench current = laboratory.DesignatedBench;
                if (current != null && laboratory.CanDesignate(current).Success && listing.ButtonText("RR_Lab_Locate".Translate()))
                { CameraJumper.TryJumpAndSelect(current); }
                if (listing.ButtonText("RR_Lab_Clear".Translate())) { ShowResult(laboratory.ClearDesignation()); }
            }
            CompanyActionResult readiness = laboratory.Readiness();
            listing.Label((readiness.Success ? "RR_Lab_Ready" : readiness.MessageKey).Translate());
            listing.Label("RR_Lab_NativeResearch".Translate());

            var candidates = laboratory.AvailableBenches().OrderBy(b => b.def.defName).ThenBy(b => b.thingIDNumber).ToList();
            const int pageSize = 6;
            int pages = Math.Max(1, (candidates.Count + pageSize - 1) / pageSize);
            laboratoryBenchPage = Math.Max(0, Math.Min(laboratoryBenchPage, pages - 1));
            if (candidates.Count == 0) { listing.Label("RR_Lab_NoCandidates".Translate()); return; }
            listing.Label("RR_Lab_Candidates".Translate(candidates.Count, laboratoryBenchPage + 1, pages));
            if (laboratoryBenchPage > 0 && listing.ButtonText("RR_Lab_Previous".Translate())) { laboratoryBenchPage--; }
            if (laboratoryBenchPage + 1 < pages && listing.ButtonText("RR_Lab_Next".Translate())) { laboratoryBenchPage++; }
            foreach (Building_ResearchBench candidate in candidates.Skip(laboratoryBenchPage * pageSize).Take(pageSize))
            {
                listing.Gap(5f);
                listing.Label("RR_Lab_Candidate".Translate(candidate.LabelCap, candidate.Position.ToString()));
                if (candidate != laboratory.DesignatedBench && listing.ButtonText("RR_Lab_Designate".Translate(candidate.LabelCap)))
                { ShowResult(laboratory.DesignateBench(candidate)); }
                if (listing.ButtonText("RR_Lab_InspectCandidate".Translate(candidate.LabelCap)))
                {
                    if (laboratory.CanDesignate(candidate).Success) { CameraJumper.TryJumpAndSelect(candidate); }
                    else { ShowResult(laboratory.CanDesignate(candidate)); }
                }
            }
            listing.GapLine();
        }
    }
}
