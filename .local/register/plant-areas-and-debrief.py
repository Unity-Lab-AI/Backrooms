# -*- coding: utf-8 -*-
"""Plant a fault, run the batch proof, require exit 1, restore."""
import io
import os
import subprocess
import sys

SRC = "src/RimroomsAsyncIndustries"
ROOF = SRC + "/ConnectedWork/Providers/RoofWorkProvider.cs"
UPKEEP = SRC + "/ConnectedWork/Providers/UpkeepProviders.cs"
DEBRIEF = SRC + "/Company/StaffDebrief.cs"
EXP = SRC + "/Expedition/RimroomsExpeditionComponent.cs"
PANE = SRC + "/UI/OperationsFacilities.cs"
CAMPAIGN = SRC + "/Company/RimroomsCampaignComponent.cs"
XML = "Mod/Rimrooms - Async Industries/1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml"


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
_RR_SENTINEL = os.path.join(".local", "register", ".plant-in-progress")


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


PLANTS = [
    # --- roof family
    ("the roof continuation drops below Core's BuildRoofs", XML,
     "<priorityInType>101</priorityInType>", "<priorityInType>99</priorityInType>"),

    ("the roof provider stops asking Core's roof-holder refusal", ROOF,
     "                if (!RoofCollapseUtility.WithinRangeOfRoofHolder(cell, map)) { continue; }\n", ""),

    ("the build route stops skipping cells that are already roofed", ROOF,
     "                if (cell.Roofed(map)) { continue; }\n", ""),

    ("a roof route loses its ceiling reservation", ROOF,
     "                if (work == null &&\n"
     "                    !pawn.CanReserve(cell, 1, -1, ReservationLayerDefOf.Ceiling))\n"
     "                { continue; }\n"
     "                return true;\n"
     "            }\n"
     "            return false;\n"
     "        }\n"
     "\n"
     "        /// <summary>\n"
     "        /// A cell the player marked for no roof that has one.",
     "                return true;\n"
     "            }\n"
     "            return false;\n"
     "        }\n"
     "\n"
     "        /// <summary>\n"
     "        /// A cell the player marked for no roof that has one."),

    # REAL CODE, NOT A COMMENT. This plant used to insert
    # `/* Backrooms Coordinate check */` and demand a failure, which the proof could never
    # deliver: it reads this file through `strip_cs_comments` on purpose, because a comment
    # naming the Backrooms is not a second opinion that can drift out of step with the rule.
    # A depth test that short-circuits the provider is, so that is what gets planted.
    ("the roof provider grows a Backrooms exception of its own", ROOF,
     "        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)\n        {",
     "        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)\n"
     "        {\n            if (BackroomsCoordinateDepthOf(map) > 0) { return false; }"),

    ("the roof provider is built but never registered",
     SRC + "/ConnectedWork/ConnectedDeploymentProvider.cs",
     "                { RoofWork, roofWork },\n", ""),

    # --- weather routes
    ("the snow test becomes an AND and refuses real work", UPKEEP,
     "if (map.snowGrid.GetDepth(cell) < 0.2f && cell.GetSandDepth(map) < 0.2f)",
     "if (map.snowGrid.GetDepth(cell) < 0.2f || cell.GetSandDepth(map) < 0.2f)"),

    ("the pollution route loses its null-grid guard", UPKEEP,
     "            if (!snow && map.pollutionGrid == null) { return false; }\n", ""),

    ("the cleaning family stops reaching the weather routes from the definitive half", UPKEEP,
     "            if (AnyWeatherToClear(pawn.Map, pawn, null)) { return true; }\n", ""),

    # --- debrief
    ("somebody can debrief themselves", DEBRIEF,
     '            if (interviewer == crewMember) { return "RR_Debrief_SelfReport"; }\n', ""),

    ("the debrief invents its own Social floor", DEBRIEF,
     "                social.Level < InterviewerSocialFloor)",
     "                social.Level < 6)"),

    ("a debrief can be taken on the far side", DEBRIEF,
     '            if (crewMember.Map == null || crewMember.Map != Headquarters)\n'
     '            { return "RR_Debrief_NotHome"; }\n', ""),

    ("taking the report stops clearing the hold", DEBRIEF,
     "            debriefHolds.Remove(hold);\n", ""),

    ("raising a hold stops being idempotent", DEBRIEF,
     "                if (HoldFor(pawn) != null) { continue; }\n", ""),

    ("the saved hold list loses its cap", DEBRIEF,
     "                while (debriefHolds.Count > MaximumDebriefHolds) { debriefHolds.RemoveAt(0); }\n", ""),

    ("a hold whose pawn is gone is kept and blocks dispatch forever", DEBRIEF,
     "                debriefHolds.RemoveAll(hold => hold == null || !hold.IsValid);\n", ""),

    ("the holds stop being saved", CAMPAIGN, "            ExposeDebriefs();\n", ""),

    # --- quarantine
    ("QUARANTINE: dispatch stops refusing an undebriefed crew member", EXP,
     "            for (int index = 0; index < crew.Count; index++)\n"
     "            {\n"
     "                if (Campaign.AwaitingDebrief(crew[index]))\n"
     '                { return Refuse("RR_Exp_AwaitingDebrief"); }\n'
     "            }\n", ""),

    ("the hold is never raised on return", EXP,
     "            Campaign.NoteReturnedFromField(run.crew, run.coordinateId);\n", ""),

    ("a stranded trip starts raising holds too", EXP,
     "            run.status = ExpeditionStatus.Stranded;\n            run.failureKey = key;",
     "            run.status = ExpeditionStatus.Stranded;\n"
     "            Campaign.NoteReturnedFromField(run.crew, run.coordinateId);\n"
     "            run.failureKey = key;"),

    # --- pane
    ("the pane stops drawing the outstanding count", PANE,
     'listing.Label("RR_Debrief_Outstanding".Translate(holds.Count));',
     'string unused = "RR_Debrief_Outstanding".Translate(holds.Count);'),

    ("the pane goes silent when nobody is waiting", PANE,
     '            { listing.Label("RR_Debrief_NoneOutstanding".Translate()); return; }',
     '            { return; }'),

    ("the interviewer choice stops being deterministic", PANE,
     "                .ThenBy(candidate => candidate.ThingID, StringComparer.Ordinal)\n", ""),

    ("the pane offers the crew member as their own interviewer", PANE,
     "candidate != null && candidate != crewMember &&", "candidate != null &&"),

    ("the debrief pane is never reached", PANE,
     "            DrawDebriefs(listing, campaign);\n", ""),
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
        code = subprocess.call([sys.executable, ".local/register/proof-areas-and-debrief.py"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is
        # what makes a destructive instrument safe, and it was the one
        # line not protected -- a leaked devnull handle raised OSError
        # mid-run twice and left the planted source on disk.
        io.open(path, "w", encoding="utf-8", newline="").write(original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
