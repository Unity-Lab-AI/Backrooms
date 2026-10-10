# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.61-dev, written for the tenth launch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## DO THIS FIRST — READ THE LOG FROM THE NEXT LAUNCH"

NEW = u"""## DO THIS FIRST — READ THE LOG FROM THE TENTH LAUNCH

**Read `Player.log` before anything else, and read it before telling the owner anything works.**
Four checkpoints in a row were answered from proofs rather than from a log and four times the
answer was wrong.

### THE NINTH LAUNCH WORKED. THE OWNER WALKED A BACKROOMS LEVEL.

*"okay it fucking worked!!! im in the backrooms!!!"* — first time in nine launches. The coordinate
generated, the gate was blue, the crossing worked, and they explored a whole level.

**And almost everything they found wrong was switched off on purpose.** Three separate systems
carried the same gate, and the defs said so out loud:

```
RR_RoomArchetypes.xml:  "minDepth is what keeps the shallow yellow rooms empty.
                         Nothing here can appear at [depth 1]"
```

All fourteen archetypes were `minDepth >= 2`; every inhabitant family, including the missing
person and the recent dead, was `minDepth >= 2`; every anomaly event was `minDepth >= 2`; and
`RockIntrusionCells`, `CorridorHalfWidthBetween` and `Derange` each refused to run at depth 1.
**A first level had no laboratory, no ward, no storeroom, no loot, no people, no bodies, no
events, no shapes and no varied corridors. It was built to be empty and the owner explored all of
it.**

### THE RULE THAT REPLACED ALL OF THEM

**Distance from the spawn hall counts as depth.** Three links out is one level deeper, capped at
four bands. Near the arrival it is the yellow rooms exactly as before; the further you walk the
more of the existing library the level can reach. **Fourteen archetypes were already written and
the first level could not touch one of them.**

It is the owner's own sentence made literal: *"the normal yellow backrooms look isnt the whole
floor but the main spanw room and going deeping in can mean the numner of branch hallways and
rooms distancing from the main portal spawn"*.

### WHAT THE TENTH LAUNCH HAS TO SETTLE

1. **Does a level still generate at all**, with 24 rooms at depth 1 instead of 9, back-to-back
   pairs, shaped corners and varied corridors. **Everything else depends on this.**
2. **Is it a maze** — branches, dead ends, rooms of different sizes and shapes
3. **Is the spawn hall still grand and yellow**, and does the yellow stop a few rooms out
4. **Two portals per level**: one out to the world map, one deeper. Guaranteed, not drawn
5. **Loot, weird rooms, people, bodies, events** — out past the yellow rooms, not beside the door
6. **A lamp on every pillar**, in four tones, and the dim one dim rather than off
7. **Doors that go nowhere** — an opening a third along a blank wall, onto rock
8. **Furniture spread through rooms** rather than in the four corners

### THINGS THAT WILL WASTE A LAUNCH IF FORGOTTEN

* **The owner's save will not change.** A coordinate is generated once and recorded; everything
  here affects levels generated from now on. A new level, or a new start, is what shows it.
* **`GuaranteedFrontiers` and `RoomArchetypeService` hold caches of live `Thing`s and link
  graphs**, cleared in `BackroomsContainment.FinalizeInit`. If either leaks across a load it
  hands a new game the previous game's doors.
* **Register row [218] Stargates! is stance "No integration", and the owner overruled it.** The
  register is guidance. Their gate component rides an ordinary Core door, their mod is untouched,
  and the build has no reference to their assembly.

### THE TRAP THAT KEEPS COSTING CHECKPOINTS

**Three times in this checkpoint a claim guarded a DEFINITION while a plant deleted the CALL.**
`MakeHall`, `VariedRoomSpan`, `SpawnPillarLamps` — each defined, each correct, each unreached, and
every numeric claim about them still passing. **Computing a value correctly and using it are two
different facts.** Assert the call site.

And nine claims refused these changes outright, every refusal correct. One required depth 1 to be
*"at most eight rooms of at least sixty cells"* — a faithful reading of an earlier direction, and
**the exact claim that produced the nine-room warehouse.** Another caught that the wall-material
gate still tested `coordinate.Depth`, so the per-room material was never reached on the level the
owner actually walked. **A proof refusing a change is the proof working; go back and read what it
was protecting before you edit it.**

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for the tenth launch")
