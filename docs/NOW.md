# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

So: **replace this file, never append to it.** Narrative goes to `FINALIZED.md`. A rule that must survive goes to `.claude/CONSTRAINTS.md` or becomes a checker. Open work goes to `docs/TODO.md`.

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, every owner direction verbatim, **open work only** |
| `docs/DECOMPOSED.md` | smallest execution units, **open only** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

---

## ⛔⛔ TWO HOLDS, BOTH THE OWNER'S, BOTH CURRENT ⛔⛔

**1. Nothing publishes until the launch list is finished.** Owner, 2026-10-06: *"we are not stageing now.md and cascading to all three remotes correctly and properly until we are sure all of this is completed"*. Work is committed **locally only** — the branch sits ahead of every remote on purpose, and **every commit of this session is unpushed.**

**2. Forgejo is down.** Owner, 2026-10-06: *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **The cascade is SIX refs while that stands** — `github` × five branches here, plus `github/main` on the mod-only repository.

**The remote is HELD, not removed, and that distinction is the point.** Deleting it would make every receipt read *complete*, and a future reader would never learn a destination had gone missing. `export-public-repo.py` keeps `forgejo` in `REMOTES`, skips it through `HELD_REMOTES`, **prints the hold and its reason every run**, and **refuses outright if every remote is held**. `PUBLISHING.md` opens with it, including: **do not push to it to test whether it is up.**

---

## ⛔ STAGE BEFORE THE OWNER LAUNCHES, NOT AT PUBLICATION ⛔

**This cost a whole launch report on 2026-10-06 and is the most expensive lesson of the session.** The owner reported the solo start broken; the staged assembly was **02:51** and the build on disk was **23:00**. They tested a DLL twenty-one hours old. `check-package-integrity` rule 10 had already said so — nine differing files — and it was read as an environmental note because the game was open.

- `powershell -File tools/stage-mod.ps1 -UpdateExisting` — **the staged copy is the copy a launch loads.**
- Run it **after the last build and before telling the owner anything is testable.**
- `check-package-integrity` must read **PASS** before a launch report is trusted. It compares every file by content, because **the version is a label and the bytes are what runs.**

**It is staged and PASS as of this writing.**

---

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04:** *"yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes"*, and when I over-corrected: *"you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the one instrument covering the file you just touched.**
- **At publication, once:** 29 checkers → 59 proofs → 36 plant suites → `check-plant-residue.py`. **Then `export-public-repo.py --push`, then commit, then the cascade — and then `curl` the published site.**
- **THE OWNER ALONE LAUNCHES, SORTS AND PUBLISHES.**
- ⛔ **NEVER RUN THE PLANT SUITES CONCURRENTLY WITH ANYTHING ELSE.** A suite writes a real fault into the tree and restores it; anything reading the tree in that window sees the fault. Doing so reported **four failures that did not exist**.
- **THE REGISTER IS AN INPUT TO WORK, NOT A BACKLOG OF IT.** A row's disposition is settled when something is built that touches that mod, or when a launch gives evidence — **never as a bulk sweep**.

---

## State, measured 2026-10-06

| | |
|---|---|
| Branch | **`feature/bug-testing`**, ahead of every remote by owner direction |
| Version | **0.12.99-dev** — read from `About.xml`, never from a document |
| Build | **251 C# files, 106 package files**, zero warnings, zero errors |
| Instruments | **29 checkers**, **59 proofs**, **36 plant suites** |
| Queue | **10 open · 5 partial · 50 `[T]` · 0 `[x]`** — from 20 open at the start of the session |
| Staged copy | **MATCHES THE BUILD.** `check-package-integrity` PASS |
| Launches | **Fourteen.** The fourteenth found the solo start dead on arrival, and the cause was ours |

---

## What shipped this session, and the pattern under most of it

1. **The journal and quest system, eight of nine steps.** Write-up kinds as defs — the owner's ellipsis *was* the specification — the records desk, one-writer-two-readers with a three-state green light, the branch ledger, quest-bound click actions, beacon send-back, and a book per accepted quest.
2. **Exploration.** A drafting-style toggle; the pawn writes each room into the journal for **twenty seconds**, the owner's own figure, and the book is required because an explorer without one is a colonist on a walk.
3. **Cross-map traversal, all seven rows.** Invariant #1 rewritten with **half kept**; outbound crossing for hostiles and friendlies; colonists crossing for a need with the stranding guard at the decision.
4. **The record book's identity.** `CompRouteEvidence.TransformLabel` had existed for versions and **was never called once**, because `Verse.Book` overrides the property that runs the comp chain.
5. **Operator relief.** A station question instead of a pawn question, correcting six call sites in one derivation.
6. **The solo start's way out**, and the **sealed-vault validator** that killed the fourteenth launch.
7. **The crew cap removed**, and the records-bonus defect it was concealing.
8. **Four new instruments.** Checkers 26–29, plant suites 35–36.

---

## Read these before touching anything

