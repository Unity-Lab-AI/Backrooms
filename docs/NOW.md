# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

So: **replace this file, never append to it.** Narrative goes to `FINALIZED.md`. A rule that must survive goes to `.claude/CONSTRAINTS.md`, to `PUBLISHING.md`, or becomes a checker. Open work goes to `docs/TODO.md`.

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, every owner direction verbatim, **buildable work only**. **Currently empty** |
| `docs/DECOMPOSED.md` | smallest execution units, **open only** |
| **`docs/TEST.md`** | **NEW 2026-10-06 — the test phase. 53 `[T]` rows, every one needing a launch** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

**Owner direction, 2026-10-06, verbatim:** *"we should make a seperate todo=Test.md and move all test items to it to be done and clear todo , if its true all items are done."* It was true of `TODO.md` and of nothing else: **the master TODO still carries 66 unticked rows and the ROADMAP still carries 7 milestone containers**, and neither was touched. The move is proved rather than read — every line byte-identical, every body line conserved, no `[T]` left behind.

---

## ⛔ THE MOD HAS ITS OWN ART AND ITS OWN VOICE AGAIN ⛔

**Owner, 2026-10-06, verbatim:** *"whats phase 2 are we making our own items and benches and gates? becasue if so i fucking love it! ... and a audio folder! sounds dope!!! how do we do sounds can we? can we do all of this for all our shit?"* — answered at the fork as **full reversal**.

**This reverses a binding owner direction of 2026-09-28, and that direction is deleted nowhere.** It is what retired this art across 0.9.0-dev, 0.9.9-dev and 0.12.22-dev; every retirement record cites it; invariant 105 forbids making a removal look like progress. Nine places carry both now.

**WHAT DID NOT REVERSE, AND INFERRING OTHERWISE WOULD HAVE BROKEN THE MOD:**

| Unchanged | Why |
|---|---|
| **No cloned door def** | Gate sizes come from **binding a run of real doors** — 1x1, 1x2 on `OrnateDoor`, 1x3, 2x3, plus Doors Expanded. Cloning destroys the binding and cuts the gate off from Locks, Doors Expanded, ReBuild, Vault Walls and Doors, Secret Passage Doors, AirtightGarageDoors — **and from the prisoner crossing, which is door permissions and nothing else** |
| **Never copy another package's assets** | Untouched, and now the clause most at risk. Rule 6a requires every shipped asset to have a master under `assets/source/` |
| **Reuse stays the default** | Original content is added **beside** every binding. A branch that builds none of it works exactly as before |

---

## ⛔ THINGS ROTATE, AND IT IS A BUILD FAILURE NOW ⛔

**Owner:** *"remember things rotate"*. `Graphic_Multi` resolves `_north`, `_east`, `_south`; RimWorld mirrors `_west` from `_east` and **nothing else is free**. `check-register-compliance.py` **rule 6b** fails the build on a `Graphic_Multi` of ours missing any of the three.

- **`uniform`** — cutoff, beacon. Read the same from every side, so one master honestly produces every facing.
- **`flat`** — the fluorescent, and it is a strategy the first draft missed. A flat fixture read from above genuinely turns with its footprint: `_east` is `_south` turned ninety degrees at **128x384** for the swapped footprint. **Geometry, not a trick.**
- **non-rotatable** — gate console, generator, bench, recorder, evidence case, survey tag. Front elevations with no back and no side view. They ship `Graphic_Single` and the cutter prints them under **ROTATIONS WANTED**. **Six buildings want rotations: 12 drawings, and only the owner can author them.** The machine gate is **not** among them — it is the Set Gate gizmo's icon, drawn flat in the interface, and an icon has no facing to be missing.

---

## ⛔ ADDING CONTENT WAS ONE DECISION FROM BREAKING THE DOOR'S SET-GATE BUTTON ⛔

**Owner called it before it happened:** *"rmeembr this might change the set gate option and stuff on doors"*.

The role test was hard-coded **twice** — the Operations pane's lister and `NativeGateBinding.ExactProvider` — so widening one would have offered a console the other refused, which reads as a broken button. `RimroomsGateProviders` owns it once. **The component is the allowlist** (this codebase's own principle, stated at `NativeDoorProvider`) and **the type is the role**.

