
---

## 2026-09-29 — Zones on both sides of a gate, audited, and one defect that trapped a colonist (0.6.8-dev)

### Verbatim owner requests

> *"we also need to make sure zones work properly when putting them on boith sides of any type of gate"*

> *"and as a continueations through the gate"*

### The constraint that shaped every answer

- [x] **A RimWorld `Zone` cannot span two maps.** `Zone.Map` is single-valued, `ZoneManager` is per-map, and the same holds for every `Area`. So "a zone that continues through the gate" cannot be one object, and nothing here pretends otherwise. Continuation had to mean **two zones, one each side, behaving as one**: goods flow between them, work on either side attracts somebody, and the far one's own settings are what get respected. That is the standard the audit held every case to.

### The defect, which is the reason the question was worth asking

- [x] **A growing zone inside the Backrooms could never be sown — and the provider held the worker there anyway.** `GrowingProvider.ZoneHasWork` decided sowing was wanted from three facts about the **zone** (`allowSow`, `CanAcceptSowNow()`, `GetPlantDefToGrow() != null`) and treated any empty cell as work. It never asked whether that **cell** could be sown. Coordinate rooms are floored with `Concrete` and `PavedTile`; both inherit `FloorBase`, which declares no `fertility` and therefore carries the field default of **0**, while every Core plant requires `fertilityMin` of at least **0.01**, and `CanEverPlantAt` refuses when `map.fertilityGrid.FertilityAt(c) < plantDef.plant.fertilityMin`.
- [x] **Step four is what made it serious.** A grower was sent; Core refused on arrival; **and `HasWorkHere` asked the identical question and also said yes**, so the deployment was never released and the colonist stood in the Backrooms indefinitely holding a live commitment. A wasted crossing costs one walk. A deployment that will not release costs a colonist.
- [x] **Fixed with Core's own two gates**, both of which read the cell and its own map and take no pawn, so both are fair to ask remotely: `wantedPlant.CanEverPlantAt(cell, map)` for terrain fertility, blockers, roof and edifices, and `PlantUtility.GrowthSeasonNow(cell, map, wantedPlant)` for the cell's room and temperature — which matters independently, because a coordinate has no climate control beyond whatever generator and heater the player keeps powered. Nothing is reimplemented; a mod that changes any of those numbers changes this answer too. `zone.GetPlantDefToGrow()` is used rather than `WorkGiver_Grower.wantedPlantDef`, which Core writes mid-scan and a remote probe must never touch.
- [x] **A wrong hypothesis of mine, corrected before it reached the code.** The first theory was that a fully-roofed coordinate blocks sowing for lack of **sunlight**. It does not — `GrowthSeasonNow` reads room and temperature, not light, and Core sows indoors happily; plants simply grow slowly without light, which is the player's business and no different from an unlit greenhouse in vanilla. The real gate is **terrain fertility**. Building on the light theory would have produced a check that tested the wrong thing and still shipped the bug.

### Everything else audited rather than assumed

- [x] **`Zone_Stockpile` works in both directions.** `storeMap.haulDestinationManager.AllHaulDestinationsListInPriorityOrder` and `IsValidStorageFor(storeMap, thing)` mean the **far** stockpile's own filter and priority decide what lands in it, and the adapter plans both directions, so a stockpile on either side pulls from the other.
- [x] **`Zone_Fishing` works** (built 0.6.7-dev): `ShouldFishNow` and `HasAnyFishableCells` are read from the far zone, and unpainted water attracts nobody.
- [x] **`Area_Home` works** for cleaning, repair and firefighting — all three read the far map's own Home area, so a corridor nobody called home attracts nobody.
- [x] **`Area_Allowed` works as an observation plus a definitive check.** `ObserveAreaHere` records a worker's `EffectiveAreaRestrictionInPawnCurrentMap` for whatever map it stands on; `ObservedAreaAllows` consults it for a map it is not on; an unobserved map answers *unrestricted*, matching Core, with the per-pawn check on arrival and a destination-refusal cooldown behind it.
- [x] **`Area_NoRoof` is deliberately emptied** inside the Backrooms by the containment component. That is the world rule, not a defect, and ordinary maps are untouched.
- [x] **Zones persist across visits, which is the precondition for all of it.** `RimroomsDestinationMapParent.ShouldRemoveMapNow` returns `false` unconditionally, so a coordinate map is never removed and every zone painted there survives leaving and returning, with its settings. Already true by construction; written down because it is load-bearing and non-obvious.

### Three area types not covered, and why that is right today

- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` have no cross-gate route** — and currently cannot need one. A coordinate is already all thick rock, roof removal there is forbidden by the world rule, and it has no outside and therefore no weather. **All of them become live the moment the far side of a gate can be an ordinary world map**, so the row is recorded as a **dependency of the ordinary-map portal endpoint** rather than as a free-floating gap. A colony map genuinely gets snow, genuinely wants roofs built, and may be polluted.

### What "continuation" turned out to mean

- [x] **Satisfied functionally, deliberately not by linking objects.** Nothing gives two zones a shared name or copies settings between them, and neither would be an improvement. Two stockpiles either side of a gate are already continuous in the only sense that matters. The failure mode to avoid was never *"the zones are not linked"* — it was *"a zone on the far side is invisible to the work layer, or visible but impossible"*, and the second of those was real.

### Documents updated in the same change

`research/ZONES_AND_AREAS_ACROSS_A_GATE.md` (new audit), `TODO.md` (both directions captured verbatim, seven rows), `DEFERRED.md` (a new section, with the area row hung off the ordinary-map endpoint), `NOW.md` (a new invariant, a new reading-order entry, and the dependency noted on the endpoint item), `REGRESSION_CONTAINMENT.md` (two new rot checks, including the sunlight mistake so nobody repeats it), `CHANGELOG.md`, `About.xml`, the csproj.

### Build evidence

0.6.8-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **117** C# source files and **76** approved package files, both unchanged — this checkpoint is one corrected predicate and the documentation around it. Assembly SHA-256 `4E474FF0A277861CB788A87C893714CF0C9A0CFC3834473B6972D8F4941C9930`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence folder `implementation/evidence/zones-across-a-gate-2026-09-29/`. `audit-gate0.py` PASS with zero errors; `check-dlc-gating.py` passes; the register verifies; reference manifest recomputed with no drift; no attribution strings. Published via the cascade in `PUBLISHING.md`; refs read back in session output. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files changed: 1. Docs updated: 6 (1 new). Owner directions captured verbatim: 2.
Zone and area types audited against the work layer: **9**. Working: 6. Fixed: 1. Correctly uncovered and scoped to a later item: 3 area types (counted as one row).
Defects found and fixed: **1, and it was the kind that costs a colonist rather than a walk** — a deployment that could never release.
Wrong hypotheses of mine caught before reaching the code: 1 (sunlight rather than fertility).
