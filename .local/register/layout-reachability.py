# -*- coding: utf-8 -*-
"""Flood-fill each start's generated layout and report what the arrival cell can actually reach.

Owner report, 2026-09-30: *"store stare was not the map i chose with the buildings being built
there instead i was stuck in a super micro blocked in area"*.

`GenStep_Headquarters` builds a wall on **every cell of every room rect's perimeter**, then
replaces the wall at each declared door cell with a door. So reachability is decidable from the
def alone, without launching anything: build the wall set, remove the doors, flood from the
arrival cell, and count.

This is the measurement that should have existed before any of these layouts shipped.
"""
import io
import os
import re
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                    "RimroomsStartDefs", "RR_Starts.xml")

text = io.open(PATH, encoding="utf-8").read()


def body(start_def):
    found = re.search(r"<defName>%s</defName>(.*?)</RimroomsAsyncIndustries\.Scenario\."
                      r"RimroomsStartDef>" % re.escape(start_def), text, re.S)
    return found.group(1) if found else ""


def block(start_def, tag):
    found = re.search(r"<%s>(.*?)</%s>" % (tag, tag), body(start_def), re.S)
    return found.group(1) if found else ""


def one(start_def, tag, cast=int):
    found = re.search(r"<%s>([^<]+)</%s>" % (tag, tag), body(start_def))
    return cast(found.group(1)) if found else None


def cell(start_def, tag):
    found = re.search(r"<%s>\((\-?\d+),\s*\d+,\s*(\-?\d+)\)</%s>" % (tag, tag), body(start_def))
    return (int(found.group(1)), int(found.group(2))) if found else None


def cells(raw):
    return set((int(a), int(b)) for a, b in re.findall(r"\((\-?\d+),\s*\d+,\s*(\-?\d+)\)", raw))


for start_def in ("RR_AsyncIndustriesStart", "RR_FurnitureStoreStart", "RR_SoloGroupStart"):
    size = one(start_def, "mapSize") or 60
    arrival = cell(start_def, "arrivalCell")
    doors = cells(block(start_def, "doors"))

    rooms = []
    for entry in re.findall(r"<li>(.*?)</li>", block(start_def, "rooms"), re.S):
        def field(name, default=None):
            got = re.search(r"<%s>([^<]*)</%s>" % (name, name), entry)
            return got.group(1) if got else default
        rooms.append((int(field("x")), int(field("z")),
                      int(field("width")), int(field("height"))))

    # Walls: every perimeter cell of every room rect, exactly as the generator builds them.
    walls = set()
    for x, z, w, h in rooms:
        min_x, min_z, max_x, max_z = x, z, x + w - 1, z + h - 1
        for cx in range(min_x, max_x + 1):
            for cz in range(min_z, max_z + 1):
                if cx in (min_x, max_x) or cz in (min_z, max_z):
                    walls.add((cx, cz))
    walls -= doors

    # Buildings that are edifices block movement too. Only the ones that plausibly do: a wall
    # is the only thing the generator itself places, but planned furniture can block a corridor.
    furniture = set()
    for entry in re.findall(r"<li><thing>([A-Za-z_0-9]+)</thing>(.*?)</li>",
                            block(start_def, "buildings"), re.S):
        name, rest = entry
        got = re.search(r"<cell>\((\-?\d+),\s*\d+,\s*(\-?\d+)\)</cell>", rest)
        if got and name in ("Wall",):
            furniture.add((int(got.group(1)), int(got.group(2))))

    blocked = walls | furniture
    start_cell = arrival
    reachable = set()
    if start_cell and start_cell not in blocked:
        queue = deque([start_cell])
        reachable.add(start_cell)
        while queue:
            cx, cz = queue.popleft()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (cx + dx, cz + dz)
                if not (0 <= nxt[0] < size and 0 <= nxt[1] < size):
                    continue
                if nxt in blocked or nxt in reachable:
                    continue
                reachable.add(nxt)
                queue.append(nxt)

    total_open = size * size - len(blocked)
    print("=" * 78)
    print("%s  map %dx%d" % (start_def, size, size))
    print("  arrival cell      : %s" % (arrival,))
    print("  rooms             : %d" % len(rooms))
    print("  wall cells        : %d" % len(walls))
    print("  doors             : %d" % len(doors))
    print("  open cells on map : %d" % total_open)
    print("  REACHABLE FROM ARRIVAL : %d  (%.1f%% of open map)"
          % (len(reachable), 100.0 * len(reachable) / max(1, total_open)))
    if len(reachable) < 200:
        xs = sorted(c[0] for c in reachable)
        zs = sorted(c[1] for c in reachable)
        print("  *** SEALED *** bounding box x %d..%d  z %d..%d"
              % (xs[0], xs[-1], zs[0], zs[-1]))
    # Which declared rooms can never be entered from the arrival cell?
    for x, z, w, h in rooms:
        interior = set((cx, cz) for cx in range(x + 1, x + w - 1)
                       for cz in range(z + 1, z + h - 1))
        if interior and not (interior & reachable):
            print("  UNREACHABLE ROOM  : x %d..%d z %d..%d" % (x, x + w - 1, z, z + h - 1))
