# Fifteen work givers, and a clamp that was overwriting the mod's own numbers — 0.12.34-dev

**Rows closed:** 1266 (the eleven DLC container hauling givers) and the painting half of the
coverage row. **Defect found and fixed on the way:** six shipped work-giver priorities were being
silently overwritten on every game load.

No game was launched. Nothing here claims a gameplay, balance, performance or compatibility
result.

---

## 1. The question row 1266 was actually asking

`HaulingUpkeepProvider` enumerated all thirty `Hauling` givers at 0.6.7-dev, covered the three
Core container routes, and left eleven named rather than swept in, with its reason recorded in its
own source:

> *"Each carries a pawn or a live subject into a machine, or moves an entity between platforms,
> and each needs its own source review of what that does to custody before a worker is sent
> across a gate to do it."*

That is the right instinct and it is why the row sat open for twenty-seven checkpoints. **Invariant
55 rules a pawn transfer absolutely** — a transfer that can lose a pawn is a corruption, not a
threat — and three of the eleven move a pawn into a machine while three move an entity between
platforms. If any of them could move a subject across a gate, the family would need preflight,
restore-on-failure and a whole custody apparatus.

### The finding: Core forbids all eleven from crossing anything

All eleven were decompiled and read. Every single one refuses to act unless the thing it moves is
already on the worker's own map, and Core enforces it itself:

| Giver | Core's own same-map constraint |
|---|---|
| `CarryToGrowthVat`, `CarryToGeneExtractor`, `CarryToSubcoreScanner` | `WorkGiver_CarryToBuilding.HasJobOnThing` returns false unless `selectedPawn.Map == pawn.Map` |
| `HaulToGeneBank` | `FindGeneBank` requires `genepack.targetContainer.Map == genepack.Map`, and searches from `genepack.Position, genepack.Map` |
| `HaulToGrowthVat` | `CanHaulSelectedThing` returns false unless `selectedThing.Map == pawn.Map`; `FindNutrition` searches `pawn.Position, pawn.Map` |
| `HaulMechsToCharger` | candidates are `pawn.Map.mapPawns.SpawnedPawnsInFaction(pawn.Faction)` |
| `EmptyWasteContainer` | the destination comes from `TryFindBestBetterStorageFor(..., pawn.Map, ...)` |
| `HaulToBiosculpterPod` | `FindNutrition` searches `pawn.Position, pawn.Map` |
| `TakeBioferriteOutOfHarvester` | the job is the building alone; nothing travels |
| `TakeEntityToHoldingPlatform` | returns false unless `targetHolder.MapHeld == t.MapHeld` |
| `TransferEntity` | both platforms are reserved by one worker, and it refuses when `HeldPlatform == targetHolder` |

So the family is the **ordinary deployment shape**, and it is the safest of them rather than the
riskiest: the worker crosses, and everything it touches is already on the far side. A pawn carried
into a growth vat was standing beside that vat before the hauler arrived. An entity moved between
platforms moves between two platforms in one room.

**Invariant 55 is never engaged, because there is no transfer to govern.** That answer was read out
of Core rather than assumed — and assuming it the other way is exactly what kept the row open.

---

## 2. What was built: `MachineLoadingProvider`

One provider, id `machine-loading`, nine routes covering all eleven givers. It hands out no job:
it justifies a crossing and Core's own giver does the work on arrival, in that pawn's own priority
order, with Core's reservations.

| Route | Givers | Core question asked remotely |
|---|---|---|
| `AnyWasteContainer` | `EmptyWasteContainer` | `CompWasteProducer.CanEmptyNow` and a wastepack held |
| `AnyHarvester` | `TakeBioferriteOutOfHarvester` | `unloadingEnabled` and `ReadyForHauling` |
| `AnyCapturableEntity` | `TakeEntityToHoldingPlatform` | `targetHolder` set, same `MapHeld`, platform empty, `ThreatDisabled` |
| `AnyMisplacedEntity` | `TransferEntity` | `HeldPawn` present and `HeldPlatform != targetHolder` |
| `AnyGenepack` | `HaulToGeneBank` | `Genepack.AutoLoad`, and a `CompGenepackContainer` with room |
| `AnyGrowthVatSupply` | `HaulToGrowthVat` | `NutritionNeeded > 2.5`, or a `selectedEmbryo` still on the floor |
| `AnyBiosculpterPod` | `HaulToBiosculpterPod` | `PowerOn`, `autoLoadNutrition`, `State == LoadingNutrition` |
| `AnyUnchargedMech` | `HaulMechsToCharger` | `IsColonyMech`, shut down or downed, below `GetMaxRechargeLimit` |
| `AnyEnterable` | `CarryToGrowthVat`, `CarryToGeneExtractor`, `CarryToSubcoreScanner` | `SelectedPawn` on that map, `CanAcceptPawn`, and Core's cannot-walk-in test |

