"""Collapse the unreachable non-native gate branches, part 1: everything but the two core files.

Every edit here is a boolean identity applied to `IsNativeProvider`, which became a constant
true when RR_MachineGate was retired in 0.9.0-dev:

    true ? A : B   ==  A
    true && X      ==  X
    !true || X     ==  X
    if (!true) {}  ==  removed

So behaviour is unchanged by construction, not by judgement.
"""
import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:70]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('collapsed ' + path.split('/')[-1])

G = 'src/RimroomsAsyncIndustries/Gate/'
U = 'src/RimroomsAsyncIndustries/UI/'

patch(G + 'NativeGateBinding.cs', [
 ('public bool IsDesignated { get { return !IsNativeProvider || (NativeDoorProvider() && nativeBindingSchema == 1 && nativeDesignated); } }',
  'public bool IsDesignated { get { return NativeDoorProvider() && nativeBindingSchema == 1 && nativeDesignated; } }'),
 ('public Thing LinkedBattery { get { return IsNativeProvider ? nativeBattery : null; } }',
  'public Thing LinkedBattery { get { return nativeBattery; } }'),
 ('public Thing AssemblyBench { get { return IsNativeProvider ? nativeAssemblyBench : FindConsole(); } }',
  'public Thing AssemblyBench { get { return nativeAssemblyBench; } }'),
 ('                if (!IsNativeProvider) { return null; }\n', ''),
 ('            if (!IsNativeProvider || !NativeDoorProvider()) { return RefuseNative("UnsupportedProvider"); }\n            if (nativeBindingSchema != 1) { return RefuseNative("UnknownSchema"); }\n            if (IsOpening) { return RefuseNative("ActiveCannotRebind"); }',
  '            if (!NativeDoorProvider()) { return RefuseNative("UnsupportedProvider"); }\n            if (nativeBindingSchema != 1) { return RefuseNative("UnknownSchema"); }\n            if (IsOpening) { return RefuseNative("ActiveCannotRebind"); }'),
 ('other != null && other != this && other.IsNativeProvider && other.nativeDesignated &&',
  'other != null && other != this && other.nativeDesignated &&'),
 ('            if (!IsNativeProvider) { return RefuseNative("UnsupportedProvider"); }\n', ''),
 ('            if (!IsNativeProvider || !NativeDoorProvider()) { return "RR_NativeGate_UnsupportedProvider"; }',
  '            if (!NativeDoorProvider()) { return "RR_NativeGate_UnsupportedProvider"; }'),
 ('            if (!IsNativeProvider || NativeCampaign == null || !NativeCampaign.CanOperate ||',
  '            if (NativeCampaign == null || !NativeCampaign.CanOperate ||'),
])

patch(G + 'NativeGateKillSwitch.cs', [
 ('if (!IsNativeProvider || !NativeDoorProvider()) { return RefuseNative("UnsupportedProvider"); }',
  'if (!NativeDoorProvider()) { return RefuseNative("UnsupportedProvider"); }'),
])

patch(G + 'NativeGateServicing.cs', [
 ('{ get { return IsNativeProvider && IsDesignated && ServiceConditionTicks <= 0; } }',
  '{ get { return IsDesignated && ServiceConditionTicks <= 0; } }'),
 ('                return IsNativeProvider && IsDesignated && !IsOpening &&',
  '                return IsDesignated && !IsOpening &&'),
 ('                if (IsNativeProvider && !NativeElectricalAvailable()) { factor *= UnpoweredWearFactor; }',
  '                if (!NativeElectricalAvailable()) { factor *= UnpoweredWearFactor; }'),
 ('            if (!IsNativeProvider || !IsDesignated) { return; }', '            if (!IsDesignated) { return; }'),
 ('            if (!IsNativeProvider || !IsDesignated) { return null; }', '            if (!IsDesignated) { return null; }'),
])

patch(G + 'PortalGateOpening.cs', [
 ('                IsNativeProvider && CheckStationReadiness(assignedOperator).Success &&',
  '                CheckStationReadiness(assignedOperator).Success &&'),
 ('                !IsNativeProvider || !IsDesignated || portalOwnerFault ||',
  '                !IsDesignated || portalOwnerFault ||'),
 ('                !string.IsNullOrEmpty(activeExpeditionId) || !IsNativeProvider)',
  '                !string.IsNullOrEmpty(activeExpeditionId))'),
])

patch(G + 'GateSpinUp.cs', [
 ('            if (portalOwnerFault || !IsNativeProvider || !IsDesignated)',
  '            if (portalOwnerFault || !IsDesignated)'),
])

