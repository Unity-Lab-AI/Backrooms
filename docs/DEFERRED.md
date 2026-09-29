# DEFERRED — the register of everything put off, and who owns it

**Owner rule (2026-09-28, verbatim):** *"make sure things u deferr(ther really shouldnt be defferments if u do the correct order of work)(might be different than stated) dont get lost in the mix and never properly built"*

So: a deferment is only legitimate when the work genuinely belongs to a later step in the dependency order, and it is **only** legitimate once it is written here with a named owner step. Nothing leaves this file by being forgotten. An entry leaves only when it is built and archived in [`FINALIZED.md`](FINALIZED.md), or when the owner explicitly cancels it (then it moves to the TOMBSTONES section with the reason).

Every session must read this file alongside `TODO.md`. When a step in `TODO.md` closes, every row here whose owner is that step must be either done or re-owned to a later step with a reason. A step cannot be marked complete in `TODO.md` while it still owns an open row here.

Status: `[ ]` open · `[~]` in progress · `[x]` built (archived in `FINALIZED.md`, row kept here for the trail) · `[!]` blocked on the owner.

---

## Open deferments

### Owned by M1 resume step 3 (crossing jobs, player controls, emergency return)

- [ ] **Player-facing text for the 32 crossing failure keys.** `RR_PortalCrossing_*` keys are returned by `PortalCrossingService` and had no `Keyed/` entries. Partially closed in step 2 (`RR_Portals.xml` now carries them); the remaining work is showing them at the point a crossing is actually attempted, which needs the crossing job. Source: `docs/implementation/CONNECTED_CROSSING_CALLER_REVIEW.md` §3.
- [ ] **Emergency-return route for a laboratory session that closes while workers are across.** Contract: workers stay where they are with their real inventory; return only by physically crossing a reopened edge (`RecoverPortalOpening` debits once per operation id) or through receipt recovery. No teleport, no duplicate debit. Source: caller review §3, `CONNECTED_COLONY_PORTALS.md`.
- [ ] **Surface unresolved crossing receipts in the Operations network view.** A pawn held in the crossing service's `ThingOwner` does not tick (no needs, no healing); recovery is the only exit, so it must never be invisible. Source: caller review §3.
- [ ] **Deliberate-cross gizmo must name the refusal reason for an ineligible pawn** (drafted, downed, prisoner, slave, quest lodger, mental state) rather than hiding the option. Source: caller review §3.

### Owned by M1 resume step 4 (work intents, leases, adapters)

- [ ] **Adapter families, one at a time with source evidence per route:** ~~storage hauling~~ (BUILT 0.5.0-dev) → construction supply/finish → bills → research → tend/rescue → food → rest → remaining families (cleaning, repair, firefighting, plants/mining/hunting, patient feeding, prisoner/guest, wardening, childcare, animals/mechs, refuel/rearm, joy, rituals, hauling providers) → every installed work giver in the 294-row profile. Source: `CONNECTED_WORK_CORE_API.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md`.
- [ ] **Container and provider haul destinations.** A delivery currently resolves to a storage *cell* only. `StoreUtility.TryFindBestBetterStorageFor` can also return an `IHaulDestination` container, and Core's container route is a different driver. Until that adapter exists, a container-only destination reads as "no storage on arrival" and the object is set down as a real item instead. This is where Adaptive Storage (10/24/25/26), LWM Deep Storage (122), Warehouse (259) and RimFridge (195) belong, each needing its own reviewed adapter. Source: `implementation/CONNECTED_WORK_IMPLEMENTATION.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md`.
- [ ] **Remote allowed-area preflight.** `Pawn_PlayerSettings` exposes no public arbitrary-map area accessor, so 0.5.0-dev deliberately claims **no** remote allowed-area compliance: the candidate half checks faction-level forbidding only, and the definitive per-pawn check runs on arrival, closing the trip with a keyed reason rather than stranding anyone. Closing this row needs either a separately reviewed accessor/integration route or an explicitly declared limited policy the owner accepts. Never by map spoofing. Source: `CONNECTED_WORK_CORE_API.md` §Scheduler/target APIs.
- [ ] **People and corpses as connected work.** The storage-hauling family deliberately refuses `Pawn` and `Corpse`. Carrying someone downed, dead or imprisoned through a gate is permitted by `PortalTraversalPolicy`, but it is rescue, capture or burial work and needs the tend/rescue and remains families with their own bed, custody and grave rules. Source: `implementation/CONNECTED_WORK_IMPLEMENTATION.md`.

