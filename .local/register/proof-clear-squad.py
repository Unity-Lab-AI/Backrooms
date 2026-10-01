# -*- coding: utf-8 -*-
"""The clear squad: The Company arrives, and the laboratory is open again without its people.

Why this proof exists
---------------------
**Four of the five bond defects, and seven before them, were built, correct, and unreachable.**
`TransformLabel` on a Book that never walks comps. `RedeemBondsInRadius` with one caller nobody
had built. `Discover` with none. `IsLiveGate` needing a mark nothing could set. So the first
claims below are not that the squad exists -- they are that **something calls it**.

The second thing this proves is that the owner's scoping is real. *"this only happens for the lab
secnerio for now"*. The Store and Solo/Group branches were promised a clean-up team in 0.11.7-dev
with **five** staff and a trigger that waits for actual death, and `proof-facility-relief.py`
asserts both. **Those two claims must still hold**, which is why the squad is a separate path and
not an edit to the old one.

And the third is that the grave actually fits, which is read out of the game's own data rather
than assumed. Core's `Grave` is **(1,2)** and needs **`Diggable`** terrain; **every constructed
floor is excluded**, so a grave cannot be dug inside the facility at all.

Run from the repository root.
"""
import io
import os
import re
import sys
import glob

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Requests.xml")
DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

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


squad = no_comments(read(SRC, "Company", "CompanyClearSquad.cs"))
relief = no_comments(read(SRC, "Company", "FacilityRelief.cs"))
component = no_comments(read(SRC, "Company", "RimroomsCampaignComponent.cs"))
upkeep = no_comments(read(SRC, "ConnectedWork", "Providers", "UpkeepProviders.cs"))
keyed = read(KEYED)

print("")

# =============================================================== IS IT REACHED AT ALL
check("THE SQUAD IS CALLED, FROM A TICK THAT ALREADY RUNS",
      "TickClearSquad(map)" in relief
      and "internal void TickClearSquad(Map map)" in squad
      and "if (now % 60 == 30) { TickFacilityRelief(); }"
      in no_comments(read(SRC, "Company", "CampaignServices.cs")),
      "-- **DEFINED AND CALLED.** The dominant defect in this project is a system that is built, "
      "correct and switched off. A claim that something exists proves nothing")

check("and the fork is BEFORE the relief's own trigger, so the laboratory never reaches it",
      # Pinned in order, on adjacent lines, so a guard cannot be slipped between them and the
      # relief cannot run on top of the squad: eight arrivals and a bill for three.
      ("            if (IsLaboratoryBranch) { TickClearSquad(map); return; }" + chr(10)
       + "            if (AnyLivingStaff()) { return; }") in relief,
      "-- running both would land eight people and charge twenty-five million for three of them")

check("AND IT IS SCOPED TO THE LABORATORY, WHICH IS WHAT THE OWNER ASKED FOR",
      'private const string LaboratoryScenarioId = "async_industries";' in squad
      and "string.Equals(scenarioId, LaboratoryScenarioId, StringComparison.Ordinal)" in squad
      and "if (!IsLaboratoryBranch) { return; }" in squad,
      "-- *\"this only happens for the lab secnerio for now\"*. Two guards: one at the fork and "
      "one inside, so a future caller cannot reach it for another scenario by accident")

check("and the laboratory's own start really carries that id",
      "<scenarioId>async_industries</scenarioId>"
      in read(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
              "RimroomsStartDefs", "RR_Starts.xml"),
      "-- a scenario gate matched against an id no start declares is a feature that never fires")

check("and the save keeps it, so a clearance is not replayed on load",
      "ExposeClearSquad();" in component
      and 'Scribe_Values.Look(ref clearSquadCount, "rr_clearSquadCount", 0);' in squad,
      "-- the count is in the operation id of the charge; an unsaved count bills again")

# =============================================================== THE TRIGGER, AND WHAT IT COST
check("DOWNED COUNTS AS LOST FOR THE LABORATORY",
      "private bool AnyCapableStaff()" in squad
      and "if (pawn.Downed) { continue; }" in squad
      and "if (AnyCapableStaff()) { return; }" in squad,
      "-- *\"when all pawns incompacitated\"*. **DEFINED AND CALLED**")

