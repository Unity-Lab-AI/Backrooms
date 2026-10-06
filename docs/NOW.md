# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

So: **replace this file, never append to it.** Narrative goes to `FINALIZED.md`. A rule that must survive goes to `.claude/CONSTRAINTS.md`, to `PUBLISHING.md`, or becomes a checker. Open work goes to `docs/TODO.md`.

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

**1. Nothing publishes until the launch list is finished.** Owner, 2026-10-06: *"we are not stageing now.md and cascading to all three remotes correctly and properly until we are sure all of this is completed"*. Work is committed **locally only** — the branch sits ahead of every remote on purpose, and **every commit of this session and the last is unpushed.**

**2. Forgejo is down.** Owner, 2026-10-06: *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **The cascade is SIX refs while that stands** — `github` × five branches here, plus `github/main` on the mod-only repository.

**The remote is HELD, not removed, and that distinction is the point.** Deleting it would make every receipt read *complete*, and a future reader would never learn a destination had gone missing. `export-public-repo.py` keeps `forgejo` in `REMOTES`, skips it through `HELD_REMOTES`, **prints the hold and its reason every run**, and **refuses outright if every remote is held**. `PUBLISHING.md` opens with it, including: **do not push to it to test whether it is up.**

---

## ⛔ THE ONE THING THAT IS THE OWNER'S TO ANSWER ⛔

**Fieldcraft T5 has no subject, and it is the only open row in the queue.**

They approved *"All six, including the fourth crew member"*, and minutes later, answering a different question: *"rememberber pawns can cross gate as they plkease so no max number"*. The fifth candidate **was** the fourth crew member — a project whose whole effect was raising `CrewPlanner.MaxCrew` from three to four. With no cap there is nothing to raise, which makes it *"a project that promises something and changes nothing"*: the exact phrase four deleted projects were deleted for.

**So it was not built, and the absence is proved rather than assumed.** `proof-research-tier5.py` asserts the absence **and the condition that makes it correct** — if a crew cap is ever reintroduced, that proof starts failing and names the sweep. A Fieldcraft T5 can exist. It needs a different number.

Everything else the owner answered on 2026-10-06 is built.

---

## ⛔ STAGE BEFORE THE OWNER LAUNCHES, AND IT IS IN A DURABLE PLACE NOW ⛔

This cost a whole launch report on 2026-10-06: the staged assembly was **02:51**, the build was **23:00**, and the owner tested a DLL **twenty-one hours old**. `check-package-integrity` rule 10 had already reported it with nine differing files and it was read as environmental because the game was open. **It was the warning working.**

The rule lived only here — in the one file that gets replaced wholesale. **It is now its own interdiction in `PUBLISHING.md`**, above the cascade, with the figures.

- `powershell -File tools/stage-mod.ps1 -UpdateExisting` — **the staged copy is the copy a launch loads.**
- `python tools/check-package-integrity.py` must read **PASS** before any launch report is trusted.
- **It is staged and PASS as of this writing**, so the next launch runs this code.

---

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04:** *"yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes"*, and when I over-corrected: *"you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the instrument covering the file you just touched.**
- **At publication, once:** 29 checkers → 63 proofs → 41 plant suites → `check-plant-residue.py`. **Then `export-public-repo.py --push`, then commit, then the cascade — and then `curl` the published site.**
- **THE OWNER ALONE LAUNCHES, SORTS AND PUBLISHES.**
- ⛔ **NEVER RUN THE PLANT SUITES CONCURRENTLY WITH ANYTHING ELSE.** A suite writes a real fault into the tree and restores it; anything reading the tree in that window sees the fault. Doing so reported **four failures that did not exist**.
- **THE REGISTER IS AN INPUT TO WORK, NOT A BACKLOG OF IT.**

---

## State, measured 2026-10-06

| | |
|---|---|
| Branch | **`feature/bug-testing`**, ahead of every remote by owner direction |
| Version | **0.12.99-dev** — read from `About.xml`, never from a document |
| Build | **252 C# files, 106 package files**, zero warnings, zero errors |
| Instruments | **29 checkers**, **63 proofs**, **41 plant suites** |
| Queue | **1 open · 4 partial · 50 `[T]` · 0 `[x]`** — from 10 open · 5 partial at the start of this session |
| Research tree | **43 projects, T0 to T6, nine branches** |
| Staged copy | **MATCHES THE BUILD.** `check-package-integrity` PASS |
| Commits this session | **Seven**, all local |

