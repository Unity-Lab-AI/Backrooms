# SKILL_TREE

> **Superseded 2026-10-01 — dependencies.** This document predates the owner's decision that the
> package has hard dependencies. `About.xml` now declares all five expansions and the whole
> collection as requirements, so anything here describing a Core-only route is history rather than
> a current claim. Recorded as a change to D3 and D4 in
> [Gate 0 decisions](GATE_0_DECISIONS.md#decision-log).

Capability inventory for Rimrooms - Async Industries as of 0.6.4-dev (2026-09-28, branch `feature/connected-colony-portals`), covering **every system the finished mod contains**, not only what exists in source. A "skill" is a thing the mod can do or must be able to do before release. Every entry carries a status so nobody mistakes compiled source for a working game:

| Status | Meaning |
|--------|---------|
| **Source** | Implemented in `src/` and/or XML, compiles with zero warnings/errors |
| **Build** | Source + packaged in the 73-file allowlist with saved manifests |
| **Runtime-pending** | Source/Build exists; behaviour never observed in-game (owner has not launched) |
| **Substrate** | API exists but no caller reaches it in play |
| **Design** | Contract written, no source |
| **Blocked** | Waits on an owner decision or an owner-launched run |
| **Deferred** | Owner explicitly deferred (S1/B names, later candidate starts) |

Canonical detail: [`SYSTEMS_CATALOG.md`](SYSTEMS_CATALOG.md), [`FEATURE_TRACEABILITY.md`](FEATURE_TRACEABILITY.md), [`CAMPAIGN_CONTENT_CATALOG.md`](CAMPAIGN_CONTENT_CATALOG.md), [`CAMPAIGN_ROSTER_FREEZE.md`](CAMPAIGN_ROSTER_FREEZE.md), the master TODO. Feature IDs in brackets are the traceability keys.

---

## By Domain

### 1. Scenario and starts [RR-SCEN]
- Async Industries start: `RimroomsStartDef` plan, once-only initializer, guarded native arrival, company review page, chosen-tile receipt, native `Colonist` roster of 5 (1–20 validated) with 14 defined supply lines — **Build / Runtime-pending**
- Native / Prepare Carefully customized pawns preserved through setup (review page appended after the native pawn page; EdB skips `CanDoNext`) — **Source (ordering documented) / Runtime-pending**
- Shared versioned start contract consumed by all starts — **Design**
- Furniture & Knickknack Store: 50×50 shop, 3 controlled people, anomalous basement threshold, secure/search/report choices, $500,000 advance offer, convergence into a contracted site — **Design** (after Gate 2)
- Lone Survivor (`lone_survivor`): inside start in a 6–8 room coordinate, one survivor + finite kit, exit/radio/foothold choices — **Blocked** (party size; first-exit fixed vs chosen) then **Design**
- Later candidates `isolated_outpost`, `town_distortion`, `company_in_crisis` — **Deferred** until a design brief exists
- Per-scenario acceptance checklist (8 rows in `SCENARIOS.md`) — **Blocked** (owner launch)

### 2. Company simulation [RR-FAC, RR-STA, RR-ECO]
- Branch identity, one-time $50,000,000 allocation, USD ledger separate from 150 physical silver — **Build / Runtime-pending**
- Payroll tick ($5,000/staff/day), $25,000/day overhead, arrears, obligations — **Build / Runtime-pending**
- Staff records, company role assignment (advisory; no priority overwrite), once-only hire registration — **Build / Runtime-pending**
- Native-pawn applicants: request, inspect, quote/hire ($100,000 setup), interrupted-arrival recovery, cancel/refund, decline/dismiss, bounded history — **Build / Runtime-pending**
- Procurement: Core-goods quotes (7 catalog entries), one-time charge, supplier custody, receiving stockpiles, partial delivery, redirection, receipts, live stack limits — **Build / Runtime-pending**
- HQ facilities report: buildings, rooms, power, bed classes, care needs, native inspect/assign — **Build / Runtime-pending** (transient, never saved)
- Contracts: one accepted onboarding survey ($5,000,000 + optional $1,000,000 bonus), case records — **Build / Runtime-pending**
- Nine staff categories (research, gate ops, engineering, security, field ops, medical/containment, logistics, communications, administration) with training, certification, schedules, field history, trust/stress/exposure, equipment familiarity — **Design** (Phase 3)
- Twelve facility functions (gate chamber, power/maintenance, laboratory, evidence archive, decontamination/quarantine, security/armory, workshop, medical bay, radio/dispatch, logistics/receiving, quarters, transport/space) as concrete capabilities with "why not functional" alerts — **Design** (Phase 3)
- Applicant pools (candidates, specialists, contractors, survivors, returning staff, referrals) — **Design**
- Cafeteria/sleep/recreation/shift rotation/wellbeing/accommodation capacity — **Design**
- Ledger breadth: upkeep, shipments, advances, salvage, penalties (cap 25%), compensation, profit report; shipment delay/loss/damage incidents; space leasing ($100,000/day) and outposts ($250,000/day); seven economy stages — **Design**
- Hospitality/guest/prisoner/medical/QoL adapters, evidence-backed only — **Design** (per-row)

### 3. Gate and portals [RR-GATE]
- Native provider designation: Core `Door`/`Autodoor` gate, `CommsConsole` station, `TableMachining` assembly bench, `Battery` reserve (17 keyed refusal reasons) — **Build / Runtime-pending**
- Assembly via native bill (100 Steel + 8 Components), calibration job, assigned operator, actual battery debit verified before/after, fault + acknowledge — **Build / Runtime-pending**
- Opening/recovery receipts, emergency cutoff, interrupted-debit recovery, legacy gate objects hidden from construction — **Build / Runtime-pending**
- Portal-session ownership on the gate (`BeginPortalOpening` / `ClosePortalOpening` / `RecoverPortalOpening`, post-load owner validation) — **Build / Runtime-pending**
- Saved portal/endpoint graph, Laboratory vs Natural kinds, idempotent registration, collision refusal — **Build / Runtime-pending**
- Resumable bidirectional route search (budget ≤ 1024 ops/advance, loop detection, `Pending|Complete|Unreachable|Invalidated|InvalidState`) — **Build / Runtime-pending**
- Same-pawn/same-cargo crossing service with receipts, post-spawn door/area checks, rollback, recovery (max 256 pending) — **Build / Runtime-pending**
- Derived laboratory and natural address registration, deterministic discovered-coordinate API, explicit legacy threshold repair — **Build / Runtime-pending** (0.4.2-dev)
- Discovery of further natural gates in play: a colonist surveys a doorway deeper in and records a permanently open way onward, deterministic per doorway position under the coordinate's own saved seed so a revisit never rerolls it, capped at two per coordinate — **Build / Runtime-pending** (0.5.1-dev)
- Ordinary crossing job, per-address crossing orders, laboratory open/close wiring, emergency-return route, unresolved-crossing reconcile surface — **Build / Runtime-pending** (0.4.2-dev)
- Gate traversal policy: inhabitants and monstrosities never cross on their own, an open gate is never an objective/lure/spawn target/raid route/attack trigger, and anything else rides only in a carrier's hands (downed, dead or imprisoned passengers included) — **Build / Runtime-pending** (0.4.3-dev)
- Gradual, saved, bounded escalation of what a space presents (quiet start, saved causes only, caps per opening and per coordinate, required quiet stretches, no summing across gates) — **Built** (0.8.0-dev, the escalation ladder; its specification moved to `TODO.md` when `DEFERRED.md` was closed)
- Saved cross-map work intents, bounded expiring planning leases and definitive native destination revalidation — **Build / Runtime-pending** (0.5.0-dev)
- Cross-gate storage hauling in both directions: real pickup under native reservation, real carry under native mass and stack limits, native placement into storage the destination's own settings accept — **Build / Runtime-pending** (0.5.0-dev). Cell destinations only; container and provider destinations are **Design**.
- Cross-gate rescue of our own downed people to a bed, and cross-gate recovery of remains to a grave or storage — **Build / Runtime-pending** (0.5.2-dev). Capture is a player order by design, not automatic work.
- Cross-gate construction supply: real material carried into a real frame or blueprint, using the site's own requirement and Core's own container and construct toils — **Build / Runtime-pending** (0.5.3-dev)
- Cross-gate construction finishing: a builder travels through a gate to finish a frame that already has its material, and Core's own giver does the building on arrival; the worker is never walked home — **Build / Runtime-pending** (0.5.5-dev)
- Travel-to-work deployments as a reusable shape for any work done at the far site with nothing carried (research and stationary work are the next providers) — **Build / Runtime-pending** (0.5.5-dev)
- Adapters for bills and unfinished work, research, tending across a gate, food, rest and all remaining work families — **Design** (resume step 4, one at a time with source evidence per route)
- Travel-to-work intents, for work done at the far site with nothing carried (construction *finishing* and similar) — **Design** (a new intent shape, not another adapter)
- Upgrades: stabilizers, monitoring, cool-down, modules, reliability; aperture/duration/recall/efficiency; larger door providers (Doors Expanded 2×1/3×1/3×2, ReBuild, VVE garage) — **Design**
- Gate window ladder 20 min → 2 h → 1 day → 7 days → 30 days with power/heat/maintenance/supply/rotation/comms costs — **Design**
- Native recolor (`Building.ChangePaint`) with original paint restored; Core `HeatGlow` aura with disable/reduced-motion guards — **Build** (aura) / **Design** (paint)
- Legacy gate/console/cutoff/generator migration or declared dev-save break — **Design** (shared with content replacement)

### 4. Expedition and recovery [RR-EXP, RR-THREAT]
- Dispatch with crew + cargo manifest, approach job, transfer of the original pawns/things, recall, relief, casualty return, abandonment/resume, cargo declarations, closure records, interrupted-transfer recovery — **Build / Runtime-pending**
- First-slice site bookkeeping: six numbered tags, return beacon, Borrowed Corridor mismatch (3-minute cost, no injury), Quiet Pursuer (2 rooms away, +1 room per 2 min, max 3, one recoverable strike) — **Build / Runtime-pending**
- Ordinary crossing without manifests; expedition planner becomes optional mission UI — **Design** (connected-colony contract)
- Crew/cargo planner with skill/health/weight/window checks and cost preview — **Design**
- Schedule, warning (10/5/2), recall, evacuation, emergency close, lost-connection, failed return, rescue workflows — **Design**
- Fog-of-war atlas (unexplored/seen/surveyed/visited/blocked/last-known-changed), route notes, last-known position, return beacon, saved room graph, revisit changes — **Design**
- Field gear effects on detection/safety/information/cargo/route/return, bound to existing objects with saved roles — **Design** (content-reuse rule; no new item Defs)
- Entity/anomaly sheets for the six frozen families; five named sketches — **Design** / **Deferred** (S1/B)
- Containment rooms, prisoner/witness interviews, debrief, quarantine, alarm/escape response, case records — **Design**

### 5. Generation and procedural space [RR-SPACE]
- Stable coordinate + seed + generator/room-library versions; one finite persisted site per coordinate; `AI-01` = `<branch>:coordinate:000001` — **Build / Runtime-pending**
- Bounded 6–8 furnished-room layout, deterministic candidates, fallback, native doors/fog; Core lamp/heater/floors/chemfuel generator/conduit (content v3); Core steel-door threshold (content v4); versions 0–3 readable — **Build / Runtime-pending**
- Failed-site `:fallback:1` replacement (AI-01R, six rooms, cap 1 failed + 1 replacement) — **Build / Runtime-pending**
- Tagged room/corridor library (Shape/Connections/Use/Mood/Play/Story/Modifiers) across nine families and four size bands — **Design**
- Seven-step generation order with preflight, retry cap, reserved return route, no consumption during preflight — **Design** (partially embodied by the 6–8 planner)
- Bounded non-Euclidean effects; rule-based anomaly propagation with clues, caps, decay, event log — **Design**
- Equipment/research changing what is detected or generated without breaking seed reproducibility — **Design**
- Map state versioning, archival, generator upgrades, explicit migration, recovery when an old site cannot load — **Design**
- Coordinate/complexity persistence, procedural inhabitants in native states, rare monstrosities, evolving saved events — **Design** (connected-colony contract)
- Connected-site scheduling/streaming within measured budgets — **Design** / **Blocked** (measurement needs owner launch)

### 6. Investigation, evidence and research [RR-EVD]
- Designated native research bench as company laboratory, native speed factor preserved — **Build / Runtime-pending**
- Evidence as a real Core `TextBook` with once-only creation, saved custody, same-object recovery — **Build / Runtime-pending**
- Route evidence/aid comps, deploy job, analysis job (3000 work), frozen reports, once-only settlement, one research insight — **Build / Runtime-pending**
- `RR_GateTelemetry` insight-gated company project (`RimroomsProjectDef`) — **Build / Runtime-pending**
- Evidence types (route maps/tags, radio fragments, recordings/transcripts, instrument readings, room photographs, samples, entity traces, recovered furniture/equipment, witness accounts) with provenance/custody/value/risk/confidence — **Design**
- Analyze/interview/compare/review workflows; missing-person mysteries; sale/study/contain/release/recruit/detain/transfer choices with consequences — **Design**
- Research tiers T0–T6 and nine branches with IDs, gates, evidence prerequisites, dossier output, DLC-absent fallback — **Design**
- Research Dossier as an existing physical document object for RWT exchange — **Design** (release gate)

### 7. World, incidents and outposts [RR-MSN, RR-OUT]
- Onboarding route survey mission — **Build / Runtime-pending**
- Twelve further mission families (repeat survey, salvage, sample delivery, missing crew, reappearance/death, entity contract, settlement opening, commercial/lease, outpost ops, internal incident, ground transport, orbital support) with bounded seeded variation — **Design**
- Settlement anomaly openings as timed quests (perimeter, rescue, evidence, witnesses, close/stabilize) — **Design**
- Outpost ladder: relay/cache → field shelter → guarded station → leased space → site network → ground transport → orbital layer → deep-site access; supply/comms/defense/evacuation/abandonment — **Design**
- Vehicles and space travel as logistics branches; VGE Chapter 1 logistics link; Chapter 2 orbital security/salvage hooks — **Design** (optional)

### 8. Interface and presentation [RR-UI, RR-STYLE]
- Operations main tab: ten panes (company, personnel, procurement, facilities, dispatch/expedition/manifest/machine, evidence, evidence recovery, native gate binding, laboratory binding) + four dialogs; keyed English; `CompanyActionResult` surfacing — **Build / Runtime-pending**
- Original menu slideshow: two 1672×941 images, 30 s dwell, 2 s fade, reduced-motion still, disable, native fallback, yields to third-party backgrounds, dynamic title + version at x=350 — **Build / Runtime-pending**
- Cosmetic portal aura; optional Core-sound cues with mute/volume — **Build / Runtime-pending**
- Eleven-pane Company Command with deep links, reason codes, previews, undo/recovery, empty/loading/error states — **Design** (Phase 5)
- Native menu/tab remap preserving Architect/Work/Assign/Research/World/map/pawn actions — **Design**
- Tutorial (six sections, seven-step teaching order, seven verbatim refusal messages), glossary, keyboard/controller paths, contrast/scale, localization — **Design**
- Accessibility: no color/audio/flash-only cues, persistent logs, reduced-effect settings, long-string locale, mouse-free routes — **Design** (acceptance rows)
- Additional menu images per shipped scenario with provenance — **Design**

### 9. Build, package, tooling
- Locked restore + deterministic warnings-as-errors compile against pinned Core hash — **Build**
- Explicit 71-file allowlist, XML well-formedness, source/package/reference manifests — **Build**
- RimSort Local Mods staging with hash verification, backup, refuse-while-running — **Build**
- Preview card renderer; Gate 0 audit; pinned-target audit (307 hashes, 294 rows, 0 issues); installed-metadata audit — **Build**
- Owner-operated read-only RimBridgeServer client (explicit PID, 512-entry array limit) — **Build / Blocked** (attach after owner launch)
- Opt-in diagnostics counters (16 × 2,048) and Player.log identity dump — **Build** (no sample collected)
- Cascade publication procedure — **Build** (`PUBLISHING.md`)

### 10. Compatibility [RR-MP, RR-DLC, RR-SPACEFLIGHT, RR-COMPAT]
- Core-only solo campaign — **Build / Runtime-pending**
- RWT feature detection, setup diagnostics, unavailable states; no custom server schema — **Design**
- RWT verification: visits, transfer spot, aid, gifts, trading, dossier transfer, reconnect, server restart — **Blocked** (owner two-client run)
- Five DLC conditional layers via isolated LoadFolders + guarded patches — **Design**
- VGE Chapter 1/2 clean-stack chain and narrow link — **Design** / **Blocked**
- 294-row six-tier disposition closure and compatibility report — **Design** / **Blocked**

---

## By Complexity

### Beginner (Learn First)
> What a new contributor must understand before touching anything

- The two-layer doc map and authority order (`HOWTO.md`, `AGENTS.md`)
- `CompanyActionResult` and the "UI reads, services mutate" rule
- `rr_` save keys, `RR_` Def/keyed prefixes, integer schema per owner, receipt idempotency
- `tools/build.ps1` / `stage-mod.ps1` and the package allowlist
- Existing-content-only rule and the connected-colony contract
- The three entry counts: 294 / 295 / 296

### Intermediate (Build On Basics)
> Requires beginner skills, enables day-to-day feature work

- Adding a keyed string + DefInjected entry and wiring it through a pane
- Adding a bounded record type under an existing owner with schema bump + forward-only migration
- Native provider binding via guarded XML patch + explicit designation
- Writing a task record → source review → implementation record → build record with evidence folder
- Job/WorkGiver pairs that target the originals (`JobDriver_CompanyLaboratory`, `WorkGiver_RRCalibrateGate`)
- Economy quote rules: saved amounts, advances, capped penalties, once-only posting

### Advanced (Deep Knowledge)
> Complex implementations, cross-owner coordination

- Same-object transfer across maps: despawn → nonmerging carry transfer → spawn → post-spawn checks → rollback
- Deterministic bounded generation with content-version gating, preflight and fallback
- Receipt idempotency across gate debits, portal sessions, deliveries, crossings, evidence creation
- Legacy vs native gate coexistence and the migration/dev-save-break decision
- Scenario setup ordering with Prepare Carefully present and absent
- Threat authoring against the 11-field sheet template

### Expert (Mastery Required)
> System design, cross-map semantics, optional-mod interoperability

- Cross-map job discovery, leases and adapters preserving native priorities, schedules, areas, locks, custody (`LocalTargetInfo` has no map; `CanReserve` rejects cross-map; `Global` scanners still use the current map)
- Streaming/scheduling of connected sites within the benchmark budgets
- RWT adapter design without a supported client extension API
- Procedural inhabitants/monstrosities from native state transitions only, DLC/mod-aware
- 294-row provider integration one family at a time with source and runtime evidence

---

## By Dependency (Skill Tree Visualization)

```
[Build + package pipeline] ──► [Core-only solo campaign] ──► [Async Industries start]
                                      │
        ┌─────────────────────────────┼──────────────────────────────┐
        ▼                             ▼                              ▼
[Company ledger/staff]      [Native gate binding]           [Finite seeded site (v4)]
        │                             │                              │
        ▼                             ▼                              ▼
[Personnel + Procurement]   [Portal graph + session]  ◄─── [Endpoint registration + legacy repair]
        │                             │                              │
        ▼                             ▼                              │
[Facilities report]         [Crossing service] ──────────────────────┘
        │                             │
        │                             ▼
        │                 [Crossing jobs + player controls]  ◄── [Keyed portal text]
        │                             │
        │                             ▼
        │                 [Work intents + leases + revalidation]
        │                             │
        │     ┌───────────────────────┼───────────────────────┐
        │     ▼                       ▼                       ▼
        │ [Hauling/construction]  [Bills/research]   [Medical/food/bed needs]
        │     └───────────────────────┼───────────────────────┘
        │                             ▼
        │            [Optional provider adapters + scenario openings (Store, Lone Survivor*)]
        │                             │
        ▼                             ▼
[Room functions · training · applicant pools]   [Room library · propagation · inhabitants · complexity]
        │                             │
        └──────────────┬──────────────┘
                       ▼
     [Contracts/leases · evidence breadth · research tiers · containment · settlement quests · outposts]
                       │
                       ▼
     [RWT adapter · DLC layers · 294 closure]  ──►  [Company Command · tutorial · accessibility · slideshow]
                       │
                       ▼
     [Validation · balance · performance · release report]  ◄── [Owner-launched acceptance (Gate 2 → release)]
```

Parallel branches that do not depend on the portal chain: existing-content replacement (needs the migration decision shared with legacy repair); menu image additions; RWT/DLC source-side guards; Company Command pane structure. Every runtime row converges on the owner's first RimSort launch.

### Skill Unlock Paths

- **Portal chain (active major M1):** boundary review → registration + legacy repair → crossing jobs + controls → intents/leases → adapters → providers + inhabitants → streaming. Steps 1–3 decomposed in `DECOMPOSED.md`.
- **Content replacement (M2):** replacement-map rows → provider choice per role → migration or declared break → allowlist cleanup → historical evidence retained.
- **Company breadth (M3):** room functions → training/pools/wellbeing → contracts/leases/evidence → research tiers → containment/settlement quests → outposts → vehicles/VGE.
- **Alternate starts (M3):** shared start contract → Store setup/grant/objective → inside start after the two owner answers.
- **Compatibility (M4):** feature detection + guards now → owner two-client run → per-row closure → report.
- **Release (M5–M6):** Company Command → tutorial/accessibility → M6a validation and mod page → M6b balance/performance/acceptance → Workshop. **D1 changed 2026-09-29:** public Workshop is the first distribution target, so the private RWT prototype is no longer a gate. Compatibility claims still wait on recorded results.

---

## By Priority

### Critical (Must Have)
> Required for the owner's binding requirements to be true in play

| Skill | Domain | Complexity | Status |
|-------|--------|------------|--------|
| Crossing-service boundary review before callers | Gate/Portals | Advanced | **Done** (step 1, 2026-09-28) |
| Endpoint/address registration + legacy endpoint repair | Gate/Portals | Advanced | **Build / Runtime-pending** (step 2, 0.4.2-dev) |
| Ordinary crossing jobs + player controls + emergency return | Gate/Portals | Advanced | **Build / Runtime-pending** (step 3, 0.4.2-dev) |
| Cross-map work intents, leases, revalidation | Gate/Portals | Expert | Design (step 4) |
| Work/needs adapters preserving native rules | Gate/Portals | Expert | Design (step 4) |
| Permanent natural portals with discovery | Gate/Portals | Intermediate | Registration **Build**; discovery trigger **Design** (step 5) |
| Inhabitants stay in the Backrooms unless carried | Gate/Portals | Intermediate | **Build / Runtime-pending** (0.4.3-dev) |
| Cross-gate work intents and planning leases | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.0-dev) |
| Cross-gate storage hauling, both directions | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.0-dev) |
| Cross-gate delivery into storage containers | Gate/Portals | Intermediate | **Build / Runtime-pending** (0.5.1-dev) |
| Observed remote allowed-area preflight | Gate/Portals | Intermediate | **Build / Runtime-pending** (0.5.1-dev) |
| Natural gate discovery by survey | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.1-dev) |
| Cross-gate casualty rescue to a bed | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.2-dev) |
| Cross-gate recovery of remains | Gate/Portals | Intermediate | **Build / Runtime-pending** (0.5.2-dev) |
| Cross-gate construction supply | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.3-dev) |
| Cross-gate construction finishing (travel-to-work) | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.5-dev) |
| Cross-gate bill ingredient logistics | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.7-dev) |
| Cross-gate research (second travel-to-work provider) | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.8-dev) |
| Cross-gate tending: doctor travels to a patient who stays put | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.9-dev) |
| Cross-gate medicine supply (cargo consumed by the work) | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.9-dev) |
| Cross-gate food supply, with last-meal and own-people guards | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.0-dev) |
| Cross-gate patient feeding (fourth travel-to-work provider) | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.0-dev) |
| Cross-gate rescue in place: bed a casualty where they lie | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.1-dev) |
| Cross-gate upkeep: cleaning, repair, firefighting (Home-area scoped) | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.2-dev) |
| Cross-gate fieldwork: mining, hunting, plant cutting, growing zones | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.2-dev) |
| Cross-gate fuel and turret rearming (one family) | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.2-dev) |
| Ways onward findable on ordinary world maps, never in a player-built door | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.3-dev) |
| Backrooms containment: no outside, roof never removable, interior fully strippable | Generation | Advanced | **Build / Runtime-pending** (0.6.4-dev) |
| Cross-gate wardening, childcare and animal handling | Gate/Portals | Advanced | **Build / Runtime-pending** (0.6.4-dev) |
| Live-tunable cross-gate work priorities in mod settings | Interface | Foundational | **Build / Runtime-pending** (0.5.6-dev) |
| Verified RimWorld/Steam compliance position with automated checks | Release | Foundational | **Build** (0.5.6-dev) |
| Travel-to-work deployment shape, reusable per provider | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.5-dev) |
| Audited zero-hard-dependency position | Compatibility | Foundational | **Build / Verified** (0.5.3-dev) |
| Laboratory gate duration ladder to indefinite | Gate/Portals | Advanced | **Build / Runtime-pending** (0.5.4-dev). Top of the ladder needs M3's research tree. |
| Player-named company, renameable in play | Company | Foundational | **Build / Runtime-pending** (0.5.4-dev) |
| Gradual bounded escalation of far-side pressure | Generation | Expert | **Built** (0.8.0-dev; spec moved to `TODO.md`, `DEFERRED.md` is closed) |
| Existing-content replacement of legacy gate/gear/fixtures/terrain/threat/PawnKinds | Company/Gate/Generation | Advanced | Design (M2) |
| Keyed text for portal failure keys | Interface | Beginner | **Build** (`RR_Portals.xml`, 0.4.2-dev) |

