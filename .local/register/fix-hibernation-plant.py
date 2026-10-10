# -*- coding: utf-8 -*-
"""Retarget the hibernation plant, and plant the reporting that was missing.

The hibernation guard grew a reason string when every silent refusal learned to name itself, so
the plant's one-line anchor no longer matches. Retargeted at the condition rather than the whole
statement, which is also the more honest plant: what must not happen is *dialling a hibernating
gate*, not *this exact formatting*.

Two plants added for the reporting itself. **The reason the wormhole took a whole launch to
diagnose is that every refusal returned without a word** -- the owner's log contained nothing at
all while the gate sat there doing nothing. That reporting is now load-bearing, so it is guarded
like anything else: silence it and the proof must refuse.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-stargate-bridge.py")

OLD = ('    ("a hibernating gate is dialled, fighting their one-gate-per-map rule", EMERGENCE,\n'
       '     "if (StargateBridge.IsHibernating(near)) { return; }", ""),')

NEW = ('    ("a hibernating gate is dialled, fighting their one-gate-per-map rule", EMERGENCE,\n'
       '     "if (StargateBridge.IsHibernating(near))", "if (false)"),\n'
       '\n'
       '    # EVERY SILENT REFUSAL MUST NAME ITSELF. The wormhole took a whole launch to diagnose\n'
       '    # because these paths returned without a word and the owner\'s log held nothing at all.\n'
       '    ("A REFUSAL GOES SILENT AGAIN, so the next launch cannot say why", EMERGENCE,\n'
       '     "private void ReportGateState(string reason)",\n'
       '     "private void ReportGateStateUnused(string reason)"),\n'
       '\n'
       '    ("the far end being a non-door stops being reported", EMERGENCE,\n'
       '     "the far end of this route is not a door",\n'
       '     "the far end of this route is not a doorway"),')

text = io.open(PLANT, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("hibernation plant retargeted; two reporting plants added")
