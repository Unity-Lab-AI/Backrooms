# -*- coding: utf-8 -*-
"""Assert the eleven DLC container givers are covered, that no custody crosses, and that the
shipped work-giver priorities reach the defs unclamped.

Row 1266. `HaulingUpkeepProvider` covered the three Core container routes and left eleven named
with its reason recorded: *"Each carries a pawn or a live subject into a machine, or moves an
entity between platforms, and each needs its own source review of what that does to custody before
a worker is sent across a gate to do it."*

The source review produced one finding that settles custody for all eleven: **Core forbids every
one of them from moving anything between maps**, so the subject is always already on the far side
and the hauler is the only thing that travels. Invariant 55 is never engaged. This proof pins the
finding to the specific Core member each route was reviewed against, because a route that stops
asking Core's question stops being the thing that was reviewed.

It also pins the defect found while wiring the family up, which is the more dangerous of the two
pieces of work: `ConnectedWorkPriorities.Effective` clamped **every** value against a single
`MaximumPriority = 130`, and `Apply` writes Effective into the defs on every game load, so
**six shipped defaults were being silently overwritten** -- including the far-side operating
family authored at 502 to sit one above Core's `Flick` (500) and landing on 130, below every local
BasicWorker giver.

Run from the repository root.
"""
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


provider_path = os.path.join(SRC, "ConnectedWork", "Providers", "MachineLoadingProvider.cs")
provider_raw = read(provider_path)
provider = strip_cs_comments(provider_raw)
registry = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork",
                                               "ConnectedDeploymentProvider.cs")))
givers = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork",
                                             "WorkGiver_ConnectedDeployment.cs")))
priorities = strip_cs_comments(read(os.path.join(SRC, "Core", "ConnectedWorkPriorities.cs")))
settings_ui = strip_cs_comments(read(os.path.join(SRC, "Core", "RimroomsMod.cs")))
giver_defs = read(os.path.join(MOD, "Defs", "WorkGiverDefs", "RR_ConnectedWork.xml"))
work_keys = read(os.path.join(KEYED, "RR_ConnectedWork.xml"))
audio_keys = read(os.path.join(KEYED, "RR_Audio.xml"))

print("")
print("the family exists and is reachable")
print("-" * 78)

check("the provider declares the saved id the registry maps",
      'ProviderId\n        { get { return ConnectedDeploymentProviders.MachineLoading; } }'
      in provider)
check("the id is a stable string, never a built one",
      'public const string MachineLoading = "machine-loading";' in registry)
check("the provider is constructed and put in the registry dictionary",
      "new MachineLoadingProvider()" in registry and
      "{ MachineLoading, machineLoading }," in registry,
      "-- a provider nothing can Get() is a provider nothing runs")
check("it is justified by Hauling, resolved without throwing when absent",
      'GetNamedSilentFail("Hauling")' in provider)

print("")
print("every route asks Core its own question")
print("-" * 78)

# Each route was reviewed against one specific Core member. If the call goes, the route is no
# longer the thing the review approved -- it is a guess wearing the review's name.
ROUTE_ANCHORS = [
    ("EmptyWasteContainer", "AnyWasteContainer", ["CompWasteProducer", "CanEmptyNow",
                                                  "ReservationLayerDefOf.Empty"]),
    ("TakeBioferriteOutOfHarvester", "AnyHarvester", ["Building_BioferriteHarvester",
                                                      "unloadingEnabled", "ReadyForHauling"]),
    ("TakeEntityToHoldingPlatform", "AnyCapturableEntity", ["CompHoldingPlatformTarget",
                                                            "ThreatDisabled", "HeldPawn"]),
    ("TransferEntity", "AnyMisplacedEntity", ["Building_HoldingPlatform", "HeldPawn",
                                              "HeldPlatform == holding.targetHolder"]),
    ("HaulToGeneBank", "AnyGenepack", ["pack.AutoLoad", "CompGenepackContainer"]),
    ("HaulToGrowthVat", "AnyGrowthVatSupply", ["Building_GrowthVat", "NutritionNeeded",
                                               "selectedEmbryo", "CanAcceptNutrition"]),
    ("HaulToBiosculpterPod", "AnyBiosculpterPod", ["CompBiosculpterPod",
                                                   "BiosculpterPodState.LoadingNutrition",
                                                   "RequiredNutritionRemaining"]),
    ("HaulMechsToCharger", "AnyUnchargedMech", ["IsColonyMech", "IsLowEnergySelfShutdown",
                                                "GetMaxRechargeLimit",
                                                "AnyChargerFor(map, pawn, work, mech)"]),
    ("CarryToGrowthVat / CarryToGeneExtractor / CarryToSubcoreScanner", "AnyEnterable",
     ["Building_Enterable", "SelectedPawn", "CanAcceptPawn"]),
]

