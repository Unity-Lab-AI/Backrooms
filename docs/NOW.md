# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

So: **replace this file, never append to it.** Narrative about what a checkpoint found goes to `FINALIZED.md`. A rule that must survive goes to `.claude/CONSTRAINTS.md` or becomes a checker. Open work goes to `docs/TODO.md`. Nothing accumulates here.

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, every owner direction verbatim, **open work only** |
| `docs/DECOMPOSED.md` | smallest execution units, **open only** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

---

## State, measured 2026-10-04

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.82-dev** — read from `About.xml`, never from a document |
| Build | **213 C# files, 92 package files**, zero warnings, zero errors. Measure, never carry: `git ls-files -co --exclude-standard 'src/**/*.cs' \| wc -l` and the `files` array in `tools/package-files.json` |
| Dependencies | **294 declared**, `loadAfter` the same. Read from `About.xml`. **The owner has directed that this come out — see the stand-alone rows in `TODO.md`, and read the checker warning below before starting** |
| Instruments | **16 checkers** (`tools/check-*.py`), **49 proofs** (`.local/register/proof-*.py`), **23 plant suites**, **820 plant anchors**. Run by **exit status**, never by grepping output |
| Queue | **83 open · 38 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch has found was ours — not one was a mod conflict** |

---

## Publication cadence — batches of 10 to 12, not every change

**Verbatim owner direction (2026-10-03):** *"aftert u finish up go ahead and get back to the staging, now.md writeing, and the cascades but not every time u do something only after you finish like 10-12 items in the todo do u do another stage/cascade"*

Count closed items as **rows archived out of the queue into `FINALIZED.md`**, because that count cannot be inflated: a row only leaves on a proved byte-for-byte transfer. **This publication carried 21 rows.**

---

## What 0.12.82-dev changed — the generator, measured end to end

Every number below came out of `python tools/check-planner-layouts.py`, which is the only instrument that runs the real planner. **Before → after, same probe, same 200 seeds per depth.**

| | before | after |
|---|---|---|
| average links per room | **2.2 – 2.4** | **4.98 – 5.31** |
| most links on one room | **4** | **13 – 16** |
| rooms with one link | 6.5% | **0.2 – 0.7%** |
| rooms with none (sealed vaults) | 0.0% | **2.1 – 3.3%** |
| room fill, depth 1 | 46.0% | **57.2%** |
| room fill, depth 5+ | **17.1%** | **44.9%** |
| back-to-back pairs | 131 | **190 – 310 per depth** |
| refusals / fallbacks | 0 / 0 | **0 / 0** |

1. **Corridors bend, in seven shapes.** `RoomLayoutPlanner.BentLegs` + `RouteForms = 7`: two elbows through a lane beside the first room, two beside the second, two five-leg routes that reach a slot **two away**, and a **u-turn** that leaves through the wall facing away from the destination. **A lane is defined by a room's own wall, not by the slot grid**, so a route needs nothing but the two rooms' rects — no reader has to be told the spacing, so no reader can be told a different one.
2. **Degree rose because the ceiling was geometric, not a tuning.** Straight-only carving was *why* a link had to join grid-adjacent slots. Diagonal braid + reach braid + one slot in eight being a **junction** that takes every link it can, which is what produces a *spread* instead of a new uniform average.
3. **Sealed vaults, so degree 0 exists.** Slots reserved **before** the walk, so nothing can link to them. `CandidateIsSafe` now asks its reachability question of rooms that **claim** a route.
4. **The rock is worth digging.** `Generation/OreVeinBuilder.cs` — veins from every door-onto-nothing, between unlinked near pairs, and out of every vault; scattered lumps at **3× Core's own density read off Core's own scatter step**; deep-drillable resources including chemfuel into `deepResourceGrid`. **Nothing is named** — the ore list is read out of the loaded game.
5. **The space is filled.** `MaxSlotsPerAxis` 10 → 8 and `Margin` 14 → 6. A **finer** grid fills **less** space, because the rock between rooms is fixed per boundary. `MaxRooms` untouched at 60.
6. **Doors are off the wall midpoint**, via the new single authority `TryStraightCorridor`. It also unsealed the grand hall, which could previously only lead out along its own row.
7. **The menu picks a slide at random.** It was pinned to index 0 in two places. List moved to `Presentation/RimroomsSlideArt.cs`.

---

## THE NEXT THING

**The composition engine for room and facility types.** Owner, 2026-10-03, at the fork: *"option 3 but keep it not limited to my examples i want you to expand and expound on everything in a lsd way"* — build the engine, then express the named kinds (*"rooma corradors facilites infastructure roads neighborrs hood malls shoopping centers military"*) as recipes in it.

**Eight structural families ship and none of them is any of those.** A family must become a draw over **layout form × fixture set × material palette × motif**, so *"hundred s and hundreds of facilities and room types"* is a product of authored parts rather than hundreds of authored families — and *"repeated patternes in variations"* closes with it, because it is the same mechanism.

**A new family costs five artefacts and the fifth one bites.** `RepeatingFamilies` in `DestinationService`, `RR_Room_<id>`, `RR_Clue_Label_<id>`, `RR_Clue_Text_<id>`, and **a `case` in `RoomContentBuilder` — whose `default` throws `RR_Generation_InvalidRoomGraph` and kills the level.** Composition has to generate the content branch, not just the name.

---

## Read these before touching anything

