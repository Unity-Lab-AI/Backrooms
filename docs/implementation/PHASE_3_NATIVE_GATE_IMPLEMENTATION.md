# Native door portal foundation implementation

Task started 2026-09-28. Baseline `5e8215c`, `0.3.1` development checkpoint. Features RR-GATE/RR-FAC/RR-EXP/RR-COMPAT. Read the [migration impact](NATIVE_GATE_MIGRATION_IMPACT.md), [portal contract](../SCENARIO_SETUP_AND_PORTAL_NETWORK.md), [regression containment](../REGRESSION_CONTAINMENT.md) and pinned Core row 4 source. This task owns only `Gate/CompRimroomsGate.cs`, new `Gate/NativeGateBinding.cs`, and this record. Lead owns console/jobs/XML/scenario; UI agent owns binding controls. No tests, game, builds, Git or profile changes in this scope.

State remains on the original gate component/Thing, with appended native binding schema, branch ID, exact console/battery/assembly-bench references and threshold-side identity. Existing expedition refs, opening/recovery/time-debit receipts and legacy numeric reserve retain their meaning. Native doors remain dormant until explicit binding; native charge belongs to Core's actual Battery. Intended energy route: direct actual Battery withdrawal for normal opening ticks and accepted emergency/recovery operations; no native PowerOutput replacement, virtual recharge or energy copying from legacy gates. Shared network loads can consume that battery, so emergency energy is explicitly non-exclusive.

## Implemented source

- [CompRimroomsGate.cs](../../src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs) remains the authoritative public component. It now has an opt-in native provider route while retaining legacy assembly/calibration, operator, timer, emergency, latest-closed recovery and operation receipt APIs.
- [NativeGateBinding.cs](../../src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs) supplies the new partial component: explicit native links, branch/entry validation, actual battery debit, interrupted-debit receipt and saved state. The lead owns native Def patches and console/assembly hooks; the UI agent owns [OperationsGateBinding.cs](../../src/RimroomsAsyncIndustries/UI/OperationsGateBinding.cs) and its keyed text.
- Supported bindings are exact existing Core `Door` or `Autodoor`, `CommsConsole`, `Battery`, and **`TableMachining`**. The latter is the actual Core Def name, not `MachiningTable`. Unsupported descendant Defs that inherit an added component remain dormant and do not emit a provider error merely because they inherited it. Their presence does not establish an adapter.
- An ordinary native door has no Rimrooms inspect text, gizmos, charging, active ticking work or assembly until explicitly designated. Binding validates actual spawned player-owned objects in the company's headquarters, branch identity, a standable threshold-side cell and exclusive infrastructure references. It never substitutes the nearest provider. New links are preflighted and established before old links are removed; unexpected failure attempts rollback and reports interruption. Active assembly work prevents unlinking its bill giver.
- Native assembly remains the lead's physical native bill at the selected `TableMachining`. Completion validates that exact bench/gate/branch identity; an unrelated blocked entry, lost console or battery does not discard already completed material work. Rebinding preserves paid assembly and existing operation receipts, but requires recalibration and a stable powered interval. Explicitly repeating the same binding may restore a missing assembly bill without repeating already completed assembly.
- The selected actual CommsConsole remains the operator/calibration target. Native communications remain its own behavior. The gate never writes a native door/console's `PowerOutput`, forces door opening, replaces native access rules, or infers a portal window from the door's `Open` state. The lead's native aura helper is called from the designated native tick; cosmetic failure stays presentation-owned.

## Native energy accounting

The designated `Battery` is the only native energy store. Normal opening consumes `openingPowerDrawWatts * CompPower.WattsToWattDaysPerTick` from its actual `CompPowerBattery.DrawPower(float)` each successful normal tick. No native `AddEnergy`/`SetStoredEnergyPct` call is made; Core's network supplies charging, self-discharge and other consumers. Normal idle and emergency waiting introduce no fictitious Rimrooms idle/charging load. Native door, CommsConsole and other building loads remain Core-owned.

The initial readiness quote requires the configured entire normal-window energy plus one emergency-return cost. Recovery additionally requires its existing configured activation cost, which is debited once before recording its successful recovery operation. At current defaults, 833 ticks at 3,500 W cost about 48.59 Wd; the normal readiness total is about 49.59 Wd and recovery total about 50.59 Wd. These are editable balance values from the existing comp properties, not extra virtual capacity. `ReturnReserveStoredWattDays` and capacity now report the actual linked Battery for native providers; legacy gates retain their old numeric-capacitor meaning.

An Autodoor must have its own native power trader on the same actual network as the linked battery and CommsConsole. A manual Door has no native trader, so it requires a live transmitter/conduit at the threshold on that network. Normal work requires the powered, unbroken CommsConsole, usable threshold/battery circuit and stable-power interval. A reference to the assembly workshop remains validated for normal operation, but its native bill handles its own work-power requirements.

**Shared energy is non-exclusive.** Other connected loads can consume the Battery. A normal tick will not deliberately spend below the configured emergency cost, but this does not reserve charge against Core or other mods. If energy or infrastructure fails, the existing bounded emergency window begins. Emergency payment checks only the original branch/door, saved entry, actual Battery and threshold circuit; operator absence and console/workshop loss do not independently prevent return. Battery/threshold destruction, disconnect, EMP, breakdown, an unavailable entry, or map-wide electricity disable can still prevent payment. The expedition owner retains the crew/site and subsequent explicit recovery route.

