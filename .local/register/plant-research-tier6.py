# -*- coding: utf-8 -*-
"""Planted faults against `.local/register/proof-research-tier6.py`.

**This suite exists because of a green that was already wrong.** The restraint tier 6 retires --
*"the natural depth reach is not research-driven"* -- went on PASSING after the code stopped
honouring it, because the claim looked for one spelling of a ternary and the new code used another.
A proof that cannot fail is a comment with an exit code, and the only way to know a claim can fail
is to break the thing it watches and look.

So every claim gets a fault aimed at it, including the three that matter most and are least visible:
the blind dial getting its own copy of the reach back, the band derivation going back to wrapping,
and `Mud` returning as the deepest band's floor -- which would ship a level nothing can be built on
and nobody can cross at speed.

**NEVER RUN A PLANT SUITE CONCURRENTLY WITH ANYTHING ELSE.** A suite writes a real fault into the
tree and restores it; anything reading the tree in that window sees the fault.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

PROJECTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Palette.xml"
FRONTIER = "src/RimroomsAsyncIndustries/Portals/NaturalFrontierService.cs"
DIAL = "src/RimroomsAsyncIndustries/Portals/PortalRandomDial.cs"
HINTS = "src/RimroomsAsyncIndustries/Company/SoloGroupHints.cs"
PALETTE = "src/RimroomsAsyncIndustries/Generation/BackroomsPalette.cs"

PROOF = ".local/register/proof-research-tier6.py"

NL = chr(10)

RIVAL = (NL + "  <RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>" + NL
         + "    <defName>RR_Entities_DeeperStudy</defName>" + NL
         + "    <label>Planted</label>" + NL
         + "    <description>A planted fault. If this is in a shipped build, the plant suite was "
         + "interrupted and the file was not restored.</description>" + NL
         + "    <insightCost>7</insightCost>" + NL
         + "    <workRequired>26000</workRequired>" + NL
         + "  </RimroomsAsyncIndustries.Investigation.RimroomsProjectDef>" + NL)

PLANTS = [
    # ================================================= 1. the one project
    ("the only tier-6 project is renamed, so the top of the tree quietly vanishes", PROJECTS,
     "<defName>RR_Spatial_DeepFrontier</defName>",
     "<defName>RR_Spatial_DeepFrontierRenamed</defName>", PROOF),

    ("the capability stops being granted, so the deepest level is promised and unreachable",
     PROJECTS, "<li>RR_Cap_DeepFrontier</li>", "<li>RR_Cap_DeepFrontierUnused</li>", PROOF),

    ("the top of the tree prerequisites ANOTHER branch, gating two on one project", PROJECTS,
     "<li>RR_Spatial_NearExit</li>", "<li>RR_Entities_QuietProtocol</li>", PROOF),

    ("A SECOND BRANCH GROWS A TIER 6, which would be an invention rather than a sweep result",
     PROJECTS, NL + "</Defs>", RIVAL + "</Defs>", PROOF),

    ("the top project asks for less evidence than the band below it", PROJECTS,
     "<requiredEntityLogs>4</requiredEntityLogs>", "<requiredEntityLogs>2</requiredEntityLogs>",
     PROOF),

    ("the skill gate drops back to tier 4's", PROJECTS,
     "<minimumIntellectual>9</minimumIntellectual>", "<minimumIntellectual>7</minimumIntellectual>",
     PROOF),

    # ================================================= 2. the restraint that replaced the retired one
    ("THE EARNED REACH JUMPS INSTEAD OF STEPPING, which is a different project with the same card",
     FRONTIER, "DeepFrontierNaturalDepth = 7", "DeepFrontierNaturalDepth = 12", PROOF),

    ("THE REFUSAL GOES BACK TO THE BASE CONSTANT, so the card promises a level the code refuses",
     FRONTIER, "if (depth > NaturalDepthReach())", "if (depth > MaximumNaturalDepth)", PROOF),

    ("the reach stops being bounded by a constant at all", FRONTIER,
     "internal const int DeepFrontierNaturalDepth = 7;",
     "internal static int DeepFrontierNaturalDepth { get { return int.MaxValue; } }", PROOF),

    # ================================================= 3. the three readers
    ("THE BLIND DIAL GETS ITS OWN CONSTANT SIX BACK, the defect this project keeps meeting", DIAL,
     "        internal static int DeepestBlindDial" + NL
     + "        { get { return NaturalFrontierService.NaturalDepthReach(); } }",
     "        internal const int DeepestBlindDial = 6;", PROOF),

    ("the dial reads the reach through the base constant, which is a copy by another name", DIAL,
     "{ get { return NaturalFrontierService.NaturalDepthReach(); } }",
     "{ get { return NaturalFrontierService.MaximumNaturalDepth; } }", PROOF),

    ("the dial asks for the reach twice in one derivation", DIAL,
     "draw % (deepest * deepest)", "draw % (DeepestBlindDial * DeepestBlindDial)", PROOF),

    ("THE HINT CLAIMS SIX IS THE END TO A BRANCH THAT PAID TO REACH SEVEN", HINTS,
     "int reach = Portals.NaturalFrontierService.NaturalDepthReach();",
     "int reach = Portals.NaturalFrontierService.MaximumNaturalDepth;", PROOF),

    # ================================================= 4. the content half
    ("the sixth band goes, so the seventh level wears the second shallowest face in the game",
     PALETTE, "public const int Bands = 6;", "public const int Bands = 5;", PROOF),

    ("THE BAND DERIVATION GOES BACK TO WRAPPING", PALETTE,
     "            return band >= Bands ? Bands - 1 : band;", "            return band % Bands;",
     PROOF),

    # Re-aimed twice over, and the second time is the interesting one. Mud was rejected for being
    # unbuildable; `BrokenAsphalt` replaced it and was rejected by ANOTHER proof for costing nothing
    # when lifted, which would make the deepest level the one with worthless floors. The band is
    # flagstone now, and both rejected materials are worth planting.
    ("MUD COMES BACK AS THE DEEPEST FLOOR: unbuildable, path cost 14, found rather than built",
     PALETTE, 'look.floor = Named<TerrainDef>("FlagstoneSlate") ?? look.floor;',
     'look.floor = Named<TerrainDef>("Mud") ?? look.floor;', PROOF),

    # **ANCHORED ON BOTH LINES, because `Concrete` is ALSO the machinery band's accent.** The first
    # version replaced the first occurrence and so edited machinery, leaving the band it claimed to
    # test untouched -- a plant that proves nothing while reporting MISSED.
    ("a worthless natural floor comes back, so the deepest level pays nothing when lifted",
     PALETTE,
     'look.floor = Named<TerrainDef>("FlagstoneSlate") ?? look.floor;' + NL
     + '                    look.accent = Named<TerrainDef>("Concrete") ?? look.floor;',
     'look.floor = Named<TerrainDef>("FlagstoneSlate") ?? look.floor;' + NL
     + '                    look.accent = Named<TerrainDef>("PackedDirt") ?? look.floor;', PROOF),

    ("the deepest band loses its keyed string and renders a raw key on the coordinate", KEYED,
     "<RR_Palette_Undercroft>", "<RR_Palette_UndercroftUnused>", PROOF),

    ("the deepest band asks for a tint the terrain will not honour, silently", PALETTE,
     "                    look.floorColor = null;",
     '                    look.floorColor = NamedColor("Structure_BrownDirt");', PROOF),
]

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
