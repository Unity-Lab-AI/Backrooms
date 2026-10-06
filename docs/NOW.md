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
- **STAGE FIRST, AND IT WAS MISSING FROM THIS LIST UNTIL 0.12.99-dev.** `powershell -File tools/stage-mod.ps1 -UpdateExisting` copies the built package into RimSort's Local Mods folder, **which is the copy the owner actually launches.** It was in neither this sequence nor `PUBLISHING.md`, so it got skipped -- and the staged copy sat at **0.12.98-dev while the build was 0.12.99-dev**, caught minutes before a launch. A stale staged copy means the owner tests the wrong build and reports defects that were already fixed, which is the most expensive kind of wasted session there is. The owner's own direction named three things, *"the staging, now.md writeing, and the cascades"*, and only two of them were written down.
- **At publication, once:** 26 checkers → 59 proofs → 36 plant suites → `check-plant-residue.py`. **Then `export-public-repo.py --push`, then commit, then the ten-ref cascade — and then `curl` the published site.** The last step is not a formality: every banner once shipped as a 404 with all twelve refs level and every instrument green, **and the licence link shipped as a 404 the same way**, because an on-disk audit cannot see a deployment fault.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.**
- **THE OWNER ALONE LAUNCHES, SORTS AND PUBLISHES.** Deploying a site is not the same act as
  launching the game, but the Workshop is the owner's account and the owner's decision. Lifted here
  0.12.99-dev from a queue section that was being cleared: **it existed nowhere else**, and a
  standing constraint whose only copy is inside a queue section dies when that section is archived.
- **`docs/TODO.md` ENDS AS A TEMPLATE HOLDING NOTHING.** Owner direction, 2026-10-04, verbatim:
  *"read now.md and continue the work we are working off todo items to get the todo to a templet
  form with no items listed"*, and *"all complketed and moved completed into finalized.md"*. The
  terminal state is the preamble, the status-marker legend and the structural headings — nothing
  listed. **The `[T]` rows are the one honest obstacle**: a `[T]` row cannot be closed without the
  game running, so the file reaches template form when the owner has launched, not before.
- **THE REGISTER IS AN INPUT TO WORK, NOT A BACKLOG OF IT.** Owner, 2026-10-05: *"as the
  Rimrooms Mod is stand alond only adding to it when mopds are added? right?"* Right. **A row's
  disposition is settled when something is built that touches that mod, or when a launch produces
  evidence about it — never as a bulk sweep.** 94 of 295 rows are Settled and that is exactly the
  set somebody had a reason to look at. Settling the rest from a desk would break D1, because a
  disposition asks for things like *"verify stack, weight, ownership, caravan and RWT transfer
  behavior"* — runtime claims. The register's own policy says it: ***"Researched" does not mean
  "integrated"; "loads" does not mean "compatible"; "optional" does not mean tested.***
- ⛔ **NEVER RUN THE PLANT SUITES CONCURRENTLY WITH ANYTHING ELSE.** A plant suite *writes a real
  fault into the working tree* and restores it moments later; anything reading the tree inside that
  window sees the fault. Running the checkers alongside them at 0.12.99-dev reported **four
  failures that did not exist** — `check-plant-anchors`, `check-public-export`,
  `check-planner-layouts` and `check-doc-conformance`, each reading a file some suite had planted
  into. Re-run serially: **0 of 25.** The stages are sequential for a reason, and a false failure
  costs the same investigation as a real one.

---

## ⛔ AND THE FIX FOR DEAD CODE IS TO REACH IT, NOT TO DELETE IT ⛔

**Owner, 2026-10-04, verbatim:** *"okay sounds like your deleting shit rather than fixing it by what
you said,, that better not be the case"*

A ceiling I set myself is mine to manage, not a reason to delete a feature. **The same rule applies
to a claim:** when a rule demanded a document write *"the other eighteen checkers"* to pass, the fix
was to teach the rule the English construction — not to reword the document into something awkward.
A checker that cries wolf is one people scroll past.

---

