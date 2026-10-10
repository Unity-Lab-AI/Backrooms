#!/usr/bin/env python3
"""Decode a save's compressed rock grid per map, count the ore, and draw the layout.

Owner, 2026-10-07: no mineable veins between rooms, hallways *"all rock mountain"*, the corridor
network *"one massive room"*. **Natural rock is `saveCompressible`**, so it is not a `<thing>` in
the save at all -- it is one ushort per cell in `compressedThingMapDeflate`, the def's short
hash. `measure-coordinate.py` could not see a single rock for that reason, and neither can any
checker here. This decodes the grid, so the ore is counted and the carve can be looked at.

The short hash is Core's `ShortHashGiver`: `GenText.StableStringHash(defName)` reduced to a
ushort, bumped on collision in load order. The collision bump cannot be replayed here, so every
def name from the installed game and profile is hashed and a grid value is matched exactly, or
to a name whose hash is 1..3 below it (a probable bump), or reported unknown.

Read-only. Writes PNGs beside the eyes captures.

Usage:
    python .local/qa/render-coordinate.py "RRQA-handover-owner-colony-tick630304-4maps"
"""
import base64
import glob
import io
import os
import re
import sys
import zlib
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

SAVES = os.path.expanduser(
    "~/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves")
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "evidence", "eyes")
POS = re.compile(r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)")
DEFNAME = re.compile(r"<defName>([^<]+)</defName>")
SIZE = re.compile(r"\((\d+),\s*(\d+),\s*(\d+)\)")

OVERLAY = {"Wall": (92, 64, 40), "Door": (255, 140, 0), "Autodoor": (255, 140, 0),
           "WallLamp": (255, 255, 0), "StandingLamp": (255, 80, 255), "PlantPot": (0, 200, 0),
           "Column": (120, 90, 60)}


def stable_string_hash(text):
    """`GenText.StableStringHash`, with C#'s wrapping int arithmetic."""
    num = 23
    for ch in text:
        num = (num * 31 + ord(ch)) & 0xFFFFFFFF
    if num >= 0x80000000:
        num -= 0x100000000
    return num


def short_hash(text, modulus):
    h = stable_string_hash(text)
    # C# `%` truncates toward zero and keeps the sign; the cast to ushort then wraps.
    rem = h - modulus * int(h / modulus)
    return rem & 0xFFFF


def all_def_names():
    names = set()
    roots = [os.path.join(GAME, "Data"), os.path.join(GAME, "Mods"), WORKSHOP]
    for root in roots:
        for path in glob.glob(os.path.join(root, "**", "Defs", "**", "*.xml"), recursive=True):
            try:
                text = io.open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for name in DEFNAME.findall(text):
                names.add(name.strip())
    return names


def inflate(text):
    raw = base64.b64decode("".join(text.split()))
    for wbits in (-15, 15, 31):
        try:
            return zlib.decompress(raw, wbits)
        except zlib.error:
            continue
    raise SystemExit("could not inflate the thing grid")


def parse_pos(text):
    m = POS.match((text or "").strip())
    return (int(m.group(1)), int(m.group(3))) if m else None


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    path = os.path.join(SAVES, argv[0] + ".rws")
    names = all_def_names()
    print("def names hashed: %d" % len(names))

    maps = []          # (size, grid_text)
    overlay = defaultdict(lambda: defaultdict(list))
    stack = []
    for event, node in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            stack.append(node.tag)
            continue
        stack.pop()
        parent = stack[-1] if stack else ""
        # A save writes a list as `<li>` elements, so a map is an `<li>` whose parent is `<maps>`.
        if node.tag == "li" and parent == "maps":
            size = node.findtext("mapInfo/size") or ""
            grid = node.findtext("compressedThingMapDeflate") or ""
            maps.append((size, grid))
            node.clear()
            continue
        if node.tag == "thing":
            definition = node.findtext("def") or ""
            if definition in OVERLAY:
                map_text = (node.findtext("map") or "").strip()
                pos = parse_pos(node.findtext("pos"))
                if map_text.isdigit() and pos:
                    overlay[int(map_text)][definition].append(pos)
            node.clear()

    for index, (size_text, grid_text) in enumerate(maps):
        m = SIZE.match(size_text.strip())
        if not m or not grid_text.strip():
            print("map %d: no grid" % index)
            continue
        width, height = int(m.group(1)), int(m.group(3))
        data = inflate(grid_text)
        cells = len(data) // 2
        values = [data[2 * i] | (data[2 * i + 1] << 8) for i in range(cells)]
        counts = Counter(values)
        nonzero = [v for v in counts if v != 0]

        # Pick the modulus that explains the most grid values exactly.
        best = None
        for modulus in (65535, 65536):
            table = defaultdict(list)
            for name in names:
                table[short_hash(name, modulus)].append(name)
            exact = sum(1 for v in nonzero if v in table)
            if best is None or exact > best[0]:
                best = (exact, modulus, table)
        exact, modulus, table = best

        def resolve(value):
            if value in table:
                return "/".join(sorted(table[value])[:2])
            for bump in (1, 2, 3):
                if value - bump in table:
                    return "/".join(sorted(table[value - bump])[:2]) + "(+%d)" % bump
            return "?%d" % value

        print("")
        print("=== map %d  %dx%d  cells=%d  grid values=%d  modulus=%d  exact=%d"
              % (index, width, height, cells, len(nonzero), modulus, exact))
        floor = counts.get(0, 0)
        print("  empty (floor/wall/door) cells : %6d  (%.1f%%)" % (floor, 100.0 * floor / cells))
        ore_total = 0
        for value, count in counts.most_common(40):
            if value == 0:
                continue
            name = resolve(value)
            if name.startswith("Mineable") or "/Mineable" in name:
                ore_total += count
            print("  %-44s %6d" % (name, count))
        print("  ORE CELLS (names starting Mineable): %d" % ore_total)

        try:
            from PIL import Image
        except ImportError:
            print("  (no Pillow; no picture)")
            continue
        scale = 3
        image = Image.new("RGB", (width * scale, height * scale), (230, 230, 220))
        px = image.load()
        palette = {}
        for value in nonzero:
            name = resolve(value)
            if "Mineable" in name:
                colour = (0, 160, 255)
                if "Gold" in name: colour = (255, 215, 0)
                elif "Steel" in name: colour = (90, 150, 255)
                elif "Plasteel" in name: colour = (255, 255, 255)
                elif "Jade" in name: colour = (0, 255, 120)
                elif "Uranium" in name: colour = (100, 255, 0)
                elif "Silver" in name: colour = (200, 200, 255)
                elif "Component" in name: colour = (255, 120, 120)
            elif name.startswith("?"):
                colour = (255, 0, 0)
            else:
                shade = 40 + (value % 5) * 8
                colour = (shade, shade, shade + 6)
            palette[value] = colour
        for z in range(height):
            for x in range(width):
                value = values[z * width + x]
                if value == 0:
                    continue
                colour = palette[value]
                for dx in range(scale):
                    for dz in range(scale):
                        px[x * scale + dx, (height - 1 - z) * scale + dz] = colour
        for definition, positions in overlay.get(index, {}).items():
            colour = OVERLAY[definition]
            for (x, z) in positions:
                if 0 <= x < width and 0 <= z < height:
                    for dx in range(scale):
                        for dz in range(scale):
                            px[x * scale + dx, (height - 1 - z) * scale + dz] = colour
        if not os.path.isdir(OUT):
            os.makedirs(OUT)
        out = os.path.join(OUT, "RRQA-layout-map%d.png" % index)
        image.save(out)
        print("  picture: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
