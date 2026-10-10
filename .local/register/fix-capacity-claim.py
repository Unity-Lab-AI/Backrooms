# -*- coding: utf-8 -*-
"""The capacity claim asserted a string that appears twice. Count it.

`plant-gate-circuit.py` reported MISSED on *"the capacity readout narrows back to one battery"*.
The claim read:

    "List<CompPowerBattery> batteries = net.batteryComps;" in binding

and that line appears **twice** -- once in `NativeBatteryCapacity` and once in
`DrawFromNativeCircuit`. The plant replaced the first, the second stayed, and `in` found it. **The
claim held while the capacity readout was gutted.**

**Third instance of the duplicate-string trap in one session**, and the fourth overall:

* 0.12.75-dev -- the bond label expression appeared in `LabelNoCount` and `LabelNoParenthesis`, so
  a plant that gutted the first left the second and no bond was named while the claim held.
* earlier today -- `"Pawn" not in register` was a substring test wearing a type test's clothes.
* and this.

The fix is the one the bond claim took: **count, do not test presence.** Two is the number, and
the comment above it says why, so a third copy appearing is a failure that explains itself.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-circuit.py")

OLD = u'''check("and the capacity readout is the circuit's, not one battery's",
      "List<CompPowerBattery> batteries = net.batteryComps;" in binding
      and "float most = battery.Props.storedEnergyMax;" in binding,
      "-- the number a player reads has to be about the circuit they built, not whichever "
      "battery they clicked first")'''

NEW = u'''check("and the capacity readout is the circuit's, not one battery's",
      # **BOTH OCCURRENCES, COUNTED.** This line is in `NativeBatteryCapacity` and in
      # `DrawFromNativeCircuit`, so an `in` test held while the capacity reader was gutted and
      # the plant went MISSED. Duplicate-string trap, third instance this session. A third copy
      # appearing is a failure, and it should be: whoever adds one has to say which is which.
      binding.count("List<CompPowerBattery> batteries = net.batteryComps;") == 2
      and "float most = battery.Props.storedEnergyMax;" in binding
      and "if (net == null) { return 0f; }" in binding,
      "-- the number a player reads has to be about the circuit they built, not whichever "
      "battery they clicked first")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u'"List<CompPowerBattery> batteries = net.batteryComps;" in binding' in after:
    failures.append("the presence test is still there")
if u'== 2' not in after:
    failures.append("the count was not written")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("the capacity claim counts both occurrences instead of testing for one")
