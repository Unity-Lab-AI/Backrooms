# -*- coding: utf-8 -*-
"""0.12.62-dev: the layout the validator would never accept."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")
README = os.path.join(REPO, "README.md")

HASH = u"5201C4A6D368DE5E2E3A94939BEC0D0AF5858A870A1A05F4AC991F2D94BE8774"

ENTRY = u"""
---

## Session 2026-10-01 - the layout the validator would never accept (0.12.62-dev)

**Verbatim user quotes:** *"oka read now.md and i started it up after last stage and this run
through the door is not blue and i dont see the backrooms is there and cant portal to it, check
whats rrunning and what broke since last run where it was working"*.

**Files touched:** `Generation/RoomLayoutPlanner.cs`, `Generation/DestinationService.cs`,
`tools/check-planner-layouts.py` (new, checker fourteen),
`.local/harness/PlannerProbe/` (new), `.gitignore`,
`.local/register/proof-coordinate-layout.py`, `.local/register/plant-coordinate-layout.py`.

**Mod register.** Checked `RR-SCEN` (3 rows: Core [4], Character Editor [64], Hospitality:
Storefront [286]). **Nothing applied.** The room planner is pure arithmetic over our own
constants, no other mod reaches it, and the defect was two numbers in two of our own files
disagreeing. Recorded rather than skipped, because *"nothing applied"* is a finding.

**Closure notes.** **The tenth launch regressed the gate, and the cause was shipped by the ninth
checkpoint's own geometry work.**

The log was clean -- zero red, `0.12.62-dev`'s predecessor loaded, the company branch initialised.
**The evidence was a letter on the owner's screen**, read out of the running game through the
bridge: *"The company could not finish startup: No safe first-site layout was found within the
bounded attempt limit."*

`SoloGroupOpening.Open` does five things in order, and step 2 is the coordinate's map. It failed,
so step 3 never marked the door and step 4 never registered the edge -- and `IsLiveGate` requires
both a mark and an edge. **So the door was not blue because there was no Backrooms to be a gate
to.** Every symptom the owner reported is one failure.

**Three span defects, and the first is deterministic.** `ValidateRooms` refuses any room wider
than `MaxRoomSpan`, a property documented as *"the widest room the planner can produce"* and
computing `SlotRoomSpan(SlotSpacing(MinSlotsPerAxis))` -- the span of a room filling one slot, 34
cells. The grand hall added at 0.12.61-dev spans **two** slots less the gap: **80.** Candidates 0,
1 and 2 carry the hall, so **all three were refused every single time.** The fallback carries no
hall but does carry `VariedRoomSpan`, which may add up to 6 -- 40 against a ceiling of 34 -- so it
was refused whenever any one of its twenty-odd rooms rolled upward, which is every time in
practice. **Four refusals, every seed, every start.**

And `PushAgainst` broke the candidate two different ways at once. `CellRect.Overlaps` is
**inclusive on both edges**, so two rooms whose bounds share a wall column overlap by RimWorld's
own reckoning -- and overlapping rooms have been refused since the first layout. Two of its four
branches produced exactly that. The other two abutted, which the old `SharesWall` tested for
equality and therefore could not see, so the pair got neither a corridor nor a doorway and the
spur was **sealed**. The fix is abutment on all four sides, one wall each, with the move **put
back** if it leaves the map, collides with a third room, or `SharesWall` disagrees.

**And then the second doorway rule was deleted rather than fixed.** An abutting neighbour's near
edge is `maxX + 1`, which is strictly beyond `maxX`, so `DoorOpening`'s existing rule already
opens each room's own wall midpoint -- and `AreGridNeighbors` guarantees linked centres share that
axis, so the midpoints are the same cell on it and the openings meet. `SharedDoorCell` was a
second rule deciding one doorway, which is the defect this file keeps paying for.

**THE PROBE IS THE REAL OUTCOME.** The planner is pure -- no map, no world, no defs, no global
random -- so *"does this produce a layout the validator accepts"* was always answerable at the
desk, and for one whole checkpoint nobody asked. `.local/harness/PlannerProbe` runs
`TrySelect` and `ValidateRooms` over two hundred seeds at seven depth bands and counts what comes
out; `tools/check-planner-layouts.py` is **checker fourteen** and runs it. It never skips: a
missing `dotnet`, a missing install or an unbuilt assembly is a failure, because a check that
passes when it could not run is worse than no check.

