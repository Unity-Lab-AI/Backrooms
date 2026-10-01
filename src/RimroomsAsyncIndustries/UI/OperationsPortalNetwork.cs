using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Generation;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private string portalCoordinateChoice;
        private Thing portalNaturalDoorChoice;

        private void DrawPortalNetwork(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_Portals_Heading".Translate());
            listing.Label("RR_Portals_Explanation".Translate());
            if (campaign == null || !campaign.CanOperate)
            {
                listing.Label("RR_Portals_NoBranch".Translate());
                listing.GapLine();
                return;
            }
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault)
            {
                listing.Label("RR_Portals_NetworkFault".Translate());
                listing.GapLine();
                return;
            }

            RimroomsPortalCrossingService crossings = Current.Game.GetComponent<RimroomsPortalCrossingService>();
            int unresolved = crossings == null
                ? 0 : crossings.Receipts.Count(receipt => receipt != null && !receipt.IsTerminal);
            if (unresolved > 0) { listing.Label("RR_Portals_CrossingPending".Translate(unresolved)); }

            DrawRememberedAddresses(listing, network);
            DrawAddressActions(listing, campaign, network);
            DrawTravelControls(listing, campaign, network, crossings);
            DrawConnectedWork(listing);
            listing.GapLine();
        }

        private void DrawTravelControls(Listing_Standard listing, RimroomsCampaignComponent campaign,
            RimroomsPortalNetwork network, RimroomsPortalCrossingService crossings)
        {
            listing.Label("RR_Portals_TravelHeading".Translate());
            listing.Label("RR_Portals_TravelExplanation".Translate());

            CompRimroomsGate gate = CurrentGate(campaign);
            if (gate != null && gate.IsDesignated)
            {
                if (!string.IsNullOrEmpty(gate.PortalOpeningId) && !string.IsNullOrEmpty(gate.PortalConnectionId))
                {
                    PortalConnectionRecord open = network.Find(gate.PortalConnectionId);
                    listing.Label("RR_Portals_SessionOpen".Translate(gate.PortalOpeningId,
                        gate.PortalConnectionId, gate.OpeningTicksRemaining));
                    if (gate.IsEmergency)
                    {
                        listing.Label("RR_Portals_SessionEmergency".Translate());
                        if (gate.IsAwaitingRecovery && listing.ButtonText("RR_Portals_EmergencyReturn".Translate()))
                        { ShowResult(PortalTravelService.OrderEmergencyReturn(gate)); }
                    }
                    else if (listing.ButtonText("RR_Portals_CloseSession".Translate()))
                    { ShowResult(PortalTravelService.CloseSession(gate)); }
                    if (open == null) { listing.Label("RR_PortalTravel_EndpointMissing".Translate()); }
                }
                else if (gate.IsSpinningUp)
                {
                    // A ramp is running. Showing the open buttons here as well would offer a
                    // second way to start something already in progress.
                    listing.Label("RR_Portals_SpinUpRunning".Translate(
                        (gate.SpinUpProgress * 100f).ToString("F0")));
                    if (listing.ButtonText("RR_Portals_AbortSpinUp".Translate()))
                    { ShowResult(gate.AbortSpinUp()); }
                }
                else
                {
                    List<PortalConnectionRecord> openable = network.Connections
                        .Where(edge => edge != null && edge.Kind == PortalConnectionKind.Laboratory &&
                            edge.First != null && edge.First.Anchor == gate.parent).ToList();
                    // **AN EMPTY LIST USED TO DRAW NOTHING AT ALL.** No button and no sentence:
                    // a player who has commissioned the door, run the assembly bill and
                    // calibrated has done everything the gate itself asks for and still sees no
                    // way to open it, because the address has to be remembered first and nothing
                    // said so. Owner, 2026-10-01: *"what do i do to get this gate open? ive tried
                    // everything"*. The register button is further down this same tab.
                    if (openable.Count == 0)
                    { listing.Label("RR_Portals_NoLaboratoryAddress".Translate()); }
                    foreach (PortalConnectionRecord address in openable)
                    {
                        PortalConnectionRecord captured = address;
                        // Routed through the ramp rather than straight to the opening, so there
                        // is exactly one way a laboratory gate opens no matter which button
                        // started it. Owner direction 2026-09-29: opening is "a ramp up process
                        // that takes a bit of time".
                        if (listing.ButtonText("RR_Portals_OpenSession".Translate(captured.CoordinateId)))
                        { ShowResult(gate.BeginSpinUp(captured.Id)); }
                    }
                    // **AND WHAT IS STILL IN THE WAY, NAMED.** Every one of these refuses the
                    // ramp, and before this the player had to press the button and read a single
                    // refusal to find out which -- or, with no address remembered, had no button
                    // to press at all. Listed rather than first-only, because a gate is usually
                    // missing more than one thing and finding them one launch at a time is what
                    // this costs.
                    foreach (string blocker in GateOpeningBlockers(gate))
                    { listing.Label(blocker); }
                }
            }

            Map map = Find.CurrentMap;
            List<PortalConnectionRecord> local = map == null
                ? new List<PortalConnectionRecord>() : PortalTravelService.LocalAddresses(map);
            if (local.Count == 0) { listing.Label("RR_Portals_NoLocalAddresses".Translate()); }
            else
            {
                Pawn selected = Find.Selector.SingleSelectedThing as Pawn;
                if (selected == null || selected.Map != map)
                { listing.Label("RR_Portals_NoSelectedPerson".Translate()); }
                else
                {
                    listing.Label("RR_Portals_SelectedPerson".Translate(selected.LabelShortCap));
                    foreach (PortalConnectionRecord address in local)
                    {
                        PortalRouteStep step = PortalTravelService.StepFrom(address, map);
                        if (step == null || step.Source.Anchor == null) { continue; }
                        PortalConnectionRecord captured = address;
                        if (listing.ButtonText("RR_Portals_OrderCrossing".Translate(selected.LabelShortCap,
                            step.Source.Anchor.LabelCap, captured.CoordinateId)))
                        { ShowResult(PortalTravelService.OrderCrossing(selected, captured)); }
                    }
                }
            }

            DrawUnresolvedCrossings(listing, crossings);
        }

        private static void DrawUnresolvedCrossings(Listing_Standard listing, RimroomsPortalCrossingService crossings)
        {
            if (crossings == null) { return; }
            List<PortalCrossingReceipt> pending = crossings.Receipts
                .Where(receipt => receipt != null && !receipt.IsTerminal).ToList();
            if (pending.Count == 0) { return; }
            listing.Label("RR_Portals_UnresolvedCrossings".Translate(pending.Count));
            foreach (PortalCrossingReceipt receipt in pending)
            {
                string who = receipt.Pawn == null
                    ? "RR_Portals_HeldPerson".Translate().ToString() : receipt.Pawn.LabelShortCap.ToString();
                string reason = string.IsNullOrEmpty(receipt.FailureKey)
                    ? string.Empty : "RR_Portals_UnresolvedReason".Translate(receipt.FailureKey.Translate()).ToString();
                listing.Label("RR_Portals_UnresolvedCrossingLine".Translate(receipt.OperationId, who,
                    receipt.Phase.ToString(), reason));
                if (listing.ButtonText("RR_Portals_RecoverCrossing".Translate(receipt.OperationId)))
                { ShowResult(PortalTravelService.RecoverCrossing(receipt.OperationId)); }
            }
        }

        private static void DrawRememberedAddresses(Listing_Standard listing, RimroomsPortalNetwork network)
        {
            IReadOnlyList<PortalConnectionRecord> addresses = network.Connections;
            if (addresses.Count == 0)
            {
                listing.Label("RR_Portals_NoAddresses".Translate());
                return;
            }
            listing.Label("RR_Portals_AddressCount".Translate(addresses.Count));
            foreach (PortalConnectionRecord address in addresses)
            {
                if (address == null) { continue; }
                string kind = KindLabelKey(address.Kind).Translate().ToString();
                listing.Label("RR_Portals_AddressLine".Translate(address.Id, address.CoordinateId, kind,
                    AvailabilityLabel(network.Availability(address))));
            }
        }

        /// <summary>
        /// Everything that would refuse a spin-up on this gate right now, in the order a player
        /// would fix it.
        ///
        /// ## Why this exists
        ///
        /// `BeginSpinUp` checks eight things and reports **one** refusal, and the player only
        /// sees it after pressing a button that may not be drawn at all -- the open buttons come
        /// from the remembered laboratory addresses, so a gate with none shows an empty panel.
        ///
        /// Owner, 2026-10-01, verbatim: *"what do i do to get this gate open? ive tried
        /// everything.. follow my past attempts and tell me what im missing"*. They had
        /// commissioned the door, run the eight-component bill at the machining table and let
        /// the crew calibrate -- everything the gate itself asks for -- and the panel still had
        /// no button and no sentence. **Finding preconditions one launch at a time is what that
        /// costs**, so all of them are listed rather than the first.
        ///
        /// Read-only: it names causes and changes nothing. The authority on whether a gate opens
        /// is still `BeginSpinUp`, which is why every line here corresponds to one of its
        /// refusals rather than restating the rule in a second place.
        /// </summary>
        private static IEnumerable<string> GateOpeningBlockers(CompRimroomsGate gate)
        {
            if (gate == null || !gate.IsDesignated) { yield break; }
            if (!gate.AssemblyComplete)
            { yield return "RR_Portals_BlockedAssembly".Translate(); }
            else if (!gate.Calibrated)
            { yield return "RR_Portals_BlockedCalibration".Translate(); }
            if (gate.AssignedOperator == null)
            { yield return "RR_Portals_BlockedNoOperator".Translate(); }
            else if (!gate.IsOperatorOnStation)
            { yield return "RR_Portals_BlockedOperatorAway".Translate(gate.AssignedOperator.LabelShortCap); }

            // **WHICH component is still doing its day job.** The switch defaults to normal
            // operation on purpose -- commissioning a door must not change how the colony works
            // -- so a player who never saw the gizmo has two components quietly refusing.
            CompRimroomsGateConsole station = gate.LinkedConsole == null
                ? null : gate.LinkedConsole.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGateConsole workshop = gate.AssemblyBench == null
                ? null : gate.AssemblyBench.TryGetComp<CompRimroomsGateConsole>();
            if (station != null && !station.IsGateControl)
            { yield return "RR_Portals_BlockedConsoleNormalOp".Translate(gate.LinkedConsole.LabelCap); }
            if (workshop != null && !workshop.IsGateControl)
            { yield return "RR_Portals_BlockedBenchNormalOp".Translate(gate.AssemblyBench.LabelCap); }

            if (gate.NativeBindingFailureKey != null)
            { yield return gate.NativeBindingFailureKey.Translate(); }
        }

        private static string AvailabilityLabel(PortalNetworkResult result)
        {
            switch (result)
            {
                case PortalNetworkResult.Success: return "RR_Portals_StatusAvailable".Translate().ToString();
                case PortalNetworkResult.Closed: return "RR_Portals_StatusClosed".Translate().ToString();
                case PortalNetworkResult.Obstructed: return "RR_Portals_StatusObstructed".Translate().ToString();
                case PortalNetworkResult.InvalidEndpoint: return "RR_Portals_StatusEndpointMissing".Translate().ToString();
                default: return "RR_Portals_StatusOther".Translate(result.ToString()).ToString();
            }
        }

        private void DrawAddressActions(Listing_Standard listing, RimroomsCampaignComponent campaign,
            RimroomsPortalNetwork network)
        {
            IReadOnlyList<CoordinateRecord> coordinates = campaign.Coordinates;
            if (coordinates.Count == 0)
            {
                listing.Label("RR_Portals_NoCoordinates".Translate());
                return;
            }
            if (listing.ButtonText("RR_Portals_SelectCoordinate".Translate()))
            { OpenPortalCoordinateMenu(coordinates); }
            CoordinateRecord coordinate = coordinates.FirstOrDefault(record => record.Id == portalCoordinateChoice)
                ?? coordinates[0];
            portalCoordinateChoice = coordinate.Id;
            listing.Label("RR_Portals_SelectedCoordinate".Translate(coordinate.Label ?? coordinate.Id, coordinate.Id));

            RimroomsDestinationMapParent site = coordinate.Site as RimroomsDestinationMapParent;
            if (site != null && site.NeedsThresholdRepair)
            {
                listing.Label("RR_Portals_LegacyRepairNeeded".Translate());
                listing.Label("RR_Portals_RepairExplanation".Translate());
                if (!string.IsNullOrEmpty(site.ThresholdRepairReceipt))
                { listing.Label("RR_Portals_RepairRecorded".Translate(site.ThresholdRepairReceipt)); }
                else if (!site.HasMap) { listing.Label("RR_Portals_SiteNotLoaded".Translate()); }
                else if (listing.ButtonText("RR_Portals_RepairThreshold".Translate()))
                { ShowResult(PortalAddressService.RepairLegacyThreshold(coordinate)); }
                return;
            }

            CompRimroomsGate gate = CurrentGate(campaign);
            if (gate == null || !gate.IsDesignated)
            { listing.Label("RR_Portals_GateRequired".Translate()); }
            else if (listing.ButtonText("RR_Portals_RememberLaboratory".Translate()))
            { ShowResult(PortalAddressService.RegisterLaboratoryAddress(gate, coordinate)); }

            if (listing.ButtonText("RR_Portals_SelectNaturalDoor".Translate()))
            { OpenPortalNaturalDoorMenu(campaign); }
            if (portalNaturalDoorChoice != null && portalNaturalDoorChoice.Spawned)
            {
                listing.Label("RR_Portals_SelectedNaturalDoor".Translate(portalNaturalDoorChoice.LabelCap,
                    portalNaturalDoorChoice.Position));
                IntVec3 approach = NaturalApproachCell(portalNaturalDoorChoice);
                if (approach.IsValid && listing.ButtonText("RR_Portals_RememberNatural".Translate()))
                { ShowResult(PortalAddressService.RegisterNaturalAddress(portalNaturalDoorChoice, approach, coordinate)); }
            }
        }

        private void OpenPortalCoordinateMenu(IReadOnlyList<CoordinateRecord> coordinates)
        {
            List<FloatMenuOption> options = coordinates.Where(record => record != null).Select(record =>
            {
                CoordinateRecord captured = record;
                return new FloatMenuOption("RR_Portals_CoordinateOption".Translate(
                    captured.Label ?? captured.Id, captured.Id), delegate { portalCoordinateChoice = captured.Id; });
            }).ToList();
            if (options.Count == 0)
            {
                Messages.Message("RR_Portals_NoCoordinates".Translate(), MessageTypeDefOf.RejectInput, false);
                return;
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private void OpenPortalNaturalDoorMenu(RimroomsCampaignComponent campaign)
        {
            List<FloatMenuOption> options = NaturalDoorCandidates(campaign).Select(door =>
            {
                Thing captured = door;
                return new FloatMenuOption("RR_Portals_NaturalDoorOption".Translate(captured.LabelCap,
                    captured.Position), delegate { portalNaturalDoorChoice = captured; });
            }).ToList();
            if (options.Count == 0)
            {
                Messages.Message("RR_Portals_NoNaturalDoorCandidates".Translate(), MessageTypeDefOf.RejectInput, false);
                return;
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private static IEnumerable<Thing> NaturalDoorCandidates(RimroomsCampaignComponent campaign)
        {
            Map map = Find.CurrentMap;
            if (campaign == null || map == null) { return Enumerable.Empty<Thing>(); }
            return map.listerBuildings.allBuildingsColonist.OfType<Building_Door>()
                .Where(door => door != null && door.Spawned && !door.Destroyed &&
                    NaturalApproachCell(door).IsValid)
                .OrderBy(door => door.Position.x).ThenBy(door => door.Position.z)
                .ThenBy(door => door.thingIDNumber).Cast<Thing>().ToList();
        }

        /// <summary>
        /// The saved approach cell is the contract for a threshold. There is one
        /// implementation of choosing it, on the service that owns thresholds.
        /// </summary>
        private static IntVec3 NaturalApproachCell(Thing door)
        { return PortalAddressService.ApproachCellFor(door); }
    
        /// <summary>
        /// The player-facing name of a connection kind. A switch rather than a ternary so a
        /// kind added later cannot be silently displayed as a laboratory.
        /// </summary>
        private static string KindLabelKey(PortalConnectionKind kind)
        {
            switch (kind)
            {
                case PortalConnectionKind.Natural: return "RR_Portals_KindNatural";
                case PortalConnectionKind.Emergence: return "RR_Portals_KindEmergence";
                default: return "RR_Portals_KindLaboratory";
            }
        }
}
}
