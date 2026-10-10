"""Collapse the unreachable non-native gate branches, part 2: the gate component itself.

Same boolean identities as part 1. This file is where the collapse cascades: with the
non-native branch gone, the gate's own power-reserve model turns out to be entirely
unreachable. A native gate is powered from the battery the player designated, so the
component's private reserve, its applied draw and its charging tick were all vestigial --
`ApplyPowerDraw` in particular reduces to an empty method.
"""
import io

p = 'src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs'
s = io.open(p, encoding='utf-8').read()

pairs = []

# --- config errors ---------------------------------------------------------
pairs.append((
 '            if (nativeProvider && (parentDef.defName == "Door" || parentDef.defName == "Autodoor") &&\n'
 '                !typeof(Building_Door).IsAssignableFrom(parentDef.thingClass))',
 '            if ((parentDef.defName == "Door" || parentDef.defName == "Autodoor") &&\n'
 '                !typeof(Building_Door).IsAssignableFrom(parentDef.thingClass))'))

# --- readouts that were choosing between two power models ------------------
pairs.append((
 '        public float ReturnReserveStoredWattDays { get { return IsNativeProvider ? NativeStoredEnergy : returnReserveStoredWattDays; } }',
 '        public float ReturnReserveStoredWattDays { get { return NativeStoredEnergy; } }'))
pairs.append((
 '        public float ReturnReserveCapacityWattDays { get { return IsNativeProvider ? NativeBatteryCapacity : GateProps.returnReserveCapacityWattDays; } }',
 '        public float ReturnReserveCapacityWattDays { get { return NativeBatteryCapacity; } }'))
pairs.append((
 '        public float CurrentPowerDrawWatts { get { return IsNativeProvider ? (IsOpening && !IsEmergency ? GateProps.openingPowerDrawWatts : 0f)\n'
 '            : appliedPowerDrawWatts < 0f ? GateProps.idlePowerDrawWatts : appliedPowerDrawWatts; } }',
 '        public float CurrentPowerDrawWatts\n'
 '        { get { return IsOpening && !IsEmergency ? GateProps.openingPowerDrawWatts : 0f; } }'))
pairs.append((
 '        public IntVec3 GateEntryCell { get { return IsNativeProvider ? NativeEntryCell : parent.Spawned ? parent.InteractionCell : IntVec3.Invalid; } }',
 '        public IntVec3 GateEntryCell { get { return NativeEntryCell; } }'))

# --- the private reserve is gone entirely ----------------------------------
pairs.append(('        private float returnReserveStoredWattDays;\n', ''))
pairs.append(('        private CompFlickable flickable;\n', ''))
pairs.append(('        private float appliedPowerDrawWatts = -1f;\n', ''))
pairs.append(('            Scribe_Values.Look(ref returnReserveStoredWattDays, "rr_gateReturnReserveStored", 0f);\n', ''))
pairs.append((
 '                returnReserveStoredWattDays = Mathf.Clamp(returnReserveStoredWattDays, 0f, GateProps.returnReserveCapacityWattDays);\n', ''))
pairs.append(('            flickable = parent.GetComp<CompFlickable>();\n', ''))

# --- tick ------------------------------------------------------------------
pairs.append((
 '            if (IsNativeProvider && !BeginNativeTick()) { return; }\n'
 '            if (IsNativeProvider) { Presentation.NativePortalPresentation.Tick(this); }',
 '            if (!BeginNativeTick()) { return; }\n'
 '            Presentation.NativePortalPresentation.Tick(this);'))
pairs.append((
 '                bool canChargeForNormalUse = !IsOpening && !emergencyReturnSpent;\n'
 '                bool canChargeForRecovery = IsAwaitingRecovery;\n'
 '                if (!IsNativeProvider && (canChargeForNormalUse || canChargeForRecovery) &&\n'
 '                    (!emergencyReturnSpent || canChargeForRecovery) &&\n'
 '                    returnReserveStoredWattDays < GateProps.returnReserveCapacityWattDays)\n'
 '                {\n'
 '                    float chargeWattsThisTick = ReserveChargePowerWattsThisTick();\n'
 '                    returnReserveStoredWattDays = Mathf.Min(GateProps.returnReserveCapacityWattDays,\n'
 '                        returnReserveStoredWattDays + chargeWattsThisTick * CompPower.WattsToWattDaysPerTick);\n'
 '                }\n', ''))
