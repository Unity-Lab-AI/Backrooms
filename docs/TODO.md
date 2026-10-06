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

### Owner direction — the gate should look and sound like it is doing something (2026-10-06)

**Verbatim owner direction (2026-10-06):** *"an make a write up about any other audio we need for chatgpt to find and create"*

**Verbatim owner direction (2026-10-06):** *"and things like the gates activating animations and charge up and stuff"*

**Verbatim owner direction (2026-10-06):** *"can be still frame made into gif like thing or whatever the game needs"*

**Verbatim owner direction (2026-10-06):** *"and maybe have the auro for the gat be gate sensitive change color to the state of the gate and like strobe on charge up callibation and activation and shit like star trek warp core"*

### Owner decision — a natural gate stays a plain door (2026-10-06)

**Verbatim owner direction (2026-10-06):** *"remmebr natural gates dont look like the machine in the real univiverse of backrooms they are mainly just normal doors and walls that u can majicly walk through but lets keep natural doors just normal doors in game so there is distinction for it and long time in the future if mod ever pics up in popularity we can add stuff like that"*

**This closes a gap that was reported as a defect.** The machine frame draws on `CompRimroomsGate` and keys on `IsDesignated`, so a permanent natural gate — the other component — gets nothing. **That asymmetry is the information:** a framed opening was built, an unframed one was found. The decision is recorded in `GateWorldFrames.cs` where anybody tempted to "fix" it would be standing, and in `gates.md` where a player reads it.

> **The post-completion test phase lives in [`TEST.md`](TEST.md) as of 2026-10-06.** Owner:
> *"we should make a seperate todo=Test.md and move all test items to it to be done and clear
> todo , if its true all items are done."* It was true: this file reached zero open and zero
> partial, so every `[T]` row moved out whole. **`[T]` must not reappear here** — a row waiting on
> a launch belongs in that file, and a row that turns out to be buildable comes back as `[ ]`.

## TOMBSTONES

_(none)_
