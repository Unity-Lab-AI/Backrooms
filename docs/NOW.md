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

## ✅ THE SKIPPED SWEEP FROM LAST SESSION IS DISCHARGED

0.12.88-dev published without the plant sweep, and this file said so at the top. It was the first
thing run this session: **25 suites, zero misses, zero tracebacks, every suite N-of-N, residue
check clean.** Nothing was hiding in it. The obligation is closed and the warning is gone.

---

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04, three times:** *"okay once again.. yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m batteries constantly with every item you work on"*, *"you have run batteries repeatily and you havent even done ten items yet"*, and when I over-corrected: *"no you fucking retard!!!! you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the one instrument covering the file you just touched.** One checker, or one proof, or one plant suite. **Keep writing and extending them** — the instruments are not the problem, sweeping them is.
- **At publication, once:** 18 checkers → 52 proofs → 26 plant suites.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.** 0.12.87 ten, 0.12.88 eight, 0.12.89 **eleven**.

---

## ⛔ AND THE FIX FOR DEAD CODE IS TO REACH IT, NOT TO DELETE IT ⛔

**Owner, mid-batch, verbatim:** *"okay sounds like your deleting shit rather than fixing it by what you said,, that better not be the case"*

They were right, and the correction is worth keeping. I found `RecordsAwaitingReview()` with no
caller anywhere and **removed it**, because wiring it would have pushed a density ceiling I had set
myself. That is the wrong trade: **a ceiling I set is mine to manage, not a reason to delete a
feature.** It is wired now, and it cost **zero** screen words — the count rides a heading string
that already existed, which is what the ceiling was pushing me to find in the first place.

One deletion in the batch, reversed. Everything else was additive.

---

## State, measured 2026-10-05

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.89-dev** — read from `About.xml`, never from a document |
| Build | **225 C# files, 100 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **18 checkers**, **52 proofs**, **26 plant suites**, **957 plant anchors** |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **67 open · 30 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.89-dev changed

1. **THE REGISTER REACHED OBJECTS.** Owner: *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"*. 0.12.88 reached people and events and no object at all, though objects had been named specifically. **20 tells across nine classes of thing**, each one exact wrong fact, read off the thing, held to the same no-mood-adjective gate.
2. **The comp is attached in code, not by XML, and that is the interesting part.** `StaticConstructorOnStartup` is the only moment the question *can this be placed in a room* can be asked **after inheritance resolves**. `BuildingBase` is the only xpath parent broad enough and would have put the comp on every wall, door and turret in every colony in the game.
3. **Hauling can no longer destroy a tell.** `CanStackWith` never looks at comp data, so a marked stack merging with an ordinary one would lose the fact silently.
4. **The station had no inspect card at all**, and the beacon was **silent in exactly the state where a player needed telling**. A card that explains itself only once it is working explains itself only to people who did not need it.
5. **The locked supply tier row printed a raw `defName` at the player behind a null action.** Now the project's own label, linking into the research tree through Core's public `Select`.
6. **A scheduling surface that adds no clock** — the gate's own window, off by default, thresholds identical to the three warnings, and it can only ever tell people to walk home.
7. **The company pays for each of eleven goals**, off the same checklist the status board reads, with **no new saved state** because `PostTransaction` is already idempotent on its id.
8. **Five room functions** — quarantine, armory, radio, receiving, canteen — each knowing what should be kept on it and what goes wrong when it is not.

---

## THE NEXT THING

**Certifications and training jobs** (row 580) — prior exposure and configurable roles both ship
and are wired; certifications and training jobs are the named remainder on that row.

Then: **contain, release, detain and transfer** as distinct choices with their own consequences
(row 597); **confidence scoring and a destruction workflow** on evidence (595); **client/faction
identity, company tier, previous outcome and opening duration** feeding story variation (593);
**term, renewal and eviction** on space leasing (594).

And the one the owner keeps naming: **the stand-alone guarantee half** — every
`GetNamedSilentFail` degrades, both `PatchOperation`s stay guarded, no Def assumes a DLC. The
`Fillable` guard added to equipment roles this batch is that rule applied in one place; it belongs
everywhere a defName is named.

---

## Read these before touching anything

