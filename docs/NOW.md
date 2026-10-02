# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

So: **replace this file, never append to it.** It had grown to 3,053 lines and 238 KB carrying nine stacked `STATE AT THIS HANDOFF` records; all of it is archived in `FINALIZED.md`. Narrative about what a checkpoint found goes to `FINALIZED.md`. A rule that must survive goes to `.claude/CONSTRAINTS.md` or becomes a checker. Open work goes to `docs/TODO.md`. Nothing accumulates here.

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, every owner direction verbatim, **open work only** |
| `docs/DECOMPOSED.md` | smallest execution units, **open only** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

---

## State, measured 2026-10-02

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.80-dev** — read from `About.xml`, never from a document |
| Build | **211 C# files, 92 package files**, zero warnings, zero errors. Measure, never carry: `git ls-tree -r HEAD --name-only \| grep -c '^src/.*\.cs$'` and the `files` array in `tools/package-files.json` |
| Dependencies | **293 declared**, `loadAfter` 294 with Core first. Read from `About.xml` |
| Instruments | **16 checkers** (`tools/check-*.py`), **49 proofs** (`.local/register/proof-*.py`), **23 plant suites**. Run by **exit status**, never by grepping output — they end on five different phrasings and two end mid-sentence |
| Staged | **See below. This is the one blocking item.** |
| Launches | **At least twelve**, all by the owner. The ninth walked a Backrooms level. **Every defect any launch has found was ours — not one was a mod conflict** |

---

## THE ONE BLOCKING ITEM

**The package is not staged and could not be.** `stage-mod.ps1` refuses while RimWorld is running and the owner's session was live through this whole checkpoint. **It refused correctly — it will not stop a process.** The game folder holds **`0.12.78-dev`**; the build is **`0.12.80-dev`**, so the running game is two checkpoints behind and neither fix below is in it yet.

**First action once RimWorld is closed:**

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

It backs up the existing folder, hash-verifies every file against the build manifest, never touches the mod list and never starts the game. **Then cascade** — ten refs, see below.

---

## What 0.12.80-dev changed

**Architect has the far-left tab slot back.** Owner: *"i find my self trying to click archetic(which was in far left) but find my self out of habit click operations(because it took the archetect postioton)"*. `RR_MainButtons.xml` went `<order>0</order>` → `<order>5</order>`, so Core's own sort puts Architect at 1 and Operations immediately right of it. **No patch against a Core def** — that would fight every row of the Interface family at once. The proof now asserts **both** bounds (above Architect, below Work), because one bound passes a value that re-breaks the other end; three plants hold it, 57 of 57.

**The Store start grants 100 packaged survival meals instead of 24 simple ones.** It was the only scenario granting a simple meal, and **a simple meal spoils** — the start was handing over two dozen meals and quietly taking them back. Both defs were verified present in the installed game data before the swap rather than assumed.

---

## THE REAL BUG IS STILL OPEN, AND THE MEASUREMENT IS WHY NO FIX WAS WRITTEN

Owner: *"they need to properly spawn in with starting goods"*.

A **9,216-cell sweep** around the three colonists at (147, 151), through the bridge against the live process, found **none of the Store's consumable grants**: no `Silver` 200, no `WoodLog` 200, no `Cloth` 120, no `MealSimple` 24, no `MedicineHerbal` 8, no `Gun_Revolver`, and **6 `Steel` against 80**. Every shop **fixture** was present — 18 `Shelf`, 6 `Bed`, 3 `ElectricStove`, 12 `Table2x2c` — so the layout ran and the grants did not.

**The sweep reads shelf contents** (it reported `Steel`, `MedicineUltratech`, `Gun_ChargeRifle` inside shelf cells), so the absence is measured rather than a hole in the instrument.

**Do not read the loot as the start.** The one `MealSurvivalPack` on the ground and the one in each pawn's inventory are **Core's default pawn possession**. The `Gun_ChargeRifle` ×3, `MedicineUltratech`, `MechSerumYouth` and `Neurotrainer_Mining` are **ancient-danger loot**, beside `AncientCryptosleepCasket`, `AncientHermeticCrate`, `Sarcophagus` ×6 and `SteleLarge` ×12.

**Where to look first.** Prepare Carefully's equipment and the scenario grants reach the map through the **same** `ScenPart.PlayerStartingThings()` enumeration, which is why one break explains both halves of the original report. `ScenPart_RimroomsArrival` has **two silent `return` sites before it ever calls `base.GenerateIntoMap`** — the tile/`Current` guard at the top, and `if (receipt.arrivalStarted) { return; }`. Neither logs anything. The receipt-incomplete path *does* log and **no such error was in `Player.log`**, so that branch did not run.

