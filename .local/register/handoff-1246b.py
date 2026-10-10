# -*- coding: utf-8 -*-
"""The remaining NOW.md state figures for 0.12.46-dev, and the compaction header.

Asserted first, written once.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

EDITS = [
    (u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 42 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 45 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 495 done
```""",
     u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 42 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 45 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 505 done
```"""),

    (u"## Active",
     u"""## Active

**Nothing in flight. Tree clean, everything published, no half-finished task.** Written
deliberately for the session after a compaction.

### The one thing that will go wrong if you skip it

**The cascade is TEN refs, not eight.** Work is on `feature/bug-testing` now. The eight-ref
read-back that was the only publication receipt for forty-five checkpoints is:

```
forgejo, github  x  feature/connected-colony-portals, Prep, Develop, Main
```

and it is now that **plus `feature/bug-testing` on both remotes**. A publish that reads back eight
and stops has left the branch the work is actually on unpublished, silently. **Count the branch
you are on.**

### The second thing

**Use a FILE for any script with escapes or apostrophes, never a bash heredoc.** It mangled
`\\n` into real newlines **five times** in the 0.12.46-dev batch alone, each time producing a
Python syntax error in a proof or plant file that then had to be repaired. It is written down
here because writing it down has not yet been enough."""),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("state figures and compaction header written")
