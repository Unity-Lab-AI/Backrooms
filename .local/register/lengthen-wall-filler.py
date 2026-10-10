# -*- coding: utf-8 -*-
"""Lengthen the wall-plant filler past the new limit.

`reaim-three-plants.py` wrote a 335-character filler against a **360**-character wall and its own
verification refused it. **A plant that cannot trip the rule it tests is worse than no plant** --
it reports MISSED and sends somebody looking for a bug in the checker.

The old filler was sized for the old 700 limit and was cut down too far when the limit dropped.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-playing-and-help.py")

OLD = (u"The company account is a ledger in dollars and it pays quoted company costs such as "
       u"staff wages and site fees and procurement orders and outstanding obligations, and it "
       u"is never spawned as physical silver for somebody to haul across a map on foot, which "
       u"is the whole distinction the two kinds of money exist to draw in the first place.")

NEW = (u"The company account is a ledger in dollars and it pays quoted company costs such as "
       u"staff wages and site fees and procurement orders and outstanding obligations, and it "
       u"is never spawned as physical silver for somebody to haul across a map on foot, which "
       u"is the whole distinction the two kinds of money exist to draw in the first place, and "
       u"it is also the reason the ledger pane lists a written reason beside every movement "
       u"rather than leaving a player to work out where the money went on their own.")

text = io.open(SUITE, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
if len(NEW) <= 360:
    print("THE REPLACEMENT IS %d CHARACTERS AND STILL UNDER 360" % len(NEW))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(SUITE, encoding="utf-8").read()
if NEW not in after:
    print("THE LONGER FILLER WAS NOT WRITTEN")
    raise SystemExit(1)
print("filler is now %d characters against a 360 limit" % len(NEW))
