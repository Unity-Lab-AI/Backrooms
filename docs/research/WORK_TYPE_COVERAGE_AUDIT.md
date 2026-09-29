# Work type coverage audit — every work type in Core and all five DLC (2026-09-29)

**Why this exists.** The families row in `TODO.md` listed the remaining work families from memory: *"cleaning, repair, firefighting, plants/mining/hunting, prisoner and guest care, wardening, childcare, animals and mechs, refuel and rearm, joy, rituals, hauling providers."* Closing the last two names on that list — joy and rituals — would have closed the row. So before closing it, the list itself was checked against the shipped game data.

**The list was incomplete.** Two work types are missing from it entirely, and both are real: `DarkStudy` and `Fishing`. Neither appears anywhere in the mod's source. A row closed on the strength of that list would have been closed wrongly.

This audit replaces the remembered list with an enumeration, so the families question is answered once and for all against what the game actually ships.

## Method

Every `WorkGiverDef` in `Data/*/Defs/**/*.xml` across Core, Royalty, Ideology, Biotech, Anomaly and Odyssey was parsed and grouped by its `workType`. Result: **23 work types, 145 work giver defs.** Coverage was then read out of the mod's own source — `ConnectedDeploymentProviders` for the deployment ids and each provider's `WorkType` property for what it answers about, `ConnectedWorkAdapter` for the carry families.

No claim here rests on memory. Where a decision turns on a Core fact, the fact is quoted.

## The 23 work types

| Work type | Givers | DLC | Mod coverage | Verdict |
|---|---|---|---|---|
| Construction | 15 | Core | `construction-finishing`, `repair` deployments + `construction-supply` carry | **Covered** |
| Doctor | 14 | Core/Biotech/Anomaly | `tending`, `patient-feeding`, `rescue-in-place` deployments + `medicine-supply` carry | **Covered** |
| Warden | 18 | Core/Ideology/Biotech/Anomaly | `warden` deployment + `food-supply` carry reaches prisoners | **Covered** |
| Hauling | 30 | Core/Ideology/Biotech/Anomaly | `storage-hauling`, `casualty-rescue`, `fuel-supply` carry | **Partly** — see below |
| Handling | 8 | Core | `animal-handling` deployment, designation-driven | **Covered** |
| Research | 6 | Core/Biotech | `research` deployment | **Covered** |
| Childcare | 6 | Biotech | `childcare` deployment | **Covered** |
| BasicWorker | 6 | Core/Ideology | none | **Gap — candidate** |
| Crafting | 6 | Core/Anomaly | `bill-ingredients` carry | **Covered 0.6.5-dev** — bill work deployment |
| Smithing | 7 | Core/Biotech/Anomaly | `bill-ingredients` carry | **Covered 0.6.5-dev** — bill work deployment |
| Art | 5 | Core | `bill-ingredients` carry + `bill-work-art` deployment | **Covered 0.6.5-dev** for sculpting; painting remains a candidate |
| Cooking | 4 | Core | `bill-ingredients` carry | **Covered 0.6.5-dev** — bill work deployment |
| Growing | 4 | Core | `growing` deployment | **Covered** |
| Cleaning | 3 | Core/Biotech | `cleaning` deployment | **Covered** |
| PlantCutting | 3 | Core/Ideology | `plant-cutting` deployment | **Covered** |
| Mining | 2 | Core | `mining` deployment | **Covered** |
| Patient | 2 | Core | none | **Decided: never** |
| Firefighter | 1 | Core | `firefighting` deployment | **Covered** |
| Hunting | 1 | Core | `hunting` deployment | **Covered** |
| Tailoring | 1 | Core | `bill-ingredients` carry | **Covered 0.6.5-dev** — bill work deployment |
| PatientBedRest | 1 | Core | none | **Decided: never** |
| **DarkStudy** | 1 | Anomaly | **none** | **Gap — candidate, and the most on-theme of them** |
| **Fishing** | 1 | Odyssey | **none** | **Gap — candidate, lowest value** |

**As of 0.6.5-dev: seventeen work types have a deployment.** Two are decided against permanently. **Three genuine gaps remain** — `DarkStudy`, `BasicWorker` and the local-container half of `Hauling`, with `Fishing` a generation question before it is a work question. Two of the original four were absent from the remembered list this audit replaced.

## The two decided against, permanently

`Patient` and `PatientBedRest` are a pawn's own medical self-care — going to bed for treatment, for emergency treatment, to recuperate. Two invariants already forbid reaching into them, and both were established from source:

- **Needs are not work, and this layer does not reach into them.** A closing gate that stranded a pawn on its way to a bed is a dead colonist.
- **A bed is only ever a bed on its own map.** `CanUseBedNow` returns false when the bed's map differs from the sleeper's `MapHeld`.

So there is nothing to build, and the right record is a closed decision rather than an open row.

## Joy: decided, no family

Joy has **no work type at all**. The enumeration above is the proof — 23 work types, and `Joy` is not among them. Joy is a need served from the think tree:

```csharp
public class JobGiver_GetJoy : ThinkNode_JobGiver
{
    protected override Job TryGiveJob(Pawn pawn)
    {
        ...
        if (pawn.needs.joy.CurLevel >= 0.99f) { return null; }
```

`JobGiver_GetJoy` reads `pawn.needs.joy` and picks a `JoyGiverDef`. There is no work giver, no priority, and nothing for a work adapter to attach to. The needs invariant applies to it exactly as it applied to food and to rest, and for the same reason: a pawn crossing a gate to relax is a pawn who can be stranded on the far side by a closing gate while its recreation need is what sent it.

