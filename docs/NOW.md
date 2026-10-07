# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | **the test phase — 56 rows, guarded by all four queue rules** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## ⛔ THE GAME IS RUNNING A QA COLONY, AND IT IS NOT THE OWNER'S ⛔

RimWorld is up with **`Solo or group, inside`** on a fresh world, paused, saved by the bridge as `rimbridge_save_20261007_101548.rws`. **The owner's 31 saves are untouched.** Quit it from the main menu when done: `python .local/qa/hands.py 1271 641` after `go_to_main_menu`.

---

## ⛔ SIX DEFECTS THE OWNER SAW BY PLAYING, FIVE FIXED AND ONE MEASURED ⛔

**Verbatim, 2026-10-07:** *"the flower pot in the back rooms needs to be forbiden ... thousands of lights just mass numbers of lights in piles ... i didnt see it using the lights textures and skins we have ... the hallways were all rock mountain, when they were to be wooden walls ... the veins of resources that are minable inbetween isolated rooms ... the hallways were one massive room so entering one door basicly explored the whole fucking map"*.

| Finding | Cause, measured | State |
|---|---|---|
| Pots pull pawns | Corridor fixtures were `Faction.OfPlayer` and never forbidden; the sow job searches exactly that flag | **fixed** — `GeneratedContent.Quieten`: forbid, and a storage is `Unstored` because hauling never asks about forbids. 176 pots → **43** |
| Lights in piles | Corridor lamps spaced by **list index** over side cells sorted by row; `StandingLamp` in the fixture list (1,521 of them) | **fixed** — spaced by the cell's own coordinate; no lamp in the fixture list |
| Our light art unused | `BackroomsPalette` asked for `WallLamp` by name; `RR_SiteFluorescent` shipped and nothing placed it | **fixed** — `RR_SiteFluorescentFitted`, unpowered, placed per bay and per seven corridor cells. **1,197 of ours, 0 wall lamps** |
| Rock hallways | `PlaceCorridorWall` stood down on *any* edifice, and the rock fill is an edifice in every cell: **no corridor wall was ever built** | **fixed** — yields only to a built wall. 3,499 walls → **9,056** |
| No veins | They exist: 1,251–2,355 ore cells per coordinate. Rock is `saveCompressible`, so nothing could count it | **measured, unchanged** — `.local/qa/render-coordinate.py` decodes the grid and draws it |
| One massive room | Every corridor joins every other with nothing between; fog stops at doors only | **fixed** — a door across every leg ≥ 9 cells. 122 doors → **202** |

**Seen with my own eyes in the live game**, not inferred: the yellow rooms lit by our strips, corridors edged in wood, red forbid crosses on the planters, fog still standing sixty cells away. Pictures in `.local/qa/evidence/eyes/`.

**Three follow-on corrections, all kept verbatim in `TODO.md`:** *"i didnt say ban pots i said mark them forbidden"* (they are forbidden, not gone, and the colony-ownership flag is what actually stops the job), *"mark anything else u build that similar has an action like a pot does"* (shelves — storage priority), *"we dont neee 1000 of them on one level"* (fixture spacing 11 → 23, pots capped at 12).

**And the lights were never on.** 3,934 wall lamps at 30 W on a 1,000 W generator; Core browns the whole net out. The fitted fixture draws nothing, which the 0.2.0 site lamp had already got right.

---

## ⛔ I HAVE EYES AND HANDS NOW, AND YESTERDAY'S "IMPOSSIBLE" TABLE WAS MISSING A ROW ⛔

**Owner:** *"with the rimbridge i dont think u can see very well so im thinking on top of rimbridge u use something like playwrite so u can see the game too"*. Playwright drives browsers; the instinct was right anyway. **`rimworld/take_screenshot` was in the bridge's 125 tools the whole time and I never called it.**

- `.local/qa/eyes.py` — capture through the bridge, downscale 3840×2160 to 1600 wide, print the path to Read.
- `.local/qa/hands.py X Y` — click a pixel in that frame with Windows input. **Raises the game and refuses unless the game holds the foreground**, so a click can never land in the owner's other windows.
- `.local/qa/start-scenario.py --resume` — picks the page loop back up after a pixel click.

**A fresh colony end to end, twice:** New colony → scenario → storyteller → world → *Select random site* → Next → pawns → acknowledge → Start. Launch the game directly with `Start-Process RimWorldWin64.exe -WorkingDirectory` (the `steam://` URL did nothing). ~2.5 minutes to the bridge.

**One ordering bug of mine found by the first live run:** the three-cell strip took the utility room's floor before the two-by-two generator chose a cell, and `RR_Generation_NoSafeRoomCell` cost two coordinates. The generator and climate unit place first now; a strip with nowhere to go becomes a standing lamp.

---

## The asset audit the owner asked for

*"check all the assets work, opus did it"* / *"if the lights arent working then wtf other probably too"*. `.local/qa/audit-asset-consumers.py`: **12 textured defs, all 82 textures named** (menu backgrounds load by folder). **Four defs are buildable only and the generator places none** — fluorescent (now fitted), utility generator, emergency cutoff, marker beacon. A coordinate runs on Core's chemfuel set, which is right for the budget and recorded rather than changed.

**Mod register checked for lighting:** nothing in the 294 rows touches lamps or glow; nothing applied.

---

## State, measured

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev** |
| Build | **0 warnings, 0 errors, 200 package files, staged copy matches** |
| Checkers | **33 of 33** before commit |
| Fresh coordinate | 33 rooms · 1,197 strips · 0 wall lamps · 16 standing lamps · 43 pots · 9,056 walls · 202 doors · 1,251 ore cells · no warnings in the log |
| Queue | `TODO.md` still holds: the one welcome letter sent to all three starts, orphaned `RR_Start_Welcome`, no unused-key rule, `rimworld/list_maps` in the shipped allowlist, no instrument that validates a saved campaign · `TEST.md` **56 `[T]`** |
| Forgejo | **held.** GitHub only |

## Is it done?

**No.** The generator's shape is right now and seen; the test phase is still 56 rows. The next session starts by walking a crew through a corridor door and watching the fog, and by sending somebody through a gate from the Async Industries start, which no live run has done since the company validator was fixed.
