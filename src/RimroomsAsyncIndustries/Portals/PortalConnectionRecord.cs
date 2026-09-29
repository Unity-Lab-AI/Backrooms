using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    // Appended, never renumbered: saved values must keep their meaning.
    //
    // Emergence is a way *out*. Its First endpoint is a door on an ordinary branch-owned map
    // that the player explicitly marked, and its Second is a doorway inside a Backrooms
    // coordinate. Recording it anchor-first is deliberate: it means every ownership and site
    // check the network already performs on First and Second reads correctly for this kind
    // with no change at all.
    public enum PortalConnectionKind { Laboratory = 0, Natural = 1, Emergence = 2 }

    // Map references are saved load IDs, not volatile Map.Index values. Endpoint
    // cells are snapshots: moving a door cannot silently redirect a saved route.
    public sealed class PortalEndpointRecord : IExposable
    {
        private Map map;
        private Thing anchor;
        private IntVec3 anchorCell = IntVec3.Invalid;
        private IntVec3 approachCell = IntVec3.Invalid;
        public Map Map { get { return map; } }
        public Thing Anchor { get { return anchor; } }
        public IntVec3 AnchorCell { get { return anchorCell; } }
        public IntVec3 ApproachCell { get { return approachCell; } }

        public PortalEndpointRecord() { }
        internal PortalEndpointRecord(Thing anchor, IntVec3 approach)
        { this.anchor = anchor; map = anchor.Map; anchorCell = anchor.Position; approachCell = approach; }

        internal bool Matches(Thing thing, IntVec3 approach)
        { return anchor == thing && map == thing.Map && anchorCell == thing.Position && approachCell == approach; }

        public void ExposeData()
        {
            Scribe_References.Look(ref map, "map");
            Scribe_References.Look(ref anchor, "anchor");
            Scribe_Values.Look(ref anchorCell, "anchorCell", IntVec3.Invalid);
            Scribe_Values.Look(ref approachCell, "approachCell", IntVec3.Invalid);
        }
    }

    public sealed class PortalConnectionRecord : IExposable
    {
        private string id;
        private string branchId;
        private string coordinateId;
        private PortalConnectionKind kind;
        private PortalEndpointRecord first;
        private PortalEndpointRecord second;
        private string openingId;
        public string Id { get { return id; } }
        public string BranchId { get { return branchId; } }
        public string CoordinateId { get { return coordinateId; } }
        public PortalConnectionKind Kind { get { return kind; } }
        public PortalEndpointRecord First { get { return first; } }
        public PortalEndpointRecord Second { get { return second; } }
        public string OpeningId { get { return openingId; } }

        public PortalConnectionRecord() { }
        internal PortalConnectionRecord(string id, string branchId, string coordinateId,
            PortalConnectionKind kind, PortalEndpointRecord first, PortalEndpointRecord second)
        {
            this.id = id; this.branchId = branchId; this.coordinateId = coordinateId;
            this.kind = kind; this.first = first; this.second = second;
        }
        internal void ObserveOpening(string value) { openingId = value; }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "id");
            Scribe_Values.Look(ref branchId, "branchId");
            Scribe_Values.Look(ref coordinateId, "coordinateId");
            Scribe_Values.Look(ref kind, "kind");
            Scribe_Deep.Look(ref first, "first");
            Scribe_Deep.Look(ref second, "second");
            Scribe_Values.Look(ref openingId, "openingId");
        }
    }

    public sealed class PortalRouteStep
    {
        public PortalConnectionRecord Connection { get; private set; }
        public PortalEndpointRecord Source { get; private set; }
        public PortalEndpointRecord Destination { get; private set; }
        internal PortalRouteStep(PortalConnectionRecord connection, bool forward)
        {
            Connection = connection;
            Source = forward ? connection.First : connection.Second;
            Destination = forward ? connection.Second : connection.First;
        }
    }
}
