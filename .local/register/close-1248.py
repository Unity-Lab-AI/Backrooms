# -*- coding: utf-8 -*-
"""0.12.48-dev: TODO rows (opened and closed), FINALIZED entry, NOW.md state."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

# ------------------------------------------------------------------ TODO
todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
ROW = u"""## Fifth launch findings — 2026-09-30

Owner, verbatim: **"okay check it the store and pawns are there now but i dont see a natural gate
thats suppose to be on the back wall of one of the storage rooms so that they can eneter theri
300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels with
thir natual gate spawns to different levels within"**

- [x] **"the store and pawns are there now"** — **0.12.47-dev confirmed by the owner and measured live.** `get_cell_info` at (133, 135) returns a granite-block `Wall` on Concrete where a Granite `Mineable` stood before the burn. The burn and the arrival fallback both hold.

- [x] **"i dont see a natural gate thats suppose to be on the back wall of one of the storage rooms"** — **FIXED 0.12.48-dev. The door was always there; it was never marked.** Measured live: (160, 161) holds a steel `RimWorld.Building_Door` with its emergence gizmo **"Mark as way home" enabled**. `SoloGroupOpening.Open` runs coordinate → site → mark the door → register the connection, and **step 2 failed**, so the marking and the registration never happened.

  The site failed in `ValidateNativePowerNetwork`, which required `count(def == lightDef)` to equal `Rooms.Count + Rooms.Count(service_passage or utility_room)`. The extra lamps in that sum are `RoomContentBuilder`'s hard-coded **`StandingLamp`**; `BackroomsPalette` switched `lightDef` to **`WallLamp`** at **0.7.8-dev**. `climateRoom` guarantees at least one such room exists, so the shortfall was arithmetic, not chance: **no Backrooms coordinate could generate for thirty-nine checkpoints**, and no proof caught it because they read source text and nothing had ever run the generator.

  The validator now checks the lights **actually placed** and sweeps **every `CompPowerTrader` on the map** — it names no def and predicts no count. And a power fault is **reported, never fatal**: a dark, cold coordinate is playable, a missing one costs the player the gate. `ValidatePlacedLayout` stays fatal. Record `implementation/NATURAL_GATE_UNBLOCKED_IMPLEMENTATION.md`, **28 of 28** plants caught.

- [x] **the wall lamp was hanging in mid-floor** — same root. `WallLamp` draws with `drawOffsetNorth (0,0,0.9)`, into the wall it mounts on. `FindWallAttachmentCell` now returns an interior cell with the room's **own wall def** behind it and the `Rot4` facing it, branching on `lightDef.building.isAttachment` rather than the def name, and returning `IntVec3.Invalid` rather than throwing when a small room has nowhere to mount.

- [x] **"make sure to push to both remotes too i need someone else to work on this in parrellel through git hub and i need to make sure they have it all but the temp stuff i told you to git ignore"** — **DONE, and it found a real gap.** `.local/` was hiding the **40 proofs and 11 plant suites**, so a clone could run the 13 checkers and nothing else. `.gitignore` now admits exactly `.local/register/proof-*.py` and `.local/register/plant-*.py` — measured **51 newly tracked files, exactly 40 proofs and 11 plants**. Still excluded: a 132 MB nuget cache, 19 MB of decompiler binaries, the per-subsystem inspections, the scratch bridge client and the one-shot record scripts. A collaborator needs the same RimWorld install: `build.ps1` refuses any Core assembly that does not hash to the reviewed target.

- [x] **`NaturalFrontierService` reported as orphaned — WRONG, and the correction belongs on the record.** The grep excluded the file holding the caller, and the caller is a `JobDriver` in that same file. Verified end to end: `WorkGiverDef RR_SurveyFrontier` → `WorkGiver_SurveyFrontier` → `JobDef RR_SurveyFrontier` → `JobDriver` → `NaturalFrontierService.Discover`. `check-wiring.py` was right. **The onward-gate machinery exists and is reachable; the only thing blocking it was that no level could generate.**

- [ ] **"theri 300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels with thir natual gate spawns to different levels within"** — **OPEN, and fully specified by the owner across four questions this checkpoint.** Levels become **300×300** (from 60×60); **60–100 rooms** in a dense warren on a **10×10** planning grid at the existing 19-cell spacing; **threshold_room / office_copy / return_gallery stay unique**, the other five families **repeat**, and **new structural families** are authored (flooded_room, stairwell, dead_end, pillar_hall) — **layout and dressing only, no new ThingDefs**; **4–6 onward gates per level**, one per ~15 rooms, with `MaximumNaturalDepth` **3 → 6**; and a **fresh save**, dropping the 60×60 path entirely for one shape, the simplest code and the cleanest proofs.

---

"""
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

# ------------------------------------------------------------------ FINALIZED, written first
ENTRY = u"""
---

## Session 2026-09-30 - a light count took every Backrooms level down (0.12.48-dev)

**Verbatim user quote:** *"okay check it the store and pawns are there now but i dont see a natural
gate thats suppose to be on the back wall of one of the storage rooms so that they can eneter theri
300x300 gate ie the stargate mode that prcedurally generated the backrooms of diffent levels with
thir natual gate spawns to different levels within"*

**Verbatim user quote:** *"kill it again when rimsort is ready for m,e and u are done checking the
old runtime test"*

**Verbatim user quote:** *"make sure to push to both remotes too i need someone else to work on this
in parrellel through git hub and i need to make sure they have it all but the temp stuff i told you
to git ignore"*

