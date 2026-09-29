# NOW — Current Focus Snapshot

**Single-focus tracker.** One thing in flight at a time. The "what is Unity actively working on right this moment" file. Distinct from the three-tier task ledger:

| File | Grain | Scope |
|------|-------|-------|
| `docs/ROADMAP.md` | MAJOR | High-level phases / milestones (multi-session, multi-PR) — layered onto the project's Stage 0–6 development roadmap |
| `docs/TODO.md` | MINOR | Day-to-day work queue (everything pending + in-progress) — the working slice of the master backlog in `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` |
| `docs/DECOMPOSED.md` | DECOMPOSED | Smallest meaningful execution unit (one file edit, one command) |
| **`docs/NOW.md`** (this file) | **CURRENT** | **The ONE task currently in motion — the active context** |
| `docs/FINALIZED.md` | ARCHIVE | Permanent record of every completed task |

LAW #0 applies: every snapshot of the active task preserves the user's verbatim words from the request.

---

## Active

**Nothing in flight.** The last checkpoint is published and the tree is clean. This section is a handoff, written deliberately for the session that picks up after a compaction.

### State at handoff

| | |
|---|---|
| Branch | `feature/connected-colony-portals` |
| Published commit | `68b64ec` — 0.5.4-dev |
| Remotes | `forgejo` and `github`, both with `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` all at `68b64ec` |
| Working tree | clean, 0 changes |
| Build | 94 C# source files, 76 approved package files, zero warnings, zero errors |
| Assembly | SHA-256 `FA88C94730F13AB09CD49F52C5C1A39236D640BADC2533C6D4DE51209A17F3F9`, reproduced by a second deterministic build |
| Register | 27 open, 2 owner-blocked, 29 built (`DEFERRED.md`) |
| Game launches | **none, ever.** Every runtime claim in this repo is pending the owner's first RimSort launch |

### What exists now, in order of arrival

- **0.4.2-dev** — remembered gate addresses, legacy threshold repair, the ordinary crossing job, laboratory session controls, emergency return, unresolved-crossing reconcile surface.
- **0.4.3-dev** — the owner's gate traversal rule at one chokepoint (`PortalTraversalPolicy`): inhabitants and monstrosities never cross on their own; anything else rides only in a carrier's hands.
- **0.5.0-dev** — the cross-map work engine: saved work intents, planning leases, bounded route cursors, the adapter contract, and the first family (**storage hauling**, both directions).
- **0.5.1-dev** — a deferment audit that closed **nine** rows, seven of which were blocked on nothing and three of which had already shipped. Added natural-gate discovery by survey, container delivery destinations, observed remote allowed areas, and a bound on the crossing-receipt archive.
- **0.5.2-dev** — **casualties and remains**: our own downed people carried home to a bed, our dead to a grave or storage.
- **0.5.3-dev** — **construction supply** (material carried into a real frame or blueprint), plus an audit proving the mod requires nothing but base Core, plus the capability-matching method that dissolved the M2 content blockers.
- **0.5.4-dev** — four owner decisions: the laboratory duration ladder, natural-gate exemption confirmed, one tech tree for every scenario, and a player-named company.

### The next task, already designed — travel-to-work intents

**Owner-selected.** Every family so far is fetch → carry → deliver. Construction *finishing*, and any work done at the far site with nothing carried, is a different shape and needs a new intent, not another adapter. Building it inside a family would put it in the wrong place.

The design, so it does not have to be re-derived:

- **A deployment intent.** A worker crosses *because qualifying work exists over there*, and the intent exists only to justify the crossing and to stop thrash. Without it the shape oscillates: cross, find nothing, cross back.
- **Shape.** Either a new `ConnectedWorkPhase.Deployed` on `ConnectedWorkIntent` with no `SourceThing` and a recorded work-type defName, or a sibling record. If the existing record is reused, note that `ValidateSavedState` currently requires a `SourceThing` for `Planned` — a deployment must be exempted explicitly rather than by accident.
- **Candidate predicate, explicit-map as always.** For construction finishing: does the far map hold a player-faction `Frame` with work remaining, not forbidden to the player faction, not fogged? That is a fair question about a map nobody stands on. **Do not** ask Core whether a work giver has a job there — the remote-probe prohibition still applies.
- **On arrival, do nothing.** Core's own `WorkGiver_ConstructFinishFrames` picks the work up locally. The deployment intent holds the worker there rather than issuing work itself.
- **Release** when no qualifying work remains on that map, or the lease expires. Then the worker is simply free: a pawn already across legitimately stays there with its own needs and local work, per the portal contract. It must not be dragged home.
- **Anti-thrash** reuses what exists: the per-worker planning cooldown, the per-destination refusal memory, and `MaximumCrossAttempts`. Do not plan a deployment for a worker already standing on a map that has qualifying work.

