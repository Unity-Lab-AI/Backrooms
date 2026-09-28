# Rimrooms - Async Industries: first-slice content inventory

**Status:** pre-code content contract, version 0.1. Names and counts below are original working content for the first playable. They are not shipped assets, final lore, or tested game behavior. The slice remains Core-only and single-player-capable.

**Purpose:** make the Async Industries opening concrete enough to prepare implementation without expanding the first build into the whole campaign. Shared systems and optional integrations are mapped in [FEATURE_TRACEABILITY.md](FEATURE_TRACEABILITY.md), [SYSTEMS_CATALOG.md](SYSTEMS_CATALOG.md), and the [294-mod register](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx).

## Opening site and company

Use the canonical start card in [SCENARIOS.md](SCENARIOS.md): a 60×60 headquarters, five company pawns, a provisional $50,000,000 Company Account, 150 physical silver, starter stock, an incomplete gate, and an already accepted onboarding survey. The starting faction belongs to the player's branch. Nearby factions begin neutral. The start is not a crashlanded story.

| Content group | First-slice roster | Player use |
| --- | --- | --- |
| People | Operations lead, researcher, engineer, security guard, medic/logistics generalist | Roles help the player understand assignments; any capable pawn can cover a task. No named pawn is required. |
| Facility | Gate chamber, power room, workshop, research bench, receiving/storage, small infirmary, dormitory, mess/recreation area, secured entrance | Each area has a visible building or stock function. No hidden room score gates progress. |
| Machine | Incomplete gate frame, control console, emergency cutoff, utility generator, reserve battery | Finish assembly, verify power, assign an operator, open and recall once. |
| Starting stock | 250 steel, 18 components, 2 advanced components, five days of food for the five staff, medicine for two serious treatments, two serviceable firearms, one protective vest | The final gate step uses 100 steel and 8 components. Existing stock covers the first expedition; no purchase is needed to complete it. |
| Field kit | One recorder/radio, six numbered survey tags, one short return tether/beacon, one sealed evidence case, basic medical supplies, guard's firearm and vest | The crew can record a route, identify a changed doorway, request recall, stabilize a sample, and retreat. These are original Rimrooms items and need their own art, text, and Def records. |
| Company records | Accepted AI-01 onboarding survey, branch-local USD Company Account ledger, coordinate card, first case record | Show what the company asked for, what the crew found, and why payment was posted. |

The named field-kit items are already included among the starting resources on the [`async_industries` scenario card](SCENARIOS.md); they are not an additional starting grant. Allocate those physical items to the field loadout exactly once, then record their return, consumption, damage, or loss normally. They must not silently duplicate on reload.

## First destination: AI-01

Generate a stable, finite site of six to eight connected rooms under the shared [procedural space contract](PROCEDURAL_SPACE_CONTRACT.md). Room names are working labels, not canonical Backrooms locations. Each valid site has an entry/return point, a route clue, one environmental distortion, one hostile-entity encounter opportunity, and a small evidence lead. The route to the gate remains recoverable if optional rooms are unexplored.

| Room family | Required or optional | Content purpose |
| --- | --- | --- |
| Threshold Room | Required | Safe entry, expedition start, and validated route back to the gate. |
| Survey Lobby | Required | First room map, coordinate marker, and place to read the mission card. |
| Office Copy | Required or equivalent | The AI-01 route recording and one evidence lead. Details and text are original. |
| Service Passage | Required | Route-tag teaching space and approach to the first distortion. |
| Borrowed Corridor | Required event room | Hosts the bounded loop described in [the first threat sheets](THREAT_DESIGN_SHEETS.md). |
| Storage Nook | Optional | One piece of ordinary furniture or labeled salvage; taking it uses the crew's cargo capacity. |
| Utility Room | Optional | A dead-end room with an environmental clue, not a mandatory gate-control puzzle. |
| Return Gallery | Required or equivalent | Connects to the validated exit route; its visual label remains readable without color or sound. |

The generator selects compatible templates from these families; a valid map need not use every optional room. Room adjacency, doors, walkability, mission objects, and a return path must be checked before the expedition begins. Preserve the exact generated coordinate on revisit. Do not copy a specific Kane or A24 room layout, prop arrangement, shot, or sequence.

