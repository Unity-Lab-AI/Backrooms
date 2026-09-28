# Rimrooms - Async Industries: campaign scenarios

**Status:** design contract for selectable campaign openings. Async Industries is the first playable implementation target; this file describes the shared rules and the planned alternate starts. The scenario list is extensible, but each added start must pass the common contract below. Use the linked [first-slice inventory](FIRST_SLICE_CONTENT_INVENTORY.md), [threat sheets](THREAT_DESIGN_SHEETS.md), and [economy model](CAMPAIGN_ECONOMY_MODEL.md) with this contract.

**Selected dependency contract:** all three starts remain playable on Core without DLC or optional profile mods. Co-op requires Harmony/RWT; the rest of the 294 profile is optional. See [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md).

## Why scenarios exist

Rimrooms should support different ways into the Backrooms company/survival loop. A player may start as a small research company, ordinary people confronting a breach in a retail basement, or a lone person already trapped inside. These are separate opening experiences that converge on shared coordinate, expedition, evidence, threat, and progression systems. Do not duplicate the procedural-space generator or campaign state for each opening.

The furniture-store threshold is a high-level cue from the [official A24 synopsis](https://a24films.com/films/backrooms), which describes a strange doorway in a furniture-showroom basement. Scenario events, staff, objectives, and implementation details remain original game design. A separate, secondary fan-summary story note is recorded in the [feature review file](research/reviews/a24-feature/feature-review.md); A24 production notes establish an Async branch and callbacks to the web series, but the film's detailed plot and the game's scenario remain separately documented.

## Shared scenario contract

Every scenario definition must provide:

| Field | Required behavior |
| --- | --- |
| Stable scenario ID and schema version | Remains stable across saves and scenario updates; changed layouts use explicit migration rules. |
| Starting context | Starting map/site, owning faction, pawns and relationships, inventory/funds, buildings, gate or portal state, known coordinates, and initial cases/evidence. |
| Seed and identity | Any generated Backrooms start has a saved coordinate ID, seed inputs, generator version, and a deterministic initial room graph. Reloading must not silently create a new destination. |
| Objectives and tutorial | Ordered or branching first objectives, clear completion/failure signals, relevant tutorial messages, and no dependency on one specific UI layout. |
| Failure and recovery | Explicit handling for death, incapacitation, lost gear, sealed route, failed generation, broken gate, or abandoned settlement as applicable; no unrecoverable softlock. |
| Convergence | A documented route into shared systems: company operation, paid investigation, rescued survivor, established outpost, or continued solo expedition. Convergence must preserve evidence and coordinate identity. |
| Save/load idempotency | New-game grants, map setup, objectives, quests, items, pawns, and site links must not duplicate after reload or migration. |
| Dependency boundary | Complete solo route using RimWorld Core. All five DLC and other 294-profile mods are optional. Harmony/RWT are required for co-op only. |
| Multiplayer eligibility | Declared as solo, co-op compatible, or unverified. Do not assume multiple players can select independent new-game scenarios inside one RWT world. |

Scenario generation may vary roster, stock, starting damage, early signals, and objective order by seed, but the opening must remain bounded and legible. The scenario chooses starting conditions; common campaign services own transactions, coordinates, evidence custody, gate/portal state, and saved progression.

## Planned opening scenarios

| Scenario ID | Opening | First objective | Route into the wider campaign | Implementation order |
| --- | --- | --- | --- | --- |
| `async_industries` | Underfunded headquarters, small staff, starter stock, unfinished/disabled machine gate, limited funds, and a project board. | Restore safe power, complete gate assembly/calibration, and retrieve one useful result with a prepared crew. | Becomes the full company-management campaign: hire, research, procure, defend, explore, lease, build, and expand. | First playable / vertical slice. |
| `furniture_knickknack_store` | Small retail business with ordinary staff/customers, furniture and knickknack stock, and an anomalous basement threshold. No established Backrooms corporation. | Secure the public area, account for missing people, and decide how to investigate or close the threshold. | Open a contracted investigation, evacuate into a rescue path, or turn the breach into a guarded company site with a later machine-gate connection. | After the facility vertical slice. |
| `lone_survivor` | One survivor starts inside a seeded Backrooms coordinate with field equipment, limited supplies, no facility, and a compromised/unknown route home. | Stay alive, learn a local rule, record a return clue, and choose whether to seek escape, rescue, or a foothold. | Escape/rescue unlocks company play; a successful foothold opens an independent outpost/solo expedition route. | After the facility vertical slice. |

## Pre-code start cards: v0.2 balance hypotheses

These cards make the opening playable on paper before code begins. Counts, costs, map dimensions, and timings below are **tuning hypotheses**, not owner-approved canon or proven RimWorld behavior. Keep them together as scenario data so balancing does not require changing the shared campaign rules. Names, traits, relationships, and nonessential stock can vary by seed; required capabilities and routes cannot.

### `async_industries` — first vertical slice

- **Starting site and faction:** one 60×60 headquarters map. The five controlled staff belong to the player's company faction; ordinary neighboring factions begin neutral. The facility has a secured perimeter, small dormitory, mess area, storage, infirmary corner, workshop, research bench, one utility generator with a small reserve battery, and an unfinished gate chamber. The gate is assembled to roughly three-quarters and cannot open yet.
- **Starting people:** five generated staff: one operations lead, one researcher, one engineer, one guard, and one medic/logistics generalist. Ensure at least one pawn can perform each essential first-slice task. Roles are assignments, not locked classes; any suitable staff member may cover another role.
- **Starting resources and offer:** 250 steel, 18 components, 2 advanced components, five days of food, basic medicine for two serious treatments, two serviceable firearms, one protective vest, ordinary room furnishings, one recorder/radio, six numbered survey tags, one short return tether/beacon, and one sealed evidence case. The branch starts with a provisional **$50,000,000 authorized Company Account**; physical petty cash remains 150 silver. The project board includes one already-accepted onboarding survey with a **$5,000,000** payment for valid first-extraction deliverables and an optional **$1,000,000** records bonus if all three crew return with the route, distortion, and entity-observation records. A recoverable injury does not cancel the bonus. The parent-company valuation is not branch cash. Company orders still have to arrive as physical items before use.
- **Gate and first coordinate:** the gate needs a final 100 steel and 8 components, stable power, and an assigned operator. The first open window is 20 in-game minutes. Initial coordinate `AI-01` is a saved, seed-derived site with 6–8 rooms, one safe rest/return point, the Borrowed Corridor route distortion, one bounded Quiet Pursuer encounter, one recoverable evidence lead, and a clear exit route. The first run teaches recall, investigation, and a fight-or-retreat choice; it does not require a pawn sacrifice.
- **Opening objectives:** restore reserve power; finish and calibrate the gate; appoint an operator and a three-person field crew; review the already-accepted onboarding survey and mission card; enter `AI-01`; tag the first junction, record the route anomaly, and recover the recording with its separate physical case; encounter the Quiet Pursuer and choose whether to repel it or withdraw; return before the window closes; secure the find; complete the first analysis; then choose an AI-01 resurvey or Gate Telemetry research. Generated paid follow-on contracts are a Phase 3 requirement.
- **Failure and recovery:** insufficient power, missing operator, incomplete gate, or invalid return route prevents dispatch with a direct reason and a fix. An abort before entry returns the crew and preserves supplies. A recall during the expedition returns the crew through the last validated route and leaves optional cargo behind. Injury, death, or a sealed route creates a case and a recovery lead; it never silently deletes the expedition record. If no usable route can be generated, keep the gate closed and offer a reroll under a new coordinate ID.
- **First success and convergence:** completing the accepted onboarding survey posts its provisional $5,000,000 payment once and grants one research insight, marks `AI-01` known, and opens the repeat-expedition loop. The optional $1,000,000 bonus is a separately listed contract term. The branch is already the company campaign; success then supports follow-on hiring, procurement, better gate capacity, site revisits, and later outposts.
- **Co-op status:** target for Core solo and the pinned RWT/Harmony co-op baseline. Distinct players' scenarios, shared research, and remote facility visits stay unpromised until the exact RWT profile passes the disposable-server test.

### `furniture_knickknack_store` — breach investigation

- **Starting site and faction:** one 50×50 shop map. The owner, employee, and guard belong to the player's small local store faction; nearby settlement factions begin neutral. The map has a sales floor, stockroom, office, staff room, and a basement containing a narrow anomalous threshold. The threshold is not a working machine gate. Store walls, doors, and stock use original scenario setup and available RimWorld content; no third-party mod assets are copied into the project.
- **Starting people:** three controlled people: the owner/manager, one employee, and one capable night guard. Up to two ordinary visitors can be present as independent visitors; one expected customer is already missing when the scenario begins. Visitor handling must have a Core-only route and cannot depend on Hospitality.
- **Starting resources:** store stock worth an estimated 500 silver in ordinary furnishings and curios, 200 silver in the till, two days of food, basic first aid, and a radio with unreliable reception. The store begins outside a corporate branch account; its opening investigation offer may advance a provisional $500,000 against a separately quoted multi-million-dollar contract. The scenario begins without company research, a corporation, or a powered machine gate.
- **First incident and choices:** secure the public entrance and basement; account for staff and visitors; then choose one of three readable approaches: evacuate and seal the basement, conduct a short supervised search for the missing customer, or document the threshold and request outside help. Each choice records what was secured, who is missing, and which evidence was recovered. The first threshold trip uses a bounded 4–6-room site with a generated return clue.
- **Failure and recovery:** a breached perimeter raises an incident and limits access but does not delete the shop. A pawn injury triggers ordinary medical recovery. A failed search can still return a clue and open a later rescue lead. The player can close the threshold and continue the shop's ordinary survival loop, or reopen only after a visible safety action.
- **Convergence:** completing the initial incident creates a paid investigation offer. Accepting it establishes a branch ledger and research case for this player, lets the shop operate as a contracted local site, and opens procurement of a small machine-gate kit. Refusing keeps the store as a self-contained breach campaign with optional later recruitment. The same coordinate/evidence/contract records are used in either route.
- **Co-op status:** solo first. Do not assume this and Async Industries can be selected by different players on the same RWT server until tested.

### `lone_survivor` — inside start

- **Starting site and faction:** one generated 6–8-room coordinate. The player controls the sole survivor as a one-person local faction; no outside factions or allies are assumed present or already contacted. The site has a restable shelter, limited supplies, at least two connected route clues, and a traversable path to the initial objective and a possible exit. Save the coordinate ID, seed, and generator version at new game.
- **Starting person and kit:** one survivor with a varied, seed-generated background but enough baseline skills to tend wounds, repair simple equipment, and understand clues. Start with five meals, two medical supplies, a field recorder, a light source, a basic repair tool, a short-range radio with one damaged battery, and one clearly marked personal item. No company, facility, gate, or allies are assumed.
- **Opening objective:** secure a rest point; identify one environmental rule from an observable tell; mark two route clues; and choose whether to follow the exit lead, attempt radio contact, or prepare a tiny supply foothold. The player should see the survival pressure and a plausible route forward before committing to a long exploration.
- **Failure and recovery:** starvation, exposure, injury, and threat outcomes use ordinary RimWorld needs and combat. If the survivor is downed, show whether a known route or rescue signal can reach them; never claim a guaranteed rescue where no relay exists. Death ends the survivor's active run but retains its case, coordinate, and clues as a new rescue/investigation lead when the player elects to continue with a later company start.
- **Convergence:** an escape lead reaches a surface contact and opens a rescue/contract route; a radio response can establish a small remote outpost; or the player may keep exploring as a solo expedition. These outcomes enter the same coordinate atlas, evidence custody, case, and contract systems without retroactively inventing a staffed headquarters.
- **Co-op status:** solo until mixed-start behavior is demonstrated on the pinned RWT release. A lone-survivor pawn is not automatically transferred to another player's branch.

## Later candidate scenarios

These are options for future scenario content, not promised release features. Give each an owner-approved objective chain and acceptance criteria before implementation.

| Candidate | Opening premise | Distinct pressure | Likely convergence |
| --- | --- | --- | --- |
| `isolated_outpost` | A remote company post loses its radio relay and supply link. | Small crew, low stock, unreliable communications, and uncertain evacuation. | Restore a route, call aid, or operate as a self-sufficient site on the corporate network. |
| `town_distortion` | A settlement reports an unstable opening and missing residents. | Public safety, witnesses, time pressure, perimeter security, and limited authority. | Paid investigation, rescue, follow-up contracts, or permanent monitored site. |
| `company_in_crisis` | An existing branch begins with debts, damaged infrastructure, and a missing crew. | Payroll, security, reputation, and recovery compete with research and expansion. | Rebuild a viable facility and reopen expeditions. |

## Acceptance checklist for each implemented scenario

- [ ] Appears with an accurate name and opening summary in scenario selection.
- [ ] Has a unique new-game setup and shares the same stable campaign, coordinate, and evidence services.
- [ ] Gives every start an actionable first objective, visible failure state, and recovery/exit route.
- [ ] Remains playable without optional DLC or the optional 294-profile mods; co-op setup requires the pinned Harmony/RWT stack.
- [ ] Saves and reloads without duplicating starting pawns, items, buildings, objectives, contracts, or rewards.
- [ ] Generated destinations remain reproducible and revisitable under their saved coordinate and generator version.
- [ ] Joins or is excluded from RWT co-op based on a pinned-build result; mixed scenario starts are not promised before that result.
- [ ] Records the tested game/DLC/mod/RWT profile and save/log evidence in the project.

## Source and implementation links

- [Game design](GAME_DESIGN.md) — campaign loop and first playable scope.
- [Campaign content catalog](CAMPAIGN_CONTENT_CATALOG.md) — progression arcs, research themes, mission families, threats, spaces, and long-term company expansion.
- [First playable contract](FIRST_PLAYABLE_CONTRACT.md) — provisional Async Industries starting values, opening loop, gate/expedition behavior, and future acceptance evidence.
- [System catalog](SYSTEMS_CATALOG.md) — scenario opening matrix and related systems.
- [Multiplayer/mod integration plan](MOD_INTEGRATION_PLAN.md) — RWT scenario-selection constraint.
- [Technical architecture](TECHNICAL_ARCHITECTURE.md) — save ownership and stable coordinate contracts.
- [Pre-production backlog](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) — scenario design gate and implementation phases.
- [Source register](SOURCE_REGISTER.md) — source URLs, local references, and research status.
