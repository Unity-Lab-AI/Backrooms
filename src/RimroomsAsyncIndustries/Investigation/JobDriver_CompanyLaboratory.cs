using System.Collections.Generic;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class JobDriver_CompanyLaboratory : JobDriver
    {
        private bool IsAnalysis { get { return job.def.defName == "RR_AnalyzeEvidence"; } }
        private RimroomsCampaignComponent Campaign { get { return Current.Game.GetComponent<RimroomsCampaignComponent>(); } }
        private EvidenceRecord Evidence
        { get { return Campaign.FindEvidence(TargetThingB == null ? null : TargetThingB.TryGetComp<CompRouteEvidence>()?.EvidenceId); } }
        private string projectId;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref projectId, "rr_projectId");
        }
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed) &&
                pawn.ReserveSittableOrSpot(TargetThingA.InteractionCell, job, errorOnFailed) &&
                (!IsAnalysis || pawn.Reserve(TargetB, job, 1, -1, null, errorOnFailed));
        }
        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !LaboratoryUtility.CanWork(pawn, TargetThingA, Campaign, 4));
            if (IsAnalysis)
            {
                yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch);
                yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            }
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);
            Toil work = ToilMaker.MakeToil("RimroomsLaboratoryWork");
            work.initAction = delegate
            {
                if (!IsAnalysis && projectId == null) { projectId = Campaign.ActiveProject?.Id; }
            };
            work.tickIntervalAction = delegate(int delta)
            {
                float amount = pawn.GetStatValue(StatDefOf.ResearchSpeed) *
                    TargetThingA.GetStatValue(StatDefOf.ResearchSpeedFactor) * delta;
                CompanyActionResult result;
                if (IsAnalysis)
                {
                    EvidenceRecord record = Evidence;
                    result = Campaign.AddAnalysisWork(record, pawn, TargetThingA, amount);
                    if (result.Success && record.Status == EvidenceStatus.Analyzed) { ReadyForNextToil(); }
                }
                else
                {
                    ProjectRecord project = Campaign.ActiveProject;
                    if (project == null || project.Id != projectId) { EndJobWith(JobCondition.Succeeded); return; }
                    result = Campaign.AddProjectWork(project, pawn, TargetThingA, amount);
                    if (result.Success && project.Completed) { ReadyForNextToil(); }
                }
                if (!result.Success) { EndJobWith(JobCondition.Incompletable); return; }
                pawn.skills.Learn(SkillDefOf.Intellectual, 0.1f * delta);
                pawn.GainComfortFromCellIfPossible(delta, chairsOnly: true);
            };
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            work.defaultCompleteMode = ToilCompleteMode.Delay;
            work.defaultDuration = 2500;
            work.activeSkill = () => SkillDefOf.Intellectual;
            work.WithProgressBar(TargetIndex.A, delegate
            {
                if (IsAnalysis) { return Evidence == null ? 0f : Evidence.AnalysisWork / TargetThingB.TryGetComp<CompRouteEvidence>().WorkRequired; }
                ProjectRecord project = Campaign.ActiveProject;
                RimroomsProjectDef definition = project == null ? null : DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(project.ResearchDefName);
                return definition == null ? 1f : project.WorkDone / definition.workRequired;
            });
            yield return work;
            if (IsAnalysis) { yield return Toils_Haul.DropCarriedThing(); }
        }
    }
}