### The enterable condition is easy to read backwards

Core hands the carry job out **only when the subject cannot walk in by itself** — prisoner of the
colony, downed, incapable of moving, or with the giver's own work type disabled — and returns false
otherwise, because an able colonist walks to the vat on its own errand. The work type compared is
the giver def's, which for both of this family's giver defs is `Hauling`, the same def the
provider's `WorkType` returns, so the parity is exact. Reading that condition the other way round
would haul colonists who were already walking there.

### No expansion branch anywhere, deliberately

Seven of the eleven are Biotech, one Ideology, three Anomaly, and the obvious design — three
providers behind three `ModsConfig.XActive` gates — is the wrong one. Every route degrades on its
own:

* the `MayRequire` `ThingDefOf` fields it needs (`Genepack`, `GrowthVat`, `BiosculpterPod`,
  `BioferriteHarvester`) are **null** without their expansion, and each is null-checked;
* every other route matches a `ThingRequestGroup` or a comp, and `ThingsInGroup` returns an
  **empty list** for content that is not installed;
* every class and comp named (`Building_Enterable`, `CompWasteProducer`, `CompBiosculpterPod`,
  `Building_HoldingPlatform`, `CompHoldingPlatformTarget`) lives in the always-present base
  assembly, so no type reference can fail to resolve on a Core-only install.

An absent expansion is an **empty world, not a condition** — fewer moving parts, and strictly more
capable: the enterable route matches `Building_Enterable` rather than the three shipped buildings,
so a modded enterable is covered with nothing naming it. `WorkGiver_CarryToBuilding` is itself an
ungated abstract class; only its three subclasses carry the Biotech skip, and they carry it because
the three *buildings* are Biotech, not because the shape is.

### The one Core answer that could not be borrowed

`JobGiver_GetEnergy_Charger.GetClosestCharger(mech, carrier, forced)` builds
`TraverseParms.For(carrier)` and calls `carrier.CanReach`, so asking it about a map the carrier is
not standing on is precisely the remote-reachability mistake this layer exists to avoid. The
candidate half substitutes the **presence** of a charger that `CanPawnChargeCurrently` accepts for
that mech. Necessary, not sufficient — an optimistic miss delays one pass, a false positive wastes
one walk — and Core makes the real call on arrival.

By contrast `Pawn.ThreatDisabled(IAttackTargetSearcher)` **is** safe from here, which was checked
rather than assumed: it reads the entity's own spawn state, duty, mind state, downed state and
comps, and uses the passed searcher only for `attackDownedIfStarving` and a roamer comparison. It
reads no map and takes no reservation, so the capture route asks Core's question outright.

### Priorities

| Def | Priority | Why |
|---|---|---|
| `RR_ConnectedMachineLoadingContinue` | 301 | one above `TakeEntityToHoldingPlatform` (300), **the highest `Hauling` giver in the whole game**, which this family travels for |
| `RR_ConnectedMachineLoading` | 3 | below `HaulMerge` (5), the lowest local giver in the type, and below `hauling-upkeep`'s plan (4) |

Being planned after container upkeep is an accepted cost: both plan only when nothing of their kind
is waiting on this side at all, and the connected-map scan rotates, so neither starves the other.

---

## 3. The other half of the same row: the four painting givers

The coverage row's own reason for staying open named **three** things, not one: the eleven
container givers, *"the four painting givers in `Art`"*, and any wholly mod-added work type. The
four were the easiest to lose, because `Art` already has a family — `bill-work-art`, which crosses
for sculpting — and a work type that is already covered reads as finished.

