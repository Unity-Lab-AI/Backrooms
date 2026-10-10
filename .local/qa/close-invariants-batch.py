# -*- coding: utf-8 -*-
"""Close the three rows measurement and instruments finished; note the one needing no decision yet."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] The hinge opens **everything**.',
  'CLOSED 0.12.93-dev ON MEASUREMENT, AND IT IS ALREADY GUARDED. **38 projects across 8 '
  'branches, 0 cross-branch prerequisites, exactly 8 entry points — one per branch — and 0 '
  'prerequisites naming a project that does not exist.** Each branch keeps its own internal '
  'ladder exactly as the row specifies, and no branch gates another. '
  '**The property does not rest on today’s measurement:** `proof-research-branches.py` asserts, '
  'per project, that it is *not a chokepoint between branches* — every one reports **1 lineage** '
  '— and that is the stronger form of the rule. A cross-branch prerequisite would merge two '
  'lineages and fail the claim; so would a project that two branches both have to pass through, '
  'which a plain no-cross-prerequisite test would miss. Consistent with the standing direction '
  '*"but remmebr this is all open eneded they can play how they choose"*. **Closes chart §6 '
  'item 2**, as the row says.'),

 ('- [ ] **Five `RR_*Staff` PawnKinds**',
  'CLOSED 0.12.93-dev, AND THE ROW IS STALE IN ITS PREMISE. **The goal is already satisfied and '
  'always was: a pawn generated from any of the five IS a native colonist.** All five derive '
  '`RR_StaffBase`, which derives Core’s `BasePlayerPawnKind` with '
  '`<defaultFactionDef>PlayerColony</defaultFactionDef>`. **A `PawnKindDef` is a generation '
  'recipe — skills, apparel, work tags — not a pawn class**, and `Pawn.IsColonist` reads the '
  'faction, never the kind. There was never a non-native pawn to migrate. '
  '**And the retirement half is superseded by the owner’s own direction.** The row wanted them '
  '*"readable-only"*, meaning kept for old saves and otherwise retired. They are now **wired '
  'and used**: `FacilityRelief.ReliefKindFor` generates the corporation’s relief team from '
  'exactly these five role profiles, under invariant 131 — owner verbatim, *"make sure shit '
  'isnt unused it was put there for a reason"* — and its own comment records that these defs '
  '*"already existed and were read by nothing"* before that. **A def nobody wired is a job '
  'nobody finished**, so retiring them now would undo the fix. Recorded as superseded rather '
  'than quietly dropped, the same treatment the chart gives four superseded prep documents.'),

 ('- [ ] **The laundering routes are closed and must stay closed.**',
  'CLOSED 0.12.93-dev. **THE PURPOSE IS SATISFIED; THE MECHANISM THE ROW SPECIFIED WAS '
  'SUPERSEDED BY A STRONGER ONE, AND THAT IS NOW WRITTEN DOWN.** '
  'The row feared *"marking on spawn"*. The shipped design **does** mark on spawn, and that is '
  'what closes the hole rather than opening it — because the stamp is **one-way** and '
  '**everything** gets one. Anything that first exists anywhere but a Backrooms coordinate is '
  'stamped `Outside` for ever, so **a crate of colony cotton is proven ordinary at birth and '
  'can never become odd**, whatever gate it is later hauled through. Under the row’s own '
  'mechanism that cotton would have been stamped nothing, and the hole would have stayed closed '
  'only by vigilance — which is what the row itself worries about in the words *"any future '
  'code that marks a thing anywhere else"*. '
  '**The row’s mechanism was also incomplete.** Marking only generated contents left everything '
  'that comes into existence *inside* a coordinate unmarked: rock mined from its walls, '
  'material from a deconstructed partition, a plant cut in one of its rooms, meat butchered '
  'from something found in it. All of that is genuinely odd and none of it was covered. '
  '**What the row actually asks for is that the property STAY true, and a sentence in a queue '
  'cannot do that.** `proof-odd-origin-laundering.py` holds it as **28 claims**: the stamp is '
  'one-way and refuses to write `Unknown` back over an answer; the field is private and '
  'assigned in exactly two places, both inside the comp; **every origin stamp in the whole tree '
  'is inside the Economy namespace**, which is the row’s *"anywhere else"* made checkable; '
  'merging is refused in **both** directions; a split piece inherits the mark; the service '
  'refuses to restamp; the generation pass skips pawns and returns a **sorted** list. '
  '`plant-odd-origin-laundering.py` lands **15 of 15**, and two of those plants are the ones '
  'that matter: removing the `Outside` arm — which breaks **no visible behaviour at all**, odd '
  'goods stay odd and contracts still fill, while hauled-in cotton quietly becomes '
  'indistinguishable from cotton found there — and writing a stamp from a file outside the '
  'economy, which is the row’s own sentence planted as real code. '
  '**The acceptance test holds:** an odd demand can only be filled by goods stamped in a '
  'coordinate, the mark survives a reload, the 0.7.2-dev legacy mark is still read, and the '
  'whole feature rides four Core hooks with no Harmony and no Core patch.'),
]

NOTES = [
 ('- [ ] **Migration decision or declared development-save break**',
  'NO DECISION IS NEEDED YET, AND THE CANDIDATE LIST IS NOW MEASURED RATHER THAN OPEN-ENDED, '
  '0.12.93-dev. The row fires *"before removing any Def a saved `Thing` references"* — and '
  '**nothing is being removed.** The five `RR_*Staff` PawnKinds were the other half of this '
  'cluster and they are **kept and wired**, not retired, so the save-break risk the row guards '
  'against does not arise from them at all. The one remaining candidate is the hidden legacy '
  'analysis bench, and `SAVE_MIGRATION_POLICY.md` already records its terms in the file: new '
  'starts do not spawn it, it cannot be built, company jobs do not use it, and *"final removal '
  'still requires migration or the explicit development-save boundary"*. **The row stays open '
  'because the decision is the owner’s and it is blocking nothing being built** — a save break '
  'is a decision about other people’s games, and per the M6 answer there are none yet: *"we '
  'dont have other peoples saves we just publish it all and update it as we go fixing bugs"*. '
  'It becomes a real question the first time a removal is actually proposed, and none is.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:80]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("NOTE ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:80]))
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
