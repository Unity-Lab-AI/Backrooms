# -*- coding: utf-8 -*-
"""0.12.63-dev: a second stool stopped a level being built."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"B61001A7DB056FC142650421231773F757A41297AE9BD294AB5EC7CECA423193"

TODO_ENTRY = u"""
## The eleventh launch: the map was there and the gate was not - 2026-10-01 (0.12.63-dev) - DONE

Owner, verbatim:

> **"okay i see the backrooms is there but the gate natural door is not. its jsut a normal door no
> blue no blue hue no stargate fx"**

- [x] **"i see the backrooms is there"** - the map was created, then `GenStep.Generate` threw
  partway through content placement, so it was never finished
- [x] **"but the gate natural door is not"** - `EnsureSite` reported the failure, so
  `SoloGroupOpening` stopped before step 3 and the door was never marked
- [x] **"its jsut a normal door no blue no blue hue no stargate fx"** - `IsLiveGate` needs a mark
  AND a registered edge; with neither, the glower stays dark, the tint is never applied and no
  Stargate component is attached

---
"""

ENTRY = u"""
---

## Session 2026-10-01 - a second stool stopped a level being built (0.12.63-dev)

**Verbatim user quotes:** *"okay i see the backrooms is there but the gate natural door is not.
its jsut a normal door no blue no blue hue no stargate fx"*.

**Files touched:** `Generation/RoomContentBuilder.cs`,
`Generation/GenStep_BackroomsDestination.cs`, `.local/harness/PlannerProbe/Program.cs`,
`.local/register/proof-generation-batch.py`, `.local/register/plant-generation.py`.

**Mod register.** Checked `RR-SCEN` and the power rows behind the conduit fix. **One thing
applied, and it is the first mod interaction this project has had in eleven launches**: several
mods in the owner's profile attach a hidden conduit under a powered building automatically, and
the lamps this generator now places on every pillar are powered buildings. The register's standing
instruction for those rows is to preserve their native behaviour, so nothing of theirs is
touched -- our conduit simply refuses a cell that already transmits.

**Closure notes.** **The coordinate generated this time. Then a stool had nowhere to go and took
the level with it.**

The log was not clean this time -- hundreds of red lines -- but every one of them was downstream.
The first entry was the whole story:

```
[Rimrooms][Generation] Site layout stopped: InvalidOperationException: RR_Generation_NoSafeRoomCell
  at RoomContentBuilder.Place(...)
  at RoomContentBuilder.Populate(...)
  at GenStep_BackroomsDestination.Generate(...)
```

`Place` refused any cell whose footprint had an edifice within one -- *"keep a walkable margin
around each fixture"* -- and **a room's own perimeter wall, its pillar lattice, the rock standing
in its shaped corners, the lamp on every pillar and every fixture already placed are all
edifices**, on top of the three-cell route cross that `Populate` reserves outright. A room could
be left with a single placeable cell: the first fixture took it, and the second threw.

**0.12.61-dev is what made that reachable** -- varied room spans, `Derange` cutting hallways at
depth 1, rock in the corners at depth 1, and a lamp on every pillar. The measured pressure is
plain: the probe reports **the tightest room at depth 2 and below has ZERO margined cells**, and
up to **928 rooms per two hundred seeds** have one or none.

The throw reached `Generate`, so the level stopped being built halfway. `EnsureSite` reported
failure, `SoloGroupOpening` never reached step 3, and **`IsLiveGate` needs both a mark and a
registered edge** -- so the door was not blue, had no glow and carried no Stargate component.
Every symptom, from a furniture rule, two steps removed.

**The margin was never what keeps a room walkable.** The reserved route cross is, and it is
reserved separately and unconditionally -- every doorway sits at a wall midpoint, so a clear cross
is a clear walk between any two of them. So the margin is now a **preference**: the first cell
that has one, or the first cell that does not. A fixture with no margin is a fixture against a
wall.

**And only the landmark is required.** `ValidatePlacedLayout` demands exactly one clue per room
and the clue is the landmark, so that one is still refused loudly -- and the probe shows every
room in two hundred seeds at seven depths can take one. The other twelve family fixtures are
scenery, and `DressRoom` four lines below them already said what to do: *"a fixture that will not
fit is skipped, and a room that ends up bare is a bare room. The alternative -- failing
generation because a decorative shelf had nowhere to go -- would take a working coordinate away
from a player over scenery."* **The rule was written down and the code beside it did the
opposite.**

**The power spam was a real second defect, not just debris.** Core refuses a second transmitter on
a cell -- *"there can't be two transmitters on the same cell"* -- and leaves its own bookkeeping
inconsistent, so `PowerConnectionMaker.TryConnectToAnyPowerNet` threw out of `Map.FinalizeInit`
and then out of **every Update for the rest of the session.** `wiredCells` is this generator's own
bookkeeping and cannot see a transmitter somebody else put there. Both conduit paths now ask
Core's own `ThingDef.EverTransmitsPower` about whatever is on the cell -- the same property
`PowerNetManager` registers on, so it cannot disagree with the thing that refuses the duplicate.

**The probe was extended to measure this, and that is the point.** It now counts, per room,
the cells that could hold a landmark and the cells that have a clear margin -- asking the shipping
code for every rule: `PillarCells`, `RockIntrusionCells` and `ShapeDepthOf` from the planner, and
a newly extracted `RoomContentBuilder.OnRouteCross`, so the probe and the generator cannot
disagree about what is reserved.

**Three mistakes of my own, caught by the instruments rather than by a launch.** A fix script
rebuilt a proof as `text[:start] + replacement + text[end:]` and **deleted two claims written four
minutes earlier** -- the plant suite reported both as MISSED immediately. The margin claim
asserted the fallback machinery rather than the branch that uses it, so a plant restoring the hard
`continue` left every asserted line in place and was missed: **computing a value and using it are
two different facts, for the fourth time this week.** And an absence claim named
`Place(..., "Shelf", ..., 0)`, which is a substring of `service_passage`'s own landmark --
thirty-seventh instance of the scoping trap, now scoped to a bare statement.

**A bash heredoc mangled an escaped newline for the eleventh time.** The rule is at the top of
`docs/NOW.md` and writing it down has never been enough; the fix was redone with the Write tool.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`B61001A7DB056FC142650421231773F757A41297AE9BD294AB5EC7CECA423193`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 566 of
566** planted faults caught across sixteen suites.
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
    (u"| Published | **0.12.62-dev**.", u"| Published | **0.12.63-dev**."),
    (u"SHA-256 `5201C4A6D368DE5E2E3A94939BEC0D0AF5858A870A1A05F4AC991F2D94BE8774`",
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
print("NOW.md updated for 0.12.63-dev")
