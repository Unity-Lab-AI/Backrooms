# -*- coding: utf-8 -*-
"""Assert the top of the tree: one project, a bounded reach decided in one place, and a seventh
level that actually looks like somewhere.

The property this exists for
---------------------------
**This project retires a restraint, and a retired restraint is the most dangerous thing in this
repository.** `proof-research-tier4.py` asserted *"THE NATURAL DEPTH REACH IS NOT RESEARCH-DRIVEN,
WHATEVER ITS VALUE"*. The owner then approved a Spatial tier 6 whose entire subject is that number.

**The old claim went on passing after the code changed**, because it looked for the ternary
`HasCapability(...) ? <something>MaximumNaturalDepth` and the new code reads
`? DeepFrontierNaturalDepth : MaximumNaturalDepth` -- an identifier that does not end in the name
the pattern wanted. So the build briefly carried a proof asserting the opposite of what the code
did, and nothing said so. That is the exact failure class this battery exists to remove, and it is
why this file states plainly what replaced the old rule:

    The reach is BOUNDED, and ONE place decides it.

Both are asserted below. A capability raises the bound by one; nothing makes it unbounded, and
nothing outside `NaturalFrontierService` gets to have an opinion about how deep found doors go.

The second hazard: three places read the reach
----------------------------------------------
The refusal in `Discover`, the blind dial's deepest rung, and the hint that tells a branch it has
gone as deep as found doors go. **The dial carried its own constant six**, with a comment saying it
matched the natural cap -- and a comment is not a derivation. Left alone it would have shipped a
branch that could walk to depth seven while a blind dial refused to send anybody there and a hint
claimed six was the end. All three are asserted to go through one method.

The third hazard: a seventh level with nothing to look like
-----------------------------------------------------------
The sweep called this *"A CONTENT DECISION, NOT A SWEEP RESULT"* and it was right. The palette had
five bands and the band derivation **wrapped**, so depth seven would have come up Poolrooms: the
second shallowest face in the game worn by the deepest space in it. The sixth band and the
saturating derivation are what make the project honest, so they are claims here rather than
decoration.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
PROJECTS = os.path.join(MOD, "Defs", "RimroomsProjectDefs", "RR_CompanyProjects.xml")
KEYED = os.path.join(MOD, "Languages", "English", "Keyed", "RR_Palette.xml")

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


def defs():
    text = strip_xml_comments(read(PROJECTS))
    found = {}
    for match in re.finditer(
            r"<RimroomsAsyncIndustries\.Investigation\.RimroomsProjectDef>(.*?)"
            r"</RimroomsAsyncIndustries\.Investigation\.RimroomsProjectDef>", text, re.S):
        body = match.group(1)
        name = re.search(r"<defName>([^<]+)</defName>", body)
        if name:
            found[name.group(1).strip()] = body
    return found


project = defs()
source = {}
for root, _, files in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in files:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))

frontier = source.get(os.path.join(SRC, "Portals", "NaturalFrontierService.cs"), "")
dial = source.get(os.path.join(SRC, "Portals", "PortalRandomDial.cs"), "")
hints = source.get(os.path.join(SRC, "Company", "SoloGroupHints.cs"), "")
palette = source.get(os.path.join(SRC, "Generation", "BackroomsPalette.cs"), "")

print("")
print("proof: one project at the top, a bounded reach from one place, and a seventh level with a face")
print("")

# ------------------------------------------------------------------ 1. the one project
print("1. exactly one tier-6 project, and it is Spatial's")
at_tier = sorted(name for name, body in project.items()
                 if "<insightCost>7</insightCost>" in body)
check("exactly one project costs insight 7", len(at_tier) == 1, "-- found %s" % (at_tier,))
body = project.get("RR_Spatial_DeepFrontier")
check("RR_Spatial_DeepFrontier exists", body is not None)
if body is not None:
    check("it is tier 6 by cost and gate",
          "<insightCost>7</insightCost>" in body
          and "<workRequired>26000</workRequired>" in body
          and "<minimumIntellectual>9</minimumIntellectual>" in body)
    check("it asks for six routes, five distortions and four entity logs",
          "<requiredRouteLogs>6</requiredRouteLogs>" in body
          and "<requiredDistortionLogs>5</requiredDistortionLogs>" in body
          and "<requiredEntityLogs>4</requiredEntityLogs>" in body,
          "-- the top of the tree asks for more of everything than the band below it")
    check("it climbs Spatial's own tier 5",
          "<li>RR_Spatial_NearExit</li>" in body,
          "-- a tier 6 reaching across branches would gate two of them on one project")
    check("it grants RR_Cap_DeepFrontier", "<li>RR_Cap_DeepFrontier</li>" in body)
check("no OTHER branch has a tier 6",
      not [n for n in at_tier if not n.startswith("RR_Spatial_")],
      "-- a sixth band on a branch whose fifth was declined would be two inventions, not one")

# ------------------------------------------------------------------ 2. the restraint, restated
print("")
print("2. THE REPLACEMENT FOR THE RETIRED RESTRAINT: bounded, and decided in one place")
check("the reach is answered by one named method",
      "internal static int NaturalDepthReach()" in frontier
      and len(re.findall(r"internal static int NaturalDepthReach\(\)", frontier)) == 1)
check("THE REACH IS BOUNDED: both ends are plain integer constants",
      re.search(r"const int MaximumNaturalDepth = (\d+);", frontier) is not None
      and re.search(r"const int DeepFrontierNaturalDepth = (\d+);", frontier) is not None,
      "-- a capability raises the bound by one. Nothing may make it unbounded")
base = re.search(r"const int MaximumNaturalDepth = (\d+);", frontier)
earned = re.search(r"const int DeepFrontierNaturalDepth = (\d+);", frontier)
check("the earned reach is exactly one deeper than the free reach",
      base is not None and earned is not None
      and int(earned.group(1)) == int(base.group(1)) + 1,
      "-- found %s then %s. One level is the project; a jump would be a different project"
      % (base.group(1) if base else "?", earned.group(1) if earned else "?"))
check("the capability is read ONCE, inside that method",
      len(re.findall(r'HasCapability\("RR_Cap_DeepFrontier"\)', "\n".join(source.values()))) == 1
      and 'HasCapability("RR_Cap_DeepFrontier")' in frontier)
check("the refusal in Discover compares against the METHOD, not the base constant",
      "if (depth > NaturalDepthReach())" in frontier
      and "if (depth > MaximumNaturalDepth)" not in frontier,
      "-- comparing against the constant is how the project would promise a level the code refuses")

# ------------------------------------------------------------------ 3. the three read sites
print("")
print("3. all three readers go through the one method, including the one that had its own copy")
check("THE BLIND DIAL NO LONGER CARRIES ITS OWN SIX",
      not re.search(r"DeepestBlindDial\s*=\s*\d+", dial)
      and "NaturalFrontierService.NaturalDepthReach()" in dial,
      "-- it had a constant six and a comment saying it matched the cap. A comment is not a "
      "derivation, and this is the project's most expensive recurring defect")
check("the dial's weighting asks for the reach once and holds it",
      "int deepest = DeepestBlindDial;" in dial
      and "draw % (deepest * deepest)" in dial,
      "-- a property read twice in one derivation is a derivation that can disagree with itself")
check("the natural-limit hint reads the earned reach",
      "NaturalFrontierService.NaturalDepthReach()" in hints
      and "NaturalFrontierService.MaximumNaturalDepth" not in hints,
      "-- a hint firing at six for a branch that paid to reach seven tells somebody they have hit "
      "a wall they already moved, and this hint fires once and cannot be taken back")
direct = sorted(os.path.relpath(path, REPO).replace(os.sep, "/")
                for path, text in source.items()
                if "MaximumNaturalDepth" in text
                and path != os.path.join(SRC, "Portals", "NaturalFrontierService.cs"))
check("nothing outside NaturalFrontierService reads the base constant at all", not direct,
      "-- read directly in %s" % ", ".join(direct))

# ------------------------------------------------------------------ 4. the seventh level has a face
print("")
print("4. the content half, which was the real blocker")
bands = re.search(r"const int Bands = (\d+);", palette)
check("the palette has a sixth band", bands is not None and int(bands.group(1)) == 6,
      "-- found %s" % (bands.group(1) if bands else "none"))
check("THE BAND DERIVATION SATURATES RATHER THAN WRAPPING",
      "return band >= Bands ? Bands - 1 : band;" in palette
      and "% Bands" not in palette,
      "-- the wrap is what made a depth-six coordinate come up Poolrooms on half its seeds, so the "
      "deepest place a branch could reach wore the second shallowest face in the game")
check("the deepest band is authored out of buildable Core terrain",
      '"BrokenAsphalt"' in palette and '"PackedDirt"' in palette and '"Mud"' not in palette,
      "-- Mud declares no Light/Medium/Heavy affordance and a path cost of 14, so a band floored "
      "in it is a level nothing can be built on and nobody can cross")
check("the deepest band names itself and the name is translated",
      '"RR_Palette_Undercroft"' in palette
      and "<RR_Palette_Undercroft>" in read(KEYED),
      "-- a band with no keyed string renders a raw key on the coordinate")
check("the deepest band asks for no floor colour rather than an unhonoured one",
      re.search(r"look\.floorColor = null;", palette) is not None,
      "-- a tint on terrain that does not expect one is a silent no-op, which is the failure this "
      "file already carries a long comment about")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: one project at the top, the reach bounded and decided once, and a seventh level "
      "that looks like nowhere else")
