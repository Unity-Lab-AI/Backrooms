# Development roadmap

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.

## Workflow major-milestone tier

**Tier 1 of 3** in the Claude Code three-tier task cascade (ROADMAP → `TODO.md` → `DECOMPOSED.md`; completed work archives to `FINALIZED.md`). Added 2026-09-28 when the Claude Code workflow took over from the previous build agent. This section layers status markers, scope, exit conditions and dependencies over the existing Stage 0–6 roadmap below; it changes no stage scope or exit condition. The [master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) keeps the complete backlog and formal gates; every open item of it is mirrored verbatim in `TODO.md` under these majors. The sections after the stages (decision log, dependency graph, risks, timeline, next actions) are the workflow's project-wide view.

Status markers: `[ ]` pending · `[~]` in progress · `[x]` complete (archived to `FINALIZED.md`) · `[!]` blocked.

### Current status

| Metric | Value |
|--------|-------|
| **Development version** | 0.4.2-dev (`About.xml`, csproj), branch `feature/connected-colony-portals` |
| **Gate 0 (docs/source preparation)** | PASSED 2026-09-28 (`research/GATE_0_COMPLETION_AUDIT.md`) |
| **Gate 2 (first loop in play)** | OPEN — no Rimrooms build has ever been launched |
| **Master TODO** | 133 items checked, 121 open (mirrored in `TODO.md`; deferments tracked in `DEFERRED.md`) |
| **Source** | 78 C# files, 15 namespaces, 9 save owners, no Harmony |
| **Package** | 73 allowlisted files, 27 Def XMLs, 2 patches, 25 language files, 16 PNGs |
| **Active major** | M1 connected colony portals — addresses, crossing, controls, natural-gate discovery and five cross-map work families (storage hauling, casualties and remains, construction supply, construction finishing, bill ingredients) reachable in source, one of them the first travel-to-work shape rather than a carry; nineteen deferments closed; research next |
| **Next unblocked minor** | Resume step 4 (work intents, leases, adapter families) |
| **Owner questions open** | 3 (inside-start party size; first-exit fixed vs chosen; opening duration) |

### Majors

- [x] **M0 — Claude Code workflow handoff.** User's verbatim request (2026-09-28): *"we need to build all the workflow files for the .claude templetes into the root doc folder like archetecture finalized roadmap updated readme how to ect ect all the .claude tmeplete files need to be built in the doc folder while you read and maintain the current docs as we will be picking up from where ChatGPT6 Astra left off from today while building all the needed workflow flow files and setting everything up for claude usage and get prepared to begin work where ChatGPT left off in the TODOs"*. Closed the same day; see `FINALIZED.md` session 2026-09-28.

- [~] **M1 — Connected colony portals** (feature IDs RR-GATE, RR-EXP, RR-SPACE, RR-FAC, RR-COMPAT; contract [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md)).
  **Scope:** independent connection ownership, permanent natural portals, free bidirectional crossing of the same pawns and cargo, cross-map job discovery/reservations, cross-portal hauling/construction/bills/research/care, closure/reopen reconciliation, 294-row work/storage provider integration, replacement of dispatch-only travel controls, coordinate/seed/complexity persistence, bounded procedural inhabitants and rare monstrosities, connected-site streaming.
  **Done so far (0.4.2-dev):** saved portal graph with Laboratory/Natural kinds, resumable route search, laboratory session ownership, same-pawn crossing service with receipts and recovery, content version 4 Core-door thresholds (all 0.4.1-dev); then resume steps 1–3 — the crossing-service boundary review, derived laboratory and natural address registration, the deterministic discovered-coordinate API, the explicit legacy threshold repair, the `RR_CrossPortal` job with its save-stable operation id, the Operations portal pane with open/close/emergency-return/crossing/reconcile controls, and player text for every result. The substrate is now reachable in play.
  **Exit condition:** the 11-item required implementation backlog is source-complete with compiler evidence per step, every supported native work route is listed with source evidence, and the owner-launched acceptance row is recorded (the last item stays `[!]` until the owner launches).
  **Working sequence:** resume steps 1–6 in `TODO.md`; steps 1–3 decomposed in `DECOMPOSED.md`. Maps to Stage 2 → Stage 5 below.

