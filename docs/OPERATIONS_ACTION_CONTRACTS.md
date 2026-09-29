# Rimrooms - Async Industries: Operations action contracts

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** full-campaign player-facing contract. The [0.2.0 development slice](implementation/PHASE_2_BUILD_RECORD.md) implements Overview, Personnel, Contracts, Ledger, Atlas, Activity, Investigation, Machine and Expedition panes. Actions cover the next opening objective, gate work/operator orders, physical kit pickup, dispatch/recall/rescue, route-aid deployment/recovery, evidence/research, arrears payment, explicit abandonment and auditable cargo declarations. Native Work/Research controls remain available. UI/runtime acceptance is pending; later company actions below remain planned.

**Feature route:** [RR-UI](FEATURE_TRACEABILITY.md), with the owning gameplay rules in [GAME_DESIGN.md](GAME_DESIGN.md), [SCENARIOS.md](SCENARIOS.md), [FIRST_PLAYABLE_CONTRACT.md](FIRST_PLAYABLE_CONTRACT.md), and [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md).

**Planned scenario/door actions:** [the setup and portal-network contract](SCENARIO_SETUP_AND_PORTAL_NETWORK.md) requires preserved pawn customization, company world-site selection, explicit door/equipment binding, connection readiness, choose/dial known coordinate, enter/return, recall and emergency close. These replace historical custom-building actions only after the equivalent native-door state and recovery paths are implemented.

## Interface rule

Operations is the company's overview and shortcut board. It must deep-link to the actual pawn, building, map, item, project, contract, or site that owns the work. Keep vanilla Work, Architect, Assign, Research, World, and pawn controls available. Do not put a second hidden copy of a RimWorld job, item stack, research queue, or map behind the company screen.

Every command shows its required input, expected cost or risk, and the record it changes. If a precondition fails, name the missing person, stock, power, route, permission, or setting and give a useful next step. Irreversible losses need a clear warning and an explicit player action. A panel can report unavailable when its optional DLC, mod, or RWT action is absent; it must not silently pretend the action worked.

## Action map

| Pane and action | Preconditions | Successful result | Refusal or failure message | State owner |
| --- | --- | --- | --- | --- |
| Overview — open an alert or objective | A saved incident, task, or status exists | Opens the owning object and keeps its map/record context | “This record is no longer available” with the last known case or map link | Local branch plus normal pawn/building/map owner |
| Personnel — assign a role or training goal | Pawn is in this branch and available; required skill/work type exists | Updates company assignment and leaves ordinary work priorities accessible | Identifies the unavailable pawn, missing work type, or competing assignment | Pawn for normal needs/skills; branch for company role/training history |
| Facilities — inspect room/security/power status | Facility map is loaded or can be opened | Deep-links to room, building, stockpile, power network, or access point | Reports missing/destroyed building or unavailable map; never fabricates room state | Local map and its buildings |
| Gate — assemble, calibrate, repair | Required blueprint/project, physical stock, worker, and safe access exist | Completes one documented gate step and updates the gate display | Names each missing material, eligible worker, power condition, or required prior step | Gate building plus local branch project record |
| Gate — open, abort, or recall | Gate ready; operator assigned; power reserve, crew, equipment, coordinate, and return plan pass checks | Opens the selected coordinate, logs each state change, and gives warnings before recall | Explains the exact blocked precondition or remaining return limit; failure creates a readable incident | Gate building, expedition record, destination map |
| Expeditions — create and dispatch a plan | Destination is known or a valid signal can generate one; crew and cargo are eligible | Locks a manifest and opens the mission using the saved gate window | Shows crew/equipment conflicts, missing return equipment, invalid destination, or cargo limit | Local branch plan and expedition; pawns/items remain normal game objects |
| Atlas — inspect, mark, or revisit a coordinate | Coordinate record exists; gate or later relay can reach it | Shows only discovered facts, records a player marker, or reopens the saved site | Names unknown signal, missing relay, or unavailable gate; no hidden fog-of-war reveal | Branch discovery record and destination map/site |
| Evidence — secure, quarantine, analyze | Physical evidence/person is present or an acquisition record exists; appropriate room/staff is available | Updates custody, analysis, and linked coordinate/case; outcomes point to a project or contract | Identifies missing sample, secure storage, researcher, or case link; unsafe subjects remain visibly unprocessed | Physical item/pawn plus local branch case/evidence record |
| Research — start, pause, complete | Project unlocked; required evidence and staffed bench are available | Advances local research and names its concrete building, policy, equipment, or contract unlock | Shows missing evidence, bench, researcher, or prerequisite; no silent research grant | Local branch research record; ordinary bench/pawn state remains native |
| Contracts/Ledger — accept, fulfill, post payment | Contract is offered and branch is eligible; fulfillment evidence/cargo is present | Logs acceptance and posts one uniquely identified reward/penalty after fulfillment | Shows deadline, missing deliverable, or eligibility reason; late/lost work retains its report | Local branch contract and ledger |
| Procurement — order and receive supplies | Supplier route exists; branch account and destination are valid | Deducts the quoted amount once; delivery creates the named physical items or a visible shipment in transit | Reports cost, supplier, route, or capacity issue; failed delivery stays recoverable in the shipment record | Local branch order/transaction; physical goods on receiving map |
| Cases/Containment — restrict access or resolve a case | Case and subject/sample still exist; player has a valid facility or world action | Records the chosen disposition and any custody/contract outcome | Names missing authorization, location, safe room, or person; blocked action leaves custody unchanged | Local case record plus normal pawn/item/map state |
| Outposts — establish, stock, evacuate, abandon | Destination and route are known; contract, staff, supplies, and upkeep are funded | Creates a branch-linked local site or a recorded supply/evacuation action | Names missing route, budget, staff, or relay; abandonment previews what remains or is lost | Local branch outpost record and site map/stock |
| Multiplayer — trade, send a dossier, or visit | The pinned RWT build exposes the action; both branches and server settings pass its requirements | Uses the verified RWT route and records a transfer receipt; dossier recipient studies its own copy locally | “Unavailable on this server/build” or an explicit transfer recovery state; never implies shared map/research | Each local branch plus RWT's supported transfer/activity owner |
| Space/gravship operations | Optional DLC/mod is present and exact selected content is verified | Opens native content or the documented narrow adapter | Explains missing DLC/mod or unverified integration; Core gate campaign remains available | Native gravship/DLC owner; Rimrooms branch only records its own contract link |

