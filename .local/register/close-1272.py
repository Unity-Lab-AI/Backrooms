# -*- coding: utf-8 -*-
"""0.12.72-dev: the wall lamp that had no wall behind it, and Core dereferenced it."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: close-1272.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

ENTRY = u"""
---

## Session 2026-10-01 - the wall lamp that had no wall behind it (0.12.72-dev)

**Verbatim user quotes:** *"check the game!!! why are my colonists on the world map!!!!!!!!! they
should be in the backrooms in this scenerio... and wtf there is nt even a gate to get there but
that dont matter the scenerio for starting in the backroromms is fucked if i keep starting in the
world tile map"*; *"we loaded solo/group start into the backrooms correctly before so what the fuck
these regress isssues are getting annoying"*.

**Files touched:** `Generation/GenStep_BackroomsDestination.cs`, `proof-generation-batch.py`,
`plant-generation.py`.

**Mod register.** Checked the *Power and industrial infrastructure* family (10 rows: stances
Optional, Configuration only, No integration) and `find conduit` (0 rows). **Nothing applied, and
the register's own stance is the reason:** this defect is in how **we** place a Core building on
**our** map, and the fix patches nothing anybody else owns. Row 4, Core -- *"keep the company's
base loop playable through the base game"* -- is what the fix is for.

### The owner is right that it is a regression, and right about which scenario worked

*"we loaded solo/group start into the backrooms correctly before"*. **They did.**
`FindWallAttachmentCell` finds a wall and then faces it, and for a long time it was the only thing
that placed the palette's light. **Two placers added after it both got the arithmetic wrong**, and
they landed in the two checkpoints the owner is calling a regression.

### What Core does, verbatim, and it has no null check

`RimWorld.PowerConnectionMaker.TryConnectToAnyPowerNet`, decompiled from the installed 1.6
assembly:

```csharp
CompPower compPower = BestTransmitterForConnector(
    pc.parent.def.building.isAttachment
        ? GenConstruct.GetWallAttachedTo(pc.parent).Position
        : pc.parent.Position,
    pc.parent.Map, disallowedNets);
```

And `GenConstruct.GetWallAttachedTo(pos, rot, map)` returns **null** unless the cell at
`pos + GenAdj.CardinalDirections[rot.AsInt]` holds something with
`building.supportsWallAttachments`.

**`BackroomsPalette` resolves `WallLamp`, which is `isAttachment`.** So one wall lamp facing open
floor is a guaranteed `NullReferenceException` inside Core's own power rebuild.

### Why that cost the whole level and not one lamp

`Map.FinalizeInit` calls `powerNetManager.UpdatePowerNetsAndConnections_First()` as **step four of
fifteen**. Everything after it -- the temperature cache, `avoidGrid`, animal pens, plant growth
rates, the gas grid, **every `Thing.PostMapInit()`**, the filth lister, the map drawer, the
resource counter, the wealth recount -- never ran. The throw left `MapGenerator.GenerateMap`, so
`GetOrGenerateMapUtility.GetOrGenerateMap` threw, so `DestinationService.EnsureSite` reported
failure and `SoloGroupOpening` never reached the step that moves anybody inside.

**So `EnsureSite` discarding that map is CORRECT and was left alone.** The obvious-looking fix --
keep the map, since our own GenStep finished and `MarkLayoutReady` ran -- was considered and
**rejected on the evidence**: a map whose `FinalizeInit` died at step four has no regions, no pens
and no `PostMapInit`. Reading `Map.FinalizeInit` before building that is what stopped it being
built.

And because Core clears its delayed power queue only **after** the loop that processes it, the
queue was never cleared, so every later tick re-ran it: `Root level exception in Update()` for the
rest of the session, plus *"Tried to register trasmitter ChemfuelPoweredGenerator167984 at
(263, 0, 38), but there is already a power net here"* when the re-run re-registered the generator
on its own cell.

**The full-exception logging added at 0.12.71-dev is the only reason this was findable.** The
previous log printed `(NullReferenceException)` sixty-two times and named neither the Core method
nor the thing. One line with a stack answered it on the next launch, exactly as that checkpoint
said it would.

