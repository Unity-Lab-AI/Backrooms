# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase, and the owner's play brief at the top of it |
| **`docs/PLAYBOOK.md`** | **every play order the owner has given, verbatim, and §9 the survey procedure. Read before playing** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The standing order

**Owner, 2026-10-07, verbatim:** *"wtf keep fucking playing and set a watch dog so if u stop thinking idel for 1 minute we get woken with \"get the tests all completed\""*

The watchdog is a session cron: `*/1 * * * *`, prompt **"get the tests all completed"**. It dies with the session; the next session re-arms it the same way.

## What this session did

**Shipped and seen in play:** expedition windows on the ladder (*"Opening time: 7776 in-game minutes"*), a built gate's controls restored, analysis that can finish (AI-01 *Analyzed 100 %*, survey **Completed**), the catalogue selling again, a case for every coordinate (AI-03 took a crew), and the battery fix three of four. **Shipped, not yet seen:** the Quiet Pursuer retired with sightings from any stranger, depth-scaled encounter numbers, one journal per job.

**Money:** every request the company names has paid -- account about **87.6M USD**. *Choose a direction* ($10M) has its write-up filed; its journal `RR_RouteRecording1001822` sits in Unity's pack and goes to the **credit beacon at `(135, 139)`**.

**The colony** (`PLAYBOOK.md` §3 has the room plan): freezer and every room's shelves set by copy/paste, shelves one priority above each stockpile; hospital; prison barracks; records desk; Smokeleaf zone; seven generators.

## ⛔ OPEN, IN ORDER ⛔

1. **Drop the stamped journal in the credit beacon's radius** and watch *Choose a direction* settle.
2. **Raid the one-defender Cuvin Flamehome outpost** (world map, north-west of home) with three rifles; bring the defender home to the prison barracks.
3. **Antibiotics:** research, a drug lab, penoxycyline every 5 days on every pawn's drug policy -- the owner's direction in `PLAYBOOK.md` §4.
4. **AI-03 survey**, second opening, to see a stranger recorded as the entity observation.
5. TODO: AI-02's failed layout, the link menu's identical rows (and moving the records archive off the freezer shelf `(159, 141)` to a lab shelf), the first-room survey rule, three stale plant anchors.

## Tools added this session, all in `.local/qa/`

| Tool | Use |
|---|---|
| `explore-to.py <pawn> x z w h` | walks a drafted pawn into a room through fog. **Undraft between legs — drafted pawns do not eat** |
| `gizmo.py x z "<label>"` | runs a selected thing's gizmo by label; float-menu gizmos still need a pixel click after |
| `battery-read.sh` | each battery's stored charge off its own pane |
| `find-things.py`, `designate-cells.py`, `dispatch-crew.sh` | map search, designations over a cell list, empty-hands dispatch |

**`select_pawn` switches the current map**; `jump_camera_to_pawn` does not cross maps.

## State, measured

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev**, 0 warnings, 0 errors, staged copy hash-checked |
| Checkers | **32 of 33** — the stale plant anchors, failing before this session |
| Forgejo | **held.** GitHub only |

## Is it done?

**No.** The survey loop is proven end to end; the threat half of it cannot run until the pursuer can spawn.
