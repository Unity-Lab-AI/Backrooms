# -*- coding: utf-8 -*-
"""Checker 25 -- an open row must NAME its blocker, never point at a neighbour.

Why this exists, and why it was declined once first
---------------------------------------------------
0.12.98-dev found a row held open by a pointer to a row **that no longer existed**: the
eleven-pane row said the menu remap *"is open and questioned on its own row above"*, that row had
been archived, and the decision it carried had been made long before. **A pointer survives the
thing it points at.**

At the time this was deliberately NOT made a rule: two cases, and *"the row below"* has no
mechanical meaning. That judgement was wrong, and the measurement is what changed it. Counted
2026-10-05 across `docs/TODO.md`: **five** rows resolve an openness declaration positionally, and
**three of the five point at nothing at all** --

  * *"the individual routes listed below"*
  * *"optional provider adapters, on their own row below"* (no such row)
  * *"the optional provider interfaces, on their own row below"* (no such row)
  * *"containment, vehicles and the VGE hooks, each listed individually above"* (no such rows)
  * and in prose, *"Four genuine gaps remain, recorded below as new rows"* -- all four were
    built at 0.6.7-dev and archived, so the sentence advertises four open rows that do not exist.

What is checked, and why it cannot cry wolf
-------------------------------------------
Not every positional phrase. A section heading saying *"it binds every row below"* is describing
its own contents and is correct; `**SUPERSEDED, see below**` inside a historic block is a
narrative, not a blocker. Twelve lines in the queue carry a positional phrase and only five are
faults, so a blanket ban would be wrong about more than half of what it reported -- which is
exactly how a checker starts getting scrolled past.

The detectable property is narrower and is the one that matters: **a statement of what is still
open, resolved by position instead of by subject.** Those two things in one line, in that order,
is the construction that rots. The fix is always available and always an improvement: say what
the blocker *is*.

Quoted spans are stripped first, because a row that *quotes* a pointer in order to record that it
was removed must not fail on its own evidence -- the resolution of the eleven-pane row does
exactly that, and it was the first false positive this rule produced.

Exit status is the result. Run from the repository root.
"""
import io
import os
import re
import sys

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The open tiers only. `FINALIZED.md` is an archive: a closed row's pointer is part of the record
# of what was true, and rewriting history to satisfy a rule is worse than the rule not applying.
QUEUES = [os.path.join("docs", "TODO.md"), os.path.join("docs", "DECOMPOSED.md")]

ROW = re.compile(r"^\s*- \[[ ~T]\] ")

# `*"..."*` and plain `"..."`. A claim reads its own documentation; this one has to not.
QUOTED = re.compile(r"\*?\"[^\"]*\"\*?")

OPENNESS = re.compile(
    r"(\*\*Open:\*\*|\bstill open\b|\bis open\b|\bare open\b|\bstays open\b|\bstay open\b"
    r"|\bremains?\b|\bwhat is actually open\b|\bopen and\b)", re.I)

POSITIONAL = re.compile(
    r"((?:on|in|at) (?:its|their|the) own rows? (?:above|below)"
    r"|rows? (?:above|below)"
    r"|listed (?:individually )?(?:above|below)"
    r"|recorded (?:above|below)"
    r"|(?:section|item|items|bullet|entry|entries) (?:above|below)"
    r"|see (?:above|below))", re.I)

# How far after the openness word a pointer still reads as resolving it. One clause, measured
# against the five real faults: the longest of them puts 74 characters between the two.
WINDOW = 160


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def main():
    rows = 0
    lines_read = 0
    faults = []
    for relative in QUEUES:
        path = os.path.join(REPO, relative)
        if not os.path.isfile(path):
            say("FAILED: %s does not exist, so this rule guards nothing" % relative)
            return 1
        text = io.open(path, encoding="utf-8-sig").read()
        for number, raw in enumerate(text.split(NL), 1):
            lines_read += 1
            if ROW.match(raw):
                rows += 1
            clean = QUOTED.sub(" ", raw)
            for declaration in OPENNESS.finditer(clean):
                pointer = POSITIONAL.search(
                    clean, declaration.end(), declaration.end() + WINDOW)
                if pointer is None:
                    continue
                faults.append((relative, number, clean[declaration.start():pointer.end()]))
                break

    say("queue-pointers")
    say("  queue files    : %s" % ", ".join(q.replace(os.sep, "/") for q in QUEUES))
    say("  lines read     : %d" % lines_read)
    say("  open rows      : %d" % rows)
    say("")
    if rows == 0:
        say("FAIL: no open rows found in any queue tier at all. This rule only ever reports "
            "what it finds, so an empty scope would pass by construction -- which is a failure, "
            "not a clean run.")
        return 1
    if faults:
        say("FAIL: %d statement(s) of open work resolved by position instead of by subject"
            % len(faults))
        for relative, number, snippet in faults:
            say("  - %s:%d" % (relative, number))
            say("      %s" % " ".join(snippet.split())[:200])
        say("")
        say("      Name the blocker. A pointer survives the thing it points at: three of the "
            "five this rule was written against pointed at rows that had already been closed "
            "and archived, so each read as work somebody could go and pick up when there was "
            "nothing there. Saying what the blocker IS cannot go stale the same way.")
        return 1
    say("PASS: every statement of open work names its own blocker")
    return 0


if __name__ == "__main__":
    sys.exit(main())