### Owned by M1 resume step 5 (providers, scenario openings, inhabitants)

- [ ] **Natural-portal discovery trigger.** Step 2 built the deterministic coordinate API (`CreateDiscoveredCoordinate`) and natural-edge registration, but nothing in the game yet *discovers* a natural threshold. The trigger belongs with procedural frontiers. Source: `CONNECTED_COLONY_PORTALS.md` §Coordinates and repeat visits.
- [ ] **Procedural inhabitants, rare monstrosities, evolving saved events, technology-driven complexity families.** Source: `CONNECTED_COLONY_PORTALS.md` §People, monstrosities and increasing complexity.
- [ ] **The saved, bounded escalation ladder** required by the owner's gate-pacing rule, to be authored before any inhabitant generation ships. Concrete spec: a newly opened coordinate starts quiet; pressure rises only from saved observable causes (operating history at that coordinate, depth and complexity, unlocked technology, what has already been taken out), never from wall-clock time, a fresh draw per load, or the mere fact a gate is open; caps on simultaneous encounters, inhabitants and events per opening and per coordinate, where raising a cap is itself a recorded progression step; quiet stretches are required content, so a space presenting something in every room fails; several open gates never sum into one escalating number, for any start; reopening a known space resumes its saved pressure without rerolling up to punish a revisit or down to make one safe. Inherits the frozen threat rules: readable warning, learnable rule, at least one countermeasure, no unavoidable instant failure. Source: `CONNECTED_COLONY_PORTALS.md` §Who may cross, and the pacing of what waits on the other side.
- [ ] **Optional work/storage provider adapters** (Pick Up And Haul 164, Haul To Stack 107, Adaptive Storage 10/24/25/26, LWM Deep Storage 122, Warehouse 259, RimFridge 195, Prison Labor 288, Research Whatever 279, Meals On Wheels 125, Gastronomy 269). Core-only path must work with every one absent. Source: `CONNECTED_WORK_PROFILE_BOUNDARIES.md`.

### Owned by M1 resume step 6 (milestone hygiene)

- [ ] **Bounded-archive policy for crossing receipts.** Retained without compaction today; only becomes a real cost once receipts are reachable in play. Source: caller review §3.
- [ ] **Connected-site scheduling and streaming, then measurement.** Active connected job destinations must not be silently unloaded to meet a budget. Measurement itself is owner-blocked. Source: `CONNECTED_COLONY_PORTALS.md`, `research/PERFORMANCE_BENCHMARK_PLAN.md`.
- [ ] **Converge the three `OwnsMap` implementations.** The canonical accessor now lives on `RimroomsCampaignComponent.OwnsMap(Map)` and all new code calls it, but private copies remain inside `RimroomsPortalNetwork` and `RimroomsPortalCrossingService`. The crossing service's copy is the strictest of the three. Converging them mid-feature was deliberately avoided; do it as hygiene, behaviour-preserving, with the strict version winning. Source: `implementation/CONNECTED_WORK_IMPLEMENTATION.md`.
- [!] **Balance review of the two connected-hauling work-giver priorities.** `RR_ConnectedHaulingContinue` at 95 and `RR_ConnectedHauling` at 14 are deliberate balance choices against Core's `Hauling` ladder (`HaulToPortal` 105, `Strip` 100, `HaulCorpses` 90, `HaulGeneral` 15). Starting a gate trip must not outrank local hauling; finishing one must not lose to it. Whether those exact numbers feel right needs the owner's launch. Source: `implementation/CONNECTED_WORK_IMPLEMENTATION.md`.

### Owned by M2 (existing-content replacement)

