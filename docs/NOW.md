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

## State, measured 2026-10-03

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.81-dev** — read from `About.xml`, never from a document |
| Build | **211 C# files, 92 package files**, zero warnings, zero errors. Measure, never carry: `git ls-tree -r HEAD --name-only \| grep -c '^src/.*\.cs$'` and the `files` array in `tools/package-files.json` |
| Dependencies | **293 declared**, `loadAfter` 294 with Core first. Read from `About.xml`. **The owner has directed that this come out — see the stand-alone row in `TODO.md`** |
| Instruments | **16 checkers** (`tools/check-*.py`), **49 proofs** (`.local/register/proof-*.py`), **23 plant suites**. Run by **exit status**, never by grepping output |
| Queue | **79 open · 39 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch has found was ours — not one was a mod conflict** |

---

## PUBLICATION CADENCE CHANGED — batches of 10 to 12, not every change

**Verbatim owner direction (2026-10-03):** *"aftert u finish up go ahead and get back to the staging, now.md writeing, and the cascades but not every time u do something only after you finish like 10-12 items in the todo do u do another stage/cascade"*

This replaced *"no need to stage and no need to cascade until told to start again"*, which was that direction's own stated exit. So: stage, rewrite this file, and run the **ten-ref** cascade — but only once a batch of **10–12 closed items** has landed. Count closed items as **rows archived out of the queue into `FINALIZED.md`**, because that count cannot be inflated: a row only leaves on a proved byte-for-byte transfer.

**This publication carried 49 archived rows**, far past one batch, because the preceding session ran under the no-cascade direction.

---

## What 0.12.81-dev changed

1. **A world tile is a round trip.** Emerging through a natural gate was one-way by construction — `LeaveThroughWorldExit` was the only direction, while `WorldExitRecord` had been saving `coordinateId` and `doorLoadId` all along with nothing reading them. `EstablishReturnGate` registers the claimed map as a remote site, spawns a marked Core `Door`, and registers an `Emergence` edge home **before anybody is despawned**. Every failure after the spawn destroys the door rather than leaving a false way home standing.
2. **A door can be commissioned as the gate before its circuit exists.** `DesignateAsGate()`. The old button resolved three providers and refused if any was absent or ambiguous, so a company start with no battery had no route from door to gate at all.
3. **An open gate is not charged power to pass somebody through.** `PortalWindowBlockerKey` was applying three *opening*-time power conditions to a crossing — including `ProjectedOpeningPowerFailure`, whose own docstring says *"This gates opening only"*.
4. **The blank record book explains itself**, instead of returning a null inspect string in the one state a player ever starts holding.
5. **The grand hall is placed from the seed**, position and orientation. It was two literals and had opened in the bottom-left corner of every level ever generated.
6. **The corridor has one authority.** `RoomLayoutPlanner.CorridorLegs` — extents, width, walls, the back-to-back skip — read by both the validator and the carver. Extraction proved byte-identical across all seven depths.

---

## THE NEXT THING, AND THE FINDING THAT SHAPES IT

**Bent corridors, and they unlock three other owner clauses at once.** Straight-only carving is *why* links must be grid-adjacent, so *"corradors arent all straight"*, *"room connected to like 0 - 10 other rooms"*, *"u -turns"* and *"multiple coices on directions to take in every rooms"* are **one job, not four**.

**Doglegging between room centres is UNSAFE, which is why this is not a loop change.** At depth 1 slots sit 45 apart and rooms are ~34 across: an L-corridor for the diagonal pair (0,0)→(1,1) runs from (36,36) toward x=81 and straight into the room at slot (1,0), which occupies x 64..98. Bends must run in the **rock gap lanes** between slots. `CorridorLegs` is now the one function that has to change.

**Two hazards it must answer, both silent if missed:** a multi-leg corridor places a **wall at each joint** inside the next leg's floor, so wall placement must skip any leg's floor cells; and `CorridorSideCells` would report a joint cell that is another leg's **centre line**, so the dressing could furnish the middle of the route. A blocked corridor is the unreachable-room class that cost this project thirty-nine checkpoints.

---

## Measured numbers to aim at — `check-planner-layouts.py`

Checker 14 is the only instrument that runs the planner for real, and it was taught to see degree, fill and hall placement this session because **every column it had was about whether a layout was LEGAL, not whether it reads as a maze.**

| depth | avg degree | max degree | roomfill | hall spots | in old corner |
|---|---|---|---|---|---|
| 1 | 2.37 | **4** | 46.0% | 56 | 16% |
| 3 | 2.39 | **4** | 38.8% | 59 | 7.5% |
| 5–8 | ~2.2 | **4** | **17.1%** | 113–116 | ~13% |

- **avg degree 2.2–2.4 is literally one entrance and one exit.** The braid adds ~0.4 over a bare spanning tree.
- **max degree 4 is a hard ceiling**, because every link must join grid-adjacent slots. The owner's 0–10 is unreachable without bent corridors.
- **roomfill falls to 17% by depth 5**, so a deep coordinate is 83% uncarved rock — and it gets *worse* with depth.

---

## Read these before touching anything

- **The cascade is TEN refs, not eight.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. A publish that reads back eight has silently left the branch the work is on unpublished. **Count the branch you are on.** Full procedure: `PUBLISHING.md`.
- **A CLAIM AFTER A PROOF'S EXIT GATE IS A CLAIM THAT CANNOT FAIL.** Appending checks after `if failures: sys.exit(1)` records failures nothing acts on. It happened this session and the plants caught it, not the author. Swept all 49 proofs: no other instance.
- **An absence claim must read comment-stripped source.** `"x" not in planner` fails against correct code because the comment explaining the removed `x` quotes it. Use `planner_code` / `no_comments()`. `code()`'s docstring had counted thirty-six instances; this session made thirty-seven.
- **REBUILD THE MOD BEFORE BELIEVING THE PROBE.** `check-planner-layouts.py` rebuilds the *probe* and links the already-built assembly. Measuring before `tools/build.ps1` reported a fix that had not shipped.
- **CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT.** Twenty-one rows were closed this session as already-built; separately, two slices of a seven-slice plan turned out unnecessary or already done.
- **A `[~]` row is not automatically honest.** Ten of fifty partials were governance wearing checkboxes or finished work nobody ticked.
- **The mod register is GUIDANCE, not law.** `python tools/register-query.py use <trace>`.
- **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document.
- **Use the Write tool for any script with escapes or apostrophes.** A bash heredoc has mangled `\n`, `\s` or an apostrophe eleven times here.

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

Both tools **moved out of gitignored `.local/qa/` into tracked `tools/` on 2026-10-03** by owner direction: `CONSTRAINTS.md` names them as the proof of verbatim transfer, and a LAW instrument that exists on one machine is not an instrument the team has. The mover snapshots the queue and the archive **before** writing anything, and the verifier reads the newest snapshot — so run it straight after. `STALE SNAPSHOT` exit **2** (baseline predates other edits; nothing was checked) is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0.

---

## Is it done?

**The build is. The play is not.** `0.12.81-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches. Run `python tools/check-planner-layouts.py` first — checker 14, the only one that runs the planner for real.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`. One launch's log had hundreds of red lines all downstream of the first; another had none and the answer was in a letter.
