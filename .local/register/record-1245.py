# -*- coding: utf-8 -*-
"""Record the map-placement and natural-gate fixes, and the glow pod correction."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

todo = io.open(TODO, encoding="utf-8").read()

ANCHOR = u"## TOMBSTONES"

ROWS = u"""## First launch findings, second pass — 2026-09-30

- [x] **"store stare was not the map i chose with the buildings being built there instead i was stuck in a super micro blocked in area AND there wasnt a Backrooms natural Gate for me to enter"** — **BOTH FIXED 0.12.45-dev, and both were exactly as reported.**

  **The mod threw away the chosen map size.** `ScenPart_RimroomsStart` did `Find.GameInitData.mapSize = startDef.mapSize`, forcing **50 for the Store** and 60 for the others — against RimWorld's smallest new-game option of **200**. A 50×50 map is **2,500 cells where a default map is 62,500**, with the shop occupying **41%** of it behind an 8-cell margin. Owner direction: *"the map size is selected on world seteup before world generation by the player and they select the tile they appear in so the store gets genreeate in that selected tiles map"*. It does now: the override is gone, and `HeadquartersLayout` offsets the authored layout onto whatever map exists, centred, clamped so it can never cross an edge. **The defs keep their coordinates** — rewriting ~100 hand-placed cells across three starts would be a large unverifiable diff, and those coordinates encode which room is the stockroom and which door is the back door. On a 250×250 map the shop lands at x 108..141 with about 108 cells of real terrain on every side. **Nothing was ever sealed:** all three layouts flood-fill to **100% reachable** from their arrival cell, which is the measurement that should have existed before any of them shipped and now runs in the proof.

  **The Store had no Backrooms connection of any kind.** `SoloGroupOpening.Open` returned immediately unless `insideStart`, and nothing in the headquarters generator creates a connection, so there was genuinely no door to enter. Owner direction: *"ther is a natural gate that leads to a seeded fixed backrooms and all backrooms have portals that lead deeper and lead to the world maps tiles"* — and **the deeper and world-tile halves already existed**: `NaturalFrontierService` bounds onward ways to two per coordinate at depth ≤ 3, and `RecordWorldExit` already makes a way out lead to a world tile the branch does not hold. **Only the seeding was missing.** Steps 1–4 of `Open` — mint the coordinate, generate its map, mark the named door, register the connection — are exactly what a surface start needs; only step 5, moving the party inside, is specific to beginning in the Backrooms. So **any start that names an `emergenceDoorCell` now begins with a permanently open natural gate**, and the Store names its back-room door at (35, 0, 34). `CONNECTED_COLONY_PORTALS.md` already called *"the starts that begin with only a natural gate"* load-bearing; this is the first time one actually did.

  **The door lookup had to be offset too** — the single easiest thing to miss in the change, since the layout now moves and reading the authored cell would look for a door where no door is. Record `implementation/START_PLACEMENT_IMPLEMENTATION.md`, proof `proof-startplacement.py`, **19 of 19 planted faults caught**.

- [x] **The three glow pods were put in the wrong start at 0.12.44-dev, and pre-placing them was wrong for that start anyway.** They belonged to the **solo/group** scenario, not the Store — whose own note says *"no company kit, no field recorder, no glow pods"*. I read line 135 of `RR_Scenarios.xml` and assumed Store because Store is second in `RR_Starts.xml`; the scenario file's order is Async, Store, Solo. **And the fix itself was wrong for solo:** `SoloGroupOpening` moves that party **inside a coordinate on the first tick**, so anything left standing in the surface shell is abandoned immediately. So the solo three are restored as **carried** starting things and the Store's three are removed. EdB logs its warning for the solo scenario and that is the right trade: **a warning is cheaper than a start whose only light source is left behind.** The Async eight stay pre-placed, because that crew starts on the surface beside them.

---

"""

if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROWS + ANCHOR, 1))
print("second-pass findings recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.44-dev**.", u"| Published | **0.12.45-dev**."),
    (u"SHA-256 `D0EF34D3358A9390E74D5DEA7BB066AB3F8FC27A343AECD35A02009112378F63`",
     u"SHA-256 `B4E57D05F52BCD7947465A34E70834165A5CD23CB25BBE6831EA8DA6586EFFA3`"),
    (u"| Build | **198 C# files, 89 package files**",
     u"| Build | **199 C# files, 89 package files**"),
    (u"| Proofs | **THIRTY-NINE** in `.local/register/proof-*.py`.",
     u"| Proofs | **FORTY** in `.local/register/proof-*.py`."),
    (u"## WHAT THE FIRST LAUNCH FOUND — read this before anything else",
     u"""## WHAT THE FIRST LAUNCH FOUND — read this before anything else

**Second pass, and these two were the worst of the lot.**

**The mod threw away the player's chosen map size.** `Find.GameInitData.mapSize = startDef.mapSize`
forced **50 for the Store** against RimWorld's smallest option of **200** — 2,500 cells where a
default map has 62,500, the shop taking 41% of it. *"Not the map i chose ... a super micro blocked
in area"* was literally accurate. The layout is offset onto the player's own map now, centred and
clamped. **Nothing was ever sealed** — all three layouts flood-fill to 100% reachable, and that
measurement now runs every checkpoint.

**The Store had no Backrooms connection at all.** `SoloGroupOpening` returned early unless
`insideStart`, and nothing in the generator creates one. The **deeper** and **world-tile** halves
the owner described already existed; only the seeding was missing. Any start naming an
`emergenceDoorCell` now begins with a permanently open natural gate.

---

"""),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.45-dev")
