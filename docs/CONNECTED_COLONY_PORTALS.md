# Connected colony portals and procedural inhabitants

**Binding owner clarification, 2026-09-28.** This document supersedes earlier requirements that ordinary portal crossing requires a dispatched expedition, selected crew, cargo manifest or a separate labor/material pool. The full mod scope remains intact. Implementation of the old expedition slice is historical progress, not completion of this requirement.

## One working colony across an open portal

When a laboratory or natural portal is open, its connected spaces function as one local branch's colony for pawn work and resource access. Pawns may move in either direction on their own to perform a job. A builder in the facility can fetch actual materials from Backrooms storage and build on either side; a hauler can deliver to storage or a bill across the portal. There must be no mandatory expedition dispatch or manual cargo-transfer step for routine work.

Unify eligible labor, material search, work orders, hauling, construction, bills/production, research, rescue, medical care, food, beds and other native needs/work routes across reachable endpoints. Preserve native work priorities, schedules, skills, permissions, danger policies, forbidden items, allowed areas, custody and provider restrictions. The final integration must account for affected mod workgivers and storage/hauling behavior in the complete profile; supporting one hauling job is not a claim of unified work support.

Unity here means one connected playable colony, not duplicated inventories or automatic delivery. Actual pawns must travel through actual portal endpoints, carrying actual items with native mass/capacity and live OgreStack limits. Work, ingredients, progress and ownership remain tied to their original objects. No remote instant consumption, cloned pawns/items or separate abstract resource balance may substitute for physical jobs.

Expedition planning may remain an optional mission/crew organization interface. It must not own the existence of an open connection or be the only way to cross. Remove fixed crew-count, operator-as-traveler and cargo-manifest prerequisites from ordinary crossing. Laboratory equipment and staff still govern machine operation under their approved research/power rules.

## Portal lifetime, reachability and failure

- **Laboratory portal:** connected while its supported opening is sustained. Power, equipment, research and upgrades govern its operation, duration and supported complexity. Route discovery and job assignment must observe the actual current connection.
- **Natural mysterious portal:** permanently open. No laboratory fuel cost, expiration timer, expedition completion or return-window rule may close it. A physically blocked doorway can obstruct passage without changing that permanent connection. Do not invent a normal timed shutdown for it.
- Crossing preserves the same pawn and carried objects, with saved source/destination endpoints and a recoverable transfer receipt. Jobs must not reserve or consume the same item on two maps. Save/reload or an interrupted crossing must resume/reconcile the original transfer.
- If a laboratory connection closes, stop creating impossible routes; safely cancel or suspend affected job continuations and release reservations. A pawn already across remains physically there, with its real inventory and local needs/work. Reopening the same coordinate reconnects that colony space. Never teleport everyone home or delete a site to simplify failure handling.
- Natural connections, discovered routes and laboratory address records persist independently of a single mission. Support both directions and connected chains of spaces, with loop detection and bounded searches.

RimWorld's engine can retain separate `Map` instances internally. They must behave as one connected job/material network in the player experience. The engineering task is a cross-map route/reservation/job adapter layer, with valid map-aware targets and native work execution on the destination. Do not claim that renaming two maps as one solves native pathfinding or optional-mod interoperability.

## Coordinates and repeat visits

An address selects a persistent coordinate identity and generation seed/version. The first opening to an undiscovered address generates its space. Reopening a known address returns to the same saved space: layout, player construction, harvested/removed resources, people, corpses, evidence and consequences persist. It must not reset loot, revive a corpse or reroll an unfavorable event. Advancement enables reliable recording/recall and access to more complex coordinates; it does not erase known-site history.

Further doors/frontiers can propagate additional procedural spaces. Use bounded generation and active simulation, with persistent frontier/connection records, rather than preallocating infinity. Active connected job destinations must not be silently unloaded or disconnected to meet a performance budget. Streaming, route eligibility and scheduling need an explicit implementation and later measured acceptance.

## People, monstrosities and increasing complexity

Generate unusual inhabitants and encounters from actual available native/provider mechanics: living people, varied factions/relationships, mental states (including psychotic behavior), catatonic or otherwise incapacitated people, injuries, illnesses, starvation, exhaustion, prisoners, dead pawns/corpses and other supported states. These are procedural content families, not a fixed cast or a requirement that every encounter is hostile. Rare monstrosities remain possible.

Use valid native state transitions and existing pawn/entity presentations. Preserve corpse/pawn identity, relationships, health and custody. Respect DLC/mod availability; never reference absent definitions or create new gameplay assets. Broader named threat sketches remain governed by their recorded owner decisions; this clarification approves the broad dynamic inhabitants/encounter direction without selecting previously deferred names.

Portal complexity and related technological advancement increase the range and intensity of architecture, inhabitants, anomalies, difficulty and random events. Record complexity at discovery with the seed/generator version and encounter provenance. Known spaces evolve through saved events and player actions, not arbitrary whole-map rerolls on each reopening. The combination system must offer coherent playable routes and rare surprises, including quiet stretches, rather than filling every room with an encounter.

