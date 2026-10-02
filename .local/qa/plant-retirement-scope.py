#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plant the clause-scoping defect back in and confirm the tightened rule catches it.

The live text this was written for is reproduced verbatim as case 1: a paragraph carrying three
false dependency claims that read green for a day because an unrelated "until" sat on the same
line. Cases 2 and 3 guard the other direction -- a genuine retirement in the same clause must
still be excused, or the fix would turn every historical record into a finding.

Read-only. Writes nothing.
"""

from __future__ import print_function

import importlib.machinery
import importlib.util
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

loader = importlib.machinery.SourceFileLoader(
    "doc_conformance", os.path.join(REPO, "tools", "check-doc-conformance.py"))
spec = importlib.util.spec_from_loader(loader.name, loader)
conformance = importlib.util.module_from_spec(spec)
loader.exec_module(conformance)

LIVE_DEFECT = (
    u"**Gate 0 decisions recorded:** public Steam Workshop as the first distribution target "
    u"(**D1 changed 2026-09-29**; was a private RWT prototype first), with no compatibility "
    u"announced until validation is complete; exact displayed title `Rimrooms - Async "
    u"Industries`; semantic versions; Core-only solo path; optional support for all five DLC; "
    u"other 294-profile mods optional; English-first localization-ready.")

CASES = (
    # (name, line, phrase, must_be_excused)
    ("the live defect: unrelated 'until' on the same line",
     LIVE_DEFECT, "core-only", False),
    ("retirement in the same clause is still excused",
     u"The Core-only solo path is superseded by the declared collection.", "core-only", True),
    ("retirement in a NEIGHBOURING clause does not excuse",
     u"That decision is superseded; the Core-only solo path remains the target.",
     "core-only", False),
    ("a dated change in the same clause is excused",
     u"Core-only was the target, changed 2026-10-01 to a declared collection.",
     "core-only", True),
    ("a bare claim with no retirement anywhere",
     u"- Target RimWorld 1.6. Preserve a complete Core-only solo campaign.", "core-only", False),
)


def main():
    failures = 0
    for name, line, phrase, must_be_excused in CASES:
        excused = conformance.retirement_covers(line, phrase)
        ok = (excused == must_be_excused)
        if not ok:
            failures += 1
        print("%-4s %-56s excused=%-5s expected=%-5s"
              % ("PASS" if ok else "FAIL", name[:56], excused, must_be_excused))

    print("")
    if failures:
        print("FAIL: %d of %d planted cases behaved wrongly" % (failures, len(CASES)))
        return 1
    print("PASS: %d of %d planted cases caught, including the live defect" % (len(CASES), len(CASES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