### One mistake, made twice, and one rule that now has one home

| Placer | What it did | Verdict |
|---|---|---|
| `FindWallAttachmentCell` | `behind = cell + direction`, `facing = Rot4.FromIntVec3(direction)` | **correct**, and it is why this used to work |
| `SpawnPillarLamps` | lamp at `pillar + d`, facing **`+d`** -- looked for a wall *two cells past* the pillar | **inverted** |
| `DressCorridors` | `GenSpawn.Spawn(lamp, cell, map, Rot4.North)`, **no wall test of any kind** | **wrong**, and a corridor side cell's wall is almost never north |
| the room fallback | no wall found, so it placed `lightDef` -- the `WallLamp` -- on open floor facing north | **wrong** |

The pillar comment said *"facing out of the pillar: the lamp draws into the wall behind it, and the
wall behind it is the pillar"*. **The intent was right and the arithmetic was inverted**: Core reads
the wall at `position + rotation.FacingCell`, so a lamp one cell north of a pillar has to face
SOUTH to be attached to it.

**`WallAttachmentHolds` asks Core's own `GenConstruct.GetWallAttachedTo`** rather than restating the
rule. Core is what dereferences the answer, so Core is the only thing whose opinion matters; a
local copy could disagree with it, and that disagreement is this project's most expensive defect
shape -- `MaxRoomSpan` said 34 while the hall was 80, and a light count disagreed with the lights
for thirty-nine checkpoints.

**`SpawnAttachableLight` is the only thing that spawns a lamp now**, for all three callers. It
tries the caller's preferred wall, then the other three -- a corridor side cell has a wall on
exactly one side and the caller cannot know which -- then falls back to a floor-standing lamp, and
places **nothing** rather than an attachment in mid-air. A room with no wall to mount on still gets
a light, which is what *"the basic rooms are well lit"* asked for.

### And a sweep, because three obedient callers is not the same as a rule

`RemoveUnattachedAttachments` runs after every placer and **before a single conduit is laid**: any
`isAttachment` thing on the coordinate whose `GetWallAttachedTo` is null is destroyed, and dropped
from the list the power validation reads.

**This is what makes the fourth placer harmless.** It also closes a hole nobody had noticed: the
archetype dressing spawns arbitrary modded defs at a scattered facing through `TryPlace` and never
checked, so a profile whose laboratory archetype resolved a wall-mounted fixture had the same
guaranteed throw waiting in it. The worst case is now a dark corner, which is the trade this
generator makes everywhere else.

### The suite caught the proof, which is new

**`thing.Destroy(DestroyMode.Vanish);` appears three times in this generator** -- the rock
clearance, one other, and the sweep. The claim asserted it bare, so a plant that made the sweep
find every stranded lamp and leave all of them standing **passed**. `102 of 103` is the only
reason that was found.

**Forty-third instance of the scoping trap, and the first this session where a plant caught a
claim rather than a claim catching the code.** The claim pins the destroy to the line above it now,
in order.

Eight plant anchors reported `PLANT SETUP BROKEN` rather than passing, and two existing claims
failed against correct code. Both are the right direction.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`%(hash)s`, measured after the version bump, reproduced by two clean recompiles.
**Fifteen checkers pass, forty-five proofs hold, 103 of 103 planted faults caught in the
generation suite.**
""" % {"hash": HASH}

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = u"## IN PROGRESS - the wall lamp that had no wall behind it - 2026-10-01 (0.12.72-dev)"
HEAD_NEW = u"## The wall lamp that had no wall behind it - 2026-10-01 (0.12.72-dev) - DONE"
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
    (u"| Published | **0.12.71-dev**.", u"| Published | **0.12.72-dev**."),
    (u"SHA-256 `F4E367E7C4DBC3C3AF92E7A06FF7CF59E421A397426A3F404206367BF91ACE41`",
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
print("NOW.md updated for 0.12.72-dev")
