# -*- coding: utf-8 -*-
"""Assert the premises the gate equipment-link design rests on.

Every claim below is one the design would be wrong without, and each is checked against the
INSTALLED game data rather than against memory. The first assertion is the one that already
bit: the owner said "multianalysers", and `Multianalyzer` is a ResearchProjectDef. The
building is `MultiAnalyzer`.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
ROLES = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                     "RimroomsGateEquipmentDefs", "RR_GateEquipment.xml")

failures = []


def check(claim, condition, detail=""):
    if condition:
        print("  OK   %s" % claim)
    else:
        print("  FAIL %s %s" % (claim, detail))
        failures.append(claim)


# --------------------------------------------------------------------------- game ThingDefs
thing_defs = {}
for path in glob.glob(os.path.join(GAME, "**", "ThingDefs*", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root:
        name = node.findtext("defName")
        if node.tag == "ThingDef" and name:
            thing_defs[name.strip()] = (node, os.path.relpath(path, GAME))

print("installed ThingDefs indexed: %d" % len(thing_defs))
check("the game data was found and parsed", len(thing_defs) > 1000,
      "(only %d defs; is the install path right?)" % len(thing_defs))

# --------------------------------------------------------------------------- our roles
root = ET.parse(ROLES).getroot()
roles = []
for node in root:
    roles.append({
        "defName": node.findtext("defName"),
        "label": node.findtext("label"),
        "maxLinked": int(node.findtext("maxLinked") or "4"),
        "order": int(node.findtext("displayOrder") or "0"),
        "things": [li.text.strip() for li in node.find("thingDefNames")],
    })

print("")
print("roles declared: %d" % len(roles))
check("at least one role is declared", len(roles) > 0)

# 1. Every def name a role accepts must actually exist. THE one that already bit.
for role in roles:
    for name in role["things"]:
        check("%s accepts %s, which exists in the game" % (role["defName"], name),
              name in thing_defs,
              "-- not a ThingDef in the installed data")

# 2. No def name may appear in two roles: RoleFor() returns the first match in display order,
#    so an overlap would make a thing's role depend on display order rather than on what it is.
seen = {}
overlap = []
for role in roles:
    for name in role["things"]:
        if name in seen:
            overlap.append("%s is in both %s and %s" % (name, seen[name], role["defName"]))
        seen[name] = role["defName"]
check("no def name appears in two roles", not overlap, "-- " + "; ".join(overlap))

# 3. Display order must be unique, or the picker order is arbitrary between ties.
orders = [role["order"] for role in roles]
check("display orders are distinct", len(set(orders)) == len(orders))

# 4. maxLinked must be above one everywhere. The direction was "some shelves and multiples";
#    a role capped at one is the thing being fixed, not the fix.
for role in roles:
    check("%s allows multiples (maxLinked=%d)" % (role["defName"], role["maxLinked"]),
          role["maxLinked"] > 1)


def comp_classes(name):
    node = thing_defs[name][0]
    found = []
    comps = node.find("comps")
    if comps is None:
        return found
    for li in comps:
        found.append(li.get("Class") or "")
    return found


# 5. The power rule must actually bite on something, and the exemption must be necessary.
#    If every candidate were powered, the exemption would be dead code; if none were, the rule
#    would be. Both halves are asserted so neither can quietly become untrue.
powered = [n for n in seen if any("CompProperties_Power" in c for c in comp_classes(n))]
unpowered = [n for n in seen if n not in powered]
print("")
print("powered candidates:   %s" % ", ".join(sorted(powered)))
print("unpowered candidates: %s" % ", ".join(sorted(unpowered)))
check("at least one candidate is powered, so the same-power-net rule bites", len(powered) > 0)
check("at least one candidate is unpowered, so the exemption is necessary", len(unpowered) > 0)

# 6. Shelf specifically must be unpowered. The archive role is the queued evidence-case
#    replacement, and requiring a power net of a shelf would make it permanently unfillable.
check("Shelf has no power component", "Shelf" in unpowered)

# 7. The premise of not reusing Core's facility comps: its defaults really are 8 cells and
#    line-of-sight required. If Core ever changed these, the argument in the source comment
#    would stop being true and somebody should find out from here rather than from a player.
assembly = os.path.join(os.path.dirname(GAME), "RimWorldWin64_Data", "Managed", "Assembly-CSharp.dll")
ilspy = os.path.join(REPO, ".local", "tools", "ilspycmd.exe")
import subprocess
out = subprocess.check_output([ilspy, "-t", "RimWorld.CompProperties_Facility", assembly],
                              stderr=subprocess.STDOUT).decode("utf-8", "replace")
check("Core CompProperties_Facility still defaults to maxDistance 8",
      re.search(r"public float maxDistance = 8f;", out) is not None)
check("Core CompProperties_Facility still defaults to requiresLOS true",
      re.search(r"public bool requiresLOS = true;", out) is not None)

# 8. The candidates that carry Core's own facility comp keep it. Our link is a parallel
#    relationship, and silently removing theirs would change vanilla research linking.
core_facility = [n for n in seen if any("CompProperties_Facility" in c for c in comp_classes(n))]
print("")
print("candidates that also carry Core's facility comp: %s" % ", ".join(sorted(core_facility)))
check("MultiAnalyzer still carries Core's own facility comp", "MultiAnalyzer" in core_facility)
check("ToolCabinet still carries Core's own facility comp", "ToolCabinet" in core_facility)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every claim the equipment-link design rests on")