check("AND THE OTHER TWO SCENARIOS KEEP THE TRIGGER THEY WERE PROMISED",
      "private bool AnyLivingStaff()" in relief
      and "Downed" not in re.search(r"private bool AnyLivingStaff\(\).*?\n        \}",
                                    relief, re.S).group(0),
      "-- `proof-facility-relief.py` asserts *the living-staff scan does not treat downed as "
      "dead*, and that claim is still true. **The owner scoped the change; a universal edit "
      "would have silently rewritten the bargain for two starts nobody mentioned**")

check("and the relief still lands five while the squad lands three",
      len(re.findall(r'"([a-z_]+)"', re.search(
          r"ReliefRoles\s*=\s*\{([^}]*)\}", relief).group(1))) == 5
      and len(re.findall(r'"([a-z_]+)"', re.search(
          r"ClearSquadRoles\s*=\s*\{([^}]*)\}", squad).group(1))) == 3,
      "-- *\"leeaves three new pawns\"*. A truncation of the relief's list would have broken the "
      "proof that asserts five")

# =============================================================== NO WITNESSES
check("NO WITNESSES: THE BRANCH'S OWN PEOPLE DO NOT SURVIVE IT",
      "private static int SilenceWitnesses(Map map)" in squad
      and "silenced += SilenceWitnesses(owned[index]);" in squad
      and "pawn.Kill(null);" in squad,
      "-- ***\"the downed: No Witnesses\"***, asked and answered before this was written. "
      "**DEFINED AND CALLED**")

check("and a prisoner on the property is a witness, while an animal is not",
      "bool held = pawn.IsPrisonerOfColony;" in squad
      and "if (!pawn.RaceProps.Humanlike) { continue; }" in squad.replace(
          "pawn.RaceProps == null || !pawn.RaceProps.Humanlike", "pawn.RaceProps.Humanlike")
      or ("pawn.RaceProps == null || !pawn.RaceProps.Humanlike" in squad
          and "bool held = pawn.IsPrisonerOfColony;" in squad),
      "-- a pet is property, not somebody who can tell")

check("and it is KILLED not destroyed, because the burial needs a body",
      ".Kill(null)" in squad and "SilenceWitnesses" in squad
      and "Destroy(DestroyMode.Vanish)" in relief,
      "-- *\"takes the dead\"* needs something to take. `ClearHostiles` vanishes hostiles "
      "instead, so the replacement crew do not inherit forty corpses")

check("and the witnesses are silenced BEFORE the dead are gathered",
      squad.index("SilenceWitnesses(owned[index]);") < squad.index("InterTheDead(owned[index]"),
      "-- a pawn still down when the corpses are collected would be left on the floor of a "
      "finished facility")

# =============================================================== THE GRAVE ACTUALLY FITS
grave_xml = None
for path in glob.glob(os.path.join(DATA, "Core", "Defs", "ThingDefs_Buildings", "*.xml")):
    text = io.open(path, encoding="utf-8-sig").read()
    found = re.search(r"<ThingDef[^>]*>\s*<defName>Grave</defName>.*?</ThingDef>", text, re.S)
    if found:
        grave_xml = found.group(0)
        break

check("CORE'S GRAVE IS TWO CELLS AND NEEDS DIGGABLE GROUND, READ FROM THE GAME",
      grave_xml is not None
      and "<size>(1,2)</size>" in grave_xml
      and "<terrainAffordanceNeeded>Diggable</terrainAffordanceNeeded>" in grave_xml,
      "-- **not assumed.** A one-cell model of a two-cell building places graves that never "
      "appear, and this project has had three separate models of rotation maths disagree")

