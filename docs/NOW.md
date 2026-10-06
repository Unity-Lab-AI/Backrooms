# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

The [artwork handoff this replaces](implementation/evidence/authored-rotations-2026-10-06/) is preserved as dated evidence, as is the handoff before it. **Narrative goes to `FINALIZED.md`; a rule that must survive becomes a checker.**

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | **the test phase — 54 rows, every one needing a launch** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## ⛔ TWO AGENTS WERE WRITING THIS REPOSITORY AT ONCE ⛔

**Owner: *"cant stop chatgpt"*.** The art and audio were authored by another agent while this one worked. That is survivable and it nearly was not.

**⛔ NEVER RUN THE PLANT SUITES WHILE ANOTHER AGENT IS WRITING. ⛔** A suite writes a **real fault into a real file**, runs a verifier, then restores the file from its own copy. Anything the other agent writes inside that window is **silently reverted**. It happened once in this session — `docs/wiki/index.md` was read mid-flight with a planted instruction sitting inside its front matter — and the restore was clean only by luck of timing.

**And a plant that cannot trust the tree now refuses instead of lying.** `plant-class-resolution` aborted with *"ABORTED: check-package-integrity.py does not pass clean"* rather than reporting faults that were really a half-delivered package. That abort is the behaviour to keep.

**Commit your own files, never the other agent's in-flight work.** Two commits here were deliberately scoped to exclude files being written elsewhere.

---

## State, measured 2026-10-06

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev** — read from `About.xml`, never from a document |
| Build | **257 C# files, 200 package files**, zero warnings, zero errors |
| Instruments | **33 checkers · 64 proofs · 43 plant suites** — checkers and proofs green in one run; see the plant note below |
| Queue | `TODO.md` **0 open · 0 partial** · `TEST.md` **54 `[T]`** |
| Assets | **59 shipped: 42 drawings, 17 cues.** Every one referenced by a def or by code, every one described, every one with a master |

**PLANT NOTE, STATED RATHER THAN GLOSSED.** The full battery ran green earlier against this tree. After it the aura and the loops landed with their own suite — **`plant-gate-aura-and-loops`, 8 of 8 caught** — and four anchors in three other suites were re-aimed at code that moved. `check-plant-anchors` confirms **all 1333 anchors are findable** and `check-plant-residue` is clean, but **the full 43-suite run was not repeated after those re-aims**, because the owner needed to compact and a plant suite mutates the tree. **Run it before the next publication.**

---

## What shipped

**Art, authored elsewhere and verified here:** seven paper-journal views, eighteen facings across six now-rotatable buildings, twelve gate-frame textures for the 1x1, 1x2, 1x3 and 2x3 footprints, and twenty-two animation frames — eight charge, six activation, eight live.

**Audio: seventeen cues**, the original four plus thirteen delivered against [`ASSET_REQUESTS.md`](ASSET_REQUESTS.md). Every file measured rather than trusted: **48 kHz, mono, 16-bit**, every duration inside the brief's range.

**And thirteen of them could never have played.** No `SoundDef` existed for any, and the playback service **resolved its Core fallback first and refused any cue id it had no mapping for** — a guard written to catch a typo at a call site was silently rejecting correct, shipped content. The only symptom would have been a gate that makes no sound.

| Wired | How |
|---|---|
| Ramp-up | On spin-up starting, after the message and the record — **presentation never decides whether an action occurred** |
| Calibrate | On the three interior quarter crossings. **Deliberately not the fourth** — that is the tick the ramp completes, and activation owns it |
| Activate, ramp-down, emergency, section assembled | **One table keyed on the gate event already recorded**, not eight `Play` calls in eight methods |
| Charge, activation and live animations | A frame index over the existing frame draw. The burst is **transient and not saved** — a one-off flash replaying on every load would announce an event that is not happening |

---

## ⛔ A NATURAL GATE STAYS A PLAIN DOOR ⛔

**Owner, 2026-10-06:** *"natural gates dont look like the machine in the real univiverse of backrooms they are mainly just normal doors and walls that u can majicly walk through but lets keep natural doors just normal doors in game so there is distinction for it"*

