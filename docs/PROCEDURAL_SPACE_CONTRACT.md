# Rimrooms - Async Industries: procedural space contract

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** full-campaign design contract, version 0.1. The [current destination implementation](implementation/PHASE_2_DESTINATION_IMPLEMENTATION.md) records the bounded first-site subset, saved ownership, inspected Core APIs and remaining layout/fallback/capacity work. This contract defines the wider campaign's continuing discovery of finite, saved destinations. Room and event rules are original game design inspired by the selected series and film notes; they are not confirmed canon or runtime proof.

**Feature route:** RR-SPACE, RR-EXP, RR-GATE, RR-MSN, RR-EVD, RR-THREAT, RR-OUT, and RR-STYLE in [FEATURE_TRACEABILITY.md](FEATURE_TRACEABILITY.md). The implementation boundary and local 1.6 research are in [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) and [RimWorld 1.6 generation findings](research/RIMWORLD_1_6_PACKAGE_AND_GENERATION.md). The first site uses the [AI-01 content inventory](FIRST_SLICE_CONTENT_INVENTORY.md), [first playable contract](FIRST_PLAYABLE_CONTRACT.md), and [starter threat sheets](THREAT_DESIGN_SHEETS.md).

**Entry and return routes:** [the scenario/door contract](SCENARIO_SETUP_AND_PORTAL_NETWORK.md) adds distinct configurable starts and physical paired door endpoints. An established portal recalls its saved coordinate/map rather than regenerating it; the proposed inside start begins in a saved Backrooms site before a real-world exit is revealed. Party/first-exit choices remain pending.

## Player-facing promise

The Backrooms feel larger than the company can understand. The game creates that feeling through a growing network of destinations, not one endless map. A player opens a finite site, discovers parts of it, returns to the gate, and can later revisit the same saved place. New coordinates reveal new room families and rule combinations. Earlier places do not silently reroll because the generator or mod list changed.

The player can always distinguish:

- where the crew entered;
- which rooms and routes they have actually seen;
- which landmark or return clue they can follow;
- what changed since their last visit;
- what is still unknown;
- whether a known route home remains usable.

Confusing spaces are allowed. Unreadable or arbitrary progress loss is not the intended challenge.

## Coordinate identity and generation

Each local campaign branch owns its discovered coordinate records and site maps. A coordinate has a stable local ID and generation record. A public name such as AI-01 is a label, not its identity key.

Before a site is first opened, save the inputs that shape it: the branch's campaign seed, coordinate ID, generator version, room-library version, mission type, first-generation equipment and research flags, and the bounded variation choices. The seed is made from stable identifiers, not pawn names, UI ordering, current wall-clock time, or a new random draw on every load.

After generation, the saved site map is authoritative. Returning to the same coordinate restores its rooms, pawn/building/item changes, discoveries, evidence, and event state. New gear or research can make the crew better at noticing or surviving a place; it does not silently create a different map under the same coordinate ID. A new map requires a new coordinate ID.

RWT does not share maps by implication. A traded report may give the recipient a coordinate clue or a physical dossier. The recipient's branch records its own discovery and site state unless a later, explicitly tested visit feature demonstrates something more.

## Room library

Room templates are project-owned content records. Each one describes a small, useful space rather than a complete mission. Templates carry these player-facing and generation tags:

| Tag group | Examples and use |
| --- | --- |
| Shape | compact, long, broad, narrow, open, split, loop-prone; helps create recognizable rooms with deliberate contrasts. |
| Connections | allowed doorway sides, corridor links, dead-end status, and whether the room may be a start, objective, or return space. |
| Use | office, storage, utility, passage, rest point, lab-like space, transit room, shelter, or unknown function. |
| Mood | material family, lighting, furnishing density, sound treatment, age/condition, and readable visual landmark. |
| Play | minimum clear floor, cover, sightlines, hazard locations, and space for pawns, creatures, and required objects. |
| Story | evidence slots, salvage slots, signs of prior use, client or mission relevance, and compatible incidents. |
| Modifiers | the spatial rules that may alter this template and the cues required to explain them. |

