# -*- coding: utf-8 -*-
"""Prepend the 0.12.86-dev entry. Newest first, nothing above it rewritten."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"

ENTRY = """## 0.12.86-dev - 2026-10-04 - Every tab is a utility, the door says what to do next, and the package asks for nothing

- **The queue was holding fragments of finished work, and the gate that guards it could not see
  them.** `tools/archive-finished-todo.py` ended an `[x]` item at the next blank line, so every
  row whose closure carried its own evidence archived its **bullet line only** and left the rest
  behind - **twelve stranded lines across 0.12.82-dev, 0.12.83-dev, 0.12.84-dev and
  0.12.85-dev**. Both halves of the owner's direction broke at once: `FINALIZED.md` was missing
  the record and `TODO.md` was holding finished text. The mover's proof is a reassembly identity,
  `kept + moved == original`, which is a real proof of the thing it proves and **says nothing
  about where a row ends**. Fixed at the source; the mover now refuses outright when unindented
  prose sits after a closed row rather than guessing which side it belongs to; every stranded
  line is recovered into `FINALIZED.md` with the row it came from, read from the pre-move
  snapshot the mover itself wrote. `tools/check-queue-integrity.py` is checker 18 and fails on a
  stranded continuation, on closure evidence that is not on a row, and on any `[x]` left in a
  queue.
- **The Operations panel is a utility, measured.** 4,015 on-screen words to **2,551**, with
  **1,583** moved onto hovers and words-per-action from 32.9 to 22.6. All eighteen pane files
  measured and named. `UI/OperationsControls.cs` holds the two primitives the whole panel now
  shares: a short line with its explanation on hover, and a control that stays visible and says
  why it will not work instead of being replaced by a sentence about its own absence.
- **And the instrument measuring it was blind twice.** It counted keys picked into a variable and
  translated later as **zero** - 367 words, the longest instructions in the panel, including the
  entire eleven-branch objective chain - so indirect groups are now resolved and charged at their
  **worst** branch, because exactly one draws per frame. And it read comments as code: a comment
  containing the word *tooltip* reclassified a heading into the hover bucket. Two ceilings went
  **up** when the blindness was removed and then came down by the work.
- **The door says what to do next.** The eleven start-up checks left a private method on the
  Operations window for `Gate/GateStartupChecklist.cs`, and the gate's own inspect card names the
  first unfinished one, first on the card - above ten readouts that all answered *what is the
  state* and none of which answered *what do I do*. The extraction normalises byte-for-byte
  identical to the original. One list, read by both surfaces, so they cannot disagree.
- **Setting the coordinate and opening the connection are commands on the door.**
  `Gate/GateAddressControls.cs`. They were the last two start-up actions that existed only as
  panel buttons, so a player could build, crew and calibrate the machine in the world and then
  had to find a tab to aim it. Both call the same services the pane calls, with the same freeze
  notice in front of the one that builds a map, and both grey out with a reason rather than
  disappearing.
- **The package declares no hard dependencies.** `About.xml` declared **293**; every one was
  already in `loadAfter`, so 1,462 lines of requirement wall came out and the load order changed
  by nothing at all. Verified as an identity before the deletion, not after.
- **A plant found the gap that deletion created.** With nothing declared, *every declared
  dependency must also be ordered* has nothing to iterate, so `loadAfter` became the only thing
  carrying the weight and the only thing unchecked - and the suite reported **MISSED** when a
  former dependency was removed from the order. `check-register-compliance.py` now requires
  `loadAfter` to match the 294-row profile register exactly. This package sat at position **197
  of 296** in the owner's live load order with 99 mods loading after it.
- **The claim rule inverted rather than relaxing.** The dangerous sentence used to be *"this
  needs nothing"*; it is now *"this works with everything"*, which nobody has shown.
  `check_broad_compatibility` refuses ten such phrasings while the declared count is zero. D1 is
  unmoved: do not announce compatibility until validation is complete. `ROADMAP.md` already
  listed promising blanket compatibility as a non-goal and nothing enforced it until now.
- **A plant suite had been crashing rather than running.** Two entries in
  `plant-startplacement.py` carried four elements where the baseline generator reads a fifth, so
  it raised `IndexError` on the line that prints `baseline` - which reads like the start of a
  run. Ninety-six plants had not been set since the day it was added. Fixed; the suite reports
  **105 of 105 caught**, and **853** plant anchors across twenty-three suites are findable in
  their targets.
- **Decision records amended in the same commit**, with every superseded owner quote struck in
  place rather than deleted: `GATE_0_DECISIONS.md` D3/D4, `ROADMAP.md`'s decision log,
  `ARCHITECTURE.md` B8, and the compliance row whose evidence line claimed `loadAfter` held Core
  alone when it holds 294 entries.

"""

text = io.open(PATH, encoding="utf-8").read()
if "## 0.12.86-dev" in text:
    print("already present")
    sys.exit(0)

head = "# Changelog" + NL + NL
if not text.startswith(head):
    print("CHANGELOG does not start with the expected heading; nothing written")
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(head + ENTRY + text[len(head):])
print("prepended the 0.12.86-dev entry (%d lines)" % (ENTRY.count(NL) + 1))
