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

## ⛔⛔ THE BATTERY RUNS ONCE. OWNER CORRECTION, TWICE, AND THE SECOND TIME WAS WORSE ⛔⛔

**Verbatim, 2026-10-04:** *"okay once again.. yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m batteries constantly with every item you work on"* and *"you have run batteries repeatily and you havent even done ten items yet"*

**They are right and this is the second time in two sessions.** During the 0.12.86-dev batch I ran the **full 23-suite plant sweep twice**, the full 18-checker sweep twice and the full 49-proof sweep twice. The plant sweep is the forty minutes. Nothing justified running it twice.

**THE RULE, and it is not a preference:**

- **During the work:** run **only the single instrument that covers the file you just touched.** One checker, or one proof, or one plant suite. Never a sweep.
- **At publication, once:** the 18 checkers, the 49 proofs, the 23 plant suites, in that order, one time.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.** The first sweep of this batch found three stale claims; the correct response was three single proofs, not a second sweep of all forty-nine.
- **Batch size is 10–12 closed rows.** This batch closed exactly ten.

---

## State, measured 2026-10-04

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.86-dev** — read from `About.xml`, never from a document |
| Build | **220 C# files, 98 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is now checked against the register |
| Instruments | **18 checkers**, **49 proofs**, **23 plant suites**, **853 plant anchors**, **852 faults caught**. Run by **exit status** |
| Operations panel | **2,551 on-screen words / 1,583 on hover / 113 controls / 22.6 words per action** |
| Queue | **69 open · 38 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.86-dev changed

1. **THE QUEUE WAS HOLDING FRAGMENTS OF FINISHED WORK AND THE GATE COULD NOT SEE THEM.** `archive-finished-todo.py` ended an `[x]` item at the next blank line, so a row whose closure carried its own evidence archived its **bullet line only** — **twelve stranded lines across four published versions**. The mover's proof is `kept + moved == original`, which is a real proof of the thing it proves and **says nothing about where a row ends**. Fixed; every stranded line recovered into `FINALIZED.md` with its parent row, read from the mover's own pre-move snapshots. **`check-queue-integrity.py` is checker 18.**
2. **The Operations panel is a utility.** 4,015 on-screen words → **2,551**, 1,583 moved to hover, 32.9 → 22.6 words per action, all eighteen pane files measured and named. `UI/OperationsControls.cs` holds the two primitives the whole panel shares.
3. **The density tool was blind twice** — 367 words of indirect keys counted as zero, and comments read as code. Two ceilings went *up* when the blindness was removed, then came down by the work.
4. **The door says what to do next.** Eleven checks moved to `Gate/GateStartupChecklist.cs`; the gate's card names the first unfinished one, first on the card. The extraction normalises byte-identical.
5. **Setting the coordinate and opening the connection are commands on the door** (`Gate/GateAddressControls.cs`) — the last two start-up actions that were panel-only.
6. **293 hard dependencies deleted, losslessly** — every one was already in `loadAfter`. A plant then found the gap that created, and `check-register-compliance.py` now matches `loadAfter` against the 294-row register.
7. **The claim rule inverted**: with nothing declared, the dangerous sentence is *"works with everything"*. `check_broad_compatibility` refuses ten phrasings while the count is zero.
8. **A plant suite had been crashing, not running** — two 4-element tuples where the baseline reads a fifth. 96 plants unset since the day it was added.

---

## THE NEXT THING

**The quest-line payouts**, three rows, logged and unbuilt: *"and once u follow the quests to get the gate up and running(full totorieal quest line payouts on each successful step(the company rewards getting to the goals)"*. The spine already exists — `GateStartupChecklist` is the eleven steps, now readable from anywhere, which is exactly what a quest step needs so a payout and a status row can never disagree.

Then: **the stand-alone guarantee half** (the *"major major work"* — every `GetNamedSilentFail` degrades, both `PatchOperation`s stay guarded, no Def assumes a DLC), the **two-maps-at-start** rework, and the **starting-goods defect** measured from the live game.

---

## Read these before touching anything

