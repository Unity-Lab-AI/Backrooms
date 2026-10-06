# -*- coding: utf-8 -*-
"""Assert that the eligibility filter can refuse, and that no authored route is unfireable.

The property this exists for
----------------------------
The owner's decision, verbatim: ***"Both - filter picks the family, card never shrinks."*** Two
rules at two levels, and this proves both halves stay where they belong:

  * **Eligibility** decides which generated family is offered: two routes of two different kinds
    that the branch can actually take.
  * **The card** shows the full authored floor, unfiltered. `RequestRoutes.Available` must not
    learn about capability, ever.

And one thing that has bitten this project four times already:

  * **A filter whose clauses cannot refuse is a hollow knob.** Invariant 136 deleted four research
    projects and three tier-2 constants for exactly this. If `CanTakeRoute` ever degenerates to
    "yes" for a kind, the filter still runs, still looks like a feature, and decides nothing.
  * **A route naming something that does not exist can never fire.** Invariant 49: before
    designing a rule, check it can fire. A `logKind` typo makes `TryLogKind` return false, the
    measurement zero, and the route permanently unsatisfiable -- with no error anywhere, because
    the XML loader validates none of it and the route still counts toward the two-kinds rule.

Run from the repository root.
"""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//") and not line.lstrip().startswith("///"))


def read(*parts):
    return strip_comments(io.open(os.path.join(*parts), encoding="utf-8-sig").read())


def body_of(text, signature):
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace:index + 1]
    return ""


generation = read(SRC, "Company", "RequestGeneration.cs")
line = read(SRC, "Company", "RequestLine.cs")
routes = read(SRC, "Company", "RequestRoutes.cs")

# ---------------------------------------------------------------- 1. the filter has teeth

take = body_of(generation, "internal bool CanTakeRoute(")
check("the eligibility filter was found", bool(take))

# Keyed off the condition each arm RETURNS, never off the enum name appearing nearby.
arms = {}
for kind in ("Deliver", "Substitute", "Purchase", "Document", "Testify", "Research", "Redirect"):
    arms[kind] = take.find("case SuccessRouteKind.%s:" % kind)
check("every route kind is considered by the filter",
      all(position >= 0 for position in arms.values()),
      "-- a kind falling to default would make every family holding it ineligible for ever")


def arm_expression(kind):
    start = arms.get(kind, -1)
    if start < 0:
        return ""
    at_return = take.find("return", start)
    stop = take.find(";", at_return)
    return take[at_return:stop] if at_return >= 0 and stop >= 0 else ""


# The load-bearing claim: no arm is unconditionally true.
for kind in ("Deliver", "Purchase", "Document", "Testify", "Research", "Redirect"):
    expression = arm_expression(kind)
    trivially_true = expression.strip() in ("return true", "return true ")
    check("the %s clause can refuse" % kind,
          bool(expression) and not trivially_true,
          "-- a clause that is always true makes the whole filter a hollow knob (invariant 136)")

check("Purchase refuses before the corporation is in contact",
      "corporationContact" in arm_expression("Purchase"),
      "-- procurement does not exist before contact, so the route would be offered and undoable")
check("Document refuses when the branch has visited nowhere",
      "coordinates.Count" in arm_expression("Document"),
      "-- you cannot write a log about a place nobody has been")
check("Testify refuses when nobody living saw it",
      "LivingWitnessCount" in arm_expression("Testify"),
      "-- the route would be offered with no possible witness")

reachable = body_of(generation, "private bool ProjectReachable(")
check("a finished project is not reachable",
      "ProjectCompleted(projectDefName)" in reachable,
      "-- a Research route against finished work is satisfied on sight: a payout button")
check("qualification is asked of the one existing gate",
      "ProjectQualificationFailureKey(definition)" in reachable,
      "-- a second copy of the log-tier rule would eventually disagree with the research screen")

check("the catalogue is one source of truth, shared not copied",
      "internal static bool CatalogueCarries" in routes
      and "RequestRoutes.CatalogueCarries" in generation
      and "private static bool CatalogueCarries" not in generation,
      "-- two ideas of what is orderable would drift apart")

# ---------------------------------------------------------------- 2. two routes, two kinds

eligible = body_of(generation, "internal bool FamilyEligible(")
check("eligibility demands two takeable routes",
      "takeable >= 2" in eligible,
      "-- one way through breaks the owner absolute \"never offer only one path\"")
check("eligibility demands two different kinds",
      "kinds.Count >= 2" in eligible,
      "-- two routes of one kind is one route wearing two hats")
check("eligibility never applies to a tutorial request",
      "definition.tutorial" in eligible,
      "-- a fresh branch could be offered nothing at all, for ever")

# ---------------------------------------------------------------- 3. the card never shrinks

available = body_of(routes, "public static List<RimroomsSuccessRoute> Available(")
check("the card does not consult the eligibility filter",
      "CanTakeRoute" not in available and "FamilyEligible" not in available,
      "-- the card would shrink when the branch is poor, against the owner's decision")