## State, measured 2026-10-05

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.99-dev** — read from `About.xml`, never from a document |
| Build | **232 C# files, 103 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **26 checkers**, **59 proofs**, **36 plant suites**, **1,206 plant anchors**. `check-queue-pointers.py` is the newest: **a statement of what is still open may not be resolved by position.** It found five, and three pointed at rows that were closed and archived |
| Remotes | **TWELVE refs** — this repository 10 (`forgejo` 5, `github` 5) plus the mod-only pair 2 |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **0 open · 4 partial · 50 `[T]` · 0 `[x]`** — down from **16 open · 11 partial**. **`[ ]` now means *doable today*, and nothing is**: eight rows said in their own text that they need a launch and have been moved to `[T]` where they gate nothing |
| Public repos | **`Rimrooms-AsyncIndustries` on BOTH hosts** — `forgejo GFourteen/...` and `github G-Fourteen/...`. **The mod as staged, the public face, nothing else** |
| Published site | **LIVE** — `https://g-fourteen.github.io/Rimrooms-AsyncIndustries/`. Pages serves `/docs` as the **site root**, so a page is `<site>/gates.html` and every reference must be site-relative |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.99-dev changed

**The owner asked a fair question:** *"i think we only have a handful of open items but idk how many
of those are buildable and unblocked undiffered, u didnt specify too correctly"*. The answer is a
count. Of sixteen open rows: **two were commissioned work already answered, four were M6a and close
without a launch, five were held open by pointers to rows that do not exist**, and the rest wait on
a launch, on Steam, or on a domain.

1. **A ROW HELD OPEN BY A POINTER TO NOTHING, FIVE TIMES.** 0.12.98-dev found this twice and
   **declined to make it a rule** — *"two cases, and 'the row below' has no mechanical meaning"*.
   That was wrong, and the measurement changed it: **five** statements of open work resolved by
   position, **three of them pointing at rows already closed and archived**. Each read as work
   somebody could go and pick up. **Checker 25 refuses one construction rather than one phrase**,
   which is why it does not cry wolf: twelve lines carry a positional phrase and only five are
   faults. **And my first fix was wrong in a way the checker caught** — appending the correction
   while leaving the pointer standing is two statements about one thing with one of them dead.
2. **"A MOD NOBODY HAS NAMED" WAS TWELVE NAMED MODS, INSTALLED ON THIS MACHINE.** Every mod in the
   profile is named by the register and **288 of the 294 are on disk**, so the claim was checkable.
   **Twelve add thirteen work types**, every giver class decompiled against its installed assembly.
   **Exactly one was buildable and it is built** — `MedicalTraining`, whose giver derives from
   `WorkGiver_DoBill`, which is the entire requirement because `BillWorkProvider` matches benches
   **by capability** and names nothing. **No code anywhere references that mod.** The other twelve
   are a closed decision: the only generic candidate query reads `pawn.Map`, which is the one map a
   deployment question is never about.
3. **THE SETTINGS PANE DREW SLIDERS FOR WORK THE PLAYER DOES NOT OWN, and it had since 0.6.4-dev.**
   Four families are `MayRequire`-gated; `Apply` always skipped an absent one and **the pane never
   did**. A player without Anomaly saw a cross-gate dark-study slider reporting a shipped default of
   **0**, writing an override keyed to a defName nothing carries. Both now ask through **one**
   lookup, and **the proof counts the lookups** rather than testing for their presence — two pieces
   of code asking the same question separately is what produced it.
4. **THE DLC GATE COULD NOT SEE A MOD.** It indexes the game's `Data` folders, so a work type a
   profile mod adds is not DLC-only and is therefore invisible. Ungated, that is the identical
   unresolved cross-reference two childcare givers shipped with. Scoped to `<workType>` because it
   is the one tag here whose text is always a def name and never prose.
5. **SEVEN PATCH TARGETS NOBODY COULD VERIFY WERE VERIFIABLE ALL ALONG.** Both mods declaring them
   are in the owner's own 294 and both installed. **A note that cannot be checked reads as checked
   and fine**, and it was hiding the worse outcome: a renamed optional target applies to nothing and
   reports nothing. Now an unknown optional target is a **failure**, and an unreachable library
   degrades to the old notes rather than to a silent pass.
6. **THE LICENCE LINK ON THE PUBLISHED CREDITS PAGE WAS A 404.** The image guard was aimed at
   `<img src>` because that was the fault in hand the day the banners broke; **`<a href>` has the
   identical failure mode.** `lstrip("./")` strips the *characters* `.` and `/`, so `../../LICENSE`
   came out as `LICENSE` — a site-relative-looking href for a file not at the site root. **A broken
   image is visible; a dead link looks exactly like a working link.** Fixed three ways: the renderer
   separates `./` noise from a `..` escape, **the licence is published inside the site** as the art
   is, and `check_links_resolve` is the sibling the image guard shipped without.
