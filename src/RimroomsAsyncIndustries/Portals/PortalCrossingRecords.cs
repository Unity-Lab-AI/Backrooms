using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    public enum PortalCrossingPhase
    {
        Prepared = 0,
        CargoSecured = 1,
        PawnDespawned = 2,
        Arrived = 3,
        Committed = 4,
        RolledBack = 5,
        NeedsRecovery = 6,
        RecoveredAtActualLocation = 7
    }

    public enum PortalCrossingStatus
    {
        Completed,
        Existing,
        Refused,
        RolledBack,
        NeedsRecovery,
        RecoveredAtActualLocation
    }

    /// <summary>
    /// One idempotent, physical pawn move through one saved graph edge. Pawn and
    /// cargo references are observations of their real objects, never templates.
    /// </summary>
    public sealed class PortalCrossingReceipt : IExposable
    {
        private string operationId;
        private long sequence;
        private string branchId;
        private string connectionId;
        private string coordinateId;
        private PortalConnectionKind connectionKind;
        private string openingId;
        private bool sourceIsFirst;
        private Map sourceMap;
        private Map destinationMap;
        private Thing sourceAnchor;
        private Thing destinationAnchor;
        private string sourceAnchorLoadId;
        private string destinationAnchorLoadId;
        private IntVec3 sourceAnchorCell = IntVec3.Invalid;
        private IntVec3 destinationAnchorCell = IntVec3.Invalid;
        private IntVec3 sourceApproachCell = IntVec3.Invalid;
        private IntVec3 destinationApproachCell = IntVec3.Invalid;
        private IntVec3 originalPawnCell = IntVec3.Invalid;
        private Pawn pawn;
        private string pawnLoadId;
        private Thing carriedThing;
        private string carriedThingLoadId;
        private int carriedStackCount;
        private PortalCrossingPhase phase;
        private int startedTick;
        private string failureKey;

        public string OperationId { get { return operationId; } }
        public long Sequence { get { return sequence; } }
        public string BranchId { get { return branchId; } }
        public string ConnectionId { get { return connectionId; } }
        public string CoordinateId { get { return coordinateId; } }
        public PortalConnectionKind ConnectionKind { get { return connectionKind; } }
        public string OpeningId { get { return openingId; } }
        public bool SourceIsFirst { get { return sourceIsFirst; } }
        public Map SourceMap { get { return sourceMap; } }
        public Map DestinationMap { get { return destinationMap; } }
        public Thing SourceAnchor { get { return sourceAnchor; } }
        public Thing DestinationAnchor { get { return destinationAnchor; } }
        public string SourceAnchorLoadId { get { return sourceAnchorLoadId; } }
        public string DestinationAnchorLoadId { get { return destinationAnchorLoadId; } }
        public IntVec3 SourceAnchorCell { get { return sourceAnchorCell; } }
        public IntVec3 DestinationAnchorCell { get { return destinationAnchorCell; } }
        public IntVec3 SourceApproachCell { get { return sourceApproachCell; } }
        public IntVec3 DestinationApproachCell { get { return destinationApproachCell; } }
        public IntVec3 OriginalPawnCell { get { return originalPawnCell; } }
        public Pawn Pawn { get { return pawn; } }
        public string PawnLoadId { get { return pawnLoadId; } }
        public Thing CarriedThing { get { return carriedThing; } }
        public string CarriedThingLoadId { get { return carriedThingLoadId; } }
        public int CarriedStackCount { get { return carriedStackCount; } }
        public PortalCrossingPhase Phase { get { return phase; } }
        public int StartedTick { get { return startedTick; } }
        public string FailureKey { get { return failureKey; } }
        public bool IsTerminal
        {
            get
            {
                return phase == PortalCrossingPhase.Committed || phase == PortalCrossingPhase.RolledBack ||
                    phase == PortalCrossingPhase.RecoveredAtActualLocation;
            }
        }

        public PortalCrossingReceipt() { }

        internal PortalCrossingReceipt(string operationId, long sequence, string branchId,
            PortalRouteStep step, Pawn pawn, string coordinateId, int startedTick)
        {
            this.operationId = operationId;
            this.sequence = sequence;
            this.branchId = branchId;
            connectionId = step.Connection.Id;
            this.coordinateId = coordinateId;
            connectionKind = step.Connection.Kind;
            openingId = step.Connection.OpeningId;
            sourceIsFirst = step.Source == step.Connection.First;
            sourceMap = step.Source.Map;
            destinationMap = step.Destination.Map;
            sourceAnchor = step.Source.Anchor;
            destinationAnchor = step.Destination.Anchor;
            sourceAnchorLoadId = sourceAnchor.GetUniqueLoadID();
            destinationAnchorLoadId = destinationAnchor.GetUniqueLoadID();
            sourceAnchorCell = step.Source.AnchorCell;
            destinationAnchorCell = step.Destination.AnchorCell;
            sourceApproachCell = step.Source.ApproachCell;
            destinationApproachCell = step.Destination.ApproachCell;
            originalPawnCell = pawn.Position;
            this.pawn = pawn;
            pawnLoadId = pawn.GetUniqueLoadID();
            phase = PortalCrossingPhase.Prepared;
            this.startedTick = startedTick;
        }

        internal void RecordCarriedThing(Thing thing)
        {
            carriedThing = thing;
            carriedThingLoadId = thing == null ? null : thing.GetUniqueLoadID();
            carriedStackCount = thing == null ? 0 : thing.stackCount;
        }

        internal void SetPhase(PortalCrossingPhase value, string failure = null)
        {
            phase = value;
            failureKey = failure;
        }

        internal bool MatchesRequest(string requestedOperationId, string requestedBranchId,
            Pawn requestedPawn, PortalRouteStep step)
        {
            if (step == null || step.Connection == null || step.Source == null || step.Destination == null)
            { return false; }
            return operationId == requestedOperationId && branchId == requestedBranchId && pawn == requestedPawn &&
                pawnLoadId == (requestedPawn == null ? null : requestedPawn.GetUniqueLoadID()) &&
                connectionId == step.Connection.Id && connectionKind == step.Connection.Kind &&
                sourceIsFirst == (step.Source == step.Connection.First) &&
                sourceMap == step.Source.Map && destinationMap == step.Destination.Map &&
                sourceAnchor == step.Source.Anchor && destinationAnchor == step.Destination.Anchor &&
                sourceAnchorLoadId == (step.Source.Anchor == null ? null : step.Source.Anchor.GetUniqueLoadID()) &&
                destinationAnchorLoadId == (step.Destination.Anchor == null ? null : step.Destination.Anchor.GetUniqueLoadID()) &&
                sourceAnchorCell == step.Source.AnchorCell && destinationAnchorCell == step.Destination.AnchorCell &&
                sourceApproachCell == step.Source.ApproachCell && destinationApproachCell == step.Destination.ApproachCell;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref operationId, "operationId");
            Scribe_Values.Look(ref sequence, "sequence");
            Scribe_Values.Look(ref branchId, "branchId");
            Scribe_Values.Look(ref connectionId, "connectionId");
            Scribe_Values.Look(ref coordinateId, "coordinateId");
            Scribe_Values.Look(ref connectionKind, "connectionKind");
            Scribe_Values.Look(ref openingId, "openingId");
            Scribe_Values.Look(ref sourceIsFirst, "sourceIsFirst");
            Scribe_References.Look(ref sourceMap, "sourceMap");
            Scribe_References.Look(ref destinationMap, "destinationMap");
            Scribe_References.Look(ref sourceAnchor, "sourceAnchor");
            Scribe_References.Look(ref destinationAnchor, "destinationAnchor");
            Scribe_Values.Look(ref sourceAnchorLoadId, "sourceAnchorLoadId");
            Scribe_Values.Look(ref destinationAnchorLoadId, "destinationAnchorLoadId");
            Scribe_Values.Look(ref sourceAnchorCell, "sourceAnchorCell", IntVec3.Invalid);
            Scribe_Values.Look(ref destinationAnchorCell, "destinationAnchorCell", IntVec3.Invalid);
            Scribe_Values.Look(ref sourceApproachCell, "sourceApproachCell", IntVec3.Invalid);
            Scribe_Values.Look(ref destinationApproachCell, "destinationApproachCell", IntVec3.Invalid);
            Scribe_Values.Look(ref originalPawnCell, "originalPawnCell", IntVec3.Invalid);
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_Values.Look(ref pawnLoadId, "pawnLoadId");
            Scribe_References.Look(ref carriedThing, "carriedThing");
            Scribe_Values.Look(ref carriedThingLoadId, "carriedThingLoadId");
            Scribe_Values.Look(ref carriedStackCount, "carriedStackCount");
            Scribe_Values.Look(ref phase, "phase");
            Scribe_Values.Look(ref startedTick, "startedTick");
            Scribe_Values.Look(ref failureKey, "failureKey");
        }
    }

    public sealed class PortalCrossingResult
    {
        public PortalCrossingStatus Status { get; private set; }
        public bool Success { get; private set; }
        public bool AlreadyApplied { get; private set; }
        public string FailureKey { get; private set; }
        public PortalCrossingReceipt Receipt { get; private set; }

        internal PortalCrossingResult(PortalCrossingStatus status, bool success, bool alreadyApplied,
            string failureKey, PortalCrossingReceipt receipt)
        {
            Status = status;
            Success = success;
            AlreadyApplied = alreadyApplied;
            FailureKey = failureKey;
            Receipt = receipt;
        }
    }
}
