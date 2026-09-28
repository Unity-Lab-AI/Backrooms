# Rimrooms - Async Industries: Operations action contracts

**Status:** pre-code player-facing contract. These are proposed actions and outcomes; no menu or integration has been implemented. They define what the Operations interface must let the player do and how it must explain a blocked action.

**Feature route:** [RR-UI](FEATURE_TRACEABILITY.md), with the owning gameplay rules in [GAME_DESIGN.md](GAME_DESIGN.md), [SCENARIOS.md](SCENARIOS.md), [FIRST_PLAYABLE_CONTRACT.md](FIRST_PLAYABLE_CONTRACT.md), and [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md).

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

## First playable pane set

The Async Industries slice needs Overview, Personnel, Facilities, Gate, Expeditions, Atlas, Evidence/Research, and Contracts/Ledger. Cases/Containment, Outposts, Multiplayer, and Space/Gravship panes can arrive later. An omitted pane is not a hidden blocker: the first campaign action stays available through a focused building, pawn, map, or vanilla interface route.

## Acceptance checks before an action ships

- The action is reachable from its documented pane and from the owning in-game object where appropriate.
- Success changes the named owner exactly once; save/load does not repeat grants, payments, launches, transfers, or scenario setup.
- Every refusal names the missing requirement and an actionable recovery route.
- Costs, consumed stock, assigned pawns, cargo, and returned/lost items are visible before or after the action.
- Disabled DLC, optional mods, RWT settings, and unavailable adapters produce a plain unavailable state and preserve the Core-only solo campaign.
- Accessibility checks cover readable labels, keyboard navigation, non-color warnings, and alerts that remain clear without sound.
- Record actual RimWorld/DLC/mod/RWT versions and save/log evidence before calling any action tested.