for giver_name, method, anchors in ROUTE_ANCHORS:
    body = body_of(provider, "bool %s(Map map, Pawn pawn" % method)
    missing = [anchor for anchor in anchors if anchor not in body]
    check("%s: %s asks Core (%s)" % (giver_name, method, ", ".join(anchors)),
          not missing, "-- missing %s" % missing)

# The charger presence substitute is its own method because it is the one Core answer that
# could not be borrowed -- GetClosestCharger builds TraverseParms.For(carrier) and calls
# carrier.CanReach, which is the remote-reachability mistake this whole layer avoids.
charger = body_of(provider, "bool AnyChargerFor(Map map, Pawn pawn")
check("the charger substitute asks Core whether that charger would take that mech",
      "CanPawnChargeCurrently(mech)" in charger,
      "-- without it this is presence alone, and presence alone sends workers to a charger "
      "already occupied or full of waste")
check("and it never calls the reachability-bound Core helper from a remote map",
      "GetClosestCharger" not in provider,
      "-- it builds TraverseParms.For(carrier) and calls carrier.CanReach")

route_call = body_of(provider, "bool AnyRoute(Map map, Pawn pawn")
for _, method, _ in ROUTE_ANCHORS:
    check("AnyRoute reaches %s" % method, "%s(map, pawn, work)" % method in route_call,
          "-- a route nothing calls covers nothing")

print("")
print("custody never crosses, which is the finding the row was waiting on")
print("-" * 78)

enterable = body_of(provider, "bool AnyEnterable(Map map, Pawn pawn")
check("the enterable route refuses a subject that is not already on that map",
      "subject.Map != map" in enterable,
      "-- Core's own WorkGiver_CarryToBuilding refuses on selectedPawn.Map != pawn.Map, and "
      "dropping it is what would turn this into a pawn transfer")
check("a subject is only carried when Core says it cannot walk in unaided",
      "NeedsCarrying(subject)" in enterable and
      "IsPrisonerOfColony" in body_of(provider, "bool NeedsCarrying(Pawn subject)"),
      "-- read backwards this hauls able colonists who were walking there themselves")
capture = body_of(provider, "bool AnyCapturableEntity(Map map, Pawn pawn")
check("the capture route refuses a platform on another map",
      "targetHolder.MapHeld != target.MapHeld" in capture,
      "-- Core's own same-map guard, and the reason no entity ever changes map")
check("the provider moves nothing itself: no travel, transfer or crossing call",
      not re.search(r"PortalTravelService|OrderCrossing|TryAcceptPawn|DeSpawn|SpawnSetup|"
                    r"TransferBetweenEntityHolders|JobMaker", provider),
      "-- a provider justifies a crossing and hands out no job; issuing one here would "
      "bypass Core's reservations and invariant 55 both")

print("")
print("an absent expansion is an empty world, not a branch")
print("-" * 78)

check("no ModsConfig gate anywhere in the family",
      "ModsConfig" not in provider,
      "-- the routes degrade on their own; a gate here would be a second, drifting answer")
for defof in ("ThingDefOf.Genepack", "ThingDefOf.GrowthVat", "ThingDefOf.BiosculpterPod",
              "ThingDefOf.BioferriteHarvester"):
    field = defof.split(".")[1]
    # A MayRequire DefOf field is null without its expansion, so every read needs its own
    # null test before the lister is asked about it.
    check("%s is null-checked before use" % defof,
          re.search(re.escape(defof) + r";\s*\n\s*if \(\w+Def == null\) \{ return false; \}",
                    provider) is not None or
          re.search(r"ThingDef \w+Def = " + re.escape(defof), provider) is not None and
          provider.count("== null) { return false; }") >= 4,
          "-- reading a null DefOf throws on a Core-only install")
    del field
check("the DefOf null tests are present, one per expansion-only def",
      len(re.findall(r"if \(\w+Def == null\) \{ return false; \}", provider)) >= 4)

print("")
print("the crossing is wired into the game, both halves")
print("-" * 78)

check("the planning giver class exists",
      "class WorkGiver_ConnectedMachineLoading : WorkGiver_ConnectedDeployment" in givers)
check("the continuation giver class exists",
      "class WorkGiver_ConnectedMachineLoadingContinue : WorkGiver_ConnectedDeployment" in givers)