- [~] **M2 — Existing-content replacement** (RR-STYLE, RR-GATE, RR-EVD, RR-THREAT; policy [CONTENT_REUSE_POLICY.md](CONTENT_REUSE_POLICY.md), map [implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md)).
  **Scope:** replace every remaining custom gameplay Def and asset from 0.2.0 with an existing Core/profile provider bound by saved role; define the migration or declared dev-save break; drop obsolete files from the allowlist; reconcile scenario grants and recipes.
  **Done so far:** evidence book (Core `TextBook`), laboratory (designated Core research bench), four audio cues (Core sounds), gate/console/battery/bench designation on Core `Door`/`Autodoor`/`CommsConsole`/`Battery`/`TableMachining`, native room lighting/heater/generator/floors.
  **Still custom:** gate objects (`RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator`), `RR_FieldAnalysisBench`, four field items + `RR_RouteRecording`, `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, `RR_ReturnAnchor`, `RR_QuietPursuer` presentation, five `RR_*Staff` PawnKinds, 14 gameplay PNGs.
  **Exit condition:** package allowlist contains no superseded gameplay Def or gameplay PNG; historical masters retained under `implementation/historical-content/`; migration route or dev-save break documented; runtime acceptance row recorded after owner launch. Maps to Stage 1–2.

- [ ] **M3 — Phase 3 interconnected company simulation** (RR-SCEN, RR-FAC, RR-STA, RR-GATE, RR-EXP, RR-SPACE, RR-EVD, RR-THREAT, RR-MSN, RR-ECO, RR-OUT).
  **Scope (six groups, 50 master TODO items):** scenario framework and the Store and Lone Survivor starts; physical room functions, applicant pools, roles/training/certification/wellbeing; native door/endpoint bindings, machine upgrades, field gear effects, crew planner, window progression 20 min → 2 h → 1 day → 7 days → 30 days, recall/evacuation/rescue workflows, fog-of-war atlas; tagged room library across the four size bands (6–8, 8–16, 16–32, 24–48), non-Euclidean effects, anomaly propagation, map versioning, tick budgets; USD ledger breadth, procurement incidents, contract/quest templates for the 13 mission families, leases, evidence custody, missing-person cases; research IDs across the 9 branches and tiers T0–T6, entity sheets (broad families only per S1/B), containment, settlement openings, outposts, vehicles, VGE hooks.
  **Exit condition:** master TODO Phase 3 source items checked with evidence; campaign arcs 2–6 have reachable content; each new scenario passes the `SCENARIOS.md` acceptance checklist up to the owner-launched rows. Maps to Stage 4–5.

- [ ] **M4 — Phase 4 multiplayer, DLC and the full profile** (RR-MP, RR-DLC, RR-SPACEFLIGHT, RR-COMPAT).
  **Scope:** RWT feature detection and setup diagnostics for pinned 26.8.31.1 (no supported client extension API identified; no custom server schema); Research Dossier bound to an existing physical document object; five DLC conditional layers each present/absent; VGE Chapter 1/2 clean-stack chain; per-row closure of all 294 register rows with one of the six support tiers; compatibility report.
  **Exit condition:** source-side guards and adapters compile; every verification row is `[!]` until the owner runs the two-client disposable profile; release notes list only tested configurations. Maps to Stage 3.

- [ ] **M5 — Phase 5 Company Command interface and polish** (RR-UI, RR-STYLE).
  **Scope:** the 11 panes (Overview, Personnel, Facilities, Gate, Expeditions, Atlas/Routes, Research/Evidence, Contracts/Ledger, Cases/Containment, Outposts/Company Network, Gravship Operations) with deep links, reason codes, previews and recovery; native menu/tab remap preserving every Architect/Work/Assign/Research/World action; tutorial, glossary, keyboard paths, contrast/scale options; main-menu slideshow (≥1 image per shipped scenario, 30 s dwell, 2 s fades, reduced-motion still, no audio) with dynamic title/version.
  **Exit condition:** every Operations action passes the six acceptance checks in `OPERATIONS_ACTION_CONTRACTS.md`; 100% of player text keyed; long-string locale clips nothing; owner-launched readability rows recorded. Maps to Stage 6.

- [ ] **M6 — Phase 6 QA, balance and release** (all IDs).
  **Scope:** Def/key/patch/package validation; scenario acceptance per opening; invalid-state matrix including the one-million-silver case (67 stacks OgreStack / 2,000 Core); performance against `research/PERFORMANCE_BENCHMARK_PLAN.md` budgets on RR-DEV-01; economy balance; release report; install/uninstall/update/server tests; mod page and provenance; tag and archive.
  **Exit condition (D1):** private RimWorld Together prototype passes the Core-only solo path and the pinned co-op tests; public Workshop only after named-profile and multiplayer validation. Maps to Stage 6.

- [!] **Runtime acceptance gates (Gate 2 onward).** Blocked on the owner launching the 295-entry product target through RimSort (296 with the RimBridgeServer QA overlay attached afterward). The build agent never launches RimWorld, never alters the active RimSort list, never attaches RimBridgeServer outside `research/RIMBRIDGE_TEST_HARNESS.md`. Source and build work continues across M1–M6 per the owner's [build-continuation direction](GATE_0_DECISIONS.md#build-continuation-and-deferred-game-testing).

The work is sequenced so that later content depends on an accepted company loop. Gate 0 preparation passed, repository/build foundations exist, and the first Async Industries facility-to-expedition slice is implemented in development. The integrated 0.2.0 package compiled with zero warnings/errors; all 61 staged files match the saved manifest. No gameplay or compatibility gate is closed by those compiler results. See the [current build record](implementation/PHASE_2_BUILD_RECORD.md) and [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) for exact evidence and remaining work.

These stage numbers group the long-term roadmap; the master TODO controls task order and formal gates. Status notes distinguish existing first-slice code/assets from owner-launched acceptance and unimplemented broader systems. This reconciliation changes no stage scope or exit condition.

## Stage 0 — decisions and research

**Status:** Gate 0 documentation/source preparation is complete. Its decisions, source reviews and 294-mod feature map preceded code creation. Historical preparation results do not establish gameplay or optional-mod compatibility. Current implementation evidence is in the [0.2.0 build record](implementation/PHASE_2_BUILD_RECORD.md).

- Use the selected title, package ID, namespace, distribution target, and MIT source-code license. Set author/publisher metadata to `Operator`; track art/audio provenance and licensing separately.
- Capture the exact RimWorld 1.6 build, DLC set, RimWorld Together client version, server release, and client load order.
- Maintain the completed 23-entry Kane fan-summary notes and separate A24 fan-summary story note; check official sources only for design-critical gaps, and assess supplemental Kane-related material without folding broader community canon into shipped content.
- Establish folder layout, build setup, language-key conventions, save ownership rules, and multiplayer synchronization approach.

**Exit condition:** a concrete versioned target profile and a documented content-provenance rule exist.

## Stage 1 — facility start and company shell

**Status:** the data-driven Async Industries scenario, five-person starter facility, physical stock, company records/ledger, machine assembly/calibration/operator/power work and Operations actions exist in source/package content. Fresh-start behavior, one-time grants, real work and persistence still need owner-launched acceptance; this stage's exit condition is not yet observed.

- Use [`SCENARIOS.md`](SCENARIOS.md) as the data-driven scenario setup contract and implement the first new-game scenario: Async Industries with a small facility, a roster, starter resources, a disabled gate, and a first project.
- Add the basic machine building, calibration/assembly project, operator and power requirements, and clear gate status feedback.
- Add the first company console and minimal operations record: funds, staff, active projects, and incidents.
- Preserve normal pawn management, work priorities, needs, health, storage, and construction.

**Exit condition:** a save starts and plays as a facility-management campaign before any endless destination system exists.

The Furniture & Knickknack Store breach and Lone Survivor starts are planned scenarios, not part of the first playable acceptance target. Their starting-state contracts are documented in [`SCENARIOS.md`](SCENARIOS.md); implement them after the facility-to-expedition vertical slice has stable save and return behavior. Add outpost, town-distortion, and company-crisis openings only after their acceptance criteria and procedural variation are designed.

## Stage 2 — first expedition vertical slice

**Status:** saved AI-01 generation now includes 6–8 furnished rooms, deterministic bounded candidates and fallback, native doors/fog, original clues/salvage, crew/cargo dispatch and recovery, the starter encounter, durable analysis reports, Gate Telemetry, original art and optional quiet cues/settings. Opt-in diagnostics exist without collected runtime measurements. Finish current source/package receipts and the pending opening-time decision, then record load, first loop, failure/recovery, save/revisit, presentation and performance observations. Gate 2 remains open; source presence does not demonstrate this exit condition.

- Add one stable seeded coordinate that creates a single local site from a small room set.
- Send a named crew and equipment loadout through a time-limited opening.
- Add one return method, one environmental risk, one entity encounter, one recoverable evidence chain, and one payment/research outcome.
- Reopen the coordinate and preserve meaningful prior exploration and recovered state.
- Serialize campaign, coordinate, gate, quest, crew, and site state.

**Exit condition:** the full prepare → enter → investigate → extract → analyze → reward loop works in a save and can be repeated.

## Stage 3 — co-op and DLC foundation

**Status:** future implementation and verification. The current assembly uses Core APIs; the 294 source reviews and RWT/DLC plans do not establish an adapter, supported transfer, shared research, visit or combined-profile result.

- Add a narrow RimWorld Together adapter using only supported extension points; keep branch-local campaign state authoritative.
- Verify guilds, sites/roads/events, item trade/gifts, pawn aid, configured facility visits, transfer spots, and reconnect/save behavior against a pinned client/server release.
- Implement physical dossier exchange only after the exact RWT build reliably transfers the Backrooms dossier; research completion remains local to each branch.
- Add optional DLC content for Royalty, Ideology, Biotech, Anomaly, and Odyssey; keep the complete Core-only campaign path playable.
- Run the mod in a clean baseline and then the exact recorded local server profile; keep an explicit list of known interactions.

**Exit condition:** a second client can operate a separate company branch, exchange verified supplies/dossiers, use supported RWT world activities, and reconnect without duplicating or corrupting either branch. Direct shared research is enabled only if the selected supported ledger extension passes synchronization tests; otherwise dossiers remain the technology-transfer path. No live shared-map control is assumed.

## Stage 4 — management breadth

**Status:** the first slice provides a small local ledger, initial staff roles, one survey contract, analysis/research and Operations. The full hiring/training, procurement/shipment, dynamic contract, facility and company-management systems below remain unimplemented broader scope in master TODO Phase 3; retain that task order.

- Expand hiring, role assignments, training, staff records, labs, cafeterias, dormitories, medical/quarantine, evidence storage, contracts, procurement, and shipment schedules.
- Add two-way company economy with operating costs, salvage valuation, wages or contract labor, penalties, and equipment loss.
- Add the Operations interface for finance, projects, staff, research clues, contracts, destinations, and incidents.
- Grow the Operations panes into the Company Command navigation layout, retaining direct access to vanilla pawn/work/research/world controls.

**Exit condition:** the company has meaningful operating choices between expeditions, not only construction chores.

## Stage 5 — world network and spatial variation

**Status:** the bounded first site exists. The broader coordinate/template library, generated mission families, persistent outpost network, safe many-map archival and vehicle/space logistics below remain later work. Preserving one saved site is not acceptance of an expanding multi-site campaign.

- Expand room templates, map themes, coordinate selection, radio reports, return navigation, remote supply, relay stations, and outposts.
- Add rescue, survey, retrieval, containment, and town-distortion quest families.
- Add stable map archival and generator-version migration rules.
- Introduce vehicle/space travel as a later logistics layer that supports the company's reach without replacing gate exploration.

**Exit condition:** an established company can run parallel sites and revisit saved spaces without save corruption or runaway map growth.

## Stage 6 — long-form progression and release

**Status:** later progression/release work. Initial original sprites, carpet and short audio cues exist with provenance, but the complete coherent asset set, main-menu slideshow, translations, final presentation, balance and published compatibility matrix are not complete.

- Expand threat catalog, countermeasures, deeper research branches, long-duration openings, multi-team operations, advanced transport, and endgame phenomena.
- Add remaining original narratives, art, sounds, translations, accessibility options, settings, tutorials, and Workshop packaging.
- Maintain a published compatibility table for RimWorld 1.6 builds, DLC combinations, RimWorld Together versions, and explicitly supported optional mods.

**Exit condition:** release notes, credits, licensing records, installation guidance, save/migration policy, and compatibility statements match what was actually verified.

## Non-goals for the first playable build

- A literal infinite map loaded at once.
- Replacing every vanilla tab and menu before the simulation loop works.
- Requiring the local 294-mod profile as a dependency set.
- Promising compatibility with every mod simply because the server has `AllowAllMods` enabled.
- Reusing film footage, screenshots, transcripts, distinctive named entities, or unverified community assets as shipped content.

---

## Workflow view — decision log, dependencies, risks, timeline, next actions

Everything below was added 2026-09-28 by the Claude Code workflow as the project-wide view the three-tier cascade works from. Sources: `GATE_0_DECISIONS.md`, `CAMPAIGN_CONTENT_CATALOG.md`, `CAMPAIGN_ECONOMY_PROGRESSION.md`, `FEATURE_TRACEABILITY.md`, `research/PERFORMANCE_BENCHMARK_PLAN.md`, `research/PREPRODUCTION_ACCEPTANCE_STANDARD.md`, the implementation records and the source survey in `ARCHITECTURE.md`.

### Decision log (binding; change only by recording a new owner decision in `GATE_0_DECISIONS.md` first)

| ID | Date | Decision | Impact on the roadmap |
|----|------|----------|-----------------------|
| D1 | 2026-09-27 | Private RimWorld Together test build first; public Workshop only after named-profile and multiplayer validation | M6 exit condition; no Workshop work before M4 verification |
| D2 | 2026-09-27 | Title exactly `Rimrooms - Async Industries`; author/publisher `Operator`; package `UnityLabAI.RimroomsAsyncIndustries`; namespace `RimroomsAsyncIndustries`; semantic versions (`0.x` pre-release, `1.0.0` first stable) | Identity is implemented; every version bump touches `About.xml`, csproj, `CHANGELOG.md` together |
| D3 | 2026-09-27 | All 294 profile rows are the research/test target; only Core + Harmony/RWT required for co-op; everything else optional; rows 182 (Questionable Ethics Enhanced) and 274 (Medical Dissection) stay in the co-op candidate test despite publisher warnings | M4 scope; no adapter may become a hidden dependency |
| D4 | 2026-09-27 | Core-only campaign; all five DLC optional detected content; validate the all-five profile | M4 DLC layers; no DLC type may gate the machine or the first mission |
| D5 | 2026-09-27 | Kane Pixels continuity + A24 feature only, adapted indirectly; wider community canon excluded | All entity/room/story content is original; provenance register per shipped asset |
| D6 | 2026-09-27 | Technology exchange as physical Research Dossier items; shared ledger only if a supported RWT extension point exists and sync is proven safe | M4; no supported client API found 2026-09-27, so dossiers are the only planned route |
| D7 | 2026-09-27 | English first, every label keyed; Core-only solo path; RWT for co-op | 100% keyed text is an M5/M6 acceptance row |
| D8 | 2026-09-27 | MIT for original source code; art/audio licensed separately | Third-party assets never bundled (VGE is CC BY-NC-ND 4.0) |
| D9 | 2026-09-27 | Mature psychological horror/management at the strongest presentation the game and profile support | Content questionnaire honest at release; no "all ages" |
| S1/B | 2026-09-28 | Freeze broad later threat/anomaly families; the five named sketches (Signal Sink, The Long Exchange, Chalkline Spread, The Receiver, The Latch Visitor) are deferred and need owner approval + a full sheet before scope | M3 entity work stays family-level |
| Content reuse | 2026-09-28 | Existing Core/DLC/profile content only; no new gameplay items, benches, sprites, textures, audio; original main-menu images are the sole visual exception | M2 exists; M3 gear/room/threat items bind existing objects |
| Connected colony | 2026-09-28 | Open portals unify one branch's labor and materials across maps; natural portals permanently open; expedition dispatch becomes optional mission UI | M1 exists and supersedes dispatch-only contracts where they conflict |
| Build continuation | 2026-09-28 | Continue source/content work with game testing deferred; runtime gates govern acceptance, not permission to code | M1–M6 proceed in dependency order with `[!]` runtime rows |
| Regression containment + publication cadence | 2026-09-28 | Every task records baseline/callers/saved fields/preserved behaviour; publish only at meaningful milestones, all changes batched, both cascades, refs read back, no separate receipt file | `PUBLISHING.md`; each resume step closes with compiler evidence |
| Tracking `.claude/` | 2026-09-28 | Owner: ".claude gets pushed the whole backrooms folder always gets pushed except obvious dependacies and node stuff and logs,temps,and cache like files and configes ect ect that are auto generated and not product ship worthy" | `.gitignore` carries only session-state and personal-file excludes inside `.claude/` |

### Dependency graph

```
Gate 0 PASSED ──► 0.1.0 foundation ──► 0.2.0 slice ──► 0.3.0 company ──► 0.3.1 setup ──► 0.4.0 native providers ──► 0.4.1 portal substrate
                                                                                                                              │
   ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
   ▼                                                                                                                          ▼
