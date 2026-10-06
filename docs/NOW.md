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

## ⛔ ONE HOLD LEFT. THE PUBLICATION HOLD IS LIFTED ⛔

**The owner lifted it, 2026-10-06, verbatim:** *"okay wrap up what ur on, write now.md and cascade to the github remotes"*. The earlier instruction — *"we are not stageing now.md and cascading to all three remotes correctly and properly until we are sure all of this is completed"* — is **satisfied and superseded**: the queue reached 0 open and 0 partial first, which is what *all of this is completed* meant.

**THE FORGEJO HOLD STILL STANDS.** Owner: *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **So the cascade is SIX refs** — `github` × five branches here, plus `github/main` on the mod-only repository.

**The remote is HELD, not removed, and that distinction is the point.** Deleting it would make every receipt read *complete*, and a future reader would never learn a destination had gone missing. `export-public-repo.py` keeps `forgejo` in `REMOTES`, skips it through `HELD_REMOTES`, **prints the hold and its reason every run**, and **refuses outright if every remote is held**. `PUBLISHING.md` opens with it, including: **do not push to it to test whether it is up.**

---

## ⛔ A PRISONER MAY CROSS A GATE, AND I HAD JUST SHIPPED THE OPPOSITE ⛔

**Owner, 2026-10-06, verbatim:** *"A prisoner could cross a gate... a prisoner should be able to cross a gate is allowed to ( send the prisonerrs to live and work in there and cross path back if zoned to and door are allowed access remmebr mods we have also along side all of that.. locks and prisoner mods... u know???"*

**I had found the hole and closed it hours earlier. The hole was the feature.** A prisoner crossing is ordinary movement through a door, decided by zoning, door permissions and this profile's own access-control mods. Register row 273 (**Locks**) had already planned for it: *"validate door pathing, guest/prisoner access, emergency exits"*.

| | |
|---|---|
| **One derivation replaced four faction tests** | `InOurCare` — faction **or** custody. A prisoner carries somebody else's faction while `HostFaction` is yours, so a faction test was never a test of whose pawn it is |
| **Custody crosses with them** | A prisoner arrives with **no `Lord`**. A `Lord` makes an actor out of a transferred pawn and would launder somebody in your hands into a free one |
| **The world-tile walk is still refused** | That path calls `PassToWorld`. *"Cross path back"* is not a caravan |
| **Six instruments and documents restated** | Including the register's own row 288, which called the ban *"settled"* |

**Two judgement calls that were mine, both one line to change:** a **quest lodger** stays refused (losing one fails a quest the player never chose to fail); a **slave** is admitted (their faction *is* the player's, so refusing the more-owned category while admitting the less-owned one reads as no rule at all).

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
- **At publication, once:** 29 checkers → 63 proofs → 42 plant suites → `check-plant-residue.py`. **Then `export-public-repo.py --push`, then commit, then the cascade — and then `curl` the published site.**
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
| Instruments | **29 checkers**, **63 proofs**, **42 plant suites** — **the whole battery green in one run, plus `check-plant-residue`** |
| Queue | **0 open · 0 partial · 53 `[T]` · 0 `[x]`** |
| Research tree | **44 projects, T0 to T6, nine branches** |
| Staged copy | **MATCHES THE BUILD.** `check-package-integrity` PASS |
| Commits this session | **Eleven**, and the cascade is authorised |

---

## What shipped this session

1. **The four approved tier-5 projects**, each moving a constant nothing else claims and each visible without reading source. Facilities moves **wear, not capacity** — capacity is the denominator every saved gate condition is read against, so raising it would have made a finished research project read as every gate half empty.
2. **Spatial T6 and the sixth palette band.** The content blocker was answered by authoring rather than by shipping the limitation, and the band derivation **stopped wrapping** — at five bands a depth-six coordinate came up Poolrooms on half its seeds.
3. **Four assembly benches, four sections**, at exactly the price one bill cost. A section is **never allocated to a bench**, so losing one cannot orphan work.
4. **Parallel records desks that actually work.** Two writers could both write the same report, and the second's progress landed on the *next* one.
5. **A branch can hold more than one job.** It could hold exactly one, which made the ledger and the desks unreachable.
6. **The ore density is Core's own figure at last**, per tile hilliness.
7. **Zoning proved to stay the player's**, as an absence, with a plant suite behind it.
8. **Fieldcraft T5's second subject**, chosen from three measured options rather than invented.
9. **Sixteen entity family sheets** — eleven describing shipped content, five saying plainly that nothing is built.
10. **A prisoner could cross a gate**, and that was mine from this session. Fixed, and checker 29 got the plant suite it never had.
11. **A full sweep of every instrument**, which found **eleven stale ones** — including 23 false reds, one real defect in my own palette band, and thirteen broken plant anchors that would each have died with PLANT SETUP BROKEN.

---

## Read these before touching anything

- **RUN EVERY INSTRUMENT ONCE BEFORE BELIEVING THE BATTERY.** Four stale instruments turned up by accident, so all 29 checkers and 63 proofs were run in one pass: **eleven were stale and two had been enforcing defects.** The sweep is cheap, it is read-only, and it is the only thing that finds an instrument nobody has run since the code moved under it.
- **A FALSE RED IS STILL A FINDING.** `proof-starts` reported 23 failures saying the Async Industries facility would throw on generation. Every one was wrong: `Cooler` and `Vent` declare `canPlaceOverWall` in Core and the generator has honoured it all along — the proof was the stale derivation, not the start. **Measure the game before believing an instrument about it.**
- **AND A PLANT ANCHOR THAT NO LONGER MATCHES IS A SUITE THAT PROVES NOTHING.** `check-plant-anchors` found thirteen, across eight suites. Re-aiming them exposed four more weak rules of mine, every one the same shape: a substring, a whole file instead of one band, one of two call sites, or a plant pointed at a verifier that never owned the claim.
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

**The cascade, then a launch.**

The six refs are `github` × `feature/bug-testing`, `feature/connected-colony-portals`, `Prep`, `Develop`, `Main`, plus `github/main` on the mod-only repository. **Order matters and only one way round works:** `python tools/export-public-repo.py --push` runs against the tree that was built and verifies every file's SHA256, so it goes **before** the commit here. Then the five branches. Then `curl` the published site.

After that it is the 53 `[T]` rows, every one of which needs the game running — **the owner alone launches, sorts and publishes.**

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.

## Is it done?

**The buildable list is finished and the battery is green in one run.** 29 checkers, 63 proofs, 42 plant suites, no plant residue, staged copy matching the build.

What remains is the test phase and the two holds. Nothing is waiting on an answer.
