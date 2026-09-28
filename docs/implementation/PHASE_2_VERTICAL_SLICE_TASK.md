# Phase 2: Async Industries playable loop

**Authorized:** 2026-09-28, owner directed continued implementation through the complete mod. **Status:** in progress. The full completion objective remains active; this task is the next dependency in the [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-2--code-architecture-and-safe-vertical-slice).

## Inputs and boundary

- Feature IDs: RR-SCEN, RR-FAC, RR-STA, RR-ECO, RR-MSN, RR-GATE, RR-EXP, RR-SPACE, RR-EVD, RR-THREAT, RR-UI, RR-STYLE, RR-COMPAT.
- Canonical player contracts: [scenario](../SCENARIOS.md), [first playable](../FIRST_PLAYABLE_CONTRACT.md), [content inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [economy](../CAMPAIGN_ECONOMY_MODEL.md), [state ownership](../CAMPAIGN_STATE_DICTIONARY.md), [actions](../OPERATIONS_ACTION_CONTRACTS.md), [procedural spaces](../PROCEDURAL_SPACE_CONTRACT.md), [threat sheets](../THREAT_DESIGN_SHEETS.md), [tutorial](../TUTORIAL_SCRIPT.md), [style](../research/VISUAL_AUDIO_STYLE_BRIEF.md).
- Exact source input: Core row 4, package `Ludeon.RimWorld`, installed Assembly-CSharp SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. Rechecked 307 pinned hashes with no unexplained change. [Core review](../research/reviews/mods/official-4-Ludeon.RimWorld.md), [API map](../research/FIRST_SLICE_CORE_API_SOURCE_MAP.md), [interaction map](../research/FIRST_SLICE_MOD_INTERACTION_MAP.md).
- Source/style attribution: the scenario, facility arrangement, equipment, AI-01, Borrowed Corridor and Quiet Pursuer are original game design. The linked fan notes supply inspiration, not exact mechanics or copied content.
- Core-only first slice. No Harmony, DLC or optional-mod assembly dependency. Preserve normal pawn/jobs/items and native UI. No live shared maps, copied third-party files, scenario grants on ordinary saves, or automatic cash from physical events.

## File ownership and delegation

The lead owns campaign records/services, integration, package allowlist, versioning and canonical document updates. Three bounded Core row-4 source assignments inspect independent API routes: scenario/start/map setup; destination generation/map transitions; and powered buildings/work/jobs/research. Each owns its distinct source-review document only until the lead assigns a concrete implementation interface. Decompiled reference text stays in ignored `.local/`. Agents report source facts, proposed routes and unresolved risks; no game launches or tests are delegated.

Implemented directories: `src/RimroomsAsyncIndustries/Scenario/`, `Gate/`, `Expedition/`, `Generation/`, `Investigation/`, `Threats/`, `Audio/`, and extensions to `Company/`, `Core/` and `UI/`. Current package content lives under `1.6/Defs/`, `Languages/English/`, `Textures/` and `Sounds/`; see the explicit [package allowlist](../../tools/package-files.json). The [current build record](PHASE_2_BUILD_RECORD.md) routes every subsystem to its implementation, original assets and source evidence.

## Ownership, action and recovery

The branch owns its stable identity, scenario/init receipt, USD ledger, staff links, coordinate/case/contract/project records and expedition manifest. Physical objects retain RimWorld ownership and reference serialization. The gate owns operation state; the destination owns its saved map. View code calls services and never owns simulation state.

Player route: select Async Industries → inspect facility/staff and funding → assemble and staff the machine → inspect power/gear/return readiness → dispatch to saved AI-01 → survey, encounter and recover evidence → extract → analyze through staffed work → settle the quoted contract once → research/revisit. Invalid inputs refuse before spending/moving pawns. Interruptions, missing objects, power loss, failed generation and expired windows retain records and a visible recovery route.

## Completion evidence

Save source reviews, compiler results, static Def/language/asset checks, package/reference manifests and staging outcome with source paths and feature IDs. Keep old schema-1 saves inactive through an explicit migration. Record newly written fields and stable IDs in the save policy. Do not mark the gameplay gate passed from compilation.

Runtime acceptance remains the owner's RimSort-launched full target followed by focused cases, with RimBridgeServer attached only afterward. Needed observations include one-time initialization, physical stock totals, operator/work/power checks, generation/return reachability, item/pawn identity, evidence/reward idempotency, save/load/revisit, threat counterplay, UI accessibility and performance. No active profile may be changed or game launched by an agent.
