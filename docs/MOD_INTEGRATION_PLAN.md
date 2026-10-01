# Rimrooms - Async Industries: complete systems and mod integration plan

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** design specification for RimWorld 1.6. No runtime mod code or in-game integration is implemented yet. The scope below turns the owner's campaign brief and the 2026-09-27 local 294-entry server profile into a buildable design. The companion [294-mod workbook](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.html) contains one row per profile record, source package ID/order, dependency stance, intended use, integration approach, conflict watch, and evidence status.

**Decision status:** owner choices D1–D9 and supplemental S1/B (family-level later threats; names deferred) are recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md). Gate 0 documentation/source preparation passed on 2026-09-28. Feature-specific research, compatibility, and runtime validation remain staged for implementation and acceptance; no feature is considered implemented or tested until evidence is saved. Each profile entry and feature is cross-linked in [`FEATURE_TRACEABILITY.md`](FEATURE_TRACEABILITY.md).

## 1. Product definition and boundaries

Rimrooms - Async Industries is a company-management simulation built inside RimWorld. RimWorld remains the game engine: pawn needs, work, skills, health, combat, construction, storage, trade, world map, DLC content, and (where selected) gravships continue to use their native systems. The mod adds a corporate layer for a powered machine gate, branch/facility operations, expeditions, generated Backrooms destinations, evidence, research, contracts, procurement, incidents, and long-term expansion.

The campaign begins at a small, underfunded research/security facility. The player hires a small crew, restores basic utilities, assembles and tests the machine, takes a short first expedition, recovers a useful result, and grows the operation through repeat visits, contracts, hires, labs, defenses, outposts, and better logistics. Profit, knowledge, survival, and containment compete for staff, time, and materials.

“Endless” means a reproducible stream of seeded coordinates and saved visited sites, not an infinitely large map loaded at once. One expedition map is finite and playable. A coordinate atlas remembers discoveries, known routes, team notes, changed rooms, relays, and unresolved signals. New generator versions must not silently rebuild or erase already visited sites.

### Settled product direction (Gate 0 owner choices recorded)

| Area | Decision |
| --- | --- |
| Game version | RimWorld 1.6; publish only for game builds actually verified. |
| DLC | Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional integrations. The full company campaign must remain playable with Core alone. |
| Multiplayer | RimWorld Together (RWT) is the co-op environment. Players run separate company branches and use only verified world transfers/activities. There is no live co-control of a shared map. Research dossiers are the baseline exchange; shared research is conditional on a supported, safely tested RWT extension. |
| Required dependencies | RimWorld Core is required. The co-op profile also requires Harmony and RimWorld Together. Every other mod in the 294 profile is optional; verify exact dependencies before packaging. |
| Local 294 profile | All 294 records are the required research target, not a required player dependency list. Each has an accepted source-fact note and a proposed treatment with evidence status; proposed treatments are not final compatibility dispositions. The [first-slice interaction map](research/FIRST_SLICE_MOD_INTERACTION_MAP.md) records source-backed ownership/treatment and post-build checks or deferrals for the actual opening. Inspect each optional API before implementing its adapter; no full-profile runtime compatibility is claimed. |
| Gravships | Proposed optional roles: Chapter 1 may supply late-game mobile-base/logistics content, and Chapter 2 may supply optional orbital threat/defense content, using native features only where the exact release and selected profile support them. Neither replaces the machine gate or creates Backrooms coordinates. Their APIs, compatibility, and wider orbital scope remain unverified; do not promise stations or moon play from these two chapters. |
| Source material | Use Kane Pixels' continuity and the A24 feature as indirect references. Do not directly recreate specific scenes or characters; exclude broader community canon from shipped content. Maintain source/provenance records. Third-party RimWorld mod assets and code are not bundled or copied by this plan. |
| Project identity and license | Displayed title is exactly `Rimrooms - Async Industries`. Author/publisher metadata is `Operator`. Use package ID `Rimrooms.AsyncIndustries`, namespace `RimroomsAsyncIndustries`, semantic versions, and MIT for original source code; track asset/audio licensing separately. |
| First release and language | **Public Steam Workshop is the first distribution target (D1 changed 2026-09-29; was: private RWT test build first).** Do not announce compatibility until validation is complete — publishing early makes that rule the main protection, not a formality. English first with localization keys; retain a Core-only solo path. |

The official Workshop page advertises separate colonies and shared-world activities. RWT's official wiki describes configurable offline visits/raids and exchange of items or pawns; the trading guide says direct trades and gifts require both players online. Direct real-time play on shared world tiles is future work. The local server's Aid and Trade actions are enabled, but offline-visit availability is not established and the enforced start is Crashlanded. A closed upstream report describes errors during remote settlement View loading, while an open report describes pawn-state changes after aid; both are test leads, not proof of current-release defects. Keep branch ledgers and research separate. Follow the [RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md), [baseline test plan](research/RWT_BASELINE_TEST_PLAN.md), and [RWT story/design review](research/reviews/mods/3005289691-nova.rimworldtogether.md).