## Who may cross, and the pacing of what waits on the other side

**Binding owner clarification, 2026-09-28, verbatim:**

> and something we need is that people and monstrosites further in need to not all run for the gate to exit and or attack when the gate opens or is a natural gate they need to more or less stay in the backrroms and not cross the gate(the machine door) and not crooss natural portals unless a player directly uses game machanics and pawn controls and normal pawn tasks to bring the materials tools equipment resources and such back through the gate, as they can carry pretty much anything they find from furnature to production equipemnet to resources and peoiple and monstrosities all back through the opening but we dont want everything on the backrroms connect portal to rush the gate as soon as it connects things have to get crazier but not all at once, balance to it all

> gate/gate(s)

> company, solo/group, and furnature store starts can all eventual have multiple gates

> gates= machine door = portals in my vocab

**Terminology, owner's vocabulary (authoritative for every Rimrooms document from here on):** **gate**, **gates**, **machine door** and **portal** all mean the same thing — one connection threshold. Where older text distinguishes "the machine gate" from "a portal", read them as the same object. The only distinction that survives is the connection's **kind**: a *laboratory* gate whose connection lives while its supported opening is sustained, and a *natural* gate that is permanently open. Both are gates.

**Scope of the rule: every gate, all of them at once.** It is stated per connection and holds simultaneously for one gate, many gates, and every permanently open natural gate. Opening a second or tenth gate never relaxes it. There is no aggregate exception once several gates, or a chain of connected spaces, are open together.

**All three starts reach multiple gates.** Async Industries, the solo-or-group inside start (`lone_survivor`) and the Furniture & Knickknack Store start can each eventually hold more than one gate. No start is a single-gate design, and no code path may assume one gate per branch, one gate per map, or one gate per coordinate. Consequences already carried by the source: the saved graph is a list of independent connections, a single laboratory machine may remember several addresses while only its current opening activates one, and each connection's availability is evaluated on its own. Consequences for later work: work scheduling, route search, pressure pacing and the interface all have to hold several simultaneous gates per branch without summing them into one number.

### Inhabitants stay in the Backrooms

No pawn that is not this company's own crosses a gate under its own will. That covers generated people in any native state, animals, rare monstrosities, hostile factions, prisoners, wanderers and anything else the far side produces. An open connection is **not** an objective, a lure, a spawn target, a raid route or a trigger. Nothing on the far side may be given a reason, a destination or a permission to move toward a threshold because a gate connected, and nothing may attack through one.

This is not a difficulty setting, a research unlock or an upgrade. There is no path through the design where it flips.

### What does come back, and how

Everything else reaches the near side because one of this company's own pawns physically carried it through, through ordinary game mechanics, pawn controls and normal pawn tasks. That carry can be:

- materials, tools, equipment, resources and any ordinary item stack;
- furniture and production equipment, as actual minified objects;
- corpses and remains;
- **people and monstrosities**, when they are genuinely being carried — downed, dead, or held as prisoners. A person or creature still on its own feet is not cargo; letting it walk through would be traversal, which the rule forbids.

The company's own pawns may cross on their own for work, which is the unified-colony requirement above. That autonomy belongs to this branch's colonists and to nothing else. When the work adapters arrive they inherit exactly this boundary: a colonist may decide to cross to do a job; an inhabitant may never decide anything about a gate.

### Pacing: it gets crazier, not all at once

Pressure on the far side escalates, and it escalates gradually. The following are requirements on generation and activation, not on traversal:

- A newly opened coordinate starts quiet. First contact is bounded and legible, in the spirit of the first-slice starter encounter.
- Escalation is driven by saved, observable causes: how often and how long this company has operated at that coordinate, how deep or complex the space is, what technology and research it has unlocked, and what it has already taken out. It is never driven by wall-clock time, a fresh random draw per load, or the mere fact that a gate is open.
- Escalation is bounded per opening and per coordinate. A cap on how many active encounters, inhabitants and events a space may present at once is part of the contract, and raising the cap is itself a recorded progression step.
- Quiet stretches are required content, not a gap. A space that presents something in every room fails this rule.
- More gates open at once does not multiply pressure on the company. Each coordinate paces on its own record; the design must not sum them into a single escalating number. This holds for every start, each of which can eventually run several gates.
- Reopening a known space resumes its saved state and its saved pressure. It does not reroll upward to punish a revisit, and it does not reset downward to make one safe.

The numeric ladder belongs with the procedural inhabitants work; it must be authored as an explicit, saved, bounded progression before any inhabitant generation ships, and it inherits the threat rules already frozen in [`THREAT_DESIGN_SHEETS.md`](THREAT_DESIGN_SHEETS.md): a readable warning, a learnable rule, at least one countermeasure, and no unavoidable instant failure.

### How the source enforces it

