# -*- coding: utf-8 -*-
"""Assert that the mission line actually reaches a player, and that no two routes are one check.

The property this exists for
----------------------------
`RimroomsRequestDef`, `RequestRoutes` and seven authored requests -- the whole tutorial line and
the hinge -- shipped in 0.11.1-dev and 0.11.2-dev as `CAMPAIGN_CHART.md` §7 steps 4 and 5, and
the build order recorded both as done. **Nothing read any of it.** `ConfigErrors` validated the
defs at load, two tools checked them, a proof proved their shape, and no player could ever see a
request. That is the same defect as the five `PawnKindDef`s found authored and read by nothing,
at feature scale.

So the first claim here is the one that would have caught it: **the request surface has readers.**

Four more properties, each of which decays silently if nothing watches it:

  * **No two route kinds are the same question.** `RimroomsRequestDef.ConfigErrors` already
    forbids a request whose routes are all one kind -- *"one route wearing two hats"*. That rule
    is satisfied by the def. If the runtime check for two different kinds collapsed to the same
    expression, the def rule would be passing on text alone while the game treated the two routes
    as one. The pair most at risk is Document and Testify, which both name a log kind.
  * **The tutorial line is never capability-filtered.** The owner's eligibility answer -- *"filter
    picks the family, card never shrinks"* -- is about **generated** requests. Applied to the
    tutorial it would let a fresh branch be offered nothing, for ever.
  * **A request cannot complete for free, and cannot complete unaccepted.** Payment posts before
    the status flips, and only an Accepted request completes.
  * **There is no clock.** Chart §1.1. The shape has no expiry field; no wording here may imply
    one either.

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

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def strip_comments(text):
    """Comments must never satisfy a claim. Cost four wrong assertions earlier this session."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//") and not line.lstrip().startswith("///"))


def read(*parts):
    return strip_comments(io.open(os.path.join(*parts), encoding="utf-8-sig").read())


def body_of(text, signature):
    """The brace-balanced body of one method, so a claim cannot be satisfied by a neighbour."""
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


line = read(SRC, "Company", "RequestLine.cs")
pane = read(SRC, "UI", "OperationsRequests.cs")
tab = read(SRC, "UI", "MainTabWindow_Operations.cs")
services = read(SRC, "Company", "CampaignServices.cs")
component = read(SRC, "Company", "RimroomsCampaignComponent.cs")
requests_xml = io.open(os.path.join(MOD, "Defs", "RimroomsRequestDefs", "RR_Requests.xml"),
                       encoding="utf-8-sig").read()

# ---------------------------------------------------------------- 1. the surface has readers

# The claim that would have caught the original defect. Keyed off files OTHER than the two that
# define the surface, because a type referring to itself proves nothing.
DEFINING = {os.path.join(SRC, "Company", "RequestDefs.cs"),
            os.path.join(SRC, "Company", "RequestRoutes.cs")}
readers = []
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    if os.path.abspath(path) in {os.path.abspath(p) for p in DEFINING}:
        continue
    text = strip_comments(io.open(path, encoding="utf-8-sig").read())
    if "RimroomsRequestDef" in text or "RequestRoutes." in text:
        readers.append(os.path.basename(path))

print("request surface readers: %s" % (", ".join(sorted(readers)) or "NONE"))
check("the request def is read by source outside its own definition",
      len(readers) >= 2,
      "-- the whole tutorial line and the hinge would be content nothing presents")
check("a player-facing pane draws requests",
      "DrawRequests(listing, campaign)" in tab and "RequestRoutes.Available" in pane,
      "-- the offer would exist and never reach a screen")
check("the line is ticked",
      "TickRequestLine()" in services,
      "-- offers would never appear and completions would never be noticed")
check("the records are saved",
      "ExposeRequests();" in component,
      "-- a reload would forget every request this branch had taken on")

# ---------------------------------------------------------------- 2. no two routes are one check

# The per-kind switch moved from RouteSatisfied into MeasureRoute at 0.12.12-dev, when
# satisfaction became progress-against-a-baseline instead of absolute state. The properties
# below are unchanged; only their address is. This proof failing on the refactor is the proof
# working -- a claim that survives its subject moving is a claim keyed off nothing.
satisfied = body_of(line, "private int MeasureRoute(")
check("the per-kind measurement switch was found", bool(satisfied))

# Each arm must name a DIFFERENT expression. Keyed off the call each arm makes, not off the
# presence of the enum name, because the enum name appearing proves only that it was mentioned.
arms = {}
for kind in ("Deliver", "Substitute", "Purchase", "Document", "Testify", "Research", "Redirect"):
    marker = "case SuccessRouteKind.%s:" % kind
    position = satisfied.find(marker)
    arms[kind] = position
check("every route kind has an arm in the switch",
      all(position >= 0 for position in arms.values()),
      "-- a kind falling to default is a route that can never be satisfied")


def arm_expression(kind):
    """The text from one case label up to its return, so arms cannot borrow each other's."""
    start = arms.get(kind, -1)
    if start < 0:
        return ""
    end = satisfied.find("return", start)
    stop = satisfied.find(";", end)
    return satisfied[end:stop] if end >= 0 and stop >= 0 else ""


document_arm = arm_expression("Document")
testify_arm = arm_expression("Testify")
research_arm = arm_expression("Research")
redirect_arm = arm_expression("Redirect")

check("Document and Testify are not the same check",
      bool(document_arm) and bool(testify_arm) and document_arm.strip() != testify_arm.strip(),
      "-- request 5's only two routes would be one route wearing two hats")
check("Document measures the analysed records",
      "CompletedLogsOfKind" in document_arm,
      "-- the paperwork route must read a completed log")
