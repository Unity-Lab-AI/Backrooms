# Native portal and room implementation task

**Baseline:** published commit `5e8215cb4fb955bb329e64b7d0e3a8b6217f5886`, compiled/staged 0.3.1-dev. Previous goal turn made progress through scenario implementation, compilation, staging and both verified remote cascades. The complete mod remains the objective.

## Contracts and ownership

Read [portal/scenario contract](../SCENARIO_SETUP_AND_PORTAL_NETWORK.md), [gate migration impact](NATIVE_GATE_MIGRATION_IMPACT.md), [room review](PHASE_3_ROOM_PROVIDER_REUSE.md), [content reuse](../CONTENT_REUSE_POLICY.md), [regression containment](../REGRESSION_CONTAINMENT.md) and [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md). Features RR-GATE, RR-EXP, RR-SPACE, RR-FAC, RR-SCEN, RR-COMPAT.

- Core gate agent: `Gate/CompRimroomsGate.cs`, optional new binding helper and own implementation record. Preserve the existing gate API and saved keys; add dormant native-provider bindings and actual energy accounting.
- Room agent: `Generation/GenStep_BackroomsDestination.cs`, `FailedSiteRecovery.cs`, `RoomContentBuilder.cs` and room record. Preserve existing saved maps and route/evidence/fog ownership.
- UI agent: `UI/OperationsGateBinding.cs`, `OperationsExpeditions.cs`, native gate keyed XML and its implementation record. Explicit selection and visible recovery; preserve old run controls.
- Lead: station/bill/job integration, exact-provider XML patches, headquarters layout, facilities classification, task/design/TODO updates, compilation and full-batch publication.

Core providers are exact native Defs, not copied content. Source correction: the machining table is **TableMachining**, verified in installed Core `ThingDefs_Buildings/Buildings_Production.xml`; `MachiningTable` is not its DefName. Patches target Door/Autodoor individually, not DoorBase or every third-party door. Optional wider doors remain later adapter work.

## Invariants and deliberate changes

The expedition component retains ownership of people, transfers, site identity and closure. Existing gate references and old save keys remain readable. Native station roles require explicit player selection; ordinary doors/consoles/workbenches remain native until selected. Calibration/operator jobs target the selected communications console. Material assembly uses the selected existing TableMachining and native ingredient/work consumption; an active assembly job prevents unlinking its provider.

Native portal energy comes from the actual designated Battery. Preserve native door/console power demand, grid charging and stored-energy ownership. Network consumers can drain the shared reserve; never promise protected power or create a virtual replacement. Binding, opening, recovery and emergency paths must preflight and preserve operation receipts without duplicate cost/grants.

New headquarters uses an actual Autodoor, CommsConsole, TableMachining, three WoodFiredGenerator objects and the existing Battery. The starting generators' fuel is part of the fixed facility manifest; loose editable WoodLog supplies remain separately native-owned. Legacy custom gate objects remain loadable but are hidden from new construction. Existing saves are not silently rewritten.

## Completion queue

- [x] Native provider binding, active-window energy and recovery source integrated.
- [x] Station/bill/operator/UI and native scenario references integrated together.
- [x] New generated room fixtures/floors and failure-recovery provider lists integrated.
- [x] Exact provider source, saved-field changes, deliberate behavior changes and remaining limitations recorded.
- [x] Integrated compilation and package evidence saved; only evidenced TODO increments checked.
- [ ] All current project source/docs/evidence committed together and both remote cascades verified.

No game launch or tests in this task. Later owner-launched acceptance covers plain/automatic door rotation and locks, native bills/comms, shared power loss/EMP, repeated operation receipts, active and legacy run recovery, save/reload, floor/lighting/fog and all preserved company functions. Source/build evidence does not close those gates.

Source/build checks above are supported by [the 0.4.0 checkpoint](PHASE_3_NATIVE_PROVIDER_BUILD.md). The latest [connected-colony contract](../CONNECTED_COLONY_PORTALS.md) requires a subsequent portal ownership/job-routing refactor; those broader features remain unimplemented, and no runtime acceptance is claimed.
