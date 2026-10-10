# -*- coding: utf-8 -*-
"""Ledger for 0.12.33-dev: surgery cannot cross, and three things were invisible."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def sub(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    write(rel, s.replace(old, new, 1))


sub('CHANGELOG.md', u'## 0.12.32-dev', u"""## 0.12.33-dev - 2026-09-29 - three things you could not see

- **You can send somebody through a gate from the gate itself now.** Select who you mean, click the door, pick them off the list. Anyone who cannot cross is listed with the reason instead of being left out.
- **Every coordinate now tells you how hostile it is** - quiet, unsettled, active or hostile. The game has always known; it never said.
- **Selling everything at a credit beacon asks first.** It is a large, irreversible action and the only warning used to be text you read after clicking.
- **Surgery on a crew member always happens at home, and now that is written down as a rule rather than a gap.** The base game needs the patient, the doctor and the medicine in one place, so a casualty is carried back through the gate to a bed - which the rescue work has always done.
- **Patient feeding and prisoner care across a gate were already working.** Checked rather than assumed.

Full record: [surgery cannot cross, and three things were invisible](docs/implementation/MEDICAL_AND_SURFACES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.32-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - surgery cannot cross, and three things were invisible (0.12.33-dev)

**Verbatim user quote:** *"get to it lets pic up the pace more code work less fluff flattery"*

### What shipped

Four rows closed: 227 by proof, and 889 / 1010 / 832 by adding the surface each was missing.

### Files touched

`src/.../Portals/DoorCrossingGizmo.cs` **new**, `src/.../Gate/CompRimroomsGate.cs`, `src/.../Portals/CompRimroomsEmergence.cs`, `src/.../Economy/CompRimroomsCreditBeacon.cs`, `src/.../Threats/CoordinatePressureLadder.cs`, `src/.../UI/MainTabWindow_Operations.cs`, `1.6/Languages/English/Keyed/RR_Portals.xml`, `1.6/Languages/English/Keyed/RR_Company.xml`, `.local/register/proof-medical-routes.py` **new**, `.local/register/proof-three-surfaces.py` **new**, `docs/implementation/MEDICAL_AND_SURFACES_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **SURGERY ACROSS A GATE CANNOT BE BUILT, read out of Core rather than assumed.** `Bill_Medical.GiverPawn` is `billStack.billGiver as Pawn`, so **the patient IS the bill giver**; `WorkGiver_DoBill` reserves it through `pawn.MapHeld.reservationManager`, and a reservation manager is per-map, so **a patient on another map cannot be reserved at all**; and `TryFindBestIngredientsHelper` takes `rootReg = billGiverRootCell.GetRegion(pawn.Map)` and calls `AddEveryMedicineToRelevantThings(pawn, billGiver, ..., pawn.Map)`, so **ingredients are searched on the doctor's map around the patient's position**. Doctor, patient and ingredients must be co-located. **There is no seam to adapt**: the answer is that the patient comes home, which `ConnectedCasualtyAdapter` has done since 0.5.2-dev. `uniqueRequiredIngredients` needs no handling for the same reason - the row called it *"a case no other family has"*, and it is a case no family needs.
- **The other two items in row 227 were already built and registered**, checked rather than assumed: patient feeding through `FeedPatientUtility.IsHungry` with `PatientFeeding` in the provider registry, and prisoner and guest care through a `WardenProvider` that is constructed and registered. **Hospitality needs nothing at all** - guest care is Core's warden work, which that provider already crosses for, so there is no patch and no reference to an optional mod. **Row 227 was stale-open.**
- **Three surfaces added over machinery that already worked, and the risk in each was the same:** closing a presentation gap can introduce a **second opinion beside the rule it presents**. The proof asserts against that for all three.
- **889:** the beacon sale now opens `Dialog_MessageBox.CreateConfirmation` naming the count and total and saying it cannot be undone. **`SellValuables` is untouched** - a confirmation must not become a second place that decides what sells.
- **1010:** `CoordinatePressureLadder.BandFor` has decided how hostile a space is since 0.8.4-dev, drives anomaly events and gates incursion, and **had never been shown to anybody** - learnable only by being hurt by it, which is the opposite of invariant 28. Now a row per coordinate. The pane calls `BandFor` and prints; **the ladder still decides**. Label keys are literals, because an assembled key cannot be checked and this project has caught that five times.
- **832:** the crossing order is on the door. **Invariant 1 was the thing at risk** - `PortalTraversalPolicy` is the only traversal chokepoint, and a gizmo deciding eligibility for itself is how a chokepoint stops being one. So it asks `RimroomsPortalCrossingService.EligibilityFailureKey` and orders through `PortalTravelService.OrderCrossing`, and the proof asserts it holds **no** eligibility rule of its own. A pawn who cannot cross is **listed with the reason** rather than hidden, because *drafted* and *prisoner* are things a player needs told. It appears on a designated gate and on a natural way out, because both are doors.
- **A FAULT PLANT CAUGHT A BLIND CLAIM OF MINE.** The first version of *"the readout is wired into the coordinate row"* checked that `RR_UI_CoordinateBand` **appeared** in the pane. Planting `listing.Label(` to `Nothing(` left the key in place and **the claim passed while the row was not drawn at all.** Tightened to assert the whole call and re-planted: caught. **A claim that searches for a string is not a claim about behaviour**, which is the entire reason fault-planting is not optional.
- Build 0.12.33-dev, **180 C# files, 87 package files**, **0 warnings, 0 errors**. Assembly `B7EA5785E49DD0B8F123A560C3752AC86F7D213FA74476A0FF720E9E389908C6`, identical across two clean rebuilds. Eleven checkers pass, **thirty** proofs exit zero, **6 of 6** planted faults caught. **No game was launched.**

---

## Completed sessions""")

print('ledger written for 0.12.33-dev')
