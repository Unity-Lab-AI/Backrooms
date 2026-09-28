# Phase 2 development instrumentation

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Task:** master Phase 2 diagnostics and Phase 1 performance follow-up. **Features:** RR-COMPAT, RR-UI, RR-GATE, RR-SPACE, RR-EXP. **Inputs:** [benchmark plan](../research/PERFORMANCE_BENCHMARK_PLAN.md), [Core build/source record](PHASE_1_CORE_SOURCE_REVIEW.md), [state dictionary](../CAMPAIGN_STATE_DICTIONARY.md).

[RimroomsDiagnostics](../../src/RimroomsAsyncIndustries/Core/RimroomsDiagnostics.cs) is a bounded, opt-in in-process timer using framework `Stopwatch`. It is disabled by default and can be started/stopped/logged only through the developer-mode Activity controls. Its transient counters do not alter campaign outcomes, saved IDs, the mod list or launch behavior. The no-op disabled path returns a value-type scope without starting a stopwatch or allocating a buffer.

At most 16 category buffers exist, each holding 2,048 durations. Each scope accumulates full-window count/mean/max; snapshot percentiles refer to retained recent durations only. Snapshot construction/sorting occurs on explicit logging, not every tick/frame. CLR managed and process-private memory are separately labeled; both are observations for that process, not an attribution of all memory to Rimrooms.

Company/expedition/site/gate tick entry points and Operations draw use fixed categories. Generation and route validation scopes are described in the [destination implementation](PHASE_2_DESTINATION_IMPLEMENTATION.md). Instrumentation does not measure whole-game ticks, achieve a baseline, or prove any budget. The owner must launch the correct RimSort profile first, then the benchmark plan governs collection and interpretation.

**Acceptance outstanding:** compare counters against a profiler, check disabled overhead, verify enabled buffer bounds over long runs and confirm log accessibility through the attach-only bridge. No game or performance sample was run to create this file.

The separate developer Activity action **Write build, loaded order and coordinate identity to Player.log** records the loaded Rimrooms assembly's module ID, Core assembly version, native ordered package IDs/count, current tick, branch ID and coordinate seed/version/status/map/candidate/failure. Native `Game.InitNewGame` uses the same `LoadedModManager.RunningMods` / `PackageIdPlayerFacing` route (ignored `.local/inspection-agent/Verse.Game.cs`). This is an on-demand read, not a profile edit or automatic compatibility assertion. It records no bridge token or settings secrets. Package version/hash, RimSort and bridge version still come from the separate acceptance capture.