## 2. Cooperative company model

### What players share

1. **Guild/company identity:** players can organize through RWT's player-made faction/guild system. Each player owns and runs a separate facility and local campaign state.
2. **Physical supply:** use only the RWT routes verified for the pinned build. Direct trades and gifts require both players online; treat offline visits and supply exchange as separate functions. The official guide also describes vanilla drop-pod transfers but does not specify offline-recipient behavior; test this route before relying on asynchronous deliveries. Silver remains the ordinary payment instrument unless the exact custom item transfer is verified. Do not promise unattended direct trades or gifts.
3. **Technology exchange:** physical Research Dossiers are a candidate baseline, not a proven RWT feature. The receiving branch would accept a dossier into its own lab and complete a local study project for a defined insight, recipe, or progress bonus. Direct trade/gifts require both players online. The dossier never silently writes research into another save. Transfer is a release gate: if the chosen RWT build cannot reliably move the custom item, leave it disabled until a supported, tested representation exists. Add direct shared-research ledger synchronization only if the pinned RWT build provides a supported extension point and disposable-profile tests prove safe, nonduplicating updates; otherwise retain dossier exchange alone.
4. **Facility visits:** use RWT's configured visit/activity behavior only after confirming it is enabled and safe in the pinned build. The local config does not establish offline-visit availability; a remote settlement View issue is a test lead. Treat a visit as a server-controlled activity or snapshot interaction, not two players simultaneously commanding one colony. A visit can have a purpose (inspection, delivery, rescue handoff, training exchange) and a log entry, but it must respect RWT's actual activity rules.
5. **Shared world activity:** where enabled, guild sites, roads, events, aid, and trade support a player-run company network. Each branch's Backrooms map, staff, gate state, contract state, and ledger remain locally authoritative unless RWT exposes and the project validates a supported way to transfer a particular record.

### Multiplayer implementation contract

- RWT server configuration controls whether trades, aid, player guilds, sites, roads, visits/raids, and events are available. The inspected local Aid and Trade actions are enabled; an offline Visit/Activity setting was not found. The mod's setup page must state which features are needed and degrade gracefully when an administrator disables one.
- The existing server profile reports `AllowAllMods=true`, `EnforceSettings=false`, and no enforced mod order. That is a profile snapshot, not a guarantee that every joining client uses identical files, DLC, order, or settings. For a release server, admins must pin the exact RimWorld build, RWT server/client release, required mod list/order, DLC set, and relevant settings.
- Keep map generator choices deterministic from saved seeds, coordinate IDs, generator version, and explicit mission inputs. Avoid local wall-clock deadlines, client-only UI side effects, and unsaved global random draws.
- The first adapter should use supported RWT extension points only. Do not invent an API, patch server internals, or mark all local mod actions “synchronized” without verification.
- Multiplayer progression is branch-to-branch: local study, local gate openings, local casualties, and local finance are independent. Cross-branch cooperation happens through concrete transfers, visit activities, and shared world objects that RWT actually supports.
- Keep transfer manifests and receiving logs. If an item is rejected or arrives in the wrong place, do not delete it or credit the same shipment twice. Use the RWT transfer spot where configured and show the player a recovery path.

## 3. Full player journey and operating cycle

### Scenario selection and starting setup

Use a selectable, data-driven scenario layer. Every scenario records its starting map/location, pawns, faction and relationships, silver/resources, gate/portal state, discovered coordinates, early incident/quest, win/failure conditions, and first tutorial objectives. Scenarios alter the opening setup while sharing the common coordinate, evidence, threat, and procedural generation systems. The canonical start-state contract and later scenario candidates are in [SCENARIOS.md](SCENARIOS.md).

| Scenario | Opening package | First objective and convergence |
| --- | --- | --- |
| **Async Industries** (first playable) | Small campus; limited silver/stock; incomplete gate; several staff; project board; first low-risk signal. | Restore power, complete calibration, field a crew, extract a sample/report, and start the company campaign. |
| **Furniture & Knickknack Store** | Ordinary retail site, staff/customers, sale stock/furnishings, strange basement opening, no established company. | Secure the site and investigate missing people; later turn the breach into a company operation or contracted site. |
| **Lone Survivor** | Single pawn, compact field equipment, no accessible facility, inside a seeded coordinate with the route home compromised. | Survive, learn rules, and mark/build a return path; escape to trigger rescue/company play or establish a limited outpost. |

