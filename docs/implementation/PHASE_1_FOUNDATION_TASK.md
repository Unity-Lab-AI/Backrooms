# Phase 1: build and package foundation

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Authorized:** owner requested beginning the mod build after Gate 0 closed, 2026-09-28. **Status:** compile/package/staging scope complete; runtime acceptance pending. See the [build record](PHASE_1_BUILD_RECORD.md). This task does not close the playable-campaign gate.

## Inputs and scope

- Master work: [Phase 1](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-1--repository-build-and-content-foundations).
- Features: `RR-COMPAT` package/build, `RR-UI` Operations entry, `RR-SCEN` inert save owner, `RR-ECO` future branch authority only, `RR-STYLE` original identity card.
- Core profile row 4: [review](../research/reviews/mods/official-4-Ludeon.RimWorld.md), [API/source route](../research/FIRST_SLICE_CORE_API_SOURCE_MAP.md), [pinned build](../research/RWT_AND_GRAVSHIP_FEASIBILITY.md#pinned-local-rimworld-test-target).
- Contracts: [state dictionary](../CAMPAIGN_STATE_DICTIONARY.md), [Operations actions](../OPERATIONS_ACTION_CONTRACTS.md), [architecture](../TECHNICAL_ARCHITECTURE.md), [identity decisions](../GATE_0_DECISIONS.md#d2-public-identity-package-identity-and-versioning), [RimSort staging](../research/RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md), [style](../research/VISUAL_AUDIO_STYLE_BRIEF.md).
- Owner boundaries: Core-only product references; no Harmony/RWT/DLC runtime references in this foundation; no active-profile changes; owner alone launches RimWorld. The full 295 product entries remain the first startup target, with bridge overlay counted separately.

## Deliverables and file ownership

The lead owns `src/`, `Mod/`, build/staging tools and canonical documentation. The delegated Core source reviewer owns only `PHASE_1_CORE_SOURCE_REVIEW.md` in this directory; it summarizes inspected method bodies without redistributing them. Decompiled files and downloaded inspection tooling stay in ignored `.local/`.

| Deliverable | Path | State owner / boundary |
| --- | --- | --- |
| C# project | [RimroomsAsyncIndustries.csproj](../../src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj) | One .NET Framework library; local game references never copied |
| Entry point | [RimroomsMod.cs](../../src/RimroomsAsyncIndustries/Core/RimroomsMod.cs) | Logging-only Mod constructor; no game/Def access before Def loading |
| Campaign foundation | [RimroomsCampaignComponent.cs](../../src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs) | Game-local component with forced schema version; no scenario activation, money grants, spawns or shared state |
| Package identity | [About.xml](../../Mod/Rimrooms%20-%20Async%20Industries/About/About.xml), [LoadFolders.xml](../../Mod/Rimrooms%20-%20Async%20Industries/LoadFolders.xml) | Exact title, Operator, chosen package ID, only the 1.6 content folder |
| Operations view | [MainTabWindow_Operations.cs](../../src/RimroomsAsyncIndustries/UI/MainTabWindow_Operations.cs), matching MainButtonDef and English text | Read-only view resolves current game when drawn; preserves native tabs |
| Build/stage tooling | [build.ps1](../../tools/build.ps1), [stage-mod.ps1](../../tools/stage-mod.ps1), saved reference/package manifests in the build record | Compile locally, copy own DLL only, stage only validated package into current RimSort Local Mods |
| Contributor/install guidance | [CONTRIBUTING.md](../../CONTRIBUTING.md), [BUILDING.md](../BUILDING.md), changelog, credits, migration and issue guidance | Distinguishes compilation from owner-launched runtime acceptance |

## Player route, refusal and recovery

The Operations main tab opens a readable information panel. A save without a company branch shows an inactive state and explains that company scenarios are not in this foundation. A missing campaign component or future schema shows an explicit unavailable state rather than initializing or replacing records. Native pawn/work/research controls remain available. No player-facing C# string bypasses localization.

No company-start button, purchasable object, research award, gate, expedition, scenario or RWT transfer is advertised as implemented by this task. The full campaign stays in the master TODO. Saved component fields establish a safe place for the later initializer; they do not authorize mid-save conversion.

## Acceptance evidence

During this task: actual compiler result against pinned references; hashes/versions of used references; package XML and localization/reference checks; package manifest/allowed-file list; confirmed RimSort configured local path; documented stage outcome; Git diff and link integrity. No unit/game tests are added or run as part of this foundation task.

After owner launch: visible mod entry and Operations label; no startup/Def errors; correct inactive UI; native tab navigation; inert save/load; no duplicate initialization or grants; Core-only and full-profile cases; baseline performance collection. These remain pending until observed through the approved harness. Any build or staging failure must leave a readable error and preserve the previous installed Rimrooms folder.
