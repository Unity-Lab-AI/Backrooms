# -*- coding: utf-8 -*-
"""Assert three surfaces exist over mechanics that already worked, and that none of them decides.

Rows 889, 1010 and 832, all three of which the queue correctly described as presentation gaps over
working machinery. The risk in a presentation gap is not that it stays open -- it is that closing it
introduces a **second opinion** beside the rule it is presenting.

  * **889 -- confirming the beacon sale.** Selling everything inside the radius is large and
    irreversible, and the gizmo description was the only warning, read after the click.

  * **1010 -- the coordinate's band.** `CoordinatePressureLadder.BandFor` has decided how hostile a
    space is since 0.8.4-dev, drives anomaly events and gates incursion, and **had never been shown
    to a player.** Invariant 28 wants every rule learnable; this one was learnable only by being
    hurt by it.

  * **832 -- the crossing order on the door.** The row: *"The capability is done... What is
    outstanding is surfacing the order and its reason on the door itself."* **Invariant 1 is the
    thing at risk here:** `PortalTraversalPolicy` is the only traversal chokepoint, and a gizmo
    that decides eligibility for itself is exactly how a chokepoint stops being one.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed")

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


beacon = strip_cs_comments(read(os.path.join(SRC, "Economy", "CompRimroomsCreditBeacon.cs")))
ladder = strip_cs_comments(read(os.path.join(SRC, "Threats", "CoordinatePressureLadder.cs")))
pane = strip_cs_comments(read(os.path.join(SRC, "UI", "MainTabWindow_Operations.cs")))
cross = strip_cs_comments(read(os.path.join(SRC, "Portals", "DoorCrossingGizmo.cs")))
gate = strip_cs_comments(read(os.path.join(SRC, "Gate", "CompRimroomsGate.cs")))
emergence = strip_cs_comments(read(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")))
company_keys = read(os.path.join(KEYED, "RR_Company.xml"))
portal_keys = read(os.path.join(KEYED, "RR_Portals.xml"))

print("")
print("proof: three surfaces, and not one of them decides anything")
print("")

print("1. the beacon sale is confirmed before it happens")
check("the sell gizmo opens a confirmation rather than selling",
      "Dialog_MessageBox.CreateConfirmation" in beacon,
      "-- the description was the only warning, and it is read after the click")
check("the confirmation names the count and the total",
      "RR_Exchange_SellConfirm" in beacon and
      "itemCount.ToString" in body_of(beacon, "var sell = new Command_Action"))
check("the confirmation is translated and says it cannot be undone",
      "<RR_Exchange_SellConfirm>" in company_keys and
      "cannot be undone" in company_keys)
check("the sale itself is unchanged",
      "campaign.ExchangeValuables(" in body_of(beacon, "private void SellValuables()"),
      "-- a confirmation must not become a second place that decides what sells")

print("")
print("2. the band is shown, and the ladder still owns it")
check("a keyed label exists for every band",
      all(('"RR_Band_%s"' % name) in ladder
          for name in ("Quiet", "Unsettled", "Active", "Hostile")))
check("the label keys are literals, not built from the enum",
      '"RR_Band_" +' not in ladder,
      "-- a key assembled at run time cannot be checked, and this project has caught that five times")
check("all four are translated",
      all(("<RR_Band_%s>" % name) in portal_keys
          for name in ("Quiet", "Unsettled", "Active", "Hostile")))
check("the readout calls BandFor rather than deriving a band",
      "CoordinatePressureLadder.BandFor(coordinate," in pane,
      "-- the ladder decides; the pane only prints")
check("the readout is actually drawn, not merely mentioned",
      'listing.Label("RR_UI_CoordinateBand".Translate(' in pane and
      "<RR_UI_CoordinateBand>" in company_keys,
      "-- an unshown label is the unwired defect class again. A fault plant caught the first "
      "version of this claim passing while the row was not drawn at all: it checked the key was "
      "PRESENT, not that it reached listing.Label")

print("")
print("3. the door order asks the chokepoint and never decides")
check("eligibility comes from the crossing service",
      "RimroomsPortalCrossingService.EligibilityFailureKey(pawn)" in cross,
      "-- invariant 1: PortalTraversalPolicy is the ONLY traversal chokepoint")
check("the order comes from the travel service",
      "PortalTravelService.OrderCrossing(ordered, connection)" in cross)
check("the gizmo contains no eligibility rule of its own",
      not re.search(r"(?i)(IsPrisoner|IsSlave|Drafted|Downed)", cross),
      "-- a second opinion in a gizmo is how a chokepoint stops being one")
check("the connection is read from the network, not from the door",
      "GetComponent<RimroomsPortalNetwork>()" in cross,
      "-- a moved door or a cleared address must stop offering the order at once")
check("a refused pawn is listed WITH the reason rather than hidden",
      "RR_DoorCross_Refused" in cross,
      "-- a name missing from a menu explains nothing")
check("selected pawns are sorted before being listed",
      "OrderBy(pawn => pawn.LabelShortCap.ToString(), System.StringComparer.Ordinal)" in cross,
      "-- invariant 26, and this menu issues an order")
check("the gizmo appears on a designated gate",
      "Portals.DoorCrossingGizmo.For(parent)" in gate)
check("and on a natural way out, which is also a door",
      "DoorCrossingGizmo.For(parent)" in emergence)
for key in ("RR_DoorCross_Label", "RR_DoorCross_Desc", "RR_DoorCross_Send",
            "RR_DoorCross_Refused", "RR_DoorCross_NobodySelected"):
    check("%s is translated" % key, "<%s>" % key in portal_keys)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: three surfaces added, and every rule still lives where it lived")