- **TWO DERIVATIONS OF ONE RULE IS THE DEFECT THIS PROJECT KEEPS MEETING, and it caused four separate faults this session.** The planner and the layout validator disagreed about a sealed vault and **killed a start**. My own exploration completion and the survey precondition disagreed about the same vault and would have made a write-up permanently unwritable. The gate's readout and its emergency test nearly disagreed about who was at the controls. Custody needed a refactor rather than a copy. **When a second place needs the same answer, extract — never copy.**
- **A CAP CONCEALS THE FAULT BENEATH IT.** `InitialCrew.Count == 3` made the records bonus unreachable for any other crew size, and **with the cap in place no player could easily send four and find out.**
- **MEASURE THE PROVENANCE OF A NUMBER BEFORE DEFENDING IT.** *"dont know where 3 came from"* — it was the start def's staff roster, promoted to a design cap by being written down somewhere else.
- **A CONSTANT DENYING WHAT THE CODE DOES IS A STALE COMMENT WITH A COMPILER BEHIND IT.** `AutonomousNonPlayerTraversalPermitted` was deleted rather than left at false. And a cap of `int.MaxValue` is still a cap somebody reads as a rule: **the absence is the rule.**
- **AN INSTRUMENT THAT CRASHES WHILE REPORTING CANNOT REPORT.** `archive-finished-todo` died printing a heading character, **after** the reassembly identity had held — leaving a half-written report and no statement of whether the move happened. Three queue tools carry the replacing print now.
- **A FILE THAT PARSES IS NOT A FILE THAT WORKS.** My fix for that broke two tools into infinite recursion, because they already had a `say(line)` whose body is `print(line)`. Caught by **running** all five.
- **`--` IS ILLEGAL INSIDE AN XML COMMENT AND I HAVE NOW WRITTEN ONE FOUR TIMES.** `check-package-integrity` already names the file and the line. The instrument was never missing; the **order** was.
- **A GUARD THAT ACCEPTS ANY MATCHING TEXT IN THE VICINITY IS NOT READING THE GUARD.** A plant walked past a rule that allowed 400 characters of slack around a `default: return false;`.
- **ASSERT THE CALL, NOT THE DEFINITION.** A rule matched `StampForQuest(string questId, int writeUpsFiled)` — the declaration. Anchor to the dot.
- **A RULE ABOUT CODE MUST READ CODE.** Checker 29's first run refused the policy's own prose explaining the change it was checking for.
- **READ THE API OUT OF THE INSTALLED GAME.** `.local/tools/ilspycmd.exe` settled `Verse.Book`, `CompBook`, `ThingWithComps`, `Pawn_PlayerSettings`, `FogGrid`, `ScribeExtractor` and `Dialog_MessageBox` this session. **`Pawn_PlayerSettings.allowedAreas` is a `Dictionary<Map, Area>`** — cross-map zoning was already in the game.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.**
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK.** *"A gate's connection has a duration. Nothing else in this mod has a duration."*
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved.

---

## The queue

```
grep -c '^\s*- \[ \]' docs/TODO.md     # open
grep -c '^\s*- \[~\]' docs/TODO.md    # partial
grep -c '^\s*- \[T\]' docs/TODO.md    # post-completion test phase
grep -c '^\s*- \[x\]' docs/TODO.md    # 0, and it must stay 0
```

```
python tools/archive-finished-todo.py --apply
python tools/verify-archive-move.py                      # straight after, every time
python tools/check-queue-integrity.py                    # and this, which the above cannot see
python tools/check-queue-pointers.py                     # and this, which neither can
```

---

## THE NEXT THING

**Ten open rows. Five are the owner's fork answers from 2026-10-06, and one of those answers is now in conflict.**

1. ⛔ **FIELDCRAFT T5 IS SUPERSEDED AND THE OWNER NEEDS TO CHOOSE AGAIN.** They approved *"All six, including the fourth crew member"* — and minutes later said *"pawns can cross gate as they plkease so no max number"*. **With no cap there is nothing for that tier to raise**, which makes it *"a project that promises something and changes nothing"*, the exact phrase four deleted projects were deleted for. A Fieldcraft T5 can exist; it needs a different subject.
2. **Build the four clean research tiers** — Facilities T5 servicing interval, Measurement T5 trained eye, Spatial T5 near exit, Entities T5 (`MaxEventsPerOpening` **only**). All approved.
3. **Spatial T6** — approved, and the one tier with a dependency outside research: a sixth palette band, or level seven reuses the deepest existing band as a stated limitation.
4. **Four machine benches, splitting the component count** — approved, and the build has to answer the cost named in the option: a destroyed or unlinked bench must not leave an unfinishable remainder.
5. **Journal step 9** — quest variety after the tutorial, and the quest half of the wiki.
6. **The ore-scatter scan** — why `GenStep_ScatterLumpsMineable` was not found on the owner's profile, so coordinate ore density is this mod's guess rather than Core's.
7. **Five partial rows**, four of which need the owner to launch and hand-fix a facility.

---

## Is it done?

**No, and the reason is a short list rather than an absence of evidence.** Twenty open rows became ten in one session, every closure carries its measurement, and the staged copy finally matches the build — so the next launch tests the code that exists.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
