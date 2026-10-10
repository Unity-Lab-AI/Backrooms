# -*- coding: utf-8 -*-
"""Two plant anchors in `plant-clearsquad.py` were written from memory of the source, not from it.

The repair and gate calls sit on the brace line -- `{ repaired += RepairTheFacility(...); }` --
and the anchors assumed they were on their own indented line. `PLANT SETUP BROKEN (0 matches)` is
the suite refusing rather than silently testing nothing, which is exactly the behaviour wanted,
and it is the same class of mistake `tools/check-plant-anchors.py` exists to find in bulk.

**Re-aimed at the code as it stands. The claim each one plants against is unchanged.**
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-clearsquad.py")

EDITS = [
    (u'    ("REPAIR IS WRITTEN AND NEVER RUN", SQUAD,\n'
     u'     "                repaired += RepairTheFacility(owned[index]);" + NL, "", PROOF),',
     u'    ("REPAIR IS WRITTEN AND NEVER RUN", SQUAD,\n'
     u'     "            { repaired += RepairTheFacility(owned[index]); }", "            { }",\n'
     u'     PROOF),'),

    (u'    ("THE GATE IS NEVER SHUT DOWN", SQUAD,\n'
     u'     "                gates += ShutDownGates(owned[index]);" + NL, "", PROOF),',
     u'    ("THE GATE IS NEVER SHUT DOWN", SQUAD,\n'
     u'     "            { gates += ShutDownGates(owned[index]); }", "            { }", PROOF),'),
]

text = io.open(SUITE, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text)

after = io.open(SUITE, encoding="utf-8").read()
failures = []
if u'"            { repaired += RepairTheFacility(owned[index]); }"' not in after:
    failures.append("the repair anchor was not re-aimed")
if u'"            { gates += ShutDownGates(owned[index]); }"' not in after:
    failures.append("the gate anchor was not re-aimed")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("two anchors re-aimed at the source as it stands; both claims unchanged")