M2 content replacement ◄──── shares saved keys with ────►  M1 portals: step 1 boundary review ─► step 2 registration + legacy repair
   │  (legacy gate/anchor migration decided once, together)                                          │
   │                                                                                                  ▼
   │                                                                               step 3 crossing jobs + controls + emergency return
   │                                                                                                  │
   │                                                                                                  ▼
   │                                                                               step 4 work intents/leases ─► adapters (haul, build, bills, research, care)
   │                                                                                                  │
   ▼                                                                                                  ▼
M3 scenario framework (Store, Lone Survivor*) ◄── step 5 providers + scenario openings + inhabitants/complexity
M3 facility/personnel · gate upgrades · room library/propagation · economy/contracts · research/containment/outposts
   │
   ▼
M4 RWT adapter · DLC layers · 294-row closure  (source guards now; verification [!] until owner launch)
   │
   ▼
M5 Company Command · tutorial/accessibility · slideshow integration
   │
   ▼
M6 validation · balance · release report · D1 private RWT prototype ─► Workshop (later, only after validation)

* Lone Survivor waits on two owner answers (party size; first exit fixed vs chosen). Provisional assumption in use.
Every "[!]" row across all majors converges on one external event: the owner's first RimSort launch of the 295-entry target.
```

### Critical path

1. M1 steps 1–3 (the substrate becomes reachable: registration, crossing job, controls). Nothing in M3's gate/expedition/procedural groups should be built on the old dispatch-only path after this point.
2. M2's migration decision (legacy gate objects and legacy return anchor) is made together with M1 step 2, because they share saved keys.
3. M1 step 4 adapters unlock M3's facility/personnel breadth being meaningful across maps.
4. The owner's first launch unblocks Gate 2, the performance baselines, and every `[!]` row; until then every major ends at "source + build evidence".
5. M4 verification and M6 release both require that launch plus a two-client disposable server.

### Risk assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Portal substrate stays unconnected while other systems grow on the dispatch path | Rework across Expedition/Gate/UI; owner requirement unmet | High if M3 starts first | M1 steps 1–3 before any M3 gate/expedition item; `TODO.md` order enforces it |
| Two gate opening paths double-debit or adopt an active legacy trip | Save corruption, duplicate energy debits | Medium | Receipt rules already exist; step 3 must call only `BeginPortalOpening`; never migrate `rr_gateActiveExpeditionId` silently |
| Legacy content-version 0–3 sites cannot be registered | Existing dev saves lose portal access | Medium | Explicit repair route in step 2; never retarget a saved edge; keep the old anchor Def loadable |
| No runtime observation exists for any build | Any of the 120 open items may fail in play; balance numbers untested | Certain until owner launches | Every runtime row is `[!]`; compile + manifest evidence only; benchmark plan waits |
| Cross-map work adapters break native priorities, areas, locks or optional-mod work givers | Owner's "one colony" promise silently wrong in the 294 profile | High | Step 4 ships one adapter family at a time with source evidence per route; 294-row provider boundaries in `CONNECTED_WORK_PROFILE_BOUNDARIES.md` |
| RWT has no supported client extension API | Dossier transfer may be impossible; shared research impossible | Known | D6: dossier is a physical existing document object; ship disabled if the pinned build cannot move it |
| Custom gameplay assets ship by accident | Violates content-reuse policy at release | Medium | M2 exit condition removes them from the allowlist; `BuildCommon.ps1` rejects extras |
| Procurement component grows past readable size | Regressions in the largest owner | Medium | Split into partials before the next procurement feature |
| Performance budgets fail on large room bands | Late redesign of generation/streaming | Unknown | Bands 8–16 and up gated on measured 6–8 results; `RimroomsDiagnostics` counters ready |
| Three owner questions remain unanswered | Lone Survivor and opening-duration work built on assumptions | Medium | Assumptions recorded as provisional; no saved scenario ID renamed; ask once, grouped, when the work is reached |
| Branch-name mismatch (`Prep`/`Develop`/`Main` vs config `main`/`develop`) | A future session pushes to the wrong branch or creates lowercase twins | Low now | `PUBLISHING.md` names the real branches; config left as-is on purpose |

### Progress timeline

```
2026-09-27  Gate 0 research: 294-row source review, RWT/gravship audit, Kane/A24 notes, D1–D9
2026-09-28  Gate 0 PASSED · 0.1.0 foundation · 0.2.0 first-expedition slice · 0.3.0 company ops
            · 0.3.1 customizable setup · 0.4.0 native providers · 0.4.1 portal substrate
            · owner: content reuse, connected colony, deferred testing, regression containment
            · previous agent paused (usage conservation) · Claude Code workflow handoff (M0)
            · workflow ledger built; .claude/ tracked by owner decision; PUBLISHING.md written
