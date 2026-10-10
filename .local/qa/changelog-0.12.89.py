# -*- coding: utf-8 -*-
"""Prepend the 0.12.89-dev entry. Newest first, nothing above it rewritten."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"

ENTRY = """## 0.12.89-dev - 2026-10-05 - The thing says what it is, the link goes there, and the company pays for the goal

- **THE UNNERVING REGISTER REACHED OBJECTS, which the owner had named specifically and the last
  version had missed.** Owner: *"not just room shape echoes but echos of thier inhabitance in weird
  ways and items and equipment and production benches"*. 0.12.88-dev took the register to people
  and events; a coordinate's objects were materially varied, correctly placed, and said nothing at
  all about who had been using them. Twenty object tells now ship across nine classes - bench,
  seat, table, bed, storage, light, item, equipment and anything - each one exact wrong fact read
  off the thing for as long as the thing exists. *"The bills are still queued on it. The last one
  is for a meal, and there is nothing in this space to cook."*
- **The classes ask the definition a question rather than naming defs**, so a bench from a mod
  installed tomorrow is a bench today - the same discipline the room archetypes already use. And
  the comp is attached in code at `StaticConstructorOnStartup` rather than by XML, because that is
  the only moment the question can be asked *after def inheritance resolves*. The patch file's own
  note records why that matters: an xpath runs on raw XML and `BuildingBase` is the only parent
  broad enough to catch the furniture, which would have put this comp on every wall, door and
  turret in every colony in the game to reach the few that can be dressed into a Backrooms room.
- **The same no-mood-adjective gate the people and events are held to.** The rule is
  `UNIVERSE_ADAPTATION.md`'s, not invented here: the uncanny is *one exact change to something
  ordinary*. A bench that is *eerie* tells the player nothing. And **most objects carry no tell**,
  which is the design rather than a shortfall - *quiet stretches are required content*, and a
  coordinate with a placard on every stool buries the sharper people and event beats.
- **Hauling can no longer silently destroy a tell.** `Thing.CanStackWith` compares def, stuff and
  hit points and never looks at comp data, so a marked stack dropped onto an ordinary one would
  merge and the fact would survive or vanish depending on which absorbed which. A readable warning
  that disappears because somebody tidied up is not a readable warning.
- **THE STATION HAD NO INSPECT CARD AT ALL.** Owner: *"we also need to be making sure all mod
  ingame decriptions and informational informations for everything is properly in the cards like
  the game does currently"*. The gate had one and the beacon had one; the thing a player clicks on
  to *run* a gate had nothing, so a station bound to no gate looked exactly like one bound to a
  gate. The sharpest edge was gate control - it holds every unrelated bill on the machining bench
  suspended, which is correct and was asked for, and a player who left it that way and could not
  work out why nothing was being crafted had no way to find out from the bench.
- **And the beacon was silent in exactly the state where a player needed telling.** It read
  `if (!designated) return null` and stopped, so bonds piled up inside its radius with nothing
  banking them and nothing on the thing saying one toggle was the answer. **A card that explains
  itself only once it is already working explains itself only to people who did not need it.** It
  speaks now only when there are company bonds in range, which keeps the dormant-until-designated
  rule intact: this comp sits on Core's own trade beacon in every colony in the game.
- **The locked supply tier row printed a raw `defName` straight at the player.** An internal
  identifier like `MicroelectronicsBasics`, which the game displays nowhere else, behind a **null
  action**. So the one screen that told somebody they needed a research project named it
  unrecognisably and gave them no way to go and look at it. It now shows the project's own label
  and opens the research tree at it through Core's public `MainTabWindow_Research.Select` -
  confirmed by decompiling the installed assembly rather than remembered - and deliberately does
  **not** set the player's current project, because a link shows somebody where a thing is and
  choosing to research it is still theirs.
- **Deep links out to a pawn and a building, through one helper.** The Personnel detail view holds
  the richest readout of a person anywhere in the package and had no way to go and look at them; it
  refuses **by name** for an off-site applicant, because somebody not standing anywhere yet is
  worth saying out loud. A link that cannot arrive is never offered - *a button that can only
  refuse is worse than no button*.
