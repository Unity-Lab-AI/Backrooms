# -*- coding: utf-8 -*-
"""Assert tier 4 moves six real knobs, and that its two ABSENCES are deliberate and correct.

The property this exists for
---------------------------
Invariant 136, and the precedent that gives it teeth: **0.12.5-dev deleted four tier 3 projects**
because the systems an unlock would have modified were not written, and they would have been
invented effects. Tier 3 became writeable at 0.12.18-dev only because arc 5 wrote those systems.

So tier 4 was surveyed rather than assumed, and the survey said six, not eight:

    Facilities   dialSpinUpWorkRequired      how long bringing a gate up takes
    Fieldcraft   RecoveryRate                how fast a crew shakes the place off once out
    Commerce     OrdinaryExchangeRate        what the company pays for ordinary goods
    Measurement  MinimumInterviewerSocial    who is allowed to take a statement
    Spatial      WorldFrontierRarity         how often a way in turns up on your own map
    Entities     MaxPenalty                  the worst the place can weigh on somebody

**The two absences are the load-bearing claims in this file**, because an absence cannot be seen by
reading the def file -- a reader sees six projects and has no way to know whether the other two were
considered and declined or simply forgotten:

  * **LOGISTICS** -- lead time (tier 1), dispatch delay (tier 2), order capacity (tier 0) and
    unattended delivery (tier 3) are all claimed. What remains in Procurement is
    `MaximumOpenOrders` at 100, `MaximumPhysicalStacksPerOrder` at 4096 and
    `MaximumStacksDeliveredPerTick` at 4: safety bounds a player will never reach.

  * **THE GATE LINE** -- its fourth rung is already *"a connection that no longer counts down"*,
    and `portalIndefiniteTier` is 4. **There is nothing above indefinite**, so a fifth rung is
    impossible rather than merely unwritten.

And three restraints had to survive the tier:

  * the per-coordinate frontier cap is **not** a research knob (0.12.18-dev);
  * shelter never reaches zero (0.12.18-dev) -- so Entities took the penalty ceiling, not the
    shelter rate a second time;
  * `MaximumNaturalDepth` is **six** since 0.12.49-dev, and **the restraint that no capability may
     move it was RETIRED at 0.12.99-dev** when the owner approved Spatial tier 6, whose whole
     subject is that number. Restated here as what it always protected -- the reach is bounded and
     one place decides it -- and owned in full by `proof-research-tier6.py`. The old claim went on
     passing after the code changed, which is why it is restated out loud rather than quietly.

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

    Stripped because this tier's rationale is written at length in a comment block that names
    Logistics, the gate line and every restraint -- so an unstripped search would find the
    explanation for an absence and read it as the absence being filled.
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


project = defs()
source = {}
for root, _, files in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in files:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))
all_source = "\n".join(source.values())

TIER4 = {
    "RR_Facilities_PractisedDialling": ("RR_Cap_PractisedDialling", "RR_Facilities_SiteNetwork"),
    "RR_Fieldcraft_Decompression": ("RR_Cap_Decompression", "RR_Fieldcraft_WayHomeDiscipline"),
    "RR_Commerce_OpenMarket": ("RR_Cap_OpenMarket", "RR_Commerce_SiteEfficiency"),
    "RR_Measurement_StatementDiscipline": ("RR_Cap_StatementDiscipline", "RR_Measurement_RapidSurvey"),
    "RR_Spatial_SurfaceReading": ("RR_Cap_SurfaceReading", "RR_Spatial_CoordinateReading"),
    "RR_Entities_SteadyNerve": ("RR_Cap_SteadyNerve", "RR_Entities_SpaceDiscipline"),
}

print("")
print("proof: tier 4 moves six real knobs, and declines two branches on purpose")
print("")

# ------------------------------------------------------------------ 1. the six
print("1. six projects, each moving a knob real code reads")
check("exactly six projects cost insight 5",
      len([b for b in project.values() if "<insightCost>5</insightCost>" in b]) == 6,
      "-- found %d" % len([b for b in project.values() if "<insightCost>5</insightCost>" in b]))
for name, (capability, prerequisite) in sorted(TIER4.items()):
    body = project.get(name)
    check("%s exists" % name, body is not None)
    if body is None:
        continue
    check("%s is tier 4 by cost and gate" % name,
          "<insightCost>5</insightCost>" in body and
          "<workRequired>18000</workRequired>" in body and
          "<minimumIntellectual>7</minimumIntellectual>" in body)
    check("%s climbs its own branch" % name,
          "<li>%s</li>" % prerequisite in body,
          "-- a tier 4 whose prerequisite is another branch would be a chokepoint")
    check("%s grants %s" % (name, capability), "<li>%s</li>" % capability in body)
    reads = [p for p, text in source.items() if 'HasCapability("%s")' % capability in text]
    check("%s is read by exactly one source file" % capability, len(reads) == 1,
          "-- read by %d" % len(reads))

# ------------------------------------------------------------------ 2. Logistics, declined
print("")
print("2. Logistics has no tier 4, and every reason it could have had one is taken")
check("no Logistics project costs insight 5",
      not any(name.startswith("RR_Logistics_") and "<insightCost>5</insightCost>" in body
              for name, body in project.items()),
      "-- a fifth Logistics rung would have to move a number, and there is not one left")
procurement = source.get(os.path.join(SRC, "Procurement", "RimroomsProcurementComponent.cs"), "")
for capability, knob in (("RR_Cap_Relays", "lead time"), ("RR_Cap_ForwardDispatch", "dispatch delay"),
                         ("RR_Cap_StandingOrders", "order capacity")):
    check("%s still claims %s" % (capability, knob),
          'HasCapability("%s")' % capability in procurement,
          "-- if a lower tier stopped claiming this, tier 4 would have a knob after all and this "
          "proof should start failing")
check("unattended delivery is still claimed by tier 3",
      'HasCapability("RR_Cap_UnattendedDelivery")' in all_source)
check("the procurement bounds left over are unreachable safety limits",
      "MaximumOpenOrders = 100" in procurement and
      "MaximumPhysicalStacksPerOrder = 4096" in procurement,
      "-- if either of these became a small number a player could hit, it would BE a knob and "
      "Logistics should get its tier 4")

# ------------------------------------------------------------------ 3. the gate line, impossible
print("")
print("3. the gate line cannot have a fifth rung")
gate = source.get(os.path.join(SRC, "Gate", "CompRimroomsGate.cs"), "")
ladder = re.search(r"portalWindowTierProjects\s*=\s*new List<string>\s*\{(.*?)\}", gate, re.S)
check("the window tier ladder is declared", ladder is not None)
if ladder is not None:
    rungs = re.findall(r'"([^"]+)"', ladder.group(1))
    check("the ladder has exactly four rungs", len(rungs) == 4, "-- found %d" % len(rungs))
    check("the top rung is the standing connection",
          rungs and rungs[-1] == "RR_GateStandingConnection")
check("the indefinite tier is four, which the ladder reaches",
      "portalIndefiniteTier = 4" in gate,
      "-- the fourth rung already stops the countdown, so there is nothing above it to unlock")
check("no gate project costs insight 5",
      not any(name.startswith("RR_Gate") and "<insightCost>5</insightCost>" in body
              for name, body in project.items()))

# ------------------------------------------------------------------ 4. the restraints
print("")
print("4. the restraints survived the tier")
frontier = source.get(os.path.join(SRC, "Portals", "NaturalFrontierService.cs"), "")
check("the per-coordinate frontier count is still not a research knob",
      re.search(r"Cap = FrontiersFor\(record\)", frontier) is not None and
      "MaximumFrontiersPerCoordinate" in frontier and
      not re.search(r"HasCapability\([^)]*\)\s*\?\s*\w*Frontiers", frontier),
      "-- 0.12.18-dev asserted this and Spatial took the ordinary-map rarity instead")
check("the ordinary-map frontier CAP is untouched too",
      "Cap = MaximumFrontiersPerOrdinaryMap" in frontier and
      not re.search(r"HasCapability\([^)]*\)\s*\?\s*\w*MaximumFrontiersPerOrdinaryMap", frontier),
      "-- only the rarity moved, which is how often, not how many")
# **THIS CLAIM WAS RETIRED AND REPLACED AT 0.12.99-dev, AND IT HAD TO BE DONE OUT LOUD.**
#
# It read: "THE NATURAL DEPTH REACH IS NOT RESEARCH-DRIVEN, WHATEVER ITS VALUE", and it was correct
# for every tier up to four. Then the owner approved **Spatial tier 6, whose entire subject is that
# number**, so the restraint stopped being true the moment that project was built.
#
# **The old claim went on passing**, which is the part worth recording. It looked for the ternary
# `HasCapability(...) ? <something>MaximumNaturalDepth`, and the capability was written as
# `? DeepFrontierNaturalDepth : MaximumNaturalDepth` -- an identifier that does not end in the name
# the pattern required. A green instrument over a restraint that no longer holds is worse than no
# instrument, and **leaving it green because it happened to pass would have been the dishonest
# move**: the build would have carried a proof asserting the opposite of what the code does.
#
# So the claim is restated to what it ALWAYS protected, which survives the change: the reach is
# **bounded**, and **one place decides it**. Tier 4 does not touch it, and the capability that moves
# it belongs to the top of the tree. The full rule, including the constants and the three read sites,
# is owned by `proof-research-tier5.py`'s sibling `proof-research-tier6.py` -- named here rather than
# copied, because two derivations of one rule is the defect this project keeps meeting.
check("the natural depth reach is not a TIER 4 knob, and is still decided in one place",
      re.search(r"MaximumNaturalDepth\s*=\s*\d+", frontier) is not None
      and "internal static int NaturalDepthReach()" in frontier
      and not re.search(r"RR_Cap_(PractisedDialling|Decompression|OpenMarket|"
                        r"StatementDiscipline|SurfaceReading|SteadyNerve)[^;]*NaturalDepth",
                        frontier),
      "-- retired and restated at 0.12.99-dev when the owner approved Spatial tier 6. "
      "proof-research-tier6.py owns the bound and the single read site now")

pressure = source.get(os.path.join(SRC, "Threats", "BackroomsPressure.cs"), "")
check("shelter never reaches zero",
      "DisciplinedShelterRate = 0.12f" in pressure,
      "-- Entities took the penalty ceiling at tier 4 rather than the shelter rate a second time")
check("the reduced penalty ceiling is well above the minimum",
      "SteadyNervePenalty = 6" in pressure and "MinPenalty = 1" in pressure,
      "-- a branch can learn to carry the place, not to stop feeling it")
check("the interview floor lowers but never to zero",
      "PractisedInterviewerSocial = 2" in
      source.get(os.path.join(SRC, "Company", "EvidenceInterview.cs"), ""),
      "-- same rule: cheapen a thing without abolishing it")
check("practised dialling discounts the requirement, not the floor",
      "PractisedDiallingFactor = 0.8f" in
      source.get(os.path.join(SRC, "Gate", "GateSpinUp.cs"), ""),
      "-- the owner made 'costs more to run' a condition of the larger gate sizes")
check("the odd exchange premium is untouched",
      "OddExchangeRate = 1.5f" in
      source.get(os.path.join(SRC, "Company", "ValuablesExchange.cs"), ""),
      "-- Commerce learns to stop being fleeced on scrap, not to make the Backrooms pay better")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: six real knobs, two deliberate absences, and every restraint intact")
