# -*- coding: utf-8 -*-
"""Find genuinely free interior cells for the pre-placed glow pods.

`GenStep_Headquarters` **throws** when a planned building cell is out of bounds or already holds
an edifice, so a wrong cell is a hard crash at map generation rather than a cosmetic slip. That
makes eyeballing coordinates off a diff the wrong method: this computes the free set.

A cell is usable when it is
  * inside one of the start's roofed interior rooms, **excluding the room's perimeter** (walls are
    generated on the room edge, so the border ring is never placeable),
  * not a door cell, a conduit cell, the stock cell or the arrival cell,
  * not already occupied by a planned building.

Prints candidates per start. Nothing is written; the caller decides which to take.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                    "RimroomsStartDefs", "RR_Starts.xml")

text = io.open(PATH, encoding="utf-8").read()


def block(start_def, tag):
    body = re.search(r"<defName>%s</defName>(.*?)</RimroomsAsyncIndustries\.Scenario\."
                     r"RimroomsStartDef>" % re.escape(start_def), text, re.S)
    if not body:
        return ""
    inner = re.search(r"<%s>(.*?)</%s>" % (tag, tag), body.group(1), re.S)
    return inner.group(1) if inner else ""


def cells(raw):
    return set((int(a), int(b)) for a, b in re.findall(r"\((\-?\d+),\s*\d+,\s*(\-?\d+)\)", raw))


def single_cell(start_def, tag):
    body = re.search(r"<defName>%s</defName>(.*?)</RimroomsAsyncIndustries\.Scenario\."
                     r"RimroomsStartDef>" % re.escape(start_def), text, re.S)
    if not body:
        return set()
    found = re.search(r"<%s>\((\-?\d+),\s*\d+,\s*(\-?\d+)\)</%s>" % (tag, tag), body.group(1))
    return {(int(found.group(1)), int(found.group(2)))} if found else set()


def interiors(start_def):
    """Roofed rooms, perimeter excluded. The largest room is the outer compound, skipped."""
    rooms = []
    for entry in re.findall(r"<li>(.*?)</li>", block(start_def, "rooms"), re.S):
        def field(name, default=None):
            found = re.search(r"<%s>([^<]*)</%s>" % (name, name), entry)
            return found.group(1) if found else default
        if (field("roofed", "true") or "true").lower() != "true":
            continue
        rooms.append((int(field("x")), int(field("z")),
                      int(field("width")), int(field("height"))))
    usable = set()
    for x, z, w, h in rooms:
        for cx in range(x + 1, x + w - 1):
            for cz in range(z + 1, z + h - 1):
                usable.add((cx, cz))
    return usable, rooms


for start_def, wanted in (("RR_AsyncIndustriesStart", 8), ("RR_FurnitureStoreStart", 3)):
    usable, rooms = interiors(start_def)
    taken = cells(block(start_def, "buildings"))
    taken |= cells(block(start_def, "doors"))
    taken |= cells(block(start_def, "conduits"))
    taken |= single_cell(start_def, "stockCell")
    taken |= single_cell(start_def, "arrivalCell")
    free = sorted(usable - taken)

    print("=" * 78)
    print("%s -- %d roofed rooms, %d interior cells, %d occupied, %d free"
          % (start_def, len(rooms), len(usable), len(taken), len(free)))
    if len(free) < wanted:
        print("  NOT ENOUGH FREE CELLS")
        sys.exit(1)
    # Take a run along one row so the pods sit together on a shelf-like line rather than
    # scattered through the facility looking like clutter.
    best = None
    by_row = {}
    for cx, cz in free:
        by_row.setdefault(cz, []).append(cx)
    for cz in sorted(by_row):
        xs = sorted(by_row[cz])
        run = [xs[0]]
        for value in xs[1:]:
            if value == run[-1] + 1:
                run.append(value)
            else:
                if len(run) >= wanted and best is None:
                    best = (cz, run[:wanted])
                run = [value]
        if len(run) >= wanted and best is None:
            best = (cz, run[:wanted])
        if best:
            break
    if best is None:
        print("  no contiguous run of %d; taking the first %d free cells" % (wanted, wanted))
        chosen = free[:wanted]
    else:
        chosen = [(cx, best[0]) for cx in best[1]]
    print("  chosen %d:" % wanted)
    for cx, cz in chosen:
        print("      <li><thing>GlowPod</thing><cell>(%d, 0, %d)</cell></li>" % (cx, cz))
