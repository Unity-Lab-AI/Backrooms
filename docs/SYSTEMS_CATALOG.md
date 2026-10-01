# Systems catalog

> **Superseded 2026-10-01 — dependencies.** This document predates the owner's decision that the
> package has hard dependencies. `About.xml` now declares all five expansions and the whole
> collection as requirements, so anything here describing a Core-only route is history rather than
> a current claim. Recorded as a change to D3 and D4 in
> [Gate 0 decisions](GATE_0_DECISIONS.md#decision-log).

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


This catalog turns the campaign brief into candidate system families. The broader progression and player-facing content breadth are collected in the [campaign content catalog](CAMPAIGN_CONTENT_CATALOG.md); these are working labels, while final Def names and balance belong to later implementation. The first playable should stay focused on the vertical slice in [the roadmap](ROADMAP.md) and use its concrete [content inventory](FIRST_SLICE_CONTENT_INVENTORY.md), [threat sheets](THREAT_DESIGN_SHEETS.md), and [economy model](CAMPAIGN_ECONOMY_MODEL.md). The complete company flow, multiplayer contract, gravship scope, and 294-profile integration mapping are in the [systems and mod integration plan](MOD_INTEGRATION_PLAN.md).

## New-game setup

Offer selectable scenarios with different starting maps, pawn rosters, budgets/inventories, gate states, known coordinates, and early objectives. Implement the **Async Industries** facility campaign first, then add the **Furniture & Knickknack Store** breach and **Lone Survivor** in a seeded Backrooms coordinate. These starts share the procedural-space, coordinate, evidence, threat, and progression data systems while providing distinct opening pressures and routes into the broader campaign. See the canonical [scenario design](SCENARIOS.md) and its [player-facing overview](GAME_DESIGN.md#scenario-framework-and-opening-scenarios).

| Starting scenario | Starting assets/constraints | Opening goal |
| --- | --- | --- |
| Async Industries | Small facility, staff, limited funds, supplies, disabled/incomplete gate | Secure the facility and safely open the first expedition. |
| Furniture & Knickknack Store | Retail building, ordinary staff, stock/furniture, anomalous basement opening, no company infrastructure | Secure the breach and account for people/evidence. |
| Lone Survivor | One pawn, field kit, no surface base or active company gate | Survive, understand the space, and locate/rebuild a viable route home. |

Each scenario must define a seed, starting faction/ownership rules, failure conditions, recovery/return path, tutorial/objective chain, and compatibility with save/load. Test how scenario-specific world generation works with RimWorld Together before advertising mixed-start multiplayer.

Keep ordinary RimWorld systems for pawn needs, work, health, relationships, combat, construction, research, storage, power, growing, crafting, and trade. Add the company layer for assignments, contracts, evidence, coordinates, USD-denominated branch finance, and expeditions. Company cash stays a ledger value; physical goods still use real carry, stack, storage, and hauling capacity. The [economy model](CAMPAIGN_ECONOMY_MODEL.md) defines the scale and bulk-handling rules.

## Staff and work categories

Roles are recommendations and work priorities, not pawn classes. Staff can cross-train.

| Work category | Candidate tasks | Useful skills |
| --- | --- | --- |
| Research | Analyze samples, compare reports, decode records, write site profiles | Intellectual |
| Gate operations | Calibrate, open, stabilize, recall, shut down, and repair the gate | Intellectual, Crafting |
| Engineering | Maintain power, fabricate equipment, repair tools, assemble modules | Crafting, Construction |
| Security | Guard the gate, escort teams, train, manage controlled access | Shooting, Melee, Social |
| Field operations | Survey rooms, mark routes, collect evidence, install beacons, recover cargo | Intellectual, Medical, Construction |
| Medical and containment | Treat crews, decontaminate, examine, isolate, monitor arrivals | Medical |
| Logistics | Receive shipments, pack expeditions, manage storage, dispatch outposts | Social, Intellectual, Crafting |
| Communications | Maintain radios, relay reports, triangulate signals, coordinate remote teams | Intellectual, Social |
| Administration | Fulfill contracts, hire, authorize projects, manage payroll and claims | Social, Intellectual |

Skills, traits, passions, beliefs, health, and expedition history affect outcomes. Training comes from supervised work, projects, assignments, and equipment practice.

## Facility functions

| Function | Core contents | Decision |
| --- | --- | --- |
| Gate chamber | Machine gate, control console, safety perimeter, emergency cutoff | Throughput versus exposure and power use |
| Power and maintenance | Generators, batteries, switchgear, repair bench, spare parts | Reserve capacity versus cost and outage risk |
| Research laboratory | Analysis bench, sample cabinets, instruments | Which evidence deserves scarce staff time |
| Evidence archive | Secure storage, terminal, map and transcript records | Keep, study, restrict, contract, or dispose |
| Decontamination and quarantine | Airlock, wash station, medical bed, secure cells | Space spent on uncertain arrivals |
| Security and armory | Weapons, armor, training area, guard post, locks | Rapid response versus safe staff access |
| Workshop and fabrication | Machining, textile work, components, field tools | Manufacture or buy equipment |
| Medical bay | Beds, medicine, diagnostics, emergency treatment | Routine care versus expedition returns |
| Radio and dispatch | Comms console, antenna, map table, relay gear | Coordination versus expense and exposure |
| Logistics and receiving | Loading area, bulk and cold storage, packing | Central stock versus outpost supply |
| Staff quarters | Beds, schedules, comfort and recreation | Staff recovery versus expansion pressure |
| Transport and space operations | Vehicle bays and later gravship support when available | Extend reach without replacing gate play |

Recognize facilities from their buildings and functions. Avoid hidden room-score requirements.

## Operations interface

The first playable adds an Operations main tab as a company dashboard. The full-mod target grows this into a company-first menu and tab layout that groups facility, personnel, projects, expeditions, discoveries, cases, contracts, finance, and outposts. Preserve working access to familiar pawn, building, map, work, research, and world actions as these views are reorganized; the dashboard is the first step, not the final UI scope.

1. **Overview:** urgent alerts, active projects, gate state, cash, payments due. **No deadlines** - see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).
2. **Personnel:** roster, role recommendations, training, injuries, field history.
3. **Projects and research:** machine progress, technical projects, evidence waiting for analysis.
4. **Gate network:** known coordinates, routes, site state, radio quality, last contact, return gear.
5. **Expedition planning:** objective, destination, crew, equipment, cargo, duration, recall rule.
6. **Contracts and finance:** fees, salaries, orders, salvage, penalties, compensation.
7. **Incidents and case files:** distortions, missing crew, returned people, interviews, quarantine, evidence.
8. **Outposts:** staffing, supplies, security, communications, upkeep, resupply.

Each record should link to its pawn, building, quest, map, or saved coordinate. Urgent events belong on the overview; detailed reports belong in their own views.

## Gate and expedition equipment

Gate progression: frame and power subsystem; calibration array and console; safety cutoff; stabilizer modules; coordinate recorder; mapping relay; return beacon; remote signal triangulation; longer-duration and multi-gate systems.

Field kit: protective gear; role-appropriate weapons; medical packs and restraints; quarantine containers; map markers; sensors and recorders; sample containers; radios and repeaters; tethers; emergency beacons; portable power; cargo frames; construction and repair tools.

Every device should expose its effect: range, charge, noise, protection, capacity, survey quality, or return reliability.

## Research branches

| Tier | Branches | Example capability |
| --- | --- | --- |
| Start-up | Facility basics, power reserve, repair, hiring | Gate assembly, safety perimeter, stock control |
| First entry | Field protocols, protective gear, recall | Short opening, crew kit, first evidence analysis |
| Measurement | Sensors, recording, mapping, radio | Coordinate records, room tags, signal monitoring |
| Repeat access | Gate stability, power efficiency, site memory | Reopen known sites, longer windows, return beacons |
| Remote operations | Logistics, relays, shipments, outpost defense | Forward stores, staffed relay, rescue support |
| Distortion response | Settlement surveys, containment, witness handling | Reality-incident response and advanced quarantine |
| Industrial expansion | Fabrication, vehicles, gravship/space support | Multi-team work and remote supply |
| Deep-space study | Spatial topology, stabilization, unknown phenomena | Late gate modules and complex destinations |

Let evidence, contracts, and documented room rules open alternate research routes. Do not make every branch a flat bench prerequisite.

## Mission families

| Family | Objective | Possible complication |
| --- | --- | --- |
| Baseline survey | Record layout, exits, light, hazards, coordinate signature | Map drift or interrupted radio |
| Salvage and retrieval | Return requested equipment, furnishings, or supplies | Cargo pressure or gate instability |
| Sample study | Collect, seal, label, and return evidence | Contamination or storage limits |
| Missing crew | Trace a signal, rescue survivors, recover records | Conflicting time reports or changed route |
| Relay installation | Build or repair a radio/return point | Short window or limited materials |
| Containment | Secure a threat or prevent an exit event | Limited restraints or unclear behavior |
| Reality distortion | Investigate an opening at a settlement or ordinary site | Missing civilians, authority pressure, several routes to success |
| Commercial contract | Meet a survey or recovery request | Clawback, rival interests, elevated risk |
| Outpost expedition | Establish, supply, defend, or evacuate a site | Lost communications or depleted stock |

Seed mission generation from coordinate state, company capability, previous events, staffing, gate duration, client, and difficulty. Combine weighted choices with authored objectives so stories vary without losing coherence.

## Company economy

Show income and costs in a readable ledger: contracts and advances; salvage and research deliverables; recruitment, payroll, food, training, and medicine; gate energy and repairs; security, replacement equipment, shipments, and outpost upkeep; compensation and penalties. Rare findings can be held for research rather than sold. Profit should reward documented results and safe recovery, not only killing threats.

## World incidents and people

- Openings can appear at settlements or ordinary sites as quests with a clear location and clock.
- Crews can vanish, return late or injured, make contact, or return with contradictory accounts that open a case.
- People found through the gate can become rescue candidates, hires, guests, prisoners, witnesses, patients, or research subjects according to the event and player policy.
- Use vanilla faction, prisoner, guest, health, and relationship systems where they fit.
- Major incidents should leave evidence and a trail visible from the Operations board.

## Procedural room records

Room templates carry tags for dimensions, doors, passages, materials, lighting, furniture, usable points, loot, hazards, exits, and compatible modifiers. Each coordinate selects a deterministic room graph, assembles compatible templates, validates paths, then applies a bounded number of seeded changes. Store its generator version and saved state for revisits.

## DLC and third-party integrations

Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional content layers. Content should load only when its DLC exists, and the campaign must retain a Core-only route. Hospitality, prisoner, storage, research, vehicle, and power mods are optional integration examples from the 294-profile research target. Core systems should avoid undocumented or unreviewed bridges.
