# -*- coding: utf-8 -*-
"""Planted faults against the gate circuit and the refusal that names its cause.

Both defects this guards reached the owner **in a running game** because nothing in forty-eight
proofs had ever claimed anything about the energy a gate runs on. So the plants go at the places
the real defects lived: a reading that quietly narrows to one battery, a spend that refuses on one
battery, and a refusal that stops naming its cause.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

BINDING = "src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs"
OPENING = "src/RimroomsAsyncIndustries/Gate/PortalGateOpening.cs"
TRAVEL = "src/RimroomsAsyncIndustries/Portals/PortalTravelService.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"

PROOF = ".local/register/proof-gate-circuit.py"

NL = chr(10)

PLANTS = [
    # ====================================================== the reserve narrows back to one
    ("THE RESERVE NARROWS BACK TO ONE BATTERY", BINDING,
     "                float stored = net.CurrentStoredEnergy();",
     "                float stored = NativeBatteryComp.StoredEnergy;", PROOF),

    ("the capacity readout narrows back to one battery", BINDING,
     "                List<CompPowerBattery> batteries = net.batteryComps;",
     "                List<CompPowerBattery> batteries = new List<CompPowerBattery>();", PROOF),

    # ====================================================== the spend
    ("THE SPEND GOES BACK TO DRAWING FROM ONE BATTERY", BINDING,
     "            try { taken = DrawFromNativeCircuit(remaining); }",
     "            try { taken = 0f; NativeBatteryComp.DrawPower(remaining); }", PROOF),

    ("the idle tick goes back to drawing from one battery", BINDING,
     "            DrawFromNativeCircuit(cost);",
     "            NativeBatteryComp.DrawPower(cost);", PROOF),

    ("the draw reports what it asked for instead of what it got", BINDING,
     "                float observed = before - battery.StoredEnergy;" + NL,
     "", PROOF),

    ("the anchor stops being required, so a gate with no battery has a circuit", BINDING,
     "            if (NativePowerNet == null) { return; }" + NL, "", PROOF),

    # ====================================================== the refusal
    ("THE REFUSAL STOPS NAMING A FLAT BATTERY", OPENING,
     '            if (NativeStoredEnergy < needed) { return "RR_PortalTravel_NoCharge"; }' + NL,
     "", PROOF),

    ("THE BLOCKER KEY IS WRITTEN AND NEVER ASKED", TRAVEL,
     "                    if (why != null) { return CompanyActionResult.Refused(why); }",
     "                    if (false) { return CompanyActionResult.Refused(why); }", PROOF),

    ("the predicate derives the conditions a second time", OPENING,
     "            return PortalWindowBlockerKey(connectionId, openingId) == null;",
     "            return !portalOwnerFault && !string.IsNullOrEmpty(portalOpeningId);", PROOF),

    ("the generic fallback is dropped, so an unanticipated cause goes silent", TRAVEL,
     "                return CompanyActionResult.Refused(AvailabilityKey(availability));",
     "                return CompanyActionResult.Refused(\"RR_PortalTravel_NoCharge\");", PROOF),

    # ====================================================== the words
    ("a reason loses its string and prints a raw key", KEYED,
     "  <RR_PortalTravel_NoCharge>", "  <RR_PortalTravel_NoChargeXX>", PROOF),

    ("the charge message stops telling the player the limit is gone", KEYED,
     "Any number of them count.", "Bind one battery.", PROOF),

    # ====================================================== the door, found in a running game
    ("THE CROSSING STOPS ASKING WHETHER THE DOOR OPENS", TRAVEL,
     "            string doorBlock = DoorBlockerKey(connection, pawn);" + NL
     + "            if (doorBlock != null) { return CompanyActionResult.Refused(doorBlock); }"
     + NL, "", PROOF),

    ("the door check is written and never called", TRAVEL,
     "            if (doorBlock != null) { return CompanyActionResult.Refused(doorBlock); }",
     "            if (false) { return CompanyActionResult.Refused(doorBlock); }", PROOF),

    ("a held-open door starts being refused", TRAVEL,
     "            if (door.HoldOpen || door.FreePassage) { return null; }" + NL, "", PROOF),

    # **Not a comment.** The first version appended `// DoorsExpanded` and the proof strips
    # comments, so it tested nothing. What matters is a real TYPE reference, which is what would
    # actually add a hard dependency on another mod's assembly.
    ("the door question stops going through Core and names another mod", TRAVEL,
     "            var door = connection.First.Anchor as Building_Door;",
     "            var door = connection.First.Anchor as DoorsExpanded.Building_DoorRemote;", PROOF),
]


_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the verifier must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = dict((path, io.open(path, encoding="utf-8").read())
               for path in set(plant[1] for plant in PLANTS))

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in opening.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every touched file verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
