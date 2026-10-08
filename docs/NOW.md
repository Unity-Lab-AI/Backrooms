# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase; **"Owner direction — global control"** is the live section |
| **`docs/PLAYBOOK.md`** | **every play order the owner has given, verbatim. §4a is global control. Read before playing** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The standing order

Watchdog cron `*/1 * * * *`, prompt **"get the tests all completed"**. Dies with the session; re-arm it the same way.

## What this session did

**The freezer coolers, a mod defect.** `RR_AsyncIndustriesStart` put the freezer's four coolers in the east wall at rotation 0; decompiled `Building_Cooler` cools `South.RotatedBy(rot)` and does nothing unless both sides are open, so they never cooled. Def now rotation 1; `check-start-layout.py` fails any cooler with a blocked side or its blue side outside. Built and staged; the colony's own four were rebuilt facing east at 16 F.

**The colony:** leader Gee (*God Almighty*), moral guide Unity (*Lord*) at a ritual spot `(158,147)`; two trades (exotic caravan, combat supplier by comms console); 10,000 company silver ordered; an applicant requested; stun batons and pain sticks as sidearms on all three; stonecutter on Forever; freezer zone takes animal corpses; ~60 old letters dismissed. Save: **`rimbridge_save_20261007_before_payonce`**.

**Gee, Scar and Unity are all age 14** -- no romance, no children until an adult hire. Visitors offer *"Invite to stay (No guest beds)"*: guest beds are the recruiting route.

## ⛔ OPEN, IN ORDER ⛔

1. **Repeat requests need a different gate address** (TODO, owner's answer verbatim there).
2. **The stone wing** is built in limestone (hall x156, cross hall z115, four bedrooms, nursery, guest room). Still: the east bedroom vent at `(157,124)`, pawns assigned to the double beds, guest beds set for guests. The fence pen east of it (x165-176, z111-119) was blueprinted while the owner stopped the call -- ask before keeping it.
3. **Six wild muffalo marked to tame** for milk; a pen once the owner says where.
4. **Stray double bed at `(107,168)`** in the river: deconstruction designated; then *Remove foundation* on the bridge under it.
5. **Research:** Microelectronics, then Multi-analyzer and the computing line, building each as it lands; hi-tech research bench.
6. **AI-03** second opening; Misha and Feeb home. **Raid** the one-defender outpost. **Antibiotics.**
7. **Wiki / mod register:** 195 of 297 mods read "not yet confirmed in a running game" -- update from the runs (TEST row).

## Tools added, `.local/qa/`

| Tool | Use |
|---|---|
| `keys.py --clear N` / `--esc` | real key presses: numeric fields (unicode typing does not reach them) and Escape, which drops a live designator that `press_cancel` does not |
| `terrain-map.py x0 z0 x1 z1` | character map: walls, doors, rock, trees, chunks, blueprints |
| `blueprints.py x z w h` | blueprints, frames and solids per cell |

**Rotated placement** needs a real click: select the designator, press `E`/`Q` via `keys.py`, centre the camera on the cell, click the screen centre. `apply_architect_designator` ignores rotation.

## State, measured

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev**, built and staged, hash-checked |
| Checkers | **32 of 33** — the stale plant anchors, failing before this session |
| TEST | **73 `[T]` rows open**; ~15 closed in the last 6 hours |
| Forgejo | **held.** GitHub only |
