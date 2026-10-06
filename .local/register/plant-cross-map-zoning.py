# -*- coding: utf-8 -*-
"""Planted faults against `.local/register/proof-cross-map-zoning.py`.

**Every claim in that proof is about something NOT being there, which is the hardest kind to trust.**
A proof of an absence passes on an empty repository, on a typo in its own pattern, and on the day
somebody renames the thing it was watching. The only way to know it can fail is to put the forbidden
thing in and look.

The two that matter most are the two a future session would reach for honestly: writing a pawn's
area *"just to put them somewhere sensible"*, and reflecting into the private `allowedAreas`
dictionary because Core offers no public per-map getter. Both would make this mod the second author
of a player setting.

**NEVER RUN A PLANT SUITE CONCURRENTLY WITH ANYTHING ELSE.**

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

WORK = "src/RimroomsAsyncIndustries/ConnectedWork/RimroomsConnectedWorkComponent.cs"
NEED = "src/RimroomsAsyncIndustries/ConnectedWork/CrossForNeed.cs"
CROSSING = "src/RimroomsAsyncIndustries/ConnectedWork/ConnectedCrossing.cs"

PROOF = ".local/register/proof-cross-map-zoning.py"

NL = chr(10)

PLANTS = [
    # ============================================== 1. the absence, both ways it gets broken
    ("THE MOD WRITES A PAWN'S AREA, which makes it the second author of a player setting", WORK,
     "        public void ObserveAreaHere(Pawn pawn)" + NL + "        {",
     "        public void ObserveAreaHere(Pawn pawn)" + NL + "        {" + NL
     + "            pawn.playerSettings.AreaRestrictionInPawnCurrentMap = null;", PROOF),

    ("REFLECTION REACHES THE PRIVATE PER-MAP STORE, which is what somebody tries next", WORK,
     "        public bool ObservedAreaAllows(Pawn pawn, Map map, IntVec3 cell)" + NL + "        {",
     "        public bool ObservedAreaAllows(Pawn pawn, Map map, IntVec3 cell)" + NL + "        {" + NL
     + "            var planted = typeof(Pawn_PlayerSettings).GetField(\"allowedAreas\");", PROOF),

    # ============================================== 2. the read's shape
    ("the observation stops checking that the pawn supports areas at all", WORK,
     "            if (!pawn.playerSettings.SupportsAllowedAreas) { return; }", "", PROOF),

    ("THE CACHE DEFAULTS TO REFUSING, which silently stops cross-gate work for new workers", WORK,
     "                return observation.Allows(cell);" + NL
     + "            }" + NL
     + "            return true;",
     "                return observation.Allows(cell);" + NL
     + "            }" + NL
     + "            return false;", PROOF),

    ("the cache stops evicting and grows with the save", WORK,
     "            if (areaObservations.Count >= MaximumAreaObservations)",
     "            if (false)", PROOF),

    # ============================================== 3. one crossing implementation
    ("THE NEED-CROSSING STOPS GOING THROUGH THE ONE CROSSING, so it honours no zoning", NEED,
     "ConnectedCrossing.StepToward(pawn, destination, work, out ",
     "ConnectedCrossingPlanted(pawn, destination, work, out ", PROOF),

    ("the one crossing implementation is renamed away, so nothing can be asserted about it",
     CROSSING, "internal static ConnectedCrossingOutcome StepToward(",
     "internal static ConnectedCrossingOutcome StepTowardRenamed(", PROOF),
]

for _plant in PLANTS:
    if len(_plant) != 5:
        sys.stderr.write("PLANT LIST MALFORMED: %r has %d field(s), not 5\n"
                         % (_plant[0], len(_plant)))
        sys.exit(2)

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