### Important (Should Have)
> Significantly improves the campaign or closes documented gaps

| Skill | Domain | Complexity | Status |
|-------|--------|------------|--------|
| Procedural inhabitants / monstrosities / evolving events / complexity | Generation | Expert | Design |
| Room template library, bands 8–48, propagation, archival | Generation | Advanced | Design |
| Store start; inside start (after owner answers) | Scenario | Advanced | Design / Blocked |
| Room functions, training, certification, applicant pools, wellbeing | Company | Intermediate | Design |
| Contract/quest families (13), leases, shipment incidents | Company/World | Advanced | Design |
| Research tiers T0–T6 + nine branches; entity family sheets | Investigation | Advanced | Design |
| Containment, interviews, settlement openings, outposts | World | Advanced | Design |
| Company Command (11 panes) + deep links + alerts | Interface | Advanced | Design |
| Gate upgrades and window ladder | Gate | Advanced | Design |

### Nice-to-Have (Could Have)
> Polish and later-campaign depth

| Skill | Domain | Complexity | Status |
|-------|--------|------------|--------|
| Procurement component split into partials | Company | Intermediate | Not started |
| Receipt-history compaction policy everywhere | Company/Gate/Portals | Intermediate | Not started |
| Diagnostics measurements + benchmark budgets | Presentation/Core | Intermediate | Blocked (owner launch) |
| Additional menu images reflecting shipped features | Presentation | Beginner | Design |
| Tutorial/help glossary/accessibility options | Interface | Intermediate | Design (Phase 5) |
| Vehicles / VGE Chapter 1–2 links | World | Advanced | Design (optional) |

