# -*- coding: utf-8 -*-
"""Six existing claims named signatures and call shapes that 0.12.71-dev changed.

Every one of them failed against CORRECT code, which is the right direction for a claim to fail
in: four were cascades of `stray_at == -1` after `ConnectStrayConsumers` went from `void` to
`bool`, one counted a `FixtureCell` call that now carries the approach argument, and one counted
three identical `RebuildPowerNets(map, coordinate);` statements where two are now guarded.

**The claims are kept and re-aimed, never weakened.** Each still asserts the same fact: the sweep
is found, the pass runs after the dressing, one function finds a cell, one implementation rebuilds
the grid.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

EDITS = [
    # The sweep reports whether the grid is still answering, so its signature changed.
    (u'stray_at = genstep.find("private static void ConnectStrayConsumers(")',
     u'stray_at = genstep.find("private static bool ConnectStrayConsumers(")'),
    # The call is inside the `&&` that stops a second rebuild after a refusal, so it has no
    # trailing semicolon. Matched up to the argument list, which is the part the claim is about.
    (u'call_at = genstep.find("ConnectStrayConsumers(map, coordinate, voidFloor, conduitDef, wiredCells, generator);")',
     u'call_at = genstep.find("ConnectStrayConsumers(map, coordinate, voidFloor, conduitDef, wiredCells, generator)")'),
    # The landmark asks for a cross-adjacent cell first and falls back to none, so `FixtureCell`
    # takes an approach set. THREE calls now, and the count still proves one search loop.
    (u'      content.count("FixtureCell(map, room, reserved, thing, rotation, preferred)") == 2\n',
     u'      content.count("FixtureCell(map, room, reserved, thing, rotation, preferred, ") == 3\n'),
    # Two of the three rebuild calls are guarded now -- that IS the fix for the owner's sixty-two
    # warnings -- so the claim counts the calls rather than one spelling of them.
    (u'      and genstep.count("RebuildPowerNets(map, coordinate);") == 3,',
     u'      and genstep.count("RebuildPowerNets(map, coordinate)") == 4,'),
    (u'      "private static void RebuildPowerNets(Map map, CoordinateRecord coordinate)" in genstep',
     u'      "private static bool RebuildPowerNets(Map map, CoordinateRecord coordinate)" in genstep'),
    (u'      and "try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }" in genstep',
     u'      and "map.powerNetManager.UpdatePowerNetsAndConnections_First();" in genstep'),
    (u'      "-- THREE call sites, one implementation.',
     u'      "-- FOUR call sites, one implementation, and two of them guarded.'),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:72]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("six claims re-aimed at the shapes 0.12.71-dev changed")
