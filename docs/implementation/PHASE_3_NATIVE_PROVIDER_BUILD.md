# Native provider integration checkpoint

This checkpoint follows [the native-provider task](PHASE_3_NATIVE_PROVIDER_TASK.md) and published [0.3.1 scenario baseline](PHASE_3_SCENARIO_PROVIDER_BUILD.md). The complete master TODO remains the objective.

**Subsequent owner clarification:** [connected colony portals](../CONNECTED_COLONY_PORTALS.md) supersede dispatch-only ordinary travel. This source supplies native infrastructure but still couples opening/travel to expedition records. It is not the required unified cross-map job/material system; that refactor and permanent natural portals remain implementation work.

## Integrated player route

The player explicitly designates an existing Core Door/Autodoor, CommsConsole, Battery and TableMachining in Operations. Native communication and bill behavior remain available. One installation assembly bill consumes 100 Steel and 8 ComponentIndustrial through native work. Calibration/operator jobs use the selected communications console. Native portal energy is withdrawn from the actual linked Battery; native grid generation and other consumers retain their own behavior. Shared charge is not protected reserve.

The existing expedition component owns dispatch, crew/cargo, saved sites, return and recovery. Old gate references and save keys are retained; newly designated native doors do not acquire old gate state or charge on load. Legacy custom gate buildings are hidden from new construction. The new company facility uses native providers and three wood generators, with disclosed initial fuel/charge and native loose supplies.

Existing Core HeatGlow supplies a restrained optional portal aura, with disable/reduced-motion settings, current-map/fog guards, no random gameplay draws and no new gameplay texture. Native door open/hold-open behavior is distinct from an expedition window. Automatic paint changes, wider optional-provider doors, upgrades and inside-start portals remain further work.

## Source review and preserved behavior

The integration review identified and addressed station reassignment during active assembly, suspended bills on explicit rebinding, native door components inherited by unsupported mod doors, actual rather than requested energy accounting, interrupted-debit recovery, and emergency access independent of a lost assembly bench/operator. Per-system implementation records own the final source details and remaining limitations.

Headquarters conduit placement now avoids an existing native transmitter footprint and calls `UpdatePowerNetsAndConnections_First()` to resolve queued connections. This does not run native power ticks, refill batteries or force consumers on. A physical conduit connects the third generator to the facility grid. Core's own ticks continue fuel use, power switching and battery charge/discharge.

## Build and acceptance

**0.4.0-dev** compiled successfully using `./tools/build.ps1 -NoRestore`: zero warnings/errors, .NET SDK 9.0.308, Release/net472, **69 source files and 71 approved package files**. DLL SHA-256: `5BDE6B78F46DF77B404E8D78DD6684313523E86F90FA4FC0725A154FEAA359C7`.

- [Compiler output](evidence/phase3-native-providers-2026-09-28/build-output.txt), [source manifest](evidence/phase3-native-providers-2026-09-28/source-manifest.json), [package manifest](evidence/phase3-native-providers-2026-09-28/package-manifest.json), [reference manifest](evidence/phase3-native-providers-2026-09-28/reference-manifest.json).
- [Staging receipt](evidence/phase3-native-providers-2026-09-28/staging-receipt.json): all 71 copied hashes matched; previous installation backed up; no profile change or game launch.
- Implementation records: [native gate](PHASE_3_NATIVE_GATE_IMPLEMENTATION.md), [binding UI](PHASE_3_NATIVE_GATE_UI.md), [native rooms](PHASE_3_ROOM_PROVIDER_REUSE.md).

Additional lead correction: Core `Building_Door.DoorPreDraw()` changes one-cell door rotation while rendering. Native entry now uses its saved bound orientation/position, so drawing the door cannot silently retarget or invalidate an active expedition approach. Moves and blocked approach cells remain explicit failures.

No game or tests have been run for this checkpoint. Later owner-launched RimSort acceptance must cover new and old saves, material bills, role links, actual energy, outages/EMP, interrupted debits, emergency/recovery, terrain/lighting/fog, vanilla building controls and the full profile. Source inspection or successful compilation will not close those gates. The newly required unified colony portal network remains separate unfinished implementation work.
