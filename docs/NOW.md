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

## ⛔ WHAT THE TRIPLE CHECK FOUND ⛔

**Owner, 2026-10-06:** *"read now.md i think all items are complete lets do a triple check to make sure nothing is fucked and make sure everything is staged and done"*

**The answer is that four things were fucked, and the previous handoff was one of them.** Every instrument was green the whole time. That is the finding worth keeping: *all three batteries passing is not the same claim as the documents being true.*

### 1. The queue read zero because the rows had no checkboxes

`## Pending` in `docs/TODO.md` held two subsections carrying **five verbatim owner directions and no status marker of any kind.** Every counter in this project counts markers, so all of them read `0 open · 0 partial` — and the previous handoff published that number in its state table while its own closing section said *"`TODO.md` holds five open rows rather than none"*. **The file contradicted itself and the contradiction was the true part.**

**And two of the five had never reached `docs/FINALIZED.md`** — the audio write-up direction and the natural-gate decision. The previous batch reported `VERBATIM TRANSFER CONFIRMED`, which was true about the three rows it moved and said nothing about the two it never saw.

**A row with no marker is not absent from the queue. It is unmeasured by it.**

### 2. The archiver stranded the owner's words, twice, and the second time was mine

`check-queue-integrity.py` now has a **fourth rule: no pending section without a row** — and it caught a live bug in `archive-finished-todo.py` within minutes of being written.

`GROUP_START` splits on a `###` heading **and** on each `**Verbatim` line. A section written the way this queue writes them — heading, four of the owner's sentences, then the rows answering all four — splits into five spans of which **only the last holds any rows.** The other four counted zero and were kept. So the rows archived correctly, the reassembly identity held because nothing was lost, and `docs/TODO.md` was left holding a heading and **three of the owner's sentences over an empty space.**

A rowless span now **merges forward into the next span that has rows.** The first version of that merge then swallowed the structural `## Pending` heading itself and archived it, which is what `STRUCTURAL` exists to prevent — so the preamble above the first group is excluded, because a group begins at a `GROUP_START` by definition.

**Stated rather than glossed: the queue and the archive were restored from the mover's own snapshot twice and the move redone.** Both times the archive append was still uncommitted, so **no published archive entry was touched** — reverting an uncommitted modification is not deleting a record.

### 3. Twenty-two notes inside a PASS said something untrue

`check-package-integrity.py` printed *"texture ships but nothing references it"* for every one of the twenty-two animation frames — frames `GateWorldFrames.cs` line 239 demonstrably draws. It knew two exemptions, `Graphic_Multi` rotations and `GetAllInFolder` folders, and **had never learned the numbered-sequence prefix rule that `build-asset-page.py` learned when it hit the same wall.** The rule lived in one instrument and was never carried to the other.

**A false statement inside a PASS is worse than a failure**, because the next reader discounts the whole note list and the one real entry goes with the rest.

It is replaced by something stronger than the note it removes: **every frame a sequence declares is now demanded by name, and a missing one is a failure.** `Sequence.Resolve` returns on the first texture it cannot find and leaves the whole animation null, so frame seven of eight going astray costs the entire effect with nothing in the log. Proved by holding one frame back and reading the failure, then restoring it.

### 4. The asset numbers were wrong in three ways

The previous handoff said *"59 shipped: 42 drawings, 17 cues … every one with a master"*. Measured from the generator rather than copied between pages:

| | |
|---|---|
| Shipped files | **100** — 83 `.png`, 17 audio |
| Page entries | **69** — **52 drawings, 17 cues** (a rotatable set is one drawing, several files) |
| With a master | **59 of 69** |
| Without | **10, every one a menu background** — excluded from the rule by name, because a slide ships at its authored size and has no cutting step |
| Named by nothing | **0** |
| Undescribed | **0** |

**59 was the master count, published as the shipped total.** A number copied between documents is how both of them came to be wrong.

---

## State, measured 2026-10-06, after the above

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev** — read from `About.xml`, never from a document |
| Instruments | **33 checkers · 64 proofs · 43 plant suites — all three batteries run to completion, 33/33, 64/64, 43/43** |
| Plant tree | restored byte-clean; the only dirty files after the battery were the five this batch changed |
| Queue | `TODO.md` **0 open · 0 partial · 0 `[x]`**, and `## Pending` is empty rather than quietly occupied · `TEST.md` **54 `[T]`** |
| Staging | `check-package-integrity` reads **PASS** — *"staged copy matches the build at 0.13.0-dev, every file compared by content"* |

**THE OUTSTANDING PLANT RUN FROM THE PREVIOUS HANDOFF IS DONE.** It asked for the full 43-suite battery before the next publication, because four anchors had been re-aimed and the battery had not been repeated. **It was run twice in this batch** — once before any change and once after — **43 of 43 both times**, with the tree byte-clean afterwards.

---

## ⛔ TWO AGENTS WERE WRITING THIS REPOSITORY AT ONCE ⛔

**Owner: *"cant stop chatgpt"*.** The art and audio were authored by another agent while this one worked.

