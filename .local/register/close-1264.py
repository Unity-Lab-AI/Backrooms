# -*- coding: utf-8 -*-
"""0.12.64-dev: the conduits were laid before anything needed them."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"29933F471C7631CCCA650E6246A6E09DBF63946C406FD055775A56658BAF5A8B"

TODO_ENTRY = u"""
## The twelfth launch: the gate again, and the cause again upstream - 2026-10-01 (0.12.64-dev) - DONE

Owner, verbatim:

> **"okay im getting worried, there still is not correctly the blue aura, the door isnt blue, and
> its not portaling people to the backrooms... what happened it used to work fine until we
> reformulated the back rooms seed genrations. you do remmeber when it was working and i said i
> loved the backrooms... i currently see the backrooms is available but i cant get my pawns to it
> as the door is just a normal door not corrtly the natural gate it should and shall be"**

- [x] **"there still is not correctly the blue aura, the door isnt blue"** - the coordinate's
  generation aborted again, so the door was never marked and no edge was registered
- [x] **"its not portaling people to the backrooms"** - same cause: no registered edge means no
  crossing is ever offered
- [x] **"what happened it used to work fine until we reformulated the back rooms seed
  genrations"** - **the owner is right.** The ninth launch worked. Every failure since has been a
  consequence of the generation work that followed it
- [x] **"i currently see the backrooms is available but i cant get my pawns to it"** - the map is
  created by Core before our GenStep runs, so an aborted GenStep leaves a visible, unfinished map
- [x] **"the door is just a normal door not corrtly the natural gate it should and shall be"** -
  `IsLiveGate` requires a mark AND a registered edge; the door itself was never at fault

---
"""

ENTRY = u"""
---

## Session 2026-10-01 - the conduits were laid before anything needed them (0.12.64-dev)

**Verbatim user quotes:** *"okay im getting worried, there still is not correctly the blue aura,
the door isnt blue, and its not portaling people to the backrooms... what happened it used to work
fine until we reformulated the back rooms seed genrations. you do remmeber when it was working and
i said i loved the backrooms... i currently see the backrooms is available but i cant get my pawns
to it as the door is just a normal door not corrtly the natural gate it should and shall be"*.

**Files touched:** `Generation/GenStep_BackroomsDestination.cs`,
`.local/register/proof-generation-batch.py`, `.local/register/plant-generation.py`.

**Mod register.** The same power rows as 0.12.63-dev, and this time the interaction is the whole
defect rather than a side effect. Their mods are untouched: the fix is entirely in **when** this
generator lays its own conduits.

**Closure notes.** **The owner is right, and it is worth writing down plainly: the ninth launch
worked, and every failure since has been a consequence of the generation work that followed it.**
Three launches, three different causes, one chain. The furniture fix held -- that throw is gone --
and the next thing in the same method threw instead.

```
[Rimrooms][Generation] Site layout stopped: NullReferenceException
  at PowerConnectionMaker.TryConnectToAnyPowerNet
  at PowerNetManager.UpdatePowerNetsAndConnections_First
  at GenStep_BackroomsDestination.Generate
```

**The conduit guard added last checkpoint was correct and ran too early to see anything.**
`SpawnNativePowerNetwork` was the **first** thing in the generator -- before the generator
building, the climate unit, the ceiling lights and the pillar lamps were spawned. So conduits went
down on empty cells and then **every powered building in the coordinate was spawned on top of
one.** Several mods in the owner's profile attach a hidden conduit under a powered building
automatically, so that is a second transmitter on a cell that already held ours, on every one of
those cells.

Core refuses the second -- *"there can't be two transmitters on the same cell"* -- and leaves its
own bookkeeping inconsistent, so the rebuild threw. **The order is the fix.** Wiring last is what
lets `AlreadyTransmits` answer truthfully, and nothing between the old position and the new one
reads the grid: a conduit is not an edifice and does not block standability, so no placement
decision above it changes. It is also the direction this generator had already moved once --
`ConnectStrayConsumers` exists precisely because pre-wiring rooms on the chance something would
land in them was the wrong shape.

**And the deeper defect, which is why this was the third launch lost to the same chain.**
`MarkLayoutReady` -- the call that gives `SoloGroupOpening` its threshold anchor -- is the **last
line** of `Generate`. Every phase before it could abort the gate, and three different phases did:
a light count for thirty-nine checkpoints, a stool, and a power net. The rebuild calls were bare
`map.powerNetManager.UpdatePowerNetsAndConnections_First()` in three places, and **the decision
had already been made twelve lines below them**, about the validation of that very grid: *"A
coordinate whose heater or one lamp failed to join the grid is dark and cold and completely
playable. A coordinate that does not exist costs the player the gate that leads to it."* The
validation honoured it; the rebuild it validates did not. All three now go through
`RebuildPowerNets`, which logs and continues.

**So there are two independent guarantees now:** the duplicate should not occur, and if it occurs
anyway it cannot cost the coordinate.

**`SpawnNativeConduit` is deleted.** It had **no callers** and threw
`RR_Generation_ContentPlacementFailed` on a cell that could not take a conduit -- the exact
behaviour this checkpoint removed everywhere else. Two existing claims refused its deletion
because they counted its call sites, and **a claim that counts call sites refusing a correctly
deleted one is the claim working**; both were updated rather than relaxed.

**The owner's existing save cannot be salvaged, and the reason is deliberate.** The coordinate was
generated and recorded, and `EnsureSite` refuses to rebuild a map for a coordinate whose rooms are
already surveyed -- that rule is what stops a broken reference replacing an explored place.
`SoloGroupOpening.Open` is idempotent and would finish the job, but it is only ever called from
`ScenPart_RimroomsStart`, so there is no retry surface. **A new start is required, for the third
time.**

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`29933F471C7631CCCA650E6246A6E09DBF63946C406FD055775A56658BAF5A8B`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 570 of
570** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"\n## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    todo.replace(ANCHOR, TODO_ENTRY + ANCHOR, 1))
print("TODO row added and closed, owner words verbatim")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.63-dev**.", u"| Published | **0.12.64-dev**."),
    (u"SHA-256 `B61001A7DB056FC142650421231773F757A41297AE9BD294AB5EC7CECA423193`",
     u"SHA-256 `" + HASH + u"`"),
]
problems = []
for old, _ in NOW_EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in NOW_EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.64-dev")