- **The scheduling surface, and it adds no clock.** Owner's row: *"Add schedule, warning, recall,
  evacuation, emergency close, lost-connection, failed return, and rescue workflows"* - schedule
  was the one left. A standing recall calls the crew home at a point in the opening's window the
  player picked. `CAMPAIGN_CHART.md` 1.1 is absolute and checker-enforced - *a gate's connection
  has a duration, nothing else in this mod has a duration* - so this reads the gate's existing
  window, is off by default, and only ever tells people to walk home: it cannot close the gate,
  cannot strand anybody and cannot end the trip. **Its thresholds are the three warning
  thresholds**, not new ones, because a schedule that could sit between two warnings would be a
  second opinion about when a window is nearly over.
- **Why it is worth having:** the way a player loses a crew is not misunderstanding the rules, it
  is being busy elsewhere on the map when the five-minute warning scrolls past. A warning needs
  somebody watching. A standing order does not.
- **THE COMPANY PAYS FOR EACH START-UP GOAL REACHED.** Owner: *"and once u follow the quests to get
  the gate up and running(full totorieal quest line payouts on each successful step(the company
  rewards getting to the goals)"*. Eleven goals, eleven payouts, scaled so the early ones are a
  nudge and a connection actually open is worth more than the other ten together. The spine is
  `GateStartupChecklist.Steps` - **the same list the machine tab's status board and the door's own
  inspect card read**, so a payout and a tick can never disagree about whether something is done.
- **And it added no saved state at all, because the ledger is already the record.**
  `PostTransaction` is idempotent on its operation id, so *has step six been paid* is answered
  permanently by the branch's own books; a second bookkeeping field could only ever drift from
  them. The id names the step and not the gate, so the chain pays **once per branch** - paying per
  door would turn eleven payouts into an income stream, and a plant proves that version fails.
- **The five named room functions that were never built:** quarantine, armory, radio, receiving and
  canteen, as gate equipment link roles. The row's own analysis decided the shape and was right -
  *RimWorld already builds rooms; what this mod adds is what a gate is linked to*. **Every defName
  was read out of the installed game data**: `TableLong` was the first choice for the canteen and
  does not exist. So a role nothing in the loaded game can fill is now **hidden rather than offered
  and unfillable**, which is the stand-alone guarantee applied to a role.
- **A role knows what should be kept on it, and what goes wrong when it is not.** A role that only
  *accepts* equipment is a label; one that knows what belongs on it is a function - an armory with
  no weapons in it is not an armory, and nothing anywhere could say so before. Counted on the
  role's **own linked things and never map-wide**, because a branch with five rifles in a bedroom
  does not have an armory. Each risk names the consequence - *"a crew that meets something hostile
  down there has nothing to meet it with"* - and never scores it.
- **`RecordsAwaitingReview()` had no caller for a whole checkpoint**, which is exactly what its own
  file warns about: *"Four of five bond defects, and seven before them, were built, correct and
  unreachable."* It is wired now and the awaiting-sign-off heading carries the branch-wide count.
  **The fix for an unreachable surface is to reach it, not to remove it** - that correction came
  from the owner mid-batch, and it cost no screen words at all because the count rides a string
  that already existed.
- **Two instruments added, and four claims in them were wrong before they were right.**
  `proof-operations-reach.py` is 38 claims and `plant-operations-reach.py` reports **38 of 38
  caught**; `plant-unnerving-register.py` is now **50 of 50**. Two claims failed on their first run
  because an absence assertion read the documentation too - good documentation explains the thing
  it avoids **by naming it** - and two more passed a plant they should have caught: one asserted a
  `for` line that appears twice in the file and matched the wrong one, and one asserted that an
  error *message* existed rather than the condition that fires it. **A message is not a rule.**
- **Two rows closed on measurement rather than work.** Non-rectangular rooms and corridors: built,
  seven shape forms banded by distance from the arrival hall. Material variation across items,
  equipment, walls, floors, lights, furniture and benches: built, and reaching both placement paths.
  The clause that was genuinely missing was the one about objects saying something, above.
- Instruments: **18 checkers, 52 proofs, 26 plant suites, 957 plant anchors.** Queue: 67 open, 30
  partial, 38 post-completion test, 0 completed-and-unarchived.

"""

text = io.open(PATH, encoding="utf-8-sig").read()
if "## 0.12.89-dev" in text:
    print("already present")
    sys.exit(0)
head = "# Changelog" + NL + NL
if not text.startswith(head):
    print("CHANGELOG does not start with the expected heading; nothing written")
    sys.exit(1)
io.open(PATH, "w", encoding="utf-8-sig", newline=NL).write(head + ENTRY + text[len(head):])
print("prepended the 0.12.89-dev entry (%d lines)" % (ENTRY.count(NL) + 1))
