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

**Owner, 2026-10-04, three times:** *"okay once again.. yu should be completeing like near a dozen
items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m
batteries constantly with every item you work on"*, *"you have run batteries repeatily and you
havent even done ten items yet"*, and when I over-corrected: *"no you fucking retard!!!! you still
need to do instrament checks and build them when needed just dont run them for every fucking code
change"*

- **During the work:** run **only the one instrument covering the file you just touched.** One
  checker, or one proof, or one plant suite. **Keep writing and extending them.**
- **At publication, once:** 20 checkers → 57 proofs → 31 plant suites.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.** 0.12.93 closed **nine** and noted four.

---

## ⛔ AND THE FIX FOR DEAD CODE IS TO REACH IT, NOT TO DELETE IT ⛔

**Owner, 2026-10-04, verbatim:** *"okay sounds like your deleting shit rather than fixing it by what
you said,, that better not be the case"*

A ceiling I set myself is mine to manage, not a reason to delete a feature. **0.12.93 is the same
rule applied to a claim:** when the checker-count rule demanded a document write *"the other
eighteen checkers"* to pass, the fix was to teach the rule the English construction — not to
reword the document into something awkward. A checker that cries wolf is one people scroll past.

---

## State, measured 2026-10-05

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.93-dev** — read from `About.xml`, never from a document |
| Build | **232 C# files, 103 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **20 checkers**, **57 proofs**, **31 plant suites**, **1091 plant anchors** |
| Remotes | **all TEN refs level** — `forgejo` 5 of 5, `github` 5 of 5. Forgejo caught up 2026-10-05 after four commits down |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **49 open · 20 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.93-dev changed

**Nine rows closed, four noted. Two of the nine were the same work written twice in two different
sections**, which is worth knowing: a duplicate closed in one place and left open in the other is
how a finished thing gets built a second time.

1. **ENABLING PAGES WOULD HAVE PUBLISHED THE ENTIRE WORK LEDGER.** The row said *"a comment is not a guard"* and was righter than it knew. `_config.yml` claimed everything but the wiki was *"deliberately excluded"* while naming **four directories, two of which do not exist** — and Jekyll publishes whatever it is not told to exclude. **Fifty-four documents sit at `docs/` root**, none with front matter, so `TODO.md`, `NOW.md`, `FINALIZED.md` and `DECOMPOSED.md` would have been copied verbatim and served as raw downloads.
2. **Two independent instruments hold it now.** One keeps the list current — `build-site.py` writes it from the directory itself. One **refuses the bad outcome without reading that list at all**: it models what Jekyll would publish and fails on the answer, so a broken generator cannot produce a quiet pass.
3. **The site's non-markdown published files are covered.** A version in a layout, a branch in a stylesheet comment, a retired def on the front door: all would have shipped unexamined. **A layout is never fetched by a reader and its text is on every page that is.**
4. **The site had no root document and answered 404 at its own address.** `docs/index.html` is the front door — no front matter, a **relative** link because a project site is served from a subpath, and a real anchor as well as the refresh.
5. **The checker count is read off `tools/` instead of typed.** It said `8` while nineteen shipped. The derived version immediately caught a real stale claim the fixed phrase list structurally could not see — **and then caught this very file saying 19 after the twentieth checker landed.**
6. **THE PACK IS NOT A CARGO ROUTE, AND NOTHING USED TO LOOK AT IT.** Every cargo rule and the crossing receipt govern `carryTracker` — the hands — so anything in `pawn.inventory` crossed **unrecorded**, and the branch's own account of what went through its gate was wrong by whatever was in the bag. **The hole is ours, not a mod's.**
7. **No adapter and no patch for any of the three work providers**, each for a recorded reason, so invariant 42 holds by there being nothing to apply. Prison Labor's open axis was never a runtime question: **7 of 7 adapters and 2 of 2 work givers** gate on one function.
8. **The laundering invariant is held by an instrument instead of a sentence.** The row's purpose is satisfied and its mechanism is recorded as superseded — marking on spawn is what *closes* the hole, because the stamp is one-way and everything gets one.
9. **Three rows closed on measurement.** 38 projects / 8 branches / **0 cross-branch prerequisites**; the five `RR_*Staff` PawnKinds were always native colonists because **a `PawnKindDef` is a generation recipe, not a pawn class**; and the DLC half of the no-compatibility-claim rule is enforced, with the *control* mattering more than the refusal.

---

## THE NEXT THING

**The docs and site cluster is finished except for two owner switches.** Settings → Pages →
`main` / `/docs`, and a domain when you want one. Everything else about the site ships, is
generated, and is guarded — including the thing that would have put the ledger online.

**Then the four expansion rows**, each needing a decision about what the *optional* version of
genes, rituals, or a gravship that carries a branch actually is. These are the largest open design
questions left and they are not measurement jobs.

**T5/T6 of the research tree is a knob sweep**, not an authoring job: 274 tunable constants exist
and 34 are claimed by capabilities, so there is somewhere to look — but a tier may only exist where
a player could *name the effect*, and inventing seven projects without that is the lie the file
deletes projects for.

Then: **entity/anomaly design sheets as authored documents**; **vehicles and the VGE hooks**; and
the **world-tile rows**, which need a new world object and a generated map and are their own
checkpoint.

**And the two starting-goods rows wait on a launch, not on code.** They are the only rows whose
next step is a `Player.log`.

---

## Read these before touching anything

