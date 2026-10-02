# -*- coding: utf-8 -*-
"""Author About.xml's dependency blocks from the owner's live load order.

Owner direction, 2026-10-01, verbatim: *"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO
GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and when
asked which ones: *"there are alot more depeandacies than just the DLC we have alkinds of mods in
the 274 mod list WE ARE USING ALL OF THEM!!!!"*.

And the posture for the code, owner's answer to the second question: **keep the graceful guards
anyway** -- declare the dependency so RimSort enforces it, but keep `GetNamedSilentFail`-style
lookups so a player who ignores the warning degrades instead of crashing.

## What this emits, and why each of the two blocks is needed

* **`<modDependencies>`** is the half RimSort and RimWorld read to say *this is missing*. Without
  it nothing is enforced, which is the gap the owner is naming: the shipped About.xml declared
  **no dependencies at all** and a description that said *"Core only ... No Harmony, no
  dependencies."*
* **`<loadAfter>`** is the half that makes the order right. It is the functionally load-bearing
  one: a patch cannot see a def from a mod that loads after it. Our mod sat at **position 197 of
  296**, so **99 mods were loading after us** and anything we patch against them was reading a
  def that did not exist yet.

**This never writes to ModsConfig.xml.** That is the owner's file and the standing constraint is
that the active RimSort list is never altered. This reads it and writes only our own About.xml;
RimSort does the re-sorting itself once the constraints are declared.

## The cycle check is not optional

Declaring `loadAfter` against 289 mods deadlocks if any one of them declares a constraint back on
us. This refuses rather than shipping a load order no sorter can satisfy.

Run from the repository root.
"""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ABOUT = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")

CONFIG = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow",
                      "Ludeon Studios", "RimWorld by Ludeon Studios", "Config",
                      "ModsConfig.xml")
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
LOCAL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

OURS = "rimrooms.asyncindustries"
CORE = "ludeon.rimworld"

# Active on this workstation and never a player dependency. The owner's live load order is the
# right source for what the package needs, and it is not the same question as what a PLAYER
# needs: this machine also runs the QA instrument, and generating straight from the order
# declared it as a requirement. A player told they need a debug server has been told something
# false, and `AGENTS.md` already forbids it in as many words -- *"it is not a player dependency
# and must not replace a target mod"*.
#
# Excluded by name with the reason recorded, which is the same shape the cycle check demands of
# anything it refuses. Excluded from BOTH blocks: ordering against an attach-only read-only
# instrument means nothing, and a `loadAfter` row is published text about a debug server too.
QA_ONLY = {
    "brrainz.rimbridgeserver":
        "attach-only read-only QA instrument, owner-operated after launch; never shipped to a "
        "player and never a load-order constraint on us",
}

# The five expansions, in Ludeon's own order. Declared with their canonical casing because a
# dependency row is player-facing text as much as a constraint.
DLC_NAMES = {
    "ludeon.rimworld.royalty": ("Ludeon.RimWorld.Royalty", "RimWorld - Royalty"),
    "ludeon.rimworld.ideology": ("Ludeon.RimWorld.Ideology", "RimWorld - Ideology"),
    "ludeon.rimworld.biotech": ("Ludeon.RimWorld.Biotech", "RimWorld - Biotech"),
    "ludeon.rimworld.anomaly": ("Ludeon.RimWorld.Anomaly", "RimWorld - Anomaly"),
    "ludeon.rimworld.odyssey": ("Ludeon.RimWorld.Odyssey", "RimWorld - Odyssey"),
}


def first(node, tag):
    if node is None:
        return None
    for child in node:
        if child.tag.lower() == tag.lower():
            return (child.text or "").strip()
    return None


def all_of(node, tag):
    """Every <li> under a named tag, case-insensitively."""
    out = []
    if node is None:
        return out
    for child in node:
        if child.tag.lower() != tag.lower():
            continue
        for li in child:
            text = (li.text or "").strip()
            if text:
                out.append(text)
            else:
                package = first(li, "packageId")
                if package:
                    out.append(package)
    return out