DONE        M1 step 1 → 2 → 3 (0.4.2-dev) · gate traversal rule (0.4.3-dev) · step 4 intent/lease engine and
            the storage-hauling family (0.5.0-dev), each checkpointed and cascaded
DONE        M1 step 4 families: storage hauling (0.5.0-dev), casualties and remains (0.5.2-dev),
            construction supply (0.5.3-dev), construction finishing as the first
            travel-to-work deployment (0.5.5-dev), bill ingredients (0.5.7-dev).
            Dependency position audited: base Core only.
NEXT        travel-to-work intents (owner-selected): completes construction finishing and unlocks
            every later "work done over there" family → bills → research → tending → food → rest
THEN        M1 step 5 providers/inhabitants · step 6 hygiene · M2 migration decision · M3 groups in order
BLOCKED     every runtime row until the owner's first RimSort launch of the 295-entry target
```

### Next actions

**Immediate (next session):**
1. `docs/NOW.md` → `docs/TODO.md` M1 resume step 1 → `docs/DECOMPOSED.md` first slice: read `PortalCrossingService.cs` + `PortalCrossingRecords.cs` in full.
2. Write `implementation/CONNECTED_CROSSING_CALLER_REVIEW.md` with the regression-containment fields.
3. Decide each open crossing constraint (finish / defer to step 2 or 3); compile with `-NoRestore` only if source changed.

**Short term (this milestone):**
- Steps 2 and 3 per `DECOMPOSED.md`; new `Keyed/RR_Portals.xml`; version 0.4.2-dev; evidence folder; cascade publish per `PUBLISHING.md`.
- Ask the owner the three open questions once, grouped, when Lone Survivor or opening-duration work is actually reached.

**Long term:**
- M1 step 4–5, M2 closure, then M3 in master TODO order; M4/M5/M6 source-side work interleaved where it does not depend on runtime evidence.
- Owner launch → Gate 2 → benchmark baselines → every `[!]` row.

### Open owner questions (carried from the previous agent; do not answer on the owner's behalf)

1. Inside start (`lone_survivor`): configurable party versus strictly lone start.
2. Inside start: does the first reliable exit reveal a fixed discovered surface destination, or does the player choose a settlement?
3. Opening-duration clarification — the accepted 20 in-game-minute first window is retained until directed otherwise.

Provisional assumption in use for 1–2 (recorded in `SCENARIO_SETUP_AND_PORTAL_NETWORK.md`): configurable solo/group, automatic Backrooms entry, fixed discovered surface destination.
