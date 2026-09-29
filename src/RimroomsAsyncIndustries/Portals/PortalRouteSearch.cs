using System;
using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    public enum PortalRouteSearchStatus { Pending, Complete, Unreachable, Invalidated, InvalidState }

    /// <summary>
    /// A transient, non-owning topology query. Keep the same query between calls.
    /// Each operation examines one candidate or advances one bounded bookkeeping
    /// step; this is not a measurement of native geometry or wall-clock cost.
    /// </summary>
    public sealed class PortalRouteSearch
    {
        private enum Phase { Capture, Search, Reconstruct, CopyRoute, Validate, Finished }
        private sealed class Observation
        {
            internal PortalConnectionRecord Connection;
            internal PortalNetworkResult Availability;
        }

        public const int MaximumOperationsPerAdvance = 1024;
        private static readonly IReadOnlyList<PortalRouteStep> EmptyRoute =
            new List<PortalRouteStep>().AsReadOnly();
        private readonly RimroomsPortalNetwork network;
        private List<Observation> observations = new List<Observation>();
        private Dictionary<Map, List<PortalRouteStep>> adjacency =
            new Dictionary<Map, List<PortalRouteStep>>();
        private Queue<Map> queue = new Queue<Map>();
        private HashSet<Map> seen = new HashSet<Map>();
        private Dictionary<Map, PortalRouteStep> previous = new Dictionary<Map, PortalRouteStep>();
        private List<PortalRouteStep> backwards = new List<PortalRouteStep>();
        private List<PortalRouteStep> candidateRoute = new List<PortalRouteStep>();
        private IReadOnlyList<PortalRouteStep> publishedRoute = EmptyRoute;
        private Phase phase;
        private Map currentMap;
        private Map reconstructMap;
        private int captureIndex;
        private int adjacentIndex;
        private int copyIndex;
        private int validationIndex;
        private bool found;

        public Map Source { get; private set; }
        public Map Destination { get; private set; }
        public PortalRouteSearchStatus Status { get; private set; }
        public long TopologyRevision { get; private set; }
        public int LastAdvanceOperations { get; private set; }
        public long TotalOperations { get; private set; }
        public int VisitedMapCount { get { return seen.Count; } }
        public int CapturedConnectionCount { get { return observations.Count; } }
        public IReadOnlyList<PortalRouteStep> Route
        { get { return Status == PortalRouteSearchStatus.Complete ? publishedRoute : EmptyRoute; } }

        internal PortalRouteSearch(RimroomsPortalNetwork network, Map source, Map destination)
        {
            this.network = network;
            Source = source;
            Destination = destination;
            Reset();
        }

        /// <summary>
        /// Continue the same query. Complete and Unreachable are observations,
        /// not permanent caches: calling again rechecks captured availability.
        /// Invalidated has already reset the cursor; the next call makes progress.
        /// A search cursor owns no game objects and is intentionally not saved.
        /// </summary>
        public PortalRouteSearchStatus Advance(int maxOperations)
        { return Advance(maxOperations, int.MaxValue); }

        // The map limit is only for the legacy single-pass FindRoute wrapper.
        // Persistent callers use the public method so a fixed total-map cap
        // cannot permanently prevent their cursor from progressing.
        internal PortalRouteSearchStatus Advance(int maxOperations, int maxVisitedMaps)
        {
            LastAdvanceOperations = 0;
            if (maxOperations < 1 || maxVisitedMaps < 1 || !network.ValidSearchMaps(Source, Destination))
            {
                Status = PortalRouteSearchStatus.InvalidState;
                publishedRoute = EmptyRoute;
                return Status;
            }
            if (TopologyRevision != network.TopologyRevision || Status == PortalRouteSearchStatus.InvalidState)
            { return Invalidate(); }
            if (Status == PortalRouteSearchStatus.Complete || Status == PortalRouteSearchStatus.Unreachable)
            {
                validationIndex = 0;
                phase = Phase.Validate;
            }
            Status = PortalRouteSearchStatus.Pending;
            int limit = Math.Min(maxOperations, MaximumOperationsPerAdvance);
            while (LastAdvanceOperations < limit)
            {
                LastAdvanceOperations++;
                TotalOperations++;
                if (!Step(maxVisitedMaps)) { break; }
                if (Status != PortalRouteSearchStatus.Pending) { break; }
            }
            return Status;
        }

        /// <summary>
        /// Recheck the actual selected edge immediately before a crossing.
        /// This checks topology only; pawn pathing, locks, areas and custody
        /// remain mandatory checks in the crossing/job implementation.
        /// </summary>
        public PortalNetworkResult ValidateStepForTraversal(int stepIndex)
        {
            if (Status != PortalRouteSearchStatus.Complete || stepIndex < 0 || stepIndex >= publishedRoute.Count)
            { return PortalNetworkResult.InvalidState; }
            if (TopologyRevision != network.TopologyRevision || !network.ValidSearchMaps(Source, Destination))
            { Invalidate(); return PortalNetworkResult.InvalidState; }
            PortalNetworkResult result = network.ValidateRouteStep(publishedRoute[stepIndex]);
            if (result != PortalNetworkResult.Success) { Invalidate(); }
            return result;
        }

        private bool Step(int maxVisitedMaps)
        {
            switch (phase)
            {
                case Phase.Capture:
                    if (Source == Destination)
                    {
                        found = true;
                        phase = Phase.Validate;
                        return true;
                    }
                    if (captureIndex < network.SearchConnectionCount)
                    {
                        PortalConnectionRecord edge = network.SearchConnectionAt(captureIndex++);
                        PortalNetworkResult availability = network.Availability(edge);
                        observations.Add(new Observation { Connection = edge, Availability = availability });
                        if (availability == PortalNetworkResult.Success)
                        {
                            AddAdjacent(new PortalRouteStep(edge, true));
                            AddAdjacent(new PortalRouteStep(edge, false));
                        }
                        return true;
                    }
                    queue.Enqueue(Source);
                    seen.Add(Source);
                    phase = Phase.Search;
                    return true;

                case Phase.Search:
                    if (currentMap == null)
                    {
                        if (queue.Count == 0) { phase = Phase.Validate; return true; }
                        currentMap = queue.Dequeue();
                        adjacentIndex = 0;
                        return true;
                    }
                    List<PortalRouteStep> neighbours;
                    if (!adjacency.TryGetValue(currentMap, out neighbours) || adjacentIndex >= neighbours.Count)
                    { currentMap = null; return true; }
                    PortalRouteStep step = neighbours[adjacentIndex];
                    Map next = step.Destination.Map;
                    if (seen.Contains(next)) { adjacentIndex++; return true; }
                    if (seen.Count >= maxVisitedMaps) { return false; }
                    adjacentIndex++;
                    seen.Add(next);
                    previous.Add(next, step);
                    if (next == Destination)
                    {
                        found = true;
                        reconstructMap = Destination;
                        phase = Phase.Reconstruct;
                    }
                    else { queue.Enqueue(next); }
                    return true;

                case Phase.Reconstruct:
                    if (reconstructMap == Source)
                    { copyIndex = backwards.Count - 1; phase = Phase.CopyRoute; return true; }
                    PortalRouteStep previousStep = previous[reconstructMap];
                    backwards.Add(previousStep);
                    reconstructMap = previousStep.Source.Map;
                    return true;

                case Phase.CopyRoute:
                    if (copyIndex < 0) { phase = Phase.Validate; return true; }
                    candidateRoute.Add(backwards[copyIndex--]);
                    return true;

                case Phase.Validate:
                    if (validationIndex < observations.Count)
                    {
                        Observation observed = observations[validationIndex++];
                        if (network.Availability(observed.Connection) != observed.Availability)
                        { Invalidate(); return false; }
                        return true;
                    }
                    // Native callers are on the game thread. Endpoint state can
                    // still change after this result, hence traversal rechecks.
                    if (TopologyRevision != network.TopologyRevision)
                    { Invalidate(); return false; }
                    publishedRoute = found ? candidateRoute.AsReadOnly() : EmptyRoute;
                    Status = found ? PortalRouteSearchStatus.Complete : PortalRouteSearchStatus.Unreachable;
                    phase = Phase.Finished;
                    return false;

                default:
                    return false;
            }
        }

        private void AddAdjacent(PortalRouteStep step)
        {
            List<PortalRouteStep> values;
            if (!adjacency.TryGetValue(step.Source.Map, out values))
            { values = new List<PortalRouteStep>(); adjacency.Add(step.Source.Map, values); }
            values.Add(step);
        }

        private PortalRouteSearchStatus Invalidate()
        {
            Reset();
            Status = PortalRouteSearchStatus.Invalidated;
            return Status;
        }

        private void Reset()
        {
            TopologyRevision = network.TopologyRevision;
            // Swap buffers instead of walking the old graph to clear it. A route
            // already returned to a caller also keeps its original immutable
            // list; invalidating this query must not mutate that caller's list.
            observations = new List<Observation>();
            adjacency = new Dictionary<Map, List<PortalRouteStep>>();
            queue = new Queue<Map>();
            seen = new HashSet<Map>();
            previous = new Dictionary<Map, PortalRouteStep>();
            backwards = new List<PortalRouteStep>();
            candidateRoute = new List<PortalRouteStep>();
            publishedRoute = EmptyRoute;
            currentMap = null; reconstructMap = null;
            captureIndex = 0; adjacentIndex = 0; copyIndex = 0; validationIndex = 0;
            found = false;
            phase = Phase.Capture;
            Status = PortalRouteSearchStatus.Pending;
        }
    }
}
