using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Turns a branch-owned coordinate into a saved portal address. Registration
    /// never generates a new space for an already visited site, never retargets a
    /// saved edge and never converts a legacy expedition into a graph connection.
    /// </summary>
    public static class PortalAddressService
    {
        private const string CoreDoorDef = "Door";

        /// <summary>
        /// Stable address identity: branch, coordinate and the actual threshold
        /// object. It is derived, never counted, so a replay produces the same id.
        /// </summary>
        public static string AddressId(RimroomsCampaignComponent campaign, CoordinateRecord coordinate, Thing threshold)
        {
            if (campaign == null || coordinate == null || threshold == null) { return null; }
            return campaign.BranchId + ":portal:" + coordinate.Id + ":" + threshold.GetUniqueLoadID();
        }

        public static bool NeedsLegacyThresholdRepair(CoordinateRecord coordinate)
        {
            RimroomsDestinationMapParent site = coordinate == null ? null : coordinate.Site as RimroomsDestinationMapParent;
            return site != null && site.NeedsThresholdRepair;
        }

        public static PortalConnectionRecord FindAddress(RimroomsCampaignComponent campaign,
            RimroomsPortalNetwork network, CoordinateRecord coordinate, Thing localThreshold)
        {
            if (network == null) { return null; }
            string id = AddressId(campaign, coordinate, localThreshold);
            return id == null ? null : network.Find(id);
        }

        /// <summary>
        /// Remember one laboratory address on a designated native gate. The site is
        /// ensured through the existing coordinate owner, so a saved space is
        /// recalled rather than rebuilt.
        /// </summary>
        public static CompanyActionResult RegisterLaboratoryAddress(CompRimroomsGate gate, CoordinateRecord coordinate)
        {
            RimroomsCampaignComponent campaign = Campaign();
            RimroomsPortalNetwork network = Network();
            if (campaign == null || !campaign.CanOperate || network == null || network.HasStateFault)
            { return Refuse("InvalidState"); }
            if (gate == null || gate.parent == null || !gate.IsNativeProvider || !gate.IsDesignated ||
                gate.HasPortalOwnerFault || gate.NativeBindingFailureKey != null)
            { return Refuse("GateNotReady"); }
            if (gate.parent.Map != campaign.Headquarters) { return Refuse("HeadquartersRequired"); }
            IntVec3 approach = gate.GateEntryCell;
            if (!approach.IsValid || !approach.InBounds(gate.parent.Map) || !approach.Standable(gate.parent.Map))
            { return Refuse("LocalApproachBlocked"); }
            if (coordinate == null || campaign.Coordinates.Count(record => ReferenceEquals(record, coordinate)) != 1)
            { return Refuse("UnknownCoordinate"); }

            Map siteMap;
            IntVec3 siteEntry;
            CompanyActionResult ensured = DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry);
            if (!ensured.Success) { return ensured; }
            RimroomsDestinationMapParent site = coordinate.Site as RimroomsDestinationMapParent;
            if (site == null || !site.LayoutReady || siteMap == null || site.Map != siteMap)
            { return Refuse("SiteUnavailable"); }
            if (site.NeedsThresholdRepair) { return Refuse("LegacyThreshold"); }

            Thing threshold = site.ReturnAnchor;
            IntVec3 thresholdApproach = site.ReturnCell;
            if (!UsableThreshold(threshold, thresholdApproach, siteMap)) { return Refuse("SiteThresholdUnavailable"); }

            string id = AddressId(campaign, coordinate, threshold);
            PortalNetworkResult result = network.Register(id, coordinate.Id, PortalConnectionKind.Laboratory,
                gate.parent, approach, threshold, thresholdApproach);
            if (result == PortalNetworkResult.Success)
            { campaign.RecordEvent("RR_Event_PortalAddressRegistered", id, coordinate.Id); }
            return Translate(result);
        }

        /// <summary>
        /// Remember one permanently open natural threshold. No gate, timer, operator
        /// or battery is consulted for this kind, now or later.
        /// </summary>
        public static CompanyActionResult RegisterNaturalAddress(Thing localThreshold, IntVec3 localApproach,
            CoordinateRecord coordinate)
        {
            RimroomsCampaignComponent campaign = Campaign();
            RimroomsPortalNetwork network = Network();
            if (campaign == null || !campaign.CanOperate || network == null || network.HasStateFault)
            { return Refuse("InvalidState"); }
            if (!UsableThreshold(localThreshold, localApproach, localThreshold == null ? null : localThreshold.Map))
            { return Refuse("LocalThresholdUnavailable"); }
            if (localThreshold.Faction != Faction.OfPlayer && localThreshold.Faction != null)
            { return Refuse("LocalThresholdUnavailable"); }
            if (coordinate == null || campaign.Coordinates.Count(record => ReferenceEquals(record, coordinate)) != 1)
            { return Refuse("UnknownCoordinate"); }

            Map siteMap;
            IntVec3 siteEntry;
            CompanyActionResult ensured = DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry);
            if (!ensured.Success) { return ensured; }
            RimroomsDestinationMapParent site = coordinate.Site as RimroomsDestinationMapParent;
            if (site == null || !site.LayoutReady || siteMap == null || site.Map != siteMap)
            { return Refuse("SiteUnavailable"); }
            if (site.NeedsThresholdRepair) { return Refuse("LegacyThreshold"); }
            if (localThreshold.Map == siteMap) { return Refuse("SameMap"); }

            Thing threshold = site.ReturnAnchor;
            IntVec3 thresholdApproach = site.ReturnCell;
            if (!UsableThreshold(threshold, thresholdApproach, siteMap)) { return Refuse("SiteThresholdUnavailable"); }

            string id = AddressId(campaign, coordinate, threshold);
            PortalNetworkResult result = network.Register(id, coordinate.Id, PortalConnectionKind.Natural,
                localThreshold, localApproach, threshold, thresholdApproach);
            if (result == PortalNetworkResult.Success)
            { campaign.RecordEvent("RR_Event_PortalAddressRegistered", id, coordinate.Id); }
            return Translate(result);
        }

        /// <summary>
        /// Replace a historical generated return anchor with an actual Core door so
        /// the saved site can hold a portal endpoint. The room graph, layout
        /// fingerprint, player construction and discoveries are untouched; only the
        /// one threshold object is replaced, once, against a saved receipt.
        /// </summary>
        public static CompanyActionResult RepairLegacyThreshold(CoordinateRecord coordinate)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign == null || !campaign.CanOperate) { return Refuse("InvalidState"); }
            if (coordinate == null || campaign.Coordinates.Count(record => ReferenceEquals(record, coordinate)) != 1)
            { return Refuse("UnknownCoordinate"); }
            RimroomsDestinationMapParent site = coordinate.Site as RimroomsDestinationMapParent;
            if (site == null || !site.LayoutReady) { return Refuse("SiteUnavailable"); }
            if (!site.NeedsThresholdRepair) { return CompanyActionResult.Existing(); }
            Map map = site.Map;
            if (map == null || !Find.Maps.Contains(map)) { return Refuse("SiteNotLoaded"); }

            Thing legacy = site.ReturnAnchor;
            if (legacy == null || !legacy.Spawned || legacy.Destroyed || legacy.Map != map)
            { return Refuse("LegacyAnchorMissing"); }
            IntVec3 anchorCell = legacy.Position;
            Rot4 rotation = legacy.Rotation;
            IntVec3 approach = site.ReturnCell;
            if (!approach.IsValid || !approach.InBounds(map) || !approach.Standable(map) ||
                !approach.AdjacentToCardinal(anchorCell) || !SingleCell(legacy.def))
            { return Refuse("LegacyGeometryUnsupported"); }

            ThingDef doorDef = DefDatabase<ThingDef>.GetNamedSilentFail(CoreDoorDef);
            if (doorDef == null || doorDef.thingClass == null ||
                !typeof(Building_Door).IsAssignableFrom(doorDef.thingClass) || !SingleCell(doorDef))
            { return Refuse("CoreDoorUnavailable"); }
            if (Current.Game.GetComponent<RimroomsPortalCrossingService>()?.Receipts
                .Any(receipt => receipt != null && !receipt.IsTerminal &&
                    (receipt.SourceMap == map || receipt.DestinationMap == map)) == true)
            { return Refuse("CrossingInProgress"); }

            string operationId = coordinate.Id + ":threshold-repair:1";
            Building_Door replacement = ThingMaker.MakeThing(doorDef,
                doorDef.MadeFromStuff ? ThingDefOf.Steel : null) as Building_Door;
            if (replacement == null) { return Refuse("CoreDoorUnavailable"); }

            // Preflight is complete: the one-cell legacy anchor is removed and the
            // Core door takes exactly its cell and orientation in the same action.
            try
            {
                legacy.Destroy(DestroyMode.Vanish);
                replacement.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(replacement, anchorCell, map, rotation);
                replacement.SetForbidden(false, false);
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Portals] Threshold repair interrupted on " + coordinate.Id +
                    "; the site, its graph and its discoveries are retained: " + error);
                return Refuse("RepairInterrupted");
            }
            if (!replacement.Spawned || replacement.Map != map || replacement.Position != anchorCell ||
                !site.TryRepairReturnThreshold(replacement, operationId))
            {
                Log.Error("[Rimrooms][Portals] Threshold repair could not be recorded on " + coordinate.Id +
                    "; the replacement door remains in place for manual review.");
                return Refuse("RepairNotRecorded");
            }
            campaign.RecordEvent("RR_Event_PortalThresholdRepaired", coordinate.Id, operationId);
            return CompanyActionResult.Applied();
        }

        private static bool SingleCell(ThingDef definition)
        { return definition != null && definition.size.x == 1 && definition.size.z == 1; }

        /// <summary>
        /// The approach cell for a threshold: the first standable cell cardinally
        /// adjacent to it. Chosen explicitly and never derived from a door's drawn
        /// rotation, because Core rotates a one-cell door during rendering.
        /// This is the single implementation; callers must not re-derive it.
        /// </summary>
        internal static IntVec3 ApproachCellFor(Thing door)
        {
            if (door == null || !door.Spawned || door.Map == null) { return IntVec3.Invalid; }
            foreach (IntVec3 direction in GenAdj.CardinalDirections)
            {
                IntVec3 candidate = door.Position + direction;
                if (candidate.InBounds(door.Map) && candidate.Standable(door.Map)) { return candidate; }
            }
            return IntVec3.Invalid;
        }

        internal static bool UsableThreshold(Thing anchor, IntVec3 approach, Map map)
        {
            return anchor is Building_Door && anchor.Spawned && !anchor.Destroyed && map != null &&
                anchor.Map == map && Find.Maps.Contains(map) && approach.IsValid && approach.InBounds(map) &&
                approach.Standable(map) && approach.AdjacentToCardinal(anchor.Position);
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }

        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }

        private static CompanyActionResult Refuse(string suffix)
        { return CompanyActionResult.Refused("RR_PortalAddress_" + suffix); }

        private static CompanyActionResult Translate(PortalNetworkResult result)
        {
            switch (result)
            {
                case PortalNetworkResult.Success: return CompanyActionResult.Applied();
                case PortalNetworkResult.Existing: return CompanyActionResult.Existing();
                case PortalNetworkResult.IdentityConflict: return Refuse("IdentityConflict");
                case PortalNetworkResult.InvalidEndpoint: return Refuse("EndpointRejected");
                case PortalNetworkResult.UnknownCoordinate: return Refuse("UnknownCoordinate");
                case PortalNetworkResult.WrongBranch: return Refuse("WrongBranch");
                case PortalNetworkResult.Obstructed: return Refuse("Obstructed");
                case PortalNetworkResult.Closed: return Refuse("Closed");
                default: return Refuse("InvalidState");
            }
        }
    }
}
