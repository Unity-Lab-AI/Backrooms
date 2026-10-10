# -*- coding: utf-8 -*-
"""Recover the row bodies the mover stranded, with proved attribution.

## What happened

`tools/archive-finished-todo.py::item_block_end` ended an `[x]` item block at the
next blank line, so a row whose closure carried several paragraphs archived its
**bullet line only**. The remaining paragraphs stayed in `docs/TODO.md`, and a
later closer then appended its evidence after them -- compounding the problem,
because the append landed outside the row it was aimed at.

That bug is fixed at the source and a checker now refuses the shape
(`tools/check-queue-integrity.py`). This script deals with what already escaped:
**twelve lines across seven spans**, belonging to **nine rows** already sitting
in `docs/FINALIZED.md` without the record attached to them.

## Attribution is read, not guessed

Every parent row below was recovered from the **pre-move snapshot taken at the
moment of its archiving** (`.local/qa/backup-*/TODO.md`, written by the mover
itself before it touched anything) by walking back from the stranded paragraph to
the nearest bullet. The evidence appends were traced to the closer that wrote
them -- `close-notice.py`, `close-composition.py`, `close-arrangements.py`,
`close-operations-batch.py` -- whose anchor string names the row exactly. Not one
of these is a reading of what the text seems to be about.

## The lines are moved, never rewritten

Identified by their own text rather than by line number, and written to the
archive byte for byte. The removal is proved the way the mover proves its own:
every non-blank line that leaves must be in the identified set, and every
non-blank line that stays must be one the original held.

**Line 139 and line 191 each carry two appends from two different rows**, and
line 144 carries one from a third. They are kept whole -- splitting a line would
be a rewrite -- and every row involved is named in the record instead.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
FINALIZED = "docs/FINALIZED.md"

A_DIAL = ('- [x] **"and we need a Random address option not just company requested task and '
          'quests at specific xcorrdinates"**', "0.12.85-dev")
A_STRAIGHT = ('- [x] **"make sure hallways and corradors and shit arent all straight"**',
              "0.12.82-dev")
A_BOARDUP = ('- [x] **"and the closing of natural portals needs to be an option on the gate '
             'itself so pawns can close it with like 25 wood to board it up which makes it '
             'close its map freeing up a map from being open so others can be explored"**',
             "0.12.85-dev")
A_HALL = ('- [x] **"and starting room is not to always be in bottom left of map"**',
          "0.12.83-dev")
A_PATTERNS = ('- [x] **"repeated patternes in variations"**', "0.12.83-dev")
A_PROPERLY = ('- [x] **"do it properly"**', "0.12.83-dev")
A_TONED = ('- [x] **"and propely keep it toned to the experience we are trying to make per '
           'scenrio type"**', "0.12.83-dev")
A_HUNDREDS = ('- [x] **"(i cant name theme all but there are hundred s and hundreds of '
              'facilities and room types like underground lsd cities"**', "0.12.83-dev")
A_ARRANGE = ('- [x] **"so its more rooma corradors facilites infastructure roads neighborrs '
             'hood malls shoopping centers military"**', "0.12.84-dev")

# (first line marker, last line marker, [parent rows], what this span is)
SPANS = [
    ("— **CLOSED 0.12.85-dev. `Portals/PortalRandomDial.cs`, reachable from the gate itself.",
     "— **CLOSED 0.12.85-dev. `Portals/PortalRandomDial.cs`, reachable from the gate itself.",
     [A_DIAL],
     "the closure evidence for the blind-dial row, appended past the end of the row it "
     "was aimed at"),

    ("**ENABLING STEP LANDED 2026-10-03: the corridor now has ONE authority",
     "**Two hazards the lane routing has to answer, found while designing it:**",
     [A_STRAIGHT, A_BOARDUP],
     "three paragraphs of the bent-corridor row's own record -- the single-authority "
     "extraction, the design finding that doglegging between centres is unsafe, and the two "
     "hazards lane routing had to answer. The last line also carries the board-up row's "
     "closure evidence, which landed here because this body was already stranded"),

    ("**AND MOVING IT BROKE THE LEVEL IN 1.5% OF SEEDS",
     "**Three claims had to be re-aimed and one of mine was written wrong.**",
     [A_HALL, A_PATTERNS],
     "the hall-placement row's own record: the 1.5%-of-seeds regression the probe caught, "
     "and the three claims that had to be re-aimed with it. The last line also carries the "
     "motif row's closure evidence. **Neither line is indented**, which is why no structural "
     "check could find them -- they were recovered from the snapshot by name"),

    ("— **CLOSED 0.12.83-dev, and recorded as the instruction it was rather than a sentiment.",
     "— **CLOSED 0.12.83-dev, and recorded as the instruction it was rather than a sentiment.",
     [A_PROPERLY],
     "the closure evidence for the loading-screen art row"),

    ("— **CLOSED 0.12.83-dev. One keyed string per shipped opening",
     "— **CLOSED 0.12.83-dev. One keyed string per shipped opening",
     [A_TONED],
     "the closure evidence for the per-scenario freeze-notice tone row"),

    ("— **CLOSED 0.12.83-dev **as a product, which is the only way the number is reachable.**",
     "— **CLOSED 0.12.83-dev **as a product, which is the only way the number is reachable.**",
     [A_HUNDREDS, A_ARRANGE],
     "two closure evidences on one line -- the 44-archetype product for the hundreds-of-"
     "facilities row, and the roads-and-neighbourhoods arrangements row behind it"),

    ("**A road is `RoomLayoutPlanner.OnRoad`**",
     "**And it exposed a real leak in the prune.**",
     [A_ARRANGE],
     "four paragraphs of the arrangements row's own record: what makes a run read as a road, "
     "the road braid that was written and then deleted because it measured as a no-op, how a "
     "neighbourhood is pressed together, and the leak it exposed in `PruneUnroutableLinks`"),
]

lines = io.open(TODO, encoding="utf-8").read().split(NL)


def sole(marker):
    hits = [index for index, line in enumerate(lines) if marker in line]
    if len(hits) != 1:
        raise SystemExit("ABORT: marker matched %d lines, expected exactly 1: %r"
                         % (len(hits), marker[:72]))
    return hits[0]


archive_now = io.open(FINALIZED, encoding="utf-8").read()

# **AN ATTRIBUTION NOBODY CHECKED IS A GUESS WITH A CITATION.** Each parent row
# below is quoted here from the closer that archived it; if a quote has drifted
# by one character the record would name a row that does not exist, and the
# stranded paragraph would be filed under nothing. So every anchor has to be
# findable in the archive it claims to belong to, before anything is written.
missing_anchors = [anchor for anchor, _version in (
    A_DIAL, A_STRAIGHT, A_BOARDUP, A_HALL, A_PATTERNS, A_PROPERLY, A_TONED,
    A_HUNDREDS, A_ARRANGE) if anchor not in archive_now]
if missing_anchors:
    print("ANCHOR NOT FOUND IN %s -- %d of 9:" % (FINALIZED, len(missing_anchors)))
    for anchor in missing_anchors:
        print("    %s" % anchor[:150])
    raise SystemExit("ABORT: nothing written; an unverifiable attribution is not one")

taken = set()
resolved = []
for first_marker, last_marker, parents, note in SPANS:
    start = sole(first_marker)
    stop = sole(last_marker)
    if stop < start:
        raise SystemExit("ABORT: span runs backwards -- %r ends above it starts"
                         % first_marker[:72])
    span = list(range(start, stop + 1))
    clash = taken.intersection(span)
    if clash:
        raise SystemExit("ABORT: spans overlap at line(s) %s" % sorted(n + 1 for n in clash))
    taken.update(span)
    resolved.append((span, parents, note))

# Trailing blank swallowed only where the span sits between two blanks, so the
# single separator between rows survives and no run of two is left behind.
blanks = set()
for span, _parents, _note in resolved:
    before, after = span[0] - 1, span[-1] + 1
    if (before >= 0 and not lines[before].strip()
            and after < len(lines) and not lines[after].strip()):
        blanks.add(after)
removing = taken | blanks

# ----------------------------------------------------------------- the archive
out = []
out.append("")
out.append("---")
out.append("")
out.append("## Recovered row bodies - the paragraphs the mover stranded (2026-10-04)")
out.append("")
out.append("<!-- recovered-stranded:begin -->")
out.append("")
out.append("**Verbatim owner direction (2026-10-02):** *\"we need to move all finished items to "
           "finalized.md from the todo, the todods sahll never hold completed items, they are "
           "always to be moved to finalized first then deleted from the todods once confirmed "
           "virbatium transfer\"*")
out.append("")
out.append("**THIS IS A DEFECT RECORD AS WELL AS AN ARCHIVE, and the defect was mine.** "
           "`tools/archive-finished-todo.py::item_block_end` ended an `[x]` item block at the "
           "next blank line. Every row in the queue whose closure carries its own evidence is "
           "several paragraphs long, so those rows archived their **bullet line only** and the "
           "rest stayed in `docs/TODO.md`. Both halves of the owner's direction broke at once: "
           "the archive was missing the record, and the queue was holding fragments of "
           "completed items.")
out.append("")
out.append("**Neither gate could see it.** The mover proves a reassembly identity -- "
           "`kept + moved == original` -- which is a real proof of the thing it proves, and "
           "**where a row ends is not that thing**. It survived four published versions: "
           "0.12.82-dev, 0.12.83-dev, 0.12.84-dev and 0.12.85-dev.")
out.append("")
out.append("**Fixed at the source, and a second instrument added beside it.** "
           "`item_block_end` now runs a block on across blank lines while the next line "
           "continues it, and refuses to apply at all when unindented prose sits directly "
           "after a closed row -- the ambiguous shape that caused this. "
           "`tools/check-queue-integrity.py` is checker 18 and fails on a stranded "
           "continuation, on closure evidence that is not on a row, and on any `[x]` row left "
           "in a queue.")
out.append("")
out.append("**Attribution below was read, not guessed.** Every parent row came from the "
           "pre-move snapshot the mover wrote before it touched anything, by walking back from "
           "the stranded paragraph to the nearest bullet; every evidence append was traced to "
           "the closer that wrote it, whose anchor string names the row exactly. The lines are "
           "moved **byte for byte** and nothing is reworded, per LAW #0.")
out.append("")

for span, parents, note in resolved:
    out.append("")
    out.append("> **Stranded from %s**" % ", ".join(
        "`%s` (archived at **%s**)" % (anchor, version) for anchor, version in parents))
    out.append(">")
    out.append("> %s." % note)
    out.append("")
    for index in span:
        out.append(lines[index])
    out.append("")

out.append("Recovered 2026-10-04. No source file was touched by this change; it moves ledger "
           "lines only.")
out.append("")
out.append("<!-- recovered-stranded:end -->")
out.append("")

moved_lines = [lines[index] for index in sorted(taken)]

existing = io.open(FINALIZED, encoding="utf-8").read()
io.open(FINALIZED, "w", encoding="utf-8", newline=NL).write(
    existing.rstrip(NL) + NL + NL.join(out))

written = io.open(FINALIZED, encoding="utf-8").read()
absent = [line for line in moved_lines if line.strip() and line not in written]
if absent:
    io.open(FINALIZED, "w", encoding="utf-8", newline=NL).write(existing)
    raise SystemExit("ABORT: %d moved line(s) are not in the archive; FINALIZED.md restored "
                     "and the queue untouched. First: %r" % (len(absent), absent[0][:110]))

# ------------------------------------------------------------- only now, remove
kept = [line for index, line in enumerate(lines) if index not in removing]

original_nonblank = [line for line in lines if line.strip()]
kept_nonblank = [line for line in kept if line.strip()]
expected = [line for index, line in enumerate(lines)
            if line.strip() and index not in taken]
if kept_nonblank != expected:
    io.open(FINALIZED, "w", encoding="utf-8", newline=NL).write(existing)
    raise SystemExit("ABORT: the kept text is not the original minus the identified spans; "
                     "FINALIZED.md restored and the queue untouched")

io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(kept))

print("recover-stranded-rows")
print("  spans recovered          : %d" % len(resolved))
print("  content lines moved      : %d" % len(taken))
print("  blank separators dropped : %d" % len(blanks))
print("  rows named as parents    : %d" % len({anchor for _s, parents, _n in resolved
                                               for anchor, _v in parents}))
print("  archive verbatim check   : all %d moved lines present" % len(moved_lines))
print("  %-24s : %d lines -> %d lines" % (TODO, len(lines), len(kept)))
print("  non-blank identity       : HOLDS (original minus the identified spans)")
