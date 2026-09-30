# Every coordinate in the game was made of wood — 0.12.37-dev

**Rows closed:** 1005 (material variety per coordinate), 1011 (inhabitant families tiered by depth
and wealth), 1101 (mineable materials and recoverable floors — the row closes completely), 922 (the
unknown-def-field checker, which is now the **twelfth**), 1055 (`disposition_stance()`). **Five
rows, one publish.**

No game was launched. Nothing here claims a gameplay, balance, performance or compatibility
result.

---

## 1. Row 1005 was worse than the row said

The row read *"material variety per coordinate — archetype fixtures take their default stuff
today."* The code read:

```csharp
ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.WoodLog : null);
```

Not the def's own default. **One hardcoded material.** Every table, chair, shelf, stool, lamp and
plant pot in every room of every coordinate any player will ever walk into was wooden, and would
have stayed wooden forever.

### A coordinate has a palette, not a material per item

Rolling a material per fixture would produce a jumble — a steel table beside a wooden chair beside
a granite stool, in one small room — which reads as noise rather than as a place. So a coordinate
gets a **short ordered palette** (three entries) and every fixture takes the first entry it can
actually be made of. One coordinate was fitted out in steel, another in wood, another in slate;
two coordinates look different from each other and each looks like somewhere.

### The load-bearing line is a sort

```csharp
DefDatabase<ThingDef>.AllDefsListForReading
    .Where(Usable)
    .OrderBy(definition => definition.defName, StringComparer.Ordinal)
```

`GenStuff.AllowedStuffsFor` and the def database return defs in **database order, which depends on
which mods are installed and in what order**. Indexing into that unsorted would mean:

* two players on the same seed with different mod lists see different materials, and
* a coordinate changes appearance when the player installs something unrelated.

A coordinate is regenerated from its seed and **two players must see the same thing** — the rule
that already governs `GateIncursion`'s candidate ordering and the between-visit displacement at
0.10.3-dev. Sorting by name makes the choice a function of the seed and the available material set
alone. The proof calls this out as the load-bearing line and a plant that removes it is caught.

There is also **no `Rand` call in the derivation at all**, even though the caller has pushed a
seeded state: a pure function of the seed cannot be perturbed by how many `Rand` calls happened
earlier in generation, and the room-content pass has changed shape once already.

### Existing content only, and nothing is named

Eligibility is `stuffProps.categories` plus Core's own `allowedInStuffGeneration` opt-out — Core
already marks the materials that should not appear in generated content, so no exclusion list of
ours is needed. **No material is named anywhere in the file**, so there is no list to fall out of
date; a mod that adds a stuffable material widens the palette without being known about, and a
mod that restricts one is obeyed. Our own defs are excluded by prefix, because a coordinate is
furnished out of the world's materials and not ours.

**Register:** `family materials` is one of the seven the retro sweep has not reached, so its rows
were read directly. **97 Gemstones** is *"optional resource/trade content… do not require gems or
reuse content"* — honoured exactly: a gem becomes fixture material only if Core's own
`AllowedStuffsFor` says it may, nothing requires it, and no gem is named. A profile with many
materials makes coordinates *more* varied, which is the intended direction.

---

## 2. Rows 1011 and 1101 were already built

**Row 1011 — inhabitant families tiered by depth and wealth, every variation seeded.**
`RimroomsInhabitantDef` already declares `minDepth`, `maxDepth`, `minBand` and `weight`;
`InhabitantService.Legal(depth, band, …)` filters on depth, and the band comes from
`CoordinatePressureLadder.BandFor(coordinate, wealth)` with `wealth = ColonyWealth()`. **Wealth
reaches it through the ladder, which is where it belongs** — there is one wealth rule in this mod
and it is not duplicated here. Selection is seeded from `Gen.HashCombineInt(coordinate.Seed, …)`,
which is the *"every variation seeded"* the row asks for. **Closed by proof.**

**Row 1101 — mineable materials and recoverable floors.** The mineable half shipped long ago:
`FillWithRock` places rock from `Find.World.NaturalRockTypesIn(map.Tile)`. The floors half needed
no code, and the reason is worth recording:

* A coordinate's floors are `Concrete` and `PavedTile`, both **Core** terrain.
* Both descend from Core's `FloorBase`, which sets `layerable: true`.
* `TerrainDef.Removable` **is** `layerable` — read from the decompiled class.

So Core's own floor-removal designator already works on a coordinate and returns the floor's
`costList` material. **The floors were never special.** And stripping one is safe: `SetTerrain`
refuses to file an impassable terrain as under-terrain, and the void floor is `WaterDeep`, which
is impassable — so Core substitutes the generator's own default rather than putting deep water
under a room. **Closed by proof.** The row asked for *"all of it"* and all of it is there.

---

## 3. Row 922 — the twelfth checker, and it caught itself twice

