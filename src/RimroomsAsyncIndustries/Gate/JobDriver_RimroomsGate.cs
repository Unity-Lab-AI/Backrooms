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

    /// <summary>
    /// Reconditioning the assembly. Deliberately the same shape as calibration, down to the
    /// skill and the progress bar, because it is the same colonist at the same console doing
    /// the same kind of careful work: monitoring and adjusting rather than repairing.
    /// </summary>
    public sealed class JobDriver_RRReconditionGate : JobDriver
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
            Scribe_Values.Look(ref workDone, "rr_gateReconditionWorkDone", 0f);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed)) { return false; }
            return TargetThingA != null && pawn.ReserveSittableOrSpot(TargetThingA.InteractionCell, job, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Gate == null || !Gate.CanRecondition(pawn));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

            Toil work = ToilMaker.MakeToil("RimroomsGateReconditionWork");
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.tickIntervalAction = delegate(int delta)
            {
                CompRimroomsGate gate = Gate;
                if (gate == null || !gate.CanRecondition(pawn))
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                workDone += pawn.GetStatValue(StatDefOf.ResearchSpeed) * delta;
                pawn.skills.Learn(SkillDefOf.Intellectual, 0.1f * delta);
                pawn.GainComfortFromCellIfPossible(delta, chairsOnly: true);
                // **Asked for THIS pawn.** A trained technician (`RR_Cert_ReserveTechnician`)
                // services the gate for less work; everybody else needs exactly what they
                // always did. The progress bar below asks the same question, so the bar and
                // the completion cannot disagree about how far along the job is.
                if (workDone >= gate.ReconditionWorkFor(pawn))
                {
                    CompanyActionResult result = gate.CompleteReconditioning(pawn);
                    EndJobWith(result.Success ? JobCondition.Succeeded : JobCondition.Incompletable);
                }
            };
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            work.activeSkill = () => SkillDefOf.Intellectual;
            work.WithProgressBar(TargetIndex.A,
                () => Gate == null ? 0f : workDone / Gate.ReconditionWorkFor(pawn));
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
                CompRimroomsGate gate = Gate;
                if (gate == null || gate.AssignedOperator != pawn || pawn.Downed || pawn.InMentalState)
                { EndJobWith(JobCondition.Incompletable); }
                else
                {
                    pawn.GainComfortFromCellIfPossible(delta, chairsOnly: true);
                    // Bringing a connection up is learned work, like calibrating the same
                    // machine. Standing watch over a gate that is not ramping teaches nothing,
                    // which is why this is inside the check rather than beside it.
                    if (gate.IsSpinningUp && gate.SpinUpIsSupported)
                    { pawn.skills.Learn(SkillDefOf.Intellectual, 0.1f * delta); }
                }
            };
            station.FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell);
            station.activeSkill = () => SkillDefOf.Intellectual;
            // While a connection is ramping this shows the real progress, which is what makes
            // the owner's "like a item build in a way" literally true at the console. With no
            // ramp running it falls back to the plain on-station indicator it always was.
            station.WithProgressBar(TargetIndex.A, delegate
            {
                CompRimroomsGate gate = Gate;
                if (gate == null) { return 0f; }
                if (gate.IsSpinningUp) { return gate.SpinUpProgress; }
                return gate.IsOperatorOnStation ? 1f : 0f;
            });
            yield return station;
        }
    }
}
