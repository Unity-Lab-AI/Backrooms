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
| Hauling | 30 | Core/Ideology/Biotech/Anomaly | carry families + `hauling-upkeep` and `machine-loading` deployments | **Fully covered 0.12.34-dev** — the eleven DLC container givers closed, and none of them can move anything between maps |
| Handling | 8 | Core | `animal-handling` deployment, designation-driven | **Covered** |
| Research | 6 | Core/Biotech | `research` deployment | **Covered** |
| Childcare | 6 | Biotech | `childcare` deployment | **Covered** |
| BasicWorker | 6 | Core/Ideology | `basic-worker` deployment | **Covered 0.6.7-dev** |
| Crafting | 6 | Core/Anomaly | `bill-ingredients` carry | **Covered 0.6.5-dev** — bill work deployment |
| Smithing | 7 | Core/Biotech/Anomaly | `bill-ingredients` carry | **Covered 0.6.5-dev** — bill work deployment |
| Art | 5 | Core | `bill-ingredients` carry + `bill-work-art` and `painting` deployments | **Fully covered 0.12.34-dev** — painting is designation work, so it needed its own family; a bill lives on a bench and paint lives on a designation |
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
| **DarkStudy** | 1 | Anomaly | `dark-study` deployment | **Covered 0.6.6-dev** |
| **Fishing** | 1 | Odyssey | `fishing` deployment | **Covered 0.6.7-dev** |

**As of 0.6.7-dev: twenty-one work types have a deployment.** Two are decided against permanently. **No work-type gaps remain.** Every work type in Core and all five expansions is either covered or decided against with its reason recorded. Two of the original four were absent from the remembered list this audit replaced.

**As of 0.12.34-dev both remaining named gaps are closed.** The eleven DLC container hauling givers became `machine-loading`, and the custody review they were waiting on found that **Core forbids every one of them from moving anything between maps** — so the worker crosses and the subject is always already there. The four painting givers became `painting`, a second `Art` family, because `bill-work-art` asks whether a bench has a deliverable bill and paint is a designation on a floor or a wall.

**What remained was described as not buildable against an unknown:** a wholly mod-added work type gets no provider, because the providers and their giver defs are shipped rather than derived. The bill family already covers modded *benches* inside existing work types, and every capability-matched route added since covers modded *content* inside covered types.

**That premise was stale, and the section below replaces it.** The unknown was never unknown — the profile is 294 named mods and 288 of them are installed on disk. Measured 2026-10-05: **twelve of them add thirteen work types**, and one of the thirteen is covered by a shape this mod already has.

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

### 2. DarkStudy — BUILT 0.6.6-dev, and the most thematically apt thing in the audit

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

## The thirteen work types the 294 profile adds (2026-10-05)

**Why this section exists.** The families row's last remainder read *"a mod-added work type with its own givers... it cannot be built against a mod nobody has named."* Every mod in the profile **is** named — by the register, with a review card each — and 288 of the 294 are installed. So the claim was checkable, and checking it is cheaper than leaving a row open on it.

**Method.** Every `*.xml` under each installed profile mod was scanned for `<WorkTypeDef>`, and each resulting work type's `WorkGiverDef`s were read for their `giverClass`. Each giver class was then **decompiled against the installed assembly** with `.local/tools/ilspycmd.exe` to get its real base type. No base class here is inferred from a name.

| Work type | Mod (register row) | Giver class | Base type | Verdict |
|---|---|---|---|---|
| **MedicalTraining** | Medical Dissection (**274**) | `WorkGiver_DoDissectionBill` | **`WorkGiver_DoBill`** | **COVERED 0.12.99-dev** |
| NuclearWork | Dubs Rimatomics (83) | 5 givers, `WorkGiver_LoadFuelModule` and others | `WorkGiver_Scanner` | Not buildable generically |
| RimefellerCrafting | Rimefeller (194) | `WorkGiver_OperateResourceConsole` | `WorkGiver_Scanner` | Not buildable generically |
| HPGMGenerate | Human Power Generator (110) | `WorkGiver_HPGMcycling` | `WorkGiver_Scanner` | Not buildable generically |
| PrisonLabor_Jailor | Prison Labor (288) | `WorkGiver_Supervise`, `WorkGiver_HandleChains` | `WorkGiver_Warden` | Not buildable generically |
| QE_MaintainVat | Questionable Ethics Enhanced (182) | `WorkGiver_GrowerMaintenance` | `WorkGiver_Scanner` | Not buildable generically |
| Storefront_Selling | Hospitality: Storefront (286) | `WorkGiver_Sell`, `WorkGiver_StandBy` | `WorkGiver_Scanner` | Not buildable generically |
| CaptureThemCapture | Capture Them (60) | `WorkGiver_CapturePrisoners` | `WorkGiver_RescueDowned` | Not buildable generically |
| Diplomat | Hospitality (270) | `WorkGiver_Diplomat`, `WorkGiver_Recruiter` | `WorkGiver_Scanner` | Not buildable generically |
| Gastronomy_Waiting | Gastronomy (269) | 4 givers, `WorkGiver_TakeOrder` and others | `WorkGiver_Scanner` | Not buildable generically |
| MiscTraining_CombatTraining | Misc. Training (129) | `WorkGiver_Training` | `WorkGiver_Scanner` | Not buildable generically |
| FinishingOff | Allow Tool (30) | `WorkGiver_FinishOff` | `WorkGiver_Scanner` | Not buildable generically |
| HaulingUrgent | Allow Tool (30) | `WorkGiver_HaulUrgently` | `WorkGiver_Scanner` | Not buildable generically |