It immediately found a second thing nothing else could. `chainLength` was capped at `MaxRooms`, so
**from depth 5 the serpentine alone reached sixty rooms and the spur loop never executed once** --
no dead ends, no branches, no back-to-back pairs on the deepest levels, the exact opposite of
*"it needs to be more maze liek"*. Capped at two thirds of the budget, depth 5 went from **0
back-to-back pairs to 493**.

**And a plant proved the point in one character.** Reverting `mover.x = b.maxX + 1` to
`mover.x = b.maxX` was **missed by all forty-five proofs**: the new revert guard saw the overlap
and put the room back, so every layout stayed valid and the feature was simply **never produced
again.** Switched off, silently, with every claim passing -- which is this project's dominant
defect class, and the probe counts the pairs precisely because a source claim cannot.

**An absence claim also read my own comment and called it code** -- `"a.maxX == b.minX" not in
planner` failed against correct source because the comment explaining why that test was wrong
quotes it. Thirty-sixth instance of one class; `check-compliance.py` met it from the other side.
The proof now keeps a comment-free view and every absence claim reads that instead.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`5201C4A6D368DE5E2E3A94939BEC0D0AF5858A870A1A05F4AC991F2D94BE8774`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 556 of
556** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
TODO_EDITS = [
    (u"## IN PROGRESS - the tenth launch regressed the gate - 2026-10-01 (0.12.62-dev)",
     u"## The tenth launch regressed the gate - 2026-10-01 (0.12.62-dev) - DONE"),
    (u'- [~] **"this run through the door is not blue"**',
     u'- [x] **"this run through the door is not blue"** - `IsLiveGate` needs a mark AND an edge, '
     u'and the opening registers neither once the coordinate fails'),
    (u'- [~] **"i dont see the backrooms is there and cant portal to it"**',
     u'- [x] **"i dont see the backrooms is there and cant portal to it"** - no coordinate '
     u'generated: `MaxRoomSpan` was 34 and the grand hall is 80, so all four candidates were '
     u'refused'),
    (u'- [~] **"check whats rrunning and what broke since last run where it was working"**',
     u'- [x] **"check whats rrunning and what broke since last run where it was working"** - read '
     u'out of the running game through the bridge: the startup letter named it. Broken by '
     u'0.12.61-dev\'s own grand hall and back-to-back rooms'),
]
problems = []
for old, _ in TODO_EDITS:
    if todo.count(old) != 1:
        problems.append("%d of %r" % (todo.count(old), old[:56]))
if problems:
    for problem in problems:
        print("TODO ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in TODO_EDITS:
    todo = todo.replace(old, new, 1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO marked done, every description kept")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.61-dev**.", u"| Published | **0.12.62-dev**."),
    (u"SHA-256 `29F1BAA124DB807247C148F5D514E6AB53F6ED614EBB2EAD2166FC7BC0EDE791`",
     u"SHA-256 `" + HASH + u"`"),
    (u"| Build | **200 C# files, 91 package files**",
     u"| Build | **204 C# files, 91 package files**"),
    (u"| Checkers | **THIRTEEN**, all passing.",
     u"| Checkers | **FOURTEEN**, all passing. **The fourteenth is the only one that runs code "
     u"rather than reading it**, and it exists because the thirteen that read text, the "
     u"forty-five proofs and five hundred and fifty plants **all passed over a planner that "
     u"could not produce one valid layout** -- `MaxRoomSpan` said 34 while the grand hall was 80, "
     u"and no amount of reading either file can see two numbers disagree. "
     u"`check-planner-layouts.py` builds `.local/harness/PlannerProbe` and runs `TrySelect` and "
     u"`ValidateRooms` over 200 seeds at seven depths, demanding both that a layout is accepted "
     u"**and that back-to-back pairs exist** -- because a plant that moved a pushed room one cell "
     u"was missed by every proof when the revert guard quietly switched the feature off. **It "
     u"never skips**: no dotnet, no install or no built assembly is a failure, not a pass."),
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
print("NOW.md updated for 0.12.62-dev")

readme = io.open(README, encoding="utf-8").read()
if readme.count(u"**Current development version: 0.12.61-dev.**") != 1:
    print("README ANCHOR PROBLEM")
    raise SystemExit(1)
io.open(README, "w", encoding="utf-8", newline="").write(readme.replace(
    u"**Current development version: 0.12.61-dev.**",
    u"**Current development version: 0.12.62-dev.**", 1))
print("README version updated")
