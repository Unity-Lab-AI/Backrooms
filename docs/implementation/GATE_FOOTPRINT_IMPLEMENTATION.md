# A gate has a size (0.9.2-dev)

**Baseline:** `1c9c91b` (0.9.1-dev, 155 C# files, 79 package files).

**This checkpoint — 0.9.2-dev:** **156 C# source files** (one new), **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `0A2B527ED14475D56428DD2E63A0970853D5C70A854D4BB3516E4D9831FBE001`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"and rember ther are 1x1 1x2 and 1x3 and 2x3 gate doors that allow differnt capabilities as to the universe and scerios needs"*

## What the installed game data actually said

The plan going in assumed Core ships only 1×1 doors, so every wider gate would have to be built from a run of adjacent doors.

**Reading the installed data instead of trusting that changed the design.** RimWorld 1.6 ships `Building_MultiTileDoor`, and two defs use it:

| Def | Size | Source |
|---|---|---|
| `OrnateDoor` | 2×1 | **Core** |
| `SecurityDoor` | 2×1 | Anomaly |

`Building_MultiTileDoor : Building_SupportedDoor : Building_Door`, confirmed by decompiling rather than assumed.

**So a 1×2 gate needs no mods at all.** Enumerating Doors Expanded's installed copy then produced the rest — `PH_DoorDouble` and `PH_AutodoorDouble` at 2×1, `PH_DoorTriple` and `PH_AutodoorTriple` at 3×1, and `PH_DoorThickBlastDoor` at **3×2**, which is exactly the 2×3 the owner named. The four sizes in the direction line up one-for-one with a real lineup of doors that already exists.

This is invariant #19 earning its place again: *never trust a remembered list against shipped game data — enumerate.*

## Two numbers, deliberately not one

- **`GateWidth`** — how many cells wide the *opening* is, on the face people walk through.
- **`GateCellCount`** — the whole footprint.

A 2×3 blast door is **three wide but six cells of machine**. Keeping them apart is why a thick door costs more to run without letting anything bigger through than a thin door of the same width, which is the honest result rather than the convenient one.

## Throughput is not capped, and that is the point

> *"2 should really limit numbers through at once because in vinilla any number of pawns can use a door at once so we dont want limitations"*

A wide gate gets **no permit quota**. There is no counter anywhere in the new file, deliberately. What a wide gate gets is **more doorway cells**, and ordinary pathfinding spreads people across them exactly as it does across any wide vanilla door.

Checked before building: `OrderCrossing` only ever refused *the same pawn twice*, never a second pawn. The existing behaviour was already vanilla-equivalent, so the correct action was to **add nothing** — widening the physical opening is the whole mechanism.

## The component is the allowlist

`NativeDoorProvider()` used to name Core `Door` and `Autodoor` explicitly. It no longer needs to: the component is only ever attached by this mod's own patches, so **carrying the component is the allowlist** and the patch file is where supported providers are declared. What is still checked in code is the *shape*, because the capability ladder is defined for four footprints and nothing else.

## Costs more to run

Opening draw and spin-up work both scale on **cell count**, not width: a bigger gate is more machine to energise. The owner made *"costs more to run"* a condition of the larger sizes rather than a side effect, which is what keeps a 2×3 something a branch works toward.

A 2×3 draws six times a 1×1 — more than a geothermal generator — so it is a real installation with a real power plan behind it.

## Cannot be resized while working

> *"gate doors expansions can NOT be done on a working gate"*

Binding and unbinding already refused while a gate was open or had an unresolved trip. **A ramp is the gate working too**, so spinning up now blocks a rebind by the same rule.

## A checker gap, closed narrowly

Patching Doors Expanded's defs made `check-package-integrity.py` fail seven targets that "exist neither in the game's Data nor in this package" — **correctly**, because it had no concept of optional compatibility.

A target inside a `PatchOperationFindMod` is optional *by construction*: the operation applies nothing when that mod is absent. The check now exempts exactly those, and **still reports them as notes** — an optional target renamed by the other mod is a real compatibility break, it is just not a reason to refuse the package.

**The exemption was proved narrow by breaking it**: a bogus target planted *outside* `FindMod` still fails loudly. An exemption that leaked would be worse than no check.

## Not done, and named in `TODO.md`

- **What a size lets through.** Body-size limits at `PortalTraversalPolicy` — *"to fit vehicals and the like and bigger creatures"*. Its own checkpoint, because it belongs at the traversal chokepoint and deserves a diff that says only that.
- **Hostiles needing width** to follow a pawn through, which depends on the incursion work.
- **The adjacent-door-run fallback**, for reaching 1×3 and 2×3 without Doors Expanded.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. The new patch XML parses, and the `--` rule caught it once first.
- Compliance: **no new gameplay def, asset or work type.** One new source file, one keyed string, patches only.

## For the post-completion test phase

Confirming an `OrnateDoor` can be designated and reports a two-wide opening; that a 1×1 door still reports one; that the draw and spin-up of a wide gate are visibly higher; that a gate refuses to rebind while ramping; that installing or removing Doors Expanded changes nothing for a player not using it; and that a Doors Expanded triple or blast door designates correctly for a player who is.
