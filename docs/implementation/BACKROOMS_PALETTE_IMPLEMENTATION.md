# The yellow rooms, and what happens further in (0.7.8-dev)

**Baseline:** `39b313e` (0.7.7-dev, 137 C# files, 84 package files).

**This checkpoint — 0.7.8-dev:** **138 C# source files** (one new), **85 approved package files** (one new keyed file). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `262F02B6EBACE586D281A9251566E5728A1A0490158521421DA2851F60BE1392`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly"*

> *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

**The second message is the one that shaped the design.** A single global palette could only ever deliver the first half. So the look is a **function of depth**.

## Core already had the overhead light

The owner reached for floor lights on the assumption the game had no overhead fluorescent. **Core ships `WallLamp`** — wall-mounted, not standing.

It is the better answer in two ways. It is closer to the intended look, and it **frees the floor**: an endless corridor reads as endless precisely because nothing is standing in it. Generation had been using `StandingLamp`, which put a piece of furniture in the middle of every room.

## Yellow, from Core, with no new asset

| Piece | How |
|---|---|
| **Floor** | Core `Carpet`, whose own description says it is *"dyed a single color"*. `TerrainGrid.colorGrid` is a **public field**, so the colour is applied directly after `SetTerrain` — no Harmony, no new terrain def. |
| **Walls** | Core `Wall` from `WoodLog`, tinted through `CompColorable`, which generation already used for its grey and tan rooms. |
| **Light** | Core `WallLamp`. |

**No new texture, no new terrain, no new building.** The whole look is Core content wearing a colour. The tint is `Structure_Mustard` — sickly ochre rather than a clean primary, which is what the reference actually looks like.

`SetTerrain` **clears** the colour grid, so the colour has to be applied after the terrain and the cell redrawn. Missing either produces a floor that is silently the wrong colour until something else dirties the mesh.

## Depth is the new axis

`CoordinateRecord.depth`, counted in portals from the ordinary world. A frontier found on a world map mints **depth 1**; every step inward adds one, without limit. Defaults to 1, so every coordinate in an existing save reads as shallow — which is both the safe answer and the true one.

| Depth | Look |
|---|---|
| **1** | **The yellow rooms. Fixed, never rolled.** |
| 2+ | Poolrooms · Machinery · Abandoned offices · Cold storage · **Wrong** |

**Depth 1 does not roll, and that is deliberate.** The first space a player ever sees must be the yellow rooms, every time, on every seed. It is the image the whole setting rests on, and a random alternative there would be a worse game for the sake of variety.

Deeper bands roll from the coordinate's own seed, so a space is **stable across reloads** and two spaces at the same depth are not identical.

The band list is deliberately short. Variation deeper down should come from **what is in a room**, not from an ever-growing list of paint schemes — a palette that never repeats stops reading as a place at all. That is the next checkpoint's work, and it is where the owner's *"labs, workshops, nursaries, everything imanginable"* lands.

## Not done, and named in `TODO.md` rather than deferred

The other half of the owner's direction is a much larger body of work and is recorded in full:

- **Room archetype library** — labs, workshops, nurseries, and every variation, with furniture and equipment density per archetype.
- **Material variety** — *"materials of all types"*, drawn from what the loaded game offers rather than a fixed list.
- **Anomalous places and events** — *"wild waky carzxzy creepy things"*, as saved, bounded content rather than random noise.
- **Balance against colony wealth**, so a tier scales with what the branch has rather than with wall-clock time.
- **Solo survivability at high tiers** — the owner's explicit requirement that a solo group can *"build and get supplies on backrroms instances and find a way out before dying"*. That is an acceptance condition on the escalation ladder, not a nice-to-have.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. `check-keyed-strings.py`: 1,172 references all resolving.
- Compliance: one keyed file added. **No new gameplay ThingDef, no terrain, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming a first coordinate is yellow carpet, yellow wood walls and wall lamps every time on every seed; confirming the carpet colour survives save and reload; confirming a depth-2 coordinate looks different and that the *same* one looks the same after reloading; confirming wall lamps light a room adequately without floor lamps present; confirming an existing save's coordinates read as depth 1 and regenerate as yellow; and confirming the stripe pattern still reads as a non-colour cue in every band.
