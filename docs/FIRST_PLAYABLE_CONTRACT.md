# Rimrooms - Async Industries: first playable contract

**Status:** pre-code design target, version 0.2. All numbers are balance hypotheses for a later RimWorld 1.6 prototype. They are not gameplay results, compatibility claims, or frozen canon. Keep values adjustable and revise this document with the scenario contract when a playtest changes them.

**Purpose:** define the first complete player loop tightly enough that implementation can begin with one coherent slice: a small company facility, a short gate opening, one seeded destination, a recoverable route distortion, one learnable hostile encounter, an evidence result, and a reason to prepare the next run. The named starting roster and room contents are in the [first-slice content inventory](FIRST_SLICE_CONTENT_INVENTORY.md); the starter encounter rules are in [THREAT_DESIGN_SHEETS.md](THREAT_DESIGN_SHEETS.md).

**Feature route:** [RR-SCEN, RR-FAC, RR-STA, RR-GATE, RR-EXP, RR-SPACE, RR-EVD, RR-THREAT, RR-MSN, RR-ECO, RR-UI](FEATURE_TRACEABILITY.md). Lore inspiration is indirect and stays in the [fan cliff notes](research/KANE_PIXELS_FAN_CLIFF_NOTES.md), separate [film story note](research/reviews/a24-feature/feature-review.md), and [visual/audio brief](research/VISUAL_AUDIO_STYLE_BRIEF.md). The concrete first mission below is original game design.

## Starting offer

Use the `async_industries` opening in [SCENARIOS.md](SCENARIOS.md): one headquarters map, five staff in flexible roles, a provisional $50,000,000 Company Account, 150 physical silver, a partially assembled gate, the starter stock listed on that card, and one already-accepted onboarding survey contract. The $5,000,000 target reward is paid only after the survey requirements are recorded as complete. An optional $1,000,000 bonus pays if all three crew return and the route, distortion, and entity observation records are delivered; a recoverable injury does not cancel it. Start with the project board visible and the next actionable step highlighted. Do not require a DLC, optional profile mod, RWT, or a named pawn to complete the solo first run.

| Measure | v0.1 starting target | Player-facing meaning |
| --- | --- | --- |
| Facility map | 60×60 | Enough space for the starter operation without asking the player to expand immediately. |
| Field crew | 3 people plus 1 gate operator kept at the facility | A researcher, guard, and flexible medic/logistics pawn can enter; the operator keeps the exit available. |
| Gate completion | Final 100 steel and 8 components, plus stable power and an operator | The opening asks the player to use construction, stock control, and staff assignments. |
| Gate opening | 20 in-game minutes for the first trip | A short first excursion with a visible warning and a recall decision. |
| First destination | 6–8 connected rooms, one safe return point, the Borrowed Corridor distortion, one bounded Quiet Pursuer encounter, and one evidence lead | The map teaches route reading, investigation, and a first fight-or-retreat choice without a sprawling first mission. |
| First crew load | Up to three pawns and their carried gear | The first run is intentionally easy to account for in a manifest. |
| First successful return | $5,000,000 Company Account receipt and one research insight, both provisional | The player can see the economic and research value of a controlled expedition. |

## The first session

1. The player sees the facility, staff, gate chamber, stock, and a short explanation of the company account versus physical trade goods.
2. The player confirms enough power is available, assigns a qualified gate operator, and completes the gate with the listed physical materials.
3. The player selects three available staff, checks their equipment and return plan, and reads the accepted survey's mission card for coordinate `AI-01`.
4. The crew enters a deterministic 6–8-room site. The Borrowed Corridor provides a visible route tell, followed by one bounded Quiet Pursuer encounter. The crew can tag the route, record the encounter, repel the entity, collect the evidence lead, or recall early.
5. The crew returns through a validated route before the gate window ends. Evidence is sealed in the facility, linked to `AI-01`, and analyzed by a researcher.
6. After the survey requirements are recorded, the player receives the provisional payment and insight, then chooses a local gate-telemetry project or a follow-on survey contract. Either choice points to a second expedition.

## Gate and expedition rules for the prototype