- [ ] **Legacy gate objects** `RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator` → designated Core `Autodoor`/`CommsConsole`/`PowerSwitch` + generation. No single Core generator meets the 3,500 W opening draw (`GeothermalGenerator` is 3,600 W); pick the provider deliberately. Hidden from construction today, still in the package.
- [ ] **Legacy field gear** `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon`, `RR_SealedEvidenceCase`, `RR_RouteRecording` → existing objects with saved role bindings. Core has no portable recorder/tag/case; removing the mechanics is a **rejected** scope reduction. `MedicineIndustrial` is explicitly an unsafe substitute.
- [ ] **Legacy fixtures and terrain** `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, plus `RR_FieldAnalysisBench` retirement.
- [ ] **`RR_QuietPursuer` presentation** → existing native pawn presentation (`Megascarab` reskin candidate) or removal, keeping the learned rules and encounter.
- [ ] **Five `RR_*Staff` PawnKinds** → native `Colonist` (new starts already use it; old kinds are readable-only).
- [ ] **Five recipes** (`RR_MakeFieldRecorder`, `RR_MakeSurveyTags`, `RR_MakeReturnBeacon`, `RR_MakeEvidenceCase`, `RR_AssembleMachineGate`).
- [ ] **Migration decision or declared development-save break** before removing any Def a saved `Thing` references, with the old build preserved. Shares saved keys with the portal legacy-threshold repair built in step 2 — decide them together.
- [ ] **Remove the 14 historical gameplay PNGs from the package allowlist** once their references are gone.

### Owned by M3 (Phase 3 breadth) — deferred by dependency, not by choice

- [ ] Room functions, applicant pools, training/certification, wellbeing (needs the cross-map adapters to be meaningful across maps).
- [ ] Contract/quest templates for the 13 mission families, leases, shipment incidents.
- [ ] Research IDs across tiers T0–T6 and the nine branches; entity family sheets (broad families only per S1/B).
- [ ] Containment, interviews, settlement openings, outposts, vehicles, VGE hooks.
- [ ] Store start; Lone Survivor start (also owner-blocked, below).

### Owned by M5 (interface) / M6 (release)

- [ ] Eleven-pane Company Command, deep links, reason codes, native menu remap.
- [ ] Tutorial, glossary, keyboard paths, contrast/scale, localization completeness.
- [ ] Slideshow integration review, additional menu images per shipped scenario.
- [ ] Validation sweep, invalid-state matrix, balance, release report, packaging.

### Blocked on the owner — cannot be built by an agent

- [!] **Inside start: configurable party versus strictly lone start.** Provisional assumption in use: configurable solo/group. Source: `SCENARIO_SETUP_AND_PORTAL_NETWORK.md`.
- [!] **Inside start: first reliable exit reveals a fixed discovered surface destination, or the player chooses a settlement.** Provisional assumption: fixed discovered destination.
- [!] **Opening duration.** The accepted value is 833 ticks ≈ 14 real seconds at normal speed; the previous agent asked whether 20 real minutes, two in-game hours, or 20 in-game minutes was meant, and recorded it as a usability/balance risk. Retained until directed otherwise.
- [!] **Every runtime acceptance row** across M1–M6 (Gate 2 onward). Needs the owner's RimSort launch of the 295-entry target. The agent never launches the game.

---

## Built (kept for the trail)

- [x] **Crossing-service boundary review** — closed by resume step 1; record `implementation/CONNECTED_CROSSING_CALLER_REVIEW.md`. No source change was needed and no check was weakened.
- [x] **Legacy saved-endpoint repair route** — closed by resume step 2; a Core steel door replaces the historical `RR_ReturnAnchor` on an already generated site, receipt-recorded, without rebuilding the map.
- [x] **Deterministic discovered-coordinate API** — closed by resume step 2 (`CreateDiscoveredCoordinate`), so no future discovery caller can invent coordinate ids or seeds.
- [x] **Gate traversal guard** — closed 2026-09-28 by `PortalTraversalPolicy`, the single chokepoint every crossing path asks. Inhabitants and monstrosities cannot cross on their own, an open gate is never a destination or trigger, and anything else rides only in a carrier's hands. The pacing half of the same owner rule is the open ladder row above.
- [x] **Cross-map work intents and quantity leases** — closed 2026-09-28 in 0.5.0-dev. `RimroomsConnectedWorkComponent` owns saved intents; each intent owns its own bounded, expiring lease keyed by the actual `Thing` plus a quantity, so the two can never desync. The lease is explicitly not a native reservation: it excludes no native pawn and grants no claim, which is the only safe reading of `ReservationManager.CanReserve` rejecting cross-map claimants. Real custody starts with a real local native reservation on arrival. Record `implementation/CONNECTED_WORK_IMPLEMENTATION.md`.
- [x] **Native destination job revalidation** — closed 2026-09-28 in 0.5.0-dev. The adapter contract separates a candidate half, which runs against an explicit `Map` and never probes a native work giver remotely, from a definitive half that runs only once the worker is standing on the map in question.
- [x] **Storage hauling adapter, both directions** — closed 2026-09-28 in 0.5.0-dev, first of the families. Also fixed there, found in self-review before publishing: the bounded candidate scans originally examined a fixed prefix, which would have starved the fifth and later connected maps forever and broken the owner's multiple-gates rule; they are now rotating windows.

---

## TOMBSTONES

_(nothing cancelled yet)_
