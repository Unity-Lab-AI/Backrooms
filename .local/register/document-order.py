# -*- coding: utf-8 -*-
"""The definitive order of operations, in the owner's words, where it cannot be missed.

> *"and dont forget to stage , now.md , then cascade"*
> *"thats the definiative order of operation(remember it and document)"*

**STAGE, then NOW.md, then CASCADE.** Written into `docs/NOW.md` at the top of the handoff and into
`AGENTS.md` beside the build rules, because the reason for that order is not obvious and getting
it wrong wastes the owner's time:

  * **Stage first** so the owner can start playing the moment the work is done, rather than
    waiting on documentation they are not reading yet.
  * **NOW.md second** so the handoff records the version that is actually in the game folder --
    written after the stage, it can quote a verified hash instead of an intended one.
  * **Cascade last** so the published commit contains the handoff. A cascade before NOW.md
    publishes a tree whose own notes are out of date, and then needs a second cascade to fix it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")
AGENTS = os.path.join(REPO, "AGENTS.md")

ORDER = u"""## THE ORDER OF OPERATIONS, AND IT IS THE OWNER'S

> *"and dont forget to stage , now.md , then cascade"* — *"thats the definiative order of
> operation(remember it and document)"*, 2026-10-01

**STAGE → NOW.md → CASCADE.** In that order, every time, once the work and the battery are done.

| # | Step | Why it is here and not later |
|---|---|---|
| 1 | `tools/stage-mod.ps1 -UpdateExisting` | The owner can start playing the moment the work is done, instead of waiting on documentation they are not reading yet. Staging also refuses while RimWorld runs, so it is the step most likely to need attention. |
| 2 | Write `docs/NOW.md` | Written **after** the stage, the handoff can quote the hash and version **verified in the game folder** rather than the one that was intended. |
| 3 | Commit, then cascade ten refs | Last, so the published commit **contains** the handoff. Cascading before NOW.md publishes a tree whose own notes are out of date and needs a second cascade to correct it. |

**The read-back is the only receipt**, and it is ten refs: `feature/bug-testing`,
`feature/connected-colony-portals`, `Prep`, `Develop`, `Main`, on both `forgejo` and `github`.

"""

text = io.open(NOW, encoding="utf-8").read()
ANCHOR = u"## DO THIS FIRST — THE PACKAGE ID CHANGED, AND EIGHT CHECKPOINTS SHIPPED UNVERIFIED"
if text.count(ANCHOR) != 1:
    print("NOW ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ORDER + ANCHOR, 1))
print("NOW.md leads with the order of operations")

agents = io.open(AGENTS, encoding="utf-8").read()
A_ANCHOR = u"The package title must be `Rimrooms - Async Industries`"
if agents.count(A_ANCHOR) != 1:
    print("AGENTS ANCHOR PROBLEM: %d" % agents.count(A_ANCHOR))
    raise SystemExit(1)
A_NEW = (u"**Order of operations when work is finished: STAGE, then write `docs/NOW.md`, then "
         u"commit and cascade.** Owner direction, 2026-10-01, verbatim: *\"and dont forget to "
         u"stage , now.md , then cascade\"*, *\"thats the definiative order of operation(remember "
         u"it and document)\"*. Stage first so play can begin immediately; NOW.md second so the "
         u"handoff quotes a hash verified in the game folder rather than an intended one; cascade "
         u"last so the published commit contains the handoff. The read-back of all ten refs is "
         u"the only receipt.\n\n" + A_ANCHOR)
io.open(AGENTS, "w", encoding="utf-8", newline="").write(agents.replace(A_ANCHOR, A_NEW, 1))
print("AGENTS.md records it beside the build rules")
