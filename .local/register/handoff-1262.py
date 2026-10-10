# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.62-dev, written for the eleventh launch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## DO THIS FIRST — READ THE LOG FROM THE TENTH LAUNCH"

NEW = u"""## DO THIS FIRST — READ THE LOG FROM THE ELEVENTH LAUNCH, AND THEN READ THE LETTERS

**The log was CLEAN and the game was broken.** That is the single most useful thing the tenth
launch taught, and it changes the first job.

Zero red lines. `0.12.61-dev` loaded, the mod's own build line printed, the company branch
initialised, no exception anywhere. And the owner had no Backrooms, no blue door and no way
through. **The evidence was a letter**, sitting unread on their screen:

```
The company could not finish startup:
No safe first-site layout was found within the bounded attempt limit.
```

So: **`Player.log` first, and then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.**
A refusal this package produces on purpose is a letter, not an error -- it is written that way
deliberately -- so a clean log says nothing about whether anything worked.

### WHAT BROKE IT, AND IT WAS OURS, FROM THE CHECKPOINT BEFORE

`ValidateRooms` refuses any room wider than `MaxRoomSpan`, which computed the span of a room
filling **one** slot: 34 cells. 0.12.61-dev gave the threshold a grand hall spanning **two**
slots: 80. Candidates 0, 1 and 2 all carry the hall, so **all three were refused every single
time**, and the fallback was refused whenever any room's span varied upward -- which over twenty
rooms is always.

`SoloGroupOpening.Open` is five steps in order and the coordinate is step 2. **Step 3 marks the
door and step 4 registers the edge, and `IsLiveGate` needs both.** So one failure produced every
symptom the owner reported, and none of them were about the door.

### THE INSTRUMENT THAT CAME OUT OF IT -- USE IT BEFORE ASKING FOR A LAUNCH

```
python tools/check-planner-layouts.py
```

**Checker fourteen, and the only one in the battery that runs code rather than reading it.** It
builds `.local/harness/PlannerProbe` against the compiled assembly and runs the real
`TrySelect` and `ValidateRooms` over 200 seeds at seven depth bands.

Thirteen checkers, forty-five proofs and five hundred and fifty planted faults **all passed over a
planner that could not produce one valid layout.** They read source text, and two numbers in two
files disagreeing is not a thing source text shows. **The planner is pure -- no map, no world, no
defs, no global random -- so this was always answerable at the desk, and for a whole checkpoint
nobody asked.**

It demands two things, and the second matters as much as the first: that a layout is accepted,
**and that back-to-back pairs actually exist.** A plant that reverted one `+ 1` was missed by all
forty-five proofs, because the new revert guard caught the resulting overlap and put the room back
-- so every layout stayed valid and the feature was simply **never produced again.** Switched off,
silently, with every claim still passing. That is this project's dominant defect class and the
probe is the answer to it.

**Anything else that is pure and has a validator deserves the same treatment.** The content
builder, the frontier draw and the archetype selector are all candidates.

### WHAT THE ELEVENTH LAUNCH HAS TO SETTLE

**Everything the tenth was supposed to settle, because it never generated a level.** In order:

1. **Does a coordinate generate at all** -- the gate blue, the Backrooms map present, a pawn able
   to cross. **Everything below depends on this.**
2. **24 rooms at depth 1** plus one grand hall of eighty cells, back-to-back pairs, shaped
   corners, varied corridors
3. **Is it a maze** -- branches off three slots in four, dead ends, rooms of different sizes
4. **Is the spawn hall still grand and yellow**, and does the yellow stop a few rooms out
5. **Two portals per level**: one out to the world map, one deeper. Guaranteed, not drawn
6. **Loot, weird rooms, people, bodies, events** -- out past the yellow rooms
7. **A lamp on every pillar**, in four tones, the dim one dim rather than off
8. **Doors that go nowhere** -- an opening a third along a blank wall, onto rock
9. **Furniture spread through rooms** rather than in the four corners

### THINGS THAT WILL WASTE A LAUNCH IF FORGOTTEN

* **The owner's existing save still will not change.** A coordinate is generated once and
  recorded, and the one in their current game was never generated at all -- it failed. **A new
  start is what shows this work.** The branch that failed startup keeps its failure.
* **`GuaranteedFrontiers` and `RoomArchetypeService` hold caches of live `Thing`s and link
  graphs**, cleared in `BackroomsContainment.FinalizeInit`.
* **Register row [218] Stargates! is stance "No integration", and the owner overruled it.** The
  register is guidance. Their component rides an ordinary Core door, their mod is untouched, and
  the build has no reference to their assembly.

### THE TRAP, UPDATED

**A claim that pins call text proves a call happened. It cannot prove the call was legal.**
`PushAgainst(rooms[rooms.Count - 1], rooms[host])` was pinned as literal text and held while two
of that method's four branches produced a layout the validator refuses outright.

And **an absence claim cannot read raw source**: `"a.maxX == b.minX" not in planner` failed
against correct code because the comment explaining why that test is wrong quotes it. Thirty-sixth
instance of that one class. `proof-coordinate-layout.py` keeps a comment-free `code()` view now
and every absence claim reads that.

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for the eleventh launch")
