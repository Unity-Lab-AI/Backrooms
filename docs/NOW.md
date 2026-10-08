# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase; **"Owner direction — global control"** is the live section |
| **`docs/PLAYBOOK.md`** | **every play order the owner has given, verbatim. §00 order of operations, §01 architecture, §4a global control. Read before playing** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The standing order

**Owner, 2026-10-08, verbatim:** *"you are dsoing test items right you keep getting lost in the game play, set fucking goals foo"*

Prompt **"get the tests all completed"**. No timers (owner: *"telling you not to set timers means exactly that NOT itsa okay to set 1m ones!!!!"*). Never build, stage or edit game files while the game runs.

## ⛔ GOALS, IN ORDER — each one closes a TEST row ⛔

Base-building is done only where a goal needs it. When a goal closes, its TEST row gets the evidence and the next goal starts.

| # | Goal | Closes | Done when |
|---|------|--------|-----------|
| **G1** | **Store gate.** Finish the facility (x157-173, z169-176; gate door `(165,172)`, hall door `(161,169)`, both wooden), move the machining table into the control room, console + battery inside, bind, commission `(165,172)`, assemble, calibrate, console to gate control, remember an address, open a connection | TEST *"Furniture and Knickknack Store opening -- a gate built"* | a connection opens through the Store gate |
| **G2** | **Emergency abort in play** on that connection's load notice | TODO abort row (shipped in source, unproved in play) | the notice reads *"Connection aborted. Nothing was opened, sent or charged."* and nothing was charged |
| **G3** | **Repeat request needs a different address** — repeat a request on the Store gate | TODO repeat-address row | the used address is refused and a new one is required |
| **G4** | **Solo or group, inside** — new colony on that start, a gate built | TEST *"Solo or group, inside -- a gate built"* | a gate stands and operates there |
| **G5** | Store-colony rows that ride along: smokeleaf harvested and **sold** (cash crops), the cow pen closed out, shelves for every resource, trade with every trader | TEST cash crops / corral / shelves / trade rows | each with its evidence |
| **G6** | **Save, reload, revisit** a coordinate on the Store colony | TEST *"Save, reload, revisit the same coordinate"* | map state and rewards persist without duplication |

Everything else open in TEST is launch-gated on the owner (RimSort profiles, DLC matrices, RWT server, art review) and is not mine to close by playing.

## State, measured 2026-10-08

| | |
|---|---|
| Colony | **Store**, save **`rimbridge_save_20261008_store_walls`**, tick ~1,266,700 |
| Facility | walls framing; doors `(161,169)` and `(165,172)` wooden frames; north hall wall still blueprints x170-174 |
| Research | Machining, then Multi-analyzer |
| Branch | **`feature/bug-testing`**, last commit e39cb9b |
| Checkers | **32 of 33** — the stale plant anchors, failing before this session |
| Forgejo | **held.** GitHub only |

## Tools, `.local/qa/`

`play_for` takes **`{"durationMs":N,"speed":"Superfast"}`** — `ticks` is rejected and the game does not move. `keys.py --esc` drops a live designator. `terrain-map.py x0 z0 x1 z1` maps walls/doors/frames (`o` there is a frame or plant, not a hole). Right-click an Architect material button for its material menu (no limestone door is offered — wood).
