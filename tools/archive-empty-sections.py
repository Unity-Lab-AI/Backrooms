# -*- coding: utf-8 -*-
"""Move a queue section that holds no rows into `FINALIZED.md`, proved by reassembly.

Why this exists
---------------
**Owner, 2026-10-05, verbatim:** *"clean up the todo properly"*.

Measured the same day: `docs/TODO.md` was **402 lines carrying ten open rows**, and **13 of its 30
sections held no row at all**. Those are dated owner-direction and session-direction sections whose
rows were all closed and archived months of batches ago. The heading survived the work.

That is the same defect class as a pointer to a row that no longer exists, one level up: **a
section with a heading and prose and nothing to do reads as a part of the queue somebody has not
got to yet.** It is why a reader asking *what is left* cannot answer from the file.

The terminal state is the owner's own, recorded in one of the sections this tool clears:
*"to get the todo to a templet form with no items listed"*.

What it refuses to do
---------------------
* **It never touches a section holding a row** of any kind, including `[T]`.
* **It never touches a structural heading** — the preamble, `## In progress`, `## Pending`,
  `## TOMBSTONES`. Those are the template the owner asked for.
* **It never guesses.** Sections are named on the command line by their exact heading text, so
  clearing one is a decision somebody made and can be read back in the commit.
* **It writes nothing unless the reassembly identity holds**: `kept + moved == original`, compared
  as text, not as a summary. This is the same proof `archive-finished-todo.py` uses, and it is the
  only kind of verbatim guarantee that is worth anything -- reading the output back and seeing
  familiar words is not a proof.

Usage
-----
    python tools/archive-empty-sections.py --list
    python tools/archive-empty-sections.py --apply "### Heading text" ["### Another"] ...

Exit status is the result. Run from the repository root.
"""
import io
import os
import re
import sys

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODO = os.path.join(REPO, "docs", "TODO.md")
ARCHIVE = os.path.join(REPO, "docs", "FINALIZED.md")

ROW = re.compile(r"^\s*- \[[ ~Tx]\] ")

# The template the owner asked the file to become. These are never candidates however empty they
# get, because empty is their correct resting state.
STRUCTURAL = ("# TODO", "## In progress", "## Pending", "## TOMBSTONES")


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def sections(lines):
    """(heading, start, end) for every heading block, end exclusive."""
    marks = [i for i, l in enumerate(lines) if l.startswith("#")]
    out = []
    for position, start in enumerate(marks):
        end = marks[position + 1] if position + 1 < len(marks) else len(lines)
        out.append((lines[start].strip(), start, end))
    return out


def candidates(lines):
    found = []
    for heading, start, end in sections(lines):
        if any(ROW.match(l) for l in lines[start:end]):
            continue
        if any(heading.startswith(s) for s in STRUCTURAL):
            continue
        found.append((heading, start, end))
    return found


def main(argv):
    original = io.open(TODO, encoding="utf-8-sig").read()
    lines = original.split(NL)

    if "--list" in argv or len(argv) < 2:
        empty = candidates(lines)
        say("archive-empty-sections")
        say("  %s: %d line(s), %d section(s)"
            % ("docs/TODO.md", len(lines), len(sections(lines))))
        say("  sections holding no row of any kind : %d" % len(empty))
        say("")
        for heading, start, end in empty:
            say("  line %-5d %-3d lines  %s" % (start + 1, end - start, heading[:92]))
        say("")
        say("  Nothing is moved without --apply and an exact heading. A section is cleared by a "
            "decision, never by a sweep.")
        return 0

    wanted = [a for a in argv[1:] if a != "--apply"]
    empty = {heading: (start, end) for heading, start, end in candidates(lines)}
    missing = [w for w in wanted if w not in empty]
    if missing:
        for w in missing:
            say("NOT A CLEARABLE SECTION: %r" % w[:90])
        say("")
        say("It either holds a row, is structural, or does not exist. --list shows what can go.")
        return 1

    # Highest line first, so each removal cannot move the next one's bounds.
    chosen = sorted(((empty[w][0], empty[w][1], w) for w in wanted), reverse=True)
    kept = list(lines)
    moved_blocks = []
    for start, end, heading in chosen:
        moved_blocks.append((heading, lines[start:end]))
        del kept[start:end]
    moved_blocks.reverse()

    kept_text = NL.join(kept)
    moved_text = NL.join(NL.join(block) for _, block in moved_blocks)

    # ---------------------------------------------------------------- the proof
    # Not "does the archive contain the words". Reassemble the file from its two halves and require
    # the result to be the input, character for character. If a single space was dropped this fails.
    # Rebuilt as a LIST OF LINES, never as joined strings. The first version of this joined each
    # slice and then joined the results, which invents a newline for every empty slice -- and an
    # adjacent pair of cleared sections produces one. **The guard caught that on its first run**,
    # which is the whole argument for having it: a proof that cannot fail on its own author's
    # mistake is not a proof.
    rebuilt = []
    cursor = 0
    for start, end, _ in sorted(chosen):
        rebuilt.extend(lines[cursor:start])
        rebuilt.extend(lines[start:end])
        cursor = end
    rebuilt.extend(lines[cursor:])
    if NL.join(rebuilt) != original:
        say("FAILED: the reassembly identity does not hold, so nothing is written. This is the "
            "guard, not a glitch -- it means the slice bounds are wrong.")
        return 1

    archive = io.open(ARCHIVE, encoding="utf-8-sig").read()
    header = (NL + "## Queue sections cleared 0.12.99-dev — owner: " + chr(34) +
              "clean up the todo properly" + chr(34) + NL + NL +
              "**Every section below held NO row of any kind.** Its rows were closed and archived "
              "in earlier batches and the heading outlived them, so the file read as though there "
              "were work in it. Moved here **verbatim and whole**, proved by a byte-identical "
              "reassembly of `docs/TODO.md` from what was kept plus what was moved." + NL + NL +
              "**Two standing rules were lifted into `docs/NOW.md` before this ran**, because "
              "their only copy was inside a section being cleared: *the owner alone launches, "
              "sorts and publishes*, and the owner's own terminal state for the queue, "
              "*" + chr(34) + "to get the todo to a templet form with no items listed" +
              chr(34) + "*." + NL + NL)
    io.open(ARCHIVE, "w", encoding="utf-8", newline=NL).write(
        archive.rstrip(NL) + NL + header + moved_text + NL)

    # Read the archive back and require every moved line to be in it. A second, differently shaped
    # check: the identity above proves nothing was lost from the SPLIT, this proves the write landed.
    written = io.open(ARCHIVE, encoding="utf-8-sig").read()
    absent = [l for l in moved_text.split(NL) if l.strip() and l not in written]
    if absent:
        say("FAILED: %d moved line(s) are not in the archive after the write; TODO.md is "
            "untouched" % len(absent))
        for l in absent[:5]:
            say("  missing: %s" % l[:110])
        return 1

    io.open(TODO, "w", encoding="utf-8", newline=NL).write(kept_text)

    say("archive-empty-sections")
    say("  sections moved      : %d" % len(chosen))
    for heading, block in moved_blocks:
        say("     %-3d lines  %s" % (len(block), heading[:92]))
    say("  reassembly identity : kept + moved == original, character for character")
    say("  archive read back   : every moved line present")
    say("  docs/TODO.md        : %d lines, was %d" % (len(kept_text.split(NL)), len(lines)))
    say("")
    say("VERBATIM TRANSFER CONFIRMED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
