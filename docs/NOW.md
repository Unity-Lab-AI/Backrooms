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
| Version | **0.12.83-dev** — read from `About.xml`, never from a document |
| Build | **215 C# files, 92 package files**, zero warnings, zero errors. Measure, never carry: `git ls-files -co --exclude-standard 'src/**/*.cs' \| wc -l` and the `files` array in `tools/package-files.json` |
| Dependencies | **294 declared**, `loadAfter` the same. Read from `About.xml`. **The owner has directed that this come out — see the stand-alone rows in `TODO.md`, and the checker warning below before starting** |
| Instruments | **16 checkers** (`tools/check-*.py`), **49 proofs** (`.local/register/proof-*.py`), **23 plant suites**, **836 plant anchors**. Run by **exit status**, never by grepping output |
| Queue | **70 open · 38 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch has found was ours — not one was a mod conflict** |

---

## Publication cadence — batches of 10 to 12, not every change

**Verbatim owner direction (2026-10-03):** *"aftert u finish up go ahead and get back to the staging, now.md writeing, and the cascades but not every time u do something only after you finish like 10-12 items in the todo do u do another stage/cascade"*

Count closed items as **rows archived out of the queue into `FINALIZED.md`** — that count cannot be inflated, because a row only leaves on a proved byte-for-byte transfer. **This publication carried 13 rows.**

---

## What 0.12.83-dev changed

### A floor has an architecture

`Generation/CoordinateMotif.cs`. Seven room shapes already existed and **every room rolled its own, independently of every other room** — which does not make a pattern, it makes noise. A coordinate now draws one **shape** and one **theme** from its own seed, and *how hard that grip holds falls with depth*.

| depth | 1 | 2 | 3 | 4 | 5 | 6 | 8 |
|---|---|---|---|---|---|---|---|
| rooms on the motif shape | **89.3%** | 74.9% | 72.3% | 62.5% | 53.7% | 44.5% | **36.5%** |

All seven shapes appear at every depth. **A random floor sits at 14.3%.** One number produces both the monotonous shallow floors the yellow look depends on and the *"further in it gets very varied and weird"* curve.

### Forty-four kinds of room, and a floor is somewhere

Archetypes were drawn against their own weight alone, so a coordinate held a classroom beside a weapons locker beside a nursery. Each now declares `themes` from the eight in `CoordinateMotif.Themes`, and a coordinate's own theme makes a matching one **×3** likelier — **a bias and never a filter**, because a market holding nothing but shops is a themed level rather than a Backrooms level. The owner's named kinds all exist by name, plus twenty-one more. **44 archetypes × 7 shapes = 308 distinguishable rooms before a single slot is rolled.**

### The freeze says so before it happens

`Presentation/RimroomsGenerationNotice.cs`. Both Operations-pane openings now draw a **full-screen notice carrying one of the mod's own menu images**, then run the generation inside `LongEventHandler.QueueLongEvent` with our wait text. A tone per shipped scenario. **And the menu had been opening on slide one of six, every launch, forever** — the index was pinned to `0` in two places.

---

## THE NEXT THING

**Roads and neighbourhoods as *arrangements*, not as room kinds.** The `TODO.md` row for *"rooma corradors facilites infastructure roads neighborrs hood malls shoopping centers military"* was right about itself: every kind now exists as a room, **but two of them are not room shapes at all.** A road is a run of rooms sharing a through-line; a neighbourhood is a cluster standing wall to wall off one spine. Both are reachable now — `PushAgainst` can press any room against any neighbour, and the lane router reaches a slot two away — and **nothing composes them yet.**

After that, the two biggest open items are the **stand-alone/dependency work** (see the checker warning below) and **the gate-enter path for the freeze notice**, which needs the result chain deferred.

---

## Read these before touching anything

