# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.72-dev, written after the stage so it quotes a verified hash."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## STATE AT THIS HANDOFF — `0.12.71-dev`, STAGED AND VERIFIED"

NEW = u"""## STATE AT THIS HANDOFF — `0.12.72-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.72-dev  91 files
assembly    8FFCF0F0BE7CA434F2883F94F7693B53AE65F4CF08B353F1CB0F7086BC1739D6
            read back out of the game folder after staging, not from the build
battery     15 checkers - 45 proofs - 646 of 646 plants - 16 suites
tree        no planted fault, porcelain 0
```

### TWO LAUNCHES, TWO DIFFERENT CAUSES, SAME SYMPTOM

The owner reported the same thing twice -- *"why are my colonists on the world map!!!!!!!!! they
should be in the backrooms in this scenerio"* -- and it was **not** the same defect. Both stopped
`SoloGroupOpening` before step 5, and that is the only thing they had in common.

| | Launch | Cause | Where it threw |
|---|---|---|---|
| 0.12.71-dev | solo/group on the world map | **a clue landmark the dressing had sealed in** | our `ValidatePlacedLayoutCore` |
| 0.12.72-dev | solo/group on the world map **again** | **a `WallLamp` with no wall behind it** | **Core's `Map.FinalizeInit`**, not our generator at all |

**The second one is a regression and the owner was right to call it one.** *"we loaded solo/group
start into the backrooms correctly before"* -- they did. `FindWallAttachmentCell` finds a wall and
then faces it, and for a long time it was the only thing placing the palette's light. The pillar
lamps and the corridor dressing, added after it, both got the arithmetic wrong.

### THE CORE BEHAVIOUR TO KNOW BEFORE PLACING ANYTHING ELSE

`RimWorld.PowerConnectionMaker.TryConnectToAnyPowerNet` does this, with no null check:

```csharp
pc.parent.def.building.isAttachment
    ? GenConstruct.GetWallAttachedTo(pc.parent).Position
    : pc.parent.Position
```

`GetWallAttachedTo` returns null unless the cell at `pos + GenAdj.CardinalDirections[rot.AsInt]`
holds something with `building.supportsWallAttachments`. **`WallLamp` is `isAttachment`.** So one
lamp facing open floor is a guaranteed `NullReferenceException` inside Core's power rebuild --
**step four of fifteen in `Map.FinalizeInit`**, so regions, pens, plant growth, every
`PostMapInit` and the wealth recount never run, and the finished level is discarded on the way out.
Core never clears the queue it threw out of, so it re-runs every tick afterwards.

**`EnsureSite` discarding that map is correct and was deliberately left alone.** Rescuing it was
considered -- our GenStep had finished and `MarkLayoutReady` had run -- and **rejected after
reading `Map.FinalizeInit`**: a map that dies at step four has no regions and no `PostMapInit`.

**One rule, one home, plus a net:**

| | |
|---|---|
| `WallAttachmentHolds` | asks **Core's own `GenConstruct.GetWallAttachedTo`**. Core is what dereferences the answer, so a local copy of the rule could disagree with it -- the `MaxRoomSpan` shape |
| `SpawnAttachableLight` | the only thing that spawns a lamp, for all three callers. Preferred wall, then the other three, then a floor-standing lamp, then **nothing** rather than an attachment in mid-air |
| `RemoveUnattachedAttachments` | sweeps the finished coordinate before any conduit is laid. **This is what makes the fourth placer harmless**, and it also covers the archetype dressing, which spawns arbitrary modded defs at a scattered facing and never checked |

### THE RESIDUE CHECKER WAS BLIND IN EXACTLY THE CASE IT EXISTS FOR

`plant-containment.py`'s restore raised `OSError: [Errno 22]`, so its `finally` never reached
`_rr_unmark()` and the sentinel **was** left behind -- correctly. **Then the next suite's
`_rr_unmark()` deleted it**, because all sixteen shared one sentinel path. `check-plant-residue.py`
reported a clean tree with `campaign.ClearBreachResponded();` missing from
`ContainmentProtocol.cs`.

**Fourth instance of residue reaching the tree and the first the sentinel could not see.** Each
suite names its sentinel after itself now, the checker globs them, and the restore retries and
verifies before anything believes it. The error was transient -- the same path had just been
written twice -- so one retry makes it a non-event.

### WHAT THE OWNER HAS NOT SEEN YET

**Eleven checkpoints are built; the last launch to reach a playable Backrooms level was
`0.12.67-dev`.** Two launches since have each got one step further.

| Checkpoint | Unseen in a game |
|---|---|
| 0.12.68-dev | the braided maze, the raised graph ceiling, **the new packageId** |
| 0.12.69-dev | institutions on a first level, complexes to six rooms, loot in all sixteen archetypes |
| 0.12.70-dev | the assembly as a player-queued bill, and gate control on the components |
| 0.12.71-dev | the landmark's reserved approach -- **this one is confirmed working**, the level generated |
| 0.12.72-dev | **a solo/group start surviving `Map.FinalizeInit`** |

**A NEW START IS REQUIRED.** Nothing retries a failed opening; owner's decision when asked,
2026-10-01: *"Just the fix, I'll restart"*.

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for 0.12.72-dev, after the stage")
