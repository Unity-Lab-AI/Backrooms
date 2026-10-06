# -*- coding: utf-8 -*-
"""Checker 18 -- a queue holds whole open rows and nothing else.

## Why this exists, and what it caught on the day it was written

`tools/archive-finished-todo.py` ended an `[x]` item block at the next blank
line. Every row in this queue whose closure carries its own evidence is several
paragraphs long, so those rows archived their **bullet line only** and left the
rest behind. Measured 2026-10-04: **eleven stranded lines** across four published
versions -- 0.12.82-dev, 0.12.83-dev, 0.12.84-dev and 0.12.85-dev.

Both halves of `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE` were broken at
once, and neither existing gate could see it:

  * `docs/FINALIZED.md` was **missing** the paragraphs. The archive held the row
    without the record attached to it.
  * `docs/TODO.md` was **holding fragments of completed items**, against the
    owner's direction, 2026-10-02, verbatim: *"we need to move all finished items
    to finalized.md from the todo, the todods sahll never hold completed items,
    they are always to be moved to finalized first then deleted from the todods
    once confirmed virbatium transfer"*.

The mover's own proof is a reassembly identity -- `kept + moved == original`. It
is a real proof of the thing it proves, and **where a row ends is not that
thing**, which is how this survived eight batches of a gate working exactly as
written. So the proof is not strengthened here; a second, differently-shaped
instrument is added beside it, which is this repository's standing answer to a
gate that cannot see its own blind spot.

## The three rules

  1. **No stranded continuation.** An indented paragraph whose owning bullet is
     gone. This is the residue the defect leaves, and it is detectable from the
     queue alone with no reference to the archive.
  2. **No closure evidence off a row.** A line carrying `**CLOSED <version>` or
     `**PARTLY CLOSED` that is not itself a row. Only a closer ever writes that
     text and it is always appended to a row, so finding one loose means a
     closer's append landed outside the row it was aimed at -- which is the other
     half of what happened here.
  3. **No `[x]` row.** The LAW: a queue tier carries `[ ]`, `[~]` and `[T]` only,
     `[x]` is transient, and archiving happens in the same batch that closes the
     row. A queue still holding `[x]` at check time means the batch stopped
     halfway.
  4. **No unstatused work in a pending section.** A subsection inside a pending
     region with no row under it at all.

## What rule 4 caught, 2026-10-06, and why the first three could not

The first three rules are all **about rows**, and that is the blind spot they
share. Rule 1 needs an indented continuation, rule 2 needs a closer's signature,
rule 3 needs an `[x]`. A subsection carrying owner direction and **no status
marker of any kind** trips none of them.

Two such sections sat under `## Pending` in `docs/TODO.md` holding five verbatim
owner directions, and **two of the five had never reached `docs/FINALIZED.md`**.
Every counter in the project read the queue as `0 open / 0 partial` and the
handoff published that number, because a row with no marker is invisible to a
count of markers -- it is not absent from the queue, it is unmeasured by it.

This is the repository's own most repeated finding turned on its own ledger: **a
rule satisfied by its subject not being there is not a rule.** So the rule is
scoped to a pending region rather than to every heading, because `ROADMAP.md`'s
`### Risk assessment` and `DECOMPOSED.md`'s `## Decomposition rules` are prose by
design and a checker that cried wolf on them would be switched off.

Run by **exit status**, like every other instrument here. Never by reading the
output.
"""
import io
import os
import re
import sys

# The console here is cp1252 and every line this reports comes out of a document
# written with em dashes. A codec error in the reporting path is a total failure
# of a checker, and the first draft of the orphan finder died of exactly that.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Every tier that holds rows. `docs/NOW.md` is not one -- it is the handoff and
# holds no status markers by owner direction.
QUEUES = ["docs/TODO.md", "docs/DECOMPOSED.md", "docs/ROADMAP.md", "docs/TEST.md"]

# **`docs/TEST.md` WAS NOT IN THIS LIST UNTIL 2026-10-06, AND IT IS THE TIER ABOUT TO BE WORKED.**
# It was created on 2026-10-06 and the list was never extended, so the fourth tier -- 54 rows, the
# only ones a build cannot close -- was the one queue with **no integrity guard at all**. None of
# the four rules could fire on it: a passed row left as `[x]` would have sat there indefinitely,
# and a section holding owner direction with no row would have been invisible to every count,
# which is precisely the defect this file's rule 4 was written for after it happened to `TODO.md`.
#
# The owner's question was *"are you ready to start mass chacking off (T) test items as we do
# them?"* -- and the honest answer required this first, because mass-closing rows into an unguarded
# queue is how the stranded-fragment defect of 2026-10-04 happened in the first place.

