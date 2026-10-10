
---

## 2026-09-29 — The yellow rooms, and what happens further in (0.7.8-dev)

### Verbatim owner requests

> *"and we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly, and remmeber when building the seed genrator for the back rooms everything ive said and how the backrooms universe works to be lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

> *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

### The second message is what shaped the design

- [x] **A single global palette could only ever deliver half the direction.** So the look became a **function of depth**, which meant adding a depth concept the project did not have: `CoordinateRecord.depth`, counted in portals from the ordinary world. A frontier on a world map mints depth 1 and every step inward adds one, without limit.
- [x] **Depth 1 is fixed and never rolls.** The first space a player ever sees must be the yellow rooms, every seed, every time. It is the image the whole setting rests on, and a random alternative there would be a worse game for the sake of variety. Deeper bands roll from the coordinate's own seed, so a space is stable across reloads and two spaces at the same depth are not identical.

### Core already had the overhead light

- [x] **The owner reached for floor lights on the assumption the game had no overhead fluorescent. Core ships `WallLamp`.** It is the better answer twice over: closer to the intended look, and it **frees the floor** — an endless corridor reads as endless precisely because nothing is standing in it. Generation had been using `StandingLamp`, which put a piece of furniture in the middle of every room.

### Yellow, from Core, with no new asset

- [x] **Floor:** Core `Carpet`, whose own description says it is *"dyed a single color"*. `TerrainGrid.colorGrid` is a **public field**, so the colour is applied directly after `SetTerrain` — no Harmony, no new terrain def. Tinted `Structure_Mustard`: sickly ochre rather than a clean primary, which is what the reference actually looks like.
- [x] **Walls:** Core `Wall` from `WoodLog`, tinted through `CompColorable` — the same mechanism generation already used for its grey and tan rooms.
- [x] **A trap worth recording:** `SetTerrain` **clears** the colour grid, so the colour must be applied *after* the terrain and the cell redrawn. Missing either produces a floor that is silently the wrong colour until something else dirties the mesh.
- [x] **No new texture, no new terrain, no new building.** The whole look is Core content wearing a colour.

### The band list is deliberately short

- [x] Five bands, not an ever-growing list. Variation deeper down should come from **what is in a room**, not from more paint schemes — a palette that never repeats stops reading as a place at all. That is where the owner's *"labs, workshops, nursaries, everything imanginable"* belongs, and it is the next body of work.

### Build evidence

0.7.8-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **138** C# source files (one new), **85** approved package files (one new keyed file). Assembly SHA-256 `262F02B6EBACE586D281A9251566E5728A1A0490158521421DA2851F60BE1392`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; `check-keyed-strings` 1,172 references all resolving. **No new gameplay ThingDef, no terrain, no asset, no patch operation, no new work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Source files modified: 4. Package files created: 1. Docs updated: 5 (1 new).
Owner directions captured verbatim: 2, the second of which reversed the shape of the first.
Owner assumptions corrected by reading the game's own data: 1 — the game *does* have an overhead lamp.
Core behaviours found by reading rather than by failing: 1 — `SetTerrain` clearing the colour grid.
Still open and named in `TODO.md`, not deferred: the entire seed-generator expansion — room archetypes and their variations, material variety, anomalous places and events, escalation balanced against **colony wealth** rather than wall-clock time, and the owner's explicit acceptance condition that a **solo group must be able to build, supply and find a way out** of a high-tier coordinate.
