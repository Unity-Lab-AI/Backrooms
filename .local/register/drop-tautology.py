# -*- coding: utf-8 -*-
"""Remove a claim that can never fail from `proof-review-exposure.py`.

`check("AND EVERY REFUSAL IT CAN RETURN HAS A STRING", True, "")` was a header dressed as a
claim. **A claim that cannot fail inflates the count and proves nothing**, which is the exact
criticism this battery exists to make of other people's tests. The real assertion is the one
below it, which computes the key list out of the source and reports any missing -- so the header
is folded into it and the tautology goes.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-review-exposure.py")

OLD = u'''check("AND EVERY REFUSAL IT CAN RETURN HAS A STRING",
      True,  # computed below so the detail can name them
      "")
service_keys = sorted(set(re.findall(r'"(RR_Review_[A-Za-z]+)"', review)))
missing_keys = [key for key in service_keys
                if ("<%s>" % key) not in investigation_keyed]
check("  (%d refusal keys, all present)" % len(service_keys),
      len(service_keys) >= 9 and not missing_keys,'''

NEW = u'''# The key list is computed OUT OF THE SERVICE, never typed here: a hand-kept list of refusal
# keys is a second derivation that goes stale the first time a refusal is added.
service_keys = sorted(set(re.findall(r'"(RR_Review_[A-Za-z]+)"', review)))
missing_keys = [key for key in service_keys
                if ("<%s>" % key) not in investigation_keyed]
check("AND EVERY ONE OF THE %d REFUSALS IT CAN RETURN HAS A STRING" % len(service_keys),
      len(service_keys) >= 9 and not missing_keys,'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u"      True,  # computed below" in after:
    failures.append("the tautology is still there")
if u"check(" in after and after.count(u"check(\n") > 0:
    pass
# No claim in this proof may pass a bare literal as its condition.
import re as _re
for match in _re.finditer(r"check\((?:[^,]|\n)*?,\s*(True|False)\s*,", after):
    failures.append("a claim still passes a literal condition: %r" % match.group(0)[:60])
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("tautology removed; no claim in the proof passes a literal condition")