Every actual withdrawal is compared using observed `before - after` energy; a small float-representation tolerance is permitted. An exception, nonfinite/negative change or material amount mismatch saves a fault with operation ID, Battery reference, tick, requested amount and cumulative observed amount. The fault stops further native payments/binding mutations until a visible acknowledgment. Acknowledgment never refunds/refills; retrying that same operation can pay only its remaining unobserved amount. A later distinct operation archives the acknowledged observed loss without crediting it to that operation. A nonfinite observation cannot be retried as a known paid amount. The current unresolved record is retained, while acknowledged historical records are capped at 32; the cumulative observed debit total remains saved.

## Additive integration API

All prior public gate methods/properties retain their signatures. New API on `CompRimroomsGate`:

```text
bool IsNativeProvider, IsDesignated, OppositeEntrySide
Thing LinkedBattery, AssemblyBench                 (Console remains the existing Thing property)
string NativeBindingFailureKey
float NativeEnergyRequiredToOpenWattDays, RecoveryEnergyRequiredWattDays
double NativeEnergyDrawnWattDays
CompanyActionResult BindNativeInfrastructure(Thing console, Thing battery, Thing assemblyBench, bool oppositeEntrySide = false)
CompanyActionResult ClearNativeBinding()
bool HasNativeEnergyDebitFault
string NativeDebitOperationId
float NativeDebitRequestedWattDays, NativeDebitObservedWattDays
CompanyActionResult AcknowledgeNativeEnergyDebit()
```

`IsDesignated` is false on a newly patched native door and true on legacy providers. New dispatch must choose a native designated gate; historical runs still use their saved original gate reference. `IsOpening` means an active expedition ID remains, including emergency/recovery waiting, not merely a pawn staffing the console. Bind/clear refuse active openings. After an expedition owner closes a stranded gate, damaged console/battery/workshop links can be repaired explicitly while keeping the gate's saved entry side, position and rotation. Changing that entry or clearing the entire binding is refused while a nonterminal run references it.

Refusal/status keys use `RR_NativeGate_`: `UnsupportedProvider`, `UnknownSchema`, `ActiveCannotRebind`, `HeadquartersRequired`, `EntryBlocked`, `EntryLocked`, `ProviderAlreadyBound`, `AssemblyInProgress`, `BindingInterrupted`, `NotBound`, `LinkMissing`, `Disconnected`, `PowerUnavailable`, `OpeningEnergyLow`, `RecoveryEnergyLow`, `ReturnEnergyUnavailable`, `EnergyDebitFault`. `PowerReadout` receives actual stored Wd, capacity Wd, current portal drain W, normal readiness Wd and recovery readiness Wd. Keyed definitions are UI/lead-owned.

## Save and regression containment

New native schema is 1. Appended keys store designation, branch ID, exact infrastructure references, chosen entry side, bound door position/rotation, last processed tick, cumulative observed energy, opening sequence and current/history debit faults. No load path creates a provider, restores energy, completes material work, recalibrates or pays an operation. `nativeLastProcessedTick` prevents duplicate native tick payment within the same saved game tick. Legacy gate keys and reserve/timer/receipt meanings remain unchanged; legacy active/stranded runs are not retargeted to a new door. Unbinding keeps paid assembly and old operation histories on that original door.

The source comparison covered existing `CanOpen`/`BeginOpening`, normal ticking, `SpendOpeningTicks` and receipt lookup, emergency payment, `CanRecover`/`BeginRecoveryOpening`, `CloseOpening`, operator/calibration and native bill completion. The parent handles the connected expedition selection/entry capture, scenario/provider lists, jobs, UI and XML in the same integrated wave. Provider replacement is not complete until those integrations and the recorded runtime cases succeed.

## Source basis and exact limits

Pinned Core row 4 `Assembly-CSharp.dll` SHA-256: `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. Local ILSpy `9.1.0.7988`; inspected types under ignored `.local/inspection-work/native-gate-review/`: `RimWorld.CompPowerBattery`, `RimWorld.CompPower`, `RimWorld.PowerNet`, `RimWorld.CompPowerTrader`, `RimWorld.Building_Door`, `RimWorld.Building_CommsConsole`, and `Verse.Rot4`. Confirmed Battery `StoredEnergy`, `Props.storedEnergyMax`, `StunnedByEMP`, `DrawPower(float)`, power `PowerNet` and `TransmitsPowerNow`, and rotation `FacingCell`/`Opposite`/`AsInt`. `DrawPower` directly subtracts float energy and clamps an overdraw; the implementation checks availability first and reads the result. Core's Battery tick self-discharges and the native network charges/discharges batteries independently.

Reproduce a bounded type inspection without running the game:

```powershell
$managedDir = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
& .local/tools/ilspycmd.exe -r $managedDir -t Verse.Rot4 (Join-Path $managedDir 'Assembly-CSharp.dll') |
  Set-Content -Encoding utf8 '.local/inspection-work/native-gate-review/Verse.Rot4.cs'
```

This assignment performed source/API review and wrote original implementation only. No compilation, tests, game run, staging, Git publication or profile change was performed. The lead owns integrated compile evidence and master TODO source checkmarks. This is one native Core foundation, not larger doorway/provider support, dynamic power-driven research upgrades, a gate network, or three completed scenario starts.

Future owner-launched cases: ordinary door/comms/workshop untouched; explicit binding and exclusivity; all threshold orientations and forbidden/locked approach; real grid charge/drain and low power; no native `PowerOutput` replacement; operator loss, destroyed control/workshop versus destroyed battery/circuit, EMP and solar flare; bounded emergency/stranding/relief and same-site recovery; duplicate opening/time/recovery/payment calls; anomalous partial debit acknowledgment/retry; save/load in each transaction state; old legacy active/stranded/completed saves; rebind after loss without repeated materials; assembly completing while entry becomes blocked; return-entry identity; and complete scenario → company → dispatch → return → analysis/payment → revisit regression. No runtime result or compatibility pass is claimed.
