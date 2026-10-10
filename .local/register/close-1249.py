# -*- coding: utf-8 -*-
"""0.12.49-dev closure. Written as a FILE because a heredoc just died on an apostrophe again."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Coordinate rebuild, stage one — 2026-09-30 (0.12.49-dev)

- [x] **300x300 coordinates, grand pillared halls at level zero, and the depth-scaled warren** — **DONE.** The 3x3 eight-slot grid at 19-cell spacing is gone; slots, spacing, room span and room count are all functions of depth. Depth 1 is **6 halls of 80x80 with 144 pillars each**; depth 6 is **42 rooms of 24**. Verified at every depth: nothing off the map, every span even, 10 cells of rock between neighbours, serpentine chain connected. Record `implementation/GRAND_SPACES_IMPLEMENTATION.md`.

- [x] **"u can use walls as pillars"** — **DONE.** Lattice at 6 against Core's `RoofMaxSupportDistance` of 6.9, never on the centre cross, narrowest free run 5 cells. **Decided in `RoomLayoutPlanner.PillarCells` and nowhere else**, because the planner must prove walkability before a map exists, and two independent derivations of one rule is the defect that cost thirty-nine checkpoints.

- [x] **"and remember backrooms can not and shall not have cave ins so removing walls floors columns shall not cause mountain overhead to column collapse"**, scoped by **"tgis is only for backrooms"** — **DONE, and the old code was wrong about this.** `BackroomsContainment` claimed a coordinate could be "mined to nothing and still never open a hole", treating the collapse as acceptable. Core gates cave-ins on `RoofDef.canCollapse`, which **defaults to true and which Core sets false on none of its three roofs**, so `RoofRockThick` drops `CollapsedRocks` and crushes what is under it. A roof def of our own, `RR_RoofBackroomsOverhead`, `canCollapse false`, `isThickRoof true`. **Core's roof is deliberately not patched** — that would stop mountains collapsing in every colony, for every mod in the profile.

- [x] **the coordinate geometry had no proof coverage at all** — **FIXED, and measured rather than guessed: every constant in the planner was changed and all forty existing proofs still passed.** `proof-coordinate-layout.py` is the **41st proof**; it parses the constants out of the C# and recomputes rather than hard-coding them. A plant then found a hole in that design — the model copies the formulas, so deleting an algorithm step was invisible to it — and **every modelled formula is now paired with a source claim**. `plant-coordinate-layout.py` is the 12th suite, **34 of 34**.

- [ ] **"dont let them go more than 5 remember the games mechanics and limits built in if they find a gate to a world map tile or a deeper backrroms and they have 5 mpas they should gett a warning this gate is blocked your holding open too many gates, but per scerio styled"**, clarified by **"5 is the limit of other colonies available so a backrooms level should be one colonly bacskicly in my thinking"** — **OPEN, stage two, and it SUPERSEDES the LRU-eviction answer given minutes earlier.**

  A hard cap with **no eviction** is strictly better: nothing the player looted or built ever resets, memory is bounded by construction, and the limit is **diegetic** rather than an apology about memory.

  **And the owner's clarification grounds the number in Core.** `Prefs.MaxNumberOfPlayerSettlements` is a player option, a slider from **1 to 5, default 5**, enforced by `SettleUtility` as `count >= Prefs.MaxNumberOfPlayerSettlements`. Core counts only `map.IsPlayerHome && map.Parent is Settlement` plus gravship landings, so a `RimroomsDestinationMapParent` is **invisible to it**. So the budget is read from that pref rather than hard-coded, and a coordinate map counts against it — *"a backrooms level should be one colonly bacskicly"*. A player who sets the slider to 3 gets 3.

  *"per scerio styled"* means the budget belongs on the scenario, not a global constant.

  **This ships together with raising onward gates to 4-6 and `MaximumNaturalDepth` 3 to 6**, because the cap without the gates is pointless and the gates without the cap is what kills the game: `RimroomsDestinationMapParent.ShouldRemoveMapNow` always returns false, so at 90,000 cells and ~70,000 mineables per level, hundreds of reachable levels against a `MaximumCoordinates` of 512 would be fatal.

- [ ] **still open from the same direction** — non-rectangular rooms and corridors; and the wild variation of materials across items, equipment, walls, floors, lights, furniture and benches, with the events, layouts and loot deeper in.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - grand spaces, pillars, and no cave-ins (0.12.49-dev)

**Verbatim user quote:** *"and everything doesnt have to be square rooms and rectangle halways and u
can use walls as pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms
and this can propigate depper with the wild variatiosn of material typeds in all items equaipment
walls floors lights furnature and benches that are found everywher deeper in with wild random
events and layouts and spawns to find and loot!!!!!!"*

**Verbatim user quote:** *"and remember backrooms can not and shall not have cave ins so removing
walls floors columns shall not cause mountain overhead to column collapse"*

**Verbatim user quote:** *"tgis is only for backrooms"*

**Verbatim user quote:** *"dont let them go more than 5 remember the games mechanics and limits
built in if they find a gate to a world map tile or a deeper backrroms and they have 5 mpas they
should gett a warning this gate is blocked your holding open too many gates, but per scerio styled"*

**Verbatim user quote:** *"5 is the limit of other colonies available so a backrooms level should be
one colonly bacskicly in my thinking"*

**Files touched:** `src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs` (rewritten),
`DestinationService.cs`, `GenStep_BackroomsDestination.cs`, `BackroomsContainment.cs`,
`Mod/.../1.6/Defs/RoofDefs/RR_Roofs.xml` (new), `tools/package-files.json`, About.xml, the csproj,
`README.md`, `docs/implementation/GRAND_SPACES_IMPLEMENTATION.md`, `docs/TODO.md`, `docs/NOW.md`,
plus the 41st proof and the 12th plant suite.

**Closure notes.** **Stage one of the coordinate rebuild.** Every number in the planner was a
constant; they are all functions of depth now. Depth 1 is **6 halls of 80x80 with 144 pillars
each** - the owner's *"grand large spaces"* - and the room count going DOWN is what pays for it,
which is *"leas than 60-100 romms"* satisfied by construction rather than by a cap. Depth 6 is 42
rooms of 24.

**The pillar lattice lives in exactly one function**, because the planner has to prove a room is
still walkable with the pillars in it before any map exists, and two independent derivations of one
rule is the defect that stopped every coordinate generating for thirty-nine checkpoints one
checkpoint earlier.

**The no-cave-in direction found a real defect in the existing reasoning.** `BackroomsContainment`
argued from `VanishOnCollapse => !isThickRoof` that a coordinate could be "mined to nothing and
still never open a hole in the world", and treated the collapse itself as acceptable. Half right:
no hole opens, but Core gates every cave-in on `RoofDef.canCollapse`, which **defaults to true and
which Core sets false on none of its three roofs** - so thick roof still drops `CollapsedRocks` and
crushes what stands beneath. Fixed with a roof def of our own. **Core's `RoofRockThick` is
deliberately NOT patched**, per the owner's own scoping, because that would stop mountains
collapsing in every colony for every mod in the profile. Every Core behaviour that matters reads
`isThickRoof` rather than the def's identity, which is why a roof of ours behaves identically.

**A blind spot was measured, not guessed.** Every constant in `RoomLayoutPlanner` was changed and
**all forty existing proofs still passed** - a coordinate's geometry had no coverage at all.
`proof-coordinate-layout.py` parses the constants out of the C# and recomputes from them, so it
cannot go stale when one changes. **A plant then found a hole in that design:** the model copies the
formulas while parsing the constants, so deleting `if (span % 2 != 0) { span--; }` walked straight
past the computed evenness claim. Every modelled formula is now paired with a source claim. Two of
the plants were themselves wrong rather than the proof - `Margin = 1` does not push rooms off the
map, because the spacing grows as the margin shrinks and the arithmetic self-corrects.
`proof-interior-resource.py` also objected correctly to the roof change, and now asserts the
property rather than the def name.

**199 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`A17D99ED025EAAA975011D05F588BBB735793165EFF9E8E4881E2A18B26EEB13`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** 34 of 34 in the new suite.

**Needs a fresh save**, by owner decision: one shape, the 60x60 path dropped, `PlannerVersion` 3.

**Held for stage two on purpose:** the raised gate count and depth ship WITH the map cap, because
`ShouldRemoveMapNow` always returns false and a coordinate map is never unloaded. The owner's cap
supersedes their own earlier LRU-eviction answer and is better on every count - and their
clarification grounds it in Core: `Prefs.MaxNumberOfPlayerSettlements` is a 1-to-5 player slider
that Core enforces for settlements but which cannot see a coordinate map, so the budget is read
from the pref and a coordinate counts against it.

**And the heredoc rule in NOW.md earned its place again this checkpoint** - a bash heredoc died on
an apostrophe mid-closure, which is the sixth time in two days. This file exists because of it.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("stage-one rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.48-dev**.", u"| Published | **0.12.49-dev**."),
    (u"SHA-256 `D0441DC4DA5D1255362FA5D81865561A50C134984519E69E26739FB00508BEA4`",
     u"SHA-256 `A17D99ED025EAAA975011D05F588BBB735793165EFF9E8E4881E2A18B26EEB13`"),
    (u"| Build | **199 C# files, 90 package files**",
     u"| Build | **199 C# files, 91 package files**"),
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
print("NOW.md updated for 0.12.49-dev")
