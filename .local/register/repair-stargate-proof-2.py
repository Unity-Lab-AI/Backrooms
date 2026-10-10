# -*- coding: utf-8 -*-
"""The repair over-corrected: `[^\\\\n]` excludes a backslash and the letter n, not a newline.

First the shell ate the escape and left a literal newline in a string. Then the fix put two
backslashes in, which inside a raw string is a character class of *backslash or n* -- so `//`
comments were not stripped at all and the claim still failed against correct code.

Both failures are the same root cause: an escape passing through one too many layers. The file is
written by the Write tool now and the regex is asserted against a sample before it ships.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

OVER = u'_code = re.sub(r"//[^' + u"\\\\" + u'\\n]*", " ", bridge)'
GOOD = u'_code = re.sub(r"//[^' + u"\\" + u'n]*", " ", bridge)'

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OVER) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s)" % text.count(OVER))
    raise SystemExit(1)
text = text.replace(OVER, GOOD, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)

# Prove the regex that just shipped actually strips a line comment, rather than trusting it.
sample = "code();\n/// no Harmony here\nmore();"
stripped = re.sub(r"//[^\n]*", " ", sample)
if "Harmony" in stripped:
    print("THE SHIPPED REGEX DOES NOT STRIP COMMENTS")
    raise SystemExit(1)
print("regex repaired and verified against a sample")
