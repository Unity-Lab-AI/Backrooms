using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Generation;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    public enum PortalNetworkResult
    {
        Success, Existing, InvalidState, InvalidEndpoint, IdentityConflict,
        UnknownCoordinate, WrongBranch, Closed, Obstructed, NoRoute, SearchBudgetExceeded
    }

    /// <summary>
    /// Persistent local-branch topology. This component never generates maps,
    /// moves people, schedules jobs or treats graph reachability as pawn pathing.
    /// </summary>
    public sealed class RimroomsPortalNetwork : GameComponent
    {
        private const int CurrentSchema = 1;
        private int schema = CurrentSchema;
        private List<PortalConnectionRecord> connections = new List<PortalConnectionRecord>();
        private readonly HashSet<PortalConnectionRecord> connectionIdentity = new HashSet<PortalConnectionRecord>();
        private readonly Dictionary<string, PortalConnectionRecord> connectionById =
            new Dictionary<string, PortalConnectionRecord>(StringComparer.Ordinal);
        private bool malformedState;
        // Transient cache epoch. It is not a saved connection identity and does
        // not require a schema change; search cursors are recreated after load.
        private long topologyRevision = 1;
        public RimroomsPortalNetwork(Game game) { }
        public IReadOnlyList<PortalConnectionRecord> Connections { get { return connections.AsReadOnly(); } }
        public bool HasStateFault { get { return schema != CurrentSchema || malformedState; } }
        public long TopologyRevision { get { return topologyRevision; } }
        internal int SearchConnectionCount { get { return connections.Count; } }
        internal PortalConnectionRecord SearchConnectionAt(int index) { return connections[index]; }
        private RimroomsCampaignComponent Campaign { get { return Current.Game.GetComponent<RimroomsCampaignComponent>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schema, "rr_portalNetworkSchema", CurrentSchema, forceSave: true);
            Scribe_Collections.Look(ref connections, "rr_portalConnections", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (connections == null) { connections = new List<PortalConnectionRecord>(); }
                // Preserve malformed evidence. Never silently remove an edge or
                // reconnect it to a similarly named replacement door/map.
                var ids = new HashSet<string>(StringComparer.Ordinal);
                malformedState = connections.Any(edge => edge == null || string.IsNullOrWhiteSpace(edge.Id) ||
                    !ids.Add(edge.Id) || string.IsNullOrWhiteSpace(edge.BranchId) ||
                    edge.First == null || edge.Second == null ||
                    (edge.Kind != PortalConnectionKind.Natural && edge.Kind != PortalConnectionKind.Laboratory));
                connectionIdentity.Clear();
                connectionById.Clear();
                if (!malformedState)
                {
                    foreach (PortalConnectionRecord edge in connections)
                    { connectionIdentity.Add(edge); connectionById.Add(edge.Id, edge); }
                }
                AdvanceTopologyRevision();
            }
        }

        public PortalNetworkResult Register(string id, string coordinateId, PortalConnectionKind kind,
            Thing firstAnchor, IntVec3 firstApproach, Thing secondAnchor, IntVec3 secondApproach)
        {
            RimroomsCampaignComponent campaign = Campaign;
            if (HasStateFault || campaign == null || !campaign.CanOperate || string.IsNullOrWhiteSpace(id) ||
                (kind != PortalConnectionKind.Natural && kind != PortalConnectionKind.Laboratory))
            { return PortalNetworkResult.InvalidState; }
            if (!ValidDoor(firstAnchor, firstApproach) || !ValidDoor(secondAnchor, secondApproach) ||
                firstAnchor.Map == secondAnchor.Map) { return PortalNetworkResult.InvalidEndpoint; }
            List<CoordinateRecord> candidates = campaign.Coordinates.Where(record => record.id == coordinateId).ToList();
            CoordinateRecord coordinate = candidates.Count == 1 ? candidates[0] : null;
            RimroomsDestinationMapParent site = secondAnchor.Map.Parent as RimroomsDestinationMapParent;
            if (coordinate == null || coordinate.site != site || site == null || !site.LayoutReady ||
                site.CoordinateId != coordinateId) { return PortalNetworkResult.UnknownCoordinate; }
            if (!OwnsMap(campaign, firstAnchor.Map)) { return PortalNetworkResult.WrongBranch; }
            CompRimroomsGate gate = firstAnchor.TryGetComp<CompRimroomsGate>();
            if (kind == PortalConnectionKind.Laboratory &&
                (gate == null || !gate.IsDesignated || firstAnchor.Faction != Faction.OfPlayer ||
                 gate.GateEntryCell != firstApproach)) { return PortalNetworkResult.InvalidEndpoint; }
            PortalConnectionRecord existing = Find(id);
            if (existing != null)
            {
                return existing.BranchId == campaign.BranchId && existing.CoordinateId == coordinateId &&
                    existing.Kind == kind && existing.First.Matches(firstAnchor, firstApproach) &&
                    existing.Second.Matches(secondAnchor, secondApproach)
                    ? PortalNetworkResult.Existing : PortalNetworkResult.IdentityConflict;
            }
            // A laboratory may remember several addresses on the same machine;
            // only its current opening identity can activate one of those edges.
            // Permanent natural thresholds cannot be reassigned to another site.
            if (connections.Any(edge =>
                (edge.First.Anchor == firstAnchor &&
                 (kind != PortalConnectionKind.Laboratory || edge.Kind != PortalConnectionKind.Laboratory)) ||
                edge.Second.Anchor == firstAnchor ||
                edge.First.Anchor == secondAnchor || edge.Second.Anchor == secondAnchor))
            { return PortalNetworkResult.IdentityConflict; }
            var created = new PortalConnectionRecord(id, campaign.BranchId, coordinateId, kind,
                new PortalEndpointRecord(firstAnchor, firstApproach), new PortalEndpointRecord(secondAnchor, secondApproach));
            connections.Add(created);
            connectionIdentity.Add(created);
            connectionById.Add(id, created);
            AdvanceTopologyRevision();
            return PortalNetworkResult.Success;
        }

        // Observes an already opened physical machine. This is not payment or
        // permission to open; the machine adapter owns those actions separately.
        public PortalNetworkResult ObserveLaboratoryOpening(string connectionId, string openingId)
        {
            PortalConnectionRecord edge = Find(connectionId);
            if (edge == null || edge.Kind != PortalConnectionKind.Laboratory || !Owned(edge) ||
                string.IsNullOrWhiteSpace(openingId)) { return PortalNetworkResult.InvalidState; }
            if (!EndpointPresent(edge.First) || !EndpointPresent(edge.Second))
            { return PortalNetworkResult.InvalidEndpoint; }
            CompRimroomsGate gate = edge.First.Anchor.TryGetComp<CompRimroomsGate>();
            if (gate == null || gate.HasPortalOwnerFault || !gate.IsOpening || gate.PortalOpeningId != openingId ||
                gate.PortalConnectionId != connectionId || gate.ActiveExpeditionId != null || gate.IsEmergency)
            { return PortalNetworkResult.Closed; }
            if (connections.Any(other => other != edge && other.First.Anchor == edge.First.Anchor &&
                other.OpeningId == openingId)) { return PortalNetworkResult.IdentityConflict; }
            if (edge.OpeningId != openingId)
            {
                edge.ObserveOpening(openingId);
                AdvanceTopologyRevision();
            }
            return PortalNetworkResult.Success;
        }

        public PortalConnectionRecord Find(string id)
        {
            PortalConnectionRecord result;
            return !HasStateFault && id != null && connectionById.TryGetValue(id, out result) ? result : null;
        }

        public PortalNetworkResult Availability(PortalConnectionRecord edge)
        {
            if (!Owned(edge)) { return PortalNetworkResult.InvalidState; }
            if (!EndpointPresent(edge.First) || !EndpointPresent(edge.Second))
            { return PortalNetworkResult.InvalidEndpoint; }
            RimroomsCampaignComponent campaign = Campaign;
            var site = edge.Second.Map.Parent as RimroomsDestinationMapParent;
            if (!OwnsMap(campaign, edge.First.Map) || site == null || !site.LayoutReady ||
                site.CoordinateId != edge.CoordinateId ||
                !campaign.Coordinates.Any(record => record.id == edge.CoordinateId && record.site == site))
            { return PortalNetworkResult.WrongBranch; }
            if (edge.Kind == PortalConnectionKind.Laboratory)
            {
                CompRimroomsGate gate = edge.First.Anchor.TryGetComp<CompRimroomsGate>();
                if (gate == null || gate.HasPortalOwnerFault || !gate.IsDesignated ||
                    string.IsNullOrWhiteSpace(edge.OpeningId) || !gate.HasUsablePortalWindow(edge.Id, edge.OpeningId) ||
                    gate.GateEntryCell != edge.First.ApproachCell) { return PortalNetworkResult.Closed; }
            }
            // Natural connections deliberately have no timeout, gate operator,
            // mission completion, battery or close command dependency.
            return edge.First.ApproachCell.Standable(edge.First.Map) &&
                edge.Second.ApproachCell.Standable(edge.Second.Map)
                ? PortalNetworkResult.Success : PortalNetworkResult.Obstructed;
        }

        public PortalRouteSearch BeginRouteSearch(Map source, Map destination)
        { return new PortalRouteSearch(this, source, destination); }

        /// <summary>
        /// Compatibility single-pass query. A budget result is not NoRoute;
        /// automatic callers must retain BeginRouteSearch's cursor and Advance it.
        /// The old connection budget now bounds candidate/bookkeeping operations,
        /// including capture and final validation, capped at 1024 per call.
        /// </summary>
        public PortalNetworkResult FindRoute(Map source, Map destination, int maxVisitedMaps,
            int maxExaminedConnections, out IReadOnlyList<PortalRouteStep> route)
        {
            PortalRouteSearch search = BeginRouteSearch(source, destination);
            PortalRouteSearchStatus status = search.Advance(maxExaminedConnections, maxVisitedMaps);
            route = search.Route;
            if (status == PortalRouteSearchStatus.Complete) { return PortalNetworkResult.Success; }
            if (status == PortalRouteSearchStatus.Unreachable) { return PortalNetworkResult.NoRoute; }
            return status == PortalRouteSearchStatus.InvalidState ? PortalNetworkResult.InvalidState
                : PortalNetworkResult.SearchBudgetExceeded;
        }

        public PortalNetworkResult ValidateRouteStep(PortalRouteStep step)
        {
            if (step == null || !Owned(step.Connection) ||
                !((step.Source == step.Connection.First && step.Destination == step.Connection.Second) ||
                  (step.Source == step.Connection.Second && step.Destination == step.Connection.First)))
            { return PortalNetworkResult.InvalidState; }
            return Availability(step.Connection);
        }

        internal bool ValidSearchMaps(Map source, Map destination)
        {
            RimroomsCampaignComponent campaign = Campaign;
            return !HasStateFault && campaign != null && campaign.CanOperate && source != null && destination != null &&
                Verse.Find.Maps.Contains(source) && Verse.Find.Maps.Contains(destination) &&
                OwnsMap(campaign, source) && OwnsMap(campaign, destination);
        }

        private void AdvanceTopologyRevision()
        { topologyRevision = topologyRevision == long.MaxValue ? 1 : topologyRevision + 1; }

        private bool Owned(PortalConnectionRecord edge)
        {
            RimroomsCampaignComponent campaign = Campaign;
            return !HasStateFault && campaign != null && campaign.CanOperate && edge != null &&
                connectionIdentity.Contains(edge) && edge.BranchId == campaign.BranchId &&
                edge.First != null && edge.Second != null;
        }
        private static bool OwnsMap(RimroomsCampaignComponent campaign, Map map)
        {
            if (map == campaign.Headquarters) { return true; }
            var site = map.Parent as RimroomsDestinationMapParent;
            return site != null && campaign.Coordinates.Any(record => record.site == site && record.id == site.CoordinateId);
        }
        private static bool ValidDoor(Thing anchor, IntVec3 approach)
        {
            return anchor is Building_Door && anchor.Spawned && !anchor.Destroyed &&
                Verse.Find.Maps.Contains(anchor.Map) && approach.IsValid && approach.InBounds(anchor.Map) &&
                approach.AdjacentToCardinal(anchor.Position);
        }
        private static bool EndpointPresent(PortalEndpointRecord endpoint)
        {
            return endpoint != null && endpoint.Map != null && Verse.Find.Maps.Contains(endpoint.Map) &&
                ValidDoor(endpoint.Anchor, endpoint.ApproachCell) && endpoint.Anchor.Map == endpoint.Map &&
                endpoint.Anchor.Position == endpoint.AnchorCell;
        }
    }
}
