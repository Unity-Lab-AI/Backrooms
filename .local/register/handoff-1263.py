# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.63-dev, written for the twelfth launch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## DO THIS FIRST — READ THE LOG FROM THE ELEVENTH LAUNCH, AND THEN READ THE LETTERS"

NEW = u"""## DO THIS FIRST — READ THE **FIRST** RED LINE, NOT THE LOUDEST ONE

The eleventh launch's log had **hundreds** of `NullReferenceException`s, repeating every frame,
from Core's power net and from four different mods' map components. **Every single one was
downstream.** The cause was the first red line in the file and it was ours:

```
[Rimrooms][Generation] Site layout stopped: InvalidOperationException: RR_Generation_NoSafeRoomCell
  at RoomContentBuilder.Place(...)  ->  Populate(...)  ->  GenStep.Generate(...)
```

So the order is: **`Player.log` first, `grep` for the FIRST `[Rimrooms]` line, then
`bridge.py call rimworld/list_letters` for anything this package refused on purpose.** A
half-generated map makes every other mod on it throw, and chasing those is chasing our own
wreckage.

### THE CHAIN, BECAUSE IT WILL REPEAT IN SOME OTHER FORM

A stool had nowhere to go → `Place` threw → `GenStep.Generate` aborted → the map existed but was
never finished → `EnsureSite` reported failure → `SoloGroupOpening` stopped at step 2 → the door
was never marked and no edge was registered → **`IsLiveGate` needs both, so the gate was a plain
door with no glow and no Stargate component.**

**Owner's words were about a door. The defect was in furniture placement.** Twice now the gate has
been reported broken and the cause was two steps upstream in generation. **Check whether the
coordinate finished generating before looking at anything about the door at all.**

### WHAT WAS ACTUALLY WRONG

`Place` required a walkable margin — no edifice within one cell of the footprint — and **a room's
perimeter wall, its pillar lattice, the rock in its shaped corners, the lamp on every pillar and
every fixture already placed are all edifices**, on top of the three-cell route cross `Populate`
reserves. 0.12.61-dev made that reachable by varying room spans and letting shape and lamps run at
depth 1.

Measured, not argued — `python tools/check-planner-layouts.py` reports it per depth:

```
depth 1   tightest margin  43   starved rooms     0
depth 2   tightest margin   0   starved rooms    33
depth 5   tightest margin   0   starved rooms   928
```

The margin is a **preference** now, and **only the landmark is required** — because
`ValidatePlacedLayout` demands exactly one clue per room and the clue IS the landmark. Everything
else is scenery, which is what `DressRoom` four lines below had always said.

### THE ONE MOD INTERACTION IN ELEVEN LAUNCHES

Core refuses a second transmitter on a cell and leaves its bookkeeping inconsistent, so
`PowerConnectionMaker.TryConnectToAnyPowerNet` throws from `FinalizeInit` **and from every Update
for the rest of the session.** `wiredCells` is our own bookkeeping and cannot see a transmitter
another mod put there — and several mods in the owner's profile attach a hidden conduit under a
powered building, which is what the new pillar lamps are. Both conduit paths now ask Core's own
`ThingDef.EverTransmitsPower`.

**Twenty-three defects across eleven launches and this is the first that involved another mod at
all.** Their mod is untouched; we simply decline a cell that is already wired.

### WHAT THE TWELFTH LAUNCH HAS TO SETTLE

1. **Does a coordinate finish generating** — gate blue, glow, Stargate FX, a pawn able to cross
2. **Is the log clean after the first `[Rimrooms]` line** — no power-net spam
3. **24 rooms at depth 1** plus one grand hall of eighty cells, back-to-back pairs, shaped
   corners, varied corridors
4. **Is it a maze**, and does the yellow stop a few rooms out from a still-grand spawn hall
5. **Two portals per level**: one out to the world map, one deeper. Guaranteed, not drawn
6. **Loot, weird rooms, people, bodies, events** out past the yellow rooms
7. **A lamp on every pillar** in four tones; **doors that go nowhere**; **furniture spread
   through rooms** rather than in the four corners

### THINGS THAT WILL WASTE A LAUNCH IF FORGOTTEN

* **A new start, every time.** A coordinate is generated once and recorded, and a branch whose
  startup failed keeps its failure. Three launches in a row have needed a fresh start.
* **Run `tools/check-planner-layouts.py` before asking for a launch.** It is checker fourteen and
  the only one that runs code rather than reading it.
* **Register row [218] Stargates! is stance "No integration", and the owner overruled it.** The
  register is guidance.

### THE TRAPS, ALL FOUR OF THEM, FROM THIS CHECKPOINT ALONE

* **An anchored span is a delete.** A fix script rebuilt a proof as
  `text[:start] + new + text[end:]` and removed two claims written four minutes earlier. The plant
  suite reported both as MISSED. **Read what is between the anchors.**
* **The machinery is not the behaviour.** The margin claim asserted the fallback variable and its
  return; a plant restoring the hard `continue` left all of it in place, unreached, and passed.
  **Fourth time this week.** Assert the branch.
* **An absence claim must be scoped.** `Place(..., "Shelf", ..., 0)` is a substring of
  `service_passage`'s own landmark. Thirty-seventh instance.
* **Use the Write tool.** A heredoc mangled an escaped newline for the **eleventh** time.

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for the twelfth launch")
