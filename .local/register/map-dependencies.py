# -*- coding: utf-8 -*-
"""Map every active mod's packageId to its folder, name and Workshop id.

Owner direction, 2026-10-01, verbatim: *"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO
GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and when
asked which: *"there are alot more depeandacies than just the DLC we have alkinds of mods in the
274 mod list WE ARE USING ALL OF THEM!!!!"*.

**This reads the owner's live load order and never writes to it.** `ModsConfig.xml` is the
owner's own file; the standing constraint is that only the owner launches the game and the active
RimSort list is never altered. This opens it read-only and reports.

Run from the repository root. Reports coverage; writes nothing.
"""
import io
import os
import sys
import xml.etree.ElementTree as ET

CONFIG = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow",
                      "Ludeon Studios", "RimWorld by Ludeon Studios", "Config",
                      "ModsConfig.xml")
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
LOCAL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

OURS = "rimrooms.asyncindustries"


def first(node, tag):
    """A tag's text, case-insensitively, because About.xml casing is not consistent."""
    if node is None:
        return None
    for child in node:
        if child.tag.lower() == tag.lower():
            return (child.text or "").strip()
    return None


def read_about(folder):
    """packageId, name and PublishedFileId for one mod folder, or None."""
    about = os.path.join(folder, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    try:
        root = ET.parse(about).getroot()
    except Exception as error:
        print("  UNPARSEABLE %s: %s" % (about, error))
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
        "folder": folder,
    }


def scan(root):
    found = {}
    if not os.path.isdir(root):
        return found
    for entry in sorted(os.listdir(root)):
        record = read_about(os.path.join(root, entry))
        if record is None:
            continue
        # First writer wins, and the scan order below puts Data before Workshop before Local,
        # so an official folder is never shadowed by a copy of it.
        found.setdefault(record["key"], record)
    return found


catalogue = {}
for root in (DATA, WORKSHOP, LOCAL):
    for key, record in scan(root).items():
        catalogue.setdefault(key, record)

if not os.path.isfile(CONFIG):
    print("NO MODSCONFIG AT %s" % CONFIG)
    raise SystemExit(1)

active = ET.parse(CONFIG).getroot().find("activeMods")
order = [(li.text or "").strip() for li in active if (li.text or "").strip()]

print("active entries        %d" % len(order))
print("catalogue entries     %d" % len(catalogue))

missing = [pid for pid in order if pid.lower() not in catalogue]
print("unresolved            %d" % len(missing))
for pid in missing:
    print("  MISSING FOLDER  %s" % pid)

ours = [pid for pid in order if pid.lower() == OURS]
print("our own mod in order  %s" % ("yes" if ours else "NO"))
if ours:
    print("our position          %d of %d" % (order.index(ours[0]) + 1, len(order)))

dlc = [pid for pid in order if pid.lower().startswith("ludeon.")]
others = [pid for pid in order
          if not pid.lower().startswith("ludeon.") and pid.lower() != OURS]
print("ludeon (core + dlc)   %d" % len(dlc))
print("other mods            %d" % len(others))

no_id = [pid for pid in others
         if pid.lower() in catalogue and not catalogue[pid.lower()]["published"]]
print("other mods with no Workshop id  %d" % len(no_id))
for pid in no_id:
    print("  LOCAL OR UNPUBLISHED  %-44s %s" % (pid, catalogue[pid.lower()]["name"]))

if missing:
    print("\nREFUSING: every active mod must resolve to a folder before a dependency block is "
          "generated. A dependency naming a packageId with no displayName is a row RimSort "
          "cannot explain to the player.")
    sys.exit(1)
print("\nEVERY ACTIVE MOD RESOLVED")
