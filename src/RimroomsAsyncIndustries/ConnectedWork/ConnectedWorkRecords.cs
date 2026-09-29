using Verse;
using RimroomsAsyncIndustries.Portals;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// Where one cross-map work intent stands. Only Planned and Carrying are live;
    /// the rest are terminal and release the intent's planning lease.
    ///
    /// The phase deliberately does not encode which physical segment comes next.
    /// That is derived from the phase plus the worker's actual current map, so a
    /// save reloaded mid-route resumes without storing a fragile step index, and a
    /// worker who ended up somewhere unexpected is still handled by one rule.
    /// </summary>
    public enum ConnectedWorkPhase
    {
        Planned = 0,
        Carrying = 1,
        Completed = 2,
        Cancelled = 3,
        Failed = 4
    }

    /// <summary>
    /// One saved cross-map work intent: a worker, one actual original object on its
    /// own map, the map the work finishes on, and the route context the plan was
    /// made against. The intent is the continuation state for the whole trip; a
    /// native job only ever owns one local segment of it.
    ///
    /// The intent also owns its planning lease. A lease is bounded, expiring and
    /// keyed by the actual Thing plus a quantity, and it is deliberately *not* a
    /// native reservation: it excludes no native pawn and grants no claim. It only
    /// stops this company's own planners from promising the same stack twice.
    /// Native availability is rechecked definitively on arrival.
    /// </summary>
    public sealed class ConnectedWorkIntent : IExposable
    {
        private string id;
        private string branchId;
        private string adapterId;
        private int adapterVersion;

        private Pawn pawn;
        private string pawnLoadId;

        // The original object, on the map that actually holds it. Never a Def and
        // a count: a quantity is only ever a slice of one real stack.
        private Thing sourceThing;
        private string sourceThingLoadId;
        private Map fetchMap;
        private IntVec3 fetchCell = IntVec3.Invalid;
        private int requestedCount;

        // Observed after an actual pickup. A partial pickup legitimately produces a
        // different Thing from the source stack, so the carried object is recorded
        // separately instead of being assumed identical.
        private Thing cargo;
        private string cargoLoadId;
        private int observedCount;

        private Map storeMap;
        private IntVec3 candidateStoreCell = IntVec3.Invalid;

        // The native object the work finally belongs to: a bill giver, a frame, a
        // patient. Storage hauling has none. The field exists from the first schema
        // so the later adapter families need no migration to record theirs.
        private Thing finalTarget;
        private string finalTargetLoadId;

        private string connectionId;
        private string openingId;
        private long topologyRevision;

        private ConnectedWorkPhase phase;
        private string failureKey;
        private int openedTick;
        private int leaseExpiryTick;
        private int crossAttempts;

        public string Id { get { return id; } }
        public string BranchId { get { return branchId; } }
        public string AdapterId { get { return adapterId; } }
        public int AdapterVersion { get { return adapterVersion; } }
        public Pawn Pawn { get { return pawn; } }
        public string PawnLoadId { get { return pawnLoadId; } }
        public Thing SourceThing { get { return sourceThing; } }
        public string SourceThingLoadId { get { return sourceThingLoadId; } }
        public Map FetchMap { get { return fetchMap; } }
        public IntVec3 FetchCell { get { return fetchCell; } }
        public int RequestedCount { get { return requestedCount; } }
        public Thing Cargo { get { return cargo; } }
        public string CargoLoadId { get { return cargoLoadId; } }
        public int ObservedCount { get { return observedCount; } }
        public Map StoreMap { get { return storeMap; } }
        public IntVec3 CandidateStoreCell { get { return candidateStoreCell; } }
        public Thing FinalTarget { get { return finalTarget; } }
        public string FinalTargetLoadId { get { return finalTargetLoadId; } }
        public string ConnectionId { get { return connectionId; } }
        public string OpeningId { get { return openingId; } }
        public long TopologyRevision { get { return topologyRevision; } }
        public ConnectedWorkPhase Phase { get { return phase; } }
        public string FailureKey { get { return failureKey; } }
        public int OpenedTick { get { return openedTick; } }
        public int LeaseExpiryTick { get { return leaseExpiryTick; } }
        public int CrossAttempts { get { return crossAttempts; } }

        public bool IsLive
        { get { return phase == ConnectedWorkPhase.Planned || phase == ConnectedWorkPhase.Carrying; } }

        /// <summary>
        /// The lease is held only while the worker is still on its way to the
        /// object. Once the quantity is physically in hand the carry owner holds it
        /// and the remaining source stack is free for anyone again.
        /// </summary>
        public bool HoldsLease { get { return phase == ConnectedWorkPhase.Planned; } }

        public ConnectedWorkIntent() { }

        internal ConnectedWorkIntent(string id, string branchId, ConnectedWorkAdapter adapter, Pawn pawn,
            Thing sourceThing, Map storeMap, IntVec3 candidateStoreCell, int requestedCount,
            Thing finalTarget, PortalRouteStep plannedStep, long topologyRevision, int tick, int leaseTicks)
        {
            this.id = id;
            this.branchId = branchId;
            adapterId = adapter.AdapterId;
            adapterVersion = adapter.AdapterVersion;
            this.pawn = pawn;
            pawnLoadId = pawn.GetUniqueLoadID();
            this.sourceThing = sourceThing;
            sourceThingLoadId = sourceThing.GetUniqueLoadID();
            fetchMap = sourceThing.Map;
            fetchCell = sourceThing.Position;
            this.requestedCount = requestedCount;
            this.storeMap = storeMap;
            this.candidateStoreCell = candidateStoreCell;
            this.finalTarget = finalTarget;
            finalTargetLoadId = finalTarget == null ? null : finalTarget.GetUniqueLoadID();
            if (plannedStep != null && plannedStep.Connection != null)
            {
                connectionId = plannedStep.Connection.Id;
                openingId = plannedStep.Connection.OpeningId;
            }
            this.topologyRevision = topologyRevision;
            phase = ConnectedWorkPhase.Planned;
            openedTick = tick;
            leaseExpiryTick = tick + leaseTicks;
        }

        internal void RenewLease(int tick, int leaseTicks) { leaseExpiryTick = tick + leaseTicks; }

        internal void RecordPickup(Thing carried, int count, int tick, int leaseTicks)
        {
            cargo = carried;
            cargoLoadId = carried == null ? null : carried.GetUniqueLoadID();
            observedCount = count;
            phase = ConnectedWorkPhase.Carrying;
            // The lease is released by the phase change; the window is renewed so
            // the return trip has its own bounded life rather than inheriting the
            // remainder of the outbound one.
            RenewLease(tick, leaseTicks);
        }

        internal void NoteCrossAttempt() { crossAttempts++; }

        /// <summary>
        /// The destination the definitive native search actually chose on arrival,
        /// replacing the candidate the plan was made against.
        /// </summary>
        internal void RecordResolvedStoreCell(IntVec3 cell)
        {
            candidateStoreCell = cell;
            finalTarget = null;
            finalTargetLoadId = null;
        }

        /// <summary>
        /// The destination is a container rather than a cell. Recorded in the
        /// final-target field, which is exactly what that field is for: the native
        /// object the work finally belongs to.
        /// </summary>
        internal void RecordResolvedContainer(Thing container)
        {
            finalTarget = container;
            finalTargetLoadId = container == null ? null : container.GetUniqueLoadID();
            candidateStoreCell = IntVec3.Invalid;
        }

        internal void Close(ConnectedWorkPhase terminalPhase, string key)
        {
            phase = terminalPhase;
            failureKey = key;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "id");
            Scribe_Values.Look(ref branchId, "branchId");
            Scribe_Values.Look(ref adapterId, "adapterId");
            Scribe_Values.Look(ref adapterVersion, "adapterVersion", 0);
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_Values.Look(ref pawnLoadId, "pawnLoadId");
            Scribe_References.Look(ref sourceThing, "sourceThing");
            Scribe_Values.Look(ref sourceThingLoadId, "sourceThingLoadId");
            Scribe_References.Look(ref fetchMap, "fetchMap");
            Scribe_Values.Look(ref fetchCell, "fetchCell", IntVec3.Invalid);
            Scribe_Values.Look(ref requestedCount, "requestedCount", 0);
            Scribe_References.Look(ref cargo, "cargo");
            Scribe_Values.Look(ref cargoLoadId, "cargoLoadId");
            Scribe_Values.Look(ref observedCount, "observedCount", 0);
            Scribe_References.Look(ref storeMap, "storeMap");
            Scribe_Values.Look(ref candidateStoreCell, "candidateStoreCell", IntVec3.Invalid);
            Scribe_References.Look(ref finalTarget, "finalTarget");
            Scribe_Values.Look(ref finalTargetLoadId, "finalTargetLoadId");
            Scribe_Values.Look(ref connectionId, "connectionId");
            Scribe_Values.Look(ref openingId, "openingId");
            Scribe_Values.Look(ref topologyRevision, "topologyRevision", 0L);
            Scribe_Values.Look(ref phase, "phase", ConnectedWorkPhase.Planned);
            Scribe_Values.Look(ref failureKey, "failureKey");
            Scribe_Values.Look(ref openedTick, "openedTick", 0);
            Scribe_Values.Look(ref leaseExpiryTick, "leaseExpiryTick", 0);
            Scribe_Values.Look(ref crossAttempts, "crossAttempts", 0);
        }
    }

    /// <summary>
    /// What this worker's allowed area was, the last time it was actually standing
    /// on this map.
    ///
    /// This exists because Core stores allowed areas in a private dictionary keyed
    /// by Map and exposes only "in the pawn's current map" accessors. There is no
    /// public way to ask what a pawn's area is on a map it is not standing on, and
    /// spoofing <c>pawn.Map</c> to find out is never acceptable. So instead of
    /// claiming remote area compliance we cannot check, or giving up on it, we
    /// simply write down what we saw while we were legitimately able to see it.
    ///
    /// A null area means unrestricted, which is also Core's own answer for a map the
    /// player has never set an area on — so an unobserved map is treated as
    /// unrestricted for exactly the same reason Core would.
    /// </summary>
    public sealed class ConnectedAreaObservation : IExposable
    {
        private string pawnLoadId;
        private Map map;
        private Area area;
        private int observedTick;

        public string PawnLoadId { get { return pawnLoadId; } }
        public Map Map { get { return map; } }
        public Area Area { get { return area; } }
        public int ObservedTick { get { return observedTick; } }

        public ConnectedAreaObservation() { }

        internal ConnectedAreaObservation(Pawn pawn, Map map, Area area, int tick)
        {
            pawnLoadId = pawn.GetUniqueLoadID();
            this.map = map;
            this.area = area;
            observedTick = tick;
        }

        internal void Update(Area observed, int tick)
        {
            area = observed;
            observedTick = tick;
        }

        /// <summary>
        /// Whether this observation still permits a cell. A removed area resolves to
        /// null on load, which correctly reads as unrestricted rather than as a wall.
        /// </summary>
        public bool Allows(IntVec3 cell)
        {
            if (area == null) { return true; }
            if (area.Map != map) { return true; }
            return !cell.IsValid || area[cell];
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref pawnLoadId, "pawnLoadId");
            Scribe_References.Look(ref map, "map");
            Scribe_References.Look(ref area, "area");
            Scribe_Values.Look(ref observedTick, "observedTick", 0);
        }
    }
}
