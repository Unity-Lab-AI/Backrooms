# -*- coding: utf-8 -*-
"""Two existing claims refused the wiring-order change, and both refusals were correct.

* The stray-consumer ordering claim searched for the literal call text, and
  `ConnectStrayConsumers` gained a `coordinate` parameter so the rebuild inside it could name the
  coordinate in its warning. The claim's *question* -- is power wired after the dressing has
  placed things -- is still exactly the right one, and the answer is still yes.

* My own conduit-guard claim from 0.12.63-dev required the guard to appear **twice**, once in each
  spawn path. One of those paths was `SpawnNativeConduit`, which had **no callers at all** and
  threw on a cell that could not take a conduit -- the precise behaviour this checkpoint removed
  everywhere else. Deleting it is right, so the count is one.

**A claim that counts call sites breaks when a call site is correctly deleted, and that is the
claim working.** Both were updated rather than relaxed.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

EDITS = [
    (u'''call_at = genstep.find("ConnectStrayConsumers(map, voidFloor, conduitDef, wiredCells, generator);")''',
     u'''call_at = genstep.find("ConnectStrayConsumers(map, coordinate, voidFloor, conduitDef, wiredCells, generator);")'''),

    (u'''      and genstep.count("if (AlreadyTransmits(map, cell)) { return; }") == 2,''',
     u'''      # ONE path now. The other was `SpawnNativeConduit`, which had no callers and threw
      # `RR_Generation_ContentPlacementFailed` on a cell that could not take a conduit -- the
      # exact behaviour this checkpoint removed everywhere else. A claim that counts call sites
      # refusing a correctly deleted call site is the claim working.
      and genstep.count("if (AlreadyTransmits(map, cell)) { return; }") == 1,'''),

    (u'''check("and it asks Core's own property rather than naming a def",
      "List<Thing> things = cell.GetThingList(map);" in genstep
      and 'GetNamedSilentFail("HiddenConduit")' in genstep,''',
     u'''check("and it asks Core's own property rather than naming a def",
      "List<Thing> things = cell.GetThingList(map);" in genstep
      and 'GetNamedSilentFail("HiddenConduit")' in genstep
      and "private static void SpawnNativeConduit(" not in genstep,'''),
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

# The standalone claim added by fix-proof-1264.py duplicated what now lives on the guard claim.
DUPLICATE = u'''check("and the dead throwing conduit spawner is gone rather than left to be called",
      "private static void SpawnNativeConduit(" not in genstep,
      "-- it had no callers and threw `RR_Generation_ContentPlacementFailed` on a cell that could "
      "not take a conduit, which is the exact behaviour this checkpoint removed everywhere else")

'''
if DUPLICATE in text:
    text = text.replace(DUPLICATE, u"", 1)
    print("folded the duplicate dead-spawner claim into the guard claim")

io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("both refusals answered")
