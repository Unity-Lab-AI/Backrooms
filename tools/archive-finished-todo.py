"""Move every finished item out of docs/TODO.md into docs/FINALIZED.md, verbatim.

Owner direction, 2026-10-02, verbatim:
  "we need to move all finished items to finalized.md from the todo, the todods
   sahll never hold completed items, they are always to be moved to finalized
   first then deleted from the todods once confirmed virbatium transfer"

The order in that direction is binding and is the `§FINALIZED BEFORE DELETE` LAW:
write the archive first, confirm the transfer is verbatim, only then delete from
the queue.

HOW THE TRANSFER IS PROVED VERBATIM
-----------------------------------
This script never rewrites a line. It labels every line index of the original
file either KEEP or MOVE, and the archive is built from the MOVE lines in their
original order. So "verbatim" is not a reading of the output, it is an identity:

    reassemble(KEEP lines + MOVE lines, by original index) == original bytes

That assertion runs before anything is written, and a mismatch aborts.

WHAT MOVES
----------
Three granularities, coarsest first, because a closed record should move whole
rather than be shredded into bullets:

  1. A whole `##` section when it carries at least one [x] and no [ ], [~] or
     [T] -- a closed session record end to end, prose included, because the
     prose IS the record of the completed work.
  2. Inside any other section, a whole DIRECTION GROUP when every row in it is
     [x]. A group runs from a `### ` heading or a `**Verbatim ...` line to the
     next one, which is this file's own convention: the owner's words, then the
     rows that answer them. Moving the group keeps the direction attached to its
     own closure instead of stranding the quote over an empty space.
  3. Otherwise, each [x] item block on its own: the bullet line plus its wrapped
     continuation lines, at any indent.

Then a final sweep moves any `### ` heading whose entire body has already gone,
so no empty heading is left behind.

WHAT NEVER MOVES
----------------
  * [ ] pending and [~] in-progress rows.
  * [T] rows. A [T] row belongs to the post-completion test phase, cannot be
    closed without the game running, and is not finished work.
  * A section titled DONE whose rows are still [ ]. The title is not the marker.
    Those are reported instead, because promoting a row the owner never ticked
    would be inventing a closure.
  * The structural headings the queue needs to stay readable.
"""

import datetime
import io
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# `tools/`, one level down, matching every other tracked checker here. **This
# moved from `.local/qa/` on 2026-10-03** by owner direction, because
# `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE` names this script as the proof
# of verbatim transfer and `.local/qa/*` is gitignored -- so the LAW's instrument
# existed on one machine, drifted silently, and could not reach anybody else. The
# depth changed with the move and `REPO` had to change with it: a stale
# `join(HERE, "..", "..")` here would resolve to the parent of the repository and
# quietly read somebody else's files.
REPO = os.path.dirname(HERE)
TODO = os.path.join(REPO, "docs", "TODO.md")
FINALIZED = os.path.join(REPO, "docs", "FINALIZED.md")

# Snapshots stay machine-local and gitignored. They are a per-run safety artefact,
# not a deliverable, and tracking them would put a copy of the whole ledger in the
# repository on every archive run.
BACKUPS = os.path.join(REPO, ".local", "qa")

# The name of the file recording which queue a backup folder was taken from, so
# `verify-archive-move.py` can check a `--queue docs/DECOMPOSED.md` move without
# assuming every move was a TODO move.
QUEUE_STAMP = "queue-name.txt"

# `docs/DECOMPOSED.md` writes its decomposed units as `#### [x] <title>` headings
# rather than list rows, so a status marker is either shape.
MARKER = re.compile(r"^(\s*)(?:- |#### )\[( |x|~|T)\]")
H2 = re.compile(r"^## (.*)$")
H3 = re.compile(r"^### (.*)$")
BOUNDARY = re.compile(r"^(\s*- \[| *#{1,6} |---\s*$|\s*$)")

