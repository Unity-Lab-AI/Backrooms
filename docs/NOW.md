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

## State, measured 2026-10-04

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.85-dev** — read from `About.xml`, never from a document |
| Build | **217 C# files, 98 package files**, zero warnings, zero errors |
| Dependencies | **294 declared**. Read from `About.xml`. **Owner has directed this come out — read the checker warning below first** |
| Instruments | **17 checkers** (`tools/check-*.py`), **49 proofs**, **23 plant suites**, **844 plant anchors**. Run by **exit status** |
| Operations panel | **3,980 on-screen words / 121 controls / 32.9 words per action** — `tools/check-operations-density.py` |
| Queue | **79 open · 38 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## ⚠ WORKING RHYTHM — OWNER CORRECTION, 2026-10-04

**Verbatim:** *"this setting of 10m timers conbstantly with all the checks you are doing is becoming excessive i told you we only do stageing and checks and cascades and shit only after completing a bunch of todo items not on every fucking one,, we are spoenign 9/10ths of the time just doing maintainace work"*

**They were right and it was my fault.** I was running all 17 checkers and 49 proofs after every single edit. **Run the full battery ONCE, at publication.** During the work, run only the one instrument that covers what you touched. The batch size is still 10–12 closed rows.

---

## What 0.12.85-dev changed

1. **The machine tab is a status board.** Eleven checks were fourteen wrapped paragraphs; now one row per system with a coloured light **and Core's checkbox glyph**, one next-step line for the whole tab, every instruction in full on the row's tooltip. **356 on-screen words → 58.**
2. **"Less of a text wall" is a number.** `check-operations-density.py` — words on screen vs on hover vs controls, per pane, as a **ratchet**: each pane's figure is recorded and may only come down.
3. **Internal ids off the player's screen.** `CoordinateRecord.AddressCode` is the one thing readouts ask for. The raw id had leaked in four places, one of them onto a button.
4. **A natural door can be boarded up** by a colonist for 25 wood, closing its place and freeing a map slot. Reuses `CoordinateRelease.TryRelease`; re-checks the release conditions at the **end** too, because a crew can walk in while the boards are carried.
5. **Three operational gates**, refused at **designation** not at opening.
6. **A gate can dial blind.** `PortalRandomDial` — unpredictable dial, deterministic place (monotonic index, never `Rand`). Creates an **address, not a map**.

---

## THE NEXT THING

**The Operations panel, pane by pane.** Owner: *"all the tabs of operations are well designed for a tripple A Mod currently it looks like its all just text wall and shit"* and *"all things should be done"*. The ratchet is in place and the machine tab is done; **the other seventeen panes are not.** Worst first by on-screen words: `OperationsExpeditions` 442, `MainTabWindow_Operations` 421, `OperationsPersonnel` 413, `OperationsPortalNetwork` 396.

Then: **everything doable from the device, not just the panel** (owner's own words — the board-up gizmo and the blind dial are two; *"ie setting the cordinace"* is the hard one), **the gate telling you the next step in the world**, the **quest-line payouts at every step**, and the **stand-alone/dependency work**.

---

## Read these before touching anything

- **THE CASCADE IS TEN REFS.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. Count the branch you are on. `PUBLISHING.md`.
- **A CHECKER ENFORCES THE OPPOSITE OF THE STAND-ALONE DIRECTION.** `check-doc-conformance.py` reports *"declared dependencies : 294 (no living document may say there are none)"*. That rule must invert **in the same change** as the declaration.
- **BANNED VOCABULARY, and it caught six strings this batch.** *"portal"* is the thing this mod replaced — say **gate** or **connection**. *"doorway"* is reserved against **door** and **threshold**. `check-info-cards.py` is the authority.
- **A SOURCE-TEXT CLAIM MUST ASSERT THE CALL, NOT THE CALLEE — six instances in three sessions.** Every one was found by a plant reporting MISSED, never by reading.
- **NEVER SLICE SOURCE WITH `text[text.index(A):text.index(B)]` WITHOUT ASSERTING `B` IS AFTER `A`.** A marker moved above its partner, the slice came back empty, and `str.replace("", new)` inserted the replacement between **every character** — 154,124 copies of one method. `.local/qa/arrangements-fix.py` has the guard.
- **`git checkout -- <file>` DISCARDS SOMEBODY ELSE'S UNCOMMITTED WORK.** Six provenance rows were lost that way. Check `git status` first.
- **USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES.** A heredoc has mangled `\n` **thirteen** times here; this batch it put real newlines inside an XML keyed string and once ate a pair of comment delimiters.
- **MEASURE A NEW PASS AGAINST THE BUILD WITHOUT IT**, and note that `if (false)` **will not compile** — `CS0162` is an error here, so the probe silently links the previous DLL. Gate on something opaque (`depth > 100000`).
- **A MEASUREMENT THAT MEASURES NOTHING STILL PRINTS A NUMBER.** The density tool's first version harvested keyed strings with `re.S` and matched the outer `<LanguageData>` wrapper, so every count read zero and it reported the panel comfortably inside budget.
- **A WINDOW MUST DRAW INSIDE `RimroomsWindowState.Clean()`.** A leaked zero-alpha `GUI.color` from any of 294 mods renders a frameless window **completely invisible**.
- **EVERY ARCHETYPE MUST HOLD SOMETHING WORTH CARRYING OUT** (`proof-facilities.py`), **a new family id costs five artefacts** (the fifth is a `RoomContentBuilder` case whose `default` throws), and **`CoordinateMotif.Themes` is append-only**.
- **A ROW WHOSE OWN EVIDENCE SAYS *PARTLY* MUST NOT BE ARCHIVED.** The archiver will move a row that lies.
- **The mod register is GUIDANCE.** `python tools/register-query.py use <trace>`. **`docs/CAMPAIGN_CHART.md`** beats any prep document.

---

## Findings recorded so nobody re-derives them

- **The gate-enter path still cannot announce the generation freeze.** A pawn crossing is a job tick and `GateSpinUp` reaches `EnsureSite` from a tick too; a tick cannot queue a long event and carry on. Needs the `CompanyActionResult` chain deferred. The Operations pane works because a button callback returns nothing.
- **Our art cannot be drawn behind an in-play long event without Harmony.** `Root.OnGUI` skips the UI root while `ShouldWaitForEvent`. The answer was to own the surface — the generation notice is our own full-screen window.
- **A road braid is redundant at degree 5** — measured, deleted, and the reason is in the source.
- **At degree 5 a well-connected room cannot be moved at all**, because `PushAgainst` undoes any slide carrying a link past `FurthestLinkedCentres`. Arrangements must be formed *before* the later braids.

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
```

`STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0.

---

## Is it done?

**The build is. The play is not.** `0.12.85-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
