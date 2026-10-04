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
- **At publication, once:** 21 checkers → 58 proofs → 32 plant suites.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.** 0.12.93 closed nine and noted four; 0.12.94 closed **six**, every one of a single owner direction.

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
| Version | **0.12.97-dev** — read from `About.xml`, never from a document |
| Build | **232 C# files, 103 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **21 checkers**, **59 proofs**, **34 plant suites** |
| Remotes | **all TEN refs level** — `forgejo` 5 of 5, `github` 5 of 5. Forgejo caught up 2026-10-05 after four commits down |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **36 open · 20 partial · 38 `[T]` · 0 `[x]`** |
| Public repos | **`Rimrooms-AsyncIndustries` on BOTH hosts** — `forgejo GFourteen/...` and `github G-Fourteen/...`, `main` at one commit. **The mod as staged, the public face, nothing else** |
| Published site | **LIVE** — `https://g-fourteen.github.io/Rimrooms-AsyncIndustries/`, 200 on the index, a deep page and the stylesheet |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.94-dev changed

**One owner direction, six rows, and two defects it uncovered in the mod itself.**

1. **TWO NEW REPOSITORIES HOLD THE MOD AND NOTHING ELSE**, on both hosts, and **the published site is live** — 200 on the index, a deep page and the stylesheet, verified with `curl -sI`. That is the standard the Backrooms deploy row sets and has never met.
2. **ONE DEFINITION OF THE MOD, AND IT WAS ALREADY MACHINE-READABLE.** The payload is the 103 files in `artifacts/build/package-manifest.json` — the same list `stage-mod.ps1` copies — with **every SHA256 verified on the way out**. So *what we stage* and *what we publish* cannot drift. **It refused this batch** when `About.xml` was edited after the build.
3. **AN ALLOWLIST DECIDES, A DENYLIST REFUSES THE RESULT, AND BOTH RUN.** The second pass refused the first export it ever saw: `CHANGELOG.md` is a development log and does not ship. The working README does not ship either — **every link in it is wrong there** — so the export generates its own from `About.xml` and refuses if a link would dangle.
4. **THE MOD TOLD EVERY PLAYER IT NEEDS 294 MODS, AND IT NEEDS NONE.** `About.xml` has declared zero dependencies since 0.12.86-dev while its description still said it *"declares every member of it as a dependency"*. **It is the most-read document this mod has, and nothing checked it**, because the checker globs `.md`.
5. **Found by reading generated output, not by auditing.** The export's readme said *"Needs no other mod and no expansion"* two lines above a section demanding five expansions. Nothing had ever put those two sentences side by side.
6. **`About.xml`'s description is now held to the full claims rules**, including a **new inverse dependency rule** — with nothing declared, *asserting* a dependency is the finding — and it immediately caught a second defect: the description said **"doorway"** to a player, banned everywhere else since 0.10.2-dev.
7. **The wiki renders to standalone static HTML**, no Jekyll and no build step, **importing the reading order from `build-site.py` rather than copying it**. `docs/.nojekyll` ships, or Pages rebuilds it with Jekyll and can fail outright.
8. **`git subtree split` was offered, argued against and declined** — it would have published hundreds of commits of `docs/TODO.md`.

---

## THE NEXT THING

**The public face is done and live.** What remains of it is authoring, not plumbing: a
**player-facing changelog** for the public repository — deliberately not faked by filtering the
development one — and the **Workshop page and collection**, which the queue already orders behind
a working site.

**Then the four expansion rows**, each needing a decision about what the *optional* version of
genes, rituals, or a gravship that carries a branch actually is. These are the largest open design
questions left and they are not measurement jobs.

**T5/T6 of the research tree is a knob sweep**, not an authoring job: 274 tunable constants exist
and 34 are claimed, but a tier may only exist where a player could *name the effect*.

Then: **entity/anomaly design sheets as authored documents**; **vehicles and the VGE hooks**; and
the **world-tile rows**, which need a new world object and a generated map.

**And the two starting-goods rows wait on a launch, not on code.** They are the only rows whose
next step is a `Player.log`.

**ONE PAGES DEPLOY, AND IT IS THE PUBLIC MOD REPOSITORY.** Owner, 2026-10-05, verbatim: *"the
only page deploy will be on the new github mod and wiki and public docs ONLY!!!"*, and naming the
supersession itself: *"but wait there are supper seeding rules that only the mod and public docs go
into the new mod repo as the deployable repo for the wiki"*.

**This repository is never deployed.** Pages here returns **404** and has never been enabled —
measured, not assumed. The 2026-10-01 answer *"docs/ root on this repo, github.io for now"* is
**superseded**, and `PUBLIC_RELEASE_PLAN.md` §3.3 and §3.4 are corrected rather than left recording
it as current. **`check_only_one_pages_deploy` refuses any document that tells a reader to deploy
Pages from here**, because a queue row instructing a forbidden action is worse than a stale one:
somebody does it. It caught two documents written earlier in the same session.

**Nothing was deleted to achieve that.** Owner: *"without losing capability and functioning and
documentiaons"*. The Jekyll config, layout, include and front door all stay, `build-site.py` and
`check-site-generated.py` keep maintaining them, and **the exclude list stays as the guard** — it
is the only thing that would refuse the work ledger if Pages were ever switched on here by mistake.
---

## Read these before touching anything

- **A WORD BEING PRESENT IS NOT THE WORD DOING ANYTHING. THREE MORE THIS BATCH, EVERY ONE CAUGHT BY ITS PLANT.** A regex with word boundaries cannot match inside `git_subtree_split`, because an underscore is a word character. `"--push" in sys.argv` appears twice, so containment survived a plant that deleted the push guard entirely. And `stash` is a nested function's own name, so it stayed when the call using it was removed. **Assert the call, the whole anchored statement, or the condition — never the identifier.**
- **A GENERATED ARTEFACT IS THE BEST AUDIT YOU WILL EVER RUN.** The mod telling every player it needs 294 mods had survived six versions of a checker written to catch stale claims. It was found by generating a readme from that text and reading the result, where the contradiction sat two lines apart. **Render the thing and look at it.**
- **A PLANT SUITE THAT TOUCHES A FILE WITH A BOM MUST USE BYTES.** `io.open(..., "w", encoding="utf-8")` strips one silently, which is how three were lost. `plant-public-export.py` reads and writes bytes throughout, and the BOM survived 29 plants.
- **A GUARD BELONGS IN THE BATTERY, NOT ONLY IN THE TOOL THAT KNOWS ABOUT IT.** The export audit lives in the exporter; `check-public-export.py` is what makes the battery run it. A guard only somebody remembers to fire is the `_config.yml` mistake with a different filename.
- **IMPORT, NEVER COPY, ANYTHING TWO GENERATORS AGREE ABOUT.** The static renderer imports `SECTIONS`, `page_title` and `page_summary` from `build-site.py`. A copied reading order drifts the first time a page is added, and then the two sites disagree about what the wiki is.
- **WHAT GOES IN A PUBLIC REPOSITORY IS DECIDED TWICE.** An allowlist assembles it; a denylist then refuses the assembled tree. The second pass is not redundant — it is the one that catches a mistake in the first, and it did so on its first run.
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
