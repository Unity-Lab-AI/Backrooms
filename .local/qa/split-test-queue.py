# -*- coding: utf-8 -*-
"""Move the post-completion test phase out of TODO.md into its own ledger.

Owner direction, 2026-10-06, verbatim:

    "we should make a seperate todo=Test.md and move all test items to it to be done and clear
     todo , if its true all items are done."

**The condition is met for this file and only this file.** `docs/TODO.md` holds 0 open and 0
partial rows; every remaining row is `[T]`. The master TODO still carries unticked scope and the
ROADMAP still carries milestone containers, and neither is touched here.

**NOTHING IS DELETED AND THE MOVE IS PROVED, not read.** Every line of the body is required to come
out the other side byte-identical, and the count of `[T]` rows is required to match exactly. The
same rule the archive move follows: verbatim is proved by a reassembly identity, never by looking
at the output.
"""
import io
import os
import sys

NL = chr(10)
TODO = "docs/TODO.md"
TEST = "docs/TEST.md"

TEST_HEADER = """# TEST — the post-completion test phase

**Tier 4 of 4, and the only tier whose rows a build cannot close.** Every row here needs the game
running, and **only the owner launches RimWorld, through RimSort**.

**Owner direction, 2026-10-06, verbatim:** *"we should make a seperate todo=Test.md and move all
test items to it to be done and clear todo , if its true all items are done."*

It was true of [`TODO.md`](TODO.md): zero open, zero partial, and every remaining row `[T]`. So the
whole body moved here unchanged and that file went back to its template state.

| Ledger | Grain |
|--------|-------|
| [`ROADMAP.md`](ROADMAP.md) | MAJOR — phases and milestones |
| [`TODO.md`](TODO.md) | MINOR — the working queue, **open buildable work only** |
| [`DECOMPOSED.md`](DECOMPOSED.md) | smallest execution units, open only |
| **`TEST.md`** (this file) | **the test phase — `[T]` only, every row needs a launch** |
| [`FINALIZED.md`](FINALIZED.md) | permanent archive, append-only |

Status markers here are `[T]` and nothing else. A row that turns out to be buildable after all goes
**back to `TODO.md`** as `[ ]`; it is not quietly built from here, because this file's whole meaning
is *waiting on a launch*.

**LAW #0 still binds every row:** the owner's verbatim words are preserved exactly as they were in
`TODO.md`. Nothing was reworded on the way across.

**Closing a row needs evidence from a running game** — a letter, a log line, a save that reloads —
recorded on the row, and then the row moves to `FINALIZED.md` by the usual archive ceremony.

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then
`python .local/qa/bridge.py call rimworld/list_letters '{}'`.

---
"""

TODO_EMPTY = """## In progress

_(none)_

## Pending

_(none)_

> **The post-completion test phase lives in [`TEST.md`](TEST.md) as of 2026-10-06.** Owner:
> *"we should make a seperate todo=Test.md and move all test items to it to be done and clear
> todo , if its true all items are done."* It was true: this file reached zero open and zero
> partial, so every `[T]` row moved out whole. **`[T]` must not reappear here** — a row waiting on
> a launch belongs in that file, and a row that turns out to be buildable comes back as `[ ]`.
"""


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)

    starts = [i for i, l in enumerate(lines) if l.startswith("## In progress")]
    ends = [i for i, l in enumerate(lines) if l.startswith("## TOMBSTONES")]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        print("REFUSED: could not find exactly one body between '## In progress' and '## TOMBSTONES'")
        return 1

    header = lines[:starts[0]]
    body = lines[starts[0]:ends[0]]
    tail = lines[ends[0]:]

    open_rows = [l for l in body if l.lstrip().startswith("- [ ] ")]
    partial_rows = [l for l in body if l.lstrip().startswith("- [~] ")]
    done_rows = [l for l in body if l.lstrip().startswith("- [x] ")]
    test_rows = [l for l in body if l.lstrip().startswith("- [T] ")]

    if open_rows or partial_rows or done_rows:
        print("REFUSED: the condition is not met. open=%d partial=%d complete=%d"
              % (len(open_rows), len(partial_rows), len(done_rows)))
        return 1
    if not test_rows:
        print("REFUSED: there is nothing to move")
        return 1

    test_text = TEST_HEADER + NL + NL.join(body).strip(NL) + NL
    todo_text = NL.join(header) + TODO_EMPTY + NL + NL.join(tail)

    # ---------------------------------------------------------------- the proof, before writing
    problems = []
    moved = [l for l in test_text.split(NL) if l.lstrip().startswith("- [T] ")]
    if len(moved) != len(test_rows):
        problems.append("test rows in: %d, out: %d" % (len(test_rows), len(moved)))
    for original in test_rows:
        if original not in moved:
            problems.append("a test row is not byte-identical after the move: %r" % original[:70])
    body_kept = [l for l in test_text.split(NL)]
    for line in body:
        if line.strip() and line not in body_kept:
            problems.append("a body line was lost: %r" % line[:70])
    if any(l.lstrip().startswith("- [T] ") for l in todo_text.split(NL)):
        problems.append("a test row is still in TODO.md after the move")
    for line in header + tail:
        if line.strip() and line not in todo_text.split(NL):
            problems.append("a header or tombstone line was lost: %r" % line[:70])

    if problems:
        print("REFUSED: %d problem(s), nothing written" % len(problems))
        for problem in problems[:8]:
            print("  - %s" % problem)
        return 1

    io.open(TEST, "w", encoding="utf-8", newline=NL).write(test_text)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(todo_text)

    print("moved %d test row(s) to %s" % (len(test_rows), TEST))
    print("  every moved line byte-identical : yes")
    print("  every body line conserved       : yes")
    print("  TODO.md left with [T] rows      : none")
    print("  TODO.md header and tombstones   : intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
