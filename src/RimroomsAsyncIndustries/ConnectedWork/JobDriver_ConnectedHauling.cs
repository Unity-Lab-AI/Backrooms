using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// Take physical hold of the object on the map that actually holds it. This is an
    /// ordinary local job: the worker is standing on this map, the reservation is a
    /// real native reservation, and the quantity is whatever Core's own carry code
    /// actually managed to pick up.
    ///
    /// The outcome is recorded from a job finish action rather than a final toil, so
    /// it is recorded whether the job succeeded, was interrupted, or failed partway.
    /// </summary>
    public sealed class JobDriver_ConnectedFetch : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, job.count, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            AddFinishAction(FinishFetch);
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnForbidden(TargetIndex.A);
            this.FailOn(() => LiveIntent() == null);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch)
                .FailOnSomeonePhysicallyInteracting(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A, putRemainderInQueue: false,
                subtractNumTakenFromJobCount: false, failIfStackCountLessThanJobCount: false,
                reserve: true, canTakeFromInventory: false);
        }

        private void FinishFetch(JobCondition condition)
        {
            RimroomsConnectedWorkComponent work = ConnectedWorkJobs.Work();
            ConnectedWorkIntent intent = LiveIntent();
            if (work == null || intent == null || intent.Phase != ConnectedWorkPhase.Planned) { return; }
            Thing carried = pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (carried == null || intent.SourceThing == null || carried.def != intent.SourceThing.def)
            {
                // Nothing was taken hold of. Nothing physical changed either, so this
                // is an ordinary replan rather than a failure worth reporting.
                work.Close(intent, ConnectedWorkPhase.Cancelled, "RR_ConnectedWork_PickupFailed");
                return;
            }
            // Observed, never requested. A partial pickup legitimately splits the
            // stack into a different object, and that object is what travels.
            work.NotePickup(intent, carried, carried.stackCount);
        }

        private ConnectedWorkIntent LiveIntent()
        { return ConnectedWorkJobs.LiveHaulingIntent(pawn); }
    }

    /// <summary>
    /// Place the carried object into storage the destination map's own settings
    /// accept, using Core's own hauling toils so stacking, partial fills and a cell
    /// that turns out to be full all behave exactly as they do for any other haul.
    /// </summary>
    public sealed class JobDriver_ConnectedDeliver : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            AddFinishAction(FinishDelivery);
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnBurningImmobile(TargetIndex.B);
            this.FailOnForbidden(TargetIndex.B);
            this.FailOn(() => LiveIntent() == null);
            Toil carryToCell = Toils_Haul.CarryHauledThingToCell(TargetIndex.B);
            yield return carryToCell;
            // Core's own placement toil, including its jump back to the carry step
            // when the chosen cell cannot take the whole stack.
            yield return Toils_Haul.PlaceHauledThingInCell(TargetIndex.B, carryToCell, storageMode: true);
        }

        private void FinishDelivery(JobCondition condition)
        { ConnectedWorkJobs.FinishHaulDelivery(pawn); }

        private ConnectedWorkIntent LiveIntent()
        { return ConnectedWorkJobs.LiveHaulingIntent(pawn); }
    }

    /// <summary>
    /// Place the carried object into a storage container rather than onto a cell,
    /// using Core's own container toils. This is the path a shelf never takes (a
    /// shelf is a slot-group parent and so is delivered to by cell) but that graves
    /// and the storage-framework buildings do, which is how those work here without
    /// an adapter written for each one.
    /// </summary>
    public sealed class JobDriver_ConnectedDepositInContainer : JobDriver
    {
        private Thing Container { get { return job.targetB.Thing; } }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // Mirrors Core: a destination that tracks enroute deliveries manages its
            // own accounting and must not be reserved exclusively here.
            if (Container is IHaulEnroute) { return true; }
            return pawn.Reserve(job.targetB, job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            AddFinishAction(FinishDelivery);
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnDestroyedOrNull(TargetIndex.B);
            this.FailOnForbidden(TargetIndex.B);
            this.FailOn(() => ConnectedWorkJobs.LiveHaulingIntent(pawn) == null);
            yield return Toils_Haul.CarryHauledThingToContainer();
            yield return Toils_Haul.DepositHauledThingInContainer(TargetIndex.B, TargetIndex.None);
        }

        private void FinishDelivery(JobCondition condition)
        { ConnectedWorkJobs.FinishHaulDelivery(pawn); }
    }

    /// <summary>Shared lookups for the hauling segment drivers.</summary>
    internal static class ConnectedWorkJobs
    {
        internal static RimroomsConnectedWorkComponent Work()
        {
            return Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsConnectedWorkComponent>();
        }

        internal static ConnectedWorkIntent LiveHaulingIntent(Pawn pawn)
        {
            RimroomsConnectedWorkComponent work = Work();
            ConnectedWorkIntent intent = work == null ? null : work.ActiveIntentFor(pawn);
            return intent != null && intent.AdapterId == ConnectedWorkAdapters.StorageHauling
                ? intent : null;
        }

        /// <summary>
        /// One delivery outcome rule for both the cell and the container route, so the
        /// two can never disagree about what counts as delivered.
        /// </summary>
        internal static void FinishHaulDelivery(Pawn pawn)
        {
            RimroomsConnectedWorkComponent work = Work();
            ConnectedWorkIntent intent = LiveHaulingIntent(pawn);
            if (work == null || intent == null || intent.Phase != ConnectedWorkPhase.Carrying) { return; }
            Thing carried = pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (carried != null && carried == intent.Cargo)
            {
                // Still in hand, so the placement did not finish. Leave the trip live
                // and let the next pass try again; the lease bounds how long that can
                // go on, and the object is physically held the whole time.
                return;
            }
            // Out of hand means placed. The original object may legitimately no longer
            // exist, because merging into an existing stack destroys it; that is a
            // completed delivery, not a lost item.
            work.Close(intent, ConnectedWorkPhase.Completed, null);
        }
    }
}
