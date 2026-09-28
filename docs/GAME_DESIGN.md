# Game design brief

## High concept

Run one of several Backrooms campaigns that open temporary routes into an enormous, unstable interior world. In the company campaign, the colony is headquarters; in other scenarios the player may begin at a retail breach or already trapped inside. Each start changes the initial situation and objectives, then uses the same persistent coordinate, expedition, evidence, danger, and progression systems.

The default **Async Industries** opening is not a standard crashlanded-colony start with a new monster faction pasted on. It establishes a company project, a small facility, an incomplete machine, a small roster, starter equipment, and a clear first objective: make the gate safe enough to open and bring back a valuable result. The other scenarios deliberately provide different openings rather than forcing this setup on every player.

## Player promise

The player grows a fragile operation into a network of secure facilities and forward posts. They decide what to fund, who to train, what to risk, which spaces to revisit, what to bring home, and what to contain, study, sell, or destroy. The Backrooms should feel much larger than the player's ability to understand it; reliable knowledge is earned through repeated expeditions.

## Scenario framework and opening scenarios

The complete starting-state schema, additional scenario candidates, and scenario acceptance checklist are maintained in [SCENARIOS.md](SCENARIOS.md). This section is the player-facing overview; use the canonical contract before implementation.

Scenarios are selectable campaign presets. A preset supplies a starting map or location, pawn roster, relationships, inventory, funds, gate/portal state, known coordinates, early incidents, and first objectives. It changes the entry point and pressure profile; it must not fork the procedural-space generator or duplicate the shared evidence, coordinate, and expedition systems.

| Scenario | Opening state | First objective | Path into the wider campaign |
| --- | --- | --- | --- |
| **Async Industries** (default/recommended) | A small research/security facility, several staff, limited funds, starter supplies, and an incomplete machine gate. | Restore safe power, finish calibration, staff a field crew, and return with useful evidence. | Build the company, grow gate capacity, contract work, and open outposts. |
| **Furniture & Knickknack Store** | A modest furniture and curios shop with an anomalous basement opening, ordinary staff/customers, store inventory, and no established Backrooms company. This is a game adaptation of the ordinary showroom threshold described by A24, not a scene-for-scene retelling. | Secure the shop, account for missing people, investigate the opening, and decide whether to report, contain, or exploit it. | Establish a company/contract relationship and convert the shop into a controlled access or supply site. |
| **Lone Survivor** | One survivor, field equipment, and a damaged or inaccessible route home, already inside a seeded Backrooms coordinate. No surface facility or functioning company is assumed. | Stay alive, discover reliable spatial rules, secure shelter and a return route, and decide what evidence or equipment can be carried out. | Escape to the surface to trigger a rescue/company campaign, or establish a limited forward outpost before contact. |

Later scenario candidates include an isolated outpost with a lost radio relay, a town-scale distortion response, and an established corporation under financial/security pressure. They should use the same data-driven scenario format. The lone-survivor route must retain a valid start, save/load, and return path even when it cannot use company facilities at first.

## Core campaign loop

1. **Fund the operation.** Take contracts, sell recovered materials or research, and order equipment and supplies.
2. **Prepare the facility.** Build power, storage, work areas, living quarters, food and recreation, medical support, and layered security.
3. **Staff the project.** Recruit or hire researchers, engineers, guards, logistics staff, and field specialists. Train them and manage their health, needs, skills, traits, and beliefs.
4. **Plan a run.** Select a known coordinate or investigate a new signal; assign a crew, equipment, carrying capacity, return route, and gate window.
5. **Explore and extract.** Search procedurally assembled spaces, follow clues, face environmental hazards and entities, and choose what to carry back.
6. **Recover and contain.** Close the gate, treat survivors, secure evidence, detain or isolate dangerous arrivals, and investigate missing or altered crew.
7. **Convert results into progress.** Analyze samples, furniture, equipment, recordings, and recovered objects. Complete client work, unlock research, and invest in the next operation.

## Campaign stages

### 1. The first facility

The company starts short on cash, power, tools, staff, storage, and trustworthy information. Initial work teaches room designation, stock control, staffing priorities, basic security, and gate assembly. The first expedition is short and has a clear recall threshold.

### 2. Repeatable expeditions

The gate can reopen known coordinates. Crews place markers, record route clues, establish return points, and improve the team's survival odds. Better power and machine parts extend a gate opening from minutes to hours. The player must weigh value against exposure and loss.

### 3. Connected operations

The company builds radio and supply points, outposts, forward shelters, recovery stations, and better transport. Known spaces can be revisited, but their layouts, hazards, and contents may shift. Contracts can ask for surveys, retrieval, rescue, sample analysis, or controlled construction.

### 4. Reality incidents

Openings occur away from company control: settlements report missing people, structures change, expeditions return incomplete, and equipment or witnesses appear in the wrong place. These are world events and quests that force a choice between secrecy, rescue, containment, and profit.

### 5. Deep operations

The facility becomes a major organization and can support multiple teams and remote sites. New technology improves route mapping and gate stability while exposing spaces with more complex rules, fragmented architecture, and threats that respond to previous company activity. “Infinite” means a practically renewable, seeded chain of destinations, not an unbounded live map held in memory.

## Major systems

### Facility and company operations

- Start with a defined company scenario, starter inventory, budget, project board, and gate blueprint.
- Reuse RimWorld's building, power, temperature, stockpile, work, needs, health, research, and combat systems wherever they already fit.
- Add company-specific tasks for machine assembly, gate calibration, sample processing, transcript analysis, equipment maintenance, containment, and contract fulfillment.
- Give each important room a function: gate control, lab, evidence archive, armory, decontamination, medical bay, storage, workshop, kitchen/cafeteria, dormitory, office, radio room, or recreation.
- Let room use emerge from furniture, zones, facilities, and assignments instead of requiring an opaque room score for every feature.

