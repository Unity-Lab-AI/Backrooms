# -*- coding: utf-8 -*-
"""Ledger, queue and NOW.md for 0.12.37-dev. Five rows in one batch."""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


sub("CHANGELOG.md", u"## 0.12.36-dev", u"""## 0.12.37-dev - 2026-09-29 - every coordinate in the game was made of wood

- **Spaces are furnished out of different materials now.** Every table, chair, shelf and lamp in every room of every coordinate was wooden - one hardcoded material, not the item's own default. A space now has a short palette of its own drawn from whatever materials your game has, so two spaces look different and each looks like somewhere that was fitted out.
- **The same space always looks the same**, on any machine and whatever else you have installed. That was not free and it is the fiddliest part of the change.
- **Confirmed rather than changed: you can strip a coordinate's floors and get the material back.** They were always ordinary floors; nothing about them was special. The same goes for the rock - it comes from the world's own stone types.
- **Confirmed rather than changed: what lives in a space already scales with how deep it is and how rich you are.**
- **A new build check refuses a setting the game would silently ignore.** A mistyped field name in mod data is not an error in RimWorld - it is logged and skipped - and one had been quietly doing nothing for fourteen definitions until it was caught by hand.

Full record: [every coordinate in the game was made of wood](docs/implementation/GENERATION_MATERIALS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.36-dev""")

sub("docs/FINALIZED.md", u"## Completed sessions", u"""## Session 2026-09-29 - every coordinate in the game was made of wood (0.12.37-dev)

**Verbatim user quote:** *"okay keep it up we are trying to effectively and optimully finish the work in full and completely"*

### What shipped

**Five rows in one batch.** 1005 built, 1011 and 1101 closed by proof, 922 built as the twelfth checker, 1055 fixed.

### Files touched

`src/.../Generation/CoordinateMaterials.cs` **new**, `tools/check-def-fields.py` **new**, `src/.../Generation/RoomContentBuilder.cs`, `tools/research/build-mod-register.py`, the register HTML (regenerated), `.local/register/proof-generation-batch.py` **new**, `docs/implementation/GENERATION_MATERIALS_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **ROW 1005 WAS WORSE THAN THE ROW SAID.** It read *"archetype fixtures take their default stuff today"*. The code read `ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.WoodLog : null)` -- **not the def's default, one hardcoded material.** Every table, chair, shelf, stool, lamp and plant pot in every room of every coordinate any player will ever walk into was wooden, and would have stayed wooden forever.
- **A COORDINATE GETS A PALETTE, NOT A MATERIAL PER ITEM**, and the distinction is the design. Rolling per fixture gives a steel table beside a wooden chair beside a granite stool in one small room, which reads as noise. Three entries per coordinate, each fixture takes the first it can be made of, so a coordinate reads as somewhere that was fitted out and two coordinates differ.
- **THE LOAD-BEARING LINE IS A SORT, and it is the fiddliest part of the change.** `DefDatabase` and `GenStuff.AllowedStuffsFor` return defs in **database order, which depends on which mods are installed and in what order.** Indexing that unsorted means two players on the same seed with different mod lists see different materials, and a coordinate changes appearance when the player installs something unrelated. Sorted by `defName` with an ordinal comparer, the choice is a function of the seed and the available material set alone. The proof names it as load-bearing and a plant that removes it is caught.
- **No `Rand` call in the derivation at all**, even though the caller has pushed a seeded state: a pure function of the seed cannot be perturbed by how many `Rand` calls ran earlier in generation, and the room-content pass has changed shape once already.
- **Nothing names a material.** Eligibility is `stuffProps.categories` plus Core's own `allowedInStuffGeneration` opt-out -- Core already marks what should not appear in generated content, so no exclusion list of ours exists. A mod that adds a stuffable material widens the palette without being known about; **97 Gemstones** is honoured exactly (*"do not require gems or reuse content"*) because a gem is eligible only if Core says so and no gem is named.
- **ROWS 1011 AND 1101 WERE ALREADY BUILT.** 1011: `RimroomsInhabitantDef` already declares `minDepth`/`maxDepth`/`minBand`/`weight`, `Legal()` filters on depth, and **wealth reaches it through the ladder** -- `BandFor(coordinate, ColonyWealth())` -- which is where the one wealth rule in this mod lives and is not duplicated. Seeded from `Gen.HashCombineInt(coordinate.Seed, ...)`, which is the *"every variation seeded"* the row asks for.
- **1101's floors half needed no code, and the reason is the good part.** A coordinate's floors are Core's `Concrete` and `PavedTile`; both descend from Core's `FloorBase` which sets `layerable: true`; and **`TerrainDef.Removable` IS `layerable`**, read from the decompiled class. So Core's own floor-removal designator already works there and returns the `costList` material. **The floors were never special.** And stripping one is safe: `SetTerrain` refuses to file an impassable terrain as under-terrain, and the void floor is `WaterDeep`, which is impassable -- so Core substitutes the generator's default rather than putting deep water under a room.
- **ROW 922 BUILT AS THE TWELFTH CHECKER, AND IT CAUGHT ITSELF TWICE.** Row 922's own words: *"a checker that silently passes everything is worse than no checker: it manufactures confidence."* (1) The first honest run reported **159 false positives** -- the field parser rejected any line containing `(`, and `public List<string> buildingDefNames = new List<string>();` has one in its **initialiser**, so it threw away every collection field in the project. The original attempt reported nothing, this one reported everything: **same mistake, same function.** (2) With that fixed, one finding remained -- `<canMakeRandomly>` on a FactionDef -- and it is a **real field** Core simply never writes, because the default is what Core wants. **Learning field names from usage can only find the fields somebody happened to need.** So the assembly is decompiled and cached as a third source, unioned with the data index. The union is deliberately generous because a false positive blocks a build over a real field while the defect hunted is a typo, which matches neither source. **The guard the row actually asks for** is exit **2** -- skipped, not passed -- when the parser is blinded, the index is empty, or zero defs were examined; two of six plants test exactly that.
- **ONE PLANT WAS MINE AGAIN.** I replanted the historical `maxTechLevel` defect and it passed -- because 0.8.7-dev fixed it by **adding the field to the class**, not removing it from the XML, so `maxTechLevel` is valid now. Replanted as `minTechLevel`: caught. **Sixth time this session my measurement was the defect and the code was fine.**
- **ROW 1055 FIXED TO THE ROW'S OWN PREDICTION.** `disposition_stance()` tested `"required" in lowered`, and a negator in front of the word does not change that substring. Negated occurrences are now skipped rather than negative phrases being listed, because a phrase list must anticipate every way English negates something across 104 distinct forms. **My first fix gave four, not the predicted three**: row 288 Prison Labor contains *"Pawn.IsColonist requires Faction.IsPlayer"* -- a sentence about **Core's source code** in a row whose claim is *"no Rimrooms dependency"*. Window negation cannot tell those apart because nothing is being negated, so the question is asked of the disposition's **own claim**, its first sentence. Result: **Required 17 -> 3, exactly rows 1, 4 and 14.** The row also named the `Unclassified` fallback; measured, RimWorld Together and row 2 were the **only two of 294** and both describe a planned use without asserting a requirement, which is what Optional means everywhere else, so **Unclassified 2 -> 0**. Register HTML regenerated, 294 cards intact.
- Build 0.12.37-dev, **189 C# files, 87 package files**, **0 warnings, 0 errors**, assembly identical across two clean rebuilds. **TWELVE** checkers pass, **thirty-four** proofs exit zero, **20 of 20** planted faults caught. **No game was launched.**

---

## Completed sessions""")