A template is optional content until the generator can place it without blocking a required route, objective, return clue, or safe spawn. Third-party furniture or art can inspire a design direction but is not copied into the project; every shipped asset gets its own provenance record.

## Building a destination

A coordinate is assembled as a finite connected room graph and then placed on an ordinary generated map. The graph has room IDs and links that remain stable for that coordinate. It does not exist as an infinite live grid.

Generation follows this order:

1. Choose a bounded room-count band and a mission recipe from the saved coordinate inputs.
2. Select compatible room templates and connect their allowed doorways.
3. Reserve the entry/return room, mission objective, primary evidence, and required route clues.
4. Check the graph and the placed map for a usable path from every required area back to the return point.
5. Add the chosen hazards, salvage, furniture, entity events, and spatial modifiers within their caps.
6. Check that each required object is reachable, nothing blocks the only return, and all start positions are safe.
7. Save the coordinate inputs, final graph, generated map, and event state before opening the gate to the expedition.

If a site fails a check, discard that uncommitted layout and try a bounded alternate layout under the same first-generation input set. If the attempts reach their limit, keep the gate closed, explain the failure, and provide a safe fallback or a newly identified coordinate. Do not consume crew or cargo during preflight and do not quietly regenerate a map after it has been shown to the player.

## Size and complexity

These are initial design bands, not engine limits or tested performance figures:

| Destination type | Candidate room count | Intended use |
| --- | ---: | --- |
| Tutorial and short survey | 6–8 | Teach return clues, one hazard, one evidence chain, and a short objective. |
| Standard expedition | 8–16 | Combine a few familiar room families and one or two known complications. |
| Deep survey or rescue | 16–32 | Support branches, an objective chain, and a longer route plan. |
| Major site or outpost hub | 24–48 | A rare, deliberately staged destination with more than one safe route and a planned relief/resupply route. |

