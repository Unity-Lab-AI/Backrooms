# -*- coding: utf-8 -*-
"""A portal does not extend into the real world: building beside a gate must not brick it."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ the endpoint can be repaired
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Portals', 'PortalConnectionRecord.cs')
sub(p, u"""        internal bool Matches(Thing thing, IntVec3 approach)
        { return anchor == thing && map == thing.Map && anchorCell == thing.Position && approachCell == approach; }""",
u"""        internal bool Matches(Thing thing, IntVec3 approach)
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
        }""")
print('PortalEndpointRecord gained TryRepairApproach')

# ------------------------------------------------------------------ availability repairs first
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Portals', 'RimroomsPortalNetwork.cs')
sub(p, u"""            // Natural connections deliberately have no timeout, gate operator,
            // mission completion, battery or close command dependency.
            return edge.First.ApproachCell.Standable(edge.First.Map) &&
                edge.Second.ApproachCell.Standable(edge.Second.Map)
                ? PortalNetworkResult.Success : PortalNetworkResult.Obstructed;""",
u"""            // Natural connections deliberately have no timeout, gate operator,
            // mission completion, battery or close command dependency.
            //
            // **A portal does not extend into the real world.** Owner direction, 2026-09-29:
            // *"in the real world you can mine and build and explore directly behind the gates
            // with out actually effecting the gate"*. The approach cell was snapshotted at
            // registration, so a wall built on it used to report Obstructed forever even with
            // three walkable cells beside the same door. It is now re-derived on demand.
            //
            // **Not repaired while a crossing is in flight.** A receipt records the approach cell
            // it began with and refuses to continue if it changed, which is the guard that stops
            // a transfer losing a pawn (invariant 55). Moving the cell underneath a live transfer
            // would trip that guard and abort a legitimate crossing, so a busy edge waits.
            if (!CrossingInFlight(edge))
            {
                edge.First.TryRepairApproach();
                edge.Second.TryRepairApproach();
            }
            return edge.First.ApproachCell.Standable(edge.First.Map) &&
                edge.Second.ApproachCell.Standable(edge.Second.Map)
                ? PortalNetworkResult.Success : PortalNetworkResult.Obstructed;""")

sub(p, u"""        public PortalRouteSearch BeginRouteSearch(Map source, Map destination)""",
u"""        /// <summary>
        /// Whether any crossing receipt still refers to this connection.
        ///
        /// Asked before repairing an approach cell, because a receipt's stored approach is the
        /// equality guard that protects a pawn mid-transfer. Cheap: the receipt list is bounded
        /// and is almost always empty.
        /// </summary>
        private static bool CrossingInFlight(PortalConnectionRecord edge)
        {
            if (edge == null || Current.Game == null) { return false; }
            PortalCrossingService crossings = Current.Game.GetComponent<PortalCrossingService>();
            if (crossings == null) { return false; }
            IReadOnlyList<PortalCrossingReceipt> receipts = crossings.Receipts;
            for (int index = 0; index < receipts.Count; index++)
            {
                PortalCrossingReceipt receipt = receipts[index];
                if (receipt != null && receipt.ConnectionId == edge.Id) { return true; }
            }
            return false;
        }

        public PortalRouteSearch BeginRouteSearch(Map source, Map destination)""")
print('Availability now repairs the approach when no crossing is in flight')
