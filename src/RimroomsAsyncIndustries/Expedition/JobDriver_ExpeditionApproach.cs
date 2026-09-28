using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Expedition
{
    /// <summary>Native pathing reaches the saved threshold before the controller may transfer.</summary>
    public sealed class JobDriver_ExpeditionApproach : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        { return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed); }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => !Current.Game.GetComponent<RimroomsExpeditionComponent>().IsTransitOrderValid(pawn, job));
            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
            Toil wait = ToilMaker.MakeToil("RR_WaitAtThreshold");
            wait.initAction = () => pawn.pather.StopDead();
            wait.defaultCompleteMode = ToilCompleteMode.Never;
            yield return wait;
        }
    }

    public sealed class JobDriver_CarryToReturnAnchor : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        { return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed); }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOn(() => !Current.Game.GetComponent<RimroomsExpeditionComponent>().IsTransitOrderValid(pawn, job));
            this.FailOn(() => job.targetA.Thing is Pawn patient && !patient.Downed);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch).FailOnSomeonePhysicallyInteracting(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A);
            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            Toil wait = ToilMaker.MakeToil("RR_CasualtyAtThreshold");
            wait.initAction = () => pawn.pather.StopDead();
            wait.defaultCompleteMode = ToilCompleteMode.Never;
            yield return wait;
        }
    }
}