pairs.append((
 '                    if (IsNativeProvider && !SpendNativeOpeningTick())\n'
 '                    {\n'
 '                        EnterEmergency(HasNativeEnergyDebitFault\n',
 '                    if (!SpendNativeOpeningTick())\n'
 '                    {\n'
 '                        EnterEmergency(HasNativeEnergyDebitFault\n'))
pairs.append((
 '                    if (IsNativeProvider && !SpendNativeOpeningTick())\n'
 '                    { EnterEmergency(HasNativeEnergyDebitFault ? "RR_NativeGate_EnergyDebitFault" : "RR_NativeGate_OpeningEnergyLow"); return; }',
 '                    if (!SpendNativeOpeningTick())\n'
 '                    { EnterEmergency(HasNativeEnergyDebitFault ? "RR_NativeGate_EnergyDebitFault" : "RR_NativeGate_OpeningEnergyLow"); return; }'))

# --- inspect string: the first readout was always overwritten --------------
pairs.append((
 '            string powerText = "RR_Gate_PowerReadout".Translate(CurrentPowerDrawWatts.ToString("F0"),\n'
 '                GateProps.reserveChargePowerWatts.ToString("F0"), GateProps.minimumPowerHeadroomWatts.ToString("F0"),\n'
 '                returnReserveStoredWattDays.ToString("F2"), GateProps.returnReserveCapacityWattDays.ToString("F2"),\n'
 '                GateProps.emergencyReturnCostWattDays.ToString("F2"), GateProps.recoveryOpeningCostWattDays.ToString("F2")).ToString();\n'
 '            if (IsNativeProvider)\n'
 '            {\n'
 '                powerText = "RR_NativeGate_PowerReadout".Translate(ReturnReserveStoredWattDays.ToString("F2"),\n'
 '                    ReturnReserveCapacityWattDays.ToString("F2"), CurrentPowerDrawWatts.ToString("F0"),\n'
 '                    NativeEnergyRequiredToOpenWattDays.ToString("F2"), RecoveryEnergyRequiredWattDays.ToString("F2")).ToString();\n'
 '                if (NativeBindingFailureKey != null) { powerText += "\\n" + NativeBindingFailureKey.Translate(); }\n'
 '            }',
 '            // One readout. The legacy one computed here first was overwritten on every\n'
 '            // single call before it could be shown.\n'
 '            string powerText = "RR_NativeGate_PowerReadout".Translate(ReturnReserveStoredWattDays.ToString("F2"),\n'
 '                ReturnReserveCapacityWattDays.ToString("F2"), CurrentPowerDrawWatts.ToString("F0"),\n'
 '                NativeEnergyRequiredToOpenWattDays.ToString("F2"), RecoveryEnergyRequiredWattDays.ToString("F2")).ToString();\n'
 '            if (NativeBindingFailureKey != null) { powerText += "\\n" + NativeBindingFailureKey.Translate(); }'))

# --- gizmos / opening / recovery ------------------------------------------
pairs.append(('            if (!IsNativeProvider || !IsDesignated) { return null; }',
              '            if (!IsDesignated) { return null; }'))
pairs.append((
 '            if (IsNativeProvider && NativeStoredEnergy < NativeEnergyRequiredToOpenWattDays)\n'
 '            { return CompanyActionResult.Refused("RR_NativeGate_OpeningEnergyLow"); }\n'
 '            if (!IsNativeProvider && returnReserveStoredWattDays + 0.0001f < GateProps.emergencyReturnCostWattDays)\n'
 '            { return CompanyActionResult.Refused("RR_Gate_ReserveTooLow"); }\n',
 '            if (NativeStoredEnergy < NativeEnergyRequiredToOpenWattDays)\n'
 '            { return CompanyActionResult.Refused("RR_NativeGate_OpeningEnergyLow"); }\n'))
pairs.append(('            activeExpeditionId = expeditionId;\n            if (IsNativeProvider) { nativeOpeningSequence++; }\n            openingTicksRemaining = GateProps.openingWindowTicks;',
              '            activeExpeditionId = expeditionId;\n            nativeOpeningSequence++;\n            openingTicksRemaining = GateProps.openingWindowTicks;'))
