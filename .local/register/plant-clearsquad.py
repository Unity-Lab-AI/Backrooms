# -*- coding: utf-8 -*-
"""Planted faults against the clear squad.

Why this suite exists
---------------------
`proof-clear-squad.py` makes thirty-one claims. **A claim is worth what its ability to fail is
worth**, and this project has twice shipped a proof that asserted the exact thing being reversed.

The plants are weighted toward the two defect shapes that keep recurring here:

* **built, correct, and never reached** -- the dominant one. Four of five bond defects, and seven
  before them. So the first plants cut the call, not the code.
* **machinery, not behaviour** -- eleven instances. A plant prefixing `if (false)` leaves every
  asserted character in place, so the claims it tests are pinned in order against the line above.

And one plant exists purely to protect somebody else's promise: **giving `AnyLivingStaff` the
laboratory's trigger** would silently rewrite the clean-up team for the Store and Solo/Group
branches, which the owner excluded. `proof-facility-relief.py` is listed as the verifier for that
one, because it is the proof that should scream.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

SQUAD = "src/RimroomsAsyncIndustries/Company/CompanyClearSquad.cs"
RELIEF = "src/RimroomsAsyncIndustries/Company/FacilityRelief.cs"
COMPONENT = "src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs"
UPKEEP = "src/RimroomsAsyncIndustries/ConnectedWork/Providers/UpkeepProviders.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Requests.xml"

PROOF = ".local/register/proof-clear-squad.py"
RELIEF_PROOF = ".local/register/proof-facility-relief.py"

NL = chr(10)

PLANTS = [
    # ====================================================== built, correct, and never reached
    ("THE SQUAD IS BUILT AND NOTHING CALLS IT", RELIEF,
     "            if (IsLaboratoryBranch) { TickClearSquad(map); return; }" + NL, "", PROOF),

    ("the fork moves below the relief's trigger, so a dead lab gets the wrong team", RELIEF,
     "            if (IsLaboratoryBranch) { TickClearSquad(map); return; }" + NL
     + "            if (AnyLivingStaff()) { return; }",
     "            if (AnyLivingStaff()) { return; }" + NL
     + "            if (IsLaboratoryBranch) { TickClearSquad(map); return; }", PROOF),

    ("the inner scenario guard goes, so the squad can be reached for any start", SQUAD,
     "            if (!IsLaboratoryBranch) { return; }" + NL, "", PROOF),

    ("the scenario id drifts from the one the start actually declares", SQUAD,
     'private const string LaboratoryScenarioId = "async_industries";',
     'private const string LaboratoryScenarioId = "async_laboratory";', PROOF),

    ("the clearance count stops being saved, so a reload bills again", COMPONENT,
     "            ExposeClearSquad();" + NL, "", PROOF),

    # ====================================================== the trigger, both directions
    ("THE TRIGGER GOES BACK TO WAITING FOR ACTUAL DEATH", SQUAD,
     "                if (pawn.Downed) { continue; }" + NL, "", PROOF),

    ("THE OTHER TWO SCENARIOS LOSE THE TRIGGER THEY WERE PROMISED", RELIEF,
     "                if (pawn != null && !pawn.Dead && !pawn.Destroyed && !pawn.Discarded) { return true; }",
     "                if (pawn != null && !pawn.Dead && !pawn.Destroyed && !pawn.Discarded && !pawn.Downed) { return true; }",
     RELIEF_PROOF),

    ("the squad lands five, so the owner's three becomes the relief's roster", SQUAD,
     'private static readonly string[] ClearSquadRoles = { "operations", "engineering", "security" };',
     'private static readonly string[] ClearSquadRoles = { "operations", "engineering", "security", "research", "medical_logistics" };',
     PROOF),

    # ====================================================== no witnesses
    ("NO WITNESSES IS WRITTEN AND NEVER RUN", SQUAD,
     "                silenced += SilenceWitnesses(owned[index]);" + NL, "", PROOF),

    ("the dead are gathered before the downed are resolved", SQUAD,
     "                silenced += SilenceWitnesses(owned[index]);" + NL
     + "                cleared += ClearHostiles(owned[index]);",
     "                cleared += ClearHostiles(owned[index]);", PROOF),

    ("a prisoner on the property stops counting as a witness", SQUAD,
     "                bool held = pawn.IsPrisonerOfColony;", "                bool held = false;",
     PROOF),

    # ====================================================== the grave, which is the subtle one
    ("THE GRAVE GOES BACK TO BEING ONE CELL", SQUAD,
     "            CellRect rect = GenAdj.OccupiedRect(cell, rotation, graveDef.Size);",
     "            CellRect rect = CellRect.SingleCell(cell);", PROOF),

    ("THE DIGGABLE AFFORDANCE STOPS BEING CHECKED, SO GRAVES GO ON CONCRETE", SQUAD,
     "                if (!GenConstruct.CanBuildOnTerrain(graveDef, part, map, rotation)) { return false; }"
     + NL, "", PROOF),

    ("the fire fallback goes, so a body that cannot be buried is left on the floor", SQUAD,
     "                corpse.Destroy(DestroyMode.Vanish);" + NL
     + "                incinerated++;", "", PROOF),

    ("a grave can be dug on top of a body", SQUAD,
     "                    if (thing is Corpse || thing is Pawn) { return false; }" + NL, "",
     PROOF),

    # ====================================================== repair, one derivation
    ("REPAIR IS WRITTEN AND NEVER RUN", SQUAD,
     "            { repaired += RepairTheFacility(owned[index]); }", "            { }",
     PROOF),

    ("repair grows a second derivation instead of using Core's lister", UPKEEP,
     "        internal static List<Thing> RepairableOn(Map map, Faction faction)",
     "        private static List<Thing> RepairableOn(Map map, Faction faction)", PROOF),

    ("Core's lister is never told the building is whole", SQUAD,
     "                { map.listerBuildingsRepairable.Notify_BuildingRepaired((Building)thing); }",
     "                { }", PROOF),

    # ====================================================== the gate
    ("THE GATE IS NEVER SHUT DOWN", SQUAD,
     "            { gates += ShutDownGates(owned[index]); }", "            { }", PROOF),

    ("a ramping gate is left ramping, which is the 0.12.74-dev defect again", SQUAD,
     "                if (gate.IsSpinningUp) { gate.AbortSpinUp(); closed++; continue; }" + NL,
     "", PROOF),

    # ====================================================== the money
    ("THE BONDS ARE NEVER TAKEN", SQUAD,
     "            long confiscated = ConfiscateBonds(owned);",
     "            long confiscated = 0L;", PROOF),

    ("THE BONDS ARE PAID FOR INSTEAD OF LOST", SQUAD,
     "                taken += Economy.BondService.ConsumeBonds(paper);",
     "                taken += Economy.BondService.ConsumeBonds(paper);"
     + NL + "                DepositBondPaper(null, 0L);", PROOF),

    ("THE CHARGE STOPS BEING CAPPED AT THE BALANCE", SQUAD,
     "            long amount = Math.Min(RestockingChargeUsd, BalanceUsd);",
     "            long amount = RestockingChargeUsd;", PROOF),

    ("the charge loses its clearance number, so a second clearance reads as a replay", SQUAD,
     'string operationId = branchId + ":clearsquad:" + clearSquadCount + ":restocking";',
     'string operationId = branchId + ":clearsquad:restocking";', PROOF),

    ("THE PLAYER IS BILLED FOR A CLEARANCE THAT PUT NOBODY ON THE MAP", SQUAD,
     "            long charged = ChargeRestocking();",
     "            long charged = 0L;", PROOF),

    # ====================================================== the promise itself
    ("THE PLAYER CAN STILL LOSE THE GAME", SQUAD,
     "            if (Find.GameEnder != null) { Find.GameEnder.gameEnding = false; }" + NL, "",
     PROOF),

    # ====================================================== the only account they get
    ("the letter stops telling the player what it cost them", KEYED,
     "and {5} credits drawn from the account as restocking the petty cash",
     "and an amount drawn from the account as restocking the petty cash", PROOF),
]


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception and
# does nothing for a killed sweep -- how a planted fault reached the working tree four times.
# **ONE SENTINEL PER SUITE**, because all sixteen once shared a path and a later suite's unmark
# erased an earlier suite's record.
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


print("baseline -- every verifier must pass before anything is planted")
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
        # The one line that must always run, and the sentinel is held until after it so an
        # interruption *during the verifier* stays visible to check-plant-residue.py.
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
