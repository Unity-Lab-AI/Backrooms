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

## ⛔⛔ PUBLICATION IS HELD BY THE OWNER, AND SO IS ONE REMOTE ⛔⛔

**Two separate holds, both current, both lifted only by the owner saying so.**

**1. Nothing publishes until the launch list is finished.** Owner, 2026-10-06, verbatim: *"we are not stageing now.md and cascading to all three remotes correctly and properly until we are sure all of this is completed"*. Work is committed **locally only** — the branch sits ahead of every remote on purpose.

**2. Forgejo is down.** Owner, 2026-10-06, verbatim: *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **The cascade is SIX refs while that stands** — `github` × five branches here, plus `github/main` on the mod-only repository.

**The remote is HELD, not removed, and that distinction is the point.** Deleting it would make every receipt read *complete*, and a future reader would never learn a destination had gone missing — the eight-ref publication that hid for forty-five checkpoints, wearing a different hat. `export-public-repo.py` keeps `forgejo` in `REMOTES`, skips it through `HELD_REMOTES`, **prints the hold and its reason every run**, and **refuses outright if every remote is held**. `PUBLISHING.md` opens with it, including: **do not push to it to test whether it is up.**

---

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04:** *"yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes"*, and when I over-corrected: *"you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the one instrument covering the file you just touched.**
- **STAGE FIRST at publication.** `powershell -File tools/stage-mod.ps1 -UpdateExisting` copies the build into RimSort's local mods folder, **which is the copy a launch loads.** It was in neither procedure until 0.12.99-dev, and the staged copy sat a whole version behind — caught minutes before a launch.
- **At publication, once:** 27 checkers → 59 proofs → 35 plant suites → `check-plant-residue.py`. **Then `export-public-repo.py --push`, then commit, then the cascade — and then `curl` the published site.**
- **THE OWNER ALONE LAUNCHES, SORTS AND PUBLISHES.**
- **`docs/TODO.md` ENDS AS A TEMPLATE HOLDING NOTHING**, per *"to get the todo to a templet form with no items listed"*. The `[T]` rows are the honest obstacle: one cannot close without the game running.
- ⛔ **NEVER RUN THE PLANT SUITES CONCURRENTLY WITH ANYTHING ELSE.** A suite writes a real fault into the tree and restores it; anything reading the tree in that window sees the fault. Doing so reported **four failures that did not exist**.
- **THE REGISTER IS AN INPUT TO WORK, NOT A BACKLOG OF IT.** Owner: *"as the Rimrooms Mod is stand alond only adding to it when mopds are added? right?"* Right. A row's disposition is settled when something is built that touches that mod, or when a launch gives evidence — **never as a bulk sweep**.

---

## ⛔ AND THE FIX FOR DEAD CODE IS TO REACH IT, NOT TO DELETE IT ⛔

**Owner, 2026-10-04, verbatim:** *"okay sounds like your deleting shit rather than fixing it by what you said,, that better not be the case"*

A ceiling I set myself is mine to manage, not a reason to delete a feature. **The same rule applies to an instrument:** `check-start-layout` refused a vent in a wall because the generator used to throw on one. It was **taught** `canPlaceOverWall`, not switched off — and a bed on a wall is still refused, which is most of what that rule was ever for.

---

## State, measured 2026-10-06

| | |
|---|---|
| Branch | **`feature/bug-testing`**, ahead of every remote by owner direction |
| Version | **0.12.99-dev** — read from `About.xml`, never from a document |
| Build | **235 C# files, 104 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile. **No register row claims this package requires a mod** — Core is the only `Required` row and Core is the game |
| Instruments | **27 checkers**, **59 proofs**, **35 plant suites**. Newest: `check-record-book-class.py` (27), whose own plant suite found **two false greens in it** before it was trusted |
| Remotes | **SIX active refs.** `forgejo` held on both repositories |
| Queue | **18 open · 4 partial · 50 `[T]` · 0 `[x]`** — every open row is work this launch created |
| Launches | **Thirteen.** The thirteenth is the first to produce facility data, and **every defect it found was ours** |
| Staged copy | **STALE on purpose.** Files differ while the game is open; `check-package-integrity` rule 10 says so and names the remedy |

---

## What the first real launch found

**The owner launched, fixed the company facility by hand, and reported five things. Four were defects in our code and one was a missing feature.**