pairs.append((
 '            if (IsNativeProvider)\n'
 '            {\n'
 '                if (!TrySpendNativeEnergy(GateProps.emergencyReturnCostWattDays, true, NativeOpeningDebitId("emergency")))\n'
 '                { return CompanyActionResult.Refused("RR_NativeGate_ReturnEnergyUnavailable"); }\n'
 '            }\n'
 '            else\n'
 '            {\n'
 '                if (returnReserveStoredWattDays + 0.0001f < GateProps.emergencyReturnCostWattDays)\n'
 '                { return CompanyActionResult.Refused("RR_Gate_ReserveTooLow"); }\n'
 '                returnReserveStoredWattDays = Mathf.Max(0f, returnReserveStoredWattDays - GateProps.emergencyReturnCostWattDays);\n'
 '            }\n',
 '            if (!TrySpendNativeEnergy(GateProps.emergencyReturnCostWattDays, true, NativeOpeningDebitId("emergency")))\n'
 '            { return CompanyActionResult.Refused("RR_NativeGate_ReturnEnergyUnavailable"); }\n'))
pairs.append((
 '            if (IsNativeProvider && NativeStoredEnergy < RecoveryEnergyRequiredWattDays)\n'
 '            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }\n'
 '            if (!IsNativeProvider && returnReserveStoredWattDays + 0.0001f < GateProps.returnReserveCapacityWattDays)\n'
 '            { return CompanyActionResult.Refused("RR_Gate_RecoveryReserveNotFull"); }\n',
 '            if (NativeStoredEnergy < RecoveryEnergyRequiredWattDays)\n'
 '            { return CompanyActionResult.Refused("RR_NativeGate_RecoveryEnergyLow"); }\n'))
pairs.append((
 '            if (IsNativeProvider && !TrySpendNativeEnergy(GateProps.recoveryOpeningCostWattDays, false, "recovery:" + recoveryOperationId))',
 '            if (!TrySpendNativeEnergy(GateProps.recoveryOpeningCostWattDays, false, "recovery:" + recoveryOperationId))'))
pairs.append((
 '            if (IsNativeProvider) { nativeOpeningSequence++; }\n'
 '            lastClosedExpeditionId = null;\n'
 '            if (!IsNativeProvider)\n'
 '            { returnReserveStoredWattDays = Mathf.Max(0f, returnReserveStoredWattDays - GateProps.recoveryOpeningCostWattDays); }\n',
 '            nativeOpeningSequence++;\n'
 '            lastClosedExpeditionId = null;\n'))

# --- assembly / cutoff / readiness ----------------------------------------
pairs.append((
 '            if (IsNativeProvider && (!IsDesignated || NativeCampaign == null || nativeBranchId != NativeCampaign.BranchId ||',
 '            if (!IsDesignated || NativeCampaign == null || nativeBranchId != NativeCampaign.BranchId ||'))
pairs.append((
 '            if (IsNativeProvider) { billGiver.TryGetComp<CompRimroomsGateConsole>().MarkAssemblyBillComplete(); }',
 '            billGiver.TryGetComp<CompRimroomsGateConsole>().MarkAssemblyBillComplete();'))
pairs.append((
 '            if (!IsNativeProvider)\n'
 '            {\n'
 '                if (flickable == null) { flickable = parent.GetComp<CompFlickable>(); }\n'
 '                if (flickable != null) { flickable.SwitchIsOn = false; }\n'
 '            }\n', ''))
pairs.append((
 '            if (IsNativeProvider && NativeBindingFailureKey != null)',
 '            if (NativeBindingFailureKey != null)'))