### First-survey generation failure action

Development 0.2.0 adds **Atlas → Review a replacement coordinate** for an unavailable initial coordinate. The dialog describes preserving the failed map, reassigning the untouched survey and creating a separate six-room replacement. The service rechecks eligibility on confirmation; it returns a keyed refusal when people, evidence, previous activity, missing content or the two-site cap prevent replacement. It moves no pawn or stock and pays no reward. Source and exact limits are in the [recovery implementation](implementation/PHASE_2_GENERATION_RECOVERY.md); observed acceptance remains pending.

## First playable pane set

### Additional source routes in the company systems wave

- **Personnel:** request a saved applicant batch, inspect the actual applicant's skills/traits/health/gear, select a company role and review onboarding cost, daily wage, next billing and arrival terms before hiring. Retry uses the same applicant and charge; cancellation is offered only when off-site custody and refund eligibility can be established. Native Work/Assign controls remain available. See [personnel implementation](implementation/PHASE_3_PERSONNEL_IMPLEMENTATION.md).
- **Facilities:** inspect cached native room/building/bed/power observations, refresh, filter categories, inspect the actual building or open Assign. Ordinary adult, medical, prisoner, slave, baby, animal and unknown special beds are distinguished; a slot count is not a claim that every pawn can use it. See [facility implementation](implementation/PHASE_3_FACILITIES_IMPLEMENTATION.md).
- **Procurement:** preview the existing item definition, quantity, unit/total USD quote, actual mass/stack limit, delivery timing and chosen stockpile. Receiving is bounded and physical, with retained cargo when space or filters prevent delivery. Cancellation, retry and receiving redirection must show the original order and ledger receipt. See the [current implementation wave](implementation/PHASE_3_BUILD_RECORD.md) for completion status.
- **Main menu:** show the exact mod title and current loaded version beside native top-left version information. Slideshow settings provide disable/native fallback and a still image for reduced motion; original menu images are the approved exception to gameplay content reuse.

These routes are source work; native overlay, save/reload, full-profile and usability acceptance are still pending.

The Async Industries slice needs Overview, Personnel, Facilities, Gate, Expeditions, Atlas, Evidence/Research, and Contracts/Ledger. Cases/Containment, Outposts, Multiplayer, and Space/Gravship panes can arrive later. An omitted pane is not a hidden blocker: the first campaign action stays available through a focused building, pawn, map, or vanilla interface route.

## Acceptance checks before an action ships

- The action is reachable from its documented pane and from the owning in-game object where appropriate.
- Success changes the named owner exactly once; save/load does not repeat grants, payments, launches, transfers, or scenario setup.
- Every refusal names the missing requirement and an actionable recovery route.
- Costs, consumed stock, assigned pawns, cargo, and returned/lost items are visible before or after the action.
- Disabled DLC, optional mods, RWT settings, and unavailable adapters produce a plain unavailable state and preserve the Core-only solo campaign.
- Accessibility checks cover readable labels, keyboard navigation, non-color warnings, and alerts that remain clear without sound.
- Record actual RimWorld/DLC/mod/RWT versions and save/log evidence before calling any action tested.