1. **A PAWN STARVED AT THE COMMS CONSOLE, and it was fatal by construction.** Three things were true at once: `RR_OperateGate` declares `suspendable: false` **and** `casualInterruptible: false`; the station toil is `ToilCompleteMode.Never`; and its `FailOn` tested the gate, the calibration, the operator's identity, `Downed` and `InMentalState` — **and not one need.** The only exits were collapse, a mental break, or the player noticing. **The floor is absolute and is NOT the setting**, because the owner said both halves in one sentence: *"we cant have them not going to eat or finding saftey, but there needs to be like a driop down sleector thing"*. `GateWatch.MustLeave` is starving, exhausted, burning, bleeding out — every threshold Core's own — asked **before** any posture, in the `FailOn` **and** again every tick. **There is deliberately no enum value meaning *never leave*.** Three postures, per gate, as a `FloatMenu`. Held by 8 claims and 10 plants.
2. **PAWNS SPRINTED THE WIDTH OF A MAZE TO SOW A FLOWER POT, and the generator caused it in two lines.** `RoomContentBuilder` called `SetForbidden(false, false)` on **every** piece of room content, and fixtures spawn as `Faction.OfPlayer`. **The mechanism was read out of the shipped assembly rather than guessed:** `ForbidUtility.IsForbidden` tests the forbidden flag, `InAllowedArea`, and a lord's list — **fog is not part of it**, so fogging a coordinate would have changed nothing at all. The flag beat an allowed area **because of the player**: an area would override a control they own. `UnexploredWorkMapComponent` releases content when its cell stops being fogged, 600 cells a second, and **only ever un-forbids**.
3. **THE RESEARCH WAS INVISIBLE WHERE EVERY PLAYER LOOKS.** Owner, in capitals: *"I DONT SEE ANY RESEARCH FOR THE GATE SYSTEMS AND EVERYTHING THIS MOD HAS!!!!!"* Nothing was broken — the branch initialised clean and all 38 projects had records, in an Operations section invisible to the vanilla tab and therefore to ResearchTree and Research Whatever, both of which the owner runs. **38 mirrors now, own tab, nine columns by band, two genuine routes**, synced both ways. **And the register reversed a steer carried since 0.5.x:** it forbade shipping a `ResearchProjectDef`, while rows 191 and 279 ask for the opposite in their own words. A prohibition became **four assertions**.
4. **ONE OPERATOR, ONE CONSOLE, NO HAND-OFF.** `assignedOperator` is a single `Pawn` reference and the facility authored **one** `CommsConsole`, so a gate's window was hostage to one colonist's bladder with nowhere for a second pawn to stand. And the obvious hook is not one: `RR_Cap_ReliefWatch` sounds exactly like this and is already spent on spin-up decay. Answered *"Not gated — it's a defect, fix it free"*. **Still open as a build.**
5. **THE SOLO START HANDS YOU THE WAY OUT.** The natural exit spawns in the arrival room. Owner: *"the solo start u have to find your way to get out"*. **Still open**, and to be expressed as a minimum **room** distance rather than a cell distance — a 300×300 coordinate can put a cell far away and still inside the room you woke up in.

## What the facility read cost, and what it taught

**The owner's hand-fixed facility is in the def:** 18 conduit runs all `HiddenConduit`, 6 removed walls, 4 added including the two **Steel** ones flanking the gate door, **43 buildings** with their material, **8 trade beacons** one per room holding a shelf, the card table **complete** with its four stools, **4 coolers at −8 °C**, and 12 old entries dropped.

**FOUR GENERATOR CAPABILITIES HAD TO BE BUILT FIRST**, and the first blocked twenty of the twenty-six wall changes: the buildings loop threw on any cell holding an edifice, so a `Cooler` — whose whole purpose is to sit in a wall — was refused outright.

**And the read was wrong twice before it was right, both times caught by an instrument rather than by me.** Seven false *partial footprints*, because a thing the owner **moved** overlaps its own old position. Then two overlapping generators, because an authored thing counted as present if **any** cell of its footprint held its def — true for something shifted one cell. **Testing the anchor fixed both.**

**Three conflicts were real rather than tool faults.** The owner's stove covers the receiving-bay cell, so **the bay moved** — their placement is exact, so the cell that is not theirs yields. The comms console came back facing north because the read carries no rotation, putting its interaction cell **inside a wall**; a moved thing inherits its authored facing now. And the autodoor replaces no authored wall — they built the wall segment around it — so it is a building rather than a door-list entry.

---

## Read these before touching anything