### Personnel, hiring, and training

- Use pawns as staff. Company roles guide work priorities and equipment but do not replace pawn skills, traits, health, needs, passions, relationships, or beliefs.
- Hiring can use generated candidates, rescue/recruitment outcomes, or contract rewards. Later systems may support specialists and short-term contractors.
- Add training projects for field readiness, medical handling, laboratory procedure, engineering, navigation, security, and anomaly response.
- Create meaningful differences between a trained team and an interchangeable squad: skills, equipment familiarity, stress, loyalty, field notes, and prior experience should matter.

### The machine gate and expeditions

- Treat the gate as a buildable, powered, serviceable machine with calibration, operating cost, instability, and exposure.
- Opening duration scales with components, research, operator skill, power reserve, and prepared return infrastructure.
- A mission card names the destination, known features, expected risks, requested cargo, gate window, and available recall tools.
- Each generated destination receives a stable seed and a company coordinate. Reopening the coordinate should recover the site's saved state, while permitted anomalies may change selected features.
- Return beacons, radios, tether equipment, mapped corridors, and staffed relay points are progression tools, not free guarantees.

### Procedural spaces

- Assemble maps from room and corridor templates, then apply controlled modifiers based on the coordinate, equipment, recorded phenomena, and difficulty tier.
- Room families may include offices, service tunnels, storage areas, medical spaces, unfinished construction, retail back rooms, mechanical rooms, impossible apartments, and spaces that repeat or reconfigure.
- Give each room definition tags for shape, size, lighting, materials, entrances, hazards, points of interest, loot, exits, and compatible modifiers.
- Ensure generated maps retain traversable routes and a legible way to return. Weird geometry should remain playable and diagnosable.
- Increase complexity by combining known rules and a few new rules at a time. Avoid random visual noise that has no gameplay consequence.

### Research, evidence, and technology

- Separate general engineering, gate science, fieldcraft, spatial mapping, containment, medical/anomaly research, communications, logistics, and advanced propulsion.
- Make research depend on observations, recovered samples, recordings, functional equipment, and safe lab infrastructure as well as researcher skill.
- Discover technology through evidence and project work; do not force every tree branch to be a generic research bench unlock.
- Build advanced gates, longer openings, map tools, extraction gear, protective equipment, remote supply, and large-scale transport as earned capabilities.

### Economy and procurement

- Track company funds separately from ordinary silver only if the custom interface can explain the distinction clearly. Otherwise begin with silver plus a company ledger.
- Offer contracts with payment, advance supply, deadlines, requested evidence, and consequences for loss or breach.
- Allow legal procurement through traders, comms, and scheduled shipments; later add internal company logistics and outpost re-supply.
- Make recovered furnishings and technology useful as cargo, samples, blueprints, or resale goods. Some discoveries should be too dangerous or valuable for ordinary sale.
- Every profit opportunity should have a cost: wages/food, machine upkeep, medical treatment, compensation, containment, or lost equipment.

### Threats, containment, and investigation

- Threats include entities, environmental effects, route failures, spatial distortions, equipment malfunctions, and human decisions.
- A returned person or object can start an investigation chain: quarantine, interview, examination, transcript comparison, identification, and disposition.
- Detention should use RimWorld's prisoner and guest concepts where they fit, with custom company case records and decisions layered on top.
- Lost crews should generate recoverable clues, radio contact, rescue missions, or confirmed outcomes rather than disappearing only as a hidden percentage roll.
- Give each creature or anomaly clear tells, rules, countermeasures, and evidence. Mystery comes from incomplete knowledge, not arbitrary instant death.

### World map, space, and incidents

- Use RimWorld's world map and quest/site machinery for destination sites, outposts, settlements affected by distortions, and interplanetary travel where supported.
- Establish a controlled route from ground expeditions to larger-scale space travel. The player's company technology repurposes familiar RimWorld capabilities for gate research and expansion.
- Outposts need supply, communication, defense, staffing, and a reason to return to headquarters. They should not become unrelated permanent colonies that dilute the gate loop.

## Company interface

The interface should make the unusual campaign legible without hiding core RimWorld information. Add an **Operations** board for staff roster, projects, finance, gate status, expedition planning, coordinate records, contracts, incidents, and outposts. Reuse vanilla Architect, Work, Research, Assign, and World tabs where possible. Do not replace every vanilla menu in the first playable version; replace or reorganize screens only after the company workflow is proven.

## First playable acceptance target

The first playable focuses on **Async Industries**: a new save starts at its facility; the player can build and power the machine, complete its assembly project, recruit or assign a viable crew, open one seeded expedition site, explore and extract, close/recall through the gate, return to the same saved coordinate, analyze the recovered evidence, receive a payment or research reward, and survive a threat event. Its v0.1 target values and acceptance checks are in the [first playable contract](FIRST_PLAYABLE_CONTRACT.md). The scenario framework and the Store and Lone Survivor starts are defined in [SCENARIOS.md](SCENARIOS.md) and implemented after the vertical slice proves the shared systems. The co-op design target is separate player branches that can exchange only tested items/dossiers, send supported aid, and visit another facility only if the pinned RWT build and settings expose a safe visit route. Each branch keeps its own gate, map, staff, research completion, contracts, and ledger; the design does not promise live shared-map control or synchronized company research. Test whether distinct scenario starts can coexist in one RWT server before making that a support promise. See the [complete multiplayer and systems plan](MOD_INTEGRATION_PLAN.md#2-cooperative-company-model).