## Expedition content

- **Crew:** up to three field pawns; keep a qualified gate operator at headquarters.
- **Objective:** map the assigned route, record the room count and distortion, recover the route recording, and return it to the facility.
- **Timing:** one 20 in-game minute opening, with warnings at 10, 5, and 2 minutes remaining. Recall is always available before the final return limit.
- **Cargo:** one shared field loadout for the three-person crew, using the equipment quantities listed above and including its single sealed evidence case; optional furniture uses the displayed mass/carry limit. Exact limits are tuning hypotheses in the [first playable contract](FIRST_PLAYABLE_CONTRACT.md).
- **Evidence:** one physical AI-01 Route Recording item and a linked case entry. It records contradictory room/timing observations without explaining the setting's cause.
- **Contract result:** one $5,000,000 payment and one research insight for a valid extraction. An optional $1,000,000 bonus pays if all three crew return with the route, distortion, and entity-observation records. A recoverable injury does not cancel the bonus, and neither the bonus nor entity combat is required for contract completion. These are editable pre-code targets, not tested prices.
- **Research follow-up:** Gate Telemetry is the first local project. It turns the recorded evidence into a concrete improvement to repeat-site planning. It consumes the earned insight and staffed research work; it does not require a DLC or another mod.
- **Threat response:** the crew may observe and retreat, use the guard and firearm to force distance, or spend time laying tags and checking the route. Killing or capturing the first entity is not required for contract payment or research access.

## First-session teaching order

1. Read the opening objective and inspect the company account separately from physical silver and stock.
2. Assign an operator, finish the gate step, and review the power reserve.
3. Choose three ready pawns. The launch screen names their jobs, supplies, route, and return reserve.
4. Read the AI-01 mission card, enter, tag the first junction, and record what the room map shows.
5. Identify the repeated-route clue, see the entity's warning, then decide whether to document, repel, or recall.
6. Return, reconcile the manifest, secure the recording, analyze it, and receive the one-time reward.
7. Choose Gate Telemetry or a follow-on survey. Both paths lead to a second preparation decision.

## Included and deferred

The first slice includes one headquarters, one coordinate, one accepted survey, one repeatable environmental distortion, one original entity behavior, one evidence item, one research follow-up, and one reward path. It does not include hires beyond the starting roster, prisoner interviews, entity capture, settlement openings, long leases, outposts, gravship operations, synchronized research, live shared maps, the Store start, or the Lone Survivor start. Those systems keep their broader contracts in [SCENARIOS.md](SCENARIOS.md), [SYSTEMS_CATALOG.md](SYSTEMS_CATALOG.md), and the master [pre-production backlog](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

## Lore and style route

The fan notes for [The Backrooms (Found Footage)](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-01), [First Contact](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-04), [Missing Persons](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-05), and [Informational Video](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-07) are story prompts about disorientation, unstable entry, route marking, and missing crews. They are secondary fan summaries, not creator-confirmed rules. Use the separately documented [A24 story note](research/reviews/a24-feature/feature-review.md) only for film-derived ideas. Room names, company procedures, threats, objects, and mission outcomes in this inventory are original Rimrooms design; see the [adaptation boundaries](UNIVERSE_ADAPTATION.md) and [visual/audio brief](research/VISUAL_AUDIO_STYLE_BRIEF.md).

## Implementation handoff

For each content record, reserve a stable ID, localized label/description, owner, save key, required item/building/job, player-facing route, failure message, recovery path, optional-mod/DLC rule, and acceptance evidence before implementation. The first site's generated layout and threat state must survive save/load without rerolling or duplicating evidence. This inventory describes the target; it does not establish an API, asset license, compatibility result, or runtime acceptance.

The first-slice feature owners, relevant reviewed 294-profile rows, source-backed provisional treatments, explicit deferrals, and pending FS-01–FS-07 acceptance checks are mapped in the [first-slice mod interaction map](research/FIRST_SLICE_MOD_INTERACTION_MAP.md).