# What `item_block_end` reads. Split out one per shape rather than folded into
# `BOUNDARY`, because the fix needed them to mean different things: a heading
# ends a block, an indented paragraph continues one, and `BOUNDARY` could not
# tell those apart -- it matched a blank line, which is what shredded the rows.
RULE_ONLY = re.compile(r"^---\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
FENCE = re.compile(r"^\s*```")
CONTINUATION = re.compile(r"^  +\S")
# `**From `## <section>`:**` -- the marker this queue uses when rows were lifted
# out of a dated checkpoint. It introduces the rows under it, so it ends the
# block above rather than continuing it.
FROM_MARKER = re.compile(r"^\*\*From `")

# Set from the command line so the same mover serves every queue tier.
QUEUE = TODO
QUEUE_NAME = "docs/TODO.md"

# A direction group starts at a `###` heading or at the owner's own words. Only
# `**Verbatim` splits: `**Owner answer...`, `**Owner decision...` and the like are
# parts of the direction they sit under, not new directions.
GROUP_START = re.compile(r"^(### |\*\*Verbatim)")

# A bold lead-in: the `**Master TODO items (verbatim):**` / `**Undeferred ...:**`
# shape this file uses to introduce a run of rows.
LEAD_IN = re.compile(r"^\*\*.*:(\*\*)?\s*$")

# Headings that structure the queue itself. Never archived even if every row
# beneath them closes, because removing them would leave the file shapeless.
STRUCTURAL = {"In progress", "Pending", "TOMBSTONES"}

KEEP, MOVE = 0, 1


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


def read_lines(path):
    with io.open(path, encoding="utf-8") as handle:
        return handle.read().split("\n")


def sections(lines):
    """Yield (title, start_index, end_index_exclusive) over `##` sections."""
    bounds = []
    for index, line in enumerate(lines):
        head = H2.match(line)
        if head:
            bounds.append((head.group(1), index))
    out = []
    if not bounds:
        return out
    if bounds[0][1] > 0:
        out.append(("(preamble)", 0, bounds[0][1]))
    for position, (title, start) in enumerate(bounds):
        end = bounds[position + 1][1] if position + 1 < len(bounds) else len(lines)
        out.append((title, start, end))
    return out


def census(lines, start, end):
    counts = {" ": 0, "x": 0, "~": 0, "T": 0}
    for line in lines[start:end]:
        found = MARKER.match(line)
        if found:
            counts[found.group(2)] += 1
    return counts


def item_block_end(lines, start, limit):
    """End index (exclusive) of the [x] item beginning at `start`.

    ## A BLANK LINE USED TO END THE BLOCK, AND IT SHREDDED EVERY MULTI-PARAGRAPH ROW

    This read `while not BOUNDARY.match(...)`, and `BOUNDARY` matches a blank
    line. A row whose closure carries its own evidence -- the normal shape in
    this queue -- therefore moved its **bullet line only**, and every indented
    continuation paragraph stayed behind. Measured on 2026-10-04: **eleven
    stranded lines** across four published versions, belonging to five rows that
    are sitting in `docs/FINALIZED.md` without the record attached to them.

    Both halves of the LAW broke at once and neither gate could see it. The
    archive was **missing** the paragraphs, and `docs/TODO.md` was **holding
    fragments of completed items** against the owner's own direction -- *"the
    todods sahll never hold completed items"*. The reassembly identity in
    `assert_lossless` proves `kept + moved == original`; it says nothing about
    **where a row ended**, which is why this survived eight batches of a gate
    working exactly as written.

    ## What a continuation is now

    Blank lines no longer end a block. The block runs on while the next non-blank
    line is an **indented** continuation, a table row, or inside a fenced code
    block -- and stops at the next bullet, heading, rule, direction group start or
    bold lead-in. Trailing blanks are left in the queue so the separator between
    rows survives the move.

    **Unindented prose is deliberately NOT swallowed.** A paragraph at column
    zero after a row is ambiguous: it is as likely to introduce the next row as
    to finish this one, and guessing either way is silent. `prose_hazards` refuses
    the run instead and names the lines, so the choice is made by somebody.
    """
    index = start + 1
    fenced = False
    last_content = start
    while index < limit:
        line = lines[index]
        if FENCE.match(line):
            fenced = not fenced
            last_content = index
            index += 1
            continue
        if fenced:
            last_content = index
            index += 1
            continue
        if not line.strip():
            index += 1
            continue
        if (MARKER.match(line) or H2.match(line) or H3.match(line)
                or RULE_ONLY.match(line) or GROUP_START.match(line)
                or LEAD_IN.match(line) or FROM_MARKER.match(line)):
            break
        if not (CONTINUATION.match(line) or TABLE_ROW.match(line)):
            break
        last_content = index
        index += 1
    return last_content + 1


def prose_hazards(lines, labels):
    """Unindented prose immediately after a moved block -- the stranding shape.

    Reported rather than guessed at, and it blocks `--apply`. The remedy is one
    keystroke per line: indent the paragraph by two spaces so it is visibly part
    of the row it belongs to, or lift it above the row if it belongs to the
    group. Either way a person decides, because both readings are plausible from
    the text and only one of them is true.
    """
    hazards = []
    for index in range(len(lines) - 1):
        if labels[index] != MOVE:
            continue
        walk = index + 1
        while walk < len(lines) and not lines[walk].strip():
            walk += 1
        if walk >= len(lines) or labels[walk] == MOVE:
            continue
        line = lines[walk]
        if (MARKER.match(line) or H2.match(line) or H3.match(line)
                or RULE_ONLY.match(line) or GROUP_START.match(line)
                or LEAD_IN.match(line) or FROM_MARKER.match(line)
                or CONTINUATION.match(line) or TABLE_ROW.match(line)
                or FENCE.match(line)):
            continue
        hazards.append((walk + 1, line.strip()[:96]))
    return hazards


def groups(lines, start, end):
    """Yield (group_start, group_end_exclusive) spans inside one section.

    ## A ROWLESS SPAN BELONGS TO THE ROWS BELOW IT, AND KEEPING IT STRANDED THE OWNER'S WORDS

    `GROUP_START` splits on a `### ` heading **and** on each `**Verbatim` line, so a section
    written the way this queue writes them -- a heading, four of the owner's sentences, then the
    rows answering all four -- splits into five spans of which **only the last holds any rows**.
    The first four counted zero `[x]`, so `group_done_only` was false for each, and they were kept
    while the rows left. Measured 2026-10-06 on exactly that shape: the rows archived correctly,
    `VERBATIM TRANSFER CONFIRMED` held because nothing was lost, and `docs/TODO.md` was left
    holding a heading and **three of the owner's sentences over an empty space** -- which is the
    precise outcome the docstring above promises this granularity prevents.

    The trailing sweep for an emptied `### ` heading could not save it either: the heading's body
    was not empty, it still had the three quotes.

    So a span with no rows at all **merges forward into the next span that has them.** A direction
    and the rows answering it then move as one object whichever order they were written in. A
    rowless span with nothing after it stays its own span and is kept -- that is unstatused work
    rather than a stranded quote, and `check-queue-integrity.py` rule 4 owns it.

    **THE PREAMBLE ABOVE THE FIRST GROUP IS NOT A GROUP AND NEVER MERGES.** The first draft of
    this merge let it, and it swallowed the section's own `## Pending` heading into the first
    direction group and archived it -- defeating `STRUCTURAL`, which exists precisely because
    removing such a heading leaves the file shapeless. A group begins at a `GROUP_START` by
    definition, so anything above the first one is preamble and is kept where it is.
    """
    starts = [index for index in range(start, end) if GROUP_START.match(lines[index])]
    if not starts:
        return [(start, end)]
    preamble = [(start, starts[0])] if starts[0] > start else []
    spans = []
    for position, group_start in enumerate(starts):
        group_end = starts[position + 1] if position + 1 < len(starts) else end
        spans.append((group_start, group_end))

    merged = []
    pending = None
    for span_start, span_end in spans:
        if pending is None:
            pending = span_start
        if sum(census(lines, span_start, span_end).values()):
            merged.append((pending, span_end))
            pending = None
    if pending is not None:
        merged.append((pending, spans[-1][1]))
    return preamble + merged


def plan(lines):
    labels = [KEEP] * len(lines)
    whole_sections = []
    whole_groups = []
    blocks = []
    untouched_done_titles = []

    for title, start, end in sections(lines):
        counts = census(lines, start, end)
        stripped = title.strip()
        done_only = counts["x"] and not (counts[" "] + counts["~"] + counts["T"])

        if done_only and stripped not in STRUCTURAL:
            for index in range(start, end):
                labels[index] = MOVE
            whole_sections.append((stripped, start + 1, end, counts["x"]))
            continue

        if "DONE" in stripped and not counts["x"] and counts[" "]:
            untouched_done_titles.append((stripped, start + 1, counts[" "]))

        for group_start, group_end in groups(lines, start, end):
            group_counts = census(lines, group_start, group_end)
            group_done_only = group_counts["x"] and not (
                group_counts[" "] + group_counts["~"] + group_counts["T"]
            )
            if group_done_only:
                for index in range(group_start, group_end):
                    labels[index] = MOVE
                whole_groups.append(
                    (stripped, group_start + 1, group_end, group_counts["x"])
                )
                continue

            index = group_start
            while index < group_end:
                found = MARKER.match(lines[index])
                if found and found.group(2) == "x":
                    stop = item_block_end(lines, index, group_end)
                    for inner in range(index, stop):
                        labels[inner] = MOVE
                    blocks.append((stripped, index + 1, stop - index))
                    index = stop
                    continue
                index += 1

    sweep_orphans(lines, labels)
    return labels, whole_sections, whole_groups, blocks, untouched_done_titles


def sweep_orphans(lines, labels):
    """Move any `###` heading or bold lead-in whose whole body has already gone.

    A heading or a `**...:**` lead-in left standing over nothing is the orphan
    this sweep exists to prevent -- it reads as work still outstanding when the
    rows beneath it have all closed. One whose body still holds a kept line
    stays exactly where it is.

    Runs to a fixed point, because moving a lead-in can orphan the heading above
    it, which can orphan the heading above that.

    ## ONCE A HEADING WAS STRANDED IT STAYED STRANDED FOR EVER, AND ONE HAD

    The second guard below read `if not any(labels[index] == MOVE for index in
    body): continue` -- a heading was swept **only when something in its body was
    moving in this run.** A heading whose body went in an *earlier* batch, leaving
    it standing over nothing on disk, therefore had an empty body with no MOVE
    lines in it, so every run afterwards skipped it. The sweep could clean a
    heading it had just emptied and could never clean one it had emptied before.

    Measured 2026-10-06 in `docs/TEST.md`: **`### Owner direction -- a prisoner IS
    allowed to cross a gate, and zoning and doors decide it` had been an empty
    heading since the file was created**, its verbatim body and closure record
    already in `FINALIZED.md`. It read as outstanding test work in the one ledger
    whose rows the owner was about to work through, and it was found only because
    `check-queue-integrity` was extended to cover that file.

    So an **entirely blank body** now qualifies as well. The distinction kept is
    the one that matters: a heading with any kept, non-blank line under it still
    stays exactly where it is.

    ## AND THE BLANK TEST MEASURES TO THE NEXT HEADING, NOT THE NEXT ANCHOR

    The first version of it measured to the next **anchor**, and `anchors`
    includes every `LEAD_IN` -- a `**...:**` line. **A lead-in is part of the
    section it introduces**, so a heading followed by one has a "body" of a single
    blank line and looked empty. Applied once against `docs/TEST.md`, that swept
    **four headings away from their own content**, leaving the owner's verbatim
    quotes sitting under nothing: the stranded-body defect this sweep exists to
    prevent, caused by the sweep, in one run.

    It was caught by reading the diff rather than the summary. The mover's own
    reassembly identity **held throughout** -- nothing was lost, every line was
    either kept or archived -- which is exactly why it could not see the problem:
    *where a line goes is not the thing that proof proves.*
    """
    anchors = [index for index, line in enumerate(lines)
               if H2.match(line) or H3.match(line) or LEAD_IN.match(line)]
    headings = [index for index, line in enumerate(lines)
                if H2.match(line) or H3.match(line)]
    changed = True
    while changed:
        changed = False
        for position, anchor in enumerate(anchors):
            if H2.match(lines[anchor]) or labels[anchor] == MOVE:
                continue
            end = anchors[position + 1] if position + 1 < len(anchors) else len(lines)
            body = range(anchor + 1, end)
            if any(labels[index] == KEEP and lines[index].strip() for index in body):
                continue
            moving = any(labels[index] == MOVE for index in body)
            # Residue only when there is nothing at all before the NEXT HEADING. A lead-in
            # belongs to its heading, so it must not end the region this test looks at.
            blank = False
            if H3.match(lines[anchor]):
                following = next((h for h in headings if h > anchor), len(lines))
                blank = not any(lines[index].strip()
                                for index in range(anchor + 1, following))
            if not moving and not blank:
                continue
            for index in range(anchor, end):
                labels[index] = MOVE
            changed = True


def assert_lossless(lines, labels):
    kept = [line for line, label in zip(lines, labels) if label == KEEP]
    moved = [line for line, label in zip(lines, labels) if label == MOVE]
    rebuilt = []
    keep_iter = iter(kept)
    move_iter = iter(moved)
    for label in labels:
        rebuilt.append(next(keep_iter) if label == KEEP else next(move_iter))
    if rebuilt != lines:
        raise SystemExit("ABORT: reassembly does not reproduce the original file")
    return kept, moved


def build_archive(lines, labels, whole_sections, whole_groups, blocks, version, today):
    """Render the archive section from the MOVE lines, in original order."""
    out = []
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Archived from the queue - every finished item moved out of %s (%s)"
               % (QUEUE_NAME, today))
    out.append("")
    out.append("<!-- archived-queue:begin -->")
    out.append("")
    out.append("**Verbatim owner direction (2026-10-02, three items):** *\"we need to move all "
               "finished items to finalized.md from the todo, the todods sahll never hold "
               "completed items, they are always to be moved to finalized first then deleted "
               "from the todods once confirmed virbatium transfer\"*")
    out.append("")
    out.append("Every line below was moved out of `%s` **unaltered**. The transfer is " % QUEUE_NAME +
               "not asserted by reading it: the mover labelled each line of the original file "
               "either kept or moved, and proved that reassembling the two halves in their "
               "original order reproduces the original file byte for byte. Nothing was "
               "reworded, shortened or summarised, per LAW #0.")
    out.append("")
    out.append("What moved: **%d whole `##` sections** that were closed records end to end, "
               "**%d whole direction groups** whose every row was done, and **%d further `[x]` "
               "rows** lifted out of groups that still hold open work. What did not move: every "
               "`[ ]`, `[~]` and `[T]` row, because a `[T]` row belongs to the post-completion "
               "test phase and is not finished work."
               % (len(whole_sections), len(whole_groups), len(blocks)))
    out.append("")
    out.append("Everything below is in **original queue order**. A `> moved from` line marks each "
               "change of source section, so any row can be traced back to where it sat.")
    out.append("")

    # Emit every moved line in original order, annotating each change of source
    # section. Order is the thing that carries the context, so it is preserved.
    current_section = None
    emitted_marker_for = None
    for index, line in enumerate(lines):
        head = H2.match(line)
        if head:
            current_section = head.group(1).strip()
        if labels[index] != MOVE:
            continue
        if current_section != emitted_marker_for and not head:
            out.append("")
            out.append("> moved from `## %s` in `%s`" % (current_section or "(top)", QUEUE_NAME))
            out.append("")
            emitted_marker_for = current_section
        if head:
            emitted_marker_for = current_section
        out.append(line)

    out.append("")
    out.append("Build at the time of the move: **%s**. No source file was touched by this "
               "change; it moves ledger rows only." % version)
    out.append("")
    out.append("<!-- archived-queue:end -->")
    out.append("")
    return out