**⛔ NEVER RUN THE PLANT SUITES WHILE ANOTHER AGENT IS WRITING. ⛔** A suite writes a **real fault into a real file**, runs a verifier, then restores the file from its own copy. Anything the other agent writes inside that window is **silently reverted**. The rule binds this agent too: the battery takes longer than ten minutes, and nothing may be edited while it runs.

**And a plant that cannot trust the tree now refuses instead of lying.** `plant-class-resolution` aborts with *"ABORTED: check-package-integrity.py does not pass clean"* rather than reporting faults that are really a half-delivered package. That abort is the behaviour to keep.

---

## ⛔ A NATURAL GATE STAYS A PLAIN DOOR ⛔

**Owner, 2026-10-06:** *"natural gates dont look like the machine in the real univiverse of backrooms they are mainly just normal doors and walls that u can majicly walk through but lets keep natural doors just normal doors in game so there is distinction for it"*

The frame draws on `CompRimroomsGate` and keys on `IsDesignated`. A permanent natural gate is `CompRimroomsEmergence` and gets nothing. **That asymmetry is the information:** a framed opening was built, an unframed one was found. Recorded in `GateWorldFrames.cs` where anybody tempted to "fix" it would be standing, and in `gates.md` where a player reads it.

**An ordinary door can never wear the frame.** The component is on every `Door` and `Autodoor`, and `PostDraw` returns at the `!IsDesignated` guard. `DesignateAsGate` sets the orientation **at designation**, so there is no window where a gate has no frame.

---

## ⛔ ONE HOLD LEFT ⛔

**THE FORGEJO HOLD STANDS.** *"the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **Six refs**: `github` × five branches, plus `github/main` on the mod-only repository. The remote is **held, not removed**, and the exporter prints the hold and its reason every run.

**Local `Main`, `Develop`, `Prep` and `feature/connected-colony-portals` sit behind their remotes at `6145f4a`**, because the cascade pushes this branch's HEAD to each remote ref rather than checking each branch out. The remote refs are the published record and they are level; the local pointers are stale by design. Said here so nobody reads `git branch -v` and concludes the cascade failed.

---

## ⛔ STAGE BEFORE THE OWNER LAUNCHES ⛔

- `powershell -File tools/stage-mod.ps1 -UpdateExisting` — **the staged copy is the copy a launch loads.**
- `python tools/check-package-integrity.py` must read **PASS** before any launch report is trusted. It compares every staged file by content, not by version: *the version is a label; the bytes are what runs.*

---

## Read these before touching anything

- **ALL GREEN IS NOT THE SAME CLAIM AS ALL TRUE.** Every battery passed while a queue held unmeasured work, an archiver stranded the owner's sentences, and a PASS carried twenty-two false statements. Check the documents against the generators, not against each other.
- **A RULE SATISFIED BY ITS SUBJECT NOT BEING THERE IS NOT A RULE.** Three of checker 18's rules are about rows, so content with no row tripped none of them.
- **A NUMBER COPIED BETWEEN DOCUMENTS IS HOW BOTH BECOME WRONG.** Ask the generator.
- **AN ASSET NOTHING NAMES IS THE DEFECT THAT RETIRED THIS ART ONCE ALREADY.** The 0.9.0-dev record: the defs *"had no C# consumer whatsoever and had been shipping textures nobody could see."*
- **A NUMBERED SEQUENCE IS NAMED BY ITS PREFIX.** The animation code holds one literal and appends `01`..`08`. Both instruments know this now; for months only one did.
- **A `SoundDef` HAS NO LABEL.** Walking back for one found an unrelated def's, and the asset page announced `RR_GateWarning` as *"starting staff"*.
- **A FOLDER SCAN NAMES EVERY FILE IN IT.** The menu slides load by folder, so all twelve read as unnamed until the rule learned that.
- **MEASURE, THEN PUBLISH.** A seam metric compared two edge *regions* instead of asking whether two columns join, scored a provably seamless tile at 7.15, and a figure ten times too large was published before it was checked.
- **A DROP SHADOW IS NOT THE OBJECT.** Thresholded boxes made the bench 2.21:1 and the fluorescent 4.96:1, and those decided both footprints.
- **THE COMPONENT IS THE ALLOWLIST.** Three systems resolved a single def name while a component was the real marker — gate providers, the record book, and `RouteMarkers.OnMap`.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.** Broken again in this batch and corrected mid-flight.
- **MIND THE DEPTH WHEN A SCRIPT MOVES.** A `dirname` short by one level reads somebody else's files; `archive-finished-todo.py` records the same mistake.
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved; **never a deadline, nor the word itself.**

---

## THE NEXT THING

**A launch.** `TODO.md` is genuinely empty now rather than apparently empty, every battery has been run to completion against this exact tree, and the staged copy is this build byte for byte.

**The 54 rows in `TEST.md` all need the game running — the owner alone launches, sorts and publishes.**

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.

## Is it done?

**No, and the honest reason has changed.** It is no longer *"five open rows nobody reconciled"* — those five were completed work that had lost its checkboxes, and they are archived with the transfer proved. **What remains is that `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`, the master TODO, still carries unticked scope that nobody has reconciled against what now ships.** Read it rather than trusting a count from any handoff, this one included. **An empty minor queue never meant a finished mod.**
