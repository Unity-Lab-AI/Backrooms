# -*- coding: utf-8 -*-
"""0.12.61-dev: the first walked level, and everything that was switched off."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ENTRY = u"""
---

## Session 2026-09-30 - the first walked level (0.12.61-dev)

**Verbatim user quotes:** *"okay it fucking worked!!! im in the backrooms!!! but issues..."*,
*"not enough rooms"*, *"not enough loot"*, *"zero weird events or people"*, *"there were zero
portals to be discovered"*, *"the furnature is only in the four corners of the rooms"*, *"the
normal yellow backrooms look isnt the whole floor but the main spanw room"*, *"it needs to be more
maze liek and scary inducing"*, *"every backrooms instance need a protal to the world map and a
deeper in portal"*, *"we need more lights and mixedered varies of lights ... the basic rooms are
well lit"*, *"you can have back to back roomes and mazes of halways of varied widtchs and lengs
... triangle, octangones, rombones ... doors to now where not just doors on 4 cosides of nothing
but square rooms"*.

**Files touched:** `Generation/RoomLayoutPlanner.cs`, `Generation/RoomContentBuilder.cs`,
`Generation/RoomArchetypeService.cs`, `Generation/GenStep_BackroomsDestination.cs`,
`Generation/CoordinateMaterials.cs`, `Generation/BackroomsContainment.cs`,
`Threats/InhabitantService.cs`, `Threats/AnomalyEventService.cs`,
`Portals/GuaranteedFrontiers.cs` (new), `Portals/NaturalFrontierService.cs`,
`Defs/RimroomsRoomArchetypeDefs/RR_RoomArchetypes.xml`.

**Closure notes.** **The ninth launch worked and the owner walked a level, and almost everything
they found was switched off on purpose.**

Three separate systems carried the same gate. `RR_RoomArchetypes.xml` opens with *"minDepth is
what keeps the shallow yellow rooms empty. Nothing here can appear at [depth 1]"*, and all
fourteen archetypes declare minDepth 2 or more while `Select` refuses depth 1 outright.
`RR_Inhabitants.xml` is the same - every family, including the missing person and the recent
dead. `AnomalyEventService` filters events on `coordinate.Depth` and every event is minDepth 2 or
more. **So a first level had no laboratory, no ward, no storeroom, no salvage, no loot, no people,
no bodies and no events. It was built to be empty, and the owner explored all of it.**

The fix is the owner's own sentence made literal: **distance from the spawn hall counts as
depth.** Three links out is one level deeper, capped at four bands. The yellow rooms stay yellow
near the arrival and the library opens up as you walk. Fourteen archetypes were already written
and the first level could not reach one of them.

**Shape was off the same way.** `RockIntrusionCells` refused depth 1, `CorridorHalfWidthBetween`
returned a constant 2 at depth 1, and `Derange` waited on a content library version. The corner
masses are quarter-ellipses - two adjacent make a trapezoid, two opposite a rhombus, all four an
octagon - and none of it could run. `ShapeDepthOf` answers the same distance question, and the
generator and `CandidateIsSafe` both call it, because a room shaped one way and proved walkable
another is the thirty-nine-checkpoint defect wearing a prettier outline.

**Portals were a one-in-twelve draw and a whole level can roll none**, which is what the owner
walked. `GuaranteedFrontiers` picks two doorways per coordinate from its own seed, skips the
rarity draw and the cap, and has its kind decided rather than drawn: one world exit, one deeper.
Every other rule still applies, because a guarantee that skipped the safety checks would be a bug
with a promise attached.

**Furniture went to the four corners because the code aimed at the four corners** - `preferred`
was one of exactly four cells, each corner inset by two, and every candidate was sorted by
distance to it.

**One light per room, in an eighty-cell hall.** Now a lamp on every pillar, from the same
`PillarCells` the spawner and the validator use, in four tones through Core's per-instance glower
overrides. The dim one is dimmer, never off.

**And the doors.** `DoorOpening` was the owner's complaint written as code: an opening existed
only at the midpoint of a wall facing a linked room. A wall with no link may now open onto rock, a
third along. Spurs may be pushed against their host to share a wall, with the doorway computed
**from the overlap rather than from either room's centre** - the first draft had each side opening
its own centre, which would have named different cells in the same column and sealed the pair.

**Nine proof claims refused these changes and every refusal was right.** Four pinned the old call
text for shape, one required depth 1 to be at most eight rooms of at least sixty cells - the claim
that produced the warehouse - and one caught that the wall-material gate still tested
`coordinate.Depth`, so `StuffForRoom` was never reached on the level the owner actually walked.
**And three times a claim guarded a definition while a plant deleted the call.**

**182 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`29F1BAA124DB807247C148F5D514E6AB53F6ED614EBB2EAD2166FC7BC0EDE791`, measured after the version
bump, reproduced by two clean recompiles. **Thirteen checkers pass, forty-five proofs hold. 550 of
550** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
todo = todo.replace(u"## IN PROGRESS — the first walked level — 2026-09-30 (0.12.61-dev)",
                    u"## The first walked level — 2026-09-30 (0.12.61-dev) — DONE", 1)
todo = todo.replace(u"## IN PROGRESS — lights and geometry — 2026-09-30 (0.12.61-dev)",
                    u"## Lights and geometry — 2026-09-30 (0.12.61-dev) — DONE", 1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO headings marked done, every description kept")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.60-dev**.", u"| Published | **0.12.61-dev**."),
    (u"SHA-256 `0862FB8D411E16755614AABF316DFFEB7FD1AB2ABF98714235AD0FD050DBD93D`",
     u"SHA-256 `29F1BAA124DB807247C148F5D514E6AB53F6ED614EBB2EAD2166FC7BC0EDE791`"),
]
for old, _ in EDITS:
    if now.count(old) != 1:
        print("NOW ANCHOR PROBLEM: %d of %r" % (now.count(old), old[:50]))
        raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.61-dev")
