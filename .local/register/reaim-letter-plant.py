# -*- coding: utf-8 -*-
"""Re-aim the letter plant. Trimming `RR_Clear_Body` left its anchor pointing at deleted prose.

`check-display-style.py` refused the letter at 734 characters against Core's longest of 666, so
it was trimmed -- and the trim removed the exact sentence `plant-clearsquad.py` planted against.
**`check-plant-anchors.py` caught it**, which is the seventeenth checker doing the only job it
has: reading every anchor in every suite and saying which can no longer find its target.

Worth noting plainly: **the plant suite still PASSED 27 of 27 before this was found.** The stale
anchor would have raised `PLANT SETUP BROKEN` on the next run rather than silently passing, but
the checker found it first, in bulk, without anybody running the suite at all. That is the whole
argument for having it.

**The claim is unchanged** -- the letter must still tell the player what the clearance cost them.
Only the text it reaches for has moved.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-clearsquad.py")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Requests.xml")

OLD = (u'    ("the letter stops telling the player what it cost them", KEYED,\n'
       u'     "A further {5} credits has been drawn from the account",\n'
       u'     "A further amount has been drawn from the account", PROOF),')

NEW = (u'    ("the letter stops telling the player what it cost them", KEYED,\n'
       u'     "and {5} credits drawn from the account as restocking the petty cash",\n'
       u'     "and an amount drawn from the account as restocking the petty cash", PROOF),')

text = io.open(SUITE, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("SUITE ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)

# And the new anchor must actually exist in the target, or this just moves the problem.
keyed = io.open(KEYED, encoding="utf-8-sig").read()
NEEDLE = u"and {5} credits drawn from the account as restocking the petty cash"
if keyed.count(NEEDLE) != 1:
    print("THE NEW ANCHOR IS NOT IN THE LETTER: %d" % keyed.count(NEEDLE))
    raise SystemExit(1)

io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(SUITE, encoding="utf-8").read()
failures = []
if u"A further {5} credits has been drawn" in after:
    failures.append("the stale anchor is still there")
if NEEDLE not in after:
    failures.append("the new anchor was not written")
if u'"the letter stops telling the player what it cost them"' not in after:
    failures.append("the claim label changed; it should not have")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("letter plant re-aimed at the trimmed text; the claim is unchanged")
