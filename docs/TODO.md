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
  - [x] Rest and beds. **Next (2026-09-29).** Note the same question food just answered: sleeping is a think-tree need, not work, so expect the answer to be logistical (beds available where people are) rather than sending a tired pawn through a gate. `RestUtility` rejects off-map beds, which is already pinned. — BUILT 2026-09-29 in 0.6.1-dev. The off-map bed rejection was **verified at source** (`CanUseBedNow` returns false when the bed's map differs from the sleeper's `MapHeld`), which closes the tired-pawn question outright rather than by preference, and closes bed ownership across a gate with it. Beds existing on the far side was verified as already covered by the construction families. The one real gap, `RescueInPlaceProvider`, was built: crossing to bed a casualty where they lie rather than hauling them home. Record `implementation/CONNECTED_REST_IMPLEMENTATION.md`.
  - [~] The remaining work/needs families, and every installed work giver in the 294-row profile. **Next (2026-09-29):** cleaning, repair, firefighting, plants/mining/hunting, prisoner and guest care, wardening, childcare, animals and mechs, refuel and rearm, joy, rituals, hauling providers. Expect most to be short: the deployment shape covers anything done at the far site, and the carry shape covers anything delivered. Read the relevant profile rows for each before writing. — **FIRST PASS BUILT 2026-09-29 in 0.6.2-dev:** cleaning, repair, firefighting, mining, hunting, plant cutting, growing-zone work and refuel-with-rearm (eight families, three files, no new record/driver/JobDef). Refuel and rearm turned out to be **one** family, confirmed from Core. **SECOND PASS BUILT 2026-09-29 in 0.6.4-dev:** wardening, childcare and animal handling (three more deployment providers, twenty-two families total). **THIRD PASS 2026-09-29, no new source:** joy and rituals **both decided no**, and the three hauling providers closed as register rows. **Joy has no work type at all** — 23 work types exist across Core and all five DLC and `Joy` is not among them; `JobGiver_GetJoy` is a `ThinkNode_JobGiver` reading `pawn.needs.joy`, so the needs invariant applies exactly as it did to food and rest. **No `WorkGiverDef` anywhere in Core or any DLC is ritual-driven**; a `LordJob_Ritual` owns its participants' duties, so this layer never sees a ritual participant. Hauling rows: Pick Up And Haul (164) has no seam because the connected families run their own job driver rather than `WorkGiver_HaulGeneral`; Haul to Stack (107) is inert alongside 164 by the publisher's own claim, unreproduced; Prison Labor (288) **can never send a prisoner through a gate**, verified from `Pawn.IsColonist` requiring `Faction.IsPlayer`, which a prisoner of the colony never has. Records: `implementation/CONNECTED_WORK_FAMILIES_IMPLEMENTATION.md` and `research/WORK_TYPE_COVERAGE_AUDIT.md`. **FOURTH PASS BUILT 2026-09-29 in 0.6.5-dev:** bill work as **five** families, one per work type — 27 families. Record `implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md`. **FIFTH PASS BUILT 2026-09-29 in 0.6.6-dev:** dark study — 28 families. Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`. **SIXTH PASS BUILT 2026-09-29 in 0.6.7-dev:** hauling upkeep, BasicWorker and Fishing — **31 families, 23 of them deployments**. **Every work type in the game is now either covered or decided against with its reason recorded.** Record `implementation/WORK_TYPE_GAPS_CLOSED_IMPLEMENTATION.md`. **Why this row stays `[~]` and not `[x]`:** the Core half is finished, but the row's own words are *"and every installed work giver in the 294-row profile"*, which is broader. What remains is named rather than vague: the **eleven DLC container hauling givers** (each needs a custody review before a worker crosses for it), the **four painting givers** in `Art`, and any **mod-added work type** with its own givers — the bill family covers modded *benches* inside existing work types automatically, but a wholly new work type gets no provider, because the providers and their giver defs are shipped rather than derived. Recorded in `DEFERRED.md`.

**This row does NOT close on completeness.** The remembered list above was checked against the shipped game data and found **incomplete**: it omitted `DarkStudy` and `Fishing` entirely, and both are real work types with no mention anywhere in the mod's source. The enumeration is in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md) — 23 work types, 145 giver defs, coverage read out of the mod's own source. Four genuine gaps remain, recorded below as new rows because this is new information rather than a restatement.

- [x] **Bill work deployment** — **BUILT 0.6.5-dev** as five families, one per work type, because `WorkGiver_DoBill.StartOrResumeBillJob` compares a recipe's `requiredGiverWorkType` against `def.workType` and a bench belongs to a work type only through `fixedBillGiverDefs`. The bench set is unioned from the loaded giver defs, so a modded bench in an existing work type is covered with nothing named. Also **closed a shipped defect**: the carry family's `is Bill_Production` filter admitted `Bill_Autonomous` and `Bill_Mech`, which derive from it, contrary to that family's own record. Record `implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md`. Was: the largest gap and the one the bills record left open. `CONNECTED_BILLS_IMPLEMENTATION.md` settles delivering ingredients to a bill that `ShouldDoNow()` but never decides **who runs the bill** once the material is there, so a bench on a coordinate with nobody standing on it accumulates ingredients and produces nothing. The `UnfinishedThing` fact that record pins argues *for* a deployment: `ClosestUnfinishedThingForBill` validates `Creator == pawn` and `Bill_ProductionWithUft` binds `BoundUft` to a `BoundWorker`, so a half-made thing belongs to one colonist — which is why the *carry* family must never touch one, and why a **deployed** worker running Core's own `WorkGiver_DoBill` locally is correct by construction. One family covers `Cooking`, `Crafting`, `Smithing`, `Tailoring` and the sculpting half of `Art`.
- [x] **DarkStudy deployment** — **BUILT 0.6.6-dev.** **28 families, 20 of them deployments**. Core's own scanner takes an explicit map (`GetStudiableThingsAndPlatforms(pawn.Map)`) and that method is a pure read of a per-map cache, so the candidate half is exact rather than reimplemented. Also **closed a second shipped defect**: the two childcare giver defs referenced the Biotech-only `Childcare` work type with **no `MayRequire`**, an unresolved cross-reference at load on a Core-only install since 0.6.4-dev — the same careful-C#-beside-a-contradicting-def shape as the `Bill_Production` defect. `tools/check-dlc-gating.py` now indexes the game's own data (6,063 DLC-only defs) so it cannot recur. Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`. Was: Anomaly's single giver `StudyInteract` / `WorkGiver_DarkStudyInteract`, priority 110. Studying a contained entity is what this company does and a containment facility behind a portal is the premise, making this the most thematically apt item in the audit. `WorkTypeDefOf.DarkStudy` is `[MayRequireAnomaly]`, so it gates through `GetNamedSilentFail` exactly as `Childcare` does for Biotech.
- [x] **Hauling upkeep deployment** — **BUILT 0.6.7-dev.** All thirty `Hauling` givers enumerated and classified: seven covered by existing carry families, three **decided against** because their semantics are map-bound (`HelpGatheringItemsForCaravan` and `LoadTransporters` depart from their own map; `HaulToPortal` is Core's own portal system), eleven DLC container givers named and left open pending a custody review, and four built here. Its continue priority follows the **Hauling ladder's own documented exception** rather than the generic rule. Was: the carry families cover material crossing a gate, but the `Hauling` givers that are **local container operations on the far map** have no coverage at all: `EmptyEggBox`, `FillFermentingBarrel`, `TakeBeerOutOfFermentingBarrel`, `EmptyWasteContainer`, `HaulMechsToCharger`, `UnloadCarriers`, `TakeBioferriteOutOfHarvester`. Same shape as the bill gap. This also covers the `HaulMechsToCharger` half of the *"animals and mechs"* item above; `RepairMech` sits in `Smithing` and belongs to the bill row.
- [x] **BasicWorker deployment, and Fishing settled first** — **BOTH BUILT 0.6.7-dev.** BasicWorker is purely designation-driven (`Flick`, `Open`, `EjectFuel`), so it reuses `FieldworkScan`. `Fishing` was settled and then overtaken: a coordinate *does* carry water (`GenStep_BackroomsDestination` uses `WaterDeep` as its void floor), but the deciding fact is that Core will not fish anywhere the player has not painted a `Zone_Fishing` — so it is the growing-zone shape and the terrain question is not load-bearing. Was:  — `Flick` is designation-driven, which puts it with the fieldwork families where nothing is inferred, and toggling a switch on a far map is a real thing a player cannot currently get; `Open` is likewise a designation on a specific container. `Fishing` (Odyssey, one giver, `[MayRequireOdyssey]`) needs water on the map, so **settle the generation question first** — if a generated coordinate never has fishable water the honest record is that the family is unnecessary rather than unbuilt.
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
- [x] Keep inhabitants and monstrosities in the Backrooms: no non-player pawn crosses any gate on its own, an open gate is never an objective, lure, spawn target, raid route or attack trigger, and anything else returns only carried through by our own pawns, including people and monstrosities that are genuinely downed, dead or imprisoned. Enforced at one chokepoint; see [the rule](CONNECTED_COLONY_PORTALS.md#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side) and the [travel record](implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md).
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

### Owner universe direction — the Backrooms has no outside (2026-09-29)

**Verbatim owner request (2026-09-29, five items):** *"and remembr a backrooms environment can never have an out side in of itselfe so mods like remove roof for removing mountain need something in our mod so that the full seed map for a backrroms seed instance is entirely inside "mountain roof" and all roof in a backrroms is never revovable and no one in any scerio can find them selfs in a world map eara but by finding a portal in the backrromms leading out of the backrrooms liken the one the scenerio start has for the furnature store and the one that the solo/group start has to be able to get out and start building thsir facility"*

**Binding containment rule, and the strongest world constraint in the project.** It governs `Generation/`, the roof handling on every generated coordinate, and every scenario start. It also **constrains work families already built** — see the conflict note below.

- [ ] **"a backrooms environment can never have an out side in of itselfe"** — no generated Backrooms map may contain an outdoor cell. There is no sky and no exterior anywhere inside one.
- [ ] **"so mods like remove roof for removing mountain need something in our mod so that the full seed map for a backrroms seed instance is entirely inside \"mountain roof\""** — the whole seed map, edge to edge, sits under thick mountain roof, and the mod must supply whatever is needed to hold that against mods that remove roof or mountain.
- [ ] **"and all roof in a backrroms is never revovable"** — no roof anywhere in a Backrooms map may ever be removed, by any means.
- [ ] **"and no one in any scerio can find them selfs in a world map eara but by finding a portal in the backrromms leading out of the backrrooms"** — the **only** way out of the Backrooms into a world map area is a portal found inside the Backrooms. No scenario may provide any other route out.
- [ ] **"liken the one the scenerio start has for the furnature store and the one that the solo/group start has to be able to get out and start building thsir facility"** — the furniture store start and the solo/group start each begin with exactly such a portal, which is how those starts reach the world and begin building a facility.

**Superseded by the refinement below:** an earlier note here guessed that mining, roof removal and roof building would all have to be refused inside a Backrooms map. Mining and deconstruction are **not** refused; see the refinement and the verified Core fact that thick roof never vanishes on collapse.

**Verbatim owner refinement (2026-09-29, four items):** *"but all rooms and walls and doors are all deconstructable and areas minable and of all types of materisals throughout and capte ands  tile can all be uninstalled , moved, resued , sold , studied, all of it"*

This **narrows** the containment rule above rather than widening it, and it is the better design: the interior is fully interactable, and only the roof and the absence of an outside are inviolable.

- [ ] **"all rooms and walls and doors are all deconstructable"** — every wall and door inside a Backrooms coordinate can be deconstructed like any other building.
- [ ] **"and areas minable and of all types of materisals throughout"** — the solid areas of a coordinate are mineable, and in a variety of materials across the map.
- [ ] **"and capte ands tile can all be uninstalled , moved, resued , sold , studied"** — carpet and tile can be uninstalled, moved, reused, sold and studied.
- [ ] **"all of it"** — the whole interior, without exception, is available to strip, move and use.

**Position recorded 2026-09-29, and it corrects a wrong instinct of mine:** the earlier conflict note guessed that mining inside a Backrooms coordinate would have to be *refused* to protect the roof. That guess was wrong and this refinement overrides it. **Mining stays fully allowed**, because of one Core fact verified in source: `RoofDef.VanishOnCollapse => !isThickRoof`, so **thick rock roof never vanishes when it collapses**. Mining out the support under it produces rubble and a collapse, exactly as it does under any mountain — and the map stays roofed. Containment therefore survives unlimited mining without a single restriction on the player.

What does need real work, because vanilla does not provide it:

- **The roof itself.** `WorkGiver_RemoveRoof` is driven by `map.areaManager.NoRoof` and contains **no** check for natural or thick roof, so vanilla alone can already strip a Backrooms ceiling. A guard is required, which is precisely what the owner meant by *"mods like remove roof for removing mountain need something in our mod"*.
- **Floors being recovered.** Vanilla returns no materials when a floor is removed, so *"uninstalled, moved, resued, sold"* for carpet and tile is a content feature rather than a setting, and it needs its own decision under `CONTENT_REUSE_POLICY.md`. Named here rather than assumed.

**Verbatim owner constraint (2026-09-29, three items):** *"but we still have to be able to use build roof and maountain roof remove and bbuild mountain wall on the normal maps of the world"*

- [x] **"we still have to be able to use build roof"** — roof building stays fully available on ordinary world maps.
- [x] **"and maountain roof remove"** — mountain-roof removal stays fully available on ordinary world maps.
- [x] **"and bbuild mountain wall on the normal maps of the world"** — building mountain wall stays fully available on ordinary world maps.

**Satisfied by construction, not by a special case.** `BackroomsContainmentMapComponent` tests one thing before it does anything at all: whether the map is a `RimroomsDestinationMapParent` with a ready layout. On a colony map, a quest site, or any other ordinary world map that test fails and the component returns immediately — it never clears a no-roof area and never re-roofs a cell there. So every vanilla roof and mountain tool behaves exactly as it always did outside the Backrooms, and the containment rule applies only where the fiction requires it.

This also means the guard cannot regress an existing colony, which is the same standard the content policy sets for everything else in this mod.

### Owner universe direction — continuous portal topology across every start (2026-09-29)

**Verbatim owner request (2026-09-29, seven items):** *"and remember the solo/group start  and industry async start and furnature store start all need thier portals and back rooms to sum what be continues... ie a back room can have a protal to another normal worlds map or a portal to a deep level of the backrooms ect ect so that any one backrooms portal corroridanet weither from a lab portal or a natural portal can lead to other places and other backroom instance seeds, and or pop out any where in the game world on a tile map"*

Binding topology requirement. It governs `RimroomsPortalNetwork`, `PortalAddressService`, `NaturalFrontierService`, the generation layer in `Generation/`, and all three scenario starts. Read [`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md) and [`PROCEDURAL_SPACE_CONTRACT.md`](PROCEDURAL_SPACE_CONTRACT.md) alongside it.

- [ ] **"the solo/group start  and industry async start and furnature store start all need thier portals and back rooms to sum what be continues"** — all three starts share one continuous portal topology; no start gets a dead-end or a different set of rules.
- [ ] **"a back room can have a protal to another normal worlds map"** — a Backrooms coordinate may hold a portal leading to an ordinary world map.
- [ ] **"or a portal to a deep level of the backrooms"** — a Backrooms coordinate may hold a portal leading deeper into the Backrooms.
- [ ] **"ect ect"** — and onward in the same manner; the topology is not limited to a fixed set of link kinds.
- [ ] **"so that any one backrooms portal corroridanet weither from a lab portal or a natural portal can lead to other places"** — every Backrooms coordinate, reached by a laboratory gate **or** a natural portal, can lead onward to further places. The link kind that brought you there never restricts where you can go next.
- [ ] **"and other backroom instance seeds"** — onward links may reach other Backrooms instance seeds, not only the one you are in.
- [ ] **"and or pop out any where in the game world on a tile map"** — an onward link may emerge anywhere in the game world, on a world tile.


**Verbatim owner clarification (2026-09-29, five items):** *"so what i mean by that is there can be portals with in portals and portals found on world maps when u do the cites and build the furnature store and starting lab maps basic defaults for starting equipment and posible starting facilities if you know how to do that or we just give them starting equipment building and supplies and they build it all, i dont know how good you will be at designing starting building faciliteis and portals  and stuff but we can try"*

- [ ] **"there can be portals with in portals"** — a portal may be reached from inside a space that was itself reached by a portal, without limit on nesting.
- [ ] **"and portals found on world maps"** — portals exist to be found on ordinary world maps, not only inside the Backrooms.
- [ ] **"when u do the cites and build the furnature store and starting lab maps basic defaults for starting equipment and posible starting facilities"** — site generation and the store and starting-lab maps carry basic defaults for starting equipment and, where possible, starting facilities.
- [ ] **"if you know how to do that or we just give them starting equipment building and supplies and they build it all"** — owner-offered fallback: if authored starting facilities are not workable, ship starting equipment, building materials and supplies and let the player build everything.
- [ ] **"i dont know how good you will be at designing starting building faciliteis and portals  and stuff but we can try"** — explicit permission to attempt authored starting facilities, with the fallback above available.

**Verbatim owner clarification (2026-09-29, two items):** *"remember map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map are just a few of the portal connections allowed in the game to different maps in the world"* and *"with different portal combos built and found"*

This settles the shape of the topology: **an unbounded alternation of ordinary world maps and Backrooms coordinates, in any order, to any depth.** Not "the Backrooms nests inside itself" and not "the Backrooms has an exit" — those are two special cases of one rule. A chain may re-enter the world and leave it again as many times as it likes, and the sequence of map and Backrooms segments is arbitrary. "different maps in the world" means the ordinary-map endpoints are not all the same map either.

- [ ] **"map>backrrooms>backrroms"** — an ordinary world map leads to a Backrooms coordinate, which leads to another Backrooms coordinate. **This chain already routes end to end.** 0.6.3-dev made a way onward findable on an ordinary map, and a coordinate has always been able to hold onward links into further coordinates, so nothing is needed for this one.
- [ ] **"map > backrooms > map > backrooms"** — the chain returns to an ordinary world map partway along and then re-enters the Backrooms. **Blocked on the one open piece:** a portal whose far side is an ordinary map. `RegisterNaturalAddress` takes a `CoordinateRecord` and `DestinationService.EnsureSite` produces a generated Backrooms map for it, so the far endpoint cannot yet be anything else.
- [ ] **"backrromms > map>backrooms>backrooms>map"** — starts inside the Backrooms, leaves to the world, goes two coordinates deep, and leaves to the world again. Needs the same open piece, used twice, and confirms that a chain may both begin and end outside the Backrooms.
- [ ] **"are just a few of the portal connections allowed"** — these three are examples, not an enumeration. No length limit, no ordering rule, and no forbidden combination of map and Backrooms segments.
- [ ] **"to different maps in the world"** — separate ordinary-map endpoints along one chain may be separate world maps. A chain that leaves the Backrooms twice need not come out in the same place.
- [ ] **"with different portal combos built and found"** — laboratory-built gates and naturally-found frontiers may be mixed freely along a single chain. **The non-restriction half of this is already true:** routing does not discriminate by `PortalConnectionKind`, and `Availability` consults the gate window only for `Laboratory` edges, so arriving by one kind never constrains which kind you may leave by.

**Ordering note:** every unchecked row above resolves to the same single piece of work — the ordinary-map endpoint, already queued. Building it once satisfies all of them, which is why they are recorded as one direction rather than split into separate tasks.

**Position on the last two rows, recorded 2026-09-29 so it is not re-litigated:** the starting facilities do **not** need designing from scratch. [`SCENARIOS.md`](SCENARIOS.md) already specifies all three in detail — the Async Industries 60x60 headquarters with its secured perimeter, dormitory, mess, storage, infirmary corner, workshop, research bench, utility generator with reserve battery and a gate chamber assembled to roughly three-quarters that cannot open yet; the 50x50 store with sales floor, stockroom, office, staff room and a basement threshold that is not a working machine gate; and the lone-survivor generated 6-8 room coordinate with a restable shelter, limited supplies, at least two connected route clues and a traversable path to an objective and a possible exit. So this is implementation against an existing specification, not invention, and the fallback is not needed unless a specified element turns out to be unbuildable under the existing-content-only policy.

### Owner direction — model gate upkeep on Questionable Ethics' vats (2026-09-29)

**Verbatim owner requests (2026-09-29, two items):** *"kinda like maintaince for growth vats questionable ethitcs so pawns dont have to always do it but there is a cool down dead zone where its fine"* and, correcting my misreading, *"i said i was refresncing the mod \"Questional ethics\" and how maintaince works on cloning vats and organ vats"*.

**I first read "questionable ethics" as flavour and went as far as asking which way to take the ethics angle. That was wrong.** It is a **mod name** — *Questionable Ethics Enhanced*, **profile row 182** — and the owner was pointing at a concrete, proven mechanic. **The register recovered it in one query**, and its review carried the package id and install path that led to the mod's own defs.

Record: [`implementation/GATE_SERVICING_IMPLEMENTATION.md`](implementation/GATE_SERVICING_IMPLEMENTATION.md).

- [x] **"how maintaince works on cloning vats and organ vats"** — read from that mod's own shipped description: *"Requires regular maintenance by a skilled scientist and doctor. A sterile room will significantly decrease the maintenance required. If the vat loses power, it will rapidly lose maintenance."* Three ideas, all better than a service timer: a condition that **decays continuously**; **the room modulating the decay**; and **power loss degrading it fast**.
- [x] **"so pawns dont have to always do it but there is a cool down dead zone where its fine"** — the dead zone **falls out of the model rather than being bolted on**. A well-kept room decays so slowly that nobody is called for a long stretch; a filthy one calls somebody constantly. **The player controls the dead zone by looking after the place.** Reinforced by a hard threshold: the work is offered only below a quarter condition and restores full in one visit, so nobody tops it up continuously — the growth-vat-one-nutrition-short trap.
- [x] **Nothing of that mod is copied, referenced or depended on.** Its defs and assembly are untouched and the feature works with it absent. The idea was read from its public description exactly as every profile row is read, which honours *"we are making a mod that works with the other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*
- [x] **It plugs into what already exists** rather than sitting beside it: cleanliness is kept by the cleaning family (which already crosses a gate), power ties to the kill switch built the checkpoint before, and skill reuses the `Research` work type calibration already uses, so **no new work type is added**.
- [x] **Lapsing stops the next opening and never closes one already running** — ending an opening for a bookkeeping reason would strand whoever is on the far side.

### Owner direction — the gate must keep meeting its requirements, and a how-to is owed (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and remember the gate doent always stay open we need requirment s to be maintained and reached.. ie power(its a big draw if power runs out gate closes, research(maintained amounts of maintance and research on equipment but not crazy amounts like i say the first gate opening should be liek 30minuites real time only increasing from there, and eventually we will need to write a how to to the game paly and systems"*

**Checked against the shipped values rather than assumed. Three of the four already match exactly**, and saying so is more useful than rebuilding them:

- [x] **"power(its a big draw if power runs out gate closes"** — already true every tick: `HasPowerAndHeadroom()` fails and `TickGate` calls `EnterEmergency("RR_Gate_PowerLost")`. An open gate also spends energy every tick through `SpendNativeOpeningTick()`, so running the supply dry ends a sustained session exactly as losing power does.
- [x] **"the first gate opening should be liek 30minuites real time"** — already exactly that. `portalBaseWindowTicks = 108000`, and 108,000 ÷ 60 ticks per second = **1,800 seconds = exactly 30 real minutes** at normal speed.
- [x] **"only increasing from there"** — already: `portalWindowMultiplierPerTier = 3f` per earned tier, and `portalIndefiniteTier = 4` stops the countdown entirely while power, operator and energy hold.
- [x] **"research"** — already: tiers come from **completed** projects listed in `portalWindowTierProjects`, never from spendable insight, so a tier can never be lost by spending currency on the next one.
- [x] **"maintained amounts of maintance ... on equipment but not crazy amounts"** — **BUILT 0.7.1-dev**, modelled on the reference the owner gave in a later message (see below). Was: **GENUINELY NEW. There is no equipment-upkeep concept anywhere in the gate today.** Needs its own checkpoint: what wears, what restores it, what lapsing costs, and the owner's explicit ceiling that it must not be *"crazy amounts"*. Build it from existing content only — Core's own repair, `CompRefuelable`, breakdown or bill-driven servicing, matched by capability rather than by name.
- [ ] **"eventually we will need to write a how to to the game paly and systems"** — a player-facing how-to for the gameplay and the systems. `docs/HOWTO.md` exists but documents **the build**, not play. This is a real deliverable and is owed; scope it once the systems stop moving.

### Owner direction — a kill switch for the laboratory gate (2026-09-29)

**Verbatim owner request (2026-09-29):** *"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies.. idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"*

Not yet built. Recorded here in full the moment it was asked so it cannot be lost, and scoped to its own checkpoint rather than folded into the emergence work that was in flight.

- [x] **"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies"** — **BUILT 0.7.0-dev.** An optional cutoff bound to a Core power switch, refused unless the switch is **closed and on the gate's own power net**, which is what separates a real kill switch from a decorative one: sharing a net while closed means opening it *necessarily* severs the supply, using Core's own power graph rather than simulating anything. Thrown ends the opening at once with its own cause, checked **before** the generic power test so a deliberate shutdown is never logged as a snapped conduit. **The emergency-return window is deliberately kept** — it is why the gate reserves watt-days, and one flick should not permanently strand the far side. Record `implementation/GATE_KILL_SWITCH_IMPLEMENTATION.md`. Was:  — a player-operable switch that closes an open laboratory gate at once by cutting its power. What already exists to build on: `CompRimroomsGate` is a native provider carrying `nativeConsole`, `nativeBattery` and `nativeAssemblyBench`; `NativeBindingFailureKey` already reports `RR_NativeGate_PowerUnavailable` when power is unavailable; and there is already an emergency-return window with its own reserved watt-days. What is missing is the **deliberate** act: cutting power today makes a gate *unavailable*, which is not the same as *closing it now on purpose*, and the difference matters when somebody is on the far side.
- [x] **"idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"** — answered by making the **wiring real rather than cosmetic**: the bind is refused unless the switch genuinely carries the gate's power, matched by capability (`CompFlickable` + `CompPowerTransmitter`) so a modded switch works unnamed, one switch to one gate, and the whole thing optional so no saved gate needs rebinding. A further consequence fell out for free: flicking is ordinary `Flick` work and this mod gained cross-gate `BasicWorker` support in 0.6.7-dev, so somebody at home can be ordered to throw the cutoff while a team is still inside. Was:  — open design latitude on how the equipment interconnects. Read `implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md` and the gate records before proposing, and keep every piece existing content: Core's own `PowerSwitch`, conduits, batteries and consoles, matched by capability rather than by name.

### Owner direction — the other half of the topology: a way out into the world (2026-09-29)

**Verbatim owner requests, carried from the topology direction:** *"and or pop out any where in the game world on a tile map"*, and the worked examples *"map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map"*.

Record: [`implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md`](implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md).

- [x] **A portal whose far side is an ordinary map** — **BUILT 0.6.9-dev** as `PortalConnectionKind.Emergence`, an appended enum value. Recorded **anchor-first** (`First` = the marked door on the ordinary branch-owned map, `Second` = the coordinate doorway), which is the same orientation every other kind uses — so `Availability`, the site check in `Register` and the uniqueness rule all needed **no change at all**. This is what makes `map > backrooms > map > backrooms` and `backrooms > map > backrooms > backrooms > map` route end to end.
- [x] **The player marks where it comes up, and nothing ever picks for them** — `CompRimroomsEmergence` on Core `Door` and `Autodoor`, added by one additive patch beside the existing gate comp, dormant until marked. This inherits 0.6.3-dev's rule with more force, because a way out arrives **at** the player's own map: *a door the player built is never quietly turned into a hole in the world*. Marking is refused inside the Backrooms — a way out cannot come up in the place it leads away from — and the command is not even offered there.
- [x] **Withdrawing a mark leaves an existing way out alone** — it means "no more ways out here", not "close the one that exists". A saved edge is evidence of a place somebody found.
- [x] **Found by surveying, with its own independent draw** — a distinct seed key from the frontier draw so the two can never correlate, derived from the coordinate's own seed and the doorway's position so it is stable across saves and revisits. **One in three** ways onward leads out, deliberately common, because a way home is what makes the topology usable rather than a trap. With nothing marked the doorway leads deeper instead: a fallback, not a refusal.
- [ ] **A world tile the branch does not hold** — still the larger half, needing a new world object and a generated map. Its own checkpoint.
- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` across a gate** — `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded these as a dependency of exactly this endpoint, and they are **now genuinely live rather than hypothetical**: an ordinary map is reachable through a gate, and a colony map gets snow, wants roofs built, and may be polluted.

### Owner direction — zones must work on both sides of any gate (2026-09-29)

**Verbatim owner requests (2026-09-29, two items):** *"we also need to make sure zones work properly when putting them on boith sides of any type of gate"* and *"and as a continueations through the gate"*

Full audit in [`research/ZONES_AND_AREAS_ACROSS_A_GATE.md`](research/ZONES_AND_AREAS_ACROSS_A_GATE.md), which covers every zone and area type in the game against what the work layer does with it.

**The constraint that shapes every answer:** a RimWorld `Zone` **cannot span two maps** — `Zone.Map` is single-valued and `ZoneManager` is per-map, and the same holds for every `Area`. So a zone that "continues through the gate" cannot be one object. What it has to mean instead is that two zones, one each side, **behave as one**: goods flow between them, work on either side attracts somebody, and the far one's own settings are what get respected. That is the standard the audit holds every case to.

- [x] **"we also need to make sure zones work properly when putting them on boith sides of any type of gate"** — audited every zone and area type. `Zone_Stockpile` works both directions (the far zone's own filter and priority decide, through `IsValidStorageFor(storeMap, thing)`); `Zone_Fishing` works; `Area_Home` works for cleaning, repair and firefighting; `Area_Allowed` works as a recorded observation plus the definitive check on arrival; `Area_NoRoof` is deliberately emptied inside the Backrooms by the containment rule. **`Zone_Growing` was broken and is fixed** — see below.
- [x] **"and as a continueations through the gate"** — continuation is satisfied functionally rather than by linking objects, and deliberately so. Nothing gives two zones a shared name or copies settings between them, and neither would be an improvement. Two stockpiles either side of a gate are already continuous in the sense that matters: put something in one and a hauler moves it to the other when the other is a better home for it. The failure mode to avoid was never "they are not linked" but **"a zone on the far side is invisible to the work layer, or visible but impossible"**.
- [x] **Zones persist across visits, which is the precondition for all of it** — `RimroomsDestinationMapParent.ShouldRemoveMapNow` returns `false` unconditionally, so a coordinate map is never removed and every zone painted there survives leaving and returning, with its settings.
- [x] **DEFECT FIXED: a growing zone inside the Backrooms could never be sown, and held the worker there anyway.** `ZoneHasWork` decided sowing was wanted from three facts about the *zone* and never asked whether the *cell* could be sown. Coordinate rooms are floored with `Concrete` and `PavedTile`, both of which inherit `FloorBase`, declare no `fertility` and so carry the field default of **0**, while every Core plant needs `fertilityMin` of at least **0.01**. So a grower was sent, Core refused on arrival — **and `HasWorkHere` asked the identical question and also said yes, so the deployment was never released** and the worker stood in the Backrooms indefinitely with a live commitment. Worse than a wasted trip: a wasted trip costs one walk, a deployment that will not release costs a colonist. Fixed by adding Core's own `CanEverPlantAt` and `PlantUtility.GrowthSeasonNow`, both of which read the cell and its own map and take no pawn.
- [x] **A wrong hypothesis corrected on the way** — the first theory was that a fully-roofed coordinate blocks sowing for lack of **sunlight**. It does not: `GrowthSeasonNow` reads room and temperature, not light, and Core sows indoors happily. The real gate is **fertility**, and building on the light theory would have produced a check that tested the wrong thing.
- [ ] **Three area types are not covered, and that is correct only until the far side of a gate can be an ordinary world map.** `Area_BuildRoof` (a coordinate is already all thick rock), `Area_NoRoof` (removal is forbidden there by the world rule), and `Area_SnowOrSandClear` / `Area_PollutionClear` (a coordinate has no outside, so no weather). **Revisit all of them when the ordinary-map endpoint lands** — a colony map does get snow, does want roofs built, and may be polluted.

### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)

**Verbatim owner request (2026-09-29, seven items):** *"read Now. md and any and all revent prep docs as you continue the todo work and take not there is a mode .xlml like thing that im not sure is fully working i try to open it but its not human navigatable but its suppose to spreeadsheet out all the mods and potential uses and issues and theri uses and descriptions and shit if i remember correctly and you should definatly be using it and or fixing it up as you go along with build the Mod here and or update it where need of past work already done and continue it forward and making sure it is human havigate able becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"*

**Verbatim owner identification (2026-09-29):** *"Rimrooms_Async_Industries_294_Mod_Integration_Register this thing is what i was talking about"*

**Verbatim owner report (2026-09-29, the root cause):** *"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt??? wtf i thought it was the mod spreedsheeet! fix it"*

Full record in [`implementation/MOD_REGISTER_REBUILD.md`](implementation/MOD_REGISTER_REBUILD.md); the work-type findings it produced are in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md).

- [x] **"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt???"** — **not a file problem, and it outranks every XML defect below.** Checked the machine: `.xlsx` has **no registered association at all** (`assoc .xlsx` returns nothing, no `UserChoice` key) and **no spreadsheet application is installed anywhere** — no Excel, no LibreOffice, no OnlyOffice, no WPS. Windows handed the extension to an unrelated app that loosely claimed it, the Codex desktop app. The workbook was never openable on this machine however correct its XML became, which is the actual reason the owner never saw what the previews showed.
- [x] **"i thought it was the mod spreedsheeet! fix it"** — fixed by building a format the machine *can* open: **`Rimrooms_Async_Industries_294_Mod_Integration_Register.html`**, in the same folder as the workbook. Double-click, opens in the browser, no install, and **no external asset** so it works offline. Same four views as tabs, plus two things a spreadsheet could not give: a **live search across all seventeen columns of every row**, and stance / firmness / family filters with a running match count. The workbook is still built and still verified for anyone who does have a spreadsheet application; the HTML is the primary deliverable.
- [x] **File association and installing software** — **deliberately not done.** Changing associations or installing an application on the owner's machine is the owner's call, not a build step. The HTML removes the need. If the owner ever does want the workbook openable, LibreOffice would do it and the file itself is now verified correct.

- [x] **"there is a mode .xlml like thing that im not sure is fully working"** — the owner was right to doubt it. Four defects found, all real: every one of its 5,009 text cells was typed `t="str"` (the OOXML type for a cached *formula* result) with no formula anywhere in the file and an empty `<sst/>` sharedStrings part still declared as a relationship; all 294 rows were pinned `ht="78" customHeight="1"`, which *forbids* auto-fit, while five columns carry up to 300 characters; the Overview's family tallies were stale, listing 45 families where the rows hold 66, with eleven wrong counts; and it had **no generator anywhere in the repository**, so it could not be rebuilt, updated or verified.
- [x] **"i try to open it but its not human navigatable"** — rebuilt as four sheets to the owner's selection: **Overview** (measures, computed tallies, sources), **Index** (fits one screen wide, one line per mod, links into the card), **Mod Register** (all seventeen columns, autofilter, frozen header and first two columns, row heights computed to fit their own tallest cell and left auto-fittable), and **Mod Cards** (a vertical label/value block per mod where nothing is ever clipped).
- [x] **"but its suppose to spreeadsheet out all the mods and potential uses and issues and theri uses and descriptions and shit if i remember correctly"** — the owner's memory was accurate. It carries all 294 rows across seventeen columns including Planned Use, Integration Approach, Compatibility Watch, Backrooms Dependency, Research Status, FinalDisposition, EvidenceBuild and AcceptanceEvidence.
- [x] **"and you should definatly be using it"** — used immediately: the three hauling rows (164 Pick Up And Haul, 107 Haul to Stack, 288 Prison Labor) were worked out of the register and their reviews, and the register's own `SystemFamily` column drove the tally correction.
- [x] **"and or fixing it up as you go along with build the Mod here"** — six columns of integration analysis existed **only** inside that one binary and nowhere else in the repository. They are now tracked text at `research/mod-register-integration-fields-2026-09-29.csv`, and the overview prose at `research/mod-register-overview-2026-09-29.csv`. The workbook is generated output and holds nothing unique.
- [x] **"and or update it where need of past work already done"** — the stale Overview tallies are gone: family, stance and firmness counts are now **computed from the rows on every build**, so they cannot drift from what they describe again. The three hauling rows carry their connected-work findings.
- [x] **"and continue it forward and making sure it is human havigate able"** — `tools/research/build-mod-register.py` rebuilds it from the CSVs (byte-identical on an unchanged source), `tools/research/check-mod-register.py` round-trips every cell back out and proves nothing is clipped, and `tools/research/audit-gate0.py` independently compares 3,234 workbook cells against the inventory. Rebuilding after any register edit is now a step in the checkpoint ritual.
- [x] **"becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"** — explained: the preview PNGs are 5160-pixel-wide renders of the whole grid, so they show all seventeen columns at once, while the file itself pinned every row shut. Those PNGs now depict a **superseded layout**; see the note in `implementation/MOD_REGISTER_REBUILD.md`.

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
