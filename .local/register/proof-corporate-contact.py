# -*- coding: utf-8 -*-
"""Assert a branch can earn corporation contact, and that earning it starts the Async line.

The property this exists for
---------------------------
`EstablishCorporationContact()` existed, was one-way, recorded its event, had a translated string
waiting for it -- and **had no caller anywhere in the source.** Meanwhile `corporationContact`
gates:

    RequestLine.cs           the entire tutorial line
    RequestGeneration.cs     generated requests, and the Purchase route
    FacilityRelief.cs        the clean-up team that comes for a stranded crew

and both the Store and the Solo/Group starts declare `beginsInCorporationContact false`.

**So two of the three shipped starts had no campaign at all, permanently** -- no tutorial, no
requests, no catalogue, no rescue -- while `docs/CAMPAIGN_CHART.md` said of each that *"reaching
contact is the achievement"* and `RR_Starts.xml` said in its own comment *"Reaching contact is the
achievement here, not the starting condition."*

The owner named the mechanism while this was being built, verbatim:

    "once they "contact the cvompany in comms" they can start async quest line"

Four things have to stay true:

  * **THE CALL HAS A CALLER.** This is the whole point. If `EstablishCorporationContact` ever goes
    back to being unreachable, two starts are dead again and nothing else will say so.

  * **IT STARTS THE EXISTING ASYNC LINE, NOT A NEW ONE.** Nothing was authored for the line: the
    tutorial offer routine already refuses until contact, so the line begins on its own. A second
    parallel line would be two voices teaching the same systems.

  * **IT IS EARNED.** The chart calls it the achievement, so the call asks for the whole first
    loop: a powered console somebody can work, a coordinate the branch has been into, and an
    **analysed** record. A free button on a day-one console would make the chart's word wrong.

  * **EVERY CLAUSE REFUSES SEPARATELY** and the reason shows on a disabled button rather than the
    button vanishing. Invariant 28: a player must be able to see what the call is waiting for.

Run from the repository root.
"""
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


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unbalanced body for %r" % signature)


source = {}
for root, _, files in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in files:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))

contact = source[os.path.join(SRC, "Company", "CorporateContact.cs")]
gizmo = source[os.path.join(SRC, "Company", "CorporateContactGizmo.cs")]
console = source[os.path.join(SRC, "Gate", "CompRimroomsGateConsole.cs")]
line = source[os.path.join(SRC, "Company", "RequestLine.cs")]
starts = strip_xml_comments(read(os.path.join(MOD, "Defs", "RimroomsStartDefs", "RR_Starts.xml")))
keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Requests.xml"))

print("")
print("proof: contact can be earned on a comms console, and earning it opens the Async line")
print("")

# ------------------------------------------------------------------ 1. the call has a caller
print("1. the call has a caller")
callers = [path for path, text in source.items()
           if "EstablishCorporationContact()" in text and
           not path.endswith("RimroomsCampaignComponent.cs")]
check("EstablishCorporationContact is called from real code", len(callers) >= 1,
      "-- it had NO caller at all before 0.12.30-dev, which left two starts with no campaign")
check("the caller is the corporate call",
      any(path.endswith("CorporateContact.cs") for path in callers))
check("the gizmo reaches the call",
      "campaign.CallTheCorporation(console)" in gizmo)
check("the gizmo is reachable from a spawned console",
      "CorporateContactGizmo.For(parent)" in console,
      "-- a gizmo provider nothing yields is the same defect one layer up")

# ------------------------------------------------------------------ 2. it starts the existing line
print("")
print("2. it starts the EXISTING Async line")
offer = body_of(line, "private void OfferNextTutorialRequest(")
check("the tutorial offer still gates on contact",
      "if (!corporationContact) { return; }" in offer,
      "-- this is what makes the call start the line, with nothing authored for it")
check("no second tutorial line was introduced",
      "TutorialLine()" in line and "SoloTutorialLine" not in line and
      "IndependentLine" not in line,
      "-- two lines teaching the same systems would be two voices")
check("contact is still one-way",
      "corporationContact = false" not in
      source[os.path.join(SRC, "Company", "RimroomsCampaignComponent.cs")].replace(
          "private bool corporationContact;", ""),
      "-- the method's own note says there is deliberately no way to take it back")