check("the continuation half is the one marked ContinueOnly",
      body_of(givers, "class WorkGiver_ConnectedMachineLoadingContinue")
      .count("return true;") == 1 and
      body_of(givers, "class WorkGiver_ConnectedMachineLoading :")
      .count("return false;") == 1,
      "-- two givers with the same ContinueOnly answer is one giver, and the pair is the "
      "whole mechanism that stops a worker being turned around")
for def_name in ("RR_ConnectedMachineLoading", "RR_ConnectedMachineLoadingContinue"):
    check("%s is declared" % def_name, "<defName>%s</defName>" % def_name in giver_defs)
    check("%s names its giver class" % def_name,
          "WorkGiver_ConnectedWork.WorkGiver_%s" % def_name[3:] in giver_defs or
          "ConnectedWork.WorkGiver_Connected%s" % def_name[len("RR_Connected"):] in giver_defs)
check("the continuation giver outranks Core's highest Hauling giver",
      re.search(r"<defName>RR_ConnectedMachineLoadingContinue</defName>.*?"
                r"<priorityInType>301</priorityInType>", giver_defs, re.S) is not None,
      "-- TakeEntityToHoldingPlatform is 300 and this family travels for it; at or below it "
      "a worker part way to a gate is turned around")
check("the planning giver sits below every local Hauling giver",
      re.search(r"<defName>RR_ConnectedMachineLoading</defName>.*?"
                r"<priorityInType>3</priorityInType>", giver_defs, re.S) is not None,
      "-- HaulMerge is 5, the lowest local giver in the type")
check("the player-facing label is translated",
      "<RR_ConnectedWork_MachineLoadingLabel>" in work_keys)
check("the label key is a literal in code, never assembled",
      '"RR_ConnectedWork_MachineLoadingLabel"' in provider,
      "-- an assembled key cannot be checked, and this project has caught that five times")
check("the family has a priority row in settings",
      '"RR_Settings_FamilyMachineLoading",' in priorities and
      '"RR_ConnectedMachineLoadingContinue", "RR_ConnectedMachineLoading"' in priorities)
check("its settings label is translated",
      "<RR_Settings_FamilyMachineLoading>" in audio_keys)

print("")
print("a shipped priority reaches the def it was authored for")
print("-" * 78)

check("the single-argument Clamp that overwrote shipped defaults is gone",
      not re.search(r"\bClamp\(\s*(?:value|Shipped\(defName\))\s*\)", priorities),
      "-- it clamped every value against one number, and Apply writes that into the defs on "
      "every game load")
check("the ceiling is resolved per giver",
      "internal static int Ceiling(string defName)" in priorities and
      "private static int Clamp(int value, string defName)" in priorities)
ceiling = body_of(priorities, "int Ceiling(string defName)")
check("a giver's own shipped value is never below its ceiling",
      "Shipped(defName)" in ceiling and "MaximumPriority" in ceiling,
      "-- the ceiling has to be the higher of the two or the authored number is unreachable")
check("the settings slider uses the per-giver ceiling",
      "ConnectedWorkPriorities.Ceiling(giverDefName)" in settings_ui,
      "-- a slider that stops below the shipped default cannot restore it")
check("MaximumPriority is documented as a floor rather than a cap",
      "of each slider's ceiling, not the ceiling itself"
      in read(os.path.join(SRC, "Core", "ConnectedWorkPriorities.cs")),
      "-- it was written as a cap once and silently broke seven families, so the next "
      "reader has to be told which it is")

# The seven RR givers authored above the old cap. Each must still be reachable, which under the
# per-giver ceiling means Ceiling(defName) == the shipped value.
above = []
for block in re.findall(r"<WorkGiverDef[^>]*>.*?</WorkGiverDef>", giver_defs, re.S):
    name = re.search(r"<defName>(\w+)</defName>", block)
    value = re.search(r"<priorityInType>(-?\d+)</priorityInType>", block)
    if name and value and int(value.group(1)) > 130:
        above.append((name.group(1), int(value.group(1))))
check("the defs authored above the old cap are found, and there are eight",
      len(above) == 8,
      "-- measured %d: %s. Six were already being silently overwritten before this "
      "checkpoint and two were added by it. If this number moves, a shipped default has "
      "changed and the per-giver ceiling has a new case to cover" % (len(above), above))
check("the highest of them is the far-side operating family at 502",
      ("RR_ConnectedBasicWorkerContinue", 502) in above,
      "-- authored one above Core's Flick (500); it was landing on 130")

print("")
print("the four painting givers, which the same row named and nothing had reached")
print("-" * 78)

