# NOW — handoff after compaction

**Single-focus tracker.** Distinct from the three-tier ledger:

| File | Grain |
|------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, **every owner direction verbatim** |
| `docs/DECOMPOSED.md` | smallest execution units |
| **`docs/NOW.md`** (this file) | **the handoff** |
| `docs/FINALIZED.md` | permanent archive |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

LAW #0 applies: owner words go in verbatim, everywhere. **This is now enforced** — see invariant #69.

---

## Active

**Nothing in flight. Tree clean, everything published, no half-finished task.** Written
deliberately for the session after a compaction.

### The one thing that will go wrong if you skip it

**The cascade is TEN refs, not eight.** Work is on `feature/bug-testing` now. The eight-ref
read-back that was the only publication receipt for forty-five checkpoints is:

```
forgejo, github  x  feature/connected-colony-portals, Prep, Develop, Main
```

and it is now that **plus `feature/bug-testing` on both remotes**. A publish that reads back eight
and stops has left the branch the work is actually on unpublished, silently. **Count the branch
you are on.**

### The second thing

**Use a FILE for any script with escapes or apostrophes, never a bash heredoc.** It mangled
`\n` into real newlines **five times** in the 0.12.46-dev batch, and then **three more times**
across 0.12.49 to 0.12.51 — once on a plain apostrophe in a closure script, twice on `\\s` inside
a regex. **Eight times in two days.** It is written down here because writing it down has not yet
been enough; the only thing that has worked is reaching for the Write tool first.

### State

| | |
|---|---|
| Branch | **`feature/bug-testing`**, cut from `feature/connected-colony-portals` at `12e12da` on 2026-09-30 for the play-testing phase. **Ten refs now**, not eight: the original feature branch plus Prep, Develop and Main on both remotes, and the new branch on both. `feature/connected-colony-portals` carries the build and stays where it is |
| Published | **0.12.62-dev**. `git log --oneline -1` is authoritative and the eight refs below match it. |
| Remotes | `forgejo` + `github`, all four refs each at that commit |
| Build | **204 C# files, 91 package files**, zero warnings, zero errors. **Measure this, never carry it** — it said 172 against a real 170 for five checkpoints and only came true by accident: `git ls-tree -r HEAD --name-only | grep -c '^src/.*\.cs$'` |
| Assembly | SHA-256 `5201C4A6D368DE5E2E3A94939BEC0D0AF5858A870A1A05F4AC991F2D94BE8774`, reproduced by two clean recompiles. **Re-read this from the build after the determinism run, never from memory or from this line** |
| Checkers | **FOURTEEN**, all passing. **The fourteenth is the only one that runs code rather than reading it**, and it exists because the thirteen that read text, the forty-five proofs and five hundred and fifty plants **all passed over a planner that could not produce one valid layout** -- `MaxRoomSpan` said 34 while the grand hall was 80, and no amount of reading either file can see two numbers disagree. `check-planner-layouts.py` builds `.local/harness/PlannerProbe` and runs `TrySelect` and `ValidateRooms` over 200 seeds at seven depths, demanding both that a layout is accepted **and that back-to-back pairs exist** -- because a plant that moved a pushed room one cell was missed by every proof when the revert guard quietly switched the feature off. **It never skips**: no dotnet, no install or no built assembly is a failure, not a pass. **The proof count is FORTY-ONE since 0.12.49-dev** -- `proof-coordinate-layout.py` was added after measuring that every constant in the coordinate planner could be changed with all forty existing proofs still passing. `check-info-cards.py` also caught a new keyed string saying *doorway* where the project's vocabulary says *door*. **The interpreter caught one during 0.12.47-dev** -- new proof claims named a variable `arrival` that the reachability section already used for an `re.search` match 200 lines later, and `TypeError: argument of type 're.Match' is not iterable` was the only thing standing between that and a silent pass. **Two of them caught me during 0.12.46-dev**: `check-compliance.py` flagged a patch for containing `PatchOperationReplace` **in the comment explaining why a replace is wrong** (it strips XML comments now), and `proof-starts.py` asserted the exact thing being reversed. **A checker that tests for mention rather than assertion has now cried wolf four times.** The thirteenth, `check-compliance.py`, is the compliance table made executable: a dated table of mechanical checks is the same defect as a dated count, and that one had been read as current for **thirty-six checkpoints** with three of its rows no longer true. **Two of its own rules caught it before any plant did** — the licence check flagged a comment that *denies* the GPL applies, and the assembly check read the wrong manifest key and reported *"0 assemblies, all from the official install"*. The twelfth, `check-def-fields.py`, refuses a def that sets a field the class does not have — RimWorld logs an unknown field and carries on, so one had been silently inert for fourteen defs across two checkpoints. It **caught itself twice** before it was right; see 0.12.37-dev. The tenth refuses player-facing text naming retired equipment; **the eleventh, `check-wiring.py`, refuses anything this mod authors that nothing reads** — the defect class that left the whole campaign unreachable until 0.12.11-dev |
| Proofs | **FORTY-ONE** in `.local/register/proof-*.py`, and **THIRTEEN** plant suites in `plant-*.py`. **Both are tracked in git now** — see *What the collaborator gets* — after `.local/` was found to be hiding the entire verification suite from a clone. **Run them by exit status, not by grepping their output.** Measured at 0.12.22-dev: **17 end `PROOF HELD`, 2 end `PASS:`, and 2 end on a WRAPPED CONTINUATION LINE** whose last line is not a status token at all. A grep for any one phrasing skips the rest; that is how four live proofs went unrun for most of one session, and the two wrapped ones would be missed by every phrasing. **Exit status is the only reading that cannot be fooled by formatting** |
| Chart | **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document |
| Register | `python tools/register-query.py families\|family <x>\|find <x>\|row <n>\|traces\|trace <code>\|card <x>\|use <code>` — **`use <trace>` is the query the LAW actually describes**: for every mod bearing on what you are building, what the register says about how to use it. Added 0.12.24-dev, because until then the `card` column printed the words *"open card"* and every real instruction was unreachable from the tool — **query by `trace`**: it names the Rimrooms feature a row bears on, which is the question *"what applies to what I am building"*. **The HTML is the register**, never the xlsx. **It is GUIDANCE, not law** (owner, 2026-09-29) |
| Readable HTML | `python tools/make-readable-html.py` → `outputs/readable/index.html` |
| Game launches | **NINE, all by the owner on 2026-09-30. THE NINTH WORKED: the owner walked a Backrooms level for the first time — the coordinate generated, the gate was blue, the crossing carried a pawn across. Twenty-three defects, every one ours, still not a single mod conflict.** What the ninth found was almost entirely content that was switched off at depth 1 on purpose.** The eighth confirmed the `Door` fix in the running game — **587 cross-reference errors down to ZERO** — but never reached a map: the company setup page stopped drawing after three lines because not one of the package's eight listings set Core's `maxOneColumn`, so an overflowing listing painted itself off the edge of the world with no exception.** The seventh produced **587 red lines from one line**: `<li Class="CompProperties_Colorable" />` names a type RimWorld does not have, and a bad `Class` discards the **whole ThingDef** — so `Door` and `Autodoor` left the game, 585 further errors were other defs failing to cross-reference them, and the game **never left the main menu**. The sixth found a conduit carpet sized for 12x12 rooms blowing a 512-cell cap **eightfold** at 80x80, which meant **no 300x300 coordinate could ever have generated**. An EIGHTH is what settles whether a coordinate generates at all. They have found **eleven defects** and every one was ours. **The fifth found the most expensive one in the project's history: a light count that had stopped every Backrooms level from generating since 0.7.8-dev, thirty-nine checkpoints.** **Still not a single mod conflict.** The fourth launch is also the first whose evidence came from the **running game** rather than from the log alone: the owner said *"you can use the api mod you have that we installed last so u can see wtf rimworld is doing"*, so RimBridgeServer 2.1.1 in direct mode, read-only, against their own launched process. See *What the fourth launch found*. The staged copy is current at this checkpoint, hash-verified |

### How to work, owner direction 2026-09-29

> *"lets start doing shit correctly and efficiently and keep going iin batches of items completed
> so we have less work constantly pushing and all of that"*

**Batch related rows into one checkpoint and publish once.** 0.12.36-dev closed **six** rows in one
publish, and they were related on purpose: quarantine is an area question, so the area rows rode
with it, and the two ordinary-map rows were proved in the same sweep. Chain the work, then do one
build, one determinism run, one checker and proof sweep, one commit, one cascade.

### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait. Two standing corrections that change how to read
everything below:

- **The mod register is GUIDANCE, not law.** *"remmebr its not law but guidance"*. Consult it, let
  it shape the design, say what it said — but a row never vetoes work.
- **Tests are not the concern yet.** *"test cases arnt being worried about right now we are trying
  to get the build complete so we can test"*. **Unverifiable-without-a-launch is never a reason to
  defer building something.** I parked the world exit for that reason and was overruled, correctly.

---

## Is it done? THE BUILD IS. The play is not, and nothing else can start until it does

**ZERO build items left.** Counted at 0.12.42-dev. **Ten rows closed this batch** — 206, 302, 1054, 1268, 1269 and 1286–1290. **Thirty-seven rows across the last seven batches.**

**The one numbered entry under *What is left* is a closed record**, kept deliberately so nobody rebuilds row 761. Everything else in that section is either *cannot close before the game runs once* or *excluded by the owner*.

**So the answer to the heading has changed.** The build is done. What is not done is **play**: about 8 rows need the game to run once, and the package in the game folder is sixteen checkpoints stale. **Re-staging and a first launch is now the only work that unblocks anything.**
Plus about **8 rows that cannot close before the game runs once** and **9 the owner excluded**.

Queue, one consistent pattern, command beside the number:

```
grep -c '^\s*- \[ \]' docs/TODO.md     # 42 open
grep -c '^\s*- \[~\]' docs/TODO.md    # 45 partial
grep -c '^\s*- \[x\]' docs/TODO.md    # 510 done
```

**And the master backlog, which row 1054 said understated the build by roughly thirty points.**
It was **56**. `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` went from **122 open / 134 done**
to **66 open / 190 done**, every flip naming the checkpoint that closed it, every original word
kept, and **not one runtime-acceptance row touched**.

**The raw open count overstates, and the reason is worth the paragraph.** Rows closed by work
that shipped the same day keep their `[ ]` until somebody flips them — and **NINE separate rows
this session turned out to be already built, already true, or answered by Core**:

| Row | What it actually was |
|---|---|
| 227 | surgery across a gate **cannot be built** — `Bill_Medical`'s patient *is* the bill giver |
| 308 | the contradiction was already computed and thrown away |
| 493 | the recorder fold had been decided fourteen checkpoints earlier |
| 1266 | **Core forbids all eleven givers from moving anything between maps** |
| 98 | six reasons can stop a gate and **not one reads an adjacent cell** |
| 99 | the row's premise was wrong — a gate link has **no distance or LOS check** |
| 1011 | depth, band, wealth and seeding all already there |
| 1101 | a coordinate's floors were **ordinary layerable Core terrain** all along |
| 725 | **seven of its nine subsystems** existed under different names |

**CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT.** That habit is the single highest-value
thing in this file. It has saved more work this session than every other practice combined, and
twice the row's own *“confirmed absent by grep”* was the thing that was wrong.

### The package is staged, and SIXTEEN checkpoints behind

The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.42-dev** —
**sixteen checkpoints of work are not in the game folder.** **This is now the single most useful thing anybody can do with this repository.** Re-stage before any launch:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

It backs up the existing folder, hash-verifies every file against the build manifest, and records
`ProfileChanged = false; GameLaunched = false`. **It never touches the mod list and never starts the
game.** When it was first run this session the staged copy was **0.4.0-dev** — twenty-two
checkpoints stale, so nothing built in this project's history had ever reached the game folder.

---

## WHAT THE LAUNCHES HAVE FOUND — eleven defects, every one ours

**Third pass, and this one was the root of the map complaints.** Owner: **"the map generator
is not our mod"**. `ScenPart_RimroomsStart` replaced Core's `Base_Player` — elevation, fertility,
biome terrain, caves, rocks, plants, animals, ruins, rivers, roads — with a **four-step** generator
of ours, and our terrain step flattened **every cell** to one terrain. Hence *"bare dirt not even
vegitation"*. And the owner previews tiles with **Map Preview**, which simulates the **real**
generator, so every map they rerolled against was a picture of a map the mod then discarded: **the
preview was right and the game was wrong.**

Core generates the tile now. The two gen steps are **added** to `Base_Player` by a patch — never a
replace, which would drop every step Core and other mods put there. **The load-bearing half: the
steps had to stop throwing.** They live in the generator that makes *every* player map now, so a
throw would break a second settlement, a quest site, a reloaded world. `StartForMap` returns null
and the proof refuses a `throw` in its body.

**Second pass, and these two were the worst of the lot.**

**The mod threw away the player's chosen map size.** `Find.GameInitData.mapSize = startDef.mapSize`
forced **50 for the Store** against RimWorld's smallest option of **200** — 2,500 cells where a
default map has 62,500, the shop taking 41% of it. *"Not the map i chose ... a super micro blocked
in area"* was literally accurate. The layout is offset onto the player's own map now, centred and
clamped. **Nothing was ever sealed** — all three layouts flood-fill to 100% reachable, and that
measurement now runs every checkpoint.

**The Store had no Backrooms connection at all.** `SoloGroupOpening` returned early unless
`insideStart`, and nothing in the generator creates one. The **deeper** and **world-tile** halves
the owner described already existed; only the seeding was missing. Any start naming an
`emergenceDoorCell` now begins with a permanently open natural gate.

---



**The game ran for the first time in this project's history on 2026-09-30, and found three defects
in the first minute. All three were ours.** That is the single most valuable hour this repository
has had, and it is the argument for launching again rather than building more.

**FIXED — the blank page, and the fix is now CONFIRMED by a second launch: the page renders.** The state guard was a diagnosis when it shipped; it is an observation now.

**FIXED — two controls that were drawn but unreachable.** With the page rendering, the next report was *"i cant start the game"* and *"there is no box to type in my company name"*. The confirm checkbox was the **last line of a scrolling list**, so Start refused and the thing that would satisfy it was off screen; the name field sat a few hundred pixels down that same list. The log proved `DrawReview` completed, so both were drawn — **and drawn is not the same as reachable.** Both are pinned outside the scroll view now. **A control the player is required to use must never be scrollable out of view.**

**And the same change nearly shipped an authored palette.** The name field's first draft used `DrawBoxSolid(field, new Color(0.12f, 0.12f, 0.12f))`, and it would have gone through because `check-display-style.py` scanned only `UI/` while that page lives in `Scenario/`. **A rule that only looks where it expects trouble has a blind side.** The scope is every file that draws a window now — 21 instead of 20.

**The original diagnosis, for the record.** `Page_RimroomsCompanySetup` opened after EdB Prepare Carefully with its
title and both buttons drawn and its body **completely empty**, and **nothing in the log**. Cause:
**Unity's IMGUI state is process-wide and not one of this package's six window entry points reset
any of it.** Each inherited whatever the previously drawn mod left in `GUI.color`, `Text.Font` and
`Text.Anchor`; a leaked zero-alpha colour paints nothing and logs nothing. Core draws the page title
and buttons and sets its own state, which is exactly why the frame was visible and only our content
was not.

**That is the other half of a claim made at 0.12.40-dev.** This package authors no colour and no
font size — true, and still true. **Authoring nothing is not the same as assuming nothing.** And
`check-display-style.py`, written in the same checkpoint to hold that claim, **forbade `GUI.color =`
outright and so blocked its own fix.** A rule stated as a pattern ban rather than as a purpose will
eventually forbid the right thing.

**FIXED — the hotkey is `Backslash`.** Bound by nothing in Core and nothing in the profile, and **the proof now refuses any function key at all** rather than only the ones Core takes, which is the portable form of the rule that would have caught this.

**FIXED — the glow pods are pre-placed** in each start's fixed facility, so EdB never parses them and the warning is gone. Eleven cells, **every one computed free**, because `GenStep_Headquarters` throws on a clash rather than skipping it.

**NOT A DEFECT — the Store's missing bench.** Owner: *"the store start has a natural portal and to build a machanical one they need to contact the company and resaerch whats needed"*. `beginsInCorporationContact` false and `completedProjects` empty for the Store and solo, against Async's eight. **The readout was the defect**, calling a designed progression step a deficiency; it has three conclusions now for the three real situations.

**The original, for the record — F12 collided with HugsLib.** HugsLib binds F12 to *Publish log file*, the exact thing
wanted while bug-hunting. 0.12.40-dev took F12 after checking it against **Core only**. **Every one
of F1–F12 is bound across Core plus the 288 installed mods.** Register row 85 says *"avoid
overriding hotkeys."* **Needs an owner decision** — see the queue row.

**OPEN — EdB cannot classify our GlowPod scenario grant.** Logged twice per setup. `GlowPod` is a
Core **Building** granted as a starting thing in two scenarios; vanilla minifies it automatically,
EdB's equipment database has no entry for it. Cosmetic-looking, ours, and noise on every setup.

**ANSWERED, and it found an asymmetry nothing stated.** Owner: *"shouldnt that page list the
starting equipment and supplies added from the company to get a gate up quickly as building
minified"*. **No, minified buildings are not needed** — the Async facility already places a
machining table, a console, a battery at half charge, three generators and nine doors, and the
scenario grants 250 steel against the bill's 100. **The page just never connected any of it to the
gate**, which is why the question got asked. It now reads the recipe for the cost and the bench and
states what is standing. **And counting the three starts turned up this:** Async 9/1/1/1/3;
**Furniture Store 8/0/1/1/1**; **Solo 1/0/0/0/0**. **Two of three cannot raise a gate from what
they arrive with.** Solo is the design and the readout says so. **The Store missing only a bench
looks like an oversight and is recorded for a decision.**

### The lesson that outranks the fix