- **THE CASCADE IS TEN REFS, NOT EIGHT.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. A publish that reads back eight has silently left the branch the work is on unpublished. **Count the branch you are on.** Full procedure: `PUBLISHING.md`.
- **A SOURCE-TEXT CLAIM MUST ASSERT THE CALL, NOT THE CALLEE.** Three plants walked straight past this session: the guard was still defined, the condition still named it, and the call had been replaced by a constant. Assert the assignment (`bool blocksARoute = !EveryLinkRoutes(...)`), not just that `EveryLinkRoutes` exists.
- **REBUILD THE MOD BEFORE BELIEVING THE PROBE.** `check-planner-layouts.py` rebuilds the *probe* and links the already-built assembly.
- **AND REBUILD AFTER CHANGING THE PROBE.** Its refusal diagnostic kept a **third** copy of the room-adjacency rule and reported `shares no axis` for links that were perfectly legal — so every refusal reason it printed was wrong and pointed at the wrong rule. A diagnostic that re-derives the thing it diagnoses is the defect class it exists to find.
- **A PLANT THAT STOPS PLANTING A REAL FAULT MUST BE RE-AIMED, NOT DELETED.** One went toothless this session when the braid's `AreNeighbourRooms` guard became redundant; it had been reporting CAUGHT for nothing. The MISSED is the instrument working.
- **MEASURE THE SIDE EFFECTS, NOT ONLY THE FEATURE.** Two owner-asked features were *regressing* as a side effect of the degree work and only the probe saw it: back-to-back pairs 131 → 23, and room shaping 83.5% → 42.2%. Both are fixed. Neither was in the change anybody was making.
- **A CONSTRAINT SATISFIED BY LUCK WILL BITE THE MOMENT SOMETHING ELSE MOVES.** `SpanVariation` happened to leave exactly the five cells the narrowest corridor needs, at every depth the planner produced. Changing the slot grid broke it. It is clamped to `SlotGap - (2 * NarrowestCorridorHalfWidth + 1)` now.
- **AN ABSENCE CLAIM MUST READ COMMENT-STRIPPED SOURCE.** `"x" not in planner` fails against correct code because the comment explaining the removed `x` quotes it. Use `planner_code` / `no_comments()`.
- **A CLAIM AFTER A PROOF'S EXIT GATE IS A CLAIM THAT CANNOT FAIL.** Appending checks after `if failures: sys.exit(1)` records failures nothing acts on.
- **CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT.** Twenty-one rows were closed in one earlier session as already-built.
- **The mod register is GUIDANCE, not law.** `python tools/register-query.py use <trace>`.
- **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document.
- **Use the Write tool for any script with escapes or apostrophes.** A bash heredoc has mangled `\n`, `\s` or an apostrophe eleven times here.

---

## Two findings that keep rows open, recorded so nobody re-derives them

- **The pre-generation freeze notice cannot be built until generation is deferred.** `DestinationService.EnsureSite` calls `GetOrGenerateMapUtility.GetOrGenerateMap` **synchronously** (line ~186) and hands the map back through an `out` parameter, so every caller depends on it having finished. A window added to the stack immediately before that call renders on the **next** frame — after the freeze. It needs `LongEventHandler.QueueLongEvent`, which changes the contract every caller relies on. Its own checkpoint.
- **Our art cannot be drawn behind an in-play long event without Harmony.** `Root.OnGUI` skips the UI root entirely while `LongEventHandler.ShouldWaitForEvent`, and the box drawn over the frozen frame is Core's. Entry-state waits **do** draw `UIMenuBackgroundManager.background`, so those show our art and now show it randomly. The reachable surface is one **we** own — which is the notice above, so the two rows close together.

---

## The live bug that is NOT ours — nobody hunt it in our source

```
ReflectionTypeLoadException getting types in assembly RimBridgeServer:
expected class 'HarmonyLib.CodeInstruction' in assembly '0Harmony, Version=2.4.2.0'
```

`RimBridgeServer.dll` wants **0Harmony 2.4.2.0**; `brrainz.harmony` ships **2.4.1.0**. Harmony loads at position 5 and the bridge at 198, so it is not ordering. Our package loaded clean in the same log. The fix is on the machine.

---

## The queue

```
grep -c '^\s*- \[ \]' docs/TODO.md     # open
grep -c '^\s*- \[~\]' docs/TODO.md    # partial
grep -c '^\s*- \[T\]' docs/TODO.md    # post-completion test phase
grep -c '^\s*- \[x\]' docs/TODO.md    # 0, and it must stay 0
```

**Archive at the end of every batch that closes rows**, not at a milestone:

```
python tools/archive-finished-todo.py --apply
python tools/verify-archive-move.py                                   # straight after, every time
python tools/archive-finished-todo.py --queue docs/DECOMPOSED.md --apply
python tools/verify-archive-move.py
```

Both tools are tracked in `tools/`: `CONSTRAINTS.md` names them as the proof of verbatim transfer, and a LAW instrument that exists on one machine is not an instrument the team has. The mover snapshots the queue and the archive **before** writing anything and the verifier reads the newest snapshot — so run it straight after. `STALE SNAPSHOT` exit **2** (baseline predates other edits; nothing was checked) is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0.

---

## Is it done?

**The build is. The play is not.** `0.12.82-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches. Run `python tools/check-planner-layouts.py` first — it takes about two and a half minutes now that seven route forms are tried per pair, and it is the only instrument that runs the planner for real.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`. One launch's log had hundreds of red lines all downstream of the first; another had none and the answer was in a letter.