# --- power methods reduce to the native answer -----------------------------
pairs.append((
 '        private bool HasPowerAndHeadroom()\n'
 '        {\n'
 '            if (IsNativeProvider) { return NativeBindingFailureKey == null; }\n'
 '            if (!parent.Spawned || powerTrader == null || !powerTrader.PowerOn || powerTrader.PowerNet == null ||\n'
 '                parent.IsBrokenDown() || FlickUtility.WantsToBeOn(parent) == false ||\n'
 '                parent.Map.gameConditionManager.ElectricityDisabled(parent.Map)) { return false; }\n'
 '            float headroomWatts = powerTrader.PowerNet.CurrentEnergyGainRate() / CompPower.WattsToWattDaysPerTick;\n'
 '            return headroomWatts + 0.001f >= GateProps.minimumPowerHeadroomWatts;\n'
 '        }',
 '        /// <summary>\n'
 '        /// A gate is powered when its designated infrastructure says so. The grid headroom\n'
 '        /// arithmetic that used to live here belonged to the retired machine, which drew from\n'
 '        /// the colony network directly; a gate on a door is fed by the battery the player bound\n'
 '        /// to it, and that check is inside the binding failure key.\n'
 '        /// </summary>\n'
 '        private bool HasPowerAndHeadroom()\n'
 '        {\n'
 '            return NativeBindingFailureKey == null;\n'
 '        }'))
pairs.append((
 '        private bool HasProjectedOpeningPowerHeadroom()\n'
 '        {\n'
 '            // Native portal load is paid from the linked battery, not charged twice as grid load.\n'
 '            if (IsNativeProvider) { return NativeBindingFailureKey == null; }\n'
 '            if (!parent.Spawned || powerTrader == null || !powerTrader.PowerOn || powerTrader.PowerNet == null)\n'
 '            { return false; }\n'
 '            float currentHeadroomWatts = powerTrader.PowerNet.CurrentEnergyGainRate() / CompPower.WattsToWattDaysPerTick;\n'
 '            float additionalOpeningDrawWatts = Mathf.Max(0f, GateProps.openingPowerDrawWatts - CurrentPowerDrawWatts);\n'
 '            return currentHeadroomWatts - additionalOpeningDrawWatts + 0.001f >= GateProps.minimumPowerHeadroomWatts;\n'
 '        }',
 '        /// <summary>Opening load is paid from the linked battery, never charged twice as grid load.</summary>\n'
 '        private bool HasProjectedOpeningPowerHeadroom()\n'
 '        {\n'
 '            return NativeBindingFailureKey == null;\n'
 '        }'))
pairs.append((
 '        private void ApplyPowerDraw()\n'
 '        {\n'
 '            if (IsNativeProvider) { return; }\n'
 '            if (powerTrader == null) { powerTrader = parent.GetComp<CompPowerTrader>(); }\n'
 '            if (powerTrader == null) { return; }\n'
 '            float desired = IsOpening && string.IsNullOrEmpty(failureKey) ? GateProps.openingPowerDrawWatts\n'
 '                : ((!IsOpening || IsAwaitingRecovery) && returnReserveStoredWattDays < GateProps.returnReserveCapacityWattDays\n'
 '                    ? ReserveChargePowerWattsThisTick() : GateProps.idlePowerDrawWatts);\n'
 '            if (Mathf.Abs(appliedPowerDrawWatts - desired) < 0.01f) { return; }\n'
 '            appliedPowerDrawWatts = desired;\n'
 '            powerTrader.PowerOutput = 0f - desired;\n'
 '        }\n'
 '\n'
 '        private float ReserveChargePowerWattsThisTick()\n'
 '        {\n'
 '            float remainingWattDays = GateProps.returnReserveCapacityWattDays - returnReserveStoredWattDays;\n'
 '            if (remainingWattDays <= 0f) { return 0f; }\n'
 '            float wattsForRemainingCapacity = remainingWattDays / CompPower.WattsToWattDaysPerTick;\n'
 '            return Mathf.Min(GateProps.reserveChargePowerWatts, wattsForRemainingCapacity);\n'
 '        }\n'
 '\n', ''))

for old, new in pairs:
    assert old in s, 'NOT FOUND :: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1)

# Every ApplyPowerDraw() call is now a call to a method that no longer exists.
s = s.replace('            ApplyPowerDraw();\n', '')
assert 'ApplyPowerDraw' not in s
assert 'returnReserveStoredWattDays' not in s
assert 'appliedPowerDrawWatts' not in s
assert 'flickable' not in s

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CompRimroomsGate.cs collapsed')

# The other file that called into the retired power draw.
p = 'src/RimroomsAsyncIndustries/Gate/PortalGateOpening.cs'
s = io.open(p, encoding='utf-8').read()
s = s.replace('            ApplyPowerDraw();\n', '')
assert 'ApplyPowerDraw' not in s
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('PortalGateOpening.cs call sites removed')
