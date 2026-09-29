# TODO — Minor Task List (Active Tasks)

**Tier 2 of 3** — the MINOR task list. Holds active tasks (pending + in_progress) at the day-to-day work grain. Each minor task lives under a major milestone in `docs/ROADMAP.md` and decomposes further into entries in `docs/DECOMPOSED.md` when YOLO mode picks it up.

Completed tasks move to `docs/FINALIZED.md` per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`. Never delete a task description; only flip status (LAW: NEVER DELETE TODO INFO).

Status markers:
- `[ ]` pending
- `[~]` in_progress
- `[x]` complete (move to FINALIZED.md immediately, never leave here)
- `[T]` belongs to the **post-completion test phase** — cannot be *closed* without the game running, gates no work, and is never a reason to stop building

**There is no blocked-on-owner status, by owner direction 2026-09-28.** Nothing here waits on the owner. Runtime rows are `[T]` and feed one named phase that begins only once the mod is complete; see [`DEFERRED.md`](DEFERRED.md) §The post-completion test phase.

LAW #0 reminder: every task description preserves the user's verbatim words.

**Three-tier cascade:** ROADMAP.md (major) → TODO.md (minor, this file) → DECOMPOSED.md (decomposed). YOLO mode reads all three and works the cascade — see `.claude/commands/yolo.md` and `.claude/WORKFLOW.md §YOLO MODE`.

> **Live project TODO for Rimrooms - Async Industries.** Seeded 2026-09-28 when the Claude Code workflow took over from the previous build agent (ChatGPT 6 Astra). This file carries **every open item** of the complete mod backlog, quoted verbatim from [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) (the "master TODO"), grouped under the majors in `ROADMAP.md` and in the master TODO's own order. The master TODO stays the authoritative gate/evidence record; when an item here closes, tick the identical bounded subitem there in the same change with its evidence link, per `REGRESSION_CONTAINMENT.md`. Items whose source already exists but whose runtime acceptance is open stay `[ ]` — the master TODO's rule: *"Unchecked tasks below retain their full stated implementation/acceptance scope; they do not mean all referenced source is absent."*
>
> Owner sequencing override (2026-09-28): implement remaining systems while game testing is deferred; gameplay-gate statements govern acceptance/promotion, not permission to write source. Only the owner launches RimWorld, through RimSort.

---

## In progress

**Verbatim owner request (2026-09-28, four items):** *"new feature branch for your work start on the todo weork making sure to properly finalize all completed work as i think gate 0 is still in the todo stuff but it should be finalized first and begin on any and all todo work to reach the goal of having a completed working mod in all regaurds as outlined in the many prep documentes build over 18 hours of work in gate 0"*

- [~] **"new feature branch for your work"** — branch `feature/connected-colony-portals` created from `48a8418` (= `Develop` = `Main` on both remotes). Pushed with the first milestone per `PUBLISHING.md`.
- [~] **"start on the todo weork"** — M1 resume steps 1, 2 and 3 CLOSED in 0.4.2-dev, plus the owner's gate traversal rule in 0.4.3-dev (see `FINALIZED.md`). Step 4 is IN PROGRESS: the intent/lease engine and the first adapter family (storage hauling, both directions) shipped in 0.5.0-dev; the remaining families are next.
- [~] **"making sure to properly finalize all completed work as i think gate 0 is still in the todo stuff but it should be finalized first"** — all 129 checked master TODO items archived verbatim in `FINALIZED.md` §Inherited completed work; master TODO checkboxes retained beside their evidence per `REGRESSION_CONTAINMENT.md`.
- [~] **"begin on any and all todo work to reach the goal of having a completed working mod in all regaurds as outlined in the many prep documentes build over 18 hours of work in gate 0"** — standing objective for every session from here: work the cascade M1 → M6 in `ROADMAP.md` order until the master TODO is empty; runtime rows are `[T]` and belong to the post-completion test phase, so none of them ever stops the building.

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
  - [x] Saved work intents, quantity leases and native destination job revalidation — BUILT 2026-09-28 in 0.5.0-dev. `RimroomsConnectedWorkComponent` (saved intents, leases, bounded maintenance), `ConnectedWorkIntent`, `ConnectedRouteService` (bounded; a budget-limited search is pending, never "no route"), `ConnectedWorkAdapter` (candidate half explicitly separated from the definitive native half). Record `implementation/CONNECTED_WORK_IMPLEMENTATION.md`.
  - [x] Physical hauling — BUILT 2026-09-28 in 0.5.0-dev. `ConnectedHaulingAdapter` plus `RR_ConnectedFetch` / `RR_ConnectedDeliver` and two work givers for the family (one high-priority that only finishes committed trips, one low-priority that only starts them). Priorities, schedules, areas, locks, custody and actual inventory are preserved by riding Core's own `JobGiver_Work`; nothing is ever player-forced. Cell storage destinations only; container and provider destinations are deferred.
  - [x] Rescue and remains — BUILT 2026-09-28 in 0.5.2-dev. Our own downed people carried home to a bed (`ConnectedCasualtyAdapter`, Core's `CanRescueNow` far-side check and Core's `Toils_Bed` handoff on arrival); our dead carried home to a grave or storage through the ordinary hauling family. Capture stays a player order by design. Record `implementation/CONNECTED_CASUALTIES_IMPLEMENTATION.md`.
  - [x] Tending across a gate — a doctor crossing to a patient who stays put, or medicine carried to them. A different capability from carrying a person back; not implemented. — BUILT 2026-09-28 in 0.5.9-dev, **both halves as one item**. `TendingProvider` (doctor travels; third deployment provider) and `ConnectedMedicineAdapter` (medicine travels; first family whose cargo is consumed by the work). Nine medical profile rows read from their reviews first. Surgery, patient feeding and prisoner/guest care remain as separately reviewed native routes, recorded in `DEFERRED.md`. Record `implementation/CONNECTED_TENDING_IMPLEMENTATION.md`.
  - [x] Construction supply — BUILT 2026-09-28 in 0.5.3-dev. Real material carried through a gate into a real build site (frame or blueprint), using the site's own material requirement and Core's own container and construct toils. Record `implementation/CONNECTED_CONSTRUCTION_IMPLEMENTATION.md`.
  - [x] Construction finishing — a worker crossing to do build work with nothing carried. Needs the travel-to-work intent shape rather than another adapter; see `DEFERRED.md`. **Owner-selected as the next build (2026-09-28).** — BUILT 2026-09-28 in 0.5.5-dev. `ConnectedDeploymentIntent` (a sibling record, not a new phase on the work intent), `ConnectedDeploymentProvider` with `ConstructionFinishingProvider`, two work givers in Core's `Construction` type at 82 (continue) and 5 (plan), and `ConnectedCrossing` as the one shared gate step. On arrival the deployment issues nothing: Core's own `WorkGiver_ConstructFinishFrames` does the building. Nobody is ever walked home. Record `implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md`.
  - [x] Bills and unfinished work. **Owner-selected as next (2026-09-28): finish the remaining work families before the faction layer.** — BUILT 2026-09-28 in 0.5.7-dev. `ConnectedBillAdapter` carries real ingredients through a gate into storage inside the bill's own `ingredientSearchRadius`, and Core's own `WorkGiver_DoBill` then finds and allocates them. The actual `Bill` is saved by reference, as Core's own `UnfinishedThing` does. **Unfinished work is deliberately out of scope**: Core binds a part-made thing to one creator (`Creator == pawn`, plus `BoundUft`/`BoundWorker`), so no other colonist may ever finish one — delivering material and stopping is the correct behaviour, not a shortfall. `Bill_Medical`, `Bill_Autonomous` and `Bill_Mech` each still need their own source review. Record `implementation/CONNECTED_BILLS_IMPLEMENTATION.md`.
  - [x] Research and stationary work. **Next (2026-09-28).** Should reuse the travel-to-work *deployment* shape rather than a carry adapter: stationary work at a real bench with nothing carried. — BUILT 2026-09-28 in 0.5.8-dev, and it did reuse the shape exactly: `ResearchProvider` is one new file with no new record, driver or JobDef. Five profile rows were read from their existing reviews first (279, 76, 191, 83, 39) and none needed an adapter, because a deployment never issues the work. Record `implementation/CONNECTED_RESEARCH_IMPLEMENTATION.md`.
  - [x] Food. **Next (2026-09-28).** Includes patient feeding (`DoctorFeedHumanlikes` / `DoctorFeedAnimals`), which belongs here rather than with tending. — BUILT 2026-09-29 in 0.6.0-dev as one item with three parts. `ConnectedFoodAdapter` (carry) and `FeedingProvider` (deployment) shipped; the third part, a hungry pawn walking through a gate to eat, is **decided against** rather than deferred, because eating is a think-tree need and a closing gate would strand a starving pawn. Rows 125 Meals On Wheels and 269 Gastronomy were reviewed as part of this item. Record `implementation/CONNECTED_FOOD_IMPLEMENTATION.md`.
  - [ ] Rest and beds. **Next (2026-09-29).** Note the same question food just answered: sleeping is a think-tree need, not work, so expect the answer to be logistical (beds available where people are) rather than sending a tired pawn through a gate. `RestUtility` rejects off-map beds, which is already pinned.
  - [ ] The remaining work/needs families, and every installed work giver in the 294-row profile.
- [ ] **Resume step 5:** "Integrate exact optional work/storage providers and scenario openings, then procedural inhabitants, rare monstrosities, saved events and tech-driven complexity. Keep every wider master TODO feature in scope."
- [ ] **Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change." — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`.

