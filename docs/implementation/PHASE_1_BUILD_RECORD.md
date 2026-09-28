# Foundation 0.1.0: build and staging record

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Date:** 2026-09-28. **Result:** source compiled and the separate package staged. **Runtime result:** none; RimWorld was not launched. This is a private foundation, not a playable campaign or compatibility release.

## Task and source chain

The [foundation task](PHASE_1_FOUNDATION_TASK.md) implements the repository/package portion of [Phase 1](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-1--repository-build-and-content-foundations). [Core row 4](../research/reviews/mods/official-4-Ludeon.RimWorld.md) and the [method-body review](PHASE_1_CORE_SOURCE_REVIEW.md) supply the exact bootstrap/component/Scribe/MainButton routes. Owner decisions and full game/lore/style contracts remain linked through the [feature map](../FEATURE_TRACEABILITY.md) and [source register](../SOURCE_REGISTER.md).

| Feature route | Actual files | Implemented boundary |
| --- | --- | --- |
| RR-COMPAT | [project](../../src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj), [bootstrap](../../src/RimroomsAsyncIndustries/Core/RimroomsMod.cs), [build tool](../../tools/build.ps1), [stage tool](../../tools/stage-mod.ps1) | Core references only; one logging entry point; pinned build, package manifest and scoped staging |
| RR-SCEN / future RR-ECO | [campaign component](../../src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs), [save policy](../SAVE_MIGRATION_POLICY.md) | Schema 1 and nullable branch/scenario identifiers; inactive constructor; no initialization, money, transactions, objects or research grants |
| RR-UI | [window](../../src/RimroomsAsyncIndustries/UI/MainTabWindow_Operations.cs), [Def](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/MainButtonDefs/RR_MainButtons.xml), [English keys](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_Operations.xml), [Def text](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/DefInjected/MainButtonDef/RR_MainButtons.xml) | Read-only status plus guarded native Work/Research routing; no company commands |
| RR-STYLE | [original card](../../Mod/Rimrooms%20-%20Async%20Industries/About/Preview.png), [drawing source](../../tools/render-preview.ps1), [production brief](../research/VISUAL_AUDIO_STYLE_BRIEF.md#existing-content-bindings-and-presentation), [provenance](../research/provenance-register.csv) | Original 960 × 540 mod-list identity card; no main-menu slideshow or scene art |

## Compiler and package evidence

The initial dependency restore produced the committed lock file. `./tools/build.ps1 -NoRestore` and then the ordinary `./tools/build.ps1` both succeeded against the inspected local game references. The final ordinary command performed **locked restore + Release compilation: 0 warnings, 0 errors** using .NET SDK **9.0.308**, C# **7.3**, selected target **net472**. See [BUILDING.md](../BUILDING.md) for reproduction and framework limitations.

- [Reference manifest](evidence/phase1-foundation-2026-09-28/reference-manifest.json): exact Core/Unity/framework context hashes and assembly versions; `GameplayVerified` is false.
- [Package manifest](evidence/phase1-foundation-2026-09-28/package-manifest.json): **8 files**, with byte sizes and hashes. The built DLL is **8,704 bytes**, SHA-256 `02E02892D0D67A0F8BFBADD448D5560F0512B4BF361763D8C7DEADAACBE79A9D`.
- Build tooling parsed all packaged XML, enforced exact title/author/package ID, matched project/package versions and enforced the explicit eight-file allowlist. Local game assemblies, reference packages, decompiled text, debug symbols, sources, docs and private settings are absent from the package.
- [Static binding inspection](evidence/phase1-foundation-2026-09-28/source-bindings.json) matched `RR_Operations` to the concrete compiled window, all **11** C# translation keys to English entries and both DefInjected entries to the main-button label/description. This is a source/XML binding review, not runtime Def loading.
- [Reference-integrity audit](evidence/phase1-foundation-2026-09-28/reference-integrity.json) passed across the updated document links, 294 review/register rows, 3,234 shared workbook cells, relationship records and story routes. Gate 0 retains zero open boxes. The dated Gate 0 evidence was preserved separately.
- The original preview was rendered and visually inspected. It says foundation build and does not present concept art as implemented gameplay. Its path/license/source are recorded separately.
- No unit tests or game tests were added or run. No executable RimWorld process was started or attached.

## RimSort staging evidence

The current RimSort instance was read from `%LOCALAPPDATA%/RimSort/settings.json`: **Default**, game folder `C:\Program Files (x86)\Steam\steamapps\common\Rimworld`, Local Mods `C:\Program Files (x86)\Steam\steamapps\common\Rimworld\Mods`. These are dated machine observations; the tool resolves settings again on each invocation.

`./tools/stage-mod.ps1` succeeded. Destination:

```text
C:\Program Files (x86)\Steam\steamapps\common\Rimworld\Mods\Rimrooms - Async Industries
```

The destination did not already exist. All **8 installed file hashes** matched the successful build. See the [staging receipt](evidence/phase1-foundation-2026-09-28/staging-receipt.json). The tool did not edit profiles/settings, reorder mods, activate Rimrooms or start a game. RimSort discovery/UI display itself remains unobserved until the owner refreshes it.

## Saved-state and recovery boundary

Core creates the game component for normal colonies too. All fields remain inert without the later explicit scenario initializer. The window re-resolves the current game each draw and handles absent component, inactive branch and unsupported schema. Native navigation uses the target worker's guarded activation route. The constructor and drawing path contain no grants, spawns, state initialization or repeated tick work.

Unsupported-schema text warns against re-saving with this build. It is not a forward-compatible serializer; unknown future fields cannot be retained automatically. Follow the [save policy](../SAVE_MIGRATION_POLICY.md). Build/staging failures report their boundary, and replacement staging preserves the old own-package directory before copying.

## Remaining Phase 1 acceptance

The owner still needs to capture the 295-entry target and separate bridge overlay in RimSort and launch the first disposable full-profile session. After that, record the actual loaded versions/order, Def/assembly errors, Operations visibility and localization, UI scale/scrolling, inactive ordinary-save behavior, native Work/Research navigation and save/reload. Core-only and other focused profiles follow that first full-target startup. Baselines and counters follow the [performance plan](../research/PERFORMANCE_BENCHMARK_PLAN.md); no timings or compatibility results are claimed here.

## Next work

1. Continue source inspection for scenario startup, pawn/stock creation and deep/reference Scribe paths in the [Core API map](../research/FIRST_SLICE_CORE_API_SOURCE_MAP.md). Keep ordinary saves inactive.
2. Implement the accepted Async Industries initializer and the complete campaign state/transaction foundation from [scenario](../SCENARIOS.md), [first playable](../FIRST_PLAYABLE_CONTRACT.md), [state](../CAMPAIGN_STATE_DICTIONARY.md) and [economy](../CAMPAIGN_ECONOMY_MODEL.md) contracts. Create a new task record before adding fields or content. Company USD must stay separate from physical silver.
3. Build gate → bounded seeded destination → expedition → extraction → evidence analysis, following the [first-slice inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [actions](../OPERATIONS_ACTION_CONTRACTS.md), [procedural contract](../PROCEDURAL_SPACE_CONTRACT.md), source/mod interaction map and master TODO. Add original assets only as their feature is implemented.
4. Retain all 294 review routes and optional DLC/RWT boundaries. No optional adapter or later scenario is implied by this package. The full campaign and menu showcase remain planned work.

A staged foundation allows owner-launched acceptance when requested; it does not close the first-playable gate or require the owner to test before further independent source/design work.
