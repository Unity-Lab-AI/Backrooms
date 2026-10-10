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


**Verbatim owner direction (2026-09-29), resuming after compaction:** *"read now.md to continue the work guided by the prep docs and mod register and worrkflow docs to make an all encompassing mod(You do know how to properly make rimworld mods right for 1.6?) should of asked that before now, get to work!"*

- [~] **"read now.md to continue the work guided by the prep docs and mod register and worrkflow docs"** - `docs/NOW.md` read, `docs/CAMPAIGN_CHART.md` read as the authority, and the register filtered on the Research and staff development family before designing anything (six rows, all Optional or Configuration-only, none conflicting). Item 1 of the NOW.md queue is research tier 2.
- [~] **"to make an all encompassing mod"** - the standing objective. The chart's build order is the sequence; nothing is skipped and nothing is deferred.

**Verbatim owner direction (2026-09-29), a crew left on the far side:** *"and remmebr turning off a company gate with pawns inside doesnt lose control of those pawns they have to survive till a reconnection is made so they can escape"*

- [ ] **"turning off a company gate with pawns inside doesnt lose control of those pawns"** - closing a gate on a crew **does not take them away from the player**. They stay the player's own pawns, under the player's own control, on the coordinate map.
- [ ] **"they have to survive till a reconnection is made"** - and now they are a survival problem. Food, warmth, injury, whatever is down there with them. The player plays them.
- [ ] **"so they can escape"** - reconnection is the way out, and it is the player's to arrange from the near side. **Nothing here is timed** (`docs/CAMPAIGN_CHART.md` §1.1): a stranded crew is not on a countdown, they are simply somewhere hard.
- [ ] **What to verify before writing anything:** `Company/LostPawnRegister.cs` exists and the campaign calls `ExposeLostPawns()`. **The name is the thing to check.** If a closing gate hands its crew to the world-pawn pool, or despawns them, or marks them lost in any way that removes player control, that is a defect against this direction and the most consequential kind - it takes colonists away from somebody.

**Verbatim owner answer (2026-09-29), at the exit-route fork:** *"Two maps at start, coordinate is real (Recommended)"*

- [ ] **"Two maps at start, coordinate is real"** - the solo/group start generates **two** maps. The starting map is an ordinary surface map on the tile the player picked, holding a small concrete shell with one door in it. A **real Backrooms coordinate** is generated alongside, and the starting people and their supplies are put inside it before the player ever sees the surface. The exit is a genuine registered `Emergence` connection from the first tick.
- [ ] **This supersedes the earlier answer** *"Emerges on a fresh tile chosen by the seed"*, and the reason is a hard architectural constraint that was only found by reading `RimroomsPortalNetwork.Register`:
  - `Register` requires **`secondAnchor.Map.Parent as RimroomsDestinationMapParent`** with a matching `CoordinateRecord`. The Backrooms side of any connection must be a real coordinate map.
  - The solo/group start's map **cannot be one**, because `Game.InitNewGame` generates the starting map for a **player `Settlement`** world object and errors without one.
  - So 0.12.0-dev's design - *the starting map IS the coordinate* - is the thing that makes a registered exit impossible. Keeping it would have meant widening the validation that **every existing gate depends on**, which is the riskiest change available.
- [ ] **What this reworks from 0.12.0-dev:** `GenStep_InsideStart` and the `RR_InsideStart` map generator are **retired and archived**; the coordinate is generated by the existing `DestinationService.EnsureSite` through `GenStep_BackroomsDestination`, which is the proven path. `insideStart` stops meaning *"the starting map is a coordinate"* and starts meaning *"the starting people begin in a coordinate alongside the surface map"*.
- [ ] **The cost, stated plainly:** the surface tile is the one the player chose at setup rather than one derived from the seed. The owner took that trade knowingly at the fork.

**Verbatim owner direction (2026-09-29), constraining all of the above:** *"but remmebr this is all open eneded they can play how they choose"*

