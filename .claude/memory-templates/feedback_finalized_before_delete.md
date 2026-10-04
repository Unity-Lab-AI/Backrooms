---
name: law-finalized-before-delete-and-a-queue-never-holds-a-completed-item
description: "Never delete a TODO entry until its verbatim text is in FINALIZED.md AND verified. The removal is then MANDATORY — every queue tier carries [ ], [~], [T] only; [x] is transient. Verbatim is proved by a byte-for-byte reassembly identity, never by reading the output."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 50c100e8-42a8-4690-b465-cdc13c066bad
  modified: 2026-10-02T19:44:14.381Z
---

Two rules, and the second was added 2026-10-02. The first governs the ORDER of a removal. The second makes the removal MANDATORY.

**ORDER (absolute):**

1. **Write** the task's verbatim text to `docs/FINALIZED.md` (per [[feedback_law_0_verbatim]] — verbatim, not paraphrased)
2. **Verify** the write succeeded
3. **Then** remove the entry from `docs/TODO.md`

Reverse order = lost work, silently. If FINALIZED is written after the TODO deletion and that write fails, the task disappears with no archive and nobody notices for weeks.

**A QUEUE NEVER HOLDS A COMPLETED ITEM.** Owner direction, verbatim: *"we need to move all finished items to finalized.md from the todo, the todods sahll never hold completed items, they are always to be moved to finalized first then deleted from the todods once confirmed virbatium transfer"*

- Every queue tier — `docs/TODO.md`, `docs/DECOMPOSED.md`, any queue file — carries `[ ]`, `[~]` and `[T]` ONLY. `[x]` is a **transient** state, legal only between finishing a task and archiving it **in the same batch**.
- A `[x]` row left in a queue is a **defect to clear**, not harmless history. At volume it buries what is left.
- `[T]` is NOT finished work. It belongs to the post-completion test phase and never archives on these grounds.
- A section *titled* DONE whose rows are still `[ ]` does **not** move. The title is not the marker; promoting an unticked row invents a closure.
- A closure moves **with its context** — a whole closed section, or a whole owner-direction group whose every row is done, moves intact. Shredding a closure into loose bullets strands the owner's words over empty space, which is itself a LAW #0 problem.

**Why:** corrected across multiple sessions, and the 2026-10-02 instance measured the cost. `docs/TODO.md` held **727 `[x]` rows in 2,716 lines**; archiving 2,039 of them moved the open count from **42 to 79** without closing or opening anything — the old number was counting a prefix of a file nobody could read to the end of. `docs/DECOMPOSED.md` was worse: its heading claimed *"Complete — moved to FINALIZED"* over 56 entries that had **zero** string hits in FINALIZED.md. It asserted a transfer that never happened.

**How to apply:**
- Archive at the end of **every batch that closes rows** — not "eventually", not at a milestone.
- **Prove verbatim, never assert it.** Partition the source file's line indices into kept/moved, assert reassembling the two halves reproduces the original **byte for byte**, write the archive first, confirm every moved line is present, only then rewrite the queue. A failed confirmation restores the archive and leaves the queue untouched.
- In this project: `tools/archive-finished-todo.py` (`--apply`, `--queue <path>`) and `tools/verify-archive-move.py` (re-checks the result independently, five ways).
- Moved rows land in a delimited `archived-queue` region so a checker can tell "archived from the queue" from "never reached the queue" — opposite facts, and the second is still a build failure.
- Full LAW body in `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`. Related: [[feedback_never_delete_todo_info]], [[feedback_docs_before_push]].
