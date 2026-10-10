# -*- coding: utf-8 -*-
"""0.12.69-dev: institutions on every level, loot in all of them, and checker fifteen."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"8E9ACA791C636A9636F3BAACD243DAB78BA720D7A102F250327EC9884089511F"

ENTRY = u"""
---

## Session 2026-10-01 - institutions on every level, and loot in all of them (0.12.69-dev)

**Verbatim user quotes:** *"and facilitys and :\\"buildings and neighboorhoods and complexes and
shools and hospitals and military and storages need loot inside of them too"*; *"get to it"*.

**Files touched:** `Generation/FacilityPlanner.cs`,
`Defs/RimroomsRoomArchetypeDefs/RR_RoomArchetypes.xml`, `tools/check-plant-residue.py` (new,
checker fifteen), all sixteen plant suites, `proof-facilities.py`,
`.local/harness/PlannerProbe/Program.cs`.

**Mod register.** Nothing applied. The facility grouping is our own, and the loot slots name Core's
own thing categories.

### A first level had no institutions, and it is the fourth system found the same way

`FacilityPlanner.Anchors` opened with `coordinate.Depth <= 1` and returned null, so **a first
level had no school, no hospital, no military post and no storage complex** -- only rooms that
each happened to have a bench. The archetypes for all four already existed.

That is the fourth system found gated on the coordinate's own depth rather than on distance from
the arrival, after the archetypes, the inhabitants and the shapes. The rule that replaced it
everywhere else applies here: **distance from the spawn hall counts as depth.** The gate's intent
-- the yellow arrival stays sparse -- is kept and now measured **per room**, through the same
`RoomArchetypeService.EffectiveDepth` every other reader uses, so a room the dressing treats as
deep and the facility planner treats as shallow cannot exist.

**And a complex is allowed to be one.** `MaxRooms` was four, written when a level was a
twenty-four-room line and four rooms was a sixth of it. A braided maze at depth 2 has forty-eight
rooms and the owner asked for *"neighboorhoods and complexes"* by name. Six, with the eligible
share raised from 0.45 to 0.6 -- still under two thirds, because single rooms of their own kind are
what an institution stands out against.

Measured by the probe, which now counts them: **depth 1 forms 2.5 institutions per level with the
largest at six rooms**, rising to 5.0 per level from depth 3. Before this, every depth-1 level
formed **zero**.

### Twelve of sixteen archetypes already held loot. Four held none

The office, the nursery, the gallery and the duplicate. Each has a loot slot now, in the kind a
player would expect to find there, drawn from Core's own categories.

### The facilities proof was a model with no source claims, and it had drifted

`proof-facilities.py` mirrors the planner in Python and carried `MAX_ROOMS = 4` and
`ELIGIBLE_SHARE = 0.45` with a comment saying they *"must mirror FacilityPlanner.EligibleShare
exactly"*. **Nothing checked that they did.** The C# moved to 6 and 0.6 and the proof kept passing,
asserting bounds against its own copy of numbers the code no longer used -- and its summary line
still announced *"bounded 2-4"*.

`proof-coordinate-layout.py` had already written the rule down: *"the model asserts the property,
the source claim asserts the code still computes it. One without the other is exactly the
mention-versus-assertion defect this project keeps meeting."* This proof had the model and none of
the claims. It reads the constants out of `FacilityPlanner.cs` now, and claims the removed gate,
the per-room measurement, and that **every** archetype holds something worth carrying out.

### Checker fifteen, because the restore cannot survive being killed

**A plant suite left a deliberate fault in the working tree for the third time** -- this run it was
`!anchor.Destroyed` deleted out of `RimroomsPortalNetwork.cs`, found by a proof refusing rather
than by anybody looking. The sweep had been interrupted between the plant and the restore.

The `finally` added earlier handles an exception and does nothing for a killed process. So every
suite now writes `.local/register/.plant-in-progress` naming the file and the plant before it
mutates anything, and deletes it in the same `finally`. `tools/check-plant-residue.py` refuses
while that sentinel exists and prints the path to restore. **Verified both ways**: clean when
nothing is planted, refusing when something is, and the sentinel is gitignored.

A false alarm costs one command. A missed one ships a deliberate fault.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`8E9ACA791C636A9636F3BAACD243DAB78BA720D7A102F250327EC9884089511F`, measured after the version
bump, reproduced by two clean recompiles. **Fifteen checkers pass, forty-five proofs hold. 611 of
611** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = (u"## The lab name comes out, and every level becomes a maze "
            u"- 2026-10-01 (0.12.68-dev) - PARTLY DONE")
HEAD_NEW = (u"## The lab name comes out, and every level becomes a maze "
            u"- 2026-10-01 (0.12.68-dev, 0.12.69-dev) - DONE")
if todo.count(HEAD_OLD) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(HEAD_OLD))
    raise SystemExit(1)
todo = todo.replace(HEAD_OLD, HEAD_NEW, 1)
LAST = (u'- [~] **"and facilitys and buildings and neighboorhoods and complexes and shools and '
        u'hospitals and\n  military and storages need loot inside of them too"**')
if LAST in todo:
    todo = todo.replace(LAST, LAST.replace(u"- [~]", u"- [x]", 1), 1)
    print("the loot row is closed, every word kept")
else:
    print("NOTE: the loot row was not matched; it keeps its [~] and every word")
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.68-dev**.", u"| Published | **0.12.69-dev**."),
    (u"SHA-256 `298068EE470739CF278A6972F3723770BFE2C1631C9B2386C7D65ADCE9E1076E`",
     u"SHA-256 `" + HASH + u"`"),
    (u"| Checkers | **FOURTEEN**, all passing.",
     u"| Checkers | **FIFTEEN**, all passing. **The fifteenth refuses while a planted fault is "
     u"still in the source tree.** A suite has left one there three times -- twice deleting "
     u"`Campaign.NoteReturnedFromField(...)`, once deleting `!anchor.Destroyed` -- and each would "
     u"have shipped silently if a build had gone out first. The `finally` added at 0.12.65-dev "
     u"handles an exception and does nothing for a killed process, so the suites write a sentinel "
     u"naming the file before they mutate it and `check-plant-residue.py` refuses while it "
     u"exists. **A false alarm costs one command; a missed one ships a deliberate fault.**"),
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
print("NOW.md updated for 0.12.69-dev")
