# -*- coding: utf-8 -*-
"""Collapse an always-true clause left in the re-aimed dependency rule.

`not any(f for f in [None] if False)` is always True and says nothing. It was cruft from drafting
and a condition nobody can read is a condition nobody can trust.

**Written as a file because the first attempt was a bash heredoc and the line continuation's
single backslash arrived as two.** That is the THIRTEENTH time this trap has been hit, and
`docs/NOW.md` has said so since 0.12.46-dev: *"Use a FILE for any script with escapes or
apostrophes, never a bash heredoc."*
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-register-compliance.py")

OLD = (u"        if not any(f for f in [None] if False) and not unordered and not unreachable "
       + chr(92) + u"\n                and not nameless and not duplicates:")
NEW = u"        if not (duplicates or nameless or unreachable or unordered):"

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(CHECKER, encoding="utf-8").read()
if u"any(f for f in [None] if False)" in after:
    print("THE CRUFT IS STILL THERE")
    raise SystemExit(1)
print("always-true clause collapsed to the four conditions it actually meant")