- **THE FIX FOR DEAD CODE IS TO REACH IT.** The only thing the owner has had to correct this session, and the deletion cost nothing to reverse.
- **THE BATTERY RUNS ONCE AND THE INSTRUMENTS STAY.** The only thing the owner has had to say three times.
- **THE CASCADE IS TEN REFS.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. `PUBLISHING.md`.
- **AN ABSENCE CLAIM READS THE DOCUMENTATION TOO, and good documentation names the thing it is avoiding.** Two claims failed on their first run this batch for exactly that: `GateStandingRecall.cs` explains in a comment that the standing recall is **not a deadline** and that names meaning one are refused, and `EvidenceReview.cs` says a second `evidence.Count(AwaitsReview)` would be a second definition. Both correct, both comments, both tripping assertions about code. Every absence claim goes through `code_only()`.
- **A MESSAGE IS NOT A RULE.** A claim asserted that two `ConfigErrors` strings existed; a plant replaced the condition with `if (false)`, left both strings in place, and the suite reported MISSED. Assert the test, not the text it prints.
- **A NEEDLE THAT APPEARS TWICE MATCHES THE WRONG ONE.** `for (int index = 0; index < RecallOptionTicks.Length; index++)` validates the setter **and** builds the float menu. A plant that tore the validation out satisfied the claim against the menu.
- **WRITING A FILE WITH THE WRONG ENCODING SILENTLY CHANGES IT.** Bumping the version stripped the BOM from `About.xml`, `README.md` and the `.csproj`, and prepending the changelog **added** one to `CHANGELOG.md`, which has none. `git diff --stat` after a scripted edit is how all four were caught — the line counts do not lie.
- **FORGEJO REJECTS WITH `unable to create temporary object directory` AND IT IS THE SERVER.** Not the key — SSH auth succeeds. One retry at 0.12.86, five refusals at 0.12.87, clean at 0.12.88.
- **A PATCH XPATH RUNS BEFORE DEF INHERITANCE.** This is now a *recorded limit with a code answer*: when the set you need is a capability rather than a name, attach at `StaticConstructorOnStartup` and ask the same question the consumer asks.
- **READ THE DEF NAME OUT OF THE INSTALLED GAME.** `TableLong` does not exist. Core's dining tables are `Table2x2c` and `Table3x3c`. `.local/tools/ilspycmd.exe` answers API questions the same way — `MainTabWindow_Research.Select` was confirmed, not remembered.
- **ONE RULE, ONE PLACE.** `RoomArchetypeService.Placeable` became `internal` so the tell service asks it rather than copying it. If the generator stops placing something it stops carrying a tell, in the same edit.
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved. `check-info-cards.py` is the authority.
- **THE STAGER REFUSES A PACKAGE EDITED AFTER THE BUILD**, by hash. Rebuild, then stage.
- **A ROW CAN BE STALE.** Two closed on measurement alone this batch — seven room shapes and the full material palette were already built. Measure before building.
- **The mod register is GUIDANCE.** `python tools/register-query.py use <trace>`. **`docs/CAMPAIGN_CHART.md`** beats any prep document, and its §1.1 is the rule most likely to be violated by accident.

---

## Findings recorded so nobody re-derives them

- **`CAMPAIGN_CHART.md` §1.1 is the rule a new feature is most likely to break without noticing.** A schedule, a recall policy, a maintenance interval — every one of them wants a timer. The test that passes: does it read the gate's own window, is it off by default, and can it take anything away?
- **A comp on a plain `Thing` does nothing, silently.** Only `ThingWithComps` reads `def.comps`; the entry is accepted and never instantiated.
- **`Thing.CanStackWith` ignores comp data**, so any per-instance fact on a stackable item needs `AllowStackWith` or hauling erases it.
- **An idempotent ledger is a record.** `PostTransaction` returning `Existing()` meant the payouts needed no saved state at all — a second bookkeeping field could only drift from the books.
- **Counting map-wide is laundering.** A role's stock has to be counted on the role's own linked things, or a rifle in a bedroom makes an armory.
- **A density ceiling is a prompt to write better, not a reason to cut a feature.** The review count fitted into a string that already existed.

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

**The build is. The play is not.** `0.12.89-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line — it now
carries the fixture-tell attachment count, which is the fastest way to tell whether the object
register reached anything — then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