After that, in order: **bills and unfinished work** (deliver selected ingredients to a real bill giver, keeping the actual bill and unfinished-thing references), **research**, **tending across a gate** (needs medicine-as-cargo), **food**, **rest**, then the remaining families.

### Invariants — do not break these

Hard-won, each one the result of a real defect or a pinned source fact. They are recorded in `implementation/CONNECTED_WORK_IMPLEMENTATION.md` and `implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md`.

1. **`PortalTraversalPolicy` is the only chokepoint.** A colonist may decide to cross to do a job. An inhabitant may never decide anything about a gate. Nothing may reintroduce autonomous non-player traversal.
2. **Two halves of validation, never merged.** An adapter's candidate half runs against an explicit `Map` and may never call a native `HasJob`/`JobOn` remotely, nor claim a pawn-specific or allowed-area result for a map the worker is not standing on. The definitive half runs only on arrival.
3. **A bounded search that ran out of budget is *pending*, never "no route".**
4. **Every bounded scan is a rotating window, never a prefix.** A prefix starves the fifth connected map forever and looks identical to correct code until a fifth gate opens. The rules live once, in `ConnectedWorkScan`.
5. **Two work givers per family** — a high-priority one that only finishes committed trips, a low-priority one that only starts them. One giver cannot be both.
6. **Nothing is ever `playerForced`.** Automatic work must not bypass a policy the player set.
7. **No quantity is ever hardcoded.** Every count goes through `MaxStackSpaceEver` / `GetCountCanAccept`, which is why stack-size mods work for free.
8. **No new gameplay ThingDef, art or audio.** Behaviour is patched onto Core objects and designated at runtime. Match by *capability*, never by name — that is the standing method.
9. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere; a missing def is an unavailable action, never an exception.
10. **Natural gates have no timer, operator, power or close command.** Ever. Non-corporation starts depend on it.
11. **Never force-push. Never launch the game. Never alter the RimSort list. No AI attribution anywhere.**

### Recent owner decisions that are binding

Full text in `GATE_0_DECISIONS.md` under the 2026-09-28 heading, and in `DEPENDENCIES_AND_CAPABILITY_MATCHING.md`.

- **Laboratory duration is a ladder**: 108,000 ticks first (~30 real minutes at normal speed), ×3 per earned tier, no countdown at the indefinite tier — where it still requires power, operator and a successful energy debit every tick. Tier counts **completed projects**, never spendable insight.
- **Natural gates stay permanently open.** Confirmed in source; nothing changed.
- **One research tree for every scenario.** No research, capability or duration rule may be gated on scenario identity. Every start can reach a self-built laboratory gate and a full company.
- **Every company is named by its player**, on every start, renameable any time.
- **Inside start**: configurable party; and the **player chooses the first exit destination** — this *changed* the old provisional assumption of a fixed reveal, so the scenario must implement a choice.
- **Deferments are audited, not appended to.** The four audit questions are in the header of `DEFERRED.md`; ask them every time that file is touched.
- **Validation**: keep building, launch later. No QA pass scheduled.

### Read these first, in this order

1. `docs/NOW.md` (this file) — where things stand.
2. `docs/DEFERRED.md` — every open row with its named owner, and the four audit questions in its header.
3. `docs/implementation/CONNECTED_WORK_CORE_API.md` — the pinned Core job, reservation, carry, area and spawn facts every adapter depends on, **including its appendix on Core's own map-portal system and why it cannot serve this design**.
4. `docs/implementation/CONNECTED_WORK_IMPLEMENTATION.md` — the engine and the invariants above.
5. `docs/implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md` — the audited zero-dependency position and the capability-matching method.
6. `docs/CONNECTED_COLONY_PORTALS.md` — the governing contract, including the traversal rule and the duration model.
7. `docs/PUBLISHING.md` — the exact push procedure. Follow it literally.

