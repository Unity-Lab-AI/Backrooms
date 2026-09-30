# -*- coding: utf-8 -*-
"""One proof for the 0.12.36-dev batch: four area types across a gate, staff debrief and
quarantine, and the two ordinary-map rows that turned out to be already true.

Rows: 1215 / 1235 / 1239 (the four area types), 761's last two halves (debrief, quarantine),
98 and 99 (mining and building behind a gate, and the linked-equipment exception).

The three area rows carried their own expiry condition. `ZONES_AND_AREAS_ACROSS_A_GATE.md`
recorded `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` as
**not covered and correctly so**, because a Backrooms coordinate is all thick rock, roof removal
there is forbidden by the world rule, and it has no outside and therefore no weather -- with
*"revisit when the ordinary-map endpoint lands"* attached. It landed at 0.6.9-dev, so the reason
expired and the rows became real work.

Row 99's premise turned out to be **wrong about this mod**, which is why it closes by proof rather
than by code: the row says linked equipment has placement requirements *"because a link has a
reach"*, and this mod deliberately has **no distance check and no line-of-sight check** on a gate
link, by owner direction *"reach fare and through walls"*.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
KEYED = os.path.join(MOD, "Languages", "English", "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError("unbalanced body for %r" % signature)


roof = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork", "Providers",
                                           "RoofWorkProvider.cs")))
upkeep = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork", "Providers",
                                             "UpkeepProviders.cs")))
debrief = strip_cs_comments(read(os.path.join(SRC, "Company", "StaffDebrief.cs")))
expedition = strip_cs_comments(read(os.path.join(SRC, "Expedition",
                                                 "RimroomsExpeditionComponent.cs")))
campaign = strip_cs_comments(read(os.path.join(SRC, "Company",
                                               "RimroomsCampaignComponent.cs")))
registry = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork",
                                               "ConnectedDeploymentProvider.cs")))
givers = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork",
                                             "WorkGiver_ConnectedDeployment.cs")))
priorities = strip_cs_comments(read(os.path.join(SRC, "Core",
                                                 "ConnectedWorkPriorities.cs")))
pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsFacilities.cs")))
gate = strip_cs_comments(read(os.path.join(SRC, "Gate", "CompRimroomsGate.cs")))
links = strip_cs_comments(read(os.path.join(SRC, "Gate", "GateEquipmentLinks.cs")))
approach = strip_cs_comments(read(os.path.join(SRC, "Portals",
                                               "PlaceWorker_GateApproach.cs")))
containment = strip_cs_comments(read(os.path.join(SRC, "Generation",
                                                  "BackroomsContainment.cs")))
giver_defs = read(os.path.join(MOD, "Defs", "WorkGiverDefs", "RR_ConnectedWork.xml"))
work_keys = read(os.path.join(KEYED, "RR_ConnectedWork.xml"))
audio_keys = read(os.path.join(KEYED, "RR_Audio.xml"))
company_keys = read(os.path.join(KEYED, "RR_Company.xml"))
expedition_keys = read(os.path.join(KEYED, "RR_Expedition.xml"))

print("")
print("roof areas: its own family, and the reason is a number")
print("-" * 78)

check("the roof provider exists and is registered",
      'public const string RoofWork = "roof-work";' in registry and
      "new RoofWorkProvider()" in registry and
      "{ RoofWork, roofWork }," in registry)
check("it is justified by Construction",
      'GetNamedSilentFail("Construction")' in roof)
build = body_of(roof, "bool AnyRoofToBuild(Map map, Pawn pawn")
remove = body_of(roof, "bool AnyRoofToRemove(Map map, Pawn pawn")
check("the build route reads that map's own BuildRoof area",
      "map.areaManager.BuildRoof" in build and "area.TrueCount == 0" in build,
      "-- Core's own ShouldSkip is exactly this TrueCount test")
check("and refuses a cell that is already roofed",
      "cell.Roofed(map)) { continue; }" in build)
check("and asks Core's own cheap roof-holder refusal",
      "RoofCollapseUtility.WithinRangeOfRoofHolder(cell, map)" in build,
      "-- a cell too far from anything that could hold a roof can never be roofed")
check("the thorough connected-to-holder walk is left to arrival",
      "ConnectedToRoofHolder" not in roof,
      "-- it walks the roof grid and always agrees when the cheap one refuses; asking the "
      "cheap one remotely is the standing necessary-not-sufficient split")
check("the remove route reads that map's own NoRoof area",
      "map.areaManager.NoRoof" in remove and "!cell.Roofed(map)) { continue; }" in remove)
check("both routes reserve against the ceiling layer when standing there",
      roof.count("ReservationLayerDefOf.Ceiling") == 2,
      "-- Core reserves roof work on its own layer, and a cell can be worked by one pawn")
check("both routes are reached from both halves",
      "AnyRoofToBuild(map, pawn, work)" in roof and
      "AnyRoofToRemove(map, pawn, work)" in roof and
      "AnyRoofToBuild(pawn.Map, pawn, null)" in roof and
      "AnyRoofToRemove(pawn.Map, pawn, null)" in roof)
check("the provider hands out no job of its own",
      not re.search(r"JobMaker|JobDefOf\.(BuildRoof|RemoveRoof)", roof))

check("the continuation giver outranks Core's BuildRoofs",
      re.search(r"<defName>RR_ConnectedRoofWorkContinue</defName>.*?"
                r"<priorityInType>101</priorityInType>", giver_defs, re.S) is not None,
      "-- BuildRoofs is 100 and RemoveRoofs is 90; at or below either, a worker part way to a "
      "gate is turned around")
check("the planning giver sits below every local Construction giver",
      re.search(r"<defName>RR_ConnectedRoofWork</defName>.*?"
                r"<priorityInType>1</priorityInType>", giver_defs, re.S) is not None,
      "-- ConstructSmoothWalls is 10, the lowest in the type")
check("the finishing family's 82 is untouched, which is why this is a separate family",
      re.search(r"<defName>RR_ConnectedConstructionFinishingContinue</defName>.*?"
                r"<priorityInType>82</priorityInType>", giver_defs, re.S) is not None,
      "-- hanging roof routes on it would have put them below the givers they travel for, and "
      "raising 82 would have lifted frame finishing over roof work too")
check("both roof giver classes exist",
      "class WorkGiver_ConnectedRoofWork : WorkGiver_ConnectedDeployment" in givers and
      "class WorkGiver_ConnectedRoofWorkContinue : WorkGiver_ConnectedDeployment" in givers)
check("the roof label and settings row exist",
      "<RR_ConnectedWork_RoofWorkLabel>" in work_keys and
      "<RR_Settings_FamilyRoofWork>" in audio_keys and
      '"RR_ConnectedRoofWorkContinue", "RR_ConnectedRoofWork"' in priorities)

print("")
print("snow, sand and pollution: routes on the cleaning family, whose number already held")
print("-" * 78)

weather = body_of(upkeep, "bool AnyWeatherToClear(Map map, Pawn pawn")
marked = body_of(upkeep, "bool AnyMarked(Map map, Pawn pawn")
check("both weather areas are read from that map",
      "map.areaManager.SnowOrSandClear" in weather and
      "map.areaManager.PollutionClear" in weather)
check("the snow test is Core's own OR of snow depth and sand depth",
      "map.snowGrid.GetDepth(cell) < 0.2f && cell.GetSandDepth(map) < 0.2f" in marked,
      "-- either depth alone is enough for Core, and an AND here would refuse real work")
check("the pollution test is Core's own grid question",
      "map.pollutionGrid.IsPolluted(cell)" in marked)
check("a null pollution grid is the only gate the pollution route needs",
      "map.pollutionGrid == null) { return false; }" in marked,
      "-- it is null without Biotech; an absent expansion is an empty world, not a condition")
check("both halves of the cleaning family reach the weather routes",
      "AnyWeatherToClear(map, pawn, work)" in upkeep and
      "AnyWeatherToClear(pawn.Map, pawn, null)" in upkeep)
check("the cleaning continuation already outranks both givers it now travels for",
      re.search(r"<defName>RR_ConnectedCleaningContinue</defName>.*?"
                r"<priorityInType>22</priorityInType>", giver_defs, re.S) is not None,
      "-- CleanClearSnow is 10 and CleanClearPollution is 0, so no new family was needed; "
      "this is the check that decided snow rides cleaning and roofs did not ride finishing")
check("the cleaning family hands out no job of its own",
      "JobMaker" not in upkeep)

print("")
print("the Backrooms world rule still keeps itself")
print("-" * 78)

check("BackroomsContainment still empties the no-roof area on a coordinate",
      "Area_NoRoof" in containment or "NoRoof" in containment,
      "-- roof removal inside the Backrooms is forbidden, and the containment component is "
      "what enforces it; the roof family must find nothing there rather than be told not to look")
check("the roof provider contains no Backrooms exception of its own",
      "Backrooms" not in roof and "Coordinate" not in roof,
      "-- the rule keeps itself by emptying the area; a second check here would be a second "
      "opinion that could drift from it")

print("")
print("debrief and quarantine are one mechanism")
print("-" * 78)

blocker = body_of(debrief, "string DebriefBlocker(Pawn crewMember, Pawn interviewer)")
check("nobody debriefs themselves, and it is refused first among the pair rules",
      "interviewer == crewMember) { return \"RR_Debrief_SelfReport\"; }" in blocker,
      "-- the only refusal that cannot be worked around by waiting")
check("the report is taken at home, not on the far side",
      "crewMember.Map != Headquarters" in blocker,
      "-- a report given standing in the room you are reporting about is not a debrief")
check("the interviewer must be present with them",
      "interviewer.Map != crewMember.Map" in blocker)
check("the Social floor is the interview floor, not a second number",
      "InterviewerSocialFloor" in blocker and
      not re.search(r"MinimumDebrief\w*\s*=\s*\d", debrief),
      "-- a branch that has practised taking statements has practised taking statements; a "
      "second constant here would be a second opinion about one capability")
check("the blocker is separate from the action so a surface can show the reason",
      "CompanyActionResult DebriefCrewMember(Pawn crewMember, Pawn interviewer)" in debrief and
      "string blocker = DebriefBlocker(crewMember, interviewer);" in debrief,
      "-- invariant 28: the rule has to be learnable before it is hit")

take = body_of(debrief, "CompanyActionResult DebriefCrewMember(Pawn crewMember, Pawn interviewer)")
check("taking the report clears the hold and records that it happened",
      "debriefHolds.Remove(hold);" in take and
      'RecordEvent("RR_Event_StaffDebriefed"' in take)
check("it writes no second account of the trip",
      "RecordFieldObservation" not in debrief and "EvidenceRecord" not in debrief,
      "-- the field observations were already written where they were made; a second account "
      "here would be a second source of truth about one trip")
check("it hands out no thought, mood effect or hediff",
      not re.search(r"ThoughtDef|HediffDef|needs\.mood|Thoughts\.", debrief),
      "-- the staff-psychology rows ask that native social behaviour be preserved, and a "
      "debrief that wrote a mood would need a new def as well")

note = body_of(debrief, "void NoteReturnedFromField(IEnumerable<Pawn> crew, string coordinateId)")
check("raising a hold is idempotent per pawn",
      "if (HoldFor(pawn) != null) { continue; }" in note,
      "-- a save reloaded across a completion must not stack two holds on one person")
check("the saved list is capped and drops the oldest",
      "MaximumDebriefHolds" in note and "debriefHolds.RemoveAt(0)" in note,
      "-- it grows on every returned trip, and the newest report is the one still worth hearing")
check("the hold is raised from expedition completion and nowhere else",
      expedition.count("Campaign.NoteReturnedFromField(") == 1 and
      "Campaign.NoteReturnedFromField(run.crew, run.coordinateId);" in
      body_of(expedition, "void Complete(ExpeditionRecord run)"),
      "-- Complete is reached from AllAtHeadquarters, which is the one place 'they came home' "
      "is already established")
check("a stranded or aborted trip raises no hold",
      "NoteReturnedFromField" not in body_of(expedition, "void Strand(ExpeditionRecord run, string key)"),
      "-- those people either are not home or belong to a different procedure")

dispatch = body_of(expedition, "CompanyActionResult Dispatch(CompRimroomsGate gate")
check("QUARANTINE: dispatch refuses a crew member who has not reported in",
      "Campaign.AwaitingDebrief(crew[index])" in dispatch and
      'Refuse("RR_Exp_AwaitingDebrief")' in dispatch,
      "-- this is the whole of quarantine, and it is the consequence that makes the debrief "
      "worth taking")
check("and the hold is NOT wired into traversal",
      "AwaitingDebrief" not in read(os.path.join(SRC, "Portals", "PortalTraversalPolicy.cs")),
      "-- traversal is the chokepoint a player walking one colonist through a door by hand "
      "passes through, and a company procedure has no business refusing that")
check("the holds are persisted",
      "ExposeDebriefs();" in campaign and
      'Scribe_Collections.Look(ref debriefHolds, "rr_debriefHolds", LookMode.Deep);' in debrief)
check("a hold whose pawn is gone from the save is dropped rather than blocking forever",
      "debriefHolds.RemoveAll(hold => hold == null || !hold.IsValid);" in debrief)

debrief_pane = body_of(pane, "void DrawDebriefs(Listing_Standard listing")
check("the pane lists who is waiting",
      '"RR_Debrief_Outstanding".Translate(holds.Count)' in debrief_pane and
      'listing.Label("RR_Debrief_Outstanding"' in debrief_pane,
      "-- a key present in the file is not a claim that anything is drawn")
check("the pane says so when nobody is waiting",
      '"RR_Debrief_NoneOutstanding"' in debrief_pane,
      "-- a section that vanishes when empty cannot teach a player the rule exists")
check("the interviewer choice is deterministic",
      "ThenBy(candidate => candidate.ThingID, StringComparer.Ordinal)" in pane,
      "-- a reload must not change who took the report")
check("the pane never offers the crew member as their own interviewer",
      "candidate != crewMember" in pane,
      "-- the blocker refuses it anyway, and a button whose only outcome is a refusal is worse "
      "than no button")
check("the pane is reached from the facilities pane",
      "DrawDebriefs(listing, campaign);" in pane)

for key in ("RR_Debrief_Outstanding", "RR_Debrief_NoneOutstanding", "RR_Debrief_Row",
            "RR_Debrief_Take", "RR_Debrief_UnknownStaff", "RR_Debrief_NobodyToReport",
            "RR_Debrief_NothingToReport", "RR_Debrief_SelfReport", "RR_Debrief_NotStaff",
            "RR_Debrief_InterviewerUnfit", "RR_Debrief_InterviewerUnskilled",
            "RR_Debrief_NotOurs", "RR_Debrief_NotHome", "RR_Debrief_NotTogether",
            "RR_Event_StaffDebriefed"):
    check("%s is translated" % key, "<%s>" % key in company_keys)
check("RR_Exp_AwaitingDebrief is translated",
      "<RR_Exp_AwaitingDebrief>" in expedition_keys)

print("")
print("rows 98 and 99: ordinary map behind a gate, already true")
print("-" * 78)

# Row 98. The claim is that ordinary map work near a gate cannot stop the gate working. The way to
# prove that is to enumerate what CAN stop it and show none of them reads a neighbouring cell.
# READ EVERY FILE OF THE PARTIAL CLASS, not just CompRimroomsGate.cs.
#
# This check first read that one file, and at 0.12.38-dev it kept passing when a seventh reason
# was added -- because the new one lives in `GateIntegrity.cs`, another file of the same partial
# class. The count was right and the *scope* was wrong, so a claim that reads as "these are all
# the ways a gate can stop working" was really "these are the ways one file can stop it". The
# glob is the fix: a new file of the class is covered the moment it exists.
gate_class = "".join(strip_cs_comments(read(path))
                     for path in sorted(glob.glob(os.path.join(SRC, "Gate", "*.cs"))))
reasons = sorted(set(re.findall(r'EnterEmergency\("(\w+)"\)', gate_class)))
check("the gate's failure reasons are enumerated across the whole partial class, and there "
      "are seven",
      len(reasons) == 7,
      "-- measured %s. If this set grows, row 98 has a new case to check" % reasons)
check("every one is power, the operator, the switch, the clock, an order or the machine's own "
      "condition -- never a neighbour",
      set(reasons) == {"RR_NativeGate_KillSwitchThrown", "RR_Gate_PowerLost",
                       "RR_Gate_OperatorLost", "RR_Gate_WindowExpired",
                       "RR_Gate_TimeCostWindowExhausted", "RR_Gate_EmergencyCutoff",
                       "RR_Gate_IntegrityLost"},
      "-- measured %s" % reasons)
check("and the two that are not the machine failing on its own are named",
      "RR_Gate_EmergencyCutoff" in reasons and "RR_Gate_IntegrityLost" in reasons,
      "-- the cutoff is the player's button and the containment procedure; integrity is damage "
      "to the gate itself. Neither reads a neighbouring cell, so row 98 stands")
check("ROW 98 STILL HOLDS: no reason anywhere in the class reads an adjacent cell",
      not re.search(r"CellsAdjacent|AdjacentCells", gate_class),
      "-- mine it, wall it, roof it, put a bedroom there: the gate does not look")
check("nothing in the gate reads its adjacent cells to decide whether it works",
      not re.search(r"CellsAdjacent|AdjacentCells|CellsAdjacent8Way", gate),
      "-- mine it, wall it, roof it, put a bedroom there: the gate does not look")
check("the one placement constraint is the approach cell, and it is about standing room",
      "Traversability.Standable" in approach and "GenAdj.OccupiedRect" in approach,
      "-- row 113, closed 0.12.27-dev: the approach cell is reserved against blocking, and "
      "flooring is fine because terrain never consults a PlaceWorker")
check("and every uncertainty there returns accepted",
      approach.count("AcceptanceReport.WasAccepted") >= 3,
      "-- a placement worker that guesses wrong must guess in the player's favour")

# Row 99. The row's premise is that linked equipment constrains placement "because a link has a
# reach". This mod deliberately has no reach.
check("ROW 99's premise is wrong about this mod: a gate link has no distance check",
      not re.search(r"maxDistance\s*=|DistanceTo\w*\([^)]*\)\s*[<>]|InHorDistOf", links),
      "-- owner direction was 'reach fare and through walls', so same map and same branch is "
      "the whole spatial rule")
check("and no line-of-sight check either",
      "GenSight" not in links and "requiresLOS = true" not in links)
check("the real link constraints are the power net and single ownership",
      "PowerNet" in links or "CompPower" in links,
      "-- anything with a power component must sit on the gate's own net, and a thing linked "
      "to one gate is refused to every other")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: four area types cross a gate, a debrief gates the next trip, and the "
      "cells around a gate are ordinary map")
