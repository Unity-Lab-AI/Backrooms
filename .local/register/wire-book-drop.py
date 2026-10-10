# -*- coding: utf-8 -*-
"""Wire the record-book delivery: the tick, the save, and the letter.

Owner, 2026-10-01: *"make sure the other scenerios properly get the book in a drop when they need
it and start the quest to go through their built gate"*.

**The quest half already works and is verified rather than assumed.** `OfferNextTutorialRequest`
is gated on `corporationContact` and nothing else -- no scenario check anywhere in it -- so the
tutorial line reaches every branch that calls the corporation. `RR_Request_PowerTheGate` and
`RR_Request_AssembleAndCalibrate` are the first two, which for the Store and the solo start is
exactly *build a gate and go through it*.

**The book half did not exist.** Only the laboratory start ships one, and only since today.
</summary>
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
SERVICES = os.path.join(SRC, "Company", "CampaignServices.cs")
COMPONENT = os.path.join(SRC, "Company", "RimroomsCampaignComponent.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Requests.xml")

EDITS = []

# The company tick, beside the relief it shares a cadence with. Offset so the two scans never
# land on the same tick.
EDITS.append((SERVICES, u"            if (now % 60 == 30) { TickFacilityRelief(); }",
              u"            if (now % 60 == 30) { TickFacilityRelief(); }\n"
              u"            // Offset from the relief so the two map scans never land together.\n"
              u"            if (now % 60 == 45) { TickRecordBookDelivery(); }"))

EDITS.append((COMPONENT, u"            ExposeFieldExposure();",
              u"            ExposeFieldExposure();\n            ExposeRecordBookDelivery();"))

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:46], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

ADDITION = u"""  <RR_Event_RecordBookDelivery>The corporation sent blank record books. A branch with a working gate and nothing to write in is a branch that cannot file anything.</RR_Event_RecordBookDelivery>
  <RR_BookDrop_Title>Record books delivered</RR_BookDrop_Title>
  <RR_BookDrop_Body>{0} has a gate that works and nothing to write in.

The corporation sent {1} blank record books. A crew takes one into a coordinate, writes the route, the distortion and whatever was down there into it, and carries it home. The book is the evidence; there is no separate recorder to lose.

No invoice came with them. Keep one in reserve - a branch that loses its only book cannot file anything until it makes another.</RR_BookDrop_Body>
"""
keyed = io.open(KEYED, encoding="utf-8-sig").read()
CLOSE = u"</LanguageData>"
if keyed.count(CLOSE) != 1:
    print("KEYED ANCHOR PROBLEM: %d" % keyed.count(CLOSE))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    keyed.replace(CLOSE, ADDITION + CLOSE, 1))

services = io.open(SERVICES, encoding="utf-8-sig").read()
component = io.open(COMPONENT, encoding="utf-8-sig").read()
after_keyed = io.open(KEYED, encoding="utf-8-sig").read()
failures = []
if u"TickRecordBookDelivery();" not in services:
    failures.append("THE DELIVERY IS NEVER TICKED -- built and unreachable")
if u"ExposeRecordBookDelivery();" not in component:
    failures.append("the delivery count is never saved")
for key in ("RR_Event_RecordBookDelivery", "RR_BookDrop_Title", "RR_BookDrop_Body"):
    if (u"<%s>" % key) not in after_keyed:
        failures.append("%s has no string" % key)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("book delivery wired: ticked at offset 45, saved, and announced")
