# -*- coding: utf-8 -*-
"""Plant a fault, run the containment proof, require exit 1, restore.

A check that cannot fail is the recurring defect in this project, so every claim the proof makes
gets a fault that should break it. Twelve plants across the five files.
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
WATCH = SRC + "/Threats/ContainmentWatch.cs"
ALERTS = SRC + "/Presentation/RimroomsContainmentAlerts.cs"
PROTOCOL = SRC + "/Company/ContainmentProtocol.cs"
GIZMO = SRC + "/Company/ContainmentAlarmGizmo.cs"
CAMPAIGN = SRC + "/Company/RimroomsCampaignComponent.cs"
SERVICES = SRC + "/Company/CampaignServices.cs"
PANE = SRC + "/UI/OperationsFacilities.cs"
REPORT = SRC + "/Facilities/FacilityReport.cs"
CATS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsFacilityDefs/RR_FacilityCategories.xml"


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    ("the sweep goes back to reading one map", WATCH,
     "                if (map == null || map.listerThings == null || !campaign.OwnsMap(map)) { continue; }",
     "                if (map == null || map.listerThings == null) { continue; }"),

    ("the breach alert starts speaking about the map on screen too", ALERTS,
     "                if (!state.Escaping || state.Map == Find.CurrentMap) { continue; }",
     "                if (!state.Escaping) { continue; }"),

    ("the unpowered alert starts speaking about the map on screen too", ALERTS,
     "                if (!state.Unpowered || state.Map == Find.CurrentMap) { continue; }",
     "                if (!state.Unpowered) { continue; }"),

    ("the unpowered alert stops standing down for an escaping platform", ALERTS,
     "                if (state.Escaping) { continue; }\n", ""),

    ("an alert forms a second opinion about containment strength", ALERTS,
     "                culprits.Add(state.Holder);",
     "                if (state.Holder.GetStatValue(StatDefOf.ContainmentStrength) > 0f) { }\n"
     "                culprits.Add(state.Holder);"),

    ("the procedure stops calling the gate's own cutoff", PROTOCOL,
     "                    if (gate.TriggerEmergencyCutoff().Success) { cut++; }",
     "                    cut++;"),

    ("the procedure loses its latch and fires every tick", PROTOCOL,
     "            if (!CutOnBreach(campaign) || campaign.BreachResponded) { return; }",
     "            if (!CutOnBreach(campaign)) { return; }"),

    ("the latch is rearmed during a breach instead of after it", PROTOCOL,
     "                campaign.ClearBreachResponded();\n                return;",
     "                return;"),

    ("the manual alarm reports success while closing nothing", PROTOCOL,
     "            return Execute(campaign) > 0\n"
     "                ? CompanyActionResult.Applied()\n"
     "                : CompanyActionResult.Refused(\"RR_Containment_NothingOpen\");",
     "            Execute(campaign);\n            return CompanyActionResult.Applied();"),

    ("the standing order defaults to disarmed, silently changing every old save", CAMPAIGN,
     'Scribe_Values.Look(ref cutConnectionsOnBreach, "rr_cutConnectionsOnBreach", true);',
     'Scribe_Values.Look(ref cutConnectionsOnBreach, "rr_cutConnectionsOnBreach", false);'),

    ("the procedure is never ticked", SERVICES,
     "            if (now % 60 == 15) { ContainmentProtocol.TickProcedure(this); }\n", ""),

    ("the alarm gizmo is not attached to the console", SRC + "/Gate/CompRimroomsGateConsole.cs",
     "            foreach (Gizmo gizmo in Company.ContainmentAlarmGizmo.For(parent))\n"
     "            { yield return gizmo; }\n", ""),

    ("the pane stops drawing the count while the key stays in the file", PANE,
     'listing.Label("RR_Containment_Held".Translate(holders.Count));',
     'string unused = "RR_Containment_Held".Translate(holders.Count);'),

    ("the pane only describes the order when it is armed", PANE,
     '            listing.Label(cut ? "RR_Containment_ProcedureOn".Translate()\n'
     '                : "RR_Containment_ProcedureOff".Translate());',
     '            if (cut) { listing.Label("RR_Containment_ProcedureOn".Translate()); }'),

    ("the pane section is never reached", PANE,
     "            DrawContainment(listing, campaign);\n", ""),

    ("containment goes back to naming an expansion def", CATS,
     "    <includeContainment>true</includeContainment>",
     "    <buildingDefNames><li>HoldingPlatform</li></buildingDefNames>"),

    ("the capability match loses the prisoner-bed half", REPORT,
     "                var bed = building as Building_Bed;\n"
     "                if (bed != null && bed.ForPrisoners) { return true; }\n", ""),
]

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) != 1:
        print("PLANT SETUP BROKEN (%d matches): %s" % (original.count(old), label))
        sys.exit(2)
    _rr_mark(path, label)
    io.open(path, "w", encoding="utf-8", newline="").write(original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, ".local/register/proof-containment.py"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is
        # what makes a destructive instrument safe, and it was the one
        # line not protected -- a leaked devnull handle raised OSError
        # mid-run twice and left the planted source on disk.
        _rr_restore(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