7. **THE THREE START BRIEFS, AND WRITING THEM FOUND TWO ILLEGAL PREMISES.** Owner: *"Write briefs
   for all three"*. `town_distortion`'s recorded pressure is *"time pressure"* and
   `isolated_outpost`'s is *"uncertain evacuation"* — **both clocks, and §1.1 permits one clock and
   it is the gate's.** Replaced by costs that grow: settlement standing, and an account the post
   cannot reach. The old premises stay recorded as superseded rather than quietly edited.
8. **THE TIER SWEEP, AND COMMERCE GETS NOTHING BECAUSE THAT IS BETTER.** Owner: *"Sweep the
   constants and propose the tiers to you"*. **278 constants enumerated, six candidates survive,
   four branches honestly get none.** Facilities T5 fills a gap **§1.1 itself names** — maintenance
   is one of the four factors deciding a gate's window and the only one with no project on it.
   **Commerce's candidates became player settings at 0.12.98-dev**, and a research tier over a
   slider is two controls fighting.
9. **M6a CLOSES, AND THE RELEASE RITUAL EXISTS NOW.** `PUBLISHING.md` §8: six preconditions, five
   met, and the sixth is the gate — *every feature has a recorded acceptance result*, and nothing
   has passed anything because nothing has run. **The archive is a property rather than a folder:**
   a tagged commit on four refs, and a manifest with a hash per file, which beats a zip because it
   proves a downloaded copy is the one that was built. **No tag is cut.**
10. **AND THE PLAYER-FACING CHANGELOG IS AUTHORED, NOT FILTERED.** `docs/WHATS_NEW.md`, shipped at
    the public repository root. It says plainly that nothing has been played, that nothing is
    claimed as tested with other mods, that co-op is not promised, that **development saves may
    break** — the owner's own *"Development-save break is allowed — declare it"* — and that balance
    is unjudged.

## ⛔ THE LAUNCH IS NEXT, AND THE LOOP IS AGREED ⛔

**Owner, 2026-10-05, verbatim:** *"im going to be starting it up next here soon... the first thing i
want you to do is 1. check off open items that we complete/you complete, when i start it up"*, and
the second thing: *"as i load up the different scenerios we will be needing to fix the layout of the
starting facilities(i will be manual using pawns to change the layout and fix some thing, to which
you will use the api mod to see what exactly i change/add to the starting facilities that you will
be making standard and default to the starting scenrios so that the problems like broken conduit
lines are repaired by me, then updated to match for the mods defualt facilities)"*

**Asked at two forks and answered: *"I'll hand-fix it, you read it back"*.** So **nothing is
auto-authored.** The owner places it, the tool reads it, the def follows. Same answer for the
missing battery, Async Industries only.

**The tool is `.local/qa/facility-diff.py` and its offline half is verified:**

```
python .local/qa/facility-diff.py authored RR_AsyncIndustriesStart   # what the def says, offline
python .local/qa/facility-diff.py power    RR_AsyncIndustriesStart   # grid connectivity, offline
python .local/qa/facility-diff.py snapshot RR_AsyncIndustriesStart   # read the live map
python .local/qa/facility-diff.py diff     RR_AsyncIndustriesStart   # paste-ready def XML
```

**THE PRE-LAUNCH BASELINE, so the diff has something true to compare against.** Neither facility
has working power as authored: **34 of 34** powered buildings unconnected in Async Industries with
the nearest wire **3 to 7 cells away** and **5 separate grids**, **8 of 8** in the furniture store,
and **two of the three generators are off the wire**. Neither authors a battery. **The number was
checked before it was believed** — 34 of 34 is the too-round figure that caught a false
reachability result before, so the distances were measured one by one.

**What the loop cannot carry, said before the session rather than after:** a **per-cell floor
change** (flooring is one facility-wide terrain plus a per-room boolean) and a **knocked-through
wall** (walls come from the room rectangles, so a removal is a room edit). Everything else carries,
including `stuff`, `rotation`, `batteryFraction` and `fuelFraction`.

**And blueprints and frames count as the owner's intent**, so a fix is readable before pawns
finish building it.

---

## THE NEXT THING

**Nothing is open and nothing is buildable without the owner.** One row is partial: the T5/T6
research sweep, which is written and waiting on the owner to pick from it. The Steam mod page and collection wait
on the owner's *"Not yet — ask again when the mod is ready to publish"*. The domain waits on
*"Not yet — leave it on the github.io path"*. The compatibility report and the duplicate-def
resolution structurally require a launch with the 294 profile loaded.

**What is left that does not need a launch is two things and both are decisions, not work:**

