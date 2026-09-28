using System.Collections.Generic;
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
        { get { return ThingRequest.ForGroup(ThingRequestGroup.ResearchBench); } }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            RimroomsLaboratoryComponent laboratory = Current.Game == null ? null : Current.Game.GetComponent<RimroomsLaboratoryComponent>();
            if (laboratory != null && laboratory.Readiness().Success && pawn != null && pawn.Spawned &&
                laboratory.DesignatedBench.Map == pawn.Map) { yield return laboratory.DesignatedBench; }
        }

        private Job FindWork(Pawn pawn, Thing bench, bool forced)
        {
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (!LaboratoryUtility.CanWork(pawn, bench, campaign, 4) || !pawn.CanReserveAndReach(bench, PathEndMode.InteractionCell, Danger.Some, 1, -1, null, forced) ||
                !pawn.CanReserveSittableOrSpot(bench.InteractionCell, forced)) { return null; }
            EvidenceRecord record = campaign.Evidence.FirstOrDefault(e => campaign.CanAnalyze(e, pawn, bench) && e.Item.Spawned &&
                !e.Item.IsForbidden(pawn) && pawn.CanReserveAndReach(e.Item, PathEndMode.ClosestTouch, Danger.Some, 1, -1, null, forced));
            if (record != null)
            {
                JobDef analysisDef = DefDatabase<JobDef>.GetNamedSilentFail("RR_AnalyzeEvidence");
                if (analysisDef == null) { return null; }
                Job analysis = JobMaker.MakeJob(analysisDef, bench, record.Item);
                analysis.count = 1;
                return analysis;
            }
            ProjectRecord project = campaign.ActiveProject;
            RimroomsProjectDef definition = project == null ? null : DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(project.ResearchDefName);
            if (definition == null || !LaboratoryUtility.CanWork(pawn, bench, campaign, definition.minimumIntellectual)) { return null; }
            JobDef researchDef = DefDatabase<JobDef>.GetNamedSilentFail("RR_CompanyResearch");
            return researchDef == null ? null : JobMaker.MakeJob(researchDef, bench);
        }
        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return FindWork(pawn, t, forced) != null; }
        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false) { return FindWork(pawn, t, forced); }
    }
}
