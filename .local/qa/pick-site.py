#!/usr/bin/env python3
"""Roll Select random site until the Terrain pane says mountains in a forest or a jungle.

Owner, 2026-10-07, verbatim: *"when choosing a map tile u pic on that has mountains(the rock
areas on map) in forest area and jungle areas the light green and green, terrain tab on left
tells u all this when u highlight via select the tiles"*.

The globe itself cannot be read through the bridge, but the Terrain pane that opens beside a
selected tile is an ordinary window, and its labels are. So the tile is chosen the way the owner
chooses it -- by reading the pane -- with the random button doing the pointing.

Usage:
    python .local/qa/pick-site.py            # up to 80 rolls
    python .local/qa/pick-site.py 150
"""
import importlib.util
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rr_start", os.path.join(HERE, "start-scenario.py"))
_start = importlib.util.module_from_spec(_spec)
sys.modules["rr_start"] = _start
_spec.loader.exec_module(_start)

RANDOM_SITE = ("733", "871")
BIOMES = ("temperate forest", "tropical rainforest", "boreal forest", "tropical swamp",
          "temperate swamp")
HILLS = ("large hills", "mountainous")


def pane_labels(session):
    found = _start.elements(session)
    return [label.strip() for _t, kind, label, _a in found if kind == "label" and label]


def main(argv):
    rolls = int(argv[0]) if argv else 80
    session = _start.Session()
    try:
        for roll in range(1, rolls + 1):
            subprocess.run([sys.executable, os.path.join(HERE, "hands.py"), RANDOM_SITE[0], RANDOM_SITE[1]],
                           capture_output=True)
            time.sleep(1.6)
            labels = pane_labels(session)
            lowered = [label.lower() for label in labels]
            biome = next((label for label in labels if label.lower() in BIOMES), None)
            hills = next((label for label in labels if label.lower() in HILLS), None)
            summary = [label for label in labels if label.lower() in BIOMES + HILLS
                       or label.lower() in ("flat", "small hills", "desert", "arid shrubland",
                                            "grassland", "tundra", "ice sheet", "extreme desert",
                                            "sea ice", "cold bog")]
            print("roll %3d: %s" % (roll, ", ".join(summary) or "(no terrain pane read)"))
            if biome and hills:
                print("ACCEPTED: %s, %s" % (biome, hills))
                return 0
        print("no acceptable tile in %d rolls" % rolls)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
