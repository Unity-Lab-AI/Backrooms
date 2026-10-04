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

## ⛔ FIRST THING NEXT SESSION: THE PLANT SWEEP WAS NOT RUN ON THIS PUBLICATION ⛔

**Say it plainly rather than imply the battery was complete.** 0.12.88-dev was published on the owner's instruction to *"wrap up all we are currently working on, stage, now.md, and cascade. i need to compact"*, and the 24-suite plant sweep takes roughly fifteen minutes. It was skipped.

**What WAS run, all green:**

| Instrument | Result |
|---|---|
| 18 checkers | **0 failed** |
| 51 proofs | **0 failed** |
| `check-plant-anchors.py` | **902 anchors findable** |
| `check-plant-residue.py` | **nothing planted in the tree** |
| `plant-chaser.py` (new) | **17 of 17 caught** |
| `plant-unnerving-register.py` (new) | **32 of 32 caught** |
| Build | 0 warnings, 0 errors, 98 package files |

So the two suites written this batch are proved, every anchor in all 24 suites resolves, and no fault is left in the source. **What is unproved is the other 22 suites against this build.** Run this before anything else:

```
for p in .local/register/plant-*.py; do python "$p" || echo "FAILED $p"; done
python tools/check-plant-residue.py
```

---

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04, three times:** *"okay once again.. yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m batteries constantly with every item you work on"*, *"you have run batteries repeatily and you havent even done ten items yet"*, and when I over-corrected: *"no you fucking retard!!!! you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the one instrument covering the file you just touched.** One checker, or one proof, or one plant suite. **Keep writing and extending them** — the instruments are not the problem, sweeping them is.
- **At publication, once:** 18 checkers → 51 proofs → 24 plant suites.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.** 0.12.86 closed ten, 0.12.87 ten, 0.12.88 eight.

---

## State, measured 2026-10-04

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.88-dev** — read from `About.xml`, never from a document |
| Build | **221 C# files, 98 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **18 checkers**, **51 proofs**, **24 plant suites**, **902 plant anchors** |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **73 open · 35 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.88-dev changed

1. **THE UNNERVING REGISTER REACHED PEOPLE AND EVENTS.** Owner: *"remember lsd unnerving feeling with all things ie events random spanwns, enemies, allies, nuetrals"*. The LSD direction had been read as an **architecture** direction for eight versions — all of it built — and reached no encounter, spawn or event. The owner's four-word version: *"zero weird events or people"*.
2. **The prep documents held the mechanism.** `UNIVERSE_ADAPTATION.md`, written before this code existed: *"Ordinary industrial interiors become uncanny through exact changes"*. **The uncanny is one exact change to something ordinary** — testable, not a mood. That is now a **gate**: no tell and no trace may contain a mood adjective. The lights going out is not uncanny; the switches being found already off is.
3. **A letter is not a tell.** 12 families carry a `tellKey`, 8 events a `traceKey`, both refused at load if absent, both read off the thing rather than out of a notification that has scrolled away.
4. **Ally existed nowhere.** `RR_Inhabitant_Helper` fights for you with Core's `LordJob_DefendPoint` and **will not leave with you**. Animals are something you find, not only something that chases you.
5. **Radio fragments** — the one event with a person in it, naming somebody the branch knows. And **mentioning somebody must not resolve them**: `TakeLostPawnName` removes what it returns, so a non-destructive accessor was added.
6. **Two stale rows closed by measurement.** *"fourteen historical gameplay PNGs"* — audited: thirteen images, all accounted for. No gameplay art, no audio; the empty `Sounds` tree is gone so the absence reads off the tree.

---

## THE NEXT THING

**Run the plant sweep** (above). Then:

**Loot and equipment carry no tell of their own** — the one half of *"all things"* the register has not reached. Owner: *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"*.

Then in order: **deep links** out to a pawn/building/research project (rows 609, 616); the **inspect-card audit** on the station and the beacon (664); a **scheduling surface** (548); **room functions** — quarantine, armory, workshop, radio, receiving, storage, canteen, plus per-room stock and risk (542, 543); **certifications, training jobs and prior exposure** (544); the **quest-line payouts** at every step.