BULLET = re.compile(r"^(\s*)(?:- |#### )\[( |x|~|T)\]")
HEADING = re.compile(r"^\s*#{1,6} ")
RULE_ONLY = re.compile(r"^---\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
FENCE = re.compile(r"^\s*```")
INDENTED = re.compile(r"^  +\S")

# A closer's signature. The leading `\s*` matters: the stranded lines all began
# with the single space that sat in front of the em dash in the concatenation,
# so anchoring hard at `^` would have missed every one of them.
EVIDENCE = re.compile(r"\*\*(?:PARTLY )?CLOSED \d+\.\d+")

# Where live work is listed. A region opens at one of these and closes at the next
# `##` heading, which is how TOMBSTONES ends it.
PENDING_REGION = re.compile(r"^##\s+(?:Pending|In progress)\s*$", re.I)
TOP_HEADING = re.compile(r"^##\s+\S")
SUB_HEADING = re.compile(r"^(#{3,6})\s+(\S.*)$")


def say(line=""):
    """Print a line that may hold characters the console cannot encode.

    **AN INSTRUMENT THAT CRASHES WHILE REPORTING CANNOT REPORT.** These tools print section titles
    and row text straight out of the queue, so they can be handed any character the document holds.
    One heading carrying an interdiction sign killed `archive-finished-todo` at `print`, after the
    reassembly identity had already held -- leaving a half-written report and no statement of whether
    the move had happened.

    Replaced rather than dropped, so the reader still sees where the character was. Same answer
    `check-doc-conformance.say` already carries, for the same reason.
    """
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def owner_of(lines, index):
    """The bullet that owns `index`, or None when the line is stranded.

    Walks back past blank lines and other indented continuations. Reaching a
    heading, a rule, a table or an unindented paragraph first means nothing owns
    this line.
    """
    walk = index - 1
    while walk >= 0:
        line = lines[walk]
        if not line.strip():
            walk -= 1
            continue
        if BULLET.match(line):
            return walk
        if INDENTED.match(line):
            walk -= 1
            continue
        return None
    return None


def unstatused_sections(lines):
    """Subsections inside a pending region that hold no row at all.

    The section heading is reported rather than its prose, because the heading is what a reader
    scans and what an archiver has to aim at. A region with no subsections -- a genuinely empty
    `## Pending` followed straight by `## TOMBSTONES` -- reports nothing, which is the whole point
    of the distinction: **empty and saying so is correct; occupied and unmeasured is not.**
    """
    found = []
    in_region = False
    fenced = False
    open_section = None
    for index, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        sub = SUB_HEADING.match(line)
        if PENDING_REGION.match(line):
            if open_section is not None:
                found.append(open_section)
            in_region, open_section = True, None
            continue
        if TOP_HEADING.match(line):
            if open_section is not None:
                found.append(open_section)
            in_region, open_section = False, None
            continue
        if not in_region:
            continue
        if sub:
            if open_section is not None:
                found.append(open_section)
            open_section = (index + 1, sub.group(2).strip()[:88])
            continue
        if open_section is not None and BULLET.match(line):
            open_section = None
    if open_section is not None:
        found.append(open_section)
    return found


def inspect(path):
    lines = io.open(os.path.join(REPO, path), encoding="utf-8").read().split("\n")
    stranded = []
    loose_evidence = []
    closed_rows = []
    unstatused = unstatused_sections(lines)
    fenced = False
    for index, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or not line.strip():
            continue
        found = BULLET.match(line)
        if found:
            if found.group(2) == "x":
                closed_rows.append((index + 1, line.strip()[:88]))
            continue
        if HEADING.match(line) or RULE_ONLY.match(line) or TABLE_ROW.match(line):
            continue
        if EVIDENCE.search(line):
            loose_evidence.append((index + 1, line.strip()[:88]))
            continue
        if INDENTED.match(line) and owner_of(lines, index) is None:
            stranded.append((index + 1, line.strip()[:88]))
    return len(lines), stranded, loose_evidence, closed_rows, unstatused


def report(label, rows, remedy):
    say("    %-34s : %d" % (label, len(rows)))
    for number, text in rows:
        say("        line %-5d %s" % (number, text))
    if rows:
        say("        -> %s" % remedy)
    return len(rows)


def main():
    say("check-queue-integrity")
    failures = 0
    for path in QUEUES:
        if not os.path.exists(os.path.join(REPO, path)):
            say("  %s : ABSENT" % path)
            failures += 1
            continue
        total, stranded, loose_evidence, closed_rows, unstatused = inspect(path)
        say("  %s (%d lines)" % (path, total))
        failures += report(
            "stranded continuation lines", stranded,
            "the owning row was archived without its body; recover the lines into "
            "docs/FINALIZED.md and delete them here")
        failures += report(
            "closure evidence off a row", loose_evidence,
            "a closer appended outside the row it aimed at; put the evidence on the "
            "row line itself")
        failures += report(
            "[x] rows still in the queue", closed_rows,
            "run tools/archive-finished-todo.py --apply, then tools/verify-archive-move.py")
        failures += report(
            "pending sections with no row", unstatused,
            "this section holds work no status marker governs, so every count of the queue "
            "reads past it; give each item a [ ]/[~]/[T] row, or archive the section to "
            "docs/FINALIZED.md verbatim and delete it here")

    say()
    if failures:
        say("  FAILED : %d integrity problem(s)" % failures)
        return 1
    say("  PASS   : every queue holds whole open rows and nothing else")
    return 0


if __name__ == "__main__":
    sys.exit(main())