### Future (Won't Have Now)
> Planned for Phase 4+ or explicitly deferred by owner decision

| Skill | Domain | Complexity | Status |
|-------|--------|------------|--------|
| RWT adapter verification, dossier transfer, visits | Compatibility | Expert | Blocked (two-client run) |
| Five DLC layers verified present/absent | Compatibility | Advanced | Design / Blocked |
| 294-row profile runtime closure | Compatibility | Expert | Blocked |
| Five named later-threat sketches | Threats | Advanced | Deferred (S1/B) |
| Outpost, town-distortion, company-crisis starts | Scenario | Advanced | Deferred until design briefs exist |
| Public Workshop release | Release | — | **First distribution target (D1 changed 2026-09-29).** Waits on M6a and the Core-only solo path passing, not on a private RWT prototype |

---

## Skill Details

### Same-object portal crossing

| Attribute | Value |
|-----------|-------|
| **Domain** | Gate/Portals |
| **Complexity** | Advanced |
| **Priority** | Critical (foundation for every portal skill above it) |
| **Prerequisites** | Registered edge; pawn at saved source threshold; laboratory window or natural kind available |
| **Unlocks** | Crossing jobs, work intents, adapters |
| **Status** | Build / Runtime-pending — receipt-backed and reachable through `RR_CrossPortal` since 0.4.2-dev |

