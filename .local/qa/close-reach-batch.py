# -*- coding: utf-8 -*-
"""Close what this batch built. Evidence on the row's own line, nothing past it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 # ======================================================== the object half of the register
 ('- [ ] **still open from the same direction** — non-rectangular rooms and corridors;',
  'CLOSED 0.12.89-dev, and **every clause of it was measured rather than assumed.** '
  '**Non-rectangular rooms and corridors:** built. `RoomLayoutPlanner.ShapeForms` is **seven** '
  'shapes, chosen per room by `ShapeFormOf` against the coordinate’s motif, banded by '
  '`ShapeDepthOf` so a room’s distance from the arrival hall widens what it can be. '
  '**Materials across items, equipment, walls, floors, lights, furniture and benches:** built, '
  'and more thoroughly than the row knew. `CoordinateMaterials` gives a shallow coordinate one '
  'narrow palette and a deep one *"every type of wall and material for all things randomly"* '
  'per fixture, derived from the coordinate seed and **sorted by defName before indexing** so a '
  'player installing an unrelated mod cannot change how a place looks. `RoomContentBuilder` '
  'routes **both** placement paths through it — the family fixtures and the archetype '
  'dressing, which is the loot and the benches. '
  '**Events, layouts and loot deeper in:** built — eight anomaly events, the depth-banded '
  'archetype library, and `SpaceSophistication.TechCeiling` raising what a deep coordinate '
  'produces as the branch rises. '
  '**WHAT WAS GENUINELY MISSING was none of those: it was that none of it said anything.** That '
  'is the row below and it closed in this batch too.'),

 ('- [ ] **still open from the same direction** — the wild variation of materials',
  'CLOSED 0.12.89-dev — **stale on the materials clause, and the real gap was the one the '
  'owner had named separately.** The materials half was already built (see the row above, '
  'measured against `CoordinateMaterials` and both of `RoomContentBuilder`’s placement '
  'paths). What no object in any coordinate could do was **say what was wrong with it**. '
  'Owner: *"not just room shape echoes but echos of thier inhabitance in weird ways and items '
  'and equipment and production benches"*. 0.12.88-dev took the unnerving register to people '
  'and events and reached **no object at all**, though the owner had named objects specifically. '
  'So `RimroomsFixtureTellDef` is **20 tells across nine classes of object** — bench, seat, '
  'table, bed, storage, light, item, equipment and anything — each one exact wrong fact, '
  'read off the thing for as long as the thing exists. '
  '**The classes ask the definition a question rather than naming defs**, so a bench from a mod '
  'installed tomorrow is a bench today, and the same no-mood-adjective gate the people and '
  'events are held to applies: `proof-unnerving-register.py` fails on *eerie*, *creepy*, '
  '*unsettling* and nine more. A bench that is *eerie* says nothing; a bench whose bills are '
  'still queued for a meal this space cannot cook says something. '
  '**And most objects carry no tell, which is the design** — `TellPercent` is 12, because '
  '*"quiet stretches are required content"* and a coordinate with a placard on every stool '
  'buries the sharper people and event beats.'),

 # ======================================================== the four workflows, completed
 ('- [ ] Add analyze/interview/compare/review workflows for equipment, furniture, people,',
  'CLOSED 0.12.89-dev. **Review was measured as already built, and then genuinely finished.** '
  '`Company/EvidenceReview.cs` ships `ReviewerFor`, `AwaitsReview` and `ReviewAnalysis` with '
  'every refusal keyed, it is reachable from `OperationsEvidence` (the sign-off) and '
  '`OperationsExpeditions` (the current objective), and it is **additive beside the status '
  'rather than a sixth `EvidenceStatus`** — `Analyzed` is the terminal state eight places '
  'test for and a new enum value would have changed every one of those comparisons and every '
  'saved game. '
  '**But `RecordsAwaitingReview()` had no caller anywhere**, which is precisely the defect that '
  'file’s own header warns about: *"Four of five bond defects, and seven before them, were '
  'built, correct and unreachable."* It is wired now — the awaiting-sign-off heading carries '
  'the branch-wide count through `AwaitingReviewCount()`, which counts **through** the accessor '
  'so there is one definition of *awaiting review* rather than two that can drift. '
  '**The fix for an unreachable surface is to reach it, not to delete it**, and that correction '
  'came from the owner mid-batch. It cost no screen words at all: the count rides a heading '
  'string that already existed.'),

 # ======================================================== the links reach what they name
 ('- [~] Make each screen deep-link to the relevant pawn, building, map, quest, item,',
  'CLOSED 0.12.89-dev, all three of the named gaps. `UI/OperationsLinks.cs` is now the one place '
  'a screen hands the player off to the rest of the game. '
  '**Research was the worst of the three and it was not merely missing.** The locked supply tier '
  'row printed `tier.requiredResearchDefName` **straight at the player** — an internal '
  'identifier like `MicroelectronicsBasics` that the game displays nowhere else — behind a '
  '**null action**. So the one screen that told somebody they needed a research project named it '
  'unrecognisably and gave them no way to go and look at it. It now shows the project’s own '
  'label and opens the research tree at it, through Core’s own public '
  '`MainTabWindow_Research.Select` — **confirmed by decompiling the installed assembly '
  'rather than remembered** — and it deliberately does **not** set the player’s current '
  'project, because a link shows somebody where a thing is and choosing to research it is still '
  'theirs. '
  '**Pawn:** the Personnel detail view holds the richest readout of a person anywhere in the '
  'package and had no way to go and look at them; it refuses **by name** for an off-site '
  'applicant, because somebody who is not standing anywhere yet is worth saying out loud. '
  '**Building:** this already worked and now goes through the same helper, with `CanJump` '
  'replacing `Spawned` — strictly wider, because Core answers that question for held things '
  'and world targets too. '
  '**A link that cannot arrive is never offered**, which is this package’s own rule: *a '
  'button that can only refuse is worse than no button*.'),

 # ======================================================== the cards say what a thing is
 ('- [~] **Informational text on the inspect cards** for everything a player can select or inspect:',
  'CLOSED 0.12.89-dev, **and the audit found two gaps rather than the one the row named.** '
  '**The station had no inspect card at all.** The gate had one and the beacon had one; the '
  'thing a player clicks on to *run* a gate had nothing, so every piece of its state was '
  'readable only by noticing which label one of its gizmos happened to be showing — a '
  'station bound to no gate looked exactly like a station bound to one. The sharpest edge was '
  'gate control: it holds every unrelated bill on the machining bench suspended, which is '
  'correct and was asked for (*"so other things arnt available"*), and a player who left it that '
  'way a week ago and cannot work out why nothing is being crafted had no way to find out from '
  'the bench. It says so now. '
  '**And the beacon was silent in exactly the state where a player needed telling.** It read '
  '`if (!designated) return null` and stopped, so bonds piled up inside its radius with nothing '
  'banking them and no indication anywhere on the thing that one toggle was the answer. **A card '
  'that explains itself only once it is already working explains itself only to people who did '
  'not need it.** It now speaks **only when there are company bonds in range**, which keeps the '
  'dormant-until-designated rule intact: this comp sits on Core’s `OrbitalTradeBeacon`, so '
  'every trade beacon in every colony in the game carries it, and installing this mod must not '
  'add a line to a building somebody already owns.'),

 # ======================================================== the scheduling surface
 ('- [~] Add schedule, warning, recall, evacuation, emergency close, lost-connection, failed return,',
  'CLOSED 0.12.89-dev. **Schedule was the one left**, and it is a standing recall on the gate: '
  'the player picks a point in the opening’s window and the crew is ordered home when it '
  'arrives. '
  '**It adds no clock, and that is the whole constraint.** `docs/CAMPAIGN_CHART.md` §1.1 is '
  'absolute and checker-enforced — *"A gate’s connection has a duration. Nothing else '
  'in this mod has a duration"*, from the owner’s *"nothing ever ever have time '
  'restripctions but the gate"*. So this reads `OpeningTicksRemaining`, which is itself the '
  'consequence of power, tech, maintenance and workforce. Three things keep it on the right side '
  'of the rule: it is **off by default**, it **takes nothing away** (it fires `Recall`, which '
  'tells people to walk home — it cannot close the gate, cannot strand anybody and cannot '
  'end the trip), and **its thresholds are the three warning thresholds**, not new ones. '
  'That last one is design rather than convenience: a schedule that could sit between two '
  'warnings would be a second opinion about when a window is nearly over. It is decided in the '
  'same pass over the same number as the warnings, so the order and the shout cannot drift apart '
  'by a tick and read as a bug. '
  '**Why it is worth having at all:** the way a player loses a crew is not misunderstanding the '
  'rules, it is being busy elsewhere on the map when the five-minute warning scrolls past. A '
  'warning needs somebody watching. A standing order does not.'),

 # ======================================================== the room functions
 ('- [~] Implement physical room functions: gate, control, labs, evidence archive,',
  'CLOSED 0.12.89-dev. All five the row listed as not built now ship as gate equipment link '
  'roles: `RR_Link_Quarantine`, `RR_Link_Armory`, `RR_Link_Radio`, `RR_Link_Receiving` and '
  '`RR_Link_Canteen`. '
  '**The row’s own analysis decided the shape and it was right:** *"RimWorld already builds '
  'rooms; what this mod adds is what a gate is linked to."* So a facility is defined by what the '
  'branch designated rather than by where walls happen to fall, which is also the only thing '
  'that works for the sprawling installations these roles came from. '
  '**EVERY defName WAS READ OUT OF THE INSTALLED GAME DATA.** `TableLong` was the first choice '
  'for the canteen and **does not exist** — the Core dining tables are `Table2x2c` and '
  '`Table3x3c`. That is the same class of mistake this file already records for '
  '`MultiAnalyzer`’s casing, and it is why `Fillable` now **hides a role nothing in the '
  'loaded game can fill** rather than offering one that silently accepts nothing. That guard is '
  'the stand-alone guarantee applied to a role: `thingDefNames` is exact names and `ConfigErrors` '
  'can only see that the list is non-empty. '
  'The radio room is deliberately **a second comms console**, never the gate’s own — '
  '`EquipmentLinkFailureKey` refuses that as `AlreadyAProvider`, which is what makes the role '
  'mean something: a branch that wants a radio room builds a radio rather than relabelling the '
  'console it already needed.'),

 ('- [~] Connect each room to concrete capabilities, stock needs, staff jobs, risks, and UI alerts;',
  'CLOSED 0.12.89-dev, both halves the row listed as not built. **Stock needs:** a role now '
  'declares a `ThingCategoryDef` it is supposed to hold and how much — a category rather '
  'than a def list, so Core, every DLC and all 294 profile mods answer *what counts as a weapon*. '
  '**A role that only accepts equipment is a label; a role that knows what belongs on it is a '
  'function.** An armory with no weapons in it is not an armory, and before this nothing '
  'anywhere could say so. '
  '**Counted on the role’s own linked things and never map-wide**, which is the load-bearing '
  'line: a branch with five rifles in a bedroom does not have an armory, and a map-wide count '
  'would have reported one. That is the same laundering the clue system already refuses. Asked '
  'through Core’s `GetSlotGroup`, so mod storage buildings answer too. '
  '**Risk:** each role names **what actually goes wrong** when it is short — *"a crew that '
  'meets something hostile down there has nothing to meet it with"* — and never scores it. '
  '*"Risk: 3"* tells a player nothing. The same no-mood-adjective gate the inhabitant tells are '
  'held to covers these, in `proof-operations-reach.py`. '
  '**Why a room is not functional is read off the gate**, beside the role’s own line, '
  'because that is where a player is already looking. A half-declared stock need — a target '
  'with no category, or a category with no target — is refused at load, because either one '
  'alone produces a room function that looks implemented and does nothing.'),

 # ======================================================== the quest line pays
 ('- [ ] **"once u follow the quests to get the gate up and running"**',
  'CLOSED 0.12.89-dev, and **the spine is the chain itself rather than a parallel quest '
  'script.** `GateStartupPayouts` asks `GateStartupChecklist.Steps`, which is the same list the '
  'machine tab’s status board and the door’s own inspect card read. **One source for '
  'all three**, so a payout and a tick can never disagree about whether something is done. '
  'Writing the eleven conditions a second time here is the *"two derivations of one rule"* defect '
  'this project keeps meeting, and it is the specific defect that once made '
  '`RR_Gate_CalibrationUnavailable` mean eight different things including *already calibrated*.'),

 ('- [ ] **"(full totorieal quest line payouts on each successful step"**',
  'CLOSED 0.12.89-dev. **Eleven payouts, one per goal, not one reward at the end** — '
  '`StepPayoutUsd` is a plain table of eleven numbers rather than a curve, because somebody will '
  'want to balance these by hand after the first play and a curve has to be read to be '
  'understood. Scaled as the owner asked: the early ones are a nudge that roughly covers what '
  'the step asks for, the assembly step pays more because it costs real materials, and step '
  'eleven — a connection actually open — is worth more than the other ten put together, '
  'because that is the goal the whole chain exists for. '
  '**Paid once per branch, never once per gate.** This is the tutorial chain; a branch that '
  'builds a second gate has already learned how, and paying per door would turn eleven payouts '
  'into an income stream — build ten doors, collect a hundred and ten receipts. A plant '
  'proves the per-gate version fails.'),

 ('- [ ] **"(the company rewards getting to the goals)"**',
  'CLOSED 0.12.89-dev. **The payer is the company in the mechanism as well as the fiction:** it '
  'goes through `PostTransaction`, so it lands in the branch’s balance with a ledger receipt '
  'and a keyed reason, exactly like every other sum this mod moves. **Nothing appears from '
  'nowhere** — no item spawns and no stack is dropped on the floor, which the row asked for '
  'specifically; a plant proves a version that bypasses the ledger fails. '
  '*"getting to the goals"* is the trigger: **the goal being reached pays, not a quest being '
  'accepted**, so there is nothing to accept and nothing to decline. '
  '**And the ledger IS the record, which is why this added no saved state at all.** '
  '`PostTransaction` is idempotent on its operation id — a repeat with the same amount and '
  'reason returns `Existing()` and moves no money — so *has step six been paid* is already '
  'answered permanently by the branch’s own books, and a second bookkeeping field could only '
  'ever drift from them. Nothing in `GateStartupPayouts` is scribed.'),
]

NOTES = [
 ('- [ ] **"remember lsd unnerving feeling with all things"**',
  'THE OBJECT HALF LANDED 0.12.89-dev; **the row stays open because only a launch judges a '
  'feeling.** 0.12.88-dev reached people and events; this batch reached **objects**, which the '
  'owner had named specifically — *"items and equipment and production benches"*. Twenty '
  'object tells across nine classes, each one exact wrong fact read off the thing, held to the '
  '**same no-mood-adjective gate** taken from `UNIVERSE_ADAPTATION.md`, and kept to a small '
  'derived minority of placed objects so the quiet rooms stay quiet. '
  '`plant-unnerving-register.py` is **50 of 50**. '
  '**What *"all things"* still does not cover**, named rather than implied: the room clue texts '
  'are still instructional rather than uncanny, deliberately, because they teach the vertical '
  'slice and rewriting them would remove teaching the owner valued. This is an acceptance row '
  'like *"its suppose to be a lsd trip"* and it closes when the owner plays it.'),

 ('- [~] Eleven-pane Company Command, deep links, reason codes, native menu remap.',
  'DEEP LINKS CLOSED 0.12.89-dev — pawn, building and research project all reach now, '
  'through `UI/OperationsLinks.cs`; see the deep-link row above for what the research half was '
  'doing before. **The row stays `[~]` because the native menu remap is still open and still '
  'questioned on its own row**, and nothing in this batch touched it.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0

for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    marker = "- [~] " if anchor.startswith("- [~]") else "- [ ] "
    row = "- [x] " + text[at:line_end][len(marker):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]

for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("NOTE ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    text = text[:line_end] + " — **" + note + "**" + text[line_end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows, noted %d" % (len(CLOSED), len(NOTES)))