def write_backup():
    """Snapshot the queue and the archive BEFORE either is written.

    ## Why this exists, and why its absence was invisible

    `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE` names
    `verify-archive-move.py` as re-checking this mover's result **independently**,
    and an independent check needs the pre-move file to recompute the plan from.
    **This mover never wrote one.** The folder that check reads,
    `backup-20261002/`, was copied by hand on 2026-10-02, so the re-check the LAW
    promises worked once and then reported `FAILED` on every later move -- for the
    arithmetic reason that it was comparing a newer queue against an older
    baseline, which says nothing at all about whether a transfer was verbatim.

    Written before the FINALIZED append rather than after, because a snapshot
    taken after the thing it is meant to snapshot is not one. Returns the folder
    so the caller can print it: a backup nobody can find is not a backup.

    The queue is stored under its own basename and its repo-relative name is
    recorded beside it, so a `--queue docs/DECOMPOSED.md` move is verifiable on
    the same footing as a TODO move.
    """
    # **A SECOND IS NOT A UNIQUE NAME, and this crashed on the day it was written.** Archiving
    # `docs/TODO.md` and then `docs/DECOMPOSED.md` back to back lands both inside the same second,
    # so the second run died with `FileExistsError` from `os.makedirs`. It failed safely -- the
    # snapshot is taken before anything else is written, so the queue and the archive were both
    # untouched -- but a mover that cannot run twice in a row is a mover nobody can use at the end
    # of a batch, which is exactly when the LAW says to run it.
    #
    # Suffixed rather than made longer: microseconds would still collide in principle and would
    # make the folder name unreadable. This asks the filesystem, which is the only authority on
    # whether a name is taken.
    if not os.path.isdir(BACKUPS):
        os.makedirs(BACKUPS)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = os.path.join(BACKUPS, "backup-" + stamp)
    suffix = 2
    while os.path.exists(folder):
        folder = os.path.join(BACKUPS, "backup-%s-%d" % (stamp, suffix))
        suffix += 1
    os.makedirs(folder)
    shutil.copy2(QUEUE, os.path.join(folder, os.path.basename(QUEUE)))
    shutil.copy2(FINALIZED, os.path.join(folder, os.path.basename(FINALIZED)))
    with io.open(os.path.join(folder, QUEUE_STAMP), "w", encoding="utf-8", newline="") as handle:
        handle.write(QUEUE_NAME + "\n")
    return folder