`PortalTraversalPolicy` is the single chokepoint. Every crossing path asks it, and it answers two questions: may this pawn traverse (only this company's available colonists), and may this object ride in a carrier's hands (anything genuinely carried, including a downed, dead or imprisoned passenger). It also exposes `AutonomousNonPlayerTraversalPermitted` as a constant false and `MayApproachThresholdForTraversal` as an unconditional false, so a later work adapter, scheduler, generator or threat cannot reintroduce the behaviour by accident. `RimroomsPortalCrossingService.Cross` calls the policy before it touches custody, and again before the carry transfer.

Separate maps do the rest of the work for free today: RimWorld's own pathing cannot route a pawn between `Map` instances, so nothing on the far side can walk to the near side unless this project deliberately builds that route. This rule is the standing instruction never to build it for anyone but this company's pawns.

## Required implementation backlog

- [ ] Save a portal/endpoint graph independent of expedition records, with distinct laboratory and permanent-natural lifetimes.
- [ ] Implement bidirectional free pawn movement, persistent crossing receipts and stable return endpoints.
- [~] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions. *(0.5.0-dev: discovery, destination targets, bounded route costs, planning leases and real native destination reservations exist, and native priorities/schedules/areas/locks are preserved by riding Core's own work giver path. Proven for the storage-hauling family only; runtime acceptance open.)*
- [~] Implement actual cross-portal hauling, construction ingredients, bills/production, research and care/needs access; list each supported native work route with source/acceptance evidence. *(0.5.0-dev: cross-portal storage hauling in both directions — [work record](implementation/CONNECTED_WORK_IMPLEMENTATION.md). 0.5.2-dev: rescue of our own downed people to a bed and recovery of remains to a grave or storage — [casualties record](implementation/CONNECTED_CASUALTIES_IMPLEMENTATION.md). Construction ingredients, bills/production, research and tending across a gate are NOT implemented and are not claimed.)*
- [ ] Reconcile jobs and original cargo on closure/reopen, blocked endpoints, death, save/load and interrupted crossing without duplicating consumption or objects.
- [ ] Integrate relevant profile work/storage/hauling providers; account for all 294 rows without asserting universal support from a successful load.
- [ ] Replace dispatch-only ordinary travel controls and scenario prerequisites; keep optional missions distinct from connection ownership.
- [~] Persist coordinate/seed/version/site/complexity and generated inhabitants/events; revisit the same saved space without reset. *(0.5.0-dev and earlier persist coordinate identity, seed, generator version and site, and revisit without reset. 0.5.1-dev adds the discovery of further natural gates deeper in, where a doorway's answer is drawn from its own position under that coordinate's saved seed, so a revisit never rerolls where it leads; bounded to two ways onward per coordinate. Generated inhabitants and events are NOT implemented and are not claimed.)*
- [ ] Implement bounded procedural inhabitants/state combinations, rare monstrosities, evolving events and technology-driven complexity families.
- [x] Keep inhabitants and monstrosities in the Backrooms: no non-player pawn crosses any gate on its own, an open gate is never an objective, lure, spawn target, raid route or attack trigger, and anything else returns only carried through by our own pawns, including people and monstrosities that are genuinely downed, dead or imprisoned. Enforced at one chokepoint; see [the rule](#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side) and the [travel record](implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md).
- [ ] Author and implement the saved, bounded escalation ladder: a new coordinate starts quiet; pressure rises only from saved observable causes (operating history at that coordinate, depth and complexity, unlocked technology, what has already been taken out); caps on simultaneous encounters, inhabitants and events per opening and per coordinate, with raising a cap being itself a recorded progression step; quiet stretches as required content; no summing pressure across several open gates; and a revisit that resumes saved pressure without rerolling it up or down.
- [ ] Implement connected-site scheduling/streaming and measure performance after an owner-launched build.
- [ ] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants.

## Multiplayer boundary

This unified network belongs to a local company branch. The approved RimWorld Together mode remains asynchronous cooperation between separate players' branches. It does not create live shared-map control, pooled remote-player pawn labor or automatic use of another player's storage. Visits/trade and technology exchange keep their separate integration contracts.

## Current implementation limit

The native-provider checkpoint supplies physical door/control/power foundations. The [connected-colony implementation task](implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md) now adds [independent saved graph and laboratory-session source](implementation/CONNECTED_NETWORK_IMPLEMENTATION.md). Historical expedition travel remains preserved; the new APIs still need player controls, automatic crossing and native work/needs adapters. They do **not** yet implement the unified colony behavior above. Complete the full job/path integration before marking portal travel or the full mod complete.

Implementation agents must also read the [pinned Core work API](implementation/CONNECTED_WORK_CORE_API.md), [state migration review](implementation/CONNECTED_PORTAL_STATE_MIGRATION.md) and [profile integration boundaries](implementation/CONNECTED_WORK_PROFILE_BOUNDARIES.md). These distinguish actual source constraints from planned behavior and future runtime acceptance.
