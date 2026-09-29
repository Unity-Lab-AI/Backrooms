# Zones and areas on both sides of a gate — the full audit (2026-09-29)

**Owner direction, verbatim:** *"we also need to make sure zones work properly when putting them on boith sides of any type of gate"* and *"and as a continueations through the gate"*

## The constraint that shapes every answer

**A RimWorld `Zone` cannot span two maps.** `Zone.Map` is single-valued, `ZoneManager` is a per-map object, and the same is true of every `Area`. So "a zone that continues through the gate" cannot be one object, and nothing here pretends otherwise.

What "continuous" has to mean instead is that **two zones, one on each side, behave as one thing**: goods flow between them, work on either side attracts somebody, and the settings the player put on the far one are the settings that get respected. That is the standard this audit holds every case to.

## Every zone and area type, and where it stands

| Type | Driven by | Across a gate |
|---|---|---|
| `Zone_Stockpile` | storage carry family | **Works, both directions.** `storeMap.haulDestinationManager.AllHaulDestinationsListInPriorityOrder` and `IsValidStorageFor(storeMap, thing)` mean the *far* stockpile's own filter and priority decide what lands in it. The adapter plans in both directions, so a stockpile on either side pulls from the other |
| `Zone_Growing` | growing deployment | **Was broken. Fixed here** — see below |
| `Zone_Fishing` | fishing deployment | **Works** (0.6.7-dev). `ShouldFishNow` and `HasAnyFishableCells` are read from the far zone; unpainted water attracts nobody |
| `Area_Home` | cleaning, repair, firefighting | **Works.** All three read the far map's own Home area, so a Backrooms corridor nobody called home attracts nobody, exactly as it would at home |
| `Area_Allowed` | every family | **Works, as an observation.** `ObserveAreaHere` records a worker's `EffectiveAreaRestrictionInPawnCurrentMap` for whatever map it is standing on; `ObservedAreaAllows` consults it for a map the worker is not on. An unobserved map answers *unrestricted*, which matches Core, and the definitive per-pawn check still runs on arrival with a destination-refusal cooldown behind it |
| `Area_NoRoof` | containment | **Deliberately emptied** on a Backrooms map every interval. That is the containment rule, not a defect. Untouched on ordinary maps |
| `Area_BuildRoof` | `WorkGiver_BuildRoof` | **Not covered — and correctly so today.** See below |
| `Area_SnowOrSandClear` | `CleanClearSnowOrSand` | **Not covered — and correctly so today.** See below |
| `Area_PollutionClear` | `CleanClearPollution` (Biotech) | **Not covered — and correctly so today.** See below |

## Zones persist, which is the precondition for all of it

A zone only "works" across visits if the map survives. `RimroomsDestinationMapParent.ShouldRemoveMapNow` returns **`false` unconditionally**, so a Backrooms coordinate map is never removed once generated. Every stockpile, growing zone and fishing zone the player paints there survives leaving and coming back, along with its settings.

That was already true by construction. It is written down here because it is load-bearing and non-obvious.

## The defect: a growing zone inside the Backrooms could never be sown, and held a worker there anyway

`GrowingProvider.ZoneHasWork` decided that sowing was wanted from three facts about the **zone**:

```csharp
bool sowWanted = zone.allowSow && zone.CanAcceptSowNow() && zone.GetPlantDefToGrow() != null;
```

and then treated any empty cell in such a zone as work. It never asked whether that **cell** could be sown.

Inside the Backrooms the answer is almost always no. `GenStep_BackroomsDestination` floors rooms with `Concrete` and `PavedTile`; both inherit `FloorBase`, which declares no `fertility` and therefore carries the field default of **0**. Every Core plant requires `fertilityMin` of at least **0.01**, and `PlantUtility.CanEverPlantAt` refuses when `map.fertilityGrid.FertilityAt(c) < plantDef.plant.fertilityMin`.

So the sequence was:

