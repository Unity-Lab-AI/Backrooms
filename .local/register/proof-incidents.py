# -*- coding: utf-8 -*-
"""Assert the shape of the storyteller surface.

The property this exists for
----------------------------
An `IncidentDef` whose `workerClass` does not resolve is a **silent** failure: RimWorld logs it
once at startup, in red, in a log nobody reads, and the incident simply never fires. The mod
looks like it has storyteller integration and has none. The build cannot see it, because the
class name is a string in XML.

The mirror case is worse in a different way: a worker class nobody references is code that can
never run, which is the same lie as a capability nothing reads.

And one rule here is a **never**: no `StorytellerDef`, ever. It is an exclusive slot the player
would have to give up Cassandra or Randy for, and this mod exists to work with the other 294.

Run from the repository root.
"""
import glob
import io
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
SRC = os.path.join(REPO, "src")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# --------------------------------------------------------------------------- our defs
incidents = []
our_def_types = set()
for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root:
        our_def_types.add(node.tag)
    for node in root.iter("IncidentDef"):
        incidents.append({
            "defName": (node.findtext("defName") or "").strip(),
            "worker": (node.findtext("workerClass") or "").strip(),
            "category": (node.findtext("category") or "").strip(),
            "tags": [li.text.strip() for li in (node.find("targetTags") or []) if li.text],
            "label": (node.findtext("label") or "").strip(),
            "letterLabel": (node.findtext("letterLabel") or "").strip(),
            "letterText": (node.findtext("letterText") or "").strip(),
        })

# --------------------------------------------------------------------------- our source
source = {}
for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    source[rel] = io.open(path, encoding="utf-8-sig").read()
all_source = "\n".join(source.values())

worker_classes = set()
for rel, text in source.items():
    for name in re.findall(r"class\s+(IncidentWorker_\w+)", text):
        namespace = re.search(r"namespace\s+([\w.]+)", text)
        worker_classes.add((namespace.group(1) if namespace else "") + "." + name)

concrete = {name for name in worker_classes
            if not re.search(r"abstract\s+class\s+" + re.escape(name.split(".")[-1]), all_source)}

print("incident defs   : %d" % len(incidents))
print("worker classes  : %d (%d concrete)" % (len(worker_classes), len(concrete)))
print("")

check("the mod ships at least one IncidentDef", len(incidents) > 0,
      "-- no storyteller knows this mod exists")

# 1. THE property. Every workerClass must resolve to a class we actually define.
for incident in incidents:
    check("%s workerClass resolves to a real class" % incident["defName"],
          incident["worker"] in worker_classes,
          "-- '%s' does not exist; RimWorld would log once at startup and never fire it"
          % incident["worker"])

# 2. The other direction. A concrete worker nobody references can never run.
referenced = {incident["worker"] for incident in incidents}
for name in sorted(concrete):
    check("%s is referenced by an IncidentDef" % name.split(".")[-1], name in referenced,
          "-- code that can never run")

# 3. Category must be a real Core IncidentCategoryDef, or the def fails to resolve it.
core_categories = set()
for path in glob.glob(os.path.join(GAME, "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        continue
    for node in root.iter("IncidentCategoryDef"):
        name = node.findtext("defName")
        if name:
            core_categories.add(name.strip())
for incident in incidents:
    check("%s category %s is a real Core category" % (incident["defName"], incident["category"]),
          incident["category"] in core_categories,
          "-- Core has " + ", ".join(sorted(core_categories)))

# 4. Every one of ours targets the player's home map. Each of these events is written about
#    the place the company lives, and a storyteller aiming one at the world or at a generated
#    coordinate would fire a worker whose every assumption is about the headquarters.
for incident in incidents:
    check("%s targets only Map_PlayerHome" % incident["defName"],
          incident["tags"] == ["Map_PlayerHome"],
          "-- targets " + ", ".join(incident["tags"] or ["nothing"]))

# 5. A player reads the letter. An incident with no text is an event that happens invisibly.
for incident in incidents:
    check("%s has a label, letter label and letter text" % incident["defName"],
          bool(incident["label"]) and bool(incident["letterLabel"])
          and len(incident["letterText"]) > 40)

# 6. THE NEVER. A StorytellerDef is an exclusive slot; shipping one would ask a player running
#    294 other mods to give up the storyteller they chose.
check("the mod ships no StorytellerDef", "StorytellerDef" not in our_def_types,
      "-- an exclusive slot, and this mod exists to work with the others")

# 7 and 8 ask about CODE, not prose.
#
#    The first version of claim 8 matched the whole file and failed on this mod's own doc
#    comment explaining why incursion is excluded from the incident surface. THE ASSERTION WAS
#    WRONG AND THE SOURCE WAS RIGHT (invariant 130): the rule is that no incident worker CALLS
#    into these systems, and documenting why one must not is precisely the comment worth
#    keeping. Stripping comments first is the honest way to ask the question.
def code_only(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    kept = [line for line in text.splitlines() if not line.lstrip().startswith("//")]
    return chr(10).join(kept)


incident_code = {rel: code_only(text) for rel, text in source.items() if "/Incidents/" in rel}
check("the incident sources were found", len(incident_code) > 0)

# 7. The guarantee must not become an incident. If the clean-up team ever moves behind a
#    storyteller, "facilities never die" becomes "facilities usually do not die".
check("no incident worker runs the facility relief",
      not any("RunFacilityRelief" in text or "TickFacilityRelief" in text
              for text in incident_code.values()),
      "-- a guarantee must not be subject to whether and when")

# 8. Invariant 53 keeps exactly one door into the incursion exception.
check("no incident worker calls into incursion",
      not any("Incursion" in text for text in incident_code.values()),
      "-- invariant 53 bounds incursion on five axes and names one entry point")

# 9. Core's hooks are still the hooks. If either were renamed or made public/private, our
#    overrides would stop overriding and every incident would fall back to base behaviour.
assembly = os.path.join(os.path.dirname(GAME), "RimWorldWin64_Data", "Managed",
                        "Assembly-CSharp.dll")
ilspy = os.path.join(REPO, ".local", "tools", "ilspycmd.exe")
out = subprocess.check_output([ilspy, "-t", "RimWorld.IncidentWorker", assembly],
                              stderr=subprocess.STDOUT).decode("utf-8", "replace")
check("Core IncidentWorker.CanFireNowSub is still protected virtual",
      re.search(r"protected virtual bool CanFireNowSub\(IncidentParms", out) is not None,
      "-- our gating would stop being consulted")
check("Core IncidentWorker.TryExecuteWorker is still protected virtual",
      re.search(r"protected virtual bool TryExecuteWorker\(IncidentParms", out) is not None,
      "-- our effects would stop running")
check("Core IncidentWorker still offers SendStandardLetter",
      re.search(r"protected void SendStandardLetter\(IncidentParms", out) is not None)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the storyteller surface is wired, bounded, and owns no slot")
