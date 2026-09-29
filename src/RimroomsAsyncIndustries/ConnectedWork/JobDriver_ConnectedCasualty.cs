using System.Collections.Generic;
using RimroomsAsyncIndustries.ConnectedWork.Adapters;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// Put the carried casualty into the bed that was found for them on this map.
    ///
    /// The worker arrives already carrying them, so this is only the placement half of
    /// Core's own take-to-bed job, built from Core's own bed toils: claim the bed, walk
    /// to it, release the reservation, tuck them in. Core owns the actual handoff, which
    /// is what keeps bed ownership, medical-bed rules and rescue notifications correct
    /// rather than reimplemented.
    ///
    /// The job deliberately does not keep the casualty in hand afterwards. If the
    /// placement fails, Core drops them where the worker stands — and they are on this
    /// side of the gate by then, downed and not in a bed, which is exactly the situation
    /// Core's own rescue work giver exists to handle. The cross-gate part of the trip has
    /// already succeeded, so it is recorded as finished and handed to local work.
    /// </summary>
    public sealed class JobDriver_ConnectedTakeToBed : JobDriver
    {
        private Pawn Patient { get { return job.targetA.Thing as Pawn; } }
        private Building_Bed DropBed { get { return job.targetB.Thing as Building_Bed; } }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            Pawn patient = Patient;
            Building_Bed bed = DropBed;
            if (patient == null || bed == null) { return false; }
            // Mirrors Core: the casualty's own claims are cleared before the carrier
            // takes them, and the bed is reserved by sleeping slot rather than as a whole.
            patient.ClearAllReservations();
            if (!pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed)) { return false; }
            return pawn.Reserve(job.targetB, job, bed.SleepingSlotsCount, 0, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            AddFinishAction(FinishRescue);
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnDestroyedOrNull(TargetIndex.B);
            this.FailOn(() => LiveIntent() == null);
            // This segment exists only because the worker is already holding them.
            this.FailOn(() => !pawn.IsCarryingPawn(Patient));
            this.FailOn(() => Patient == null || DropBed == null ||
                DropBed.ForPrisoners != Patient.IsPrisoner);

            yield return Toils_Bed.ClaimBedIfNonMedical(TargetIndex.B, TargetIndex.A);
            Toil goToBed = Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);
            goToBed.FailOnBedNoLongerUsable(TargetIndex.B, TargetIndex.A);
            yield return goToBed;
            yield return Toils_Reserve.Release(TargetIndex.B);
            yield return Toils_Bed.TuckIntoBed(TargetIndex.B, TargetIndex.A, rescued: true);
        }

        private void FinishRescue(JobCondition condition)
        {
            RimroomsConnectedWorkComponent work = ConnectedWorkJobs.Work();
            ConnectedWorkIntent intent = LiveIntent();
            if (work == null || intent == null || intent.Phase != ConnectedWorkPhase.Carrying) { return; }
            // Reaching this side at all is what the trip was for. Whether they ended in
            // the bed or were set down beside it, they are home and ordinary local work
            // can finish the job; either way nothing is duplicated or lost.
            if (pawn.Map != intent.StoreMap) { return; }
            bool inBed = Patient != null && Patient.InBed();
            work.Close(intent, ConnectedWorkPhase.Completed,
                inBed ? null : ConnectedCasualtyAdapter.ArrivedHomeKey);
        }

        private ConnectedWorkIntent LiveIntent()
        { return ConnectedWorkJobs.LiveIntentFor(pawn, ConnectedWorkAdapters.CasualtyRescue); }
    }
}
