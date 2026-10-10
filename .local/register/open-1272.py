# -*- coding: utf-8 -*-
"""0.12.72-dev: the wall lamp with no wall behind it. Owner words, verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - the wall lamp that had no wall behind it - 2026-10-01 (0.12.72-dev)

Owner, verbatim:

> **"check the game!!! why are my colonists on the world map!!!!!!!!! they should be in the
> backrooms in this scenerio... and wtf there is nt even a gate to get there but that dont matter
> the scenerio for starting in the backroromms is fucked if i keep starting in the world tile
> map"**

> **"we loaded solo/group start into the backrooms correctly before so what the fuck these regress
> isssues are getting annoying"**

- [~] **"why are my colonists on the world map!!!!!!!!! they should be in the backrooms in this
  scenerio"**
- [~] **"and wtf there is nt even a gate to get there"** - the same cause. The gate is registered
  at step 3 of the opening and generation failed at step 2, so there was nothing to register
  against
- [~] **"the scenerio for starting in the backroromms is fucked if i keep starting in the world
  tile map"**
- [~] **"we loaded solo/group start into the backrooms correctly before"** - **they did, and this
  is a regression, and the owner is right to call it one.** `FindWallAttachmentCell` finds a wall
  and then faces it, and for a long time it was the only thing that placed the palette's light.
  The two placers added after it both got the arithmetic wrong
- [~] **"so what the fuck these regress isssues are getting annoying"**

### What the log said this time, and it is a different step

The clue-approach fix from 0.12.71-dev held: **no `RR_Generation_UnreachableRequiredCell`, and the
level generated.** What killed it was `NullReferenceException` in
`RimWorld.PowerConnectionMaker.TryConnectToAnyPowerNet`, raised from
`PowerNetManager.UpdatePowerNetsAndConnections_First`, called by **`Verse.Map.FinalizeInit`** --
which is outside this mod's generator entirely. It left `MapGenerator.GenerateMap`, so
`GetOrGenerateMap` threw, so `DestinationService.EnsureSite` reported failure.

**The full exception text added at 0.12.71-dev is what named it.** The previous log printed
`(NullReferenceException)` sixty-two times and could not say where.
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))
print("TODO opened for 0.12.72-dev, owner words verbatim")
