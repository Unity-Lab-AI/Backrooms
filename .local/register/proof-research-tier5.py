# -*- coding: utf-8 -*-
"""Assert tier 5 moves four real knobs, that its FIVE absences are correct, and that the two
guarantees it sits next to are still absolutes rather than tech gates.

The property this exists for
---------------------------
Same as tier 4's, one band up, and with one new hazard that tier 4 did not have.

**Tier 5 was chosen from a sweep rather than invented.** `docs/research/RESEARCH_T5_T6_SWEEP.md`
enumerated 278 numeric constants across 232 files against three tests and proposed six candidates;
the owner picked. Four were CONFIDENT and are built. One is blocked on content (Spatial T6 needs a
sixth palette band). **And one was superseded hours after being approved**, which is the claim in
this file a reader cannot get from the def file:

    Owner, asked which tiers to build: "All six, including the fourth crew member"
    Owner, minutes later, on a different question:
        "rememberber pawns can cross gate as they plkease so no max number"

The fifth candidate WAS the fourth crew member -- a project whose whole effect was raising
`CrewPlanner.MaxCrew` from three to four. **With no maximum there is nothing to raise**, so building
it would have shipped *"a project that promises something and changes nothing"*, which is the exact
phrase `RR_CompanyProjects.xml` deleted four projects for at 0.12.5-dev.

**So this proof asserts the absence AND the condition that makes the absence correct.** If a crew
cap is ever reintroduced, claim 2.1 starts failing -- which is the right behaviour, because at that
moment a Fieldcraft tier 5 becomes buildable again and somebody should be told rather than left to
rediscover the sweep.

The new hazard: a tier that subtracts
-------------------------------------
Entities T5 is the only project in the whole tree that **buys safety by subtracting content**, and
the sweep attached a reservation to it rather than a recommendation. The owner confirmed the narrow
reading at a second fork: take `MaxEventsPerOpening`, leave `CoordinatePressureLadder
.QuietRoomFraction` alone. *"The first is pacing; the second is a promise."*

**That reservation is enforced here rather than remembered.** `QuietRoomFraction` is half of the
solo-survivability guarantee -- *half of every coordinate's rooms bare by count rather than by
chance* -- and **a research project that moves a guarantee turns an absolute into a tech gate.** The
restraint is asserted the way the frontier restraint is asserted in `proof-research-branches.py`: by
reading the deciding function's own body, comments stripped, rather than by looking for a capability
name somewhere in the vicinity. A rule about code must read code, and proximity is not the thing
that happens.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
PROJECTS = os.path.join(MOD, "Defs", "RimroomsProjectDefs", "RR_CompanyProjects.xml")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def defs():
    """Every project def as defName -> body, comments stripped.

    Stripped for the same reason tier 4's proof strips them, and the reason is sharper here: the
    tier 5 comment block NAMES every absence and quotes the superseded answer, so an unstripped
    search would find the explanation for an absence and read it as the absence being filled.
    Checker 29 made exactly this mistake on its first run.
    """
    text = strip_xml_comments(read(PROJECTS))
    found = {}
    for match in re.finditer(
            r"<RimroomsAsyncIndustries\.Investigation\.RimroomsProjectDef>(.*?)"
            r"</RimroomsAsyncIndustries\.Investigation\.RimroomsProjectDef>", text, re.S):
        body = match.group(1)
        name = re.search(r"<defName>([^<]+)</defName>", body)
        if name:
            found[name.group(1).strip()] = body
    return found


def body_of(text, signature):
    """One method's body, by signature, to the first dedented close brace.

    The same technique `proof-research-branches.py` uses for `FrontiersFor`. **Reading the deciding
    function is the whole point**: a restraint keyed on a capability name appearing within N
    characters of a constant fails the moment a legitimate capability-aware line is written nearby,
    which is a mistake this repository has made and paid for.
    """
    at = text.find(signature)
    if at < 0:
        return None
    end = text.find("\n        }", at)
    return text[at:end] if end > at else text[at:]


project = defs()
source = {}
for root, _, files in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in files:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))
all_source = "\n".join(source.values())

TIER5 = {
    "RR_Facilities_ServicingRegime":
        ("RR_Cap_ServicingRegime", "RR_Facilities_PractisedDialling"),
    "RR_Measurement_TrainedEye":
        ("RR_Cap_TrainedEye", "RR_Measurement_StatementDiscipline"),
    "RR_Spatial_NearExit":
        ("RR_Cap_NearExit", "RR_Spatial_SurfaceReading"),
    "RR_Entities_QuietProtocol":
        ("RR_Cap_QuietProtocol", "RR_Entities_SteadyNerve"),
}

# The branches that get no tier 5, and the reason each absence is a finding rather than a gap.
DECLINED = {
    "RR_Fieldcraft_": "superseded: its subject was the crew cap, and there is no longer a cap",
    "RR_Gate": "nothing exists above a connection that no longer counts down",
    "RR_Logistics_": "every Procurement knob is claimed by tiers 0 to 3",
    "RR_Commerce_": "its candidates became player settings at 0.12.98-dev",
}

print("")
print("proof: tier 5 moves four real knobs, declines four branches, and moves no guarantee")
print("")

# ------------------------------------------------------------------ 1. the four
print("1. four projects, each moving a knob real code reads")
at_tier = [b for b in project.values() if "<insightCost>6</insightCost>" in b]
check("exactly four projects cost insight 6", len(at_tier) == 4, "-- found %d" % len(at_tier))
for name, (capability, prerequisite) in sorted(TIER5.items()):
    body = project.get(name)
    check("%s exists" % name, body is not None)
    if body is None:
        continue
    check("%s is tier 5 by cost and gate" % name,
          "<insightCost>6</insightCost>" in body and
          "<workRequired>22000</workRequired>" in body and
          "<minimumIntellectual>8</minimumIntellectual>" in body)
    check("%s asks for five routes, four distortions and three entity logs" % name,
          "<requiredRouteLogs>5</requiredRouteLogs>" in body and
          "<requiredDistortionLogs>4</requiredDistortionLogs>" in body and
          "<requiredEntityLogs>3</requiredEntityLogs>" in body,
          "-- the ladder shape continues tiers 0 to 4 rather than restarting")
    check("%s climbs its own branch" % name,
          "<li>%s</li>" % prerequisite in body,
          "-- a tier 5 whose prerequisite is another branch would be a chokepoint")
    check("%s grants %s" % (name, capability), "<li>%s</li>" % capability in body)
    reads = [p for p, text in source.items() if 'HasCapability("%s")' % capability in text]
    check("%s is read by exactly one source file" % capability, len(reads) == 1,
          "-- read by %d" % len(reads))

# ------------------------------------------------------------------ 2. the absences
print("")
print("2. four branches have no tier 5, and each absence is still correct")
for prefix, reason in sorted(DECLINED.items()):
    offenders = [name for name, body in project.items()
                 if name.startswith(prefix) and "<insightCost>6</insightCost>" in body]
    check("no %s project costs insight 6" % prefix.rstrip("_"), not offenders,
          "-- %s; found %s" % (reason, ", ".join(sorted(offenders))))
check("no Transport project exists at all, at any tier",
      not any(name.startswith("RR_Transport") for name in project),
      "-- the eighth branch is deliberately empty at the BOTTOM, so a top is incoherent")

# 2.1 THE CONDITION THAT MAKES THE FIELDCRAFT ABSENCE CORRECT, and the one claim here that is
#     expected to start failing one day. A reintroduced crew cap makes "the fourth hand" buildable
#     again, and the right outcome then is a failing proof naming the sweep rather than a silent gap.
planner = source.get(os.path.join(SRC, "Expedition", "CrewPlanner.cs"), "")
# **THE FIRST DRAFT OF THIS CLAIM WAS WRONG AND THE CODE WAS RIGHT.** It refused any
# `crew.Count > <digit>`, which matches `run.crew.Count > 0` and `run.rescueCrew.Count > 0` -- both
# LOWER bounds, and the lower bound of one is deliberate: a dispatch with nobody in it is not a trip.
# An upper bound is a comparison against two or more, so that is what this looks for. Widening a rule
# until existing code passes is how a rule stops meaning anything; narrowing it to the thing it is
# actually about is not the same move.
upper_bound = re.search(r"[Cc]rew\.Count\s*>=?\s*([2-9]|\d\d+)", all_source)
check("THERE IS NO CREW CAP, WHICH IS WHY THE FOURTH HAND CANNOT BE A TIER",
      "MaxCrew" not in all_source and upper_bound is None and planner != "",
      "-- the owner: \"rememberber pawns can cross gate as they plkease so no max number\". If a "
      "cap is ever back, a Fieldcraft tier 5 is buildable again and this claim is how anybody "
      "finds that out. Found %r" % (upper_bound.group(0) if upper_bound else "MaxCrew"))

# ------------------------------------------------------------------ 3. the guarantees
print("")
print("3. the two guarantees this tier sits next to are still absolutes")
ladder = source.get(os.path.join(SRC, "Threats", "CoordinatePressureLadder.cs"), "")
required = body_of(ladder, "public static int RequiredQuietRooms(int roomCount)")
quiet_room = body_of(ladder, "public static bool IsQuietRoom(")
check("the quiet-room derivation is declared where this expects it",
      required is not None and quiet_room is not None)
check("QUIET ROOMS ARE NOT RESEARCH-DRIVEN, WHICH THE OWNER CONFIRMED AT A SECOND FORK",
      required is not None and "Capability" not in required
      and quiet_room is not None and "Capability" not in quiet_room,
      "-- half of every coordinate's rooms stay bare BY COUNT. A capability here would turn the "
      "solo-survivability guarantee into a tech gate, which is a promise becoming a purchase")
check("the quiet fraction itself is untouched",
      "QuietRoomFraction = 0.5f" in ladder,
      "-- the sweep offered this constant to Entities T5 and the owner declined it")
check("the absolute encounter ceiling is untouched and not research-driven",
      "MaxSimultaneousEncounters = 3" in ladder
      and not re.search(r"HasCapability\([^)]*\)\s*\?\s*\w*MaxSimultaneousEncounters", ladder),
      "-- no combination of depth, wealth, history or RESEARCH may exceed it")

events = source.get(os.path.join(SRC, "Threats", "AnomalyEventService.cs"), "")
check("the quiet protocol subtracts to one and never to none",
      "QuietProtocolEventsPerOpening = 1" in events
      and "MaxEventsPerOpening = 2" in events,
      "-- an opening where nothing COULD happen is not a quieter coordinate, and this is the only "
      "project in the tree that pays for safety by subtracting content")
check("the event ceiling is asked once per arrival, from one place",
      len(re.findall(r"int ceiling = EventCeiling\(\);", events)) == 1
      and len(re.findall(r"private static int EventCeiling\(\)", events)) == 1,
      "-- two derivations of one rule is the defect this project keeps meeting")

# ------------------------------------------------------------------ 4. each knob's own restraint
print("")
print("4. every one of the four moved a number without removing a floor")
servicing = source.get(os.path.join(SRC, "Gate", "NativeGateServicing.cs"), "")
check("the servicing project moves WEAR, not the assembly's capacity",
      "ServiceCapacityTicks = 600000" in servicing
      and "RegimeWearFactor = 0.5f" in servicing
      and not re.search(r"HasCapability\([^)]*\)\s*\?\s*\w*ServiceCapacityTicks", servicing),
      "-- capacity is the denominator every saved serviceConditionTicks is read against, so "
      "raising it would make a completed research project read as every gate half empty")
check("the technician's saving deepens and the untrained figure is unchanged",
      "TechnicianServiceFactor = 0.7f" in servicing
      and "RegimeTechnicianServiceFactor = 0.5f" in servicing
      and "ReconditionWorkRequired { get { return 1400f; } }" in servicing,
      "-- the card says a TECHNICIAN does it faster, so the certification stays worth earning")

tells = source.get(os.path.join(SRC, "Generation", "FixtureTellService.cs"), "")
tell_step = re.search(r"TrainedEyeTellPercent = (\d+)", tells)
check("the trained eye moves the tell share one step rather than uncapping it",
      "TellPercent = 12" in tells and tell_step is not None
      and 12 < int(tell_step.group(1)) <= 25,
      "-- the sweep's own reservation: at 12% a wrong fixture is an event, at 50% it is wallpaper")
check("the tell share is asked through one function, so both figures cannot drift apart",
      len(re.findall(r"private static int MarkedPercent\(\)", tells)) == 1
      and "roll % 100 >= MarkedPercent()" in tells)

exits = source.get(os.path.join(SRC, "Portals", "WorldExit.cs"), "")
near_min = re.search(r"NearExitMinimumTiles = (\d+)", exits)
check("the near exit keeps a floor above the branch's own doorstep",
      near_min is not None and int(near_min.group(1)) >= 2
      and "NearExitMaximumTiles = 10" in exits,
      "-- a way out that surfaces beside the headquarters is a second front door, not a way out")
check("THE NARROWED BAND CAN ONLY ADD: the full band still answers when it finds nothing",
      exits.count("TileFinder.TryFindNewSiteTile(out destination, from,") == 2
      and "WorldExitMinimumTiles, WorldExitMaximumTiles, allowCaravans: false" in exits
      and "if (!found)" in exits,
      "-- a tier that sometimes COST a branch a way out is a tier a player learns to regret")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: four real knobs, five deliberate absences, and no guarantee became a tech gate")