sub("README.md", u"**Current development version: 0.12.36-dev.**",
    u"**Current development version: 0.12.37-dev.**")

# ------------------------------------------------------------------ the queue
TODO = os.path.join(REPO, "docs", "TODO.md")
t = io.open(TODO, encoding="utf-8").read()


def tsub(old, new):
    global t
    assert old in t, "todo anchor missing: %r" % old[:90]
    assert t.count(old) == 1, "todo anchor not unique: %r" % old[:90]
    t = t.replace(old, new, 1)


tsub(u"- [ ] **An unknown-def-field checker, written and then removed rather than shipped.**",
     u"- [x] **An unknown-def-field checker, written and then removed rather than shipped.** — "
     u"**BUILT 0.12.37-dev as `tools/check-def-fields.py`, the twelfth checker**, starting from "
     u"the verified parts as this row asked. Three sources: our own C# classes with the base "
     u"chain walked, the names the game's own defs of each type use, and **the real fields "
     u"decompiled from the assembly and cached** -- the third because the second has a hole the "
     u"checker itself found: `canMakeRandomly` on a FactionDef is a real field Core never writes. "
     u"**It caught itself twice.** First run: **159 false positives**, because the field parser "
     u"rejected any line containing `(` and every collection field has one in its initialiser -- "
     u"the original attempt reported nothing and this one reported everything, **same mistake, "
     u"same function**. **The guard this row asks for is exit 2**, skipped rather than passed, "
     u"when it has looked at nothing; two of six fault plants test it. Record "
     u"`implementation/GENERATION_MATERIALS_IMPLEMENTATION.md`. Was: ")

tsub(u"- [ ] **Consequence: fix `disposition_stance()` in the register generator.**",
     u"- [x] **Consequence: fix `disposition_stance()` in the register generator.** — **FIXED "
     u"0.12.37-dev, to this row's own prediction: Required 17 → 3, exactly rows 1, 4 and 14.** "
     u"Negated occurrences are skipped rather than negative phrases being listed, because a "
     u"phrase list must anticipate every way English negates something across 104 forms. **The "
     u"first attempt gave four**: row 288 contains *\"Pawn.IsColonist requires Faction.IsPlayer\"*, "
     u"a sentence about **Core's source code** in a row whose claim is *\"no Rimrooms "
     u"dependency\"* -- window negation cannot tell those apart because nothing is being negated, "
     u"so the question is asked of the disposition's **own claim**, its first sentence. Row 196 "
     u"is fixed too: measured, it and row 2 were the **only two** falling through to "
     u"`Unclassified` of 294, and both describe a planned use without asserting a requirement, "
     u"which is what Optional means everywhere else -- so **Unclassified 2 → 0**. Register HTML "
     u"regenerated, 294 cards intact. Was: ")

io.open(TODO, "w", encoding="utf-8", newline="").write(t)
print("queue rows 922 and 1055 closed")
