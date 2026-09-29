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

        /// <summary>
        /// Re-derive the approach cell when the saved one has been built over.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"in the real world maps the portals dont
        /// extend into the real world environment so in the real world you can mine and build and
        /// explore directly behind the gates with out actually effecting the gate"*.
        ///
        /// The approach cell was snapshotted at registration and never revisited, so a wall built
        /// on it made `RimroomsPortalNetwork.Availability` return `Obstructed` **forever** — even
        /// with three other perfectly walkable cells beside the same door. **A portal is its own
        /// door cell and reserves nothing**, so walling one side of it must cost no more than
        /// walling one side of any other door.
        ///
        /// **The anchor cell is deliberately NOT refreshed.** That snapshot is what stops a moved
        /// door silently redirecting a saved route, and it is still exactly right. Only the cell a
        /// traveller stands on moves, because that is a fact about the local geometry rather than
        /// about the connection.
        ///
        /// Returns true when the endpoint has a usable approach afterwards. A door genuinely
        /// sealed on all four sides returns false, which is the honest answer: the player closed
        /// their own door in.
        /// </summary>
        internal bool TryRepairApproach()
        {
            if (anchor == null || !anchor.Spawned || anchor.Destroyed || map == null ||
                anchor.Map != map || anchor.Position != anchorCell)
            { return false; }
            if (approachCell.IsValid && approachCell.InBounds(map) && approachCell.Standable(map) &&
                approachCell.AdjacentToCardinal(anchorCell))
            { return true; }
            IntVec3 fresh = PortalAddressService.ApproachCellFor(anchor);
            if (!fresh.IsValid) { return false; }
            approachCell = fresh;
            return true;
        }

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