---

## What shipped this session

1. **The four approved tier-5 projects**, each moving a constant nothing else claims and each visible without reading source. Facilities moves **wear, not capacity** — capacity is the denominator every saved gate condition is read against, so raising it would have made a finished research project read as every gate half empty.
2. **Spatial T6 and the sixth palette band.** The content blocker was answered by authoring rather than by shipping the limitation, and the band derivation **stopped wrapping** — at five bands a depth-six coordinate came up Poolrooms on half its seeds.
3. **Four assembly benches, four sections**, at exactly the price one bill cost. A section is **never allocated to a bench**, so losing one cannot orphan work.
4. **Parallel records desks that actually work.** Two writers could both write the same report, and the second's progress landed on the *next* one.
5. **A branch can hold more than one job.** It could hold exactly one, which made the ledger and the desks unreachable.
6. **The ore density is Core's own figure at last**, per tile hilliness.
7. **Zoning proved to stay the player's**, as an absence, with a plant suite behind it.

---

## Read these before touching anything

- **A RULE SATISFIED BY ITS SUBJECT NOT BEING THERE IS NOT A RULE, AND THIS SESSION FOUND FOUR.** `find(a) < find(b)` passes when `a` is deleted, because `find` returns **-1**. A substring test passed a rename to `unclaimedRequestId` because the new name **contains** the old one. A per-pawn rule passed because **one of two** call sites still matched. A `body_of(...) or ""` test passed when the method was gone. Every ordering claim now fails on absence; every name claim is word-bounded; every call-site claim counts.
- **AND TWO PROOF CLAIMS WERE ENFORCING DEFECTS.** *"The natural depth reach is not research-driven"* went on passing after the code stopped honouring it, because it knew one spelling of a ternary. *"Only one request is ever open"* was holding in place the rule that a branch may hold one job. **Both were restated out loud rather than quietly edited** — a green instrument over a dead restraint is worse than no instrument.
- **A FEATURE WHOSE PRECONDITION IS IMPOSSIBLE IS A FEATURE NOBODY CAN REPORT AS BROKEN.** The paperwork ledger and the parallel desks were both unreachable because one guard limited a branch to one job. Found by reading a guard, not by playing.
- **MEASURE THE GAME BEFORE BELIEVING A LOG LINE.** *"Core's mineable scatter step was not found"* was read for a whole checkpoint as evidence about a 294-mod profile. **There is no such def in RimWorld 1.6 at all** — the class is constructed in code. The fallback had been used on every map ever generated, and nothing looked wrong because the fallback was right by coincidence.
- **MUD HAS NO BUILD AFFORDANCE AND A PATH COST OF 14.** It was the obvious floor for the deepest palette band and would have shipped a level nothing can be built on, found by a player rather than by a build.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.** I broke this one rule after writing a rule about absence: two `\b` word boundaries arrived in a checker as literal **0x08 backspace bytes**, and a correct rule failed on correct code.
- **TWO DERIVATIONS OF ONE RULE IS STILL THE DEFECT THIS PROJECT KEEPS MEETING.** The blind dial carried its own constant six *with a comment saying it matched the natural cap* — and a comment is not a derivation.
- **WHEN A WIKI PAGE NEVER MENTIONS A FEATURE, THE FEATURE DOES NOT EXIST FOR THE PLAYER.** `grep` found *relief station* in exactly one file in the repository: the queue. The whole paperwork system had no page either. Both are written now.
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK.** *"A gate's connection has a duration. Nothing else in this mod has a duration."*
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved. And **never a deadline, nor the word itself** — a player-facing string may not use it even to deny one, and two of them did until this session.

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

**The queue is one open row and four partial, and three of the five need the owner rather than me.**

1. ⛔ **Fieldcraft T5 needs a new subject** — the only open row. See the interdiction above.
2. **The starting-facility feedback loop** (three partial rows) — the offline half is verified and the rest **needs a launch**: `facility-diff.py` can only compare an authored layout against a real one once a facility has been generated and hand-fixed.
3. **Entity family sheets** — the other half of the research-IDs row, now that its research half is finished. `THREAT_DESIGN_SHEETS.md` holds the authoring sheet and two worked families and says plainly that the rest *"remain open design work"*. That is content design and it needs the owner.

---

## Is it done?

**The buildable list is finished.** Every row the owner answered on 2026-10-06 is built, proved and documented; what remains is one question for them, one launch, and one piece of content design.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