It was not covered. A bill lives on a bench and is chosen from a bill stack; paint lives on a
**designation** and is chosen by the player pointing at a floor or a wall. `BillWorkProvider` asks
whether any bench on that map has a deliverable bill, which is false on a map with fifty
painted-blue designations and no sculpting bench. **Nobody would ever cross for any of it.**

`PaintingProvider` (id `painting`) covers all four, and all four are designation-driven, which is
what makes the family safe:

```
WorkGiver_PaintFloor.ShouldSkip           -> !map.designationManager.AnySpawnedDesignationOfDef(PaintFloor)
WorkGiver_PaintBuilding.ShouldSkip        -> !map.designationManager.AnySpawnedDesignationOfDef(PaintBuilding)
WorkGiver_RemovePaintFloor.ShouldSkip     -> !map.designationManager.AnySpawnedDesignationOfDef(RemovePaintFloor)
WorkGiver_RemovePaintBuilding.ShouldSkip  -> !map.designationManager.AnySpawnedDesignationOfDef(RemovePaintBuilding)
```

**Nothing is inferred: no designation, nobody crosses.** A coordinate full of stained yellow wall
attracts nobody until the player says so.

Two conditions were read out of Core rather than guessed:

* **Paint needs dye and stripping paint does not.** `ShouldPaintCell` and `ShouldPaintThing` both
  end in a `checkDye` branch over `ThingsOfDef(ThingDefOf.Dye)` and refuse with `NoIngredient`;
  neither remove-paint giver mentions dye at all. So the two paint routes ask for dye presence on
  that map and the two strip routes do not — requiring it there would refuse real work.
* **A colour already applied is not work.** Core compares the designation's own `colorDef` against
  `map.terrainGrid.ColorAt(cell)` for a floor and `Building.PaintColorDef` for a building. Both are
  facts about the map asked about, so both are asked here, and a stale designation over an
  already-blue wall cannot pull anybody through a gate.

The conflicting-designation refusals are Core's too, read from **the target's** designation manager
rather than the worker's, because here those are different maps.

| Def | Priority | Why |
|---|---|---|
| `RR_ConnectedPaintingContinue` | 203 | above `RemovePaintFloor` and `RemovePaintBuilding` (both 202), and below `RR_ConnectedBillWorkArtContinue` (204) so the two `Art` families never tie |
| `RR_ConnectedPainting` | 1 | below `DoBillsSculpt` (100), the lowest local giver in the type, and below `bill-work-art`'s plan (2) — a sculpture somebody ordered outranks a wall somebody wants recoloured |

---

## 4. The defect found while wiring both families up

`ConnectedWorkPriorities` exists so the crossing priorities can be tuned during a live play
session without a rebuild. It held one shared cap:

```csharp
internal const int MaximumPriority = 130;   // "Above Core's highest construction giver (120)"
```

and `Effective` clamped **every** value against it, including the shipped default:

```csharp
return Clamp(Shipped(defName));
```

`Apply` writes `Effective` into `WorkGiverDef.priorityInType` for every family, and `FinalizeInit`
calls `Apply` on **every game load**. So six of the mod's own authored defaults were being
overwritten before a single pawn ever ran:

| Def | Authored | Applied | What that broke |
|---|---|---|---|
| `RR_ConnectedBasicWorkerContinue` | **502** | 130 | authored one above Core's `Flick` (500); landing below every local `BasicWorker` giver, so a worker part way to a gate to flick a switch was turned around by any switch at home |
| `RR_ConnectedBillWorkSmithingContinue` | 222 | 130 | below `DoBillsSubcoreEncoder` (220) and `DoBillsMechGestator` (210) |
| `RR_ConnectedBillWorkArtContinue` | 204 | 130 | below both paint-removal givers (202) and both paint givers (200) |
| `RR_ConnectedChildcareContinue` | 202 | 130 | below Core's childcare ladder |
| `RR_ConnectedHandlingContinue` | 152 | 130 | below Core's handling ladder |
| `RR_ConnectedHaulingUpkeepContinue` | 131 | 130 | authored one above `UnloadCarriers` (130), landing in a **tie** with it, which resolves by database order rather than by a decision |

This is the exact failure the two-giver split exists to prevent — a committed trip turned around by
work that appeared at home — happening inside the code that exists to prevent it.

### The fix: the ceiling is per giver

`MaximumPriority` becomes the **floor** of each slider's ceiling rather than a cap, and the ceiling
is resolved per giver:

```csharp
internal static int Ceiling(string defName)
{
    int shippedValue = Shipped(defName);
    return shippedValue > MaximumPriority ? shippedValue : MaximumPriority;
}
```

A shipped number is authored against the native givers it has to beat and reviewed in the def file
beside its reasoning, so **it is never a value the player is refused**. `Clamp` takes the defName,
and the settings slider's range comes from `Ceiling` so a family's own default is always reachable
and a slider dragged away can be dragged back.

The rejected alternative was one cap above the game's own highest giver — `ChildcarerTeach` at
**9999** — which would make every slider in the pane a 0-to-10000 drag with every number that
matters inside the first two percent.

**Eight defs now ship above 130** (the six above, plus this checkpoint's two), and the proof asserts
the count so a new one cannot be added without the ceiling being considered.

---

## 5. Register rows read before building

`python tools/register-query.py use RR-DLC` returns **forty** rows. The instruction on all six
expansion rows is one sentence repeated:

> *"Add conditional definitions and code only for DLC-specific extensions; do not make a DLC
> feature the sole route through the campaign."*

Both families are additive by construction — each is one more reason a hauler or an artist may
cross, and the campaign never asks for either — so the base loop is untouched when every expansion
is absent, which is the condition that row cares about.

The rows sitting under the machines were read too. **51 Better Gene Inheritance**, **94 Force
Xenogerm Implantation**, **112 Inject Genes** and **114 Integrated Genes** all change what genes
*do*; nothing here reads a gene, a xenotype or a genepack's contents — the questions are *"is this
pack marked to auto-load"* and *"is there a bank with room"* — and `Building_GeneExtractor.CanAcceptPawn`
is Core's own, so a mod that changes which pawns have extractable genes changes Core's answer and
not one of ours. Their shared watch is *"check pawn health/custody state, treatment choice, and
transfer; preserve a vanilla fallback"*, and §1 above is that answer: no transfer occurs, and the
fallback is Core doing all of the work on arrival.

**39 Anomaly Research Asteroid** is optional off-site content whose watch asks that the no-DLC
campaign path keep working; it adds no holding-platform behaviour, and the containment routes match
`HoldingPlatformTarget` and `EntityHolder` by group, so a platform from any source is covered and
none is required. **140 Name Your Entities** is display naming only and reads nothing either
provider writes. For painting, `use RR-UI` and `family interface` carry the colour and style rows,
and none creates a seam: paint is terrain and building state, read from Core's own grids, and there
is no list of paints here to fall out of date.

None of those is a dependency, none is patched, and every one may be absent.

---

## 6. Files

**New:** `src/.../ConnectedWork/Providers/MachineLoadingProvider.cs`,
`src/.../ConnectedWork/Providers/PaintingProvider.cs`,
`.local/register/proof-machine-loading.py`, this record.

**Edited:** `src/.../ConnectedWork/ConnectedDeploymentProvider.cs` (two ids, two instances, two
registry rows), `src/.../ConnectedWork/WorkGiver_ConnectedDeployment.cs` (four giver classes),
`src/.../Core/ConnectedWorkPriorities.cs` (the per-giver ceiling), `src/.../Core/RimroomsMod.cs`
(the slider range), `1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml` (four defs),
`1.6/Languages/English/Keyed/RR_ConnectedWork.xml`, `1.6/Languages/English/Keyed/RR_Audio.xml`,
`CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `docs/NOW.md`, `docs/TODO.md`,
`docs/FINALIZED.md`, `docs/research/WORK_TYPE_COVERAGE_AUDIT.md`.

**No new gameplay content.** Four `WorkGiverDef`s and two keyed strings per family are the wiring
every existing family shipped with; no `ThingDef`, `PawnKindDef`, recipe, bench, item, texture or
sound was added.

## 7. Verification

* **Build 0.12.34-dev** — 182 C# files, 87 package files, **0 warnings, 0 errors**.
* **Assembly reproduced across two clean rebuilds.**
* **Eleven checkers pass. Thirty-one proofs exit zero.**
* **18 of 18 planted faults caught** — nine against the container family, nine against painting,
  including the one that matters most: removing `subject.Map != map` from the enterable route makes
  the custody claim fail.
* **No game was launched.** Every statement here is structural.