def package_version():
    about = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")
    try:
        text = io.open(about, encoding="utf-8-sig").read()
    except IOError:
        return "unknown"
    found = re.search(r"<modVersion>([^<]+)</modVersion>", text)
    return found.group(1).strip() if found else "unknown"


def main():
    global QUEUE, QUEUE_NAME
    apply_it = "--apply" in sys.argv
    if "--queue" in sys.argv:
        QUEUE_NAME = sys.argv[sys.argv.index("--queue") + 1]
        QUEUE = os.path.join(REPO, QUEUE_NAME)
    lines = read_lines(QUEUE)
    labels, whole_sections, whole_groups, blocks, untouched = plan(lines)
    kept, moved = assert_lossless(lines, labels)

    say("archive-finished-todo")
    say("  original lines           : %d" % len(lines))
    say("  lines moved              : %d" % len(moved))
    say("  lines kept               : %d" % len(kept))
    say("  reassembly identity      : HOLDS")
    say()
    say("  whole sections moved     : %d" % len(whole_sections))
    for title, start, end, done in whole_sections:
        say("      %5d-%-5d x=%-3d %s" % (start, end, done, title[:66]))
    say()
    say("  whole direction groups   : %d" % len(whole_groups))
    grouped = {}
    for title, _start, _end, done in whole_groups:
        entry = grouped.setdefault(title, [0, 0])
        entry[0] += 1
        entry[1] += done
    for title in grouped:
        say("      %-3d groups, %-4d rows  from  %s"
              % (grouped[title][0], grouped[title][1], title[:56]))
    say()
    say("  loose [x] rows moved     : %d" % len(blocks))
    counted = {}
    for title, _line, _span in blocks:
        counted[title] = counted.get(title, 0) + 1
    for title in counted:
        say("      %-4d from  %s" % (counted[title], title[:66]))

    multi = [(t, n, s) for t, n, s in blocks if s > 1]
    say()
    say("  rows with continuations  : %d" % len(multi))
    for title, line_number, span in multi[:20]:
        say("      line %-5d %d lines  (%s)" % (line_number, span, title[:50]))

    if untouched:
        say()
        say("  SECTIONS TITLED DONE WHOSE ROWS ARE STILL [ ] - NOT MOVED:")
        for title, start, open_rows in untouched:
            say("      line %-5d %d open rows  %s" % (start, open_rows, title[:60]))

    remaining = census(kept, 0, len(kept))
    say()
    say("  queue after the move     : x=%d  open=%d  partial=%d  test=%d"
          % (remaining["x"], remaining[" "], remaining["~"], remaining["T"]))

    hazards = prose_hazards(lines, labels)
    if hazards:
        say()
        say("  UNARCHIVABLE PROSE DIRECTLY AFTER A MOVED BLOCK - %d line(s):" % len(hazards))
        for line_number, text in hazards:
            say("      line %-5d %s" % (line_number, text))
        say()
        say("  A paragraph at column zero after a closed row is ambiguous: it reads as the")
        say("  end of that row and as the introduction to the next one, and the mover is")
        say("  not allowed to guess. Indent it two spaces to make it part of the row, or")
        say("  lift it above the row to make it part of the group. Nothing is written until")
        say("  it is one or the other -- this is the exact shape that stranded eleven lines")
        say("  across four published versions.")
        return 3

    if not apply_it:
        say()
        say("  PLAN ONLY. Nothing written. Re-run with --apply.")
        return 0

    # **NOTHING MOVED MEANS NOTHING IS WRITTEN, and this was learned the hard way.** Running
    # `--apply` on a queue that already holds no `[x]` row used to append an archive region
    # containing a heading, the owner's quoted direction, three paragraphs of preamble and **zero
    # rows** -- a record of a transfer that did not happen. Two of them went into
    # `docs/FINALIZED.md` while regression-testing the back-to-back fix above, and had to be taken
    # back out by hand.
    #
    # The LAW protects archived entries, and an empty region contains none, so removing those two
    # deleted nothing. But a ledger that accumulates ceremonial no-ops is a ledger people stop
    # reading, which is the same failure as a queue full of `[x]` rows nobody can read past.
    if not moved:
        say()
        say("  NOTHING TO MOVE. %s holds no [x] row, so no archive region was written." % QUEUE_NAME)
        return 0

    # **The real clock, not a literal.** This read `today = "2026-10-02"`, so every
    # archive region this mover would ever write was stamped that day forever --
    # and `docs/FINALIZED.md` carries one written on 2026-10-03 saying 2026-10-02.
    # This repo enforces a dated-claim rule on every other document; its own
    # archiver was the thing breaking it.
    today = datetime.date.today().isoformat()
    version = package_version()
    archive = build_archive(lines, labels, whole_sections, whole_groups, blocks,
                            version, today)

    # The pre-move snapshot, written before anything else is, so the independent
    # re-check the LAW names has a baseline that matches THIS move.
    backup = write_backup()

    # FINALIZED FIRST, per the LAW and per the owner's stated order.
    existing = io.open(FINALIZED, encoding="utf-8").read()
    with io.open(FINALIZED, "w", encoding="utf-8", newline="") as handle:
        handle.write(existing.rstrip("\n") + "\n" + "\n".join(archive))

    # Confirm the archive now contains every moved line, verbatim, before deleting.
    written = io.open(FINALIZED, encoding="utf-8").read()
    missing = [line for line in moved if line.strip() and line not in written]
    if missing:
        with io.open(FINALIZED, "w", encoding="utf-8", newline="") as handle:
            handle.write(existing)
        raise SystemExit("ABORT: %d moved lines are not present in the archive; "
                         "FINALIZED.md restored, the queue untouched. Pre-move "
                         "snapshot kept at %s. First: %r"
                         % (len(missing), os.path.relpath(backup, REPO), missing[0][:120]))

    # Only now does anything leave the queue.
    with io.open(QUEUE, "w", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(kept))

    say()
    say("  pre-move snapshot        : %s" % os.path.relpath(backup, REPO))
    say("  docs/FINALIZED.md        : archive appended, %d lines" % len(archive))
    say("  verbatim confirmation    : all %d moved lines present in the archive" % len(moved))
    say("  %-24s : rewritten, %d lines" % (QUEUE_NAME, len(kept)))
    say()
    say("  Now re-check it independently:  python tools/verify-archive-move.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
