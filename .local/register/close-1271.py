# -*- coding: utf-8 -*-
"""0.12.71-dev: a clue nobody could walk up to cost the owner the whole level."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: close-1271.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

ENTRY = u"""
---

## Session 2026-10-01 - the solo/group start never got inside (0.12.71-dev)

**Verbatim user quotes:** *"read now.md to resume. i just started it up and tried solo/group start
and for some weird reason i ended up in the world map with no connection to the back rooms.. i
should of been in the back rooms and i dont have a warp do to get back.. i think it was the issue
of the building starting door being the same as the warp gate door, but im suppose to find the gate
to the world map in the backrooms before i can get my pawns to the world map tile i selected at
game and world setup,.... so wtf is up can u fix this easily by checking the game running"*.

**Files touched:** `Generation/RoomContentBuilder.cs`, `Generation/GenStep_BackroomsDestination.cs`,
`tools/check-planner-layouts.py`, `.local/harness/PlannerProbe/Program.cs`,
`.local/harness/PdbLine/` (new), `proof-generation-batch.py`, `plant-generation.py`.

**Mod register.** Checked `use RR-SCEN` (3 rows), `use RR-STA` (149 rows) and the
*Power and industrial infrastructure* family (10 rows); `find conduit` returns nothing.
**Nothing applied.** Row 4, Core, is the only row that bears on either change and it asks exactly
what was done -- *"keep the company's base loop playable through the base game"*. The power family
is Optional, Configuration-only and No-integration across the board, and this change patches
nothing of theirs: it stops **us** calling Core's rebuild a second time.

### What the owner reported, and what the log actually said

`[Rimrooms][Company] Initialized ... scenario=lone_survivor`, then
`RR_Generation_UnreachableRequiredCell` thrown out of `ValidatePlacedLayoutCore` and up through
`MapGenerator.GenerateContentsIntoMap`. So the opening stopped at **step 2 of five**: the
coordinate's map. Steps 3 and 4 -- *mark the surface door* and *register the emergence address* --
never ran, and step 5 never moved anybody inside. **The door the owner suspected was never
reached.** Their hypothesis, *"i think it was the issue of the building starting door being the
same as the warp gate door"*, is recorded in `docs/TODO.md` and is wrong, and saying so is cheaper
than redesigning a door that was fine.

`SoloGroupOpening.Open` returned the refusal and `ScenPart_RimroomsStart` reported it, which is why
the colony existed on the surface map with no coordinate and no way in -- *"i ended up in the world
map with no connection to the back rooms"*.

### Which of the two throws it was, and how that was answered

**`ValidatePlacedLayoutCore` raised one key from two places.** The stack carried `[0x001f8]` and
nothing else; reading the source cannot tell those apart, and guessing costs the owner a launch.

`.local/harness/PdbLine` reads the portable PDB's sequence points and maps an IL offset to a
source line. It resolved `0x001f8` to **line 1446 -- the clue landmark's approach** -- and printed
the assembly MVID `f7b34bd8-720b-462b-b5bb-f355f8d9d8bf`, **the same MVID the stack trace carried**,
which is what makes the answer evidence rather than inference. Tracked, because the question
recurs.

**And there is one throw site for that key now.** Two sites raising one key is the defect behind
the whole detour.

### Two correct decisions, and the hole between them

Every landmark this builder places -- `Stool`, `Table1x2c`, `Shelf`, `PlantPot`, `StandingLamp` --
is `PassThroughOnly`, so `footprint.Contains(cell) && cell.Standable(map)` is never true for its
own cell and **the approach is always a neighbour.** Then:

* `FixtureCell` relaxed the walkable margin from a requirement to a **preference** at 0.12.61-dev.
  That was right: requiring one aborted whole levels, and it says so at length.
* `DressRoom` places fixtures **until one will not fit** -- `if (placed == null) { break; }` -- so
  the last cells it takes are exactly the no-margin cells flush against whatever is already there.
* 0.12.69-dev put loot in all sixteen archetypes, which is what made a room dense enough to
  actually reach that point.

So the dressing took all four neighbours of the landmark, and the clue loop refused the layout.
**`FixtureCell`'s own claim is true and was read one step too far:** *"The margin was never what
keeps the room walkable. The reserved route cross is."* The cross keeps the **room** walkable and
says nothing about the landmark's approach -- which is off the cross **by construction**, because
cross cells are reserved.

### The fix: the approach comes from the cross, so it cannot be taken

`RoomContentBuilder.RouteTrunk` returns the **clear, joined-up** part of the room's reserved route
cross, and the landmark is offered a cell orthogonally beside it. A cross cell is reserved for the
whole of population, so nothing placed later can occupy it: **the guarantee is structural instead
of lucky.**

*Joined up*, not merely on the cross, because a pillar or a stand of shaped rock severs an arm and
a cell in a severed arm is standable and unreachable -- the exact pair of properties the validator
rejects. `TouchesApproach` tests orthogonal adjacency, which is the test the validator applies;
a second derivation of one rule is this project's most repeated defect.

