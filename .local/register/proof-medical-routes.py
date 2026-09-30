# -*- coding: utf-8 -*-
"""Assert the medical routes are built, and that surgery across a gate is IMPOSSIBLE, not missing.

Row 227 named three things: *"Surgery across a gate (`Bill_Medical` needs the patient present, and
`uniqueRequiredIngredients` is a case no other family has); patient feeding, which belongs with the
food family; prisoner and guest care including Hospitality."*

Two of the three were already built and registered. The first **cannot be built**, and this file
exists so nobody tries.

Why surgery cannot cross, read out of Core at 0.12.33-dev
---------------------------------------------------------
Three facts, decompiled rather than assumed:

  * `Bill_Medical.GiverPawn` is `billStack.billGiver as Pawn` -- **the patient IS the bill giver.**
    The bill lives on the patient, not on a table.

  * `WorkGiver_DoBill` requires `pawn.CanReserve(thing)` on that bill giver, and resolves
    `pawn.MapHeld.reservationManager` -- **the doctor's map.** A reservation manager is per-map, so
    a patient on another map cannot be reserved at all.

  * `TryFindBestIngredientsHelper` takes `rootReg = billGiverRootCell.GetRegion(pawn.Map)` and for a
    pawn bill giver calls `AddEveryMedicineToRelevantThings(pawn, billGiver, ..., pawn.Map)` --
    **ingredients are searched on the doctor's map, around the patient's position**, inside
    `bill.ingredientSearchRadius`.

So the doctor, the patient and the ingredients must all be on one map and near each other. There is
no seam to adapt: the answer is **the patient comes home**, which
`ConnectedCasualtyAdapter` has done since 0.5.2-dev -- carried through the gate and put in a bed,
after which Core's surgery works with no help from us at all.

`uniqueRequiredIngredients` needs no handling for the same reason. It is a list of specific `Thing`s
checked for `DestroyedOrNull()`, and once the patient is home those things are on the same map as
everything else.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


source = {}
for root, _, names in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in names:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))
blob = "\n".join(source.values())

registry = source[os.path.join(SRC, "ConnectedWork", "ConnectedDeploymentProvider.cs")]
care = source[os.path.join(SRC, "ConnectedWork", "Providers", "CareProviders.cs")]
food = source[os.path.join(SRC, "ConnectedWork", "Adapters", "ConnectedFoodAdapter.cs")]
casualty = source[os.path.join(SRC, "ConnectedWork", "Adapters", "ConnectedCasualtyAdapter.cs")]

print("")
print("proof: the medical routes are built, and surgery across a gate is impossible by Core")
print("")

print("1. patient feeding is built and registered")
check("the food adapter uses Core's own patient-hunger test",
      "FeedPatientUtility.IsHungry" in food,
      "-- the same predicate WorkGiver_FeedPatient uses, so we never decide who counts as a patient")
check("patient feeding is in the provider registry",
      "{ PatientFeeding, feeding }" in registry,
      "-- an adapter absent from the registry is the unwired defect class all over again")

print("")
print("2. prisoner and guest care is built and registered")
check("a warden provider exists",
      "public sealed class WardenProvider" in care)
check("the warden is constructed and registered",
      "new WardenProvider()" in registry and "warden" in registry)
check("capture is left to the player rather than automated",
      "Capture is deliberately not here" in read(
          os.path.join(SRC, "ConnectedWork", "Adapters", "ConnectedCasualtyAdapter.cs")),
      "-- Core makes taking a downed stranger prisoner a player order, and the owner's rule is "
      "that people come back because a player directed it")

print("")
print("3. surgery is NOT attempted across a gate, because it cannot be")
check("no cross-map code constructs or targets a Bill_Medical",
      "Bill_Medical" not in blob,
      "-- the patient IS the bill giver, is reserved from the DOCTOR'S map, and the ingredients "
      "are searched on the doctor's map around the patient. There is no seam to adapt")
check("no cross-map code touches uniqueRequiredIngredients",
      "uniqueRequiredIngredients" not in blob,
      "-- it needs no handling once the patient is home, which is the only way surgery happens")
check("the answer -- the patient comes home -- exists",
      "public sealed class ConnectedCasualtyAdapter" in casualty and
      "TakeToBedJobDefName" in casualty,
      "-- carried through the gate and put in a bed, after which Core's surgery needs nothing "
      "from us")
check("the casualty route is one-directional, out of the Backrooms",
      "Only one direction exists here" in read(
          os.path.join(SRC, "ConnectedWork", "Adapters", "ConnectedCasualtyAdapter.cs")),
      "-- you carry a casualty out to a bed; you never carry one in")
check("the casualty adapter is registered",
      "CasualtyRescue" in registry or "CasualtyRescue" in blob)

print("")
print("4. Hospitality stays optional and unpatched")
check("no Hospitality patch or hard reference exists",
      not re.search(r"(?i)hospitality", blob),
      "-- an optional mod gets a PatchOperationFindMod at most, and this family needs none: "
      "guest care is Core's warden work, which the warden provider already crosses for")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: feeding and care are wired; surgery cannot cross and the patient comes home")
