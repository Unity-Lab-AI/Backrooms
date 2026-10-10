# -*- coding: utf-8 -*-
"""Close the two world-tile rows, which are the same row written twice."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SHARED = (
 'CLOSED 0.12.96-dev ON MEASUREMENT — **built, and asserted.** The row asks for *"a new world '
 'object and a generated map"*, and `RimroomsCampaignComponent.ClaimTileAndWalkOut` is both: a '
 'Core `Settlement` is the world object and `GetOrGenerateMapUtility.GetOrGenerateMap(tile, null)` '
 'is the map. It is reached from `LeaveThroughWorldExit`, **a gizmo the player clicks**, and '
 '`proof-world-exit.py` asserts that routine has **exactly one caller** and that the caller is a '
 'player command — no tick, no work giver, no incident can reach it. '
 '**The ordering is the safety and it is claimed:** the map is generated and the return gate '
 'established **before any pawn is despawned**, so if the gate cannot be established nothing has '
 'moved; a failed spawn puts the pawn back where it was; and a claim that moves nobody is reported '
 'as a refusal rather than a success that did not happen. '
 '**Over the five-map cap it forms a caravan instead**, per the owner\'s own earlier rule *"anything '
 'over 5 maps defaults to caravans"* — and that is the **only** path in the mod reaching '
 '`PassToWorld`, from a player\'s click, into a caravan they still own.')

CLOSED = [
 ('- [ ] **A world tile the branch does not hold** — still the larger half,',
  SHARED + ' **This row and its twin below were the same work written twice**, in two sections — '
  'which is how a finished thing gets built again. Both are closed together and both say so.'),
 ('- [ ] **A world tile the branch does not hold** — still open.',
  SHARED + ' **The duplicate of the row above**, in a different section and in slightly different '
  'words. Kept and closed rather than silently dropped, because LAW #0 does not let a restatement '
  'be deleted — but recorded as the duplicate it is.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:85]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
