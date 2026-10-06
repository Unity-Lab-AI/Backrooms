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

### Active portal artwork and code handoff (2026-10-06)

**Verbatim owner direction:** *"what about active portal ones. should you do those to and write an ote to claude in todo"*

- [ ] **Note to Claude — runtime integration:** after the nonlooping `RR_GateActivation_01..06` burst completes, display `RR_GateOpen_01..08` as a slower repeating effect while a **company machine portal's connection is live**. Share one set across every supported footprint/facing and reuse the existing whole-run/fog guards. Stop the effect on closure, loss of the live state, destruction and map unload; derive/reconcile state on reload without replaying activation. Respect the visual disable/reduced-motion behavior, preserve native door leaves/pawns, and keep text/state indicators. **Natural portals stay ordinary unframed doors, without these machine-energy overlays.** This is code work, separate from delivered artwork; do not close it merely because PNGs exist. See the [asset brief](ASSET_REQUESTS.md#live-open-portal-loop).

### Owner direction — the gate should look and sound like it is doing something (2026-10-06)

**Verbatim owner direction (2026-10-06):** *"an make a write up about any other audio we need for chatgpt to find and create"*

**Verbatim owner direction (2026-10-06):** *"and things like the gates activating animations and charge up and stuff"*

**Verbatim owner direction (2026-10-06):** *"can be still frame made into gif like thing or whatever the game needs"*

**Verbatim owner direction (2026-10-06):** *"and maybe have the auro for the gat be gate sensitive change color to the state of the gate and like strobe on charge up callibation and activation and shit like star trek warp core"*

**Verbatim owner direction (2026-10-06):** *"ramp up and down and rev"*

**The brief is written: [`ASSET_REQUESTS.md`](ASSET_REQUESTS.md).** It carries the format rules, the cue list grounded in real code events, the animation shape and the aura palette. These rows are the **code** that has to exist for those assets to do anything.

- [ ] **"and maybe have the auro for the gat be gate sensitive change color to the state of the gate"** — **the aura is one colour and binary today.** `CompRimroomsEmergence` holds a single `LiveGlowColor` of `(70,130,220)` and sets it on or clears it. The gate already computes everything a state-driven aura needs — designated, spinning up with a progress fraction, live, emergency, awaiting recovery — and **both the glow colour and its radius are settable per instance**, so this needs no art at all. **The fairness rule binds it:** `THREAT_DESIGN_SHEETS.md` forbids colour or sound being the only way to notice a tell, so the aura may be beautiful and may never be the only signal.
- [ ] **"like strobe on charge up callibation and activation and shit like star trek warp core"** — the strobe, driven from the spin-up fraction the gate already computes, with a pulse at each quarter. **Live stays the current blue unchanged**, so an existing colony looks the same as it did.
- [ ] **"and things like the gates activating animations and charge up and stuff"**, **"can be still frame made into gif like thing or whatever the game needs"** — **the frame is already drawn by us** in `GateWorldFrames.PostDraw`, so an animation is a frame index rather than a new engine concept, and *"still frame made into gif like thing"* is exactly right: a numbered sequence of PNGs the code picks from. **Author one square overlay sheet, not a sequence per footprint** — four footprints times three facings times six frames is 72 files and every future footprint multiplies it.
- [ ] **"ramp up and down and rev"** — ⛔ **`RimroomsAudio.Usable` REFUSES any `SoundDef` with `sustain` set**, because every existing cue is a one-shot and a sustainer nobody stops runs until the map unloads. So a loop needs a sustainer started on a state change and **explicitly stopped on the opposite one, including on destruction, map unload and a reload mid-cycle** — that is the risky half, not the audio. The four one-shots carry the whole cycle without it.
- [ ] **The one thing the cues have to get right, recorded so it is not lost between the brief and the build:** ramp-up ends **unresolved** and ramp-down **resolves**. That single contrast tells a player whether the gate is becoming dangerous or becoming safe without reading a word.

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
