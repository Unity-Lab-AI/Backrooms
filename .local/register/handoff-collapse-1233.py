# -*- coding: utf-8 -*-
"""Collapse eight per-checkpoint "Done" sections that had accumulated in NOW.md.

The handoff protocol's whole point is that a post-compaction session reads this file to **act**, not
to catch up. Eight `## Done, 0.12.xx` sections had piled up between the next task and the queue --
about 250 lines of history standing between a fresh session and the work.

Every one of them is already summarised in the session table further down and recorded in full in
its own `docs/implementation/` record, which is the permanent home. So they go, and the table gains
nothing because it already has a row for each.

Also corrected: the staging note said 0.12.26-dev, which was true when written and is two
checkpoints stale now, and the "IS IT DONE" section duplicated the rewritten queue.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()

# ------------------------------------------------------------------ drop the eight Done sections
removed = 0
while True:
    match = re.search(r'\n## Done, 0\.12\.\d+-dev[^\n]*\n', s)
    if match is None:
        break
    start = match.start()
    # Runs to the next top-level heading.
    nxt = s.find('\n## ', start + 1)
    assert nxt > start, 'a Done section has no following heading'
    s = s[:start] + s[nxt:]
    removed += 1
print('removed %d accumulated Done section(s)' % removed)

# ------------------------------------------------------------------ the "is it done" section
# It answered a question the owner asked directly, and the rewritten queue now carries the same
# figures in more detail. Keep the answer, drop the duplication.
start = s.index(u'## THE ANSWER TO "IS IT DONE"')
end = s.index(u'## DO THIS FIRST')
s = s[:start] + u"""## Is it done? NO, and the shape of what is left

**~21 genuine build items**, measured at 0.12.33-dev, listed in full under **What is left** below.
Plus about **8 rows that cannot close before the game runs once** and **9 the owner excluded**.

Queue, one consistent pattern, command beside the number:

```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 75 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 50 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 457 done
```

**The raw open count overstates.** Rows closed by work that shipped the same day keep their `[ ]`
until somebody flips them, and four separate rows this session turned out to be **already built** —
227 (medical routes), 308 (contradictory accounts), 493 (the recorder fold) and 1266's neighbours.
**Check a row against the code before building for it.** That habit has saved more work this
session than it cost.

### The package is staged, and one checkpoint behind

The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.33-dev**. Re-stage
before any launch:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

It backs up the existing folder, hash-verifies every file against the build manifest, and records
`ProfileChanged = false; GameLaunched = false`. **It never touches the mod list and never starts the
game.** When it was first run this session the staged copy was **0.4.0-dev** — twenty-two
checkpoints stale, so nothing built in this project's history had ever reached the game folder.

---

""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md collapsed: the file now leads with state, then the work')