### The checkpoint ritual

1. Read every file in full before editing it.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — must be zero warnings and zero errors.
3. Bump `About.xml` and the csproj together; add a `CHANGELOG.md` entry in plain language.
4. Write the implementation record and an evidence folder under `docs/implementation/evidence/<name>-<date>/` with compiler output plus source, package and **recomputed** reference manifests.
5. Update the ledger: `DEFERRED.md`, `TODO.md`, `NOW.md`, `DECOMPOSED.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`, `ARCHITECTURE.md`, `SKILL_TREE.md`.
6. Verify: XML parses, every referenced `RR_` key resolves, every relative doc link resolves, no attribution strings, and the rebuilt assembly hash **matches the recorded evidence**.
7. Commit once, atomically, then push the feature branch and cascade by refspec to `Prep`, `Develop`, `Main` on **both** remotes, then read back all eight refs. Do not edit anything after the push.

### Practical gotchas learned the hard way

- **Long bash heredocs fail** on apostrophes and quotes. Write a `.local/*.py` file with the Write tool, run it, delete it.
- **`cd` inside a Bash call persists** and moves the working directory. Use absolute paths.
- Python cannot open `/c/Program Files (x86)/...`; use the `C:\...` form.
- Package manifests are UTF-8 **with BOM** — read with `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe`; pipe through `head` **only after** writing the file, or the output truncates mid-statement.
- Assembly string literals are UTF-16 in the DLL; a UTF-8 byte search gives false negatives.
- C# 7.3: no target-typed conditionals. `AcceptanceReport` and `bool` will not unify in a ternary.

### Genuinely blocked on the owner

Only two rows remain, and neither is a decision:

- **Every runtime-acceptance row** across M1–M6. Needs the owner's RimSort launch of the 295-entry target. The agent never launches the game.
- **Balance review of the work-giver priorities** set for connected hauling, casualties and construction. Needs play to judge feel.

---

## Next up (from the cascade)

**Immediate:** travel-to-work intents, per the design above. Then bills and unfinished work, research, tending across a gate, food, rest, and the remaining work families — one at a time, each with source evidence per route.

**Then** M1 step 5 (the saved bounded escalation ladder before any inhabitant generation ships, procedural inhabitants, optional provider adapters) and step 6 (connected-site scheduling and streaming).

**Then** M2 existing-content replacement, now unblocked on content grounds by capability matching — remaining work there is implementation plus the save-migration decision, which is shared with the legacy threshold repair already built. Then M3 breadth, M5 interface, M6 release.

---

## How to use this file

1. **When starting a meaningful task** — populate the Active section with verbatim user request + goal + files
2. **During work** — update Files Touched + Verification Plan + Blockers as state shifts; this is a living snapshot
3. **When finishing** — append the closure to `docs/FINALIZED.md` (per FINALIZED-BEFORE-DELETE LAW), then reset the Active section back to _(none — no work currently in motion)_
4. **Never delete the Active section structure** — the placeholder lines stay; only the content shifts

The file always has exactly one Active section. When it says _(none)_, the bridge stream is idle and Unity is awaiting next direction.

---

## Why this file exists alongside TODO.md

`TODO.md` is the queue — everything pending + in-progress, grouped by section. It can hold dozens of `[~]` items if multiple parallel threads are open.

`NOW.md` is the lens — ONE task, all the context, no scroll. Useful when:
- Session resumes after compaction and you need the "where were we" anchor in 10 seconds, not 10 minutes
- The user asks "what are you doing right now" mid-task
- A pre-compact snapshot needs to capture exactly one current context (not the whole TODO queue)
- The harness hooks want a single-task pointer for the state-refresh banner

Read `NOW.md` first for "what's happening", then `TODO.md` for "what's queued", then `ROADMAP.md` for "where are we headed".