**And the obvious implementation was a regression in a feature's clothes.** The button binds only on an unambiguous role, so *one more candidate* means a branch building our console **beside** Core's is told `RR_NativeGate_NoSingleConsole` — **the owner's own open 2026-10-03 report, caused by adding content.** One of ours wins outright over any number of native ones, so building ours can only ever *resolve* an ambiguity.

**The battery is deliberately not widened.** Admitting every `CompPowerBattery` in the profile, in the one role a crew's way home depends on, is a change nobody asked for.

---

## ⛔ A DUPLICATE defName SHIPPED, AND NOTHING IN A THIRTY-CHECKER BATTERY SAW IT ⛔

The company journal was authored as `RR_RouteRecording` in a new file while `RR_FieldEquipment.xml` had declared a ThingDef of that exact name since 0.2.0. **Two ThingDefs, one defName, committed and pushed.** RimWorld resolves that by one winning silently, and which one is not something a reader can tell by looking.

**`check-def-references.py` resolves names outward and is blind to a name declared twice.** The build only validates that each file is well-formed XML.

`check-def-duplicates.py` is checker 31. Two rules, and **the second matters more on a 296-mod profile**: no two defs of the same type share a name, and **no def of ours silently overrides one the game ships** — declaring `<ThingDef><defName>Shelf` does not warn, it *replaces* Core's shelf for every mod in the load order. It parses **13,161 game defs** to say so, and it recognises that a `JobDef` and a `WorkGiverDef` sharing a name is legal, which this package does four times on purpose.

---

## ⛔ THE THIRD DEF-NAME COUPLING IN ONE DAY ⛔

Three systems resolved a single def name while a **component** was the real marker, so new content carrying that component was invisible to the system built to read it:

| Where | Would have broken |
|---|---|
| Gate providers | Our console offered in the pane and refused by the validator |
| The crew's record book | A crew carrying the company journal told it had none |
| `RouteMarkers.OnMap` | A survey tag designatable from its own button, then **missing from every route, ledger entry and distortion count** |

**All three are one derivation now.** The pattern to watch for: a `GetNamedSilentFail("...")` or a `def.defName == "..."` standing in for *does this thing carry our component*.

---

## ⛔ THE WIKI SAID THINGS THAT STOPPED BEING TRUE TODAY ⛔

**Owner:** *"we should make sure all regress and inacurracyies in the wiki are all correct as we changed alot today"*. Three were real and one was a hole:

| Page | Was | Now |
|---|---|---|
| `credits.md` | *"No gameplay art or audio is shipped — every object in play is existing game or mod content"* | Everything shipped is original to this project, and **no other package's assets are ever copied** |
| `index.md` | *"A gate is an ordinary door you designate. No custom buildings."* | The gate half is still true and is **why** a door from any mod can become one. The company's own kit is named and linked, with *none of it required* |
| `first-hour.md` | *"Nothing special is required, and nothing special is provided"* | Nothing special is **required**. The company does build its own generator, and the battery must still be the game's own |
| — | **No page told a player what they can build** | `building.md`, a new page under Playing: every buildable, where it is in the menu, what it needs, and why some do not rotate |

**And `ROADMAP.md`'s status table was six versions stale** — 0.7.1-dev, 120 C# files, 76 package files, against 0.13.0-dev, 254 and 134. It also still led with the content rule the owner reversed. Both restated.

---

## ⛔ ONE HOLD LEFT ⛔

**THE FORGEJO HOLD STANDS.** Owner: *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **The cascade is SIX refs** — `github` × five branches here, plus `github/main` on the mod-only repository.

**The remote is HELD, not removed, and that distinction is the point.** Deleting it would make every receipt read *complete*. `export-public-repo.py` keeps `forgejo` in `REMOTES`, skips it through `HELD_REMOTES`, **prints the hold and its reason every run**, and **refuses outright if every remote is held**. `PUBLISHING.md` opens with it, including: **do not push to it to test whether it is up.**

---

## ⛔ STAGE BEFORE THE OWNER LAUNCHES ⛔

This cost a whole launch report on 2026-10-06: the staged assembly was **02:51**, the build **23:00**, and the owner tested a DLL **twenty-one hours old**. It is its own interdiction in `PUBLISHING.md` now, above the cascade.

