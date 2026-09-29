# Tending across a gate: the doctor travels, and the medicine travels (0.5.9-dev)

**Baseline:** `742bdd6` (0.5.8-dev, 102 C# files, 76 package files).

**This checkpoint — 0.5.9-dev:** **104 C# source files**, **76 approved package files** (unchanged — four work giver defs and five keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `AE6BD0CCE437253568FCD54B45490EB969E66CF9086905836B807691A4848014`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/connected-tending-2026-09-28/`](evidence/connected-tending-2026-09-28/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## One TODO item, and everything it needed

The owner's instruction for this checkpoint:

> get to it all working through the todo and documenting work in the rair case adding an item to it if needed but in most cases you will do the todo work item and all relaeted work needed for that item as that item in the todo

So the register row *"Tending across a gate — a doctor crossing to a patient who stays put, or medicine carried to them"* was closed as **one item covering both halves**, rather than split into a new row. Two families ship here:

| Half | Shape | What it is |
|---|---|---|
| **Doctor travels** | deployment — third `ConnectedDeploymentProvider` | `TendingProvider`. Patient stays exactly where they are; the doctor crosses. |
| **Medicine travels** | carry — seventh adapter | `ConnectedMedicineAdapter`. The first family whose cargo is **consumed by the work**. |

Both were built, both are in the settings screen, and no new record, driver or `JobDef` was needed for either.

## Why the patient stays put

This is not a duplicate of the casualty family. 0.5.2-dev carries our own *downed* people home to a bed. This carries nobody: a patient already lying in a bed on the far side should be treated *there*, and hauling them through a gate first would be strictly worse for them.

## The doctor half fits the deployment shape almost perfectly

Core's own `WorkGiver_Tend.HasJobOnThing` turns out to be **almost entirely patient-side**, with the reservation as the only doctor-specific question. That is unusually convenient and it was checked, not hoped for:

| Rule | Reads | Asked remotely? |
|---|---|---|
| `map.mapPawns.SpawnedPawnsWithAnyHediff` | the explicit map — Core's own accessor in `PotentialWorkThingsGlobal` | yes |
| `HealthAIUtility.ShouldBeTendedNowByPlayer` | the patient's `medCare`, prisoner execution mode, slaughter designation, own hediffs | yes |
| `WorkGiver_Tend.GoodLayingStatusForTend` | for a humanlike who is not the doctor, reduces to `patient.InBed()` | yes |
| mutant medical-care entitlement | the patient's `mutant.Def` | yes |
| aggro mental state, unless scaria | the patient's mind and hediffs | yes |
| `pawn.CanReserve(patient)` | the doctor's map and reservation manager | **no — arrival only** |

Because `GoodLayingStatusForTend` requires a humanlike patient to be **in bed**, a doctor is never sent through a gate for somebody merely walking around injured. That falls out of matching Core rather than needing a rule of our own.

## The medicine half hangs on one Core fact

`HealthAIUtility.FindBestMedicine` searches:

```
patient.MapHeld.listerThings.ThingsInGroup(ThingRequestGroup.Medicine)
```

**The patient's map — not the doctor's.** So getting medicine onto the patient's map is exactly and only what is required; the doctor then finds it through Core's own search with no help from us. And unlike a bill there is no radius to respect: Core's search is map-wide, so any storage that map accepts will be found.

### Medicine is optional to tending, and that shapes the family

`WorkGiver_Tend.JobOnThing` falls through to `MakeJob(TendPatient, patient)` with **no medicine at all** when none is found. So this family never decides *whether* somebody is treated — only how well. A trip that arrives late has cost a walk; a trip that never happens still leaves the patient tended. That is worth stating plainly because it sets the correct urgency: valuable, never critical.

### Three patient-side rules honoured rather than reinvented

- A patient whose `medCare` is `NoCare` or `NoMeds` wants no medicine — `FindBestMedicine` returns null outright for both — so nothing is carried for them.
- `Medicine.GetMedicineCountToFullyHeal(patient)` is the count. Never a number of ours.
- `medCare.AllowsMedicine(def)` decides which medicine qualifies, so a patient set to herbal-or-worse never has glitterworld medicine hauled across a gate for them.

### A throwing-call trap caught

`MedicalCareUtility.AllowsMedicine` is a `switch` expression whose default arm **throws `InvalidOperationException`** rather than returning false. An unexpected `MedicalCareCategory` — from a mod, or a corrupted save — would therefore have thrown from inside a work-giver scan. It is guarded with `Enum.IsDefined` and an undefined value is treated as "no medicine", per the standing rule that a bad lookup is an unavailable action and never an exception.

### Shortage counted across every allowed medicine

The same mistake the bill family avoided: presence is counted across **every** medicine def the patient's care setting allows, not just the one being considered. A patient with plenty of herbal medicine beside them is short of nothing, and counting only industrial medicine would have sent somebody across a gate for nothing, repeatedly, because the situation is stable.

## What the prep work supplied

Per the owner's standing rule, the profile's medical rows were read from their existing reviews first. Nine were relevant; these carry the load:

| Row | Mod | What its review establishes | Effect here |
|---|---|---|---|
| **209** | Smart Medicine | Sources medicine from pawn and patient **inventories**, adds field tending, per-injury settings that do not persist | The one that matters most. With it installed a doctor may already have medicine in hand, making our trip unnecessary — which is **harmless**, because the shortage test counts only what is on the patient's map and Core simply tends from the inventory without consulting our delivery. |
| **193** | ReTend | Re-tend to a chosen quality; a player-ordered convenience | No interaction with automatic work. |
| **225** | TendYourself | Downed pawns self-tend bleeding wounds | Independent of both halves; a patient may simply stop needing tending, which both halves already handle as a completed trip. |
| **126** | Medical IVs Fork | IV drips | No work-giver interaction established. |
| **113** | Injured Carry | Rescuing injured non-downed pawns | Adjacent to the casualty family, not this one. |
| **109** | Hospital | Drop-pod patients requesting care | Its review explicitly says the base facility must provide its own medical route and not tie company progress to this visitor event. |
| **34** | Animal Medical Bed | Animal medical beds | Covered by matching Core, which tends animals through its own giver. |

Every one carries the same recorded disposition: **optional, no Rimrooms adapter, must work with the mod absent, do not copy code.** Both halves satisfy that by construction — the deployment half because it never issues the tend job, and the carry half because it only moves goods and never touches how tending chooses or applies them.

## Priorities

Two work types, because the two halves *are* two kinds of work.

Core `Doctor`: `110` TendEmergency, `100` TendToHumanlikes, `90` TendToSelf, `80` FeedHumanlikes, `70` MedicalOperation, `65` FeedHemogen, `60` Rescue, `50` TendToAnimals, `40` FeedAnimals, `30` AnimalOperation, `20` TakeToBedToOperate, `10` VisitSickPawn.

| Giver | Work type | Priority | Why there |
|---|---|---|---|
| `RR_ConnectedTendingContinue` | Doctor | **102** | Above routine local tending, so a doctor partway to a gate is not turned around by an ordinary patient at home — but **below a local emergency (110)**, which must always win. That ordering is the medically correct one and it is deliberate. |
| `RR_ConnectedTending` | Doctor | **5** | Below every Core doctor giver including visiting the sick. A doctor crosses only when there is no doctoring at all on this side. |
| `RR_ConnectedMedicineContinue` | Hauling | **13** | Above construction's 12 and bills' 11. |
| `RR_ConnectedMedicine` | Hauling | **9** | Above construction's 8 and bills' 7: a patient needing medicine outranks a stalled build or a stalled bench. Still well below Core's `HaulGeneral` (15). |

Sixteen cross-gate numbers now, all player settings, tunable live.

## Saved state

**None added.** The medicine adapter records the patient in the intent's existing `finalTarget` field — which is what that field has been for since schema 1, "the native object the work finally belongs to" — and reuses `RecordResolvedCellForTarget` so the patient is not erased when the delivery cell is chosen. The deployment half adds nothing at all. A 0.5.8-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key referenced from source resolves with 0 missing; every `giverClass` resolves to a real class.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Not done, and named — the rest of the medical routes

The pinned review warned that surgery, prisoner and guest care, patient feeding and self-tend are **each a distinct native route**, and that remains true. What shipped here is *tending* and *medicine for tending*. Still open, each needing its own source review before being claimed:

- **Surgery across a gate.** `DoBillsMedicalHumanOperation` is a `Bill_Medical` on a patient, which the bill family explicitly skips because a surgery needs the patient present. Cross-gate surgery would be a deployment plus a medical-bill supply, and `Bill_Medical.uniqueRequiredIngredients` adds a case nothing else has.
- **Patient feeding** (`DoctorFeedHumanlikes`, `DoctorFeedAnimals`) — belongs with the food family, not this one.
- **Prisoner and guest care**, including Hospitality's guest patients.
- **Self-tend** is by definition local and needs nothing from this layer.

Next in the queue: **food**, then **rest**, then the remaining families. Then the 1990s period and the universe factions.

## For the post-completion test phase

Opening a gate with an injured colonist in a bed on the far side and no doctor there, and confirming a doctor crosses and treats them; confirming a doctor does **not** cross while any doctoring remains at home, and that a local *emergency* still interrupts a doctor who is only partway to the gate; confirming an injured pawn who is not in a bed does not attract a doctor through a gate; confirming medicine is carried when the patient's side has none, and is **not** carried when the patient is set to no-meds or already has enough allowed medicine nearby; confirming a patient on herbal-or-worse never receives glitterworld medicine; confirming a patient who recovers or self-tends mid-carry results in the medicine being set down rather than lost; and — with rows 209, 193, 225, 126, 113, 109 and 34 active — confirming each behaves as its review predicts, and that removing all of them changes nothing about either half.
