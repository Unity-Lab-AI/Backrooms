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
comp = no_comments(read(SRC, "Gate", "CompRimroomsGate.cs"))
keyed = read(KEYED)
gate_keys = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6",
                              "Languages", "English", "Keyed", "RR_Gate.xml"))

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
      and '"RR_PortalTravel_SessionClosed"' in opening
      and '"RR_PortalTravel_InEmergency"' in opening
      and '"RR_PortalTravel_WindowExpired"' in opening,
      "-- seven conditions used to collapse into one bool and one message. *\"the laboratory "
      "address for that is not open\"* is what a FLAT BATTERY said, and the owner spent a "
      "session on the address because of it")

# ======================================================= and it is no longer a power question
#
# **RE-AIMED 2026-10-03, and the claim came out stronger.** This used to assert
# `"RR_PortalTravel_NoCharge"` appeared in the blocker -- that a flat battery was one of the named
# causes of a refused crossing. Owner direction has overruled the behaviour, not the naming:
#
#   *"i build and set up and open the gate but it incorrectly says i dont have power to send
#   people through, even tho the gate is open and connected,,, thast is wrong if its open it
#   doenst need special power to send things through the gate"*
#
# and, naming the message, *"a error about not enough reserver power in the batteries"*.
#
# So the causes above are asserted by the names that still exist, and the removal gets a claim of
# its own, stated negatively, because **the regression here is an addition** -- somebody putting a
# power condition back on the crossing path. The three it used to apply all arrive together
# through `CheckStationReadiness`, so asserting the exact call line is what pins it.
# Scoped to the blocker's own body, not the whole file, and that is load-bearing in BOTH
# directions. `RecoverPortalOpening` legitimately reads `NativeStoredEnergy` a few methods below,
# so a file-wide assertion could never say this; and a claim written as the absence of one exact
# line would miss a toll reintroduced with any other comparison, which is precisely what the
# matching plant inserts. `opening` has already had its comments stripped, so this splits on code.
blocker = (opening.split("public string PortalWindowBlockerKey(")[-1]
           .split("public bool HasUsablePortalWindow(")[0])

check("AND AN OPEN APERTURE IS NEVER CHARGED TO PASS SOMEBODY THROUGH",
      "CheckCrossingReadiness(assignedOperator)" in blocker
      and "CheckStationReadiness" not in blocker
      and "NativeStoredEnergy" not in blocker
      and "RR_PortalTravel_NoCharge" not in blocker,
      "-- every line above the readiness call already establishes that the opening is LIVE, so an "
      "opening-time power condition there could only ever fire in the one case the owner forbids. "
      "`ProjectedOpeningPowerFailure` says *\"This gates opening only\"* in its own docstring and "
      "`RR_Gate_SupplyTooLow` says *\"to start an opening\"* in its own text, while both were "
      "being shown to somebody whose opening was already running")

check("and the power conditions still guard the paths that DO start an opening",
      "CompanyActionResult ready = CheckStationReadiness(assignedOperator);" in opening
      and "RecoveryEnergyRequiredWattDays" in opening,
      "-- the removal is scoped to crossing. Starting and recovering an opening still pay, and "
      "`RecoverPortalOpening` still refuses on `RR_NativeGate_RecoveryEnergyLow`; a crossing fix "
      "that made openings free would be a different defect wearing this one's clothes")

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



# ====================================================== which door is the gate, decided on its own
#
# Owner, 2026-10-03, verbatim: *"i try to first thing set a door as gate on the doors ui bar, but
# it tells me i have to set up the battery used for reserver before i can do anything, incrattely,
# i should be able to set the gate on a door first"*, scoped *"in company scenerio"*.
#
# The door's own button resolved all three providers and REFUSED if any was absent or ambiguous,
# so on a company start with no battery bound the only route from a door to a gate said
# `RR_NativeGate_NoSingleBattery` and stopped. A refusal is not a route.
designate = (binding.split("public CompanyActionResult DesignateAsGate()")[-1]
             .split("public CompanyActionResult ClearNativeBinding()")[0])

check("WHICH DOOR IS THE GATE CAN BE SET ON ITS OWN",
      "public CompanyActionResult DesignateAsGate()" in binding
      and "nativeDesignated = true;" in designate,
      "-- the owner asked for the FIRST of binding's four decisions to be takeable alone")

check("AND IT ASKS FOR NO PROVIDER, WHICH IS THE WHOLE POINT",
      "ExactProvider" not in designate
      and "nativeBattery" not in designate
      and "nativeConsole" not in designate
      and "nativeAssemblyBench" not in designate,
      "-- a battery, console or bench condition in here would put the owner's refusal straight "
      "back. `IsDesignated` never meant *fully bound* -- it is "
      "`!IsRunExtension && NativeDoorProvider() && schema == 1 && nativeDesignated` -- and what "
      "reports a missing circuit is `NativeBindingFailureKey` -> `RR_NativeGate_LinkMissing`")

