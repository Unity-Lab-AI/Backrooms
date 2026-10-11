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
        /// <summary>Not saved: re-resolved from the station after a load.</summary>
        private CompRimroomsGate resolvedGate;

        /// <summary>
        /// The gate this station holds a window for: its own console or one of its relief links,
        /// resolved through `BoundConsoles` exactly as the staffing work giver offers it.
        /// </summary>
        private CompRimroomsGate Gate
        {
            get
            {
                Thing station = TargetThingA;
                if (station == null) { return null; }
                if (resolvedGate != null && Holds(resolvedGate, station)) { return resolvedGate; }
                resolvedGate = null;
                CompRimroomsGateConsole console = station.TryGetComp<CompRimroomsGateConsole>();
                CompRimroomsGate direct = console == null ? null : console.Gate;
                if (direct != null && Holds(direct, station)) { resolvedGate = direct; return direct; }
                if (station.Map == null) { return null; }
                foreach (Building building in station.Map.listerBuildings.allBuildingsColonist)
                {
                    CompRimroomsGate gate = building.TryGetComp<CompRimroomsGate>();
                    if (gate != null && Holds(gate, station)) { resolvedGate = gate; return gate; }
                }
                return null;
            }
        }

        private static bool Holds(CompRimroomsGate gate, Thing station)
        {
            foreach (Thing candidate in gate.BoundConsoles)
            {
                if (candidate == station) { return true; }
            }
            return false;
        }

        /// <summary>
        /// The assigned operator may always take the post. Any other qualified staff member may
        /// take it only while a connection is being held, which is relief; startup stays with the
        /// assigned operator.
        /// </summary>
        private bool MayHold(CompRimroomsGate gate)
        {
            if (gate == null || !gate.Calibrated || pawn.Downed || pawn.InMentalState) { return false; }
            if (gate.AssignedOperator == pawn) { return true; }
            return gate.IsOpening && gate.QualifiedToStaff(pawn);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed)) { return false; }
            return TargetThingA != null && pawn.ReserveSittableOrSpot(TargetThingA.InteractionCell, job, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !MayHold(Gate));
            // **THE NEED CHECK THAT WAS NOT HERE, AND ITS ABSENCE KILLED A COLONIST.**
            //
            // Owner report, 2026-10-06: *"current a pawn dies at the comms console... and we cant
            // have them not going to eat or finding saftey"*. This toil is
            // `ToilCompleteMode.Never`, the job def is `suspendable: false`, and the failure
            // conditions above test the gate, the calibration, the operator's identity, `Downed`
            // and `InMentalState` -- **not one need**. So RimWorld could not pull the pawn off and
            // neither could we, and the only exits were collapse or the player noticing.
            //
            // The floor is checked here, separately and BEFORE the posture, so no posture can
            // switch it off. `GateWatch.MustLeave` is starving, exhausted, burning, bleeding out,
            // downed or in a mental state -- every one a state where standing still is the thing
            // doing the harm.
            this.FailOn(() => GateWatch.MustLeave(pawn)
                || GateWatch.Releases(pawn, Gate == null ? GateWatchPosture.Balanced : Gate.WatchPosture));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

            Toil station = ToilMaker.MakeToil("RimroomsGateOperatorStation");
            station.defaultCompleteMode = ToilCompleteMode.Never;
            station.tickIntervalAction = delegate(int delta)
            {
                CompRimroomsGate gate = Gate;
                if (!MayHold(gate))
                { EndJobWith(JobCondition.Incompletable); }
                // Asked every tick as well as in the FailOn, because a FailOn is evaluated by the
                // driver's own cadence and a pawn crossing into starvation between evaluations is
                // exactly the window this defect lived in. Ending here releases the post; the gate
                // keeps its own state and another pawn may take the station.
                else if (GateWatch.MustLeave(pawn)
                    || GateWatch.Releases(pawn, gate.WatchPosture))
                { EndJobWith(JobCondition.InterruptForced); }
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
