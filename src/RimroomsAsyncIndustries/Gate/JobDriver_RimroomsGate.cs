using System.Collections.Generic;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Gate
{
    public sealed class JobDriver_RRCalibrateGate : JobDriver
    {
        private float workDone;
        private CompRimroomsGate Gate
        {
            get
            {
                CompRimroomsGateConsole console = TargetThingA == null ? null : TargetThingA.TryGetComp<CompRimroomsGateConsole>();
                CompRimroomsGate gate = console == null ? null : console.Gate;
                return gate != null && gate.Console == TargetThingA ? gate : null;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workDone, "rr_gateCalibrationWorkDone", 0f);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed)) { return false; }
            return TargetThingA != null && pawn.ReserveSittableOrSpot(TargetThingA.InteractionCell, job, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Gate == null || !Gate.CanCalibrate(pawn));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

            Toil work = ToilMaker.MakeToil("RimroomsGateCalibrationWork");
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.tickIntervalAction = delegate(int delta)
            {
                CompRimroomsGate gate = Gate;
                if (gate == null || !gate.CanCalibrate(pawn))
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                workDone += pawn.GetStatValue(StatDefOf.ResearchSpeed) * delta;
                pawn.skills.Learn(SkillDefOf.Intellectual, 0.1f * delta);
                pawn.GainComfortFromCellIfPossible(delta, chairsOnly: true);
                if (workDone >= gate.CalibrationWorkRequired)
                {
                    CompanyActionResult result = gate.CompleteCalibration(pawn);
                    EndJobWith(result.Success ? JobCondition.Succeeded : JobCondition.Incompletable);
                }
            };
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            work.activeSkill = () => SkillDefOf.Intellectual;
            work.WithProgressBar(TargetIndex.A, () => Gate == null ? 0f : workDone / Gate.CalibrationWorkRequired);
            yield return work;
        }
    }

    /// <summary>A real, reserving console job. The gate reads this current job to determine operator readiness.</summary>
    public sealed class JobDriver_RROperateGate : JobDriver
    {
        private CompRimroomsGate Gate
        {
            get
            {
                CompRimroomsGateConsole console = TargetThingA == null ? null : TargetThingA.TryGetComp<CompRimroomsGateConsole>();
                CompRimroomsGate gate = console == null ? null : console.Gate;
                return gate != null && gate.Console == TargetThingA ? gate : null;
            }
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed)) { return false; }
            return TargetThingA != null && pawn.ReserveSittableOrSpot(TargetThingA.InteractionCell, job, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Gate == null || !Gate.Calibrated || Gate.AssignedOperator != pawn || pawn.Downed || pawn.InMentalState);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

            Toil station = ToilMaker.MakeToil("RimroomsGateOperatorStation");
            station.defaultCompleteMode = ToilCompleteMode.Never;
            station.tickIntervalAction = delegate(int delta)
            {
                if (Gate == null || Gate.AssignedOperator != pawn || pawn.Downed || pawn.InMentalState)
                { EndJobWith(JobCondition.Incompletable); }
                else { pawn.GainComfortFromCellIfPossible(delta, chairsOnly: true); }
            };
            station.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            station.WithProgressBar(TargetIndex.A, () => Gate != null && Gate.IsOperatorOnStation ? 1f : 0f);
            yield return station;
        }
    }
}
