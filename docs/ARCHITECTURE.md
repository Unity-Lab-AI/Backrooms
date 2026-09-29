# ARCHITECTURE

> Rimrooms - Async Industries — a RimWorld 1.6 company-management campaign about operating a facility that opens, investigates and profits from unstable spaces beyond a machine gate.
> Unity AI Lab — Gee, Red, Sponge, Alfreddo

### Credits

- **GFourteen (Gee)** — Co-founder · Engineer · Financial Advisor. The other half of Unity's spine. Brings finance discipline. Primary operator.
- **SpongeBong (Sponge / hackall360)** — Co-founder · Engineer · Ethical Hacker · Sys Admin. Started Unity. Owns the infrastructure, the prompt archive, and the on-call pager.
- **Alfreddo** — Engineer · Agentic Systems · Researcher · Developer. Lives inside the planner / executor / critic loop.
- **Red** — Engineer · Security · Sys Admin · Researcher. The reason every Unity deployment has a closed door, a logged door, and a second key.

---

## Overview

This file has two halves. **Part A** (through Recommendations) is the **as-built** map of the repository at 0.6.3-dev (2026-09-28, branch `feature/connected-colony-portals`): what exists in `src/`, what ships in the package, what the tools do, who owns which saved state. **Part B** (from "Design system map" onward) is the **whole-project architecture** condensed from the design contracts so a session does not have to re-read forty documents to know how the finished mod is shaped: feature IDs, campaign systems, save contracts, content-replacement state, the portal/work design and its pinned Core API facts, economy, multiplayer/DLC/profile model, and the acceptance infrastructure. The canonical contracts remain authoritative ([`TECHNICAL_ARCHITECTURE.md`](TECHNICAL_ARCHITECTURE.md), [`CAMPAIGN_STATE_DICTIONARY.md`](CAMPAIGN_STATE_DICTIONARY.md), [`FEATURE_TRACEABILITY.md`](FEATURE_TRACEABILITY.md) and the reading order in [`AI_BUILD_HANDOFF.md`](AI_BUILD_HANDOFF.md)); when this file and those disagree about intent, they win; when they disagree about what the code currently does, Part A wins until someone proves it stale.

Three facts shape everything below:

1. **Core-only, no Harmony.** The assembly references `Assembly-CSharp.dll` and three Unity modules, nothing else. Every vanilla integration goes through XML `PatchOperation`s, Def-declared classes, RimWorld's automatic `GameComponent` / `MapComponent` discovery, or subclassing. `About.xml` declares no dependencies.
2. **One save owner per concern, explicit integer schemas, refuse-on-unknown.** Nine components each carry their own `rr_*Schema` key. Mutating services check the schema and return a refusal instead of guessing. Migrations are forward-only and grant nothing.
3. **The connected-colony portal layer became reachable in 0.4.2-dev.** The 0.4.1-dev substrate (graph, route search, laboratory session ownership, same-pawn crossing service) gained its first callers: derived address registration, an explicit legacy threshold repair, the `RR_CrossPortal` job, and an Operations pane with open, close, emergency-return, crossing and reconcile controls. Cross-map **work** — hauling, construction ingredients, bills, research, needs — is still not implemented; that is resume step 4, owned and tracked in [`DEFERRED.md`](DEFERRED.md). The legacy expedition dispatch path is untouched and still owns its own runs.

Compilation status at 0.6.3-dev: zero warnings/errors, warnings treated as errors, .NET SDK 9.0.308, Release/net472, 110 C# source files, 76 approved package files; the assembly hash is reproduced after deleting `obj/` and `bin/` rather than by an incremental rebuild. Dependency position audited: every non-Rimrooms def the code uses is base Core; no DLC, no Harmony, no mod is required; zero throwing def lookups. No in-game run of any Rimrooms build has ever been recorded; every runtime claim in this repo is pending owner-launched acceptance.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | C# 7.3 (`LangVersion` pinned), XML (RimWorld Defs, Patches, Keyed/DefInjected language), PowerShell 5+ (build/stage), Python 3 (research + QA read-only tools) |
| **Framework** | RimWorld 1.6 Core API (`Verse`, `RimWorld` namespaces) via `Assembly-CSharp.dll`; Unity `CoreModule`, `IMGUIModule`, `TextRenderingModule` |
| **Build Tool** | `dotnet build` (SDK 9.0.308 via `global.json`) targeting `net472`, deterministic, `TreatWarningsAsErrors`, `PathMap` normalized; wrapped by `tools/build.ps1` |
| **Package Manager** | NuGet with locked restore (`packages.lock.json`); sole package `Microsoft.NETFramework.ReferenceAssemblies.net472 1.0.3`; caches in ignored `.local/` |
| **Linting** | Compiler warnings-as-errors; `.editorconfig` (four spaces, block namespaces, explicit braces); `BuildCommon.ps1` package allowlist + XML well-formedness check |
| **Mod loader** | RimWorld `LoadFolders.xml` single `1.6/` folder; `About.xml` packageId `UnityLabAI.RimroomsAsyncIndustries`, author `Operator`, `loadAfter: Ludeon.RimWorld` |
| **Optional runtime peers** | RimWorld Together + Harmony (co-op only, not referenced yet); five DLC (optional, not referenced yet); 294-mod profile (research/test target, none referenced) |

---

## Directory Structure

```
Backrooms/
├── AGENTS.md                      build-agent operating guide (authority order, rules)
├── README.md · CONTRIBUTING.md · CHANGELOG.md · LICENSE (MIT, source only)
├── global.json · NuGet.Config · .editorconfig · .gitattributes · .gitignore
├── .claude/                       Unity AI Lab workflow (tracked; session state ignored; see docs/HOWTO.md)
├── .github/ISSUE_TEMPLATE/        bug report form
├── .local/                        ignored: dotnet/nuget caches, decompiled inspection-*/ trees, QA
├── artifacts/                     ignored: build manifests, staging backups
├── assets/                        source masters for original presentation art
├── docs/                          design, research, implementation records, evidence, workflow ledger
│   ├── implementation/            task records, source reviews, implementation + build records
│   │   ├── evidence/<wave>-<date>/  compiler output, source/package/reference manifests, receipts
│   │   ├── historical-content/0.2.0/ superseded custom assets kept as evidence
│   │   └── assets/                provenance JSON for original art/audio
│   └── research/                  Gate 0 research, 294-row register, RWT/DLC audits, reviews/
├── outputs/                       planning workbooks (economy, 294-mod register)
├── src/
│   ├── RimroomsAsyncIndustries.sln
│   └── RimroomsAsyncIndustries/   one project, one namespace per folder (15 folders, 79 files)
├── tools/                         build.ps1, stage-mod.ps1, BuildCommon.ps1, render-preview.ps1,
│   ├── package-files.json         the 73-entry package allowlist (ground truth for what ships)
│   ├── assets/                    audio cue renderer (historical)
│   ├── qa/                        rimbridge_readonly.py (owner-operated, attach-only)
│   └── research/                  audit-gate0.py, audit-pinned-targets.ps1, metadata audit
└── Mod/Rimrooms - Async Industries/   the ONLY loadable/copyable package root
    ├── About/About.xml · Preview.png · License.txt
    ├── LoadFolders.xml
    └── 1.6/
        ├── Assemblies/RimroomsAsyncIndustries.dll   (built, gitignored)
        ├── Defs/                  27 XML files (see Package Contents)
        ├── Patches/               2 guarded PatchOperations
        ├── Languages/English/     Keyed/ (19) + DefInjected/ (6)
        └── Textures/              16 PNGs (14 historical gameplay sprites + 2 menu backgrounds)
```

### Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `src/RimroomsAsyncIndustries/Core/` | `RimroomsMod` entry point, `RimroomsSettings` (user preferences only), `RimroomsDiagnostics` opt-in perf counters |
| `.../Audio/` | Optional cue playback + warn-once; gameplay must never depend on a cue |
| `.../Company/` | **The save hub.** `RimroomsCampaignComponent` (schema 2) and its deep-saved records: ledger, staff, obligations, contracts, coordinates, rooms, cases, evidence, projects, events |
| `.../Expedition/` | `RimroomsExpeditionComponent` (schema 2, `IThingHolder`): dispatch/recall/relief/abandon, cargo manifests + declarations, closure records, interrupted-transfer recovery; approach and carry job drivers |
| `.../Gate/` | `CompRimroomsGate` (three partials): assembly, calibration, operator, power reserve, opening/recovery receipts, native door/console/battery/bench binding, portal-session ownership; console/cutoff comps; gate jobs and work giver |
| `.../Generation/` | `DestinationService` (finite persisted site per coordinate), `GenStep_BackroomsDestination` (6–8 room graph), `RimroomsDestinationMapParent` (world object owner, `rr_contentVersion`), `RoomContentMapComponent`, planner/builder (content version 4) |
| `.../Investigation/` | Laboratory binding to a designated native research bench (schema 1), evidence creation via a real Core `TextBook` (schema 1), route evidence/aid comps, lab job + work giver, `RimroomsProjectDef` |
| `.../Personnel/` | `RimroomsPersonnelComponent` (schema 1, holds unspawned applicants): request/hire/retry/cancel/decline/dismiss; `HiringPolicyDef`; role recommendation |
| `.../Procurement/` | `RimroomsProcurementComponent` (schema 1, largest file at 1,270 lines): quotes, orders, supplier cargo custody, receiving zones, partial delivery, redirection, receipts; `RimroomsProcurementCatalogDef` |
| `.../Facilities/` | Transient (never saved) HQ building/room/power/bed observation report; `RimroomsFacilityCategoryDef` is presentation-only |
| `.../Scenario/` | `ScenPart_RimroomsStart` / `ScenPart_RimroomsArrival`, `RimroomsStartDef` plan holders, startup receipt component (schema 1), HQ map component + GenSteps, company setup and staff configuration pages |
| `.../Threats/` | `FirstSliceSiteComponent` (per-site encounter/route bookkeeping, deployment-item recovery), `Thing_QuietPursuer` entity |
| `.../Portals/` | **Connected colony:** `RimroomsPortalNetwork` (saved graph, availability, resumable search), `PortalRouteSearch`, `RimroomsPortalCrossingService` (same-pawn/cargo crossing + recovery receipts, max 256 pending), records, plus `PortalAddressService` (derived address ids, laboratory and natural registration, legacy threshold repair), `PortalTravelService` with `JobDriver_CrossPortal` (crossing orders, session close, emergency return, reconcile), `PortalTraversalPolicy` (the one chokepoint deciding who may traverse and what may ride in a carrier's hands), and `NaturalFrontierService` with its survey work giver and driver (how a further permanently open gate is actually found in play: deterministic per doorway position under the coordinate's own seed, capped per coordinate) |
| `.../ConnectedWork/` | **Cross-map work:** `RimroomsConnectedWorkComponent` (saved work intents, each owning its own bounded expiring planning lease; bounded maintenance sweep), `ConnectedWorkIntent`, `ConnectedRouteService` (retained bounded route cursors, where budget-limited means pending and never "no route"), `ConnectedWorkAdapter` + registry (candidate half against an explicit `Map`, definitive native half only on arrival), `ConnectedWorkScan` (the rotating-window scan rules every family shares), `Adapters/ConnectedHaulingAdapter` (storage hauling both directions including remains, two candidate sources, cell and container destinations), `Adapters/ConnectedCasualtyAdapter` with `JobDriver_ConnectedTakeToBed` (our own downed people carried home to a bed via Core's own rescue precondition and bed handoff), `Adapters/ConnectedConstructionAdapter` with `JobDriver_ConnectedDeliverToSite` (real material carried into a real frame or blueprint through Core's own container and construct toils), `WorkGiver_ConnectedWork` with a plan/continue pair per family, and the `JobDriver_ConnectedFetch` / `JobDriver_ConnectedDeliver` segment drivers. **Travel-to-work (0.5.5-dev)** is a parallel shape on the same component for work done at the far site with nothing carried: `ConnectedDeploymentIntent` (a *sibling* record, deliberately not a phase on `ConnectedWorkIntent`, whose integrity check requires a source object), `ConnectedDeploymentProvider` + registry, `Providers/ConstructionFinishingProvider` (splits Core's own `GenConstruct.CanConstruct` by what each rule reads), `WorkGiver_ConnectedDeployment` with its own plan/continue pair, and `ConnectedCrossing` — the single shared implementation of stepping through a gate, now used by both shapes. A deployment issues **no job on arrival**: Core's own local giver does the work |
| `.../Presentation/` | `[StaticConstructorOnStartup]` menu bootstrap, title-screen controller, crossfading Backrooms background slideshow (`UI_BackgroundMain` subclass), cosmetic portal aura |
| `.../UI/` | `MainTabWindow_Operations` split into eleven partial files by tab (the eleventh is the portal network pane) (company, personnel, procurement, facilities, dispatch/expedition/manifest/machine, evidence, evidence recovery, native gate binding, laboratory binding); four dialogs. Pure sink: reads services, surfaces `CompanyActionResult` |
| `Mod/.../1.6/Defs/` | Scenario, starts, gate/fixture/equipment/site things, jobs, work givers, recipes, project, catalog, hiring policy, facility categories, terrain, map generators, world object, main button |
| `Mod/.../1.6/Patches/` | Adds dormant `CompProperties_RimroomsGate{Console}` to Core `Door`/`Autodoor`/`CommsConsole`/`TableMachining`; adds `CompProperties_RouteEvidence` to Core `TextBook` |
| `tools/` | Build/stage/preview scripts; read-only research and QA tools that never launch the game |
| `docs/implementation/evidence/` | Six dated evidence folders (phase1-foundation, phase2-first-expedition, phase3-company, phase3-scenario-provider, phase3-native-providers, connected-colony), each with `build-output.txt` + manifests |

---

## Component Diagram

```
                     ┌──────────────────────────────────────────────┐
  RimWorld loader    │  RimroomsMod (Core)  ─ settings, version log  │
  ───────────────►   │  RimroomsMenuBootstrap (Presentation)         │  title-screen slideshow
                     └──────────────────────────────────────────────┘
                                          │ automatic GameComponent discovery
   ┌──────────────────────────────────────┼───────────────────────────────────────┐
   │                                      ▼                                       │
   │   ┌─────────────────── RimroomsCampaignComponent (schema 2) ──────────────┐  │
   │   │  branch identity · USD ledger · payroll · staff records · contracts     │  │
   │   │  coordinates · rooms · cases · evidence · projects · company events     │  │
   │   └───────▲──────────▲──────────▲──────────▲──────────▲──────────▲─────────┘  │
   │           │          │          │          │          │          │            │
   │   Expedition     Personnel  Procurement  Laboratory  EvidenceCreation  Startup │
   │   (schema 2)     (schema 1) (schema 1)   (schema 1)  (schema 1)        (s.1)  │
   │   IThingHolder   IThingHolder IThingHolder            IThingHolder             │
   │        │                                                                      │
   │        │ opens / recalls                        ┌────────────────────────┐    │
   │        ▼                                        │ RimroomsPortalNetwork  │    │
   │   CompRimroomsGate (ThingComp on RR_MachineGate │ (saved graph, schema)  │    │
   │   OR a designated Core Door/Autodoor)           │ PortalRouteSearch      │    │
   │     assembly · calibration · operator · reserve │ PortalCrossingService  │    │
   │     native console/battery/bench binding        │ (NO CALLERS YET)       │    │
   │     PortalGateOpening partial ─── observes ────►│                        │    │
   │        │                                        └────────────────────────┘    │
   │        ▼ DestinationService.EnsureSite                                        │
   │   RimroomsDestinationMapParent (world object, rr_contentVersion 4)            │
   │     └─ GenStep_BackroomsDestination → RoomLayoutPlanner → RoomContentBuilder  │
   │     └─ RoomContentMapComponent · FirstSliceSiteComponent · Thing_QuietPursuer │
   │                                                                               │
   │   MainTabWindow_Operations (UI) ── reads every component, calls services,     │
   │     shows CompanyActionResult; four dialogs                                   │
   └───────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
New game
  ScenarioDef RR_AsyncIndustries
    → ScenPart_RimroomsStart (once) → RimroomsStartupComponent receipt
    → GenStep_HeadquartersTerrain / GenStep_HeadquartersFacility → HeadquartersSetupComponent receipt
    → ScenPart_RimroomsArrival (guarded native arrival)
    → RimroomsCampaignComponent.InitializeBranch (one-time budget + roles)

Daily loop (source present, runtime unverified)
  Operations tab
    ├─ Personnel: RequestApplicants → HireApplicant → arrival → AssignCompanyRole → payroll tick
    ├─ Procurement: CreateQuote → AcceptQuote (ledger debit) → supplier cargo held → delivery to receiving zone → receipt
    ├─ Gate binding: designate Core Door/CommsConsole/Battery/TableMachining → assembly bill (100 Steel, 8 Components)
    │               → CalibrateGate job → AssignOperator → power reserve from the bound Battery
    ├─ Dispatch: ExpeditionComponent.Dispatch(crew, cargo) → gate.BeginOpening(runId)
    │            → DestinationService.EnsureSite(coordinate) → MapParent + GenStep (content v4, Core steel door threshold)
    │            → JobDriver_ExpeditionApproach → transfer of the SAME pawns/things → site map
    │            → FirstSliceSiteComponent (route tags, pursuer, distortion cost)
    │            → Recall / SendRelief / casualty return → closure record → cargo declaration
    ├─ Evidence: CompRouteEvidence on a real Core TextBook → JobDriver_CompanyLaboratory at the designated bench
    │            → EvidenceAnalysisReport (frozen) → once-only settlement → ProjectRecord (RR_GateTelemetry)
    └─ Facilities: transient FacilityReport over actual buildings/rooms/power/beds

Portal layer (compiled, unconnected)
  Register(edge) → Availability(edge) → BeginRouteSearch(map,map).Advance() → ValidateStepForTraversal
    → PortalCrossingService.Cross(pawn, step, opId) [despawn → nonmerging carry transfer → spawn same pawn → post-spawn checks → rollback on denial]
    → Recover(opId) on interruption
  CompRimroomsGate.BeginPortalOpening / ClosePortalOpening / RecoverPortalOpening own the laboratory session id
```

### Flow Description

Every mutating action goes: **UI → service on the owning `GameComponent` → `CompanyActionResult`**. Services check their own schema, validate preconditions, mutate once, write a receipt where idempotency matters (openings, debits, deliveries, crossings, evidence creation), and return a keyed refusal on failure. UI never initializes scenarios, grants funds, generates rooms, reserves stock or completes research. Components are fetched with `Current.Game.GetComponent<T>()`; there is no dependency injection or service locator. Physical objects are always the originals: expeditions move the same `Pawn`/`Thing` instances, evidence is a real `TextBook`, procurement cargo sits in an `IThingHolder` until delivered, and the crossing service explicitly forbids cloning or Def-based reconstruction.

---

## Patterns Detected

### Architectural Patterns

- **One save owner per concern.** Nine `GameComponent`/`MapComponent` owners, each with an integer schema key and forward-only migration. Records are `IExposable` classes deep-saved under their owner; nested record fields use bare names, component-level keys are `rr_`-prefixed (370 distinct keys).
- **Receipt idempotency.** Openings, energy debits, recovery, deliveries, crossings and evidence creation each carry an operation id + monotonic sequence so a retry cannot double-apply. Receipt history is retained, not compacted.
- **Refuse, never guess.** Unsupported schema, missing provider, broken endpoint or malformed id disables the affected operation and keeps the evidence; nothing is deleted or regenerated to "repair" state.
- **Native-provider binding instead of custom Defs.** Since 0.3.x the code attaches dormant comps to existing Core things via XML patches and activates them only by explicit player designation. This is the mechanism the content-reuse policy demands; the remaining custom `RR_*` ThingDefs are legacy awaiting replacement.
- **Partial-class feature slicing.** `CompRimroomsGate`, `RimroomsCampaignComponent`, `RimroomsExpeditionComponent`, `RimroomsPersonnelComponent`, `FirstSliceSiteComponent` and `MainTabWindow_Operations` are split across files by concern, keeping each file readable while the class stays the single owner.
- **Content version vs. schema version.** Generated-site format is tracked separately (`rr_contentVersion`, currently 4) from component schema so a generator change never forces a save migration; older sites stay readable under their own version.

### Design Patterns

- Result object (`CompanyActionResult`: `Refused` / `Applied` / `Existing` / `Valid`) everywhere a mutation can fail.
- Resumable cursor (`PortalRouteSearch.Advance(maxOperations)`) with explicit `Pending | Complete | Unreachable | Invalidated | InvalidState` and a topology revision to invalidate stale results.
- Holder pattern (`IThingHolder`) for anything unspawned between maps or awaiting placement.
- Data-driven starts (`RimroomsStartDef` plan holders) so a scenario is XML, not code.
- Guarded XML patches (`PatchOperationConditional`) so re-applying is idempotent and absent targets do not error.

---

## Dependencies

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| RimWorld `Assembly-CSharp.dll` | 1.6 (pinned by SHA-256 in `PHASE_1_CORE_SOURCE_REVIEW.md`; build refuses drift) | Core game API |
| `UnityEngine.CoreModule` / `IMGUIModule` / `TextRenderingModule` | shipped with the game | Rendering, IMGUI windows, text |
| Harmony | — | **Not referenced.** Required later only for the RWT co-op path |
| RimWorld Together | 26.8.31.1 (pinned artifacts, not referenced) | Future co-op adapter target |

### Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| .NET SDK | 9.0.308 (`global.json`) | Compiler host |
| `Microsoft.NETFramework.ReferenceAssemblies.net472` | 1.0.3 (locked) | Framework reference assemblies |
| PowerShell | 5.1+ | `tools/*.ps1` |
| Python 3 | any recent | `tools/research/audit-gate0.py`, `tools/qa/rimbridge_readonly.py` |
| RimSort | current instance | Owner-operated discovery, sorting, launch; `stage-mod.ps1` reads its `settings.json` |

### Internal Dependencies

```
Core ⇄ Audio                      (settings ↔ warn-once)
Presentation → Core, Gate         (cosmetic aura only)
Company ⇄ Expedition ⇄ Gate ⇄ Portals
Company ⇄ Generation ⇄ Expedition
Company ⇄ Investigation ⇄ Threats
Company ⇄ Personnel
Company ← Procurement, Facilities, Scenario      (clean one-way slices)
UI → Company, Expedition, Facilities, Gate, Generation, Investigation,
     Personnel, Procurement, Scenario, Threats    (pure sink; NOT Portals, NOT Core)
Portals → Company, Gate, Generation               (near-leaf; only Gate reaches back in)
```

`Company` is the hub every feature depends on, and it depends back on four of them through service partials (`EvidenceObservations.cs`, `InvestigationServices.cs`, `PersonnelServices.cs`, and `Generation/FailedSiteRecovery.cs`, which is filed under `Generation/` but declares the `Company` namespace). Cross-cutting coupling is carried by exactly two types: `CompanyActionResult` and `RimroomsCampaignComponent`.

---

## Complexity Map

| Component | Complexity | Notes |
|-----------|------------|-------|
| `Procurement/RimroomsProcurementComponent.cs` (1,270) | High | Quote/order/custody/delivery/redirect/receipt state machine in one owner; largest file in the repo |
| `Gate/CompRimroomsGate.cs` + `NativeGateBinding.cs` + `PortalGateOpening.cs` (1,387) | High | Legacy custom gate AND native-provider binding AND portal session ownership coexist; two opening paths (`BeginOpening` vs `BeginPortalOpening`) |
| `Generation/GenStep_BackroomsDestination.cs` (652) + `DestinationService.cs` (503) | High | Deterministic bounded layout, fallback, content-version gating, legacy return-anchor vs Core door threshold |
| `Expedition/RimroomsExpeditionComponent.cs` (540) + closure/cargo/records | High | Crew/cargo transfer of real objects, relief, casualty return, abandonment, interrupted-transfer recovery |
| `Portals/PortalCrossingService.cs` (556) | High | Despawn → transfer → spawn → post-spawn checks → rollback ladder; 256 pending bound; called by the player travel order (0.4.2-dev) and by automatic connected work (0.5.0-dev) |
| `ConnectedWork/*` (~1,900 across 12 files) | Medium-High | Two-phase validation per family, a four-segment trip rebuilt from phase plus current map, and every scan bounded by a rotating window; plus the deployment shape, whose arrival check is deliberately *un*windowed because a miss there would loop the worker back across the gate. The complexity is in the invariants, not the control flow |
| `Company/*` (1,467 across 8 files) | Medium | Many record types, but each service is small; schema 2 migration is trivial |
| `UI/*` (1,686 across 10 files) | Medium | Wide, not deep; ten tabs read state and call services |
| `Personnel/`, `Investigation/`, `Scenario/`, `Threats/` | Medium | Bounded slices with their own schema or map receipts |
| `Core/`, `Audio/`, `Presentation/`, `Facilities/` | Low | Infrastructure and transient views |

### High Complexity Areas (Attention Required)

- **Two gate opening paths.** The expedition flow calls `BeginOpening(run.id)`; the portal flow adds `BeginPortalOpening(connectionId)`. Both share the physical timer/energy owner. Connecting portal callers (resume steps 2–3) must not let a session double-debit or adopt an active legacy trip; the checkpoint forbids silent migration of active missions.
- **Legacy return anchor vs. Core door.** Sites at content versions 0–3 still use `RR_ReturnAnchor`; version 4 uses a real steel `Door`. Any endpoint registration or repair path has to handle both without rebuilding a visited map.
- **Remaining custom gameplay Defs.** `RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator`, `RR_FieldAnalysisBench`, the four field items, `RR_RouteRecording`, `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, `RR_QuietPursuer` presentation and the five `RR_*Staff` PawnKinds predate the existing-content-only rule. They are hidden/legacy in places but still in the allowlist; replacement needs a migration or a declared dev-save break per `CONTENT_REUSE_POLICY.md`.
- **Procurement component size.** 1,270 lines in one owner is at the edge of the 800-line read standard for a single chunk; read it in two chunks and do not grow it further without splitting into partials.

---

## Technical Debt

### Critical (Fix ASAP)

- **Cross-map work is not implemented.** Addresses and crossing exist; hauling, construction ingredients, bills, research and care across an open portal do not. Until resume step 4 lands, the owner's "one connected colony" requirement is only half true. Sequence and owner: `DEFERRED.md`.
- **Natural-portal discovery has no trigger.** Registration and the deterministic coordinate API exist, but nothing in play discovers a natural threshold yet (resume step 5).

### Important (Plan to Fix)

- Superseded custom gameplay content still ships in the package allowlist (see High Complexity above); the replacement map exists at `implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md` but most rows are open.
- `Generation/FailedSiteRecovery.cs` is physically misfiled (declares `Company` namespace). Harmless today; move it or document it before adding more `Company` partials outside `Company/`.
- Dependency cycles (`Company ⇄ Expedition ⇄ Gate ⇄ Portals`, etc.) are tolerable in a single assembly but will bite the planned future extension-package split noted in `TECHNICAL_ARCHITECTURE.md`.
- Receipt histories are retained without compaction (crossings, deliveries, debits). Bounded-history policy exists for personnel/procurement but not everywhere.

### Minor (Nice to Have)

- `Textures/` still carries 14 historical gameplay PNGs that the content rule says must not ship in a release; remove from the allowlist once their references are replaced.
- No `Sounds/` folder exists in the package; the `RimroomsAudio` cue path and the `rr_cueVolume` setting reference Core sounds only. Confirm the settings UI wording matches.
- `RimroomsDiagnostics` counters exist but no measurements have ever been collected; the benchmark plan waits on the first owner launch.

---

## Entry Points

| Entry Point | Purpose | Location |
|-------------|---------|----------|
| `RimroomsMod : Mod` | Loads settings, resolves version from `AssemblyInformationalVersion`, logs the development-package banner | `src/RimroomsAsyncIndustries/Core/RimroomsMod.cs` |
| `RimroomsMenuBootstrap` `[StaticConstructorOnStartup]` | Creates the title-screen controller for the Backrooms slideshow | `src/RimroomsAsyncIndustries/Presentation/RimroomsMenuController.cs` |
| `MainButtonDef RR_Operations` | Opens `MainTabWindow_Operations` (order 95, valid without map) | `Mod/.../1.6/Defs/MainButtonDefs/RR_MainButtons.xml` |
| `ScenarioDef RR_AsyncIndustries` | The only implemented start; `ScenPart_RimroomsStart` + `ScenPart_RimroomsArrival` | `Mod/.../1.6/Defs/ScenarioDefs/RR_Scenarios.xml` |
| `MapGeneratorDef RR_Headquarters` / `RR_BackroomsGeneration` | HQ terrain/facility GenSteps; destination GenStep | `Mod/.../1.6/Defs/ScenarioDefs/RR_Scenarios.xml`, `MapGeneratorDefs/RR_BackroomsGeneration.xml` |
| Automatic `GameComponent` discovery | Campaign, Expedition, Personnel, Procurement, Laboratory, EvidenceCreation, Startup, PortalNetwork, PortalCrossingService | each component class |
| `tools/build.ps1` | Restore (locked) → compile → package allowlist validation → manifests | `tools/build.ps1` |
| `tools/stage-mod.ps1` | Copy only the package root to RimSort's Local Mods; hash-verify; back up existing | `tools/stage-mod.ps1` |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `global.json` | Pins .NET SDK 9.0.308 |
| `NuGet.Config` | nuget.org source; caches redirected to `.local/` |
| `src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj` | net472, C# 7.3, warnings-as-errors, deterministic, `RimWorldPath` resolution, `RequireLocalGameReferences` guard, version `0.4.1-dev` |
| `src/RimroomsAsyncIndustries/packages.lock.json` | Locked restore |
| `tools/package-files.json` | 71-entry package allowlist; `BuildCommon.ps1` rejects extras and malformed XML |
| `Mod/.../About/About.xml` | Identity: title, `Operator`, packageId, `modVersion 0.4.1-dev`, `supportedVersions 1.6`, `loadAfter Ludeon.RimWorld` |
| `Mod/.../LoadFolders.xml` | Single `1.6/` folder |
| `.editorconfig` | Four spaces, block namespaces, explicit braces |
| `.gitignore` | Ignores build products, `.local/`, `artifacts/`, DLLs, editor state, machine profiles, generic dependency/cache/temp noise, and only the machine-local state + personal files inside `.claude/` (the workflow folder itself is tracked by owner decision, 2026-09-28) |
| `.claude/project-config.json` | Git Flow opt-in marker (enabled; names `main`/`develop` while the project cascade uses `Prep`/`Develop`/`Main`) |
| `docs/SAVE_MIGRATION_POLICY.md` | Authoritative per-field save contract table |

---

## Recommendations

1. **Continue the checkpoint's order at step 4** (work intents and quantity leases, destination job revalidation, then the adapter families one at a time with source evidence per route). Steps 1 to 3 are closed; `DEFERRED.md` names the owner of every remaining piece. Superseded guidance follows for the trail: wire the portal substrate in the checkpoint's order (review crossing boundaries → address registration + legacy endpoint repair → crossing jobs + player controls → work intents/leases + adapters). Each step is a minor task in `TODO.md`; the first is decomposed in `DECOMPOSED.md`. Do not skip to adapters: a job that targets a remote map without a registered edge has nothing to validate against.
2. **Add `Keyed/RR_Portals.xml` with the first crossing job**, so failure keys become player text the moment they can be reached.
3. **Split `RimroomsProcurementComponent` into partials** (quotes / orders / delivery / receipts) before the next procurement feature; keep the single owner.
4. **Keep the content-version gate honest.** When registering endpoints for versions 0–3 sites, provide the explicit repair route the checkpoint asks for; never retarget a saved edge to a new door.
5. **Cut a checkpoint per resume step**, not per edit: build with `-NoRestore`, save `build-output.txt` + manifests under `implementation/evidence/<name>-<date>/`, write the implementation record, tick the bounded master TODO subitem, then publish both cascades once.
6. **Do not touch RimSort, RimBridgeServer or the game.** Every runtime row in this file stays "pending owner-launched acceptance" until the owner says otherwise.
7. **Regenerate this file with `rescan`** after any wave that adds a folder, a save owner, a schema bump, or a package allowlist change.

---

# Part B — Design system map (whole project)

Condensed 2026-09-28 from the canonical contracts. Status vocabulary: **Source** (compiles), **Build** (in the 71-file package with manifests), **Substrate** (API with no caller), **Design** (contract only), **Blocked** (owner decision or owner launch). Nothing in this project has runtime acceptance.

## B1. Owner decisions that shape every system

| Decision | Effect on architecture |
|----------|------------------------|
| D2 identity | Title `Rimrooms - Async Industries`, author `Operator`, package `UnityLabAI.RimroomsAsyncIndustries`, namespace `RimroomsAsyncIndustries`, semver `0.x` → `1.0.0` |
| D3/D4 dependencies | Core-only solo path is complete; Harmony + RimWorld Together only for co-op; all five DLC and all other 294 profile rows optional; rows 182 and 274 stay in the co-op candidate test despite publisher warnings |
| D5 sources | Kane Pixels continuity + A24 feature, adapted indirectly; every entity, room, story, rule is original; wider community canon excluded |
| D6 tech exchange | Physical Research Dossier items (bound to an existing document object); shared ledger only via a supported RWT extension point, none identified |
| D7/D8/D9 | English keyed first; MIT for code only; mature psychological horror at the strongest presentation the game supports |
| S1/B | Broad threat families frozen; five named sketches deferred (Signal Sink, The Long Exchange, Chalkline Spread, The Receiver, The Latch Visitor) |
| Content reuse (2026-09-28) | No new gameplay ThingDefs/benches/items/sprites/textures/audio; existing providers bound by saved role; menu images are the sole visual exception |
| Connected colony (2026-09-28) | Open laboratory/natural portals make one branch's labor and materials work across maps; natural portals never close; expedition dispatch becomes optional mission UI |
| Build continuation (2026-09-28) | Source work continues in dependency order; runtime gates govern acceptance only; owner alone launches via RimSort |

## B2. Feature IDs (the 17 traceability keys) and where each stands

| ID | Scope | Status (as-built) | What remains |
|----|-------|-------------------|--------------|
| RR-SCEN | Three starts on shared systems | Async Industries **Build**; Store/Lone Survivor **Design** | Native-pawn preservation, chosen tile honored, inside start (2 owner answers pending) |
| RR-FAC | Facility build/operate | HQ observations **Build**; laboratory bench **Build** | Functional room roles, security/containment, outposts, provider adapters |
| RR-STA | Hire/train/equip/recover staff | Native applicants + roles + payroll **Build** | Training, certification, field history, wellbeing, specialist sources |
| RR-GATE | Machine gate lifecycle | Legacy gate, native binding, portal session, addresses and crossing controls **Build** (0.4.2-dev) | Upgrades (aperture, duration, recall), legacy gate migration |
| RR-EXP | Plan/explore/extract | Dispatch/recall/relief/closure/cargo **Build** | Ordinary crossing without manifests; expedition as optional mission UI |
| RR-SPACE | Finite seeded room graphs | 6–8 room v4 sites, graph, search, addresses, legacy repair **Build** (0.4.2-dev) | Room library, bands 8–48, propagation, non-Euclidean effects, archival, streaming |
| RR-EVD | Evidence lifecycle | TextBook custody, analysis, settlement, Gate Telemetry **Build** | Other evidence types, custody breadth, dossier transfer |
| RR-THREAT | Entities/anomalies | Borrowed Corridor + Quiet Pursuer **Build** | Family-level sheets; presentation via existing pawns (content reuse) |
| RR-MSN | Mission families | Onboarding survey **Build** | 12 further families, seeded variation |
| RR-ECO | USD ledger, procurement, contracts | Ledger, payroll, quotes/orders/delivery **Build** | Shipment incidents, contract templates, leases, balance |
| RR-OUT | Outposts/relays/leases | **Design** | Everything |
| RR-MP | Async RWT co-op | **Design** | Feature detection, dossier item, verification (blocked on two-client run) |
| RR-DLC | Five optional layers | **Design** | Guarded LoadFolders/patches, present/absent runs |
| RR-SPACEFLIGHT | VGE Chapters 1–2 hooks | **Design** | Clean-stack chain, narrow link + cargo receipt |
| RR-COMPAT | Usable in the owner's profile | Core compiler/package route only | Six-tier disposition per row, compatibility report |
| RR-UI | Company-first interface | Operations 10 panes + menu **Build** | 11-pane Company Command, deep links, alerts, native remap, accessibility |
| RR-STYLE | Consistent presentation | Menu art v2, native audio **Build** | Provenance per asset; no placeholders at release |

## B3. Campaign systems (what the finished mod contains)

**Core loop:** fund → prepare facility → staff → plan a run → explore/extract → recover/contain → convert results → repeat. **Progression arcs (8):** keep the doors open (first slice) · measure before trusting · return with control · make a business of it · build beyond headquarters · respond to the outside world · expand industrial reach (optional) · enter deeper systems (open-ended). Gate window ladder: **20 min → 2 h → 1 day → 7 days → 30 days**, each step earned by power, cooling, stability, crew rotation, supply and return logistics, never a raw timer extension.

**Staff and work categories (9):** research · gate operations · engineering · security · field operations · medical and containment · logistics · communications · administration. Roles are assignments over native pawns, cross-trainable, never PawnKind locks (new starts already use native `Colonist`).

**Facility functions (12):** gate chamber · power and maintenance · research laboratory · evidence archive · decontamination/quarantine · security/armory · workshop/fabrication · medical bay · radio/dispatch · logistics/receiving · staff quarters · transport/space operations. Recognized from actual buildings and functions, no hidden room score.

**Research:** tiers T0 facility foundations → T1 first entry → T2 measurement and repeat access (contains the only named project, Gate Telemetry) → T3 services and remote ops → T4 public response and containment → T5 industry and space support → T6 deep-site topology; nine cross-cutting branches (facilities/power, gate engineering, fieldcraft/security/medicine, measurement/evidence, mapping/topology, entities/containment, communications/logistics, commerce/organization, transport/orbital). Evidence and contracts open alternate routes; no branch may depend on a DLC.

**Mission families (13):** onboarding route survey (first slice) · repeat survey/route verification · retrieval/salvage · sample or record delivery · missing crew/rescue · reappearance and death case · entity observation/containment contract · settlement opening response · commercial site and lease work · outpost establish/resupply/repair/evacuation · internal company incident · ground transport · optional orbital support.

**Room families (9):** threshold and survey · office and records · service and transit (first slice: Threshold Room, Survey Lobby, Office Copy, Service Passage, Borrowed Corridor, Return Gallery; optional Storage Nook, Utility Room) · retail and domestic · industrial and power · medical and institutional · shelter and communications · unfinished and altered · transit and orbital support. Template tag groups: Shape · Connections · Use · Mood · Play · Story · Modifiers. Size bands 6–8 / 8–16 / 16–32 / 24–48; a routine expedition adds at most one new major spatial rule plus two familiar modifiers.

**Outpost ladder:** HQ → relay and cache → field shelter → guarded station/temporary lab → leased or monitored space → network of sites → ground transport → optional orbital/gravship layer → deep-site access.

**Interface (11 panes → Company Command):** Overview · Personnel · Facilities · Gate · Expeditions · Atlas/Routes · Research/Evidence · Contracts/Ledger · Cases/Containment · Outposts/Company Network · Gravship Operations (only with Odyssey + chapter content). Every action: precondition → one saved owner mutation → `CompanyActionResult`; unavailable DLC/mod/RWT reads "unavailable", never a fake success. Operations today ships ten panes plus four dialogs.

**Threat rules (shared):** visible accessible warning, learnable rule, at least one countermeasure, recorded outcome, never color-or-sound-only, first contact never instantly kills a healthy pawn, effects bounded and seed-stable. First slice: **The Borrowed Corridor** (route mismatch after a tagged junction; returns crew to last validated junction; costs 3 reported in-game minutes; cannot injure) and **The Quiet Pursuer** (appears two rooms away; advances one room per 2 in-game minutes or on loud action; at most 3 rooms; never enters the Threshold Room; one strike, recoverable injury; fighting never the only completion path).

## B4. Economy model

- **Company Account** is a branch-local USD ledger (1 unit = $1). Opening allocation **$50,000,000**; physical silver **150**; parent company's multi-trillion valuation is setting only. Cash is never an item; a $1,000,000,000 balance is one number.
- **Opening targets (v0.2 hypotheses):** staff pay $5,000/day each (5 staff) · HQ overhead $25,000/day · first survey payment $5,000,000 once · optional bonus up to $1,000,000 · penalties capped at 25% of base payment · new hire setup $100,000 · survey-kit order $750,000 · research-material shipment $2,000,000 · leased space $100,000/active day · outpost $250,000/active day. Day-30 worked example: $53,500,000 with the survey receipt, $48,500,000 without; steady HQ burn $50,000/day.
- **Power (not cash):** 250 W standby, 3,500 W opening draw, 250 W headroom, 2 Wd return capacitor via an accounted 1,000 W load, 1 Wd per emergency return or recovery, starter generation 6,000 W target (three wood generators at HQ in 0.4.0). Native-gate defaults: 833 ticks at 3,500 W ≈ 48.59 Wd; readiness ≈ 49.59 Wd; recovery ≈ 50.59 Wd, debited from the real bound `Battery` via `DrawPower`, never `AddEnergy`.
- **Seven economy stages** map to the arcs: 1 first safe survey ($5M) · 2 repeat access ($250K–$5M/contract) · 3 specialist services ($1M–$25M) · 4 leases and remote sites · 5 large recovery/network work ($5M–$100M) · 6 vehicle/orbital support · 7 deep-site operations ($25M–$500M+). Milestone funding requests $25M–$1B, released only on completion plus explicit approval.
- **Logistics:** four separate limits never merged: cash capacity, pawn carry, storage, handling throughput. Stack limits read from the live save: OgreStack (row 157, default ×30 on small-volume) → 15,000 silver/stack → **67 stacks per million**; Core 500/stack → **2,000 stacks**. Never encode the preset, never require OgreStack.
- **Non-duplication:** every grant/payment/debit/delivery/crossing/evidence creation carries a receipt key; replay returns the recorded outcome. The same item is never paid twice as sale and deliverable; RWT moves physical items with receipts, never balances or research; the `:fallback:1` replacement coordinate cannot pay a reward twice.

## B5. Save contract (as implemented; full table in `SAVE_MIGRATION_POLICY.md`)

| Owner | Schema | Notable keys | Rule that must hold |
|-------|--------|--------------|---------------------|
| `RimroomsCampaignComponent` | 2 (from 1) | `rr_schemaVersion`, `rr_branchId`, `rr_scenarioId`, deep lists (ledger, staff, obligations, contracts, coordinates, cases, evidence, projects, events) | Migration grants nothing; integrity faults disable mutation with a visible message; sole ledger/payroll owner |
| `RimroomsExpeditionComponent` | 2 (from 1) | monotonic run IDs, `rr_gate` ref, manifests, closure history, transfer journals, deep-held interrupted pawn | Schema 1 cargo declarations become unverified historical entries; one non-closed `Active` run at a time |
| `CompRimroomsGate` legacy | — | `rr_gateAssignedOperator`, `rr_gateActiveExpeditionId`, opening/emergency ticks, warned flags, `rr_gateOpeningSpendReceipts`, `rr_gateRecoveryReceipts` | Repeated operation IDs never refill time or double-spend |
| `CompRimroomsGate` native binding | native 1 (appended) | designated door/console/battery/bench refs, entry side, bound door position/rotation, `nativeLastProcessedTick`, observed energy, debit faults (history 32) | Load never creates a provider, restores energy or pays; same-tick duplicate payment blocked |
| `CompRimroomsGate` portal session | appended | `rr_gatePortalConnectionId`, `rr_gatePortalOpeningId`, sequence, `PortalOpeningRecoveryReceipt` list | Post-load owner validation faults on dual legacy+portal ownership; emergency sessions cannot be closed to bypass recovery cost |
| `RimroomsPortalNetwork` / `PortalConnectionRecord` | 1 | `rr_portalNetworkSchema`, `rr_portalConnections`; edge id/branch/coordinate/kind/endpoints/openingId | Old saves load empty; malformed IDs disable the graph but keep evidence; natural kind never consults timers |
| `RimroomsDestinationMapParent` threshold repair | content version | `rr_thresholdRepairReceipt` (additive, 0.4.2-dev) | At most one legacy threshold repair per site; a replay is refused as already recorded |
| `JobDriver_CrossPortal` | (job-scoped) | `rr_portalCrossingOperation` (additive, 0.4.2-dev) | Keeps one crossing idempotent across save and reload |
| `RimroomsPortalCrossingService` | — | receipts (operation id, sequence, endpoints, pawn, carried thing, phase, failure), deep holder | Max 256 unresolved; receipts retained; recovery only to saved endpoint cells |
| `RimroomsConnectedWorkComponent` deployments | appended 0.5.5-dev | `rr_connectedWorkDeployments` (deep) | Additive and no schema bump, so a 0.5.4-dev save still loads; absent reads as nobody deployed. `nextSequence` is shared with the intents so ids are unique across both lists, and validation shares its id **and** live-worker sets across them, so no save can load with one worker owing a carry trip and a deployment. Capped at 32 live, 64 total. Deliberately requires **no** source object, which is why it is a separate record |
| `RimroomsConnectedWorkComponent` area observations | appended 0.5.1-dev | `rr_connectedWorkAreaObservations` (deep) | Additive and no schema bump, so a 0.5.0-dev save still loads; absent reads as nothing observed and therefore unrestricted, which is Core's own default. Bounded at 256; a row whose area or map no longer resolves is dropped on load |
| `RimroomsConnectedWorkComponent` | 1 (new 0.5.0-dev) | `rr_connectedWorkSchema`, `rr_connectedWorkNextSequence`, `rr_connectedWorkIntents` (deep) | Old saves load with no intents; a live intent must name its worker and one worker may never own two, or the save faults and the whole layer disables itself without altering anything; an intent whose recorded adapter version is not current is cancelled rather than run under changed rules; capped at 64 live and 128 total |
| `RimroomsDestinationMapParent` / `CoordinateRecord` | content 4 | `rr_contentVersion`, coordinate id/seed/generator/room-library versions, status, layout receipt, anchors | Visited maps never rebuilt or retargeted; `AI-01` = `<branch>:coordinate:000001` |
| `RimroomsLaboratoryComponent` | 1 | bench ref + load ID + provider | Starts unbound; missing provider blocks work, never substitutes |
| `RimroomsEvidenceCreationComponent` | 1 | attempt/registration receipts, deep-held unfinished `TextBook` | Never reminted after loss; retry uses the same original |
| `RimroomsPersonnelComponent` | 1 | applicant offers, deep-held pawns | Hire uses the original generated pawn; charge/refund op IDs reconcile with the ledger |
| `RimroomsProcurementComponent` | 1 | quotes, orders, held goods | One charge; undelivered quantity never shown as map stock; unresolved cargo never archived |
| `RimroomsStartupComponent` / `HeadquartersSetupComponent` | 1 / receipt 1→2 | chosen tile, pawn refs + load IDs, roles, `setupStarted`/`arrivalStarted` flags | Registration retry reuses physical setup; grants never replay |
| `FirstSliceSiteComponent` | — | route tags, mismatch, pursuer counters, pending time-cost receipt, deep-held recovery items | Same-expedition reopen preserves encounter limits |
| Core-owned | — | `Battery.storedPower`, pawn `innerContainer` | Never copy `rr_gateReturnReserveStored` into a Core Battery |

Stable ID categories: scenario definition/version, branch, coordinate, site, expedition, crew assignment, evidence, case, research project, contract, company transaction, shipment, transfer receipt, endpoint, connection, portal opening + sequence, crossing receipt. IDs never derive from names, list order or UI selection; durations in game ticks; enum values append only. Declared dev-save boundaries: never re-save a newer save in an older build; existing-content replacement is its own migration boundary (hidden migration-only Defs or a declared fresh-save break with the old build preserved); the portal rollout performs **no automatic conversion** of active legacy runs.

## B6. Existing-content replacement state

| Role | Provider now | Status |
|------|--------------|--------|
| Route evidence | Core `TextBook` (patched `CompProperties_RouteEvidence`, 3000 analysis work) | Source done |
| Company laboratory | Designated Core `SimpleResearchBench` / `HiTechResearchBench` | Source done; `RR_FieldAnalysisBench` legacy-only |
| Gameplay audio | Core `Power_OnSmall`, `Message_ThreatSmall`, `CommsWindow_Open`, `Message_NegativeEvent` | Source done; WAVs archived |
| Site lighting / climate / floors / power | Core `StandingLamp`, `Heater`, `PavedTile`/`Concrete`/`MetalTile`, `ChemfuelPoweredGenerator` + `Chemfuel` + `HiddenConduit` (content recipe v3) | Source done; demand ≤ 475 W, ≈ 6.67 fuel-days |
| Gate threshold/station/energy/assembly | Core `Door`/`Autodoor`, `CommsConsole`, `Battery`, `TableMachining` (100 Steel + 8 Components bill) | Source done (0.4.0); legacy Defs hidden, not removed |
| Generated return threshold | Core steel `Door` (content version 4) | Source done (0.4.1) |
| Portal aura | Core `HeatGlow` fleck; paint via `Building.ChangePaint` proposed | Source done (aura) |
| Menu art | `RR_Menu_FacilityThreshold_v2`, `RR_Menu_FieldSurvey_v2` (1672×941, original) | Approved exception, done |
| **Open** | `RR_MachineGate`/`RR_GateConsole`/`RR_EmergencyCutoff` (→ `Autodoor`/`CommsConsole`/`PowerSwitch`), `RR_UtilityGenerator` (no single Core generator meets 3,500 W; `GeothermalGenerator` 3,600 W), `RR_FieldRecorder`/`RR_SurveyTag`/`RR_ReturnBeacon`/`RR_SealedEvidenceCase` (no portable Core equivalents; `MedicineIndustrial` explicitly unsafe), `RR_RouteRecording` (→ `TextBook`/`Schematic`), `RR_ReturnAnchor` (→ `Door`), `RR_QuietPursuer` (→ `Megascarab` reskin or removal), five `RR_*Staff` PawnKinds (→ `Colonist`, already used by new starts), five recipes | Binding correction: removing recorder/marker/beacon/case mechanics is a rejected scope reduction; hauling, loss/recovery, navigation and study must survive with saved role bindings |

## B7. Connected-colony design and the pinned Core facts it rests on

**Who may cross (owner rule, enforced in source).** Inhabitants and monstrosities stay in the Backrooms. `PortalTraversalPolicy` is the single chokepoint: only this company's own colonists traverse; everything else rides in a carrier's hands, including people and monstrosities that are genuinely downed, dead or imprisoned, while anyone still on their own feet is refused. `AutonomousNonPlayerTraversalPermitted` is a constant false and `MayApproachThresholdForTraversal` is unconditionally false, so an open gate can never become an objective, lure, spawn target, raid route or attack trigger for a later adapter, scheduler, generator or threat. Gate, machine door and portal are one thing; the rule is per connection and holds for every gate at once; every start can eventually run several gates, so nothing assumes one gate per branch, map or coordinate. Separate `Map` instances already make cross-map pathing impossible in vanilla — the policy is the standing guard against building a route for anyone but our own pawns. The **pacing** half of the rule (gradual, saved, bounded escalation of what a space presents) is specified in the contract and owned by resume step 5 in `DEFERRED.md`.

**Three saved records:** portal endpoint (map, anchor thing + load ID, cell, approach/orientation), portal connection (`Laboratory` | `NaturalPermanent`, branch, coordinate, two endpoints, opening id), crossing receipt (operation, sequence, direction, endpoints, original pawn and cargo, phase, failure). **Three identities kept distinct:** permanent connection id; the connection selected for a session; portal opening id + sequence. One gate may own many addresses but one open aperture per session; `CompRimroomsGate` is the single timer/energy owner for legacy and portal modes; legacy `rr_gateActiveExpeditionId` stays legacy-exclusive.

**Pinned Core behaviors (ILSpy 9.1.0.7988 against `Assembly-CSharp.dll` `5CF1B5BE…`):** `LocalTargetInfo` has no map, so map identity must live in the Rimrooms intent · `WorkGiver_Scanner` "Global" methods still use the current map, and `HasJob*` may call `JobOn*` with side effects, so speculative remote probes are unsafe · `ReservationManager.CanReserve` rejects claimants and targets not on `map`, so cross-map reservations need a Rimrooms lease that excludes nobody · `Pawn_PlayerSettings` keeps allowed areas in a private per-map dictionary, so full area compliance is checked after spawn on the destination · `Pawn.DeSpawn` clears reservations across maps and job cleanup can drop cargo, hence the nonmerging carry transfer first · `GenSpawn.Spawn(Thing, …)` reuses the object; Def overloads create new objects and are wrong for crossing · `Pawn_PathFollower.StartPath` resolves against `pawn.Map`, so routes are local segments · `CompPowerBattery.DrawPower` clamps and is not transactional, so debits are verified by observed before/after · `Building_Door.DoorPreDraw()` rotates one-cell doors during render, so entry uses the saved bound orientation.

**Adapter families (in order):** ~~storage hauling~~ → ~~casualties and remains~~ → ~~construction supply~~ → ~~construction finishing~~ (0.5.5-dev, the first *deployment* rather than an adapter) → ~~bills~~ (0.5.7-dev; unfinished things out of scope by Core's own one-creator binding) → research → tend/rescue → food → rest → remaining families (cleaning, repair, firefighting, plants/mining, wardening, childcare, animals/mechs, refuel, joy, rituals, hauling providers) → every installed work giver in the profile. Architecture A (recommended): Core-only staged adapters via custom WorkGiver/ThinkNode + JobDefs + saved intent/crossing services inserted by XML patch; Harmony not intrinsically required. **No installed mod provides a general cross-map job/path/reservation/storage API**, so Rimrooms owns the graph and adapters; per-row boundaries recorded for Stargates! (218, GPL-3.0, not a dependency), RWT (196), Pick Up And Haul / Haul To Stack (164/107), OgreStack (157), storage frameworks (10/24/25/26/122/259), RimFridge (195), construction helpers (57/212/55/111), UI mods (67/156/30), work-policy mods (288/279/125/269), travel/economy owners (270/249/247/281/11/265).

**Door providers reviewed:** Core `Door`/`Autodoor` 1×1 paintable; Doors Expanded 2×1/3×1/3×2 (`Building_DoorExpanded` inherits `Building_MultiTileDoor`); ReBuild 2×1/3×1; Remote Doors 25 W; VVE garage doors 4×1/5×1 with separate opened Defs (runtime Thing identity unverified); Locks + PrisonersDontHaveKeys (273/175) are authoritative, no teleport bypass. Adapter records store package/Def/class family, load ID, map, rotation, footprint, approach/arrival sides; loss pauses the route and exposes rebind, never binds whichever door appears at that cell.

**Prepare Carefully facts:** its `StartGame()` skips `CanDoNext()`; `PreparePawns()` replaces the roster instances; setup receipt captured during startup; Rimrooms appends its review page after the native pawn page via `ScenPart.GetConfigPages()`. Setup ordering: storyteller → world → surface site (unless `ScenPart_ForcedMap`) → ideology → part pages; `PrepForMapGen()` runs before `PreMapGenerate()`.

## B8. Multiplayer, DLC and profile model

- **RWT (pinned 26.8.31.1):** guild/company identity; separate facilities and branch-local state; direct trade/gift needs both online; offline visit availability unknown (server has Aid/Trade enabled, no Visit/Activity file, Crashlanded enforced, `AllowAllMods=true`, `EnforceSettings=false`); dossiers are the candidate technology route and a release gate if the pinned build cannot move the item; visits are server-controlled activities with a purpose and a log, never two players commanding one colony; no supported client extension API identified; upstream issue #296 (aid state changes) is a test lead.
- **DLC:** isolated `LoadFolders.xml` + package-guarded patches per expansion; Core-only complete; publish exactly which combinations were run (32-row bitmask only if claimed).
- **VGE Chapters 1 (3609835606) / 2 (3799737423):** Odyssey + VEF (+ Chapter 1 for 2); CC BY-NC-ND 4.0, never repackaged; exposed interfaces `IGravshipFuelProvider`, `ITurretLinker`, `IGravEngineGraphic`, `IOxygenVerb` are leads, not stable APIs; both DLLs reference Assembly-CSharp 1.6.9544 vs the pinned 1.6.9676 (clean-stack test trigger).
- **294-profile:** every row gets exactly one of six support tiers (native feature · configuration only · optional adapter · compatibility patch · verified alongside/no touch · unsupported/conflict); 914 declared relationships, 602 in-profile, 443 unique pairs, 0 in-profile `IncompatibleWith`; 266 overlap flags are triage; creed: "researched ≠ integrated; loads ≠ compatible; optional ≠ tested".

## B9. Acceptance infrastructure

- **Counts:** 294 profile · **295** product target (plus Rimrooms) · **296** normal loaded count with RimBridgeServer QA overlay. Never drop a target entry to fit the bridge.
- **RimSort:** owner refreshes Local Mods, adds Rimrooms, sorts, saves, launches; never `RimWorld.exe` directly, never GABS launch, never another manager rewriting the list.
- **RimBridgeServer 2.1.1:** attach-only, disposable profile/saves, copied server config; bridge actions never launch, enable/disable or reorder; `tools/qa/rimbridge_readonly.py` requires an explicit PID.
- **Performance (machine RR-DEV-01: Ryzen 7 5800X, 127.91 GiB, RTX 4070 Ti SUPER, Windows 11 Home 26200):** paired comparisons Core vs Core+Rimrooms, 294 vs 294+Rimrooms, RWT vs RWT+Rimrooms. Budgets: added mean tick ≤ 10% and ≤ 1 ms, p95 ≤ 2 ms · 100 seeds per band, 6–8 room p95 ≤ 10 s, none > 30 s, ≤ 3 failed attempts · UI added p95 ≤ 2 ms/frame, acknowledgement ≤ 250 ms · 20 revisits ≤ 128 MiB and ≤ 5% growth · save/load p95 ≤ baseline ×1.20 + 1 s · slideshow ≤ 2 ms, ≤ 2 textures, ≤ 128 MiB over 30 min. `RimroomsDiagnostics`: opt-in, 16 categories × 2,048 samples, developer-mode Activity controls; no sample ever collected.
- **Acceptance standard:** Core solo route end to end; 1,000 seed cases identical per generator release; ≥ 100 save/load cycles with zero duplication; ≥ 100 co-op transfers + 20 reconnects with zero duplicate postings; no softlockable required objective; 100% keyed text with a long-string locale; no color/audio-only warnings; no placeholders and full provenance at release; D1 private RWT prototype before any public release.
- **Owner questions, all three ANSWERED 2026-09-28** (this line previously listed them as open; corrected in the 2026-09-29 doc-rot sweep): inside-start party is **configurable**; the first exit is **chosen by the player**, not a fixed reveal; and opening duration is the laboratory duration ladder (108,000 ticks for a first opening, about thirty real minutes at normal speed, multiplying by three per earned tier, with no countdown at the indefinite tier while power, operator and energy hold). See [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) and [`implementation/GATE_DURATION_AND_COMPANY_NAMING.md`](implementation/GATE_DURATION_AND_COMPANY_NAMING.md). The old 833-tick value survives only for legacy expeditions.