**Description:** `RimroomsPortalCrossingService.Cross(pawn, step, operationId)` executes one graph step with the original `Pawn` and its actual carry stack. It checks branch/map ownership, graph availability, eligibility (player-faction humanlike colonists only), source door/cell permission and destination spawn safety; secures the carry stack with a nonmerging transfer; despawns; rechecks availability; spawns the same object at the saved approach cell; then checks destination door permission and the destination map's allowed area, rolling back to the source cell on denial. `Recover(operationId)` reconciles an interrupted receipt using only the saved endpoints.

**Implementation Notes:** at most 256 unresolved crossings; receipts retained for idempotency; no cloning, Def-based reconstruction, job creation, remote stock access or receipt deletion. Failure keys need `Keyed/` entries. Mechs, subhumans and optional-provider doors are explicitly unsupported.

**Files Involved:** `src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs`, `PortalCrossingRecords.cs`, `RimroomsPortalNetwork.cs`, `PortalRouteSearch.cs`; review basis `docs/implementation/CONNECTED_CROSSING_IMPLEMENTATION.md`, `CONNECTED_WORK_CORE_API.md`.

### Native gate binding

| Attribute | Value |
|-----------|-------|
| **Domain** | Gate |
| **Complexity** | Advanced |
| **Priority** | Critical (this is how the content-reuse rule is satisfied for the machine) |
| **Prerequisites** | Guarded XML patches on Core `Door`/`Autodoor`/`CommsConsole`/`TableMachining`; player designation in Operations |
| **Unlocks** | Assembly bill, calibration, operator, battery reserve, portal sessions |
| **Status** | Build / Runtime-pending |

