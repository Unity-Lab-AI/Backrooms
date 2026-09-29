# One kind of gate (0.9.1-dev)

**Baseline:** `ffe391e` (0.9.0-dev, 155 C# files, 79 package files).

**This checkpoint — 0.9.1-dev:** **155 C# source files**, **79 approved package files**, **net −112 lines**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `152660F9835E71DD9A75E9D59C1B9EDE72F9D09CF47C488F0A552EF1DC9FCBAE`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## Why this is its own checkpoint

Retiring `RR_MachineGate` in 0.9.0-dev made `IsNativeProvider` a constant. Sixty-eight sites branched on it, and every else-side became unreachable.

That cleanup was **deliberately kept out of the retirement commit**. A diff that says only *"remove the dead branch"* can be read and checked; the same change mixed into a content retirement cannot. This is the entire diff.

## Why it is safe, and how that is known rather than believed

Every edit is a **boolean identity** applied to a value that is now constantly true:

```
true ? A : B    ==  A
true && X       ==  X
!true || X      ==  X
if (!true) {…}  ==  removed
```

Nothing here is a judgement about what the code *should* do. Behaviour is unchanged **by construction**.

The method was also chosen so the compiler could act as the enumerator: rather than hand-editing around the property, it was pinned to `true`, every site transformed, and then the property **deleted outright**. Anything missed becomes a compile error rather than a silent survivor. One genuinely was — an unbalanced parenthesis in the assembly-bill guard — and the compiler named the line.

## What fell out of it: an entire power model

With the non-native branch gone, `ApplyPowerDraw()` reduced to an empty method, and that exposed a whole vestigial system underneath it.

The retired machine drew from the colony power network directly, so the component carried its own reserve: a stored watt-day figure, an applied draw, a per-tick charging step and a charge-rate calculation. **A gate on a door has never used any of it** — it is fed by the battery the player binds to it, and that is what every energy check already consults.

Removed: `returnReserveStoredWattDays` (and its saved value), `appliedPowerDrawWatts`, `ReserveChargePowerWattsThisTick()`, `ApplyPowerDraw()` and its **nine** call sites, the door's own `CompFlickable` handle, and the grid-headroom arithmetic in both power checks.

`HasPowerAndHeadroom()` and `HasProjectedOpeningPowerHeadroom()` now each answer with the binding failure key, which is where the real check always lived.

## The readout that could never be seen

`CompInspectStringExtra` built the legacy power readout, then **overwrote it on every single call** with the native one before returning. The first string was computed and discarded every tick a player had a gate selected. It is gone, along with the `RR_Gate_PowerReadout` key.

Six other keyed strings went orphan with the legacy UI they served and were pruned rather than left shipping as dead text.

## The field and the XML went together

`nativeProvider` was removed from both `CompProperties` classes **and from the patch that set it, in the same change**.

Removing only the field would have left an XML element no class declares, which **RimWorld ignores in complete silence at load**. That is the exact latent-defect class that cost two checkpoints when `maxTechLevel` did it, and it is why the two halves are never separated.

## Not done, and named in `TODO.md`

- The field gear, whose mechanics need replacements before its defs can go.
- `RR_QuietPursuer`, the five staff PawnKinds and their recipes.
- Multi-cell gates, which this checkpoint existed to clear the ground for.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. Keyed references 1,207 → 1,200, all resolving; seven orphaned keys pruned.
- Net **−112 lines** across 18 files. **Nothing added.**

## For the post-completion test phase

Confirming a gate still binds, calibrates, assembles, opens, spins up, recovers and closes exactly as before this change; that the inspect readout shows the battery figures it always showed; that an emergency cutoff still works through the designated power switch; and that no saved game reports an unknown component field at load.
