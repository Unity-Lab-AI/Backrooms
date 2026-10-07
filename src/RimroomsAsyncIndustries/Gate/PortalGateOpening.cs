using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    public sealed partial class CompRimroomsGate
    {
        private string portalConnectionId;
        private string portalOpeningId;
        private int portalOpeningSequence;
        private bool portalOwnerFault;

        /// <summary>
        /// Whether something has already come through on this opening.
        ///
        /// One per opening, so **closing the gate is a countermeasure that works** and is
        /// learnable from a single incident. It is cleared when the session ends rather than
        /// on a timer, which is what makes "close it and reopen" the deliberate cost.
        /// </summary>
        private bool incursionSpent;
        public bool IncursionSpentThisOpening { get { return incursionSpent; } }
        internal void NoteIncursionSpent() { incursionSpent = true; }
        private void ClearIncursionSpent() { incursionSpent = false; }
        private List<PortalOpeningRecoveryReceipt> portalRecoveryReceipts = new List<PortalOpeningRecoveryReceipt>();
        public string PortalConnectionId { get { return portalConnectionId; } }
        public string PortalOpeningId { get { return portalOpeningId; } }
        public bool HasPortalOwnerFault { get { return portalOwnerFault; } }
        private string CurrentOpeningId { get { return !string.IsNullOrEmpty(activeExpeditionId) ? activeExpeditionId : portalOpeningId; } }

        /// <summary>
        /// How far this branch has advanced the machine's ability to hold a connection.
        /// Counted from *completed* company projects, never from spendable insight, so
        /// a tier already earned cannot be lost by spending currency on the next one.
        /// </summary>
        public int PortalWindowTier
        {
            get
            {
                List<string> ladder = GateProps.portalWindowTierProjects;
                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                if (ladder == null || campaign == null || !campaign.CanOperate) { return 0; }
                int tier = 0;
                for (int index = 0; index < ladder.Count; index++)
                {
                    string project = ladder[index];
                    if (campaign.Projects.Any(record => record != null && record.Completed &&
                        record.ResearchDefName == project))
                    { tier++; }
                }
                return tier;
            }
        }

        /// <summary>
        /// Whether a supported opening now holds without a countdown. Reached by
        /// advancement only; the physical requirements still apply every tick, so
        /// "indefinite" means "for as long as it is powered, staffed and fed".
        /// </summary>
        public bool PortalOpeningIsIndefinite
        { get { return PortalWindowTier >= GateProps.portalIndefiniteTier; } }

        /// <summary>How long a laboratory opening lasts at the current tier, in ticks.</summary>
        public int PortalWindowTicksForTier
        {
            get
            {
                double ticks = GateProps.portalBaseWindowTicks;
                int tier = PortalWindowTier;
                for (int step = 0; step < tier; step++)
                {
                    ticks *= GateProps.portalWindowMultiplierPerTier;
                    if (ticks >= int.MaxValue) { return int.MaxValue; }
                }
                return (int)Math.Min(ticks, int.MaxValue);
            }
        }

        /// <summary>
        /// How long an **expedition's** opening lasts, in ticks: the same ladder a laboratory
        /// opening climbs, and the same figure the crew planner quotes.
        ///
        /// **It used to be the flat `openingWindowTicks`, 833 ticks -- about twenty in-game
        /// minutes -- while the Expedition page promised *"About 129.6 hours at advancement tier
        /// 1"*.** Found playing, 2026-10-07: an onboarding survey crew was stranded twenty minutes
        /// after crossing, and every recovery window after it closed before a crew could walk
        /// from where it was working to the return door, 150 and 230 cells away. Two derivations
        /// of one window, and the one the crew was actually given was the one nobody read.
        ///
        /// At the top rung a laboratory opening holds with no countdown at all. An expedition
        /// reads that as the longest window an int holds rather than as zero, because its return
        /// window is "ticks remaining above zero" and a zero would close it on the first tick.
        /// </summary>
        public int ExpeditionWindowTicks
        { get { return PortalOpeningIsIndefinite ? int.MaxValue : PortalWindowTicksForTier; } }

        /// <summary>
        /// A live portal session that is held rather than counted down. Legacy
        /// expeditions are never this, and neither is a natural connection, which has
        /// no machine, no operator and no timer of any kind.
        /// </summary>
        public bool IsSustainedPortalSession
        {
            get
            {
                return string.IsNullOrEmpty(activeExpeditionId) && !string.IsNullOrEmpty(portalOpeningId) &&
                    PortalOpeningIsIndefinite;
            }
        }

        /// <summary>
        /// Why a crossing cannot use this window right now, as a keyed reason, or null when it
        /// can.
        ///
        /// **Seven conditions used to collapse into one bool**, and the one message a player got
        /// was *"The laboratory connection for that address is not open."* So a drained battery
        /// reported an address fault, which cost the owner a session in a running game:
        /// *"its the same problem as before: the laboratory address for that is not open"*, and
        /// *"which i think is a power porblem"* -- they were right, and the text had sent them
        /// looking at the address.
        ///
        /// Third of its kind, after <c>CalibrationBlockerKey</c> and
        /// <c>StaffConsoleBlockerKey</c>, both added because one generic refusal covered several
        /// problems with several different fixes.
        /// </summary>
        public string PortalWindowBlockerKey(string connectionId, string openingId)
        {
            if (portalOwnerFault) { return "RR_PortalTravel_OwnerFault"; }
            if (string.IsNullOrEmpty(portalOpeningId) ||
                portalConnectionId != connectionId || portalOpeningId != openingId)
            { return "RR_PortalTravel_SessionClosed"; }
            if (!string.IsNullOrEmpty(activeExpeditionId))
            { return "RR_PortalTravel_ExpeditionHolds"; }
            if (IsEmergency) { return "RR_PortalTravel_InEmergency"; }
            if (openingTicksRemaining <= 0 && !PortalOpeningIsIndefinite)
            { return "RR_PortalTravel_WindowExpired"; }
            // **CROSSING readiness, not OPENING readiness**, and the difference is the whole of
            // owner direction 2026-10-03: *"if its open it doenst need special power to send
            // things through the gate"*. `CheckStationReadiness` is asked only where an opening
            // is actually started or recovered; it carries the spin-up counter and the supply
            // projection, and `ProjectedOpeningPowerFailure`'s own docstring says *"This gates
            // opening only"* while this call site was a crossing. See `CheckCrossingReadiness`.
            CompanyActionResult station = CheckCrossingReadiness(assignedOperator);
            if (!station.Success) { return station.MessageKey ?? "RR_Gate_OperatorLost"; }
            // **The stored-charge toll on a crossing is gone, deliberately.** It used to read
            //     float needed = OpeningPowerDrawWatts * CompPower.WattsToWattDaysPerTick;
            //     if (NativeStoredEnergy < needed) { return "RR_PortalTravel_NoCharge"; }
            // which charged the battery for passing through an aperture that is **already held**
            // — the owner's *"a error about not enough reserver power in the batteries"*. Every
            // line above this point establishes that the opening is live, so this check could
            // only ever fire in the one case the direction forbids.
            //
            // Nothing is unguarded by removing it: the tick spends the opening's energy every
            // tick and calls `EnterEmergency` when the supply runs dry, and `IsEmergency` is
            // refused above as `RR_PortalTravel_InEmergency`. Draining the reserve still ends the
            // session — it just no longer blocks a crossing before it has.
            //
            // `RR_PortalTravel_NoCharge` is kept in `Keyed/RR_Portals.xml` rather than deleted,
            // and the reason is **not** that the opening and recovery paths return it -- they do
            // not, they return `RR_NativeGate_OpeningEnergyLow` and
            // `RR_NativeGate_RecoveryEnergyLow`. It is kept because its text carries the owner's
            // *"there should be no loimit"* on how many batteries a gate may draw from --
            // *"Any number of them count."* -- and `proof-gate-circuit.py` asserts that sentence
            // separately. The proof derives the keys it guards from this file's own code, so an
            // unreachable key is correctly no longer treated as a refusal that could print raw.
            return null;
        }

        /// <summary>
        /// **Asks the blocker key rather than restating the conditions.** One authority, so the
        /// predicate that gates a crossing and the message a player reads cannot disagree.
        /// </summary>
        public bool HasUsablePortalWindow(string connectionId, string openingId)
        {
            return PortalWindowBlockerKey(connectionId, openingId) == null;
        }

        private void ExposePortalOpening()
        {
            // Missing fields on old saves stay empty; legacy runs never become
            // new graph connections implicitly.
            Scribe_Values.Look(ref portalConnectionId, "rr_gatePortalConnectionId");
            Scribe_Values.Look(ref portalOpeningId, "rr_gatePortalOpeningId");
            Scribe_Values.Look(ref portalOpeningSequence, "rr_gatePortalOpeningSequence", 0);
            Scribe_Values.Look(ref incursionSpent, "rr_gateIncursionSpent", false);
            Scribe_Collections.Look(ref portalRecoveryReceipts, "rr_gatePortalRecoveryReceipts", LookMode.Deep);
        }

        private void ValidatePortalOpeningOwner()
        {
            if (portalRecoveryReceipts == null) { portalRecoveryReceipts = new List<PortalOpeningRecoveryReceipt>(); }
            var operations = new HashSet<string>(StringComparer.Ordinal);
            portalOwnerFault = string.IsNullOrEmpty(portalConnectionId) != string.IsNullOrEmpty(portalOpeningId) ||
                (portalConnectionId != null && string.IsNullOrWhiteSpace(portalConnectionId)) ||
                (portalOpeningId != null && string.IsNullOrWhiteSpace(portalOpeningId)) ||
                (!string.IsNullOrEmpty(portalOpeningId) && !string.IsNullOrEmpty(activeExpeditionId)) ||
                (!string.IsNullOrEmpty(portalOpeningId) && portalOpeningSequence == 0) ||
                portalOpeningSequence < 0 || portalRecoveryReceipts.Any(receipt => receipt == null ||
                    string.IsNullOrWhiteSpace(receipt.OperationId) || string.IsNullOrWhiteSpace(receipt.OpeningId) ||
                    !operations.Add(receipt.OperationId));
            if (portalOwnerFault) { Log.Error("[Rimrooms][Gate] Conflicting saved portal ownership; operation disabled, original state retained."); }
        }

        public CompanyActionResult BeginPortalOpening(string connectionId)
        {
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();
            PortalConnectionRecord edge = network.Find(connectionId);
            RimroomsCampaignComponent campaign = Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (edge == null || edge.Kind != PortalConnectionKind.Laboratory || edge.First.Anchor != parent ||
                campaign == null || !campaign.CanOperate || edge.BranchId != campaign.BranchId ||
                !IsDesignated || portalOwnerFault || portalOpeningSequence < 0 || portalOpeningSequence == int.MaxValue ||
                nativeOpeningSequence < 0 || nativeOpeningSequence == int.MaxValue)
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            if (!string.IsNullOrEmpty(activeExpeditionId) || HasUnresolvedNativeTrip())
            { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }
            if (!string.IsNullOrEmpty(portalOpeningId))
            {
                if (portalConnectionId != connectionId) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }
                if (IsEmergency) { return CompanyActionResult.Refused("RR_Gate_RecoveryRequired"); }
                return network.ObserveLaboratoryOpening(connectionId, portalOpeningId) == PortalNetworkResult.Success
                    ? CompanyActionResult.Existing() : CompanyActionResult.Refused("RR_Gate_InvalidOperation");
            }
            // Readiness/physical energy are shared with the existing controller;
            // saved ownership remains separate from legacy expedition IDs.
            string nextId = campaign.BranchId + ":portal-window:" + parent.GetUniqueLoadID() + ":" + (portalOpeningSequence + 1);
            CompanyActionResult ready = CanOpen(assignedOperator, nextId);
            if (!ready.Success) { return ready; }
            portalOpeningSequence++;
            portalConnectionId = connectionId;
            portalOpeningId = nextId;
            incursionSpent = false;
            nativeOpeningSequence++;
            // A portal session runs on the duration ladder, not the historical
            // expedition window. At the top of the ladder there is no countdown at all.
            openingTicksRemaining = PortalOpeningIsIndefinite ? 0 : PortalWindowTicksForTier;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            ResetOpeningWarnings();
            failureKey = null;
            stablePowerTicks = Math.Min(stablePowerTicks, GateProps.stablePowerTicksRequired);
            if (network.ObserveLaboratoryOpening(connectionId, nextId) != PortalNetworkResult.Success)
            {
                // No energy has been debited yet. Retain consumed sequence IDs;
                // a retry cannot reuse another opening's receipts.
                portalConnectionId = null;
                portalOpeningId = null;
                openingTicksRemaining = 0;
                return CompanyActionResult.Refused("RR_Gate_InvalidOperation");
            }
            RecordGateActivity("RR_Event_GateOpeningStarted", nextId);
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult ClosePortalOpening(string connectionId)
        {
            if (portalOwnerFault || !string.IsNullOrEmpty(activeExpeditionId) || string.IsNullOrEmpty(portalOpeningId) ||
                portalConnectionId != connectionId) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            // An outage must not be cleared by close/open to evade its physical
            // recovery debit. Recover the same saved session first.
            if (IsEmergency) { return CompanyActionResult.Refused("RR_Gate_RecoveryRequired"); }
            CloseOpeningCore();
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult RecoverPortalOpening(string connectionId, string recoveryOperationId)
        {
            if (portalOwnerFault || string.IsNullOrWhiteSpace(recoveryOperationId) ||
                string.IsNullOrEmpty(portalOpeningId) || portalConnectionId != connectionId ||
                !string.IsNullOrEmpty(activeExpeditionId))
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            PortalOpeningRecoveryReceipt prior = portalRecoveryReceipts.FirstOrDefault(r => r.OperationId == recoveryOperationId);
            if (prior != null)
            {
                return prior.OpeningId == portalOpeningId ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Gate_OperationIdConflict");
            }
            if (!IsAwaitingRecovery) { return CompanyActionResult.Refused("RR_Gate_RecoveryWindowStillActive"); }
            if (!assemblyComplete || !calibrated || nativeOpeningSequence == int.MaxValue)
            { return CompanyActionResult.Refused("RR_Gate_NotCalibrated"); }
            CompanyActionResult ready = CheckStationReadiness(assignedOperator);
            if (!ready.Success) { return ready; }
            if (NativeStoredEnergy < RecoveryEnergyRequiredWattDays)
            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }
            if (!TrySpendNativeEnergy(GateProps.recoveryOpeningCostWattDays, false,
                portalOpeningId + ":recovery:" + recoveryOperationId))
            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }
            portalRecoveryReceipts.Add(new PortalOpeningRecoveryReceipt(recoveryOperationId, portalOpeningId));
            nativeOpeningSequence++;
            openingTicksRemaining = PortalOpeningIsIndefinite ? 0 : PortalWindowTicksForTier;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            ResetOpeningWarnings();
            failureKey = null;
            RecordGateActivity("RR_Event_GateRecoveryOpeningStarted", portalOpeningId,
                GateProps.recoveryOpeningCostWattDays.ToString("F2", System.Globalization.CultureInfo.InvariantCulture));
            return CompanyActionResult.Applied();
        }
    }

    public sealed class PortalOpeningRecoveryReceipt : IExposable
    {
        private string operationId;
        private string openingId;
        public string OperationId { get { return operationId; } }
        public string OpeningId { get { return openingId; } }
        public PortalOpeningRecoveryReceipt() { }
        internal PortalOpeningRecoveryReceipt(string operationId, string openingId)
        { this.operationId = operationId; this.openingId = openingId; }
        public void ExposeData()
        {
            Scribe_Values.Look(ref operationId, "operationId");
            Scribe_Values.Look(ref openingId, "openingId");
        }
    }
}
