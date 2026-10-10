# -*- coding: utf-8 -*-
"""Record the FINALIZED ledger-script defect in the 0.11.8 implementation record."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rel = 'docs/implementation/INCIDENT_SURFACE_IMPLEMENTATION.md'
p = os.path.join(REPO, rel)
s = io.open(p, encoding='utf-8').read()

anchor = u'## The heredoc, for the seventh time'
block = u"""## A ledger script ate a heading

While writing this checkpoint's ledger the patch failed on a missing anchor, which is how a
defect in the **0.11.7** ledger script was found.

Its `edit()` helper did `s.replace(anchor, new)` where `new` did **not** re-include the anchor,
so inserting the 0.11.7 entry **consumed** the heading

```
## Inherited pre-workflow history (2026-09-27 → 2026-09-28, previous build agent)
```

and left that whole section headless underneath the new entry.

**`FINALIZED.md` is append-only.** No entry text was lost — only the heading and its
parenthetical — and both are restored verbatim from `HEAD~1`. The check that proves it is a diff
filtered for removed lines, which now returns nothing.

Two things changed as a result:

- Every insertion in the 0.11.8 script uses an `insert_before` helper that **re-includes its
  anchor**, so the same mistake cannot be written again.
- The diff of an append-only file is **checked for removed lines** before the commit, rather than
  trusted because the script printed "updated".

It is invariant 144. The general shape is one this session keeps meeting from different angles:
**a patch that silently succeeds at the wrong thing is worse than one that fails**, and the only
defence is to assert the property rather than the operation.

---

"""

assert anchor in s, 'anchor not found'
assert s.count(anchor) == 1, 'anchor not unique'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ledger defect recorded')
