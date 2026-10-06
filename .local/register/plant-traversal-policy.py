# -*- coding: utf-8 -*-
"""Planted faults against `tools/check-traversal-policy.py`.

**Checker 29 shipped without a plant suite, and a claim nobody has broken on purpose is a claim
nobody has checked.** This is the second instrument in this session found in that state, and the
first one -- `proof-request-generation.py` -- turned out to have a claim that had been *enforcing a
defect* for its whole life.

It guards the surviving half of invariant #1, which makes it the most load-bearing checker in the
package: the owner discarded *"the answer is always no"* and kept *"one chokepoint, and nothing is
ever lured"*. Every crossing in the mod is fair **because** of the kept half, so each of its rules
gets a fault aimed at it.

**The custody clause is the newest and the reason this suite exists now.** Outbound crossing shipped
with no custody test at all: a prisoner of the colony keeps their own faction, so a captured raider
who got out of their cell and stood near an open gate was transferred into the coordinate -- and the
doorstep scan *prefers* a hostile faction. Invariant 17 forbids exactly that.

**NEVER RUN A PLANT SUITE CONCURRENTLY WITH ANYTHING ELSE.**

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

POLICY = "src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs"
INCURSION = "src/RimroomsAsyncIndustries/Threats/GateIncursion.cs"
EGRESS = "src/RimroomsAsyncIndustries/Threats/GateEgress.cs"
ARCHITECTURE = "docs/ARCHITECTURE.md"

CHECK = "tools/check-traversal-policy.py"

NL = chr(10)

PLANTS = [
    # ===================================== rule 1, the surviving half of invariant #1
    ("THE GATE BECOMES A DESTINATION, so it can become an objective, a lure and a raid route",
     POLICY,
     "        public static bool MayApproachThresholdForTraversal(Thing thing)" + NL
     + "        {" + NL
     + "            return false;" + NL
     + "        }",
     "        public static bool MayApproachThresholdForTraversal(Thing thing)" + NL
     + "        {" + NL
     + "            return thing != null;" + NL
     + "        }", CHECK),

    # ===================================== rule 2, the retired constant stays retired
    ("the retired constant comes back, denying in code what the code beside it does", POLICY,
     "        public static string OutboundCrossingFailureKey(Pawn traveller, CompRimroomsGate gate)",
     "        public const bool AutonomousNonPlayerTraversalPermitted = false;" + NL
     + "        public static string OutboundCrossingFailureKey(Pawn traveller, CompRimroomsGate gate)",
     CHECK),

    # ===================================== rule 3, one chokepoint
    ("a crossing decision leaves the chokepoint, so an adapter can decide one for itself", POLICY,
     "public static string OutboundCrossingFailureKey(",
     "public static string OutboundCrossingMovedElsewhere(", CHECK),

    # ===================================== rules 4 to 6, the bounds
    # **THE RENAME DELIBERATELY DOES NOT CONTAIN THE ORIGINAL NAME.** The first version appended
    # "Unused", and the checker's `in` test passed because the new name CONTAINED the old one -- the
    # bound was gutted and the instrument said nothing. The rule is word-bounded now, and this plant
    # is what proves it.
    ("INBOUND STOPS BEING ONCE PER OPENING, so a coordinate can empty itself into your base",
     POLICY, "IncursionSpentThisOpening", "AlreadySpentOnThisVisit", CHECK),

    # Re-aimed onto the lodger clause, which is the one custody line that survived the owner's
    # correction. The fault planted is unchanged: outbound borrowing a bound that describes the FAR
    # side's danger, which says nothing about whether somebody already in your base should walk
    # through a door.
    ("outbound copies inbound's band bound, which describes the wrong side entirely", POLICY,
     "            if (traveller.IsQuestLodger()) { return \"RR_Egress_InYourCustody\"; }",
     "            if (gate.PressureBand < Band.Hostile) { return \"RR_Egress_NotEligible\"; }" + NL
     + "            if (traveller.IsQuestLodger()) { return \"RR_Egress_InYourCustody\"; }",
     CHECK),

    # Anchored on `traveller` rather than `intruder`: the two directions call `FitFailureKey` with
    # otherwise identical argument lists, and replacing the first occurrence would have gutted the
    # INBOUND bound while claiming to test the outbound one.
    ("a body too large for the opening walks out through it", POLICY,
     "            return FitFailureKey(traveller, gate.GateWidth, gate.GateOpeningDepth);",
     "            return null;", CHECK),

    # ===================================== CUSTODY, AFTER THE OWNER CORRECTED THE RULE
    #
    # **These four plants used to break the prisoner ban. The ban lasted one afternoon.** Owner,
    # 2026-10-06: *"a prisoner should be able to cross a gate is allowed to ( send the prisonerrs to
    # live and work in there and cross path back if zoned to and door are allowed access"*. A plant
    # that plants the owner's own design proves nothing, so they are re-aimed at the rule that
    # replaced it: **custody has to survive the crossing.**
    ("THE PRISONER BAN COMES BACK, which the owner overruled", POLICY,
     "            if (traveller.IsQuestLodger()) { return \"RR_Egress_InYourCustody\"; }",
     "            if (traveller.IsPrisoner || traveller.HostFaction != null)" + NL
     + "            { return \"RR_Egress_InYourCustody\"; }", CHECK),

    ("a quest lodger walks out and fails a quest the player never chose to fail", POLICY,
     "            if (traveller.IsQuestLodger()) { return \"RR_Egress_InYourCustody\"; }", "",
     CHECK),

    ("A PRISONER IS GIVEN AN ARRIVAL LORD, which launders them into a free pawn", EGRESS,
     "            if (pawn.IsPrisonerOfColony) { return; }", "", CHECK),

    ("whether a pawn is OURS goes back to a bare faction test, locking prisoners out again",
     "src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs",
     "        public static bool InOurCare(Pawn pawn)",
     "        public static bool InOurCareDisabled(Pawn pawn)", CHECK),

    # ===================================== rules 7 to 9, the transfers
    ("AN ARRIVING PAWN IS GIVEN NO LORD, so it stands still and nothing says why", EGRESS,
     "LordMaker.MakeNewLord", "LordMakerPlanted", CHECK),

    ("a failed spawn loses the pawn instead of putting them back", INCURSION,
     "GenSpawn.Spawn(pawn, originCell, origin", "GenSpawn.Spawn(pawn, originCell, planted", CHECK),

    ("the hostile arrival stops coming for valuables and members, which were the owner's words",
     EGRESS, "canSteal: true", "canSteal: false", CHECK),

    # **ANCHORED ON THE CODE, NOT THE DOC COMMENT.** The first version replaced the first
    # occurrence of the name, which is inside a `///` block explaining the rule -- so it edited
    # prose, and the checker strips comments and rightly saw nothing change. Second time this exact
    # mistake has been made in a plant in this session.
    ("A VISITOR WHO WANDERED THROUGH A DOOR IS GIVEN AN ASSAULT LORD", EGRESS,
     ": new LordJob_DefendPoint(cell, 12f);",
     ": new LordJob_AssaultColony(pawn.Faction);", CHECK),

    # ===================================== rule 10, the documents
    ("a document goes back to asserting the removed constant", ARCHITECTURE,
     "## Overview", "## Overview" + NL + NL
     + "`AutonomousNonPlayerTraversalPermitted` is a constant false.", CHECK),
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