**`docs/PLAYING.md` promises nothing fails silently.** A blank page with an empty log was that
promise broken. So the setup page now **cannot go blank silently regardless of cause**: the
introduction draws outside the scroll view, the body is wrapped so a throw is logged **and painted
on the page**, and the listing closes on every path. **If it fails again it will say what broke.**

**And be honest about the state guard: it is a diagnosis, not an observation.** The evidence is
strong — frame drawn, body not, nothing logged, six windows resetting nothing in a 288-mod load.
But nobody has yet seen that page draw correctly. What is certain is the reporting half.

---

## THE BRANCH CHANGED — read this before publishing anything

**Work happens on `feature/bug-testing` from 2026-09-30.** It was cut from
`feature/connected-colony-portals` at `12e12da`, the commit that fixed the map placement and the
Store's natural gate, and pushed to both remotes.

**The cascade is now TEN refs, not eight.** The eight-ref read-back that has been the only receipt
for forty-five checkpoints was:

```
forgejo, github  x  feature/connected-colony-portals, Prep, Develop, Main
```

and it is now that **plus `feature/bug-testing` on both remotes**. A publish that reads back eight
and stops has left the branch the work is actually on unpublished. **Read back the branch you are
on, every time, and count it.**

`feature/connected-colony-portals` is not deleted and not abandoned — it holds the build history
and sits at `12e12da`. Bug fixes found in play land on `feature/bug-testing` and cascade from
there.

---

## DO THIS FIRST — READ THE LOG FROM THE ELEVENTH LAUNCH, AND THEN READ THE LETTERS

**The log was CLEAN and the game was broken.** That is the single most useful thing the tenth
launch taught, and it changes the first job.

Zero red lines. `0.12.61-dev` loaded, the mod's own build line printed, the company branch
initialised, no exception anywhere. And the owner had no Backrooms, no blue door and no way
through. **The evidence was a letter**, sitting unread on their screen:

```
The company could not finish startup:
No safe first-site layout was found within the bounded attempt limit.
```

So: **`Player.log` first, and then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.**
A refusal this package produces on purpose is a letter, not an error -- it is written that way
deliberately -- so a clean log says nothing about whether anything worked.

### WHAT BROKE IT, AND IT WAS OURS, FROM THE CHECKPOINT BEFORE

`ValidateRooms` refuses any room wider than `MaxRoomSpan`, which computed the span of a room
filling **one** slot: 34 cells. 0.12.61-dev gave the threshold a grand hall spanning **two**
slots: 80. Candidates 0, 1 and 2 all carry the hall, so **all three were refused every single
time**, and the fallback was refused whenever any room's span varied upward -- which over twenty
rooms is always.

`SoloGroupOpening.Open` is five steps in order and the coordinate is step 2. **Step 3 marks the
door and step 4 registers the edge, and `IsLiveGate` needs both.** So one failure produced every
symptom the owner reported, and none of them were about the door.

### THE INSTRUMENT THAT CAME OUT OF IT -- USE IT BEFORE ASKING FOR A LAUNCH

```
python tools/check-planner-layouts.py
```

**Checker fourteen, and the only one in the battery that runs code rather than reading it.** It
builds `.local/harness/PlannerProbe` against the compiled assembly and runs the real
`TrySelect` and `ValidateRooms` over 200 seeds at seven depth bands.

Thirteen checkers, forty-five proofs and five hundred and fifty planted faults **all passed over a
planner that could not produce one valid layout.** They read source text, and two numbers in two
files disagreeing is not a thing source text shows. **The planner is pure -- no map, no world, no
defs, no global random -- so this was always answerable at the desk, and for a whole checkpoint
nobody asked.**

It demands two things, and the second matters as much as the first: that a layout is accepted,
**and that back-to-back pairs actually exist.** A plant that reverted one `+ 1` was missed by all
forty-five proofs, because the new revert guard caught the resulting overlap and put the room back
-- so every layout stayed valid and the feature was simply **never produced again.** Switched off,
silently, with every claim still passing. That is this project's dominant defect class and the
probe is the answer to it.

**Anything else that is pure and has a validator deserves the same treatment.** The content
builder, the frontier draw and the archetype selector are all candidates.

### WHAT THE ELEVENTH LAUNCH HAS TO SETTLE

**Everything the tenth was supposed to settle, because it never generated a level.** In order:

1. **Does a coordinate generate at all** -- the gate blue, the Backrooms map present, a pawn able
   to cross. **Everything below depends on this.**
2. **24 rooms at depth 1** plus one grand hall of eighty cells, back-to-back pairs, shaped
   corners, varied corridors
3. **Is it a maze** -- branches off three slots in four, dead ends, rooms of different sizes
4. **Is the spawn hall still grand and yellow**, and does the yellow stop a few rooms out
5. **Two portals per level**: one out to the world map, one deeper. Guaranteed, not drawn
6. **Loot, weird rooms, people, bodies, events** -- out past the yellow rooms
7. **A lamp on every pillar**, in four tones, the dim one dim rather than off
8. **Doors that go nowhere** -- an opening a third along a blank wall, onto rock
9. **Furniture spread through rooms** rather than in the four corners

### THINGS THAT WILL WASTE A LAUNCH IF FORGOTTEN

* **The owner's existing save still will not change.** A coordinate is generated once and
  recorded, and the one in their current game was never generated at all -- it failed. **A new
  start is what shows this work.** The branch that failed startup keeps its failure.
* **`GuaranteedFrontiers` and `RoomArchetypeService` hold caches of live `Thing`s and link
  graphs**, cleared in `BackroomsContainment.FinalizeInit`.
* **Register row [218] Stargates! is stance "No integration", and the owner overruled it.** The
  register is guidance. Their component rides an ordinary Core door, their mod is untouched, and
  the build has no reference to their assembly.

### THE TRAP, UPDATED

**A claim that pins call text proves a call happened. It cannot prove the call was legal.**
`PushAgainst(rooms[rooms.Count - 1], rooms[host])` was pinned as literal text and held while two
of that method's four branches produced a layout the validator refuses outright.

And **an absence claim cannot read raw source**: `"a.maxX == b.minX" not in planner` failed
against correct code because the comment explaining why that test is wrong quotes it. Thirty-sixth
instance of that one class. `proof-coordinate-layout.py` keeps a comment-free `code()` view now
and every absence claim reads that.

## DO THIS FIRST — READ THE LOG FROM THE TENTH LAUNCH

**Read `Player.log` before anything else, and read it before telling the owner anything works.**
Four checkpoints in a row were answered from proofs rather than from a log and four times the
answer was wrong.

### THE NINTH LAUNCH WORKED. THE OWNER WALKED A BACKROOMS LEVEL.

*"okay it fucking worked!!! im in the backrooms!!!"* — first time in nine launches. The coordinate
generated, the gate was blue, the crossing worked, and they explored a whole level.

**And almost everything they found wrong was switched off on purpose.** Three separate systems
carried the same gate, and the defs said so out loud:

```
RR_RoomArchetypes.xml:  "minDepth is what keeps the shallow yellow rooms empty.
                         Nothing here can appear at [depth 1]"
```

All fourteen archetypes were `minDepth >= 2`; every inhabitant family, including the missing
person and the recent dead, was `minDepth >= 2`; every anomaly event was `minDepth >= 2`; and
`RockIntrusionCells`, `CorridorHalfWidthBetween` and `Derange` each refused to run at depth 1.
**A first level had no laboratory, no ward, no storeroom, no loot, no people, no bodies, no
events, no shapes and no varied corridors. It was built to be empty and the owner explored all of
it.**

### THE RULE THAT REPLACED ALL OF THEM

**Distance from the spawn hall counts as depth.** Three links out is one level deeper, capped at
four bands. Near the arrival it is the yellow rooms exactly as before; the further you walk the
more of the existing library the level can reach. **Fourteen archetypes were already written and
the first level could not touch one of them.**

It is the owner's own sentence made literal: *"the normal yellow backrooms look isnt the whole
floor but the main spanw room and going deeping in can mean the numner of branch hallways and
rooms distancing from the main portal spawn"*.

### WHAT THE TENTH LAUNCH HAS TO SETTLE

1. **Does a level still generate at all**, with 24 rooms at depth 1 instead of 9, back-to-back
   pairs, shaped corners and varied corridors. **Everything else depends on this.**
2. **Is it a maze** — branches, dead ends, rooms of different sizes and shapes
3. **Is the spawn hall still grand and yellow**, and does the yellow stop a few rooms out
4. **Two portals per level**: one out to the world map, one deeper. Guaranteed, not drawn
5. **Loot, weird rooms, people, bodies, events** — out past the yellow rooms, not beside the door
6. **A lamp on every pillar**, in four tones, and the dim one dim rather than off
7. **Doors that go nowhere** — an opening a third along a blank wall, onto rock
8. **Furniture spread through rooms** rather than in the four corners

### THINGS THAT WILL WASTE A LAUNCH IF FORGOTTEN

* **The owner's save will not change.** A coordinate is generated once and recorded; everything
  here affects levels generated from now on. A new level, or a new start, is what shows it.
* **`GuaranteedFrontiers` and `RoomArchetypeService` hold caches of live `Thing`s and link
  graphs**, cleared in `BackroomsContainment.FinalizeInit`. If either leaks across a load it
  hands a new game the previous game's doors.
* **Register row [218] Stargates! is stance "No integration", and the owner overruled it.** The
  register is guidance. Their gate component rides an ordinary Core door, their mod is untouched,
  and the build has no reference to their assembly.

### THE TRAP THAT KEEPS COSTING CHECKPOINTS

**Three times in this checkpoint a claim guarded a DEFINITION while a plant deleted the CALL.**
`MakeHall`, `VariedRoomSpan`, `SpawnPillarLamps` — each defined, each correct, each unreached, and
every numeric claim about them still passing. **Computing a value correctly and using it are two
different facts.** Assert the call site.

And nine claims refused these changes outright, every refusal correct. One required depth 1 to be
*"at most eight rooms of at least sixty cells"* — a faithful reading of an earlier direction, and
**the exact claim that produced the nine-room warehouse.** Another caught that the wall-material
gate still tested `coordinate.Depth`, so the per-room material was never reached on the level the
owner actually walked. **A proof refusing a change is the proof working; go back and read what it
was protecting before you edit it.**

## DO THIS FIRST — READ THE LOG FROM THE NEXT LAUNCH

### THE EIGHTH LAUNCH NEVER REACHED A MAP: the setup page stopped drawing after three lines

**0.12.55-dev loaded clean — the owner's log went from 587 cross-reference errors to ZERO**, and
`[Rimrooms] odd-origin marker attached to 2744 thing definitions` is up from 2742, which is `Door`
and `Autodoor` back in the game. The `CompProperties_Colorable` fix is **confirmed in the running
game**, not from proofs.

**But the company setup page drew three lines and stopped**, so that launch never reached a map.
No roster, no funding, no supplies, no facility, one of five gate prerequisites — and **no
exception anywhere in the log.** The owner: *"there are no lists or supplies on the card pop up at
all.. so what the fuck?"*

`Verse.Listing.GetRect` → `NewColumnIfNeeded` → unless `maxOneColumn` is set,
`curY = 0f; curX += ColumnWidth + 17f` the moment content outgrows the rect. `Begin` sets
`ColumnWidth` to the **full width**, so the overflow is drawn a whole width to the right —
**outside the group `Begin` opened and clips to.** Painted off the edge, silently. And `CurHeight`
is `curY`, which `NewColumn` just zeroed, so `contentHeight = CurHeight + 20f` measured the
*second* column: the content shrank, the wrap came sooner, and it settled at three lines. That is
also why there was no scrollbar.

**Eight listings in the package, not one set the flag.** Seven fixed, including the Operations
board — the main window of the mod, which was carrying the same silent truncation. The settings
window keeps its deliberate two columns.

**THE LESSON, AND IT IS THE SAME SHAPE AS THE SEVENTH LAUNCH.** Every line of our code was
correct. The defect was **an unset Core default interacting with a value Core resets** — invisible
to any proof that reads our source, exactly like a `Class` name that does not resolve. **When a
claim is about whether something *works* rather than whether it is *written*, assert the engine's
contract, not our text.** `proof-setup-page-draws.py` does that: every listing in the package must
declare whether it is one column or more, and a new one that declares neither fails.

### AND THE SUPPLIES SECTION WAS ASKING THE WRONG OBJECT

It read `Find.Scenario.AllParts` — the **live** scenario — and EdB Prepare Carefully rewrites
exactly those parts (`ReplaceScenarioPatch`, `ShouldReplaceScenarioPart`, `OriginalScenarioParts`,
`ReplacedScenarioParts`, `CreateScenarioPartForCustomizedEquipment`). It reads the **authored
`ScenarioDef`** now, found by the start it declares, and draws **both** lists, because the owner
asked for *"the equipemnet for the gate that u get added to ur start on top of what u fill out in
edb prepare carfully"*. Register row **[85]** is Optional/Provisional and says *never a runtime
dependency* — nothing is patched, named in code, or required.

**A content bug this exposed by accident:** `RR_Setup_GateCost` promised *"Those are in the
supplies below."* The bill wants **100 steel and 8 components**; the **Furniture Store start
arrives with 80 steel and no components at all.** Written against the Async start, asserted for
all three.

### ORIGINAL ORDER OF BUSINESS, STILL UNSETTLED

**Read `Player.log` before anything else, and read it before telling the owner anything works.**
Three checkpoints in a row have now been answered from proofs rather than from a log, and three
times the answer was wrong.

### WHAT THE SEVENTH LAUNCH FOUND: 587 RED LINES FROM ONE LINE

**The game never left the main menu, so the seventh launch tested NOTHING but def load.**

```
Exception loading def from file Buildings_Structure.xml: System.ArgumentException:
  Could not find type named CompProperties_Colorable from node
  <li Class="CompProperties_Colorable" />
Could not resolve cross-reference to Verse.ThingDef named Door ...        (x529)
Could not resolve cross-reference: No Verse.ThingDef named Autodoor ...   (x59)
```

Every one of the 587 errors named `Door`, `Autodoor` or `CompProperties_Colorable` **and nothing
else**. There is no `CompProperties_Colorable` type: `CompColorable` takes a plain
`CompProperties` with a `compClass`, as Core does for textiles, apparel and the Ideology floor
coverings — and the last of those are buildings, so it was the right mechanism for a door all
along, spelled with a class that does not exist. **A bad `Class` throws out of
`DirectXmlToObjectNew`, which discards the entire ThingDef**, so `Door` and `Autodoor` left the
game and 585 further errors were other defs — 541 of them vanilla prefabs — failing to
cross-reference them.

**Still not one mod conflict in seven launches.** Doors Expanded and Mechhive appear in that log
only as victims of our missing `Door`.

### THREE THINGS TO KNOW BEFORE WRITING ANOTHER PROOF

1. **A proof that reads text cannot tell whether a resolver resolves.** The forty-second proof,
   `proof-class-resolution.py`, is the first that **imports the checker and interrogates it**.
   When a claim is about whether something *works* rather than whether it is *written*, execute
   it. The first draft of that very resolver split the metadata heap on NUL, which misses
   suffix-shared names and **rejected `Building`** — failing correct code, which is worse than
   the hole it closed, and entirely invisible to a text-reading proof.
2. **Asserting our XML contains a string proves we wrote it, never that the game can use it.**
   `proof-gate-links.py` required `'<li Class="CompProperties_Colorable" />'` as its evidence that
   a gate is blue — **it held the bug in place**, and the matching plant mangled that string and
   watched the proof fail, which is a plant proving a broken line was load-bearing.
3. **Run EVERY plant suite, not the ones you touched.** Doing so found a plant that could never
   have been caught: it planted a comment at a proof that strips comments on purpose. The proof
   was right and the plant was wrong — the inverse of the usual trap.

### What the EIGHTH launch has to settle, in this order

1. **DOES A COORDINATE GENERATE AT ALL.** Fourth attempt, and the generator has still never run
   end to end. Everything below depends on it.
2. **is the back-room door blue and glowing** once a level exists
3. **select a colonist, right-click the gate → "Enter the gate"** — they should walk over and
   come out on the other map
4. **every other door in the colony is unlit and unchanged** — the `IThingGlower` veto
5. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything
   matching
6. **one level in, the materials go wild** — two tables in one room in different stuffs, each
   room's walls a different material. Newest thing in the build, least like anything that has run
7. **no cave-in** when a wall or a pillar is deconstructed
8. **Operations → Places** lists the colony and any level, with the budget as `n/5`

**What changed since the sixth launch, and why it matters more than it sounds:** a systematic sizing
pass over every constant in the generation path found **two more that would have killed a
coordinate**, and one of them would have killed it *invisibly* — level 0 would have generated and
every level below it would have died. See *THE LESSON* below. So the seventh launch is the first one
where the generator has a real chance of completing.

```
grep -n -i "rimrooms\|Error in GenStep\|Exception" \
  "$USERPROFILE/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
```

**And the bridge, if the process is still up**, which answers in one call what the log only hints
at — see *The bridge is available now*. `.local/qa/bridge.py` is the scratch client:
`list`, `call <tool> '<json>'`, `scan <minx> <minz> <maxx> <maxz>`.

### What is actually verified, and what is not — be honest about this

The owner asked *"they work now right?"* and the answer given was **no, and I will not claim it**.
That split still holds and the next session must not quietly upgrade it:

| | |
|---|---|
| **Measured in the running game** | the Store's back-room **door exists** at (160, 161) carrying the emergence comp with `Mark as way home` enabled; Deconstruct and Uninstall both offered; a granite-block wall where the burn removed a Granite formation; `list_colonists` non-zero after the arrival fix |
| **Source-verified only, NEVER EXECUTED** | the light-count fix, the **entire 300x300 generator**, pillars, room shapes, corridor widths, the map budget, release, carry-a-doorway, and the material split. **Forty-one proofs check properties of code, not behaviour of a running game.** |

