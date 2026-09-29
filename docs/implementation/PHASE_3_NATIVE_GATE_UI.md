# Phase 3 native gate binding UI

**Status:** Source handoff for integrated compilation. This task did not build the package or launch RimWorld; UI behavior, save migration, and runtime power interactions remain unverified.

## Player route and scope

Operations → Machine (pane 7) now contains the native infrastructure panel. With no open expedition, the player explicitly selects a player-owned Core `Door` or `Autodoor` on the current company headquarters map. The player then selects the exact existing Core `CommsConsole`, `Battery` (`CompPowerBattery`), and `TableMachining` (`Building_WorkTable`) to use. Candidate selection is local to that headquarters map, lists the actual building location, and provides inspect/jump actions. It never picks a nearest door or infrastructure building. The panel displays branch identity and headquarters map ID before the binding action.

Saving calls `CompRimroomsGate.BindNativeInfrastructure(console, battery, assemblyBench, oppositeEntrySide)`; clearing calls `ClearNativeBinding()`. The gate service remains authoritative for branch/map ownership, link uniqueness, powered-network connection, threshold approach validation, assembly jobs, saved-run locks, and failure reasons. The UI reports those failure keys. Candidate selection itself creates no building, energy, cargo, or company transaction.

## Existing runs and portal state

`CurrentGate` resolves `ExpeditionRecord.Gate` whenever an expedition is active, including a stranded one, and never substitutes the selected door. A legacy expedition remains attached to its old provider with its existing gate and recovery controls. A native expedition remains attached to its saved native door; the approach side is shown as locked. Once its opening is closed, the player can repair links on that same door if the gate service allows the specific change. Clearing the designation appears only with no active expedition.

New dispatch is available only when a selected native provider is designated. The UI distinguishes the Rimrooms portal window from ordinary Core door `Open`/`HoldOpen` state. It shows actual battery charge/capacity and configured opening/emergency/recovery energy requirements. Copy explicitly says the battery is shared on its power network and can be drained by other consumers; the UI promises neither exclusive energy nor guaranteed emergency power.

If a native energy debit is unresolved, the UI displays its operation ID and requested/observed watt-days. Acknowledge records review only; it does not refill the battery or refund the company. English labels for the portal aura and reduced-motion settings are also present in the new keyed file because settings now read those keys.

## Files

- [OperationsGateBinding.cs](../../src/RimroomsAsyncIndustries/UI/OperationsGateBinding.cs) implements explicit gate and role selectors, binding/clearing, inspection links, and energy-debit review.
- [OperationsExpeditions.cs](../../src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs) wires the Machine and Dispatch panes to explicit selection and the saved expedition gate.
- [RR_NativeGate.xml](<../../Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_NativeGate.xml>) contains user-facing setup, refusal, power, portal-state, debit-review, and settings text.
- [NativeGateBinding.cs](../../src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs) owns the called gate/link/energy APIs; this UI change does not alter that service.
- [NATIVE_GATE_MIGRATION_IMPACT.md](NATIVE_GATE_MIGRATION_IMPACT.md) preserves the source-backed integration limits and save boundary.

## Remaining acceptance

Integrated build and owner-launched game checks still need to verify actual candidate filtering, layout at supported UI sizes, inspection/jump behavior, both door orientations, binding/refusal cases, native and legacy active/stranded saves, and controlled interrupted-battery-debit acknowledgment. Source inspection does not establish those runtime results.