1. the player paints a growing zone in a coordinate,
2. the candidate half reports work and a grower is sent across the gate,
3. Core refuses to sow on arrival, because the floor has no fertility,
4. **`HasWorkHere` asks the identical question and also says yes**, so the deployment is *not* released,
5. the worker stands in the Backrooms indefinitely with a live commitment and nothing to do.

Step 4 is what makes this worse than the futile-trip class fixed for bills. A wasted crossing costs one walk; a deployment that will not release costs a colonist.

**The fix** adds Core's own two gates to the per-cell test, both of which read the cell and its own map and take no pawn, so both are fair to ask remotely:

```csharp
if (!wantedPlant.CanEverPlantAt(cell, map)) { return false; }
return PlantUtility.GrowthSeasonNow(cell, map, wantedPlant);
```

`CanEverPlantAt` covers terrain fertility, blockers, roof and edifices. `GrowthSeasonNow` covers the cell's room and its temperature — which matters independently, because a coordinate has no climate control beyond whatever generator and heater the player keeps powered.

Nothing is reimplemented: fertility thresholds, blocker rules and temperature bands stay Core's numbers read through Core's methods, so a mod that changes any of them changes this answer too.

`zone.GetPlantDefToGrow()` is used rather than `WorkGiver_Grower.wantedPlantDef`, which Core writes mid-scan and which a remote probe must never touch.

### One thing I got wrong on the way, corrected

The first hypothesis was that a fully-roofed coordinate blocks sowing for lack of **sunlight**. It does not. `GrowthSeasonNow` reads room and temperature, not light, and Core will happily sow indoors — the plants simply grow slowly or not at all without light, which is the player's business and no different from an unlit greenhouse in vanilla. The real gate is **fertility**, and building on the light theory would have produced a check that tested the wrong thing.

## Three area types not covered, and why that is right *today*

These are gaps, named rather than hidden — but each is currently unreachable, and the reason is the containment rule rather than an oversight.

- **`Area_BuildRoof`.** The construction deployment looks for `BuildingFrame`s, not roof areas. Inside a Backrooms coordinate every cell already carries thick rock roof, so a build-roof area there has nothing to do.
- **`Area_NoRoof`.** Roof removal inside the Backrooms is forbidden outright, and the containment component keeps the area empty. Covering it would be building the thing the world rule exists to prevent.
- **`Area_SnowOrSandClear` and `Area_PollutionClear`.** The cleaning deployment covers `Filth` in the Home area only. A coordinate has no outside and therefore no weather, so no snow or sand accumulates.

**All three become live the moment the far side of a gate can be an ordinary world map** — the remaining half of the topology direction. A colony map genuinely does get snow, genuinely does want roofs built, and genuinely may be polluted. **Revisit this table when that endpoint lands**; it is recorded in `DEFERRED.md` against that item rather than as a free-floating row.

## What "continuation" turned out to mean in practice

Worth stating, because the phrase could have led somewhere wrong. Nothing here links two zones into one object, gives them a shared name, or copies settings between them — and none of that would be an improvement. Two stockpiles either side of a gate are already continuous in the only sense that matters: put something in one, and a hauler will move it to the other if the other is a better home for it, judged by the far zone's own filter and priority.

The failure mode to avoid was never "the zones are not linked". It was "a zone on the far side is invisible to the work layer, or visible but impossible" — and that is what this audit was for.

## For the post-completion test phase

A stockpile on a coordinate accepting only steel, and confirming only steel is carried to it; the same stockpile at a higher priority than one at home, and confirming steel moves *out* of the home map to it; a growing zone painted on a coordinate's concrete floor attracting **nobody**, repeatedly, rather than pulling a grower who then stands there; a growing zone on hydroponics or soil inside a coordinate attracting a grower who actually sows; a growing zone in a coordinate cold enough to be out of the plant's temperature band attracting nobody; a fishing zone painted on a coordinate's water attracting a fisher and unpainted water attracting nobody; an allowed area painted on a coordinate restricting a worker who has been there before; and a Home area covering part of a coordinate attracting cleaners only to that part. Then leave, return, and confirm every zone and its settings survived.