# ------------------------------------------------------------------ 3. it is earned
print("")
print("3. it is earned, not free")
blocker = body_of(contact, "public string CorporationCallBlocker(")
check("a powered console is required",
      "RR_Contact_Unpowered" in blocker and "CompPowerTrader" in blocker)
check("the console must be a comms console the branch owns",
      "Building_CommsConsole" in blocker and "OwnsMap(console.Map)" in blocker)
check("somebody employed must be able to speak",
      "RR_Contact_NoOperator" in blocker and
      "PawnCapacityDefOf.Talking" in body_of(contact, "private bool AnyEmployedOperator("))
check("a coordinate the branch has been into is required",
      "RR_Contact_NoCoordinate" in blocker and "coordinates.Count == 0" in blocker)
check("an ANALYSED record is required",
      "RR_Contact_NoFinding" in blocker and
      "record.analyzedTick >= 0" in body_of(contact, "private bool AnyAnalysedRecord("),
      "-- the whole first loop: found the place, went in with a book, came home, read it")
check("the analysed test does not depend on the report snapshot",
      "analysisReport" not in body_of(contact, "private bool AnyAnalysedRecord("),
      "-- a legacy save can carry a completed analysis without one")

# ------------------------------------------------------------------ 4. refusals are visible
print("")
print("4. every clause refuses, and the reason is visible")
for key in ("RR_Contact_Inactive", "RR_Contact_AlreadyInContact", "RR_Contact_NoConsole",
            "RR_Contact_NotOurs", "RR_Contact_Unpowered", "RR_Contact_NoOperator",
            "RR_Contact_NoCoordinate", "RR_Contact_NoFinding"):
    check("%s is a refusal" % key, '"%s"' % key in contact)
    check("%s is translated" % key, "<%s>" % key in keys)
check("the gizmo disables with the reason rather than hiding",
      "call.Disable(blocker.Translate())" in gizmo,
      "-- a vanished button tells a player nothing about what the call is waiting for")
check("the action re-checks every condition rather than trusting the button",
      "CorporationCallBlocker(console)" in body_of(contact, "public CompanyActionResult CallTheCorporation("),
      "-- a button can be clicked on the tick the generator goes off")
check("the gizmo is not offered to a branch already in contact",
      "campaign.CorporationContact" in gizmo and "yield break" in gizmo)
check("the gizmo refuses a machining table, which shares the component",
      "console is Building_CommsConsole" in gizmo,
      "-- nobody telephones anybody from a machining table")
check("success is announced to the player",
      "RR_Contact_Established" in contact and "<RR_Contact_Established>" in keys)

# ------------------------------------------------------------------ 5. the starts it unblocks
print("")
print("5. the two starts this exists for still open out of contact")
check("two starts declare beginsInCorporationContact false",
      starts.count("<beginsInCorporationContact>false</beginsInCorporationContact>") == 2,
      "-- if either flipped to true the achievement would have been given away instead of earned")
check("one start opens in contact",
      starts.count("<beginsInCorporationContact>true</beginsInCorporationContact>") == 1)
check("the solo hint still points at a comms console",
      "RR_Hint_Comms" in source[os.path.join(SRC, "Company", "SoloGroupHints.cs")],
      "-- the hint told a player to build one and there was nothing to do with it until now")

# =============================================================== the book, and the quest
# Owner, 2026-10-01: *"make sure the other scenerios properly get the book in a drop when they
# need it and start the quest to go through their built gate"*.
_delivery = io.open(os.path.join(SRC, "Company", "RecordBookDelivery.cs"),
                    encoding="utf-8-sig").read()
_services = io.open(os.path.join(SRC, "Company", "CampaignServices.cs"),
                    encoding="utf-8-sig").read()
_line = io.open(os.path.join(SRC, "Company", "RequestLine.cs"), encoding="utf-8-sig").read()
_reqdef = io.open(os.path.join(SRC, "Company", "RimroomsRequestDef.cs"),
                  encoding="utf-8-sig").read() if os.path.isfile(
                      os.path.join(SRC, "Company", "RimroomsRequestDef.cs")) else ""