**It needs a fresh start on a staged `0.12.80-dev` to measure against.** Rewriting the arrival path on a hunch is how three consecutive launches were lost to three different causes in the same method.

**Instrument:** `python .local/qa/scan-starting-goods.py <rimworld pid> [x0 z0 x1 z1]` → `.local/qa/live-goods-report.txt`.

---

## Read these before touching anything

- **The cascade is TEN refs, not eight.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. A publish that reads back eight has left the branch the work is on unpublished, silently. **Count the branch you are on.**
- **The bridge works.** `127.0.0.1:5174`, read via `.local/qa/bridge.py` or the allowlisted `tools/qa/rimbridge_readonly.py`. A previous session declared it dead while probing the wrong ports; check the log for `[RimBridge] GABP server running standalone on port` before claiming otherwise. Its Lua is a lowered DSL over other capabilities, **not** general Lua — it cannot reach `listerThings`, so reading the map means cell sweeps.
- **Use the Write tool for any script with escapes or apostrophes.** A bash heredoc has mangled `\n`, `\s` or a plain apostrophe **eleven times** here.
- **CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT.** Nine rows in one session turned out already built, already true, or answered by Core.
- **The mod register is GUIDANCE, not law.** Consult it, say what it said; a row never vetoes work. `python tools/register-query.py use <trace>`.
- **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document.
- **Tests are not the concern yet.** Unverifiable-without-a-launch is **never** a reason to defer building something.
- **Do not stop.** Chain checkpoints; batch related rows and publish once.

---

## The live bug that is NOT ours — nobody hunt it in our source

```
ReflectionTypeLoadException getting types in assembly RimBridgeServer:
expected class 'HarmonyLib.CodeInstruction' in assembly '0Harmony, Version=2.4.2.0'
```

`RimBridgeServer.dll` wants **0Harmony 2.4.2.0**; `brrainz.harmony` ships **2.4.1.0**. **Harmony loads at position 5 and the bridge at 198, so it is not ordering.** Our package loaded clean in the same log: zero Rimrooms errors, zero cross-reference errors. The fix is on the machine. (Note: the GABP standalone server on 5174 **is** running and answering regardless.)

---

## The queue

```
grep -c '^\s*- \[ \]' docs/TODO.md     # open
grep -c '^\s*- \[~\]' docs/TODO.md    # partial
grep -c '^\s*- \[T\]' docs/TODO.md    # post-completion test phase
grep -c '^\s*- \[x\]' docs/TODO.md    # 0, and it must stay 0
```

**`docs/TODO.md` went from 493.8 KB to ~79 KB and `docs/DECOMPOSED.md` from 30.6 KB to 4.1 KB** by owner direction: *"the todods sahll never hold completed items"*. Three things came out, and the last two a row count cannot see: 727 `[x]` rows; nine `##` sections titled as dated checkpoint records (their 38 open rows carried forward into Pending); and **finished work written inside open rows** — one `[~]` row was 3,796 characters, ~3,000 of them six completed build passes.

**Archive at the end of every batch that closes rows**, not at a milestone:

```
python .local/qa/archive-finished-todo.py --apply
python .local/qa/archive-finished-todo.py --queue docs/DECOMPOSED.md --apply
python .local/qa/verify-archive-move.py
```

The mover **never rewrites a line**: it labels every line index KEEP or MOVE and asserts reassembly reproduces the original **byte for byte**, writes the archive **first**, confirms every moved line present, and only then rewrites the queue. LAW: `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`.

---

## Three things in the queue that need a human, first

1. **Two sections titled DONE carry twenty-two unticked `[ ]` rows** — *The first walked level* and *Lights and geometry*, both 0.12.61-dev, under *Open rows carried out of the play-testing checkpoints*. **The title is not the marker.** Read them and tick what is actually done.
2. **The adapter-families row contradicts the surgery row.** It says *"Surgery across a gate is the named remainder"*; the surgery row closed at 0.12.33-dev finding Core **forbids** it. If that closure stands, the adapter row is `[x]`. Flagged, not flipped.
3. **The workbook row contradicts the retro-sweep row.** One says 14 of 21 register families swept with 7 to go; the other closed at 0.12.42-dev saying all twenty-one are done.

---

## Is it done?

**The build is. The play is not.** Re-staging and a launch is the only work that unblocks anything, and `python tools/check-planner-layouts.py` (checker 14, which runs the planner for real) goes first.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`. One launch's log had hundreds of red lines all downstream of the first; another had none and the answer was in a letter.
