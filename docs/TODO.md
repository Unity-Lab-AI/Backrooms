# TODO — Minor Task List (Active Tasks)

**Tier 2 of 3** — the MINOR task list. Holds active tasks (pending + in_progress) at the day-to-day work grain. Each minor task lives under a major milestone in `docs/ROADMAP.md` and decomposes further into entries in `docs/DECOMPOSED.md` when YOLO mode picks it up.

Completed tasks move to `docs/FINALIZED.md` per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`. Never delete a task description; only flip status (LAW: NEVER DELETE TODO INFO).

Status markers:
- `[ ]` pending
- `[~]` in_progress
- `[x]` complete (move to FINALIZED.md immediately, never leave here)
- `[!]` blocked (waits on an owner decision or an owner-launched run)

LAW #0 reminder: every task description preserves the user's verbatim words.

**Three-tier cascade:** ROADMAP.md (major) → TODO.md (minor, this file) → DECOMPOSED.md (decomposed). YOLO mode reads all three and works the cascade — see `.claude/commands/yolo.md` and `.claude/WORKFLOW.md §YOLO MODE`.

> **Live project TODO for Rimrooms - Async Industries.** Seeded 2026-09-28 when the Claude Code workflow took over from the previous build agent (ChatGPT 6 Astra). This file carries **every open item** of the complete mod backlog, quoted verbatim from [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) (the "master TODO"), grouped under the majors in `ROADMAP.md` and in the master TODO's own order. The master TODO stays the authoritative gate/evidence record; when an item here closes, tick the identical bounded subitem there in the same change with its evidence link, per `REGRESSION_CONTAINMENT.md`. Items whose source already exists but whose runtime acceptance is open stay `[ ]` — the master TODO's rule: *"Unchecked tasks below retain their full stated implementation/acceptance scope; they do not mean all referenced source is absent."*
>
> Owner sequencing override (2026-09-28): implement remaining systems while game testing is deferred; gameplay-gate statements govern acceptance/promotion, not permission to write source. Only the owner launches RimWorld, through RimSort.

---

## In progress

**Verbatim owner request (2026-09-28, four items):** *"new feature branch for your work start on the todo weork making sure to properly finalize all completed work as i think gate 0 is still in the todo stuff but it should be finalized first and begin on any and all todo work to reach the goal of having a completed working mod in all regaurds as outlined in the many prep documentes build over 18 hours of work in gate 0"*

- [~] **"new feature branch for your work"** — branch `feature/connected-colony-portals` created from `48a8418` (= `Develop` = `Main` on both remotes). Pushed with the first milestone per `PUBLISHING.md`.
- [~] **"start on the todo weork"** — M1 resume steps 1, 2 and 3 CLOSED in 0.4.2-dev (see `FINALIZED.md`); step 4 (work intents, leases, adapters) is next.
- [~] **"making sure to properly finalize all completed work as i think gate 0 is still in the todo stuff but it should be finalized first"** — all 129 checked master TODO items archived verbatim in `FINALIZED.md` §Inherited completed work; master TODO checkboxes retained beside their evidence per `REGRESSION_CONTAINMENT.md`.
- [~] **"begin on any and all todo work to reach the goal of having a completed working mod in all regaurds as outlined in the many prep documentes build over 18 hours of work in gate 0"** — standing objective for every session from here: work the cascade M1 → M6 in `ROADMAP.md` order until the master TODO is empty; runtime rows stay `[!]` until the owner launches.

---

## Pending

### Major M1 — Connected colony portals (ROADMAP M1; master TODO §Native-provider foundation — 0.4.0-dev)

Binding contract: [`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md). Baseline commit `8ed4e32`, 0.4.1-dev, 75 C# files, 71 package files, zero warnings/errors. Read `implementation/CONNECTED_COLONY_CHECKPOINT.md`, `CONNECTED_COLONY_IMPLEMENTATION_TASK.md`, `CONNECTED_NETWORK_IMPLEMENTATION.md`, `CONNECTED_CROSSING_IMPLEMENTATION.md`, `CONNECTED_WORK_CORE_API.md`, `CONNECTED_PORTAL_STATE_MIGRATION.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md` before editing `src/RimroomsAsyncIndustries/Portals/` or `Gate/`. Source fact: nothing in the repo calls `RimroomsPortalNetwork.Register`, `PortalCrossingService.Cross`/`Recover`, or `CompRimroomsGate.BeginPortalOpening` yet.

