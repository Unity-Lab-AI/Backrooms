# -*- coding: utf-8 -*-
"""Apply the `Machine pane` exemption. Defining it was not enough.

`fix-machine-word.py` added `DOC_BANNED_EXEMPT` and **nothing read it** -- which is this project's
single most repeated defect, now caught in the very checkpoint whose record says so. Four of five
bond defects, and seven before them, were *built, correct and never reached*.

The exemption is applied by blanking the exempt phrase out of the prose **before** the ban scans
it, rather than by excusing a match afterwards. That ordering matters: a page saying both
*"the Machine pane"* and *"the machine"* must still fail on the second, and excusing matches one
at a time would have let the first hide the second.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")

OLD = u"""        for term, pattern in DOC_BANNED:
            match = pattern.search(prose)
            if match:
                problems.append("%s says %r to a reader -- %s"
                                % (rel, match.group(0), DOC_BANNED_TERMS[term]))"""

NEW = u"""        # The pane's own name is removed BEFORE the ban scans, not excused after it. A page
        # that says both "the Machine pane" and "the machine" must still fail on the second,
        # and excusing matches one at a time would let the first hide the second.
        scanned = DOC_BANNED_EXEMPT.sub(" ", prose)
        for term, pattern in DOC_BANNED:
            match = pattern.search(scanned)
            if match:
                problems.append("%s says %r to a reader -- %s"
                                % (rel, match.group(0), DOC_BANNED_TERMS[term]))"""

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(CHECKER, encoding="utf-8").read()
failures = []
if u"scanned = DOC_BANNED_EXEMPT.sub(\" \", prose)" not in after:
    failures.append("the exemption is still not applied")
if u"pattern.search(scanned)" not in after:
    failures.append("the ban still scans the unexempted prose")
if after.count(u"DOC_BANNED_EXEMPT") < 2:
    failures.append("DOC_BANNED_EXEMPT is defined and never read -- the defect this fixes")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("exemption applied before the scan, and it is actually read")
