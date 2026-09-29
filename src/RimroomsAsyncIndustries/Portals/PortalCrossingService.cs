using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Executes one already-planned graph step using the original Pawn and its
    /// actual carry owner. This component does not create jobs or route pawns.
    /// </summary>
    public sealed class RimroomsPortalCrossingService : GameComponent, IThingHolder
    {
        private const int CurrentSchema = 1;
        private const int MaximumPendingCrossings = 256;

        /// <summary>
        /// How many finished receipts are kept as history. Unresolved receipts are
        /// never touched by this and keep their own separate bound, because they own
        /// real custody. Dropping the oldest *finished* records is safe for replay
        /// protection: every operation id is derived from an identity that cannot
        /// recur (a job load id, or a gate opening id), and a receipt can only be
        /// finished once the crossing it describes has already completed or rolled
        /// back, so no in-flight job can be holding a compacted id.
        /// </summary>
        private const int MaximumArchivedCrossings = 512;
        private int schema = CurrentSchema;
        private long nextSequence = 1;
        private List<PortalCrossingReceipt> receipts = new List<PortalCrossingReceipt>();
        private ThingOwner<Thing> heldThings;
        private string stateFaultKey;
        private bool busy;

        public RimroomsPortalCrossingService(Game game)
        { heldThings = new ThingOwner<Thing>(this); }

        public IReadOnlyList<PortalCrossingReceipt> Receipts { get { return receipts.AsReadOnly(); } }
        public string StateFaultKey { get { return stateFaultKey; } }
        public int HeldThingCount { get { return heldThings == null ? 0 : heldThings.Count; } }
        public IThingHolder ParentHolder { get { return null; } }
        public ThingOwner GetDirectlyHeldThings() { return heldThings; }
        public void GetChildHolders(List<IThingHolder> outChildren)
        { ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, heldThings); }

        private RimroomsCampaignComponent Campaign
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }
        private RimroomsPortalNetwork Network
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schema, "rr_portalCrossingSchema", CurrentSchema, forceSave: true);
            Scribe_Values.Look(ref nextSequence, "rr_portalCrossingNextSequence", 1L);
            Scribe_Collections.Look(ref receipts, "rr_portalCrossingReceipts", LookMode.Deep);
            Scribe_Deep.Look(ref heldThings, "rr_portalCrossingHeldThings", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                receipts = receipts ?? new List<PortalCrossingReceipt>();
                heldThings = heldThings ?? new ThingOwner<Thing>(this);
                // An older save may carry more history than the current bound.
                CompactArchivedReceipts();
                ValidateSavedState();
            }
        }

        /// <summary>
        /// Cross exactly one validated edge. The caller must bring the pawn to
        /// the saved source threshold; this method never schedules or pathfinds.
        /// </summary>
        public PortalCrossingResult Cross(Pawn pawn, PortalRouteStep step, string operationId)
        {
            if (busy) { return Refused("RR_PortalCrossing_Busy"); }
            RimroomsCampaignComponent campaign = Campaign;
            RimroomsPortalNetwork network = Network;
            if (!CanOperate(campaign, network)) { return Refused(stateFaultKey ?? "RR_PortalCrossing_InvalidState"); }
            if (!ValidOperationId(operationId) || pawn == null || step == null || step.Connection == null ||
                step.Source == null || step.Destination == null)
            { return Refused("RR_PortalCrossing_InvalidRequest"); }
            if (nextSequence == long.MaxValue)
            { return Refused("RR_PortalCrossing_SequenceExhausted"); }

            PortalCrossingReceipt prior = receipts.FirstOrDefault(r => r != null && r.OperationId == operationId);
            if (prior != null)
            {
                if (!prior.MatchesRequest(operationId, campaign.BranchId, pawn, step))
                { return Refused("RR_PortalCrossing_IdentityConflict", prior); }
                if (prior.IsTerminal) { return ResultFor(prior, true); }
                return ResultFor(prior, false);
            }
            if (receipts.Count(r => r != null && !r.IsTerminal) >= MaximumPendingCrossings)
            { return Refused("RR_PortalCrossing_PendingLimit"); }
            // Trim history before adding to it, so the saved list cannot creep past
            // its bound one automatic haul at a time.
            CompactArchivedReceipts();
            if (receipts.Any(r => r != null && !r.IsTerminal && r.Pawn == pawn))
            { return Refused("RR_PortalCrossing_PawnInTransit"); }

            string validationKey = ValidateRouteAndPawn(campaign, network, pawn, step);
            if (validationKey != null) { return Refused(validationKey); }
            if (!CanSafelySpawn(pawn, step.Destination.Map, step.Destination.ApproachCell))
            { return Refused("RR_PortalCrossing_DestinationUnsafe"); }

            string coordinateId = step.Connection.CoordinateId;
            var receipt = new PortalCrossingReceipt(operationId, nextSequence++, campaign.BranchId,
                step, pawn, coordinateId, Find.TickManager.TicksGame);
            receipts.Add(receipt); // Stable receipt exists before any custody change.
            busy = true;
            try
            {
                Thing carried = pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
                string cargoPolicy = PortalTraversalPolicy.CargoFailureKey(carried, pawn);
                if (cargoPolicy != null) { return FailBeforeDespawn(receipt, cargoPolicy); }
                receipt.RecordCarriedThing(carried);
                if (carried != null)
                {
                    if (carried.holdingOwner != pawn.carryTracker.innerContainer)
                    { return FailBeforeDespawn(receipt, "RR_PortalCrossing_CarryOwnerChanged"); }
                    Thing moved;
                    int count = pawn.carryTracker.innerContainer.TryTransferToContainer(carried, heldThings,
                        carried.stackCount, out moved, canMergeWithExistingStacks: false);
                    if (count != receipt.CarriedStackCount || moved != carried ||
                        !heldThings.Contains(carried) || carried.stackCount != receipt.CarriedStackCount)
                    { return FailBeforeDespawn(receipt, "RR_PortalCrossing_CargoCustodyFailed"); }
                }
                receipt.SetPhase(PortalCrossingPhase.CargoSecured);

                pawn.DeSpawn();
                receipt.SetPhase(PortalCrossingPhase.PawnDespawned);
                if (pawn.holdingOwner == null && !heldThings.TryAdd(pawn, canMergeWithExistingStacks: false) &&
                    !heldThings.Contains(pawn))
                { return MarkRecovery(receipt, "RR_PortalCrossing_PawnCustodyFailed"); }
                if (!heldThings.Contains(pawn))
                { return MarkRecovery(receipt, "RR_PortalCrossing_PawnCustodyMissing"); }

                // DeSpawn stops jobs and releases reservations. Recheck the
                // physical laboratory session after that cleanup before crossing.
                PortalConnectionRecord liveEdge = Network == null ? null : Network.Find(receipt.ConnectionId);
                if (liveEdge == null || !ConnectionMatchesReceipt(liveEdge, receipt) ||
                    Network.Availability(liveEdge) != PortalNetworkResult.Success)
                {
                    receipt.SetPhase(PortalCrossingPhase.NeedsRecovery, "RR_PortalCrossing_EdgeClosedDuringCleanup");
                    return TryRecoverToSource(receipt);
                }

                if (!TrySpawnOwnedPawn(pawn, step.Destination.Map, step.Destination.ApproachCell))
                {
                    receipt.SetPhase(PortalCrossingPhase.NeedsRecovery, "RR_PortalCrossing_DestinationSpawnFailed");
                    return TryRecoverToSource(receipt);
                }
                if (!CanUseEndpointNow(pawn, step.Destination))
                {
                    receipt.SetPhase(PortalCrossingPhase.NeedsRecovery, "RR_PortalCrossing_DestinationAccessDenied");
                    return TryRecoverToSource(receipt);
                }
                receipt.SetPhase(PortalCrossingPhase.Arrived);
                return FinishAtCurrentEndpoint(receipt, step.Destination.Map, step.Destination.ApproachCell,
                    PortalCrossingPhase.Committed);
            }
            catch (Exception ex)
            {
                Log.Error("[Rimrooms][Portals] Crossing " + operationId + " raised " + ex.GetType().Name + ".");
                return RecoverAfterException(receipt);
            }
            finally { busy = false; }
        }

        /// <summary>
        /// Reconciles an interrupted receipt without inventing a pawn/item. A
        /// held pawn is spawned only at one of its saved endpoint approach cells.
        /// </summary>
        public PortalCrossingResult Recover(string operationId)
        {
            if (busy) { return Refused("RR_PortalCrossing_Busy"); }
            if (!CanRecover(Campaign))
            { return Refused(stateFaultKey ?? "RR_PortalCrossing_InvalidState"); }
            if (!ValidOperationId(operationId)) { return Refused("RR_PortalCrossing_InvalidRequest"); }
            PortalCrossingReceipt receipt = receipts.FirstOrDefault(r => r != null && r.OperationId == operationId);
            if (receipt == null) { return Refused("RR_PortalCrossing_ReceiptMissing"); }
            if (receipt.IsTerminal) { return ResultFor(receipt, true); }

            busy = true;
            try { return ReconcileAndRecover(receipt); }
            catch (Exception ex)
            {
                Log.Error("[Rimrooms][Portals] Recovery " + operationId + " raised " + ex.GetType().Name + ".");
                EnsurePawnCustody(receipt);
                return MarkRecovery(receipt, "RR_PortalCrossing_RecoveryException");
            }
            finally { busy = false; }
        }

        public PortalCrossingReceipt FindReceipt(string operationId)
        { return receipts.FirstOrDefault(r => r != null && r.OperationId == operationId); }

        /// <summary>
        /// Trim the finished-receipt history to its bound, oldest first by the
        /// monotonic sequence the receipts already carry. Unresolved receipts are
        /// never removed: they own a deep-held pawn or cargo, and losing one would
        /// lose that custody.
        /// </summary>
        private void CompactArchivedReceipts()
        {
            int archived = 0;
            for (int index = 0; index < receipts.Count; index++)
            {
                if (receipts[index] != null && receipts[index].IsTerminal) { archived++; }
            }
            if (archived <= MaximumArchivedCrossings) { return; }
            List<PortalCrossingReceipt> oldest = receipts
                .Where(receipt => receipt != null && receipt.IsTerminal)
                .OrderBy(receipt => receipt.Sequence)
                .Take(archived - MaximumArchivedCrossings)
                .ToList();
            for (int index = 0; index < oldest.Count; index++) { receipts.Remove(oldest[index]); }
        }

        private PortalCrossingResult ReconcileAndRecover(PortalCrossingReceipt receipt)
        {
            if (!ReceiptIdentityIntact(receipt))
            { return MarkRecovery(receipt, "RR_PortalCrossing_ReceiptIdentityChanged"); }
            Pawn pawn = receipt.Pawn;
            if (pawn.Spawned)
            {
                if (pawn.Map == receipt.DestinationMap && pawn.Position == receipt.DestinationApproachCell)
                {
                    if (!CanUseReceiptEndpointNow(pawn, receipt, source: false))
                    { return TryRecoverToSource(receipt); }
                    receipt.SetPhase(PortalCrossingPhase.Arrived);
                    return FinishAtCurrentEndpoint(receipt, receipt.DestinationMap,
                        receipt.DestinationApproachCell, PortalCrossingPhase.Committed);
                }
                if (pawn.Map == receipt.SourceMap && pawn.Position == receipt.OriginalPawnCell)
                {
                    return FinishAtCurrentEndpoint(receipt, receipt.SourceMap, receipt.OriginalPawnCell,
                        PortalCrossingPhase.RolledBack);
                }
                if (OwnsMap(Campaign, pawn.Map) && RestoreCarriedThing(receipt))
                {
                    receipt.SetPhase(PortalCrossingPhase.RecoveredAtActualLocation,
                        "RR_PortalCrossing_RecoveredAtChangedLocation");
                    return ResultFor(receipt, false);
                }
                return MarkRecovery(receipt, "RR_PortalCrossing_PawnLocationUnresolved");
            }

            if (!EnsurePawnCustody(receipt))
            { return MarkRecovery(receipt, "RR_PortalCrossing_PawnCustodyMissing"); }

            RimroomsPortalNetwork network = Network;
            PortalConnectionRecord connection = network == null ? null : network.Find(receipt.ConnectionId);
            bool canContinueForward = connection != null && ConnectionMatchesReceipt(connection, receipt) &&
                network.Availability(connection) == PortalNetworkResult.Success;
            if (canContinueForward && TrySpawnOwnedPawn(pawn, receipt.DestinationMap, receipt.DestinationApproachCell))
            {
                if (!CanUseReceiptEndpointNow(pawn, receipt, source: false))
                { return TryRecoverToSource(receipt); }
                receipt.SetPhase(PortalCrossingPhase.Arrived);
                return FinishAtCurrentEndpoint(receipt, receipt.DestinationMap,
                    receipt.DestinationApproachCell, PortalCrossingPhase.Committed);
            }
            return TryRecoverToSource(receipt);
        }

        private PortalCrossingResult TryRecoverToSource(PortalCrossingReceipt receipt)
        {
            Pawn pawn = receipt.Pawn;
            if (pawn.Spawned)
            {
                if (pawn.Map == receipt.SourceMap && pawn.Position == receipt.OriginalPawnCell)
                { return FinishAtCurrentEndpoint(receipt, receipt.SourceMap, receipt.OriginalPawnCell, PortalCrossingPhase.RolledBack); }
                if (pawn.Map != receipt.DestinationMap || pawn.Position != receipt.DestinationApproachCell)
                { return MarkRecovery(receipt, "RR_PortalCrossing_PawnLocationUnresolved"); }
                if (!SecureCarriedThing(receipt))
                { return MarkRecovery(receipt, "RR_PortalCrossing_CargoCustodyFailed"); }
                pawn.DeSpawn();
            }
            if (!EnsurePawnCustody(receipt))
            { return MarkRecovery(receipt, "RR_PortalCrossing_PawnCustodyMissing"); }
            if (!TrySpawnOwnedPawn(pawn, receipt.SourceMap, receipt.OriginalPawnCell))
            { return MarkRecovery(receipt, "RR_PortalCrossing_SourceRecoveryBlocked"); }
            return FinishAtCurrentEndpoint(receipt, receipt.SourceMap, receipt.OriginalPawnCell,
                PortalCrossingPhase.RolledBack);
        }

        private PortalCrossingResult FinishAtCurrentEndpoint(PortalCrossingReceipt receipt, Map map,
            IntVec3 cell, PortalCrossingPhase terminalPhase)
        {
            if (!receipt.Pawn.Spawned || receipt.Pawn.Map != map || receipt.Pawn.Position != cell)
            { return MarkRecovery(receipt, "RR_PortalCrossing_EndpointMismatch"); }
            if (!RestoreCarriedThing(receipt))
            {
                receipt.SetPhase(PortalCrossingPhase.NeedsRecovery, "RR_PortalCrossing_CargoRestoreFailed");
                return ResultFor(receipt, false);
            }
            receipt.SetPhase(terminalPhase);
            return ResultFor(receipt, false);
        }

        private PortalCrossingResult RecoverAfterException(PortalCrossingReceipt receipt)
        {
            if (!ReceiptIdentityIntact(receipt))
            { return MarkRecovery(receipt, "RR_PortalCrossing_ReceiptIdentityChanged"); }
            Pawn pawn = receipt.Pawn;
            if (pawn.Spawned)
            {
                if (pawn.Map == receipt.DestinationMap && pawn.Position == receipt.DestinationApproachCell)
                {
                    if (!CanUseReceiptEndpointNow(pawn, receipt, source: false))
                    { return TryRecoverToSource(receipt); }
                    receipt.SetPhase(PortalCrossingPhase.Arrived);
                    return FinishAtCurrentEndpoint(receipt, receipt.DestinationMap,
                        receipt.DestinationApproachCell, PortalCrossingPhase.Committed);
                }
                if (pawn.Map == receipt.SourceMap && pawn.Position == receipt.OriginalPawnCell)
                { return FinishAtCurrentEndpoint(receipt, receipt.SourceMap, receipt.OriginalPawnCell, PortalCrossingPhase.RolledBack); }
            }
            EnsurePawnCustody(receipt);
            return TryRecoverToSource(receipt);
        }

        private PortalCrossingResult FailBeforeDespawn(PortalCrossingReceipt receipt, string key)
        {
            if (RestoreCarriedThing(receipt))
            {
                receipt.SetPhase(PortalCrossingPhase.RolledBack, key);
                return ResultFor(receipt, false);
            }
            return MarkRecovery(receipt, key);
        }

        private PortalCrossingResult MarkRecovery(PortalCrossingReceipt receipt, string key)
        {
            receipt.SetPhase(PortalCrossingPhase.NeedsRecovery, key);
            return ResultFor(receipt, false);
        }

        private bool RestoreCarriedThing(PortalCrossingReceipt receipt)
        {
            Thing cargo = receipt.CarriedThing;
            if (cargo == null) { return string.IsNullOrEmpty(receipt.CarriedThingLoadId); }
            if (cargo.GetUniqueLoadID() != receipt.CarriedThingLoadId || cargo.Destroyed)
            { return false; }
            Pawn pawn = receipt.Pawn;
            if (pawn.carryTracker == null || pawn.carryTracker.innerContainer == null)
            { return false; }
            ThingOwner<Thing> carry = pawn.carryTracker.innerContainer;
            if (carry.Contains(cargo))
            { return cargo.stackCount == receipt.CarriedStackCount && !heldThings.Contains(cargo); }
            if (!heldThings.Contains(cargo) || cargo.holdingOwner != heldThings ||
                cargo.stackCount != receipt.CarriedStackCount) { return false; }
            Thing moved;
            int count = heldThings.TryTransferToContainer(cargo, carry, receipt.CarriedStackCount,
                out moved, canMergeWithExistingStacks: false);
            return count == receipt.CarriedStackCount && moved == cargo && carry.Contains(cargo) &&
                cargo.stackCount == receipt.CarriedStackCount && !heldThings.Contains(cargo);
        }

        private bool SecureCarriedThing(PortalCrossingReceipt receipt)
        {
            Thing cargo = receipt.CarriedThing;
            if (cargo == null) { return string.IsNullOrEmpty(receipt.CarriedThingLoadId); }
            if (heldThings.Contains(cargo))
            { return cargo.holdingOwner == heldThings && cargo.stackCount == receipt.CarriedStackCount; }
            Pawn pawn = receipt.Pawn;
            if (pawn.carryTracker == null || pawn.carryTracker.innerContainer == null ||
                !pawn.carryTracker.innerContainer.Contains(cargo) || cargo.stackCount != receipt.CarriedStackCount)
            { return false; }
            Thing moved;
            int count = pawn.carryTracker.innerContainer.TryTransferToContainer(cargo, heldThings,
                receipt.CarriedStackCount, out moved, canMergeWithExistingStacks: false);
            return count == receipt.CarriedStackCount && moved == cargo && heldThings.Contains(cargo) &&
                cargo.stackCount == receipt.CarriedStackCount;
        }

        private bool EnsurePawnCustody(PortalCrossingReceipt receipt)
        {
            Pawn pawn = receipt == null ? null : receipt.Pawn;
            if (pawn == null || pawn.Destroyed || pawn.GetUniqueLoadID() != receipt.PawnLoadId)
            { return false; }
            if (pawn.Spawned) { return false; }
            if (heldThings.Contains(pawn)) { return pawn.holdingOwner == heldThings; }
            if (pawn.holdingOwner != null || Find.WorldPawns.Contains(pawn)) { return false; }
            return heldThings.TryAdd(pawn, canMergeWithExistingStacks: false) && heldThings.Contains(pawn);
        }

        private bool TrySpawnOwnedPawn(Pawn pawn, Map map, IntVec3 cell)
        {
            if (pawn == null || pawn.Destroyed || pawn.Spawned || !heldThings.Contains(pawn) ||
                pawn.holdingOwner != heldThings || !CanSafelySpawn(pawn, map, cell)) { return false; }
            Thing spawned = GenSpawn.Spawn(pawn, cell, map, pawn.Rotation, WipeMode.Vanish);
            return spawned == pawn && pawn.Spawned && pawn.Map == map && pawn.Position == cell;
        }

        private bool CanSafelySpawn(Pawn pawn, Map map, IntVec3 cell)
        {
            if (pawn == null || pawn.Destroyed || map == null || !Find.Maps.Contains(map) ||
                !cell.IsValid || !cell.InBounds(map) || !cell.Standable(map) ||
                !GenSpawn.CanSpawnAt(pawn.def, cell, map, pawn.Rotation, canWipeEdifices: false))
            { return false; }
            foreach (Thing existing in cell.GetThingList(map))
            {
                if (existing is Pawn || GenSpawn.SpawningWipes(pawn.def, existing.def)) { return false; }
            }
            return true;
        }

        private string ValidateRouteAndPawn(RimroomsCampaignComponent campaign,
            RimroomsPortalNetwork network, Pawn pawn, PortalRouteStep step)
        {
            PortalConnectionRecord edge = step.Connection;
            PortalEndpointRecord source = step.Source;
            PortalEndpointRecord destination = step.Destination;
            if (!network.Connections.Contains(edge) || network.Availability(edge) != PortalNetworkResult.Success ||
                (source != edge.First && source != edge.Second) ||
                (destination != edge.First && destination != edge.Second) || source == destination ||
                source.Map == destination.Map ||
                (source != edge.First ? source != edge.Second : destination != edge.Second))
            { return "RR_PortalCrossing_EdgeUnavailable"; }
            if (edge.BranchId != campaign.BranchId || !OwnsMap(campaign, source.Map) ||
                !OwnsMap(campaign, destination.Map)) { return "RR_PortalCrossing_WrongBranch"; }
            if (source.Anchor == null || destination.Anchor == null || source.Anchor.Destroyed ||
                destination.Anchor.Destroyed || source.Anchor.Map != source.Map || destination.Anchor.Map != destination.Map ||
                source.Anchor.Position != source.AnchorCell || destination.Anchor.Position != destination.AnchorCell ||
                pawn.Map != source.Map || pawn.Position != source.ApproachCell)
            { return "RR_PortalCrossing_NotAtSourceThreshold"; }
            if (!CanUseEndpointNow(pawn, source)) { return "RR_PortalCrossing_SourceAccessDenied"; }
            // One chokepoint owns who may pass and in what role, so no later
            // adapter or scheduler can let the far side walk out on its own.
            string traveller = PortalTraversalPolicy.TravellerFailureKey(pawn);
            if (traveller != null) { return traveller; }
            Thing carried = pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            return PortalTraversalPolicy.CargoFailureKey(carried, pawn);
        }

        /// <summary>
        /// The single eligibility rule, shared with callers so an order can refuse
        /// with the same reason the crossing itself would give. Mechs, subhumans and
        /// non-colonists are deliberately out of scope.
        /// </summary>
        public static string EligibilityFailureKey(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Drafted || pawn.InMentalState ||
                pawn.Faction != Faction.OfPlayer || !pawn.IsColonist || pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger())
            { return "RR_PortalCrossing_PawnNotEligible"; }
            return null;
        }

        /// <summary>Whether this pawn is already inside an unresolved crossing.</summary>
        public bool HasUnresolvedCrossing(Pawn pawn)
        { return pawn != null && receipts.Any(receipt => receipt != null && !receipt.IsTerminal && receipt.Pawn == pawn); }

        private bool ReceiptIdentityIntact(PortalCrossingReceipt receipt)
        {
            RimroomsCampaignComponent campaign = Campaign;
            if (receipt == null || campaign == null || !campaign.CanOperate || receipt.BranchId != campaign.BranchId ||
                receipt.Pawn == null || receipt.Pawn.Destroyed || receipt.Pawn.GetUniqueLoadID() != receipt.PawnLoadId ||
                receipt.SourceMap == null || receipt.DestinationMap == null ||
                !Find.Maps.Contains(receipt.SourceMap) || !Find.Maps.Contains(receipt.DestinationMap) ||
                !OwnsMap(campaign, receipt.SourceMap) || !OwnsMap(campaign, receipt.DestinationMap))
            { return false; }
            Thing cargo = receipt.CarriedThing;
            return string.IsNullOrEmpty(receipt.CarriedThingLoadId) ||
                (cargo != null && !cargo.Destroyed && cargo.GetUniqueLoadID() == receipt.CarriedThingLoadId);
        }

        private static bool ConnectionMatchesReceipt(PortalConnectionRecord connection,
            PortalCrossingReceipt receipt)
        {
            if (connection == null || receipt == null || connection.Id != receipt.ConnectionId ||
                connection.BranchId != receipt.BranchId || connection.CoordinateId != receipt.CoordinateId ||
                connection.Kind != receipt.ConnectionKind || connection.OpeningId != receipt.OpeningId ||
                connection.First == null || connection.Second == null) { return false; }
            PortalEndpointRecord source = receipt.SourceIsFirst ? connection.First : connection.Second;
            PortalEndpointRecord destination = receipt.SourceIsFirst ? connection.Second : connection.First;
            return source.Map == receipt.SourceMap && destination.Map == receipt.DestinationMap &&
                source.Anchor == receipt.SourceAnchor && destination.Anchor == receipt.DestinationAnchor &&
                source.Anchor != null && destination.Anchor != null &&
                source.Anchor.GetUniqueLoadID() == receipt.SourceAnchorLoadId &&
                destination.Anchor.GetUniqueLoadID() == receipt.DestinationAnchorLoadId &&
                source.AnchorCell == receipt.SourceAnchorCell && destination.AnchorCell == receipt.DestinationAnchorCell &&
                source.ApproachCell == receipt.SourceApproachCell &&
                destination.ApproachCell == receipt.DestinationApproachCell;
        }

        private static bool CanUseEndpointNow(Pawn pawn, PortalEndpointRecord endpoint)
        {
            Building_Door door = endpoint == null ? null : endpoint.Anchor as Building_Door;
            return pawn != null && pawn.Spawned && endpoint != null && door != null &&
                pawn.Map == endpoint.Map && endpoint.Anchor != null && endpoint.Anchor.Spawned &&
                endpoint.Anchor.Position == endpoint.AnchorCell && endpoint.ApproachCell == pawn.Position &&
                !endpoint.Anchor.IsForbidden(pawn) && !endpoint.ApproachCell.IsForbidden(pawn) &&
                door.CanPhysicallyPass(pawn);
        }

        private static bool CanUseReceiptEndpointNow(Pawn pawn, PortalCrossingReceipt receipt, bool source)
        {
            if (receipt == null) { return false; }
            Building_Door door = (source ? receipt.SourceAnchor : receipt.DestinationAnchor) as Building_Door;
            Map map = source ? receipt.SourceMap : receipt.DestinationMap;
            IntVec3 cell = source ? receipt.OriginalPawnCell : receipt.DestinationApproachCell;
            IntVec3 anchorCell = source ? receipt.SourceAnchorCell : receipt.DestinationAnchorCell;
            // Evaluate area restrictions only after the pawn is on the endpoint's
            // actual map; Core stores those restrictions by Map.
            return pawn != null && pawn.Spawned && pawn.Map == map && pawn.Position == cell &&
                door != null && door.Spawned && door.Position == anchorCell &&
                !door.IsForbidden(pawn) && !cell.IsForbidden(pawn) && door.CanPhysicallyPass(pawn);
        }

        private void ValidateSavedState()
        {
            stateFaultKey = null;
            if (schema != CurrentSchema || nextSequence < 1 || heldThings == null)
            { stateFaultKey = "RR_PortalCrossing_InvalidSave"; return; }
            var ids = new HashSet<string>(StringComparer.Ordinal);
            var heldReferences = new HashSet<Thing>();
            foreach (Thing thing in heldThings)
            {
                if (thing == null || !heldReferences.Add(thing))
                { stateFaultKey = "RR_PortalCrossing_InvalidSave"; return; }
            }
            long highestSequence = 0;
            foreach (PortalCrossingReceipt receipt in receipts)
            {
                if (receipt == null || !ValidOperationId(receipt.OperationId) || !ids.Add(receipt.OperationId) ||
                    receipt.Sequence < 1 || !Enum.IsDefined(typeof(PortalCrossingPhase), receipt.Phase) ||
                    string.IsNullOrEmpty(receipt.BranchId) || string.IsNullOrEmpty(receipt.ConnectionId) ||
                    (!receipt.IsTerminal && receipt.Pawn == null) ||
                    (receipt.Pawn != null && receipt.PawnLoadId != receipt.Pawn.GetUniqueLoadID()))
                { stateFaultKey = "RR_PortalCrossing_InvalidSave"; return; }
                highestSequence = Math.Max(highestSequence, receipt.Sequence);
                if (!receipt.IsTerminal && receipt.Pawn != null &&
                    !heldReferences.Contains(receipt.Pawn) && !receipt.Pawn.Spawned)
                { stateFaultKey = "RR_PortalCrossing_UnownedPawn"; return; }
                if (!string.IsNullOrEmpty(receipt.CarriedThingLoadId))
                {
                    Thing cargo = receipt.CarriedThing;
                    if (!receipt.IsTerminal && (cargo == null || cargo.Destroyed || cargo.GetUniqueLoadID() != receipt.CarriedThingLoadId))
                    { stateFaultKey = "RR_PortalCrossing_UnownedCargo"; return; }
                    if (!receipt.IsTerminal && cargo != null && !heldReferences.Contains(cargo) &&
                        (receipt.Pawn.carryTracker == null || !receipt.Pawn.carryTracker.innerContainer.Contains(cargo)))
                    { stateFaultKey = "RR_PortalCrossing_UnownedCargo"; return; }
                }
            }
            if (nextSequence <= highestSequence) { stateFaultKey = "RR_PortalCrossing_InvalidSave"; return; }
            foreach (Thing thing in heldReferences)
            {
                bool referenced = receipts.Any(receipt => receipt != null && !receipt.IsTerminal &&
                    (receipt.Pawn == thing || receipt.CarriedThing == thing));
                if (!referenced) { stateFaultKey = "RR_PortalCrossing_OrphanedHeldThing"; return; }
            }
        }

        private bool CanOperate(RimroomsCampaignComponent campaign, RimroomsPortalNetwork network)
        {
            return CanRecover(campaign) && network != null && !network.HasStateFault;
        }

        private bool CanRecover(RimroomsCampaignComponent campaign)
        { return stateFaultKey == null && schema == CurrentSchema && campaign != null && campaign.CanOperate && heldThings != null; }

        // Branch map ownership has one implementation, on the campaign component.
        private static bool OwnsMap(RimroomsCampaignComponent campaign, Map map)
        {
            return campaign != null && campaign.OwnsMap(map);
        }

        private static bool ValidOperationId(string value)
        { return !string.IsNullOrWhiteSpace(value) && value.Length <= 256; }

        private static PortalCrossingResult ResultFor(PortalCrossingReceipt receipt, bool alreadyApplied)
        {
            PortalCrossingStatus status;
            bool success = false;
            if (receipt.Phase == PortalCrossingPhase.Committed)
            { status = alreadyApplied ? PortalCrossingStatus.Existing : PortalCrossingStatus.Completed; success = true; }
            else if (receipt.Phase == PortalCrossingPhase.RolledBack)
            { status = PortalCrossingStatus.RolledBack; }
            else if (receipt.Phase == PortalCrossingPhase.RecoveredAtActualLocation)
            { status = PortalCrossingStatus.RecoveredAtActualLocation; }
            else { status = PortalCrossingStatus.NeedsRecovery; }
            return new PortalCrossingResult(status, success, alreadyApplied, receipt.FailureKey, receipt);
        }

        private static PortalCrossingResult Refused(string key, PortalCrossingReceipt receipt = null)
        { return new PortalCrossingResult(PortalCrossingStatus.Refused, false, false, key, receipt); }
    }
}