The store's retail threshold is inspired by the [official A24 synopsis](https://a24films.com/films/backrooms) of a strange doorway in a furniture-showroom basement; use that as an original gameplay start, not a beat-by-beat film recreation. The Survivor scenario is a distinct survival opening but must preserve shared coordinate identity, evidence, and route rules. Candidate starts include a cut-off outpost, town-scale distortion response, and company in crisis; see [SCENARIOS.md](SCENARIOS.md). A separate first-pass fan-summary story note is recorded; it is not a direct feature review. See [SOURCE_REGISTER.md](SOURCE_REGISTER.md).

**Multiplayer constraint:** the local RWT server enforces Crashlanded. Verify mixed starting scenarios only with a disposable configuration copy. If the pinned RWT build does not support branches choosing different starts in one server/world, document a shared compatible scenario requirement; never imply each player can independently create a world or rewrite the shared world on join.

Core onboarding projects: inspect the gate site; restore power reserve; build a serviceable gate chamber and cutoff; assign an operator, engineer, and field team; set a basic recall rule; complete calibration; open the first brief window; return a labeled sample or recording; analyze it and receive the first contract payment/research lead.

### Facility layout and room function

Rooms are physically built and used with ordinary RimWorld rooms, bills, zones, stockpiles, power, temperature, beds, recreation, and security. Furniture or room designation identifies intended function; the company UI reports missing capacity and hazards without imposing opaque arbitrary room scores.

| Facility | Required gameplay purpose | Important links |
| --- | --- | --- |
| Gate chamber and control room | Assemble, calibrate, power, schedule, open, recall, and shut down the machine; enforce an exclusion perimeter. | Main power reserve, operator assignment, cutoff, security access, destination atlas. |
| Switchgear and maintenance | Supply steady power, store reserve, isolate failures, repair machinery, hold spare parts. | Gate modules, backup generator, maintenance jobs, safety alerts. |
| Laboratory | Analyze samples, rooms, devices, transcripts, and recovered equipment. | Research projects, evidence custody, skilled researchers, safe storage. |
| Evidence archive | Preserve records with chain-of-custody and case links. | Cases, contracts, dossier printing, coordinate history. |
| Decontamination, medical, and quarantine | Treat returning crews; hold uncertain people or materials; manage exposure. | Medical jobs, prison/guest systems where compatible, access policy. |
| Security and armory | Issue gear, train guards, lock sensitive areas, stage response teams. | Work assignments, locks, weapons, visitor routes, gate perimeter. |
| Workshop and test bay | Maintain/produce field equipment, sensors, beacons, sample containers, and replacement modules. | Crafting, procurement, recipe unlocks, cargo staging. |
| Receiving, warehouse, and cold/sample storage | Receive trade/shipment cargo, prepare manifests, segregate ordinary goods and evidence. | RWT transfer spot, stockpile filters, caravan/outpost dispatch. |
| Cafeteria, recreation, and quarters | Feed staff, schedule rest, maintain recreation and relationships. | Hospitality/food systems, visitor seating, bed and shift plans. |
| Radio/dispatch and records room | Track reports, coordinate crews, route messages, evaluate signal quality. | Radios, relays, coordinate atlas, missing-person cases. |
| Outpost and relay | Stage supplies, protect personnel, preserve route knowledge, support return. | Site ownership, resupply, radio chain, evacuation and loss policy. |

### Staffing, recruiting, and training

Staff remain normal pawns. Company roles are saved assignments and recommendations, not exclusive pawn classes. Role templates can suggest work priorities and loadouts, while the player retains control of skills, traits, passions, health, needs, schedules, beliefs, and relationships. Recruitment is organized as applicant pools: open candidates, trained specialists, contractors, rescued survivors, returning staff, and referrals. Candidates show skills/traits/health and salary or contract terms before hire; the company can maintain a reserve talent pool without automatically spawning free staff.

Roles: researcher/analyst, engineer, gate operator, guard, field surveyor, medic, containment officer, logistics clerk, radio operator, administrator, and outpost lead. Hire generated candidates through a company board, recruit rescued people, accept contract specialists, or train existing staff. Each person's skill, health, traits, ideology, trust, equipment familiarity, prior exposure, and expedition record influence performance. Training is a staged project using drills and supervised work for medical response, radio, mapping, weapons, sample handling, gate operations, de-escalation, containment, and field construction.

Work categories add inspectable bills/jobs for calibration, gate maintenance, packing, evidence intake, analysis, decontamination, training, site repair, radio watch, and contract documentation. Existing work priority mods remain authoritative; do not create a second mandatory work-priority screen.

### Gate machinery and window progression