check("Testify measures living witnesses",
      "LivingWitnessCount" in testify_arm,
      "-- the testimony route must read a person, not a book")
check("Research and Redirect are not the same check",
      bool(research_arm) and bool(redirect_arm) and research_arm.strip() != redirect_arm.strip(),
      "-- the hinge offers both against the same project and would have one answer")

completed_body = body_of(line, "private bool ProjectCompleted(")
started_body = body_of(line, "private bool ProjectStarted(")
check("finishing a project and committing to one are different tests",
      bool(completed_body) and bool(started_body)
      and "record.completed" in completed_body
      and ("insightCommitted" in started_body or "workDone" in started_body)
      and "insightCommitted" not in completed_body,
      "-- declaring a direction would require arriving at it")

witness_body = body_of(line, "private int LivingWitnessCount(")
check("testimony counts distinct people",
      "HashSet<string>" in witness_body,
      "-- one witness counted twice would satisfy a route promising two accounts")
check("testimony requires the witness to be alive and employed",
      "witness.Dead" in witness_body and "IsEmployedPawn(witness)" in witness_body,
      "-- a dead crew member could testify, which is the whole distinction from Document")

# The def and the runtime must agree about what "two accounts" means.
check("request 5 asks for two witnesses, matching its own label",
      re.search(r"RR_Route_TwoAccountsLabel.*?<count>2</count>", requests_xml, re.S) is not None,
      "-- the card would promise two accounts and accept one")

# ---------------------------------------------------------------- 3. what may be counted as home

owned = body_of(line, "private int OwnedThingCount(")
check("a delivered thing is counted only at a branch place",
      "CanReceiveDeliveryAt(map)" in owned,
      "-- a thing anywhere in the world would satisfy a delivery")
check("a coordinate never counts as home",
      "OwnsMap" not in owned,
      "-- OwnsMap admits this branch's coordinates, so a book still lying in the Backrooms "
      "would count as brought back")

# ---------------------------------------------------------------- 4. offering, and its refusals

offer = body_of(line, "private void OfferNextTutorialRequest(")
check("the offer routine was found", bool(offer))
check("no request line before contact",
      "if (!corporationContact) { return; }" in offer,
      "-- two of the three starts open in silence and the silence is the design")
check("one request at a time",
      "OpenRequest != null" in offer,
      "-- a tutorial teaching one system per step would become a list of chores")
check("the tutorial line is NOT capability-filtered",
      "Eligib" not in offer and "CanTake" not in offer,
      "-- a fresh branch could be offered nothing at all, for ever")

prerequisites = body_of(line, "private bool PrerequisitesResolved(")
check("a cancelled request still unblocks what came after it",
      "Resolved" in prerequisites and "RequestStatus.Completed" not in prerequisites,
      "-- turning one request down would strand the rest of the line behind it")

# ---------------------------------------------------------------- 5. completion cannot be free

complete = body_of(line, "private void CompleteRequest(")
check("the completion routine was found", bool(complete))
payment_at = complete.find("PostTransaction")
status_at = complete.find("record.status = RequestStatus.Completed")
check("payment is posted before the status flips",
      payment_at >= 0 and status_at >= 0 and payment_at < status_at,
      "-- a refused payment would complete the request for nothing")
check("a refused payment leaves the request alone",
      "if (!paid.Success) { return; }" in complete,
      "-- the request would complete unpaid and never retry")

sweep = body_of(line, "private void CompleteSatisfiedRequests(")
check("only an accepted request completes",
      "record.status != RequestStatus.Accepted" in sweep,
      "-- a request nobody took on would pay out")

bonus_body = body_of(line, "private bool EverybodyCameBack(")
check("the bonus has a real condition",
      bool(bonus_body) and "staffAtAcceptance" in bonus_body,
      "-- bonusUsd would be a number on a card that always pays, which is invariant 136")
check("the bonus is measured against the snapshot, not the live roster",
      "record.staffAtAcceptance" in bonus_body,
      "-- firing the casualty would earn the bonus")
check("the bonus is read by completion",
      "EverybodyCameBack(record)" in complete,
      "-- the condition would exist and decide nothing")

# ---------------------------------------------------------------- 6. there is no clock

for token in ("expire", "Expire", "deadline", "Deadline", "timeout", "TimeOut"):
    check("the request line never mentions '%s'" % token,
          token not in line and token not in pane,
          "-- chart §1.1: the only clock is the gate")

keyed_raw = io.open(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Requests.xml"),
                    encoding="utf-8-sig").read()
# XML comments are stripped because the claim is about strings a PLAYER READS, and a comment is
# not one. This is narrowing the population, not softening the rule -- invariant 130, where a word
# search matched a doc comment and reported a breach that did not exist. The narrowing is proved
# not to blind the rule immediately below.
keyed = re.sub(r"<!--.*?-->", "", keyed_raw, flags=re.S)
check("stripping comments did not empty the keyed file",
      len(keyed) > len(keyed_raw) * 0.5 and "RR_Requests_Heading" in keyed,
      "-- a narrowed population that removed the strings would pass every rule below vacuously")
# The same tokens, against the words a player actually reads. This is the rule the key
# `RR_Requests_NoDeadline` fell foul of on the first run -- its TEXT denied a clock, but the rule
# cannot read intent, and softening a rule so my own wording passes is how a checker stops
# working. The key was renamed instead.
for token in ("expire", "Expire", "deadline", "Deadline", "time limit", "run out of time"):
    check("no request string a player reads mentions '%s'" % token,
          token not in keyed,
          "-- the wording would imply a clock the shape cannot even express")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the mission line reaches a player, and no two routes are one check")