**It falls back rather than refusing.** A refused landmark throws `RR_Generation_NoSafeRoomCell`,
which is the same dead level by another name. And the landmark's ring is reserved once it is
placed, exactly as `Populate` already does for the gate anchor, so a landmark that did fall back
still keeps the neighbours it was placed with.

**And an unreachable clue is now reported rather than fatal.** The generator's own rule, applied
where it had been missed: *"A coordinate whose heater or one lamp failed to join the grid is dark
and cold and completely playable. A coordinate that does not exist costs the player the gate that
leads to it."* One clue nobody can walk up to is one awkward room. The structural checks around it
stay fatal, because a coordinate you cannot walk through really is broken.

### The instrument can see it, which is the part that would otherwise rot

`check-planner-layouts.py` grew a third demand: **every room must be able to stand its landmark
beside its own clear route cross.** It reports `approach` and `noapproach` per band, and
`noapproach` was **0 across all seven bands, 1,400 layouts and roughly 50,000 rooms** when it was
written -- so anything above zero is new.

**This is the `fellback` lesson again.** That column exists because the probe once reported a clean
`refused 0/200` while the fallback was catching every single seed. A net that catches everything is
a net nobody can see through, so the fallback here is measured rather than trusted.

`LandmarkCells`, `MarginedCells` and the new `ApproachCells` now share one `BlockedCells` -- and
that was not cosmetic: `LandmarkCells` had not been modelling the **lamp on every pillar**, which
`SpawnPillarLamps` places before `Populate` and which blocks a cell exactly as a pillar does. Three
copies of one rule is the shape that let the planner and the validator disagree about the widest
room in the place.

Also measured and worth writing down: **`margin` reads 0 at every depth.** The tightest room in
every band has **no** margined cell at all, which means the no-margin fallback is the normal path
rather than the exception -- and that is precisely the mechanism that boxed the clue in.

### Sixty-two power warnings, and the retry that made the real fault

The same generation logged **62** copies of *"could not rebuild its power connections
(NullReferenceException)"* and, in the middle of them, Core's *"Tried to register trasmitter
ChemfuelPoweredGenerator163327 at (130, 0, 38), but there is already a power net here"* -- naming
the **generator**, on the **generator's own cell**, which `SpawnNativePowerNetwork` seeds into
`wiredCells` precisely so no conduit of ours can ever go there.

**The retry produced it.** Core processes its delayed register/deregister queue inside
`UpdatePowerNetsAndConnections_First` and clears the processed entries **after** the loop, so a
throw part-way through leaves already-applied entries queued. `ConnectStrayConsumers` rebuilt once
per stray consumer, so it called again, re-applied them, and re-registered a transmitter that was
already registered -- which is the permanent fault this generator documents in `AlreadyTransmits`.
**The first failure was the real one; the next sixty-one were self-inflicted.**

So `RebuildPowerNets` returns a bool, the sweep stops on false, and the caller does not ask again.
And the exception is logged **in full** instead of by type name: sixty-two lines reading
`(NullReferenceException)` could not name the Core method or the thing, and that was the whole
question. One line with a stack can answer it on the next launch.

**What is NOT claimed:** the root cause of the first throw is not known. It is inside Core, reached
through a 294-mod profile, and the log as written could not say where. This checkpoint stops the
compounding fault and makes the next log answer the question; it does not pretend to have fixed
something it could not see.

### The traps, counted

**The claim-scoping trap, a forty-second time, and it was mine coming the other way.** Re-aiming
the power claim at the new signature briefly left it asserting only
`map.powerNetManager.UpdatePowerNetsAndConnections_First();` **without the `try` around it** -- a
claim that would pass against an unguarded rebuild, which is the exact defect it exists for. It
asserts the whole guarded block, in order, now.

**And eight plant anchors reported `PLANT SETUP BROKEN (0 matches)` rather than passing**, which is
the suite doing its job: an anchor that no longer exists is reported, never silently skipped. Six
existing claims failed against **correct** code for the same reason, which is the right direction
for a claim to fail in.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`%(hash)s`, measured after the version bump, reproduced by two clean recompiles.
**Fifteen checkers pass, forty-five proofs hold.** Planted faults caught: all of them, across
sixteen suites.
""" % {"hash": HASH}

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = u"## IN PROGRESS - the solo/group start never got inside - 2026-10-01 (0.12.71-dev)"
HEAD_NEW = u"## The solo/group start never got inside - 2026-10-01 (0.12.71-dev) - DONE"
if todo.count(HEAD_OLD) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(HEAD_OLD))
    raise SystemExit(1)
todo = todo.replace(HEAD_OLD, HEAD_NEW, 1)
start = todo.index(HEAD_NEW)
end = todo.index(u"\n---", start)
block = todo[start:end].replace(u"- [~] **", u"- [x] **")
todo = todo[:start] + block + todo[end:]
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO marked done, every description kept")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.70-dev**.", u"| Published | **0.12.71-dev**."),
    (u"SHA-256 `EC6AAA0B82D00F3884994DEDECC2460B4E6777C0F90B4C64398725DB3CA0D30A`",
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
print("NOW.md updated for 0.12.71-dev")
