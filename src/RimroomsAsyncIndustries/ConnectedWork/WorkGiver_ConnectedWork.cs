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
            // One commitment per worker, across both record kinds. Someone sent through
            // a gate to build must not also be promised a haul: it would abandon one of
            // the two, and which one it abandoned would depend on job-search timing.
            if (committed || work.ActiveDeploymentFor(pawn) != null || !work.MayPlanFor(pawn, AdapterId))
            { return true; }
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
            if (ContinueOnly || !work.MayPlanFor(pawn, AdapterId)) { return null; }
            // A worker already deployed somewhere is doing local work there on purpose.
            // Planning a carry trip for it would pull it straight back off that site.
            if (work.ActiveDeploymentFor(pawn) != null) { return null; }
            work.NotePlanningPass(pawn, AdapterId);
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
        /// Hand out one ordinary crossing job toward the next hop, through the single
        /// shared implementation in <see cref="ConnectedCrossing"/>. What stays here is
        /// only what is specific to a carry trip: the attempt cap, and the fact that a
        /// carry trip which ran out of attempts failed with cargo in real hands.
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
            Job job;
            ConnectedCrossingOutcome outcome = ConnectedCrossing.StepToward(pawn, destination, work, out job);
            if (outcome == ConnectedCrossingOutcome.NoRoute)
            {
                work.Close(intent, ConnectedWorkPhase.Cancelled, "RR_ConnectedWork_NoRoute");
                return null;
            }
            if (outcome != ConnectedCrossingOutcome.Step) { return null; }
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

    /// <summary>Starts a trip to bring building material to a site across a gate.</summary>
    public sealed class WorkGiver_ConnectedConstruction : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.ConstructionSupply; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes a material delivery already under way.</summary>
    public sealed class WorkGiver_ConnectedConstructionContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.ConstructionSupply; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Starts a trip to bring a bill the ingredients it is short of.</summary>
    public sealed class WorkGiver_ConnectedBill : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.BillIngredients; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes carrying ingredients to a bill.</summary>
    public sealed class WorkGiver_ConnectedBillContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.BillIngredients; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Starts a trip to bring medicine to a patient on the other side.</summary>
    public sealed class WorkGiver_ConnectedMedicine : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.MedicineSupply; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes carrying medicine to a patient.</summary>
    public sealed class WorkGiver_ConnectedMedicineContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.MedicineSupply; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Starts a trip to bring food to people who have none on their side.</summary>
    public sealed class WorkGiver_ConnectedFood : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.FoodSupply; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes carrying food through a gate.</summary>
    public sealed class WorkGiver_ConnectedFoodContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.FoodSupply; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Starts a trip to bring fuel or shells to something of ours that has run dry.</summary>
    public sealed class WorkGiver_ConnectedFuel : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.FuelSupply; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Finishes carrying fuel through a gate.</summary>
    public sealed class WorkGiver_ConnectedFuelContinue : WorkGiver_ConnectedWork
    {
        protected override string AdapterId { get { return ConnectedWorkAdapters.FuelSupply; } }
        protected override bool ContinueOnly { get { return true; } }
    }
}