check("the authored floor is still taken whole",
      "definition.successRoutes" in available,
      "-- the floor is what makes the two-route absolute unbreakable")

# ---------------------------------------------------------------- 4. generation, and its refusals

offer = body_of(generation, "private void OfferNextGeneratedRequest(")
check("the generated offer routine was found", bool(offer))
check("nothing is generated before the hinge",
      "PastTheHinge" in offer,
      "-- generated work would appear during the tutorial and compete with it")
check("nothing is generated before contact",
      "corporationContact" in offer,
      "-- a branch nobody has heard of would get client work")
# **RESTATED AT 0.12.99-dev, AND THE OLD CLAIM WAS ENFORCING A DEFECT.** It read:
#
#     check("only one request is ever open", "OpenRequest != null" in offer,
#           "-- two open requests means two payouts running at once")
#
# `OpenRequest` is *offered **or** accepted*, so that guard stopped the company offering anything
# else the moment a job was accepted: **a branch could hold exactly one job, ever.** The owner's
# direction is *"with ability to accept more than one quests at a time"*, and two shipped features
# depended on it -- the paperwork ledger that lists *every accepted quest*, and the parallel records
# desks. Both were unreachable in play rather than merely unused.
#
# **The worry behind the old wording was two PAYOUTS, and that was never what it was testing.** A
# payout is settled per request when its routes are satisfied; two accepted jobs are two jobs, which
# is the thing being asked for. What must stay bounded is **the question**: the company asks for one
# answer at a time, so there is exactly one offer awaiting one.
check("only one OFFER is ever awaiting an answer",
      "OfferedRequest != null" in offer,
      "-- the company may ask one question at a time; how many jobs the branch is carrying is the "
      "player's business")
check("AND THE GUARD IS NOT THE OLD OPEN-OR-ACCEPTED TEST",
      "OpenRequest != null" not in offer,
      "-- that reading is what limited a branch to one job at a time, and it would come back "
      "looking like a tidy-up")

# There is no clock and none is coming back. Chart 1.1.
for token in ("TicksGame %", "nextRequestTick", "interval", "Interval", "cooldown", "Cooldown"):
    check("generation has no clock: '%s'" % token,
          token not in offer,
          "-- two offer clocks were retired in 0.11.0-dev; the only clock is the gate")

check("the candidate list is sorted ordinally before anything is rolled",
      "StringComparer.Ordinal" in offer and "CampaignSeed.Derive" in offer,
      "-- invariant 26: a list in def order rolls differently on different mod lists")
# **A PLANT PROVED THIS CLAIM TOO WEAK.** It tested only that `TimesAsked` appears somewhere in the
# body, and the body names it twice -- once to find the fewest and once to filter on it. A plant that
# gutted the first (`int asked = 0;`) left the second standing and the claim passed, while variety
# had become *whichever family is first in the list*. So both halves of the derivation are asserted:
# the scan that finds the minimum, and the filter that keeps only families at it.
check("variety comes from least-asked-first, not from a timer",
      "int asked = TimesAsked(" in offer
      and "TimesAsked(definition.defName) == fewest" in offer,
      "-- the company would repeat whichever family is cheapest, or whichever happens to be first")

# ---------------------------------------------------------------- 5. progress, not absolute state

offer_any = body_of(line, "private RequestRecord OfferRequest(")
check("a generated request records where its routes started",
      "routeBaselines.Add" in offer_any and "MeasureRoute(route)" in offer_any,
      "-- absolute state is permanently true once true, so a repeatable request would pay out "
      "the instant it was accepted")
check("a tutorial request takes no baseline",
      "if (!definition.tutorial)" in offer_any,
      "-- a branch that already holds a battery has already learned request 1's lesson")

satisfied = body_of(line, "private bool RouteSatisfied(")
check("satisfaction is measured from the baseline",
      "baseline + required" in satisfied,
      "-- the baseline would be recorded and then ignored, which is worse than not recording it")

required = body_of(line, "private static int RequiredProgress(")
check("Research and Redirect ask for one, not for count",
      "SuccessRouteKind.Research" in required and "return 1;" in required,
      "-- a def could ask for one project to be completed three times")

valid = body_of(line, "internal bool RequestRecordsValid(")
check("a tutorial request can appear only once in a save",
      "definition.tutorial" in valid,
      "-- a fixed request offered twice would be paid twice")
# Restated for the same reason as the offer guard above: the bound is on OFFERS, and counting
# `record.Open` here made a save invalid the moment a branch held two jobs -- the save-level half of
# the same restriction. Both halves are asserted, because the bound is worthless if the thing being
# counted quietly goes back to meaning offered-or-accepted.
check("a save may hold at most one OFFERED request",
      "open <= 1" in valid,
      "-- two offers is two questions at once, and means an offer guard was bypassed")