The gate is an independent buildable machine with frame, power feed, control console, calibration hardware, emergency cutoff, replaceable modules, condition, heat/load state, stability, and an opening log. Operating time advances in game ticks. Operator skill, power reserve, maintenance, modules, destination signal, relay network, and research influence the safe window. Low-tier failures warn and give a recall choice; late-tier incidents may cause site drift, damage, lost cargo, or a rescue chain.

Progression: short test pulse → first controlled opening → calibrated repeat coordinate → reliable recall equipment → radio/tethered return → relay-assisted long operation → multi-team and remote outpost support → late high-complexity windows. Duration grows from minutes to hours and days, then to weeks or month-scale only when the player earns the power, cooling, stability, crew rotations, supply, and return logistics to justify it. Never use a raw timer extension without new costs or risks.

### Expedition and coordinate atlas

An expedition card records objective, coordinate/signal, seed, known rooms, crew, gear, cargo allowance, gate window, return plan, radio/beacon state, and recall conditions. Selecting a crew checks medical readiness, training, equipment, carrying capacity, and any required specialist. Departure creates or loads a finite site map. Crews survey, mark exits, collect evidence and materials, salvage furniture/equipment, set relays, build a forward post, encounter entities, and decide when to return.

Each coordinate retains its saved generated site, previously mapped route graph, known rules, room alterations, unresolved signals, installed beacons, missing-person clues, recovered value, and last exit/return status. To re-enter, select an atlas record or investigate a fresh signal. Field equipment can affect map generation: scanners reveal room/route tags; mapping boards increase navigable graph memory; radio repeaters reduce communication gaps; acoustic/electromagnetic equipment biases which room families or modifiers are exposed; survey drones place remote markers; protective suits enable work in hazardous modules. Equipment influences information and survivability, not arbitrary magical control over the generator.

### Procedural rooms and spatial behavior

Use seeded room-family and corridor templates tagged by size, shape, material, lighting, door count, entrance/exit rules, room role, points of interest, salvage, hazards, entities, and supported modifiers. Generate a graph first; place compatible maps/rooms; validate player and pawn paths; place mission-required return clues; then apply a bounded number of spatial alterations. Possible authored families include offices, service areas, storage, retail back rooms, medical rooms, mechanical rooms, unfinished construction, corridors, apartments, and other spaces in the approved source direction.

Uncanny architecture comes from intentional topology: repeated halls, impossible adjacency across connected map/site transitions, moved doors, altered dimensions, recursive room identity, a remembered object appearing in a different room, or a route that changes after a documented trigger. Some phenomena can **propagate** along the site's room graph: a bounded spread rule tracks source room, adjacent paths, elapsed game time, and conditions such as power, noise, light, or activity. Survey gear detects spread; barriers, shutdowns, anchors, or containment work can slow, redirect, or stop it. Propagation is deterministic from saved inputs and leaves discoverable records. Every change has a clue or gameplay consequence. One finite map cannot contain a literally infinite labyrinth; the atlas and linked maps provide open-ended continuation. Store generator version with each coordinate and preserve visited state across releases.

### Study, research, entities, and casework

Evidence has a type, source coordinate, time, collector, container, contamination/custody state, known properties, confidence, case links, contract value, and research value. Staff can analyze samples, recordings, maps, furniture, devices, room changes, and transcripts. Results reveal partial rules, equipment recipes, threat behaviors, safe routes, mission leads, countermeasures, and company policy choices.

Entities and anomalies need explicit tells, triggers, limits, countermeasures, evidence, encounter consequences, and escalation behavior. Threats can be evaded, deterred, injured, captured, quarantined, monitored, studied, transferred, sold under an appropriate contract, or destroyed according to the case and player decision. Capturing an entity is not mandatory for research. Study actions require safe infrastructure, staffing, time, and incident planning; a containment failure leaves a traceable case.

Missing crews generate radio fragments, abandoned equipment, route anomalies, witness statements, delayed return, rescue objectives, and a final documented outcome. Returned people may be treated as rescued staff, hires, guests, witnesses, patients, detainees, or contract subjects; a contract can also request a custody transfer or sale, with the associated reputation and relationship consequences shown before acceptance. Use the vanilla guest/prisoner/faction/medical systems where possible, with Backrooms case state layered on top. Interview/debrief, examine, compare transcript, assess memory/health, classify evidence, and choose disposition. The game should support detention/interrogation as a fictional game-management decision while retaining human-readable custody, release, rescue, and evidence outcomes.

### Research tree and tech transfer

Create Backrooms-owned research families: facility and power; gate engineering; field safety; surveying and mapping; evidence handling; communications; route stabilization; threat study and containment; medical recovery; cargo/remote logistics; transport/space operations; topology and deep-space operations. Research can require bench time, components, staff skill, and specific documented evidence. Evidence can open branches or alternate prerequisites rather than making every unlock an identical bench timer.

