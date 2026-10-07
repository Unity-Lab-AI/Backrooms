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

**The AI-01 onboarding survey was played from dispatch to payout: "AI-01 onboarding survey — Completed".** Four requests paid on the way. Account **69,481,860 USD**.

**Three mod defects stopped it, each found in the running game and fixed, built, staged and seen working:**

| Defect | Seen after the fix |
|---|---|
| Expedition windows were a flat 833 ticks, twenty in-game minutes, while the page quoted 129.6 hours | *"Opening time: 7776 in-game minutes remaining"* |
| A built gate's door lost every control after *Watch* | *Linked equipment*, *Open a connection*, operator controls and the rest back on the door |
| Analysis needed the record on the shelf and in the analyst's hands at once | 0 % → *"Analyzed; analysis 100 %"* |

**And the earlier battery fix is three of four seen:** with seven generators fuelled and the gate open, the net read +695 W and every battery held at 600 / 600.

**Built for the colony:** three wood-fired generators (seven total, +3.9 kW with the gate closed), a butcher table, the archive link, the cook bill at 50.

## The colony

**`rimbridge_save_20261007_survey_analyzed`** — the latest. Gee, Scar, Unity all home and fed. The archive is the shelf at `(159, 141)`, Books only, Critical.

## ⛔ OPEN, IN ORDER ⛔

1. **The Quiet Pursuer never spawns** (TODO). Placement only accepts a room that reaches the crew without opening a door, and every corridor leg has a door since `bcf0701`. **A design fork for the owner — how should the chaser path?** Blocks the optional entity observation and the first real threat test.
2. **"Report a disagreement"** is the next request on the table — the two-witness accounts mechanic.
3. **The battery `[T]` row's last check:** the connection closing at the emergency-return floor.
4. TODO: the first-room-only survey rule, the identical-row link menu, three stale plant anchors (32 of 33), the DefInjected gate recipe text.
5. **The play brief, per `PLAYBOOK.md`:** shelves, a vault, the prison, guest beds, defences, the *Galaxy* sculpture and the empty Lord role the ideoligion keeps alerting on. Gee no longer hunts, so Construct comes first for him.

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
