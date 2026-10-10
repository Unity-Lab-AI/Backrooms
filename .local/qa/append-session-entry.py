"""Append the 2026-10-02 session entry to docs/FINALIZED.md.

Written with the Write tool and applied from a file rather than a heredoc: a
heredoc has mangled an escape or an apostrophe eleven times in this repository,
and `docs/NOW.md` records each one.
"""

import io
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FINALIZED = os.path.join(REPO, "docs", "FINALIZED.md")

ENTRY = u"""
---

## Session 2026-10-02 - the queue was eight parts archive to one part work (0.12.79-dev)

**Verbatim user direction:** *"we need to move all finished items to finalized.md from the todo,
the todods sahll never hold completed items, they are always to be moved to finalized first then
deleted from the todods once confirmed virbatium transfer"*

**Files touched:** `docs/TODO.md`, `docs/DECOMPOSED.md`, `docs/FINALIZED.md`, `docs/NOW.md`,
`.claude/CONSTRAINTS.md`, `.claude/CLAUDE.md`, `.claude/memory-templates/MEMORY.md`,
`.claude/memory-templates/feedback_finalized_before_delete.md`,
`tools/check-doc-conformance.py`, `.local/register/proof-housekeeping.py`,
`.local/register/plant-housekeeping.py`, `.local/qa/archive-finished-todo.py` (new),
`.local/qa/verify-archive-move.py` (new), `.local/qa/plant-archived-queue-scope.py` (new, suite
TWENTY-TWO), `.local/qa/check-queue-orphans.py` (new), `.local/qa/todo-census.py` (new),
`.local/qa/todo-inventory.py` (new), `.local/qa/preview-kept-todo.py` (new).

**No source file was touched.** This is a ledger change, a LAW change and a two-instrument
re-aim. The build is unchanged at 0.12.79-dev.

### WHAT THE QUEUE ACTUALLY WAS

`docs/TODO.md` held **727 `[x]` rows across 2,716 lines**. Of that, **thirty whole `##`
sections** were closed session records end to end and **fifty-one whole owner-direction groups**
had every row done. **2,039 lines moved out. 676 remain.**

**The open count went UP, 42 to 79, and that is the finding rather than a side effect.** Nothing
closed and nothing opened. The old number was a count of a prefix of a file nobody could read to
the end of, and `NOW.md` had been quoting it as the queue depth for weeks.

### `DECOMPOSED.md` ASSERTED A TRANSFER THAT HAD NEVER HAPPENED

Its heading read *"Complete - moved to FINALIZED, descriptions retained per LAW"* over
**fifty-six entries**. Checked by string against `FINALIZED.md`: **zero hits for any of them.**
Not one of those decomposed units had ever been archived. The file was not stale, it was wrong,
and it had been wrong in a way that read as compliance. 228 lines moved, 79 remain.

**This is the defect the direction exists to prevent**, found by acting on the direction rather
than by auditing for it.

### VERBATIM IS AN IDENTITY HERE, NOT A READING

`.local/qa/archive-finished-todo.py` **never rewrites a line.** It labels every line index of the
source either KEEP or MOVE and asserts

```
reassemble(KEEP + MOVE, by original index) == original bytes
```

before writing anything. Then the user's order exactly: archive written **first**, every moved
line confirmed present in it, and only then is the queue rewritten - and a missing line restores
`FINALIZED.md` and leaves the queue untouched rather than half-finishing.

`.local/qa/verify-archive-move.py` re-checks the finished result against a pre-move backup
**independently of the mover**, five ways: the queue is byte-identical to the recomputed KEEP
half; every moved line is in the archive region in the same relative order; the line multiset is
conserved; the archive is unaltered above the append point; zero `[x]` rows remain. All five
hold, for both files.

### A CLOSURE MOVES WITH ITS CONTEXT, AND THE FIRST CUT GOT THAT WRONG

The first pass moved `[x]` rows at bullet granularity and left **verbatim owner directions
standing over empty space** - the quote with nothing under it, reading as outstanding work. That
is a LAW #0 problem, not a cosmetic one.

So the cut has three granularities, coarsest first: a whole `##` section that is a closed record;
a whole direction group, from a `###` heading or a `**Verbatim` line to the next, whose every row
is done; then individual rows. A fixed-point sweep then moves any heading or `**...:**` lead-in
whose entire body has gone. **677 lines became 676** on that sweep alone, and the queue stopped
having holes in it.

### TWO SECTIONS TITLED DONE WERE DELIBERATELY NOT MOVED

*The first walked level* and *Lights and geometry*, both 0.12.61-dev, carry **twenty-two `[ ]`
rows** between them under headings that say DONE. **The title is not the marker.** Promoting a
row the user never ticked would be inventing a closure, so they stayed, the mover reports them
every run, and they are now the first thing in the queue to look at.

### ONE RULE AND ONE PROOF RE-AIMED, AND BOTH CAME OUT STRONGER

**`check-doc-conformance.py` rule 6** fails the build when a direction quoted in `FINALIZED.md`
never reached `TODO.md`. Read literally it would now fail for **every archived direction** -
demanding the queue keep exactly what the direction says it must not. It is scoped to a delimited
`archived-queue:begin` / `:end` region, written only by the mover and only alongside the rows
that closed it. A direction acted on and never queued still appears only in a session write-up,
outside every region, and still fails.

**Proved both ways** by `.local/qa/plant-archived-queue-scope.py`, suite twenty-two, **4 of 4**: a
direction outside every region fails; the same direction inside a region passes, so the escape is
not dead code; a region whose markers are stripped fails, so the markers are load-bearing.

**`proof-housekeeping.py`** read four closure markers out of `docs/TODO.md`, where a closed row no
longer sits. It reads the archive now **and additionally asserts the row is gone from the queue** -
which the single-file read could not express. **A row flipped to `[x]` and left sitting in the
queue now fails a claim that used to pass it**, and so does a row deleted with nothing archived.
Four plant anchors in `plant-housekeeping.py` re-aimed with it; **41 of 41 still caught**.

### THE LAW GAINED ITS MISSING HALF

`§FINALIZED BEFORE DELETE` governed the **order** of a removal and never said the removal was
**mandatory**. It does now, as its second rule: every queue tier carries `[ ]`, `[~]` and `[T]`
only; `[x]` is transient, legal between finishing and archiving **in the same batch**; `[T]` is
not finished work; a DONE title is not a marker; closures move with their context; and verbatim
means the reassembly identity above. Indexed in `.claude/CLAUDE.md` and written to project memory
and the memory template.

**Sixteen checkers pass, forty-nine proofs hold**, 41 of 41 in the re-aimed housekeeping suite and
4 of 4 in the new one. **Not published** - the cascade is the user's call.
"""

existing = io.open(FINALIZED, encoding="utf-8").read()
if "## Session 2026-10-02 - the queue was eight parts archive" in existing:
    raise SystemExit("entry already present; nothing appended")
io.open(FINALIZED, "w", encoding="utf-8", newline="").write(
    existing.rstrip("\n") + "\n" + ENTRY
)
print("appended session entry, FINALIZED.md now %d lines"
      % len(io.open(FINALIZED, encoding="utf-8").read().split("\n")))