- **THE CASCADE IS TEN REFS, NOT EIGHT.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. A publish that reads back eight has silently left the branch the work is on unpublished. **Count the branch you are on.** `PUBLISHING.md`.
- **A SOURCE-TEXT CLAIM MUST ASSERT THE CALL, NOT THE CALLEE — five instances in two sessions.** The guard is still defined, the condition still names it, and the call has been replaced by a constant. Assert `bool onMotif = (roll / 101) % 100 < Hold;`, not that `ShapeFor` exists. Every one of the five was found by a plant reporting MISSED, never by reading.
- **A CHECKER CURRENTLY ENFORCES THE OPPOSITE OF THE STAND-ALONE DIRECTION.** `check-doc-conformance.py` reports *"declared dependencies : 294 (no living document may say there are none)"*. That rule has to invert **in the same change** as the declaration, or the build gate fails on correct documents.
- **A NEW FAMILY ID COSTS FIVE ARTEFACTS AND THE FIFTH ONE BITES.** `RepeatingFamilies` in `DestinationService`, `RR_Room_<id>`, `RR_Clue_Label_<id>`, `RR_Clue_Text_<id>`, and **a `case` in `RoomContentBuilder` — whose `default` throws `RR_Generation_InvalidRoomGraph` and kills the level.** An *archetype* costs none of that, which is why the composition engine went there.
- **EVERY ARCHETYPE MUST HOLD SOMETHING WORTH CARRYING OUT.** Owner: *"need loot inside of them too"*. `proof-facilities.py` enforces it per archetype by requiring a `<category>` slot — and it caught eight of the twenty-eight new kinds shipping as furniture only.
- **REBUILD THE MOD BEFORE BELIEVING THE PROBE**, and **rebuild the probe after changing it**. It kept a third copy of the adjacency rule and reported `shares no axis` for links that were perfectly legal, so every refusal reason it printed was wrong.
- **MEASURE THE SIDE EFFECTS, NOT ONLY THE FEATURE.** Two owner-asked features were *regressing* as a side effect of the degree work and only the probe saw it: back-to-back pairs 131 → 23, room shaping 83.5% → 42.2%. Both fixed. Neither was in the change anybody was making.
- **A WINDOW MUST DRAW INSIDE `RimroomsWindowState.Clean()`.** Unity's IMGUI state is process-wide; a leaked zero-alpha `GUI.color` from any of 294 other mods renders a frameless full-screen window **completely invisible**. `check-display-style.py` refuses an unguarded one, and it refused the new notice until it was fixed.
- **THE THEME LIST IS APPEND-ONLY.** `CoordinateMotif.Themes` is indexed from the coordinate's seed, so inserting one in the middle re-themes every coordinate already saved. A place a player has walked would come back as somewhere else.
- **A PLANT THAT STOPS PLANTING A REAL FAULT MUST BE RE-AIMED, NOT DELETED.** One went toothless when a guard became redundant; it had been reporting CAUGHT for nothing. The MISSED is the instrument working.
- **AN ABSENCE CLAIM MUST READ COMMENT-STRIPPED SOURCE** (`planner_code` / `no_comments()`), and **a claim after a proof's exit gate cannot fail**.
- **The mod register is GUIDANCE, not law.** `python tools/register-query.py use <trace>`.
- **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document.
- **USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES OR APOSTROPHES.** A bash heredoc has mangled `\n`, `\s` or an apostrophe **twelve** times here — the twelfth was this session, building a plant file, and it also ate a pair of XML comment delimiters.

---

## Findings recorded so nobody re-derives them

- **Our art cannot be drawn behind an *in-play* long event without Harmony**, and this mod ships none by decision: `Root.OnGUI` skips the UI root entirely while `LongEventHandler.ShouldWaitForEvent`, and the box over the frozen frame is Core's. **The answer was to own the surface instead** — the notice is our own full-screen window, drawn before the event is queued. Entry-state waits do draw `UIMenuBackgroundManager.background`, so those show our art already.
- **The gate-enter path still cannot announce.** A pawn crossing is a job tick and `GateSpinUp` reaches `EnsureSite` from a tick too. A tick cannot queue a long event and carry on, so that path needs the `CompanyActionResult` chain deferred. The Operations pane works because a button callback returns nothing.
- **Doglegging a corridor between two room centres is unsafe** — worked at depth 1, an L for the diagonal pair (0,0)→(1,1) runs straight through the room at slot (1,0). Bends run in the **rock lanes**, and a lane is defined by a room's own wall rather than by the slot grid, so a route needs nothing but the two rooms' rects.

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

**A row whose own evidence says *partly* must not be archived.** One was marked `[x]` this session and put back to `[ ]` before the move, because half of it — the gate-enter path — is genuinely open. The archiver will happily move a row that lies.

Both tools are tracked in `tools/`: `CONSTRAINTS.md` names them as the proof of verbatim transfer, and a LAW instrument that exists on one machine is not an instrument the team has. `STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0.

---

## Is it done?

**The build is. The play is not.** `0.12.83-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches. Run `python tools/check-planner-layouts.py` first — about two and a half minutes now, and the only instrument that runs the planner for real.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`. One launch's log had hundreds of red lines all downstream of the first; another had none and the answer was in a letter.
