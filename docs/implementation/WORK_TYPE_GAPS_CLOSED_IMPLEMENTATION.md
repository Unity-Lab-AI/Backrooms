# Every work type in the game is now answered (0.6.7-dev)

**Baseline:** `9204048` (0.6.6-dev, 115 C# files, 76 package files).

**This checkpoint — 0.6.7-dev:** **117 C# source files** (two new), **76 approved package files** (unchanged — six work giver defs and six keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `9A73827B2E0F6C6AC33712BE447CEA5C7F8959C72820080AE7C2C00BA75A8EAE`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/work-type-gaps-closed-2026-09-29/`](evidence/work-type-gaps-closed-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## What this closes

`research/WORK_TYPE_COVERAGE_AUDIT.md` enumerated all 23 work types across Core and the five expansions and found **four gaps**. Bill work closed in 0.6.5-dev and dark study in 0.6.6-dev. This checkpoint closes the remaining three routes in one pass:

- **hauling upkeep** — containers on the far map,
- **BasicWorker** — flick, open, eject fuel,
- **Fishing** — which the audit had deliberately deferred as a *generation* question.

**Thirty-one families, twenty-three of them travel-to-work deployments. Every work type in the game is now either covered, or decided against with its reason recorded.**

## Hauling, enumerated rather than skimmed

`Hauling` is the largest work type in the game — thirty giver defs — and "it is only partly covered" was not a good enough answer. All thirty were classified:

| Givers | Disposition |
|---|---|
| `HaulGeneral`, `HaulMerge` | the storage carry family's route |
| `HaulCorpses` | the casualty carry family |
| `DeliverResourcesToFrames`, `DeliverResourcesToBlueprints` | the construction supply family |
| `Refuel`, `RearmTurrets` | the fuel carry family, which is one family for both |
| `DoBillsCremate`, `DoBillsHaulCampfire` | bills; the bill families own them |
| `HelpGatheringItemsForCaravan`, `LoadTransporters` | **semantically map-bound** — a caravan forms on, and a pod launches from, one specific map, so crossing a gate to load either would be loading the wrong departure |
| `HaulToPortal` | Core's **own** map-portal system, which `CONNECTED_WORK_CORE_API.md` already established cannot serve this design. It is not our gate |
| `Strip` | custody-adjacent; needs its own review |
| the eleven Biotech / Ideology / Anomaly container givers | **named and left open**, not swept in |
| `UnloadCarriers`, `EmptyEggBox`, `FillFermentingBarrel`, `TakeBeerOutOfFermentingBarrel` | **built here** |

Three of those lines are decisions rather than deferrals, and each is the kind that would have been a quiet bug if guessed at. Loading a caravan through a gate is not "unimplemented" — it is *wrong*, because the caravan leaves from the map it formed on.

### The DLC container givers are named, not omitted

`HaulToGeneBank`, `HaulToGrowthVat`, `CarryToGrowthVat`, `CarryToGeneExtractor`, `CarryToSubcoreScanner`, `HaulMechsToCharger`, `EmptyWasteContainer` (Biotech), `HaulToBiosculpterPod` (Ideology), `TakeBioferriteOutOfHarvester`, `TakeEntityToHoldingPlatform`, `TransferEntity` (Anomaly). Every one carries a pawn or a live subject into a machine, or moves an entity between platforms. Each needs its own review of what that does to **custody** before a worker is sent across a gate to do it. Recorded as open rather than guessed at.

### The priority followed the Hauling ladder, not the generic rule

Every other family's continue giver sits just above the highest Core giver in its work type. Applying that here would have put this at 302 — and it would have been **wrong**, because the cross-gate hauling numbers are a documented, deliberate exception. `CONNECTED_FOOD_IMPLEMENTATION.md` calibrates them against `HaulGeneral` (15) and states outright that *"Core's local rearming at 150 will always beat it anyway."*

So container upkeep continues at **131**: above every container giver it travels for, including `UnloadCarriers` (130), and **below** `Refuel` (140) and `RearmTurrets` (150) — because a turret out of shells at home beats eggs across a gate. Plan sits at **4**, below `HaulMerge` (5) and below every existing cross-gate hauling plan giver, because this is the least urgent crossing in the mod.

That exception was found by reading the existing records before picking a number, which is the only reason this family does not silently contradict the four that came before it.

## BasicWorker: designation-driven, and the most useful small thing here

All three Core givers read nothing but their own designation off the map:

```csharp
WorkGiver_Flick.ShouldSkip     -> !map.designationManager.AnySpawnedDesignationOfDef(Flick)
WorkGiver_Open.ShouldSkip      -> !map.designationManager.AnySpawnedDesignationOfDef(Open)
WorkGiver_EjectFuel.ShouldSkip -> !map.designationManager.AnySpawnedDesignationOfDef(EjectFuel)
```

So this sits with the fieldwork families where **nothing is inferred**: no designation, nobody goes. It reuses `FieldworkScan`, which already owns the designation questions, rather than asking them a second way.

Flicking a switch on a far map is an ordinary thing a player asks for and could not previously get, and a power switch is exactly what a Backrooms facility is full of.

`ExtractSkull` and `ChangeTreeMode` are Ideology ritual-adjacent content and `BasicReleasePrisoner` is custody work the warden family already justifies a crossing for. None is claimed.

## Fishing: the generation question, settled, then overtaken

The audit deferred fishing on purpose: it needs water, and whether a generated coordinate ever *has* fishable water is a generation question. If the answer were no, the honest record would have been "unnecessary" rather than "unbuilt".

**The answer is yes** — `GenStep_BackroomsDestination` uses `WaterDeep` as its void floor, so a coordinate genuinely carries water terrain.

But the deciding fact turned out to be different and better. Core will not fish anywhere the **player** has not painted a zone:

```csharp
if (allZone is Zone_Fishing { ShouldFishNow: not false, HasAnyFishableCells: not false })
```

which puts this family with growing zones. So the terrain question is not load-bearing after all: whether that water reads as a lake or an abyss, the player decides by painting or not painting, and `IsFishable` checks the water body type on that map either way. A coordinate full of void floor that nobody zoned attracts nobody.

Both gates are facts about the zone and its own map — `ShouldFishNow` reads `Allowed`, `OverTargetPopulation`, `PausedDueToResourceCount` and `UnderTargetResourceCount`; `IsFishable` reads the cell's terrain and water body type. **Neither takes a pawn.** Core's `NonScanJob` does everything else on arrival: choosing the zone, picking a cell, finding a stand spot out of the water, the reservations, and the ideoligion check on slaughtering fish.

Odyssey content, so it is gated in **both** halves — `GetNamedSilentFail` in C# and `MayRequire="Ludeon.RimWorld.Odyssey"` on both defs. The gating check caught them automatically, which is what it is for.

## Profile rows read before writing

The register flagged eleven *Storage and recovered-material logistics* rows whose planned use implies Rimrooms builds something. They were read first and each changed something or was explicitly ruled out:

- **157 OgreStack** changes stack sizes globally. Nothing here reads a stack size — the questions are "is this barrel fermented" and "does this box hold eggs". The one count involved is Core's own `CompEggContainer.CanEmpty` against the comp's `minCountToEmpty`.
- **122 LWM's Adaptive Deep Storage**, **259 Warehouse Storage**, **26 Adaptive Simple Storage**, **195 RimFridge** add storage buildings. The *destination* for emptied eggs is chosen by Core's `TryFindBestBetterStorageFor` on arrival, so a modded store is used automatically and nothing here needs to know it exists.
- **164 Pick Up And Haul** and **107 Haul to Stack** were closed as register rows previously; this provider hands out no hauling job of its own either.
- **245 Vanilla Fix: Haul After Slaughter** and **93 Food Poisoning Stack Fix** correct vanilla hauling behaviour that is never reimplemented here.
- **87 Egg Incubator** adds egg content; the egg route matches by `CompEggContainer` rather than by a named building, so a modded container with that comp is covered with nothing naming it.

Nothing of anyone else's is edited, copied, patched, replaced or bundled.

## A build check that earned its keep

The XML validator in `BuildCommon.ps1` rejected a comment containing `--`, which is illegal inside an XML comment and would have been a load failure. Caught at build time, before anything shipped.

## Saved state

**None added.** The deployment record already carries a provider id; `hauling-upkeep`, `basic-worker` and `fishing` are new values in an existing field. A 0.6.6-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` label and settings key resolves with **0 missing**; every Rimrooms `giverClass` resolves; all **31** priority pairs name real `WorkGiverDef`s with keyed labels; **24** providers registered.
- `tools/check-dlc-gating.py`: 6,063 DLC-only defs indexed, **6** references, all gated.
- Compliance: zero destructive patch operations, no `texPath` outside `RR_`, no `modDependencies`, no non-original package asset. 76 approved package files, 0 missing. Reference manifest recomputed, no drift. No attribution strings.

## For the post-completion test phase

A fermenting barrel on a far coordinate with wort present attracting a hauler, and the same barrel with no wort attracting nobody; a barrel whose ambient temperature is near ruining attracting nobody; a fermented barrel attracting somebody to take the beer out; an egg box with eggs attracting a hauler and an empty one attracting nobody; a pack animal marked to unload attracting a hauler; a switch marked to flick on a far map attracting a worker, and an unmarked switch attracting nobody; with Odyssey, a painted fishing zone on a coordinate attracting a fisher and unpainted water attracting nobody; and without Odyssey, the fishing giver defs absent with zero load errors.