- **Pick from the tier sweep.** Four candidates are ready to build, one (a fourth crew member) is
  explicitly the owner's call because it re-shapes the pressure arithmetic, and one (a seventh
  level) is blocked on authoring a sixth palette band.
- **Say whether any of the three start briefs should be built**, and in what order. The briefs exist
  precisely so that call can be made without guessing.

**And the two starting-goods rows are RETIRED by owner direction, 2026-10-05:** *"remove these,
they are no longer needed"*. What was found stays in the archive -- a 9,216-cell sweep and four
candidate causes eliminated against the installed game -- and the diagnostic that reports a
promised-but-absent starting grant stays in the package, held by its own proof claims. **No further
investigation is owed.**

**ONE PAGES DEPLOY, AND IT IS THE PUBLIC MOD REPOSITORY.** Owner, 2026-10-05, verbatim: *"the only
page deploy will be on the new github mod and wiki and public docs ONLY!!!"*. **This repository is
never deployed.** Pages here returns **404** and has never been enabled — measured, not assumed.
`check_only_one_pages_deploy` refuses any document that tells a reader to deploy Pages from here,
because a row instructing a forbidden action is worse than a stale one: somebody does it.

**Nothing was deleted to achieve that.** Owner: *"without losing capability and functioning and
documentiaons"*. The Jekyll config, layout, include and front door all stay, and **the exclude list
stays as the guard** — it is the only thing that would refuse the work ledger if Pages were ever
switched on here by mistake. It is **generated** by `tools/build-site.py`, so a new document at
`docs/` root cannot quietly join the published set; run the generator after adding one.

---

## Read these before touching anything

- **ONE PATTERN, ALL THE REFERENCES IT GUARDS.** The escape-path rule was written for `<img src>`
  the day every banner 404'd and was never given to `<a href>` — and the licence link on the
  credits page was **404 on the live site** the whole time. A guard written for the fault in hand
  covers the fault in hand. Ask what else has that shape, immediately, while the rule is fresh.
- **A WORD BEING PRESENT IS NOT THE WORD DOING ANYTHING, AND I DID IT AGAIN THIS BATCH.** A claim
  asserted `"def foreign_work_types(owner):" in gating` — the **definition**, not the call. Its
  plant correctly reported MISSED: a rule defined and never invoked does nothing, and the identifier
  was there either way. **Assert the call, the whole anchored statement, or the condition.**
- **AND `in` CANNOT TELL ONE SITE FROM TWO.** Adding a second rule to `check-dlc-gating.py` put a
  second copy of `for node, required in nodes_with_requirements(definition):` in the file, which
  silently made an existing claim survive a plant that gutted the first walk entirely. **Count it.**
- **AN ON-DISK AUDIT CANNOT SEE A DEPLOYMENT FAULT. READ THE LIVE SITE BACK.** `curl` against the
  published URL is the last step of publishing, and it is the only instrument that has ever caught
  either of the two 404 classes.
- **A NOTE THAT CANNOT BE CHECKED READS AS CHECKED AND FINE.** Seven *"cannot be verified"* notes
  survived every battery for weeks while the thing they described was sitting in the owner's own mod
  folder. If a note says *unverifiable*, ask **from where** — the answer was *from a path nobody had
  looked at*.
- **A STALE DOC COMMENT IS THE UPSTREAM OF A PUBLISHED LIE.** The wiki told readers the free ways
  through stop at depth 3 because `MaximumNaturalDepth` carried **two** `<summary>` blocks and the
  first still argued for three. **Write a reader-facing sentence from the constant and the keyed
  string, never from the comment beside them.**
- **A ROW CAN BE STALE IN ITS PREMISE, NOT JUST ITS STATUS.** Four were this batch — *"a mod nobody
  has named"*, two start premises that ran clocks, and a provider-adapter row the register had
  already settled. **Measure before building.**
- **A GENERATED ARTEFACT IS THE BEST AUDIT YOU WILL EVER RUN.** The mod telling every player it
  needed 294 mods survived six versions of a checker written to catch stale claims. It was found by
  generating a readme and reading it. **Render the thing and look at it.**
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.** Mangled again this batch; a quote inside
  a quoted heredoc ate the rest of the file. Four occurrences across two sessions.
- **WRITING A FILE WITH THE WRONG ENCODING SILENTLY CHANGES IT.** Read with `utf-8-sig`, **re-write
  only the BOM you actually found**, and **diff-stat after every scripted edit**.
