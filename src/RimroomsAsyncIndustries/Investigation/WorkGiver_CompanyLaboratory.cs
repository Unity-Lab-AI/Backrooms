using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class WorkGiver_CompanyLaboratory : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        { get { return ThingRequest.ForDef(DefDatabase<ThingDef>.GetNamed("RR_FieldAnalysisBench")); } }

        private Job FindWork(Pawn pawn, Thing bench, bool forced)
        {
            RimroomsCampaignComponent campaign = Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (!LaboratoryUtility.CanWork(pawn, bench, campaign, 4) || !pawn.CanReserveAndReach(bench, PathEndMode.InteractionCell, Danger.Some, 1, -1, null, forced) ||
                !pawn.CanReserveSittableOrSpot(bench.InteractionCell, forced)) { return null; }
            EvidenceRecord record = campaign.Evidence.FirstOrDefault(e => campaign.CanAnalyze(e, pawn, bench) && e.Item.Spawned &&
                !e.Item.IsForbidden(pawn) && pawn.CanReserveAndReach(e.Item, PathEndMode.ClosestTouch, Danger.Some, 1, -1, null, forced));
            if (record != null)
            {
                Job analysis = JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("RR_AnalyzeEvidence"), bench, record.Item);
                analysis.count = 1;
                return analysis;
            }
            ProjectRecord project = campaign.ActiveProject;
            RimroomsProjectDef definition = project == null ? null : DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(project.ResearchDefName);
            if (definition == null || !LaboratoryUtility.CanWork(pawn, bench, campaign, definition.minimumIntellectual)) { return null; }
            return JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("RR_CompanyResearch"), bench);
        }
        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return FindWork(pawn, t, forced) != null; }
        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false) { return FindWork(pawn, t, forced); }
    }
}