RWT technology sharing may use printed research dossier items tied to a completed project and a stable project ID/version, if the custom item transfers reliably. The sender places it in a supported item trade/gift route (direct trades and gifts require both players online); the receiver's branch records receipt and offers an analysis project. On completion it grants an agreed local bonus/unlock under compatibility rules. Consumed/used dossier IDs are recorded locally to prevent duplicate claims within that save. This does not imply shared company research state.

### Contracts, missions, money, and material flow

Mission and contract templates provide authored objectives with seeded variations. Generated jobs use the coordinate and its saved history, client/faction, company tier, discovered rules, prior success/failure, available crew/equipment, gate duration, and risk budget as inputs. The generator chooses a coherent objective chain and bounded complication set; it must never randomly remove all return routes or invent a clue the player could not observe.

| Mission family | Core objective | Variable complication or follow-up |
| --- | --- | --- |
| Survey and mapping | Record rooms, exits, hazards, or coordinate signature. | Route shift, interrupted signal, newly visible branch. |
| Equipment/furniture retrieval | Recover named cargo or salvage useful stock. | Weight limit, unstable opening, claim dispute. |
| Sample and transcript analysis | Collect and document evidence. | Contamination, contradictory accounts, hidden rule. |
| Missing personnel/rescue | Follow radio or physical clues and find a crew. | Delayed time, changed room identity, split survivors. |
| Containment/security | Secure an entity, protect a site, or escort a client. | Countermeasure unknown, breach risk, several routes to success. |
| Relay/outpost and lease | Build, staff, rent, supply, defend, or evacuate a location. | Lease terms, cutoff, resupply delay, route pressure. |
| Town distortion response | Secure ordinary-world opening and investigate missing residents. | Local authority pressure, witness conflict, unstable threshold. |
| Commercial service | Meet a survey, retrieval, research, or custody-transfer request. | Bonus for evidence quality or penalty for unsafe handling. |
| Gravship/space support | Optional late-game branch using installed, verified native content for travel, cargo, or defense. | DLC/mod absent, exact-profile conflict, or no documented supported connection to a Rimrooms mission. |

Repeating a mission family changes its evidence, coordinate rules, crew history, and contract terms rather than changing only enemy count. Major outcomes update the atlas and case timeline, creating leads for later quests.

Keep a branch-local USD Company Account for payroll, contracts, expenses, shipment schedules, and profit; the parent company's multitrillion valuation is not the player's spendable balance. Use physical vanilla silver and transferable goods for ordinary RimWorld/RWT item transactions. Company-account balances do not cross RWT branches. Contract cards specify client, advance, requested deliverables, **two or more routes to success**, optional quality/safety terms, payment, penalty cap, ownership, and cancellation. **No deadline** - see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate). Orders name quantity, price, source, arrival window, and receiving area. Shipments can be delayed, lost, contaminated, intercepted, or redirected by explicit world events.

