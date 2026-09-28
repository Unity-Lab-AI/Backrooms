using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using Verse;

namespace RimroomsAsyncIndustries.Expedition
{
    public sealed partial class RimroomsExpeditionComponent
    {
        public CompanyActionResult CanAbandonExpedition(string expeditionId)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = records.FirstOrDefault(r => r.id == expeditionId && r.branchId == Campaign.BranchId);
            if (run == null) { return Refuse("RR_Exp_UnknownRun"); }
            if (run.status == ExpeditionStatus.Abandoned) { return CompanyActionResult.Existing(); }
            if (run != Active || run.Closed || run.openedTick < 0) { return Refuse("RR_Exp_CannotAbandon"); }
            CompRimroomsGate gate = GateFor(run);
            if (gate != null && gate.IsOpening && gate.ActiveExpeditionId != run.id) { return Refuse("RR_Exp_OwnerMissing"); }
            return CompanyActionResult.Applied();
        }

        // The UI must show the closure preview and obtain the player's explicit confirmation.
        // This closes a company operation; it never deletes or remotely recovers its people or property.
        public CompanyActionResult AbandonExpedition(string expeditionId, string reason)
        {
            CompanyActionResult check = CanAbandonExpedition(expeditionId);
            if (!check.Success || check.AlreadyApplied) { return check; }
            if (string.IsNullOrWhiteSpace(reason)) { return Refuse("RR_Exp_ClosureReasonRequired"); }
            ExpeditionRecord run = Active;
            ExpeditionCargo.Reconcile(run);
            UpdateReturned(run);
            ExpeditionClosureRecord closure = CreateClosureSnapshot(run, reason);
            run.closures.Add(closure);
            run.status = ExpeditionStatus.Abandoned;
            run.closedTick = closure.tick;
            run.reliefPending = false;
            run.failureKey = "RR_Exp_Abandoned";
            CompRimroomsGate gate = GateFor(run);
            if (gate != null && gate.ActiveExpeditionId == run.id) { gate.CloseOpening(); }
            StopTransitOrders(run, run.headquarters);
            StopTransitOrders(run, run.destination);
            Campaign.RecordEvent("RR_Event_ExpeditionAbandoned", run.id, run.coordinateId, closure.reason);
            Notify("RR_Exp_Abandoned");
            return CompanyActionResult.Applied();
        }

        public ExpeditionClosureRecord PreviewAbandonment(string expeditionId)
        {
            CompanyActionResult check = CanAbandonExpedition(expeditionId);
            if (!check.Success || check.AlreadyApplied) { return null; }
            ExpeditionCargo.Reconcile(Active);
            return CreateClosureSnapshot(Active, null);
        }

        private ExpeditionClosureRecord CreateClosureSnapshot(ExpeditionRecord run, string reason)
        {
            var closure = new ExpeditionClosureRecord
            {
                id = run.id + ":closure:" + run.closures.Count,
                reason = BoundedNote(reason, 500),
                tick = Find.TickManager.TicksGame,
                pendingTransferCount = transferRecovery.Count(r => r.expeditionId == run.id),
                heldForRecoveryCount = transferRecovery.Count(r => r.expeditionId == run.id && r.pawn != null && recoveryHeld.Contains(r.pawn))
            };
            List<Pawn> roster = run.crew.Concat(run.rescueCrew).Concat(run.recoveryPassengers).ToList();
            var seen = new HashSet<Pawn>();
            for (int i = 0; i < roster.Count; i++)
            {
                Pawn pawn = roster[i];
                if (pawn != null && !seen.Add(pawn)) { continue; }
                Map observed = MemberMap(pawn);
                closure.crew.Add(new CrewClosureRecord
                {
                    pawn = pawn,
                    pawnId = pawn == null ? run.id + ":unresolved-roster-slot:" + i : pawn.GetUniqueLoadID(),
                    label = pawn == null ? "RR_Exp_UnknownCrew".Translate().ToString() : pawn.LabelShortCap.ToString(),
                    knownDead = pawn != null && pawn.Dead,
                    observedMap = observed,
                    location = observed == null ? CrewClosureLocation.Unknown : observed == run.headquarters ? CrewClosureLocation.Headquarters :
                        observed == run.destination ? CrewClosureLocation.AtSite : CrewClosureLocation.Elsewhere
                });
            }
            foreach (CargoManifestEntry entry in run.cargo)
            {
                closure.cargo.Add(new CargoClosureRecord { entryId = entry.id, thingId = entry.itemLoadId,
                    label = entry.Label, count = entry.observedCount, location = entry.location,
                    knownDestroyed = entry.item != null && entry.item.Destroyed,
                    declaration = entry.declaration, declaredCount = entry.declaredCount, note = entry.note });
            }
            return closure;
        }

