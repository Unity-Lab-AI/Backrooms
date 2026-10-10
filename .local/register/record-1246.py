# -*- coding: utf-8 -*-
"""Record the map-generator fix."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
ROW = u"""## First launch findings, third pass — 2026-09-30

- [x] **"same problem but differnt now the map is bigger but its not the 300x300 i choose and its not the tilemap i chose the land features are all barren to just bare dirt not even vegitation and the map still is the wrong size not the exact map i picked useing the mod for viewing the map and rerolling them before selection"** — **FIXED 0.12.46-dev, and the owner named the cause: "the map generator is not our mod".**

  `ScenPart_RimroomsStart` set `Find.GameInitData.mapGeneratorDef = startDef.mapGenerator`, replacing Core's **`Base_Player`** with `RR_Headquarters`. `Base_Player` inherits `MapCommonBase` and runs the whole chain — elevation, fertility, biome terrain, caves, rocks from grid, plants, animals, ruins, rivers, roads, plus the Royalty, Biotech and Anomaly steps. **`RR_Headquarters` had four steps:** our terrain pass, our facility, `ScenParts`, `Fog`. And our terrain pass did `foreach (IntVec3 cell in map.AllCells) SetTerrain(cell, outdoorTerrain)` — **flattening the entire map to one terrain.** That is precisely *"all barren to just bare dirt not even vegitation"*.

  **And it explains the preview mismatch exactly.** The mod the owner uses is **Map Preview** (`m00nl1ght.MapPreview`, installed), which simulates the **real** generator for a tile. So every map previewed and rerolled against was a picture of a map this mod then discarded. **The preview was right and the game was wrong.**

  Fixed as the owner directed: **the override is gone**, Core generates the tile at the size the player picked, and the two gen steps are added to `Base_Player` by `Patches/RR_StartGenSteps.xml`. **`PatchOperationAdd`, never a replace** — a replace would take ownership of the list and silently drop every step Core and every other mod put there, which is why `check-compliance.py` refuses destructive operations outright.

  **The load-bearing half is that the gen steps had to stop throwing.** `RequireStart` threw when a map was not the company start, which was harmless while only our own generator could reach it. Inside `Base_Player` it would break **every** player map a game ever generates — a second settlement, a quest site, a reloaded world. It is `StartForMap` now and returns **null**, and both steps return immediately on null. The proof reads the guard's own body and refuses a `throw` in it.

  **The terrain step only floors the facility footprint now.** The rest of the tile is whatever Core generated, which was the entire point.

  `RR_Headquarters` and the `mapGenerator` def field are **retired, not orphaned** — removed from the class, from `ConfigErrors` and from all three start defs, because a value nothing reads is a job nobody finished. Record `implementation/START_PLACEMENT_IMPLEMENTATION.md`, proof `proof-startplacement.py`, **27 of 27 planted faults caught**.

  **Two of my own checkers caught me during this.** `check-compliance.py` flagged the new patch for containing `PatchOperationReplace` — in the **comment explaining why a replace is wrong.** It strips XML comments now, for the same reason `check-display-style.py` does: testing for mention rather than assertion is the defect class this project has been caught by four times. And `proof-starts.py` asserted the exact thing being reversed, with wording that revealed the old assumption — it called Core falling back to *"an ordinary colony map"* the failure, when an ordinary colony map for the chosen tile is what the player wants.

---

"""
if todo.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM")
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("third-pass finding recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.45-dev**.", u"| Published | **0.12.46-dev**."),
    (u"SHA-256 `B4E57D05F52BCD7947465A34E70834165A5CD23CB25BBE6831EA8DA6586EFFA3`",
     u"SHA-256 `1C0348B2D59F8B58743BE50BEA7AA67C6D2E79E832A10CD08497E6E5154E8455`"),
    (u"| Build | **199 C# files, 89 package files**",
     u"| Build | **199 C# files, 90 package files**"),
    (u"**Second pass, and these two were the worst of the lot.**",
     u"""**Third pass, and this one was the root of the map complaints.** Owner: **"the map generator
is not our mod"**. `ScenPart_RimroomsStart` replaced Core's `Base_Player` — elevation, fertility,
biome terrain, caves, rocks, plants, animals, ruins, rivers, roads — with a **four-step** generator
of ours, and our terrain step flattened **every cell** to one terrain. Hence *"bare dirt not even
vegitation"*. And the owner previews tiles with **Map Preview**, which simulates the **real**
generator, so every map they rerolled against was a picture of a map the mod then discarded: **the
preview was right and the game was wrong.**

Core generates the tile now. The two gen steps are **added** to `Base_Player` by a patch — never a
replace, which would drop every step Core and other mods put there. **The load-bearing half: the
steps had to stop throwing.** They live in the generator that makes *every* player map now, so a
throw would break a second settlement, a quest site, a reloaded world. `StartForMap` returns null
and the proof refuses a `throw` in its body.

**Second pass, and these two were the worst of the lot.**"""),
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
print("NOW.md updated for 0.12.46-dev")