if grave_xml:
    diggable = []
    for path in glob.glob(os.path.join(DATA, "Core", "Defs", "TerrainDefs", "*.xml")):
        text = io.open(path, encoding="utf-8-sig").read()
        for block in re.finditer(r"<TerrainDef[^>]*>(.*?)</TerrainDef>", text, re.S):
            body = block.group(1)
            name = re.search(r"<defName>(.*?)</defName>", body)
            affordances = re.search(r"<affordances>(.*?)</affordances>", body, re.S)
            if name and affordances and "Diggable" in affordances.group(1):
                diggable.append(name.group(1))
    check("and no constructed floor is diggable, so a grave cannot be dug indoors",
          "Soil" in diggable and "Sand" in diggable and "Gravel" in diggable
          and "Concrete" not in diggable and "SterileTile" not in diggable
          and "MetalTile" not in diggable and "PavedTile" not in diggable,
          "-- %d Core terrains carry it and every built floor is excluded. **This is why the "
          "fallback exists at all**, and finding it by reading the data rather than at runtime "
          "is the difference between a feature and a feature that never worked"
          % len(diggable))

check("THE FOOTPRINT IS CHECKED THROUGH CORE'S OWN ARITHMETIC, NOT A SECOND COPY",
      "CellRect rect = GenAdj.OccupiedRect(cell, rotation, graveDef.Size);" in squad
      and "GenConstruct.CanBuildOnTerrain(graveDef, part, map, rotation)" in squad
      and "foreach (IntVec3 part in rect)" in squad,
      "-- both cells, and the affordance question answered by the code that owns it. A table of "
      "diggable terrains here would go stale the first time Core added one")

check("and a grave is never dug on top of a body or a pawn",
      "if (thing is Corpse || thing is Pawn) { return false; }" in squad,
      "-- the one placement that would destroy the thing the grave is for")

check("AND THE FIRE IS THE FALLBACK, AND IT IS REACHED",
      "if (TryBury(map, corpse)) { buried++; continue; }" in squad
      and "corpse.Destroy(DestroyMode.Vanish);" in squad
      and "incinerated++;" in squad,
      "-- *\"burry the dead or incenerate on propery\"*. **DEFINED AND CALLED.** No crematorium "
      "is built: a bill needs a worker and there is nobody alive to work it, so an unpowered one "
      "would be scenery pretending to be a mechanism")

# =============================================================== REPAIR, ONE DERIVATION
check("REPAIR USES CORE'S OWN REPAIRABLE LISTER THROUGH THE MOD'S ONE WRAPPER",
      "internal static List<Thing> RepairableOn(Map map, Faction faction)" in upkeep
      and "map.listerBuildingsRepairable.RepairableBuildings(faction)" in upkeep
      and "ConnectedWork.Providers.RepairProvider.RepairableOn(map, Faction.OfPlayer)" in squad
      and "repaired += RepairTheFacility(owned[index]);" in squad,
      "-- *\"fix broken walls and equipment\"*. **ONE derivation.** A second hand-rolled scan of "
      "damaged buildings is the defect this project keeps meeting: `MaxRoomSpan` against the "
      "graph ceiling, three copies of `AdjustForRotation`")

check("and Core's lister is told the building is whole again",
      "map.listerBuildingsRepairable.Notify_BuildingRepaired((Building)thing);" in squad,
      "-- otherwise a repair job stays queued against something at full hit points")

check("and only things that actually use hit points are touched",
      "if (thing.def == null || !thing.def.useHitPoints) { continue; }" in squad
      and "if (thing.HitPoints >= thing.MaxHitPoints) { continue; }" in squad,
      "-- and the count reported is the number actually brought back up")

# =============================================================== THE GATE
check("THE GATE IS SHUT DOWN, RAMP OR OPEN CONNECTION",
      "private static int ShutDownGates(Map map)" in squad
      and "gates += ShutDownGates(owned[index]);" in squad
      and "if (gate.IsSpinningUp) { gate.AbortSpinUp(); closed++; continue; }" in squad
      and "if (gate.IsOpening && gate.TriggerEmergencyCutoff().Success) { closed++; }" in squad,
      "-- *\"disconnect the gate\"*, *\"and shut down the gate\"*. **DEFINED AND CALLED.** A ramp "
      "is not an open connection and needed its own call, which cost a launch at 0.12.74-dev")

