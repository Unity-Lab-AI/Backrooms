# -*- coding: utf-8 -*-
"""Find the residue archived rows left behind in a queue file.

## The defect, measured rather than supposed

`tools/archive-finished-todo.py::item_block_end` ends an `[x]` item block at the
next BOUNDARY, and BOUNDARY includes **a blank line**. A row whose body is
several paragraphs -- the normal shape in this queue, where a closure carries its
own evidence -- therefore moves its **bullet line only**. Every indented
continuation paragraph stays in the queue.

Two consequences, both invisible to the verbatim gate:

  1. `docs/FINALIZED.md` is **missing** those paragraphs. The archive holds the
     row and not the record attached to it.
  2. `docs/TODO.md` holds fragments of completed items, against the owner's own
     direction: *"the todods sahll never hold completed items"*.

The reassembly identity in the mover proves `kept + moved == original`. It says
nothing about **where the row ended**, which is why eight batches of this got
through a gate that was working exactly as written.

## What counts as an orphan here

An indented (2+ space) non-blank line whose owning bullet is gone. Scanning back
past blank lines must reach a bullet; if it reaches a heading, a rule, a table
row or an unindented paragraph first, nothing owns this line.

Unindented prose is NOT flagged -- section-level context legitimately sits
between rows. The one exception is a line carrying appended closure evidence
(`-- **CLOSED` / `-- **PARTLY CLOSED`), which only a closer ever writes and which
therefore belongs to a row by construction.

**A FENCED BLOCK IS NOT AN INDENT, and the first run of this reported five.**
`docs/TODO.md` quotes real source in ```csharp fences, and C# is indented, so
every brace line inside one looked like a stranded continuation. Fence state is
tracked rather than the lines being pattern-excused, because `return;` is a
perfectly ordinary thing for a stranded paragraph to begin with.
"""
import io
import re
import sys

# The console here is cp1252 and this file reports em dashes and arrows straight
# out of the queue. Printing is the whole output of this tool, so a codec error
# is a total failure, and it reported one on its first run against DECOMPOSED.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUEUE = sys.argv[1] if len(sys.argv) > 1 else "docs/TODO.md"

BULLET = re.compile(r"^(\s*)(?:- |#### )\[( |x|~|T)\]")
HEADING = re.compile(r"^\s*#{1,6} ")
RULE = re.compile(r"^---\s*$")
TABLE = re.compile(r"^\s*\|")
INDENTED = re.compile(r"^  +\S")
# The closer's own signature. `(\s*)` rather than `^` because the stranded line
# begins with the single space the concatenation left in front of the em dash.
EVIDENCE_LEAD = re.compile(r"^\s*(?:—|--) \*\*(?:PARTLY )?CLOSED")

lines = io.open(QUEUE, encoding="utf-8").read().split("\n")


def owner_of(index):
    """The bullet that owns `index`, or None if the line is stranded."""
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


FENCE = re.compile(r"^\s*```")

orphans = []
fenced = False
for index, line in enumerate(lines):
    if FENCE.match(line):
        fenced = not fenced
        continue
    if fenced:
        continue
    if not line.strip():
        continue
    if BULLET.match(line) or HEADING.match(line) or RULE.match(line) or TABLE.match(line):
        continue
    stranded = INDENTED.match(line) and owner_of(index) is None
    evidence = EVIDENCE_LEAD.match(line)
    if stranded or evidence:
        orphans.append((index + 1, "stranded-body" if stranded else "stranded-evidence", line))

print("find-orphaned-row-bodies  %s" % QUEUE)
print("  lines                    : %d" % len(lines))
print("  orphan lines             : %d" % len(orphans))
for number, kind, line in orphans:
    print("      %-5d %-18s %s" % (number, kind, line.strip()[:86]))

sys.exit(1 if orphans else 0)