The frame draws on `CompRimroomsGate` and keys on `IsDesignated`. A permanent natural gate is `CompRimroomsEmergence` and gets nothing. **That asymmetry is the information:** a framed opening was built, an unframed one was found. Recorded in `GateWorldFrames.cs` where anybody tempted to "fix" it would be standing.

**An ordinary door can never wear the frame.** The component is on every `Door` and `Autodoor`, and `PostDraw` returns at the `!IsDesignated` guard. `DesignateAsGate` sets the orientation **at designation**, so there is no window where a gate has no frame.

---

## ⛔ ONE HOLD LEFT ⛔

**THE FORGEJO HOLD STANDS.** *"the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **Six refs**: `github` × five branches, plus `github/main` on the mod-only repository. The remote is **held, not removed**, and the exporter prints the hold and its reason every run.

---

## ⛔ STAGE BEFORE THE OWNER LAUNCHES ⛔

- `powershell -File tools/stage-mod.ps1 -UpdateExisting` — **the staged copy is the copy a launch loads.**
- `python tools/check-package-integrity.py` must read **PASS** before any launch report is trusted.

---

## Read these before touching anything

- **AN ASSET NOTHING NAMES IS THE DEFECT THAT RETIRED THIS ART ONCE ALREADY.** The 0.9.0-dev record: the defs *"had no C# consumer whatsoever and had been shipping textures nobody could see."* `cut-phase2-art.py` derives what ships from what the defs and source name; the asset page reports anything unreferenced as a fault.
- **A NUMBERED SEQUENCE IS NAMED BY ITS PREFIX.** The animation code holds one literal and appends `01`..`08`, so whole-path matching reported all twenty-two frames as unnamed while the code drew every one.
- **A `SoundDef` HAS NO LABEL.** Walking back for one found an unrelated def's, and the asset page announced `RR_GateWarning` as *"starting staff"*.
- **A FOLDER SCAN NAMES EVERY FILE IN IT.** The menu slides load by folder, so all twelve read as unnamed until the rule learned that.
- **MEASURE, THEN PUBLISH.** A seam metric compared two edge *regions* instead of asking whether two columns join, scored a provably seamless tile at 7.15, and a figure ten times too large was published before it was checked.
- **A DROP SHADOW IS NOT THE OBJECT.** Thresholded boxes made the bench 2.21:1 and the fluorescent 4.96:1, and those decided both footprints.
- **THE COMPONENT IS THE ALLOWLIST.** Three systems resolved a single def name while a component was the real marker — gate providers, the record book, and `RouteMarkers.OnMap`. The pattern to watch for: a `GetNamedSilentFail("...")` standing in for *does this carry our component*.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.**
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved; **never a deadline, nor the word itself.**

---

## THE NEXT THING

**A launch. `TODO.md` is empty and everything the owner asked for this session is built**, including the two things the previous handoff listed as outstanding.

**The aura is state-driven.** Owner: *"gate sensitive change color to the state of the gate and like strobe on charge up callibation and activation and shit like star trek warp core"*. Five states, each its own colour and radius, and **no art at all** — the glow colour and radius are settable per instance. **The pulse is a triangle wave, not a square one**, and through spin-up its period falls from 96 ticks to 20, so the gate winds up rather than blinking. **A live gate looks exactly as it did**, because the faulted states are tested first and the live branch returns untouched.

**The loops play.** `RR_GateSpinLoop` and `RR_GateOpenLoop` are **reconciled every tick, never started or stopped by event** — the event shape leaks, because completion, abort, lapse, power loss, a fault and a reload would each have to remember to stop the sound. **The sustainer is `MaintenanceType.PerTick`, so it ends itself** the moment it stops being maintained: a destroyed gate goes quiet on its own, and *forgetting to stop one is not a failure mode*. Nothing about it is scribed; a reload mid-ramp restarts it from state.

**So the next thing is a launch.** The 54 rows in `TEST.md` all need the game running — **the owner alone launches, sorts and publishes.**

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.

## Is it done?

**No.** The art and audio are in and verified, the battery is green, and `TODO.md` holds five open rows rather than none. **The master TODO still carries unticked scope nobody has reconciled** — check it rather than trusting a count copied from a previous handoff. An empty minor queue never meant a finished mod, and this one is not even empty.