**Files touched:** `src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs`,
`.gitignore`, `Mod/Rimrooms - Async Industries/About/About.xml`,
`src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj`, `README.md`,
`docs/implementation/NATURAL_GATE_UNBLOCKED_IMPLEMENTATION.md`, `docs/TODO.md`, `docs/NOW.md`,
plus **51 newly tracked verification scripts** under `.local/register/`.

**Closure notes.** **The most expensive defect this project has had, and the cheapest to state.**
`ValidateNativePowerNetwork` counted things whose `def == lightDef` and required the total to equal
`Rooms.Count + Rooms.Count(service_passage or utility_room)`. The extra lamps in that formula are
`RoomContentBuilder`'s hard-coded `StandingLamp`; `BackroomsPalette` switched `lightDef` to
`WallLamp` at **0.7.8-dev**. `climateRoom` guarantees at least one service_passage or utility_room,
so the shortfall was **arithmetic, not chance**: from 0.7.8-dev to 0.12.47-dev **no Backrooms
coordinate could generate**, and no proof saw it because they read source text and nothing had ever
run the generator until a player reached a gate. A comment three hundred lines away proves the
author knew RoomContentBuilder adds another lamp — **the coupling was by count, and a count cannot
notice that the thing being counted changed identity.**

**The door was always there.** Read live from the owner's process: (160, 161) holds a steel
`Building_Door` whose emergence gizmo **"Mark as way home" is enabled**, and `mapCount` was **2** —
the level had been created. `SoloGroupOpening.Open` stops at step 2 when the site fails, so the
marking and the connection never happened. The same reads confirmed 0.12.47-dev: a granite-block
`Wall` now stands where a Granite `Mineable` stood.

**The fix stops predicting and starts observing.** The validator takes the lights the caller
actually spawned and sweeps **every `CompPowerTrader` on the map** — no def named, no count
predicted, so a lamp any other code adds later is covered automatically. And it is **reported, never
fatal**: a dark, cold coordinate is playable; a missing one costs the player the gate.
`ValidatePlacedLayout` stays fatal, because a coordinate you cannot walk through really is broken.

**The lamp was in the wrong place for the same reason.** `WallLamp` draws with
`drawOffsetNorth (0,0,0.9)`, into the wall it mounts on, and was being placed mid-floor.
`FindWallAttachmentCell` mounts it on the room's own wall def with the facing rotation, branches on
`lightDef.building.isAttachment` rather than the def name, and returns `IntVec3.Invalid` rather
than throwing.

**A correction, stated plainly.** `NaturalFrontierService` was reported mid-investigation as
orphaned. That was wrong, and the mistake was in the search: the grep excluded the file holding the
caller, a `JobDriver` in that same file. `check-wiring.py` was right. The whole chain was then
verified end to end.

**The collaborator gap was real.** `.local/` hid the **40 proofs and 11 plant suites**, so a clone
could run the 13 checkers and nothing else. `.gitignore` now admits exactly those two globs —
measured 51 newly tracked files — while still excluding a 132 MB nuget cache, 19 MB of binaries,
the per-subsystem inspections and the one-shot scripts.

**A plant walked past the first version of the fatality claim.** Inserting a `throw` inside
`if (powerFault != null)` did not disturb `Log.Warning` or the condition, and the claim asserted
only that both were present. **A claim that a warning exists is not a claim that a throw does not**
— sixth time this shape has defeated a claim here. Fixed by reading the block body on its own.

**199 C# files, 90 package files**, zero warnings, zero errors. Assembly SHA-256
`D0441DC4DA5D1255362FA5D81865561A50C134984519E69E26739FB00508BEA4`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty proofs hold.** 28 of 28 plants in the generation suite,
56 of 56 in start placement. Record:
`implementation/NATURAL_GATE_UNBLOCKED_IMPLEMENTATION.md`.

**Five launches, eleven defects, every one ours. Still not a single mod conflict.**

**Owner decisions taken this checkpoint, for the queued 300x300 warren:** levels **300x300**;
**60-100 rooms** on a 10x10 grid at 19-cell spacing; threshold/office/return **unique**, the other
five **repeating**, plus **new structural families** (flooded_room, stairwell, dead_end,
pillar_hall) that are layout and dressing only with **no new ThingDefs**; **4-6 onward gates** per
level and `MaximumNaturalDepth` **3 to 6**; **fresh save**, the 60x60 path dropped.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED entry written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("fifth-launch rows recorded")

# ------------------------------------------------------------------ NOW.md
now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.47-dev**.", u"| Published | **0.12.48-dev**."),
    (u"SHA-256 `85B6769552B8D94641A5DA8B93BB9514715FE90AE9087BC0106C528F60ECE540`",
     u"SHA-256 `D0441DC4DA5D1255362FA5D81865561A50C134984519E69E26739FB00508BEA4`"),
    (u"| Game launches | **FOUR, all by the owner on 2026-09-30.** They have found **ten "
     u"defects** and every one was ours.",
     u"| Game launches | **FIVE, all by the owner on 2026-09-30.** They have found **eleven "
     u"defects** and every one was ours. **The fifth found the most expensive one in the "
     u"project's history: a light count that had stopped every Backrooms level from generating "
     u"since 0.7.8-dev, thirty-nine checkpoints.**"),
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
print("NOW.md updated for 0.12.48-dev")
