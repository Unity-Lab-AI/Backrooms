using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Generation;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Expedition
{
    /// <summary>Branch-local trip records. Pawns/items remain native owners except a failed-transfer recovery holder.</summary>
    public sealed partial class RimroomsExpeditionComponent : GameComponent, IThingHolder
    {
        private const int CurrentSchemaVersion = 2;
        private int schemaVersion = CurrentSchemaVersion;
        private int closedObservationCursor;
        private List<ExpeditionRecord> records = new List<ExpeditionRecord>();
        private List<TransferRecoveryRecord> transferRecovery = new List<TransferRecoveryRecord>();
        private ThingOwner<Pawn> recoveryHeld;
        public RimroomsExpeditionComponent(Game game) { recoveryHeld = new ThingOwner<Pawn>(this); }
        public IReadOnlyList<ExpeditionRecord> Records { get { return records; } }
        public IReadOnlyList<TransferRecoveryRecord> InterruptedTransfers { get { return transferRecovery; } }
        public ExpeditionRecord Active { get { return records.FirstOrDefault(r => r != null && !r.Closed); } }
        public IThingHolder ParentHolder { get { return null; } }
        public ThingOwner GetDirectlyHeldThings() { return recoveryHeld; }
        public void GetChildHolders(List<IThingHolder> outChildren)
        { ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, recoveryHeld); }
        private RimroomsCampaignComponent Campaign { get { return Current.Game.GetComponent<RimroomsCampaignComponent>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_expeditionSchema", 1, true);
            Scribe_Collections.Look(ref records, "rr_expeditions", LookMode.Deep);
            Scribe_Collections.Look(ref transferRecovery, "rr_transferRecovery", LookMode.Deep);
            Scribe_Deep.Look(ref recoveryHeld, "rr_recoveryHeld", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                records = records ?? new List<ExpeditionRecord>();
                transferRecovery = transferRecovery ?? new List<TransferRecoveryRecord>();
                recoveryHeld = recoveryHeld ?? new ThingOwner<Pawn>(this);
                if (schemaVersion == 1) { MigrateSchemaOne(); }
                if (schemaVersion != CurrentSchemaVersion) { Log.Error("[Rimrooms][Expedition] Unsupported saved expedition schema; actions disabled."); }
            }
        }

        public CompanyActionResult QueueLoadout(List<Pawn> crew)
        {
            CompanyActionResult check = CheckCrew(crew, null);
            if (!check.Success) { return check; }
            if (Active != null) { return Refuse("RR_Exp_AlreadyActive"); }
            return ExpeditionCargo.QueueLoadout(Campaign.Headquarters, crew);
        }

        public CompanyActionResult Dispatch(CompRimroomsGate gate, CoordinateRecord coordinate, List<Pawn> crew)
        {
            if (Active != null) { return Refuse("RR_Exp_AlreadyActive"); }
            if (HasBlockingTransfers()) { return Refuse("RR_Exp_TransferInterrupted"); }
            if (gate == null) { return Refuse("RR_Exp_OwnerMissing"); }
            CompanyActionResult check = CheckCrew(crew, gate);
            if (!check.Success) { return check; }
            if (coordinate == null || !Campaign.Coordinates.Contains(coordinate)) { return Refuse("RR_Exp_InvalidDestination"); }
            check = ExpeditionCargo.CheckKit(crew);
            if (!check.Success) { return check; }
            string id = Campaign.BranchId + ":expedition:" + Guid.NewGuid().ToString("N");
            check = gate.CanOpen(gate.AssignedOperator, id);
            if (!check.Success) { return check; }
            Map destination;
            IntVec3 entry;
            check = DestinationService.EnsureSite(Campaign, coordinate, out destination, out entry);
            if (!check.Success) { return check; }
            check = Campaign.EnsureRouteRecording(coordinate);
            if (!check.Success) { return check; }
            RimroomsDestinationMapParent parent = coordinate.Site as RimroomsDestinationMapParent;
            if (parent == null || destination == null || !entry.Standable(destination) || !parent.ReturnCell.Standable(destination))
            { return Refuse("RR_Exp_InvalidDestination"); }
            List<IntVec3> positions;
            if (!TryApproachPositions(gate.GateEntryCell, Campaign.Headquarters, crew, out positions))
            { return Refuse("RR_Exp_GatePathBlocked"); }
            var run = new ExpeditionRecord { id = id, branchId = Campaign.BranchId, coordinateId = coordinate.Id,
                status = ExpeditionStatus.Staging, gate = gate.parent, headquarters = Campaign.Headquarters,
                destination = destination, entryCell = entry, returnCell = parent.ReturnCell,
                crew = new List<Pawn>(crew), createdTick = Find.TickManager.TicksGame };
            records.Add(run);
            for (int i = 0; i < crew.Count; i++)
            {
                if (!OrderApproach(crew[i], positions[i], false))
                { run.failureKey = "RR_Exp_ApproachInterrupted"; AbortStaging(); return Refuse(run.failureKey); }
            }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult AbortStaging()
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = Active;
            if (run == null || run.status != ExpeditionStatus.Staging) { return Refuse("RR_Exp_NotStaging"); }
            StopTransitOrders(run, run.headquarters);
            if (run.reliefPending)
            { run.reliefPending = false; run.status = ExpeditionStatus.Stranded; }
            else { run.status = ExpeditionStatus.Aborted; run.closedTick = Find.TickManager.TicksGame; }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult Recall()
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = Active;
            if (run == null || (run.status != ExpeditionStatus.OnSite && run.status != ExpeditionStatus.Returning))
            { return Refuse("RR_Exp_NoOpenTrip"); }
            run.status = ExpeditionStatus.Returning;
            int orders = IssueReturnOrders(run);
            return orders > 0 || AllAtHeadquarters(run) ? CompanyActionResult.Applied() : Refuse("RR_Exp_ReturnNeedsRescue");
        }

        public CompanyActionResult ReopenReturnRoute()
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = Active;
            if (run == null || run.status != ExpeditionStatus.Stranded || HasBlockingTransfers())
            { return Refuse("RR_Exp_NoStrandedTrip"); }
            CompRimroomsGate gate = GateFor(run);
            if (gate == null || !SiteExists(run)) { return Refuse("RR_Exp_OwnerMissing"); }
            CompanyActionResult check = PrepareRecoveryOperation(run, gate);
            if (!check.Success) { return check; }
            check = gate.BeginRecoveryOpening(run.id, run.currentRecoveryOperationId);
            if (!check.Success) { return check; }
            run.emergency = false;
            run.failureKey = null;
            run.status = ExpeditionStatus.Returning;
            IssueReturnOrders(run);
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult SendRelief(Pawn rescuer)
        {
            ExpeditionRecord run = Active;
            if (run == null || run.status != ExpeditionStatus.Stranded || HasBlockingTransfers())
            { return Refuse("RR_Exp_NoStrandedTrip"); }
            CompRimroomsGate gate = GateFor(run);
            var relief = new List<Pawn> { rescuer };
            if (gate == null) { return Refuse("RR_Exp_OwnerMissing"); }
            CompanyActionResult check = CheckCrew(relief, gate);
            if (!check.Success) { return check; }
            if (run.crew.Contains(rescuer) || (run.rescueCrew.Count > 0 && !run.rescueCrew.Contains(rescuer)))
            { return Refuse("RR_Exp_ReliefLimit"); }
            if (!SiteExists(run)) { return Refuse("RR_Exp_OwnerMissing"); }
            List<Pawn> kitOwners = Members(run).Where(p => MemberMap(p) == run.destination || p == rescuer).ToList();
            if (!kitOwners.Contains(rescuer)) { kitOwners.Add(rescuer); }
            check = ExpeditionCargo.CheckKit(kitOwners, run.destination, run.coordinateId);
            if (!check.Success) { return check; }
            check = PrepareRecoveryOperation(run, gate);
            if (!check.Success) { return check; }
            List<IntVec3> positions;
            if (!TryApproachPositions(gate.GateEntryCell, run.headquarters, relief, out positions))
            { return Refuse("RR_Exp_GatePathBlocked"); }
            if (!run.rescueCrew.Contains(rescuer)) { run.rescueCrew.Add(rescuer); }
            run.reliefPending = true;
            run.status = ExpeditionStatus.Staging;
            if (!OrderApproach(rescuer, positions[0], false))
            { run.reliefPending = false; run.status = ExpeditionStatus.Stranded; return Refuse("RR_Exp_ApproachInterrupted"); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult QueueReliefLoadout(Pawn rescuer)
        {
            ExpeditionRecord run = Active;
            if (run == null || run.status != ExpeditionStatus.Stranded || !SiteExists(run)) { return Refuse("RR_Exp_NoStrandedTrip"); }
            CompRimroomsGate gate = GateFor(run);
            if (gate == null) { return Refuse("RR_Exp_OwnerMissing"); }
            var relief = new List<Pawn> { rescuer };
            CompanyActionResult check = CheckCrew(relief, gate);
            if (!check.Success) { return check; }
            if (run.crew.Contains(rescuer) || (run.rescueCrew.Count > 0 && !run.rescueCrew.Contains(rescuer)))
            { return Refuse("RR_Exp_ReliefLimit"); }
            return ExpeditionCargo.QueueLoadout(run.headquarters, relief,
                Members(run).Where(p => MemberMap(p) == run.destination), run.destination, run.coordinateId);
        }

        public CompanyActionResult QueueCasualtyReturn(Pawn carrier, Pawn casualty)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = Active;
            if (run == null || !Members(run).Contains(carrier) || (!Members(run).Contains(casualty) && !IsHistoricalRecoverySubject(run, casualty)) || carrier == casualty ||
                !CanWalk(carrier, run.destination) || carrier.carryTracker.CarriedThing != null)
            { return Refuse("RR_Exp_ReturnNeedsRescue"); }
            Thing target = casualty.Dead ? (Thing)casualty.Corpse : casualty;
            if (target == null || !target.Spawned || target.Map != run.destination || (!casualty.Dead && !casualty.Downed) ||
                !carrier.CanReserveAndReach(target, PathEndMode.ClosestTouch, Danger.Deadly) ||
                !carrier.CanReach(run.returnCell, PathEndMode.OnCell, Danger.Deadly))
            { return Refuse("RR_Exp_ReturnNeedsRescue"); }
            if (!ReturnWindowOpen(run)) { return Refuse("RR_Exp_ReturnClosed"); }
            JobDef carryDef = DefDatabase<JobDef>.GetNamedSilentFail("RR_CarryToReturnAnchor");
            if (carryDef == null) { return Refuse("RR_Exp_JobDefMissing"); }
            Job job = JobMaker.MakeJob(carryDef, target, run.returnCell);
            job.count = 1;
            bool added = !Members(run).Contains(casualty);
            if (added) { run.recoveryPassengers.Add(casualty); }
            if (!carrier.jobs.TryTakeOrderedJob(job, JobTag.Misc))
            {
                if (added) { run.recoveryPassengers.Remove(casualty); }
                return Refuse("RR_Exp_ReturnNeedsRescue");
            }
            run.status = ExpeditionStatus.Returning;
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult RecordCargoDisposition(string entryId, CargoDisposition disposition, string note)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            CargoManifestEntry entry;
            ExpeditionRecord run = FindCargoOwner(entryId, out entry);
            if (run == null) { return Refuse("RR_Exp_CargoUnknown"); }
            ExpeditionCargo.Reconcile(run);
            int count = disposition == CargoDisposition.Unspecified ? 0 :
                disposition == CargoDisposition.Consumed || disposition == CargoDisposition.Lost ? entry.UnresolvedCount : entry.observedCount;
            return RecordCargoDisposition(entryId, disposition, count, note);
        }

        public bool IsTransitOrderValid(Pawn pawn, Job job)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return false; }
            ExpeditionRecord run = Active;
            if (run == null || job == null || !Members(run).Contains(pawn) || !CanWalk(pawn, pawn.Map)) { return false; }
            if (job.def.defName == "RR_ApproachGate")
            { return run.status == ExpeditionStatus.Staging && pawn.Map == run.headquarters; }
            return (job.def.defName == "RR_ReturnThroughGate" || job.def.defName == "RR_CarryToReturnAnchor") &&
                pawn.Map == run.destination && (run.status == ExpeditionStatus.OnSite || run.status == ExpeditionStatus.Returning) && ReturnWindowOpen(run);
        }

        public override void GameComponentTick()
        {
            using (Core.RimroomsDiagnostics.Measure("expedition-tick")) { TickExpeditions(); }
        }

        private void TickExpeditions()
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate || Find.TickManager.TicksGame % 10 != 0) { return; }
            if (Find.TickManager.TicksGame % 60 == 0) { ObserveOneClosedRun(); }
            ExpeditionRecord run = Active;
            if (run == null) { return; }
            if (run.branchId != Campaign.BranchId) { run.failureKey = "RR_Exp_BranchUnavailable"; return; }
            try
            {
                UpdateReturned(run);
                if (run.status == ExpeditionStatus.Staging) { TickStaging(run); }
                else if (run.status == ExpeditionStatus.OnSite || run.status == ExpeditionStatus.Returning) { TickField(run); }
                if (Find.TickManager.TicksGame % 60 == 0) { ExpeditionCargo.Reconcile(run); }
            }
            catch (Exception exception)
            {
                Log.Error("[Rimrooms][Expedition] Trip retained after controller failure: " + exception);
                Strand(run, "RR_Exp_ControllerFailure");
            }
        }

        private void TickStaging(ExpeditionRecord run)
        {
            CompRimroomsGate gate = GateFor(run);
            List<Pawn> entering = run.reliefPending ? new List<Pawn>(run.rescueCrew) : new List<Pawn>(run.crew);
            if (gate == null || entering.Any(p => !CanWalk(p, run.headquarters)))
            { run.failureKey = "RR_Exp_ApproachInterrupted"; AbortStaging(); return; }
            if (entering.Any(p => p.CurJob?.def.defName != "RR_ApproachGate"))
            { run.failureKey = "RR_Exp_ApproachInterrupted"; AbortStaging(); return; }
            if (entering.Any(p => p.Position != p.CurJob.targetA.Cell || !p.Position.InHorDistOf(gate.GateEntryCell, 2.9f))) { return; }
            CompanyActionResult check = CheckCrew(entering, gate);
            if (check.Success)
            {
                check = run.reliefPending
                    ? ExpeditionCargo.CheckKit(Members(run).Where(p => MemberMap(p) == run.destination || entering.Contains(p)), run.destination, run.coordinateId)
                    : ExpeditionCargo.CheckKit(entering);
            }
            if (!check.Success) { run.failureKey = check.MessageKey; AbortStaging(); Notify(check.MessageKey); return; }
            if (!SiteExists(run)) { run.failureKey = "RR_Exp_OwnerMissing"; AbortStaging(); return; }
            List<IntVec3> destinationCells;
            if (!TryLandingPositions(run.entryCell, run.destination, entering.Count, out destinationCells))
            { run.failureKey = "RR_Exp_InvalidDestination"; AbortStaging(); return; }
            check = run.reliefPending ? gate.BeginRecoveryOpening(run.id, run.currentRecoveryOperationId) : gate.BeginOpening(run.id);
            if (!check.Success) { run.failureKey = check.MessageKey; AbortStaging(); Notify(check.MessageKey); return; }
            FirstSliceSiteComponent site = run.destination.GetComponent<FirstSliceSiteComponent>();
            site.BeginOpening(run.id, new List<Pawn>(run.crew));
            if (run.reliefPending) { foreach (Pawn rescuer in entering) { site.AddReliefPawn(rescuer); } }
            ExpeditionCargo.Capture(run, entering);
            run.status = ExpeditionStatus.OnSite;
            run.emergency = false;
            run.failureKey = null;
            run.reliefPending = false;
            if (run.openedTick < 0) { run.openedTick = Find.TickManager.TicksGame; }
            for (int i = 0; i < entering.Count; i++)
            {
                if (!TryMove(run, entering[i], run.destination, destinationCells[i]))
                { Strand(run, "RR_Exp_TransferInterrupted"); return; }
            }
            Notify("RR_Exp_Dispatched");
        }

        private void TickField(ExpeditionRecord run)
        {
            CompRimroomsGate gate = GateFor(run);
            if (gate == null || !SiteExists(run)) { Strand(run, "RR_Exp_OwnerMissing"); return; }
            if (AllAtHeadquarters(run)) { Complete(run); return; }
            FirstSliceSiteComponent site = run.destination.GetComponent<FirstSliceSiteComponent>();
            if (site.OpeningId == run.id && site.PendingDistortionCost > 0 && gate.ActiveExpeditionId == run.id)
            {
                CompanyActionResult debit = gate.SpendOpeningTicks(run.id, site.PendingDistortionCost, run.id + ":borrowed-corridor");
                if (debit.Success) { site.AcknowledgeDistortionCost(); }
                else { run.failureKey = debit.MessageKey; }
            }
            if (!string.IsNullOrEmpty(gate.FailureKey) && !run.emergency)
            {
                run.emergency = true;
                run.status = ExpeditionStatus.Returning;
                run.failureKey = gate.FailureKey;
                IssueReturnOrders(run);
                Notify("RR_Exp_EmergencyRecall");
            }
            if (!ReturnWindowOpen(run)) { Strand(run, "RR_Exp_Stranded"); return; }
            foreach (Pawn pawn in Members(run).ToList())
            {
                if (!CanWalk(pawn, run.destination) || pawn.CurJob == null) { continue; }
                string jobName = pawn.CurJob.def.defName;
                if (jobName != "RR_ReturnThroughGate" && jobName != "RR_CarryToReturnAnchor") { continue; }
                IntVec3 target = jobName == "RR_CarryToReturnAnchor" ? pawn.CurJob.targetB.Cell : pawn.CurJob.targetA.Cell;
                if (pawn.Position != target || !pawn.Position.InHorDistOf(run.returnCell, 2.9f)) { continue; }
                CompanyActionResult check = ExpeditionCargo.CheckCapacity(pawn);
                if (!check.Success) { run.failureKey = check.MessageKey; continue; }
                List<IntVec3> landing;
                if (!TryLandingPositions(gate.GateEntryCell, run.headquarters, 1, out landing))
                { run.failureKey = "RR_Exp_GatePathBlocked"; continue; }
                if (run.emergency && !gate.EmergencyReturnSpentForActiveExpedition)
                {
                    check = gate.TrySpendEmergencyReturnReserve(run.id);
                    if (!check.Success) { Strand(run, check.MessageKey); return; }
                }
                ExpeditionCargo.Capture(run, new[] { pawn });
                if (!TryMove(run, pawn, run.headquarters, landing[0]))
                { Strand(run, "RR_Exp_TransferInterrupted"); return; }
                if (pawn.carryTracker?.CarriedThing != null)
                { pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out _); }
                UpdateReturned(run);
            }
            if (AllAtHeadquarters(run)) { Complete(run); }
        }

        private CompanyActionResult CheckCrew(List<Pawn> crew, CompRimroomsGate gate)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            if (crew == null || crew.Count < 1 || crew.Count > 3 || crew.Distinct().Count() != crew.Count ||
                crew.Any(p => !CanWalk(p, Campaign.Headquarters) || !Campaign.Staff.Any(s => s.Employed && s.Pawn == p)))
            { return Refuse("RR_Exp_InvalidCrew"); }
            if (gate != null && (gate.parent == null || !gate.parent.Spawned || gate.parent.Map != Campaign.Headquarters || crew.Contains(gate.AssignedOperator)))
            { return Refuse("RR_Exp_OperatorMustStay"); }
            foreach (Pawn pawn in crew)
            {
                if (pawn.carryTracker?.CarriedThing != null) { return Refuse("RR_Exp_FinishHauling"); }
                CompanyActionResult capacity = ExpeditionCargo.CheckCapacity(pawn);
                if (!capacity.Success) { return capacity; }
            }
            return CompanyActionResult.Applied();
        }

        private static CompanyActionResult PrepareRecoveryOperation(ExpeditionRecord run, CompRimroomsGate gate)
        {
            if (run.recoveryAttemptCounter == int.MaxValue) { return Refuse("RR_Exp_RecoveryIdLimit"); }
            int next = run.recoveryAttemptCounter + 1;
            string operationId = run.id + ":recovery:" + next;
            CompanyActionResult ready = gate.CanRecover(gate.AssignedOperator, run.id, operationId);
            if (!ready.Success) { return ready; }
            run.recoveryAttemptCounter = next;
            run.currentRecoveryOperationId = operationId;
            return CompanyActionResult.Applied();
        }

        private static bool CanWalk(Pawn pawn, Map map)
        {
            return pawn != null && map != null && pawn.Spawned && pawn.Map == map && pawn.Faction == Faction.OfPlayer &&
                !pawn.Dead && !pawn.Downed && !pawn.InMentalState && pawn.jobs != null &&
                pawn.health.capacities.CapableOf(PawnCapacityDefOf.Moving);
        }
        private static IEnumerable<Pawn> Members(ExpeditionRecord run) { return run.crew.Concat(run.rescueCrew).Concat(run.recoveryPassengers).Where(p => p != null).Distinct(); }
        private static Map MemberMap(Pawn pawn) { return pawn == null ? null : pawn.Dead ? pawn.Corpse?.MapHeld : pawn.MapHeld; }
        private static CompRimroomsGate GateFor(ExpeditionRecord run)
        { return run.gate == null || run.gate.Destroyed || !run.gate.Spawned ? null : run.gate.TryGetComp<CompRimroomsGate>(); }
        private static bool SiteExists(ExpeditionRecord run)
        { return run.destination != null && Find.Maps.Contains(run.destination) && run.returnCell.Standable(run.destination) && run.headquarters != null && Find.Maps.Contains(run.headquarters); }
        private static bool AllAtHeadquarters(ExpeditionRecord run)
        { return run.crew.Count > 0 && run.crew.All(p => MemberMap(p) == run.headquarters) && run.rescueCrew.All(p => MemberMap(p) == run.headquarters) && run.recoveryPassengers.All(p => MemberMap(p) == run.headquarters); }
        private static void UpdateReturned(ExpeditionRecord run)
        { run.returned = run.crew.Where(p => p != null && run.entered.Contains(p) && !p.Dead && MemberMap(p) == run.headquarters).ToList(); }
        private static bool ReturnWindowOpen(ExpeditionRecord run)
        {
            CompRimroomsGate gate = GateFor(run);
            if (gate == null || gate.ActiveExpeditionId != run.id) { return false; }
            return string.IsNullOrEmpty(gate.FailureKey)
                ? gate.IsOpening && gate.OpeningTicksRemaining > 0 : gate.EmergencyReturnTicksRemaining > 0;
        }
        private static bool TryLandingPositions(IntVec3 anchor, Map map, int count, out List<IntVec3> positions)
        {
            positions = new List<IntVec3>();
            if (map == null || !anchor.InBounds(map) || !anchor.Standable(map)) { return false; }
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(anchor, 2.9f, true))
            {
                if (!cell.InBounds(map) || !cell.Standable(map) || cell.GetFirstPawn(map) != null ||
                    !map.reachability.CanReach(anchor, cell, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors))) { continue; }
                positions.Add(cell);
                if (positions.Count == count) { return true; }
            }
            return false;
        }
        private static bool TryApproachPositions(IntVec3 anchor, Map map, List<Pawn> pawns, out List<IntVec3> positions)
        {
            positions = new List<IntVec3>();
            foreach (Pawn pawn in pawns)
            {
                IntVec3 chosen = IntVec3.Invalid;
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(anchor, 2.9f, true))
                {
                    if (cell.InBounds(map) && cell.Standable(map) && !positions.Contains(cell) &&
                        pawn.CanReserveAndReach(cell, PathEndMode.OnCell, Danger.Deadly)) { chosen = cell; break; }
                }
                if (!chosen.IsValid) { return false; }
                positions.Add(chosen);
            }
            return true;
        }
        private static bool OrderApproach(Pawn pawn, IntVec3 cell, bool returning)
        {
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(
                returning ? "RR_ReturnThroughGate" : "RR_ApproachGate");
            if (definition == null) { return false; }
            Job job = JobMaker.MakeJob(definition, cell);
            return pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
        }
        private int IssueReturnOrders(ExpeditionRecord run)
        {
            var mobile = Members(run).Where(p => CanWalk(p, run.destination)).ToList();
            List<IntVec3> positions;
            if (mobile.Count == 0 || !TryApproachPositions(run.returnCell, run.destination, mobile, out positions)) { return 0; }
            int issued = 0;
            for (int i = 0; i < mobile.Count; i++) { if (OrderApproach(mobile[i], positions[i], true)) { issued++; } }
            return issued;
        }
        private static void StopTransitOrders(ExpeditionRecord run, Map map)
        {
            foreach (Pawn pawn in Members(run))
            {
                if (pawn.Map == map && pawn.CurJob != null && (pawn.CurJob.def.defName == "RR_ApproachGate" ||
                    pawn.CurJob.def.defName == "RR_ReturnThroughGate" || pawn.CurJob.def.defName == "RR_CarryToReturnAnchor"))
                { pawn.jobs.EndCurrentJob(JobCondition.InterruptForced); }
            }
        }
        private void Strand(ExpeditionRecord run, string key)
        {
            run.status = ExpeditionStatus.Stranded;
            run.failureKey = key;
            CloseOwnedOpening(run);
            StopTransitOrders(run, run.destination);
            StopTransitOrders(run, run.headquarters);
            ExpeditionCargo.Reconcile(run);
            Notify(key);
        }
        private void Complete(ExpeditionRecord run)
        {
            run.status = ExpeditionStatus.Completed;
            run.closedTick = Find.TickManager.TicksGame;
            CloseOwnedOpening(run);
            UpdateReturned(run);
            ExpeditionCargo.Reconcile(run);
            Notify("RR_Exp_Returned");
        }
        private static CompanyActionResult Refuse(string key) { return CompanyActionResult.Refused(key); }
        private static void CloseOwnedOpening(ExpeditionRecord run)
        {
            CompRimroomsGate gate = GateFor(run);
            if (gate != null && gate.ActiveExpeditionId == run.id) { gate.CloseOpening(); }
        }
        private static void Notify(string key) { Messages.Message(key.Translate(), MessageTypeDefOf.NeutralEvent, false); }

        private bool TryMove(ExpeditionRecord run, Pawn pawn, Map destination, IntVec3 cell)
        {
            Map source = pawn.Map;
            IntVec3 sourceCell = pawn.Position;
            bool drafted = pawn.Drafted;
            bool fireAtWill = pawn.drafter != null && pawn.drafter.FireAtWill;
            var receipt = new TransferRecoveryRecord { pawn = pawn, source = source, sourceCell = sourceCell, expeditionId = run.id };
            transferRecovery.Add(receipt);
            try
            {
                if (!pawn.Spawned || destination == null || !cell.Standable(destination)) { throw new InvalidOperationException("Transfer anchor unavailable."); }
                pawn.DeSpawnOrDeselect();
                GenSpawn.Spawn(pawn, cell, destination, Rot4.South);
                if (!pawn.Spawned || pawn.Map != destination) { throw new InvalidOperationException("Native spawn did not attach the original pawn."); }
                pawn.inventory.UnloadEverything = false;
                if (pawn.drafter != null) { pawn.drafter.Drafted = drafted; pawn.drafter.FireAtWill = fireAtWill; }
                if (destination == run.destination && !run.entered.Contains(pawn)) { run.entered.Add(pawn); }
                transferRecovery.Remove(receipt);
                return true;
            }
            catch (Exception exception)
            {
                Log.Error("[Rimrooms][Expedition] Transfer stopped for " + pawn.GetUniqueLoadID() + ": " + exception);
                if (pawn.Spawned) { transferRecovery.Remove(receipt); return false; }
                try
                {
                    if (source != null && Find.Maps.Contains(source) && sourceCell.Standable(source))
                    { GenSpawn.Spawn(pawn, sourceCell, source, Rot4.South); }
                }
                catch (Exception rollback) { Log.Error("[Rimrooms][Expedition] Transfer rollback retained for explicit recovery: " + rollback); }
                if (pawn.Spawned) { transferRecovery.Remove(receipt); }
                else if (pawn.holdingOwner == null) { recoveryHeld.TryAdd(pawn, false); }
                return false;
            }
        }

        public CompanyActionResult RecoverInterruptedTransfers()
        {
            if (schemaVersion != CurrentSchemaVersion || transferRecovery.Count == 0) { return Refuse("RR_Exp_NoTransferRecovery"); }
            foreach (TransferRecoveryRecord receipt in transferRecovery.ToList())
            {
                Pawn pawn = receipt.pawn;
                if (pawn == null) { continue; }
                if (pawn.Spawned) { transferRecovery.Remove(receipt); continue; }
                if (!recoveryHeld.Contains(pawn) || receipt.source == null || !Find.Maps.Contains(receipt.source)) { continue; }
                List<IntVec3> positions;
                if (!TryLandingPositions(receipt.sourceCell, receipt.source, 1, out positions)) { continue; }
                recoveryHeld.Remove(pawn);
                try
                {
                    GenSpawn.Spawn(pawn, positions[0], receipt.source, Rot4.South);
                    if (pawn.Spawned) { transferRecovery.Remove(receipt); }
                    else { recoveryHeld.TryAdd(pawn, false); }
                }
                catch (Exception exception)
                {
                    if (!pawn.Spawned && pawn.holdingOwner == null) { recoveryHeld.TryAdd(pawn, false); }
                    Log.Error("[Rimrooms][Expedition] Recovery remains pending: " + exception);
                }
            }
            return transferRecovery.Count == 0 ? CompanyActionResult.Applied() : Refuse("RR_Exp_TransferInterrupted");
        }
    }
}
