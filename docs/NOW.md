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

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04, twice in one session:** *"okay once again.. yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m batteries constantly with every item you work on"* and *"you have run batteries repeatily and you havent even done ten items yet"*

**And then, when I over-corrected:** *"no you fucking retard!!!! you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

**Both corrections matter and they point the same way:**

- **During the work:** run **only the one instrument that covers the file you just touched.** One checker, or one proof, or one plant suite. **Keep writing and extending them** — the instruments are not the problem, sweeping them is.
- **At publication, once:** the 18 checkers, the 50 proofs, the 24 plant suites, in that order, one time.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.** This batch the checker sweep found one banned word; the response was one checker, not eighteen.
- **Batch size is 10–12 closed rows.** 0.12.86-dev closed ten; 0.12.87-dev closed ten.

---

## State, measured 2026-10-04

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.87-dev** — read from `About.xml`, never from a document |
| Build | **220 C# files, 98 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **18 checkers**, **50 proofs**, **24 plant suites**, **869 plant anchors**, **869 faults caught** |
| Operations panel | **2,551 on-screen words / 1,583 on hover / 113 controls / 22.6 words per action** |
| Queue | **73 open · 38 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.87-dev changed

1. **THE CHASER IS AN ORDINARY PAWN.** `RR_QuietPursuer` was a `ThingDef` drawn as a 1.4-tile black mote that **teleported** (`pursuer.Position = cell` — it never walked, pathfound or opened a door), **struck once, scripted** (two blunt to a named arm, only above 80% health), and **withdrew on a counter**. Now a real `Pawn` from Core's `PawnGenerator`, drawn from vetted hostile kinds **and the biome's own wild animals**, hunting with Core's AI. Def retired, class deleted, five teleport-era saved fields gone.
2. **AND IT HAD NO COVERAGE AT ALL** — no proof, no plant, for twenty-seven versions. `proof-chaser.py` (21 claims) and `plant-chaser.py` (**17 of 17**). Two plants reported MISSED first time and **both were my claims being wrong**: one matched the old code's exact line layout, one tested a comment.
3. **A gate's width means something for vehicles.** Width three used to return *no limit*, and **nothing could tell a 1x3 gate from a 2x3** — two of four legal footprints were the same gate. `GateOpeningDepth` is new; *"depending size"* is the vehicle's narrower dimension against the depth. Recognised by footprint, never by type.
4. **The company's books carry the company's label**, marked once at granting; every other `TextBook` keeps Core's.
5. **No shipped start names another mod's def.** Two ReBuild glass walls out, and a rule that refuses more. **The rule's first version read 114 of 171 references as nothing** — it listed `thingDef` and missed `<thing>`.

---

## THE NEXT THING

**The ally relation, and animals in the inhabitant families.** Both named by the row that stayed open: *"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"*. Enemy ships and neutral ships; **nothing down there helps a crew**, and wild animals reach the player only through the chaser, not through an inhabitant family.

Then, in order: **deep links** out to a pawn/building/research project (rows 609, 616); the **inspect-card audit** on the station and the beacon, the way the gate already has one (664); **radio fragments** (561); a **scheduling surface** (548); **room functions** — quarantine, armory, workshop, radio, receiving, storage, canteen, plus per-room stock and risk (542, 543); **certifications, training jobs and prior exposure** (544).

And the one the owner keeps naming: **the stand-alone guarantee half** — every `GetNamedSilentFail` degrades, both `PatchOperation`s stay guarded, no Def assumes a DLC. *"everything the mod needs is supplied wwith the mod as the mod, which will have all things needed to operate"*.

---

## Read these before touching anything

