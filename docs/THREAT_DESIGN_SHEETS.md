# Rimrooms - Async Industries: threat and distortion design sheets

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** pre-code design contract, version 0.1. The two first-slice entries are original game design, not confirmed Backrooms canon or tested behavior. Later entities and anomalies need their own completed sheets before their Defs or quests are implemented.

**Feature route:** [RR-THREAT](FEATURE_TRACEABILITY.md), [RR-SPACE](FEATURE_TRACEABILITY.md), [RR-EXP](FEATURE_TRACEABILITY.md), [RR-EVD](FEATURE_TRACEABILITY.md), and [RR-MSN](FEATURE_TRACEABILITY.md). The initial encounter is specified in the [first playable contract](FIRST_PLAYABLE_CONTRACT.md) and [content inventory](FIRST_SLICE_CONTENT_INVENTORY.md).

## Shared design rules

- Every encounter has a visible or otherwise accessible warning, a learnable rule, at least one countermeasure, and a recorded outcome.
- Do not use color or sound as the only way to notice a tell. Pair visual changes with a label, map marker, text alert, or other clear cue.
- A threat may surprise the player, but first contact must not kill a healthy pawn instantly or erase the return route without warning.
- The player can learn, avoid, repel, contain, study, trade, sell, or abandon a threat only where that behavior is explicitly specified. Do not grant a hidden capture, sale, or research result.
- Threat effects are bounded, seed-stable, logged against a coordinate, and recoverable after saving and reloading.
- Source story notes can suggest a mood or question. Use original names, shapes, text, rooms, and event sequences; do not treat fan summaries as rules from the series.

## RR-D-001 — The Borrowed Corridor

**Type:** environmental route distortion. **First-slice status:** required once on AI-01. **Lore label:** original design inspired by uncertain routes and marked paths described in the series fan notes for [Found Footage](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-01), [Missing Persons](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-05), and [Informational Video](research/KANE_PIXELS_FAN_CLIFF_NOTES.md#episode-07). The exact loop rule below is invented for Rimrooms.

| Rule | First-slice behavior |
| --- | --- |
| Tell | The room/map label repeats after the crew passes a tagged junction. A numbered survey tag appears on the wrong side of the familiar doorway. A text alert says the route and physical landmark disagree. |
| Trigger | The event can activate once when the crew crosses the seeded Borrowed Corridor connection. It cannot activate again during the same opening. |
| Effect | The familiar-looking doorway returns the crew to the last validated junction and consumes 3 reported in-game minutes. It does not create an unbounded graph loop or silently move the gate exit. |
| Counterplay | Stop at the mismatch, compare the numbered tags, place the short return beacon at the known junction, and follow the last validated route. The player may recall immediately instead of investigating. |
| Risk | Ignoring the mismatch costs time and can leave optional salvage behind. The event alone causes no injury and cannot kill a pawn. The creature encounter below supplies the first combat decision. |
| Evidence | The route recording stores the duplicated room label and mismatched tag position. A researcher can use it for Gate Telemetry. |
| Recovery | Recall uses the saved validated path. If path recovery fails, dispatch is refused or the expedition returns to the last valid point with a case note; it never rerolls AI-01. |
| Accessibility | Use a map-label change, numbered tag, and written alert. Sound can add atmosphere but never carries the only warning. |

## RR-ENT-001 — The Quiet Pursuer

**Type:** original hostile entity. **First-slice status:** one bounded sighting on AI-01; it may injure a pawn, but capture is deferred. Its working name and appearance are not taken from a Kane Pixels or A24 character.

| Rule | First-slice behavior |
| --- | --- |
| Appearance | A distant upright figure holds still beyond the crew's light or view. Use an original silhouette and readable posture; avoid a direct recreation of a video or film shot. |
| Tell | The figure appears two rooms away. It is visibly nearer after two in-game minutes without the crew changing rooms or immediately after a loud action. The route recorder also records a missing interval. The UI logs its last seen room and distance. |
| Trigger | It appears once after the crew reaches the Borrowed Corridor. It advances one room every two in-game minutes while the crew remains in its connected area. A loud action advances it immediately instead of waiting. |
| Limit | It advances at most three rooms, never travels through the Threshold Room or validated gate exit, and does not spawn a second copy during the same opening. Its current state is saved on the site. |
| Counterplay | The crew can withdraw behind a closed door, keep moving along numbered markers, or use the guard's firearm to force it back one room. The crew gets a clear warning before it advances again. |
| Contact | If it reaches the crew and they remain in the same room through one further one-minute warning, it can strike one pawn once, causing a recoverable injury, then withdraw. It cannot one-hit kill a healthy pawn in this tutorial encounter. |
| Evidence | A clear observation, recorder gap, and a recovered trace are separate facts. A single sighting does not identify what the entity is or unlock capture. |
| Outcome | Retreating completes the onboarding survey if its required route record is returned. A fight is optional and cannot be the only way to finish the contract. Injuries follow ordinary medical care and are written to the expedition/case record. |
| Containment/sale | Not available in the first slice. Later capture, study, sale, detention, or disposal requires a separate containment, custody, and value contract. |
| Accessibility | Pair distance and warning text with the visible figure/map marker. Do not rely on footsteps, static, darkness, red overlays, or color alone. |

## Authoring sheet for every later threat

Complete this record before implementation and link it from [FEATURE_TRACEABILITY.md](FEATURE_TRACEABILITY.md):

| Field | Required answer |
| --- | --- |
| Stable ID and name | Unique internal ID plus player-facing name; note whether the name is provisional. |
| Type and intended use | Entity, environmental distortion, incident, equipment failure, or human decision; identify the scenario, quest, or coordinate that can use it. |
| Lore route | Cite the relevant series or separate film note. Label the source fact, fan interpretation, or original design; identify all invented behavior. |
| Appearance and tells | What players can see, hear, read, or measure before the effect occurs; provide redundant cues and accessibility alternatives. |
| Trigger and behavior | Exact trigger, selection conditions, action loop, range, duration, target, and what ends or interrupts it. |
| Limits and fairness | Maximum active count, escalation bound, warning interval, protected start/return areas, and conditions that prevent unavoidable instant failure. |
| Counterplay | At least one accessible player response, required gear/staff, time/cost/risk, and the result of each response. |
| Evidence and study | Physical/logged evidence, custody rules, confidence, analysis, unlock, and what remains unknown. |
| Capture and disposition | Whether capture exists; required room, staff, equipment, containment capacity, transfer rules, sale/study/release outcomes, and failure recovery. If not implemented, say so. |
| Save and generation | Stable coordinate/seed inputs, saved event state, duplicate prevention, revisit behavior, and migration behavior. |
| Dependencies and acceptance | Core path, optional DLC/mod handling, exact UI/job route, test profile, success cases, failure cases, save/reload evidence, and logs needed before claiming support. |

## Not yet designed

The Quiet Pursuer and Borrowed Corridor cover only the vertical slice. The other proposed monstrosities, world-town openings, missing-crew outcomes, infected or altered arrivals, containment escapes, hostile sites, and late-game space threats remain open design work. Do not reuse these two behaviors as a generic random-threat generator or mark the full threat backlog complete.

