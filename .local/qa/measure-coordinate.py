#!/usr/bin/env python3
"""Count what the generator actually built, out of a save, per map.

Owner, 2026-10-07, after playing: lights *"in piles and piles"*, hallways *"all rock mountain"*,
no mineable veins between rooms, and the corridor network *"one massive room"*. Every one of
those is a claim about a generated map, and no instrument here reads one -- the checkers read
source and defs. This reads the save the owner's own colony wrote and reports the figures, so a
fix is aimed at a measurement rather than a description.

Read-only. Streams the XML, because a 52 MB save parsed whole is a gigabyte of tree.

Usage:
    python .local/qa/measure-coordinate.py "RRQA-handover-owner-colony-tick630304-4maps"
"""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

SAVES = os.path.expanduser(
    "~/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves")
POS = re.compile(r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)")

WATCHED_PREFIXES = ("WallLamp", "StandingLamp", "PlantPot", "Mineable", "Wall", "Door",
                    "Autodoor", "Shelf", "Stool", "Column", "Pillar")


def parse_pos(text):
    m = POS.match((text or "").strip())
    return (int(m.group(1)), int(m.group(3))) if m else None


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    path = os.path.join(SAVES, argv[0] + ".rws")
    by_map = defaultdict(Counter)
    lamp_cells = defaultdict(list)
    wall_stuff = defaultdict(Counter)
    map_sizes = {}
    real_maps = 0
    stack = []
    coordinates = []

    # Streaming. **A thing carries its own `<map>N</map>` field** -- the first run of this
    # counted every one of those as a map and reported 54,411 of them. So a map is only a
    # `<map>` whose parent is `<maps>`, and a thing is bucketed by the index it names itself.
    for event, node in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            stack.append(node.tag)
            continue
        stack.pop()
        parent = stack[-1] if stack else ""
        if node.tag == "li" and parent == "maps":
            size = node.find("mapInfo/size")
            map_sizes[real_maps] = (size.text or "").strip() if size is not None else "?"
            real_maps += 1
            node.clear()
            continue
        if node.tag == "thing":
            definition = node.findtext("def") or ""
            if definition.startswith(WATCHED_PREFIXES):
                map_text = (node.findtext("map") or "").strip()
                map_index = int(map_text) if map_text.lstrip("-").isdigit() else -1
                by_map[map_index][definition] += 1
                if definition in ("WallLamp", "StandingLamp"):
                    pos = parse_pos(node.findtext("pos"))
                    if pos:
                        lamp_cells[map_index].append(pos)
                if definition == "Wall":
                    wall_stuff[map_index][node.findtext("stuff") or "(none)"] += 1
            node.clear()
            continue
        if node.tag == "rr_coordinates":
            for coordinate in list(node):
                cid = (coordinate.findtext("rr_id") or coordinate.findtext("id") or "")[:36]
                rooms = coordinate.find("rr_rooms")
                if rooms is None:
                    rooms = coordinate.find("rooms")
                room_list = list(rooms) if rooms is not None else []
                link_counts = []
                for room in room_list:
                    links = room.find("rr_links")
                    if links is None:
                        links = room.find("links")
                    link_counts.append(len(list(links)) if links is not None else 0)
                coordinates.append((cid, len(room_list), link_counts))
            node.clear()

    print("maps: %d" % real_maps)
    for index in sorted(by_map):
        print("")
        print("=== map %d  size %s" % (index, map_sizes.get(index, "?")))
        counts = by_map[index]
        for name in sorted(counts, key=lambda n: -counts[n])[:24]:
            print("  %-34s %6d" % (name, counts[name]))
        if wall_stuff[index]:
            print("  Wall by stuff: %s" % dict(wall_stuff[index].most_common(8)))
        cells = lamp_cells[index]
        if cells:
            cellset = set(cells)
            dup = len(cells) - len(cellset)
            adjacent = 0
            for (x, z) in cellset:
                for dx, dz in ((1, 0), (0, 1)):
                    if (x + dx, z + dz) in cellset:
                        adjacent += 1
            print("  lamps: %d placed, %d on a cell another lamp is on, %d adjacent pairs"
                  % (len(cells), dup, adjacent))
            # The densest 5x5 block of lamps, which is what a pile would be.
            blocks = Counter((x // 5, z // 5) for (x, z) in cells)
            top = blocks.most_common(3)
            print("  densest 5x5 blocks (lamps): %s" % [(b[0][0] * 5, b[0][1] * 5, b[1]) for b in top])

    print("")
    print("=== coordinates: %d" % len(coordinates))
    for cid, room_count, link_counts in coordinates:
        total_links = sum(link_counts)
        print("  %s  rooms=%d  links(total, directed)=%d  per-room max=%d  mean=%.1f"
              % (cid, room_count, total_links, max(link_counts) if link_counts else 0,
                 (float(total_links) / room_count) if room_count else 0.0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
