using RimWorld;
using RimroomsAsyncIndustries.Portals;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// How cross-map work reaches a pawn: as an ordinary WorkGiver, inside Core's own
    /// <c>JobGiver_Work</c>, in that pawn's own priority and schedule order. Nothing
    /// here pushes a job at anybody and nothing is ever marked player-forced, so
    /// hunger, sleep, danger, drafting, mental states, disabled work types and manual
    /// priorities all keep working exactly as they did.
    ///
    /// Each family is registered twice, as two WorkGiverDefs sharing this class:
    ///
    /// * a **continuation** giver, high in its work type, which only ever finishes a
    ///   trip the worker already committed to;
    /// * a **planning** giver, just below its native counterpart, which only ever
    ///   starts a new one.
    ///
    /// The split exists because those two need opposite priorities. Starting a trip
    /// through a gate must not outrank ordinary local work of the same kind. But a
    /// worker already standing on the far side holding leased cargo must not lose to
    /// local work either, or it would wander off and abandon the delivery. One giver
    /// cannot be both low and high, so there are two.
    /// </summary>
    public abstract class WorkGiver_ConnectedWork : WorkGiver
    {
        protected abstract string AdapterId { get; }

        /// <summary>True for the high-priority half that only continues committed trips.</summary>
        protected abstract bool ContinueOnly { get; }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            RimroomsConnectedWorkComponent work = Work();
            if (work == null || !work.CanOperate || pawn == null || !pawn.Spawned) { return true; }
            bool committed = work.ActiveIntentFor(pawn) != null;
            if (ContinueOnly) { return !committed; }
            if (committed || !work.MayPlanFor(pawn)) { return true; }
            // Nothing to plan against until this branch actually remembers a gate.
            RimroomsPortalNetwork network = Network();
            return network == null || network.HasStateFault || network.Connections.Count == 0;
        }

        public override Job NonScanJob(Pawn pawn)
        {
            RimroomsConnectedWorkComponent work = Work();
            ConnectedWorkAdapter adapter = ConnectedWorkAdapters.Get(AdapterId);
            RimroomsPortalCrossingService crossings = Crossings();
            if (work == null || !work.CanOperate || adapter == null || crossings == null ||
                crossings.StateFaultKey != null || pawn == null || !pawn.Spawned)
            { return null; }
            // The gate rule, asked on every path into this layer and not only at the
            // threshold: a colonist may decide to cross to work, nothing else may
            // decide anything about a gate.
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }
            // Someone held inside an unresolved crossing belongs to the crossing
            // service until its receipt is reconciled. Never hand them a job.
            if (crossings.HasUnresolvedCrossing(pawn)) { return null; }
            // The one legitimate moment this worker's allowed area on this map is
            // observable is while it is standing on it. Write it down every pass so a
            // later planning decision about this map is made on evidence.
            work.ObserveAreaHere(pawn);

            ConnectedWorkIntent intent = work.ActiveIntentFor(pawn);
            if (intent != null)
            {
                // Only the continuation half advances a committed trip, and only for
                // the family that owns it.
                if (!ContinueOnly || intent.AdapterId != AdapterId) { return null; }
                return Continue(intent, adapter, pawn, work);
            }
            if (ContinueOnly || !work.MayPlanFor(pawn)) { return null; }
            work.NotePlanningPass(pawn);
            intent = adapter.TryPlan(pawn, work);
            return intent == null ? null : Continue(intent, adapter, pawn, work);
        }

        /// <summary>
        /// One segment of the trip, chosen from the intent's phase and the worker's
        /// actual current map. Nothing is stored about "which step comes next", so a
        /// reload, an interruption or an unexpected location all resolve here.
        /// </summary>
        private Job Continue(ConnectedWorkIntent intent, ConnectedWorkAdapter adapter, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            string blocking = work.LiveFailureKey(intent);
            if (blocking != null)
            {
                work.Close(intent, RimroomsConnectedWorkComponent.LifecyclePhaseFor(blocking), blocking);
                return null;
            }
            if (intent.Phase == ConnectedWorkPhase.Planned)
            {
                if (pawn.Map != intent.FetchMap) { return CrossToward(intent, pawn, work, intent.FetchMap); }
                string refusal = adapter.RevalidateAtFetchSide(intent, pawn);
                if (refusal != null)
                {
                    // We crossed for this and were turned away on arrival. Remember the
                    // map for a while so the next pass does not repeat the walk.
                    if (pawn.Map != intent.StoreMap) { work.NoteDestinationRefused(pawn, pawn.Map); }
                    work.Close(intent, adapter.TerminalPhaseFor(refusal), refusal);
                    return null;
                }
                work.RenewLease(intent);
                return adapter.FetchJob(intent, pawn);
            }
            if (pawn.Map != intent.StoreMap) { return CrossToward(intent, pawn, work, intent.StoreMap); }
            string storeRefusal = adapter.RevalidateAtStoreSide(intent, pawn);
            if (storeRefusal != null)
            {
                work.Close(intent, adapter.TerminalPhaseFor(storeRefusal), storeRefusal);
                return null;
            }
            work.RenewLease(intent);
            return adapter.DeliverJob(intent, pawn);
        }

        /// <summary>
        /// Hand out one ordinary crossing job toward the next hop. This reuses the
        /// crossing the player's own travel order uses, so there is exactly one
        /// implementation of stepping through a gate, with one set of rules.
        /// </summary>
        private Job CrossToward(ConnectedWorkIntent intent, Pawn pawn,
            RimroomsConnectedWorkComponent work, Map destination)
        {
            // The loop guard. A route that keeps being refused at the threshold must
            // fail visibly rather than ordering the same walk forever. This bounds
            // retries, not hops: a legitimate multi-hop trip fits inside it.
            if (intent.CrossAttempts >= RimroomsConnectedWorkComponent.MaximumCrossAttempts)
            {
                work.NoteDestinationRefused(pawn, destination);
                work.Close(intent, ConnectedWorkPhase.Failed, "RR_ConnectedWork_RouteExhausted");
                return null;
            }
            PortalRouteStep step;
            bool pending;
            if (!work.Routes.TryNextStep(pawn.Map, destination, out step, out pending))
            {
                // A bounded search that has not finished is not an answer. Only a
                // search that genuinely exhausted the reachable graph ends the trip.
                if (!pending) { work.Close(intent, ConnectedWorkPhase.Cancelled, "RR_ConnectedWork_NoRoute"); }
                return null;
            }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(PortalTravelService.CrossJobDefName);
            IntVec3 approach = step.Source.ApproachCell;
            if (definition == null || step.Source.Anchor == null || !approach.IsValid ||
                !approach.Standable(pawn.Map))
            { return null; }
            // Automatic work respects this pawn's own danger policy, its allowed area
            // and locked or forbidden doors. A player order may use Deadly; work never.
            if (step.Source.Anchor.IsForbidden(pawn) || approach.IsForbidden(pawn) ||
                !pawn.CanReach(approach, PathEndMode.OnCell, pawn.NormalMaxDanger()))
            { return null; }
            Job job = JobMaker.MakeJob(definition, step.Source.Anchor, approach);
            job.count = 1;
            work.NoteCrossAttempt(intent);
            return job;
        }

        private static RimroomsConnectedWorkComponent Work()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsConnectedWorkComponent>(); }
        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }
        private static RimroomsPortalCrossingService Crossings()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalCrossingService>(); }
    }

    /// <summary>Starts a storage-hauling trip. Sits just below Core's own general hauling.</summary>
    public sealed class WorkGiver_ConnectedHauling : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.StorageHauling; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes a storage-hauling trip already under way. Sits high in hauling.</summary>
    public sealed class WorkGiver_ConnectedHaulingContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.StorageHauling; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Starts a trip to bring one of our own home. Sits just below native rescue.</summary>
    public sealed class WorkGiver_ConnectedCasualty : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.CasualtyRescue; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes carrying a casualty home. Sits just above native rescue.</summary>
    public sealed class WorkGiver_ConnectedCasualtyContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.CasualtyRescue; } }
        protected override bool ContinueOnly { get { return true; } }
    }
}
