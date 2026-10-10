# -*- coding: utf-8 -*-
"""Repair the one line the shell ate, and record the ninth instance of the same mistake.

A heredoc was used to patch `proof-stargate-bridge.py` and the shell expanded the `\\n` inside
`r"//[^\\n]*"`, leaving a literal newline inside a string literal and a file that will not parse.

**Ninth time. The rule is: use the Write tool for anything containing a backslash escape, an
apostrophe, or a regex.** This file exists so the count is written down rather than remembered.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

BROKEN = u'_code = re.sub(r"//[^\n]*", " ", bridge)'
FIXED = u'_code = re.sub(r"//[^\\\\n]*", " ", bridge)'

text = io.open(PROOF, encoding="utf-8").read()
if text.count(BROKEN) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(BROKEN))
    raise SystemExit(1)
text = text.replace(BROKEN, FIXED, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)

import ast
try:
    ast.parse(io.open(PROOF, encoding="utf-8").read())
    print("repaired and parses")
except SyntaxError as problem:
    print("STILL BROKEN: %s" % problem)
    raise SystemExit(1)
