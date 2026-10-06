# TODO — Minor Task List (Active Tasks)

**Tier 2 of 4** — the MINOR task list. Holds active tasks (pending + in_progress) at the day-to-day work grain. Each minor task lives under a major milestone in `docs/ROADMAP.md` and decomposes further into entries in `docs/DECOMPOSED.md` when YOLO mode picks it up.

**It holds buildable work only.** Rows that cannot be closed without the game running live in [`TEST.md`](TEST.md) since 2026-10-06.

Completed tasks move to `docs/FINALIZED.md` per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`. Never delete a task description; only flip status (LAW: NEVER DELETE TODO INFO).

Status markers:
- `[ ]` pending
- `[~]` in_progress
- `[x]` complete (move to FINALIZED.md immediately, never leave here)
- ~~`[T]`~~ **moved out 2026-10-06. It must not reappear here** — see [`TEST.md`](TEST.md)

**There is no blocked-on-owner status, by owner direction 2026-09-28.** Nothing here waits on the owner. Runtime rows are `[T]` and live in [`TEST.md`](TEST.md), one named phase that begins only once the mod is complete.

LAW #0 reminder: every task description preserves the user's verbatim words.

**Four-tier cascade:** ROADMAP.md (major) → TODO.md (minor, this file) → DECOMPOSED.md (decomposed), with [`TEST.md`](TEST.md) alongside for everything that needs a launch. The first three are the build cascade and YOLO works them; the fourth is not buildable by anyone here — see `.claude/commands/yolo.md` and `.claude/WORKFLOW.md §YOLO MODE`.

> **Live project TODO for Rimrooms - Async Industries.** Seeded 2026-09-28 when the Claude Code workflow took over from the previous build agent (ChatGPT 6 Astra). This file carries **every open item** of the complete mod backlog, quoted verbatim from [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) (the "master TODO"), grouped under the majors in `ROADMAP.md` and in the master TODO's own order. The master TODO stays the authoritative gate/evidence record; when an item here closes, tick the identical bounded subitem there in the same change with its evidence link, per `REGRESSION_CONTAINMENT.md`. Items whose source already exists but whose runtime acceptance is open stay `[ ]` — the master TODO's rule: *"Unchecked tasks below retain their full stated implementation/acceptance scope; they do not mean all referenced source is absent."*
>
> Owner sequencing override (2026-09-28): implement remaining systems while game testing is deferred; gameplay-gate statements govern acceptance/promotion, not permission to write source. Only the owner launches RimWorld, through RimSort.

---
## Pending

### From the live session, 2026-10-06 — found by watching rather than by being told

**Verbatim owner question (2026-10-06):** *"have you been paying attention?"*

**Everything below came out of the owner's running game through the bridge and the log.** The owner reported none of it and was not asked to. **Nothing here is built while they are playing** — a rebuild re-stages the package under a live session and makes the staged copy disagree with the running one.

**Session facts, measured:** `0.13.0-dev` loaded — today's build, so the sort and save landed. Scenario `lone_survivor`, seed 1969031978, 3 colonists, 2 maps, tick climbing past 1346. Fixture tells attached to 1802 definitions, odd-origin marker to 2769.

- [ ] **ONE WELCOME LETTER IS SENT TO ALL THREE STARTS, AND IT DESCRIBES A FACILITY AND A GATE THAT TWO OF THEM DO NOT HAVE.** `ScenPart_RimroomsStart` sends `RR_Start_WelcomeTitle` + **`RR_Setup_Welcome`** unconditionally, with no branch on `startDef`. On the `lone_survivor` start the player is told *"The fixed facility is separate from those supplies"* and to *"complete the gate and prepare a real return route"* — and `scenarios.md` says that start has **"None, and no facility"**. The owner read that letter this session.
- [ ] **AND THE RIGHT TEXT ALREADY EXISTS WITH NO CONSUMER.** `RR_Start_Welcome` is declared in `RR_Scenario.xml` and **no C# file names it**: *"Your Async Industries branch is operational. The gate is still incomplete."* So the Async-specific welcome was written, shipped, and never sent, while the generic one goes to everybody. **This is the third instance today of content with no consumer** — after five sound cues and the gallery pictures — and `check-keyed-strings.py` has **no unused-key rule at all**, so an orphaned keyed string is invisible exactly as an unplayed cue was.
- [ ] **A GENERATED CLUE CANNOT BE REACHED, reported by our own code in the live game.** Verbatim: *"the clue Gold in room 32 at (123, 0, 176) has no reachable cell beside it, so that one room's evidence cannot be collected. The space, its gate anchor and its way home are unaffected."* The bound is honest and the warning is good; the room still loses its evidence, so a player can survey it and get nothing.
- [ ] **A LAMP IS PLACED OFF THE POWER NET.** Verbatim: *"generated with an incomplete native power grid (WallLamp is not on the generator's power net). The space, its gate anchor and its way home are unaffected."* A light that can never light.
- [ ] **`rimworld/list_maps` DOES NOT EXIST ON THIS BRIDGE, and it is in the shipped client's allowlist.** `tools/qa/rimbridge_readonly.py` lists `maps` in `READ_TOOLS`; the live bridge answers *"Tool 'rimworld/list_maps' not found"*. It failed **50 times in one session**. Either the name changed or it never existed — `rimworld/list_zones`, `list_areas` and `get_game_info`'s own `mapCount` are what the live bridge offers.
- [ ] **605 OFF-THREAD RESOURCE ERRORS IN THE SESSION, AND I NEARLY REPORTED THEM AS TODAY'S FAULT.** Verbatim, repeating: *"Tried to get a resource "lock" from a different thread. All resources must be loaded in the main thread."* **The first one lands immediately after our own `[Rimrooms][Company] Initialized ... scenario=lone_survivor` line**, which looks like a smoking gun and is not one. **Yesterday's 0.12.99-dev session has 580 of the same thing** — so it is pre-existing, it is not today's build, and it is not the watcher, which did not exist yesterday. **The shape is exact and worth keeping:** five resources — `lock`, `unlock`, `UI/Commands/CopySettings`, `UI/Commands/PasteSettings`, `UI/Commands/ChangeColor` — each requested **the same number of times** (121 each today, 116 each yesterday, 5 × 121 = 605). That is **a door's gizmo set, resolved once per door**, during threaded map generation. **It is not us doing the enumerating:** we *provide* gizmos through `CompGetGizmosExtra` on `CompRimroomsGate`, and providing one resolves no icon until something asks — nothing in our source calls `GetGizmos`. The `lock`/`unlock` pair points at a door-access mod in the profile. **Bears on the compatibility rows rather than on a Rimrooms defect**, and the correlation with our log line is an artefact of company init being the last thing written before generation threads.
- [ ] **THE WATCHER'S JOURNAL IS MOSTLY NOISE AND THAT IS MY DEFECT.** 263 records for **one** genuinely new game event. `ping` carries a timestamp and `game` carries a tick, so both differ every sweep and every sweep journals them as *changed*; `colonists` carries operation ids and does the same. And **eleven records are `"No game is currently loaded"`** — journaled as evidence when it is the absence of any. A journal nobody can read is the same failure as a note nobody believes.

## TOMBSTONES

_(none)_
