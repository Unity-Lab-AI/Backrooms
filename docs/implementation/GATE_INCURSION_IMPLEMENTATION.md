# It came through with them (0.9.6-dev)

**Baseline:** `4bd870e` (0.9.5-dev, 156 C# files, 79 package files).

**This checkpoint — 0.9.6-dev:** **157 C# source files** (one new), **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `76F6C531C095C1EB6F8508209A23C18BE43E711CD8F205EF6E604AA3B88E584B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"and even at higher techs they can come through the portal into your base and attack, kidnap, steal, do everything npcs can do in game"*

Asked at the fork and answered: **depth plus technology, while an opening is live** — *"it follows your pawn to the threshold; if it reaches the threshold before you close: it comes through."*

## This inverts the founding rule, so it is bounded on five axes at once

Everything else in this code base exists to keep the far side on the far side. That rule is not abandoned; it is given a **named, narrow exception** the player can see coming, cause, and stop.

| Bound | Why |
|---|---|
| **A live opening only** | A closed gate is a wall. |
| **`Band.Hostile` only** | The band already defined as *"the space stops being forgiving"*. A quiet coordinate never does this. |
| **Advanced machine only** | *"even at higher techs"* — you made the gate hold longer, and that cuts both ways. |
| **It has to fit** | A thing too large for the opening cannot use it, which makes a narrow gate a **real defensive choice** rather than the starter option. |
| **Once per opening** | So *"close the gate"* is a countermeasure that works, and is learnable from one incident. |

The tech condition is `PortalWindowTier >= 1`, which requires the `RR_GateTelemetry` project. That project exists and is completable — checked, because this session already produced an invariant about writing rules that can never fire.

## The inhabitant still decides nothing

Invariant #1 holds exactly as written, and the wording matters:

- `MayApproachThresholdForTraversal` **still returns false for everything.** Nothing on the far side is ever given a threshold as a destination or a reason to converge on one.
- A hostile walks to the doorway **because your people are standing there** — that is the pursuit from 0.9.5-dev, which is vanilla assault-lord behaviour aimed at colonists, not at a door.
- The gate then notices what is already on its doorstep and **asks the policy**. The decision is made in `PortalTraversalPolicy.IncursionFailureKey` and nowhere else, which is the same shape as every other crossing in the mod.

`AutonomousNonPlayerTraversalPermitted` is still a constant `false`. The class-level documentation was **rewritten rather than left standing**, because a founding comment that no longer describes the code is worse than no comment.

## Losing a pawn to a bug is not a threat, it is a corruption

The transfer preflights completely before anything is despawned, and a spawn that somehow fails **puts the pawn back where it stood**. A vanished hostile is a save with a hole in it that the player would never know about, and it would look exactly like the feature working.

## Determinism

Candidate cells are taken in a fixed radial order, so the same situation resolves the same way on every machine. A coordinate is regenerated from a seed, and two players in the same position must see the same thing happen.

## What it does once it is through

Nothing bespoke. It is an ordinary hostile pawn on a player map, so **every native behaviour applies** — *"attack, kidnap, steal, do everything npcs can do in game"* is satisfied by writing no behaviour code at all.

Note the deliberate asymmetry with 0.9.5-dev: kidnapping and stealing are switched **off** inside a coordinate, because a kidnapper leaving by a map edge there is a disappearance with no story. In the colony they are switched **on**, because that is an ordinary raid and the player can chase it.

## Not done, and named in `TODO.md`

- **The adjacent-door-run fallback** for 1×3 and 2×3 without Doors Expanded.
- Facilities, new-game playability, the player-facing how-to, and the rest of M2.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All five checkers pass.
- Compliance: **no new def, asset, patch operation or work type.** One new source file, seven keyed strings.

## For the post-completion test phase

Confirming nothing ever comes through from a `Quiet`, `Unsettled` or `Active` coordinate; that nothing comes through before `RR_GateTelemetry` is complete; that a creature too large for the gate is refused while a smaller one is not; that exactly one thing comes through per opening and that closing and reopening resets it; that closing the gate while something is approaching prevents it entirely; that the letter fires and points at the intruder; that the intruder behaves as an ordinary raider once inside; and that a failed transfer leaves the pawn where it stood rather than destroying it.
