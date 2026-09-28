# Rimrooms - Async Industries: first playable contract

**Status:** pre-code design target, version 0.1. All numbers are balance hypotheses for a later RimWorld 1.6 prototype. They are not gameplay results, compatibility claims, or frozen canon. Keep values adjustable and revise this document with the scenario contract when a playtest changes them.

**Purpose:** define the first complete player loop tightly enough that implementation can begin with one coherent slice: a small company facility, a short gate opening, one seeded destination, a recoverable risk, an evidence result, and a reason to prepare the next run.

**Feature route:** [RR-SCEN, RR-FAC, RR-STA, RR-GATE, RR-EXP, RR-SPACE, RR-EVD, RR-THREAT, RR-MSN, RR-ECO, RR-UI](FEATURE_TRACEABILITY.md). Lore inspiration is indirect and stays in the [fan cliff notes](research/KANE_PIXELS_FAN_CLIFF_NOTES.md), separate [film story note](research/reviews/a24-feature/feature-review.md), and [visual/audio brief](research/VISUAL_AUDIO_STYLE_BRIEF.md). The concrete first mission below is original game design.

## Starting offer

Use the `async_industries` opening in [SCENARIOS.md](SCENARIOS.md): one headquarters map, five staff in flexible roles, 900 company credits, 150 physical silver, a partially assembled gate, and the starter stock listed on that card. Start the scenario with the first project board visible and the next actionable step highlighted. Do not require a DLC, optional profile mod, RWT, or a named pawn to complete the solo first run.

| Measure | v0.1 starting target | Player-facing meaning |
| --- | --- | --- |
| Facility map | 60×60 | Enough space for the starter operation without asking the player to expand immediately. |
| Field crew | 3 people plus 1 gate operator kept at the facility | A researcher, guard, and flexible medic/logistics pawn can enter; the operator keeps the exit available. |
| Gate completion | Final 100 steel and 8 components, plus stable power and an operator | The opening asks the player to use construction, stock control, and staff assignments. |
| Gate opening | 20 in-game minutes for the first trip | A short first excursion with a visible warning and a recall decision. |
| First destination | 6–8 connected rooms, one safe return point, one environmental distortion, one evidence lead | The map teaches route reading and investigation without a sprawling first mission. |
| First crew load | Up to three pawns and their carried gear | The first run is intentionally easy to account for in a manifest. |
| First successful return | 240 company credits and one research insight, both provisional | The player can see the economic and research value of a controlled expedition. |

## The first session

1. The player sees the facility, staff, gate chamber, stock, and a short explanation of the company account versus physical trade goods.
2. The player confirms enough power is available, assigns a qualified gate operator, and completes the gate with the listed physical materials.
3. The player selects three available staff, checks their equipment and return plan, and reads a mission card for coordinate `AI-01`.
4. The crew enters a deterministic 6–8-room site. A visible environmental tell provides time to respond; the crew can record it, collect one evidence lead, or recall early.
5. The crew returns through a validated route before the gate window ends. Evidence is sealed in the facility, linked to `AI-01`, and analyzed by a researcher.
6. The player receives the provisional payment and insight, then chooses a local gate-telemetry project or a small paid survey contract. Either choice points to a second expedition.

## Gate and expedition rules for the prototype

- Opening is refused with a specific reason if the gate is incomplete, the operator is absent/unqualified, the reserved power margin is below the starting threshold, the crew is empty, or no return route is stored.
- The first opening lasts 20 in-game minutes. Show clear warnings at 10 minutes and 5 minutes remaining, then a final recall prompt at 2 minutes. The player can recall sooner. These notices must not depend on color or sound alone.
- The first crew plan has a required return reserve. Once it is crossed, the gate warns and offers recall; it does not silently end the expedition. If power fails, use the reserved battery for one return attempt and create a logged emergency state.
- The generator stores `AI-01`'s coordinate ID, seed, generator version, and initial site state. Reopening the same coordinate restores that site and recorded route changes; generating a replacement site requires a new coordinate ID.
- The first map is capped at 8 rooms in this slice. Rooms are connected and path-checked before opening. A failed layout is discarded before the player commits to it, and the gate remains closed with a clear explanation.
- The environmental distortion has one observable tell, one low-risk countermeasure, and one documented outcome. It may separate the crew or damage equipment, but the tutorial site does not use an unavoidable instant-kill rule.
- Cargo has an explicit manifest. On return, each item is accounted for as delivered, consumed, damaged, left behind, or lost; do not create free copies or silently destroy carried gear.

## First-session acceptance evidence

These are future in-game acceptance checks, not tests already run. Record the RimWorld build, DLC, ordered mod list, scenario seed, save, log, and observed result for each run. Use Core-only first; run the pinned Core+Harmony/RWT profile separately after its baseline exists.

| Case | Expected result |
| --- | --- |
| Fresh Core-only start | Async Industries setup appears once; the player can identify the first objective and required materials. |
| Gate has too little power | Opening is refused with a reason and a path to add reserve; no crew or cargo disappears. |
| No qualified operator | Opening is refused and identifies the staffing requirement. |
| Blocked or invalid route | Dispatch is refused before entry; the generator records a recoverable failure and does not create a dead-end site. |
| Player aborts before entry | Crew, gear, time, and stock remain accounted for. |
| Player recalls mid-expedition | Crew returns through the last validated route; cargo left behind is listed in the report. |
| Distortion causes injury | The pawn follows normal medical/recovery rules and the event is recorded against the coordinate. |
| Evidence is analyzed | One analysis outcome links to the physical evidence, coordinate, researcher, and project/contract result. |
| Payment is posted | The owning branch ledger gets one transaction; reloading cannot pay it twice. |
| Save and revisit | The same coordinate identity and prior discoveries return; no duplicate starting grant, mission, or reward appears. |
| Optional content absent | No optional mod or DLC is needed to assemble, open, explore, recover, analyze, and continue. |

## Boundaries

- This slice does not require hires beyond the starting five, multiplayer visits, synchronized research, direct video/film assets, VGE, outposts, town incidents, or a full technology tree.
- Research and company credits are local to the player's branch. Any RWT dossier or supported cargo transfer is a separately tested later feature.
- These starting targets are hypotheses. A future playtest can adjust map size, gate duration, costs, crew count, reward, and room count; the save identity, recovery path, branch ownership, and traceability rules remain the contract.
- Do not mark this as runtime complete until the acceptance evidence table has dated records from an actual game build.