check("and the gate is LEFT COMMISSIONED",
      "ClearNativeBinding" not in squad and "Decommission" not in squad,
      "-- *\"like starting all over again\"* is the crew starting again, not the machine. "
      "Decommissioning would make three arrivals rebuild an eight-component assembly before "
      "they could do the job they were sent for")

# =============================================================== THE MONEY
check("EVERY BOND ON EVERY OWNED MAP IS TAKEN, AND CREDITED NOWHERE",
      "private static long ConfiscateBonds(List<Map> owned)" in squad
      and "long confiscated = ConfiscateBonds(owned);" in squad
      and "Economy.BondService.ConsumeBonds(paper)" in squad
      and "Economy.BondService.FaceValueOf(thing)" in squad,
      "-- *\"haull abay all bonds printed that are on the map u lose it all\"*. **DEFINED AND "
      "CALLED**")

check("and it does NOT route through the deposit, which would pay for them",
      "DepositBondPaper" not in squad and "RedeemBondsInRadius" not in squad
      and "CombineBondPaper" not in squad,
      "-- *\"u lose it all\"*. `DepositBondPaper` credits the ledger, which is the exact "
      "opposite. The total is reported in the letter and posted nowhere")

check("THE CHARGE IS CAPPED AT THE BALANCE AND NEVER GOES BELOW ZERO",
      "long amount = Math.Min(RestockingChargeUsd, BalanceUsd);" in squad
      and "private const long RestockingChargeUsd = 25000000L;" in squad
      and "if (amount <= 0L) { return 0L; }" in squad,
      "-- *\"upto 25M from account never going under 0 dollars in account\"*, said twice in one "
      "sentence. Clamped BEFORE posting: `PostTransaction` would refuse the whole charge and take "
      "nothing, where the owner asked for whatever is there")

check("and the charge carries a stable operation id, so a reload cannot bill twice",
      'string operationId = branchId + ":clearsquad:" + clearSquadCount + ":restocking";' in squad
      and 'PostTransaction(operationId, -amount, "RR_Clear_RestockingReason", BranchId)' in squad,
      "-- the clearance number is in the id, so a second clearance is a second charge and a "
      "replay of the first is not")

check("AND NOBODY IS CHARGED FOR A CLEARANCE THAT PUT NO ONE ON THE MAP",
      squad.index("if (payload.Count == 0)") < squad.index("long charged = ChargeRestocking();"),
      "-- billing twenty-five million and landing nobody would be worse than the failure itself. "
      "The early return is above the charge, in that order, and this claim is the order")

# =============================================================== NEVER LOSING THE GAME
check("THE PLAYER NEVER LOSES THE GAME",
      "if (Find.GameEnder != null) { Find.GameEnder.gameEnding = false; }" in squad,
      "-- *\"this happens in game with the player never losing the game\"*. Core clears it once a "
      "map holds a free colonist, so three arrivals are usually enough. **This is a guarantee, "
      "and usually is not one**")

# =============================================================== THE LETTER
check("THE PLAYER IS TOLD, IN NUMBERS, WHAT WAS DONE TO THEM",
      "<RR_Clear_Title>" in keyed and "<RR_Clear_Body>" in keyed
      and "<RR_Clear_RestockingReason>" in keyed and "<RR_Event_ClearSquad>" in keyed
      and 'Find.LetterStack.ReceiveLetter(' in squad
      and '"RR_Clear_Title".Translate(),' in squad,
      "-- this is the only account they ever get of what happened while nobody was conscious")

body = keyed.split("<RR_Clear_Body>")[1].split("</RR_Clear_Body>")[0]
check("and the letter uses every argument it is given",
      all(("{%d}" % index) in body for index in range(7)),
      "-- a letter that takes seven and prints five shows the player a placeholder")

check("and the restocking reason is the owner's own words",
      "Restocking the petty cash" in keyed,
      "-- *\":restocking the pedycash\"*")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the squad is reached, scoped to the laboratory, and the laboratory is open "
      "again without its people")
