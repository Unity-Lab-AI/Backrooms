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
        public bool nativeProvider;
        public int openingWindowTicks = 833;
        public int emergencyReturnWindowTicks = 300;
        public int stablePowerTicksRequired = 60;
        public float minimumPowerHeadroomWatts = 250f;
        public float idlePowerDrawWatts = 250f;
        public float openingPowerDrawWatts = 3500f;
        public float reserveChargePowerWatts = 1000f;
        public float returnReserveCapacityWattDays = 2f;
        public float emergencyReturnCostWattDays = 1f;
        public float recoveryOpeningCostWattDays = 1f;
        public float calibrationWorkRequired = 2500f;

        public CompProperties_RimroomsGate()
        {
            compClass = typeof(CompRimroomsGate);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
            if (nativeProvider && (parentDef.defName == "Door" || parentDef.defName == "Autodoor") &&
                !typeof(Building_Door).IsAssignableFrom(parentDef.thingClass))
            { yield return "Native Rimrooms gate provider supports only Core Door and Autodoor."; }
            if (!nativeProvider && (parentDef.size.x != 3 || parentDef.size.z != 3))
            { yield return "RR_MachineGate must use a 3x3 footprint."; }
            if (openingWindowTicks <= 0 || emergencyReturnWindowTicks <= 0 || stablePowerTicksRequired < 0)
            { yield return "Rimrooms gate timing settings must be positive."; }
            if (!PositiveFinite(minimumPowerHeadroomWatts) || !PositiveFinite(idlePowerDrawWatts) ||
                !PositiveFinite(openingPowerDrawWatts) || !PositiveFinite(reserveChargePowerWatts) ||
                !PositiveFinite(returnReserveCapacityWattDays) || !PositiveFinite(emergencyReturnCostWattDays) ||
                !PositiveFinite(recoveryOpeningCostWattDays) ||
                emergencyReturnCostWattDays + recoveryOpeningCostWattDays > returnReserveCapacityWattDays ||
                !PositiveFinite(calibrationWorkRequired))
            { yield return "Rimrooms gate power, reserve, and work settings must be finite and positive."; }
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
        private float returnReserveStoredWattDays;
        private int stablePowerTicks;
        private string lastClosedExpeditionId;
        private List<GateWindowSpendReceipt> openingSpendReceipts = new List<GateWindowSpendReceipt>();
        private List<GateRecoveryReceipt> recoveryReceipts = new List<GateRecoveryReceipt>();
        private CompPowerTrader powerTrader;
        private CompFlickable flickable;
        private Thing consoleCache;
        private float appliedPowerDrawWatts = -1f;

        private CompProperties_RimroomsGate GateProps { get { return (CompProperties_RimroomsGate)props; } }
        public Pawn AssignedOperator { get { return assignedOperator; } }
        public bool AssemblyComplete { get { return assemblyComplete; } }
        public bool Calibrated { get { return calibrated; } }
        public bool IsOpening { get { return !string.IsNullOrEmpty(activeExpeditionId) || !string.IsNullOrEmpty(portalOpeningId); } }
        public string ActiveExpeditionId { get { return activeExpeditionId; } }
        public int OpeningTicksRemaining { get { return openingTicksRemaining; } }
        public int EmergencyReturnTicksRemaining { get { return emergencyReturnTicksRemaining; } }
        public bool EmergencyReturnSpentForActiveExpedition { get { return emergencyReturnSpent; } }
        public bool IsEmergency { get { return IsOpening && !string.IsNullOrEmpty(failureKey); } }
        public string FailureKey { get { return failureKey; } }
        public float ReturnReserveStoredWattDays { get { return IsNativeProvider ? NativeStoredEnergy : returnReserveStoredWattDays; } }
        public float ReturnReserveCapacityWattDays { get { return IsNativeProvider ? NativeBatteryCapacity : GateProps.returnReserveCapacityWattDays; } }
        public float RecoveryOpeningCostWattDays { get { return GateProps.recoveryOpeningCostWattDays; } }
        public float EmergencyReturnCostWattDays { get { return GateProps.emergencyReturnCostWattDays; } }
        public float MinimumPowerHeadroomWatts { get { return GateProps.minimumPowerHeadroomWatts; } }
        public float CurrentPowerDrawWatts { get { return IsNativeProvider ? (IsOpening && !IsEmergency ? GateProps.openingPowerDrawWatts : 0f)
            : appliedPowerDrawWatts < 0f ? GateProps.idlePowerDrawWatts : appliedPowerDrawWatts; } }
        public IntVec3 GateEntryCell { get { return IsNativeProvider ? NativeEntryCell : parent.Spawned ? parent.InteractionCell : IntVec3.Invalid; } }
        public float CalibrationWorkRequired { get { return GateProps.calibrationWorkRequired; } }
        public Thing Console { get { return FindConsole(); } }
        public bool IsAwaitingRecovery { get { return IsOpening && IsEmergency && emergencyReturnTicksRemaining <= 0; } }

        public bool IsOperatorOnStation
        {
            get
            {
                Thing console = FindConsole();
                Pawn pawn = assignedOperator;
                if (console == null || !IsConsolePowered(console) || pawn == null || !IsEmployedStaff(pawn) ||
                    !pawn.Spawned || pawn.Map != parent.Map || pawn.Dead || pawn.Destroyed ||
                    pawn.Downed || pawn.InMentalState || pawn.jobs == null || pawn.CurJob == null || pawn.Position != console.InteractionCell)
                { return false; }
                Job job = pawn.CurJob;
                return job.def != null && job.def.defName == "RR_OperateGate" && job.GetTarget(TargetIndex.A).Thing == console;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref assignedOperator, "rr_gateAssignedOperator");
            Scribe_Values.Look(ref assemblyComplete, "rr_gateAssemblyComplete", false);
            Scribe_Values.Look(ref calibrated, "rr_gateCalibrated", false);
            Scribe_Values.Look(ref activeExpeditionId, "rr_gateActiveExpeditionId");
            ExposePortalOpening();
            Scribe_Values.Look(ref openingTicksRemaining, "rr_gateOpeningTicksRemaining", 0);
            Scribe_Values.Look(ref emergencyReturnTicksRemaining, "rr_gateEmergencyReturnTicksRemaining", 0);
            Scribe_Values.Look(ref emergencyReturnSpent, "rr_gateEmergencyReturnSpent", false);
            Scribe_Values.Look(ref warnedHalfWindow, "rr_gateWarnedHalfWindow", false);
            Scribe_Values.Look(ref warnedQuarterWindow, "rr_gateWarnedQuarterWindow", false);
            Scribe_Values.Look(ref warnedTenthWindow, "rr_gateWarnedTenthWindow", false);
            Scribe_Values.Look(ref failureKey, "rr_gateFailureKey");
            Scribe_Values.Look(ref returnReserveStoredWattDays, "rr_gateReturnReserveStored", 0f);
            Scribe_Values.Look(ref stablePowerTicks, "rr_gateStablePowerTicks", 0);
            Scribe_Values.Look(ref lastClosedExpeditionId, "rr_gateLastClosedExpeditionId");
            Scribe_Collections.Look(ref openingSpendReceipts, "rr_gateOpeningSpendReceipts", LookMode.Deep);
            Scribe_Collections.Look(ref recoveryReceipts, "rr_gateRecoveryReceipts", LookMode.Deep);
            ExposeNativeBinding();
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (openingSpendReceipts == null) { openingSpendReceipts = new List<GateWindowSpendReceipt>(); }
                if (recoveryReceipts == null) { recoveryReceipts = new List<GateRecoveryReceipt>(); }
                openingSpendReceipts.RemoveAll(receipt => receipt == null || string.IsNullOrWhiteSpace(receipt.OperationId));
                recoveryReceipts.RemoveAll(receipt => receipt == null || string.IsNullOrWhiteSpace(receipt.OperationId));
                returnReserveStoredWattDays = Mathf.Clamp(returnReserveStoredWattDays, 0f, GateProps.returnReserveCapacityWattDays);
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
            flickable = parent.GetComp<CompFlickable>();
            consoleCache = null;
            ApplyPowerDraw();
        }

        public override void CompTick()
        {
            using (Core.RimroomsDiagnostics.Measure("gate-tick")) { TickGate(); }
        }

        private void TickGate()
        {
            base.CompTick();
            if (!parent.Spawned || portalOwnerFault) { return; }
            if (IsNativeProvider && !BeginNativeTick()) { return; }
            if (IsNativeProvider) { Presentation.NativePortalPresentation.Tick(this); }

            ApplyPowerDraw();
            if (HasPowerAndHeadroom())
            {
                if (stablePowerTicks < int.MaxValue) { stablePowerTicks++; }
                bool canChargeForNormalUse = !IsOpening && !emergencyReturnSpent;
                bool canChargeForRecovery = IsAwaitingRecovery;
                if (!IsNativeProvider && (canChargeForNormalUse || canChargeForRecovery) &&
                    (!emergencyReturnSpent || canChargeForRecovery) &&
                    returnReserveStoredWattDays < GateProps.returnReserveCapacityWattDays)
                {
                    float chargeWattsThisTick = ReserveChargePowerWattsThisTick();
                    returnReserveStoredWattDays = Mathf.Min(GateProps.returnReserveCapacityWattDays,
                        returnReserveStoredWattDays + chargeWattsThisTick * CompPower.WattsToWattDaysPerTick);
                }
            }
            else { stablePowerTicks = 0; }

            if (!IsOpening) { return; }
            if (string.IsNullOrEmpty(failureKey))
            {
                if (!HasPowerAndHeadroom()) { EnterEmergency("RR_Gate_PowerLost"); }
                else if (!IsOperatorOnStation) { EnterEmergency("RR_Gate_OperatorLost"); }
                else if (openingTicksRemaining > 0)
                {
                    if (IsNativeProvider && !SpendNativeOpeningTick())
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

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }

            yield return new Command_Action
            {
                defaultLabel = "RR_Gate_AssignOperatorLabel".Translate(),
                defaultDesc = "RR_Gate_AssignOperatorDesc".Translate(),
                icon = IsNativeProvider ? parent.def.uiIcon : ContentFinder<Texture2D>.Get("Buildings/Gate/RR_GateConsole", true),
                action = OpenOperatorMenu
            };

            if (assignedOperator != null && AssemblyComplete && !Calibrated && !IsOpening)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_CalibrateLabel".Translate(),
                    defaultDesc = "RR_Gate_CalibrateDesc".Translate(),
                    icon = IsNativeProvider ? parent.def.uiIcon : ContentFinder<Texture2D>.Get("Buildings/Gate/RR_GateConsole", true),
                    action = delegate { ShowOrderResult(OrderCalibration()); }
                };
            }

            if (assignedOperator != null && Calibrated && (!IsOpening || IsEmergency))
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_StaffConsoleLabel".Translate(),
                    defaultDesc = "RR_Gate_StaffConsoleDesc".Translate(),
                    icon = IsNativeProvider ? parent.def.uiIcon : ContentFinder<Texture2D>.Get("Buildings/Gate/RR_MachineGate", true),
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
            string operatorText = assignedOperator == null ? "RR_Gate_NoOperator".Translate().ToString()
                : (IsOperatorOnStation ? "RR_Gate_OperatorPresent".Translate(assignedOperator.LabelShortCap).ToString()
                    : "RR_Gate_OperatorAway".Translate(assignedOperator.LabelShortCap).ToString());
            string powerText = "RR_Gate_PowerReadout".Translate(CurrentPowerDrawWatts.ToString("F0"),
                GateProps.reserveChargePowerWatts.ToString("F0"), GateProps.minimumPowerHeadroomWatts.ToString("F0"),
                returnReserveStoredWattDays.ToString("F2"), GateProps.returnReserveCapacityWattDays.ToString("F2"),
                GateProps.emergencyReturnCostWattDays.ToString("F2"), GateProps.recoveryOpeningCostWattDays.ToString("F2")).ToString();
            if (IsNativeProvider)
            {
                powerText = "RR_NativeGate_PowerReadout".Translate(ReturnReserveStoredWattDays.ToString("F2"),
                    ReturnReserveCapacityWattDays.ToString("F2"), CurrentPowerDrawWatts.ToString("F0"),
                    NativeEnergyRequiredToOpenWattDays.ToString("F2"), RecoveryEnergyRequiredWattDays.ToString("F2")).ToString();
                if (NativeBindingFailureKey != null) { powerText += "\n" + NativeBindingFailureKey.Translate(); }
            }
            string active = IsOpening
                ? "RR_Gate_OpeningReadout".Translate(DescribeWindow(openingTicksRemaining),
                    DescribeWindow(emergencyReturnTicksRemaining), string.IsNullOrEmpty(failureKey) ? "RR_Gate_NoFailure".Translate() : failureKey.Translate()).ToString()
                : "";
            return string.Join("\n", new[] { status, operatorText, powerText, active }.Where(s => !string.IsNullOrEmpty(s)));
        }

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
            CompanyActionResult ready = CheckStationReadiness(gateOperator);
            if (!ready.Success) { return ready; }
            if (IsOpening && expeditionId == activeExpeditionId && string.IsNullOrEmpty(failureKey))
            { return CompanyActionResult.Existing(); }
            if (!IsOpening && expeditionId == lastClosedExpeditionId) { return CompanyActionResult.Existing(); }
            if (IsOpening && expeditionId == activeExpeditionId)
            { return CompanyActionResult.Refused("RR_Gate_RecoveryRequired"); }
            if (IsOpening) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }
            if (IsNativeProvider && NativeStoredEnergy < NativeEnergyRequiredToOpenWattDays)
            { return CompanyActionResult.Refused("RR_NativeGate_OpeningEnergyLow"); }
            if (!IsNativeProvider && returnReserveStoredWattDays + 0.0001f < GateProps.emergencyReturnCostWattDays)
            { return CompanyActionResult.Refused("RR_Gate_ReserveTooLow"); }
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
            if (IsNativeProvider) { nativeOpeningSequence++; }
            openingTicksRemaining = GateProps.openingWindowTicks;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            ResetOpeningWarnings();
            failureKey = null;
            stablePowerTicks = Math.Min(stablePowerTicks, GateProps.stablePowerTicksRequired);
            ApplyPowerDraw();
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
            openingTicksRemaining = 0;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            failureKey = null;
            ApplyPowerDraw();
        }

        public CompanyActionResult TrySpendEmergencyReturnReserve(string expeditionId)
        {
            if (!IsOpening || string.IsNullOrWhiteSpace(expeditionId) || expeditionId != activeExpeditionId)
            { return CompanyActionResult.Refused("RR_Gate_ExpeditionMismatch"); }
            if (!IsEmergency || emergencyReturnTicksRemaining <= 0)
            { return CompanyActionResult.Refused("RR_Gate_NoEmergencyWindow"); }
            if (emergencyReturnSpent) { return CompanyActionResult.Existing(); }
            if (IsNativeProvider)
            {
                if (!TrySpendNativeEnergy(GateProps.emergencyReturnCostWattDays, true, NativeOpeningDebitId("emergency")))
                { return CompanyActionResult.Refused("RR_NativeGate_ReturnEnergyUnavailable"); }
            }
            else
            {
                if (returnReserveStoredWattDays + 0.0001f < GateProps.emergencyReturnCostWattDays)
                { return CompanyActionResult.Refused("RR_Gate_ReserveTooLow"); }
                returnReserveStoredWattDays = Mathf.Max(0f, returnReserveStoredWattDays - GateProps.emergencyReturnCostWattDays);
            }
            emergencyReturnSpent = true;
            ApplyPowerDraw();
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
            if (IsNativeProvider && NativeStoredEnergy < RecoveryEnergyRequiredWattDays)
            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }
            if (!IsNativeProvider && returnReserveStoredWattDays + 0.0001f < GateProps.returnReserveCapacityWattDays)
            { return CompanyActionResult.Refused("RR_Gate_RecoveryReserveNotFull"); }
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

            if (IsNativeProvider && !TrySpendNativeEnergy(GateProps.recoveryOpeningCostWattDays, false, "recovery:" + recoveryOperationId))
            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }
            recoveryReceipts.Add(new GateRecoveryReceipt(recoveryOperationId, expeditionId));
            activeExpeditionId = expeditionId;
            if (IsNativeProvider) { nativeOpeningSequence++; }
            lastClosedExpeditionId = null;
            if (!IsNativeProvider)
            { returnReserveStoredWattDays = Mathf.Max(0f, returnReserveStoredWattDays - GateProps.recoveryOpeningCostWattDays); }
            openingTicksRemaining = GateProps.openingWindowTicks;
            emergencyReturnTicksRemaining = 0;
            emergencyReturnSpent = false;
            ResetOpeningWarnings();
            failureKey = null;
            stablePowerTicks = Math.Min(stablePowerTicks, GateProps.stablePowerTicksRequired);
            ApplyPowerDraw();
            RecordGateActivity("RR_Event_GateRecoveryOpeningStarted", expeditionId,
                GateProps.recoveryOpeningCostWattDays.ToString("F2", System.Globalization.CultureInfo.InvariantCulture));
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult OrderCalibration()
        {
            if (!CanCalibrate(assignedOperator)) { return CompanyActionResult.Refused("RR_Gate_CalibrationUnavailable"); }
            return OrderAssignedJob("RR_CalibrateGate");
        }

        public CompanyActionResult OrderStaffConsole()
        {
            if (IsOperatorOnStation) { return CompanyActionResult.Existing(); }
            if ((IsOpening && !IsEmergency) || !calibrated || assignedOperator == null || !IsEmployedStaff(assignedOperator))
            { return CompanyActionResult.Refused("RR_Gate_JobUnavailable"); }
            return OrderAssignedJob("RR_OperateGate");
        }

        public bool CanCalibrate(Pawn pawn)
        {
            return !IsOpening && assemblyComplete && !calibrated && pawn != null && pawn == assignedOperator &&
                IsEmployedStaff(pawn) && parent.Spawned && HasPowerAndHeadroom() && IsConsolePowered(FindConsole());
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
            if (IsNativeProvider && (!IsDesignated || NativeCampaign == null || nativeBranchId != NativeCampaign.BranchId ||
                !SameNativeHeadquartersThing(billGiver) || billGiver != nativeAssemblyBench ||
                billGiver.TryGetComp<CompRimroomsGateConsole>().LinkedGate != parent))
            { return CompanyActionResult.Refused("RR_Gate_InvalidAssemblyBill"); }
            if (assemblyComplete) { return CompanyActionResult.Existing(); }
            if (!parent.Spawned || billGiver.Map != parent.Map)
            { return CompanyActionResult.Refused("RR_Gate_MachineUnavailable"); }
            assemblyComplete = true;
            if (IsNativeProvider) { billGiver.TryGetComp<CompRimroomsGateConsole>().MarkAssemblyBillComplete(); }
            RecordGateActivity("RR_Event_GateAssemblyCompleted", parent.GetUniqueLoadID());
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult TriggerEmergencyCutoff()
        {
            if (!IsOpening) { return CompanyActionResult.Refused("RR_Gate_NotOpen"); }
            if (!IsEmergency) { EnterEmergency("RR_Gate_EmergencyCutoff"); }
            if (!IsNativeProvider)
            {
                if (flickable == null) { flickable = parent.GetComp<CompFlickable>(); }
                if (flickable != null) { flickable.SwitchIsOn = false; }
            }
            return CompanyActionResult.Applied();
        }

        private void EnterEmergency(string reasonKey)
        {
            if (!IsOpening || !string.IsNullOrEmpty(failureKey)) { return; }
            failureKey = reasonKey;
            emergencyReturnTicksRemaining = GateProps.emergencyReturnWindowTicks;
            ApplyPowerDraw();
            RecordGateActivity(reasonKey == "RR_Gate_TimeCostWindowExhausted"
                ? "RR_Gate_TimeCostWindowExhausted" : reasonKey, CurrentOpeningId);
            Messages.Message(reasonKey.Translate(), parent, MessageTypeDefOf.SilentInput, false);
            Audio.RimroomsAudio.Play("RR_GateWarning", parent.Map, parent.Position, false);
        }

        private CompanyActionResult CheckStationReadiness(Pawn gateOperator)
        {
            if (portalOwnerFault) { return CompanyActionResult.Refused("RR_Gate_InvalidOperation"); }
            if (IsNativeProvider && NativeBindingFailureKey != null)
            { return CompanyActionResult.Refused(NativeBindingFailureKey); }
            if (gateOperator == null || gateOperator != assignedOperator || !IsEmployedStaff(gateOperator))
            { return CompanyActionResult.Refused("RR_Gate_NoAssignedOperator"); }
            if (!IsOperatorOnStation) { return CompanyActionResult.Refused("RR_Gate_OperatorAway"); }
            if (stablePowerTicks < GateProps.stablePowerTicksRequired || !HasPowerAndHeadroom())
            { return CompanyActionResult.Refused("RR_Gate_PowerUnstable"); }
            if (!HasProjectedOpeningPowerHeadroom())
            { return CompanyActionResult.Refused("RR_Gate_OpeningPowerUnstable"); }
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
        }

        private void ResetOpeningWarnings()
        {
            warnedHalfWindow = false;
            warnedQuarterWindow = false;
            warnedTenthWindow = false;
        }

        private bool HasPowerAndHeadroom()
        {
            if (IsNativeProvider) { return NativeBindingFailureKey == null; }
            if (!parent.Spawned || powerTrader == null || !powerTrader.PowerOn || powerTrader.PowerNet == null ||
                parent.IsBrokenDown() || FlickUtility.WantsToBeOn(parent) == false ||
                parent.Map.gameConditionManager.ElectricityDisabled(parent.Map)) { return false; }
            float headroomWatts = powerTrader.PowerNet.CurrentEnergyGainRate() / CompPower.WattsToWattDaysPerTick;
            return headroomWatts + 0.001f >= GateProps.minimumPowerHeadroomWatts;
        }

        private bool HasProjectedOpeningPowerHeadroom()
        {
            // Native portal load is paid from the linked battery, not charged twice as grid load.
            if (IsNativeProvider) { return NativeBindingFailureKey == null; }
            if (!parent.Spawned || powerTrader == null || !powerTrader.PowerOn || powerTrader.PowerNet == null)
            { return false; }
            float currentHeadroomWatts = powerTrader.PowerNet.CurrentEnergyGainRate() / CompPower.WattsToWattDaysPerTick;
            float additionalOpeningDrawWatts = Mathf.Max(0f, GateProps.openingPowerDrawWatts - CurrentPowerDrawWatts);
            return currentHeadroomWatts - additionalOpeningDrawWatts + 0.001f >= GateProps.minimumPowerHeadroomWatts;
        }

        private static bool IsConsolePowered(Thing console)
        {
            if (console == null || !console.Spawned || console.Map == null || console.IsBrokenDown() ||
                FlickUtility.WantsToBeOn(console) == false || console.Map.gameConditionManager.ElectricityDisabled(console.Map))
            { return false; }
            CompPowerTrader consolePower = console.TryGetComp<CompPowerTrader>();
            return consolePower != null && consolePower.PowerOn && consolePower.PowerNet != null;
        }

        private void ApplyPowerDraw()
        {
            if (IsNativeProvider) { return; }
            if (powerTrader == null) { powerTrader = parent.GetComp<CompPowerTrader>(); }
            if (powerTrader == null) { return; }
            float desired = IsOpening && string.IsNullOrEmpty(failureKey) ? GateProps.openingPowerDrawWatts
                : ((!IsOpening || IsAwaitingRecovery) && returnReserveStoredWattDays < GateProps.returnReserveCapacityWattDays
                    ? ReserveChargePowerWattsThisTick() : GateProps.idlePowerDrawWatts);
            if (Mathf.Abs(appliedPowerDrawWatts - desired) < 0.01f) { return; }
            appliedPowerDrawWatts = desired;
            powerTrader.PowerOutput = 0f - desired;
        }

        private float ReserveChargePowerWattsThisTick()
        {
            float remainingWattDays = GateProps.returnReserveCapacityWattDays - returnReserveStoredWattDays;
            if (remainingWattDays <= 0f) { return 0f; }
            float wattsForRemainingCapacity = remainingWattDays / CompPower.WattsToWattDaysPerTick;
            return Mathf.Min(GateProps.reserveChargePowerWatts, wattsForRemainingCapacity);
        }

        private Thing FindConsole()
        {
            if (IsNativeProvider) { return IsDesignated && SameNativeHeadquartersThing(nativeConsole) ? nativeConsole : null; }
            if (!parent.Spawned || parent.Map == null) { return null; }
            if (consoleCache != null && consoleCache.Spawned && consoleCache.Map == parent.Map) { return consoleCache; }
            ThingDef consoleDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_GateConsole");
            if (consoleDef == null) { return null; }
            consoleCache = parent.Map.listerBuildings.AllBuildingsColonistOfDef(consoleDef)
                .OrderBy(t => t.Position.DistanceToSquared(parent.Position)).FirstOrDefault();
            return consoleCache;
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
