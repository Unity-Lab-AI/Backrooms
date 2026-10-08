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

**Pushed `f5202c3`.** Expedition windows on the ladder, a built gate's controls restored, analysis that can finish, the catalogue selling, a case for every coordinate, one journal per job, the Quiet Pursuer retired. AI-01's survey **Completed**; every request the company names has paid -- account **87.6M USD**.

**The colony** (`PLAYBOOK.md` §3 is the room plan): freezer and every room's shelves set by copy/paste, shelves one priority above each stockpile; hospital; prison barracks; records desk; Smokeleaf zone; seven generators. Save: **`rimbridge_save_20261007_rooms_organised`**.

## ⛔ OPEN, IN ORDER ⛔

1. **Choose a direction ($10M) -- the reason it has not paid, found:** `QuestPaperwork.LightFor` turns green only when the journal is in **archive custody** (on the gate's linked *Records archive* shelf), and collection then needs it inside a **credit beacon's** radius. The archive link is still on `(159, 141)`, a **freezer** shelf that no longer takes books. **Do:** gate → *Linked equipment* → release that shelf, link a **lab shelf** (`(130/133/136, 141)`, they take evidence) as *Records archive*; the lab sits inside the credit beacon at `(135, 139)`. Then the stamped journal (`RR_RouteRecording1001822`, most write-ups on it) has to reach that shelf. The link menu's rows carry no positions (TODO), so check which shelf was linked by saving and reading `Thing_Shelf` ids.
2. **Stone chunks: DONE.** All 12 inside the base were hauled out after a long burst -- they had been reserved by Gee, not stranded; the earlier "nowhere to go" guess was wrong.
3. **Raid the one-defender Cuvin Flamehome outpost** (world map) with three rifles; prisoner to the prison barracks.
4. **Antibiotics:** research, a drug lab, penoxycyline every 5 days on every pawn's drug policy (`PLAYBOOK.md` §4).
5. **AI-03 survey**, second opening, to see a stranger recorded as the entity observation.
6. TODO: AI-02's failed layout; the link menu's identical rows, then move the records archive off the freezer shelf `(159, 141)` to a lab shelf; the first-room survey rule; three stale plant anchors.

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
