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
| Version | **0.12.84-dev** — read from `About.xml`, never from a document |
| Build | **215 C# files, 98 package files** (six new menu slides), zero warnings, zero errors. Measure, never carry: `git ls-files -co --exclude-standard 'src/**/*.cs' \| wc -l` and the `files` array in `tools/package-files.json` |
| Dependencies | **294 declared**, `loadAfter` the same. Read from `About.xml`. **The owner has directed that this come out — see the stand-alone rows in `TODO.md` and the checker warning below** |
| Instruments | **16 checkers** (`tools/check-*.py`), **49 proofs** (`.local/register/proof-*.py`), **23 plant suites**, **842 plant anchors**. Run by **exit status**, never by grepping output |
| Queue | **69 open · 38 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch has found was ours — not one was a mod conflict** |

---

## Publication cadence — batches of 10 to 12, not every change

**Verbatim owner direction (2026-10-03):** *"aftert u finish up go ahead and get back to the staging, now.md writeing, and the cascades but not every time u do something only after you finish like 10-12 items in the todo do u do another stage/cascade"*

Count closed items as **rows archived out of the queue into `FINALIZED.md`** — that count cannot be inflated, because a row only leaves on a proved byte-for-byte transfer. **This publication carried 1 row**, which is below the batch size and deliberate: the owner delivered new art mid-slice and asked for it staged and cascaded, so the arrangements work went out with it rather than waiting.

---

## What 0.12.84-dev changed

### Roads and neighbourhoods are arrangements now, not kinds of room

The queue row for *"rooma corradors facilites infastructure roads neighborrs hood malls shoopping centers military"* was right about itself: the kinds landed at 0.12.83-dev, and **two of them were never room shapes at all.**

- **A road** is `RoomLayoutPlanner.OnRoad` — a straight run of linked rooms carrying on past at least one end, with **every corridor along it cut at the wide half-width** whatever its own roll said. The run already existed; it read as a chain of ordinary hallways. Derived from the saved graph and stored nowhere.
- **A neighbourhood** is a block pressed wall to wall off one hub. Back-to-back pairs **248 → 376** at depth 1 and **366 → 488** at depth 3, in blocks of four.

### Three things the probe said that reading would not have

1. **The road braid did nothing and was deleted.** A pass picking a row and linking every slot along it moved the longest straight run *not at all* — 6 to 8 either way, which at depth 3+ is the whole slot row. At five links per room the braids already join almost every adjacent collinear pair.
2. **The neighbourhood push was a no-op where it was first written.** Largest wall-to-wall group: 3 with it, 3 without. **A room holding five or six links cannot slide** — `PushAgainst` undoes any move carrying one past `FurthestLinkedCentres`. Moving the pass *before* the diagonal and reach braids, and offering the hub's neighbours **least-connected first**, is what made it land.
3. **The prune was leaking.** It refused to touch any link whose centres shared an axis — true of the spanning tree, too coarse for the reach braid, which makes links two slots apart *along* an axis. The probe printed `link 2-6 has no route under it`. It now removes the edge and keeps the removal only if every room still claiming a route can still be reached from the threshold.

### Twelve slides, and four of them had been shipping undisclosed

Six new menu images arrived, discovered by the existing folder scan with no code change, and they are loading-screen backgrounds as well as menu backgrounds. **The disclosure claim was satisfied by one provenance file existing anywhere under `outputs/`** — so when the count went from six to twelve, the 2026-09-29 batch was shipping with no register row at all. Steam's AI-content requirement is **per asset**. All four are registered retroactively and `proof-menu-slides.py` now refuses any slide without its own row.

---

## THE NEXT THING

**The stand-alone / dependency work** is now the largest open item, and it has a trap in it — read the checker warning below before starting. After that: the gate-enter path for the freeze notice, and the `[T]` test phase that only a launch can open.

---

## Read these before touching anything