And the one the owner keeps naming: **the stand-alone guarantee half** — every `GetNamedSilentFail` degrades, both `PatchOperation`s stay guarded, no Def assumes a DLC.

---

## Read these before touching anything

- **THE BATTERY RUNS ONCE AND THE INSTRUMENTS STAY.** The only thing the owner has had to say three times.
- **THE CASCADE IS TEN REFS.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. `PUBLISHING.md`.
- **FORGEJO REJECTS WITH `unable to create temporary object directory` AND IT IS THE SERVER.** Not the key — SSH auth succeeds. Disk or permissions on `git.unityailab.com`. It took one retry at 0.12.86 and refused five at 0.12.87.
- **AN ABSENCE CLAIM PASSES AGAINST AN EMPTY FILE.** `proof-chaser.py`'s first run had the wrong repository root and **eight absence claims reported green**. `read()` now refuses an empty haystack. A `.local/register/` script is **three** levels from the root.
- **A SOURCE-TEXT CLAIM MUST NOT ENCODE THE OLD CODE'S LAYOUT.** Three plants came back MISSED this session and **all three were claims being wrong, not code**: one compared call positions when the property was *a missing letter key must not lose the record*, one matched three specific lines, one tested a comment.
- **A PLANT THAT EDITS A COMMENT TESTS NOTHING** — every proof here strips comments first.
- **NO POST-PROCESSING OF A `PLANTS` TABLE.** A dedupe loop after the literal made `check-plant-anchors.py` report `has no readable PLANTS table`. If two plants need deduping, one of them is aimed wrong.
- **ENUMERATE THE TAGS, DO NOT GUESS THEM.** The Core-only start rule listed `thingDef` and missed `<thing>` — 114 of 171 references — and passed a planted foreign def.
- **A PATCH XPATH RUNS BEFORE DEF INHERITANCE.** `ThingDef[race/intelligence="Animal"]` matches only defs that state it themselves. Patch the abstract parent instead, and record which mods that misses.
- **USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES — sixteenth and seventeenth instances this session.** A heredoc collapsed a regex's backslashes twice and a needle plainly present reported `NOT UNIQUE (0)`.
- **A CLOSER APPENDS TO THE ROW'S OWN LINE.** `check-queue-integrity.py` fails on closure evidence that is not on a row.
- **BANNED VOCABULARY, and it caught one of mine.** *"portal"* → **gate**/**connection**; *"doorway"* → **door**/**threshold**; *"the machine"* is reserved. `check-info-cards.py` is the authority.
- **THE STAGER REFUSES A PACKAGE EDITED AFTER THE BUILD**, by hash. Rebuild, then stage.
- **A ROW WHOSE OWN EVIDENCE SAYS *PARTLY* MUST NOT BE ARCHIVED.**
- **A ROW CAN BE STALE.** Two closed this batch on measurement alone — the fourteen PNGs were already gone. Measure before building.
- **The mod register is GUIDANCE.** `python tools/register-query.py use <trace>`. **`docs/CAMPAIGN_CHART.md`** beats any prep document.

---

## Findings recorded so nobody re-derives them

- **`UNIVERSE_ADAPTATION.md` line 21 is the most useful sentence in the prep documents.** It says *how* the feeling is produced, and it is checkable.
- **A gizmo action may queue a long event; a tick may not.** Why the door's address commands announce the generation freeze and the **gate-enter crossing still cannot**.
- **A sighting must ask the site which pawn is the chaser.** Scanning for hostiles would count any raider as an entity observation — a false positive on a paid bonus.
- **`TakeLostPawnName` removes what it returns.** Correct for placing a missing person, wrong for naming one.
- **A derived index into an unordered list is reproducible by luck only.** Order before indexing; def-database and roster order are not promises.
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

`STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0. The mover returns **3** for unarchivable prose after a closed row, and writes nothing.

---

## Is it done?

**The build is. The play is not.** `0.12.88-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
