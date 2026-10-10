"""Archive the dated-checkpoint sections of docs/TODO.md and carry their open rows forward.

Owner direction, 2026-10-02, verbatim:
  "we need to move all finished items to finalized.md from the todo, the todods
   sahll never hold completed items, they are always to be moved to finalized
   first then deleted from the todods once confirmed virbatium transfer"

and, on being shown the queue still at ~96 KB:
  "BEcause the todos are still like 100kb and i know that not all unfinished work
   and only unfinished work like it shall be"

THE PROBLEM THIS SOLVES
-----------------------
Nine `##` sections in the queue are titled as dated checkpoint records -- a launch
finding, a coordinate-rebuild stage, a doc sweep. They are **21 KB, 12 KB of it
finished-session prose**: what was measured, what was diagnosed, what shipped,
with plant counts and record links. The row-level mover could not take them,
because each still holds a few open rows and a section with an open row in it is
not a closed record.

But the section IS a record. "Fifth launch findings - 2026-09-30" is a thing that
happened, not a thing to do. So:

  * the whole section goes to the archive, verbatim, record intact;
  * its open rows are carried forward into the queue under one heading, each
    tagged with the checkpoint it came out of, so nothing open is lost.

An open row therefore appears twice: in the archive as part of the historical
record, and in the queue as work. That is deliberate -- splitting the prose from
the rows would leave a record that no longer says what it found.

CONTINUATION LINES
------------------
Rows in these sections carry indented bodies: tables, multi-paragraph analyses.
A row's block runs to the next row at the same-or-shallower indent, the next
heading, or a rule -- NOT to the next blank line, which is the rule the row-level
mover uses and which would cut these rows in half.
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINALIZED = os.path.join(REPO, "docs", "FINALIZED.md")

H2 = re.compile(r"^## (.*)$")
ROW = re.compile(r"^(\s*)- \[( |x|~|T)\]")
DATED = re.compile(r"\d\.\d+\.\d+-dev|launch findings|Releasing a place|doc sweep")
INSERT_AFTER = "## Pending"

BEGIN = "<!-- archived-queue:begin -->"
END = "<!-- archived-queue:end -->"


def read_lines(path):
    return io.open(path, encoding="utf-8").read().split("\n")


def row_block_end(lines, start, limit):
    """End of the row beginning at `start`, including its indented body."""
    indent = len(ROW.match(lines[start]).group(1))
    index = start + 1
    while index < limit:
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("#") or line.strip() == "---":
            break
        found = ROW.match(line)
        if found and len(found.group(1)) <= indent:
            break
        if len(line) - len(line.lstrip()) <= indent and not found:
            break
        index += 1
    while index - 1 > start and not lines[index - 1].strip():
        index -= 1
    return index


def main():
    apply_it = "--apply" in sys.argv
    lines = read_lines(TODO)

    bounds = [(H2.match(line).group(1), index)
              for index, line in enumerate(lines) if H2.match(line)]

    targets = []
    for position, (title, start) in enumerate(bounds):
        end = bounds[position + 1][1] if position + 1 < len(bounds) else len(lines)
        if DATED.search(title):
            targets.append((title.strip(), start, end))

    if not targets:
        print("no dated checkpoint sections found; nothing to do")
        return 0

    # Open rows, in file order, grouped by source section.
    carried = []
    for title, start, end in targets:
        index = start
        rows = []
        while index < end:
            found = ROW.match(lines[index])
            if found and found.group(2) in (" ", "~"):
                stop = row_block_end(lines, index, end)
                rows.append(lines[index:stop])
                index = stop
                continue
            index += 1
        carried.append((title, rows))

    # Deduplicate rows that repeat verbatim across checkpoints. Reported, never
    # silently dropped: the same open item written three times is one item.
    seen = {}
    duplicates = []
    for title, rows in carried:
        for block in rows:
            key = "\n".join(block).strip()
            if key in seen:
                duplicates.append((title, seen[key], block[0][:80]))
            else:
                seen[key] = title

    moved_spans = [(start, end) for _title, start, end in targets]
    moved_bytes = sum(sum(len(line) + 1 for line in lines[start:end])
                      for start, end in moved_spans)
    carried_bytes = sum(sum(len(line) + 1 for line in block)
                        for _title, rows in carried for block in rows)

    print("lift-checkpoint-sections")
    print("  dated checkpoint sections : %d" % len(targets))
    for title, start, end in targets:
        size = sum(len(line) + 1 for line in lines[start:end])
        rows = len([1 for t, r in carried if t == title for _ in r])
        print("      %5d-%-5d %6d B  %2d open rows  %s" % (start + 1, end, size, rows, title[:54]))
    print()
    print("  bytes archived            : %.1f KB" % (moved_bytes / 1024.0))
    print("  bytes carried forward     : %.1f KB" % (carried_bytes / 1024.0))
    print("  net reduction             : %.1f KB" % ((moved_bytes - carried_bytes) / 1024.0))
    print()
    print("  open rows carried         : %d" % sum(len(r) for _t, r in carried))
    print("  verbatim duplicates       : %d" % len(duplicates))
    for title, first, head in duplicates:
        print("      %s" % head)
        print("        repeats one already carried from %r" % first[:50])

    if not apply_it:
        print()
        print("  PLAN ONLY. Nothing written. Re-run with --apply.")
        return 0

    # ---- build the carried-forward block -------------------------------------
    block = []
    block.append("")
    block.append("### Open rows carried out of the play-testing checkpoints (2026-09-30 to 2026-10-01)")
    block.append("")
    block.append("**Lifted here 2026-10-02 by owner direction:** *\"we need to move all finished items "
                 "to finalized.md from the todo, the todods sahll never hold completed items, they are "
                 "always to be moved to finalized first then deleted from the todods once confirmed "
                 "virbatium transfer\"* and, on being shown the queue still at ~96 KB, *\"BEcause the "
                 "todos are still like 100kb and i know that not all unfinished work and only "
                 "unfinished work like it shall be\"*.")
    block.append("")
    block.append("Nine `##` sections titled as dated checkpoint records held **%.1f KB** between them, "
                 "most of it the finished write-up of a launch or a rebuild stage, with these open rows "
                 "buried inside. **A section called \"Fifth launch findings - 2026-09-30\" is a thing "
                 "that happened, not a thing to do.** Each section is archived whole in "
                 "`FINALIZED.md`, record intact; every open row it held is below, verbatim, tagged with "
                 "the checkpoint it came out of." % (moved_bytes / 1024.0))
    block.append("")
    if duplicates:
        block.append("**%d row(s) repeated verbatim across checkpoints and are carried once.** The same "
                     "open item written three times is one open item; the repeats are named in the "
                     "archive rather than dropped silently." % len(duplicates))
        block.append("")

    emitted = set()
    for title, rows in carried:
        kept = []
        for row in rows:
            key = "\n".join(row).strip()
            if key in emitted:
                continue
            emitted.add(key)
            kept.append(row)
        if not kept:
            continue
        block.append("**From `## %s`:**" % title)
        block.append("")
        for row in kept:
            block.extend(row)
            block.append("")

    # ---- archive text --------------------------------------------------------
    archive = []
    archive.append("")
    archive.append("---")
    archive.append("")
    archive.append("## Archived from the queue - the dated checkpoint sections (2026-10-02)")
    archive.append("")
    archive.append(BEGIN)
    archive.append("")
    archive.append("**Verbatim owner direction (2026-10-02):** *\"we need to move all finished items to "
                   "finalized.md from the todo, the todods sahll never hold completed items, they are "
                   "always to be moved to finalized first then deleted from the todods once confirmed "
                   "virbatium transfer\"*")
    archive.append("")
    archive.append("**And, on being shown the queue still at ~96 KB after the row-level pass:** *\"BEcause "
                   "the todos are still like 100kb and i know that not all unfinished work and only "
                   "unfinished work like it shall be\"* / *\"what the fuck are you doing this is a simple "
                   "move completed item to another folder\"*")
    archive.append("")
    archive.append("The owner was right and the row-level pass had missed this. **Nine `##` sections of "
                   "`docs/TODO.md` were titled as dated checkpoint records** - a launch finding, a "
                   "coordinate-rebuild stage, a doc sweep - holding **%.1f KB**, most of it the finished "
                   "write-up of what was measured, diagnosed and shipped. The row-level mover could not "
                   "take them because each still held a few open rows, and a section with an open row in "
                   "it is not a closed record. **But the section is a record.** Each is below, whole and "
                   "unaltered; the **%d open rows** they held were carried forward into `TODO.md` under "
                   "*Open rows carried out of the play-testing checkpoints*, verbatim and tagged with "
                   "their source, so nothing open was lost. An open row therefore appears in both files "
                   "on purpose: splitting the prose from the rows would leave a record that no longer "
                   "says what it found."
                   % (moved_bytes / 1024.0, sum(len(r) for _t, r in carried)))
    archive.append("")
    if duplicates:
        archive.append("**%d open row(s) repeated verbatim across checkpoints.** Carried once into the "
                       "queue, named here so the consolidation is on the record rather than silent:"
                       % len(duplicates))
        archive.append("")
        for title, first, head in duplicates:
            archive.append("- In `## %s`, repeating a row already carried from `## %s`: %s"
                           % (title, first, head))
        archive.append("")

    for title, start, end in targets:
        archive.append("> moved from `## %s` in `docs/TODO.md`" % title)
        archive.append("")
        archive.extend(lines[start:end])
        archive.append("")

    archive.append(END)
    archive.append("")

    # ---- write the archive FIRST, then confirm, then touch the queue ---------
    existing = io.open(FINALIZED, encoding="utf-8").read()
    io.open(FINALIZED, "w", encoding="utf-8", newline="").write(
        existing.rstrip("\n") + "\n" + "\n".join(archive)
    )
    written = io.open(FINALIZED, encoding="utf-8").read()
    moved_lines = [line for start, end in moved_spans for line in lines[start:end]]
    missing = [line for line in moved_lines if line.strip() and line not in written]
    if missing:
        io.open(FINALIZED, "w", encoding="utf-8", newline="").write(existing)
        raise SystemExit("ABORT: %d archived lines not present; FINALIZED.md restored, "
                         "queue untouched. First: %r" % (len(missing), missing[0][:110]))

    # ---- rewrite the queue ---------------------------------------------------
    drop = set()
    for start, end in moved_spans:
        drop.update(range(start, end))
    kept = [line for index, line in enumerate(lines) if index not in drop]

    at = kept.index(INSERT_AFTER)
    kept = kept[:at + 1] + block + kept[at + 1:]

    io.open(TODO, "w", encoding="utf-8", newline="").write("\n".join(kept))

    print()
    print("  docs/FINALIZED.md         : archive appended, %d lines" % len(archive))
    print("  verbatim confirmation     : all %d archived lines present" % len(moved_lines))
    print("  docs/TODO.md              : rewritten, %d lines, %.1f KB"
          % (len(kept), sum(len(line) + 1 for line in kept) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