- `powershell -File tools/stage-mod.ps1 -UpdateExisting` — **the staged copy is the copy a launch loads.**
- `python tools/check-package-integrity.py` must read **PASS** before any launch report is trusted.

---

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04:** *"yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes"*, and *"you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the instrument covering the file you just touched.**
- **At publication, once:** 32 checkers → 63 proofs → 42 plant suites → `check-plant-residue.py`. **Then `export-public-repo.py --push`, then commit, then the cascade — and then `curl` the published site.**
- **THE OWNER ALONE LAUNCHES, SORTS AND PUBLISHES.**
- ⛔ **NEVER RUN THE PLANT SUITES CONCURRENTLY WITH ANYTHING ELSE.** A suite writes a real fault into the tree and restores it; anything reading the tree in that window sees the fault.
- **THE REGISTER IS AN INPUT TO WORK, NOT A BACKLOG OF IT.**

---

## State, measured 2026-10-06

| | |
|---|---|
| Branch | **`feature/bug-testing`**, ahead of every remote by owner direction |
| Version | **0.13.0-dev** — read from `About.xml`, never from a document |
| Build | **254 C# files, 134 package files**, zero warnings, zero errors |
| Instruments | **32 checkers**, **63 proofs**, **42 plant suites** |
| Queue | **`TODO.md` 0 open · 0 partial · 0 `[T]`** — empty. **`TEST.md` 53 `[T]`** |
| Shipped art | **18 textures**, from 11.5 MB of masters. **One cut and held** — the Quiet Pursuer, by owner decision |
| Shipped audio | **4 original cues**, positional, Core fallback retained |

---

## Read these before touching anything

- **A NEW CHECKER EXISTS BECAUSE ONLY THE OWNER LAUNCHES.** `check-def-references.py` parses **12,283 def and abstract names** out of the installed `Data/` folders — Core and all six expansions — and resolves every `ParentName`, build cost, research prerequisite, category and Rimrooms type the package names. On a 296-mod profile a typo'd def name is a red log read as *this mod broke my game*. **It passed on its first run, which is not evidence: four faults were planted and all four were caught.** It reports **SKIPPED with a non-zero exit** when the game is absent rather than passing.
- **A MEASUREMENT WAS PUBLISHED BEFORE IT WAS CHECKED, AND IT WAS WRONG BY AN ORDER OF MAGNITUDE.** The carpet seam was called **18.3 against a threshold of 6** — *a grid across every room*. That proxy compared two edge **regions** for similarity rather than asking whether two columns join, and **it scored a provably seamless quad mirror at 7.15**, which is how it was caught. The real figure is **x1.4 / x1.7**: a faint seam. The fix still takes it to **x0.00**. **The fix was worth making and the alarm was not.**
- **A DROP SHADOW IS NOT THE OBJECT.** Bounding boxes at a zero alpha threshold reported the field analysis bench as taller than wide, for a visibly long counter. At a real threshold it is **2.21 : 1** and the fluorescent is **4.96 : 1**. Both footprints came from the corrected number.
- **NO TEXTURE SHIPS THAT NOTHING NAMES.** The 0.9.0-dev retirement's own words: the art *"had no C# consumer whatsoever and had been shipping textures nobody could see"*. The cutter **derives** shipment by reading which paths the defs and the C# reference, so authoring a def ships its texture on the next run and nothing else does.
- **TWO INSTRUMENTS WERE FOUND STALE BY THIS WORK, AND BOTH WERE REPLACED RATHER THAN REMOVED.** Rule 6 asserted *zero gameplay art ships*. And **`RETIRED_DEFS` was a typed tuple of ten names eleven lines above its own comment diagnosing typed counts as "a dated assertion wearing a check's clothes"** — six shipped again, so a rule meant to stop documents promising what the package cannot deliver began refusing them for describing what it **does**.
- **A NAME THAT HAS STOPPED BEING TRUE IS A DEFECT.** `IsLegacyCarrier` matched only old saves until the def shipped again; it is `IsCompanyCarrier`, because a reader trusting the old name would delete the branch as dead code.
- **COUNTING IS PLURAL; ISSUING IS SINGULAR.** A crew carrying the company journal was told it had no record book, because the kit counted one def.
- **RUN EVERY INSTRUMENT ONCE BEFORE BELIEVING THE BATTERY.** A full sweep on 2026-10-06 found **eleven stale instruments**, including 23 false reds and two that had been *enforcing* defects.
- **A RULE SATISFIED BY ITS SUBJECT NOT BEING THERE IS NOT A RULE.** `find(a) < find(b)` passes when `a` is deleted, because `find` returns **-1**.
- **MEASURE THE GAME BEFORE BELIEVING AN INSTRUMENT ABOUT IT.** `Cooler` and `Vent` declare `canPlaceOverWall` in Core; there is no mineable-scatter GenStepDef in 1.6 at all; `Mud` has no build affordance.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.**
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK.** *"A gate's connection has a duration. Nothing else in this mod has a duration."*
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved. And **never a deadline, nor the word itself**.

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

