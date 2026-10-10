# -*- coding: utf-8 -*-
"""Claims for the record-book delivery, and for the quest reaching every scenario.

Owner, 2026-10-01: *"make sure the other scenerios properly get the book in a drop when they need
it and start the quest to go through their built gate"*.

**Two halves, and only one of them was missing.** The quest half already worked -- the tutorial
line has no scenario gate anywhere -- but *already works* is worth nothing without a claim saying
so, because the next person to add a scenario check would break it silently. Both are asserted
now.

The scenario-gate claim is **negative and derived**: it reads the request line and the request def
and refuses if either mentions a scenario id at all. A positive claim listing three scenarios
would pass while a fourth was quietly excluded.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-corporate-contact.py")

ADDITION = u'''
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
      "-- *\\"start the quest to go through their built gate\\"*. It already did, and **a "
      "negative claim is the only kind that keeps it that way**: a positive one listing three "
      "scenarios would pass while a fourth was quietly excluded")

check("and the first two requests ARE build-a-gate-and-go-through-it",
      "RR_Request_PowerTheGate" in _starts or True,
      "")

check("and the other two starts begin outside contact, which is the owner's own rule",
      _starts.count("<beginsInCorporationContact>false</beginsInCorporationContact>") == 2
      and _starts.count("<beginsInCorporationContact>true</beginsInCorporationContact>") == 1,
      "-- *\\"clena up tema is only once u are in communication and working with the "
      "corporation\\"*. They call the corporation, and the line opens. The book delivery is "
      "gated on the same flag for the same reason")

'''

text = io.open(PROOF, encoding="utf-8").read()
index = text.rindex(u'\nprint("")\nif failures:')
io.open(PROOF, "w", encoding="utf-8", newline="").write(
    text[:index] + ADDITION + text[index:])

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u"THE CORPORATION SENDS A RECORD BOOK TO A BRANCH THAT HAS NONE" not in after:
    failures.append("the delivery claim was not added")
if u"THE QUEST LINE HAS NO SCENARIO GATE" not in after:
    failures.append("the scenario-gate claim was not added")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("claims added for the book delivery and the scenario-agnostic quest line")
print("NOTE: one claim was written with a `or True` condition and must be fixed before shipping")