**The sixth launch DID run 0.12.52-dev, and the generator failed again** — on a different
constant, the conduit cap. So the correct statement is sharper than *"never run"*: **the
coordinate generator has never once completed.** Everything downstream of it — the gate marking,
the connection, the glow, the walk-through, level 0's look, the material split, the pillars, the
shapes — has therefore **still never executed**, because none of it is reached until a level
exists.

That is why item 1 of the seventh-launch list is the only one that matters until it passes.

**The one thing de-risked without a launch:** `CandidateIsSafe` was modelled against the new
layouts at **every depth across six seeds** — every room reachable, zero failures — so generation
should be *accepted* rather than refused with `RR_Generation_NoSafeCandidate`. That was the
likeliest silent killer. It is not proof that it runs.

### The two gates are completely different things, and only one should exist yet

**The natural gate** is the one to check first, and the chain that has to hold is:

```
SoloGroupOpening.Open
  1. CreateDiscoveredCoordinate      mint the place
  2. DestinationService.EnsureSite   GENERATE THE 300x300 MAP   <- failed at launch 5
  3. CompRimroomsEmergence.Mark()    mark the Store's back door
  4. RegisterNaturalAddress          register the connection
```

Step 2 failed on the fifth launch for the light-count reason, so **steps 3 and 4 have never run.**
If the back-room door is still an ordinary steel door, step 2 failed again and the log names the
key. Look for `RR_Event_NaturalGateOpening`.

**The machine gate is NOT there and is not supposed to be.** Owner, verbatim: *"the store start
has a natural portal and to build a machanical one they need to contact the company and resaerch
whats needed"*. The Store ships `Battery`, `CommsConsole` and `WoodFiredGenerator` — **no Autodoor
and no TableMachining.** So the player must build a Machining Table and an Autodoor, designate
door/console/battery/bench on Operations' **Machine** pane, then run `RR_AssembleMachineGate`:
**100 Steel + 8 ComponentIndustrial, 6000 work, Crafting**, no research prerequisite on the recipe
itself. The setup page's readiness review already names the missing hardware.

### WHAT THE SIXTH LAUNCH FOUND, AND WHY IT IS THE SAME SHAPE TWICE

**The level never generated. Again. The cause was new and it was ours.**

```
[Rimrooms][Generation] Site layout stopped: RR_Generation_ContentPlacementFailed
  at GenStep_BackroomsDestination.SpawnNativeConduit
  at GenStep_BackroomsDestination.SpawnNativePowerNetwork
```

`MarkLayoutReady` never ran → `SoloGroupOpening` stopped at step 2 → the Store's back door was
**never marked**. **An unmarked door is an ordinary steel door**, which is the whole of what the
owner saw: *"its not blue!!! it doesnt have a light aura, and it in no way is a portal"*.

**The cause, measured:** the power grid carpeted every powered room with conduit. ~100 cells at
12x12 rooms. At depth 1 a `service_passage` is **60x80**, so `ContractedBy(1)` is **4,524 cells**
against `MaxNativePowerConduits = 512` — **an eightfold blowout on the first powered room, every
time.** No 300x300 coordinate could ever have generated.

**THE LESSON, AND IT HAD ALREADY COST TWO LAUNCHES.** Both the light count at 0.12.48-dev and
this conduit carpet were **assumptions about scale that a constant quietly encoded**, and both
survived every proof because a proof reads source text and cannot see that a number no longer
fits. **When a dimension changes, go and size everything that was written against the old one.**

**0.12.54-dev did exactly that, once, instead of one bug per launch** — and found **two more that
would have killed a coordinate.** `FindConduitRoute` threw twice when a consumer could not be
reached, and `MaxNativePowerConduits = 512` was sized for 60x60: modelled against what the routing
actually does, a coordinate needs **460 cells at depth 1 rising to 1,436 at depth 6**. Depth 1
fitted under 512 **by forty cells**, so the seventh launch would probably have generated level 0
and killed every level below it — **the worst failure mode there is, because it looks fixed.**

The cap is 4,000 with 2.5x headroom at double the consumers, exceeding it stops the wiring instead
of throwing, and an unreachable consumer is skipped. **The sizing is a proof claim computed from
the planner's own constants**, so it cannot silently stop fitting again — and it refuses a cap so
large it could never bind, because that is not a cap. Seven other constants were sized and are
fine, recorded in `docs/TODO.md` rather than left implied.

### What the SEVENTH launch has to settle, in this order

1. **DOES A COORDINATE GENERATE AT ALL.** Third attempt. Everything below depends on it, and the
   generator has still never run end to end.
2. **is the back-room door blue and glowing** once a level exists
3. **select a colonist, right-click the gate → "Enter the gate"** — they should walk over and come
   out on the other map
4. **every other door in the colony is unlit and unchanged** — the `IThingGlower` veto
5. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything matching
6. **one level in, the materials go wild** — two tables in one room in different stuffs, each
   room's walls a different material. Newest thing in the build, least like anything that has run
7. **no cave-in** when a wall or a pillar is deconstructed
8. **Operations → Places** lists the colony and any level, with the budget as `n/5`

### The three things the sixth launch changed, and how to check each

| | |
|---|---|
| **it generates** | the carpet is gone. `ConnectStrayConsumers` wires whatever the dressing added, **after** it exists, using the same `CompPowerTrader` sweep the validator uses to detect a stray — so report and repair cannot disagree. `TrySpawnNativeConduit` returns where the throwing form threw: a dark corner can never cost the coordinate again |
| **it looks like a gate** | `CompGlower` + `CompColorable`, both Core, both settable per instance — blue and casting light with **no new texture and no new def**. **The trap was that a glower on `Door` lights every door in the game**; Core's `IThingGlower` lets our comp veto it, so every ordinary door is provably dark by Core's own rule. Only a gate with a **real network edge** lights up |
| **you walk through it** | the travel job always did this correctly. **What was missing was where a player looks for it** — it was a gizmo plus a float menu, which is a dispatch console rather than a door. `CompFloatMenuOptions` is Core's right-click hook and that is where it lives now. The order is still `OrderCrossing`, the rule is still `PortalTraversalPolicy` |

### AND THE STARGATE COMPLAINT WAS FAIRLY AIMED — read this before designing anything else

Owner, after saying it repeatedly: *"ive said stargate mod repeaditly is how the gates work but u
keep fucking ignoring me and doing you own fucking thing"*.

**They were right, and the specific failure is worth naming so it is not repeated.** *"Like the
stargate mod"* was a statement about the **interaction** — you walk a pawn into a door and they
come out on another map — and it was repeatedly heard as a statement about the **destination**,
which the build already handled. The travel was correct for checkpoints; the way to ask for it was
buried where no RimWorld player would look.

**Register row [218] Stargates! is stance "No integration".** That means *do not depend on it or
adapt to it*. **It has never meant ignore it as the interaction model**, and treating those as the
same thing is how three checkpoints passed with the order in a gizmo. When the owner names a mod
as how something should *feel*, read it.

---

## The re-stage command and the old fifth-launch list

### The bridge is available now, and it changes how to diagnose

Owner direction, 2026-09-30, verbatim: **"you can use the api mod you have that we installed last
so u can see wtf rimworld is doing"**. **RimBridgeServer 2.1.1 is installed and it answered
questions in one call that would have taken a launch each to guess at.**

Direct mode, and the only inputs are the owner's own log and process:

```
grep -n "RimBridge" "$USERPROFILE/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
    [RimBridge] GABP server running standalone on port <port>
    [RimBridge] Bridge token: <token>
```

`.local/qa/bridge.py` is the scratch client for this — `list`, `call <tool> '<json>'`, and
`scan <minx> <minz> <maxx> <maxz>` for a cell-by-cell rect survey. The shipped
`tools/qa/rimbridge_readonly.py` keeps its five-tool allowlist and its fail-closed PID/log
pairing; the scratch client is for diagnosis, not for evidence.

The reads that earned their keep: `rimworld/get_cell_info` (what is actually in a cell — terrain,
roof, every thing, its class and hit points), `rimworld/list_colonists`, `rimworld/list_letters`,
`rimworld/get_game_info`, `rimworld/get_ui_layout` and `rimworld/take_screenshot` with
`clipTargetId`, `rimworld/list_selected_gizmos`.

**Only the owner launches. The bridge is read-only against a process they started, and they close
it themselves.** `kill` the game only when the owner says so — they did, verbatim: *"and when ur
ready to redo rimsort kill rimworld .exe and build the mod correctly in local with other mods and
then ill start rimsort"*.

### What the fourth launch found

**Two defects, both consequences of 0.12.46-dev correctly handing map generation back to Core** —
which was the right fix and had a bill nobody paid until a real launch.

The owner diagnosed it themselves before any code was read: *"i think the issue was there was shit
where it planned on putting the store and pawns so it errored it needs a like a burn into place
functiions to carve everyhting out and cut everything down and fill in with soil where water is
unmder where the store needs to propigate before game start"*.

**Measured in the live game.** `Player.log` named the throw at `(133, 0, 135)`; the bridge found a
**Granite Mineable with 900 hit points** there; a sweep of all **1020** footprint cells found
**164 Marble and 70 Granite formations, 177 cells of natural rock roof, ~440 plant cells, 34 cells
of rubble and chunks, and two monkeys**. `list_colonists` returned **0**. **234 of 1020 cells held
natural rock** — the facility had no chance and threw on its very first cell.

| | What went wrong | The fix |
|---|---|---|
| 9 | `Build` **refused** ground Core generated instead of preparing it | prevention **plus** the burn — see below |
| 10 | the arrival step **threw out of Core's `GenStep_ScenParts`**, so Core's whole scenario step died: **no colonists, no supplies** | fall back to `base.GenerateIntoMap` and never throw |

**Defect 10 is the important one to carry forward.** `MapGenerator.GenerateContentsIntoMap`
abandons a gen step at its first exception. **Anything this mod does inside a Core gen step must
not throw**, or the player loses everything else that step was going to do for them.

**The fix for defect 9 has two halves, and the first is why the map still looks like a map.**
`GenStep_RocksFromGrid` spawns a formation wherever `MapGenerator.Elevation` exceeds **0.7**, and
it runs at order 200; Core builds that grid at order 10. `RR_HeadquartersTerrain` moved from
**order 5 to order 100**, between them, and lowers site elevation to **0.55** — so the rock is
**never generated**, rather than carved out afterwards into a 234-cell crater. Then
`HeadquartersBuilder.BurnIntoPlace` runs **before a single wall** and carves, cuts, clears natural
roof and fills water with soil.

### Useful Core numbers, measured from the install this build targets

```
ElevationFertility   10      RocksFromGrid       200   (rock above elevation 0.7)
Terrain             210      Roads               390
MutatorCritical     500      MutatorNonCritical  700
ScatterRuinsSimple  750      ScatterShrines      750   (both respect UsedRects)
FindPlayerStartSpot 850      (only picks when PlayerStartSpot is invalid)
ScenParts           875      Plants              900
ScatterGeysers      950      RockChunks          970
Snow               1150      Animals            1200      Fog   1500
```

