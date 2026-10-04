# -*- coding: utf-8 -*-
"""Prove every claim in `proof-crossing-pack.py` can fail.

A claim nobody has watched fail is indistinguishable from a comment, which is the same argument
the queue row made about the config: *"a comment is not a guard"*.

Three properties get a plant each, and one of them is a lesson this battery has paid for twice:

* **Ordering.** Clearing a pack after `DeSpawn` has no map to drop onto and clearing it after
  custody transfer is too late, so both orderings are planted rather than only the absence.
* **Count, not containment.** One plant strips the traveller gate from **a single adapter** out of
  seven. A claim written with `in` would still pass -- *"`in` CANNOT TELL ONE SITE FROM THREE"* is
  recorded as the recurring defect, and this is the plant that would catch it here.
* **The rollback must stay exempt.** Planting a call INTO `TryRecoverToSource` must fail, because
  a crossing that failed through no fault of the pawn's must not cost it its goods.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-crossing-pack.py"]

POLICY = "src/RimroomsAsyncIndustries/Portals/CrossingInventoryPolicy.cs"
SERVICE = "src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs"
TRAVERSAL = "src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs"
ONE_ADAPTER = "src/RimroomsAsyncIndustries/ConnectedWork/Adapters/ConnectedHaulingAdapter.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"

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
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


CALL = ("                CrossingInventoryPolicy.DropFreight(pawn);" + chr(10) +
        "                if (CrossingInventoryPolicy.HasFreight(pawn))" + chr(10) +
        "                { return FailBeforeDespawn(receipt, \"RR_PortalCrossing_PackNotCleared\"); }")

PLANTS = [
    ("the pack is never cleared at all", SERVICE,
     "CrossingInventoryPolicy.DropFreight(pawn);", "// cleared nowhere", 1),

    ("the pack is cleared AFTER the pawn is despawned, with no map to drop onto", SERVICE,
     CALL, "", 1),

    ("a pack that will not empty is crossed with instead of refused", SERVICE,
     "                if (CrossingInventoryPolicy.HasFreight(pawn))" + chr(10) +
     "                { return FailBeforeDespawn(receipt, \"RR_PortalCrossing_PackNotCleared\"); }",
     "", 1),

    ("a second call site appears, which containment could not see", SERVICE,
     "CrossingInventoryPolicy.DropFreight(pawn);",
     "CrossingInventoryPolicy.DropFreight(pawn); CrossingInventoryPolicy.DropFreight(pawn);", 1),

    ("the rollback path starts costing the pawn its goods", SERVICE,
     "                if (!SecureCarriedThing(receipt))",
     "                CrossingInventoryPolicy.DropFreight(pawn);" + chr(10) +
     "                if (!SecureCarriedThing(receipt))", 1),

    ("Core's keep-list is replaced by a hand-rolled one", POLICY,
     "return pawn.inventory.FirstUnloadableThing.Thing != null;",
     "return pawn.inventory.innerContainer.Count > 0;", 1),

    ("the whole pack is emptied, so a pawn loses its own medicine", POLICY,
     "            if (!HasFreight(pawn)) { return 0; }",
     "            pawn.inventory.DropAllNearPawn(pawn.Position);" + chr(10) +
     "            if (!HasFreight(pawn)) { return 0; }", 1),

    ("the loop bound is removed, so a failing drop could spin for ever", POLICY,
     "public const int MaximumFreightStacks = 64;",
     "public const int MaximumFreightStackLimit = 64;", 1),

    ("the unspawned guard is removed, so a drop is attempted with no map", POLICY,
     "            if (!pawn.Spawned || pawn.Map == null) { return 0; }", "", 1),

    ("the policy reaches for the mod that raised the question", POLICY,
     "using Verse;", "using Verse;" + chr(10) + "// PickUpAndHaul comp read here", 1),

    ("saved state creeps in for something that is derived", POLICY,
     "        public const int MaximumFreightStacks = 64;",
     "        public static int scribed; // Scribe_Values here" + chr(10) +
     "        public const int MaximumFreightStacks = 64;", 1),

    ("ONE adapter of seven loses its traveller gate", ONE_ADAPTER,
     "PortalTraversalPolicy.TravellerFailureKey(pawn) != null", "false", 1),

    ("the traveller gate stops requiring colonist status", TRAVERSAL,
     "if (traveller.Faction != Faction.OfPlayer || !traveller.IsColonist)",
     "if (traveller.Faction != Faction.OfPlayer)", 1),

    ("autonomous non-player traversal stops being constant false", TRAVERSAL,
     "AutonomousNonPlayerTraversalPermitted = false",
     "AutonomousNonPlayerTraversalPermitted = true", 1),

    ("the refusal has no keyed string, so it would show the player an identifier", KEYED,
     "<RR_PortalCrossing_PackNotCleared>", "<RR_PortalCrossing_PackNotClearedTypo>", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:50], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable] + PROOF,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == want
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted %d)"
          % ("CAUGHT " if ok else "MISSED!", label, code, want))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
