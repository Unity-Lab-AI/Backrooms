# -*- coding: utf-8 -*-
"""Show staff prior exposure, and the strings for it.

**A modifier the player cannot see is the same defect as one that never runs.** The dial gets
faster, the player is never told why, and the feature reads as noise in a number. So the crew
panel names who has been through before and how often, and says plainly when somebody has walked
this exact address.

The panel already lists every candidate rather than filtering -- *"a staff member who has
vanished from the list is indistinguishable from one who was never hired"* -- and this follows
that: a novice is labelled a novice rather than left blank.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UI = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI", "OperationsCrewPlanner.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_CrewPlanner.xml")

OLD = u"""                listing.Label(candidate.Ready
                    ? "RR_Plan_RowReady".Translate(name, Kilograms(candidate.FreeMass))
                    : "RR_Plan_RowUnready".Translate(name, candidate.ReasonKey.Translate()));
            }"""

NEW = u"""                listing.Label(candidate.Ready
                    ? "RR_Plan_RowReady".Translate(name, Kilograms(candidate.FreeMass))
                    : "RR_Plan_RowUnready".Translate(name, candidate.ReasonKey.Translate()));

                // **Staff prior exposure, said out loud.** The operator's own experience of an
                // address takes work off the dial, and a discount nobody can see is a discount
                // the player reads as noise. A novice is named a novice rather than left blank,
                // for the same reason this list shows unready candidates instead of hiding them.
                int trips = campaign.FieldTripsFor(candidate.Pawn);
                string address = gate == null ? null : gate.SpinUpCoordinateId;
                if (trips <= 0) { listing.Label("RR_Plan_ExposureNone".Translate()); }
                else if (campaign.HasBeenTo(candidate.Pawn, address))
                {
                    listing.Label("RR_Plan_ExposureKnowsRoute".Translate(
                        trips.ToString(CultureInfo.CurrentCulture)));
                }
                else
                {
                    listing.Label("RR_Plan_ExposureTrips".Translate(
                        trips.ToString(CultureInfo.CurrentCulture)));
                }
            }"""

text = io.open(UI, encoding="utf-8-sig").read()
if text.count(OLD) != 1:
    print("UI ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(UI, "w", encoding="utf-8-sig", newline="").write(text.replace(OLD, NEW, 1))

ADDITION = u"""  <RR_Plan_ExposureNone>    No field history. This would be their first trip through.</RR_Plan_ExposureNone>
  <RR_Plan_ExposureTrips>    {0} trips through, none of them to this address.</RR_Plan_ExposureTrips>
  <RR_Plan_ExposureKnowsRoute>    {0} trips through, and they have walked this address before. As operator they bring the gate up faster.</RR_Plan_ExposureKnowsRoute>
"""

keyed = io.open(KEYED, encoding="utf-8-sig").read()
CLOSE = u"</LanguageData>"
if keyed.count(CLOSE) != 1:
    print("KEYED ANCHOR PROBLEM: %d" % keyed.count(CLOSE))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    keyed.replace(CLOSE, ADDITION + CLOSE, 1))

after_ui = io.open(UI, encoding="utf-8-sig").read()
after_keyed = io.open(KEYED, encoding="utf-8-sig").read()
failures = []
for token in ("campaign.FieldTripsFor(candidate.Pawn)",
              "campaign.HasBeenTo(candidate.Pawn, address)"):
    if token not in after_ui:
        failures.append("the panel never asks %r" % token[:44])
for key in ("RR_Plan_ExposureNone", "RR_Plan_ExposureTrips", "RR_Plan_ExposureKnowsRoute"):
    if (u"<%s>" % key) not in after_keyed:
        failures.append("%s is missing" % key)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("exposure is on the crew panel, with a line for a novice, a veteran, and one who knows the route")
