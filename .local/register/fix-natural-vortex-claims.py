# -*- coding: utf-8 -*-
"""The vortex claims now have to know which kind of gate they are talking about.

Owner: *"the gate is a natural one and shouuld always be open ... i understand the machine gate
opening and closing and will kill anyone standing near in front on start up. but the natural
portals are open always right?"*

The claims that proved the vortex is door-sized were right about the machine gate and **wrong to
apply at all to a natural one**, which must have no vortex whatsoever. They are split, and a new
claim states the reason the distinction is load-bearing rather than cosmetic: their wormhole
closes itself after about forty seconds idle, so a permanently-open natural gate is re-dialled
on a loop, and a vortex on it would have fired every time.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

EDITS = [
    (u'''check("BOTH ANCHORS OF THE ROUTE GET THE GATE",
      "StargateBridge.Attach(near)" in emergence and "StargateBridge.Attach(far)" in emergence,''',
     u'''check("BOTH ANCHORS OF THE ROUTE GET THE GATE, BOTH AS NATURAL",
      "StargateBridge.Attach(near, true)" in emergence
      and "StargateBridge.Attach(far, true)" in emergence,'''),

    (u'''check("THE GATE IS ACTUALLY GIVEN THE SIZED PROPERTIES",
      "gate.Initialize(SizedProps(door.def));" in bridge,''',
     u'''check("THE GATE IS ACTUALLY GIVEN THE SIZED PROPERTIES",
      "gate.Initialize(SizedProps(door.def, naturalGate));" in bridge,'''),

    (u'''check("the vortex is one cell deep, across the door's width",
      '.Append(",0,1)</li>")' in bridge
      and "for (int offset = -half; offset <= width - 1 - half; offset++)" in bridge
      and bridge.count('Append("<li>(') == 1,
      "-- the threshold, whichever way the door faces: their VortexCells rotates these offsets by "
      "the door's rotation. EVERY cell must come from the one loop -- checking that the right "
      "cell is emitted does not stop a second one being appended after it")''',
     u'''check("A NATURAL GATE HAS NO UNSTABLE VORTEX AT ALL",
      "naturalGate ? false : offset <= width - 1 - half" in bridge,
      "-- owner: *\\"the natural portals are open always right?\\"*. A natural gate never OPENS, "
      "so nothing spins up and nothing is vaporised. **And this is not cosmetic:** their wormhole "
      "closes itself after about forty seconds idle, so a permanently-open gate is re-dialled on "
      "a loop -- a vortex on it would have detonated its own doorway every time, for ever")

check("the machine gate's vortex is one cell deep, across the door's width",
      '.Append(",0,1)</li>")' in bridge
      and "for (int offset = -half; naturalGate ? false : offset <= width - 1 - half; offset++)"
      in bridge
      and bridge.count('Append("<li>(') == 1,
      "-- owner: *\\"i understand the machine gate opening and closing and will kill anyone "
      "standing near in front on start up\\"*. The threshold, whichever way the door faces. EVERY "
      "cell must come from the one loop -- checking that the right cell is emitted does not stop "
      "a second one being appended after it")

check("and the two kinds cannot share a cached result",
      'door.defName + (naturalGate ? "|natural" : "|machine")' in bridge,
      "-- caching on the def alone would hand the first kind asked for to the second, which is "
      "how a natural gate quietly inherits a machine gate's kawoosh")'''),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("vortex claims split: natural has none, machine has a doorway")