- **THE BATTERY RUNS ONCE AND THE INSTRUMENTS STAY.** See the top of this file. It is the only thing the owner has had to say twice.
- **THE CASCADE IS TEN REFS.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. Count the branch you are on. `PUBLISHING.md`.
- **FORGEJO REJECTS WITH `unable to create temporary object directory` AND IT IS THE SERVER.** Not the key, not the repo. Retry; it took first attempt. If it persists, check that host's free space.
- **AN ABSENCE CLAIM PASSES AGAINST AN EMPTY FILE.** `proof-chaser.py`'s first run had the wrong repository root, every `read()` returned `""`, and **eight absence claims reported green** — *nothing teleports*, *nothing scripts damage*, *the counters are gone*. `read()` now refuses an empty haystack. A `.local/register/` script is **three** levels from the root.
- **A SOURCE-TEXT CLAIM MUST NOT ENCODE THE OLD CODE'S LAYOUT.** A regex matching three specific lines let the same fault back in on a different line and the plant reported MISSED. Scope to the method, assert the property, not the shape.
- **A PLANT THAT EDITS A COMMENT TESTS NOTHING**, because every proof here strips comments first.
- **ENUMERATE THE TAGS, DO NOT GUESS THEM.** The Core-only start rule listed `thingDef` and missed `<thing>` — 114 of 171 references — and reported PASS on a hand-planted foreign def.
- **A CLOSER APPENDS TO THE ROW'S OWN LINE.** Four batches of evidence were stranded past the end of the row block; `check-queue-integrity.py` now fails on closure evidence that is not on a row.
- **A PLANT ANCHOR IS THE FIRST THING A UI OR THREAT CHANGE BREAKS.** Run `check-plant-anchors.py` after any pass that moves a call.
- **BANNED VOCABULARY, and it caught one of mine this batch.** *"portal"* → **gate**/**connection**; *"doorway"* → **door**/**threshold**; *"the machine"* is reserved. `check-info-cards.py` is the authority.
- **USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES — sixteenth instance this batch.** A heredoc collapsed a regex's backslashes and a needle that was plainly present reported `NOT UNIQUE (0)`.
- **A PLANT SUITE THAT CRASHES LOOKS LIKE ONE THAT STARTED** — the `IndexError` fired on the line that prints `baseline`. Read the last line.
- **WRITE RETRIES BELONG ON THE PLANT, NOT JUST THE RESTORE.** `Errno 22` on the way in killed a full sweep while the identical transient on the way out was a non-event.
- **NEVER SLICE SOURCE WITH `text[text.index(A):text.index(B)]` WITHOUT ASSERTING `B` IS AFTER `A`.**
- **`git checkout -- <file>` DISCARDS SOMEBODY ELSE'S UNCOMMITTED WORK.** Check `git status` first.
- **A WINDOW MUST DRAW INSIDE `RimroomsWindowState.Clean()`.**
- **A ROW WHOSE OWN EVIDENCE SAYS *PARTLY* MUST NOT BE ARCHIVED.**
- **The mod register is GUIDANCE.** `python tools/register-query.py use <trace>`. **`docs/CAMPAIGN_CHART.md`** beats any prep document.

---

## Findings recorded so nobody re-derives them

- **A gizmo action may queue a long event; a tick may not.** This is why the new address commands on the door announce the generation freeze correctly and the **gate-enter crossing path still cannot** — a pawn crossing is a job tick, and `GateSpinUp` reaches `EnsureSite` from a tick too.
- **A sighting must ask the site which pawn is the chaser.** Scanning the map for hostiles would count any raider as an entity observation, which is a false positive on a contract bonus the player is paid for.
- **A derived index into an unordered list is reproducible by luck only.** Def database order is not a promise; order before indexing.
- **The glazing mechanism was always safe and that was never the point.** `ResolveFirstLoaded` left a plain wall when ReBuild was absent. *"to acturatley make sure"* is a claim-accuracy problem: a start that names another mod cannot be audited by reading it.
- **A primitive the dialogs cannot call is a primitive the panel gets a second copy of.**
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

`STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0. The mover returns **3** for unarchivable prose sitting after a closed row, and writes nothing.

---

## Is it done?

**The build is. The play is not.** `0.12.87-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