        public CompanyActionResult ResumeAbandonedExpedition(string expeditionId)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            if (Active != null) { return Refuse("RR_Exp_AlreadyActive"); }
            ExpeditionRecord run = records.FirstOrDefault(r => r.id == expeditionId && r.branchId == Campaign.BranchId);
            if (run == null || run.status != ExpeditionStatus.Abandoned) { return Refuse("RR_Exp_UnknownRun"); }
            if (HasBlockingTransfers() || transferRecovery.Any(r => r.expeditionId == run.id)) { return Refuse("RR_Exp_TransferInterrupted"); }
            CompRimroomsGate gate = GateFor(run);
            if (gate == null || !SiteExists(run)) { return Refuse("RR_Exp_OwnerMissing"); }
            if (run.recoveryAttemptCounter == int.MaxValue) { return Refuse("RR_Exp_RecoveryIdLimit"); }
            // Gate permits only its active stranded ID or its latest closed ID. A newer closed run
            // requires a new dispatch to the preserved site and physical pickup/carry recovery instead.
            CompanyActionResult ready = gate.CanRecover(gate.AssignedOperator, run.id,
                run.id + ":recovery:" + (run.recoveryAttemptCounter + 1));
            if (!ready.Success) { return ready; }
            run.status = ExpeditionStatus.Stranded;
            run.closedTick = -1;
            run.failureKey = "RR_Exp_Stranded";
            Campaign.RecordEvent("RR_Event_ExpeditionResumed", run.id, run.coordinateId);
            return CompanyActionResult.Applied();
        }

        public IReadOnlyList<Pawn> RecoverableCrewAtActiveSite()
        {
            ExpeditionRecord run = Active;
            if (run == null) { return new List<Pawn>(); }
            return records.Where(r => r.status == ExpeditionStatus.Abandoned && r.branchId == run.branchId && r.coordinateId == run.coordinateId)
                .SelectMany(Members).Where(p => MemberMap(p) == run.destination && !Members(run).Contains(p)).Distinct().ToList();
        }

        private bool IsHistoricalRecoverySubject(ExpeditionRecord active, Pawn pawn)
        {
            return pawn != null && MemberMap(pawn) == active.destination && records.Any(r => r != active &&
                r.branchId == active.branchId && r.coordinateId == active.coordinateId && r.status == ExpeditionStatus.Abandoned && Members(r).Contains(pawn));
        }

        public CompanyActionResult QueueRecoveredCrewReturn(Pawn pawn)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = Active;
            if (run == null || (run.status != ExpeditionStatus.OnSite && run.status != ExpeditionStatus.Returning) ||
                !CanWalk(pawn, run.destination) || (!run.recoveryPassengers.Contains(pawn) && !IsHistoricalRecoverySubject(run, pawn)))
            { return Refuse("RR_Exp_RecoveredCrewUnavailable"); }
            if (!ReturnWindowOpen(run)) { return Refuse("RR_Exp_ReturnClosed"); }
            CompanyActionResult capacity = ExpeditionCargo.CheckCapacity(pawn);
            if (!capacity.Success) { return capacity; }
            List<IntVec3> positions;
            if (!TryApproachPositions(run.returnCell, run.destination, new List<Pawn> { pawn }, out positions))
            { return Refuse("RR_Exp_GatePathBlocked"); }
            bool added = !run.recoveryPassengers.Contains(pawn);
            if (added) { run.recoveryPassengers.Add(pawn); }
            ExpeditionStatus previous = run.status;
            run.status = ExpeditionStatus.Returning;
            if (!OrderApproach(pawn, positions[0], true))
            {
                if (added) { run.recoveryPassengers.Remove(pawn); }
                run.status = previous;
                return Refuse("RR_Exp_ApproachInterrupted");
            }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult RefreshManifest(string expeditionId)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            ExpeditionRecord run = records.FirstOrDefault(r => r.id == expeditionId && r.branchId == Campaign.BranchId);
            if (run == null) { return Refuse("RR_Exp_UnknownRun"); }
            UpdateReturned(run);
            ExpeditionCargo.Reconcile(run);
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult CheckCargoDisposition(string entryId, CargoDisposition disposition, int count)
        {
            if (schemaVersion != CurrentSchemaVersion || !Campaign.CanOperate) { return Refuse("RR_Exp_BranchUnavailable"); }
            CargoManifestEntry entry;
            ExpeditionRecord run = FindCargoOwner(entryId, out entry);
            if (run == null || !Enum.IsDefined(typeof(CargoDisposition), disposition)) { return Refuse("RR_Exp_CargoUnknown"); }
            ExpeditionCargo.Reconcile(run);
            return CargoDeclarationFitsObservation(run, entry, disposition, count)
                ? CompanyActionResult.Applied() : Refuse("RR_Exp_CargoContradiction");
        }

        public CompanyActionResult RecordCargoDisposition(string entryId, CargoDisposition disposition, int count, string note)
        {
            CompanyActionResult check = CheckCargoDisposition(entryId, disposition, count);
            if (!check.Success) { return check; }
            if (disposition != CargoDisposition.Unspecified && string.IsNullOrWhiteSpace(note)) { return Refuse("RR_Exp_CargoNoteRequired"); }
            CargoManifestEntry entry;
            ExpeditionRecord run = FindCargoOwner(entryId, out entry);
            string savedNote = BoundedNote(note, 240);
            if (entry.declaration == disposition && entry.declaredCount == count && entry.note == savedNote && !entry.declarationNeedsReview)
            { return CompanyActionResult.Existing(); }
            entry.declarationHistory.Add(new CargoDeclarationRecord { disposition = disposition, count = count, note = savedNote,
                tick = Find.TickManager.TicksGame, observedCount = entry.observedCount, observedLocation = entry.location });
            entry.declaration = disposition;
            entry.declaredCount = count;
            entry.note = savedNote;
            entry.declarationNeedsReview = false;
            Campaign.RecordEvent("RR_Event_CargoDisposition", run.id, entry.id, disposition.ToString(), count.ToString());
            return CompanyActionResult.Applied();
        }

        internal static bool CargoDeclarationFitsObservation(ExpeditionRecord run, CargoManifestEntry entry, CargoDisposition disposition, int count)
        {
            if (disposition == CargoDisposition.Unspecified) { return count == 0; }
            if (count < 1) { return false; }
            if (disposition == CargoDisposition.Consumed || disposition == CargoDisposition.Lost)
            { return count <= entry.UnresolvedCount; }
            if (entry.item == null || entry.item.Destroyed || count > entry.observedCount) { return false; }
            if (disposition == CargoDisposition.LeftBehind)
            { return run.destination != null && entry.item.MapHeld == run.destination && (entry.item.Spawned || run.Closed); }
            // Used is an explicit report of using reusable equipment, never a claim that it vanished.
            return disposition == CargoDisposition.Used && run.openedTick >= 0;
        }

        private ExpeditionRecord FindCargoOwner(string entryId, out CargoManifestEntry entry)
        {
            entry = null;
            foreach (ExpeditionRecord run in records.Where(r => r.branchId == Campaign.BranchId))
            {
                entry = run.cargo.FirstOrDefault(e => e.id == entryId);
                if (entry != null) { return run; }
            }
            return null;
        }

        private static string BoundedNote(string text, int limit)
        { return string.IsNullOrWhiteSpace(text) ? null : text.Trim().Substring(0, Math.Min(limit, text.Trim().Length)); }

        private bool HasBlockingTransfers()
        {
            // Explicit closure can leave an irrecoverable old source pending without blocking the company.
            // Its original held pawn and recovery journal remain deep-saved and can still be restored only there.
            if (transferRecovery.Any(receipt => !records.Any(r => r.id == receipt.expeditionId &&
                r.branchId == Campaign.BranchId && r.status == ExpeditionStatus.Abandoned))) { return true; }
            return recoveryHeld.Cast<Pawn>().Any(pawn => !transferRecovery.Any(receipt => receipt.pawn == pawn));
        }

        private void ObserveOneClosedRun()
        {
            // Bound background work as expedition history grows; the selected UI record can refresh explicitly.
            if (records.Count == 0) { return; }
            if (closedObservationCursor >= records.Count) { closedObservationCursor = 0; }
            ExpeditionRecord run = records[closedObservationCursor++];
            if (!run.Closed || run.branchId != Campaign.BranchId) { return; }
            UpdateReturned(run);
            ExpeditionCargo.Reconcile(run);
        }

        private void MigrateSchemaOne()
        {
            // Additive migration: existing enum values, records, physical references and receipts are unchanged.
            // Old unvalidated declarations remain visible as history and require review, never invented proof.
            foreach (CargoManifestEntry entry in records.SelectMany(r => r.cargo))
            {
                if (entry.declaration == CargoDisposition.Unspecified) { continue; }
                entry.declaredCount = entry.declaration == CargoDisposition.Consumed || entry.declaration == CargoDisposition.Lost
                    ? entry.UnresolvedCount : entry.observedCount;
                entry.declarationNeedsReview = true;
                entry.declarationHistory.Add(new CargoDeclarationRecord { disposition = entry.declaration, count = entry.declaredCount,
                    note = entry.note, tick = -1, observedCount = entry.observedCount, observedLocation = entry.location });
            }
            schemaVersion = CurrentSchemaVersion;
        }
    }
}
