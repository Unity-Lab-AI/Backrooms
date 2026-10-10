# -*- coding: utf-8 -*-
"""Rewrite the gate-readiness conclusion strings for the three real situations.

Owner, verbatim: *"the store start has a natural portal and to build a machanical one they need
to contact the company and resaerch whats needed"*. A start that is out of contact and has no
completed projects is **earlier in its own progression**, not deficient, and the first version of
this readout called it *"does not arrive able to raise a gate"*.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                    "Keyed", "RR_StartupSetup.xml")

original = io.open(PATH, encoding="utf-8").read()

OLD = (u"  <RR_Setup_GateNotReady>This branch does not arrive able to raise a gate. Missing: {0}. "
       u"That may be the point of this opening rather than an oversight - the inside start begins "
       u"in the Backrooms and looks for a way out - but it is worth knowing before you start."
       u"</RR_Setup_GateNotReady>")

NEW = (u"  <RR_Setup_GateNotReady>This branch is in contact and holds the gate research, but is "
       u"missing hardware: {0}. Build it or order it from the company before an opening is "
       u"possible.</RR_Setup_GateNotReady>\n"
       u"  <RR_Setup_GateLaterWork>A built gate is later work for this opening, not a missing "
       u"piece of it. Not here yet: {0}.</RR_Setup_GateLaterWork>\n"
       u"  <RR_Setup_GateContactRoute>This branch starts outside company contact and with no gate "
       u"research finished, so it is not meant to assemble one yet. There is already a way "
       u"through that nobody built. Reach the corporation, research what a gate needs, then order "
       u"the equipment.</RR_Setup_GateContactRoute>\n"
       u"  <RR_Setup_GateInsideRoute>This opening begins inside the Backrooms, outside company "
       u"contact and with no gate research finished. Finding a way out comes first; ways through "
       u"that nobody built reach only so deep, and going further needs a gate you have earned the "
       u"right to build.</RR_Setup_GateInsideRoute>")

if u"RR_Setup_GateContactRoute" in original:
    print("already rewritten")
    raise SystemExit(0)
if original.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s)" % original.count(OLD))
    raise SystemExit(1)

io.open(PATH, "w", encoding="utf-8", newline="").write(original.replace(OLD, NEW, 1))
print("conclusion strings rewritten: three situations, three answers")
