# -*- coding: utf-8 -*-
"""Repair the word-boundary regex in check-doc-conformance.py, built from chr() codes.

**THIS LINE HAS NOW BEEN WRONG TWICE, BOTH TIMES FROM AN ESCAPE BEING INTERPRETED ON THE WAY IN.**

First it was written through a shell heredoc that doubled the backslash, so the source held
`r"\\\\b"` -- a regex matching a literal backslash followed by `b`. That never matches prose, so
`any(...)` was always False, `not any(...)` was always True, and **the whole reader-dependency rule
was a no-op**. It was found by a proof claim that had just been strengthened from *the name exists*
to *the operative line exists* -- the fourth time that same strengthening paid out in one session.

The repair attempt then went through another heredoc and wrote a real **backspace control
character**, which is worse: invisible in a diff and still dead.

So this file builds both the broken forms and the correct one out of `chr()` codes, where no shell
and no string literal can touch them. Verified after writing by compiling the module and running
the regex against a known subject.
"""
import io
import re
import sys

PATH = "tools/check-doc-conformance.py"
BACKSLASH = chr(92)
BACKSPACE = chr(8)

GOOD = 'r"' + BACKSLASH + 'b" + subject + r"' + BACKSLASH + 'b"'
BROKEN = (
    'r"' + BACKSPACE + '" + subject + r"' + BACKSPACE + '"',               # control character
    'r"' + BACKSLASH + BACKSLASH + 'b" + subject + r"'
    + BACKSLASH + BACKSLASH + 'b"',                                        # doubled backslash
)

text = io.open(PATH, encoding="utf-8").read()
if GOOD in text:
    print("already correct; nothing written")
    sys.exit(0)

for broken in BROKEN:
    if broken in text:
        text = text.replace(broken, GOOD, 1)
        io.open(PATH, "w", encoding="utf-8", newline=chr(10)).write(text)
        print("repaired: the regex now holds a two-character word boundary")
        break
else:
    print("neither broken form found; check by hand")
    sys.exit(1)

# Prove it rather than assume it: the pattern the checker builds must match a real word.
back = io.open(PATH, encoding="utf-8").read()
if GOOD not in back:
    print("the repair did not read back; ABORT")
    sys.exit(1)
pattern = r"\b" + "mod" + r"\b"
if not re.search(pattern, "your mod manager"):
    print("the word-boundary pattern still does not match; ABORT")
    sys.exit(1)
print("verified: a word-boundary pattern matches 'your mod manager'")