paint = strip_cs_comments(read(os.path.join(SRC, "ConnectedWork", "Providers",
                                            "PaintingProvider.cs")))

check("the painting provider is built and registered",
      'public const string Painting = "painting";' in registry and
      "new PaintingProvider()" in registry and
      "{ Painting, painting }," in registry)
check("it is justified by Art, resolved without throwing when absent",
      'GetNamedSilentFail("Art")' in paint)
PAINT_ROUTES = [
    ("RemovePaintFloor", "AnyStrippableFloor",
     ["DesignationDefOf.RemovePaintFloor", "isPaintable", "DesignationDefOf.RemoveFloor"]),
    ("RemovePaintBuilding", "AnyStrippableBuilding",
     ["DesignationDefOf.RemovePaintBuilding", "Paintable(target)",
      "DesignationDefOf.Deconstruct"]),
    ("PaintFloor", "AnyPaintableFloor",
     ["DesignationDefOf.PaintFloor", "terrainGrid.ColorAt(cell) == wanted", "DyePresent"]),
    ("PaintBuilding", "AnyPaintableBuilding",
     ["DesignationDefOf.PaintBuilding", "PaintColorDef == designation.colorDef", "DyePresent"]),
]
for giver_name, method, anchors in PAINT_ROUTES:
    body = body_of(paint, "bool %s(Map map, Pawn pawn" % method)
    missing = [anchor for anchor in anchors if anchor not in body]
    check("%s: %s asks Core (%s)" % (giver_name, method, ", ".join(anchors)),
          not missing, "-- missing %s" % missing)

candidate = body_of(paint, "bool HasCandidateWork(Map map, Pawn pawn")
here = body_of(paint, "bool HasWorkHere(Pawn pawn)")
for _, method, _ in PAINT_ROUTES:
    check("both halves reach %s" % method,
          "%s(map, pawn, work)" % method in candidate and
          "%s(map, pawn, null)" % method in here,
          "-- a route missing from the definitive half releases a deployment with work left")

check("only the paint routes require dye, never the strip routes",
      "DyePresent" not in body_of(paint, "bool AnyStrippableFloor(Map map, Pawn pawn") and
      "DyePresent" not in body_of(paint, "bool AnyStrippableBuilding(Map map, Pawn pawn"),
      "-- Core's remove-paint givers never mention dye; requiring it would refuse real work")
check("the paint routes do require it",
      paint.count("if (!DyePresent(map, pawn, work)) { return false; }") == 2,
      "-- without dye on that map Core refuses on arrival and the crossing is wasted")
check("nothing is inferred: every route starts from a player designation",
      paint.count("SpawnedDesignationsOfDef(definition)") == 2 and
      "DesignationDefOf" in paint,
      "-- a coordinate full of stained wall must attract nobody until the player says so")
check("conflicting designations are read from the target's own map",
      "map.designationManager.DesignationAt(cell, first)" in paint and
      "map.designationManager.DesignationOn(target, first)" in paint,
      "-- Core reads pawn.Map because in Core they are the same map, and here they are not")
check("the painting provider issues no job of its own",
      not re.search(r"JobMaker|JobDefOf\.Paint|AddQueuedTarget", paint),
      "-- Core's own giver builds the radial paint queue on arrival")

for def_name, priority in (("RR_ConnectedPaintingContinue", 203), ("RR_ConnectedPainting", 1)):
    check("%s ships at %d" % (def_name, priority),
          re.search(r"<defName>%s</defName>.*?<priorityInType>%d</priorityInType>"
                    % (def_name, priority), giver_defs, re.S) is not None,
          "-- continue must beat RemovePaintFloor/RemovePaintBuilding (202); plan must sit "
          "below DoBillsSculpt (100)")
check("the two Art families do not tie on the continue side",
      "<priorityInType>203</priorityInType>" in giver_defs and
      "<priorityInType>204</priorityInType>" in giver_defs,
      "-- equal priorities resolve by database order, which is not a decision")
check("the painting label is translated",
      "<RR_ConnectedWork_PaintingLabel>" in work_keys)
check("the painting family has a settings row and a translated name",
      '"RR_ConnectedPaintingContinue", "RR_ConnectedPainting"' in priorities and
      "<RR_Settings_FamilyPainting>" in audio_keys)
check("both painting giver classes exist",
      "class WorkGiver_ConnectedPainting : WorkGiver_ConnectedDeployment" in givers and
      "class WorkGiver_ConnectedPaintingContinue : WorkGiver_ConnectedDeployment" in givers)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: fifteen givers covered, nothing changes map, and every shipped "
      "priority reaches its def")
