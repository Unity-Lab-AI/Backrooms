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
QUEUES = ["docs/TODO.md", "docs/DECOMPOSED.md", "docs/ROADMAP.md"]

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


def inspect(path):
    lines = io.open(os.path.join(REPO, path), encoding="utf-8").read().split("\n")
    stranded = []
    loose_evidence = []
    closed_rows = []
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
    return len(lines), stranded, loose_evidence, closed_rows


def report(label, rows, remedy):
    print("    %-34s : %d" % (label, len(rows)))
    for number, text in rows:
        print("        line %-5d %s" % (number, text))
    if rows:
        print("        -> %s" % remedy)
    return len(rows)


def main():
    print("check-queue-integrity")
    failures = 0
    for path in QUEUES:
        if not os.path.exists(os.path.join(REPO, path)):
            print("  %s : ABSENT" % path)
            failures += 1
            continue
        total, stranded, loose_evidence, closed_rows = inspect(path)
        print("  %s (%d lines)" % (path, total))
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

    print()
    if failures:
        print("  FAILED : %d integrity problem(s)" % failures)
        return 1
    print("  PASS   : every queue holds whole open rows and nothing else")
    return 0


if __name__ == "__main__":
    sys.exit(main())
