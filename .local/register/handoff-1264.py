# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.64-dev, written for the thirteenth launch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## DO THIS FIRST — READ THE **FIRST** RED LINE, NOT THE LOUDEST ONE"

NEW = u"""## THE OWNER IS RIGHT: THE NINTH LAUNCH WORKED AND EVERY FAILURE SINCE IS OURS

> *"what happened it used to work fine until we reformulated the back rooms seed genrations. you
> do remmeber when it was working and i said i loved the backrooms"*

**Yes. Three launches lost, three different causes, one chain**, and all three were introduced by
the generation work that followed the launch that worked:

| Launch | Threw | Where |
|---|---|---|
| 10th | no candidate layout was legal | `MaxRoomSpan` 34 vs an 80-cell hall |
| 11th | a second stool had nowhere to go | `Place` demanded a walkable margin |
| 12th | Core's power rebuild | a duplicate transmitter on one cell |

**Each fix was correct and the next thing in the same method threw instead.** That is the real
lesson of this run: the failures were not one bug, they were one *structure*.

### THE STRUCTURE, AND IT IS STILL THERE

`parent.MarkLayoutReady(...)` — the call that gives `SoloGroupOpening` its threshold anchor — is
**the last line of `GenStep.Generate`.** Everything before it can abort the gate: the shell, the
power grid, the lamps, the content, the validation, the bodies, the odd-origin pass. **Three
separate phases have now done exactly that**, and a light count did it for thirty-nine checkpoints
before them.

**So the question to ask of any new generation phase is: can this throw, and should a coordinate
cease to exist because it did?** The answer is almost always no. The project had already written
the rule down, about the power validation:

> *"A coordinate whose heater or one lamp failed to join the grid is dark and cold and completely
> playable. A coordinate that does not exist costs the player the gate that leads to it."*

The validation honoured it. **The rebuild it validates did not, and neither did the furniture.**

### WHAT THE OWNER WILL SEE, AND WHY A NEW START IS NEEDED AGAIN

Core creates the map **before** our GenStep runs, so an aborted GenStep leaves a map that is
visible on the colony bar and unfinished — which is exactly *"i currently see the backrooms is
available but i cant get my pawns to it"*. The coordinate is then recorded, and `EnsureSite`
refuses to rebuild a map for a coordinate whose rooms are already surveyed, because that rule is
what stops a broken reference replacing a place somebody explored.

`SoloGroupOpening.Open` is idempotent and would finish the job, but **it is only ever called from
`ScenPart_RimroomsStart`, so there is no retry surface.** If a fourth launch fails, building one is
worth more than another fix.

### BEFORE ASKING FOR A LAUNCH

```
python tools/check-planner-layouts.py     # checker 14: runs the planner for real
```

And read the log in this order: **`Player.log`, grep the FIRST `[Rimrooms]` line**, then
`python .local/qa/bridge.py call rimworld/list_letters '{}'`. The eleventh launch's log had
hundreds of red lines and every one was downstream of the first. The tenth had **none at all** and
the answer was in a letter.

### WHAT THE THIRTEENTH LAUNCH HAS TO SETTLE

1. **Does the GenStep finish** — no `[Rimrooms][Generation] ... stopped` line at all
2. **Gate blue, glow, Stargate FX, a pawn crossing**
3. **24 rooms at depth 1** plus one grand hall of eighty cells, back-to-back pairs, shaped
   corners, varied corridors; is it a maze; does the yellow stop a few rooms out
4. **Two portals per level** — one world exit, one deeper. Guaranteed, not drawn
5. **Loot, weird rooms, people, bodies, events** out past the yellow rooms
6. **A lamp on every pillar** in four tones; **doors that go nowhere**; **furniture spread
   through rooms**

A `[Rimrooms][Generation] Coordinate ... could not rebuild its power connections` warning is now
**acceptable**: the space, its gate and its way home are unaffected and the level still finishes.
It should not appear, because the conduits are laid last now — but it is a warning, not a failure.

### THE TRAPS FROM THIS RUN

* **An anchored span is a delete.** A fix script rebuilt a proof as
  `text[:start] + new + text[end:]` and removed two claims written minutes earlier. The plant
  suite caught both. **Read what is between the anchors.**
* **The machinery is not the behaviour.** A claim asserted a fallback variable and its return; a
  plant restoring the hard `continue` left all of it unreached and passed.
* **A claim that pins call text proves a call happened, not that it was legal.**
* **An absence claim cannot read raw source** — it reads the comment explaining the removal.
  `proof-coordinate-layout.py` keeps a `code()` view; `proof-generation-batch.py` strips comments.
* **Use the Write tool.** A heredoc mangled an escaped newline for the **eleventh** time.

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for the thirteenth launch")
