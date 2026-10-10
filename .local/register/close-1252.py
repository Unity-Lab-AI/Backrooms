# -*- coding: utf-8 -*-
"""0.12.52-dev closure: every type of material, and level 0 stays yellow."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Every type of material, and level 0 stays yellow — 2026-09-30 (0.12.52-dev)

- [x] **"with the wild variatiosn of material typeds in all items equaipment walls floors lights furnature and benches that are found everywher deeper in"** — **DONE, after one round of getting it wrong.**

  **What was already right and needed nothing.** `CoordinateMaterials` already derived its choice from the coordinate's seed, sorted by defName so a mod list cannot change a coordinate's appearance, drawn from `GenStuff.AllowedStuffsFor` so any material the profile adds widens it and any it restricts is obeyed, with no material named anywhere. `RoomArchetypeService` already gates **which** defs appear by depth. The variety of *things* already grew inward.

  **Three gaps, all the same shape — a material chosen somewhere the palette could not reach.** The palette was a flat 3 at every depth. `TryPlace` — the path that places the depth-scaled archetype dressing, which is the benches, equipment and loot the owner means — used `GenStuff.DefaultStuffFor` and never consulted the palette at all, so the content that was meant to vary was the one content that could not. And walls were **one of two named defs**, `WoodLog` or `Steel`, across five bands.

- [x] **"this is wrong we want every type of wall and material for all things randomly"** and **"but depth 0 in the backrroms is the standard yellow style"** and **"ive already lkayed this out"** — **CORRECTED. The owner had laid it out, in their own words, already quoted inside `BackroomsPalette`:** *"yellow carpet and yellow wood walls for the main backrooms look"* followed immediately by *"andf remmebr thats just the main backrooms looks further in it gets very varied and weird"*.

  The first fix grew the palette with depth, from 2 to 6. **That was still wrong, because a growing palette is still a palette:** every fixture takes the first entry it can use, so a deep level still reads as *fitted out in three materials* and a table and a wall in one place tend to match. The palette's own doc argued **for** that, calling per-item choice *"a jumble ... which reads as noise rather than as a place"* — **that argument was mine, and for the deep bands the owner is right: "very varied and weird" is the brief, and coherence is the thing being left behind as you go inward.**

  So the behaviour is a **split**, which is the specification:

  | | |
  |---|---|
  | **Level 0** (`CoherentDepth`) | one narrow shared palette — the standard yellow style, monotonous on purpose, yellow wood walls |
  | **Deeper** | **no palette at all.** Every fixture draws from **the full set Core allows for its own def**, indexed per fixture, so two tables in one room can be different woods, different metals, or one of each |

  Walls are chosen **per room** deeper in — not per cell, because a wall whose every cell is a different stone is a patchwork rather than a wall, and `BuildRoomWalls` places one room's ring at a time so the room is the unit the geometry already has.

  Still deterministic: a pure function of the coordinate's seed and id, the def's name and the fixture's variant, **no `Rand` call**, and the candidate list **sorted by defName** before anything indexes into it — because `AllowedStuffsFor` returns database order, which depends on the installed mod list. Still existing-content-only: Core's own `allowedInStuffGeneration` opt-out is honoured on the wild path too, and **nothing names a material**.

  **`ColonistEcho.CopyApparel` was deliberately not changed.** It copies one of the player's own colonists, so the source pawn's material is the right one and `DefaultStuffFor` there is only a fallback for a piece that had none. An echo should mirror the colonist, not the coordinate.

  **Register rows read first, per LAW:** family `materials` — **[221] Stuff Mass Matters** and **[52] BetterWeight** (mass scales with stuff, so a wider material set changes hauling weight, which is native behaviour and correct), **[101] Gold & Silver Ingots** and **[144] No Burn Metal** (add or alter stuff defs, picked up automatically because nothing is named), **[53] Big Little Mod Patch** (furniture/workbench bundle). A profile that adds materials makes coordinates **more** varied, which is the intended direction.

  Record `implementation/WILD_MATERIALS_IMPLEMENTATION.md`. **43 of 43** planted faults caught.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - every type of material, and level 0 stays yellow (0.12.52-dev)

**Verbatim user quote:** *"get to it"*

**Verbatim user quote:** *"this is wrong we want every type of wall and material for all things
randomly : WALLS GO BACK TO ONE OF TWO NAMED MATERIALS"*

**Verbatim user quote:** *"but depth 0 in the backrroms is the standard yellow style"*

**Verbatim user quote:** *"ive already lkayed this out"*

**Files touched:** `Generation/CoordinateMaterials.cs`, `Generation/RoomContentBuilder.cs`,
`Generation/GenStep_BackroomsDestination.cs`, About/csproj/README,
`docs/implementation/WILD_MATERIALS_IMPLEMENTATION.md`, `docs/TODO.md`, `docs/NOW.md`.

**Closure notes.** **The owner corrected me once and they were right both halves of the way.**

The line they quoted back - *"WALLS GO BACK TO ONE OF TWO NAMED MATERIALS"* - was a **plant
label**, the name of a fault deliberately planted to prove the proof catches it, not a statement
of shipped behaviour. Worth recording because a plant label reads exactly like a bug report.

**The substantive correction was real and I had it too narrow.** The first pass grew the
per-coordinate palette with depth, 2 to 6. A growing palette is still a palette: every fixture
takes the first entry it can use, so a deep level still reads as *fitted out in three materials*.
The palette's own doc argued FOR that and called per-item choice a jumble - **that argument was
mine**, and for the deep bands the owner is right, because *"very varied and weird"* is the brief
and coherence is what is being left behind as you go inward.

**And they had already laid it out**, which is why *"ive already lkayed this out"* was the right
thing to say to me: their two sentences from 2026-09-29 are quoted inside `BackroomsPalette`
already - *"yellow carpet and yellow wood walls for the main backrooms look"* and *"further in it
gets very varied and weird"*. The specification was in the codebase, in their words, and I built a
compromise instead of reading it.

So: **level 0 shares one narrow palette** and stays the standard yellow style; **deeper, every
thing draws from the full set Core allows for its own def**, indexed per fixture, so two tables in
one room can differ. Walls are per ROOM deeper in rather than per cell, because a wall whose every
cell is a different stone is a patchwork and `BuildRoomWalls` already works a room at a time.

**Three gaps were closed in the first pass and all three were the same shape** - a material chosen
somewhere the palette could not reach: a flat palette size, the depth-scaled dressing path using
`GenStuff.DefaultStuffFor` and never consulting the palette at all, and walls as one of two named
defs across five bands.

**Deliberately unchanged:** `ColonistEcho.CopyApparel`, which copies one of the player's own
colonists - the source pawn's material is the right one there, and an echo should mirror the
colonist rather than the coordinate.

**Six proof claims objected correctly across two passes**, every one of them encoding a previous
decision rather than a property: `PaletteSize = 3`, then the grown palette, then four whose exact
strings moved. And **three plants found loose claims**: a `CoherentDepth` with no upper bound
passed 99, the variant never had to reach the hash key, and a 16-space anchor was a substring of a
20-space one so the harness refused to run rather than mis-score. The duplicate-string trap, twice
in one checkpoint.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`9D7DCDAF2FFA06C740F800437458571351511B56DDBDC1123463886B46ED7DF4`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** **43 of 43** planted faults caught.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("material rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.51-dev**.", u"| Published | **0.12.52-dev**."),
    (u"SHA-256 `378493F20F4B7CD8BB932608073434CC00315C00EE94567C50FE995CCADF1A79`",
     u"SHA-256 `9D7DCDAF2FFA06C740F800437458571351511B56DDBDC1123463886B46ED7DF4`"),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.52-dev")
