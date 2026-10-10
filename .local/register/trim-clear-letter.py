# -*- coding: utf-8 -*-
"""Trim `RR_Clear_Body` to inside Core's own letter range.

`check-display-style.py` refused it: **734 characters on a surface where the longest letter Core
ships is 666**, median 62. The checker measures against Core's own population rather than a number
somebody picked, which is why it is worth obeying -- a letter longer than anything the game ships
is one the window was never laid out for.

**Every one of the seven numbers is kept.** The cut is adjectives and restatement, not
information: the player still learns how many of their people were resolved, how many went into
the ground or the fire, what was repaired, what the paper was worth, what the bill was, and how
many arrived. That was the whole point of the letter.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Requests.xml")

OLD = u"""Everyone at the laboratory went down. The Company does not lose a facility, and it does not leave anybody behind who was there.

They came in on all-access passes and left no one standing. {1} of your people were resolved on site. {2} of the dead were buried on the property or put in the fire. {3} damaged structures and fixtures were brought back to full repair, and every open connection was shut down at the gate.

The paper is gone. {4} credits of bearer bonds were collected from the site and will not be seen again. A further {5} credits has been drawn from the account, recorded as restocking the petty cash.

{6} replacement staff are on the ground as of today, on the ordinary wage. The gate is still commissioned. {0} is open."""

NEW = u"""Everyone at the laboratory went down. The Company does not lose a facility.

They came in on all-access passes and left no one standing: {1} of your people resolved on site, {2} of the dead buried or burned on the property, {3} structures repaired, every connection shut down at the gate.

The paper is gone. {4} credits of bonds were taken and will not be seen again, and {5} credits drawn from the account as restocking the petty cash.

{6} replacement staff are on the ground today, on the ordinary wage. The gate is still commissioned. {0} is open."""

text = io.open(KEYED, encoding="utf-8-sig").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(KEYED, encoding="utf-8-sig").read()
body = after.split(u"<RR_Clear_Body>")[1].split(u"</RR_Clear_Body>")[0]

failures = []
if len(body) > 666:
    failures.append("still %d characters, over Core's longest of 666" % len(body))
for index in range(7):
    if (u"{%d}" % index) not in body:
        failures.append("argument {%d} was lost in the trim" % index)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("RR_Clear_Body is %d characters, inside Core's range, all seven arguments kept"
      % len(body))