- **THE CASCADE IS TEN REFS, NOT EIGHT.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. A publish that reads back eight has silently left the branch the work is on unpublished. `PUBLISHING.md`.
- **A CHECKER CURRENTLY ENFORCES THE OPPOSITE OF THE STAND-ALONE DIRECTION.** `check-doc-conformance.py` reports *"declared dependencies : 294 (no living document may say there are none)"*. That rule has to invert **in the same change** as the declaration, or the build gate fails on correct documents.
- **A SOURCE-TEXT CLAIM MUST ASSERT THE CALL, NOT THE CALLEE — six instances in two sessions.** The guard is still defined, the condition still names it, and the call has been replaced by a constant. Every one of the six was found by a plant reporting MISSED, never by reading.
- **NEVER SLICE SOURCE WITH `text[text.index(A):text.index(B)]` WITHOUT ASSERTING `B` COMES AFTER `A`.** A marker moved above its partner, the slice came back empty, and `str.replace("", new)` inserted the replacement between **every character in the file** — 154,124 copies of one method in `RoomLayoutPlanner.cs`. `.local/qa/arrangements-fix.py` has the guard that caught it on the retry.
- **`git checkout -- <file>` DISCARDS SOMEBODY ELSE'S UNCOMMITTED WORK.** Six provenance rows written by the art pass were lost that way while restoring a hand-made test edit, and had to be reconstructed. Check `git status` for a file before reverting it.
- **MEASURE A NEW PASS AGAINST THE BUILD WITHOUT IT.** Two passes were written this session and one was deleted on the measurement. **And disabling a pass with `if (false)` will not compile** — `CS0162 Unreachable code detected` is an error here, so the probe silently linked the previous DLL and reported identical numbers. Gate on something opaque (`depth > 100000`) instead.
- **REBUILD THE MOD BEFORE BELIEVING THE PROBE**, and **rebuild the probe after changing it**. It kept a third copy of the adjacency rule and reported `shares no axis` for links that were perfectly legal.
- **MEASURE THE SIDE EFFECTS, NOT ONLY THE FEATURE.** Back-to-back pairs 131 → 23 and room shaping 83.5% → 42.2% both regressed as side effects of the degree work, and only the probe saw it.
- **A WINDOW MUST DRAW INSIDE `RimroomsWindowState.Clean()`.** Unity's IMGUI state is process-wide; a leaked zero-alpha `GUI.color` from any of 294 other mods renders a frameless full-screen window **completely invisible**.
- **EVERY ARCHETYPE MUST HOLD SOMETHING WORTH CARRYING OUT** (`proof-facilities.py`, a `<category>` slot), **a new family id costs five artefacts** and the fifth is a `RoomContentBuilder` case whose `default` throws, and **`CoordinateMotif.Themes` is append-only** because it is indexed from the coordinate's seed.
- **A ROW WHOSE OWN EVIDENCE SAYS *PARTLY* MUST NOT BE ARCHIVED.** The archiver will happily move a row that lies.
- **A PLANT THAT STOPS PLANTING A REAL FAULT MUST BE RE-AIMED, NOT DELETED.** The MISSED is the instrument working.
- **AN ABSENCE CLAIM MUST READ COMMENT-STRIPPED SOURCE** (`planner_code` / `no_comments()`), and **a claim after a proof's exit gate cannot fail**.
- **The mod register is GUIDANCE, not law.** `python tools/register-query.py use <trace>`.
- **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document.
- **USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES OR APOSTROPHES.** A bash heredoc has mangled `\n`, `\s` or an apostrophe **twelve** times here, and once ate a pair of XML comment delimiters.

---

## Findings recorded so nobody re-derives them

- **Our art cannot be drawn behind an *in-play* long event without Harmony**, and this mod ships none by decision. The answer was to own the surface: the generation notice is our own full-screen window, drawn before the event is queued.
- **The gate-enter path still cannot announce the freeze.** A pawn crossing is a job tick and `GateSpinUp` reaches `EnsureSite` from a tick too; a tick cannot queue a long event and carry on. That path needs the `CompanyActionResult` chain deferred. The Operations pane works because a button callback returns nothing.
- **Doglegging a corridor between two room centres is unsafe** — at depth 1 an L for the diagonal pair (0,0)→(1,1) runs straight through the room at slot (1,0). Bends run in the **rock lanes**, and a lane is defined by a room's own wall rather than by the slot grid.
- **A road braid is redundant at degree 5.** Recorded in the source where somebody would otherwise write it again.

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

Both tools are tracked in `tools/`: `CONSTRAINTS.md` names them as the proof of verbatim transfer, and a LAW instrument that exists on one machine is not an instrument the team has. `STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0.

---

## Is it done?

**The build is. The play is not.** `0.12.84-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches. Run `python tools/check-planner-layouts.py` first — about two and a half minutes, and the only instrument that runs the planner for real.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`. One launch's log had hundreds of red lines all downstream of the first; another had none and the answer was in a letter.
