# -*- coding: utf-8 -*-
"""The gate's reserve is the whole circuit, and a refusal names the real cause.

Why this proof exists
---------------------
Owner, 2026-10-01, from a running game: *"its the same problem as before: the laboratory address
for that is not open.... thats just clicking on the portal and trying to send them through not
working,,, and using operations clicking send pawns through which i think is a power porblem but
you can check the game current running,, looks like only being able to connect 1 battery isnt
anough and there should be no loimit"*.

**`grep -l` across forty-eight proofs for `NativeStoredEnergy`, `HasUsablePortalWindow` and
`ReturnReserveStored` returned nothing.** Not one claim had ever been made about the energy the
gate runs on, which is why a defect this central reached the owner in play.

Two defects, one blind spot:

* **The reserve was one battery.** `nativeBattery` is the anchor that identifies the gate's
  circuit, and `NativeGenerationWatts` has always summed the whole net while
  `NativePowerConnected` has always checked it. **Stored energy was the one reading that never
  followed.** Worse, `TrySpendNativeEnergy` refused outright when that single battery could not
  cover a cost -- so a drained anchor stalled a gate with ten full batteries beside it.
* **The refusal named the wrong thing.** `HasUsablePortalWindow` collapsed seven conditions into
  one bool, `RimroomsPortalNetwork` turned false into `Closed`, and the player read *"The
  laboratory connection for that address is not open."* A flat battery reported an address fault
  and the owner spent a session on the address.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Portals.xml")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(*parts):
    return io.open(os.path.join(*parts), encoding="utf-8-sig").read()


def no_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


binding = no_comments(read(SRC, "Gate", "NativeGateBinding.cs"))
opening = no_comments(read(SRC, "Gate", "PortalGateOpening.cs"))
travel = no_comments(read(SRC, "Portals", "PortalTravelService.cs"))
keyed = read(KEYED)

print("")

# =============================================================== the circuit, not one battery
check("THE RESERVE IS EVERY BATTERY ON THE CIRCUIT, THROUGH CORE'S OWN SUM",
      "private PowerNet NativePowerNet" in binding
      and "float stored = net.CurrentStoredEnergy();" in binding,
      "-- *\"only being able to connect 1 battery isnt anough and there should be no loimit\"*. "
      "`PowerNet.CurrentStoredEnergy()` walks `batteryComps` and skips EMP-stunned batteries, so "
      "an EMP'd one stops counting without this knowing what EMP is")

check("and the capacity readout is the circuit's, not one battery's",
      # **BOTH OCCURRENCES, COUNTED.** This line is in `NativeBatteryCapacity` and in
      # `DrawFromNativeCircuit`, so an `in` test held while the capacity reader was gutted and
      # the plant went MISSED. Duplicate-string trap, third instance this session. A third copy
      # appearing is a failure, and it should be: whoever adds one has to say which is which.
      binding.count("List<CompPowerBattery> batteries = net.batteryComps;") == 2
      and "float most = battery.Props.storedEnergyMax;" in binding
      and "if (net == null) { return 0f; }" in binding,
      "-- the number a player reads has to be about the circuit they built, not whichever "
      "battery they clicked first")

check("AND THE SPEND DRAWS ACROSS THE CIRCUIT",
      "private float DrawFromNativeCircuit(float amount)" in binding
      and "battery.DrawPower(take);" in binding
      and binding.count("DrawFromNativeCircuit(") >= 3,
      "-- **DEFINED AND CALLED, at every spend site.** Copied from Core's own "
      "`ChangeStoredEnergy`, which does exactly this and is private")

check("and no spend reads a single battery's charge any more",
      "battery.StoredEnergy < remaining" not in binding
      and "battery.DrawPower(cost);" not in binding,
      "-- the old spend refused outright when the ANCHOR could not cover a cost, so a drained "
      "bound battery stalled a gate that had ten full batteries on the same net. **That is the "
      "defect the owner found in play**")

check("and the draw reports what it OBSERVED, never what it asked for",
      "float observed = before - battery.StoredEnergy;" in binding
      and "return drawn;" in binding,
      "-- a battery that will not give what it said it held is the case the debit-fault "
      "machinery exists for, and that machinery compares observed against requested")

check("and the anchor is still required, so a gate without a bound battery has no circuit",
      "private CompPowerBattery NativeBatteryComp" in binding
      and "if (NativePowerNet == null) { return; }" in binding,
      "-- removing the limit is not removing the binding. The bound battery is how the gate "
      "knows which net is its own")

# =============================================================== the refusal names the cause
check("A CROSSING REFUSAL NAMES THE REAL CAUSE",
      "public string PortalWindowBlockerKey(string connectionId, string openingId)" in opening
      and '"RR_PortalTravel_NoCharge"' in opening,
      "-- seven conditions used to collapse into one bool and one message. *\"the laboratory "
      "address for that is not open\"* is what a FLAT BATTERY said, and the owner spent a "
      "session on the address because of it")

check("and the crossing path actually asks it",
      "blocked.PortalWindowBlockerKey(connection.Id, connection.OpeningId)" in travel
      and "if (why != null) { return CompanyActionResult.Refused(why); }" in travel,
      "-- **DEFINED AND CALLED.** A blocker key nothing consults is the defect that accounts for "
      "four of five bond defects")

check("AND THE PREDICATE DELEGATES, SO THE GATE AND THE MESSAGE CANNOT DISAGREE",
      "return PortalWindowBlockerKey(connectionId, openingId) == null;" in opening,
      "-- one authority. `CalibrationBlockerKey` and `StaffConsoleBlockerKey` exist for exactly "
      "this reason; two derivations of one rule is the defect this project keeps meeting")

check("and the generic text is still there for the cases the key cannot explain",
      "AvailabilityKey(availability)" in travel
      and "availability == PortalNetworkResult.Closed" in travel,
      "-- the key is asked FIRST and the fallback is kept, so a cause nobody anticipated still "
      "produces a sentence rather than silence")

keys = sorted(set(re.findall(r'"(RR_PortalTravel_[A-Za-z]+)"', opening)))
missing = [key for key in keys if (u"<%s>" % key) not in keyed]
check("AND EVERY ONE OF THE %d REASONS IT CAN RETURN HAS A STRING" % len(keys),
      len(keys) >= 5 and not missing,
      "-- missing: %s. A refusal with no string prints a raw key at the player"
      % ", ".join(missing))

check("and the charge message tells the player the limit is gone",
      "Any number of them count." in keyed,
      "-- the owner asked for no limit; the text has to say so, or somebody binds one battery "
      "and assumes that is all a gate will take")

# =============================================================== the door itself
# **The owner's gate read `Door locked` with every other condition green**: calibrated, operator
# on station, connection open, charge ten times the opening cost. `OrderCrossing` validated the
# APPROACH cell -- on the near side -- and never asked whether the door would open, so the crew
# were ordered somewhere they could reach through something they could not pass, with no reason.
check("A CROSSING ASKS WHETHER THE GATE'S DOOR WILL ACTUALLY OPEN",
      "private static string DoorBlockerKey(PortalConnectionRecord connection, Pawn pawn)" in travel
      # **THE REFUSAL REACHED, not the call written.** A plant swapping the guard for
      # `if (false)` left every asserted character in place and the lock went unchecked.
      # Twelfth instance of machinery-not-behaviour, so the act is pinned to the line above it.
      and ("            string doorBlock = DoorBlockerKey(connection, pawn);" + chr(10)
           + "            if (doorBlock != null) { return CompanyActionResult.Refused(doorBlock); }")
      in travel
      and "door.PawnCanOpen(pawn)" in travel,
      "-- **DEFINED AND CALLED.** Found in a running game, where a locked door refused every "
      "crossing silently")

check("and it asks through Core, so a re-classed door answers for itself",
      "as Building_Door" in travel and "DoorsExpanded" not in travel,
      "-- `PawnCanOpen` is public and virtual. The owner's gate is a door another mod re-classed, "
      "and nothing here names that mod or references its assembly")

check("and a held-open or already-open door is never refused",
      "if (door.HoldOpen || door.FreePassage) { return null; }" in travel,
      "-- neither needs permission, and refusing one would break a gate the player had "
      "deliberately pinned open")


print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the reserve is the whole circuit, there is no battery limit, and a refusal "
      "names the real cause")
