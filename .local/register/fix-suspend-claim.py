# -*- coding: utf-8 -*-
"""The claim recorded the ids and never asserted the suspending. Eighth instance.

A plant deleted `bill.suspended = true;` and left `suspendedByGateControl.Add(...)` standing, so
gate control recorded which bills it had suspended while suspending none of them -- and every
asserted line was still present. **Computing a value and using it are two different facts**, for
the eighth time in this session.

The two lines are pinned together and in order, so neither can go without the other.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

OLD = u'''      "suspendedByGateControl.Add(bill.GetUniqueLoadID());" in console
      and "if (bill == null || bill.suspended) { continue; }" in console'''

NEW = u'''      # **THE SUSPENDING, not just the recording.** A plant deleted `bill.suspended = true`
      # and left the Add line, so gate control recorded which bills it had suspended while
      # suspending none of them, and every asserted line was still there. Eighth instance this
      # session. The two are pinned together and in order, so neither can go without the other.
      (u"bill.suspended = true;" + chr(10)
       + "                    suspendedByGateControl.Add(bill.GetUniqueLoadID());") in console
      and "if (bill == null || bill.suspended) { continue; }" in console'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the claim pins the suspend and the record together")
