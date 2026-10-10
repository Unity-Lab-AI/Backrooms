# -*- coding: utf-8 -*-
"""Retire the two 2026-10-02 bug-report rows on the owner's direction.

**Owner, 2026-10-05, verbatim:** *"remove these, they are no longer needed"*, naming the two rows
by their own summary: the starting-goods one and the Prepare Carefully food one.

LAW: FINALIZED before DELETE. These are closed here with the owner's verbatim words as the reason,
then moved by `tools/archive-finished-todo.py` and proved by `tools/verify-archive-move.py`. Not a
single word of either row is edited -- the status letter changes and the reason is appended.

**The direction is recorded rather than acted on silently**, because a row retired without its
reason is indistinguishable from a row that got lost, and that has already happened twice in this
queue.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

REASON = (
    "**RETIRED 0.12.99-dev BY OWNER DIRECTION, verbatim: *\"remove these, they are no longer "
    "needed\"*.** Named directly, as the starting-goods report and the Prepare Carefully food "
    "report. **No further investigation is owed and none is implied by this closure** -- the row "
    "is not being deferred, re-scoped or quietly carried somewhere else. "
    "**What was found stays recorded in the archive rather than being thrown away with the row:** "
    "a 9,216-cell sweep of the live start, and four candidate causes eliminated against the "
    "installed game -- the arrival scen part, the start spot, the gen step order and the drop "
    "method. The diagnostic that reports a promised-but-absent starting grant is built, reads the "
    "promise without creating anything, and never blocks a start; it stays in the package and is "
    "held by its own proof claims. So if either symptom is ever seen again, the next reader starts "
    "from the four eliminations rather than repeating them."
)

PHRASES = [
    "they need to properly spawn in with starting goods",
    "my preparecarfully mod food did not appear",
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    missed = []
    done = 0
    for phrase in PHRASES:
        hits = [i for i, line in enumerate(lines)
                if line.lstrip().startswith(("- [ ] ", "- [~] ", "- [T] ")) and phrase in line]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        index = hits[0]
        raw = lines[index]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[index] = "%s- [x] %s -- %s" % (lead, raw.lstrip()[6:].rstrip(), REASON)
        done += 1
    if missed:
        for phrase, count in missed:
            print("NOT RETIRED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("retired %d row(s) with the owner's verbatim reason attached" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
