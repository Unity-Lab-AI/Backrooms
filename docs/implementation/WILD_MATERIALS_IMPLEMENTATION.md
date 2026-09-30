# Every type of material, and level 0 stays yellow — 0.12.52-dev

## The direction, verbatim

> *"with the wild variatiosn of material typeds in all items equaipment walls floors lights
> furnature and benches that are found everywher deeper in with wild random events and layouts and
> spawns to find and loot!!!!!!"*

and the correction, when the first attempt was too narrow:

> *"this is wrong we want every type of wall and material for all things randomly"*

> *"but depth 0 in the backrroms is the standard yellow style"*

> *"ive already lkayed this out"*

## They had already laid it out, and it was in the codebase in their own words

`BackroomsPalette` quotes them from 2026-09-29:

> *"we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main
> backrooms look"*
>
> *"andf remmebr thats just the main backrooms looks further in it gets very varied and weird"*

**That is the whole specification and it was already written down.** The right response to *"ive
already lkayed this out"* is that the layout existed, it was quoted in the source, and a compromise
was built instead of reading it.

## The register, first, per LAW

`register-query.py family materials`:

| Row | Relevance |
|---|---|
| **[221] Stuff Mass Matters** | mass scales with stuff, so a wider material set changes hauling weight — native behaviour, and correct |
| **[52] BetterWeight** | same family, same conclusion |
| **[101] Gold & Silver Ingots** | adds stuff defs, picked up automatically because nothing is named |
| **[144] No Burn Metal** | alters stuff behaviour, obeyed for the same reason |
| **[53] Big Little Mod Patch** | furniture/workbench bundle; widens what is stuffable |

**A profile that adds materials makes coordinates *more* varied, not less**, because everything is
drawn from whatever Core says is allowed. That is the intended direction and it needs no adapter.

## What was already right and needed nothing

`CoordinateMaterials` already:

- derived its choice from the coordinate's **seed**, so a regenerated coordinate is the same place;
- **sorted candidates by defName** before indexing — the load-bearing line, because
  `AllowedStuffsFor` returns database order, which depends on which mods are installed and in what
  order;
- drew from `GenStuff.AllowedStuffsFor`, so a mod adding a material widens it and a mod restricting
  one is obeyed;
- **named no material anywhere**;
- made **no `Rand` call**.

And `RoomArchetypeService` already gated **which defs** appear by depth — `minDepth`, `maxDepth`, a
tech ceiling, an anomalous weight factor. **The variety of things already grew inward.** None of
that needed touching, and saying so is part of the work.

## Three gaps, all the same shape

A material chosen somewhere the palette could not reach.

1. **The palette never grew.** `PaletteSize` was a flat `3` at every depth — the whole of *"wild
   variatiosn ... deeper in"*, sitting as a `const int`.
2. **The dressing path never consulted the palette at all.** `TryPlace` used
   `GenStuff.DefaultStuffFor`, and `TryPlace` is the path that places the depth-scaled archetype
   dressing — the benches, the equipment, the loot. **The content that was supposed to vary was the
   one content that could not.**
3. **Walls were one of two named defs.** `BackroomsPalette` sets `wallStuff` to `WoodLog` or `Steel`
   across five bands: a hard-coded pair where every other material in the place is drawn from what
   the profile offers.

## The first fix was still wrong, and the owner said so

Growing the palette with depth — 2 to 6 — closed the gaps but missed the point. **A growing palette
is still a palette.** Every fixture takes the first entry it can use, so a deep level still reads as
*fitted out in three materials*, and a table and a wall in one place tend to match.

The palette's own doc argued **for** exactly that, calling per-item choice *"a jumble ... which reads
as noise rather than as a place."* **That argument was mine, and for the deep bands it is wrong:**
*"very varied and weird"* is the brief, and coherence is the thing being left behind as you travel
inward.

## The behaviour, which is a split

| | |
|---|---|
| **Level 0** — `CoherentDepth` | one narrow shared palette. Monotonous on purpose: the standard yellow style, yellow wood walls, and a level where the table, the shelf and the walls match is what makes the yellow rooms read as a **place** |
| **Deeper** | **no palette at all.** Every fixture draws from **the full set Core allows for its own def**, indexed by its own variant — so two tables in one room can be different woods, different metals, or one of each |

**Walls are chosen per ROOM deeper in**, not per cell. A wall whose every cell is a different stone
is a patchwork rather than a wall, and `BuildRoomWalls` places one room's ring at a time, so the room
is the unit the geometry already has. At level 0 every room takes the band's wood, unchanged.

**The variant is what makes it per fixture.** Built from the placement seed and the slot, both
already deterministic per coordinate. Both placement helpers pass it, and the proof **counts both** —
because one of them not passing it would silently return the whole level to one material per place.

Everything that made the old path safe is kept on the new one: `StableHash` from the coordinate's
seed and id plus the def's name plus the variant, **no `Rand`**, **sorted by defName**, Core's own
`allowedInStuffGeneration` opt-out honoured, **no material named**, and a def Core allows nothing for
falls through to the palette and then to Core's default — because a generation pass must never fail
over a furnishing choice.

## Deliberately unchanged

**`ColonistEcho.CopyApparel`.** It copies one of the player's **own** colonists, so the source pawn's
material is the right one and `DefaultStuffFor` there is only a fallback for a piece that had none.
An echo should mirror the colonist, not the coordinate.

## The proofs, and what objected

**Six claims objected correctly across the two passes, and every one encoded a previous decision
rather than a property worth protecting:** `PaletteSize = 3`; then the grown palette; then four more
whose exact strings moved when the signatures changed. That is the proofs doing their job twice in
one checkpoint, including against the fix for the thing they caught the first time.

**Three plants found loose claims of mine:**

- `CoherentDepth` had a lower bound but no upper one, so a planted `99` — which would make the whole
  Backrooms coherent — passed. Bounded to `1..2` now.
- **nothing asserted that the variant reached the hash key.** Deleting `+ ":" + variant` left the
  derivation per-def rather than per-fixture, which is the entire feature, and every other claim in
  the section still passed.
- a 16-space anchor was a substring of the 20-space one in `TryPlace`, so it matched twice and **the
  harness refused to run rather than score a fault it never planted** — twice in this checkpoint,
  and the same trap as last checkpoint.

`plant-generation.py` is **43 of 43**.

## Build

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`9D7DCDAF2FFA06C740F800437458571351511B56DDBDC1123463886B46ED7DF4`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.**

## What a launch should settle

- **level 0 is the yellow rooms**: wood walls, yellow carpet, coherent, everything matching
- **one level in** the materials go wild: two tables in one room in different stuffs, and each room's
  walls a different material
- a profile material this mod has never heard of turns up in a deep room, because nothing is named
- reloading a save gives the **same** materials, because none of it is a `Rand` roll
