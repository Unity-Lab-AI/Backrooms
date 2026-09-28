using System.Collections.Generic;
using RimroomsAsyncIndustries.Threats;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class JobDriver_DeployRouteAid : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        { return pawn.Reserve(TargetA, job, 1, -1, null, errorOnFailed); }
        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => pawn.Map == null || TargetThingB == null || TargetThingB.Destroyed ||
                pawn.inventory == null || !pawn.inventory.innerContainer.Contains(TargetThingB));
            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
            yield return Toils_General.Wait(90).WithProgressBarToilDelay(TargetIndex.A);
            Toil deploy = ToilMaker.MakeToil("RimroomsDeployRouteAid");
            deploy.initAction = delegate
            {
                var result = pawn.Map.GetComponent<FirstSliceSiteComponent>().DeployAid(pawn, TargetThingB, TargetA.Cell);
                if (!result.Success) { EndJobWith(JobCondition.Incompletable); }
            };
            yield return deploy;
        }
    }
}
