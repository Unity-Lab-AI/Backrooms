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

## Required implementation backlog

- [ ] Save a portal/endpoint graph independent of expedition records, with distinct laboratory and permanent-natural lifetimes.
- [ ] Implement bidirectional free pawn movement, persistent crossing receipts and stable return endpoints.
- [ ] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions.
- [ ] Implement actual cross-portal hauling, construction ingredients, bills/production, research and care/needs access; list each supported native work route with source/acceptance evidence.
- [ ] Reconcile jobs and original cargo on closure/reopen, blocked endpoints, death, save/load and interrupted crossing without duplicating consumption or objects.
- [ ] Integrate relevant profile work/storage/hauling providers; account for all 294 rows without asserting universal support from a successful load.
- [ ] Replace dispatch-only ordinary travel controls and scenario prerequisites; keep optional missions distinct from connection ownership.
- [ ] Persist coordinate/seed/version/site/complexity and generated inhabitants/events; revisit the same saved space without reset.
- [ ] Implement bounded procedural inhabitants/state combinations, rare monstrosities, evolving events and technology-driven complexity families.
- [ ] Implement connected-site scheduling/streaming and measure performance after an owner-launched build.
- [ ] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants.

## Multiplayer boundary

This unified network belongs to a local company branch. The approved RimWorld Together mode remains asynchronous cooperation between separate players' branches. It does not create live shared-map control, pooled remote-player pawn labor or automatic use of another player's storage. Visits/trade and technology exchange keep their separate integration contracts.

## Current implementation limit

The native-provider checkpoint supplies physical door/control/power foundations. The [connected-colony implementation task](implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md) now adds [independent saved graph and laboratory-session source](implementation/CONNECTED_NETWORK_IMPLEMENTATION.md). Historical expedition travel remains preserved; the new APIs still need player controls, automatic crossing and native work/needs adapters. They do **not** yet implement the unified colony behavior above. Complete the full job/path integration before marking portal travel or the full mod complete.

Implementation agents must also read the [pinned Core work API](implementation/CONNECTED_WORK_CORE_API.md), [state migration review](implementation/CONNECTED_PORTAL_STATE_MIGRATION.md) and [profile integration boundaries](implementation/CONNECTED_WORK_PROFILE_BOUNDARIES.md). These distinguish actual source constraints from planned behavior and future runtime acceptance.