### The one that is covered, and why exactly one

`HMDissection.WorkGiver_DoDissectionBill` **derives from `WorkGiver_DoBill`**, and its giver def carries `fixedBillGiverDefs`. That is the whole requirement: `BillWorkProvider.BenchDefs` unions the `fixedBillGiverDefs` of every loaded `WorkGiverDef` whose giver class is assignable to `WorkGiver_DoBill`, so the bench set is a capability match against live data and **names nothing**.

So `MedicalTraining` needed one provider registration, one giver def pair and one label — and **no code anywhere referencing Medical Dissection**. `MedicalTraining` is a defName string through `GetNamedSilentFail`, exactly as `Cooking` is. Both defs carry `MayRequire="Heremeus.MedicalDissection"`, so without the mod the family is not in the game.

### Why the other twelve are not a backlog

They are `WorkGiver_Scanner`, `WorkGiver_Warden` or `WorkGiver_RescueDowned` subclasses. A deployment provider has to answer *is there work of my kind on that map* **against an explicit `Map`** — the provider contract forbids asking a native pawn-specific query about a map the worker is not standing on. The only generic candidate query available is `WorkGiver_Scanner.PotentialWorkThingsGlobal(pawn)`, and it reads `pawn.Map`, which is the one map the question is never about.

So each would need a hand-written candidate predicate reading that mod's own types, which is a code reference to a third-party assembly. `OPTIONAL_MOD_SUPPORT_POLICY.md` permits an optional adapter only *"against a documented, versioned extension point"*, and a `giverClass` is not one — it is an implementation detail with no stability promise.

**This is a closed decision, not a deferral.** It is recorded as a limit with its reason and the thirteen names, so the next reader does not re-derive it. If a mod later publishes a real extension point, that is a new row with new evidence.

### The register was read first, per the standing LAW

Row **274**, *Detention and subject casework*, traces `RR-STA;RR-EVD;RR-THREAT;RR-MP;RR-COMPAT`. Planned use: *"Use existing prisoner, capture, restraint, and medical systems"*. Final disposition: *"Optional; include in the owner-selected RWT candidate test profile"*. Nothing in the card forbids a provider, and nothing in the provider replaces, patches or copies anything of the mod's.

Row **83** (Dubs Rimatomics) and row **194** (Rimefeller) were already read when `BillWorkProvider` was written, and its header records the same conclusion this section reaches independently: *"a separate modded system is neither claimed nor broken. It simply is not this work."*

### And the measurement found a live defect beside the one it was looking for

Four families are `MayRequire`-gated — childcare on Biotech, dark study on Anomaly, fishing on Odyssey, and now medical training on a profile mod. `ConnectedWorkPriorities.Apply` had always skipped a family whose giver defs were absent. **The settings pane had not.** It iterated the family list unconditionally, so a player without Anomaly was shown a cross-gate dark-study priority slider, labelled with a shipped default of **0** because no def had ever loaded to read one from, and dragging it wrote an override keyed to a defName nothing carries.

Both now ask through one method, `TryGivers`, which is the single lookup site — the pane takes the verdict and the applier takes the defs. Two pieces of code asking the same question separately is what produced the phantom control, so the proof **counts** the lookups rather than testing for their presence.

## What this audit changes in the ledger

The families row closes on **joy and rituals decided, both no, with the reasons recorded above.** It does not close on completeness: four gaps are named here with their evidence, and they are new rows because the enumeration found work the remembered list did not contain. That is the rare case the TODO rules allow for — new information, not a restatement.