Never allocate every possible coordinate as a map. Generate a destination when the player visits it; store only known coordinate records and maps the campaign actually needs. Campaign discovery can continue through new coordinates while each map and active-site budget stays bounded. Use the named machine, initial budgets and post-build measurement sequence in the [performance benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Measure the candidate upper bands after a build exists and before enabling them for release; do not require a game run during pre-build preparation.

Complexity grows by recombining learned room families and rules, then introducing one unfamiliar change at a time. A routine expedition uses no more than one new major spatial rule and two familiar modifiers. A late-game mission may raise that cap only when its briefing and equipment make the added risks understandable. More rooms do not automatically mean more difficulty or more rewards.

## Spatial changes and propagation

A generated site has an initial layout plus a saved set of documented changes. A change is an event with a cause, clue, affected room/link, start stage, limit, and possible counterplay. Examples include a repeated room, a changed doorway, a route appearing to join the wrong corridor, an object that has moved, or a newly opened branch.

- The first-slice Borrowed Corridor is one bounded route event. It can send the crew back to the last validated junction but cannot erase the exit.
- A later propagation event may spread from a discovered source to an adjacent room or link when its stated trigger occurs. It advances in visible, logged steps, never as an invisible whole-map reroll.
- Each event has a saved maximum reach, number of active effects, duration or ending rule, and a limit on how often it can advance.
- A propagation step cannot close every return route, cover the only required objective, spawn into an occupied pawn, or strand the crew without a warning and recovery option.
- A revisit can show a documented change. Unvisited rooms remain unknown and are not altered solely to surprise the player when they return.
- Effects, clues, and countermeasures use stable IDs and saved state. Reloading the game does not advance an event or reroll its outcome.

The player can learn that a space is changing without being given a complete explanation of why. The system records the cause and rule for simulation and debugging; the UI exposes the evidence the crew could actually observe.

## Discovery and fog of war

At entry, show only the known coordinate signal and the rooms the crew can see or has surveyed. A room becomes mapped through direct observation, a recorder, a beacon, or a later research tool. Each map record distinguishes unexplored, seen, surveyed, visited, blocked, and last-known-changed states.

Room labels and route edges retain their identity after discovery. The player can mark a junction, attach evidence to it, and add a short route note. Unseen connections appear as unknown, not as empty corridors. Reports or transferred dossiers can add a clue but do not reveal another player's saved map.

If a known route is changed, keep its old state in the route history and show the new clue. Do not overwrite the player's note or imply that an undiscovered path is safe.

## Return, loss, and recovery

Every expedition plan names its planned exit, route clues, return reserve, and backup method before dispatch. The first site uses numbered survey tags and a short return tether/beacon. Later gear can extend reliable marking, signal range, or emergency recall.

Before dispatch, a generated site must have a verified path from the entry room to the exit. During play:

- show a warning before a required route changes;
- preserve the last validated path in the expedition record;
- let the crew withdraw, use a known alternate route, place a return marker, or recall when available;
- report cargo or evidence left behind before closing the run;
- if an unexpected map failure prevents travel, stop the dangerous event and use the documented emergency return or recovery quest rather than deleting a pawn or inventing an extraction.

An accident can still injure, separate, or lose a crew if the player accepts the stated risk. A route that becomes impossible without warning or an available recovery path is a generator failure, not intended difficulty.

## Save, revisit, and migration

Save the coordinate ID, seed inputs, generator and room-library versions, mission recipe, room and link IDs, initial layout, player-made changes, known map state, discoveries, active propagation events, objective and evidence links, exit/return information, and last-visit history.

- Normal save/load resumes the same map and event state.
- Visiting an already generated coordinate loads that saved destination; it does not use the current generator to remake it.
- New generator releases apply only to new coordinates by default.
- A migration may add a documented field or map a removed template to a compatible replacement while preserving room IDs, player construction, items, cases, and route history.
- Never silently reroll an old coordinate. If a migration cannot preserve a site safely, keep its old saved data and offer an explicit recovery choice.
- If the saved map cannot load at all, retain the coordinate and case record, create a recovery incident, and do not grant its reward twice.

## First-survey failure recovery in development 0.2.0

The [recovery implementation](implementation/PHASE_2_GENERATION_RECOVERY.md) adds one explicit Atlas action for a geometry-related failure during initial generation, before any visit, expedition, evidence or person reaches that site. It retains the failed map and creates a distinct `:fallback:1` coordinate, labeled AI-01R, with a preflighted six-room layout. The existing unpaid survey contract and empty case point to the replacement. Repeating the same action cannot create another site or reward.

This development slice retains at most one failed site and one usable replacement. A visited site, lost recording, unresolved transfer, missing definition or unknown generation failure is ineligible; its existing records remain available for diagnosis. It does not implement campaign-wide map archival, migration repair or recovery from arbitrary corruption. Those remain later work. Runtime generation, retry and save/reload evidence is pending.

## Acceptance evidence before implementation can rely on it

This contract is design closure only. Later prototypes must record the exact game build, DLC, mod order, RWT build where relevant, generator version, coordinate, save, logs, and observed result for:

| Case | Required result |
| --- | --- |
| Same coordinate and inputs | Same initial graph and objective slots; no extra random draw changes the result. |
| New coordinate | New ID and saved seed; no collision with an earlier branch-local coordinate. |
| Invalid doorway/template set | Preflight refuses or retries within its cap; no crew dispatch or lost stock. |
| Return route check | Every required room is reachable from entry and can route back to the exit. |
| Distortion event | One event follows its saved trigger/cap; its clue and counterplay are visible; the last route is recoverable. |
| Save/load during a run | Room state, active event, crew, cargo, evidence, and time resume without duplication. |
| Revisit after site changes | Player changes and discoveries remain, and a documented event does not reroll unrelated rooms. |
| New generator version | New sites use the new version; old sites keep their map or complete an explicit migration. |
| Large destination | Room, pawn, event, and path checks stay within measured limits on the named test machine. |
| Separate RWT branches | Each branch keeps its own discovered map and changes unless a tested supported visit flow expressly exposes a snapshot. |

Do not mark generation APIs, save behavior, deterministic replay, map revisits, or performance as verified until those runs exist.
