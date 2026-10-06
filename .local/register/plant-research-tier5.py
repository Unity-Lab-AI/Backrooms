# -*- coding: utf-8 -*-
"""Planted faults against `.local/register/proof-research-tier5.py`.

**The proof passed on its first run, which proves nothing at all.** This tier is the one most able to
ship a green instrument over a real fault, for two reasons:

1. **Four of its claims are about things that are ABSENT.** An absence cannot be seen by reading the
   def file — a reader sees four projects and has no way to know whether the other five branches were
   considered and declined or quietly forgotten. A claim about an absence that cannot fail is a
   comment with an exit code.
2. **Two of its claims protect guarantees rather than knobs.** `QuietRoomFraction` and
   `MaxSimultaneousEncounters` are absolutes, and the way they stop being absolutes is one
   capability read inside one function — three lines that look exactly like the four legitimate
   capability reads this same batch added.

So every claim gets a fault aimed at it, including the two that are easy to write and hard to notice:
a quiet-room count that reads a capability, and a tell share that bypasses the one function both
figures are supposed to come from.

**NEVER RUN A PLANT SUITE CONCURRENTLY WITH ANYTHING ELSE.** A suite writes a real fault into the
tree and restores it; anything reading the tree in that window sees the fault. Doing so once reported
four failures that did not exist.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

PROJECTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml"
SERVICING = "src/RimroomsAsyncIndustries/Gate/NativeGateServicing.cs"
TELLS = "src/RimroomsAsyncIndustries/Generation/FixtureTellService.cs"
EXITS = "src/RimroomsAsyncIndustries/Portals/WorldExit.cs"
EVENTS = "src/RimroomsAsyncIndustries/Threats/AnomalyEventService.cs"
LADDER = "src/RimroomsAsyncIndustries/Threats/CoordinatePressureLadder.cs"
CARGO = "src/RimroomsAsyncIndustries/Expedition/ExpeditionCargo.cs"

PROOF = ".local/register/proof-research-tier5.py"

NL = chr(10)

# A whole project def, used by the two plants that bring a declined branch back. Written as a
# template so the two differ only in the branch they revive, which is the thing being tested.
REVIVED = (NL + "  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>" + NL
           + "    <defName>%s</defName>" + NL
           + "    <label>Planted</label>" + NL
           + "    <description>A planted fault. If this is in a shipped build, the plant suite "
           + "was interrupted and the file was not restored.</description>" + NL
           + "    <insightCost>6</insightCost>" + NL
           + "    <workRequired>22000</workRequired>" + NL
           + "  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>" + NL)

PLANTS = [
    # ================================================= 1. the four projects and their shape
    ("a tier-5 project is renamed, so a branch silently loses its top band", PROJECTS,
     "<defName>RR_Facilities_ServicingRegime</defName>",
     "<defName>RR_Facilities_ServicingRegimeRenamed</defName>", PROOF),

    ("A CAPABILITY STOPS BEING GRANTED, so the card promises an unlock nothing can reach", PROJECTS,
     "<li>RR_Cap_TrainedEye</li>", "<li>RR_Cap_TrainedEyeUnused</li>", PROOF),

    ("a tier 5 prerequisites ANOTHER branch, which makes one project gate two", PROJECTS,
     "<li>RR_Spatial_SurfaceReading</li>", "<li>RR_Entities_SteadyNerve</li>", PROOF),

    ("the log ladder flattens, so the top band asks no more of a branch than tier 3 did", PROJECTS,
     "    <requiredEntityLogs>3</requiredEntityLogs>" + NL
     + "    <prerequisiteProjects><li>RR_Entities_SteadyNerve</li></prerequisiteProjects>",
     "    <requiredEntityLogs>1</requiredEntityLogs>" + NL
     + "    <prerequisiteProjects><li>RR_Entities_SteadyNerve</li></prerequisiteProjects>", PROOF),

    ("the insight price drops, so tier 5 costs what tier 4 did", PROJECTS,
     "    <insightCost>6</insightCost>" + NL
     + "    <workRequired>22000</workRequired>" + NL
     + "    <minimumIntellectual>8</minimumIntellectual>" + NL
     + "    <requiredRouteLogs>5</requiredRouteLogs>" + NL
     + "    <requiredDistortionLogs>4</requiredDistortionLogs>" + NL
     + "    <requiredEntityLogs>3</requiredEntityLogs>" + NL
     + "    <prerequisiteProjects><li>RR_Facilities_PractisedDialling</li></prerequisiteProjects>",
     "    <insightCost>5</insightCost>" + NL
     + "    <workRequired>22000</workRequired>" + NL
     + "    <minimumIntellectual>8</minimumIntellectual>" + NL
     + "    <requiredRouteLogs>5</requiredRouteLogs>" + NL
     + "    <requiredDistortionLogs>4</requiredDistortionLogs>" + NL
     + "    <requiredEntityLogs>3</requiredEntityLogs>" + NL
     + "    <prerequisiteProjects><li>RR_Facilities_PractisedDialling</li></prerequisiteProjects>",
     PROOF),

    # ================================================= 2. the absences, which is why this exists
    ("THE SUPERSEDED FIELDCRAFT TIER COMES BACK, promising a fourth hand that already exists",
     PROJECTS, NL + "</Defs>", (REVIVED % "RR_Fieldcraft_FourthHand") + "</Defs>", PROOF),

    ("the gate line sprouts a fifth rung above a connection that already never ends", PROJECTS,
     NL + "</Defs>", (REVIVED % "RR_GateUnending") + "</Defs>", PROOF),

    ("Commerce gets a tier over a number the PLAYER already drags on a slider", PROJECTS,
     NL + "</Defs>", (REVIVED % "RR_Commerce_BetterRates") + "</Defs>", PROOF),

    ("Logistics gets a tier over a safety bound no player will ever reach", PROJECTS,
     NL + "</Defs>", (REVIVED % "RR_Logistics_MoreOrders") + "</Defs>", PROOF),

    ("the branch with no tier 0 grows a top", PROJECTS,
     NL + "</Defs>", (REVIVED % "RR_Transport_Gravship") + "</Defs>", PROOF),

    ("A CREW CAP RETURNS, which is the condition that makes the Fieldcraft absence correct", CARGO,
     "crew.Count < 1 || crew.Distinct()", "crew.Count < 1 || crew.Count > 3 || crew.Distinct()",
     PROOF),

    # ================================================= 3. the guarantees, the subtle half
    ("THE QUIET-ROOM COUNT READS A CAPABILITY, turning a survival guarantee into a tech gate",
     LADDER,
     "            return Math.Max(1, Mathf.CeilToInt(roomCount * QuietRoomFraction));",
     "            RimroomsCampaignComponent planted = Verse.Current.Game == null" + NL
     + "                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();" + NL
     + "            if (planted != null && planted.HasCapability(\"RR_Cap_QuietProtocol\"))" + NL
     + "            { return roomCount; }" + NL
     + "            return Math.Max(1, Mathf.CeilToInt(roomCount * QuietRoomFraction));", PROOF),

    ("the quiet fraction is quietly lowered, which Entities T5 was explicitly refused", LADDER,
     "QuietRoomFraction = 0.5f", "QuietRoomFraction = 0.25f", PROOF),

    ("the absolute encounter ceiling moves, which no depth, wealth or research may do", LADDER,
     "MaxSimultaneousEncounters = 3", "MaxSimultaneousEncounters = 5", PROOF),

    ("THE SUBTRACTING TIER SUBTRACTS TO NOTHING, so an opening can hold no event at all", EVENTS,
     "QuietProtocolEventsPerOpening = 1", "QuietProtocolEventsPerOpening = 0", PROOF),

    ("the event ceiling stops being asked from one place", EVENTS,
     "            int ceiling = EventCeiling();" + NL, "", PROOF),

    # ================================================= 4. each knob's own floor
    ("the servicing project raises the CAPACITY, which rewrites what every saved gate's condition "
     "means", SERVICING, "ServiceCapacityTicks = 600000", "ServiceCapacityTicks = 1200000", PROOF),

    ("the untrained servicing figure moves, so the project stops being about a technician",
     SERVICING, "ReconditionWorkRequired { get { return 1400f; } }",
     "ReconditionWorkRequired { get { return 700f; } }", PROOF),

    ("THE TELL SHARE IS UNCAPPED AND A WRONG FIXTURE BECOMES WALLPAPER", TELLS,
     "TrainedEyeTellPercent = 18", "TrainedEyeTellPercent = 50", PROOF),

    ("the tell share bypasses the one function, so the two figures can drift apart", TELLS,
     "roll % 100 >= MarkedPercent()", "roll % 100 >= TrainedEyeTellPercent", PROOF),

    ("a way out lands on the branch's own doorstep", EXITS,
     "NearExitMinimumTiles = 3", "NearExitMinimumTiles = 0", PROOF),

    ("THE FALLBACK GOES, so earning the project can COST a branch a way out it would have had",
     EXITS,
     "                if (!found)" + NL
     + "                {" + NL
     + "                    found = TileFinder.TryFindNewSiteTile(out destination, from," + NL
     + "                        WorldExitMinimumTiles, WorldExitMaximumTiles, allowCaravans: false);"
     + NL + "                }" + NL,
     "", PROOF),
]

# Every plant is (label, path, old, new, verifier). Asserted rather than assumed, because a
# four-element tuple unpacks into an `IndexError` **inside the loop** — which is to say with a real
# fault already written into the tree and the restore not yet reached. A shape mistake has to be a
# refusal at startup.
for _plant in PLANTS:
    if len(_plant) != 5:
        sys.stderr.write("PLANT LIST MALFORMED: %r has %d field(s), not 5\n"
                         % (_plant[0], len(_plant)))
        sys.exit(2)

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


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the verifier must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = dict((path, io.open(path, encoding="utf-8").read())
               for path in set(plant[1] for plant in PLANTS))

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in opening.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every touched file verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
