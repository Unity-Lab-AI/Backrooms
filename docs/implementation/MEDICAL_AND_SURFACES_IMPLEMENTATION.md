# Surgery cannot cross, and three things were invisible — 0.12.33-dev, 2026-09-29

**Dated record.** Never rewritten. Four rows closed: one by proof, three by surface.

---

## Row 227: the medical routes were already built, and surgery cannot be

The row named three things. **Two were built and registered.** The third **cannot be built**, and
the proof exists so nobody tries.

### Surgery across a gate is impossible, read out of Core

Three facts, decompiled rather than assumed:

| Fact | Consequence |
|---|---|
| `Bill_Medical.GiverPawn` is `billStack.billGiver as Pawn` | **the patient IS the bill giver** — the bill lives on the patient, not a table |
| `WorkGiver_DoBill` calls `pawn.CanReserve(thing)` on it and resolves `pawn.MapHeld.reservationManager` | a reservation manager is per-map, so **a patient on another map cannot be reserved at all** |
| `TryFindBestIngredientsHelper` takes `rootReg = billGiverRootCell.GetRegion(pawn.Map)`, and for a pawn bill giver calls `AddEveryMedicineToRelevantThings(pawn, billGiver, ..., pawn.Map)` | **ingredients are searched on the doctor's map, around the patient's position**, inside `ingredientSearchRadius` |

Doctor, patient and ingredients must all be on one map and near each other. **There is no seam to
adapt.** The answer is that the patient comes home — which `ConnectedCasualtyAdapter` has done since
0.5.2-dev, carrying a downed person through the gate and putting them in a bed, after which Core's
surgery needs nothing from us.

`uniqueRequiredIngredients` needs no handling for the same reason: it is a list of specific `Thing`s
checked for `DestroyedOrNull()`, and once the patient is home those things are on the same map as
everything else. **The row called it "a case no other family has"; it is a case no family needs.**

### The other two were already done

- **patient feeding** — `ConnectedFoodAdapter` uses `FeedPatientUtility.IsHungry`, the same
  predicate `WorkGiver_FeedPatient` uses, and `PatientFeeding` is in the provider registry.
- **prisoner and guest care** — `WardenProvider` exists, is constructed, and is registered.
  **Hospitality needs nothing**: guest care is Core's warden work, which that provider already
  crosses for, so there is no patch and no reference to an optional mod.

**Row 227 was stale-open.** The batch audit that found it is why the remaining rows get checked
against the code before anything is written for them.

---

## Three surfaces over machinery that already worked

The risk in a presentation gap is not that it stays open. It is that **closing it introduces a
second opinion beside the rule it is presenting.** All three were written to avoid that, and the
proof asserts it for each.

### 889 — the beacon sale is confirmed

Selling everything inside the radius is large and irreversible, and the gizmo's description was the
only warning — read *after* the click. Now `Dialog_MessageBox.CreateConfirmation`, naming the count
and the total, and saying it cannot be undone. **`SellValuables` is untouched**: a confirmation must
not become a second place that decides what sells.

### 1010 — the coordinate's band is visible

`CoordinatePressureLadder.BandFor` has decided how hostile a space is since 0.8.4-dev. It drives
anomaly events and gates incursion, and **had never been shown to anybody.** Invariant 28 wants
every rule learnable; this one was learnable only by being hurt by it.

Now a row under each coordinate: *quiet · unsettled · active · hostile*. The pane calls `BandFor`
and prints — **the ladder still decides.** Label keys are literals, not built from the enum name,
because a key assembled at run time cannot be checked and this project has caught that five times.

### 832 — the crossing order is on the door

The row was precise about being presentation: *"The capability is done... What is outstanding is
surfacing the order and its reason on the door itself."*

**Invariant 1 was the thing at risk**: `PortalTraversalPolicy` is the only traversal chokepoint, and
a gizmo deciding eligibility for itself is exactly how a chokepoint stops being one. So the gizmo
asks `RimroomsPortalCrossingService.EligibilityFailureKey` and orders through
`PortalTravelService.OrderCrossing`, and the proof asserts it contains **no** eligibility rule of
its own — no `IsPrisoner`, no `Drafted`, nothing.

A pawn who cannot cross is **listed with the reason** rather than hidden: *drafted* and *prisoner*
are things a player needs told, and a name missing from a menu says neither. It appears on a
designated gate and on a natural way out, because both are doors.

---

## A fault plant caught a blind claim of mine

The first version of *"the readout is wired into the coordinate row"* checked that
`RR_UI_CoordinateBand` **appeared** in the pane. Planting `listing.Label(` → `Nothing(` left the key
in place and **the claim passed while the row was not drawn at all.**

Tightened to assert the whole call, `listing.Label("RR_UI_CoordinateBand".Translate(`, and
re-planted: caught. **A claim that searches for a string is not a claim about behaviour** — which
is the entire reason fault-planting is not optional.

| Planted fault | Exit | Caught |
|---|---|---|
| the sale stops being confirmed | 1 | ✓ |
| band keys get assembled at run time | 1 | ✓ |
| **the band readout stops being drawn** | 1 | ✓ *after the claim was fixed* |
| the gizmo decides eligibility itself | 1 | ✓ |
| a refused pawn is hidden instead of explained | 1 | ✓ |
| the menu stops being sorted | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.33-dev |
| Build | **180 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `B7EA5785E49DD0B8F123A560C3752AC86F7D213FA74476A0FF720E9E389908C6`, identical across two clean rebuilds |
| Rows closed | **four** — 227 by proof, 889 / 1010 / 832 by surface |
| New rules introduced | **none.** Every decision still lives where it lived |
| Proofs | **thirty**, all exiting zero |
| Checkers | **eleven**, all passing |
| Planted faults caught | **6 of 6**, one of which exposed a blind claim first |
| Game launched | **no** |
