using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Gate
{
    public sealed class CompProperties_RimroomsGate : CompProperties
    {
        /// <summary>
        /// The historical expedition window. Unchanged, and deliberately so: legacy
        /// expeditions still run on it and their behaviour is never altered. Portal
        /// sessions do not use this value at all.
        /// </summary>
        public int openingWindowTicks = 833;

        /// <summary>
        /// A first laboratory opening, in ticks. 108,000 ticks is about thirty real
        /// minutes at normal speed, which is roughly 1.8 in-game days — long enough to
        /// actually cross, find something, and carry it home several times over. The
        /// value it replaces for portal sessions was 833 ticks, about fourteen real
        /// seconds, which could not support a single round trip.
        /// </summary>
        public int portalBaseWindowTicks = 108000;

        /// <summary>
        /// How much longer each earned tier holds the connection open. Multiplicative,
        /// so advancement increases duration sharply rather than incrementally.
        /// </summary>
        public float portalWindowMultiplierPerTier = 3f;

        /// <summary>
        /// The ladder, in order. One rung per tier: the company projects that each raise the
        /// duration tier by one.
        ///
        /// This is content. As the research tree lands, its projects are appended here and the
        /// ladder grows without a code change. **Completion is what counts, not spendable
        /// insight**, so a tier can never be lost by spending currency.
        ///
        /// This held a single name until 0.10.9-dev while <see cref="portalIndefiniteTier"/> was
        /// 4, so the tier could never exceed 1 and a standing connection was unreachable however
        /// a branch played. Four rungs declared and one built, and no checker could see it
        /// because every individual value was valid.
        /// </summary>
        public List<string> portalWindowTierProjects = new List<string>
        {
            "RR_GateTelemetry",
            "RR_GateFieldStability",
            "RR_GateSustainedAperture",
            "RR_GateStandingConnection",
        };

        /// <summary>
        /// The tier at which a supported opening stops counting down entirely. At and
        /// above it the connection is held for as long as the machine is powered,
        /// staffed and fed; losing any of those still ends it exactly as before.
        /// </summary>
        public int portalIndefiniteTier = 4;
        /// <summary>
        /// How long the emergency return window runs. **RR_Cap_ReturnDrill** (Fieldcraft and
        /// medicine, tier 0) lengthens it — a drilled crew gets back through faster, which is the
        /// same thing as having longer.
        /// </summary>
        public int emergencyReturnWindowTicks = 300;
        public int stablePowerTicksRequired = 60;
        public float minimumPowerHeadroomWatts = 250f;
        public float idlePowerDrawWatts = 250f;
        public float openingPowerDrawWatts = 3500f;
        /// <summary>
        /// How fast the gate tops its bound battery up, in watts.
        ///
        /// **Restored and wired in 0.11.5-dev.** It was retired one checkpoint earlier for being
        /// unread, which was the wrong call: owner direction, 2026-09-29, verbatim — *"make sure
        /// shit isnt unused it was put there for a reason"*. A value nobody wired is a job nobody
        /// finished, not a value nobody wanted.
        /// </summary>
        public float reserveChargePowerWatts = 1000f;

        /// <summary>
        /// The smallest battery a gate will accept as its reserve, in watt-days.
        ///
        /// **Restored and wired in 0.11.5-dev**, for the same reason. It is now what it always
        /// read like: a minimum, checked when a battery is bound, so a gate cannot be backed by a
        /// battery too small to hold an emergency return.
        /// </summary>
        public float returnReserveCapacityWattDays = 2f;
        public float emergencyReturnCostWattDays = 1f;
        public float recoveryOpeningCostWattDays = 1f;
        public float calibrationWorkRequired = 2500f;

        /// <summary>
        /// The work one opening costs before familiarity, at a base working speed. Deliberately
        /// less than a calibration, which happens once in a gate's life, because this happens
        /// every time a connection is brought up.
        /// </summary>
        public float dialSpinUpWorkRequired = 1800f;

        /// <summary>
        /// What each previous connection to the same address multiplies the required work by.
        /// A route the crew has run before comes up faster; somewhere they have never been
        /// takes the full ramp.
        /// </summary>
        public float dialSpinUpFamiliarityFactor = 0.85f;

        /// <summary>
        /// The floor familiarity may never take the ramp below, as a fraction of the base. A
        /// gate that opens instantly is a gate with no operating crew, which is the one thing
        /// the ramp exists to prevent.
        /// </summary>
        public float dialSpinUpFloorFraction = 0.25f;

        /// <summary>
        /// How fast an unheld ramp bleeds back down, **as a fraction of the rate it was
        /// actually climbing at**.
        ///
        /// Deliberately not a flat number per tick. A flat rate was written first and an
        /// offline proof rejected it: RimWorld's research speed at low Intellectual is well
        /// under one, so a fixed 0.5 would have bled a poor technician's ramp **faster than
        /// they could build it**, making a slow operator's gate impossible to bring up rather
        /// than merely slow. Expressed as a fraction of the observed climb rate, "decay is
        /// slower than progress" is true for every possible operator by construction instead
        /// of by luck.
        /// </summary>
        public float dialSpinUpDecayFraction = 0.5f;

        public CompProperties_RimroomsGate()
        {
            compClass = typeof(CompRimroomsGate);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
            if ((parentDef.defName == "Door" || parentDef.defName == "Autodoor") &&
                !typeof(Building_Door).IsAssignableFrom(parentDef.thingClass))
            { yield return "Native Rimrooms gate provider supports only Core Door and Autodoor."; }
            if (openingWindowTicks <= 0 || emergencyReturnWindowTicks <= 0 || stablePowerTicksRequired < 0)
            { yield return "Rimrooms gate timing settings must be positive."; }
            if (portalBaseWindowTicks <= 0 || portalIndefiniteTier < 0 ||
                !PositiveFinite(portalWindowMultiplierPerTier) || portalWindowMultiplierPerTier < 1f ||
                portalWindowTierProjects == null ||
                portalWindowTierProjects.Any(name => string.IsNullOrWhiteSpace(name)))
            { yield return "Rimrooms portal duration ladder must be positive, non-shrinking and fully named."; }
            // The retired clause compared the two costs against a nominal reserve size that
            // had no relationship to the battery a player actually binds, so it guaranteed
            // nothing. The real guarantee is in SpendNativeOpeningTick, which checks the
            // actual stored energy of the actual battery every tick.
            if (!PositiveFinite(minimumPowerHeadroomWatts) || !PositiveFinite(idlePowerDrawWatts) ||
                !PositiveFinite(openingPowerDrawWatts) || !PositiveFinite(emergencyReturnCostWattDays) ||
                !PositiveFinite(recoveryOpeningCostWattDays) ||
                !PositiveFinite(calibrationWorkRequired))
            { yield return "Rimrooms gate power, reserve, and work settings must be finite and positive."; }
            if (!PositiveFinite(dialSpinUpWorkRequired) ||
                !PositiveFinite(dialSpinUpDecayFraction) || dialSpinUpDecayFraction > 1f ||
                !PositiveFinite(dialSpinUpFamiliarityFactor) || dialSpinUpFamiliarityFactor > 1f ||
                !PositiveFinite(dialSpinUpFloorFraction) || dialSpinUpFloorFraction > 1f)
            {
                // Every one of these is a silent design inversion rather than a crash, which is
                // why they are refused at load. A familiarity factor above one makes a
                // well-travelled route slower than a new one; a floor above one makes every ramp
                // longer than its own base; and a decay fraction above one bleeds a ramp faster
                // than any crew can build it, which turns a slow operator's gate from slow into
                // impossible.
                yield return "Rimrooms gate spin-up settings must be positive, and the familiarity factor, floor fraction and decay fraction must not exceed one.";
            }
        }

        private static bool PositiveFinite(float value)
        {
            return value > 0f && !float.IsNaN(value) && !float.IsInfinity(value);
        }
    }

    /// <summary>Persistent gate assembly, operator, power reserve, and opening-window state.</summary>
    public sealed partial class CompRimroomsGate : ThingComp
    {
        private Pawn assignedOperator;
        /// <summary>
        /// How long an operator stays before their own body wins. **Per gate rather than
        /// global**, because a branch running a quiet survey and a branch holding a deep
        /// coordinate open are not the same decision, and the owner's words name it as a
        /// property of the post: *"stay at post strict mild, default"*.
        ///
        /// Defaults to <see cref="GateWatchPosture.Balanced"/> because the owner named
        /// that one the default: *"default&gt; inbetween strict and mild"*. **An existing
        /// save without the field loads as Balanced**, which is the enum's zero-adjacent
        /// value by intent -- `Mild` is 0, so the default is written explicitly rather
        /// than inherited from a zeroed field.
        /// </summary>
        private GateWatchPosture watchPosture = GateWatchPosture.Balanced;
        private bool assemblyComplete;
        private bool calibrated;
        private string activeExpeditionId;
        private int openingTicksRemaining;
        private int emergencyReturnTicksRemaining;
        private bool emergencyReturnSpent;
        private bool warnedHalfWindow;
        private bool warnedQuarterWindow;
        private bool warnedTenthWindow;
        private string failureKey;
        private int stablePowerTicks;
        private string lastClosedExpeditionId;
        private List<GateWindowSpendReceipt> openingSpendReceipts = new List<GateWindowSpendReceipt>();
        private List<GateRecoveryReceipt> recoveryReceipts = new List<GateRecoveryReceipt>();
        private CompPowerTrader powerTrader;

        private CompProperties_RimroomsGate GateProps { get { return (CompProperties_RimroomsGate)props; } }
        public Pawn AssignedOperator { get { return assignedOperator; } }
        public GateWatchPosture WatchPosture { get { return watchPosture; } }
        public bool AssemblyComplete { get { return assemblyComplete; } }
        public bool Calibrated { get { return calibrated; } }
        public bool IsOpening { get { return !string.IsNullOrEmpty(activeExpeditionId) || !string.IsNullOrEmpty(portalOpeningId); } }
        public string ActiveExpeditionId { get { return activeExpeditionId; } }
        public int OpeningTicksRemaining { get { return openingTicksRemaining; } }
        public int EmergencyReturnTicksRemaining { get { return emergencyReturnTicksRemaining; } }
        public bool EmergencyReturnSpentForActiveExpedition { get { return emergencyReturnSpent; } }
        public bool IsEmergency { get { return IsOpening && !string.IsNullOrEmpty(failureKey); } }
        public string FailureKey { get { return failureKey; } }
        public float ReturnReserveStoredWattDays { get { return NativeStoredEnergy; } }
        public float ReturnReserveCapacityWattDays { get { return NativeBatteryCapacity; } }
        public float RecoveryOpeningCostWattDays { get { return GateProps.recoveryOpeningCostWattDays; } }
        public float EmergencyReturnCostWattDays { get { return GateProps.emergencyReturnCostWattDays; } }
        // The crew planner's cost preview wants the opening draw in watts, and `GateFootprint`
        // already exposes `OpeningPowerDrawWatts` -- footprint-scaled and discounted by
        // RR_Cap_EfficientAperture. A second accessor reading the raw prop was written here and
        // the compiler refused it, which was the right answer: the raw prop is not what a gate
        // actually draws, so a preview built on it would have quoted the wrong number for every
        // gate bigger than 1x1.
        /// <summary>
        /// Headroom a gate needs above its draw before it will open.
        ///
        /// **RR_Cap_ReserveDiscipline** (Facilities and power, tier 0) lowers it: a branch that has
        /// studied its own reserve knows how close to the line it can safely run.
        /// </summary>
        public float MinimumPowerHeadroomWatts
        {
            get
            {
                float required = GateProps.minimumPowerHeadroomWatts;
                Company.RimroomsCampaignComponent campaign = NativeCampaign;
                if (campaign != null && campaign.HasCapability("RR_Cap_ReserveDiscipline"))
                { required *= 0.6f; }
                return required;
            }
        }
        /// <summary>
        /// What the gate is drawing right now.
        ///
        /// **`idlePowerDrawWatts` wired in 0.11.5-dev.** A designated gate used to draw exactly
        /// nothing unless a connection was open, which made the prop a job nobody finished rather
        /// than a value nobody wanted — owner direction, verbatim: *"make sure shit isnt unused it
        /// was put there for a reason"*.
        ///
        /// A designated gate is a machine that is **on**: it holds its calibration, keeps its
        /// address book live and tops up its reserve. That costs something. An undesignated door
        /// is still just a door and draws nothing, which is the same dormant-until-designated rule
        /// every other part of this component follows.
        ///
        /// Scaled by footprint like the opening draw, because a bigger gate is more machine to
        /// keep warm.
        /// </summary>
        public float CurrentPowerDrawWatts
        {
            get
            {
                if (IsOpening && !IsEmergency) { return OpeningPowerDrawWatts; }
                if (!IsDesignated) { return 0f; }
                return IdlePowerDrawWatts;
            }
        }

        /// <summary>
        /// What a designated gate costs to keep while it is closed, after research.
        ///
        /// **RR_Cap_StandbyDiscipline** (Facilities and power, tier 2) halves it. A branch that
        /// has worked out which of the standby systems actually have to stay warm between
        /// connections stops paying for the ones that do not.
        ///
        /// **This property exists so there is exactly one answer to the question.** The idle
        /// draw is read in two places -- here, for what the gate reports it is drawing, and in
        /// <see cref="SpendIdleDrawTick"/>, for what it actually takes out of the reserve. A
        /// capability applied to one and not the other would make the readout lie about the
        /// drain, and the two would drift apart silently because nothing compares them.
        /// </summary>
        public float IdlePowerDrawWatts
        {
            get
            {
                float draw = GateProps.idlePowerDrawWatts * GateCellCount;
                Company.RimroomsCampaignComponent idleCampaign = NativeCampaign;
                if (idleCampaign != null && idleCampaign.HasCapability("RR_Cap_StandbyDiscipline"))
                { draw *= 0.5f; }
                return draw;
            }
        }
        public IntVec3 GateEntryCell { get { return NativeEntryCell; } }

        /// <summary>
        /// The work calibrating an assembly costs.
        ///
        /// **RR_Cap_ReferenceStandards** (Measurement and evidence, tier 2) takes two fifths off.
        /// A branch holding its own reference standards is not deriving them again from scratch
        /// every time it calibrates, which is the tier 2 band exactly: the second time you do a
        /// thing should be cheaper than the first.
        /// </summary>
        public float CalibrationWorkRequired
        {
            get
            {
                float required = GateProps.calibrationWorkRequired;
                Company.RimroomsCampaignComponent calibrationCampaign = NativeCampaign;
                if (calibrationCampaign != null && calibrationCampaign.HasCapability("RR_Cap_ReferenceStandards"))
                { required *= 0.6f; }
                return required;
            }
        }
        public Thing Console { get { return FindConsole(); } }
        public bool IsAwaitingRecovery { get { return IsOpening && IsEmergency && emergencyReturnTicksRemaining <= 0; } }

        /// <summary>
        /// Whether anybody qualified is holding this gate's window.
        ///
        /// **THIS WAS A PAWN QUESTION AND IS NOW A STATION QUESTION, AND THE CHANGE IS MADE HERE
        /// RATHER THAN AT SIX CALL SITES.** It used to resolve `FindConsole()` and ask whether
        /// `assignedOperator` -- one named colonist -- was standing on that one cell running
        /// `RR_OperateGate`. Owner, 2026-10-06: *"he can leave when another pawn hops on the other
        /// comms console toggled to gate contrtrols"*.
        ///
        /// Every clause of the old test survives inside `QualifiedToStaff` and `StaffingStation`;
        /// only the identity clause is gone. **So a pawn who could hold the window before still
        /// can, and nobody new slipped in.**
        ///
        /// **Six places asked this and every one of them meant *is the window being held*:**
        /// spin-up support, the startup checklist step, the console progress bar, the Operations
        /// refusal, the send-to-station action and the open-connection precondition. Redefining the
        /// property corrects all six in one derivation. `GateSpinUp.SpinUpIsSupported` is the
        /// clearest case and says so in its own words -- *"the same set of conditions a live opening
        /// is held by, on purpose: bringing a connection up cannot require less than keeping one
        /// up"* -- so a relief operator who could hold a connection but not ramp one would have been
        /// a contradiction the file had already ruled out.
        ///
        /// **The emergency test does NOT read this.** It reads `TickOperatorRelief()`, which counts
        /// how long the chair has been empty, because a hand-off that drops the window for one tick
        /// is not a hand-off.
        /// </summary>
        public bool IsOperatorOnStation { get { return AnyOperatorOnStation; } }

        public override void PostExposeData()
        {
            base.PostExposeData();
            ExposeGateRun();
            ExposeConnectionHistory();
            ExposeSpinUp();
            Scribe_References.Look(ref assignedOperator, "rr_gateAssignedOperator");
            ExposeOperatorRelief();
            // Additive, and the default is written out rather than left to a zeroed
            // field: `Mild` is enum 0, so an absent value must resolve to Balanced.
            Scribe_Values.Look(ref watchPosture, "rr_gateWatchPosture", GateWatchPosture.Balanced);
            Scribe_Values.Look(ref assemblyComplete, "rr_gateAssemblyComplete", false);
            Scribe_Values.Look(ref calibrated, "rr_gateCalibrated", false);
            Scribe_Values.Look(ref activeExpeditionId, "rr_gateActiveExpeditionId");
            ExposePortalOpening();
            Scribe_Values.Look(ref openingTicksRemaining, "rr_gateOpeningTicksRemaining", 0);
            Scribe_Values.Look(ref emergencyReturnTicksRemaining, "rr_gateEmergencyReturnTicksRemaining", 0);
            Scribe_Values.Look(ref emergencyReturnSpent, "rr_gateEmergencyReturnSpent", false);
            ExposeKillSwitch();
            ExposeServicing();
            ExposeStandingRecall();
            Scribe_Values.Look(ref warnedHalfWindow, "rr_gateWarnedHalfWindow", false);
            Scribe_Values.Look(ref warnedQuarterWindow, "rr_gateWarnedQuarterWindow", false);
            Scribe_Values.Look(ref warnedTenthWindow, "rr_gateWarnedTenthWindow", false);
            Scribe_Values.Look(ref failureKey, "rr_gateFailureKey");
            Scribe_Values.Look(ref stablePowerTicks, "rr_gateStablePowerTicks", 0);
            Scribe_Values.Look(ref lastClosedExpeditionId, "rr_gateLastClosedExpeditionId");
            Scribe_Collections.Look(ref openingSpendReceipts, "rr_gateOpeningSpendReceipts", LookMode.Deep);
            Scribe_Collections.Look(ref recoveryReceipts, "rr_gateRecoveryReceipts", LookMode.Deep);
            ExposeNativeBinding();
            ExposeEquipmentLinks();
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (openingSpendReceipts == null) { openingSpendReceipts = new List<GateWindowSpendReceipt>(); }
                if (recoveryReceipts == null) { recoveryReceipts = new List<GateRecoveryReceipt>(); }
                openingSpendReceipts.RemoveAll(receipt => receipt == null || string.IsNullOrWhiteSpace(receipt.OperationId));
                recoveryReceipts.RemoveAll(receipt => receipt == null || string.IsNullOrWhiteSpace(receipt.OperationId));
                openingTicksRemaining = Math.Max(0, openingTicksRemaining);
                emergencyReturnTicksRemaining = Math.Max(0, emergencyReturnTicksRemaining);
                stablePowerTicks = Math.Max(0, stablePowerTicks);
                ValidatePortalOpeningOwner();
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            powerTrader = parent.GetComp<CompPowerTrader>();
        }

        public override void CompTick()
        {
            using (Core.RimroomsDiagnostics.Measure("gate-tick")) { TickGate(); }
        }

        private void TickGate()
        {
            base.CompTick();
            if (!parent.Spawned || portalOwnerFault) { return; }
            if (!BeginNativeTick()) { return; }
            Presentation.NativePortalPresentation.Tick(this);

            TickServicing();
            if (HasPowerAndHeadroom())
            {
                if (stablePowerTicks < int.MaxValue) { stablePowerTicks++; }
            }
            else { stablePowerTicks = 0; }

            // Before the opening block, because a ramp only exists while the gate is closed and
            // its completion is what opens one.
            TickSpinUp();
            Threats.GateIncursion.Tick(this);
            // **The other direction, on owner direction 2026-10-06.** Incursion is something following
            // your crew home; this is something on your map walking out through the open gate.
            // Separate because they are not symmetric: inbound keeps all five of its fairness bounds
            // and outbound is bounded by motive and by the doorstep instead. See GateEgress.
            Threats.GateEgress.Tick(this);
            // Row 725's repair half. A gate read no damage at all before this: it could
            // be shot to twelve per cent and still hold a connection perfectly.
            TickIntegrity();

            // **THE COMPANY PAYS FOR EACH GOAL REACHED.** Owner: *"full totorieal quest line
            // payouts on each successful step(the company rewards getting to the goals)"*. Checked
            // here rather than at each place a step can be satisfied, because there are eleven of
            // those and the whole point is that one list decides. Rate-limited: resolving eleven
            // keyed labels every tick for every gate would be real cost for an answer that
            // changes a handful of times in a campaign.
            if (GateStartupPayouts.ShouldCheck(parent)) { GateStartupPayouts.Pay(this); }

            if (!IsOpening) { return; }
            if (string.IsNullOrEmpty(failureKey))
            {
                // Checked before the generic power test on purpose. A thrown switch will cut
                // the supply a tick later anyway, but then the cause recorded would be
                // "power lost" — indistinguishable from a snapped conduit. Somebody threw
                // this, and the log and the readout should say so.
                if (KillSwitchThrown) { EnterEmergency("RR_NativeGate_KillSwitchThrown"); }
                else if (!HasPowerAndHeadroom()) { EnterEmergency("RR_Gate_PowerLost"); }
                // **A STATION QUESTION, AND COUNTED RATHER THAN REACTED TO.** This read
                // `!IsOperatorOnStation`, which asked whether one named colonist was standing on
                // one bound console's cell -- so a window was hostage to that person's bladder and
                // a hand-off was impossible. `TickOperatorRelief` asks whether ANY qualified pawn
                // is at ANY bound console, and only reports a loss once the chair has been empty
                // for longer than `ReliefGraceTicks`. The grace is the feature: if the window
                // dropped for a single tick while one pawn stood up and another sat down, relief
                // would arrive into an emergency it caused.
                else if (TickOperatorRelief()) { EnterEmergency("RR_Gate_OperatorLost"); }
                else if (IsSustainedPortalSession)
                {
                    // Held, not counted down. The energy is still spent every tick, so
                    // running the supply dry ends the session exactly as losing power
                    // does — which is what makes "indefinite" mean "while supported"
                    // rather than "free".
                    if (!SpendNativeOpeningTick())
                    {
                        EnterEmergency(HasNativeEnergyDebitFault
                            ? "RR_NativeGate_EnergyDebitFault" : "RR_NativeGate_OpeningEnergyLow");
                    }
                }
                else if (openingTicksRemaining > 0)
                {
                    if (!SpendNativeOpeningTick())
                    { EnterEmergency(HasNativeEnergyDebitFault ? "RR_NativeGate_EnergyDebitFault" : "RR_NativeGate_OpeningEnergyLow"); return; }
                    openingTicksRemaining--;
                    SendOpeningWindowWarnings();
                    if (openingTicksRemaining <= 0) { EnterEmergency("RR_Gate_WindowExpired"); }
                }
            }
            else if (emergencyReturnTicksRemaining > 0)
            {
                emergencyReturnTicksRemaining--;
                if (emergencyReturnTicksRemaining <= 0)
                {
                    failureKey = "RR_Gate_EmergencyWindowExpired";
                    RecordGateActivity(failureKey, CurrentOpeningId);
                }
            }
        }

        /// <summary>
        /// The watch-posture dropdown, offered wherever an operator can be assigned.
        ///
        /// **A `FloatMenu` rather than three buttons or a cycling one.** The owner asked for *"a
        /// driop down sleector thing"*, and a cycling button hides the options it is not showing --
        /// a player has to click it to find out what else exists. Three gizmos would spend three
        /// slots on one decision.
        ///
        /// Every option states what it does in its own description, because the difference between
        /// these three is exactly the thing a player cannot guess, and getting it wrong once cost
        /// a colonist.
        /// </summary>
        private Gizmo WatchPostureGizmo()
        {
            return new Command_Action
            {
                defaultLabel = "RR_GateWatch_Label".Translate(
                    GateWatch.LabelKey(watchPosture).Translate()),
                defaultDesc = "RR_GateWatch_Desc".Translate(
                    GateWatch.DescriptionKey(watchPosture).Translate()),
                icon = parent.def.uiIcon,
                action = delegate
                {
                    var options = new List<FloatMenuOption>();
                    foreach (GateWatchPosture choice in new[]
                    {
                        GateWatchPosture.Mild, GateWatchPosture.Balanced, GateWatchPosture.Strict,
                    })
                    {
                        GateWatchPosture picked = choice;
                        options.Add(new FloatMenuOption(
                            GateWatch.LabelKey(picked).Translate() + " - "
                                + GateWatch.DescriptionKey(picked).Translate(),
                            delegate { watchPosture = picked; }));
                    }
                    Find.WindowStack.Add(new FloatMenu(options));
                },
            };
        }

        /// <summary>
        /// Turn this door into a machine gate, with the branch's own equipment.
        ///
        /// Offered only on a door at the headquarters, because `BindNativeInfrastructure` requires
        /// every provider to stand there and a button that can only refuse is worse than no
        /// button.
        ///
        /// **Nothing is decided here.** The binding applies every rule it always did -- the exact
        /// provider defs, the reserve size, the entry cell, the branch -- and this only answers
        /// *which* console, battery and bench, and only when there is exactly one of each. That
        /// is every start this mod ships, so the owner's *"basic components there and connected
        /// just waiting to be switched on"* is a single click; anything ambiguous is named and
        /// chosen in the Operations pane, because picking one of several for the player is a
        /// decision rather than a shortcut.
        /// </summary>
        private IEnumerable<Gizmo> MakeGateGizmos()
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign == null || !campaign.CanOperate || parent.Map == null
                || campaign.Headquarters != parent.Map)
            { yield break; }
            if (!NativeDoorProvider()) { yield break; }

            yield return new Command_Action
            {
                defaultLabel = "RR_NativeGate_MakeLabel".Translate(),
                defaultDesc = "RR_NativeGate_MakeDesc".Translate(),
                icon = parent.def.uiIcon,
                action = delegate
                {
                    // **WHICH DOOR IS THE GATE IS SETTABLE ON ITS OWN, FIRST.** Owner, 2026-10-03:
                    // *"i should be able to set the gate on a door first, so idk why its tellign
                    // me i cant set the gate door without setting the batteries first"*.
                    //
                    // This button used to resolve all three providers and **refuse outright** if
                    // any was absent or ambiguous -- `SoleCandidate` returns null for *none* and
                    // for *more than one* -- so on the company start, where no battery is bound
                    // yet, the only route from a door to a gate said `RR_NativeGate_NoSingleBattery`
                    // and stopped. **A refusal is not a route**, and the owner read it as the
                    // answer rather than as a detour.
                    //
                    // So the designation happens first and on its own. Only then is the circuit
                    // bound, and only when all three resolve unambiguously -- picking one of
                    // several for the player is still a decision rather than a shortcut, which is
                    // what this method's docstring has always said.
                    CompanyActionResult designated = DesignateAsGate();
                    if (!designated.Success) { ShowOrderResult(designated); return; }

                    Thing console = UI.MainTabWindow_Operations.SoleCandidate(
                        UI.MainTabWindow_Operations.AvailableNativeConsoles(campaign));
                    Thing battery = UI.MainTabWindow_Operations.SoleCandidate(
                        UI.MainTabWindow_Operations.AvailableNativeBatteries(campaign));
                    Thing bench = UI.MainTabWindow_Operations.SoleCandidate(
                        UI.MainTabWindow_Operations.AvailableNativeAssemblyBenches(campaign));
                    if (console == null || battery == null || bench == null)
                    {
                        // **Told, not refused.** The door IS the gate now; what is missing is the
                        // circuit, and the player needs to know which piece and where to finish.
                        // Named rather than generic for the same reason as before: "it did nothing"
                        // tells them neither.
                        Messages.Message("RR_NativeGate_DesignatedNeedsCircuit".Translate(
                                (console == null ? "RR_NativeGate_NoSingleConsole"
                                : battery == null ? "RR_NativeGate_NoSingleBattery"
                                : "RR_NativeGate_ChooseBench").Translate()),
                            parent, MessageTypeDefOf.TaskCompletion, false);
                        return;
                    }
                    // The fourth argument is the entry side, which defaults to the near side.
                    // The Operations pane is where a player chooses the far side deliberately.
                    ShowOrderResult(BindNativeInfrastructure(console, battery, bench));
                }
            };
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            if (parent.Faction != Faction.OfPlayer) { yield break; }
            // **THE TOGGLE, ON THE DOOR.** Owner: *"i have no idea how the gate is suppose to
            // work as there doesnt be a toggle option to turn it from a normal door to a machine
            // gate door"*. This method used to yield break here for any undesignated door, so
            // **an ordinary door offered nothing at all** and the only route from a door to a
            // gate was a provider-picking pane in the Operations tab -- which the company's
            // state fault was also refusing. There was no route a player would find.
            if (!IsDesignated)
            {
                foreach (Gizmo gizmo in MakeGateGizmos()) { yield return gizmo; }
            }
            if (AssemblyComplete)
            {
                // Shown once the gate is a gate at all. Before that there is no post to
                // stand at and the control would be a setting for nothing.
                yield return WatchPostureGizmo();
                yield break;
            }

            yield return new Command_Action
            {
                defaultLabel = "RR_GateHistory_Label".Translate(ConnectionHistory.Count.ToString()),
                defaultDesc = "RR_GateHistory_Desc".Translate(),
                icon = parent.def.uiIcon,
                action = OpenConnectionHistoryMenu
            };

            // **DIAL SOMEWHERE NOBODY ASKED FOR, FROM THE GATE.** Owner, 2026-10-04: *"we need a
            // Random address option not just company requested task and quests at specific
            // xcorrdinates"*, and in the same message *"everything that the machine needs to
            // start up should be able to do in the worlkd from the devices themselfes with pawns
            // controls and actrions not just in the opetaions tab"*.
            //
            // Every coordinate until now arrived because something named it -- a request, a
            // quest, a contract, or a doorway somebody walked into. This is the player deciding
            // to go and look. It creates an **address**, not a map: nothing is generated until
            // somebody crosses, which is why dialling is free and the open-map budget is only
            // spent when the place is actually opened.
            if (NativeCampaign != null && NativeCampaign.CanOperate)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Dial_RandomLabel".Translate(),
                    defaultDesc = "RR_Dial_RandomDesc".Translate(
                        Portals.PortalRandomDial.DeepestBlindDial.ToString()),
                    icon = parent.def.uiIcon,
                    action = delegate
                    {
                        Company.CoordinateRecord dialled;
                        CompanyActionResult result =
                            Portals.PortalRandomDial.Dial(NativeCampaign, out dialled);
                        if (result.Success && dialled != null)
                        {
                            Messages.Message("RR_Dial_RandomFound".Translate(
                                    dialled.AddressCode, dialled.Depth.ToString()),
                                parent, MessageTypeDefOf.PositiveEvent, false);
                            return;
                        }
                        ShowOrderResult(result);
                    }
                };
            }

            // **SETTING THE COORDINATE, AND OPENING IT, FROM THE DOOR.** Owner, 2026-10-04:
            // *"everything that the machine needs to start up should be able to do in the worlkd
            // from the devices themselfes with pawns controls and actrions not just in the
            // opetaions tab,, ie setting the cordinace and all of those things need  to show"*.
            // These were the last two start-up actions that existed only as panel buttons.
            foreach (Gizmo gizmo in AddressGizmos()) { yield return gizmo; }
            // The scheduling surface. On the gate rather than in Operations, because a standing
            // order about this gate's own window belongs on this gate.
            foreach (Gizmo gizmo in StandingRecallGizmos()) { yield return gizmo; }

            if (IsSpinningUp)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_AbortSpinUpLabel".Translate(),
                    defaultDesc = "RR_Gate_AbortSpinUpDesc".Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { ShowOrderResult(AbortSpinUp()); }
                };
            }

            // Ordering a crossing from the door itself, with the refusal named in place.
            foreach (Gizmo gizmo in Portals.DoorCrossingGizmo.For(parent)) { yield return gizmo; }

            yield return EquipmentLinkGizmo();

            // The run fallback. Shown only when there is a neighbour to take or a run to give
            // back, so a gate in the middle of a wall with nothing beside it gets no button that
            // could only refuse.
            if (RunDoorCount > 1 || AdjacentRunCandidates().Count > 0)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_GateRun_Label".Translate(RunDoorCount.ToString(),
                        GateWidth.ToString()),
                    defaultDesc = "RR_GateRun_Desc".Translate(),
                    icon = parent.def.uiIcon,
                    action = OpenGateRunMenu
                };
            }

            // Ending this opening now, without disabling the gate.
            //
            // NOT the same as the kill switch below it, which is a persistent thrown state that
            // has to be cleared before the next opening. A cutoff starts the emergency return
            // window and leaves the gate usable, which is what a player wants while watching a
            // crew get into trouble. It had no surface at all until the wiring checker found the
            // method with no caller, at 0.12.32-dev.
            if (IsOpening && !IsEmergency)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_CutoffLabel".Translate(),
                    defaultDesc = "RR_Gate_CutoffDesc".Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { ShowOrderResult(TriggerEmergencyCutoff()); }
                };
            }

            yield return new Command_Action
            {
                defaultLabel = "RR_Gate_KillSwitchLabel".Translate(),
                defaultDesc = "RR_Gate_KillSwitchDesc".Translate(),
                icon = parent.def.uiIcon,
                action = OpenKillSwitchMenu
            };

            yield return new Command_Action
            {
                defaultLabel = "RR_Gate_AssignOperatorLabel".Translate(),
                defaultDesc = "RR_Gate_AssignOperatorDesc".Translate(),
                icon = parent.def.uiIcon,
                action = OpenOperatorMenu
            };

            if (assignedOperator != null && AssemblyComplete && !Calibrated && !IsOpening)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_CalibrateLabel".Translate(),
                    defaultDesc = "RR_Gate_CalibrateDesc".Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { ShowOrderResult(OrderCalibration()); }
                };
            }

            if (assignedOperator != null && Calibrated && (!IsOpening || IsEmergency))
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_StaffConsoleLabel".Translate(),
                    defaultDesc = "RR_Gate_StaffConsoleDesc".Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { ShowOrderResult(OrderStaffConsole()); }
                };
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!IsDesignated) { return null; }
            string status = calibrated ? "RR_Gate_StatusCalibrated".Translate().ToString()
                : assemblyComplete ? "RR_Gate_StatusNeedsCalibration".Translate().ToString()
                : "RR_Gate_StatusIncomplete".Translate().ToString();
            // **THE READOUT ANSWERS THE QUESTION THE GATE NOW ASKS.** It used to say only whether
            // the one named operator was at the one console, which after relief landed would have
            // read "away" while somebody else was holding the window perfectly -- a stale readout
            // is the upstream of a player fixing something that is not broken.
            //
            // So: somebody is holding it, naming who; or the named operator is away and the chair
            // is empty; or nobody is assigned at all. The station count rides along whenever there
            // is more than one, because a player who built relief stations should be able to see
            // that the gate knows about them.
            Pawn holder = CurrentStationOperator;
            int stations = BoundConsoleCount;
            string operatorText = holder != null
                ? "RR_Gate_OperatorPresent".Translate(holder.LabelShortCap).ToString()
                : assignedOperator == null ? "RR_Gate_NoOperator".Translate().ToString()
                    : "RR_Gate_OperatorAway".Translate(assignedOperator.LabelShortCap).ToString();
            if (stations > 1)
            { operatorText += " " + "RR_Gate_ReliefStations".Translate(stations).ToString(); }
            string cutoffText = KillSwitchReadout();
            // Said only when the machine is not sound. A line reading "condition 100%" on every
            // gate forever is noise, and Core's own health bar already covers the ordinary case.
            string integrityText = IntegritySound ? null
                : "RR_Gate_IntegrityReadout".Translate(
                    IntegrityFraction.ToStringPercent("F0"),
                    IntegrityFloorFraction.ToStringPercent("F0")).ToString();
            string serviceText = ServicingReadout();
            // One readout. The legacy one computed here first was overwritten on every
            // single call before it could be shown.
            string powerText = "RR_NativeGate_PowerReadout".Translate(ReturnReserveStoredWattDays.ToString("F2"),
                ReturnReserveCapacityWattDays.ToString("F2"), CurrentPowerDrawWatts.ToString("F0"),
                NativeEnergyRequiredToOpenWattDays.ToString("F2"), RecoveryEnergyRequiredWattDays.ToString("F2")).ToString();
            // The breakdown, found by the live-effects sweep: `EmergencyReturnCostWattDays` and
            // `RecoveryOpeningCostWattDays` were public accessors read by NOTHING. The totals above
            // include them, so the player saw "this much to open and come home" without ever being
            // told how much of it was the coming home. That is the number that decides whether it
            // is safe to send anybody, so it is worth its own line.
            powerText += "\n" + "RR_NativeGate_ReserveBreakdown".Translate(
                EmergencyReturnCostWattDays.ToString("F2"),
                RecoveryOpeningCostWattDays.ToString("F2"));
            if (NativeBindingFailureKey != null) { powerText += "\n" + NativeBindingFailureKey.Translate(); }
            string active = IsOpening
                ? "RR_Gate_OpeningReadout".Translate(IsSustainedPortalSession
                        ? "RR_Gate_WindowSustained".Translate().ToString() : DescribeWindow(openingTicksRemaining),
                    DescribeWindow(emergencyReturnTicksRemaining), string.IsNullOrEmpty(failureKey) ? "RR_Gate_NoFailure".Translate() : failureKey.Translate()).ToString()
                : "";
            string ramp = SpinUpReadout();
            string links = EquipmentLinkReadout();
            string footprint = FootprintReadout();
            return string.Join("\n", new[] { NextStepReadout(), status, footprint, integrityText,
                    operatorText, cutoffText, serviceText, powerText, ramp, links, active,
                    StandingRecallReadout() }
                .Where(s => !string.IsNullOrEmpty(s)));
        }

        /// <summary>
        /// What to do next, said on the door.
        ///
        /// ## Owner direction, 2026-10-04, verbatim
        ///
        /// *"and when u set a door to be a gatew  that gate should tell you next step in the game
        /// world not just in the operations tab and machine tab"*
        ///
        /// ## Why it is first, and why it is one line
        ///
        /// **First**, because it is the only line on this card a player who is stuck needs. The
        /// card already carried ten readouts — condition, operator, kill switch, servicing, power
        /// reserve and its breakdown, the ramp, the equipment links, the live window — every one
        /// of them an answer to *"what is the state"* and not one of them an answer to *"what do
        /// I do"*. The owner's report on the panel was *"ive done like 50 things in a row and its
        /// still not opening"*; this is the same gap, on the object itself.
        ///
        /// **One line**, because it asks `GateStartupChecklist` for the first unfinished check
        /// rather than restating any condition. There is exactly one list of the eleven and both
        /// the window and this card read it, so the card cannot tell a player something the
        /// status board contradicts.
        ///
        /// ## Silent on every other door in the game
        ///
        /// `CompInspectStringExtra` has already returned on `!IsDesignated` before this is
        /// reached. This component sits on **every** Core door via the native binding patch, so
        /// a next-step line computed before that guard would print start-up advice on every
        /// bedroom door on the map.
        /// </summary>
        private string NextStepReadout()
        {
            System.Collections.Generic.List<GateStartupChecklist.GateStep> steps =
                GateStartupChecklist.Steps(this);
            GateStartupChecklist.GateStep next = GateStartupChecklist.NextIncomplete(steps);
            if (next.Number != 0)
            {
                return "RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)
                    .ToString();
            }
            // Past the last check the goal is no longer the machine, so the line stops being
            // about the machine. The same two outcomes the status board distinguishes.
            return IsOpening
                ? "RR_Steps_NowCross".Translate().ToString()
                : "RR_Steps_AllDone".Translate().ToString();
        }

        /// <summary>
        /// The blue a designated gate reads as. **Owner direction, 2026-09-29, verbatim:**
        /// *"yes the gates are just repurosed doors of the game with a bue tint and maybe a blue
        /// light glow hue around it like light through a glass wall does"*.
        ///
        /// This needed no new component and no new patch operation, because
        /// <c>ThingWithComps.DrawColor</c> already consults <c>ThingComp.ForceColor()</c> on
        /// every component a thing carries, and this component is already on the door.
        /// Returning null for anything not designated means **every other door in the game is
        /// untouched**, which is the same dormant-until-designated rule the rest of the native
        /// binding follows.
        ///
        /// A colour the player painted on deliberately still wins: Core checks a painted colour
        /// *before* reaching this hook. That is the right outcome — an explicit choice beats an
        /// automatic tint — and the aura still marks the door as a gate.
        /// </summary>
        public override Color? ForceColor()
        {
            if (!IsDesignated) { return null; }
            return GateTintColor;
        }

        /// <summary>Pale blue, as light coming through glass rather than a flat repaint.</summary>
        internal static readonly Color GateTintColor = new Color(0.55f, 0.78f, 0.98f);

        private static string DescribeWindow(int ticks)
        {
            return ticks <= 0 ? "RR_Gate_WindowClosed".Translate().ToString()
                : "RR_Gate_RemainingMinutes".Translate((int)Math.Ceiling(ticks * 1440.0 / GenDate.TicksPerDay)).ToString();
        }

        public CompanyActionResult AssignOperator(Pawn pawn)
        {
            if (!IsDesignated) { return CompanyActionResult.Refused("RR_NativeGate_NotBound"); }
            if (IsOpening) { return CompanyActionResult.Refused("RR_Gate_ActiveCannotReassign"); }
            if (pawn == null)
            {
                assignedOperator = null;
                return CompanyActionResult.Applied();
            }
            if (pawn == assignedOperator) { return CompanyActionResult.Existing(); }
            if (!IsEmployedStaff(pawn)) { return CompanyActionResult.Refused("RR_Gate_StaffOnly"); }
            if (!pawn.Spawned || pawn.Map != parent.Map || pawn.Dead || pawn.Destroyed || pawn.Downed || pawn.InMentalState)
            { return CompanyActionResult.Refused("RR_Gate_OperatorUnavailable"); }
            assignedOperator = pawn;
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult CanOpen(Pawn gateOperator, string expeditionId)
        {
            if (string.IsNullOrWhiteSpace(expeditionId)) { return CompanyActionResult.Refused("RR_Gate_InvalidExpedition"); }
            if (gateOperator == null || gateOperator != assignedOperator || !IsEmployedStaff(gateOperator))
            { return CompanyActionResult.Refused("RR_Gate_NoAssignedOperator"); }
            if (!assemblyComplete) { return CompanyActionResult.Refused("RR_Gate_NotAssembled"); }
            if (!calibrated) { return CompanyActionResult.Refused("RR_Gate_NotCalibrated"); }
            // Row 725's repair half. Asked here as well as in the tick, because a gate can take
            // damage between the tick that noticed and the click that opens, and the refusal has
            // to be the same answer the readout is showing.
            if (IntegrityFailureKey != null)
            { return CompanyActionResult.Refused(IntegrityFailureKey); }
            CompanyActionResult ready = CheckStationReadiness(gateOperator);
            if (!ready.Success) { return ready; }
            if (IsOpening && expeditionId == activeExpeditionId && string.IsNullOrEmpty(failureKey))
            { return CompanyActionResult.Existing(); }
            if (!IsOpening && expeditionId == lastClosedExpeditionId) { return CompanyActionResult.Existing(); }
            if (IsOpening && expeditionId == activeExpeditionId)
            { return CompanyActionResult.Refused("RR_Gate_RecoveryRequired"); }
            if (IsOpening) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }
            if (NativeStoredEnergy < NativeEnergyRequiredToOpenWattDays)
            { return CompanyActionResult.Refused("RR_NativeGate_OpeningEnergyLow"); }
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult BeginOpening(string expeditionId)
        {
            if (string.IsNullOrWhiteSpace(expeditionId)) { return CompanyActionResult.Refused("RR_Gate_InvalidExpedition"); }
            if (IsOpening && expeditionId == activeExpeditionId && string.IsNullOrEmpty(failureKey))
            { return CompanyActionResult.Existing(); }
            if (!IsOpening && expeditionId == lastClosedExpeditionId) { return CompanyActionResult.Existing(); }
            if (IsOpening && expeditionId == activeExpeditionId)
            { return CompanyActionResult.Refused("RR_Gate_RecoveryRequired"); }
            CompanyActionResult ready = CanOpen(assignedOperator, expeditionId);
            if (!ready.Success) { return ready; }
            activeExpeditionId = expeditionId;
            nativeOpeningSequence++;
            openingTicksRemaining = GateProps.openingWindowTicks;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            ResetOpeningWarnings();
            failureKey = null;
            stablePowerTicks = Math.Min(stablePowerTicks, GateProps.stablePowerTicksRequired);
            RecordGateActivity("RR_Event_GateOpeningStarted", expeditionId);
            return CompanyActionResult.Applied();
        }

        public void CloseOpening()
        {
            if (!string.IsNullOrEmpty(portalOpeningId)) { return; }
            CloseOpeningCore();
        }

        private void CloseOpeningCore()
        {
            if (portalOwnerFault || (!string.IsNullOrEmpty(portalOpeningId) && IsEmergency)) { return; }
            // Row 725's reliability half. Read before `failureKey` is cleared below, because
            // that field IS the emergency, and filed here because this is the one place an
            // opening is torn down -- so an outcome cannot be counted twice or missed.
            NoteOpeningOutcome(IsEmergency);
            if (!string.IsNullOrEmpty(portalOpeningId))
            { RecordGateActivity("RR_Event_GateOpeningClosed", portalOpeningId); }
            if (!string.IsNullOrWhiteSpace(activeExpeditionId))
            {
                lastClosedExpeditionId = activeExpeditionId;
                RecordGateActivity("RR_Event_GateOpeningClosed", activeExpeditionId);
            }
            activeExpeditionId = null;
            portalOpeningId = null;
            portalConnectionId = null;
            ClearIncursionSpent();
            openingTicksRemaining = 0;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            failureKey = null;
        }

        public CompanyActionResult TrySpendEmergencyReturnReserve(string expeditionId)
        {
            if (!IsOpening || string.IsNullOrWhiteSpace(expeditionId) || expeditionId != activeExpeditionId)
            { return CompanyActionResult.Refused("RR_Gate_ExpeditionMismatch"); }
            if (!IsEmergency || emergencyReturnTicksRemaining <= 0)
            { return CompanyActionResult.Refused("RR_Gate_NoEmergencyWindow"); }
            if (emergencyReturnSpent) { return CompanyActionResult.Existing(); }
            if (!TrySpendNativeEnergy(GateProps.emergencyReturnCostWattDays, true, NativeOpeningDebitId("emergency")))
            { return CompanyActionResult.Refused("RR_NativeGate_ReturnEnergyUnavailable"); }
            emergencyReturnSpent = true;
            RecordGateActivity("RR_Event_GateEmergencyReturnPaid", expeditionId,
                GateProps.emergencyReturnCostWattDays.ToString("F2", System.Globalization.CultureInfo.InvariantCulture));
            return CompanyActionResult.Applied();
        }

        /// <summary>Applies a saved, idempotent environmental time debit to the active normal opening.</summary>
        public CompanyActionResult SpendOpeningTicks(string expeditionId, int ticks, string operationId)
        {
            if (string.IsNullOrWhiteSpace(operationId)) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            if (ticks <= 0) { return CompanyActionResult.Refused("RR_Gate_InvalidTimeCost"); }

            GateWindowSpendReceipt prior = openingSpendReceipts.FirstOrDefault(receipt => receipt.OperationId == operationId);
            if (prior != null)
            {
                return prior.ExpeditionId == expeditionId && prior.RequestedTicks == ticks
                    ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Gate_OperationIdConflict");
            }
            if (!IsOpening || string.IsNullOrWhiteSpace(expeditionId) || expeditionId != activeExpeditionId)
            { return CompanyActionResult.Refused("RR_Gate_ExpeditionMismatch"); }
            if (IsEmergency || openingTicksRemaining <= 0)
            { return CompanyActionResult.Refused("RR_Gate_NoNormalWindow"); }

            int appliedTicks = Math.Min(openingTicksRemaining, ticks);
            openingTicksRemaining -= appliedTicks;
            openingSpendReceipts.Add(new GateWindowSpendReceipt(operationId, expeditionId, ticks, appliedTicks));
            SendOpeningWindowWarnings();
            if (openingTicksRemaining <= 0) { EnterEmergency("RR_Gate_TimeCostWindowExhausted"); }
            return CompanyActionResult.Applied();
        }

        public bool TryGetOpeningTicksSpendReceipt(string operationId, out int requestedTicks, out int appliedTicks)
        {
            GateWindowSpendReceipt receipt = openingSpendReceipts.FirstOrDefault(item => item.OperationId == operationId);
            requestedTicks = receipt == null ? 0 : receipt.RequestedTicks;
            appliedTicks = receipt == null ? 0 : receipt.AppliedTicks;
            return receipt != null;
        }

        /// <summary>Checks a new recovery attempt after its previous bounded return window has expired.</summary>
        public CompanyActionResult CanRecover(Pawn gateOperator, string expeditionId, string recoveryOperationId)
        {
            if (string.IsNullOrWhiteSpace(expeditionId)) { return CompanyActionResult.Refused("RR_Gate_InvalidExpedition"); }
            if (string.IsNullOrWhiteSpace(recoveryOperationId)) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            GateRecoveryReceipt prior = recoveryReceipts.FirstOrDefault(receipt => receipt.OperationId == recoveryOperationId);
            if (prior != null)
            {
                return prior.ExpeditionId == expeditionId
                    ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Gate_OperationIdConflict");
            }
            bool activeRecovery = IsOpening && expeditionId == activeExpeditionId;
            bool closedRunRecovery = !IsOpening && expeditionId == lastClosedExpeditionId;
            if (!activeRecovery && !closedRunRecovery)
            { return CompanyActionResult.Refused("RR_Gate_ExpeditionMismatch"); }
            if (activeRecovery && !IsAwaitingRecovery)
            { return CompanyActionResult.Refused("RR_Gate_RecoveryWindowStillActive"); }
            if (!assemblyComplete || !calibrated)
            { return CompanyActionResult.Refused("RR_Gate_NotCalibrated"); }
            CompanyActionResult ready = CheckStationReadiness(gateOperator);
            if (!ready.Success) { return ready; }
            if (NativeStoredEnergy < RecoveryEnergyRequiredWattDays)
            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }
            return CompanyActionResult.Applied();
        }

        /// <summary>Starts one paid recovery opening; retries of its stable receipt never restore time or reserve.</summary>
        public CompanyActionResult BeginRecoveryOpening(string expeditionId, string recoveryOperationId)
        {
            if (string.IsNullOrWhiteSpace(recoveryOperationId)) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            GateRecoveryReceipt prior = recoveryReceipts.FirstOrDefault(receipt => receipt.OperationId == recoveryOperationId);
            if (prior != null)
            {
                return prior.ExpeditionId == expeditionId
                    ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Gate_OperationIdConflict");
            }
            CompanyActionResult ready = CanRecover(assignedOperator, expeditionId, recoveryOperationId);
            if (!ready.Success) { return ready; }

            if (!TrySpendNativeEnergy(GateProps.recoveryOpeningCostWattDays, false, "recovery:" + recoveryOperationId))
            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }
            recoveryReceipts.Add(new GateRecoveryReceipt(recoveryOperationId, expeditionId));
            activeExpeditionId = expeditionId;
            nativeOpeningSequence++;
            lastClosedExpeditionId = null;
            openingTicksRemaining = GateProps.openingWindowTicks;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            ResetOpeningWarnings();
            failureKey = null;
            stablePowerTicks = Math.Min(stablePowerTicks, GateProps.stablePowerTicksRequired);
            RecordGateActivity("RR_Event_GateRecoveryOpeningStarted", expeditionId,
                GateProps.recoveryOpeningCostWattDays.ToString("F2", System.Globalization.CultureInfo.InvariantCulture));
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult OrderCalibration()
        {
            // **NAMES THE CAUSE.** This refused with `RR_Gate_CalibrationUnavailable` -- *"the
            // gate is not ready for calibration"* -- for all eight of `CanCalibrate`'s conditions,
            // **including `calibrated` itself.** So a player whose crew had already done the work
            // was told the work could not start, which is how the owner lost an afternoon:
            // *"now it just says gate is not ready to calibrate,, what am i missing"* against a
            // save that read `rr_gateCalibrated True`.
            string blocker = CalibrationBlockerKey();
            if (blocker != null) { return CompanyActionResult.Refused(blocker); }
            return OrderAssignedJob("RR_CalibrateGate");
        }

        public CompanyActionResult OrderStaffConsole()
        {
            if (IsOperatorOnStation) { return CompanyActionResult.Existing(); }
            // Same correction: one `RR_Gate_JobUnavailable` covered four different problems with
            // four different fixes.
            string blocker = StaffConsoleBlockerKey();
            if (blocker != null) { return CompanyActionResult.Refused(blocker); }
            return OrderAssignedJob("RR_OperateGate");
        }

        /// <summary>
        /// Why calibration cannot be ordered, as a keyed reason, or null when it can.
        ///
        /// **One authority.** `CanCalibrate` asks this rather than restating the conditions, so
        /// the predicate the work giver uses and the message the player reads cannot disagree --
        /// two derivations of one rule is the defect this project keeps meeting.
        /// </summary>
        public string CalibrationBlockerKey()
        {
            if (calibrated) { return "RR_Gate_AlreadyCalibrated"; }
            if (IsOpening) { return "RR_Gate_AlreadyOpen"; }
            if (!assemblyComplete) { return "RR_Gate_NotAssembled"; }
            if (assignedOperator == null) { return "RR_Gate_NoAssignedOperator"; }
            if (!IsEmployedStaff(assignedOperator)) { return "RR_Gate_OperatorNotEmployed"; }
            if (!parent.Spawned) { return "RR_Gate_MachineUnavailable"; }
            // The binding fault carries its own key, which is always more specific than anything
            // that could be written here: it names the component and the problem.
            if (NativeBindingFailureKey != null) { return NativeBindingFailureKey; }
            if (!IsConsolePowered(FindConsole())) { return "RR_NativeGate_PowerUnavailable"; }
            return null;
        }

        /// <summary>Why the operator cannot be sent to the console, as a keyed reason, or null.</summary>
        public string StaffConsoleBlockerKey()
        {
            if (IsOpening && !IsEmergency) { return "RR_Gate_AlreadyOpen"; }
            if (!calibrated) { return "RR_Gate_NotCalibrated"; }
            if (assignedOperator == null) { return "RR_Gate_NoAssignedOperator"; }
            if (!IsEmployedStaff(assignedOperator)) { return "RR_Gate_OperatorNotEmployed"; }
            return null;
        }

        public bool CanCalibrate(Pawn pawn)
        {
            return pawn != null && pawn == assignedOperator && CalibrationBlockerKey() == null;
        }

        public CompanyActionResult CompleteCalibration(Pawn pawn)
        {
            if (calibrated) { return CompanyActionResult.Existing(); }
            if (!CanCalibrate(pawn)) { return CompanyActionResult.Refused("RR_Gate_CalibrationUnavailable"); }
            calibrated = true;
            RecordGateActivity("RR_Event_GateCalibrationCompleted", parent.GetUniqueLoadID());
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult CompleteAssemblyFromBill(Thing billGiver, RecipeDef recipe)
        {
            if (billGiver == null || recipe == null || recipe.defName != "RR_AssembleMachineGate" ||
                billGiver.TryGetComp<CompRimroomsGateConsole>() == null)
            { return CompanyActionResult.Refused("RR_Gate_InvalidAssemblyBill"); }
            if (!IsDesignated || NativeCampaign == null || nativeBranchId != NativeCampaign.BranchId ||
                !SameNativeHeadquartersThing(billGiver) || billGiver != nativeAssemblyBench ||
                billGiver.TryGetComp<CompRimroomsGateConsole>().LinkedGate != parent)
            { return CompanyActionResult.Refused("RR_Gate_InvalidAssemblyBill"); }
            if (assemblyComplete) { return CompanyActionResult.Existing(); }
            if (!parent.Spawned || billGiver.Map != parent.Map)
            { return CompanyActionResult.Refused("RR_Gate_MachineUnavailable"); }
            assemblyComplete = true;
            billGiver.TryGetComp<CompRimroomsGateConsole>().MarkAssemblyBillComplete();
            RecordGateActivity("RR_Event_GateAssemblyCompleted", parent.GetUniqueLoadID());
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult TriggerEmergencyCutoff()
        {
            if (!IsOpening) { return CompanyActionResult.Refused("RR_Gate_NotOpen"); }
            if (!IsEmergency) { EnterEmergency("RR_Gate_EmergencyCutoff"); }
            return CompanyActionResult.Applied();
        }

        private void EnterEmergency(string reasonKey)
        {
            if (!IsOpening || !string.IsNullOrEmpty(failureKey)) { return; }
            failureKey = reasonKey;
            // **RR_Cap_ReturnDrill** (Fieldcraft and medicine, tier 0) adds half again. A crew
            // that has practised the walk back does it faster, and a longer window is how that
            // reads from the outside.
            int returnWindow = GateProps.emergencyReturnWindowTicks;
            Company.RimroomsCampaignComponent returnCampaign = NativeCampaign;
            if (returnCampaign != null)
            {
                // **RR_Cap_RescueTraining** (Fieldcraft and medicine, tier 1) supersedes
                // RR_Cap_ReturnDrill rather than stacking with it: a branch with the deeper
                // training gets double, not two and a half times. Checked first so the two
                // can never compound into a window nobody designed.
                if (returnCampaign.HasCapability("RR_Cap_RescueTraining")) { returnWindow *= 2; }
                else if (returnCampaign.HasCapability("RR_Cap_ReturnDrill")) { returnWindow += returnWindow / 2; }
            }
            emergencyReturnTicksRemaining = returnWindow;
            RecordGateActivity(reasonKey == "RR_Gate_TimeCostWindowExhausted"
                ? "RR_Gate_TimeCostWindowExhausted" : reasonKey, CurrentOpeningId);
            Messages.Message(reasonKey.Translate(), parent, MessageTypeDefOf.SilentInput, false);
            Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
        }

        /// <summary>
        /// Why the station cannot work this gate at all: the conditions that hold whether an
        /// aperture is being **opened** or merely **crossed** — saved-ownership sanity, the
        /// physical binding, and a real operator actually at the console.
        ///
        /// ## Owner direction, 2026-10-03, verbatim
        ///
        /// *"i build and set up and open the gate but it incorrectly says i dont have power to
        /// send people through, even tho the gate is open and connected,,, thast is wrong if its
        /// open it doenst need special power to send things through the gate"*, and naming the
        /// message: *"when i try to send people through it gives me a error about not enough
        /// reserver power in the batteries or something incarrate that shouldnt be"*.
        ///
        /// ## What was wrong, and the code said so itself
        ///
        /// `PortalWindowBlockerKey` — the single authority gating a crossing — called
        /// <see cref="CheckStationReadiness"/> **whole**, so passing somebody through a live
        /// aperture was asked three *opening* questions: the `stablePowerTicks` spin-up counter,
        /// `HasPowerAndHeadroom()`, and <see cref="ProjectedOpeningPowerFailure"/>, **whose own
        /// docstring reads "This gates opening only."** Its refusal `RR_Gate_SupplyTooLow` even
        /// says *"cannot deliver enough power **to start an opening**"* — the wrong sentence to
        /// show somebody whose opening is already running, and the one the owner read as
        /// *"reserver power in the batteries"*.
        ///
        /// **And it was redundant as well as wrong, which is why this is a removal and not a
        /// tuning.** Power lost while open is owned by the tick, which calls
        /// `EnterEmergency("RR_Gate_PowerLost")`, and `PortalWindowBlockerKey` already refuses an
        /// emergency gate three lines earlier with `RR_PortalTravel_InEmergency`. The crossing
        /// path was deriving a rule the tick already enforces, a second time and with a worse
        /// message — *two derivations of one rule*, which is the defect this component keeps
        /// paying for.
        ///
        /// **Split, not copied.** <see cref="CheckStationReadiness"/> is this plus the power
        /// conditions, so the opening path and the crossing path cannot drift apart.
        /// </summary>
        private CompanyActionResult CheckCrossingReadiness(Pawn gateOperator)
        {
            if (portalOwnerFault) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            if (NativeBindingFailureKey != null)
            { return CompanyActionResult.Refused(NativeBindingFailureKey); }
            if (gateOperator == null || gateOperator != assignedOperator || !IsEmployedStaff(gateOperator))
            { return CompanyActionResult.Refused("RR_Gate_NoAssignedOperator"); }
            // A distinct key from the readout above, which takes the operator name as {0}.
            // One key served both and only one string could win, so one of the two messages
            // was always wrong. Corrected 2026-09-29.
            if (!IsOperatorOnStation) { return CompanyActionResult.Refused("RR_Gate_OperatorNotStaffing"); }
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Why the station cannot **start or recover** an opening: the crossing conditions above,
        /// plus the power that the act of opening needs.
        ///
        /// **Never ask this of a crossing** — that is <see cref="CheckCrossingReadiness"/>. An
        /// aperture that is already held needs no supply projection and no spin-up counter, by
        /// owner direction quoted there.
        /// </summary>
        private CompanyActionResult CheckStationReadiness(Pawn gateOperator)
        {
            CompanyActionResult crossing = CheckCrossingReadiness(gateOperator);
            if (!crossing.Success) { return crossing; }
            if (stablePowerTicks < GateProps.stablePowerTicksRequired || !HasPowerAndHeadroom())
            { return CompanyActionResult.Refused("RR_Gate_PowerUnstable"); }
            // A keyed reason rather than one blanket refusal: "the circuit cannot deliver
            // enough" and "there is no margin above what the gate already draws" are different
            // problems with different fixes, and one string for both always lied about one.
            string supply = ProjectedOpeningPowerFailure();
            if (supply != null) { return CompanyActionResult.Refused(supply); }
            return CompanyActionResult.Applied();
        }

        private void SendOpeningWindowWarnings()
        {
            const int tenMinutesRemaining = 417;
            const int fiveMinutesRemaining = 208;
            const int twoMinutesRemaining = 83;
            if (!warnedHalfWindow && GateProps.openingWindowTicks > tenMinutesRemaining && openingTicksRemaining <= tenMinutesRemaining)
            {
                warnedHalfWindow = true;
                Messages.Message("RR_Gate_WarningTenMinutes".Translate(), parent, MessageTypeDefOf.SilentInput, false);
                Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
                RecordGateActivity("RR_Gate_WarningTenMinutes", CurrentOpeningId);
            }
            if (!warnedQuarterWindow && GateProps.openingWindowTicks > fiveMinutesRemaining && openingTicksRemaining <= fiveMinutesRemaining)
            {
                warnedQuarterWindow = true;
                Messages.Message("RR_Gate_WarningFiveMinutes".Translate(), parent, MessageTypeDefOf.SilentInput, false);
                Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
                RecordGateActivity("RR_Gate_WarningFiveMinutes", CurrentOpeningId);
            }
            if (!warnedTenthWindow && GateProps.openingWindowTicks > twoMinutesRemaining && openingTicksRemaining <= twoMinutesRemaining)
            {
                warnedTenthWindow = true;
                Messages.Message("RR_Gate_WarningTwoMinutes".Translate(), parent, MessageTypeDefOf.SilentInput, false);
                Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
                RecordGateActivity("RR_Gate_WarningTwoMinutes", CurrentOpeningId);
            }
            // **THE SCHEDULED RECALL RIDES THE SAME PASS OVER THE SAME NUMBER.** Deciding it
            // anywhere else would let the order and the warning that accompanies it drift apart
            // by a tick, which reads as a bug. A warning needs somebody watching; a standing
            // order does not, and being busy elsewhere on the map is how a crew gets lost.
            IssueStandingRecall();
        }

        private void ResetOpeningWarnings()
        {
            warnedHalfWindow = false;
            warnedQuarterWindow = false;
            warnedTenthWindow = false;
            // An order issued during a previous opening says nothing about this one.
            ResetStandingRecall();
        }

        /// <summary>
        /// A gate is powered when its designated infrastructure says so. The grid headroom
        /// arithmetic that used to live here belonged to the retired machine, which drew from
        /// the colony network directly; a gate on a door is fed by the battery the player bound
        /// to it, and that check is inside the binding failure key.
        /// </summary>
        private bool HasPowerAndHeadroom()
        {
            return NativeBindingFailureKey == null;
        }

        /// <summary>
        /// Whether the circuit can support **starting** an opening, or a keyed reason why not.
        ///
        /// Opening load is paid from the linked battery, never charged twice as grid load — so this
        /// asks about **supply**, not about the cost of the opening itself.
        ///
        /// ## Two values that had nothing reading them
        ///
        /// **`reserveChargePowerWatts`.** Owner's answer, 2026-09-29, verbatim: *"A supply
        /// requirement before opening"* — *the gate refuses to open unless its circuit can deliver
        /// this much power*. Generation, not stored charge: a battery is a buffer, not supply, and
        /// a gate opened on one charged battery and no generator is a gate about to strand a crew.
        ///
        /// **`MinimumPowerHeadroomWatts`, which was read by NOTHING.** Found while wiring the
        /// above. Its own docstring says *"headroom a gate needs above its draw before it will
        /// open"*, and no code asked. Worse: **`RR_Cap_ReserveDiscipline` is granted by the tier 0
        /// Facilities project and its whole effect was to lower that unread number**, so the card
        /// promised *"the gate needs less spare headroom above its draw before it will open"* and
        /// changed nothing a player could ever observe.
        ///
        /// That is **invariant 136** exactly, and it is why the research proof could not catch it:
        /// the capability *is* read by real code, and the code reading it was itself dead. A live
        /// read site is not a live effect. Both values are now consumed here, so the tier 0
        /// Facilities unlock finally does the thing it says.
        ///
        /// **This gates opening only.** It is called once, from the can-open check, and never from
        /// the tick — a generation dip must not emergency-return a crew that is already through.
        /// </summary>
        private string ProjectedOpeningPowerFailure()
        {
            if (NativeBindingFailureKey != null) { return NativeBindingFailureKey; }
            float generation = NativeGenerationWatts();
            if (generation < GateProps.reserveChargePowerWatts)
            { return "RR_Gate_SupplyTooLow"; }
            if (generation < CurrentPowerDrawWatts + MinimumPowerHeadroomWatts)
            { return "RR_Gate_HeadroomTooLow"; }
            return null;
        }

        private static bool IsConsolePowered(Thing console)
        {
            if (console == null || !console.Spawned || console.Map == null || console.IsBrokenDown() ||
                FlickUtility.WantsToBeOn(console) == false || console.Map.gameConditionManager.ElectricityDisabled(console.Map))
            { return false; }
            CompPowerTrader consolePower = console.TryGetComp<CompPowerTrader>();
            return consolePower != null && consolePower.PowerOn && consolePower.PowerNet != null;
        }

        /// <summary>
        /// The station this gate is operated from: the one the player designated, and only
        /// that one.
        ///
        /// There used to be a second path here that searched the map for the nearest
        /// RR_GateConsole. That def was retired in 0.9.0-dev, and the search was the wrong
        /// answer regardless once a branch could run two gates -- "nearest" is not "mine".
        /// </summary>
        private Thing FindConsole()
        {
            return IsDesignated && SameNativeHeadquartersThing(nativeConsole) ? nativeConsole : null;
        }

        private bool IsEmployedStaff(Pawn pawn)
        {
            if (pawn == null || Current.Game == null) { return false; }
            RimroomsCampaignComponent campaign = Current.Game.GetComponent<RimroomsCampaignComponent>();
            return campaign != null && campaign.CanOperate && campaign.Staff.Any(s => s != null && s.Employed && s.Pawn == pawn);
        }

        private void OpenOperatorMenu()
        {
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            List<FloatMenuOption> options = new List<FloatMenuOption>();
            if (campaign != null && campaign.CanOperate)
            {
                foreach (StaffRecord staff in campaign.Staff.Where(s => s != null && s.Employed && s.Pawn != null &&
                    !s.Pawn.Dead && !s.Pawn.Destroyed && !s.Pawn.Downed && !s.Pawn.InMentalState &&
                    s.Pawn.Spawned && s.Pawn.Map == parent.Map))
                {
                    Pawn choice = staff.Pawn;
                    options.Add(new FloatMenuOption("RR_Gate_StaffChoice".Translate(staff.Name, staff.Role),
                        delegate { AssignOperator(choice); }));
                }
            }
            options.Add(new FloatMenuOption("RR_Gate_UnassignOperator".Translate(), delegate { AssignOperator(null); }));
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private CompanyActionResult OrderAssignedJob(string jobDefName)
        {
            Thing console = FindConsole();
            if (assignedOperator == null || console == null || !IsEmployedStaff(assignedOperator) ||
                assignedOperator.Dead || assignedOperator.Destroyed || assignedOperator.Downed || !assignedOperator.Spawned ||
                assignedOperator.Map != parent.Map)
            { return CompanyActionResult.Refused("RR_Gate_NoAssignedOperator"); }
            JobDef jobDef = DefDatabase<JobDef>.GetNamedSilentFail(jobDefName);
            if (jobDef == null) { return CompanyActionResult.Refused("RR_Gate_JobUnavailable"); }
            Job job = JobMaker.MakeJob(jobDef, console);
            if (!assignedOperator.jobs.TryTakeOrderedJob(job, JobTag.Misc))
            { return CompanyActionResult.Refused("RR_Gate_JobUnavailable"); }
            return CompanyActionResult.Applied();
        }

        private void ShowOrderResult(CompanyActionResult result)
        {
            if (result != null && !result.Success && !string.IsNullOrWhiteSpace(result.MessageKey))
            { Messages.Message(result.MessageKey.Translate(), parent, MessageTypeDefOf.RejectInput, false); }
        }

        private void RecordGateActivity(string messageKey, string relatedId, params string[] arguments)
        {
            if (Current.Game == null) { return; }
            RimroomsCampaignComponent campaign = Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate) { return; }
            campaign.RecordEvent(messageKey, string.IsNullOrWhiteSpace(relatedId) ? parent.GetUniqueLoadID() : relatedId, arguments);
            if (messageKey == "RR_Event_GateOpeningStarted" || messageKey == "RR_Event_GateRecoveryOpeningStarted")
            { Audio.RimroomsAudio.Play("RR_GatePowerRise", parent.Map, parent.Position, false); }
        }
    }

    public sealed class GateWindowSpendReceipt : IExposable
    {
        public string OperationId;
        public string ExpeditionId;
        public int RequestedTicks;
        public int AppliedTicks;

        public GateWindowSpendReceipt() { }
        public GateWindowSpendReceipt(string operationId, string expeditionId, int requestedTicks, int appliedTicks)
        { OperationId = operationId; ExpeditionId = expeditionId; RequestedTicks = requestedTicks; AppliedTicks = appliedTicks; }

        public void ExposeData()
        {
            Scribe_Values.Look(ref OperationId, "operationId");
            Scribe_Values.Look(ref ExpeditionId, "expeditionId");
            Scribe_Values.Look(ref RequestedTicks, "requestedTicks", 0);
            Scribe_Values.Look(ref AppliedTicks, "appliedTicks", 0);
        }
    }

    public sealed class GateRecoveryReceipt : IExposable
    {
        public string OperationId;
        public string ExpeditionId;

        public GateRecoveryReceipt() { }
        public GateRecoveryReceipt(string operationId, string expeditionId)
        { OperationId = operationId; ExpeditionId = expeditionId; }

        public void ExposeData()
        {
            Scribe_Values.Look(ref OperationId, "operationId");
            Scribe_Values.Look(ref ExpeditionId, "expeditionId");
        }
    }
}