check("and binding itself still refuses a half-answer",
      "ReserveTooSmall" in binding
      and 'ExactProvider(console, "CommsConsole")' in binding
      and 'ExactProvider(battery, "Battery")' in binding,
      "-- the fix is a NEW entry point, not a loosened bind. A gate that looks complete and is "
      "not strands the first crew through it")

make = comp.split("RR_NativeGate_MakeLabel")[-1].split("public override IEnumerable<Gizmo>")[0]
check("THE DOOR BUTTON DESIGNATES BEFORE IT RESOLVES ANY PROVIDER",
      "DesignateAsGate()" in make and "SoleCandidate" in make
      and make.index("DesignateAsGate()") < make.index("SoleCandidate"),
      "-- ordering is the claim. Resolving first and refusing is exactly the behaviour reported")

check("and a missing circuit is TOLD, not refused",
      'Messages.Message("RR_NativeGate_DesignatedNeedsCircuit"' in make
      and "ShowOrderResult(CompanyActionResult.Refused(" not in make,
      "-- the door IS the gate by then; what is missing is the circuit, and the player needs to "
      "know which piece and where to finish it")

for key in ("RR_NativeGate_DesignatedNeedsCircuit", "RR_NativeGate_IsRunExtension",
            "RR_Event_GateDesignated"):
    check("%s is translated" % key, ("<%s>" % key) in gate_keys,
          "-- a refusal with no string prints a raw key at the player")

# ============================================ the operator leaves before their body gives out
#
# **A colonist starved at the console in the first launch.** Owner, 2026-10-06: *"current a pawn
# dies at the comms console... and we cant have them not going to eat or finding saftey"*. It was
# fatal by construction and needed three things at once: `suspendable: false`, a
# `ToilCompleteMode.Never` station, and a `FailOn` that tested the gate, the calibration, the
# operator identity, `Downed` and `InMentalState` and **not one need**.
#
# So the claims below are about the FLOOR, not the setting. A posture tunes WHEN an operator
# leaves; nothing tunes WHETHER.
posture = no_comments(read(SRC, "Gate", "GateWatchPosture.cs"))
driver = no_comments(read(SRC, "Gate", "JobDriver_RimroomsGate.cs"))
jobs = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                         "JobDefs", "RR_GateJobs.xml"))
enum_body = posture.split("public enum GateWatchPosture")[1].split("}")[0]

check("THE OPERATOR JOB CHECKS A NEED AT ALL, which it did not when a pawn starved at it",
      "GateWatch.MustLeave(pawn)" in driver,
      "-- without it the only exits were collapse or the player noticing")

check("and it is asked in the FailOn AND every tick, counted rather than assumed",
      driver.count("GateWatch.MustLeave(pawn)") == 2,
      "-- a FailOn runs on the driver's own cadence; crossing into starvation between two of them is the window the defect lived in")

check("THE FLOOR IS THE GAME'S OWN CATEGORIES: starving, exhausted, burning, bleeding out",
      "HungerCategory.Starving" in posture and "RestCategory.Exhausted" in posture
      and "IsBurning()" in posture and "BleedRateTotal" in posture,
      "-- each is a state where standing still is the thing doing the harm, and each is Core's threshold rather than a number chosen here")

check("THE FLOOR IS ASKED BEFORE THE POSTURE, so no posture can switch it off",
      posture.index("MustLeave") < posture.index("Releases"),
      "-- the ordering IS the safety argument")

check("AND NO POSTURE MEANS NEVER LEAVE, because that value does not exist",
      "Mild" in enum_body and "Balanced" in enum_body and "Strict" in enum_body
      and "Never" not in enum_body,
      "-- a value meaning never leave would be one typo away from the bug this file exists to fix")

check("Strict adds no tolerance of its own beyond the floor",
      posture.count("case GateWatchPosture.Strict:") == 3
      and "Releases" in posture.split("case GateWatchPosture.Strict:")[0],
      "-- COUNTED, because the label and description switches carry the same case and a plant that gutted the one in Releases left two behind")

gate_source = no_comments(read(SRC, "Gate", "CompRimroomsGate.cs"))
check("the saved default is written out rather than inherited from a zeroed field",
      "private GateWatchPosture watchPosture = GateWatchPosture.Balanced;" in gate_source
      and gate_source.count("GateWatchPosture.Balanced") == 3,
      "-- the whole declaration, not the identifier. Three sites name it: the initialiser, the Scribe default and the dropdown's option list. COUNTED AFTER MEASURING, because the first version of this claim guessed two and failed on correct code")

check("THE JOB DEF RECORDS WHY IT IS STILL NOT SUSPENDABLE",
      "suspendable" in jobs and "MustLeave" in jobs,
      "-- suspendable would give exactly the mild posture and could not express the other two, so the mod keeps the decision and carries the duty")

for watch_key in ("RR_GateWatch_Label", "RR_GateWatch_Strict", "RR_GateWatch_StrictDesc",
                  "RR_GateWatch_Mild", "RR_GateWatch_Balanced"):
    check("%s is translated" % watch_key, ("<%s>" % watch_key) in gate_keys,
          "-- a dropdown showing a raw key is a dropdown nobody can use")
print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the reserve is the whole circuit, there is no battery limit, and a refusal "
      "names the real cause")