_starts = io.open(os.path.join(
    REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs", "RimroomsStartDefs",
    "RR_Starts.xml"), encoding="utf-8-sig").read()

check("THE CORPORATION SENDS A RECORD BOOK TO A BRANCH THAT HAS NONE",
      "internal void TickRecordBookDelivery()" in _delivery
      and "TickRecordBookDelivery();" in _services,
      "-- **DEFINED AND CALLED.** Only the laboratory start ships a book, and only since today. "
      "The Store spawns 27 fixtures and no book; the solo start spawns nothing at all, so a "
      "player who builds a gate from nothing hits RR_Exp_MissingRecordBook with no idea what a "
      "record book is")

check("and it waits for a gate the player actually finished",
      "if (!HasFinishedGate()) { return; }" in _delivery
      and "gate.IsDesignated && gate.Calibrated" in _delivery,
      "-- calibrated, not merely designated. Before that a book is a mystery item with nothing "
      "to use it on")

check("and it refuses while a book exists ANYWHERE the branch can reach",
      "if (AnyRecordBookHeld(book)) { return; }" in _delivery
      and "map.listerThings.ThingsOfDef(book)" in _delivery
      and "pawn.inventory.innerContainer.Contains(book)" in _delivery,
      "-- a floor, a shelf, or somebody's pack on either side of an open connection. **This is "
      "what stops it being a tap**: it can fire again if the book is lost, and never while one "
      "still exists")

check("and it asks the same question a dispatch asks, never by name",
      "Expedition.ExpeditionCargo.RecordBookDef" in _delivery
      and '"TextBook"' not in _delivery,
      "-- asking by def name here and by comp there is how a branch ends up holding a book the "
      "dispatch refuses")

check("and it sends a spare",
      "private const int RecordBookDeliveryCount = 2;" in _delivery,
      "-- a branch that loses its only book is blocked until it makes another")

check("and nothing is recorded or announced when nothing was made",
      "if (payload.Count == 0) { return; }" in _delivery,
      "-- a letter announcing an empty crate is worse than silence")

check("THE QUEST LINE HAS NO SCENARIO GATE, SO IT REACHES EVERY START",
      "scenarioId" not in _line and "async_industries" not in _line
      and "async_industries" not in _reqdef,
      "-- *\"start the quest to go through their built gate\"*. It already did, and **a "
      "negative claim is the only kind that keeps it that way**: a positive one listing three "
      "scenarios would pass while a fourth was quietly excluded")

# Read out of the request defs, in tutorial order, so the claim is about what the line
# actually offers first rather than about two names existing somewhere.
_reqxml = io.open(os.path.join(
    REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs", "RimroomsRequestDefs",
    "RR_Requests.xml"), encoding="utf-8-sig").read()
_tutorial = re.findall(
    r"<defName>(RR_Request_[A-Za-z]+)</defName>(?:(?!</RimroomsAsync).)*?"
    r"<tutorial>true</tutorial>(?:(?!</RimroomsAsync).)*?<tutorialOrder>(\d+)</tutorialOrder>",
    _reqxml, re.S)
_ordered = [name for name, _order in sorted(_tutorial, key=lambda pair: int(pair[1]))]

check("AND THE FIRST TWO REQUESTS ARE BUILD-A-GATE-AND-GO-THROUGH-IT",
      len(_ordered) >= 2
      and _ordered[0] == "RR_Request_PowerTheGate"
      and _ordered[1] == "RR_Request_AssembleAndCalibrate",
      "-- read in tutorial order, so this is about what the line OFFERS first rather than two "
      "names existing somewhere. Found: %s" % ", ".join(_ordered[:3]))

check("and the other two starts begin outside contact, which is the owner's own rule",
      _starts.count("<beginsInCorporationContact>false</beginsInCorporationContact>") == 2
      and _starts.count("<beginsInCorporationContact>true</beginsInCorporationContact>") == 1,
      "-- *\"clena up tema is only once u are in communication and working with the "
      "corporation\"*. They call the corporation, and the line opens. The book delivery is "
      "gated on the same flag for the same reason")


print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: contact is earned on a console, and earning it opens the line that existed")
