# -*- coding: utf-8 -*-
"""Two more claims that described the sizing without requiring it to be used.

Instances thirty-one and thirty-two of the same trap, in the batch that fixed nine of them:

  1. **Nothing asserted that the gate is actually given the sized properties.** Every claim
     checked that `SizedProps` computes the right numbers; none checked that `Attach` passes them
     to the component. A plant swapped the call back to `donorProps` and the whole section still
     passed while a 1x1 door got a seven-by-seven kawoosh. **Computing a value correctly and
     using it are two different facts, and only one of them was being proved.**

  2. **The vortex-depth claim checked that the right cell is emitted, not that no others are.**
     Appending `<li>(0,0,2)</li>` after the loop left the one-cell-deep assertion satisfied.
     Every vortex cell must come from the single loop, so the loop's `Append` is required to be
     the only one.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

OLD = u'''check("the vortex is one cell deep, across the door's width",
      '.Append(",0,1)</li>")' in bridge
      and "for (int offset = -half; offset <= width - 1 - half; offset++)" in bridge,
      "-- the threshold, whichever way the door faces: their VortexCells rotates these offsets by "
      "the door's rotation")'''

NEW = u'''check("THE GATE IS ACTUALLY GIVEN THE SIZED PROPERTIES",
      "gate.Initialize(SizedProps(door.def));" in bridge,
      "-- every other claim here proves the sizing is COMPUTED correctly. This is the one that "
      "proves it is USED. A plant swapped this back to their unsized properties and the whole "
      "section still passed while a 1x1 door got a seven-by-seven kawoosh")

check("the vortex is one cell deep, across the door's width",
      '.Append(",0,1)</li>")' in bridge
      and "for (int offset = -half; offset <= width - 1 - half; offset++)" in bridge
      and bridge.count('Append("<li>(') == 1,
      "-- the threshold, whichever way the door faces: their VortexCells rotates these offsets by "
      "the door's rotation. EVERY cell must come from the one loop -- checking that the right "
      "cell is emitted does not stop a second one being appended after it")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("two claims tightened: the sizing is used, and the loop is the only source of cells")