## ⛔ THE PUBLIC MOD REGISTER IS BUILT, AND IT IS A SECOND REGISTER RATHER THAN A VIEW ⛔

**Owner, 2026-10-06, verbatim:** *"okay we are adding to todo everything we need to make a similar mod registry as the one we have but this one will be pubvlic facing with all new writes in it so that it says the important stuff all players would need to know like mod interferances, what if's if not used  uses in rimrooms, required/recommended/(whatever else(s) is needed) as tags per mod in this recommended mod list for all modsand anything else relevant of note"*

***"All new writes"* is the whole instruction and it is load bearing.** Not one sentence of the engineering register's prose is carried across. A player does not need our integration approach.

| | |
|---|---|
| Page | `docs/wiki/mods-list.md`, generated, published, linked from the mods page |
| Entries | **296 mods**, plus the base game shown for context and **stated not to be counted** |
| Tags | **Required · Recommended · Optional · Visual only · Not needed** — the owner's own words, with the page saying before the table that **Required never means required to launch** |
| Spread | 83 Recommended · 192 Optional · 4 Visual only · 16 Not needed. **The only thing tagged Required is the game** |
| Hand-authored | 6 rows in `tools/public-register-text.json`, which overrides any cell on any row |
| Checker | **32**, `check-public-register.py`, because the generator is not a `check-*` and a battery that globs would never have run it |

**The count reconciles exactly rather than quietly differing**: the engineering register holds **295 rows — 294 profile entries plus one for Core** — with the six `Data/` folders inside the 294 as rows 4 to 9. So **294 + Rimbridge + Rimrooms = 296**, and the two the engineering register never had are declared in the overrides file.

---

## THE NEXT THING

**A launch. The buildable queue is empty.**

The 53 `[T]` rows live in **[`TEST.md`](TEST.md)** now and all need the game running — **the owner alone launches, sorts and publishes.**

**AND ONE THING IS NOT DONE, SAID PLAINLY BECAUSE THE OWNER ASKED WHETHER EVERYTHING WAS.** The master TODO, `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`, carries **66 unticked rows** — and they are not all runtime acceptance. Some are real open scope: applicant and talent pools, company roles and schedules and certifications, cafeteria and recreation and shift rotation, outpost and town-distortion starts, structured log categories, stable cross-save references. Others look built-but-unticked, and **nobody has reconciled which is which**. That reconciliation is itself a named open item in `ROADMAP.md` and it is the honest next piece of buildable work after a launch.

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.

**Two things are waiting on the owner rather than on work:**

1. **12 drawings.** Six buildings ship non-rotatable because their other facings do not exist — gate console, utility generator, field analysis bench, field recorder, sealed evidence case, survey tag. Each needs `_north` and `_east`; `_south` is the master already here and `_west` is mirrored free. `tools/cut-phase2-art.py` prints the count every run. **Nothing can derive them: a back view is a drawing.**
2. **The Quiet Pursuer**, held by owner decision. It needs a race `ThingDef` with `lifeStages` and body graphics rather than a texture, and a malformed race on a 296-mod profile breaks other people's pawn rendering.

## Is it done?

**`TODO.md` is empty and `TEST.md` holds the 53 rows that need a launch.** Everything claimed here is built and the whole battery is green in one run.

**But "is everything done" is NO, and the difference matters.** `TODO.md` being empty means *nothing buildable is queued*, not that the mod is finished: the master TODO's 66 unticked rows are unreconciled, and some of them are real scope nobody has built. Anyone reading an empty queue as a finished mod is reading one tier of four.
