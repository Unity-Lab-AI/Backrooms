# -*- coding: utf-8 -*-
"""The compliance claim failed against correct code, because the file EXPLAINS the rule.

`StargateBridge.cs` carries, in its doc comment, the sentence *"No Harmony, no detour, no
`SetValue`, no `BindingFlags.NonPublic`."* -- which is exactly the right thing for that file to
say, and exactly what made a bare substring test report a violation.

`check-compliance.py` strips comments before scanning for this precise reason. A proof that does
not is checking the prose rather than the code. Comments are stripped here too, and a second
claim requires the explanation to still be present -- so the lazy fix of deleting the sentence to
satisfy a grep fails as well.

(Written through the Write tool rather than a heredoc: the shell ate the `\\n` in the regex on
the first attempt, which is the ninth time that has happened in this project.)
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

OLD = u'''check("no Harmony, no detour, no reflection write, no private read",
      "Harmony" not in bridge and "SetValue" not in bridge
      and "BindingFlags.NonPublic" not in bridge,
      "-- the standing rule, and this is the file most likely to be tempted to break it")'''

NEW = u'''# COMMENTS STRIPPED FIRST, because the first draft of this claim failed against CORRECT code:
# the file's own doc comment says "No Harmony, no detour, no `SetValue`, no
# `BindingFlags.NonPublic`", and a bare substring test cannot tell an explanation from a
# violation. `check-compliance.py` strips comments before scanning for exactly this reason, and
# a proof that does not is checking the prose rather than the code.
_code = re.sub(r"//[^\\n]*", " ", bridge)
_code = re.sub(r"/\\*.*?\\*/", " ", _code, flags=re.S)

check("no Harmony, no detour, no reflection write, no private read",
      "Harmony" not in _code and "SetValue" not in _code
      and "BindingFlags.NonPublic" not in _code,
      "-- the standing rule, and this is the file most likely to be tempted to break it")

check("and the file still EXPLAINS that rule rather than only obeying it",
      "BindingFlags.NonPublic" in bridge,
      "-- the doc comment naming what is banned is why the claim above strips comments. Deleting "
      "the sentence to satisfy a grep would be the wrong fix, so it fails here too")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("compliance claim now strips comments, and requires the explanation to survive")
