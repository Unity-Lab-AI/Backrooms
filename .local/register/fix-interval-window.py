# -*- coding: utf-8 -*-
"""The window was fixed-width, and stripping comments pulled the next method into it.

The claim that the glow and the wormhole refresh together is anchored at
`CompTickInterval`, then reads a window. Once comments are stripped — which the other eight
fixes required — the doc block between `CompTickInterval` and `CompTickRare` disappears, the two
method bodies sit a few lines apart, and a 600-character window swallows both. So deleting
`RefreshStargate()` from the interval tick still matched the copy in the rare tick.

**A window into a file is only a scope if it ends where the thing it is scoped to ends.** It now
stops at the next `public override`, which is the end of the method by construction.

That is the thirtieth instance of the claim-scoping trap, and the second today whose cause was a
previous fix in the same batch: stripping comments was correct, and it moved the ground under a
claim that was measuring in characters rather than in structure.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

OLD = u'''_interval = emergence.find("public override void CompTickInterval(int delta)")
_window = emergence[_interval:_interval + 600] if _interval >= 0 else ""'''

NEW = u'''_interval = emergence.find("public override void CompTickInterval(int delta)")
# BOUNDED BY THE NEXT METHOD, not by a character count. With comments stripped, CompTickRare sits
# a few lines below and a fixed-width window swallowed its identical pair -- so deleting the call
# from the tick a door actually receives still matched the copy in the tick it never gets.
_after = emergence[_interval:] if _interval >= 0 else ""
_next = _after.find("public override", 40)
_window = _after[:_next] if _next > 0 else _after'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the interval window ends where the method ends")