- **A PLANT SUITE THAT TOUCHES A FILE WITH A BOM MUST USE BYTES.** `io.open(..., "w",
  encoding="utf-8")` strips one silently.
- **A GUARD THAT LOOKED AT NOTHING MUST NOT REPORT A PASS.** Every new rule this batch refuses an
  empty scope explicitly.
- **A CLAIM READS ITS OWN DOCUMENTATION.** `code_only()`, `xml_only()`, `yaml_only()` and
  `html_only()` exist for this. Put every absence assertion through one.
- **READ THE API OUT OF THE INSTALLED GAME — AND THE INSTALLED MODS.** `.local/tools/ilspycmd.exe`
  settled thirteen base classes this batch in one pass. The workshop library is at
  `steamapps/workshop/content/294100`, and **288 of the owner's 294 are in it.**
- **THE REGISTER ANSWERS MORE THAN IT LOOKS LIKE.** The entire optional-provider question was
  already decided in the review cards. `python tools/register-query.py card <id>` prints every
  field. **`docs/CAMPAIGN_CHART.md` beats any prep document.**
- **THE CASCADE IS TWELVE REFS, NOT TEN.** Ten here — `forgejo` and `github` × `feature/bug-testing,
  feature/connected-colony-portals, Prep, Develop, Main`, pushed **by refspec from the feature
  branch** — **plus two** via `python tools/export-public-repo.py --push`, which **runs BEFORE the
  commit here** because it verifies every file's SHA256 against the build manifest. **The exporter
  reads its own remotes back and refuses if either is behind.** `PUBLISHING.md` is the authority;
  read it rather than improvising.
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK WITHOUT NOTICING.** *"A gate's connection
  has a duration. Nothing else in this mod has a duration."* It caught two of the three start
  premises this batch, and `check-campaign-absolutes.py` refuses the forbidden noun for a thing
  that expires in a living document **even where the sentence is denying one** — reword the prose,
  never widen the rule. It has now caught that construction three times, including twice in
  documents written to explain the rule.
- **A BILL NEEDS A `Building_WorkTable`.** Research benches are `Building_ResearchBench` and have no
  bill stack, so a recipe placed on one is a feature nobody can ever reach.
- **THE STAGER REFUSES A PACKAGE EDITED AFTER THE BUILD**, by hash. Rebuild, then stage.
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"*
  is reserved. `check-info-cards.py` is the authority.

---

## Findings recorded so nobody re-derives them

- **A sentence that names a count is a second place the count lives.** Derive it; let documents name
  none. This file said *"24 checkers"* within minutes of the twenty-fifth landing, and the rule
  caught it.
- **A PLAYER SETTING CAN RETIRE A RESEARCH TIER, and that is an improvement.** Commerce had the
  cleanest-looking T5 candidates in the mod until its knobs became sliders. **A research tier and a
  player slider over one number is two controls fighting**, and the right record is that the slider
  replaced the tier rather than that the tier is missing.
- **A tier may only exist where a player could name the effect.** Most of 278 constants die on a
  third test — a schema version, a tick interval or a loop bound is not tuning, it is the machine
  working.
- **Making a claim true beats softening it.** `build-site.py --check` was documented as failing the
  battery and could not, because it is not a `check-*.py`. `tools/check-site-generated.py` is the
  entry point.
- **Derived beats stored whenever the inputs are already saved.**
- **A def nobody wired is a job nobody finished** (invariant 131).
- **An outage is recorded, not re-investigated.**

---

## The live bug that is NOT ours

```
ReflectionTypeLoadException getting types in assembly RimBridgeServer:
expected class 'HarmonyLib.CodeInstruction' in assembly '0Harmony, Version=2.4.2.0'
```

`RimBridgeServer.dll` wants **0Harmony 2.4.2.0**; the profile snapshot records `brrainz.harmony` at
**2.4.2.0** as of 2026-09-27, so this may already be resolved on the machine. Our package loaded
clean in the same log either way. The fix is not in this repository.

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
python tools/check-queue-pointers.py                                  # and this, which neither can
```

`STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED`
exit 0. The mover returns **3** for unarchivable prose after a closed row, and writes nothing —
**indent the paragraph into the row it documents**, which is the mover's own first remedy and means
the note archives with its row instead of being stranded behind it.

---

## Is it done?

**The build is. The play is not.** The next action that unblocks anything is a launch, and only the
owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line — it carries the
fixture-tell attachment count, the fastest signal that the object register reached anything — then
`python .local/qa/bridge.py call rimworld/list_letters '{}'`.
