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

- [ ] **Cross-map work intents and quantity leases.** A lease is bounded, expiring, keyed by map + actual Thing/load id + quantity + endpoint + final target; it is not a native reservation and excludes nobody (`ReservationManager.CanReserve` rejects cross-map claimants). Source: `CONNECTED_WORK_CORE_API.md`.
- [ ] **Adapter families, one at a time with source evidence per route:** storage hauling → construction supply/finish → bills → research → tend/rescue → food → rest → remaining families (cleaning, repair, firefighting, plants/mining/hunting, patient feeding, prisoner/guest, wardening, childcare, animals/mechs, refuel/rearm, joy, rituals, hauling providers) → every installed work giver in the 294-row profile. Source: `CONNECTED_WORK_CORE_API.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md`.

### Owned by M1 resume step 5 (providers, scenario openings, inhabitants)

- [ ] **Natural-portal discovery trigger.** Step 2 built the deterministic coordinate API (`CreateDiscoveredCoordinate`) and natural-edge registration, but nothing in the game yet *discovers* a natural threshold. The trigger belongs with procedural frontiers. Source: `CONNECTED_COLONY_PORTALS.md` §Coordinates and repeat visits.
- [ ] **Procedural inhabitants, rare monstrosities, evolving saved events, technology-driven complexity families.** Source: `CONNECTED_COLONY_PORTALS.md` §People, monstrosities and increasing complexity.
- [ ] **The saved, bounded escalation ladder** required by the owner's gate-pacing rule, to be authored before any inhabitant generation ships. Concrete spec: a newly opened coordinate starts quiet; pressure rises only from saved observable causes (operating history at that coordinate, depth and complexity, unlocked technology, what has already been taken out), never from wall-clock time, a fresh draw per load, or the mere fact a gate is open; caps on simultaneous encounters, inhabitants and events per opening and per coordinate, where raising a cap is itself a recorded progression step; quiet stretches are required content, so a space presenting something in every room fails; several open gates never sum into one escalating number, for any start; reopening a known space resumes its saved pressure without rerolling up to punish a revisit or down to make one safe. Inherits the frozen threat rules: readable warning, learnable rule, at least one countermeasure, no unavoidable instant failure. Source: `CONNECTED_COLONY_PORTALS.md` §Who may cross, and the pacing of what waits on the other side.
- [ ] **Optional work/storage provider adapters** (Pick Up And Haul 164, Haul To Stack 107, Adaptive Storage 10/24/25/26, LWM Deep Storage 122, Warehouse 259, RimFridge 195, Prison Labor 288, Research Whatever 279, Meals On Wheels 125, Gastronomy 269). Core-only path must work with every one absent. Source: `CONNECTED_WORK_PROFILE_BOUNDARIES.md`.

### Owned by M1 resume step 6 (milestone hygiene)

- [ ] **Bounded-archive policy for crossing receipts.** Retained without compaction today; only becomes a real cost once receipts are reachable in play. Source: caller review §3.
- [ ] **Connected-site scheduling and streaming, then measurement.** Active connected job destinations must not be silently unloaded to meet a budget. Measurement itself is owner-blocked. Source: `CONNECTED_COLONY_PORTALS.md`, `research/PERFORMANCE_BENCHMARK_PLAN.md`.

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

---

## TOMBSTONES

_(nothing cancelled yet)_
