# -*- coding: utf-8 -*-
"""Append the 0.12.83-dev publication record. Written BEFORE the commit, per PUBLISHING.md section 6."""
import io

NL = chr(10)
ENTRY = '''
## A floor has an architecture, forty-four kinds of room, and the freeze says so first - 0.12.83-dev, 2026-10-04

**Staged and read back from the game folder**, not from the build output: `0.12.83-dev`,
SHA-256 `41FEC0AAE967F424D152D0F7C0C127437405B1FE1ABFD4298F28DD548D6E2B58`, 92 package files,
44 archetype defs present in the staged copy.

**Verified before publication:** build 0 warnings / 0 errors, 215 C# files; **16 of 16 checkers**
exit 0; **49 of 49 proofs** hold; `plant-coordinate-layout` **152 of 152**, `plant-menu-slides`
**21 of 21**; **836 plant anchors** findable. Queue after the archive: **70 open / 38 partial /
38 `[T]` / 0 `[x]`**.

### The finding: independent rolls are not variation

Owner: *"repeated patternes in variations"*. Seven room shapes had existed for some time, and the
complaint was not that there were too few — **it was that every room rolled its own, independent
of every other room.** One room a wedge, the next bays, the next a cross: that reads as damage,
not as architecture. The same shape of problem sat under the archetypes, where sixteen kinds were
each drawn against their own weight, so a coordinate held a classroom beside a weapons locker
beside a nursery — a list of rooms rather than a place.

**Neither was a legality fault, so nothing in the battery could see either.** Every shape is safe
by construction and every archetype is a legal archetype. The fix is one draw per coordinate that
everything reads, and *how hard it holds falls with depth*:

| depth | 1 | 2 | 3 | 4 | 5 | 6 | 8 |
|---|---|---|---|---|---|---|---|
| rooms on the motif shape | **89.3%** | 74.9% | 72.3% | 62.5% | 53.7% | 44.5% | **36.5%** |

All seven shapes appear at every depth; a random floor sits at **14.3%**. One number produces both
the monotonous shallow floors — *the monotony is the image the setting rests on* — and the
*"further in it gets very varied and weird"* curve. That is why it is a single falling value rather
than two systems.

### Hundreds as a product, which is the only way the number is reachable

**44 archetypes against 7 shapes is 308 distinguishable rooms before a single slot is rolled**, and
every slot carries a count range and an appearance chance on top. Authored one at a time, hundreds
of *families* would also mean hundreds of `RoomContentBuilder` cases — whose `default` throws
`RR_Generation_InvalidRoomGraph` and kills the level — plus three keyed strings each. **An
archetype costs none of that**, which is the whole reason the composition engine went there rather
than into the family ids.

Every kind the owner named exists by name, including a `RR_Room_Roadway` with lane markings, a kerb
and lighting at the spacing of a road, indoors and roofed. Twenty-one more besides, and five in the
LSD register: endless shelving whose aisles meet at the far end, a room with its furniture moved to
one wall and still facing the way it was, a ward symmetrical about an axis the door is not on, and
a room holding one chair, in the middle, facing a corner.

### What the instruments caught that reading did not

- **`proof-facilities.py` refused eight of the twenty-eight new kinds**, against a standing owner
  direction nobody had restated: *"facilitys and buildings and neighboorhoods and complexes and
  shools and hospitals and military and storages need loot inside of them too"*. They shipped with
  furniture and nothing worth carrying out. A room with nothing to take is a room with no reason to
  walk into.
- **`check-display-style.py` refused the new notice window** until it drew inside
  `RimroomsWindowState.Clean()`. That is not housekeeping here: a frameless full-screen image is
  the most vulnerable draw in the mod to a leaked zero-alpha `GUI.color` from any of 294 others —
  an invisible backdrop on a window with no frame is an invisible window, so the player would be
  looking at a frozen game with no notice on it. **The exact failure the feature exists to prevent,
  arriving through the feature.**
- **Two plants reported MISSED** because two claims named the callee instead of the call: the motif
  struct existed, the hold was still computed, the carver still called `ShapeFormOf`, and a plant
  had deleted the on-motif branch so every room went back to rolling its own. Fifth instance of
  that one gap in two sessions, and all five were found by a plant rather than by reading.
- **`proof-menu-slides.py` broke the moment the slide list moved out of `RimroomsMenuBackground`**,
  which is exactly what it was built to do: it reads the folder and prefix out of the source rather
  than restating them. A second AI reading the diff independently flagged the same thing.

### The freeze, and the ordering that was the whole difficulty

Owner: *"a popup and notice ... that pops up befgore the "freeze" of the generation"*. **Before** is
the requirement and it is the hard part. `EnsureSite` generates synchronously and hands the map back
through an `out` parameter, so a window added immediately before it draws on the *next* frame —
after the freeze it was warning about.

The answer is not to defer `EnsureSite`; every caller depends on that `out`. It is to move the
**work** into `LongEventHandler.QueueLongEvent`, the pattern Core itself uses for settling — legal
exactly where nothing waits on a return value. **A UI button callback is such a place; a method
handing back a `CompanyActionResult` is not.** So the Operations pane's two openings announce, the
player dismisses a full-screen notice carrying one of the mod's own menu images while the game can
still draw, and the generation then runs inside the event with our wait text on Core's box.

**The gate-enter half is recorded rather than claimed.** A pawn crossing is a job tick, and
`GateSpinUp` reaches `EnsureSite` from a tick as well; a tick cannot queue a long event and carry
on. That path needs the result chain deferred and its row stayed open — it was marked `[x]` and put
back to `[ ]` before the archive, because **the archiver will happily move a row that lies.**

### The menu defect behind the owner's loading-screen report

`currentIndex` was pinned to `0` in the constructor **and reset to `0` again** in the settings
handler, so the main menu — and the backdrop behind every load started from it — opened on slide
one of six, every single time, forever. The slideshow cycled perfectly and every claim about the
folder scan and the crossfade held. **There was no plant suite covering the menu art at all**;
there is now, and the first plant in it is this defect.

### Mod register

`python tools/register-query.py trace RR-SPACE`. Nothing applied: the archetype slots resolve by
**capability** against the whole loaded def database rather than naming anything, so a profile mod
that adds a bench, a shelf or an ore puts it in Backrooms rooms the day it is installed — no
adapter, no row. That is the `modDependencies` direction being served by construction rather than by
a later pass.

'''

path = "docs/FINALIZED.md"
text = io.open(path, encoding="utf-8").read()
if not text.endswith(NL):
    text += NL
io.open(path, "w", encoding="utf-8", newline=NL).write(text + ENTRY)
print("publication record appended")
