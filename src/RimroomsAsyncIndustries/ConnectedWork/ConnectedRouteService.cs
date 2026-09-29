using System.Collections.Generic;
using RimroomsAsyncIndustries.Portals;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// Bounded topology routing for automatic work, built on the resumable search
    /// the portal network already owns. One cursor is retained per ordered map pair
    /// and advanced a little at a time, so a graph too large for a single pass still
    /// makes progress instead of restarting from its beginning forever.
    ///
    /// The single rule this class exists to enforce: a search that ran out of budget
    /// is **pending**, never "no route". Only an exhausted search that genuinely
    /// visited everything reachable answers unreachable. Callers act on pending by
    /// waiting, not by cancelling work.
    ///
    /// Cursors are transient. They own no game object, are never saved, and are
    /// rebuilt after load exactly as the search contract requires.
    /// </summary>
    public sealed class ConnectedRouteService
    {
        internal const int OperationsPerAdvance = 96;
        internal const int MaximumCursors = 32;

        private readonly Dictionary<long, PortalRouteSearch> cursors = new Dictionary<long, PortalRouteSearch>();

        public int CursorCount { get { return cursors.Count; } }

        /// <summary>
        /// The next hop a worker on <paramref name="from"/> should physically take
        /// toward <paramref name="to"/>, already revalidated for traversal. False
        /// with <paramref name="pending"/> true means "not yet known"; false with
        /// pending false means this map pair is genuinely not connected right now.
        /// </summary>
        public bool TryNextStep(Map from, Map to, out PortalRouteStep step, out bool pending)
        {
            step = null;
            pending = false;
            RimroomsPortalNetwork network = Network();
            if (network == null || network.HasStateFault || from == null || to == null || from == to ||
                !Find.Maps.Contains(from) || !Find.Maps.Contains(to))
            { return false; }

            // Bounded storage. Clearing restarts the affected queries; it never
            // converts a budget limit into an unreachable answer.
            if (cursors.Count >= MaximumCursors) { cursors.Clear(); }

            long key = PairKey(from, to);
            PortalRouteSearch search;
            if (!cursors.TryGetValue(key, out search) || search.Source != from || search.Destination != to)
            {
                search = network.BeginRouteSearch(from, to);
                cursors[key] = search;
            }

            PortalRouteSearchStatus status = search.Advance(OperationsPerAdvance);
            if (status != PortalRouteSearchStatus.Complete)
            {
                pending = status != PortalRouteSearchStatus.Unreachable;
                return false;
            }
            IReadOnlyList<PortalRouteStep> route = search.Route;
            if (route.Count == 0 || route[0] == null || route[0].Source == null ||
                route[0].Source.Map != from)
            { pending = true; return false; }
            if (search.ValidateStepForTraversal(0) != PortalNetworkResult.Success)
            { pending = true; return false; }
            step = route[0];
            return true;
        }

        /// <summary>Drops cursors whose maps have gone away. Cheap and bounded.</summary>
        public void DropStaleCursors()
        {
            if (cursors.Count == 0) { return; }
            List<long> stale = null;
            foreach (KeyValuePair<long, PortalRouteSearch> entry in cursors)
            {
                PortalRouteSearch search = entry.Value;
                if (search != null && search.Source != null && search.Destination != null &&
                    Find.Maps.Contains(search.Source) && Find.Maps.Contains(search.Destination))
                { continue; }
                stale = stale ?? new List<long>();
                stale.Add(entry.Key);
            }
            if (stale == null) { return; }
            foreach (long key in stale) { cursors.Remove(key); }
        }

        public void Clear() { cursors.Clear(); }

        private static long PairKey(Map from, Map to)
        {
            unchecked { return ((long)from.uniqueID << 32) | (uint)to.uniqueID; }
        }

        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }
    }
}
