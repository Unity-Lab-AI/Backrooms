# Rimrooms - Async Industries: first-session tutorial script

**Status:** provisional player-facing copy for the first-playable contract (v0.2). The [development build](implementation/PHASE_2_BUILD_RECORD.md) implements the next-objective board, action hints, written warnings and observation checklist. Narrative copy below remains a presentation target; runtime timing/readability and gameplay review are pending.

**Canonical content checks:** align the Async opening with [FIRST_SLICE_CONTENT_INVENTORY.md](FIRST_SLICE_CONTENT_INVENTORY.md), [FIRST_PLAYABLE_CONTRACT.md](FIRST_PLAYABLE_CONTRACT.md), [CAMPAIGN_ECONOMY_MODEL.md](CAMPAIGN_ECONOMY_MODEL.md), and [THREAT_DESIGN_SHEETS.md](THREAT_DESIGN_SHEETS.md). The Store and Lone Survivor openings remain in [SCENARIOS.md](SCENARIOS.md); this script does not claim to verify their RWT setup.

## 1. The first order

> **Operations Lead:** “The survey is already accepted. They want a route record from AI-01, not a hero story. We bring the crew home, seal what we find, and then we get paid.”

**Objective:** Restore safe power, finish the gate, prepare a three-person crew, and return one useful record from AI-01.

The branch has **$50,000,000** in its Company Account for quoted company costs and **150 physical silver** for ordinary RimWorld trade. Account money stays on the ledger; it is never spawned as silver that someone has to haul. Food, steel, gear, samples, and salvage remain physical stock. The five staff are flexible; assign work by ability, not by title. Keep a qualified gate operator at headquarters while the researcher, guard, and medic/logistics generalist prepare to go.

## 2. Make the gate ready

> **Engineer:** “Frame is almost there. I need the last hundred steel and eight components for assembly. Before anyone steps through, the reserve has to cover the opening and one return.”

**Gate checklist**

- Finish assembly with **100 steel and 8 components**.
- Confirm the current machine readout's power and stored-return requirements. The development slice uses a **3,500 W opening draw**, **250 W headroom**, and a **2 Wd gate-owned return capacitor**, with an ordinary **6,000 W** starter generator. These are provisional operating values, not a 3,000 W battery-capacity measurement.
- Assign a qualified operator who will remain at the facility.
- Select up to three ready field staff; check their kit and return tether.
- Confirm AI-01 and its validated way home are on the mission card.

> **Operations Lead:** “Twenty game-minutes on the clock. We call them back early if the route turns, the reserve drops, or the crew asks. Warnings come at ten, five, and two minutes.”

## 3. AI-01: mark what is real

> **Researcher, radio:** “Threshold Room is behind us. I have the first junction. Tag it, read the number back, and keep the next marker in sight.”

Place a numbered survey tag at the first junction. Follow the mission card through the Survey Lobby and Service Passage. The tags are a route record, not a guarantee that the rooms will stay familiar.

> **Researcher:** “The label says we have reached the same room again. The tag is on the wrong side of the doorway. The map and the landmark disagree.”

**Borrowed Corridor clue:** Stop at the mismatch. Compare the room label and tag number, place the short return beacon at the last validated junction, then follow the recorded route. The distortion may return the crew to that junction and cost three reported game-minutes. It cannot move the gate exit or injure the crew. You may recall now instead of investigating further.

## 4. A figure in the next rooms

> **Guard:** “Upright shape, two rooms out. The recorder missed a stretch. It’s closer than it was.”

The **Quiet Pursuer** is a sighting to document, not a required kill. Its map marker and written status report show its last room and distance. If the crew stays in its connected area, it advances at intervals; a warning appears before another advance.

Choose a response:

- **Withdraw:** close a door and follow the numbered tags toward the return route. The survey can still succeed.
- **Repel:** order the guard to fire and force it back one room. This is optional and risky; loud actions can make it advance immediately.
- **Recall:** leave optional salvage and return through the last validated path.

> **Operations Lead:** “Do not chase it. Bring back the observation and the crew.”

The first encounter cannot kill a healthy pawn in one hit. Contact may cause an ordinary, recoverable injury. Capturing or killing the entity is not part of this order.

## 5. Return, seal, and report

> **Gate Operator:** “Ten minutes remaining. Return reserve is holding.”

> **Gate Operator:** “Five minutes. Confirm recall if the crew is not already on the validated route.”

> **Gate Operator:** “Two minutes. Final recall warning.”

Recall at any time. At headquarters, check the manifest: each item is delivered, consumed, damaged, left behind, or lost. Return the **AI-01 Route Recording** and its physical evidence case together. Their expedition manifest links custody to AI-01; they remain separate items with ordinary mass and storage. Have a researcher analyze the recording at the powered bench while the case remains at headquarters. The report records the repeated label, misplaced tag, recorder gap, and any entity observation without claiming to explain their cause.

> **Operations Lead:** “Survey accepted. The branch ledger posts its **one-time $5,000,000 payment** and one research insight. The **optional $1,000,000 safety and documentation bonus** is added if all three field staff return with the route, distortion, and entity-observation records. A recoverable injury does not cancel it.”

## 6. Choose the next lead

> **Researcher:** “We can spend the insight on Gate Telemetry and make the next route easier to plan. Or we can prepare another visit and learn what else AI-01 is hiding.”

Choose **Gate Telemetry** (one insight and staffed research work) or **Prepare an AI-01 resurvey**. The latter keeps the same map, discoveries, equipment and construction. It can recover remaining salvage or people and explore rooms left unseen, but it does not repay the one-time onboarding contract or grant another insight. Either starts the next preparation decision; neither opens a new coordinate automatically. Generated paid follow-on contracts remain part of the Phase 3 campaign build.

## If Operations refuses

These messages name the problem and the immediate recovery step:

- **“Gate incomplete: add 100 steel and 8 components, then finish assembly.”**
- **“Power reserve below the first-run requirement: restore the reserve before opening.”**
- **“No qualified operator at the controls: assign an available operator and keep them at headquarters.”**
- **“No field crew selected: choose at least one ready pawn; the first plan allows up to three.”**
- **“No validated return route: mark or restore a safe route before dispatch.”**
- **“AI-01 could not be prepared safely. The gate remains closed; your crew and stock are accounted for. Retry with a new coordinate only after reviewing the report.”**
- **“Return reserve reached: recall now. Optional cargo may remain behind; the crew follows the last validated route.”**

Aborting before entry returns the crew and gear. If power fails during the run, the reserve battery allows one logged return attempt. If a crew member is injured, treat them through ordinary medical care; the expedition record keeps the route and recovery lead.

## Readable without color or sound

Gate state, countdowns, power reserve, route tags, the repeated room label, the Pursuer's distance, recall warnings, and evidence status each have a written label and a distinct icon or map marker. Important alerts remain in the log after the pop-up closes. No required clue or warning relies on color, audio, darkness, or animation alone.