Row 922 records a checker for unknown def fields that was **written and removed rather than
shipped**, because every part verified in isolation and the assembled function reported nothing:
*"a checker that silently passes everything is worse than no checker: it manufactures
confidence."* It asks the next attempt to start from the verified parts.

`tools/check-def-fields.py` checks **direct children of every def node** — the level at which
"what fields does this type have" can be answered without a reflection host, and where the
historical defect was. The docstring says so rather than implying a depth it does not have.

Three sources of truth, and the third exists because the checker found a hole in the second:

| Source | What |
|---|---|
| our own def classes | parsed from `src/**/*.cs`, base chain walked, plus `Verse.Def`'s own fields |
| the game's own data | every direct child name RimWorld's defs of that type use, across `Data/*/Defs` |
| **the assembly** | the real fields on a game def class, decompiled and cached against the assembly's timestamp and size |

**It failed twice on itself before it was right, and both failures are in the same function.**

1. The first honest run reported **159 false positives**. The field parser rejected any line
   containing `(` — and `public List<string> buildingDefNames = new List<string>();` has a
   parenthesis in its *initialiser*. That threw away every collection field in the project. The
   original attempt reported nothing; this one reported everything; **same mistake, same
   function**. The declaration is now judged on the text before the first `=`.
2. With that fixed, one finding remained: `<canMakeRandomly>` on a `FactionDef` of ours. It is a
   **real field** — Core simply never writes it in XML because the default is what Core wants.
   **Learning field names from usage can only find the fields somebody happened to need.** Hence
   source 3, unioned with source 2.

The union is deliberately generous, because a false positive blocks a build over a real field
while the defect class being hunted is a *typo* — and a typo matches neither source.

**The guard row 922 actually asks for** is that the checker cannot report a pass having looked at
nothing: it exits **2** ("skipped, not passed") when the class parser is blinded, when the data
index is empty, or when it examined zero defs or zero fields. Two of the six fault plants blind it
and require exit 2.

**One plant was mine, not the checker's.** I tried to replant the historical `maxTechLevel` defect
and it passed — because 0.8.7-dev fixed that defect by **adding the field to the class** rather
than removing it from the XML, so `maxTechLevel` is valid now. Replanted as `minTechLevel`, the
same defect in the same place with a name the class genuinely does not have: caught.

---

## 4. Row 1055 — the stance classifier, fixed to the row's own prediction

`disposition_stance()` tested `"required" in lowered`, and a negator in front of the word does not
change that substring. Row 1055: *"**14 of the 17** 'Required' rows say the opposite… Only Harmony
(1), Core (4) and Vanilla Expanded Framework (14) are genuinely required, so **82% of that bucket
is wrong**."*

Negated occurrences are now skipped rather than negative phrases being listed and checked first —
a phrase list has to anticipate every way English negates something, and these dispositions take
104 distinct forms.

**My first fix gave four, not three**, and the extra was row 288 Prison Labor, whose disposition
contains *"Pawn.IsColonist **requires** Faction.IsPlayer"* — a sentence about **Core's source
code**, in a row whose actual claim is *"no Rimrooms dependency or adapter"*. Window-based negation
cannot tell those apart, because nothing is being negated. So the requirement question is asked of
the disposition's **own claim**, which is its first sentence; everything after it is evidence.

Row 1055 also names the `Unclassified` fallback: RimWorld Together, the co-op backbone, fell
through to it. **Measured: it and row 2 were the only two of 294**, and both describe a planned use
without asserting a requirement or an exclusion — which is what Optional means everywhere else in
this register. The fallback is now Optional and the bucket is empty. A row with no disposition at
all is still `Unrecorded`.

| | before | after |
|---|---|---|
| Required | 17 | **3** — exactly rows 1, 4, 14 as the row predicted |
| Unclassified | 2 | **0** |

The register HTML was regenerated so it agrees: 294 cards intact, `Unclassified` gone.

---

## 5. Files

**New:** `src/.../Generation/CoordinateMaterials.cs`, `tools/check-def-fields.py`,
`.local/register/proof-generation-batch.py`, this record.

**Edited:** `src/.../Generation/RoomContentBuilder.cs` (both placement helpers threaded with the
coordinate, 23 call sites), `tools/research/build-mod-register.py` (the stance classifier),
`outputs/.../Rimrooms_Async_Industries_294_Mod_Integration_Register.html` (regenerated),
`CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `docs/NOW.md`, `docs/TODO.md`,
`docs/FINALIZED.md`.

**No new gameplay content.** One C# file, one checker; no `ThingDef`, `TerrainDef`, `HediffDef`,
`ThoughtDef`, recipe, bench, item, texture or sound.

## 6. Verification

* **Build 0.12.37-dev** — 189 C# files, 87 package files, **0 warnings, 0 errors**.
* **Assembly reproduced across two clean rebuilds.**
* **TWELVE checkers pass. Thirty-four proofs exit zero.**
* **20 of 20 planted faults caught** — 14 against the generation batch, 6 against the new checker.
* **No game was launched.** Every statement here is structural.