**Description:** dormant `CompProperties_RimroomsGate{Console}` comps are patched onto existing Core things and activated only by explicit designation. Assembly consumes 100 Steel + 8 ComponentIndustrial through a native bill; energy is withdrawn from the actual linked `Battery` (833 ticks at 3,500 W ≈ 48.59 Wd; readiness ≈ 49.59; recovery ≈ 50.59) and verified by observed before/after; a mismatch saves a fault that halts native payments until acknowledged (never refunded). Legacy custom gate buildings are hidden from new construction but remain loadable.

**Implementation Notes:** two opening paths coexist (`BeginOpening` for expeditions, `BeginPortalOpening` for portal sessions) sharing one physical timer/energy owner. Native `DoorPreDraw` rotation was handled so drawing cannot retarget an approach cell. Never write `PowerOutput` on the threshold trader; a shared power net reserves nothing.

**Files Involved:** `src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs`, `NativeGateBinding.cs`, `PortalGateOpening.cs`, `CompRimroomsGateConsole.cs`; `Mod/.../1.6/Patches/RR_NativeGateProviders.xml`; records `docs/implementation/PHASE_3_NATIVE_GATE_IMPLEMENTATION.md`, `PHASE_3_NATIVE_GATE_UI.md`, `NATIVE_GATE_MIGRATION_IMPACT.md`.