check("and the counter counts offers rather than obligations",
      "if (record.status == RequestStatus.Offered) { open++; }" in valid
      and "if (record.Open) { open++; }" not in valid,
      "-- counting accepted jobs here invalidates the save of any branch carrying two, which is "
      "what the owner asked to be possible")

# ---------------------------------------------------------------- 6. every authored route can fire

tree = ET.parse(os.path.join(MOD, "Defs", "RimroomsRequestDefs", "RR_Requests.xml"))
defs = tree.getroot().findall("RimroomsAsyncIndustries.Company.RimroomsRequestDef")
check("the request defs parsed", len(defs) >= 12, "-- found %d" % len(defs))

catalogue = set()
catalogue_dir = os.path.join(MOD, "Defs", "RimroomsProcurementCatalogDefs")
for name in os.listdir(catalogue_dir):
    if not name.endswith(".xml"):
        continue
    for node in ET.parse(os.path.join(catalogue_dir, name)).getroot().iter("thingDefName"):
        catalogue.add((node.text or "").strip())

projects = set()
for node in ET.parse(os.path.join(MOD, "Defs", "RimroomsProjectDefs",
                                  "RR_CompanyProjects.xml")).getroot().iter("defName"):
    projects.add((node.text or "").strip())

VALID_LOGS = {"route", "distortion", "entity"}
request_names = set((node.findtext("defName") or "").strip() for node in defs)

bad_logs, bad_projects, dead_purchases, thin = [], [], [], []
generated = 0
for node in defs:
    name = (node.findtext("defName") or "").strip()
    is_tutorial = (node.findtext("tutorial") or "false").strip().lower() == "true"
    if not is_tutorial:
        generated += 1
    kinds = set()
    for route in node.findall("successRoutes/li"):
        kind = (route.findtext("kind") or "").strip()
        kinds.add(kind)
        log_kind = route.findtext("logKind")
        if kind in ("Document", "Testify"):
            if (log_kind or "").strip() not in VALID_LOGS:
                bad_logs.append("%s/%s=%r" % (name, kind, log_kind))
        if kind == "Research":
            project = (route.findtext("projectDefName") or "").strip()
            if project not in projects:
                bad_projects.append("%s->%s" % (name, project))
        if kind == "Redirect":
            target = (route.findtext("redirectTo") or "").strip()
            if target not in projects and target not in request_names:
                bad_projects.append("%s redirect->%s" % (name, target))
        # A Purchase route the catalogue does not carry can never be taken, so it can never
        # count toward eligibility either -- a dead line on every card that offers it.
        if kind == "Purchase" and not is_tutorial:
            thing = (route.findtext("thingDefName") or "").strip()
            if thing not in catalogue:
                dead_purchases.append("%s->%s" % (name, thing))
    if len(kinds) < 2:
        thin.append(name)

check("every Document and Testify route names a real log kind",
      not bad_logs,
      "-- %s: TryLogKind returns false, the measurement is zero, and the route can NEVER fire"
      % ", ".join(bad_logs))
check("every Research and Redirect route names a def that exists",
      not bad_projects,
      "-- %s" % ", ".join(bad_projects))
check("every generated Purchase route names something the catalogue carries",
      not dead_purchases,
      "-- %s: not orderable, so CanTakeRoute refuses it for ever" % ", ".join(dead_purchases))
check("every request offers two different kinds",
      not thin,
      "-- %s" % ", ".join(thin))
# Per-arc coverage. The chart names a fixed list of things each arc is about, and a generated
# family exists for each. Counting per arc rather than in total is deliberate: a total would be
# satisfied by eighteen copies of arc 4, and the point is that every arc has somewhere to put work.
EXPECTED_PER_ARC = {4: 5, 5: 6, 6: 3, 7: 2, 8: 2}
per_arc = {}
for node in defs:
    if (node.findtext("tutorial") or "false").strip().lower() == "true":
        continue
    arc = int((node.findtext("arc") or "0").strip() or 0)
    per_arc[arc] = per_arc.get(arc, 0) + 1

for arc in sorted(EXPECTED_PER_ARC):
    want = EXPECTED_PER_ARC[arc]
    have = per_arc.get(arc, 0)
    check("arc %d has its %d generated families" % (arc, want),
          have >= want,
          "-- found %d; the chart names %d things this arc is about and each needs somewhere "
          "to be asked for" % (have, want))

check("no generated family sits outside arcs 4 to 8",
      not [arc for arc in per_arc if arc < 4 or arc > 8],
      "-- arcs 1 to 3 are the tutorial line and generate nothing: %s"
      % sorted(arc for arc in per_arc if arc < 4 or arc > 8))

print("")
print("generated families: %d   catalogue things: %d   projects: %d"
      % (generated, len(catalogue), len(projects)))
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the filter can refuse, the card never shrinks, and every route can fire")