- [ ] **"this is all open eneded they can play how they choose"** - **the tutorial chain guides, it never rails.** This is the same rule `docs/CAMPAIGN_CHART.md` already holds the Async line to and it now governs the solo/group line too:
  - The exit is **guaranteed to exist**, and **using it is a choice**. A player who wants to live down there, dig, farm and never come out is playing the game correctly.
  - The depth-3 limit is a property of **natural portals**, not a gate on the player. It does not stop anybody doing anything; it only means the free doorways run out and a built gate is how you go further **if you want to go further**.
  - Nothing in the chain expires, nothing is failed by ignoring it, and every step offers more than one way through (chart #1.1 and #1.2, both already enforced by `check-campaign-absolutes.py`).
  - **The chain is a set of offers describing what is possible, not an order of operations.** If a player reaches the surface before anybody suggested it, the chain has to read as already-done rather than skipped.

**Verbatim owner answers (2026-09-29), at the exit fork:** *"Emerges on a fresh tile chosen by the seed"* / *"option 1 and the tutorial like quest chains should lay it all out"*

- [ ] **"option 1"** - natural portals reach **through depth 3**, then stop. Level 1 where they start, plus two more levels found by doorway. Past that, deeper requires a gate they built.

**Sequencing, decided rather than asked:** the bounded natural depth and the guaranteed exit ship together, because the exit is the load-bearing half of the direction and the depth cap is what gives it a point. The tutorial chain follows in its own checkpoint, because it needs a new field on the request shape and a second line of authored content, and rushing it behind the world-tile work is how a request line ends up teaching the wrong order.

### Owner direction — the queue is not an archive (2026-10-02)

**Verbatim owner direction (2026-10-02, three items):** *"we need to move all finished items to finalized.md from the todo, the todods sahll never hold completed items, they are always to be moved to finalized first then deleted from the todods once confirmed virbatium transfer"*

- [~] **"we need to move all finished items to finalized.md from the todo"** — at the time this was given, `docs/TODO.md` held **727 `[x]` rows across 2,709 lines**, including **twenty-seven whole `##` sections** that are closed session records end to end. Every one moves to `docs/FINALIZED.md`.
- [~] **"the todods sahll never hold completed items"** — standing rule from here, over every tier of the ledger: `TODO.md` and `DECOMPOSED.md` carry pending, in-progress and `[T]` rows only. A `[x]` row sitting in a queue file is a defect to be cleared, not a record to be kept there.
- [~] **"they are always to be moved to finalized first then deleted from the todods once confirmed virbatium transfer"** — the order is binding and it is the existing `§FINALIZED BEFORE DELETE` LAW stated again: write to `FINALIZED.md` **first**, confirm the transfer is **verbatim**, and only then remove from the queue. The confirmation is a byte-for-byte reassembly check, not a reading.

---

## Pending

### Major M1 — Connected colony portals (ROADMAP M1; master TODO §Native-provider foundation — 0.4.0-dev)

Binding contract: [`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md). Baseline commit `8ed4e32`, 0.4.1-dev, 75 C# files, 71 package files, zero warnings/errors. Read `implementation/CONNECTED_COLONY_CHECKPOINT.md`, `CONNECTED_COLONY_IMPLEMENTATION_TASK.md`, `CONNECTED_NETWORK_IMPLEMENTATION.md`, `CONNECTED_CROSSING_IMPLEMENTATION.md`, `CONNECTED_WORK_CORE_API.md`, `CONNECTED_PORTAL_STATE_MIGRATION.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md` before editing `src/RimroomsAsyncIndustries/Portals/` or `Gate/`. Source fact: nothing in the repo calls `RimroomsPortalNetwork.Register`, `PortalCrossingService.Cross`/`Recover`, or `CompRimroomsGate.BeginPortalOpening` yet.

**Master TODO items (verbatim):**

- [~] Implement every open item in [connected colony portals](CONNECTED_COLONY_PORTALS.md#required-implementation-backlog): independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants/complexity. This supersedes dispatch-only travel as the target. — **PARTLY BUILT.** The foundation ships: **seven adapters** in `ConnectedWork/Adapters/` — bill, casualty, construction, food, fuel, hauling, medicine — plus the tending provider, two work givers per family, and every scan a bounded rotating window rather than a prefix (invariant 5). Individual open routes are listed below.

**Resume order (verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`; these are the working sequence for the items above):**

- [~] **Resume step 4:** "Implement saved work intents, quantity leases and native destination job revalidation; then physical hauling, construction, bills, research, medical/food/bed and other work/needs families. Preserve priorities, schedules, areas, locks, custody and actual inventory. A generic graph does not implement these adapters."
  - [~] The remaining work/needs families, and every installed work giver in the 294-row profile. **Next (2026-09-29):** cleaning, repair, firefighting, plants/mining/hunting, prisoner and guest care, wardening, childcare, animals and mechs, refuel and rearm, joy, rituals, hauling providers. Expect most to be short: the deployment shape covers anything done at the far site, and the carry shape covers anything delivered. Read the relevant profile rows for each before writing. — **FIRST PASS BUILT 2026-09-29 in 0.6.2-dev:** cleaning, repair, firefighting, mining, hunting, plant cutting, growing-zone work and refuel-with-rearm (eight families, three files, no new record/driver/JobDef). Refuel and rearm turned out to be **one** family, confirmed from Core. **SECOND PASS BUILT 2026-09-29 in 0.6.4-dev:** wardening, childcare and animal handling (three more deployment providers, twenty-two families total). **THIRD PASS 2026-09-29, no new source:** joy and rituals **both decided no**, and the three hauling providers closed as register rows. **Joy has no work type at all** — 23 work types exist across Core and all five DLC and `Joy` is not among them; `JobGiver_GetJoy` is a `ThinkNode_JobGiver` reading `pawn.needs.joy`, so the needs invariant applies exactly as it did to food and rest. **No `WorkGiverDef` anywhere in Core or any DLC is ritual-driven**; a `LordJob_Ritual` owns its participants' duties, so this layer never sees a ritual participant. Hauling rows: Pick Up And Haul (164) has no seam because the connected families run their own job driver rather than `WorkGiver_HaulGeneral`; Haul to Stack (107) is inert alongside 164 by the publisher's own claim, unreproduced; Prison Labor (288) **can never send a prisoner through a gate**, verified from `Pawn.IsColonist` requiring `Faction.IsPlayer`, which a prisoner of the colony never has. Records: `implementation/CONNECTED_WORK_FAMILIES_IMPLEMENTATION.md` and `research/WORK_TYPE_COVERAGE_AUDIT.md`. **FOURTH PASS BUILT 2026-09-29 in 0.6.5-dev:** bill work as **five** families, one per work type — 27 families. Record `implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md`. **FIFTH PASS BUILT 2026-09-29 in 0.6.6-dev:** dark study — 28 families. Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`. **SIXTH PASS BUILT 2026-09-29 in 0.6.7-dev:** hauling upkeep, BasicWorker and Fishing — **31 families, 23 of them deployments**. **Every work type in the game is now either covered or decided against with its reason recorded.** Record `implementation/WORK_TYPE_GAPS_CLOSED_IMPLEMENTATION.md`. **Why this row stays `[~]` and not `[x]`:** the Core half is finished, but the row's own words are *"and every installed work giver in the 294-row profile"*, which is broader. What remains is named rather than vague: the **eleven DLC container hauling givers** (each needs a custody review before a worker crosses for it) — **BUILT 0.12.34-dev**, and the review found that Core forbids all eleven from moving anything between maps — the **four painting givers** in `Art` — **BUILT 0.12.34-dev** as `PaintingProvider`; `Art` already had `bill-work-art` for sculpting, which is why they were nearly lost, but a bill lives on a bench and paint lives on a **designation**, so nobody would ever have crossed for any of it — and any **mod-added work type** with its own givers — the bill family covers modded *benches* inside existing work types automatically, but a wholly new work type gets no provider, because the providers and their giver defs are shipped rather than derived. **This is now the only thing left on this row**, and it cannot be built against an unknown: a wholly new work type from a mod nobody has named has no giver defs to write. `DEFERRED.md` is closed with zero rows and this pointer to it was stale.

**This row does NOT close on completeness.** The remembered list above was checked against the shipped game data and found **incomplete**: it omitted `DarkStudy` and `Fishing` entirely, and both are real work types with no mention anywhere in the mod's source. The enumeration is in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md) — 23 work types, 145 giver defs, coverage read out of the mod's own source. Four genuine gaps remain, recorded below as new rows because this is new information rather than a restatement.

- [~] **Resume step 5:** "Integrate exact optional work/storage providers and scenario openings, then procedural inhabitants, rare monstrosities, saved events and tech-driven complexity. Keep every wider master TODO feature in scope." — **PARTLY BUILT.** Scenario openings: **done**, all three starts. Optional provider adapters remain — see their own row below.
- [~] **Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change." — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`. — **PARTLY BUILT.** Source and build milestones have continued without a break through 0.12.13-dev. **Runtime acceptance is still deferred and structurally must be: only the owner launches.**

**Required implementation backlog (verbatim from `CONNECTED_COLONY_PORTALS.md`; the acceptance list the majors above must satisfy):**

- [~] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions. *(source partially complete in 0.5.0-dev: discovery, destination targets, bounded routing, planning leases and real native destination reservations exist and are proven for the storage-hauling family only; the other families are not implemented and runtime acceptance is open)*
- [ ] Implement connected-site scheduling/streaming and measure performance after an owner-launched build. — **STILL OPEN.** Scheduling and streaming ship. **Measuring performance requires an owner-launched build, which is the one thing this project cannot do for itself.**
- [T] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants. — post-completion test phase (owner RimSort launch).

**Task-record subitems still open (verbatim from `implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md`):**

- [~] Optional profile interfaces and native priority/schedule/restriction coverage. — **PARTLY BUILT.** Native priority, schedule and restriction handling is respected — nothing is ever `playerForced` and no quantity is hardcoded (invariant 9). **Optional provider interfaces remain**, on their own row below.
- [T] Owner-launched acceptance: both directions; chains/loops; closed/blocked endpoints; permanent natural links; save/reload; cargo identity; interrupted jobs; all supported native/provider routes. — post-completion test phase (owner RimSort launch).

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [~] **Adapter families, one at a time with source evidence per route:** ~~storage hauling~~ (BUILT 0.5.0-dev) → ~~casualties and remains~~ (BUILT 0.5.2-dev) → ~~construction supply~~ (BUILT 0.5.3-dev) → ~~construction finishing~~ (BUILT 0.5.5-dev as the first travel-to-work provider, the shape the intent model previously lacked) → ~~bills~~ (BUILT 0.5.7-dev; unfinished things are deliberately out of scope because Core binds a part-made thing to one worker, and medical, autonomous and mech bills each still need their own review) → ~~research~~ (BUILT 0.5.8-dev as the *second* travel-to-work provider — one new file, no new record, driver or JobDef, which is the first real evidence the deployment shape was right) → ~~tend/rescue~~ (BUILT 0.5.9-dev as both halves in one item: the doctor travels as the third deployment provider, and medicine travels as the seventh adapter; surgery and prisoner/guest care remain as separately reviewed routes) → ~~food~~ (BUILT 0.6.0-dev as three parts, one of which was *decided against* rather than deferred: a hungry pawn does not walk through a gate to eat, because eating is a think-tree need and a closing gate would strand a starving pawn) → ~~remaining families, first pass~~ (BUILT 0.6.2-dev: cleaning, repair, firefighting, mining, hunting, plant cutting, growing-zone work and refuel-with-rearm, eight families in one pass; prisoner/guest care, wardening, childcare, animals/mechs, joy, rituals and the three hauling providers remain) → ~~rest~~ (BUILT 0.6.1-dev; a tired pawn crossing to sleep is closed by **Core's own rule** rather than our caution, because `RestUtility.CanUseBedNow` rejects any bed whose map differs from the sleeper's, so the one real gap was bedding a casualty where they lie) → ~~remaining families, second pass~~ (BUILT 0.6.4-dev: wardening, childcare and animal handling — 22 families) → ~~joy, rituals, `Patient`, `PatientBedRest`~~ (**DECIDED AGAINST 2026-09-29**, each with its Core reason; joy has no work type at all and no `WorkGiverDef` anywhere is ritual-driven) → ~~the three hauling providers~~ (closed as register rows 2026-09-29) → ~~bill work~~ (BUILT 0.6.5-dev as **five** families, one per work type; **27 families, 19 of them deployments**) → ~~DarkStudy~~ (BUILT 0.6.6-dev; **28 families, 20 of them deployments**) → ~~hauling upkeep, BasicWorker and Fishing~~ (ALL BUILT 0.6.7-dev; **31 families, 23 of them deployments**). **Every work type in the game is now either covered or decided against with its reason recorded.** The remembered families list was **incomplete** — it omitted `DarkStudy` and `Fishing` entirely. Source: `research/WORK_TYPE_COVERAGE_AUDIT.md` (23 work types, 145 giver defs), `CONNECTED_WORK_CORE_API.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md`. — **PARTLY BUILT.** Seven families built with source evidence each. **Surgery across a gate is the named remainder** and has its own row.
- [ ] **Optional work/storage provider adapters** (Pick Up And Haul 164, Haul To Stack 107, Adaptive Storage 10/24/25/26, LWM Deep Storage 122, Warehouse 259, RimFridge 195, Prison Labor 288, Research Whatever 279, Meals On Wheels 125, Gastronomy 269). Core-only path must work with every one absent. **Narrowed 2026-09-28:** the generic storage half is closed — the four storage providers reach cross-gate hauling through `IHaulDestination` now that the container route exists, with no bespoke adapter each. What remains is behaviour those mods add *beyond* the interface, plus the work-behaviour providers (Pick Up And Haul, Haul To Stack, Prison Labor), each still needing its own review. **Narrowed further 2026-09-29:** Research Whatever (279) was reviewed with the research family in 0.5.8-dev, and Meals On Wheels (125) and Gastronomy (269) were reviewed with the food family in 0.6.0-dev — all three are optional with no adapter, and Gastronomy additionally has unresolved rights so its code and art must not be adapted. Source: `CONNECTED_WORK_PROFILE_BOUNDARIES.md`, `implementation/DEFERMENT_AUDIT_AND_CLOSURES.md`. — **STILL OPEN.** Each needs its own source review and a `PatchOperationFindMod` so it applies nothing when the mod is absent (invariant 42). **None is a requirement** — the package must load and run against Core alone.
- [T] **Connected-site scheduling and streaming, then measurement.** Active connected job destinations must not be silently unloaded to meet a budget. Measurement itself belongs to the post-completion test phase and gates nothing. Source: `CONNECTED_COLONY_PORTALS.md`, `research/PERFORMANCE_BENCHMARK_PLAN.md`.

### Major M2 — Existing-content replacement (ROADMAP M2; master TODO §Existing-content replacement work + Phase 5 replacement item)

Policy: [`CONTENT_REUSE_POLICY.md`](CONTENT_REUSE_POLICY.md); map: [`implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md`](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md). Already replaced in source: evidence book (Core `TextBook`), laboratory (designated Core research bench), four audio cues (Core sounds), gate/console/battery/bench designation on Core `Door`/`Autodoor`/`CommsConsole`/`Battery`/`TableMachining`, native room lighting/heater/generator/floors. Still custom and still in the 71-file allowlist: `RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator`, `RR_FieldAnalysisBench`, `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon`, `RR_SealedEvidenceCase`, `RR_RouteRecording`, `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, `RR_ReturnAnchor`, `RR_QuietPursuer` presentation, five `RR_*Staff` PawnKinds, 14 gameplay PNGs. **Retired outright since: the four legacy gate objects, the field analysis bench, the site lamp and climate unit, and the institutional carpet (0.9.0-dev); the return beacon and its recipe (0.9.9-dev).** All are archived under `implementation/historical-content/0.2.0/` rather than deleted.

- [~] Replace custom creature presentation, room fixtures and terrain with existing native/provider content, retaining learned rules, encounters, procedural variation and saved routes. — **PARTLY BUILT.** Room fixtures and terrain use existing content throughout (`BackroomsPalette` names Core `TerrainDef`s). **`RR_QuietPursuer` presentation is the last one open** and is queue item 6.
- [~] Replace the historical custom gameplay items, benches, terrain, sprites and audio with source-verified existing Core/profile content and saved role bindings; preserve the gate, field gear, evidence, threat and discovery functions. Follow `CONTENT_REUSE_POLICY.md` and the existing-content replacement map. *(master TODO Phase 5)* — **PARTLY BUILT.** Items, benches and terrain: **done**. **Fourteen historical gameplay PNGs remain in the package allowlist** and come out once the last references go, which is gated on the `RR_QuietPursuer` decision.

## Public face: the site, the Workshop page and the collection

**Verbatim owner direction (2026-09-29):** *"fyi when we get to it we will build a github deployable html build that catologs the whole mod and is the main mod site wiki and documentation dump in a beauty of a deployable github page with what ever you can do so the deploy address is not some random git hub address but is a nice backrooms url for github deployed page where we document all the mods capabilities and howto and related public facing docs and information into a website that lays everything out top to bottom beautiffully just like other rimworld mods make theri third party sites, not to metione the building of the steam workkshop mod collection and workshop mod deploy for our mode with write ups for  both with links in them to each other and the deployed site so things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop, idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"*

**Full plan: [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md)** - structure, the ordering chain, the domain question, and the three decisions that are the owner's to make.

**Not started. Owner said *"when we get to it"*, and it is correctly last:** every one of these artefacts describes the mod, so each is written twice if the mod is still changing underneath it. The same reason the player-facing how-to sits at the end of the build order.

### The ordering the owner named, which is a real dependency chain

1. **The mod is settled** - content set final, scenarios in, nothing still being retired.
2. **The site is deployed and working**, at its proper address.
3. **Then** the Workshop mod page, whose write-up links to the site.
4. **Then** the Workshop collection, whose write-up links to both.

Owner's words: *"things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop"*. Doing any of it earlier means publishing links that point at nothing.

### The site

- [ ] **A GitHub Pages build that catalogues the whole mod** - capabilities, how-to, and the public-facing documentation, *"top to bottom"*, in the shape other RimWorld mods use for their third-party sites.
- [ ] **A real domain, not a `github.io` path.** *"a nice backrooms url"*. This needs a domain the owner controls plus a `CNAME` file in the Pages branch and DNS records pointing at GitHub. **The domain is the owner's to choose and register** - ask before building the Pages config, because a custom domain and a project-path deploy are configured differently and the wrong one means rebuilding.
- [ ] **Generated, never hand-maintained.** `tools/make-readable-html.py` is already the seed of this: it renders documents to standalone styled HTML with no external dependencies. The site is that tool grown up - more pages, navigation, a real front page - so the site cannot drift from the documentation the way a hand-written site would.
- [ ] **`check-doc-conformance.py` should cover the generated site**, so a published page cannot claim a version or a branch the build does not have.

### The Steam Workshop

- [ ] **The mod page write-up**, linking to the site.
- [ ] **The collection**, with its own write-up, linking to the mod page and the site.
- [ ] **Both written from the same source as the site**, so three descriptions of one mod cannot disagree.
- [ ] **Owner idea, verbatim:** *"idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"* - Playwright driving the Steam Workshop UI. **Ask before doing this**: it means automating an authenticated session on the owner's Steam account, which is a different kind of action from anything done so far and needs explicit permission, not an assumption. The alternative is a prepared write-up the owner pastes, which is far less work for whoever is not doing the clicking.

### Standing constraints that still apply

- **No Claude attribution** in any of it - site, Workshop page, collection write-up.
- **The owner alone launches, sorts and publishes.** Deployment of a site is not the same act as launching the game, but the Workshop is the owner's account and the owner's decision.


**Verbatim owner direction (2026-09-29):** *"and remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"*

- [ ] **Still unbuilt from the same prep document:** *"contradictory accounts"* from a returning crew - a report that does not match what another crew saw - and staff **prior exposure** affecting how an expedition goes. — **CONTRADICTORY ACCOUNTS BUILT, 0.12.25-dev.** And the *"short step"* reading was wrong in an important way: two crew who disagree was not a step from a mechanism that exists, it was **a mechanism that existed and threw the disagreement away.** `StableId` is per-room only for a room survey, so one evidence record carried one witness per fact, and the second crew member was either merged in or refused as `RR_Company_ReceiptMismatch` — with the site tick ignoring the result. **Chart line 226 asks request 5 for "two crew accounts of the same room" and that was unreachable.** Accounts are now saved, corroborating or disputing, a dispute counts as testimony, and the readout names them. **Still open in this row: staff prior exposure**, and resolving a dispute (the interview). Record: [two crew who disagree](implementation/CONTRADICTORY_ACCOUNTS_IMPLEMENTATION.md).


**Verbatim owner directions:** *"go ahead with now.md protocol and get ready form compact with creating the handoff before i compact"*, *"ask me the question remebr i said sooner than later with those"*, *"that means asap"*.

- [ ] **NEXT: build the recorder fold.** Four live read sites move onto the book.

**Built 2026-09-29, 0.12.14-dev: the queue could not answer the question.**

## Owner decisions, 2026-09-29 — the three reserved questions answered, and one I should never have asked

**Verbatim owner request:** *"read Now.md to resume the work and okay shoot ask me all you want on those question u had that were blocking and lets get to finishing all this work so we have a finished mod with nothing to do but test and bug hunt"*

**Q1 — how a generated request picks its routes. THIS WAS ALREADY ANSWERED AND I RE-ASKED IT. Then the new answer contradicted the shipped one, and the owner resolved the conflict.**


**Q2 — whether the eight branches unlock in any order after the hinge. ANSWERED: all eight open, any order.**

- [ ] The hinge opens **everything**. Each branch keeps its own internal tier ladder - tier 2 in a branch still needs tier 1 in that branch - but no branch gates another. Consistent with the standing direction *"but remmebr this is all open eneded they can play how they choose"*. **Closes chart §6 item 2.**

**Q3 — the adjacent-door-run fallback. I ASKED A QUESTION THE OWNER HAD ALREADY ANSWERED.**

**Verbatim owner correction:** *"wtf are you talking about core only we have 294 recommend mods you fuck!!!!"*


**Q4 — how far the public release goes. ANSWERED: everything, including Playwright driving Steam.**

- [ ] Repo, site and the Steam Workshop page driven through Playwright. **The concern was stated plainly before the choice was made and the owner chose this option anyway**, which makes it an informed decision and it stands. Recorded here so the decision is not re-litigated at the release checkpoint. Still correctly **last** in the queue, and it needs the owner present for the Steam session.

---

## Owner directions recorded late

These three were **acted on correctly and recorded in `NOW.md` or `FINALIZED.md`, but never
written into this queue as tasks**. The owner noticed the gap on 2026-09-29 and was right.
They are recorded here verbatim now, and `check-doc-conformance.py` refuses from this point
on to let a direction reach `FINALIZED.md` without appearing here first.

**Verbatim owner direction (2026-09-29), on the glow pods:** *"tyhe glow pods can be used and lets not limit the amount as a backrooms instance can have 100s of rooms if the player is using 300x300 maps for instance and maybe lets have the glow pods color setable"* and *"color means differnt types of the needs markers"*

**Owner answers on the field kit, asked at the fork:**

- **Survey tag → Core `GlowPod`.** Minifiable, carried, deployed, and it lights the room it marks. *"place one per room you clear, room is lit AND numbered."* **BUILT 0.10.7-dev.**
- **Return beacon → dropped.** *"the gate IS the beacon"* — the address book and the saved return threshold already do its job. **DONE 0.9.9-dev.**
- **Sealed evidence case → a designated headquarters shelf is the archive.** The book is carried and custody completes when it reaches a Core `Shelf` designated as the evidence archive, the same designation pattern as the gate console and the laboratory bench.
- **Field recorder → the book is the recorder.** One Core `TextBook`: carried in blank, written in the field, carried home as the evidence. *"lose the book, lose the run."*


- [ ] **Five `RR_*Staff` PawnKinds** → native `Colonist` (new starts already use it; old kinds are readable-only).
- [ ] **Migration decision or declared development-save break** before removing any Def a saved `Thing` references, with the old build preserved. Shares saved keys with the portal legacy-threshold repair built in step 2 — decide them together.

### Phase 1 leftovers (master TODO §Phase 1 — repository, build, and content foundations)

- [T] Define RimSort-managed test profiles: preserve the 295-entry product target (the existing 294 plus Rimrooms), then record RimBridgeServer as a separate QA overlay (normally 296 loaded entries). RimSort owns sorting, saving mod lists, and every launch; the owner starts sessions through RimSort. Do not add direct RimWorld or GABS launch profiles or remove target mods to offset the bridge. — post-completion test phase (owner-operated RimSort action).
- [T] After the first owner-launched full-target startup, collect matched Core/profile performance baselines on RR-DEV-01 and implement any missing counters per the [benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Enforce the recorded budgets before promoting features or larger room/map bands. — post-completion test phase (owner RimSort launch).

### Phase 2 — code architecture and safe vertical slice (master TODO; source largely present per `implementation/PHASE_2_BUILD_RECORD.md`, full stated scope + Gate 2 acceptance still open)

**Vertical slice implementation:**

- [~] Add staff role recommendations, field kit assignment, readiness checks, and basic company tasks while retaining vanilla pawn/work controls. — **PARTLY BUILT.** Configurable roles, operator assignment and readiness refusals ship. **Field kit assignment is superseded** with the rest of the custom field gear, and native pawn and work controls are untouched throughout.
- [T] Save, reload, revisit the same coordinate, and confirm map state and unique rewards persist without duplication. — post-completion test phase (owner RimSort launch).

**Gate 2 passes when** (master TODO): "the first complete loop plays from a fresh save through build, staff, expedition, extraction, analysis, reward, save/reload, and a second visit without a softlock or lost state." — owner-launched only.

### Major M3 — Phase 3 interconnected company simulation (ROADMAP M3; master TODO §Phase 3)

**Scenario framework and alternate starts** (contract: [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md); owner questions still open: inside-start party size; first-exit fixed vs chosen):

- [ ] Add outpost, town-distortion, or company-in-crisis starts only after a design brief defines their starting state, pressure, failure/recovery, and acceptance evidence. — **Still open, and correctly gated on its own condition:** no design brief exists. Three starts ship. **This needs an owner decision before it is work at all.**
- [T] Verify every start's reload behavior, deterministic coordinate, objective idempotency, optional-DLC fallback, solo behavior, and RWT eligibility against `SCENARIOS.md`. — post-completion test phase (owner RimSort launch).

**Facility and personnel** (source checkpoint: native applicants/hiring + HQ facility observations implemented):

- [~] Implement physical room functions: gate, control, labs, evidence archive, quarantine/decontamination, medical, armory, workshop, power, radio, receiving, storage, cafeteria, recreation, quarters, and outpost. — **Partly built.** The gate, control, analysis and archive functions exist as gate equipment link roles (`RR_Link_Archive`, `RR_Link_Analysis`, `RR_Link_Tooling`, 0.10.8-dev). **Not built as room functions:** quarantine/decontamination, armory, radio, receiving, cafeteria. RimWorld already builds rooms; what this mod adds is what a gate is *linked to*.
- [~] Connect each room to concrete capabilities, stock needs, staff jobs, risks, and UI alerts; expose why a room is not functional. — **Partly built.** A gate reports why it is not functional in its inspect string and through the alerts readout (0.10.5-dev). **Not built:** per-room stock needs and risk surfacing.
- [~] Add configurable company roles, staff schedules, certifications, training jobs, field history, trust/stress/exposure and equipment familiarity; preserve pawn autonomy and vanilla skill/trait systems. — **Partly built.** Configurable roles ship (`AssignCompanyRole`) and equipment familiarity drives gate spin-up (0.8.9-dev). **Not built:** certifications, training jobs, and **staff prior exposure**, which is still a named open prep item.

**Gate, equipment, and expedition operations:**

- [~] Add schedule, warning, recall, evacuation, emergency close, lost-connection, failed return, and rescue workflows. — **Mostly built.** Recall, emergency close, the kill switch, lost-connection and the stranded-crew guarantee all ship, and 0.12.13-dev added the evacuation request family. **Not built:** a scheduling surface.

**Procedural sites and propagation** (contract: [`PROCEDURAL_SPACE_CONTRACT.md`](PROCEDURAL_SPACE_CONTRACT.md)):

- [~] Make equipment meaningfully change what is detected or generated without breaking seed reproducibility or invalidating an already saved coordinate. — **Half superseded, half held.** Seed reproducibility is held absolutely and anything feeding the layout fingerprint is snapshotted rather than read live (invariant 27). The **equipment** half died with the field gear — see the field-equipment row above.
- [~] Bound active map count, pawn/thing count, graph search, event evaluation, and background tick cost; profile large, long-running saves. — **Bounding is done; profiling is not and cannot be.** Every scan in `ConnectedWork/` is a bounded rotating window, never a prefix (invariant 5), with roughly thirty `Maximum*` scan budgets. **Profiling a long-running save requires launching the game, which only the owner does.**

**Economy, contracts, and evidence** (contracts: [`CAMPAIGN_ECONOMY_MODEL.md`](CAMPAIGN_ECONOMY_MODEL.md), [`CAMPAIGN_ECONOMY_PROGRESSION.md`](CAMPAIGN_ECONOMY_PROGRESSION.md); source checkpoint: quotes, supplier custody, payment/refund, partial delivery, rerouting, native-book evidence implemented):

- [~] Generate bounded story variations from client/faction, coordinate, staffing, discovered rules, company tier, previous outcomes, opening duration, and available equipment. — **Partly built, 0.12.12-dev.** Generation reads branch capability, coordinates visited, living witnesses, project qualification and how often a family has been asked. **Not read yet:** client/faction identity, company tier, previous outcome, opening duration.
- [~] Add space leasing/claiming with cost, boundaries, term, access/security requirements, maintenance, renewal, eviction, and exit/abandonment consequences. — **Partly built.** A registered remote site costs a share of base overhead every day and can be released with no penalty (0.12.6-dev), and 0.12.13-dev added the guarded-lease request family against `RR_Commerce_Leases`. **Not built:** term, renewal, eviction. **A release fee must never be added** — a cost for changing your mind is the same trap in a different coat.
- [~] Implement evidence provenance/custody/type/value/risk/confidence, sample storage, research value, sale value, client deliverable, archive, chain of custody, and destruction choice. — **Mostly built.** Provenance by source expedition, custody as *a place the book is* (a shelf linked as a records archive, 0.10.8-dev), observations, analysis, research value as insight, and a chain of custody. **Not built:** confidence scoring and a destruction workflow.
- [ ] Add analyze/interview/compare/review workflows for equipment, furniture, people, entity remains, recordings, transcripts, route notes, and recovered documents. — **Analysis ships; interview does not, confirmed by grep.** This is the same gap as the *"contradictory accounts"* prep item, and the two should be built together. — **HALF BUILT, 0.12.25-dev: compare ships.** Two accounts of one fact are now recorded and compared, and the readout shows the comparison. **Interview remains**, and it is now the thing that resolves what the comparison found rather than a workflow with nothing to work on. — **INTERVIEW BUILT, 0.12.28-dev. Analyse, interview and compare all ship now.** A staff member with Social 4 takes both statements and the company files one; **the other account stays on the record**. And the design changed on a reading of the code: `RecordFieldObservation` validates a fact against the real map **before** it looks for a prior observation, so **a disputing account was already checked and found true**. Nobody is lying — the marker moved between the two visits, which is 0.10.3-dev’s displacement seen from inside an evidence file. So no reliability statistic was invented, per the register. **Review remains** of the four. Record: [nobody is lying](implementation/INTERVIEW_IMPLEMENTATION.md). — **AND THE TEXT DESCRIBING THEM WAS STALE, fixed 0.12.26-dev:** fourteen player-facing strings instructed the player to use a return beacon, a survey tag, an evidence case, a field recorder or a route recording — gear retired between four and fifteen checkpoints ago. `check-retired-content.py` is the **tenth checker** and refuses it now. Record: [the in-game text stops naming things that do not exist](implementation/RETIRED_VOCABULARY_IMPLEMENTATION.md).
- [~] Add repeated missing-person mysteries with radio fragments, missing crews, delayed return, witness conflict, reappearance/death, rescue, and case closure. — **Partly built.** Case records, missing status, the lost-pawn register, and the missing-residents request family (0.12.13-dev). **Not built:** radio fragments and **witness conflict**, which is the *"contradictory accounts"* prep item. — **WITNESS CONFLICT BUILT, 0.12.25-dev.** Two crew who disagree about one room now produce a saved dispute the player is told about and the readout names. **Radio fragments remain.**
- [~] Make sale/study/use/contain/release/recruit/detain/transfer choices visible with financial, staff, faction, legal-in-world, trust, and security consequences. — **Partly built.** Sale through the valuables exchange, study through analysis, recruit through hiring, and faction standing exists. **Not built:** contain, release, detain and transfer as distinct choices with their own consequences.

**Research, entity, and expansion progression** (owner S1/B: broad threat families only; the five named sketches in `CAMPAIGN_ROSTER_FREEZE.md` stay deferred until approved):

- [~] Complete research branches for facility/power, engineering, field safety, equipment, mapping, communication, stability, containment, medicine, logistics, commerce, orbital operations, and deep topology. — **TIERS 0–3 COMPLETE across seven branches, 0.12.18-dev.** Tier 3 was deleted rather than written at 0.12.5-dev because four of seven branches had nothing observable to move; arc 5 wrote those systems and the re-run sweep found a real read site for **all seven**. Two restraints kept and asserted: the per-coordinate frontier cap is **not** a research knob, and shelter never reaches zero. **Tier 4 remains**, and should be surveyed the same way rather than assumed to have knobs. — **TIER 4 BUILT, 0.12.29-dev, AND THE LADDER IS COMPLETE.** Surveyed rather than assumed, and the survey said **six, not eight**: Facilities (spin-up work), Fieldcraft (recovery rate), Commerce (ordinary exchange rate), Measurement (the interview Social floor, which only existed because 0.12.28-dev built the interview), Spatial (ordinary-map frontier rarity) and Entities (the pressure penalty ceiling). **Logistics gets none** — all four of its knobs are claimed by tiers 0–3 and what remains are safety bounds no player reaches. **The gate line CANNOT have a fifth rung** — its fourth already stops the countdown and `portalIndefiniteTier` is 4. Both absences are proof claims, because an absence cannot be seen by reading. Record: [six rungs, and two that could not exist](implementation/RESEARCH_TIER_4_IMPLEMENTATION.md).
- [~] Author entity/anomaly design sheets first: appearance/readability, AI rules, triggers, limits, interaction, tells, counters, evidence, study risk, capture/storage, sale value, and fail states. — **Partly built.** Inhabitant defs carry AI rules, bands, tells and counters, and the escalation ladder is bounded. **Not built as authored design documents**, and the `RR_QuietPursuer` presentation is still the last open existing-content replacement.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [~] Room functions, applicant pools, training/certification, wellbeing (needs the cross-map adapters to be meaningful across maps). — **Split verdict, see the individual rows above.** Applicant pools **done**; room functions and roles **partly**; wellbeing **superseded** because RimWorld ships it.
- [~] Research IDs across tiers T0–T6 and the nine branches; entity family sheets (broad families only per S1/B). — **Tiers 0–2 complete across seven branches; T3 is the next checkpoint.** The eighth branch (transport and orbital) has **no tier 0 at all, deliberately**, and the tree is derived rather than declared, so a tier number is not a promise of a linear chain.
- [~] Containment, interviews, settlement openings, outposts, vehicles, VGE hooks. — **Settlement openings and outposts are DONE (0.12.13-dev).** Containment, interviews, vehicles and the VGE hooks remain open and are listed individually above.

### Major M4 — Phase 4 multiplayer, DLC, and the full profile (ROADMAP M4; master TODO §Phase 4)

Every item in this major needs a Rimrooms build the owner has launched; source-side preparation (feature detection, guards, adapters) can proceed, verification cannot.

**RimWorld Together adapter** (pinned release 26.8.31.1; no supported client extension API identified 2026-09-27):

- [T] Verify guild identity, facility mapping, configured visits/snapshot behavior, visits when online/offline, transfer spot, chill/defense spots, caravan interactions, events, sites, roads, aid, gifts, and trading. — post-completion test phase (owner-launched two-client run).
- [T] Verify transfer receipt IDs and item/pawn state prevent duplicates, loss, stale ownership, and broken stacks on disconnect/reconnect. — post-completion test phase (owner-launched two-client run).
- [T] Verify Backrooms Research Dossier item transfer; receiving branch must explicitly study it locally and be unable to claim it twice in one save. — post-completion test phase (owner-launched two-client run); dossier binds to an existing physical document object per the content-reuse rule.
- [T] Test unsupported/complex modded items and define an honest fallback message rather than promising an unverified transfer. — post-completion test phase (owner-launched two-client run).
- [T] Test separate colony saves, shared world actions, mod order/config enforcement, RWT server restart/backups, and an admin changing settings during play. — post-completion test phase (owner-launched two-client run).

**Five DLC layers:**

- [~] Royalty conditional content: titles/quests/faction/psycasts only as optional company routes. — **PARTLY BUILT.** The **gating mechanism** ships and is enforced. **No Royalty-specific content is authored**, which is honest rather than a gap: it must be an optional route or nothing.
- [~] Ideology conditional content: beliefs, meditation, rituals, staff policies, and recreation only when available. — **PARTLY BUILT.** Gating ships; no Ideology-specific content authored.
- [~] Biotech conditional content: genes, mechanitors, children, medicine, pollution, and mechanoid options; no mandatory gene/resource dependency. — **PARTLY BUILT.** Gating ships; no Biotech-specific content authored. Nothing is mandatory.
- [~] Anomaly conditional content: containment/research links; Backrooms entities retain a base-game implementation. — **PARTLY BUILT.** Gating ships, and the Backrooms entities **do** retain a base-game implementation, which is the load-bearing half of this row. Anomaly’s `SecurityDoor` is already recognised as a 2×1 gate when present.
- [~] Odyssey conditional content: gravship/off-world logistics and any compatible space travel. — **PARTLY BUILT.** Gating ships. Arc 7’s request families exist; no gravship integration is written, and it stays DLC-optional throughout.
- [T] Before implementing or advertising optional VGE support, verify the clean Core + Harmony + Odyssey + VEF + both VGE chapters stack, Chapter 1 operations, Chapter 2 threat/defense/salvage, optional Insectoids 2, save/reload, and the gravship-touch profile graph. Keep this in the per-integration acceptance gate; it is not a Gate 0 requirement. See the [gravship profile review](research/GRAVSHIP_PROFILE_INTERACTIONS.md). — post-completion test phase (owner RimSort launch).
- [T] Verify all five individually enabled/disabled, then all combined. Maintain a 32-row DLC bitmask matrix (all combinations of five DLCs) if claiming full combinatorial support; at minimum, explicitly publish exactly which combinations were run. — post-completion test phase (owner RimSort launch).

**All 294 profile entries** (all rows source-reviewed; zero rows runtime-cleared):

- [T] Pin the exact profile and test clean Core, Core+RWT/Harmony, selected VGE stack, each high-risk family, and the full ordered profile. — post-completion test phase (owner RimSort launch).
- [~] For each workbook row, close its status with evidence: reviewed version, load-order placement, applicable DLC, behavior used/preserved, patch/adaptor/no-code reason, and result. — **PARTLY BUILT.** The register retro sweep is genuinely in progress: 14 families swept, 7 not yet (medical, world operations, cargo, hospitality, materials, visitor economy, staff psychology).
- [T] Verify all QoL features remain available, including work-priority, UI, scheduling, storage, movement, hauling, selection, visitors, prisoners, health, combat, map, and scenario helpers represented in the list. — post-completion test phase (owner RimSort launch).
- [ ] Resolve duplicate Defs/patch collisions in the exact 294 profile; use load-after patches only where a reproducible conflict requires one. — **STILL OPEN.** **Structurally requires a launch with the 294 profile loaded**, which only the owner does, through RimSort.
- [T] Test gravship-changing profile mods against both VGE chapters; publish incompatible combinations rather than hiding known conflicts. — post-completion test phase (owner RimSort launch).
- [ ] Add a user-facing compatibility report with tested order, versions, DLC, known issues, unsupported features, and save caveats. — **STILL OPEN.** Cannot honestly state a tested order before anything has been tested.

### Major M5 — Phase 5 complete Company Command interface and polish (ROADMAP M5; master TODO §Phase 5)

Contracts: [`OPERATIONS_ACTION_CONTRACTS.md`](OPERATIONS_ACTION_CONTRACTS.md), [`research/VISUAL_AUDIO_STYLE_BRIEF.md`](research/VISUAL_AUDIO_STYLE_BRIEF.md), [`research/CONTENT_ACCESSIBILITY_BRIEF.md`](research/CONTENT_ACCESSIBILITY_BRIEF.md), [`TUTORIAL_SCRIPT.md`](TUTORIAL_SCRIPT.md). Source checkpoint: ten Operations panes, two original menu images, slideshow controller, settings, dynamic title/version exist.

- [~] Make each screen deep-link to the relevant pawn, building, map, quest, item, research project, evidence record, contract, or RWT site. — **PARTLY BUILT.** Pane-to-pane deep links exist (a failed coordinate jumps to the Expedition pane, a facility jumps to the Machine pane). **Deep links out to a pawn, building or research project do not.**
- [T] Review every slideshow image with the actual menu overlay across supported aspect ratios, resolutions, and UI scales; check text contrast, crop safety, quiet transitions, reduced-motion behavior, and no-audio use. — post-completion test phase (owner RimSort launch).
- [T] Review text length, font scale, combat readability, motion sensitivity, audio levels, UI overlap at supported screen sizes, and translations. — post-completion test phase (owner RimSort launch).
- [T] Verify no UI panel conceals urgent health, fire, power, missing crew, gate recall, containment, or contract priorities. — post-completion test phase (owner RimSort launch).

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [~] Eleven-pane Company Command, deep links, reason codes, native menu remap. — **PARTLY BUILT.** **Twelve panes and reason codes: done.** Deep links partial; the native menu remap is open and questioned on its own row above.
- [~] Slideshow integration review, additional menu images per shipped scenario. — **MOSTLY BUILT.** **Six slides ship as of 0.12.17-dev** — the four new ones landed on the owner’s parallel art track and the folder scan picked them up with no code change. `proof-menu-slides.py` now guards the naming contract, structural PNG validity, a shared aspect and the provenance record. **Still open: the integration REVIEW itself, which needs a launch** — how they read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right, cannot be judged from here.
- [ ] Validation sweep, invalid-state matrix, balance, release report, packaging. — **split 2026-09-29 by owner decision 19.** The validation sweep and packaging halves are M6a and close without a launch; the invalid-state matrix, balance and release report are M6b and cannot. Tracked as separate rows in `TODO.md`. — **STILL OPEN.** **Structurally requires a launch.** Balance in particular cannot be claimed: nothing in this mod has ever been played.
- [T] **Automated fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration.** Deferred **by explicit owner instruction**, 2026-09-29 (decision 20, verbatim *"option 2 and option 3"*), not by dependency: the owner authorised automated fixtures **and** chose to hold them until after the first launch so their content follows observed failures rather than guessed ones. This is the **only** exception to the `CONTRIBUTING.md` no-tests rule anywhere in the repo, it covers this row alone, and **nothing for it may be written before the owner has launched the game once**. Owned by M6b.
- [T] **Screenshots, trailer and preview art for the mod page.** Need a running game, so they split from the M6a mod-page row into M6b. Everything else on that row — description, feature list, installation guide, dependencies, DLC matrix, RWT setup, credits, provenance, license, FAQ, update plan — closes without a launch and is M6a.

### Major M6a — Phase 6 work that closes without a launch (ROADMAP M6a; master TODO §Phase 6)

**Split from M6 by owner decision 19, 2026-09-29.** Bookkeeping only — no row is dropped, reworded or moved out of Phase 6, and every row below is still quoted verbatim from the master TODO.

**Owner decision D1, changed 2026-09-29:** ~~private RimWorld Together test build first; public Workshop only after named-profile and multiplayer validation~~ → **public Steam Workshop is the first distribution target; do not announce compatibility until validation is complete.** Verbatim: *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*. The mod-page and provenance row therefore moves forward rather than waiting on M4 verification.

**The `CONTRIBUTING.md` no-tests rule now has exactly one scoped exception**, recorded as owner decision 20 — see the fixtures row in M6b. It covers that row alone and nothing may be written for it before the owner's first launch. The rule is otherwise unchanged everywhere in this repo.

- [ ] Validate Def references, language keys, patch targets, load folders, package metadata, missing textures/audio, logs, build output, and clean-install folder structure.
- [ ] Prepare final mod page, description, feature list, screenshots, trailer/preview art, installation guide, dependencies, DLC matrix, RWT setup, credits, source provenance, license, FAQ, known issues, and update/support plan. — **the screenshots, trailer and preview art half needs a running game and belongs to M6b; everything else closes here.**
- [ ] Tag release, archive exact source and build artifacts, preserve a known-good server profile, and publish only features that passed their listed acceptance criteria. — **the ritual and the archive close here; the actual tag cannot be cut until M6b supplies the acceptance results this row requires.**

### Major M6b — Phase 6 work that structurally requires the owner's launch (ROADMAP M6b; master TODO §Phase 6)

**Exit condition (D1, changed 2026-09-29):** the Core-only solo path passes. The private RWT prototype is no longer a release prerequisite and co-op validation no longer gates the first publication. The no-compatibility-claim rule stays binding and is now the main protection.

- [T] Create a reproducible fresh-start/save/reload/revisit checklist and automated or manual fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs, and schema migration. — **owner decision 20, 2026-09-29, verbatim: *"option 2 and option 3"***, being *automated fixtures in code* **and** *defer until after the first launch*, taken together. So: **automated fixtures are authorised** for this row, replacing the manual-checklist-only reading, **and none of it is written until the owner has launched the game once**, so its content is shaped by observed failures rather than guessed ones. The exception is narrow — the five subjects named in this row and nothing else — and is not permission for a general test suite.
- [T] Run the scenario acceptance checklist for every shipped opening: fresh start, reload, failure/recovery, route back to the shared campaign, and optional-mod/DLC absence. — post-completion test phase (owner RimSort launch).
- [T] Exercise invalid states: insufficient power, no operator, blocked route, missing exit, destroyed gate, overloaded expedition cargo, receiving bay full, split/delayed bulk shipment, missing/changed OgreStack setting, dead/missing crew, unsafe return, destroyed relay, unavailable RWT feature, failed item transfer, missing DLC, bad mod order, and old save migration. Include a one-million-silver case: 67 stacks under the active OgreStack default assumption, 2,000 under Core limits; verify actual in-save settings and record hauling/storage/transfer results. — post-completion test phase (owner RimSort launch).
- [T] Check performance on worst-case room graphs, multi-outpost company, long play time, many evidence/case records, visitors/prisoners, active threats, and gravship combat. — post-completion test phase (owner RimSort launch).
- [T] Balance economy and progression from fresh-start play through late game; check grind, runaway money, research skip routes, dead-end tech, exploitative optimal choices, and difficulty scaling. — post-completion test phase (owner-launched play).
- [T] Verify the full mod list one final time and capture game/RWT/DLC/profile versions, settings, logs, save, known compatibility issues, and results in a release report. — post-completion test phase (owner RimSort launch).
- [T] Test clean install/uninstall, load order, Workshop update, dedicated RWT server setup, player join, server backup/restore, save migration, and rollback to previous mod release. — post-completion test phase (owner-operated).
- [T] The launch-gated half of the mod-page row: **screenshots, trailer/preview art**, and any known-issues entry that needs an observed failure. The row itself lives in M6a with its full verbatim text; only these pieces need a running game. — post-completion test phase (owner RimSort launch).
- [T] The launch-gated half of the tag-release row: *"publish only features that passed their listed acceptance criteria"* — **nothing has passed anything, because nothing has run.** The row itself lives in M6a with its full verbatim text; the tag cannot be cut until the acceptance results above exist. — post-completion test phase (owner RimSort launch).

### Owner direction — credits, bonds, and the weight of the place (2026-09-29)

**Verbatim owner requests (2026-09-29, three more):** *"yeah keep teriing it then dont stop at 1 million"*; *"and ther should be a trader that is the multi trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies like a universersal trader but things are tech and company quest locked out till passed"*; *"and even cost credits to unlock item and materials and equipment gates in buying"*.

- [ ] **Exchange-rate balance** alongside catalogue balance. Both are constants in one place; neither has any play behind it.
- [ ] **Corporate catalogue balance.** The five tiers and their access fees are a first pass with no play behind them. They are data, so changing them is a def edit rather than a code change.


### Owner direction — the place copies you, and who you find in it (2026-09-29)

**Verbatim owner direction (2026-09-29):** *"and rember ther are 1x1 1x2 and 1x3 and 2x3 gate doors that allow differnt capabilities as to the universe and scerios needs fyi all starts have same tech tree just differnt starting researches finished based on scenerio"*

- [~] **PART BUILT 0.9.2-dev.** Costs-more-to-run and more-people-abreast are done: draw and spin-up scale on footprint, and width adds doorway cells with **no quota anywhere**, per *"we dont want limitations"*. Still open: what size lets *through* (body size at the traversal chokepoint) and hostiles needing width. **"allow differnt capabilities"** — width is the capability. How many people cross abreast, whether bulk cargo, pack animals or a vehicle fits through, and what the opening draws. To be specified per size as part of the multi-cell gate work.

**Verbatim owner direction (2026-09-29):** *"we also need to be making sure all mod ingame decriptions and informational informations for everything is properly in the cards like the game does currently"*

- [~] **PART BUILT 0.9.3-dev** for our own defs, which are now described **and rendered** - the facilities overview and the procurement list. **Still open:** an audit of inspect-card text on the station and the beacon, the way the gate already has one. **Informational text on the cards** for everything a player can select or inspect: gates, the station, the beacon, bonds, coordinates and the rest. What it is, what it needs, and why it is not working when it is not.


**Verbatim owner direction (2026-09-29), on ordering the remaining work:** *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*


- [ ] **"to the extent we want normal and really want the creepy insane looks and feel"** — the balance between recognisable and wrong is currently fixed by the depth curve. Whether it lands is a play question and belongs to the post-completion test phase.

### Owner direction — the look, and the seed generator that has to carry the universe (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly, and remmeber when building the seed genrator for the back rooms everything ive said and how the backrooms universe works to be lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

**And immediately after:** *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

That second message is what shaped the palette: a single global look could only ever deliver half the direction, so the look is a **function of depth**. Record: [`implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md`](implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md).

- [~] **"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying"** — **THE ARITHMETIC GUARANTEES IT AS OF 0.8.0-dev**, as three properties rather than tuning: an **absolute** cap of three simultaneous encounters at any depth and any wealth; **half of every coordinate's rooms bare by count rather than by chance**, so an unlucky run of rolls cannot produce a space with something in every room; and a first visit always quiet. Shallow coordinates are also capped below the top band regardless of wealth. **Stays in progress until inhabitants exist and the condition can actually be observed.** — **an acceptance condition on the whole generator, not a nice-to-have.** A high-tier coordinate that cannot be survived solo by building, supplying and finding a way out has failed this direction regardless of how good it looks.

### Owner direction — nothing is deferred, and what the Backrooms is *for* (2026-09-29)

**Verbatim owner request (2026-09-29), answering the floors question and going well beyond it:** *"ik think option one can work and we can add a flag to item from the back rooms like (odd) or something like that and have quests and missions and contracts and stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd) and the such for all things materials and resources ect ect that can give reason for the players to have to advance and excplore and haul and use the spaces iin the backrooms"*

**This is the answer to why a player goes back in, and it turns the whole cross-map work engine into an economy.** Thirty-one work families already move real goods through a gate; nothing in the game has ever asked for those goods *by origin*. An odd-only contract cannot be filled from the colony stockpile at any price — only by going in, working the space and hauling it out. It also gives ordinary Core resources a second tier of value **without inventing a single new item**.

- [ ] **The laundering routes are closed and must stay closed.** Marking happens in exactly one place — once, at the end of generation, before the map can be reached. Marking on spawn instead would let a player haul ordinary goods in, drop them, and carry them out as odd. Any future code that marks a thing anywhere else reopens that hole. — the stated purpose, and the acceptance test for the whole feature: if odd contracts can be satisfied without entering a coordinate, it has failed.

### Owner direction — the M6 release gate (2026-09-29)

**Verbatim owner request (2026-09-29, three answers):** *"what is the m6 gate use askme question lets get past it"*, then the answers themselves — **M6 path:** *"Split M6a / M6b, build all of M6a"*; **fixtures:** *"option 2 and option 3"*; **release:** *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*.

Two of the three override standing policy, so all three are recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) as decisions 19, 20 and 21, and **D1 is superseded** there. This is the first change to a D-numbered Gate 0 decision since they were recorded on 2026-09-27.

- [ ] **Consequence: the no-compatibility-claim rule is now the main protection, not a formality.** D1's option B text stays binding — *"do not announce compatibility until validation is complete"*. The mod page may claim the Core-only solo path and must claim **no** profile row, **no** DLC interaction and **no** RWT co-op until that row has a recorded result. **200 of the 294 dispositions are still provisional.** Owned by M6a's mod-page row.
- [ ] **Consequence: save migration becomes a standing obligation from the first published version.** It was a release-day checkbox on the assumption that publication came last. From publication onward there *are* other people's saves, so every subsequent version must carry a migration or a declared break. Owned by [`SAVE_MIGRATION_POLICY.md`](SAVE_MIGRATION_POLICY.md); D2's version policy is unchanged (`0.x` pre-release, `1.0.0` first stable).

### Owner direction — the other half of the topology: a way out into the world (2026-09-29)

**Verbatim owner requests, carried from the topology direction:** *"and or pop out any where in the game world on a tile map"*, and the worked examples *"map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map"*.

Record: [`implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md`](implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md).

- [ ] **A world tile the branch does not hold** — still the larger half, needing a new world object and a generated map. Its own checkpoint.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [ ] **A world tile the branch does not hold** — still open. A new world object and a generated map; its own checkpoint.

### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)

**Verbatim owner request (2026-09-29, seven items):** *"read Now. md and any and all revent prep docs as you continue the todo work and take not there is a mode .xlml like thing that im not sure is fully working i try to open it but its not human navigatable but its suppose to spreeadsheet out all the mods and potential uses and issues and theri uses and descriptions and shit if i remember correctly and you should definatly be using it and or fixing it up as you go along with build the Mod here and or update it where need of past work already done and continue it forward and making sure it is human havigate able becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"*

**Verbatim owner identification (2026-09-29):** *"Rimrooms_Async_Industries_294_Mod_Integration_Register this thing is what i was talking about"*

**Verbatim owner report (2026-09-29, the root cause):** *"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt??? wtf i thought it was the mod spreedsheeet! fix it"*

Full record in [`implementation/MOD_REGISTER_REBUILD.md`](implementation/MOD_REGISTER_REBUILD.md); the work-type findings it produced are in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md).



**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **The register opens without a repair prompt or a layout complaint** in whatever the owner actually uses. This is the one claim structural verification cannot make; it belongs to the post-completion test phase.

### Post-completion test phase — `[T]`, gates nothing

- [T] Runtime regression acceptance for these increments and their connected first-expedition loop, after the owner launches the disposable RimSort profile. *(master TODO §Earlier company/scenario increments)* — Needs, in the post-completion test phase: the owner's RimSort launch of the 295-entry product target (296 with the RimBridgeServer QA overlay attached afterward). Claude never starts RimWorld, never touches the active RimSort list, never attaches RimBridgeServer outside `research/RIMBRIDGE_TEST_HARNESS.md`.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **Every runtime acceptance row** across M1–M6 (Gate 2 onward), including the per-checkpoint acceptance lists at the foot of each implementation record. These feed the phase above. They gate nothing.

## Fifth launch findings — 2026-09-30

Owner, verbatim: **"okay check it the store and pawns are there now but i dont see a natural gate
thats suppose to be on the back wall of one of the storage rooms so that they can eneter theri
300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels with
thir natual gate spawns to different levels within"**



  The site failed in `ValidateNativePowerNetwork`, which required `count(def == lightDef)` to equal `Rooms.Count + Rooms.Count(service_passage or utility_room)`. The extra lamps in that sum are `RoomContentBuilder`'s hard-coded **`StandingLamp`**; `BackroomsPalette` switched `lightDef` to **`WallLamp`** at **0.7.8-dev**. `climateRoom` guarantees at least one such room exists, so the shortfall was arithmetic, not chance: **no Backrooms coordinate could generate for thirty-nine checkpoints**, and no proof caught it because they read source text and nothing had ever run the generator.

  The validator now checks the lights **actually placed** and sweeps **every `CompPowerTrader` on the map** — it names no def and predicts no count. And a power fault is **reported, never fatal**: a dark, cold coordinate is playable, a missing one costs the player the gate. `ValidatePlacedLayout` stays fatal. Record `implementation/NATURAL_GATE_UNBLOCKED_IMPLEMENTATION.md`, **28 of 28** plants caught.




- [ ] **"and everything doesnt have to be square rooms and rectangle halways and u can use walls as pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms and this can propigate depper with the wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches that are found everywher deeper in with wild random events and layouts and spawns to find and loot!!!!!!"** — **OPEN. This REVISES the room-count answer given an hour earlier and it is the better call.** Taken apart into what each clause actually requires:

  | Clause, verbatim | What it means in the generator |
  |---|---|
  | *"everything doesnt have to be square rooms and rectangle halways"* | a room's `Bounds` stays a rect for bookkeeping, but the **carved shape** does not: L, T, cross and ragged-edged rooms, and corridors that change width and bend |
  | *"u can use walls as pillars"* | interior `ThingDefOf.Wall` on a support lattice. **This is the thing that makes grand spaces possible at all** — `RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**, so a roofed span wider than ~13 cells needs something holding it up, and a pillar is exactly that |
  | *"making the 0 level rooms be grand large spaces"* | shallow depth is **few, very large, pillared halls** — not the tidy 10-16 cell boxes the planner builds today |
  | *"leas than 60-100 romms"* | **supersedes the 60-100 dense-warren answer.** Fewer rooms, each far bigger. The warren idea moves inward rather than being dropped |
  | *"this can propigate depper"* | the variation is a **function of depth**, which `BackroomsPalette` and `Derange` already are. Same axis, more of it |
  | *"wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches"* | `CoordinateMaterials` already picks stuff per coordinate; widen it across **every** placed category and let the spread grow with depth |
  | *"found everywher deeper in"* | material variety is discovered content, so what a room is **built from** is part of the loot |
  | *"with wild random events and layouts and spawns to find and loot!!!!!!"* | `AnomalyEventService`, `InhabitantService` and `RoomArchetypeService` all exist; the layouts and the loot density scale inward with the rest |

  **What stands from the four earlier answers:** levels are **300x300**; `threshold_room` / `office_copy` / `return_gallery` stay **unique** while other families **repeat**; **new structural families** are authored as layout and dressing only with **no new ThingDefs**; **4-6 onward gates** per level with `MaximumNaturalDepth` **3 to 6**; **fresh save**, the 60x60 path dropped.

  **What changes:** *"leas than 60-100 romms"* replaces the 60-100 count, and grand pillared halls at shallow depth replace the uniform small-room grid. The 10x10 planning grid at 19-cell spacing was sized for the old shape and is superseded with it — a grand hall does not fit in a 19-cell slot.

- [ ] **SUPERSEDED IN PART, same day, by the row above** -- the *"leas than 60-100 romms"* direction replaces this row's 60-100 count and its uniform small-room grid. Kept whole because the size, family, gate-count, depth-cap and save decisions in it all still stand.
- [ ] **"theri 300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels with thir natual gate spawns to different levels within"** — **OPEN, and fully specified by the owner across four questions this checkpoint.** Levels become **300×300** (from 60×60); **60–100 rooms** in a dense warren on a **10×10** planning grid at the existing 19-cell spacing; **threshold_room / office_copy / return_gallery stay unique**, the other five families **repeat**, and **new structural families** are authored (flooded_room, stairwell, dead_end, pillar_hall) — **layout and dressing only, no new ThingDefs**; **4–6 onward gates per level**, one per ~15 rooms, with `MaximumNaturalDepth` **3 → 6**; and a **fresh save**, dropping the 60×60 path entirely for one shape, the simplest code and the cleanest proofs.

---

## Coordinate rebuild, stage one — 2026-09-30 (0.12.49-dev)





- [ ] **"dont let them go more than 5 remember the games mechanics and limits built in if they find a gate to a world map tile or a deeper backrroms and they have 5 mpas they should gett a warning this gate is blocked your holding open too many gates, but per scerio styled"**, clarified by **"5 is the limit of other colonies available so a backrooms level should be one colonly bacskicly in my thinking"** — **OPEN, stage two, and it SUPERSEDES the LRU-eviction answer given minutes earlier.**

  A hard cap with **no eviction** is strictly better: nothing the player looted or built ever resets, memory is bounded by construction, and the limit is **diegetic** rather than an apology about memory.

  **And the owner's clarification grounds the number in Core.** `Prefs.MaxNumberOfPlayerSettlements` is a player option, a slider from **1 to 5, default 5**, enforced by `SettleUtility` as `count >= Prefs.MaxNumberOfPlayerSettlements`. Core counts only `map.IsPlayerHome && map.Parent is Settlement` plus gravship landings, so a `RimroomsDestinationMapParent` is **invisible to it**. So the budget is read from that pref rather than hard-coded, and a coordinate map counts against it — *"a backrooms level should be one colonly bacskicly"*. A player who sets the slider to 3 gets 3.

  *"per scerio styled"* means the budget belongs on the scenario, not a global constant.

  **This ships together with raising onward gates to 4-6 and `MaximumNaturalDepth` 3 to 6**, because the cap without the gates is pointless and the gates without the cap is what kills the game: `RimroomsDestinationMapParent.ShouldRemoveMapNow` always returns false, so at 90,000 cells and ~70,000 mineables per level, hundreds of reachable levels against a `MaximumCoordinates` of 512 would be fatal.

- [ ] **still open from the same direction** — non-rectangular rooms and corridors; and the wild variation of materials across items, equipment, walls, floors, lights, furniture and benches, with the events, layouts and loot deeper in.

---

## Coordinate rebuild, stages two to four — 2026-09-30 (0.12.50-dev)








- [ ] **"how do they turn them off to use the machine gates for more controll and aiming deeper?"** / **"get 5 natural gates u cant use a machine gate"** — **OPEN, and deliberately NOT half-built. Next checkpoint, first thing.** The owner chose an **Operations held-places list with Release**. Releasing a place is not a UI problem; it needs (1) a **save-schema field on `CoordinateRecord`**, because `EnsureSite` deliberately refuses to regenerate a coordinate whose rooms were surveyed and only a flag can distinguish a deliberate release from a broken reference; (2) map teardown that orphans neither the world object, the `Site` reference, nor a portal edge pointing in; (3) a refusal set — crew present, crossing in flight, or the headquarters. Getting any of those wrong produces an unreachable place or a dead record, which is the exact defect class that cost thirty-nine checkpoints. **Mitigation meanwhile: discovering gates is free** — no map is generated until somebody crosses — so the cap is only met after five places are held open.

- [ ] **still open from the same direction** — the wild variation of materials across items, equipment, walls, floors, lights, furniture and benches, with the events, layouts and loot deeper in.

---

## Releasing a place — 2026-09-30 (0.12.51-dev)


  **And the trap was worse than the previous record said.** That record claimed discovering a gate was free because no map existed until somebody crossed. **It was wrong:** `Discover` calls `RegisterNaturalAddress`, which calls `EnsureSite` **immediately**, because a natural edge is registered against the far side's own `ReturnAnchor` and that `Thing` does not exist until the map does. **A discovery costs a slot at the moment it is made**, so the budget check in `Discover` is load-bearing rather than over-eager, and five discoveries really do lock a player out of their machine gates. The previous record is **annotated, not rewritten**, per invariant 135.

  A natural gate is permanently open (invariant 12) and is never closed. What is released is **the space behind it**. The door stays, still marked, and **remembers which place it led to** on its own comp — written at release while the edge still says so, because the edge has to be removed and is the only other record of the pairing.

  **The teardown order is the whole of the safety, and it is asserted as an ordering:** the doors are told where they led **before** the edges are removed, and the edges are removed **before** the map is torn down. Reverse either pair and a record points at something that no longer exists, which is this project's most expensive defect class.

  **`releasedByPlayer` is the only thing that can tell a deliberate release from a broken reference** — both look identical from outside, no site and surveyed rooms — and `EnsureSite`'s explored-graph guard exempts exactly that and nothing else. It still refuses a competing owner or a live map, and the exemption is **spent the moment the place exists again**, because an exemption that outlives its reason is a hole.

  Refusals name themselves: the headquarters, crew inside (**a prisoner or an animal counts**), a crossing in flight, or a place with no live map. Re-opening goes through the same `RegisterNaturalAddress` path that first created it, is **disabled rather than hidden** at the budget, and **only forgets the shelved place on success** — forgetting on failure would strand it for ever over a transient refusal.

  Record `implementation/RELEASE_A_PLACE_IMPLEMENTATION.md`. **88 of 88** planted faults caught.

- [ ] **still open from the same direction** — the wild variation of materials across items, equipment, walls, floors, lights, furniture and benches, with the events, layouts and loot deeper in.

---

## The first walked level — 2026-09-30 (0.12.61-dev) — DONE

**IT WORKED. The owner is in the Backrooms for the first time, on the ninth launch:**
**"okay it fucking worked!!! im in the backrooms!!! but issues..."**

Owner, verbatim, in full:

> **"1. i explored it all and there were zero weird events or people, there were zero portals to
> be discovered. as in the didfferent scernios they all should have an additional portal to other
> maps and levels... and i love the backrooms level i looked at and went into one issue not enough
> rooms and not enough loot and not enough weird stuff like a room with a lost person or a room
> full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or
> tool sheed or weapons locker with loot and supplies anssd furnuture all ot of it randomly like
> and scary freaky spooky like. . its currently really nice but the furnature is only in the four
> corners of the rooms that nots very random. 2. there is a weird route thing name a self in one of
> the rooms and this is kinda weird and odd and we probably havent gotten to a routing system yet
> for emergency exit and glow pods with the company start but lets try and fix this so the normal
> yellow backrooms look isnt the whole floor but the main spanw room and going deeping in can mean
> the numner of branch hallways and rooms distancing from the main portal spawn in the back rooms
> continuw on into the map with variations and oddity and events and locations and places that vary
> more even on the first level. cant have a whole backrooms be nothing but what it currently is if
> u look at the game and where Gee is at it needs to be more maze liek and scary inducing beyond
> the main starting themed opening room and have more natural portals guaranteeed so the backrooms
> never ends \"persay\""**

> **"every backrooms instance need a protal to the world map and a deeper in portal"**

**MEASURED FROM THE LIVE MAP, so the scale of the gap is known rather than guessed.** The minimap
shows **nine rectangular rooms on straight corridors**, and the planner explains it exactly:
`slots = MinSlotsPerAxis + (depth - 1)` is **3** at depth 1, so a 3x3 grid of nine slots, of which
`chain` takes six and spurs take three. **Nine rooms, all boxes, one serpentine corridor.**

- [ ] **"every backrooms instance need a protal to the world map and a deeper in portal"** — a hard guarantee of **two** natural gates per instance: one out to the world map, one deeper. Not a chance roll.
- [ ] **"there were zero portals to be discovered"** and **"have more natural portals guaranteeed so the backrooms never ends persay"**
- [ ] **"not enough rooms"** — nine is not a Backrooms level
- [ ] **"it needs to be more maze liek and scary inducing beyond the main starting themed opening room"**
- [ ] **"the normal yellow backrooms look isnt the whole floor but the main spanw room"**
- [ ] **"going deeping in can mean the numner of branch hallways and rooms distancing from the main portal spawn in the back rooms continuw on into the map with variations and oddity and events and locations and places that vary more even on the first level"**
- [ ] **"not enough loot"**
- [ ] **"not enough weird stuff like a room with a lost person or a room full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or tool sheed or weapons locker with loot and supplies anssd furnuture"**
- [ ] **"all ot of it randomly like and scary freaky spooky like"**
- [ ] **"the furnature is only in the four corners of the rooms that nots very random"**
- [ ] **"zero weird events or people"**
- [ ] **"there is a weird route thing name a self in one of the rooms and this is kinda weird and odd"** — owner's own read: *"we probably havent gotten to a routing system yet for emergency exit and glow pods with the company start but lets try and fix this"*

---

## Lights and geometry — 2026-09-30 (0.12.61-dev) — DONE

Owner, verbatim:

> **"and we need more lights and mixedered varies of lights but the main grand themed backrooms
> universe rooms need like a wall light on every column wall used as in the universe of backrooms
> the basic rooms are well lit"**

> **"and you can have back to back roomes and mazes of halways of varied widtchs and lengs and odd
> variers walls and contructions making narrows , expansies, triangle, octangones, rombones, all
> the geomentry and mixetrues and odd contructions of doors walls corners deadends doors to now
> where not just doors on 4 cosides of nothing but square rooms"**

- [ ] **"we need more lights and mixedered varies of lights"**
- [ ] **"the main grand themed backrooms universe rooms need like a wall light on every column wall used"** — the pillar lattice already exists in `RoomLayoutPlanner.PillarCells`, so every pillar is a known cell with a wall to hang a lamp on
- [ ] **"as in the universe of backrooms the basic rooms are well lit"** — brightness is part of the theme, not a convenience
- [ ] **"you can have back to back roomes"** — rooms sharing a wall, with no corridor between
- [ ] **"mazes of halways of varied widtchs and lengs"**
- [ ] **"odd variers walls and contructions making narrows , expansies"**
- [ ] **"triangle, octangones, rombones, all the geomentry and mixetrues"**
- [ ] **"odd contructions of doors walls corners deadends"**
- [ ] **"doors to now where"** — a door that opens onto solid rock or a sealed closet
- [ ] **"not just doors on 4 cosides of nothing but square rooms"** — the current rule is literally a doorway at the midpoint of each of four walls

---

## The lab name comes out, and every level becomes a maze - 2026-10-01 (0.12.68-dev, 0.12.69-dev) - DONE

Owner, verbatim:

> **"take the Unity Lab AI and the Unity AI Lab out of all refrences and nameing but we will keep
> the repos as is for now. especially remove the Unitylabai from the mod information that i see on
> Rimsort ie the package id and folder naming and such and files, and there is one issue all the
> backrooms so far are just one lone strain of perals arangement that snakes back and forth across
> the map like one series line... i want them to be mazes like xcrazy like all levels mazes do you
> unerstand! lsd crazy shaped mazes and facilitys and :\"buildings and neighboorhoods and
> complexes and shools and hospitals and military and storages need loot inside of them too"**

- [~] **"all the backrooms so far are just one lone strain of perals arangement that snakes back
  and forth across the map like one series line"** - **the owner is describing the algorithm
  exactly.** `RoomLayoutPlanner.Build` walks the slot grid row-major with alternating direction
  and calls it a *serpentine*; it is one line that snakes, by construction

---

## One battery was the whole reserve - 2026-10-01 (0.12.77-dev) - DONE

Owner, verbatim, from a running game:

> **"its the same problem as before: the laboratory address for that is not open.... thats just
> clicking on the portal and trying to send them through not working,,, and using operations
> clicking send pawns through which i think is a power porblem but you can check the game current
> running,, looks like only being able to connect 1 battery isnt anough and there should be no
> loimit"**

**The owner's diagnosis is correct and the mechanism is worse than the symptom suggests.**

- [ ] **`returnReserveCapacityWattDays` is 2 and a Core `Battery` holds 600**, so the bind-time
  *ReserveTooSmall* refusal is **not** the cause. Checked and ruled out rather than assumed

---

## The doc sweep picked back up, and a site that does not pop like a text wall - 2026-10-01

Owner, verbatim:

> **"i docs and pages for when we deploy on github"**

> **"we were doing the massive update and corrections to content style and formate of all the docs
> pertaining to that doc push earlier that we neeed to pick back up on and docs and pages when we
> deploy the wiki and docs on github"**

and at the two forks, verbatim:

> **"docs/ root on this repo, github.io for now"**

> **"the beautiful and masterfully way paossible so the thing needs to NOT pop like a text wall"**

- [ ] **Style and format across the thirteen WIKI pages is the remaining half**, and it belongs with
  the site build below rather than here, because *"NOT pop like a text wall"* is a layout answer as
  much as a prose one.
- [ ] **"and docs and pages when we deploy the wiki and docs on github"** - the deploy half.
- [ ] **"docs/ root on this repo, github.io for now"** - Pages serves `docs/` on this repository.
  `_config.yml` keeps `include: wiki` and the working material excluded. **CNAME support authored
  now, the domain left open** - no document names a URL the deploy does not have.
- [ ] **"the beautiful and masterfully way paossible so the thing needs to NOT pop like a text
  wall"** - `jekyll-theme-primer` is a text wall with a margin. Real layout and stylesheet, and the
  thirteen pages restructured so each one is scannable rather than read from the top.
- [ ] **The generator stays internal, by the finding that opened this.** `outputs/readable/` renders
  `TODO.html` and `NOW.html` - the work ledger - to standalone HTML. Nothing publishes them today
  because `_config.yml` includes `wiki` alone, but TODO row 270 names
  `tools/make-readable-html.py` as the site's seed, and pointing it at the site would publish the
  ledger. **It stays an internal reading convenience and is never wired to the published tree.**
- [ ] **`check-doc-conformance.py` must cover the published site** (row 271), so a page cannot claim
  a version or a branch the build does not have.

**Mod register.** Checked before designing: it bears on this as the **source** for what
`COMPATIBILITY.md` and the wiki's `mods.md` may claim - `RR-COMPAT` carries 293 of the 295 rows and
`RR-DLC` 40 - and the standing no-compatibility-claim rule means those pages state **declared
requirements**, never tested-together claims. Nothing else in the register applies to a docs sweep.

---

## TOMBSTONES

_(none)_
