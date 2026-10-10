# -*- coding: utf-8 -*-
"""Move the three starting-facility feedback-loop rows to the test phase.

**Owner direction, 2026-10-06, at the fork:** convert them to `[T]`.

**Status only. Not one word of any description changes** -- that is the LAW, and it is the whole
reason this is a script that rewrites three markers rather than an edit that rewrites three rows.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

KEYS = [
    "**The starting-facility feedback loop.**",
    "**THE PRE-LAUNCH BASELINE, measured 2026-10-05 before any launch",
    "**What the loop can and cannot carry, read off `RimroomsStartDef` rather than hoped for.**",
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    moved = 0
    for key in KEYS:
        hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [~] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d partial row(s)" % (key[:48], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        rest = raw.lstrip()[len("- [~] "):]
        # The marker is the only thing that moves.
        lines[hits[0]] = "%s- [T] %s" % (lead, rest)
        moved += 1

    rewritten = NL.join(lines)
    # **PROVED RATHER THAN TRUSTED: the file differs by exactly three characters.** Three `~`
    # became three `T` and nothing else moved, which is the only statement worth making about an
    # edit to a queue that holds verbatim owner words.
    if len(rewritten) != len(text):
        print("REFUSED: length changed by %d; a status edit may not" % (len(rewritten) - len(text)))
        return 1
    differences = sum(1 for before, after in zip(text, rewritten) if before != after)
    if differences != moved:
        print("REFUSED: %d character(s) differ for %d status change(s)" % (differences, moved))
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(rewritten)
    print("moved %d row(s) to [T]; exactly %d character(s) differ" % (moved, differences))
    return 0


if __name__ == "__main__":
    sys.exit(main())