**Required implementation backlog (verbatim from `CONNECTED_COLONY_PORTALS.md`; the acceptance list the majors above must satisfy):**

- [x] Save a portal/endpoint graph independent of expedition records, with distinct laboratory and permanent-natural lifetimes. *(source complete in 0.4.2-dev: graph from 0.4.1-dev plus the address registration that actually creates edges; runtime acceptance open)*
- [x] Implement bidirectional free pawn movement, persistent crossing receipts and stable return endpoints. *(source complete in 0.4.2-dev: `RR_CrossPortal` job + `PortalTravelService`; the step is directional per call and both directions are orderable; runtime acceptance open)*
- [~] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions. *(source partially complete in 0.5.0-dev: discovery, destination targets, bounded routing, planning leases and real native destination reservations exist and are proven for the storage-hauling family only; the other families are not implemented and runtime acceptance is open)*
- [ ] Implement actual cross-portal hauling, construction ingredients, bills/production, research and care/needs access; list each supported native work route with source/acceptance evidence.
- [ ] Reconcile jobs and original cargo on closure/reopen, blocked endpoints, death, save/load and interrupted crossing without duplicating consumption or objects.
- [ ] Integrate relevant profile work/storage/hauling providers; account for all 294 rows without asserting universal support from a successful load.
- [ ] Replace dispatch-only ordinary travel controls and scenario prerequisites; keep optional missions distinct from connection ownership.
- [ ] Persist coordinate/seed/version/site/complexity and generated inhabitants/events; revisit the same saved space without reset.
- [ ] Implement bounded procedural inhabitants/state combinations, rare monstrosities, evolving events and technology-driven complexity families.
- [x] Keep inhabitants and monstrosities in the Backrooms: no non-player pawn crosses any gate on its own, an open gate is never an objective, lure, spawn target, raid route or attack trigger, and anything else returns only carried through by our own pawns, including people and monstrosities that are genuinely downed, dead or imprisoned. Enforced at one chokepoint; see [the rule](#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side) and the [travel record](implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md).
- [ ] Author and implement the saved, bounded escalation ladder: a new coordinate starts quiet; pressure rises only from saved observable causes (operating history at that coordinate, depth and complexity, unlocked technology, what has already been taken out); caps on simultaneous encounters, inhabitants and events per opening and per coordinate, with raising a cap being itself a recorded progression step; quiet stretches as required content; no summing pressure across several open gates; and a revisit that resumes saved pressure without rerolling it up or down.
- [ ] Implement connected-site scheduling/streaming and measure performance after an owner-launched build.
- [T] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants. — post-completion test phase (owner RimSort launch).

**Task-record subitems still open (verbatim from `implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md`):**

- [x] Machine ownership adapter, natural discovery registration and player controls. *(0.4.2-dev: laboratory + natural address registration, deterministic discovered-coordinate API, Operations portal pane with open/close/emergency/crossing/reconcile controls. The discovery **trigger** that finds a new natural threshold in play is owned by step 5 and tracked in `DEFERRED.md`.)*
- [x] Same-pawn crossing, carried-object custody and interrupted-transfer recovery. *(0.4.2-dev: the crossing job and reconcile surface connect the 0.4.1 API; runtime acceptance open)*
- [ ] Saved work intents, quantity leases and native destination job revalidation.
- [ ] Work-specific hauling, construction, bill, research, medical and needs adapters.
- [ ] Optional profile interfaces and native priority/schedule/restriction coverage.
- [T] Owner-launched acceptance: both directions; chains/loops; closed/blocked endpoints; permanent natural links; save/reload; cargo identity; interrupted jobs; all supported native/provider routes. — post-completion test phase (owner RimSort launch).

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

- [T] Define RimSort-managed test profiles: preserve the 295-entry product target (the existing 294 plus Rimrooms), then record RimBridgeServer as a separate QA overlay (normally 296 loaded entries). RimSort owns sorting, saving mod lists, and every launch; the owner starts sessions through RimSort. Do not add direct RimWorld or GABS launch profiles or remove target mods to offset the bridge. — post-completion test phase (owner-operated RimSort action).
- [T] After the first owner-launched full-target startup, collect matched Core/profile performance baselines on RR-DEV-01 and implement any missing counters per the [benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Enforce the recorded budgets before promoting features or larger room/map bands. — post-completion test phase (owner RimSort launch).

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
- [T] Save, reload, revisit the same coordinate, and confirm map state and unique rewards persist without duplication. — post-completion test phase (owner RimSort launch).
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
- [T] Verify every start's reload behavior, deterministic coordinate, objective idempotency, optional-DLC fallback, solo behavior, and RWT eligibility against `SCENARIOS.md`. — post-completion test phase (owner RimSort launch).

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
- [T] Verify guild identity, facility mapping, configured visits/snapshot behavior, visits when online/offline, transfer spot, chill/defense spots, caravan interactions, events, sites, roads, aid, gifts, and trading. — post-completion test phase (owner-launched two-client run).
- [T] Verify transfer receipt IDs and item/pawn state prevent duplicates, loss, stale ownership, and broken stacks on disconnect/reconnect. — post-completion test phase (owner-launched two-client run).
- [T] Verify Backrooms Research Dossier item transfer; receiving branch must explicitly study it locally and be unable to claim it twice in one save. — post-completion test phase (owner-launched two-client run); dossier binds to an existing physical document object per the content-reuse rule.
- [T] Test unsupported/complex modded items and define an honest fallback message rather than promising an unverified transfer. — post-completion test phase (owner-launched two-client run).
- [T] Test separate colony saves, shared world actions, mod order/config enforcement, RWT server restart/backups, and an admin changing settings during play. — post-completion test phase (owner-launched two-client run).
- [ ] Document exact server setup and player experience. No statement may describe live shared-colony control or synchronized research unless implemented and demonstrated.

**Five DLC layers:**

- [ ] Base Core-only campaign works and loads with every DLC absent.
- [ ] Royalty conditional content: titles/quests/faction/psycasts only as optional company routes.
- [ ] Ideology conditional content: beliefs, meditation, rituals, staff policies, and recreation only when available.
- [ ] Biotech conditional content: genes, mechanitors, children, medicine, pollution, and mechanoid options; no mandatory gene/resource dependency.
- [ ] Anomaly conditional content: containment/research links; Backrooms entities retain a base-game implementation.
- [ ] Odyssey conditional content: gravship/off-world logistics and any compatible space travel.
- [T] Before implementing or advertising optional VGE support, verify the clean Core + Harmony + Odyssey + VEF + both VGE chapters stack, Chapter 1 operations, Chapter 2 threat/defense/salvage, optional Insectoids 2, save/reload, and the gravship-touch profile graph. Keep this in the per-integration acceptance gate; it is not a Gate 0 requirement. See the [gravship profile review](research/GRAVSHIP_PROFILE_INTERACTIONS.md). — post-completion test phase (owner RimSort launch).
- [T] Verify all five individually enabled/disabled, then all combined. Maintain a 32-row DLC bitmask matrix (all combinations of five DLCs) if claiming full combinatorial support; at minimum, explicitly publish exactly which combinations were run. — post-completion test phase (owner RimSort launch).
- [ ] Check DLC-only XML folders, Def references, textures, recipes, quests, C# type lookups, startup without DLC, and save load after toggling DLC.

**All 294 profile entries** (all rows source-reviewed; zero rows runtime-cleared):

- [T] Pin the exact profile and test clean Core, Core+RWT/Harmony, selected VGE stack, each high-risk family, and the full ordered profile. — post-completion test phase (owner RimSort launch).
- [ ] For each workbook row, close its status with evidence: reviewed version, load-order placement, applicable DLC, behavior used/preserved, patch/adaptor/no-code reason, and result.
- [T] Verify all QoL features remain available, including work-priority, UI, scheduling, storage, movement, hauling, selection, visitors, prisoners, health, combat, map, and scenario helpers represented in the list. — post-completion test phase (owner RimSort launch).
- [ ] Resolve duplicate Defs/patch collisions in the exact 294 profile; use load-after patches only where a reproducible conflict requires one.
- [T] Test gravship-changing profile mods against both VGE chapters; publish incompatible combinations rather than hiding known conflicts. — post-completion test phase (owner RimSort launch).
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
- [T] Review every slideshow image with the actual menu overlay across supported aspect ratios, resolutions, and UI scales; check text contrast, crop safety, quiet transitions, reduced-motion behavior, and no-audio use. — post-completion test phase (owner RimSort launch).
- [T] Review text length, font scale, combat readability, motion sensitivity, audio levels, UI overlap at supported screen sizes, and translations. — post-completion test phase (owner RimSort launch).
- [T] Verify no UI panel conceals urgent health, fire, power, missing crew, gate recall, containment, or contract deadlines. — post-completion test phase (owner RimSort launch).

### Major M6 — Phase 6 QA, balance, and release (ROADMAP M6; master TODO §Phase 6)

Owner decision D1: private RimWorld Together test build first; public Workshop only after named-profile and multiplayer validation. Reminder from `CONTRIBUTING.md`: do not add/run tests without owner direction; the "automated or manual fixtures" line below is owner-authored scope, not permission to add a test suite unasked.

- [ ] Validate Def references, language keys, patch targets, load folders, package metadata, missing textures/audio, logs, build output, and clean-install folder structure.
- [ ] Create a reproducible fresh-start/save/reload/revisit checklist and automated or manual fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs, and schema migration.
- [T] Run the scenario acceptance checklist for every shipped opening: fresh start, reload, failure/recovery, route back to the shared campaign, and optional-mod/DLC absence. — post-completion test phase (owner RimSort launch).
- [T] Exercise invalid states: insufficient power, no operator, blocked route, missing exit, destroyed gate, overloaded expedition cargo, receiving bay full, split/delayed bulk shipment, missing/changed OgreStack setting, dead/missing crew, unsafe return, destroyed relay, unavailable RWT feature, failed item transfer, missing DLC, bad mod order, and old save migration. Include a one-million-silver case: 67 stacks under the active OgreStack default assumption, 2,000 under Core limits; verify actual in-save settings and record hauling/storage/transfer results. — post-completion test phase (owner RimSort launch).
- [T] Check performance on worst-case room graphs, multi-outpost company, long play time, many evidence/case records, visitors/prisoners, active threats, and gravship combat. — post-completion test phase (owner RimSort launch).
- [T] Balance economy and progression from fresh-start play through late game; check grind, runaway money, research skip routes, dead-end tech, exploitative optimal choices, and difficulty scaling. — post-completion test phase (owner-launched play).
- [T] Verify the full mod list one final time and capture game/RWT/DLC/profile versions, settings, logs, save, known compatibility issues, and results in a release report. — post-completion test phase (owner RimSort launch).
- [T] Test clean install/uninstall, load order, Workshop update, dedicated RWT server setup, player join, server backup/restore, save migration, and rollback to previous mod release. — post-completion test phase (owner-operated).
- [ ] Prepare final mod page, description, feature list, screenshots, trailer/preview art, installation guide, dependencies, DLC matrix, RWT setup, credits, source provenance, license, FAQ, known issues, and update/support plan.
- [ ] Tag release, archive exact source and build artifacts, preserve a known-good server profile, and publish only features that passed their listed acceptance criteria.

### Owner universe direction — period and factions (2026-09-28)

**Verbatim owner request (2026-09-28, ten items):** *"and i havent talked about it but this is 1990's when this all starts and the factions should be the factions of the universe, so US government, other corporations trying to get propietary tech, ex employes disgruntleed, high tech theives, corporate spys and sbaatosh, concerned citizens.. and anything other type of factions along these lines that will increses the backrromms universe feeling as all this needs to be defgault set in the game settup for the differernt scenerios tailored to their scenrerio"*

New binding world direction. It lands on [`UNIVERSE_ADAPTATION.md`](UNIVERSE_ADAPTATION.md), [`SCENARIOS.md`](SCENARIOS.md), [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md) and the M3 scenario framework above, and it **intersects** [`CONTENT_REUSE_POLICY.md`](CONTENT_REUSE_POLICY.md): that policy bans new physical gameplay Defs and M2 already lists `five RR_*Staff PawnKinds` for removal, so whether these factions may author new `FactionDef`/`PawnKindDef` content is an open owner question recorded below, not an assumption.

- [ ] **"this is 1990's when this all starts"** — the campaign's opening period is the 1990s. Affects naming, faction framing, in-world technology language and every scenario's presented setting.
- [ ] **"the factions should be the factions of the universe"** — the world's factions are the Backrooms universe's own factions, not RimWorld's default rimworld factions.
- [ ] **"so US government"** — a US government faction.
- [ ] **"other corporations trying to get propietary tech"** — rival corporation faction(s) whose motive is acquiring the company's proprietary technology.
- [ ] **"ex employes disgruntleed"** — a disgruntled ex-employee faction.
- [ ] **"high tech theives"** — a high-tech thief faction.
- [ ] **"corporate spys and sbaatosh"** — a corporate espionage and sabotage faction.
- [ ] **"concerned citizens.."** — a concerned-citizens faction.
- [ ] **"and anything other type of factions along these lines that will increses the backrromms universe feeling"** — further factions in the same vein wherever they increase the Backrooms universe feeling.
- [ ] **"as all this needs to be defgault set in the game settup for the differernt scenerios tailored to their scenrerio"** — all of the above is default-set during game setup, per scenario, tailored to that scenario.

### Owner direction — always check the mods, and the prep work is where that lives (2026-09-28)

**Verbatim owner requests (2026-09-28, two items):** *"remembre there are research mods you should always be checking mods too"* and *"thats what the prep work was for"*

Standing method, not a one-off task. Before implementing any work family, read the relevant rows of the 294-mod profile — the per-mod reviews in [`research/reviews/mods/`](research/reviews/mods/) already carry verified source facts and a recorded disposition for each one, and re-deriving them from scratch wastes the preparation.

- [x] **"remembre there are research mods you should always be checking mods too"** — applied for the research family in 0.5.8-dev. Four profile rows are research-relevant: 39 Anomaly Research Asteroid, 76 Do Your F\*\*\*\*\*\* Research (`MD.PrioritizeResearch`), 191 ResearchTree Eheieh (`eheieh.researchtree`), 279 Research Whatever (`avilmask.ResearchWhatever`); plus row 83 Dubs Rimatomics, which has its **own separate research table and screen** and is therefore not vanilla `ResearchManager` work at all. All carry the same recorded disposition: optional, no Rimrooms dependency, must work when absent, do not copy code or assets. Position recorded in `implementation/CONNECTED_RESEARCH_IMPLEMENTATION.md`.
- [x] **"thats what the prep work was for"** — binding method for every session from here: consult the existing per-mod reviews and the profile register **first**, rather than re-investigating. Added to the reading order in `NOW.md`.

### Owner compliance direction — RimWorld and Steam terms, official versions (2026-09-28)

**Verbatim owner request (2026-09-28):** *"make sure we are foillowing all rimworld and steam TOS and requirments when it comes to issues similar and the issue of factions and pawn heduffs and the like this mod has to be working with official versions"*

Binding release requirement, and it governs the faction layer above before a line of it is authored. Position and verification: [`COMPLIANCE_AND_OFFICIAL_VERSIONS.md`](COMPLIANCE_AND_OFFICIAL_VERSIONS.md).

- [ ] **"make sure we are foillowing all rimworld and steam TOS and requirments"** — hold the whole package against Ludeon's modding terms and the Steam Workshop and Steam Subscriber agreements, and keep the position current as content is added.
- [ ] **"when it comes to issues similar and the issue of factions"** — `FactionDef` authoring must add definitions only, never redistribute a game or DLC asset. Faction icons and pawn kinds are **referenced by path and defName**, never copied into the package.
- [ ] **"and pawn heduffs"** — the same rule for `HediffDef` and any pawn-attached definition: additive definitions referencing existing content, guarded patches on Core defs, never a copied asset and never a destructive overwrite of a Core def.
- [ ] **"and the like"** — the rule generalises to every def class the mod may add later (thoughts, traits, backstories, incidents, quests, world objects, research). One compliance test, applied to all of them.
- [ ] **"this mod has to be working with official versions"** — the mod targets official RimWorld 1.6 and official DLC only. No modified or patched game assembly, no bundled game binary, no reliance on a non-official build, and no shipped QA overlay.

### Post-completion test phase — `[T]`, gates nothing

- [T] Runtime regression acceptance for these increments and their connected first-expedition loop, after the owner launches the disposable RimSort profile. *(master TODO §Earlier company/scenario increments)* — Needs, in the post-completion test phase: the owner's RimSort launch of the 295-entry product target (296 with the RimBridgeServer QA overlay attached afterward). Claude never starts RimWorld, never touches the active RimSort list, never attaches RimBridgeServer outside `research/RIMBRIDGE_TEST_HARNESS.md`.

### Open owner questions (not tasks; answers unblock items above)

- [x] Inside start (`lone_survivor`): configurable party versus strictly lone start. — **ANSWERED 2026-09-28: configurable party, the player chooses.** Recorded in `GATE_0_DECISIONS.md` and `implementation/GATE_DURATION_AND_COMPANY_NAMING.md`. The M3 scenario row above consumes it.
- [x] Inside start: first reliable exit reveals a fixed discovered surface destination, or the player chooses a settlement. — **ANSWERED 2026-09-28: the player chooses the destination settlement.** This *changed* the earlier provisional fixed-reveal assumption, so M3 must implement a choice, not a reveal.
- [x] Opening-duration clarification (the accepted 20 in-game-minute first window is retained until directed otherwise). — **ANSWERED 2026-09-28 and superseded:** *"you should have the first opening be like 30 minutes of real time not game time there has to be time to acually do shit and it only greatly increases from there once u can re call seeds and better tech and levels to being able to open it indefintality at higherr tech and research and staff and power supplies"*. Implemented in 0.5.4-dev as the tier ladder (108,000 ticks base, ×3 per earned tier, no countdown at the indefinite tier). Natural gates stay permanently open and are exempt.

**Newly opened by the 2026-09-28 universe direction (factions and period):**

- [x] Do the universe factions author new `FactionDef` / `PawnKindDef` content, or must they be built by repurposing existing installed faction and pawn-kind content under `CONTENT_REUSE_POLICY.md`? — **ANSWERED 2026-09-28: new `FactionDef`s, reusing existing pawn kinds.** A `FactionDef` is world configuration, not a physical gameplay Def, so it sits inside the content policy. Each faction's `pawnGroupMakers` point at existing Core/profile `PawnKindDef`s and existing faction icon paths: no new pawn kind, no new texture, no new item. This is what keeps the faction layer clear of M2's deletion of the five `RR_*Staff` PawnKinds.
- [x] Starting hostility per faction per scenario: which of the seven named factions begin hostile, neutral or allied in each start, and what escalates them. — **ANSWERED 2026-09-28: all neutral, escalating from play.** Hostility is earned by what the company actually does, from saved observable causes, reusing the existing bounded escalation-ladder rule rather than a second unrelated one.
- [x] Whether the 1990s period is presentation-and-naming only, or also constrains which existing technology and content a start may grant. — **ANSWERED 2026-09-28: it also constrains starting grants.** Scenario starting equipment and buildings are period-plausible; research may still climb anywhere, so the one-tree-for-every-scenario rule holds and no start can be dead-ended.
- [x] Ordering of the faction layer against the remaining cross-map work families. — **ANSWERED 2026-09-28: keep going down the work families first** (bills, research, tending, food, rest), then the faction and period layer as one clean content checkpoint.

---

## TOMBSTONES

_(none)_
