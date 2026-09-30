using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Refuses to let anything be built that would stop a pawn standing on a gate's approach cell.
    ///
    /// Owner direction, 2026-09-29, at the fork this answers: <i>"option 2 but flooring is fine"</i>
    /// — the approach cell cannot be built on, and laying a floor there is not building on it.
    ///
    /// **Flooring is free without any code here.** A floor is a `TerrainDef`, terrain placement
    /// never consults a `PlaceWorker`, and this class only ever sees things. So the carve-out is
    /// structural rather than a special case somebody has to remember.
    ///
    /// **What counts as building on it is Core's own standability rule, not a list of ours.**
    /// `GenGrid.Standable` is walkable plus *every thing in the cell having
    /// `Traversability.Standable`*, so anything else — a wall, a barricade, a sandbag, a door,
    /// another mod's building this project has never heard of — is refused, and a power conduit or
    /// a floor-level fitting is not. A list of def names would have been wrong for the 294 mods
    /// this has to work with the moment one of them shipped a new wall.
    ///
    /// **This is a second layer, not the guarantee.** 0.12.3-dev already made the approach cell
    /// **re-derived at use time** rather than frozen at registration, which is what actually
    /// stops a connection breaking. This stops a player bricking their own gate by accident and
    /// tells them why at the moment they try. Coverage is therefore allowed to be imperfect: it
    /// reaches everything descending from Core's `BuildingBase`, which is nearly everything, and
    /// a building that descends from nothing still cannot break a connection.
    ///
    /// **Every uncertainty allows the placement.** This runs on every placement check in the
    /// game, for every building, in a profile with 294 other mods. A refusal this class gets
    /// wrong is a player unable to build; an allowance it gets wrong is a gate that re-derives
    /// its approach cell exactly as it already does. The asymmetry is not close, so anything
    /// unexpected — including a thrown exception — returns accepted.
    /// </summary>
    public sealed class PlaceWorker_GateApproach : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
            Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            try
            {
                return Check(checkingDef, loc, rot, map);
            }
            catch (Exception)
            {
                // Never let this be the reason somebody cannot build. See the class note.
                return AcceptanceReport.WasAccepted;
            }
        }

        private static AcceptanceReport Check(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map)
        {
            ThingDef definition = checkingDef as ThingDef;
            if (definition == null || map == null || !loc.IsValid) { return AcceptanceReport.WasAccepted; }

            // Core's rule: a cell is standable only if everything in it is Traversability.Standable.
            // Anything that satisfies that does not stop a pawn using the gate, so it is allowed.
            if (definition.passability == Traversability.Standable) { return AcceptanceReport.WasAccepted; }

            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null) { return AcceptanceReport.WasAccepted; }
            IReadOnlyList<PortalConnectionRecord> connections = network.Connections;
            if (connections == null || connections.Count == 0) { return AcceptanceReport.WasAccepted; }

            CellRect footprint = GenAdj.OccupiedRect(loc, rot, definition.Size);
            for (int index = 0; index < connections.Count; index++)
            {
                PortalConnectionRecord connection = connections[index];
                if (connection == null) { continue; }
                AcceptanceReport report = CheckEndpoint(connection.First, map, footprint);
                if (!report.Accepted) { return report; }
                report = CheckEndpoint(connection.Second, map, footprint);
                if (!report.Accepted) { return report; }
            }
            return AcceptanceReport.WasAccepted;
        }

        private static AcceptanceReport CheckEndpoint(PortalEndpointRecord endpoint, Map map, CellRect footprint)
        {
            if (endpoint == null) { return AcceptanceReport.WasAccepted; }
            Thing door = endpoint.Anchor;
            if (door == null || door.Destroyed || !door.Spawned || door.Map != map)
            { return AcceptanceReport.WasAccepted; }

            // Re-derived, never read from the saved endpoint. The saved cell is a snapshot that
            // exists so moving a door cannot silently redirect a route; the cell a pawn will
            // actually use is whatever the geometry says right now, and that is the one worth
            // protecting.
            IntVec3 approach = PortalAddressService.ApproachCellFor(door);
            if (!approach.IsValid || !footprint.Contains(approach)) { return AcceptanceReport.WasAccepted; }

            return new AcceptanceReport("RR_Portals_ApproachCellReserved".Translate(door.LabelShortCap));
        }
    }
}
