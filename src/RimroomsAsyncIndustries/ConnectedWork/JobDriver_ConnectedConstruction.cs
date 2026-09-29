using System.Collections.Generic;
using RimroomsAsyncIndustries.ConnectedWork.Adapters;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// Put the carried material into the build site the worker carried it to.
    ///
    /// Every step here is Core's own: carry to the container, step off the blueprint's
    /// footprint, turn a blueprint into a frame if this is its first material, and deposit
    /// into the frame's own resource container. Using Core's
    /// <c>MakeSolidThingFromBlueprintIfNecessary</c> rather than a private equivalent is
    /// exactly what makes a first delivery to an untouched blueprint work, and it is the
    /// reason blueprints did not have to be excluded from this family.
    ///
    /// The material is kept in hand if the deposit does not finish, so a retry still has
    /// it; the lease bounds how long that can go on, and it is a real stack the whole time.
    /// </summary>
    public sealed class JobDriver_ConnectedDeliverToSite : JobDriver
    {
        private Thing Site { get { return job.targetB.Thing; } }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // A site that tracks enroute deliveries does its own accounting across several
            // haulers, so it must not be reserved exclusively. Core reserves the same way.
            if (Site is IHaulEnroute) { return true; }
            return pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            AddFinishAction(FinishDelivery);
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnDestroyedOrNull(TargetIndex.B);
            this.FailOnForbidden(TargetIndex.B);
            this.FailOn(() => LiveIntent() == null);
            yield return Toils_Haul.CarryHauledThingToContainer();
            yield return Toils_Goto.MoveOffTargetBlueprint(TargetIndex.B);
            yield return Toils_Construct.MakeSolidThingFromBlueprintIfNecessary(TargetIndex.B);
            yield return Toils_Haul.DepositHauledThingInContainer(TargetIndex.B, TargetIndex.None);
        }

        private void FinishDelivery(JobCondition condition)
        {
            RimroomsConnectedWorkComponent work = ConnectedWorkJobs.Work();
            ConnectedWorkIntent intent = LiveIntent();
            if (work == null || intent == null || intent.Phase != ConnectedWorkPhase.Carrying) { return; }
            Thing carried = pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (carried != null && carried == intent.Cargo)
            {
                // Still in hand: the deposit did not finish. Leave the trip live so the
                // next pass tries again rather than abandoning material at a build site.
                return;
            }
            work.Close(intent, ConnectedWorkPhase.Completed, null);
        }

        private ConnectedWorkIntent LiveIntent()
        { return ConnectedWorkJobs.LiveIntentFor(pawn, ConnectedWorkAdapters.ConstructionSupply); }
    }
}