Cross-reference the [economy and bulk-logistics contract](CAMPAIGN_ECONOMY_MODEL.md), [OgreStack source review](research/reviews/mods/1447140290-Ogre.OgreStack.md), and [stack/cargo/RWT interaction map](research/PRIORITY_PROFILE_INTERACTIONS.md#stack-size-cargo-and-shared-item-exchange-row-157--rows-122259--rwt). Row 157 OgreStack is active in the 294 profile; its published default uses a ×30 scalar for small-volume resources. Rimrooms must read effective saved stack rules at runtime, preserve vanilla stack behavior when OgreStack is absent, and prove storage, shipment, caravan, save/reload, and RWT transfers against both paths. It must never encode the owner's current stack preset as a required dependency.

Revenue: survey/recovery contracts, safe extraction, resale of approved salvage, scientific results, equipment/furniture resale, secure containment services, procurement/consulting, and outpost services. Costs: payroll/food, medical care, fuel/power, component wear, weapon replacement, laboratory consumables, security, shipping, rent/site upkeep, prisoner/guest upkeep, cleanup, compensation, and rescue. A discovery can be studied, archived, sold, licensed in-world, contained, or discarded; risk/value differs by choice.

Stable destinations may offer **leased or claimed spaces**: the company can rent a safe room, storage area, lab corner, or route-side shelter from an in-world client/faction, or negotiate a temporary right to use a surveyed area. Each lease names boundaries, duration, rent, access rules, required guards/maintenance, and renewal or eviction conditions. The company can furnish and secure a rented space, but must keep the route supplied and the lease obligations visible. These rooms may become field labs, rest/medical points, receiving depots, or guarded commercial sites; the first implementation should use a small set of authored lease outcomes before generating free-form real estate.

### Distortions, settlements, outposts, and world map

Use RimWorld world sites/quests/incidents for outposts, stranded crews, signal stations, missing settlements, ordinary-world openings, response contracts, and return expeditions. The company network has distinct node types: the headquarters and ordinary-world facilities outside the gate; approach, security, and receiving posts at the threshold; rented/claimed rooms, field shelters, labs, radio relays, and depots inside saved Backrooms coordinates; and gravship support sites in orbit when available. A town distortion creates objectives, none of them timed: locate/secure the entry, contact missing civilians, rescue/search, establish perimeter, collect evidence, shut down or stabilize the opening, handle witnesses, and close the case. Outcomes alter company reputation, local faction relations, future signals, and contract offers.

Outposts must consume supplies, have staffing/security/communication, a defined purpose (relay, receiving depot, research station, recovery shelter), and evacuation/abandonment policy. Radio and supply points extend reach only when placed, powered, staffed or serviced, and linked to a known route. World travel, vehicles, and gravships support logistics; the machine gate remains the primary Backrooms access.

### Operations interface and tab map

For the first playable, add one company **Operations** main tab with linked panes and keep the familiar Architect, Work, Research, Assign, and World actions directly available. The full-mod target is a company-first remaster of the menu/tab layout, grown from these panes into a coherent **Company Command** navigation layer for facilities, people, projects, expeditions, sites, cases, and money. Reorganize redundant navigation in stages only after the company flow is proven; every underlying RimWorld action must remain reachable and compatible with the optional profile. Do not let the command layer replace pawn autonomy or the colony's native simulation.

| Operations pane | Contents and controls |
| --- | --- |
| Overview | Gate alarm/state, low stocks, injured/missing staff, payments due, power reserve, contract and incident priorities. |
| Personnel | Staff list, skills/health/traits, role suggestion, training queue, shift, gear, expedition history. |
| Facilities | Room function, capacity, access policy, power/safety warnings, storage and receiving areas. |
| Gate | Machine condition/modules, calibration, power window estimate, cutoff, assigned operator, open/recall/close action with cost/risk preview. |
| Expeditions | Select objective and coordinate; crew, kit, cargo, time window, return rule, dispatch and recall. |
| Atlas and routes | Saved sites, fog-of-war, map graph, room tags, radio/return status, route clues, visits and changes. |
| Research and evidence | Projects, sample queue, custody, transcripts, equipment tests, dossiers, uncertainty and discovered rules. |
| Contracts and ledger | Income, payroll, fees, procurement, shipment manifests, salvage appraisal, penalties and local branch balance. |
| Cases and containment | Missing-person cases, distortions, witnesses, prisoners, quarantine, evidence, investigation timeline, disposition. |
| Outposts and company network | Sites, staffing, stock, security, radio links, maintenance, evacuation and RWT guild/transfer reference. |
| Gravship operations | Shown only when Odyssey and selected chapter content are present; link to native gravship views and company logistics summary. |

Build Company Command on top of the Operations panes in stages. Its completed layout should make the company the primary navigation model while retaining direct routes to every relevant vanilla pawn, Work, Research, Architect, Assign, and World action. Screen replacement/reorganization is an interface presentation change, not a rewrite of the underlying RimWorld systems.

All actions that consume stock, move pawns, open a gate, change a map, advance a project, trade cargo, or alter case state need a saved transaction record. Purely informational panels may be local. Button availability must reflect installed DLC/mods and server permissions.

## 4. Gravship chapters and dependency policy

The selected Gravship Expanded Chapter 1 page requires Odyssey and Vanilla Expanded Framework; its publisher describes oxygen, fuel, power, heat, and crew management and warns that other gravship-altering mods may conflict. Chapter 2 requires Odyssey, VEF, and Chapter 1; its publisher describes orbital threat detection/combat, defenses, weapons, artillery/boarding, wreck salvage, and hostile orbital events. These are publisher descriptions, not Rimrooms runtime results or proof of a mission API. The project review records that neither chapter establishes a broader moon/station campaign; the FAQ points to Chapter 3 for broader off-world play and describes only a narrow custom-starting-ship route for Chapter 1. Both pages identify CC BY-NC-ND 4.0; keep their assets/code in their own subscribed mod, do not repackage them. [Chapter 1 page](https://steamcommunity.com/sharedfiles/filedetails/?id=3609835606), [Chapter 2 page](https://steamcommunity.com/sharedfiles/filedetails/?id=3799737423), [VEF page](https://steamcommunity.com/sharedfiles/filedetails/?id=2023507013).

Proposed integration role, subject to a clean chapter stack and exact-profile tests: expose Chapter 1's verified native travel/cargo/survival systems as an optional late-game logistics layer; expose Chapter 2's verified native threat/defense/salvage content as optional orbital activity only where normal game routes make it available. Do not promise that Rimrooms can create custom boarding missions, an orbital station, a moon surface, or a broad space campaign from these two chapters. Keep this separate from gate operation, Backrooms room generation, and entity definitions. Avoid patching gravship internals unless the VGE authors document a supported extension API and a reproduced conflict requires a narrow adapter.

## 5. Exhaustive 294-profile mapping

Every row in the workbook retains source row number, package/workshop ID, name, source load-order value, and config type, then adds a design family and a role. The table below is the workbook's family rollup for all 294 records; it is a mapping inventory, not evidence that each mod's exact 1.6 page, API, dependency, or compatibility has been inspected.

| Design family | Records | Intended company use |
| --- | ---: | --- |
| Additional portal content | 1 | Keep separate from the Backrooms gate; compare as a distinct portal or contract target. |
| Animals and field support | 14 | Optional security, hauling, cargo, and field support. |
| Combat incident records and casualty review | 1 | Debrief/casualty clue only after exact mod behavior review. |
| Cross-mod fixes and balance patches | 2 | Retain source patches; add no duplicate patches without reproduced conflict. |
| Detention and subject casework | 19 | Layer case/custody records over existing capture and prisoner workflows. |
| Detention clothing and custody compatibility | 1 | Preserve prisoner/detainee apparel behavior; title-based use pending page review. |
| DLC: Anomaly | 1 | Optional containment and anomaly integration. |
| DLC: Biotech | 1 | Optional genes, mechanitors, medicine, and biological content. |
| DLC: Ideology | 1 | Optional beliefs, rituals, and meditation. |
| DLC: Odyssey | 1 | Optional gravship and off-world campaign layer. |
| DLC: Royalty | 1 | Optional titles, quests, and psycasts. |
| Emergency care and containment response | 6 | Preserve fire, recovery, and medical/containment procedures. |
| Facilities and spatial construction | 24 | Build headquarters, rooms, secure zones, and expedition infrastructure. |
| Facility access control | 1 | Secure labs, armory, gate, quarantine, and visitor routes. |
| Facility construction and material access | 5 | Construction planning, delivery, linking, and prefabrication. |
| Field medical and repair kits | 1 | Expeditions carry native med/repair kit options. |
| Food service and staff welfare | 4 | Cafeterias, nutrition, recreation, and employee routines. |
| Furniture, clothing, and visual content | 17 | Furnish and outfit facilities; use installed assets without bundling them. |
| Hospitality and visitor economy | 7 | Optional guests, services, recruitment, and visitor handling. |
| Interface and startup quality of life | 1 | Preserve startup convenience without gameplay dependency. |
| Interface, scenario setup, and quality of life | 11 | Keep native convenience and UI; add focused Operations panels. |
| Materials, cargo, and recovered resources | 9 | Shape expedition weight, appraisal, salvage, storage, and manifest rules. |
| Medical, biological, and recovery systems | 29 | Treat crews and use optional medicine/biology; core treatment remains independent. |
| Mod framework | 6 | Use only concrete public services; no broad framework dependency in core. |
| Multiplayer: guild and world exchange | 1 | Separate branches, trade, aid, guild/site/road/activity integrations. |
| Orbital operations: Gravship Expanded Chapter 1 | 1 | Candidate late mobile-base/logistics content; use only verified native features. |
| Orbital operations: Gravship Expanded Chapter 2 | 1 | Candidate optional orbital-threat/defense content; mission and adapter support remain unverified. |
| Performance and simulation controls | 1 | Preserve speed/performance tools; use tick time for simulation. |
| Power and industrial infrastructure | 10 | Facility power, generation, storage, maintenance, and production. |
| Power storage and surge protection | 2 | Optional reserve and electrical protection. |
| Remains and facility waste handling | 1 | Optional remains/contaminated-waste procedure. |
| Research and staff development | 9 | Integrate with optional research presentation and training mods. |
| RimWorld base game | 1 | Primary engine and required core systems. |
| Salvage and site recovery | 1 | Recoverable ancient structures/wrecks and material appraisal. |
| Security and combat equipment | 25 | Guard loadouts, defenses, training, and field countermeasures. |
| Security tactics and guard response | 1 | Native drafted guard response; do not automate irreversible combat choices. |
| Staff jobs, policies, and social systems | 9 | Roles, schedules, priorities, beliefs, relationships, and work quality. |
| Staff psychology, relationships, and faction standing | 11 | Applicant fit, morale, interpersonal events, and reputation. |
| Staff welfare and recreation | 1 | Meditation/recovery within existing pawn needs. |
| Staff work-flow quality of life | 3 | Preserve native work convenience and task recovery. |
| Storage and recovered-material logistics | 13 | Stockpiles, cold storage, warehouse, evidence, and cargo handling. |
| Transport and expedition logistics | 14 | Vehicles/animals/carrying/travel; gate remains the primary access. |
| World operations, contracts, and commerce | 12 | Quests, traders, contracts, comms, outposts, and revenue. |
| World threat and event pacing | 3 | Respect profile event suppressions; make Backrooms incidents independent. |
| World, environment, and evidence | 10 | Draw clues and salvage from sites while keeping deterministic generation separate. |
| **Total** | **294** | **All profile records represented.** |

The map groups mods by intended use; a single mod may touch multiple systems. The individual workbook row is the source of truth for assigned family, planned use, integration approach, compatibility watch, and review status. Most rows are explicitly marked as design-level mappings with per-page/dependency/API verification pending. The source profile reports 294 entries but does not prove current versions or compatible settings.

## 6. Versioning, DLC, and compatibility rules

- Core starts and saves on RimWorld 1.6 with no gameplay-mod dependency. A single-player-only load must work if RWT is absent; the intended co-op setup adds RWT/Harmony.
- Load DLC-specific definitions only when their DLC exists. Fallbacks preserve the same broad function: vanilla research, local caravan/world site, vanilla medicine, vanilla storage, and ordinary building/power systems.
- Treat all 294 entries as the user's selected profile and research surface. Do not silently remove, repackage, or require them in an unrelated distribution. Group optional hooks by package ID and keep each patch narrow.
- The current server allows all mods and does not enforce settings/order. This is insufficient evidence of a fixed multiplayer target. Record client game build, RWT client/server build, DLC set, ordered package IDs, server configuration, save, and logs per verified release.
- Gravship compatibility risk is unusually high because both selected chapters explicitly warn about other gravship-changing mods. Don't modify the gravship system from Backrooms code; use normal RWT-compatible world/transfer pathways and test the selected late-game set as a separate compatibility milestone.
- Save schemas need explicit versions. Serialize IDs, seeds, stage enums, source/dossier IDs, ownership branch IDs, generator versions, and item transaction IDs. Include migration handling before changing keys or generated-site schemas.

## 7. Release and implementation checklist

### Design is specified in this workspace

- [x] Initial company start, operation loop, facility functions, work roles, research/evidence, economy, incidents, coordinates, procedural sites, and late-stage expansion.
- [x] Record D4: all five DLC are optional; maintain a complete Core-only campaign and validate the all-five local profile.
- [x] Record the RWT design boundary: separate branches and no live shared-map promise; trade/aid/guild/visits remain conditional on documented or tested RWT behavior.
- [x] Record proposed, optional late-game roles and dependency boundaries for Gravship Chapters 1 and 2; native capabilities and exact-profile compatibility remain unverified.
- [x] All 294 local profile rows captured and assigned to a design family in the workbook.
- [x] UI panes and facility roles enumerated.
- [x] Backrooms infinite-scale requirement expressed as deterministic, persistent coordinate/site generation.

### Still required before calling the mod implemented or profile-supported

- [ ] Create RimWorld mod packaging, `About.xml`, language keys, XML Defs, original art/audio, C# source, and build output.
- [ ] Implement scenario, staff/work systems, gate state machine, expedition lifecycle, coordinate atlas, seeded room graph, evidence/case files, contracts/ledger, outposts, research, and Operations UI.
- [ ] Implement and inspect a named RWT adapter; verify custom dossier and cargo transfers, offline facility visits, events, guilds, roads/sites, aid, reconnects, save/load, and admin-disabled features.
- [ ] Capture and pin exact game/DLC/RWT/build/load-order/server settings for the local profile.
- [ ] Review the actual Workshop page, declared dependency, version notes, changed Defs/code/API, and known compatibility for the remaining 283 profile entries beyond Core, the five DLCs, Harmony, RWT, VEF, and the two gravship chapters; replace title-based assumptions where needed.
- [ ] Run an in-game compatibility pass against baseline, each advertised DLC combination, both gravship chapters, and the complete ordered 294 profile. No such runtime result is represented by the design workbook.
- [ ] Complete the official Kane Pixels episode-by-episode viewing log and the feature-film viewing log before specifying scene-specific content; the current index lists 23 videos but does not claim those works have all been reviewed.
- [ ] Implement the selected package identity and MIT source-code license; set the author/publisher field to `Operator`. Complete original asset provenance and save migration policy.

The workbook is complete as a 294-row **design register**, not as a compatibility certification. Until the checklist's implementation and validation items are completed, describe the project as a thorough design package rather than a finished or fully tested RimWorld mod.