patch('src/RimroomsAsyncIndustries/Portals/PortalAddressService.cs', [
 ('            if (gate == null || gate.parent == null || !gate.IsNativeProvider || !gate.IsDesignated ||',
  '            if (gate == null || gate.parent == null || !gate.IsDesignated ||'),
])

patch('src/RimroomsAsyncIndustries/Presentation/NativePortalPresentation.cs', [
 ('            if (gate == null || !gate.IsNativeProvider || !gate.IsDesignated ||',
  '            if (gate == null || !gate.IsDesignated ||'),
])

patch(U + 'OperationsPortalNetwork.cs', [
 ('            if (gate != null && gate.IsNativeProvider && gate.IsDesignated)',
  '            if (gate != null && gate.IsDesignated)'),
 ('            if (gate == null || !gate.IsNativeProvider || !gate.IsDesignated)',
  '            if (gate == null || !gate.IsDesignated)'),
])

patch(U + 'OperationsGateBinding.cs', [
 ("""                selectedGate = recordedGate;
                if (!gate.IsNativeProvider)
                {
                    listing.Label("RR_NativeGate_LegacyRunLocked".Translate(activeRun.ExpeditionId));
                    if (recordedGate.Spawned && listing.ButtonText("RR_NativeGate_InspectGate".Translate()))
                    { CameraJumper.TryJumpAndSelect(recordedGate); }
                    listing.GapLine();
                    return;
                }
                SetNativeBindingTarget(gate, gate.IsOpening);""",
  """                selectedGate = recordedGate;
                SetNativeBindingTarget(gate, gate.IsOpening);"""),
 ("""            if (!gate.IsNativeProvider)
            {
                listing.Label("RR_NativeGate_LegacyProvider".Translate());
                listing.GapLine();
                return;
            }

""", ""),
 ('                    door.TryGetComp<CompRimroomsGate>()?.IsNativeProvider == true)',
  '                    door.TryGetComp<CompRimroomsGate>() != null)'),
])

patch(U + 'OperationsExpeditions.cs', [
 ('                selectedGate.TryGetComp<CompRimroomsGate>()?.IsNativeProvider != true)',
  '                selectedGate.TryGetComp<CompRimroomsGate>() == null)'),
 ("""            listing.Label((gate != null && gate.IsNativeProvider
                ? "RR_NativeGate_MachineInstructions" : "RR_UI_MachineInstructions").Translate());
            if (gate == null) { listing.Label("RR_NativeGate_NoSelectedGate".Translate()); return; }
            if (!gate.IsNativeProvider) { listing.Label("RR_NativeGate_LegacyControls".Translate()); }
            else if (!gate.IsDesignated) { listing.Label("RR_NativeGate_BindBeforeOperation".Translate()); return; }
            if (listing.ButtonText("RR_UI_SelectMachine".Translate())) { CameraJumper.TryJumpAndSelect(gate.parent); }
            listing.Label(gate.CompInspectStringExtra());
            if (!gate.IsNativeProvider && listing.ButtonText("RR_UI_SelectConsole".Translate()) && gate.Console != null)
            { CameraJumper.TryJumpAndSelect(gate.Console); }""",
  """            listing.Label((gate != null
                ? "RR_NativeGate_MachineInstructions" : "RR_UI_MachineInstructions").Translate());
            if (gate == null) { listing.Label("RR_NativeGate_NoSelectedGate".Translate()); return; }
            if (!gate.IsDesignated) { listing.Label("RR_NativeGate_BindBeforeOperation".Translate()); return; }
            if (listing.ButtonText("RR_UI_SelectMachine".Translate())) { CameraJumper.TryJumpAndSelect(gate.parent); }
            listing.Label(gate.CompInspectStringExtra());"""),
 ('            if (gate == null || !gate.IsNativeProvider || !gate.IsDesignated)',
  '            if (gate == null || !gate.IsDesignated)'),
])

patch(G + 'CompRimroomsGateConsole.cs', [
 ('            return NativeProvider && parent.Spawned && parent.Faction == Faction.OfPlayer &&',
  '            return parent.Spawned && parent.Faction == Faction.OfPlayer &&'),
 ('            if (!NativeProvider || linkedGate != expectedGate || HasAssemblyJob) { return false; }',
  '            if (linkedGate != expectedGate || HasAssemblyJob) { return false; }'),
 ('            if (!NativeProvider) { EnsureAssemblyBill(); }\n', ''),
 ('            if (NativeProvider && Gate == null) { return; }', '            if (Gate == null) { return; }'),
 ('                if (NativeProvider && Gate != null) { existing.suspended = Gate.AssemblyComplete; }',
  '                if (Gate != null) { existing.suspended = Gate.AssemblyComplete; }'),
])
print('part 1 complete')