`RR_HeadquartersTerrain` is **100**, `RR_HeadquartersFacility` is **800**.
`RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**.



**The build is done. This is the play-testing phase**, on `feature/bug-testing`, and it has
already been worth more than any equivalent stretch of building: **three launches, eight defects,
every one ours.**

**The staged copy is current** — 0.12.46-dev, hash-verified against the build. Nothing to re-stage
unless the build moves.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

**Only the owner launches, through RimSort.** Standing instruction, unchanged.

### The pattern in all ten, because it is the same pattern

**Seven of the eight were this mod overriding or replacing something the player or the base game
already owned**, and the eighth was the mod inheriting global state it never set:

| # | What was overridden | What it produced |
|---|---|---|
| 1 | Unity's IMGUI draw state, never reset | a blank page with an empty log |
| 2 | the scroll view swallowed the confirm checkbox | Start refused and the reason was off screen |
| 3 | the same for the company name field | *"there is no box to type in"* |
| 4 | `GameInitData.mapSize` | a 50x50 map: *"a super micro blocked in area"* |
| 5 | `GameInitData.mapGeneratorDef` | *"bare dirt not even vegitation"* |
| 6 | the terrain grid, every cell | the tile's character erased |
| 7 | `SoloGroupOpening` gated on `insideStart` | the Store had no gate to enter |
| 8 | F12, measured against Core alone | collided with HugsLib's log publisher |
| 9 | the footprint, assumed empty because our own generator made it | refused 234 cells of Core's rock |
| 10 | Core's `GenStep_ScenParts`, aborted by our throw | **no colonists and no supplies at all** |

**The rule that falls out of it, and it is the thing to carry into the next launch: do not replace
what the player or the base game already owns. Add to it.** Every fix in 0.12.45 and 0.12.46 was
the same move — stop overriding, start contributing. The map generator patch is
`PatchOperationAdd` for exactly this reason.

### What the fifth launch settled, and the sixth-launch list that replaced this

- the Store stands on the owner's tile and map size, on **open ground with no rock crater**, and
  the rest of the tile keeps its biome character
- **colonists and starting supplies are present** — the thing that measured zero
- select a wall: **Deconstruct and Uninstall both offered** (`rimworld/list_selected_gizmos` will
  answer this without guessing), and Remove Floor works on the concrete
- deconstruct an interior wall and **no roof collapses**
- the back-room door nobody built, and the ways deeper or out to a world tile behind it
- the Operations tab on Backslash, with no HugsLib double-fire

### What the fourth launch settled, and the old list it replaces

- **the map is yours**: your chosen size, your chosen tile, and **what Map Preview showed you**.
  Rocks, plants, water, biome terrain all present; the facility centred with real ground round it.
- **a door in the Store's back room that nobody built** — permanently open, to a seeded
  coordinate, with an event announcing it.
- **through it**, and then onward: ways deeper, or out to a world tile, found by surveying
  doorways.
- **the Operations tab on Backslash**, and no double-fire with HugsLib.

**And the standing ask, which has paid for itself three times: if anything fails silently, that is
the bug.** The setup page names its own draw faults, gate refusals name themselves, crew refusals
name the person. Silence is the thing worth reporting.

---

## The re-stage command, for when the build does move

**The build is done.** Every queue row that can close without the game running is closed. There is
nothing left to build that does not first need somebody to press play.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

The staged copy in Local Mods is **0.12.26-dev** against a build of **0.12.42-dev** — **sixteen
checkpoints**. Staging backs up the existing folder, hash-verifies every file against the build
manifest, and records `ProfileChanged = false; GameLaunched = false`. **It never touches the mod
list and never starts the game.**

**Only the owner launches, through RimSort.** That is a standing instruction and nothing below
changes it.

### What a first launch settles, in order of what it unblocks

| Rows | What only a launch can answer |
|---|---|
| 810 | duplicate def and patch collisions in the exact 294 profile — a conflict has to be reproducible to fix |
| 890, 891 | exchange-rate and catalogue balance — *"neither has any play behind it"* |
| 212, 742 | performance and profiling under a long save |
| 812 | the user-facing compatibility report — *"cannot honestly state a tested order before anything has been tested"* |
| 975 | whether the creepy-versus-normal balance lands — *"a play question"* |
| 835, 849 | the invalid-state matrix half, and the release tag |

**Read `docs/PLAYING.md` first.** It is the play document written at 0.12.40-dev, and its opening
caveat is the whole frame for a first session: every instruction in it is a structural claim about
the code, because nobody has played this. **Where it and the game disagree, the game is right.**

**The most likely first-launch failures, in the order they would appear**, each already carrying a
named refusal rather than silence: the company failing to register headquarters (the Overview pane
offers to retry), a coordinate failing to generate (the Atlas pane offers to re-address), and a
colony control unavailable in the world view. Nine gate refusals and ten crew-planner refusals all
name themselves. **If something fails silently, that is the bug worth reporting** — this package
was built so that it should not be possible.

---

## What shipped this session, 0.7.1 → 0.12.42

| Version | What |
|---|---|
| 0.7.2–0.7.7 | **The economy** — odd origin, supply contracts, pressure, bonds, corporate trader, exchange |
| 0.7.8–0.8.1 | **The look and the ladder** — yellow rooms, archetypes, escalation, construction echo |
| 0.8.2–0.8.5 | **Inhabitants** — wanderers, survivors, anomalies, colonist echoes, fog-of-war holding |
| 0.8.6–0.8.8 | **Shape** — room echoes, hallways, coherence decay, the gate address book |
| 0.8.9 | **Bringing a gate up is work** — operator-driven spin-up with familiarity; gates are blue |
| 0.9.0 | **A gate is a door and nothing else** — 8 legacy defs retired, package 92 → 79 |
| 0.9.1 | **One kind of gate** — 68 dead branches collapsed, a vestigial power model gone, −112 lines |
| 0.9.2 | **A gate has a size** — 1×1 to 2×3; Core's own `OrnateDoor` gives 1×2 free |
| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's practice |
| 0.9.4 | **What a gate's size lets through** — animals cross; width decides what fits |
| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold |
| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |
| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs |
| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared |
| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement |
| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims in 10 living docs |
| 0.10.1 | **LAW #0, made checkable** — 10 owner directions found unrecorded |
| 0.10.2 | **One set of words** — gate / connection / threshold, enforced |
| 0.10.3 | **Something is not where you left it** — silent between-visit displacement |
| 0.10.4 | **The register checked backwards** — a LAW, a query tool, a real defect; plus a readable description |
| 0.10.5 | **Every surface the game speaks through** — a seventh checker measured against Core per display surface, and the alerts readout, which this mod used none of |
| 0.10.6 | **The documents use the mod's own words** — the vocabulary and the wall rule reach the reader-facing set; two superseded rules found while reading |
| 0.10.7 | **The survey tag becomes a glow pod** — marker types with colours, three caps removed, and an outcome that could never fire |
| 0.10.8 | **A gate's facility is the equipment linked into it** — shelves, analysers and cabinets link like furniture to a bed, but far, through walls and by hand |
| 0.10.9 | **What you have learned is what you can build** — projects require completed logs; the ladder had one rung and a declared top tier of four |
| 0.11.0 | **The only clock is the gate** — the campaign chart, two offer clocks retired, seven prep documents corrected, eighth checker |
| 0.11.1 | **An offer with more than one way through** — the request shape, routes as a first-class field, contact as a branch state |
| 0.11.2 | **The company asks for six things, then stops asking** — the tutorial line and the hinge; the two-kinds rule forced a better hinge |
| 0.11.3 | **Seven ways into the tree** — research tier 0 across seven branches, each granting a capability real code honours |
| 0.11.4 | **The second rung of every branch** — research tier 1; two vestigial power props found and retired |
| 0.11.5 | **A designated gate is a machine that is on** — three unused props restored, two wired. **Reversed 0.11.4’s retirements.** |
| 0.11.6 | **The second time you do a thing should be cheaper** — research tier 2; three planned unlocks deleted for changing nothing observable |
| 0.11.7 | **The corporation does not write off a branch** — the clean-up team; five `PawnKindDef`s found authored and read by nothing |
| 0.11.8 | **The storyteller finally knows this mod exists** — the first two `IncidentDef`s; no `StorytellerDef`, now asserted |
| 0.11.9 | **A shop with a door in the back** — the Store start; three new-game crashes caught by a new proof |
| 0.12.0 | **You are already in** — the solo/group start; the map itself is a coordinate. **All three starts ship.** |
| 0.12.1 | **The free doors run out** — found doors stop at depth 3; deeper needs a built gate. Corrects 0.12.0 |
| 0.12.2 | **The way out was already there** — the guaranteed exit; two maps, a real coordinate, `GenStep_InsideStart` retired |
| 0.12.3 | **A portal is its own door cell** — a wall beside a gate no longer bricks it; eighth proof |
| 0.12.4 | **Four answers** — supply requirement, deconstruct warning, solo hints; **a tier 0 unlock that did nothing**, found by a new general sweep |
| 0.12.5 | **The queue was in the wrong order** — tier 3 has no knobs to move; the chart authorises arcs 5–8 next. Four hollow unlocks not written |
| 0.12.6 | **A remote base is a costly responsibility** — arc 5 opens: sites on the books, billed daily, and a coordinate is never one |
| 0.12.7 | **Company-to-site logistics** — shipments reach a registered site; a latent cross-map reroute bug fixed before it could bite |
| 0.12.8 | **Remote sites need people** — a shipment to an empty site waits; the stranded-crew guarantee proved rather than rebuilt |
| 0.12.9 | **The exit plan** — a gate may stand at a registered site, with its own facility. Arc 5’s named list complete |
| 0.12.10 | **The handoff** — four live proofs found unrun, five patch scripts un-named as proofs, a stale hash corrected |
| 0.12.11 | **The corporation starts asking** — the mission line reaches a player. **The whole campaign had been authored and read by nothing** |
| 0.12.12 | **The company stops naming things** — generation after the hinge, a filter that can refuse, arc 4’s five families. Fixed 0.12.11’s absolute-state flaw |
| 0.12.13 | **Arcs 5 to 8 have work in them** — thirteen more families, one per item the chart names. **Chart §7 step 8 closed** |
| 0.12.14 | **The queue could not answer the question** — 155 backlog rows re-measured against the code; open rows 254 → 107. **No `FactionDef` exists at all** |
| 0.12.15 | **The universe has factions in it** — seven, all neutral, **no settlements and no new content**. Closes the largest unbuilt owner direction |
| 0.12.16 | **The menu takes any number of slides** — folder-scanned with a load-bearing name prefix, plus the art brief. Two integrity notes that were always wrong, fixed |
| 0.12.17 | **Four more menu slides** — six now cycle. A slide that would never have appeared is caught before it ships; provenance ships for the Steam disclosure |
| 0.12.18 | **The third rung of every branch** — research tier 3, **all seven**, every one moving an observable knob. Two design restraints asserted |
| 0.12.19 | **The yellow rooms were never carpeted** — a real shipped defect; three of my own audit verdicts corrected. **Twentieth proof** |
| 0.12.20 | **The register, by the column that matters** — `trace` querying, and a **ninth checker** verifying how this mod uses other mods |
| 0.12.21 | **A way out into the world** — the last unbuilt piece of the topology. Claim a tile under five maps, caravan over. **A dead end removed** |
| 0.12.22 | **The last new art is gone** — four custom textures replaced with paths enumerated from Core. **Zero gameplay art ships**, and it is checked |
| 0.12.23 | **The handoff, audited again** — six defects in it. A question I had parked in a document, asked and answered instead |
| 0.12.24 | **The recorder became the book** — the last authored gameplay item retired without a save break, a dead end closed, and the register made readable |
| 0.12.25 | **Two crew who disagree** — the prep material’s contradictory accounts. **The contradiction was already computed and discarded**, and a tutorial request was unreachable as the chart writes it |
| 0.12.26 | **The in-game text names only what exists** — fourteen strings instructed the player to use retired gear. **A tenth checker**, and an archive hole repaired so its derivation is complete |
| 0.12.27 | **You cannot brick your own gate** — the approach cell is reserved against blocking, flooring is free. **Owner-answered at the fork**, and the integrity checker taught to verify an abstract-parent patch |
| 0.12.28 | **Nobody is lying** — the interview files one account and keeps both. **The code made a lie detector impossible and the design better**: a disputing account was already validated against the map |
| 0.12.29 | **Six rungs, and two that could not exist** — research tier 4. **Logistics gets none and the gate line cannot have one**, and both absences are asserted rather than assumed |
| 0.12.30 | **You can call the company** — `EstablishCorporationContact` had no caller, so **two of three starts had no campaign at all**. Earned on a comms console, and it opens the line that already existed |
| 0.12.31 | **A wide gate out of plain doors** — 1×3 and 2×3 with no mods, as one gate of one width. **Three rows were one feature**, and the union of a run is the `CellRect` everything already read |
| 0.12.32 | **Everything is read by something** — the **eleventh checker**. 258 defs and 102 actions audited; one unwired capability given a surface, one duplicate retired |
| 0.12.33 | **Surgery cannot cross, and three things were invisible** — row 227 closed **by proof**, plus the door crossing order, the coordinate band readout and a sale confirmation |
| 0.12.34 | **Fifteen more reasons to walk through a gate** — the eleven DLC container givers and the four `Art` painting givers. **Core forbids all eleven from moving anything between maps**, so invariant 55 was never engaged; and a clamp was silently overwriting six shipped priorities |
| 0.12.35 | **Containment you can see from the other side of a gate** — **Core's four containment alerts all read `Find.CurrentMap`**, so the gap was never "no warning" but "no warning about the maps you are not looking at". Plus the security procedure and the alarm |
| 0.12.36 | **Roofs, snow, and reporting in** — **six rows in one batch.** The area rows closed themselves because somebody had written down *why* they were uncovered; quarantine turned out to be the debrief, because this package has no `HediffDefs` at all |
| 0.12.37 | **Every coordinate in the game was made of wood** — one hardcoded material for every stuffable fixture in every room. Plus the **twelfth checker**, which caught itself twice, and the stance classifier fixed to its own row's prediction |
| 0.12.38 | **A gate read no damage at all** — it could be shot to twelve per cent and still hold a connection. **Seven of row 725's nine subsystems were already built** under different names. Reliability is a record, not a dice roll |
| 0.12.39 | **The register said don't patch, so the hook is a sentence** — reading the integration approach first made the obvious build the wrong one. Five rows, a read-only readout, and **row 791's absolute got a checker**
| 0.12.40 | **The words a player reads** — five rows in one batch. **Architect, the first surface row 821 names, opened from nowhere in this package**, and the handoff said it was already reachable. The company tab was second from the right. `docs/PLAYING.md`, a help pane with the glossary, and Core's own generator supplying the keyboard binding for one XML field
| 0.12.41 | **The last two systems** — **every check row 728 asks for was already enforced and not one was named**: five conditions across three people, all reported as `RR_Exp_InvalidCrew`. And a mission is a contract **plus survey work at depth**, because the odd mark carries no coordinate and stacks merge, so nothing can verify *where* a good came from
| 0.12.42 | **The housekeeping, which was not housekeeping** — the compliance table had been *"re-run rather than trusted"* for **thirty-six checkpoints without being re-run**, and three of its rows had stopped being true. The register's last five families were all honoured, so **their rules became checks**. Row 1054 said the master backlog understated the build by thirty points; **it was 56**

---

## What is left, in order — maintained through 0.12.39-dev, measured not carried

**Re-measure this list before trusting it.** It has been correct at every checkpoint since 0.12.33-dev because each batch edited it, but the count at the top of the file is a command for a reason: the item numbers are renumbered on every close and a stale count is the most expensive thing this file can hold.

**1 numbered entry below, and it is a closed record.** Zero genuine build items. Counted rather than estimated: `sed -n '/^## What is left, in order/,/^### Cannot close/p' docs/NOW.md | grep -cE '^[0-9]+\. \*\*'`. Anything marked closed below stays as a record so nobody rebuilds it.

### Systems still unbuilt — NONE. This heading holds a closed record only

**Every gameplay system the queue asked for is built as of 0.12.41-dev.** The entry below stays so nobody rebuilds row 761.


1. **ROW 761 IS CLOSED** (0.12.35-dev and 0.12.36-dev). Containment rooms, the security
   procedure and the alarm shipped first; **staff debrief and quarantine closed it**, and they
   turned out to be one mechanism because this package has **no `HediffDefs` folder at all**, so
   quarantine is *"you do not go back out until you have reported in"* rather than anything
   medical. Two findings worth keeping: **Core already ships four containment alerts and every one
   reads `Find.CurrentMap`**, so the gap was never that containment has no warning but that it has
   none about the maps you are not looking at; and the debrief hold bites on **`Dispatch`, not on
   `PortalTraversalPolicy`**, because a player walking one colonist through a door by hand is not
   a company dispatch.
   **Also closed, 0.12.34-dev:** row 1266's eleven DLC container hauling givers as
   `machine-loading` — **Core forbids every one of them from moving anything between maps**, so
   invariant 55 was never engaged — and the four `Art` painting givers as `painting`.
### Cannot close before the game runs once — about 8 rows

Not evasion; it is what they are, in their own words:

- **exchange-rate and catalogue balance** — *"neither has any play behind it"* (rows 890, 891)
- **duplicate def and patch collisions in the exact 294 profile** — a conflict has to be
  reproducible to fix (row 810)
- **performance measurement and profiling** under a long save (rows 212, 742)
- **the user-facing compatibility report** — *"cannot honestly state a tested order before anything
  has been tested"* (row 812)
- **whether the creepy-versus-normal balance lands** — *"a play question"* (row 975)
- **the invalid-state matrix half** of row 835, and the release tag of row 849

### Excluded by the owner — 9 rows

*"lets not count the test items and the steam collection and mod workshop setup and stuff like
that"*. Rows 268–271, 275–278, 572: the site, the Workshop page, the collection, and the Playwright
idea. [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md) holds them, and **it is correctly last.**

---

### Done since the last handoff, so nobody rebuilds it

**Eight checkpoints, 0.12.34 → 0.12.41, twenty-seven rows closed in six batches.** Every one published
to all eight refs with a read-back, a deterministic assembly, and the full checker and proof sweep.

**The owner changed how to work, mid-run:** *"lets start doing shit correctly and efficiently and
keep going iin batches of items completed so we have less work constantly pushing"*. So related
rows are grouped into one checkpoint and published once. It works — 0.12.36-dev closed **six rows
in one publish**.

**NINE ROWS TURNED OUT ALREADY BUILT, ALREADY TRUE, OR ANSWERED BY CORE.** The table under *Is it
done?* lists all nine. Twice the row's own *"confirmed absent by grep"* was itself the defect: row
725 said stabilizers and modules were absent and **both existed under different names**
(`PortalWindowTier`, `GateEquipmentLinks`). **Check a row against the code before building for
it** — it is the highest-value habit in this file.

**Custody across a gate was never a problem, and Core says so.** All eleven DLC container hauling
givers were decompiled. Every one refuses to act unless the thing it moves is already on the
worker's own map — `WorkGiver_CarryToBuilding` returns false unless `selectedPawn.Map == pawn.Map`,
`TakeEntityToHoldingPlatform` unless `targetHolder.MapHeld == t.MapHeld`, and the rest search
`pawn.Map`. So **invariant 55 was never engaged**, the family is the ordinary deployment shape, and
twenty-seven checkpoints of caution were spent on a question Core had already closed.

**A clamp was silently overwriting the mod's own shipped numbers on every game load.** `Effective`
clamped every value against one `MaximumPriority = 130` **including the shipped default**, and
`Apply` writes that into the defs at `FinalizeInit`. Six authored priorities were being replaced
before a pawn ever ran — worst, the far-side operating family authored at **502** to sit one above
Core's `Flick`, landing on **130**, below every local giver. **That is the exact failure the
two-giver split exists to prevent, inside the code that exists to prevent it.** The ceiling is now
per giver.

**Core's four containment alerts all read `Find.CurrentMap`.** Enumerating Core's own alert classes
before writing any found `Alert_InsufficientContainmentStrength`, `Alert_DangerousActivity`,
`Alert_EntityNeedsTend` and `Alert_NeedHoldingPlatform` — so shipping ours would have been a second
opinion beside a rule the player already sees. **The real gap is that Core's warnings are about the
map on screen**, and this mod's premise is several live maps at once. The two new alerts skip
`Find.CurrentMap` entirely, so the sets can never overlap.

**Quarantine could not be medical, and that is a measurement.** This package has **no `HediffDefs`
folder at all**, so there is nothing of ours to clear and inventing one is forbidden content.
Quarantine is therefore *you do not go back out until you have reported in* — which makes it and
the staff debrief **one mechanism**. The hold bites on `Dispatch`, deliberately **not** on
`PortalTraversalPolicy`, because a player walking one colonist through a door by hand is not a
company dispatch.

**Every stuffable fixture on every coordinate in the game was wooden.** Not the def's default —
`ThingDefOf.WoodLog`, hardcoded. A coordinate now takes a three-entry palette from its own seed,
and **the load-bearing line is a sort by defName**: the def database returns defs in an order that
depends on the installed mod list, so indexing it unsorted would give two players on one seed
different materials and change a coordinate when an unrelated mod is installed.

**A gate read no damage at all.** It could be shot to twelve per cent, set on fire and hit by a
mortar and still hold a connection perfectly. **The machine the entire mod is built around was the
one building in the colony that damage did not affect.** Below half condition it now loses
calibration — a state that already had a work giver, a refusal and a readout — so the fix adds no
mechanic.

**The register said don't patch, and reading it first is the only reason the last batch is right.**
*"No patch or code/assets copied"* for both gravship chapters; *"do not add vehicles solely because
the framework is installed"* for the vehicle framework. So the hook is a **read-only statement** of
what is installed and what this package does about it — which is what the rows asked for in their
own words. The defence that cannot rot is asserted: **only two files mention the detection class,
and no tracked package id appears in any other source file.**

**Every check row 728 asks for was already enforced, and not one of them was named.** `Dispatch`
refuses on fifteen distinct grounds and `CheckCrew` collapses **five** of them — wrong crew size, a
duplicate, cannot walk, not employed, and by extension dead, downed, mid-mental-break or incapable
of moving — into the single key `RR_Exp_InvalidCrew`. **One message for five conditions across
three people, naming neither the person nor the condition.** So the planner is not a second set of
checks, it is the same conditions attributed: ten named reasons, each reading the state dispatch
itself reads. Skill was the one thing genuinely absent. **The row's absolute — *"must not own
connection existence"* — is asserted structurally:** the proof enumerates every C# file and
refuses a reference to the planner from outside `UI/`, so deleting it would change no outcome.

**A mission is a contract plus survey work at depth, because that is all the code can verify.**
*"Bring back odd goods from coordinate AI-04"* cannot be built: `ThingOrigin` has three values and
**carries no coordinate at all**, and odd stacks merge, so nothing can ever check *where* a good
came from. The field condition is checked against recorded survey state instead — which cannot be
faked by hauling, and which is what makes the mission pay for **advance and explore** where the
contract only ever paid for **haul**. One settlement path, plus one call; a record with no
condition reports it met, so every existing save behaves exactly as it did.

**The Contracts pane was not silent about odd demands, it was wrong about them.** It printed the
*survey* contract's terms on every contract, so a demand for two hundred odd cotton displayed
*"Survey the route, record the distortion, recover the record book and analyse it at
headquarters."* **A confident wrong answer is worse than silence** — silence sends a player
looking, this stopped them. Three demand fields were saved, given public accessors and read by
nothing but the settlement code.

**The plant harness caught a syntax error in its own proof and refused to plant anything.** That is
the 0.12.39-dev failure reproduced one checkpoint later and caught by construction. The sweep then
found **39 of 47**, and **six of the eight misses were the same defect as the previous batch**: a
claim testing a mention rather than a use. The lesson, stated once because it has now cost two
batches — **a name is a substring of its own declaration, of any renaming of it, and of every
symbol that starts with it.** `RR_Plan_Reserve` is a prefix of `RR_Plan_ReserveShort`;
`IsOddConsignment` is a prefix of `IsOddConsignmentUnused`; `return -1f;` appears three times in
one method. A claim worth making is a claim about a **call**, and if a call happens twice the claim
is about **how many times**.

**The first surface row 821 names opened from nowhere at all.** Not from the company panel, not
from any pane, not from anywhere in 191 files: `grep -rn "Architect" --include=*.cs src` returned
**nothing**. And this file said it was already reachable, which makes it the worst kind of stale
measurement — the one a fresh session would trust instead of checking. Architect is the surface
every building action in RimWorld goes through. All five surfaces the row names now open from the
panel, each through the game's own `MainButtonDef.Worker.InterfaceTryActivate()`.

**A tab called company-first was second from the right.** Core's orders are Architect 1 through
Factions 90 and Menu 500; Operations shipped at **95**, between the last two. It is order 0 now,
left of Architect. One field, and **the invasive reading of "remap" stays unbuilt on purpose** —
rewriting Core's own tab bar would fight every interface mod in the register at once, and
reachability was what the row actually required. The absence is asserted rather than assumed,
including against the def-database route a Harmony-free mod still has.

**The whole keyboard requirement was one XML field, and Core writes the rest.**
`KeyBindingDefGenerator.ImpliedKeyBindingDefs` emits a rebindable `MainTab_<defName>` into the
`MainTabs` category for any `MainButtonDef` that sets `defaultHotKey`. So the binding appears in the
player's own Key Bindings dialog and **this package authors no `KeyBindingDef` at all**. The default
is **F12, the only function key Core leaves free** — it takes Tab and F1–F9 for main tabs,
F10 for a screenshot and F11 for screenshot mode.

**Contrast and scale were already right, with nothing holding them right.** Not one file under
`UI/` authored a colour, and the only font work in the folder is one `GameFont.Medium` heading with
the caller's font restored. So the position is that this package authors **neither colour nor font
size in anything a player reads text from**, and the player's own Options for scale, font and
colourblind mode apply exactly as they do to the base game. **An option of ours would have been a
second, worse copy of a setting the game already has.** That is now a checker rule, because it was
true by accident.

**The plant harness verifies its targets before it plants anything**, and the first sweep of this
batch justified it: **33 of 42, and all nine misses were real.** Two were gaps in the new checker
— `new UnityEngine.Color(...)` walked past a pattern matching `new Color(`, and `(GameFont)7`
walked past an exemption meant for the `previousFont` restore. Four were claims that tested a
**mention** rather than a **use**: `def check_readability(` satisfies a probe for
`check_readability(problems)`, and `AUTHORED_COLOUR` matches `AUTHORED_COLOUR_UNUSED`. One was a
detector that depended on a variable being named conveniently. Two were weak plants — and one
of those found a writing fault, because the document stated the same key in two places.

---

**Two new checkers, taking it to twelve.** The def-field checker (row 922) **caught itself twice**
before it was right, both times in the same function — first reporting nothing, then reporting 159
false positives, because the field parser rejected any line containing `(` and every collection
field has one in its initialiser. And the row 791 claim guard, which **found a real denial in
`SCENARIOS.md` on its first run**.

---

## Invariants — do not break these

Each is a real defect or a pinned fact. Numbering is historical; gaps are deliberate.

### The gate and crossing

1. **`PortalTraversalPolicy` is the only traversal chokepoint.** An inhabitant may never decide anything about a gate.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map`.
3. **Remote forbidden checks use the *faction* overload.**
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.**
6. **Two work givers per family** — high-priority continue, low-priority plan.
7. **Never infer "no local work" from a priority number.**
8. **One commitment per worker**, across every record kind.
9. **Nothing is ever `playerForced`. No quantity is hardcoded.**
10. **No new gameplay ThingDef, PawnKindDef, art or audio.** Match by *capability*. A `FactionDef`, `ThoughtDef` or mechanics def is permitted.
11. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere.
12. **Natural gates have no timer, operator, power, close command or address book, and may not dial.** Enforced by `IsDesignated`, not a second check.
13. **A Backrooms coordinate has no outside**; its roof is never removable; its interior is fully strippable.
14. **A candidate half must ask whether the *target* can take the work.**
15. **A def referencing DLC carries `MayRequire`.**
17. **A prisoner can never cross a gate; a *secure* slave can.**
18. **The topology is an unbounded alternation** of world maps and coordinates.
32. **There is exactly one way a laboratory gate opens** — through the spin-up. Every entry point routes into it.
40. **A gate's width and its footprint are different numbers.** Width decides what fits; footprint decides what it costs.
41. **Throughput is never capped.** A wide gate gets more doorway cells, never a quota. There is no counter, deliberately.
43. **Core ships `OrnateDoor` at 2×1** and `Building_MultiTileDoor` to drive it; Anomaly adds `SecurityDoor`.
47. **A connection has one width, in both directions.** Per-endpoint measuring traps an animal in the Backrooms.
48. **Company work and player orders are two different rules.** `TravellerFailureKey` is colonists-only; `OrderedCrossingFailureKey` admits player animals. **Both refuse a drafted pawn.**
53. **Incursion is the one named exception to the founding rule**, bounded on five axes: live opening, `Band.Hostile`, `PortalWindowTier >= 1`, it must fit, once per opening.
54. **`MayApproachThresholdForTraversal` must stay false for everything, forever.** Incursion works *because* nothing is drawn to a gate.
55. **A transfer that can lose a pawn is a corruption, not a threat.** Preflight fully, then move, and restore on failure.

### Generation and threats

16. **The register is generated output; the HTML one is the register.**
25. **Depth 1 is sacred.** The yellow rooms are fixed, sparse, never deranged. Higher number = deeper (owner-confirmed).
26. **Sort any candidate list ordinally before rolling.** A live trap three times.
27. **Anything saved that feeds the layout fingerprint must be snapshotted, not read live.**
28. **Every threat honours: readable warning, learnable rule, a countermeasure, no unavoidable instant failure.** The threshold room is excluded from every event and inhabitant.
29. **Undiscovered inhabitants are held.** Discovery starts their clock.
50. **`Band.Hostile` is the "deeper levels" threshold** — *"the space stops being forgiving"*. Do not invent a second number.
51. **Below `Band.Hostile` a hostile holds ground; at it, it hunts.**
52. **`LordJob_AssaultColony`'s first parameter is the ASSAULTER's faction.** Passing the player's compiles cleanly and no checker catches it.
57. **A facility is a contiguous run of 2–4 rooms sharing one archetype**, anchored at the lowest index and **stored nowhere**.
58. **Coherence is what wrongness needs.** Do not "fix" facilities by making deep coordinates tidier.
74. **A horror mechanic that fires every time is a mechanic, not horror.** Revisit displacement was weakened from 100% to 66.7% deliberately.
75. **Ownership is the test for "did the player make this".** Generation places with no faction.

### Method

19. **Never trust a remembered list against shipped game data. Enumerate.**
20. **Owner words have been mod names twice.** Search the register before reading a phrase as flavour.
21. **A D-numbered Gate 0 decision can change.** D1 changed 2026-09-29.
22. **The no-tests rule has exactly one exception** (decision 20), in `CONTRIBUTING.md`. Never widen it.
23. **Do not trust a progress percentage from a row count here.**
24. **Nothing is deferred.** Build it, queue it in `TODO.md`, or ask. **Never add a row to `DEFERRED.md`.**
31. **When an existing guarantee already covers a new requirement, say so and rely on it.**
33. **Never tie a penalty rate to a flat constant without proving it against the real stat range.** Express it as a fraction of the observed rate.
34. **Ask at the fork; never flag it for later.** *"dopnt flag shit!!! ask me then and there"*. A flagged question becomes orphaned work.
35. **`ThingComp.ForceColor()` is the tint hook**; a painted colour wins over it. `Notify_ColorChanged()` drops Core's cached graphic.
36. **A checker that reads only one kind of source has a blind side.** Ask both directions, of every source.
37. **Retired content is archived, never deleted** — `docs/implementation/historical-content/<version>/`.
38. **To remove a pervasive flag, delete it and let the compiler enumerate the sites.**
39. **A def field and the XML that sets it are removed in the same change, always.**
42. **A patch target inside `PatchOperationFindMod` is optional by construction**, and only there.
44. **"Like the game does" is measurable. Measure it.** Core describes 0 of 105 work givers and 80 of 80 recipes.
45. **A description nothing renders is text in a file.** Write it and show it in the same checkpoint.
46. **Escapes written through a shell can collapse one level too far and leave an invisible byte.**
49. **Before designing a rule, check it can fire.**
56. **When a founding comment stops describing the code, rewrite it in the same commit.**
59. **When a proof and the code disagree on a constant, change the proof.**
60. **A scenario declares what begins finished, never the tech tree.**
61. **A project that begins finished is also insight-committed.**
66. **Living documents and dated records are different things.** Dated records are **never** rewritten.
67. **A checker that cries wolf is worse than no checker.** Precision before coverage.
68. **The vocabulary is gate / connection / threshold.** Never "portal", "machine gate", "the machine", "doorway" or "gizmo" in player-facing text. **Key names are exempt.**
69. **Every owner direction quoted in `FINALIZED.md` must already exist in `TODO.md`.** A build failure. It found **ten**.
70. **When the owner suspects a process failure, measure it — do not argue.**
72. **A retired def's name outlives the def in player-facing text.** Retiring a def means retiring its vocabulary.
73. **Check a prep document against the build every checkpoint.**
76. **LAW: check the mod register before building.** Filter by system family, read the per-mod review, and **state in the record what was checked** — or that nothing applied. Retroactively too.
77. **The register's `Stance` column is not trustworthy alone.** Row 78 reads `Required`; its review reads `optional`. The review is the authority.
78. **The register HTML has TWO tables**; a naive parse yields 589 rows and silently halves every filter.
79. **Chromium blocks XSLT from `file://`** — a stylesheet on About.xml gives a **blank page**, not a styled one.
80. **RimWorld renders newlines, so a wall of text is a choice.** Fails past 420 chars with no break.
81. **Do not quote a banned string verbatim in a living document** — it trips the rule that bans it. Rephrase.
82. **RimWorld has a different convention per display surface, not one voice.** A float menu row ends with a full stop 7% of the time in Core; an explanatory tooltip does 93% of the time. Writing either in the other's register is the mistake.
83. **Measure a surface, never a file.** The first run of `check-display-style.py` reported seven faults that were not faults, every one from sampling `Letters.xml` or `GameplayCommands.xml` alone when the surface spans several files. The baselines were corrected, not the text.
84. **A census counts the zeroes.** *"to include all"* is only actionable if the report names the surfaces the mod uses **none** of. That is how the alerts readout was found unused. A zero is a question, not a failure.
85. **A count printed with no rule behind it says so.** The inspect pane is counted and not ruled on, because Core builds inspect lines from strings scattered across its keyed files and there is no clean population to measure. A stated limit is not a forgotten one.
86. **Cache an alert scan on the tick AND the game object.** Core calls `GetReport` on a rotating one-in-twenty-four schedule. Keying a cache on the tick alone hands a second save loaded at the same tick the first save's despawned components.
87. **Words quoted from somewhere else are never ours to rewrite.** The vocabulary rule excludes any double-quoted span. The A24 synopsis calls it a doorway; changing that would be misquoting a source, not tidying a vocabulary.
88. **A document that describes the CODE keeps the code's identifiers.** The vocabulary rule covers the eleven reader-facing documents only. Rewriting prose around `PortalCrossingService` would make the documents disagree with the source, which is worse than an old word.
89. **Measure paragraphs, not source lines.** A hard-wrapped document hides a wall behind short lines; a one-line-per-paragraph document reports the paragraph. Threshold 700, grounded in the documents already rewritten for readability, which top out at 542.
90. **A readability rule makes somebody read the paragraph, and reading it finds the lie.** Two superseded rules were found this way, neither of which anybody was looking for: gate and portal as one word, and nothing-ever-crosses-on-its-own after incursion was added.
91. **Retiring a def means retiring every rule only it could satisfy.** A distortion counter tested for a beacon retired three checkpoints earlier, so the outcome was unreachable and no checker could see it.
92. **A Building is moved by despawning and respawning, never by writing `Position`.** Its cells are registered in the map's thing grid at spawn.
93. **Core's `ScenPart_StartingThing_Defined` minifies its own output**, and `MinifyUtility.TryMakeMinified` passes a non-minifiable thing through unchanged. An uncrated building in a cargo hold is a thing nobody can pick up.
94. **`CompLifespan.age` is a public field.** A Core glow pod dies after 1,200,000 ticks; holding a designated one at zero leaves every other glow pod in the game alone.
95. **Count the caps, not the cap.** *"lets not limit the amount"* named one limit and there were three: per room, per crew at dispatch, and per recipe batch.
96. **Core keeps facility-link geometry on the FACILITY side.** `CompProperties_Facility` is `maxDistance = 8f`, `requiresLOS = true`; the consumer comp carries one field and no control over either. Long-range, wall-transparent links must be our own record, or vanilla research linking changes for everyone.
97. **A def name that reads correctly can still be wrong, and nothing will tell you.** `Multianalyzer` is a ResearchProjectDef; the building is `MultiAnalyzer`. RimWorld's XML loader validates neither, so the wrong one loads clean and matches nothing. **Enumerate the installed data.**
98. **A rule and its exemption must both be provably non-empty.** The same-power-net rule applies only to things with a power comp. If every candidate were powered the exemption would be dead code; if none were, the rule would be. Assert both halves.
99. **State what already works before building it again.** Six of the nine items in this direction were already satisfied by rules written for the original three providers.
100. **A ladder must be at least as long as the tier it declares.** `portalWindowTierProjects` held one rung while `portalIndefiniteTier` was 4, so the top of the gate's own capability ladder was unreachable for the whole life of the mod. **Every individual value was valid**; the fault existed only in the relationship between two settings in different files. Covered by `proof-tier-ladder.py`, which reads the ladder from the source and the rungs from the defs.
101. **Fungible currency cannot express what a branch has learned.** Insight bought the same thing whatever produced it. Completed logs are the qualification and insight is only the price; a spent currency is gone and a completed log is not.
102. **Check a qualification before charging for it.** `ProjectQualificationFailureKey` runs ahead of the insight deduction, so a branch short of logs is told which kind.
103. **Custody is a place, not a receipt.** The retired check asked whether an evidence case existed somewhere at headquarters and never asked where the book was. A rule that can be satisfied without the thing it is about being anywhere in particular is not a rule.
104. **A prerequisite chain needs a cycle check, transitively.** A cycle is unreachable content in which every individual def looks completely normal.
105. **ARCHIVE BEFORE REMOVING. Always.** A removal was made by deleting a tuned def field, a const and a keyed string outright, with no `historical-content/` archive. The owner stopped it: *"how tf do you know we didnt need that shit coded up correctly and wasnt unfinished work"*. **The conclusion was right and the method was wrong**, which is the worse failure because it looks like progress.
106. **ASK AT A FORK EVEN WHEN THE READING SEEMS OBVIOUS.** Whether *"offeres and trades"* covered a hiring applicant and a purchase quote was a real fork with two readings. It was guessed, not asked, and finished code was deleted on the strength of the guess.
107. **The only clock is the gate.** No mission, quest, offer, contract or trade ever expires. A delay, a cooldown and a timestamp are all fine; a deadline is not. Enforced by `check-campaign-absolutes.py`.
108. **Every offer carries two or more routes to success**, of at least two different kinds. Enforced before the content exists, so the first offer ever written has to satisfy it.
109. **A clock that bounds nothing is pure pressure.** Both retired offer clocks sat beside a count cap that already bounded the pool. Check what actually bounds a list before believing a timer is load-bearing.
110. **Never widen a rule so that existing text passes.** `banned` and `superseded` were briefly added to the deadline-negation list and taken straight back out; they would have masked a real promise sitting near either word.
111. **Contact is a state on the branch, not a property of a scenario.** `corporationContact` is saved per branch; `beginsInCorporationContact` decides where a start opens. Async Industries begins true, the other two false. **One-way — there is no method to revoke it.**
112. **Our research layers on the shared RimWorld tech tree and never forks it.** Owner: *"the samw universial rimworld tech tree of all our mods in the collection on top of our mod"*.
113. **The authored route floor is assembled BEFORE capability is consulted.** If deriving returns nothing, a request must still offer two ways through. The safety property is the ordering, not the count.
114. **Two routes of the same kind is one route written twice.** A request needs two routes of two DIFFERENT kinds, or the rule is satisfied by text rather than design.
115. **Enforce by absence where you can.** `RimroomsRequestDef` has no deadline field, so one cannot be configured on. Stronger than any check that a value is unset.
116. **Enforce an absolute in two places.** `ConfigErrors` catches a def arriving from a patch or another mod after shipping; a checker catches one in this repository before it ships.
117. **When a rule bites your own design, redesign — do not carve out an exception.** The hinge as charted would have had every route of one kind. The carve-out was tempting and would have been the same failure as widening a negation list. The redesign is better than what it replaced.
118. **A `ThingDef` does not have to live in a file named `ThingDefs*`.** `TextBook` is in `Core/Defs/Books/BookDefs.xml`. A proof that indexes by filename reports correct content as broken, and the obvious response is to "fix" something that works.
119. **An unknown enum-ish string fails silently.** `CompletedLogCount` returns 0 for a log kind it does not recognise, so a typo produces a route that can never be satisfied and never complains. Assert the vocabulary.
120. **The chart is living and must be corrected when it is wrong.** Four corrections this checkpoint, including one where the chart contradicted an owner answer given after it was written.
121. **One generic mechanism beats N typed effect fields.** A `public bool unlocksSomething` tells you nothing about whether anything reads it. Capabilities are strings, and `proof-research-branches.py` asserts **both directions**: a grant with no read is a lie on the card, a read with no grant is dead code.
122. **An unlock nothing honours is worse than no unlock.** The def loads, the project completes, the card reads correctly, and nothing happens. Invisible without a proof.
123. **A plant that produces TWO failures means the proof checks both ends.** Renaming one side of a grant-and-read pair should fail as an orphaned grant AND an orphaned read.
124. **Do not add a hollow entry so a count looks complete.** Transport has no tier 0 project because it is DLC-optional; inventing one to make it eight would be the exact lie the proof exists to catch.
125. **A capability is neither a def nor a keyed string.** `check-package-integrity.py` and `check-keyed-strings.py` both had to be taught that, and both defer to the proof, which catches what neither can see.
126. **A dead PROP is more dangerous than dead code.** It reads exactly like a live one: a plausible name, a sensible default, a validation rule implying somebody cared. `reserveChargePowerWatts` and `returnReserveCapacityWattDays` were declared, validated and read by nothing since 0.9.1-dev.
127. **A property and a field differing only in casing is a trap.** `ReturnReserveCapacityWattDays` read the battery; `returnReserveCapacityWattDays` read nothing. Same class, one character apart.
128. **A validation can guarantee nothing and still look like a guarantee.** The retired clause compared costs against a nominal capacity unrelated to the battery a player binds.
129. **A deeper tier SUPERSEDES rather than stacks.** Read sites check the deeper capability first and fall through, so a card that says "twice as long" means twice.
130. **When a new assertion fails, ask whether the assertion is wrong first.** The depth rule failed on the gate ladder, which is linear by design. The assertion was restated; the ladder was not widened to satisfy it.
131. **UNUSED IS NOT UNWANTED. Wire it, do not retire it.** Owner, verbatim: *"make sure shit isnt unused it was put there for a reason"*. **A value nobody wired is a job nobody finished.** Three gate props were retired across 0.11.4 and 0.11.5 and all three were restored; two are now wired. This is the **second** correction of this shape — see 105, about deleting tuned values.
132. **Sweep the class, do not grep for one name.** The first two dead props were found by stumbling. A sweep of all seventeen gate props found the third **and cleared one an earlier grep had wrongly called dead**, because that grep excluded every line containing `public ` and threw away the property wrapper reading it.
133. **A cost must not become a trap.** Idle draw stops above the emergency-return reserve. A flat battery is a cost a player can see; a crew that cannot be recovered is not, and nothing would have warned them.
134. **When two readings of a value are both defensible, ask.** `reserveChargePowerWatts` is restored and deliberately **not** wired: the reserve is a Core battery RimWorld already charges, so the phrase either duplicates Core or means something else. Guessing would invent a mechanic.
135. **A reversed dated record is annotated, never rewritten.** The 0.11.4 archive opens with a note that the decision was reversed and its body is untouched.
136. **A live read site is not a live effect.** Three tier 2 unlocks were deleted before being written because the knobs they moved were a one-second wait, a cap of 100 orders and a quantity limit already set to a million. **All three would have passed `proof-research-branches.py`**, because the capability would have been read by real code. Open the file, find the value, and ask what a player would observe.
137. **A number displayed and a number spent must come from one place.** Idle draw is read by the gate’s readout and by the tick that drains the reserve; research applied to one and not the other would make the readout lie, silently, because nothing compares them.
138. **Check that a new tier does not switch off the tier below it.** Forward Dispatch halves the dispatch delay, and the lead-time clamp had to be moved onto the effective value or Relays would have stopped biting for exactly the branches holding both.
139. **An orphaned def is more dangerous than a missing one.** Five `RR_*Staff` `PawnKindDef`s were authored, loaded and validated every run and read by **nothing**, and the queue called them *"unbuilt"*. Built and orphaned looks finished from every angle except the one nobody checks. **Third instance of invariant 131 this session.**
140. **A guarantee must not be an incident.** *"Facilities never die"* does not admit the two questions a storyteller asks — whether, and when. The floor is deterministic; the flavour is paced. Owner decision, verbatim: *"Both - guaranteed floor, storyteller flavour"*.
141. **Never ship a `StorytellerDef`.** It is an exclusive slot the player would have to give up Cassandra or Randy for, and it needs portrait art the no-new-art rule forbids. **There is no intelligence in one to borrow** — a `StorytellerComp` rolls a mean-time-between against wealth and population. The director is `IncidentWorker.CanFireNowSub`, which is ours without the slot. Asserted by `proof-incidents.py`.
142. **A proof must not punish an explanation.** The incursion claim failed on this mod’s own comment saying why incursion is excluded. Strip comments and ask about code — a rule that makes documenting a decision expensive teaches people to stop documenting decisions. **Second time this session an assertion was wrong and the code was right** (see 130).
143. **One table, two scales.** The relief crate and the courier crate are one corporation with one warehouse. Two tables drift the first time either is tuned, and the letter keeps promising the old one.
144. **A ledger patch must INSERT, never replace.** The 0.11.7 script’s helper consumed a `FINALIZED.md` section heading because its replacement text did not re-include the anchor. `FINALIZED.md` is append-only; every patch re-includes its anchor and the diff is checked for removed lines.
145. **An assertion written from what the code LOOKS like is a guess; one written from what the code THROWS on is a fact.** All three wrong assertions this session came from the first kind — the depth rule, the incursion word-search, and the wall rule that would have failed the headquarters that ships and works. See 130, 142.
146. **A start layout is a new-game crash nothing else can see.** `GenStep_Headquarters` throws on a wall collision, a door with no wall, or a bad rectangle, and the build and all eight checkers pass regardless. **Read building sizes from Core’s own `ThingDef`s** — a 2×2 generator on a 1×1 assumption put three crashes in a layout that built clean.
147. **A sealed room does not throw.** The map generates and part of it can never be entered, forever, silently. Flood-fill every start from its arrival cell.
148. **Exactly one start begins in corporation contact.** Async Industries. The other two earn it, and until they do there is no clean-up team and no courier. That absence is what makes those openings frightening, and it is asserted.
149. **Core already lets a scenario choose the starting map’s generator.** `Game.InitNewGame` reads `initData.mapGeneratorDef ?? settlement.MapGeneratorDef`, and `GameInitData.mapGeneratorDef` is a public field. **No Harmony is needed to open a game anywhere**, and this mod had already been assigning it from the start def.
150. **Share the half that carries the promises.** The coordinate shell — rock to every edge, `RoofRockThick` over every cell, rooms carved out — is one implementation used by both generators, because invariant 13 lives inside it. The furniture differs; the shell never may. Same reasoning as the anomaly effects at 0.11.8.
151. **A `workerClass` or `genStep Class` that does not resolve fails as ORDINARY BEHAVIOUR, not as a crash.** A missing genstep gives the player a normal colony while the description promises the Backrooms. Assert that every class named in XML exists in source.
152. **A claim that can fail for the wrong reason can also pass for the wrong reason.** The natural-depth ordering claim was a string-index search over a variable name; renaming the variable made it fail open. **Key an assertion off the thing that actually happens** — a refusal, a keyed string, a def name — never off an expression’s spelling. Fourth assertion corrected this session and the first of this kind (see 130, 142, 145).
153. **Cap the free doors, never the way home.** `MaximumNaturalDepth` is checked after the way-out attempt. Capping both directions makes the deepest natural band a trap, which invariant 28 forbids.
154. **Open-ended is a constraint on the content, not a mood.** Owner, verbatim: *"this is all open eneded they can play how they choose"*. A tutorial line offers and describes; it never requires an order, and a step already done by a player who got there first must read as done rather than skipped.
155. **A portal is its own door cell and reserves nothing.** No radius, no claimed cells, no protected zone. Owner, verbatim: *"in the real world you can mine and build and explore directly behind the gates with out actually effecting the gate"*. The only placement rules near a gate belong to **linked equipment**, which has a reach of its own. Enforced by `proof-portal-footprint.py`, including a banned-name check.
156. **A snapshot and a live check, in two different files, is a silent failure waiting.** The approach cell was frozen at registration and validated forever; a wall on it bricked a gate for the life of the save. **Both files read correctly alone.** When a value is snapshotted, ask what happens when the world moves under it.
157. **Find every read site before changing a shared value.** Re-deriving the approach cell live everywhere — the obvious fix — would have tripped the crossing receipt’s equality guard, which is what stops a transfer losing a pawn. The repair is skipped while a crossing is in flight because the read sites were enumerated first.
158. **Sweep the exposed surface, not the fields.** `MinimumPowerHeadroomWatts` applied a research capability and **was itself read by nothing**, so the tier 0 Facilities unlock promised a change and delivered none. `proof-live-effects.py` walks every public property that reads `GateProps` and found two more. **A live read site is not a live effect** (invariant 136); this is the sweep that catches it.
159. **A dead accessor and a dead value are different problems.** `EmergencyReturnCostWattDays` was live as a field and dead as a property: the number reached the code and never reached the player. The fix is to display it, not to wire it again.
160. **Never build a keyed string at runtime.** `"RR_Hint_" + id` cannot be verified in either direction, so a typo ships as a raw key on screen. `check-keyed-strings.py` refuses it and is right to.
161. **Gate an opening requirement at the opening, never in the tick.** `NativeBindingFailureKey` is read every tick; a supply check there would emergency-return a crew already across. A lapse blocks the **next** opening, never the current one.
162. **Acquisition is the game’s; recognition is ours.** RimWorld already settles a second tile and this mod’s topology already emerges a crew elsewhere. A remote site is **registered, never created** — `proof-remote-sites.py` bans `WorldObjectMaker.MakeWorldObject`, `GetOrGenerateMap`, `SettleInEmptyTileUtility` and `MapGenerator.GenerateMap` from that source. Inventing settling would be fighting Core for nothing and first to break on an update.
163. **A recurring cost must be a ratio of the branch’s own economy, never an absolute.** Async runs on $25,000 a day of overhead and the Store on $1,500. One number is a rounding error for one and ruinous for the other; a share of a number each start already tunes is correct for both for free.
164. **A coordinate is never a base.** It is reached through a gate, it is transient, and it is not the player’s to keep. A surcharge that counted coordinates computes zero and looks like progress.
165. **Extend the one predicate, do not thread a second one.** `OwnsMap` has 30 call sites across 16 files; its third clause is what makes work, gates and emergence anchors all reach a registered site at once. Check that **every** consequence is wanted before widening it.
166. **A bug that only exists once you add the feature is the hardest kind to find, because it is not there while you are looking.** The procurement redirect updated the receiving zone and never the receiving map — harmless with one legal map, a shipment lost for ever with two. **Read every WRITE to a record before changing what the record may hold.**
167. **Check what your claim survives before believing it.** The on-the-books claim counted a refusal string; a planted fault removed the guard, left the string, and the proof passed. **Key a claim off the thing that happens** — a guard expression, a refusal, an assignment — never off a token near it. Second instance in one day (see 152).
168. **Permitted is not reachable.** Widening procurement without widening the stockpile menu would have left site delivery legal and unofferable. Every widening needs its surface widened in the same checkpoint.
169. **A crew left on the far side is stranded, never taken.** Owner, verbatim: *"turning off a company gate with pawns inside doesnt lose control of those pawns they have to survive till a reconnection is made so they can escape"*. `ShouldRemoveMapNow` returns false **unconditionally** — any condition there is a condition under which somebody’s colonists vanish. No gate source may ever call `PassToWorld`. Asserted by `proof-stranded-crew.py`.
170. **A claim with a conditional fallback is a claim that can be trivially true.** The ordering claim keyed off a method name absent from the file and collapsed to a tautology. **Third fail-open in one day, all three found by fault-planting and none by reading** — which is what fault-planting is for (109, 152, 167).
171. **Gate a requirement where it bites, not where it is convenient.** Staffing is checked at a shipment’s **arrival**, never at its ordering: gating the order punishes planning, and gating nothing makes the rule a sentence in a document.
172. **A gate runs on the equipment beside it.** `thing.Map == parent.Map` is what makes a remote gate a real facility rather than a remote control for the headquarters. Widening *where* a gate may stand must never widen *what it may draw on*.
173. **Exclude by construction, not by a check somebody must remember.** A designated gate cannot appear in a coordinate because `OperatesAt` admits only registered places and a coordinate can never be registered. Invariant 12 then holds with nothing to forget.
174. **Two questions may share a place-set and must not share a name.** `OperatesAt` and `CanReceiveDeliveryAt` agree today and are different questions; one implementation stops them drifting, two names give the difference somewhere to go when it arrives.
175. **A def shape with content and no reader is not a feature.** `ConfigErrors`, a checker and a proof can all validate a def while nothing in the game consumes it — which is how the entire campaign shipped twice as content nobody could see. **Assert that a content surface is read from outside its own definition**, and restage the defect as a planted fault.
176. **Where two route kinds could resolve to the same expression, split them on what actually differs.** A def rule demanding two different kinds is satisfied by text alone if the runtime asks one question twice. Document is the paperwork and survives the witness dying; Testify is the person and survives the book burning.
177. **Re-measure every count in the handoff; never carry one forward.** The C# file count was wrong by two for five checkpoints, exactly as the assembly hash was. A plausible number is never checked by reading.
178. **Narrowing what a rule measures is legitimate; softening the rule is not.** A word search matching a comment is the wrong population (invariant 130). Strip the comments — then **plant a fault to prove the narrowing did not blind it.**
179. **Grep the ledger before asking the owner anything.** Two of the three questions in the 0.12.10 handoff had already been answered and recorded, and one of them was re-asked the turn after that handoff shipped. One `grep` across `.local/register/` and `docs/` is cheaper than the owner’s patience.
180. **Zero hard dependencies and Core-only are different claims.** The package must load and run against Core alone — a build property. The install it is *designed for* is the 294. Never write an option, doc line or design argument treating a vanilla install as the audience. *"wtf are you talking about core only we have 294 recommend mods you fuck!!!!"*
181. **Absolute state is permanently true once true.** A check like *"does the branch hold twenty meals"* is right for a request asked **once** and wrong for anything repeatable, where it pays out on acceptance. A repeatable job records where it started and asks for that much **more** — keyed by label key, never by list index.
182. **A route naming something that does not exist can never fire, and nothing says so.** A `logKind` typo makes the measurement zero while still counting toward the two-different-kinds rule, so every checker passes and the request ships promising two ways and having one. **Parse the content and assert each route names a real def.** Invariant 49.
183. **A filter clause that cannot refuse is a hollow knob.** Assert no arm of an eligibility switch is `return true`. Invariant 136 has already deleted four projects and three constants here for the same reason.
184. **A route against work already finished is satisfied on sight.** Exclude the completed case at the point of offering, not only at the point of measuring — otherwise the offer itself is a payout button.
185. **A proof failing because its subject MOVED is the proof working.** Retarget it and say so. A claim that survives an arbitrary refactor of the thing it describes is keyed off nothing.
186. **Count coverage per category, never in total.** Eighteen generated families is satisfied by eighteen copies of one arc. The claim that matters is that **each** arc has somewhere to put work, and only a per-arc count catches a family moving between them.
187. **Two documents can describe the same thing from two directions and nobody notices.** Arc 5’s *"still unwritten"* list — relay stations, caches, leases, resupply, evacuation — had had research projects since 0.11.6. **Before building a named item, grep the def names for its nouns.**
188. **A queue nobody re-measures cannot answer "how much is left".** 178 rows carried a status that was never re-checked; 114 of them were built. **Re-measure the queue against the code before answering any question about progress**, and append the evidence so the next reader can re-check rather than trust.
189. **Close a row with a named read site, or leave it open.** A flip on a guess is worse than a stale row, because it removes the thing from view. Anything unverifiable stays open.
190. **Say when a row cannot close without the owner.** Performance, balance, the 294 profile and the compatibility report all need a launch, and only the owner launches. Marking that is honesty, not deferral — and `DEFERRED.md` still gets no rows.
191. **A `FactionDef` is world configuration, and that is the whole of the permission.** It may reuse existing pawn kinds and existing icon paths and nothing else. **Enumerate the installed game for both** — a `factionIconPath` Core does not ship loads clean and fails at runtime, because `ContentFinder` returns null and the faction simply has no icon.
192. **`settlementGenerationWeight` 0 for anything this mod adds to the world.** Seven settlement-generating factions would change every world map every player generates, alongside 294 other mods. An interest group has people and intentions, not towns.
193. **Some correctness is achieved by NOT setting a field.** `FactionDef` has no starting-goodwill field, so *all neutral* is the default and the risk is a flag quietly appearing later. **Assert the absence**, because nothing looks wrong when it does.
194. **`ContentFinder` resolves across every loaded mod, so a folder scan is not ours.** `UI/Menu` is a generic content path; without a name prefix another mod’s art appears in our slideshow. **Scan the folder, then filter by prefix**, and say at the site that the prefix is load-bearing.
195. **A note nobody can act on is noise, and noise is how a real finding gets scrolled past.** Both menu textures were reported unreferenced on every run for months because the checker could not follow `Get(variable)`. **Teach the checker the API** rather than leaving a permanent false note.
196. **When a checker flags something legitimately new, fix it by its own design.** `check-keyed-strings.py` classifies by **call site, not spelling**, so a texture prefix counts as internal only when it is passed to `StartsWith` — and the narrowing was fault-planted to prove it still catches an undeclared key.
197. **A drop-in folder needs a proof that nothing dropped in can fail silently.** A slide named without the prefix is loaded by nothing and shown to nobody, and no build, checker or log says so. When content arrives from outside the code, **assert the naming contract** and plant a stray file to prove it fails.
198. **Validate delivered binary assets structurally, at build.** A truncated PNG fails when Unity reads it, long after the build reported success. Check the signature **and** that `IEND` is the final chunk. My first version of that check compared the last eight bytes literally and condemned every file, including ones already shipping — **the check was wrong, not the files.**
199. **Provenance for generated art is a release obligation, not a nicety.** Steam requires AI-content disclosure and menu images are the single exception to the no-new-art rule. `prompts-and-provenance.json` records tool and prompt per image, and a proof asserts it exists.
200. **A tier deleted for having no knobs is worth re-surveying once the systems land.** Tier 3 had nothing to move for four of seven branches at 0.12.5-dev and a real read site for **all seven** at 0.12.18-dev, because arc 5 wrote the systems in between. **Re-run the sweep; do not carry the old verdict.**
201. **A restraint is only a restraint if breaking it fails.** The per-coordinate frontier cap must never become a research knob, and shelter must never reach zero. Both are asserted and both were fault-planted — otherwise they are comments.
202. **Proximity is not the thing that happens.** A claim that looked for a capability name within 400 characters of a constant broke the moment a legitimate line was written above it. **Key off the assignment, the guard, the exit status — never off what sits nearby.** Fifth time.
203. **A grep for the words you expected, in the file you expected, is not a search.** The mineable-rock fill was marked *"confirmed unbuilt by grep"* while fully shipping, because the code says `Find.World.NaturalRockTypesIn` and contains none of the words searched for. **Condemning correct code on a failed search is worse than trusting a wrong comment.**
204. **`Named<X>("Foo")` on a TEMPLATE def returns null, silently, and a `??` fallback makes the wrong result look deliberate.** Core ships `Carpet` as a `TerrainTemplateDef` and generates `Carpet<Colour>`. The yellow rooms were wood plank flooring from the day they shipped. **Assert that every def a generator names actually resolves.**
205. **A filter that skips the case it guards against is worse than no check.** The floor claim excused terrains with no cost list as *"never built"*, which excused `PackedDirt` — the exact plant it existed to catch. **Only the planted fault found it; reading it would not have.**
206. **The mod register is GUIDANCE, not law.** Owner-corrected 2026-09-29: *"remmebr its not law but guidance"*. Consult it, let it shape the design, and say what it said — but a row does not veto work, and a checker built on it must only assert what is **structural**.
207. **Query the register by `trace`, not only by family.** The trace column names the **Rimrooms feature** a row bears on, which is the question the rule actually asks. It had no query until 0.12.20-dev, and that is precisely why it was the column that got skipped. **A column nobody can ask about is a column nobody consults.**
208. **A `PatchOperationFindMod` does not edit anybody’s files** — owner-confirmed. It patches the loaded def database at runtime and applies nothing when the mod is absent. What would breach *"WE ARE NOT EDITING OTHER PEOPLES MODS"* is **shipping their content here**, and that is what `check-register-compliance.py` asserts.
209. **A guarantee narrowed on a directory boundary is a guarantee evaded.** `proof-stranded-crew.py` watched `Gate/*.cs` only, so a `PassToWorld` shipped in `Portals/` would have passed on a technicality. **Say so, ask the owner, and assert the forbidden paths by name** — closing, expiry, traversal — rather than relying on where a file sits.
210. **The five-map cap is the stricter of ours and the player’s.** Ours is five, counting the coordinate they are standing in; the player’s is `Prefs.MaxNumberOfPlayerSettlements`. **A setting the player chose is never overruled by this mod.**
211. **Generate the destination before despawning anybody.** The claimed map exists before a pawn is touched, so a failure means nothing moved, and a failed spawn puts that pawn back. Invariant 55 in the one place it would have been easiest to get wrong.
212. **Let Core choose the world tile.** `TileFinder.TryFindNewSiteTile` already refuses water, space and impassable terrain and honours every mod that patches tile validity. **Seed the roll**, or the way out moves on every reload.
213. **Enumerate the replacement, never remember it.** `Data/Core/Defs` holds **908** distinct `texPath` values; every path used here was confirmed present in a real Core def first. This is the same discipline that `Named<TerrainDef>("Carpet")` skipped, and that one shipped a wrong floor for months.
214. **Check a rule as a SHAPE, not a count.** *"Remove the 14 historical PNGs"* was stale by ten. The durable assertion is *"every image this package ships is a menu slide"* — which needs no number and cannot go out of date.
215. **When a def is infrastructure, the art is the breach.** Three of the four legacy defs were mechanics or generator-placed markers that invariant 10 permits. Rebuilding working systems was never the fix. **Separate the def from its texture before deciding what to retire.**
216. **A decision nobody proved is a decision that does not ship.** The recorder became the book at
     **0.12.24-dev**; the answer was written down at **0.9.9-dev** and sat for fourteen checkpoints
     with every checker and every proof green. **No proof mentioned `RR_FieldRecorder` at all.** A
     recorded decision with no assertion behind it is indistinguishable from an idea.
217. **Retire a def by removing every way to GET one, not by deleting it.** Recipe, scenario grant,
     trade and catalogue — four routes, all closable — while the def stays loadable so saves open.
     The owner's rule is a *"migration decision or declared development-save break before removing
     any Def a saved Thing references"*, and **never granting one again satisfies it without needing
     either.** Saved field names stay too: renaming one is a save break for a cosmetic gain.
219. **When a replacement is Core content, read what Core DOES with it.** `TextBook` has
     `Flammability 1` and sells only as random outlander stock, so swapping our recorder for it
     would have made a burnt book refuse every future dispatch for ever. **That defect was in none
     of the row, the plan or the owner's answer** — only in the Core def.
220. **A LAW that points at a document its own tool cannot open is a LAW that gets skipped.** The
     register's `card` column printed the words *"open card"* — a hyperlink label — while Planned
     Use, Integration Approach and Compatibility Watch sat in the `#cards` section and 294 review
     records on disk. **Four short columns got read instead, and it counted as consulted.** Reach the
     guidance from the tool or the rule is decorative.
216. **A handoff that contains an open question is a handoff that deferred work.** `RR_FieldRecorder` was written into this document as *"needs an owner decision"*; the owner said **ask me, asap**. Invariant 34 already said so. **Ask in the turn you find it, then record the decision.**
217. **Measure the proof-output split, never carry it.** It said four `PASS:` and eleven `PROOF HELD` when there were twenty-one proofs, and **two of them announce nothing at all** — their last line is a wrapped continuation. Every phrasing-based runner misses those two, not just the wrong one.
218. **When your measurement and the document disagree, suspect the measurement first.** An invariant-count regex caught ordinary numbered lists and reported duplicates 1–9. The document was right: **209 invariants, no duplicates, gaps deliberate.**
221. **A refusal is a place where information goes to die.** `RR_Company_ReceiptMismatch` was
     *computing* the contradiction this campaign's prep material asks for, and then discarding it —
     and the only caller ignores results, so nothing anywhere saw it. **When a guard refuses
     something interesting, ask what it knew.**
222. **A new saved field must be threaded through every snapshot, copy and validity check that
     existed before it.** `EvidenceAnalysisReport` freezes observations and compares them back with
     `SameSnapshot`; a field those do not know about makes a frozen report agree with a record it no
     longer matches, **with no observable symptom until much later**. Fault-plant those two
     specifically — they cannot be found by reading.
223. **Do not let a reading of the queue substitute for reading the code.** The row said two crew
     who disagree was *"a short step from a mechanism that exists"*. It was not a step from
     anything: the mechanism existed and threw the answer away. **The row was optimistic in the
     wrong direction, which is rarer and worse than a stale row.**
224. **A string that resolves is not a string that is true.** `check-keyed-strings.py` verifies
     every key resolves and every used key exists; fourteen strings satisfied it while instructing
     the player to use a return beacon, a survey tag, an evidence case or a field recorder. **Text
     can be well-formed, translated, referenced and wrong.**
225. **A derived list is only as complete as what it derives from.** The retired-content check
     derives its names from the archive, and `RR_ReturnBeacon` had never been archived — so the
     check would have been quietly partial **and passed**. Repair the source before trusting the
     derivation.
226. **A rule that reads defs must know this mod's OWN def types.** My first retired-content check
     listed Core def types only, so it was blind to `RimroomsProjectDef`, `RimroomsRequestDef` and
     the procurement catalogue — most of what this mod authors. It would have passed with the defect
     in a live research project description.
227. **Retiring a thing leaves its WORDS behind, and they need a disposition.** Whether the concept
     survived the item cannot be derived: an emergency return is live while its cutoff is not; an
     analysis bench is live while the custom building is not. Record the decision **with its
     reason**, and make a new retirement fail until somebody makes it.
228. **Pick the mechanism whose SHAPE gives you the exception for free.** *"Option 2 but flooring is
     fine"* cost nothing to honour as a `PlaceWorker`, because a floor is a `TerrainDef` and terrain
     placement never consults one. The map-component version — my first instinct — would have
     needed the carve-out written by hand and then remembered.
229. **Derive a rule from Core's own predicate, never from a list of def names.** Blocking is
     `passability != Traversability.Standable`, straight out of `GenGrid.Standable`. A list would
     have been wrong for the 294 mods the moment one of them shipped a new wall.
230. **When a check runs on everything, doubt must allow.** A place worker fires on every placement
     check for every building in the game. A wrong refusal is a player who cannot build; a wrong
     allowance is a gate re-deriving a cell it already re-derives. **Catch the exception and
     accept.**
231. **A tool that cannot verify a technique is forbidding it.** `check-package-integrity.py`
     understood only `defName="X"`, so every patch on an abstract inheritance parent was refused as
     unverifiable — ruling out the one way to reach a property of every building at once. Teach the
     tool; do not route around it.
232. **Read the ORDER of the checks before designing on top of them.** I set out to build a lie
     detector; `validFact` runs *before* the prior-observation branch, so every disputing account
     had already been checked against the map and found true. **Nobody is lying** — the marker
     moved. The code did not merely constrain the design, it improved it, and only reading the
     sequence showed that.
233. **When two mechanics meet, one of them is already the explanation.** Between-visit displacement
     (0.10.3-dev) is *why* two honest crew accounts conflict. Nothing new had to be invented to
     justify the disagreement, and inventing a reliability statistic would have contradicted a
     mechanic that already shipped.
234. **Settle a dispute by recording the choice, never by rewriting the fact.** Both accounts stay,
     with both names. `Disputed` and `Settled` are two separate questions and a settled fact is
     still disputed. **An evidence chain that erases the testimony it declined is worth less than
     one that keeps both and says which.**
235. **A workflow that writes a saved decision must refuse once the record is frozen — AND be
     threaded through the snapshot anyway.** The refusal is the rule; the snapshot comparison is
     what catches the rule being wrong. Ship both, and fault-plant the second, because it has no
     symptom until much later.
236. **ASSERT AN ABSENCE, because an absence cannot be read.** Tier 4 has six projects and two
     branches deliberately without one. A reader sees six and cannot tell whether the other two
     were declined or forgotten. **The proof is the only thing that carries that difference
     forward** — and it also asserts *why*, so if a lower tier ever stops claiming Logistics' lead
     time, the proof fails and the decision gets revisited.
237. **Some absences are the shape of the thing, not a gap in the work.** The gate line's top rung
     is *"a connection that no longer counts down"*. There is nothing above indefinite. A fifth
     rung is impossible rather than unwritten, and writing one would have been the fifth invented
     effect this project has caught.
238. **A new system creates knobs for the tier above it.** Measurement had no fifth knob until the
     interview shipped one checkpoint earlier and gave it a Social floor to lower. **Sweep after
     building, not before** — which is exactly why the old verdict must not be carried.
239. **Four times this session my measurement was the defect, not the code.** The queue count, the
     assembly-hash grep, the keyed-string parser, and a grep that reported three hollow gate
     projects when the mechanism is a defName count. **Check before asserting a defect in working
     code** — invariant 203, and it keeps earning its place.
240. **A public method with no caller is a feature that does not exist.** `EstablishCorporationContact`
     was one-way, recorded its event, had its keyed string written — and was unreachable, which left
     **two of three starts with no campaign at all**. Grep for callers, not for definitions. The
     nine checkers and twenty-six proofs were all green over it.
241. **When two documents agree about something nobody built, they are not wrong — they are a
     specification.** The chart and `RR_Starts.xml` both said *"reaching contact is the
     achievement"*. Neither was stale. **The achievement had no mechanism**, and a hint was already
     pointing the player at a console with nothing to do with it.
242. **Follow the row into the code before scoping the work.** The row said *"the solo start has no
     tutorial line"*. The defect was that two starts had no campaign. **The row was accurate and
     far too small**, which is a different failure from a stale row and harder to see.
243. **An owner answer can delete work, not just direct it.** *"they can start async quest line"*
     meant no parallel line, no discriminator on the def, no second selector — the existing gate on
     `corporationContact` was already the whole mechanism. **Ask before building the bigger
     version.**
244. **Find the ONE value everything already derives from, and change that.** A gate's width, entry
     cells, cell count, power draw and spin-up work all come off a single `CellRect`. A run of 1×1
     doors **is** a rect, so returning the union made every one of those correct with nothing
     written for it. **Look for the existing seam before adding a parallel path.**
245. **Validate the WHOLE, not the part, when legality is a property of the whole.** Whether a door
     may join a run cannot be answered about that door: it is answered about the run it would
     make. So propose, check, and put it back on failure — and have the candidate search ask the
     same way rather than keeping a second copy of the rule to drift out of step.
246. **A legal-looking bounding box is not a shape.** A ring of doors around a gap passes every
     size test and is not an opening. **Assert the area equals the parts.**
247. **The checkers do not care that you know the rule.** Both defects at 0.12.31-dev were mine: a
     runtime-built keyed string for the fifth time in this project, and the banned word *"doorway"*
     five times — **a rule I had personally been corrected on hours earlier in the same session.**
     That is the entire argument for having them.
248. **A PUBLIC VERB WITH NO CALLER IS A FEATURE THAT DOES NOT EXIST**, and this project has been
     bitten by it four times: five PawnKinds, no `IncidentDef` at all, the entire request line, and
     `EstablishCorporationContact`. **All four passed every checker of their day**, because nothing
     was wrong with any individual file. `check-wiring.py` is the eleventh checker and exists for
     exactly this.
249. **"Wired" has three routes, not one.** By name in C#, by TYPE through `DefDatabase<T>` or
     RimWorld's own consumption, or by cross-reference from another def's XML. Checking only the
     first reported **106** false positives; only the first two reported **3**. **The real answer
     was zero** — twice the measurement was the defect.
250. **An unwired verb is either a missing surface or a duplicate path, and the two get opposite
     treatment.** `TriggerEmergencyCutoff` was a real capability nobody could reach, so it was
     wired. `RenameCompany` duplicated a live path with identical validation and an identical
     event, so it was retired. **Decide which before fixing either**, because wiring a duplicate
     doubles the drift instead of closing it.

---

## VERIFY THE PROOF PASSES BEFORE YOU PLANT ANYTHING

At 0.12.39-dev a fault-plant run reported **17 of 17 caught** and it was **worthless**. A fix to
the proof had introduced a syntax error, so the proof exited non-zero unconditionally and **every
plant registered as caught**. It looked like a clean sweep.

**A plant run against a broken proof proves nothing and looks perfect.** The first step of every
plant run is now:

```
python .local/register/proof-<name>.py >/dev/null 2>&1; echo "must be 0: $?"
```

and only then plant. The harness already re-reads every write to guard against a half-restore
(0.12.36-dev); this is the other half of the same lesson.

**And the same shape bit the doc scripts twice.** A patch script whose `sub()` throws part way
leaves the file untouched, so the edits *before* the throw are lost silently — six state edits at
0.12.38-dev, eight at 0.12.39-dev, both found only by grepping the file afterwards. **Assert every
anchor first, write once at the end, and grep the result.**

---

## The scope lesson from 0.12.38-dev, because it will happen again

**A proof that reads one file of a partial class does not know about the class.**
`proof-areas-and-debrief.py` enumerated *"every way a gate can stop working"* out of
`CompRimroomsGate.cs`, and **kept passing** when a seventh way was added in `GateIntegrity.cs` —
another file of the same `partial class`. The count was right and the scope was wrong, so a claim
that reads as *these are all of them* was really *these are the ones in this file*.

Anything asserting a **complete set** over a partial class must glob the class, not name a file.
Three of this project's largest types are partial across many files: `CompRimroomsGate`
(`Gate/*.cs`), `RimroomsCampaignComponent` (`Company/*.cs`) and `MainTabWindow_Operations`
(`UI/*.cs`). **Check every existing completeness claim against that list before trusting it.**

---

## THE REGISTER FOUND A LIVE DEFECT NOTHING IN OUR OWN CODE COULD HAVE

Owner instruction, 2026-09-30: *"make sure u are using prep and mod registry as needed"*. It paid
for itself in **one query**, and this is the strongest argument for the LAW that exists.

Register row **[188] Removable Mt.Rock Roof Patch** (Workshop `1541438898`) is **installed in this
profile** and patches:

```xml
<xpath>*/RoofDef[defName = "RoofRockThick"]/isThickRoof</xpath>
<value><isThickRoof>false</isThickRoof></value>
```

`RoofDef.VanishOnCollapse => !isThickRoof`. **So in this player's game Core's overhead mountain
vanishes on collapse and leaves open sky** — meaning invariant 13, *a Backrooms coordinate has no
outside*, **was already broken before any of this session's work**, and
`BackroomsContainment`'s claim that thick roof "never vanishes" was reasoning from unpatched Core.

The non-collapsing roof def added for the owner's *"backrooms can not and shall not have cave
ins"* direction repairs that breach as a side effect. And it is a second, independent reason
patching `RoofRockThick` would have been wrong: two mods editing one def at startup, load-order
dependent, and that mod asks to be loaded last.

**Also checked and clear:** [69] Craftable Mountains only *sets* `RoofDefOf.RoofRockThick` from
its own assembly; [63] Change map edge limit affects player map sizing and a coordinate is a fixed
size this mod creates; [128] MinifyEverything mutates `minifiedDef` on **defs, not instances**, so
every Core def the facility places is covered; [221] Stuff Mass Matters means a wider material set
changes hauling weight, which is native and correct.

## WHAT THE COLLABORATOR GETS

Owner direction: *"i need someone else to work on this in parrellel through git hub and i need to
make sure they have it all but the temp stuff i told you to git ignore"*.

**`.local/` was hiding the entire verification suite.** A clone could run the 13 checkers in
`tools/` and **none of the 41 proofs or 13 plant suites**. `.gitignore` now admits exactly two
globs and nothing else:

```
.local/*
!.local/register/
.local/register/*
!.local/register/proof-*.py
!.local/register/plant-*.py
```

Git will not descend into an ignored directory, so the parent has to be re-admitted a level at a
time — the same pattern as the existing `!.claude/bin/`. Still excluded: a 132 MB nuget cache,
19 MB of decompiler binaries, the per-subsystem inspections, the scratch bridge client, and the
hundreds of one-shot record scripts.

**A collaborator needs the same RimWorld install:** `tools/build.ps1` refuses to build unless the
Core assembly hashes to `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`.

## The warning that matters most right now

**SUSPECT YOUR OWN MEASUREMENT FIRST.** A search that finds nothing is not evidence, and across
0.12.24 → 0.12.41 **the measurement was the defect at least fifteen separate times while the code
was fine.** Five from 0.12.24 → 0.12.33 are tabulated below; the ten since are:

| Measured wrong | The truth |
|---|---|
| a public `OpeningPowerDrawWatts` written for the cost preview | **one already existed** in `GateFootprint.cs`, footprint-scaled and discounted by `RR_Cap_EfficientAperture`. The compiler caught it, which is the cheapest way this ever gets caught — and the existing one was *better*: the raw prop is not what any gate above 1×1 draws |
| **this file said `OpenNativeTab` already opens Architect** | it did not and never had. `grep -rn "Architect" --include=*.cs src` returned **nothing at all**. The stale measurement was in the handoff itself, which is the worst place for one |
| a colour guard that matched `new Color(` | `new UnityEngine.Color(...)` walked past it — and the qualified spelling is the one a file without the `using` would have to write |
| the queue count, **twice** (90 vs 86, then an item count of 19 and 13 vs 20 and 12) | the list is renumbered on every close, so the count must come from the file |
| **six** shipped work-giver priorities above the clamp | **seven** — the pattern was `<WorkGiverDef>` and missed `<WorkGiverDef MayRequire=…>` |
| **five** ways a gate can stop working | **six** — I forgot the deliberate cutoff. Then a seventh arrived and the proof kept passing, because it read one file of a **partial class** |
| a replant of the historical `maxTechLevel` defect **passed** | 0.8.7-dev fixed it by **adding the field to the class**, so the field is valid now. The plant was wrong, not the checker |
| `CompHoldingPlatformTarget` flagged as an ungated expansion defName | it is a **comp type** in the always-present base assembly |
| `MULTIPLAYER.md` reported as missing a sentence it contains | the document is **hard-wrapped** and a literal phrase search cannot cross a newline |
| a fault-plant run reporting **17 of 17 caught** | **worthless** — a syntax error made the proof fail unconditionally, so every plant registered as caught |

The five earlier ones:

| Measured wrong | The truth |
|---|---|
| a grep for the documented assembly hash returned nothing | the pattern was wrong; the line was correct |
| the queue reported **90 open** | 86 under one consistent pattern — two different greps, neither wrong about the file |
| a keyed-string parser found **33** strings | it matched the `<LanguageData>` wrapper; there are **1,499** |
| **three gate projects "grant nothing"** | they drive `PortalWindowTier` by counting completed projects **by defName**, which the def file's own comment says. I nearly shipped a three-hollow-projects finding |
| the wiring check reported **106 dangling defs**, then **3** | **zero.** Defs are consumed by name, **by type**, or by cross-reference from another def's XML, and I had only implemented the first, then the first two |

And a fault plant caught a **blind claim** of mine at 0.12.33-dev: *"the readout is wired"* checked
that a key **appeared** in the file, so replacing `listing.Label` with a no-op left the claim passing
while nothing was drawn. **A claim that searches for a string is not a claim about behaviour.**

The older instances below are kept because they are the evidence, and because two of them are the
reason `GetNamedSilentFail` is treated as dangerous here:

| What happened | Why it was worse than being wrong |
|---|---|
| **`Named<TerrainDef>("Carpet")` returned null, silently, for months** | Core ships `Carpet` as a `TerrainTemplateDef`; there is no `TerrainDef` of that name. `GetNamedSilentFail` is silent **by design** and a `??` fallback made wood plank flooring look deliberate. **The depth-1 yellow rooms — the one look invariant 25 calls sacred — were never carpeted.** |
| **I marked working code *"confirmed unbuilt by grep"*** | The mineable-rock fill ships. My grep searched `Generation/` for *"Mineable"*, *"Granite"*, *"RockRubble"* — **words the code does not contain**, because it asks `Find.World.NaturalRockTypesIn`. I then accused a correct comment of lying. **Condemning working code on a failed search is worse than trusting a wrong comment**, because it invites somebody to "fix" what works. |
| **A check I wrote to catch one specific thing PASSED that exact planted fault** | The floor-value claim skipped terrains with no cost list as *"never built"* — which excused `PackedDirt`, the precise case it existed for. **A filter that skips the case it guards against is worse than no check**, and only the planted fault found it. |
| **A claim keyed off proximity broke when correct code moved near it** | It searched for a capability name within 400 characters of a constant. **Proximity is not the thing that happens.** Fifth instance of that class. |
| **Claims matching the code's own comments** | Twice more, including a rule defeated by the two doc comments explaining why the thing it looked for is deliberately absent. **Sixth instance.** |

### THE TRAP THAT NOW OUTRANKS EVERY OTHER ONE

**0.12.53-dev added eight more, bringing it to twenty, and one of them is the lesson in miniature:
the fix written to close the prefix trap fell into the prefix trap.** Asserting
`"SpawnNativeConduit(…" not in body` fails against **correct** code, because
`TrySpawnNativeConduit` *contains* `SpawnNativeConduit`. It strips the safe calls first now.

The eight from this checkpoint, on top of the twelve below: a **retired symbol name** (so a
re-carpet under a new name walked past); a `"throw" not in body` test that a **call-site swap** does
not disturb; a cap check appearing **twice**; **two prefixes** (`CompProperties_Glower` inside
`…GlowerUnused`, same for Colorable); a `SetColor` surviving being wrapped in **`if (false)`**; a
lookup whose later use survived an early **`return true`**; and a guard **nothing asserted at
all**.

**A claim satisfiable by something other than the thing it is about.** It has defeated a proof
claim **in every single checkpoint from 0.12.46 to 0.12.52**, and the plants caught all of them.
The full list, because the shape is only obvious once it is in a table:

| What the claim read | Why a plant walked past it |
|---|---|
| `"Prefs.MaxNumberOfPlayerSettlements" in budget` | the name is also in the **doc comment** above the code |
| `"RR_Frontier_TooManyGatesHeld" in keyed` | it is a **prefix** of `…HeldUnused` |
| `"MaximumFrontiersPerCoordinate" in frontier` | the **declaration** survived while the *use* was deleted |
| `"return false;" in parent` | that shape appears **four times** in the file |
| `"if (x == center.x …)" in planner` | a later feature added the **same line** to a second function, and the harness replaces only the first |
| `genstep.count("RockIntrusionCells") == 1` | a **comment** mentioning the name counted |
| `find(a) < find(b)` across a file | `SetRoof(cell, overheadRoof)` appears **twice**, so the wrong pair was compared |
| `"!receipt.IsTerminal" in crossing` | it appears **seven times** in that file |
| `"EnsureSite(campaign, coordinate, …)" in address` | the call appears **twice**; a presence test survived deleting one |
| `"connections.Remove(" ` | did not match a planted `connections.RemoveAll(` |
| `CoherentDepth >= 1` | a planted **99** passed — no upper bound |
| nothing asserted the **variant** reached the hash key | and that variant *is* the entire per-fixture feature |

**The rule, and it is cheap to follow:** scope a claim to the **method body**, the **exact tag**,
or the **call site** — and **count what should exist** rather than testing that something does. A
claim about code must never be satisfiable by a comment, a prefix, a declaration, or a duplicate.

**Twice this session the plant harness refused to run** because a new line made an old anchor
match twice. That is the harness working: it will not score a fault it never planted.

### The rules that come out of it

- **Key a claim off the thing that happens** — an assignment, a guard, an exit status. Never a
  token near it, a variable's spelling, or a count of a string.
- **Strip comments before searching source.** Six times now.
- **A grep for the words you expected, in the file you expected, is not a search.** Check the API
  the code actually calls.
- **`GetNamedSilentFail` plus a `??` fallback is a silent wrong answer.** Assert that every def a
  generator names actually resolves — including template-generated ones.
- **Plant the fault and confirm it fails for the RIGHT reason.** A check that passes its own
  motivating case is the worst outcome available, and reading will never reveal it.
- **Never widen a rule so your own text passes.** Refused three times this session: a key was
  renamed, two descriptions were reworded, and the vocabulary rule was obeyed rather than relaxed.

### The rules that come out of that

- **Key a claim off the thing that happens** — a guard expression, an assignment, a refusal, an
  exit status. Never off a token near it, a variable's spelling, or a count of a string.
- **A claim with a conditional fallback can be trivially true.** If the anchor is missing, the
  whole expression degenerates and says nothing.
- **Plant the fault and confirm it fails for the RIGHT reason.** A claim that fails for the wrong
  reason will pass for the wrong reason too.
- **Check the plant landed.** A patch script asserts before it writes, so a mistyped anchor plants
  nothing — and the proof passing afterwards proves nothing.
- **A wrong claim is far better than an unfalsifiable one.** Three times this session a corrected
  claim was *also* wrong on its first try and failed immediately. That is the system working: the
  wrong one tells you.

**And the older lesson still holds:** when a proof only ever confirms, suspect it. Two designs
changed *because* a proof disagreed — the spin-up decay rate, and revisit displacement firing
every single time.

---

## Standing method

- **Check the register first** (LAW). `python tools/register-query.py family <x>`, then the per-mod review under `docs/research/reviews/mods/`. Say what you checked.
- **Read the prep work.** `UNIVERSE_ADAPTATION.md` had an unbuilt item nobody had noticed for the whole project.
- **A TODO item carries all its related work.**
- **At a fork: ask immediately**, multiple choice with a write-in. Never flag.
- **State what already works before building it again.**
- **Name what is not done, in `TODO.md`, in the same checkpoint.**

## Read these first

1. `docs/NOW.md` — this file.
2. `docs/TODO.md` — every owner direction verbatim.
3. `.claude/CONSTRAINTS.md` — the LAWs, including the register LAW.
4. `docs/GATE_0_DECISIONS.md` — D1–D9 **and** decisions 13–25. D1 changed.
5. `docs/implementation/CONNECTED_WORK_CORE_API.md` — pinned Core facts.
6. `docs/PUBLISHING.md` — the cascade. Follow it literally.

## The checkpoint ritual

1. **Check the register** for the system family being touched, and record what it said.
2. Read every file in full before editing.
3. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — zero warnings. It refuses if csproj and `About.xml` disagree, so bump both.
4. `CHANGELOG.md` in plain player-facing language.
5. Implementation record under `docs/implementation/`.
6. Ledger: `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`.
7. **Every checker** (ELEVEN): `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `check-register-compliance.py`, `check-retired-content.py`, `check-wiring.py`, `research/audit-gate0.py`.
7b. **Every proof (TWENTY-ONE), by exit status:**

```sh
for p in .local/register/proof-*.py; do python "$p" >/dev/null || echo "FAILED: $p"; done
```

   **Do not grep their output.** Eleven end `PROOF HELD` and four end `PASS:`; grepping one
   phrasing skipped four live proofs for most of one session. Exit status is phrasing-independent.

   The set: `displacement`, `facilities`, `facility-relief`, `fit`, `gate-links`, `incidents`,
   `interior-resource`, `live-effects`, `menu-slides`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,
   `request-line`, `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`,
   `world-exit`,
   `universe-factions`.

   **`patch-*.py` in that directory are one-shot edit scripts, not proofs.** They were once named
   `proof-*` and re-running one would try to re-apply a landed patch and fail confusingly.

   **Sanity-test any new claim by planting a fault** and confirming it fails **for the right
   reason**. Three claims this session passed a planted fault; all three were mine.
8. **Determinism**: delete `obj/` and `bin/`, rebuild **twice**, hashes must match.
9. Commit once atomically; cascade to `Prep`, `Develop`, `Main` on **both** remotes; **read back all eight refs**.

## Gotchas learned the hard way

- **XML comments cannot contain `--`.** Hit **five times**. The checker names the rule and the line.
- **Bash heredocs mangle `\n` and break on apostrophes.** Hit **TEN times**, the last three after this line already said so. **Stop reaching for a heredoc when the payload contains a backslash escape or an apostrophe** — use the Write tool, and a message file for commits.
- **A GitHub push can silently drop some refs.** Read back all eight, every time — it happened once this session.
- **A failed `assert` in a patch script means nothing was written** — the write comes last. So a fault-plant whose anchor was wrong plants nothing, and the proof passing afterwards proves nothing. Check the plant landed.
- `git` index lock goes stale; `rm -f .git/index.lock`.
- **`cd` inside a Bash call persists.** Absolute paths.
- Package manifests are UTF-8 **with BOM** — `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName> "<RimWorld>/RimWorldWin64_Data/Managed/Assembly-CSharp.dll"`. **Empty output means the type name was wrong.**
- C# 7.3: no target-typed conditionals.
- **A def field emitted in XML that no class declares is ignored silently at load.**
- Core's `StockGenerator_Category` has **all-private fields**. `GenRecipe.PostProcessProduct` is **private static**.
- `SetTerrain` **clears** the colour grid. `CompFlickable.SwitchIsOn` has a **public setter**.

## WHAT IS OPEN AFTER 0.12.52-dev

**Nothing in flight and nothing half-built.** Every decision the owner made this session is
implemented and verified at source level. What remains is **runtime acceptance**, which only a
launch can give.

One thing was explicitly deferred and then shipped the next checkpoint, so the pattern is worth
keeping: when a piece needs a save-schema change and a teardown order, say so and do it properly
next rather than half-building it. The Operations release list was that piece, and it is done.

**Owner decisions taken this session, all implemented:**

| Decision | Answer |
|---|---|
| level size | **300x300**, up from 60x60 |
| room count | **grand at level 0** — 6 halls of 80x80 with 144 pillars each — tightening to 42 rooms of 24 by depth 6 |
| families | threshold / office_copy / return_gallery **unique**; the other five repeat |
| onward gates | **4–6 per level**, one per 20 rooms; `MaximumNaturalDepth` **3 → 6** |
| saves | **fresh save**; the 60x60 path is dropped, `PlannerVersion` 3 |
| cave-ins | **never**, via a coordinate-only `RoofDef` with `canCollapse false`; Core's roof untouched |
| map budget | **`Prefs.MaxNumberOfPlayerSettlements`** (the player's own 1–5 slider), floor of 2, per-scenario override |
| natural gates | **deconstructable** (route lost) and **minifiable/movable** (route follows the door) |
| releasing a place | **Operations → Places**, with a Release button and a `releasedByPlayer` save flag |
| materials | **level 0 coherent and yellow**; deeper, **every type for all things**, per fixture |

## Open owner questions — THERE ARE NONE

**Nothing in this project is waiting on the owner.** Every remaining item in the queue above is
buildable, and the owner's standing instruction is that the register is **guidance, not law** and
that *"test cases arnt being worried about right now we are trying to get the build complete so we
can test"* — so **unverifiable-without-a-launch is never a reason to defer building something.**

### Answered this session, so nobody re-asks

- ~~**The route model**~~ — *"Both — filter picks the family, card never shrinks."* Eligibility
  gates which family is offered; the card shows the full authored floor, unfiltered.
- ~~**Branch unlock order after the hinge**~~ — **all eight open, any order.**
- ~~**The world exit vs the stranded-crew guarantee**~~ — **build it, a player caravan is still
  yours.** The narrowing is asserted by name: closing, expiry and traversal still never take a crew.
- ~~**The map cap**~~ — **five, universally**, counting the Backrooms map and every claimed tile;
  over that, caravans. The player's own `Prefs.MaxNumberOfPlayerSettlements` wins if stricter.
- ~~**The register's standing**~~ — **guidance, not law.** A row does not veto work.
- ~~**The public face**~~ — everything, including Playwright driving Steam. Still correctly last,
  and it needs the owner present.
- ~~**Testing**~~ — *"test cases arnt being worried about right now we are trying to get the build
  complete so we can test."* **Unverifiable-without-a-launch is not a reason to slow the build.**
- ~~**`RR_FieldRecorder`, the last authored gameplay item**~~ — **fold its job into the record book
  crews already carry.** Core's `TextBook` is already the native evidence carrier; the same book now
  logs rooms, mismatches and sightings. **No new def, no save break** — the recorder stays loadable
  so old saves open, and is never granted or sold again. **This is the next thing to build.**

### Answered 2026-09-29 — the last three

- ~~**How a generated request picks its routes**~~ — **a declared pool, filtered by capability.**
  A family declares a route **pool** in XML; generation filters it to what the branch can take,
  and **if fewer than two routes of two different kinds survive, the request does not generate.**
  Unblocks queue item 3, closes chart §6 item 3.
- ~~**Whether the eight branches unlock in any order after the hinge**~~ — **all eight, any
  order.** Each branch keeps its own internal tier ladder; no branch gates another. Closes chart
  §6 item 2.
- ~~**The public face**~~ — **everything, including Playwright driving Steam.** The concern was
  stated before the choice and the owner chose it anyway, so it stands and is not re-litigated.
  Still last, and it needs the owner present for the Steam session.

### The question that was never open, and I asked it anyway

**The adjacent-door-run fallback was owner-answered on 2026-09-29 — *"BOTH paths"* — and I put it
back on the table one turn after the handoff audit fixed exactly this defect.** *"wtf are you
talking about core only we have 294 recommend mods you fuck!!!!"*

Two lessons, both load-bearing:

1. **Search the ledger before asking.** `grep` for the subject across `.local/register/` and
   `docs/` costs one command. The answer was sitting in `todo-089.py:37` in capitals.
2. **Zero hard dependencies and Core-only are not the same claim.** The package must *load and
   run* against Core alone — that is a **build** property and it holds. The install this mod is
   *designed for* is **the 294**. Never write an option, a doc line or a design argument that
   treats a vanilla install as the audience.

### Closed earlier this session, so nobody re-asks

- ~~**`reserveChargePowerWatts`**~~ — **a supply requirement before opening.** Wired 0.12.4-dev,
  and wiring it revived `RR_Cap_ReserveDiscipline`, a tier-0 card that had promised an unlock and
  moved nothing.
- ~~**The 250 W idle draw**~~ — **kept.** Confirmed as the intended behaviour; no change needed.
- ~~**Natural gates indestructible**~~ — **relaxed by the owner** to a confirmation warning.
  *"dont worry about it, can we at least do a rim style pop up warning"*.
- ~~**The solo/group tutorial line**~~ — **option three:** no request line until contact, plus four
  hints in the survivors' own voice. None is an objective.
- ~~**The solo/group exit**~~ — **two maps, coordinate is real.** Superseded the earlier
  seed-tile answer once `RimroomsPortalNetwork.Register` was read.
