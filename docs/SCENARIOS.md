# Rimrooms - Async Industries: campaign scenarios

**Status:** design contract for selectable campaign openings. Async Industries is the first playable implementation target; this file describes the shared rules and the planned alternate starts. The scenario list is extensible, but each added start must pass the common contract below.

## Why scenarios exist

Rimrooms should support different ways into the Backrooms company/survival loop. A player may start as a small research company, ordinary people confronting a breach in a retail basement, or a lone person already trapped inside. These are separate opening experiences that converge on shared coordinate, expedition, evidence, threat, and progression systems. Do not duplicate the procedural-space generator or campaign state for each opening.

The furniture-store threshold is a high-level cue from the [official A24 synopsis](https://a24films.com/films/backrooms), which describes a strange doorway in a furniture-showroom basement. Scenario events, staff, objectives, and implementation details remain original game design. The full feature review is still pending; see the [source register](SOURCE_REGISTER.md) and [film review template](research/reviews/templates/a24-feature-review-template.md).

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
| Dependency boundary | A complete route using RimWorld Core. DLC and profile mods can enhance a start but cannot be its only route. |
| Multiplayer eligibility | Declared as solo, co-op compatible, or unverified. Do not assume multiple players can select independent new-game scenarios inside one RWT world. |

Scenario generation may vary roster, stock, starting damage, early signals, and objective order by seed, but the opening must remain bounded and legible. The scenario chooses starting conditions; common campaign services own transactions, coordinates, evidence custody, gate/portal state, and saved progression.

## Planned opening scenarios

| Scenario ID | Opening | First objective | Route into the wider campaign | Implementation order |
| --- | --- | --- | --- | --- |
| `async_industries` | Underfunded headquarters, small staff, starter stock, unfinished/disabled machine gate, limited funds, and a project board. | Restore safe power, complete gate assembly/calibration, and retrieve one useful result with a prepared crew. | Becomes the full company-management campaign: hire, research, procure, defend, explore, lease, build, and expand. | First playable / vertical slice. |
| `furniture_knickknack_store` | Small retail business with ordinary staff/customers, furniture and knickknack stock, and an anomalous basement threshold. No established Backrooms corporation. | Secure the public area, account for missing people, and decide how to investigate or close the threshold. | Open a contracted investigation, evacuate into a rescue path, or turn the breach into a guarded company site with a later machine-gate connection. | After the facility vertical slice. |
| `lone_survivor` | One survivor starts inside a seeded Backrooms coordinate with field equipment, limited supplies, no facility, and a compromised/unknown route home. | Stay alive, learn a local rule, record a return clue, and choose whether to seek escape, rescue, or a foothold. | Escape/rescue unlocks company play; a successful foothold opens an independent outpost/solo expedition route. | After the facility vertical slice. |

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
- [ ] Remains playable without optional DLC or any of the 294 profile mods.
- [ ] Saves and reloads without duplicating starting pawns, items, buildings, objectives, contracts, or rewards.
- [ ] Generated destinations remain reproducible and revisitable under their saved coordinate and generator version.
- [ ] Joins or is excluded from RWT co-op based on a pinned-build result; mixed scenario starts are not promised before that result.
- [ ] Records the tested game/DLC/mod/RWT profile and save/log evidence in the project.

## Source and implementation links

- [Game design](GAME_DESIGN.md) — campaign loop and first playable scope.
- [System catalog](SYSTEMS_CATALOG.md) — scenario opening matrix and related systems.
- [Multiplayer/mod integration plan](MOD_INTEGRATION_PLAN.md) — RWT scenario-selection constraint.
- [Technical architecture](TECHNICAL_ARCHITECTURE.md) — save ownership and stable coordinate contracts.
- [Pre-production backlog](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) — scenario design gate and implementation phases.
- [Source register](SOURCE_REGISTER.md) — source URLs, local references, and research status.