### Finite seeded destination (content version 4)

| Attribute | Value |
|-----------|-------|
| **Domain** | Generation |
| **Complexity** | Advanced |
| **Priority** | Critical (every portal endpoint is one of these) |
| **Prerequisites** | Coordinate record on the campaign component; gate opening |
| **Unlocks** | Endpoint registration, revisit persistence, procedural growth |
| **Status** | Build / Runtime-pending |

**Description:** `DestinationService.EnsureSite` creates or retrieves one persisted site per coordinate as a `RimroomsDestinationMapParent`; `GenStep_BackroomsDestination` builds a 6–8 room graph from deterministic candidates with a fallback; version 4 uses a real Core steel `Door` as the return threshold while versions 0–3 keep `RR_ReturnAnchor` readable. Rooms use Core `StandingLamp`, `Heater`, `PavedTile`/`Concrete`/`MetalTile`, a `ChemfuelPoweredGenerator` with `Chemfuel` and `HiddenConduit` (demand ≤ 475 W, ≈ 6.67 fuel-days, caps 512 conduit cells / 16 fuel stacks).

**Implementation Notes:** no visited map is ever rebuilt or retargeted; failed-site recovery readdresses a pristine initial survey (`:fallback:1`, AI-01R) instead of regenerating. Legacy-anchor sites need the explicit repair route resume step 2 calls for.

