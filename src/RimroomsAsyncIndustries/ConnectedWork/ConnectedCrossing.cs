using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>What one attempt to take the next hop toward a destination produced.</summary>
    internal enum ConnectedCrossingOutcome
    {
        /// <summary>A real crossing job for the next hop. The caller owns counting the attempt.</summary>
        Step = 0,

        /// <summary>
        /// Not right now. A bounded route search that has not finished, an approach cell
        /// that is currently blocked, forbidden or unreachable, or a missing job def. None
        /// of these is an answer about whether the trip is possible, so the caller must
        /// leave the record live and try again later.
        /// </summary>
        NotYet = 1,

        /// <summary>
        /// The reachable graph was genuinely exhausted. This is the only outcome that
        /// means "there is no way there", and the only one that should end a trip.
        /// </summary>
        NoRoute = 2
    }

    /// <summary>
    /// Taking one hop toward a connected map, for any kind of cross-map work.
    ///
    /// There is exactly one implementation of stepping through a gate for work, shared
    /// by the carry families and by travel-to-work, and it hands out the same ordinary
    /// crossing job the player's own travel order uses. That matters because the rules
    /// attached to it are not decoration: automatic work respects this pawn's own danger
    /// policy, its allowed area and locked or forbidden doors, and a player order may use
    /// Deadly where work never may. A second copy of this would drift, and the drift
    /// would be a colonist walking into something the player told it to avoid.
    ///
    /// Deliberately left to the caller: the attempt cap and what a refusal costs. A
    /// carry trip that runs out of attempts has failed with cargo in hand and is worth
    /// the player's attention; a deployment that runs out has cost nothing but a walk.
    /// Those are different endings and the record types close differently, so the
    /// bookkeeping stays with whoever owns the record.
    /// </summary>
    internal static class ConnectedCrossing
    {
        internal static ConnectedCrossingOutcome StepToward(Pawn pawn, Map destination,
            RimroomsConnectedWorkComponent work, out Job job)
        {
            job = null;
            if (pawn == null || !pawn.Spawned || pawn.Map == null || destination == null || work == null)
            { return ConnectedCrossingOutcome.NotYet; }

            PortalRouteStep step;
            bool pending;
            if (!work.Routes.TryNextStep(pawn.Map, destination, out step, out pending))
            {
                // A bounded search that has not finished is not an answer. Only a search
                // that genuinely exhausted the reachable graph ends a trip.
                return pending ? ConnectedCrossingOutcome.NotYet : ConnectedCrossingOutcome.NoRoute;
            }

            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(PortalTravelService.CrossJobDefName);
            IntVec3 approach = step.Source.ApproachCell;
            if (definition == null || step.Source.Anchor == null || !approach.IsValid ||
                !approach.Standable(pawn.Map))
            { return ConnectedCrossingOutcome.NotYet; }

            // Automatic work respects this pawn's own danger policy, its allowed area and
            // locked or forbidden doors. A player order may use Deadly; work never does.
            if (step.Source.Anchor.IsForbidden(pawn) || approach.IsForbidden(pawn) ||
                !pawn.CanReach(approach, PathEndMode.OnCell, pawn.NormalMaxDanger()))
            { return ConnectedCrossingOutcome.NotYet; }

            job = JobMaker.MakeJob(definition, step.Source.Anchor, approach);
            job.count = 1;
            return ConnectedCrossingOutcome.Step;
        }
    }
}
