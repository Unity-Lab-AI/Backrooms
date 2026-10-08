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

**The colony:** leader Gee (*God Almighty*), moral guide Unity (*Lord*) at a ritual spot `(158,147)`; two trades (exotic caravan, combat supplier by comms console); 10,000 company silver ordered; an applicant requested; stun batons and pain sticks as sidearms on all three; stonecutter on Forever; freezer zone takes animal corpses; ~60 old letters dismissed. Save: **`rimbridge_save_20261007_stone_wing`**.

**Gee, Scar and Unity are all age 14** -- no romance, no children until an adult hire. Visitors offer *"Invite to stay (No guest beds)"*: guest beds are the recruiting route.

## ⛔ OPEN, IN ORDER ⛔

1. **The stone wing** (limestone walls blueprinted, x149-163, z105-127): hall x156 off a new door at `(156,128)`, cross hall z115 with exits at x149/x163, four uniform 5x5 bedrooms north (doors x155/x157 at z119, z125), nursery west and guest room east (doors at z109). **Still to place:** every door in limestone, a vent and a light in each room, a double bed + end table + dresser per bedroom in the same spot and facing, guest beds, cribs. Owner: *"think uniformity"*.
2. **Choose a direction ($10M):** relink the gate's records archive from freezer shelf `(159,141)` to a lab shelf, get journal `RR_RouteRecording1001822` onto it.
3. **AI-03** second opening -- a stranger as the entity observation; bring Misha and Feeb home.
4. **Raid** the one-defender Cuvin Flamehome outpost; first prisoner.
5. **Antibiotics**, a cash-crop-to-product chain (smokeleaf joints; devilstrand is researched), a corral and cows.
6. Leader and moral-guide abilities on every cooldown.

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