**Files Involved:** `src/RimroomsAsyncIndustries/Generation/*`; `Mod/.../1.6/Defs/MapGeneratorDefs/RR_BackroomsGeneration.xml`, `WorldObjectDefs/RR_BackroomsSites.xml`; records `docs/implementation/PHASE_3_ROOM_PROVIDER_REUSE.md`, `PHASE_2_GENERATION_RECOVERY.md`.

### Cross-map work adapters (the owner's "one colony")

| Attribute | Value |
|-----------|-------|
| **Domain** | Gate/Portals → Company |
| **Complexity** | Expert |
| **Priority** | Critical |
| **Prerequisites** | Crossing jobs, registered edges, work intents/leases |
| **Unlocks** | Every Phase 3 breadth item being meaningful across maps |
| **Status** | Design (resume step 4) |

**Description:** a Rimrooms lease (map + Thing/load ID + quantity + endpoint + final target; bounded, expiring, excludes nobody) plus a carry-preserving dedicated transit job (`carryThingAfterJob=true`, `dropThingBeforeJob=false`) that crosses the same pawn and reacquires native reservations on the destination. Adapter order: storage hauling (`WorkGiver_Haul`, `StoreUtility.TryFindBestBetterStorageFor` use the carrier's map), construction supply/finish, bills (`WorkGiver_DoBill.JobOnThing`, never `Notify_IterationCompleted` remotely), research, tend/rescue (`RestUtility` rejects off-map beds), food, rest, then the remaining families and every installed profile work giver.

**Implementation Notes:** Architecture A (Core-only staged adapters via XML-inserted WorkGiver/ThinkNode + JobDefs) recommended; Harmony not intrinsically required; automatic work never `playerForced`; native recovery guards fire on excessive `StartJob`. Provider absence must yield a Core-only base path.

**Files Involved (as built):** `Portals/JobDriver_CrossPortal.cs`, `ConnectedWork/ConnectedWorkRecords.cs`, `ConnectedWork/RimroomsConnectedWorkComponent.cs`, `ConnectedWork/Adapters/*`, and for travel-to-work `ConnectedWork/ConnectedDeploymentRecords.cs`, `ConnectedDeploymentProvider.cs`, `Providers/*`, `WorkGiver_ConnectedDeployment.cs`, `ConnectedCrossing.cs`; review basis `docs/implementation/CONNECTED_WORK_CORE_API.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md`.

---

## Learning Path Recommendations

### For New Contributors

1. `HOWTO.md` → `AGENTS.md` → `ARCHITECTURE.md` Part A (as-built) then Part B (design map) → `TECHNICAL_ARCHITECTURE.md`.
2. Read `Company/CompanyActionResult.cs` and one small service (`Personnel/HiringServices.cs`) to learn the mutation pattern.
3. Read one pane (`UI/OperationsPersonnel.cs`) to see how UI stays a sink.
4. Run `./tools/build.ps1` once to confirm the pinned Core hash and the allowlist on your machine. Do not stage or launch.

### For Feature Development

1. Find the feature ID in `FEATURE_TRACEABILITY.md`; read its canonical contract and the exact source review under `docs/implementation/`.
2. Write the task record with the required fields from `REGRESSION_CONTAINMENT.md`; list callers and saved fields before editing.
3. Prefer a native provider + explicit designation over any new Def. If a new record type is needed, bump the owner's schema and add a forward-only migration.
4. Keyed text first, then code, then the pane. Compile with `-NoRestore`, save evidence at checkpoint time, tick the bounded master TODO subitem, mirror it in `TODO.md`, archive in `FINALIZED.md`.

### For Architecture Work

1. Read all five `Portals/` files and `Gate/PortalGateOpening.cs` in full, then `CONNECTED_WORK_CORE_API.md` and `CONNECTED_PORTAL_STATE_MIGRATION.md`.
2. Map every place that touches `ExpeditionComponent.Dispatch` / `gate.BeginOpening` — those are the callers the unified network must eventually supersede without deleting.
3. Decide the legacy-endpoint repair route and the legacy-gate migration/dev-save-break together; they share saved keys.

---

## Skill Gap Analysis

### Currently Missing

- Any runtime observation of any Rimrooms build (owner has not launched).
- Cross-map work adapters, the natural-discovery trigger, procedural inhabitants, streaming.
- `Compatibility/` and `ConnectedWork/` folders; RWT/DLC/profile adapters.
- Store and inside starts; training/certification/pools/wellbeing; contract families; research tiers; containment; settlement quests; outposts; Company Command remap; tutorial/accessibility layers.

### Partially Implemented

- Existing-content replacement: evidence book, laboratory bench, audio, native gate infrastructure, native room providers and the v4 threshold replaced; gate objects, field gear, fixtures, terrain, threat presentation, staff PawnKinds, recipes still custom.
- Scenario setup: Async Industries start complete in source; customized-pawn preservation ordered but runtime-unverified; alternate starts absent.
- Connected colony: graph, session ownership, route search, crossing, addresses, legacy repair, crossing job and controls are built (0.4.2-dev); cross-map work, discovery trigger, inhabitants and streaming are not.
- Economy: ledger, payroll, one contract, procurement flow exist; stages 2–7, leases, incidents, balance absent.

### Fully Implemented (in source and package; runtime pending)

- Build/package/staging pipeline with manifests and pinned references.
- Campaign ledger, payroll, contracts, cases, evidence records, projects, company events.
- Personnel hiring flow; procurement flow; facilities report.
- Native gate binding, assembly bill, calibration, operator, battery debit, recovery receipts.
- Expedition dispatch/recall/relief/closure/cargo declaration; first-slice site threats.
- Finite seeded site generation (content v4) with native rooms and Core door threshold; failed-site replacement.
- Laboratory binding, TextBook evidence, analysis reports, once-only settlement, Gate Telemetry project.
- Operations tab (ten panes, four dialogs); menu slideshow with settings and dynamic title/version; opt-in diagnostics.
