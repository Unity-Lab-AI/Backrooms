# Coherence decays, and what you find scales with you (0.8.7-dev)

**Baseline:** `26db789` (0.8.6-dev, 151 C# files, 91 package files).

**This checkpoint — 0.8.7-dev:** **152 C# source files** (one new), **91 approved package files** (unchanged). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `11D0FB47F37A78D58E7CD3A47E3C8A89D7B4769BAE731E675D6B6BC2C37B9A48`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request, and the correction in it

> *"hallways can have furniture and produiction benches too remember things are almost completely fucking werid and crazy odd and scary looking the deeping in the backrooms and higher the gete quality and rtesarch levels and tech and stuff ec t ect"*

The previous checkpoint named a gap: archetypes were not constrained by structural family, so *"a hallway can be furnished as a nursery"*.

**The owner's answer was that this is not a bug.** A production bench standing in a corridor is exactly right for the setting — **the wrongness is the content.**

So nothing was constrained. Instead **coherence decays.**

## Two inputs, and the second is the owner's own

| Input | What it represents |
|---|---|
| **Depth** | what the player chose to risk |
| **Branch advancement** — research finished, deepest reached | what the player earned |

Neither alone can max the place out: depth contributes at most 0.65, advancement at most 0.45. **The worst of it wants both.**

A shallow coordinate still honours an archetype's declared family. A deranged one ignores it entirely, rolled **per room** so some rooms in a deep space still read as ordinary — **a space where everything is wrong stops being unsettling and starts being noise. The contrast is what works.**

Anomalous archetypes also grow heavier with derangement until they outweigh the ordinary ones, because by then **the ordinary ones are the surprise.**

## What you find scales with what you can understand

*"higher the gete quality and rtesarch levels and tech and stuff"* — a pre-industrial branch finds pre-industrial things; one that has gone deep and researched widely starts turning up spacer equipment.

Never above the archetype's own declared ceiling, so a def that says it deals in industrial goods is still telling the truth. And a slot whose entire pool is above the branch's reach **falls back to the unfiltered pool**, because an empty room is a worse outcome than a slightly anachronistic one.

This also means **a deep space is worth coming back to later.** A coordinate visited early and revisited after a hundred hours of research is a different place, with nothing authored twice.

Read live rather than snapshotted — unlike the room-shape echo, which *had* to be snapshotted because layout is re-planned against a saved fingerprint. **Room contents are generated once and never re-derived**, so reading current state here cannot desynchronise anything.

## A real defect found and fixed

`maxTechLevel` was emitted in the archetype XML for **fourteen defs** while the C# class had no such field. RimWorld logs an unknown field and carries on, so it had been **failing silently at load since 0.7.9-dev** — the defs worked, the field did nothing, and nothing in the build or any checker noticed.

Wiring it as the tech-scaling ceiling both fixes the defect and turns dead data into the lever the owner asked for.

## A checker I wrote, proved broken, and removed rather than shipped

That defect should have been caught, so a check was written for it: every child element of one of our def types must be a real field on its class.

**It did not fire.** Every part of it was verified correct in isolation — the field parser reads all seven fields, the XML walk reaches the right node, the comparison flags the bad child — but the assembled function reported nothing against a deliberately planted bad field.

**It was removed rather than shipped.** A checker that silently passes everything is worse than no checker: it manufactures confidence. This is the same failure mode designed out of the layout derangement one checkpoint earlier, and shipping it here would have been hypocritical.

It is recorded in `TODO.md` as open, with what was already proven about it so the next attempt starts from the working parts.

## Not done, and named in `TODO.md`

- **The unknown-def-field checker**, above.
- **Facilities** — larger functional spaces as distinct from rooms and corridors.
- **A managed history of what laboratory gates have connected to**, which arrived during this checkpoint and is captured verbatim.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass.
- Compliance: **no new def of any kind**, no asset, no patch operation, no new work type.

## For the post-completion test phase

Confirming a shallow coordinate still reads as coherent; confirming a deep one mixes room kinds and that some rooms still read as ordinary; confirming a pre-industrial branch finds no spacer equipment and an advanced one does; confirming a deep coordinate revisited after heavy research contains better things than it did; confirming an archetype's declared tech ceiling is never exceeded; and confirming a slot with no affordable candidates still fills rather than leaving the room bare.