**Decided: no joy family. Solve recreation logistically** — the furniture the far site needs is delivered by the existing construction and storage families, and a colonist takes its recreation on whichever map it is standing on.

## Rituals: decided, no family

No `WorkGiverDef` anywhere in Core or any of the five DLC is ritual-driven. The only work giver in the whole set whose name suggests gathering is `HelpGatheringItemsForCaravan`, which is caravan loading and belongs to `Hauling`.

Rituals are driven by a `Lord`: a `LordJob_Ritual` owns its participants' duties for the ritual's whole duration, and a pawn under a lord duty is not being offered jobs by work givers at all. So there is no seam here even in principle — this layer never sees a ritual participant, and cannot send one anywhere.

**Decided: no ritual family.** One thing does deserve a runtime check rather than a mechanism: a colonist that already holds a live cross-map commitment and is then pulled into a ritual. The commitment should be released when its job ends, which `ValidateSavedState` is responsible for; that it does so in this specific case is a test-phase confirmation, recorded as such and not asserted here.

## The four gaps, in the order worth building them

### 1. Bill work — BUILT 0.6.5-dev, and the one the bills record left open

`CONNECTED_BILLS_IMPLEMENTATION.md` settled the carry half completely: ingredients cross a gate to a bill that `ShouldDoNow()`. It never decided **who runs the bill once the material is there**, so a bench on a coordinate with no staff standing on it accumulated ingredients and produced nothing.

The Core fact that record pins argues *for* a deployment rather than against one:

- `WorkGiver_DoBill.ClosestUnfinishedThingForBill` validates `((UnfinishedThing)t).Creator == pawn`.
- `Bill_ProductionWithUft` binds `BoundUft` to a `BoundWorker`, and only that worker resumes it.

A half-made thing belongs to one colonist, which is why the *carry* family must never touch one. But a **deployed** worker stands on the bill's own map and runs Core's own `WorkGiver_DoBill` locally — creating and finishing its own unfinished thing, on one map, exactly as Core intends. The deployment shape sidesteps the trap by construction rather than working around it.

**Built as five families rather than one**, which this audit got wrong when it predicted a single family. `WorkGiver_DoBill.StartOrResumeBillJob` compares `bill.recipe.requiredGiverWorkType` against `def.workType`, and a bench belongs to a work type only through `WorkGiverDef.fixedBillGiverDefs` — so one provider declaring one work type would have pulled a cook across a gate for smithing. Cooking, Crafting, Smithing, Tailoring and the sculpting half of `Art` each got their own. Record: `implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md`.

### 2. DarkStudy — one giver, and the most thematically apt thing in the audit

Anomaly ships exactly one: `StudyInteract` / `WorkGiver_DarkStudyInteract`, priority 110. Studying a contained entity on a holding platform is what this mod's company *does*, and a containment facility reached through a portal is the premise. `WorkTypeDefOf` carries it as `[MayRequireAnomaly]`, so it gates cleanly through `GetNamedSilentFail` the same way `Childcare` does for Biotech.

### 3. BasicWorker — `Flick` is the useful one

Six givers: `Flick`, `Open`, `EjectFuel`, `ExtractSkull`, `ChangeTreeMode`, `BasicReleasePrisoner`. `Flick` is designation-driven, which puts it with the fieldwork families where nothing is inferred, and toggling a switch on a far map is a real thing a player asks for and cannot currently get. `Open` is likewise a designation on a specific container.

### 4. Fishing — lowest value, and it may not apply at all

Odyssey ships one giver, `WorkGiver_Fish`, gated `[MayRequireOdyssey]`. It needs water on the map. Whether a generated Backrooms coordinate ever has fishable water is a generation question, not a work question, and the answer may simply be no — in which case the honest record is that the family is unnecessary rather than unbuilt. Settle the generation question first.

## What painting still needs

`Art` is covered for sculpting, which is `WorkGiver_DoBill` work. Its other four givers — `PaintBuilding`, `PaintFloor`, `RemovePaintBuilding`, `RemovePaintFloor` — are not bill work at all and remain uncovered. They are designation-driven, which puts them with the fieldwork families where nothing is inferred, and they belong with the `BasicWorker` gap rather than with bills.

## Hauling, and why it is only partly covered

Thirty givers, the largest work type in the game. The carry families cover the direction that needs a gate crossed: material moving from one map to another. What has no coverage is the set of givers that are **local container operations on the far map** — `EmptyEggBox`, `FillFermentingBarrel`, `TakeBeerOutOfFermentingBarrel`, `EmptyWasteContainer`, `HaulMechsToCharger`, `UnloadCarriers`, `TakeBioferriteOutOfHarvester`. Each needs a worker standing there, not material carried across.

This is the same shape as the bill gap and would be solved the same way. It is listed second in priority behind bills because bills are what a player actually notices stalling.

## Mechs

The remembered list said *"animals and mechs"*, and the animal half shipped as `animal-handling`. The mech half is not a separate work type: mech work sits inside `Smithing` (`RepairMech`, `DoBillsMechGestator`, `DoBillsSubcoreEncoder`), `Hauling` (`HaulMechsToCharger`) and `Research` (`CreateXenogerm`). So it is covered exactly to the extent those three are — gestation and encoding by the bill families, `RepairMech` and `HaulMechsToCharger` not at all. Both fall inside gaps 1 and the hauling paragraph above; neither needs a family of its own.

## What this audit changes in the ledger

The families row closes on **joy and rituals decided, both no, with the reasons recorded above.** It does not close on completeness: four gaps are named here with their evidence, and they are new rows because the enumeration found work the remembered list did not contain. That is the rare case the TODO rules allow for — new information, not a restatement.
