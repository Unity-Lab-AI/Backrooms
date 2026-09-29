# The yellow rooms were never carpeted — 0.12.19-dev, 2026-09-29

**Dated record.** Never rewritten. Corrects three verdicts in
`BACKLOG_AUDIT_IMPLEMENTATION.md` (0.12.14-dev).

---

## What I set out to build, and why I did not build it

The plan was *"the interior as a resource"* — three owner directions the 0.12.14-dev audit had
marked open:

> *"and areas minable and of all types of materisals throughout"*
> *"and capte ands tile can all be uninstalled , moved, resued , sold , studied"*
> *"all of it"*

**All three were already satisfied.** Verifying that instead of building on top of it is what found
a real bug.

---

## The bug: depth 1 has never been carpeted

`BackroomsPalette` asked for:

```csharp
floor = Named<TerrainDef>("Carpet"),
```

**There is no `TerrainDef` called `Carpet`.** Core ships a **`TerrainTemplateDef`** of that name,
and `TerrainDefGenerator_Carpet.CarpetFromBlueprint` generates one real terrain per structure
colour:

```csharp
string defName = tp.defName + colorDef.defName.Replace("Structure_", "");
```

So the real defs are `CarpetMustard`, `CarpetGreenFaded`, `CarpetUmberBurnt` and fifty-nine others.
The lookup went through `GetNamedSilentFail` — **silent by design** — returned null, and every
carpet band fell through to its `??` fallback. At depth 1 that fallback is `WoodPlankFloor`.

**Worn yellow carpet is the defining surface of the Backrooms, and invariant 25 calls depth 1
sacred.** It has been wood plank flooring in every game, on every seed, since the palette shipped.
No build error. No checker. No log line. And the fallback made the wrong floor look deliberate.

### The fix needed no new data

Every band already names its own floor colour — `Structure_Mustard` at depth 1,
`Structure_GreenFaded` for the offices band, `Structure_UmberBurnt` for the wrong band — and all
three generated defs exist.

A carpet **cannot** be tinted at runtime the way a wall can: the colour is baked into the generated
def. So the colour the band already named is exactly what picks the def. One helper, three call
sites.

---

## Three audit verdicts of mine, all wrong

### 1. The mineable rock was marked unbuilt. It ships.

`FillWithRock` and `NaturalRockTypesFor` have been in `GenStep_BackroomsDestination.cs` the whole
time, asking `Find.World.NaturalRockTypesIn(map.Tile)` — so the materials are **whatever that tile
actually has**, which satisfies *"of all types of materisals"* and keeps it Core-only on any
planet. Seeded per cell, so a coordinate looks the same on reload.

My audit grepped `Generation/` for *"Mineable"*, *"Granite"*, *"RockRubble"*. **The code contains
none of those words.** A grep for the words I expected, in the file I expected, is not a search.

### 2. I accused a comment of lying. It was telling the truth.

`BackroomsContainment.cs` says *"every solid area is mineable in a variety of materials"*. I
recorded that as a comment claiming something the code does not implement, and cited invariant 130.

**The implementation is in a different file.** I invoked the invariant while committing its
inverse — and condemning correct code on a failed search is **worse** than trusting a wrong
comment, because it marks working behaviour as broken and invites somebody to "fix" it.

### 3. The third row's premise was wrong

It asserted vanilla returns no materials for a lifted floor. It does:

```
TerrainGrid.RemoveTopLayer(IntVec3 c, bool doLeavings = true)
  -> GenLeaving.DoLeavingsFor(TerrainDef terrain, IntVec3 cell, Map map)
     -> terrain.CostListAdjusted() * terrain.resourcesFractionWhenDeconstructed
```

`BuildableDef.resourcesFractionWhenDeconstructed` defaults to **0.5f**. Every floor the palette
lays returns half its cost: carpet gives Cloth, wood gives WoodLog, tile gives Steel or Silver.

---

## So the proof is the deliverable

Nothing needed building. What was genuinely missing was **anything watching**, because the whole
behaviour depends on which terrains the palette picks — and Core ships `PackedDirt`,
`BrokenAsphalt` and stone tiles that override the fraction to **0** and return nothing.

`proof-interior-resource.py` asserts: the rock fill exists and reads the tile; the fill is
deterministic; rock is cleared where rooms are carved; **the palette never asks for a bare
`Carpet`**; every floor it lays resolves, cost something, and returns some of it; and walls and rock
are spawned **with no faction**, so they stay deconstructable and mineable (invariant 75).

---

## My first version of the key claim was blind

It skipped any terrain with no cost list, reasoning that natural terrain was never built and cannot
be lifted. That excused **precisely** the case it existed to catch: a plant swapping a floor for
`PackedDirt` **passed**.

**A filter that skips the case it guards against is worse than no check**, and **only the planted
fault found it** — reading it would not have. Rewritten to require both halves: it cost something,
and it returns some of that.

Two more claims failed on the first run, both mine:

- one searched for `RoofConstructed` and was broken by the two doc comments saying the roof is
  deliberately **not** `RoofConstructed` — a claim defeated by the code explaining itself, **sixth
  time** in this project;
- one asserted `SetFaction` never appears in generation. It appears **six times**, deliberately, on
  the player's own anchor, generator, climate unit, lights, conduit and doors — which is what makes
  them the player's to use. **My claim was backwards.** Both rekeyed off the spawn.

---

## The register, checked first, and it shaped the work

| Row | Mod | Stance | What it meant |
|---|---|---|---|
| **101** | Gold & Silver Ingots | **Required** | smelting recipes only, **no ore veins**; its review says do not require it for core progression, so mineable rock uses **Core** ore |
| **152** | Non uno Pinata | Settled | changes **corpse inventory and auto-strip**, not terrain drops — floor recovery is clear of it |
| **127** | Mine Sight | Optional | a mining **designation UI**, so real mineable rock simply appears in it |
| 144 / 221 / 52 | No Burn Metal / Stuff Mass Matters / BetterWeight | Optional | alter material **properties**, not placement |

---

## Fault-planted five ways

| Planted fault | Exit | Caught |
|---|---|---|
| a palette floor swapped for one worth nothing — **blind on the first attempt** | 1 | ✓ |
| **the original defect restaged** — a bare `Carpet` lookup | 1 | ✓ |
| a floor def that does not exist | 1 | ✓ |
| the mineable rock fill removed | 1 | ✓ |
| rock types hardcoded instead of read from the tile | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.19-dev |
| Build | 173 C# files, 91 package files, **0 warnings, 0 errors** |
| Player-visible defects fixed | **1** — depth 1 had never been carpeted |
| My audit verdicts corrected | **3** |
| Floors verified to resolve, cost and return | **9** |
| Checkers | **eight**, all passing |
| Proofs | **twenty**, all exiting zero |
| Planted faults caught | **5 of 5** |
| Game launched | **no** — the carpet is correct by def name and cost, and **nobody has seen it** |