**Master TODO items (verbatim):**

- [ ] Implement every open item in [connected colony portals](CONNECTED_COLONY_PORTALS.md#required-implementation-backlog): independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants/complexity. This supersedes dispatch-only travel as the target.
  - [ ] Finish resumable route scheduling, same-pawn/cargo crossing recovery and player-facing connection controls; integrate their compilation evidence.
  - [ ] Implement and integrate native work/needs adapters, physical ingredient logistics and per-provider coverage without separate mandatory labor/material pools.

**Resume order (verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`; these are the working sequence for the items above):**

- [x] **Resume step 1:** "Review the crossing service's documented permission, recovery and state boundaries before connecting callers. Finish unresolved constraints rather than weakening checks. Preserve original pawns/cargo and no-wipe landings." — CLOSED 2026-09-28, record `implementation/CONNECTED_CROSSING_CALLER_REVIEW.md`. Archived in `FINALIZED.md`.
- [x] **Resume step 2:** "Add explicit address registration and discovery using the existing campaign coordinate/site owner. Preserve seeds and visited maps; provide an explicit legacy saved-endpoint repair path. No auto-conversion of active legacy missions." — CLOSED 2026-09-28 in 0.4.2-dev, record `implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md`. Archived in `FINALIZED.md`.
- [x] **Resume step 3:** "Implement ordinary local threshold approach/crossing jobs and player controls without crew/manifests. Wire laboratory open/close/recovery and permanent natural links. Define the remaining emergency-return route without duplicate debits or teleporting stranded workers home." — CLOSED 2026-09-28 in 0.4.2-dev, record `implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md`. Archived in `FINALIZED.md`.
- [~] **Resume step 4:** "Implement saved work intents, quantity leases and native destination job revalidation; then physical hauling, construction, bills, research, medical/food/bed and other work/needs families. Preserve priorities, schedules, areas, locks, custody and actual inventory. A generic graph does not implement these adapters."
- [ ] **Resume step 5:** "Integrate exact optional work/storage providers and scenario openings, then procedural inhabitants, rare monstrosities, saved events and tech-driven complexity. Keep every wider master TODO feature in scope."
- [ ] **Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change." — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`.

**Required implementation backlog (verbatim from `CONNECTED_COLONY_PORTALS.md`; the acceptance list the majors above must satisfy):**

- [x] Save a portal/endpoint graph independent of expedition records, with distinct laboratory and permanent-natural lifetimes. *(source complete in 0.4.2-dev: graph from 0.4.1-dev plus the address registration that actually creates edges; runtime acceptance open)*
- [x] Implement bidirectional free pawn movement, persistent crossing receipts and stable return endpoints. *(source complete in 0.4.2-dev: `RR_CrossPortal` job + `PortalTravelService`; the step is directional per call and both directions are orderable; runtime acceptance open)*
- [ ] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions.
- [ ] Implement actual cross-portal hauling, construction ingredients, bills/production, research and care/needs access; list each supported native work route with source/acceptance evidence.
- [ ] Reconcile jobs and original cargo on closure/reopen, blocked endpoints, death, save/load and interrupted crossing without duplicating consumption or objects.
- [ ] Integrate relevant profile work/storage/hauling providers; account for all 294 rows without asserting universal support from a successful load.
- [ ] Replace dispatch-only ordinary travel controls and scenario prerequisites; keep optional missions distinct from connection ownership.
- [ ] Persist coordinate/seed/version/site/complexity and generated inhabitants/events; revisit the same saved space without reset.
- [ ] Implement bounded procedural inhabitants/state combinations, rare monstrosities, evolving events and technology-driven complexity families.
- [ ] Implement connected-site scheduling/streaming and measure performance after an owner-launched build.
- [!] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants. — blocked: owner RimSort launch.

**Task-record subitems still open (verbatim from `implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md`):**

- [x] Machine ownership adapter, natural discovery registration and player controls. *(0.4.2-dev: laboratory + natural address registration, deterministic discovered-coordinate API, Operations portal pane with open/close/emergency/crossing/reconcile controls. The discovery **trigger** that finds a new natural threshold in play is owned by step 5 and tracked in `DEFERRED.md`.)*
- [x] Same-pawn crossing, carried-object custody and interrupted-transfer recovery. *(0.4.2-dev: the crossing job and reconcile surface connect the 0.4.1 API; runtime acceptance open)*
- [ ] Saved work intents, quantity leases and native destination job revalidation.
- [ ] Work-specific hauling, construction, bill, research, medical and needs adapters.
- [ ] Optional profile interfaces and native priority/schedule/restriction coverage.
- [!] Owner-launched acceptance: both directions; chains/loops; closed/blocked endpoints; permanent natural links; save/reload; cargo identity; interrupted jobs; all supported native/provider routes. — blocked: owner RimSort launch.

### Major M2 — Existing-content replacement (ROADMAP M2; master TODO §Existing-content replacement work + Phase 5 replacement item)

Policy: [`CONTENT_REUSE_POLICY.md`](CONTENT_REUSE_POLICY.md); map: [`implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md`](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md). Already replaced in source: evidence book (Core `TextBook`), laboratory (designated Core research bench), four audio cues (Core sounds), gate/console/battery/bench designation on Core `Door`/`Autodoor`/`CommsConsole`/`Battery`/`TableMachining`, native room lighting/heater/generator/floors. Still custom and still in the 71-file allowlist: `RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator`, `RR_FieldAnalysisBench`, `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon`, `RR_SealedEvidenceCase`, `RR_RouteRecording`, `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, `RR_ReturnAnchor`, `RR_QuietPursuer` presentation, five `RR_*Staff` PawnKinds, 14 gameplay PNGs.

- [ ] Map every custom gameplay Def/asset and code consumer to existing Core/profile content, with exact provider/version and Core fallback; see [replacement map](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md).
- [ ] Replace custom gate/console/cutoff/generator objects with designated existing installed infrastructure and equivalent operator/power/emergency logic.
- [ ] Replace custom field gear, route aids and evidence items with existing objects plus saved functional/custody records; handle stack splits/merges, destruction, cargo and recovery without creating new item types.
- [ ] Replace custom creature presentation, room fixtures and terrain with existing native/provider content, retaining learned rules, encounters, procedural variation and saved routes.
- [ ] Define supported migration or explicit preserved development-save break before removing obsolete Defs; remove obsolete assets and references from the active package/allowlist once replacements exist.
- [ ] Reconcile all scenario grants, recipes, equipment readiness, content bindings and optional-provider absence against the existing-content-only policy. Source/build work continues while runtime cases remain deferred.
- [ ] Replace the historical custom gameplay items, benches, terrain, sprites and audio with source-verified existing Core/profile content and saved role bindings; preserve the gate, field gear, evidence, threat and discovery functions. Follow `CONTENT_REUSE_POLICY.md` and the existing-content replacement map. *(master TODO Phase 5)*

### Phase 1 leftovers (master TODO §Phase 1 — repository, build, and content foundations)

- [!] Define RimSort-managed test profiles: preserve the 295-entry product target (the existing 294 plus Rimrooms), then record RimBridgeServer as a separate QA overlay (normally 296 loaded entries). RimSort owns sorting, saving mod lists, and every launch; the owner starts sessions through RimSort. Do not add direct RimWorld or GABS launch profiles or remove target mods to offset the bridge. — blocked: owner-operated RimSort action.
- [!] After the first owner-launched full-target startup, collect matched Core/profile performance baselines on RR-DEV-01 and implement any missing counters per the [benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Enforce the recorded budgets before promoting features or larger room/map bands. — blocked: owner RimSort launch.

### Phase 2 — code architecture and safe vertical slice (master TODO; source largely present per `implementation/PHASE_2_BUILD_RECORD.md`, full stated scope + Gate 2 acceptance still open)

**Core contracts:**

- [ ] Implement one authoritative gate state machine with validated transitions, actions, preconditions, costs, warnings, timers, and event log.
- [ ] Implement a single transaction service for stock/currency/job/project changes; prevent duplicate delivery/reward and never silently discard unsupported transferred items.
- [ ] Implement stable site/coordinate IDs, deterministic seed construction, generator version, room graph records, map ownership, revisit behavior, and bounded cleanup policy.
- [ ] Implement stable references to pawns/buildings/sites via game-supported serialization; avoid stale references and duplicated pawn inventories.
- [ ] Add structured log categories and debug summaries for campaign/coordinate/gate/contract/case/RWT operations. Include seed and failing stage for generated-site errors.
- [ ] Add versioned save components and migration from each released schema before saving or loading content updates.

**Vertical slice implementation:**

- [ ] Create the Async Industries new-game scenario with starter facility, staff, stock, limited funds, disabled gate, first project, and tutorial, following `SCENARIOS.md`.
- [ ] Add gate frame, control console, power requirements, emergency cutoff, assembly/calibration work, operation feedback, failure states, and repair costs.
- [ ] Add staff role recommendations, field kit assignment, readiness checks, and basic company tasks while retaining vanilla pawn/work controls.
- [ ] Create one seeded, finite Backrooms site with a short room graph, one hazard, one learnable entity, one evidence chain, one exit/recall path, and one reward.
- [ ] Add expedition dispatch/recall/close flow; track crew/cargo/location/return and handle death, injury, missing, late return, and aborted runs.
- [ ] Add evidence intake, one lab analysis recipe/project, one researched capability, a payment/contract result, and a traceable company ledger entry.
- [!] Save, reload, revisit the same coordinate, and confirm map state and unique rewards persist without duplication. — blocked: owner RimSort launch.
- [ ] Provide a safe fallback map and recoverable error message when generation cannot produce a valid route.

**Gate 2 passes when** (master TODO): "the first complete loop plays from a fresh save through build, staff, expedition, extraction, analysis, reward, save/reload, and a second visit without a softlock or lost state." — owner-launched only.

### Major M3 — Phase 3 interconnected company simulation (ROADMAP M3; master TODO §Phase 3)

**Scenario framework and alternate starts** (contract: [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md); owner questions still open: inside-start party size; first-exit fixed vs chosen):

- [ ] Preserve native/Prepare Carefully edited pawn instances, relationships, inventory and role choice in all three starts; replace the historical fixed custom-kind roster checks with visible capability/role validation.
- [ ] Honor the company-selected surface world tile through native setup, and give the store its distinct setup/grant/objective flow.
- [ ] Implement the inside-start setup using the recorded provisional defaults while the grouped party/first-exit answers remain pending: direct Backrooms entry without a disposable surface colony, retained real-world state, discoverable physical exit and same-pawn/cargo transfer.
- [ ] Keep the first acceptance target on Async Industries while making its scenario setup consume the same versioned start contract intended for alternate starts.
- [ ] Implement Furniture & Knickknack Store after Gate 2: validate public-area security, store stock/ownership, basement threshold, missing-person objective, and return/contract convergence.
- [ ] Implement Lone Survivor after Gate 2: validate a seeded inside start, one-pawn survival, finite field kit, learned-rule/evidence persistence, return/rescue/outpost alternatives, and no facility prerequisite.
- [ ] Add outpost, town-distortion, or company-in-crisis starts only after a design brief defines their starting state, pressure, failure/recovery, and acceptance evidence.
- [!] Verify every start's reload behavior, deterministic coordinate, objective idempotency, optional-DLC fallback, solo behavior, and RWT eligibility against `SCENARIOS.md`. — blocked: owner RimSort launch.

**Facility and personnel** (source checkpoint: native applicants/hiring + HQ facility observations implemented):

- [ ] Implement physical room functions: gate, control, labs, evidence archive, quarantine/decontamination, medical, armory, workshop, power, radio, receiving, storage, cafeteria, recreation, quarters, and outpost.
- [ ] Connect each room to concrete capabilities, stock needs, staff jobs, risks, and UI alerts; expose why a room is not functional.
- [ ] Add applicant/talent pools for candidates, specialists, contractors, survivors, returning staff, and referrals, with inspectable skills, health, traits, salary/term, and recruit action.
- [ ] Add configurable company roles, staff schedules, certifications, training jobs, field history, trust/stress/exposure and equipment familiarity; preserve pawn autonomy and vanilla skill/trait systems.
- [ ] Add cafeteria, sleep, recreation, injury recovery, shift rotation, staff needs, conflict/wellbeing alerts, and accommodation capacity.
- [ ] Integrate existing hospitality, guest, prisoner, medical, and QoL systems only through evidence-backed adapters; keep native interactions available.

**Gate, equipment, and expedition operations:**

- [ ] Implement native door/endpoint bindings for controlled and mysterious portals, including existing supported sizes, native recolor/aura and deliberate crossing actions.
- [ ] Bind actual control/laboratory equipment and native power grids/batteries to gate installations; show connection failures, consume real energy once and use researched upgrades for aperture, duration, efficiency and saved-coordinate recall.
- [ ] Migrate the older custom gate/console state or document a preserved development-save boundary; retain existing maps, endpoints, crews and cargo through interruptions.
- [ ] Add machine subsystems/upgrades: power reserves, calibration, stabilizers, monitoring, emergency cutoff, cool-down, modules, repair, and reliability.
- [ ] Add field equipment: protective gear, weapons, restraints, med kits, recorder/camera, radio/repeater, mapping gear, detector/scanner, beacon/tether, sample kit, cargo frame, portable power, and tools. *(under the content-reuse rule: existing gear with saved role bindings, no new item Defs)*
- [ ] Give every piece of gear a visible effect on detection, safety, information, cargo, route finding, or return reliability.
- [ ] Add crew composition and cargo planner with skill/health/weight/gate-window checks, ready/unready reasons, and cost preview. *(optional mission UI under the connected-colony contract; must not own connection existence)*
- [ ] Add gate-window progression minutes → hours → days → weeks/months with power, heat, maintenance, supplies, crew rotation, communication, and increasing complexity costs.
- [ ] Add schedule, warning, recall, evacuation, emergency close, lost-connection, failed return, and rescue workflows.
- [ ] Add fog-of-war atlas, route notes, last-known position, evidence chain, return beacon, route clues, saved room graph, and revisit changes.

**Procedural sites and propagation** (contract: [`PROCEDURAL_SPACE_CONTRACT.md`](PROCEDURAL_SPACE_CONTRACT.md)):

- [ ] Implement a tagged room/corridor library and deterministic topology generation by coordinate, mission, equipment, research, company tier, and saved history.
- [ ] Validate map size, accessible entrances/exits, walkable paths, mission objects, safe return clues, playable combat spaces, and generation budget.
- [ ] Add room families, furnishing rules, lighting/material palettes, loot, salvage, hazards, clue placement, threat events, and theme variations.
- [ ] Implement bounded non-Euclidean effects: repeats, moved door/exit, impossible adjacency across site links, altered room dimensions, topology loops, changed object/room identity, and controlled map transitions.
- [ ] Add saved, rule-based anomaly propagation across room graphs with observable clues, equipment detection, player countermeasures, cap/decay, event log, and deterministic save/reload.
- [ ] Make equipment meaningfully change what is detected or generated without breaking seed reproducibility or invalidating an already saved coordinate.
- [ ] Add map state versioning, archival, generator upgrades, explicit migration tests, and recovery if an old site cannot load.
- [ ] Bound active map count, pawn/thing count, graph search, event evaluation, and background tick cost; profile large, long-running saves.

**Economy, contracts, and evidence** (contracts: [`CAMPAIGN_ECONOMY_MODEL.md`](CAMPAIGN_ECONOMY_MODEL.md), [`CAMPAIGN_ECONOMY_PROGRESSION.md`](CAMPAIGN_ECONOMY_PROGRESSION.md); source checkpoint: quotes, supplier custody, payment/refund, partial delivery, rerouting, native-book evidence implemented):

- [ ] Implement branch-local USD financial ledger with auditable entries, payroll, upkeep, purchases, shipments, contract advances, salvage, penalties, compensation, and profit report. Keep ledger balances separate from physical silver/items and prevent duplicate posting.
- [ ] Implement equipment/material procurement, source/price/deadline, shipment manifest, receiving area, delay/loss/damage events, cancellation, and delivery receipt.
- [ ] Implement contract/quest templates for surveys, retrieval, furniture/salvage, samples, transcripts, rescue, containment, security, lease/site construction, town distortion, outpost delivery, and gravship support.
- [ ] Generate bounded story variations from client/faction, coordinate, staffing, discovered rules, company tier, previous outcomes, opening duration, and available equipment.
- [ ] Add space leasing/claiming with cost, boundaries, term, access/security requirements, maintenance, renewal, eviction, and exit/abandonment consequences.
- [ ] Implement evidence provenance/custody/type/value/risk/confidence, sample storage, research value, sale value, client deliverable, archive, chain of custody, and destruction choice.
- [ ] Add analyze/interview/compare/review workflows for equipment, furniture, people, entity remains, recordings, transcripts, route notes, and recovered documents.
- [ ] Add repeated missing-person mysteries with radio fragments, missing crews, delayed return, witness conflict, reappearance/death, rescue, and case closure.
- [ ] Make sale/study/use/contain/release/recruit/detain/transfer choices visible with financial, staff, faction, legal-in-world, trust, and security consequences.

**Research, entity, and expansion progression** (owner S1/B: broad threat families only; the five named sketches in `CAMPAIGN_ROSTER_FREEZE.md` stay deferred until approved):

- [ ] Define research IDs, tier gates, evidence prerequisites, benches, labor/cost, alternative discovery routes, unlocks, dossier output, and fallback when optional research mods/DLC are absent.
- [ ] Complete research branches for facility/power, engineering, field safety, equipment, mapping, communication, stability, containment, medicine, logistics, commerce, orbital operations, and deep topology.
- [ ] Author entity/anomaly design sheets first: appearance/readability, AI rules, triggers, limits, interaction, tells, counters, evidence, study risk, capture/storage, sale value, and fail states.
- [ ] Implement containment rooms, security procedures, prisoner/witness interviews, staff debrief, quarantine, alarm/escape response, evidence custody, and case records.
- [ ] Implement anomaly openings at ordinary RimWorld settlements as timed quests with perimeter, rescue, evidence, witness, close/stabilize, and follow-up objectives.
- [ ] Add outside-gate and inside-site radio stations, supply points, relief teams, depots, guarded space rental, research/shelter outposts, servicing, loss/evacuation, and return routes.
- [ ] Add vehicles and space travel as logistics branches; maintain the gate as the defining Backrooms access mechanism.
- [ ] Add VGE Chapter 1 logistics summary/operations links without replacing its oxygen/fuel/power/heat/crew systems.
- [ ] Add VGE Chapter 2 orbital security/contracts/wreck salvage hooks without patching its gravship internals or mixing orbital enemies into Backrooms entity generation.

### Major M4 — Phase 4 multiplayer, DLC, and the full profile (ROADMAP M4; master TODO §Phase 4)

Every item in this major needs a Rimrooms build the owner has launched; source-side preparation (feature detection, guards, adapters) can proceed, verification cannot.

**RimWorld Together adapter** (pinned release 26.8.31.1; no supported client extension API identified 2026-09-27):

- [ ] Implement feature detection and setup diagnostics for the pinned RWT release; support unavailable/admin-disabled feature states.
- [ ] Implement no custom server schema or patches until supported extension points are identified from the exact code version.
- [!] Verify guild identity, facility mapping, configured visits/snapshot behavior, visits when online/offline, transfer spot, chill/defense spots, caravan interactions, events, sites, roads, aid, gifts, and trading. — blocked: owner-launched two-client run.
- [!] Verify transfer receipt IDs and item/pawn state prevent duplicates, loss, stale ownership, and broken stacks on disconnect/reconnect. — blocked: owner-launched two-client run.
- [!] Verify Backrooms Research Dossier item transfer; receiving branch must explicitly study it locally and be unable to claim it twice in one save. — blocked: owner-launched two-client run; dossier binds to an existing physical document object per the content-reuse rule.
- [!] Test unsupported/complex modded items and define an honest fallback message rather than promising an unverified transfer. — blocked: owner-launched two-client run.
- [!] Test separate colony saves, shared world actions, mod order/config enforcement, RWT server restart/backups, and an admin changing settings during play. — blocked: owner-launched two-client run.
- [ ] Document exact server setup and player experience. No statement may describe live shared-colony control or synchronized research unless implemented and demonstrated.

**Five DLC layers:**

- [ ] Base Core-only campaign works and loads with every DLC absent.
- [ ] Royalty conditional content: titles/quests/faction/psycasts only as optional company routes.
- [ ] Ideology conditional content: beliefs, meditation, rituals, staff policies, and recreation only when available.
- [ ] Biotech conditional content: genes, mechanitors, children, medicine, pollution, and mechanoid options; no mandatory gene/resource dependency.
- [ ] Anomaly conditional content: containment/research links; Backrooms entities retain a base-game implementation.
- [ ] Odyssey conditional content: gravship/off-world logistics and any compatible space travel.
- [!] Before implementing or advertising optional VGE support, verify the clean Core + Harmony + Odyssey + VEF + both VGE chapters stack, Chapter 1 operations, Chapter 2 threat/defense/salvage, optional Insectoids 2, save/reload, and the gravship-touch profile graph. Keep this in the per-integration acceptance gate; it is not a Gate 0 requirement. See the [gravship profile review](research/GRAVSHIP_PROFILE_INTERACTIONS.md). — blocked: owner RimSort launch.
- [!] Verify all five individually enabled/disabled, then all combined. Maintain a 32-row DLC bitmask matrix (all combinations of five DLCs) if claiming full combinatorial support; at minimum, explicitly publish exactly which combinations were run. — blocked: owner RimSort launch.
- [ ] Check DLC-only XML folders, Def references, textures, recipes, quests, C# type lookups, startup without DLC, and save load after toggling DLC.

**All 294 profile entries** (all rows source-reviewed; zero rows runtime-cleared):

- [!] Pin the exact profile and test clean Core, Core+RWT/Harmony, selected VGE stack, each high-risk family, and the full ordered profile. — blocked: owner RimSort launch.
- [ ] For each workbook row, close its status with evidence: reviewed version, load-order placement, applicable DLC, behavior used/preserved, patch/adaptor/no-code reason, and result.
- [!] Verify all QoL features remain available, including work-priority, UI, scheduling, storage, movement, hauling, selection, visitors, prisoners, health, combat, map, and scenario helpers represented in the list. — blocked: owner RimSort launch.
- [ ] Resolve duplicate Defs/patch collisions in the exact 294 profile; use load-after patches only where a reproducible conflict requires one.
- [!] Test gravship-changing profile mods against both VGE chapters; publish incompatible combinations rather than hiding known conflicts. — blocked: owner RimSort launch.
- [ ] Add a user-facing compatibility report with tested order, versions, DLC, known issues, unsupported features, and save caveats.

### Major M5 — Phase 5 complete Company Command interface and polish (ROADMAP M5; master TODO §Phase 5)

Contracts: [`OPERATIONS_ACTION_CONTRACTS.md`](OPERATIONS_ACTION_CONTRACTS.md), [`research/VISUAL_AUDIO_STYLE_BRIEF.md`](research/VISUAL_AUDIO_STYLE_BRIEF.md), [`research/CONTENT_ACCESSIBILITY_BRIEF.md`](research/CONTENT_ACCESSIBILITY_BRIEF.md), [`TUTORIAL_SCRIPT.md`](TUTORIAL_SCRIPT.md). Source checkpoint: ten Operations panes, two original menu images, slideshow controller, settings, dynamic title/version exist.

- [ ] Build the Operations overview and panes: Overview, Personnel, Facilities, Gate, Expeditions, Atlas/Routes, Research/Evidence, Contracts/Ledger, Cases/Containment, Outposts/Company Network, Gravship Operations.
- [ ] Make each screen deep-link to the relevant pawn, building, map, quest, item, research project, evidence record, contract, or RWT site.
- [ ] Add explainable alerts, reason codes, action previews, confirmation only for irreversible losses, undo/recovery where possible, and clear empty/loading/error states.
- [ ] Remap RimWorld's menus, tabs, and campaign views into the finished company-first Company Command layout, growing from the first-playable Operations tab. Keep every relevant Architect, Work, Assign, Research, World, map, building, and pawn action reachable; change navigation and presentation without replacing the underlying colony simulation.
- [ ] Add tutorial/guide, help glossary, keyboard/controller paths as appropriate, color/contrast/readability options, scalable UI, icons/tooltips, and localization support.
- [ ] Create and integrate the approved original RimWorld-style Backrooms main-menu slideshow, preserving provenance, native fallback, supported crops and truthful feature coverage. Show the exact mod title and loaded version beside native top-left version information; use dynamic UI text, not baked image version labels.
- [ ] Integrate the slideshow through the verified 1.6 menu surface without redistributing vanilla/DLC art; keep a disable/fallback route and test it alongside the profile's menu-changing mods.
- [!] Review every slideshow image with the actual menu overlay across supported aspect ratios, resolutions, and UI scales; check text contrast, crop safety, quiet transitions, reduced-motion behavior, and no-audio use. — blocked: owner RimSort launch.
- [!] Review text length, font scale, combat readability, motion sensitivity, audio levels, UI overlap at supported screen sizes, and translations. — blocked: owner RimSort launch.
- [!] Verify no UI panel conceals urgent health, fire, power, missing crew, gate recall, containment, or contract deadlines. — blocked: owner RimSort launch.

### Major M6 — Phase 6 QA, balance, and release (ROADMAP M6; master TODO §Phase 6)

Owner decision D1: private RimWorld Together test build first; public Workshop only after named-profile and multiplayer validation. Reminder from `CONTRIBUTING.md`: do not add/run tests without owner direction; the "automated or manual fixtures" line below is owner-authored scope, not permission to add a test suite unasked.

- [ ] Validate Def references, language keys, patch targets, load folders, package metadata, missing textures/audio, logs, build output, and clean-install folder structure.
- [ ] Create a reproducible fresh-start/save/reload/revisit checklist and automated or manual fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs, and schema migration.
- [!] Run the scenario acceptance checklist for every shipped opening: fresh start, reload, failure/recovery, route back to the shared campaign, and optional-mod/DLC absence. — blocked: owner RimSort launch.
- [!] Exercise invalid states: insufficient power, no operator, blocked route, missing exit, destroyed gate, overloaded expedition cargo, receiving bay full, split/delayed bulk shipment, missing/changed OgreStack setting, dead/missing crew, unsafe return, destroyed relay, unavailable RWT feature, failed item transfer, missing DLC, bad mod order, and old save migration. Include a one-million-silver case: 67 stacks under the active OgreStack default assumption, 2,000 under Core limits; verify actual in-save settings and record hauling/storage/transfer results. — blocked: owner RimSort launch.
- [!] Check performance on worst-case room graphs, multi-outpost company, long play time, many evidence/case records, visitors/prisoners, active threats, and gravship combat. — blocked: owner RimSort launch.
- [!] Balance economy and progression from fresh-start play through late game; check grind, runaway money, research skip routes, dead-end tech, exploitative optimal choices, and difficulty scaling. — blocked: owner-launched play.
- [!] Verify the full mod list one final time and capture game/RWT/DLC/profile versions, settings, logs, save, known compatibility issues, and results in a release report. — blocked: owner RimSort launch.
- [!] Test clean install/uninstall, load order, Workshop update, dedicated RWT server setup, player join, server backup/restore, save migration, and rollback to previous mod release. — blocked: owner-operated.
- [ ] Prepare final mod page, description, feature list, screenshots, trailer/preview art, installation guide, dependencies, DLC matrix, RWT setup, credits, source provenance, license, FAQ, known issues, and update/support plan.
- [ ] Tag release, archive exact source and build artifacts, preserve a known-good server profile, and publish only features that passed their listed acceptance criteria.

### Blocked — owner-launched acceptance (never agent-launched)

- [!] Runtime regression acceptance for these increments and their connected first-expedition loop, after the owner launches the disposable RimSort profile. *(master TODO §Earlier company/scenario increments)* — Blocked by: owner RimSort launch of the 295-entry product target (296 with the RimBridgeServer QA overlay attached afterward). Claude never starts RimWorld, never touches the active RimSort list, never attaches RimBridgeServer outside `research/RIMBRIDGE_TEST_HARNESS.md`.

### Open owner questions (not tasks; answers unblock items above)

- [!] Inside start (`lone_survivor`): configurable party versus strictly lone start.
- [!] Inside start: first reliable exit reveals a fixed discovered surface destination, or the player chooses a settlement.
- [!] Opening-duration clarification (the accepted 20 in-game-minute first window is retained until directed otherwise).

---

## TOMBSTONES

_(none)_
