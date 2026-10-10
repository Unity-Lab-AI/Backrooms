#!/usr/bin/env python3
"""Every def that owns a texture, and what in the game actually puts it in front of a player.

Owner, 2026-10-07: *"check all the assets work, opus did it"*. The checkers say every texture
resolves and every def has a reference somewhere. **That is not the same as an asset working.**
`RR_SiteFluorescent` has a def, three facings, and a wall-attachment comp -- and nothing in the
generator names it, so three coordinates hold 3,934 Core wall lamps and none of ours.

So this asks a narrower question per def: is it NAMED by C# (spawned or resolved), or REACHABLE
by a player through XML alone (a recipe makes it, a scenario starts with it, a trader sells it,
an archetype or facility lists it, or it is buildable from the Architect menu)? A def with a
texture and neither is shipped art nobody can see. Read-only.

Usage:
    python .local/qa/audit-asset-consumers.py
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACKAGE = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
SRC = os.path.join(REPO, "src")
TEXTURE_TAGS = ("texPath", "uiIconPath", "iconPath")


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def main():
    cs = {}
    for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        cs[os.path.relpath(path, REPO)] = read(path)
    xml_files = {}
    for path in glob.glob(os.path.join(PACKAGE, "**", "*.xml"), recursive=True):
        xml_files[os.path.relpath(path, REPO)] = read(path)

    # Every def in the package with a texture of its own.
    owners = []
    for rel, text in xml_files.items():
        if os.sep + "Defs" + os.sep not in rel and "/Defs/" not in rel.replace(os.sep, "/"):
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError as error:
            print("PARSE ERROR %s: %s" % (rel, error))
            continue
        for node in root:
            name = (node.findtext("defName") or "").strip()
            if not name:
                continue
            textures = []
            for element in node.iter():
                if element.tag in TEXTURE_TAGS and (element.text or "").strip():
                    textures.append(element.text.strip())
            if not textures:
                continue
            buildable = node.find("designationCategory") is not None
            owners.append((node.tag, name, rel, textures, buildable))

    print("defs owning a texture: %d" % len(owners))
    print("")
    bad = 0
    for kind, name, rel, textures, buildable in sorted(owners, key=lambda o: o[1]):
        pattern = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(name) + r'(?![A-Za-z0-9_])')
        cs_hits = [path for path, text in cs.items() if pattern.search(text)]
        xml_hits = []
        for other, text in xml_files.items():
            if other == rel:
                continue
            if pattern.search(text):
                xml_hits.append(other)
        # Only an XML hit that is a real path to a player counts: a recipe, scenario, trader,
        # archetype, facility, catalog or start def. A patch that merely names it does not.
        reachable = [h for h in xml_hits if re.search(
            r"Recipe|Scenario|Trader|Archetype|Facility|Catalog|Start|SupplyTier|Request|"
            r"FixtureTell|Inhabitant|PawnKind|Equipment|Procurement", h)]
        verdict = "OK"
        if not cs_hits and not reachable and not buildable:
            verdict = "NO CONSUMER"
            bad += 1
        print("%-12s %-32s %s" % (verdict, name, kind))
        print("             def: %s" % rel.replace(os.sep, "/"))
        for texture in textures[:3]:
            print("             tex: %s" % texture)
        if buildable:
            print("             buildable from the Architect menu")
        for hit in cs_hits[:4]:
            print("             C#:  %s" % hit.replace(os.sep, "/"))
        for hit in reachable[:4]:
            print("             XML: %s" % hit.replace(os.sep, "/"))
        if not cs_hits and not reachable and xml_hits:
            for hit in xml_hits[:3]:
                print("             named only by: %s" % hit.replace(os.sep, "/"))
    print("")
    print("%d of %d textured defs have nothing that puts them in front of a player" % (bad, len(owners)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