def read_about(folder):
    about = os.path.join(folder, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    try:
        root = ET.parse(about).getroot()
    except Exception:
        return None
    package = first(root, "packageId")
    if not package:
        return None
    published = None
    for candidate in (os.path.join(folder, "About", "PublishedFileId.txt"),
                      os.path.join(folder, "PublishedFileId.txt")):
        if os.path.isfile(candidate):
            try:
                published = io.open(candidate, encoding="utf-8-sig").read().strip()
            except Exception:
                published = None
            break
    if not published and os.path.basename(folder).isdigit():
        published = os.path.basename(folder)
    return {
        "packageId": package.strip(),
        "key": package.strip().lower(),
        "name": first(root, "name") or package.strip(),
        "published": published,
        # Everything this mod says about load order, so a cycle against us can be found.
        "after": [value.lower() for value in all_of(root, "loadAfter")],
        "before": [value.lower() for value in all_of(root, "loadBefore")],
        "forceAfter": [value.lower() for value in all_of(root, "forceLoadAfter")],
        "forceBefore": [value.lower() for value in all_of(root, "forceLoadBefore")],
    }


def scan(root):
    found = {}
    if not os.path.isdir(root):
        return found
    for entry in sorted(os.listdir(root)):
        record = read_about(os.path.join(root, entry))
        if record is not None:
            found.setdefault(record["key"], record)
    return found


catalogue = {}
for root in (DATA, WORKSHOP, LOCAL):
    for key, record in scan(root).items():
        catalogue.setdefault(key, record)

if not os.path.isfile(CONFIG):
    print("NO MODSCONFIG AT %s" % CONFIG)
    sys.exit(1)

order = [(li.text or "").strip()
         for li in ET.parse(CONFIG).getroot().find("activeMods")
         if (li.text or "").strip()]

unresolved = [pid for pid in order if pid.lower() not in catalogue]
if unresolved:
    for pid in unresolved:
        print("UNRESOLVED %s" % pid)
    print("REFUSING: a dependency row with no displayName is one RimSort cannot explain.")
    sys.exit(1)

# ---------------------------------------------------------------- the cycle check
cycles = []
for pid in order:
    key = pid.lower()
    if key in (OURS, CORE) or key.startswith("ludeon."):
        continue
    record = catalogue[key]
    if OURS in record["after"] or OURS in record["forceAfter"]:
        cycles.append((pid, "declares loadAfter on us"))
    if OURS in record["before"] or OURS in record["forceBefore"]:
        # loadBefore us is CONSISTENT with us loading after them. Not a cycle; noted only.
        pass
if cycles:
    for pid, why in cycles:
        print("CYCLE  %-46s %s" % (pid, why))
    print("\nREFUSING: declaring loadAfter against a mod that declares loadAfter on us is a "
          "load order no sorter can satisfy. Each one above must be excluded by name, with the "
          "reason recorded, before this can generate.")
    sys.exit(1)
print("cycle check            clean, no active mod declares a load constraint back on us")

# ---------------------------------------------------------------- the two blocks
dependencies = []
load_after = ["Ludeon.RimWorld"]
excluded = []

for pid in order:
    key = pid.lower()
    if key == OURS or key == CORE:
        continue
    if key in QA_ONLY:
        excluded.append((pid, QA_ONLY[key]))
        continue
    if key in DLC_NAMES:
        package, display = DLC_NAMES[key]
        dependencies.append((package, display, None))
        load_after.append(package)
        continue
    record = catalogue[key]
    dependencies.append((record["packageId"], record["name"], record["published"]))
    load_after.append(record["packageId"])


def escape(text):
    return (text.replace(u"&", u"&amp;").replace(u"<", u"&lt;").replace(u">", u"&gt;"))


lines = [u"  <modDependencies>"]
for package, display, published in dependencies:
    lines.append(u"    <li>")
    lines.append(u"      <packageId>%s</packageId>" % escape(package))
    lines.append(u"      <displayName>%s</displayName>" % escape(display))
    if published:
        lines.append(u"      <steamWorkshopUrl>steam://url/CommunityFilePage/%s"
                     u"</steamWorkshopUrl>" % escape(published))
    lines.append(u"    </li>")
lines.append(u"  </modDependencies>")
lines.append(u"  <loadAfter>")
for package in load_after:
    lines.append(u"    <li>%s</li>" % escape(package))
lines.append(u"  </loadAfter>")
BLOCK = u"\n".join(lines)

OLD_LOADAFTER = u"""  <loadAfter>
    <li>Ludeon.RimWorld</li>
  </loadAfter>"""

OLD_REQUIREMENTS = (u"Core only. Royalty, Ideology, Biotech, Anomaly and Odyssey are optional "
                    u"and used when present. No Harmony, no dependencies.")

# Kept as a TEMPLATE, separately from the filled-in text, so the regenerate-matching pattern
# below is derived from the same string a run writes. Two hand-kept copies of one sentence is
# how a pattern silently stops matching the thing it is supposed to match.
REQUIREMENTS_TEMPLATE = (
    u"This build is authored against a specific collection and declares every member of it as a "
    u"dependency, so your mod manager can tell you what is missing instead of letting the game "
    u"fail later: RimWorld - Royalty, Ideology, Biotech, Anomaly and Odyssey, and the %d mods "
    u"loaded alongside them.\n\n"
    u"Load this mod last. Every dependency is declared with loadAfter as well as being a "
    u"requirement, so a sorting manager will place it correctly on its own.\n\n"
    u"Nothing here is patched through Harmony. Content from another mod is looked up by name and "
    u"never assumed, so a missing one degrades what depends on it rather than throwing.")

NEW_REQUIREMENTS = REQUIREMENTS_TEMPLATE % (len(dependencies) - len(DLC_NAMES))

# **This has to be re-runnable, and for its first forty-eight hours it was not.** The anchors
# above match the pre-0.12.76 About.xml only, so the rule recorded alongside it -- *never
# hand-edit the dependency blocks, edit this script and re-run it* -- described something
# impossible: the second run died on its own output. A generator that can only run once is a
# migration, and calling it the source of truth makes the FILE the source of truth by default.
#
# So each replacement now accepts either shape: the original anchor on a first run, or its own
# previous output on every run after. The generated forms are matched as patterns because both
# carry counts that change, and a literal would go stale exactly like the anchor did.
GENERATED_BLOCK = re.compile(
    r"[ ]{2}<modDependencies>.*?</modDependencies>\n[ ]{2}<loadAfter>.*?</loadAfter>", re.S)

# Built from the template so the two can never disagree: escape it, then let the count vary.
GENERATED_REQUIREMENTS = re.compile(
    re.escape(REQUIREMENTS_TEMPLATE).replace(re.escape(u"%d"), r"\d+"))

text = io.open(ABOUT, encoding="utf-8-sig").read()

problems = []
first_run = text.count(OLD_LOADAFTER) == 1
regenerating = len(GENERATED_BLOCK.findall(text)) == 1
if first_run and regenerating:
    problems.append("both the original loadAfter anchor and a generated block are present")
elif not first_run and not regenerating:
    problems.append("neither the original loadAfter anchor nor exactly one generated block "
                    "is present (original: %d, generated: %d)"
                    % (text.count(OLD_LOADAFTER), len(GENERATED_BLOCK.findall(text))))

old_description = text.count(OLD_REQUIREMENTS) == 1
new_description = len(GENERATED_REQUIREMENTS.findall(text)) == 1
if old_description and new_description:
    problems.append("both the original description sentence and a generated one are present")
elif not old_description and not new_description:
    problems.append("neither the original description sentence nor exactly one generated "
                    "description is present (original: %d, generated: %d)"
                    % (text.count(OLD_REQUIREMENTS),
                       len(GENERATED_REQUIREMENTS.findall(text))))

if problems:
    for problem in problems:
        print("ANCHOR PROBLEM %s" % problem)
    sys.exit(1)

if first_run:
    text = text.replace(OLD_LOADAFTER, BLOCK, 1)
    print("mode                   first run, replacing the original loadAfter anchor")
else:
    text = GENERATED_BLOCK.sub(lambda match: BLOCK, text, count=1)
    print("mode                   regenerating, replacing this script's own previous output")

if old_description:
    text = text.replace(OLD_REQUIREMENTS, NEW_REQUIREMENTS, 1)
else:
    text = GENERATED_REQUIREMENTS.sub(lambda match: NEW_REQUIREMENTS, text, count=1)
io.open(ABOUT, "w", encoding="utf-8-sig", newline="\n").write(text)

# ---------------------------------------------------------------- read it back
after = io.open(ABOUT, encoding="utf-8-sig").read()
root = ET.fromstring(after.encode("utf-8"))
declared = all_of(root, "modDependencies")
ordered = all_of(root, "loadAfter")

failures = []
if len(declared) != len(dependencies):
    failures.append("modDependencies read back %d, expected %d" % (len(declared), len(dependencies)))
if len(ordered) != len(load_after):
    failures.append("loadAfter read back %d, expected %d" % (len(ordered), len(load_after)))
if any(value.lower() == OURS for value in declared + ordered):
    failures.append("our own packageId is in a dependency block")
if CORE not in [value.lower() for value in ordered]:
    failures.append("Core is not in loadAfter")
for key in DLC_NAMES:
    if key not in [value.lower() for value in declared]:
        failures.append("%s is not declared" % key)
if u"No Harmony, no dependencies." in after:
    failures.append("the description still claims no dependencies")
# The exclusion is asserted against the FILE, not against the list that built it. A skip that is
# only checked in the loop that performs it proves the loop ran, not that the row is gone.
for key in QA_ONLY:
    if key in [value.lower() for value in declared]:
        failures.append("%s is QA-only and is still declared as a dependency" % key)
    if key in [value.lower() for value in ordered]:
        failures.append("%s is QA-only and is still a loadAfter constraint" % key)

if failures:
    for failure in failures:
        print("READ-BACK FAILED: %s" % failure)
    sys.exit(1)

for pid, why in excluded:
    print("EXCLUDED               %-42s %s" % (pid, why))
if not excluded:
    print("excluded               nothing QA-only was active in the order")
print("modDependencies        %d declared (%d expansions + %d mods)"
      % (len(declared), len(DLC_NAMES), len(declared) - len(DLC_NAMES)))
print("loadAfter              %d entries, Core first" % len(ordered))
print("description            requirements paragraph rewritten; the no-dependencies claim is gone")
print("About.xml re-parsed after writing, every count verified from the file")