- **`--` IS ILLEGAL INSIDE AN XML COMMENT, AND I HAVE WRITTEN ONE THREE TIMES** — `RR_GateJobs.xml`, `write-facility-def.py`, and the research generator. Both generators sanitise comment **bodies** at the point of writing and never the delimiters: the first sanitiser rewrote the `--` of `<!--` itself and broke line 2.
- **A SENTINEL THAT COLLIDES WITH A REAL VALUE IS A SILENT SETTING.** `targetTemperature` uses `NaN` for absent, because **0 is a temperature somebody means**.
- **THE VERSION IS A LABEL; THE BYTES ARE WHAT RUNS.** The staging guard compared version strings, and a fix landed without a bump — so it reported the staged copy current while the DLL was stale. It compares **every file by content** now, and names whether the operator can act: staging refuses while RimWorld is open.
- **`in` CANNOT TELL ONE SITE FROM THREE, AND MEASURE BEFORE YOU COUNT.** Two claims survived plants because an identifier appeared elsewhere. Then my own correction **guessed** a count of two where the measured answer was three, and failed on correct code.
- **ASSERT THE CALL, NOT THE DEFINITION.** A claim asserted `def foreign_work_types(...)` exists; its plant correctly reported MISSED, because a rule defined and never invoked does nothing.
- **A UNIT ERROR LOOKS LIKE ARITHMETIC.** The research mirror first cost `workRequired × (1 + insightCost)` — both "bench work" — producing 8,000 to 108,000 against vanilla's measured 200 to 8,000. **"Either route works" would have been false while looking true.** Measure the thing you are matching.
- **A NOTE THAT CANNOT BE CHECKED READS AS CHECKED AND FINE.** Seven *"cannot be verified"* patch targets sat in the battery for weeks while both mods declaring them were in the owner's own profile and installed.
- **AN ON-DISK AUDIT CANNOT SEE A DEPLOYMENT FAULT.** Every banner, and later the licence link, shipped as a 404 with every instrument green. **`curl` the published site; it is the last step of publishing.**
- **ONE PATTERN, ALL THE REFERENCES IT GUARDS.** The escape-path rule was written for `<img src>` and never given to `<a href>`.
- **A STALE DOC COMMENT IS THE UPSTREAM OF A PUBLISHED LIE.** Write a reader-facing sentence from the constant and the keyed string, never from the comment beside them.
- **A ROW CAN BE STALE IN ITS PREMISE, NOT JUST ITS STATUS.** *"a mod nobody has named"* was twelve named mods installed on this machine.
- **READ THE API OUT OF THE INSTALLED GAME, AND THE INSTALLED MODS.** `.local/tools/ilspycmd.exe` settled `ForbidUtility`, `ResearchProjectDef.CanStartNow` and thirteen giver base classes this session. The workshop library is at `steamapps/workshop/content/294100`, and **288 of the owner's 294 are in it**.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.** Mangled again; two layers of Python escaping turned `\r?\n` into a real newline inside a string literal.
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK.** *"A gate's connection has a duration. Nothing else in this mod has a duration."* It rewrote two of the three alternate-start premises, and `check-campaign-absolutes` refuses the forbidden noun **even in a sentence denying one** — reword the prose, never widen the rule.
- **A BILL NEEDS A `Building_WorkTable`.** Research benches are `Building_ResearchBench` and have no bill stack.
- **THE REGISTER ANSWERS MORE THAN IT LOOKS LIKE.** `python tools/register-query.py card <id>`. **`docs/CAMPAIGN_CHART.md` beats any prep document.**
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved.

---

## The facility read-back loop, which is now a standing tool

```
python .local/qa/facility-diff.py    authored RR_AsyncIndustriesStart   # the def, offline
python .local/qa/facility-diff.py    power    RR_AsyncIndustriesStart   # grid connectivity, offline
python .local/qa/facility-diff.py    snapshot RR_AsyncIndustriesStart   # read the live map
python .local/qa/facility-changes.py          RR_AsyncIndustriesStart   # classified, readable
python .local/qa/apply-facility-read.py                                 # measure the changes
python .local/qa/write-facility-def.py                                  # write them in
```

**The authored layout is offset onto the live map** — a 300×300 map and a 44×44 footprint at (8,8) give **(120, 120)** — and the offset is **confirmed by probing a known building**, never merely computed. The first read returned 2,116 cells of unexplored mountain. **It reads blueprints and frames too**, so a fix is readable before pawns finish building it.

**What it cannot carry:** a per-cell floor change (flooring is one facility-wide terrain plus a per-room boolean) and a knocked-through wall (walls come from the room rectangles, so a removal is a room edit). Both are stated up front, because a change the def cannot express is owner time that cannot be kept.

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
python tools/archive-empty-sections.py --list            # a heading with no rows is residue
```

The mover returns **3** for unarchivable prose after a closed row and writes nothing — **indent the paragraph into the row it documents**, so the note archives with its row rather than being stranded behind it.

---

## THE NEXT THING

**Four items remain on the owner's launch list, in this order:**

1. **The journal and quest brief.** Owner: *"this is big one to need proper write up before attempting the work and using ask me question where forks"*. Two forks are answered already — **per-quest books plus a branch ledger**, and **a dedicated write-up desk**, which **overrides the content-reuse rule and is recorded as a deliberate second exception** rather than slipped in. Two more need asking: how a book physically returns to the company, and what the green light reads from.
2. **The two starting journals are named wrong.** They are Core `TextBook`s, so they carry Core's own generated title and description — the two it rolled were nutrition and shooting. **Repurposing an existing item kept its identity as well as its model.** The fix covers purchased ones too.
3. **The wiki pass**, which the owner named in the same sentence as the journals and is not optional.
4. **Check off the scenario steps this launch completed.**

**Then the two builds this launch specified:** operator relief with up to four consoles, ungated and seamless; and the solo start's exit moved out into the maze.

---

## Is it done?

**The build is not, and for the first time the reason is a list of real play defects rather than an absence of evidence.** Thirteen launches in, the thirteenth is the one that paid: a hand-fixed facility, four code defects and two missing features, every one recorded with the owner's own words.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line — it carries the fixture-tell attachment count, the fastest signal that the object register reached anything — then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
