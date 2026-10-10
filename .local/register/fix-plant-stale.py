# -*- coding: utf-8 -*-
"""Drop the plant that targeted the dead conduit spawner.

*"the guard is kept on one path and dropped from the other"* planted its fault by deleting the
`AlreadyTransmits` call out of `SpawnNativeConduit` -- a method with no callers that threw on a
cell which could not take a conduit, and which this checkpoint deleted. There is only one path
now, and the plant for it is *"A SECOND TRANSMITTER LANDS ON A CELL THAT ALREADY HAS ONE"*, which
still applies.

**The suite refused to run rather than silently matching nothing**, which is the behaviour that
matters: a plant that finds no match proves nothing while appearing to pass.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

STALE = u'''    ("the guard is kept on one path and dropped from the other", GEN,
     "            // Not a generator fault: the cell is already wired, by somebody else, and that is"
     + NL + "            // exactly as good as wiring it ourselves." + NL
     + "            if (AlreadyTransmits(map, cell)) { return; }" + NL, ""),

'''

text = io.open(SUITE, encoding="utf-8").read()
if text.count(STALE) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(STALE))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(STALE, u"", 1))
print("stale plant removed")
