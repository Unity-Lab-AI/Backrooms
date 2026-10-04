# -*- coding: utf-8 -*-
"""Planted faults against the way BACK IN from a world tile.

Why this file exists at all
---------------------------
Owner, 2026-10-03, verbatim: *"ther natureal gates in the backrrooms that lead to the world map
tiles( these gats currently dont have a way back into the backrooms ... currently and incorrectyl
there is no way for a pawn to go back into the backrooms when they exit via a natural gate"*.

**`proof-world-exit.py` had no plant suite of any kind.** Twenty-one suites existed and not one
tested it, so nobody had ever verified that its claims *can* fail -- and a claim nobody has seen
fail is a claim nobody should trust. That is the same defect class as a checker that can only
pass, and as the five claims this session found sitting after a proof's own exit gate.

Scope, stated honestly: these plants cover the **return-side** claims added 2026-10-03. The
pre-existing world-exit claims still have no plants, and that is recorded rather than implied.

What is guarded, and why each is the shape a real regression would take
----------------------------------------------------------------------
* The gate is built at all. Deleting the call is exactly what "there is no way back" was.
* **The ordering.** Building the gate after the crew moves would strand them ON A MAP rather than
  on a tile -- worse, because it looks finished. Asserted as an ordering, planted as a reorder.
* The map is made the branch's own first, because `Register` line 82 refuses otherwise.
* A failed registration takes the door back down. A door with no edge behind it is a gate that
  LOOKS like the way home and is not.
* The refusals keep their strings, or a raw key prints at the player.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

EXIT = "src/RimroomsAsyncIndustries/Portals/WorldExit.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"

PROOF = ".local/register/proof-world-exit.py"

NL = chr(10)

PLANTS = [
    # ====================================================== the way back stops being built
    ("THE WAY BACK IN IS NEVER BUILT", EXIT,
     "            CompanyActionResult returnGate = EstablishReturnGate(record, claimed, coordinateDoor);" + NL
     + "            if (!returnGate.Success) { return returnGate; }" + NL,
     "", PROOF),

    ("the gate is built but its failure is ignored, so a crew leaves anyway", EXIT,
     "            if (!returnGate.Success) { return returnGate; }",
     "            if (false) { return returnGate; }", PROOF),

    # ====================================================== the ordering, which is the safety
    ("THE GATE IS BUILT AFTER THE CREW IS ALREADY DESPAWNED", EXIT,
     "                pawn.DeSpawn();",
     "                pawn.DeSpawn();" + NL
     + "                EstablishReturnGate(record, claimed, coordinateDoor);", PROOF),

    # ====================================================== the preconditions Register demands
    ("the map is never made the branch's own, so Register must refuse the endpoint", EXIT,
     "            CompanyActionResult site = RegisterRemoteSite(claimed);" + NL
     + "            if (!site.Success) { return site; }" + NL,
     "", PROOF),

    ("the edge is registered as the wrong kind, so Register refuses it", EXIT,
     "                record.coordinateId, PortalConnectionKind.Emergence,",
     "                record.coordinateId, PortalConnectionKind.Laboratory,", PROOF),

    # ====================================================== a false way home is left standing
    ("A FAILED REGISTRATION LEAVES THE DOOR STANDING AS A FALSE WAY HOME", EXIT,
     "                gate.Destroy(DestroyMode.Vanish);" + NL
     + '                return CompanyActionResult.Refused("RR_WorldReturn_NotRegistered");',
     '                return CompanyActionResult.Refused("RR_WorldReturn_NotRegistered");', PROOF),

    # ====================================================== the words
    ("a refusal loses its string and prints a raw key", KEYED,
     "  <RR_WorldReturn_NotRegistered>", "  <RR_WorldReturn_NotRegisteredXX>", PROOF),

    ("the arrival event loses its string", KEYED,
     "  <RR_Event_WorldReturnGateBuilt>", "  <RR_Event_WorldReturnGateBuiltXX>", PROOF),
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