- **A CLAIM READS ITS OWN DOCUMENTATION. FOUR TIMES NOW, AND TWICE IN ONE FILE THIS BATCH.** Good documentation explains the thing it avoids **by naming it**, so an absence claim fails on the comment that justifies it. This batch it happened through an **HTML** comment and then again through a **Liquid `{%- comment -%}`** block the first stripper did not know existed. `code_only()`, `xml_only()`, `yaml_only()` and `html_only()` exist for this. Put every absence assertion through one.
- **A POSITIONAL CLAIM ENCODES LAYOUT, NOT THE PROPERTY.** A claim anchored `origin =` to the start of a line and reported 1 assignment where there were 2 — the second was written inline inside an `if`. Count on whitespace-normalised source.
- **A WORD BEING PRESENT IS NOT THE WORD DOING ANYTHING, and it hid in two places.** A claim that the spawn guard tests `respawningAfterLoad` passed on the **method signature**, because the parameter is named the same thing. With the signature cut it *still* passed, because `base.PostSpawnSetup(respawningAfterLoad)` **forwards** the flag. Cut both, then assert.
- **A MESSAGE IS NOT A RULE — and asserting one breaks on its own string concatenation.** A claim looked for a refusal's wording and failed on the `" "` boundary between two source lines. Assert the condition.
- **`in` CANNOT TELL ONE SITE FROM THREE.** Count it. A plant strips the traveller gate from **one adapter of seven** precisely because containment could never see that.
- **A PLANT THAT CANNOT PLANT ITS OWN FAULT TESTS NOTHING, twice this batch.** A 330-character wall paragraph against a 360 ceiling planted no wall, and a foreign-stamp plant written as a **comment** was correctly stripped by the proof. Both reported MISSED with the claim entirely innocent. Assert the fault's own size; plant real code.
- **A GUARD THAT LOOKED AT NOTHING MUST NOT REPORT A PASS.** Every rule in a published-set check is an absence rule, and an absence rule over an empty set is satisfied by construction. The site check refuses outright if it finds no page under `docs/wiki/`.
- **ONE PATTERN, ALL THE FILES IT GUARDS.** `check-plant-anchors.py` read plant tables positionally and could not parse a suite carrying a `kind` field, reporting seven sound anchors as `target missing: create`. A checker that cannot read a suite that exists is not guarding it.
- **A CONTROL THAT MUST PASS IS WORTH MORE THAN THE REFUSAL.** `mods.md` exists to say the expansions are optional, so the rule has to let it name every one of them. Two plants in this batch exist only to pass: a valid `CNAME`, and *"Biotech is not required"*.
- **EXPLICIT NAMES, NEVER GLOBS, WHERE A MISS IS SILENT.** `*` crossing a path separator is a Ruby `File.fnmatch` subtlety that cannot be verified from here. A pattern that silently fails to exclude is the one failure mode a ledger guard must not have.
- **READ THE API OUT OF THE INSTALLED GAME.** `Pawn_InventoryTracker.FirstUnloadableThing` and its exact keep-list came from `ilspycmd` against the shipped assembly, which is why the pack rule never takes a pawn's own medicine. `.local/tools/ilspycmd.exe`.
- **THE REGISTER ANSWERS MORE THAN IT LOOKS LIKE.** Two of the three provider rows were already decided in their own review cards. `python tools/register-query.py card <id>` prints every field. **`docs/CAMPAIGN_CHART.md`** beats any prep document.
- **THE CASCADE IS TEN REFS** — `forgejo` and `github` × `feature/bug-testing, feature/connected-colony-portals, Prep, Develop, Main`, pushed **by refspec from the feature branch**, never by creating local integration branches. `PUBLISHING.md` is the authority; read it rather than improvising, which is the one thing the owner has corrected about publishing.
- **WRITING A FILE WITH THE WRONG ENCODING SILENTLY CHANGES IT.** Read with `utf-8-sig`, re-write the BOM you found, and **diff-stat after every scripted edit** — the line counts do not lie.
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK WITHOUT NOTICING.** *"A gate's connection has a duration. Nothing else in this mod has a duration."*
- **A BILL NEEDS A `Building_WorkTable`.** Research benches are `Building_ResearchBench` and have no bill stack, so a recipe placed on one is a feature nobody can ever reach.
- **THE STAGER REFUSES A PACKAGE EDITED AFTER THE BUILD**, by hash. Rebuild, then stage.
- **A ROW CAN BE STALE IN ITS PREMISE, NOT JUST ITS STATUS.** Three were this batch. Measure before building — and when a row's *mechanism* has been superseded by something stronger, record that rather than quietly dropping it.
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved. `check-info-cards.py` is the authority.

---

## Findings recorded so nobody re-derives them

- **A sentence that names a count is a second place the count lives.** The rule hard-coded `8` while nineteen shipped; the document it caught then went stale *again inside the same version* when the twentieth checker landed, because the first rewrite put a different number into the explanation. Derive it, and let documents name none.
- **Making a claim true beats softening it.** `build-site.py --check` was documented as failing the battery and could not, because it is not a `check-*.py`. `tools/check-site-generated.py` is the entry point; the generator stays a generator rather than being renamed into something that looks read-only while it writes.
- **A dead exclude reads as protection and gives none.** Two of the four it replaced named directories that do not exist. `--check` now fails in both directions.
- **Derived beats stored whenever the inputs are already saved.** The pack-drop count, confidence, the material palette, the fixture tell — none needed a save migration and none can disagree with its own inputs.
- **A def nobody wired is a job nobody finished** (invariant 131). It is also why a retirement row can be superseded: five PawnKinds the queue wanted retired are the relief team's role profiles.
- **An outage is recorded, not re-investigated.** The Forgejo failure's cost was never the push; it was proving the failure was not ours. The diagnosis is in `FINALIZED.md`, and the host came back on its own.

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

**The build is. The play is not.** `0.12.93-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line — it carries
the fixture-tell attachment count, the fastest signal that the object register reached anything —
then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