- **THE BATTERY RUNS ONCE.** See the top of this file. It is the only thing the owner has had to say twice.
- **THE CASCADE IS TEN REFS.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. Count the branch you are on. `PUBLISHING.md`.
- **A CLOSER APPENDS TO THE ROW'S OWN LINE, never past the end of the row block.** Four batches of evidence were stranded by `text.find(NL + "- [")`, which lands after the blank line. `check-queue-integrity.py` now fails on closure evidence that is not on a row.
- **A PLANT ANCHOR IS THE FIRST THING A UI CHANGE BREAKS.** Twelve went stale this batch and `check-plant-anchors.py` named every one. Run it after any pass that moves a `listing.Label` call.
- **A PROOF CLAIM THAT ASSERTS `listing.Label(` CANNOT TELL *moved to hover* FROM *deleted*.** Five claims needed re-aiming; each one got **stronger**, asserting the `heading:` or `detail:` argument rather than the key's presence.
- **BANNED VOCABULARY.** *"portal"* is the thing this mod replaced — say **gate** or **connection**. *"doorway"* is reserved against **door** and **threshold**. `check-info-cards.py` is the authority.
- **USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES — fourteenth instance this batch.** A heredoc turned `\\n` into a real newline and a needle that was plainly present reported `NOT UNIQUE (0)`.
- **NEVER SLICE SOURCE WITH `text[text.index(A):text.index(B)]` WITHOUT ASSERTING `B` IS AFTER `A`.** 154,124 copies of one method, once.
- **`git checkout -- <file>` DISCARDS SOMEBODY ELSE'S UNCOMMITTED WORK.** Check `git status` first.
- **A MEASUREMENT THAT MEASURES NOTHING STILL PRINTS A NUMBER** — three times in one tool now: `re.S` swallowing the file, indirect keys counted as zero, comments read as code.
- **A WINDOW MUST DRAW INSIDE `RimroomsWindowState.Clean()`.** A leaked zero-alpha `GUI.color` from any of 294 mods renders a frameless window invisible.
- **A PLANT SUITE THAT CRASHES LOOKS LIKE A SUITE THAT STARTED.** The `IndexError` was raised on the line that prints `baseline`. Read the last line, not the first.
- **A ROW WHOSE OWN EVIDENCE SAYS *PARTLY* MUST NOT BE ARCHIVED.** The archiver will move a row that lies.
- **The mod register is GUIDANCE.** `python tools/register-query.py use <trace>`. **`docs/CAMPAIGN_CHART.md`** beats any prep document.

---

## Findings recorded so nobody re-derives them

- **The gate-enter path still cannot announce the generation freeze.** A pawn crossing is a job tick and `GateSpinUp` reaches `EnsureSite` from a tick; a tick cannot queue a long event and carry on. **A gizmo action can** — which is why the new address commands on the door announce correctly and the crossing path still does not.
- **A primitive the dialogs cannot call is a primitive the panel gets a second copy of.** The two controls began as private methods on the window and could not reach `PersonnelView` or `Dialog_ConfirmApplicantHire`, which held 130 words between them.
- **Three panel messages stay on screen deliberately**, each with the reason in place: the unsupported-save warning, the missing-policy fault, and `RR_Portals_NoLaboratoryAddress` — which exists because of *"what do i do to get this gate open? ive tried everything"* and would be re-broken by a hover.
- **Our art cannot be drawn behind an in-play long event without Harmony.** `Root.OnGUI` skips the UI root while `ShouldWaitForEvent`.
- **At degree 5 a well-connected room cannot be moved at all.** Arrangements must form before the later braids.

---

## The live bug that is NOT ours

```
ReflectionTypeLoadException getting types in assembly RimBridgeServer:
expected class 'HarmonyLib.CodeInstruction' in assembly '0Harmony, Version=2.4.2.0'
```

`RimBridgeServer.dll` wants **0Harmony 2.4.2.0**; `brrainz.harmony` ships **2.4.1.0**. Our package loaded clean in the same log. The fix is on the machine.

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
python tools/verify-archive-move.py                                   # straight after, every time
python tools/check-queue-integrity.py                                 # and this, which the above cannot see
```

`STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0. The mover now returns **3** for unarchivable prose sitting after a closed row, and writes nothing.

---

## Is it done?

**The build is. The play is not.** `0.12.86-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
