# Some places are bigger than a room (0.9.7-dev)

**Baseline:** `ec507b7` (0.9.6-dev, 157 C# files, 79 package files).

**This checkpoint — 0.9.7-dev:** **158 C# source files** (one new), **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `77C50D056BBC91570AFB912B283A30F2EB49FA3EC7264A70C9DC8F4005EF5F37`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"facilitys"* — larger functional spaces, as distinct from rooms and corridors.

> *"lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries"*

## What was wrong with what was already there

Every room rolled its own kind independently. A coordinate could put a laboratory bench in one room, a bed in the next and a smithy in the third.

Each room was fine. **The place was nothing.** There was no laboratory — only a room with a bench in it.

## A facility is a run of adjacent rooms that agree with each other

The planner walks the coordinate's **own saved room graph**, takes a contiguous run of two to four rooms, and dresses all of them as the same kind.

That is what turns three rooms into a laboratory wing, a dormitory block, a nursery. **No new def type and no new content**: it is the same fourteen archetypes, chosen once for a group instead of once per room.

Resolution is through an **anchor** — the lowest room index in the group — so every member asks the same question and gets the same answer, and **nothing is stored**. The assignment is derived from the coordinate's saved graph and seed, so it survives a save and reload by being recomputed identically rather than by being written down. Nothing can fall out of step with the graph because nothing is duplicated from it.

## Why coherence makes a deep coordinate worse, not tidier

The obvious worry is that this is the opposite of what the setting wants.

It is not. **A recognisable institution that is wrong is far worse than a jumble**, because a jumble has nothing to violate. The derangement from 0.8.7-dev still applies on top: in a deep coordinate an archetype's family constraint lapses and its contents scale with research and depth, so a three-room nursery turns up where no nursery could be, furnished at a tech level nobody there should have had.

Coherence is what gives the wrongness something to happen to.

## What it never touches

- **Depth 1.** The shallow yellow rooms stay sparse; that emptiness is the look (invariant #25).
- **The threshold room**, left undressed so the way back is never buried.
- **Quiet rooms.** A facility is assembled **only from rooms that were going to be dressed anyway**, so the required-quiet guarantee is untouched *by construction* rather than by a separate check that could drift from it.

## Proved, because this is exactly how a generator ships a no-op

Half of every coordinate is a required quiet room and one more is the threshold, so the pool a facility can be built from is **small before any roll happens**. It is entirely possible to write this, have every constraint be individually reasonable, and have it never once form a group — which would look precisely like a working feature.

`.local/register/proof-facilities.py` simulates **2,800 coordinates** across seven sizes and asserts:

- facilities actually form — **53.9%** of coordinates get one, so a plain coordinate still exists
- every group is **contiguous through the graph**, verified by walking it
- every group is **2 to 4 rooms**, and the anchor is the lowest index
- **no quiet room and no threshold room is ever consumed**
- the quiet guarantee still holds afterwards
- the same seed **replans identically**

The proof mirrors the shipped constant rather than a convenient one. `EligibleShare` was compared at 0.45, 0.50, 0.60 and 0.70 — giving 53.9%, 61.3%, 61.3% and 63.4% — and **the code kept 0.45**, with the proof changed to match it. A proof testing different numbers than the code is worthless.

## Not done, and named in `TODO.md`

- New-game playability, the player-facing how-to, and the rest of M2.
- The adjacent-door-run fallback for 1×3 and 2×3 gates.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All five checkers pass.
- `.local/register/proof-facilities.py`: 2,800 simulated coordinates, six structural properties asserted.
- Compliance: **no new def, asset, patch operation or work type.** One new source file.

## For the post-completion test phase

Confirming that a deep coordinate contains at least one run of rooms furnished as a single kind; that they are adjacent rather than scattered; that quiet rooms remain empty and are never inside one; that the threshold room is never part of one; that depth 1 has none at all; and that reloading a coordinate produces the same facilities in the same rooms.