- Opening is refused with a specific reason if the gate is incomplete, the operator is absent/unqualified, the reserved power margin is below the starting threshold, the crew is empty, or no return route is stored.
- The first opening lasts 20 in-game minutes. Show clear warnings at 10 minutes and 5 minutes remaining, then a final recall prompt at 2 minutes. The player can recall sooner. These notices must not depend on color or sound alone.
- The first crew plan has a required return reserve. Once it is crossed, the gate warns and offers recall; it does not silently end the expedition. If power fails, use the reserved battery for one return attempt and create a logged emergency state.
- The generator stores `AI-01`'s coordinate ID, seed, generator version, and initial site state. Reopening the same coordinate restores that site and recorded route changes; generating a replacement site requires a new coordinate ID.
- The first map is capped at 8 rooms in this slice. Rooms are connected and path-checked before opening. A failed layout is discarded before the player commits to it, and the gate remains closed with a clear explanation.
- The Borrowed Corridor has one observable route mismatch and one low-risk countermeasure, as specified in [THREAT_DESIGN_SHEETS.md](THREAT_DESIGN_SHEETS.md). It cannot injure the crew or move the gate exit.
- The Quiet Pursuer has a visible warning, a bounded approach, and both retreat and combat responses. One contact may cause a recoverable injury; the entity cannot one-hit kill a healthy pawn in this tutorial encounter. Killing or capturing it is not required to complete the contract.
- Cargo has an explicit manifest. On return, each item is accounted for as delivered, consumed, damaged, left behind, or lost; do not create free copies or silently destroy carried gear.

## First-session acceptance evidence

These are future in-game acceptance checks, not tests already run. The first post-build test is the full 295-entry product target (the existing 294 plus Rimrooms), sorted and launched by the owner through RimSort. For bridge-driven checks, RimBridgeServer is a separate QA overlay, normally bringing the actual loaded profile to 296 entries; record target and overlay IDs separately. After that initial full-profile startup, run the focused Core-only baseline and pinned Core+Harmony/RWT profile as separate RimSort-prepared cases. Record the RimWorld build, DLC, RimSort version, ordered mod lists, scenario seed, save, log, bridge version, and observed result for each run. The post-build [RimBridgeServer harness](research/RIMBRIDGE_TEST_HARNESS.md), [power/gate acceptance cases](research/POWER_GATE_AND_TURRET_SOURCE_AUDIT.md), and [physical-logistics plan](research/PHYSICAL_LOGISTICS_BASELINE_TEST_PLAN.md) do not verify the unimplemented Rimrooms gate, custom field kit, expedition cargo handling, or company shipment flow until those cases pass.

| Case | Expected result |
| --- | --- |
| Fresh Core-only start | Async Industries setup appears once; the player can identify the first objective and required materials. |
| Gate has too little power | Opening is refused with a reason and a path to add reserve; no crew or cargo disappears. |
| No qualified operator | Opening is refused and identifies the staffing requirement. |
| Blocked or invalid route | Dispatch is refused before entry; the generator records a recoverable failure and does not create a dead-end site. |
| Player aborts before entry | Crew, gear, time, and stock remain accounted for. |
| Player recalls mid-expedition | Crew returns through the last validated route; cargo left behind is listed in the report. |
| Threat causes injury | The pawn follows normal medical/recovery rules and the encounter is recorded against the coordinate; the route distortion itself causes no injury. |
| Evidence is analyzed | One analysis outcome links to the physical evidence, coordinate, researcher, and project/contract result. |
| Payment is posted | The owning branch ledger gets one transaction; reloading cannot pay it twice. |
| Save and revisit | The same coordinate identity and prior discoveries return; no duplicate starting grant, mission, or reward appears. |
| Optional content absent | No optional mod or DLC is needed to assemble, open, explore, recover, analyze, and continue. |

## Boundaries

- This slice does not require hires beyond the starting five, multiplayer visits, synchronized research, direct video/film assets, VGE, outposts, town incidents, or a full technology tree.
- Research and the USD-denominated Company Account are local to the player's branch. Physical silver and other goods remain actual items; any RWT cargo transfer is a separately tested later feature.
- These starting targets are hypotheses. A future playtest can adjust map size, gate duration, costs, crew count, reward, and room count; the save identity, recovery path, branch ownership, and traceability rules remain the contract.
- The first month of Company Account activity is modeled in [CAMPAIGN_ECONOMY_MODEL.md](CAMPAIGN_ECONOMY_MODEL.md) and its linked v0.2 workbook. Prices and power values remain hypotheses pending a playable balance pass.
- Do not mark this as runtime complete until the acceptance evidence table has dated records from an actual game build.
