using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// The ramp a laboratory gate runs through before a connection is actually open.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"when u establish a backrooms portal
    /// connection the specific addresss should be connected and the gate opened but it
    /// neededs to be a ramp up process that takes a bit of time like with everything the
    /// pawns needs to do/maintaing/ operate to opening the gate process like a item build in
    /// a way"*.
    ///
    /// ## The ramp belongs to opening, not to one button
    ///
    /// Three things can start an opening: dialling a remembered address, opening a session
    /// from the operations window, and re-opening after the address was just registered.
    /// All three route through here, so there is **exactly one way a gate opens** and the
    /// ramp cannot be skipped by choosing a different entry point. <see
    /// cref="CompRimroomsGate.BeginPortalOpening"/> is still the thing that opens the
    /// connection; it is simply no longer reachable without first doing the work.
    ///
    /// ## "like a item build in a way"
    ///
    /// Work, not a timer. It accumulates at the assigned operator's own working speed --
    /// the same stat calibration uses, so a better technician really does bring a gate up
    /// faster -- and it is shown on the console as a progress bar, which is the one piece of
    /// interface every RimWorld player already reads without being taught.
    ///
    /// ## "maintaing"
    ///
    /// The ramp only climbs while the gate is **actually being held**: operator on station,
    /// power and headroom present, cutoff not thrown. Left alone it bleeds back down, and at
    /// zero it lapses with a message rather than sitting as a half-finished thing nobody can
    /// see. Decay is deliberately **slower than progress**, so walking away costs real time
    /// but never instantly erases a long ramp -- the same "no unavoidable instant failure"
    /// rule every threat in this mod obeys.
    ///
    /// ## Why the address book now earns its keep
    ///
    /// Required work falls with every previous connection this gate has made to that
    /// address. A route the crew has run a dozen times comes up fast; somewhere they have
    /// never been takes the full ramp. That turns the 0.8.8 history from a convenience list
    /// into the gate's **learned routes**, and it is why pinning an entry protects something
    /// real: the familiarity lives on the entry, so evicting it costs the discount too.
    ///
    /// The discount never reaches zero. It floors at a fraction of the base, because a gate
    /// that opens instantly is a gate with no operating crew, and the whole point of the
    /// direction above is that people have to run the machine.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        private string spinUpConnectionId;
        private string spinUpCoordinateId;
        private float spinUpWorkDone;
        private float spinUpWorkRequired;
        private bool spinUpHeldAtFull;

        /// <summary>
        /// The rate this ramp was last seen climbing at. Saved, so decay stays tied to the
        /// crew that was actually running the machine even after that operator has been
        /// reassigned, downed or killed -- which is exactly when a ramp starts bleeding.
        /// </summary>
        private float spinUpObservedRate = DefaultSpinUpRate;

        /// <summary>The rate assumed before anybody has worked the ramp at all.</summary>
        private const float DefaultSpinUpRate = 1f;

        /// <summary>A ramp is running toward an opening on this gate.</summary>
        public bool IsSpinningUp
        { get { return !string.IsNullOrEmpty(spinUpConnectionId) && !IsOpening; } }

        public string SpinUpConnectionId { get { return spinUpConnectionId; } }
        public float SpinUpWorkDone { get { return spinUpWorkDone; } }
        public float SpinUpWorkRequired { get { return spinUpWorkRequired; } }

        /// <summary>Ramp progress from 0 to 1, for the console progress bar and the readout.</summary>
        public float SpinUpProgress
        {
            get
            {
                if (!IsSpinningUp || spinUpWorkRequired <= 0f) { return 0f; }
                return Mathf.Clamp01(spinUpWorkDone / spinUpWorkRequired);
            }
        }

        /// <summary>
        /// Whether the ramp is currently climbing. This is the same set of conditions a live
        /// opening is held by, on purpose: bringing a connection up cannot require less than
        /// keeping one up, or a player could ramp under conditions that immediately drop it.
        /// </summary>
        public bool SpinUpIsSupported
        {
            get
            {
                return parent != null && parent.Spawned && !portalOwnerFault && !KillSwitchThrown &&
                    IsOperatorOnStation && HasPowerAndHeadroom();
            }
        }

        internal void ExposeSpinUp()
        {
            Scribe_Values.Look(ref spinUpConnectionId, "rr_gateSpinUpConnectionId");
            Scribe_Values.Look(ref spinUpCoordinateId, "rr_gateSpinUpCoordinateId");
            Scribe_Values.Look(ref spinUpWorkDone, "rr_gateSpinUpWorkDone", 0f);
            Scribe_Values.Look(ref spinUpWorkRequired, "rr_gateSpinUpWorkRequired", 0f);
            Scribe_Values.Look(ref spinUpHeldAtFull, "rr_gateSpinUpHeldAtFull", false);
            Scribe_Values.Look(ref spinUpObservedRate, "rr_gateSpinUpObservedRate", DefaultSpinUpRate);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // A saved ramp with no target, no requirement or an impossible amount of work
                // is discarded rather than carried: it can never complete, and leaving it
                // would show the player a progress bar that never moves.
                if (string.IsNullOrWhiteSpace(spinUpConnectionId) || spinUpWorkRequired <= 0f ||
                    float.IsNaN(spinUpWorkDone) || float.IsNaN(spinUpWorkRequired))
                { ClearSpinUpState(); }
                else
                {
                    spinUpWorkDone = Mathf.Clamp(spinUpWorkDone, 0f, spinUpWorkRequired);
                    if (!(spinUpObservedRate > 0f)) { spinUpObservedRate = DefaultSpinUpRate; }
                }
            }
        }

        private void ClearSpinUpState()
        {
            spinUpConnectionId = null;
            spinUpCoordinateId = null;
            spinUpWorkDone = 0f;
            spinUpWorkRequired = 0f;
            spinUpHeldAtFull = false;
            spinUpObservedRate = DefaultSpinUpRate;
        }

        /// <summary>
        /// How many times this gate has already connected to a coordinate. Read from the
        /// gate's own address book, which is the only place that count exists.
        /// </summary>
        private int PriorConnectionsTo(string coordinateId)
        {
            if (string.IsNullOrEmpty(coordinateId)) { return 0; }
            IReadOnlyList<GateHistoryEntry> entries = ConnectionHistory;
            for (int index = 0; index < entries.Count; index++)
            {
                GateHistoryEntry entry = entries[index];
                if (entry != null && string.Equals(entry.coordinateId, coordinateId, StringComparison.Ordinal))
                { return Math.Max(0, entry.times); }
            }
            return 0;
        }

        /// <summary>
        /// The work one opening costs, after familiarity. Multiplicative decay per prior
        /// connection, floored so a well-worn route is quick but never free.
        /// </summary>
        public float SpinUpWorkRequiredFor(string coordinateId)
        {
            // Scaled by the whole footprint, for the same reason the power draw is: a bigger
            // gate is more machine to energise, and the owner made "costs more to run" a
            // condition of the larger sizes rather than a side effect of them.
            float required = GateProps.dialSpinUpWorkRequired * GateCellCount;
            float floor = required * GateProps.dialSpinUpFloorFraction;
            int prior = PriorConnectionsTo(coordinateId);
            for (int step = 0; step < prior; step++)
            {
                required *= GateProps.dialSpinUpFamiliarityFactor;
                if (required <= floor) { return floor; }
            }
            return Mathf.Max(floor, required);
        }

        /// <summary>
        /// Start the ramp toward an already-registered laboratory connection. Refuses for
        /// every reason a direct opening would, checked **before** any work is invested, so
        /// a player never spends a crew's time on a ramp that could not have finished.
        /// </summary>
        public CompanyActionResult BeginSpinUp(string connectionId)
        {
            if (string.IsNullOrWhiteSpace(connectionId)) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            if (portalOwnerFault || !IsDesignated)
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            if (IsOpening) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }
            if (IsSpinningUp)
            {
                return string.Equals(spinUpConnectionId, connectionId, StringComparison.Ordinal)
                    ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Gate_SpinUpBusy");
            }

            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (network == null || network.HasStateFault || campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            PortalConnectionRecord edge = network.Find(connectionId);
            if (edge == null || edge.Kind != PortalConnectionKind.Laboratory || edge.First == null ||
                edge.First.Anchor != parent || edge.BranchId != campaign.BranchId)
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }

            // The readiness the ramp will be held by. Checked now so the refusal names the
            // real cause while nothing has been spent, rather than after a crew has worked.
            CompanyActionResult ready = CheckStationReadiness(assignedOperator);
            if (!ready.Success) { return ready; }
            if (!calibrated) { return CompanyActionResult.Refused("RR_Gate_NotCalibrated"); }
            if (HasUnresolvedNativeTrip()) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }

            spinUpConnectionId = connectionId;
            spinUpCoordinateId = edge.CoordinateId;
            spinUpWorkRequired = SpinUpWorkRequiredFor(edge.CoordinateId);
            spinUpWorkDone = 0f;
            spinUpHeldAtFull = false;
            Messages.Message("RR_Gate_SpinUpStarted".Translate(edge.CoordinateId), parent,
                MessageTypeDefOf.TaskCompletion, false);
            RecordGateActivity("RR_Event_GateSpinUpStarted", connectionId,
                spinUpWorkRequired.ToString("F0", System.Globalization.CultureInfo.InvariantCulture));
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Dial a remembered address: establish the connection for that coordinate, then ramp
        /// toward opening it. One action, because *"the specific addresss should be connected
        /// and the gate opened"* is one intention.
        ///
        /// Registration is idempotent -- an address already remembered is simply found again
        /// -- so a dial that fails at the ramp leaves nothing half-done behind it.
        /// </summary>
        public CompanyActionResult DialRememberedAddress(GateHistoryEntry entry)
        {
            if (entry == null || string.IsNullOrEmpty(entry.coordinateId))
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }

            // A history entry can outlive its coordinate: the gate remembers dialling
            // somewhere the branch no longer holds. Say so plainly instead of refusing with a
            // generic state error the player cannot act on.
            CoordinateRecord coordinate = null;
            IReadOnlyList<CoordinateRecord> coordinates = campaign.Coordinates;
            for (int index = 0; index < coordinates.Count; index++)
            {
                CoordinateRecord record = coordinates[index];
                if (record != null && string.Equals(record.Id, entry.coordinateId, StringComparison.Ordinal))
                { coordinate = record; break; }
            }
            if (coordinate == null) { return CompanyActionResult.Refused("RR_GateHistory_CoordinateGone"); }

            string connectionId;
            CompanyActionResult registered =
                PortalAddressService.RegisterLaboratoryAddress(this, coordinate, out connectionId);
            if (!registered.Success || string.IsNullOrEmpty(connectionId)) { return registered; }
            return BeginSpinUp(connectionId);
        }

        /// <summary>Stops a ramp at the player's request; the address stays remembered.</summary>
        public CompanyActionResult AbortSpinUp()
        {
            if (!IsSpinningUp) { return CompanyActionResult.Existing(); }
            string connectionId = spinUpConnectionId;
            ClearSpinUpState();
            RecordGateActivity("RR_Event_GateSpinUpAborted", connectionId);
            Messages.Message("RR_Gate_SpinUpAborted".Translate(), parent, MessageTypeDefOf.TaskCompletion, false);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// One tick of the ramp. Climbs while held, bleeds while not, and opens the
        /// connection the moment the work is done and the machine will take it.
        /// </summary>
        private void TickSpinUp()
        {
            if (string.IsNullOrEmpty(spinUpConnectionId)) { return; }
            if (IsOpening)
            {
                // Something else opened this gate underneath the ramp. The ramp has no
                // meaning any more and is dropped silently rather than competing with it.
                ClearSpinUpState();
                return;
            }
            if (spinUpWorkRequired <= 0f) { ClearSpinUpState(); return; }

            if (SpinUpIsSupported)
            {
                float rate = assignedOperator == null
                    ? DefaultSpinUpRate : assignedOperator.GetStatValue(StatDefOf.ResearchSpeed);
                if (!(rate > 0f) || float.IsNaN(rate)) { rate = DefaultSpinUpRate; }
                spinUpObservedRate = rate;
                spinUpWorkDone = Mathf.Min(spinUpWorkRequired, spinUpWorkDone + rate);
            }
            else
            {
                // Tied to the rate this ramp was actually climbing at, so it is always slower
                // than the crew that built it. A flat rate here would bleed a low-skill
                // operator's ramp faster than they could raise it.
                spinUpWorkDone -= spinUpObservedRate * GateProps.dialSpinUpDecayFraction;
                spinUpHeldAtFull = false;
                if (spinUpWorkDone <= 0f)
                {
                    string lapsed = spinUpConnectionId;
                    ClearSpinUpState();
                    Messages.Message("RR_Gate_SpinUpLapsed".Translate(), parent, MessageTypeDefOf.NegativeEvent, false);
                    RecordGateActivity("RR_Event_GateSpinUpLapsed", lapsed);
                    Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
                }
                return;
            }

            if (spinUpWorkDone < spinUpWorkRequired) { return; }

            CompanyActionResult opened = BeginPortalOpening(spinUpConnectionId);
            if (opened.Success)
            {
                string connectionId = spinUpConnectionId;
                ClearSpinUpState();
                Messages.Message("RR_Gate_SpinUpComplete".Translate(), parent, MessageTypeDefOf.TaskCompletion, false);
                RecordGateActivity("RR_Event_GateSpinUpCompleted", connectionId);
                return;
            }

            // Finished the work, and the machine still will not take it -- stored energy
            // below the opening threshold is the ordinary case. The ramp is **held**, not
            // thrown away, so a charged gate opens by itself the moment the reserve recovers.
            // It still bleeds if the crew walks away, so a held ramp is not a free one.
            if (!spinUpHeldAtFull)
            {
                spinUpHeldAtFull = true;
                if (!string.IsNullOrWhiteSpace(opened.MessageKey))
                { Messages.Message("RR_Gate_SpinUpWaiting".Translate(opened.MessageKey.Translate()), parent,
                    MessageTypeDefOf.SilentInput, false); }
            }
        }

        /// <summary>The inspect line for a running ramp, in the same shape as a build in progress.</summary>
        internal string SpinUpReadout()
        {
            if (!IsSpinningUp) { return null; }
            string target = string.IsNullOrEmpty(spinUpCoordinateId) ? spinUpConnectionId : spinUpCoordinateId;
            if (spinUpHeldAtFull) { return "RR_Gate_SpinUpHeldReadout".Translate(target).ToString(); }
            return "RR_Gate_SpinUpReadout".Translate(target, spinUpWorkDone.ToString("F0"),
                spinUpWorkRequired.ToString("F0"),
                SpinUpIsSupported ? "RR_Gate_SpinUpClimbing".Translate() : "RR_Gate_SpinUpBleeding".Translate())
                .ToString();
        }
    }
}
