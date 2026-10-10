# -*- coding: utf-8 -*-
"""Read the owner's built facility off the running game and report it as a layout.

Owner, 2026-10-01: *"and check where i had to move stuff and where i had to add a door and add
power conduit and fix the spawn to have current lsaayout of devices generators batteries and the
like"*.

So this reads what they actually built -- not what the start authored -- and prints it as a device
inventory with coordinates, ready to diff against `build-async-facility.py`.

**Read-only.** It shells the existing allowlisted read client once per rectangle, because that
client is the one thing in this repository permitted to touch a process the owner started, and it
only ever reads.

The camera told us where to look: `viewRect` was x 118-183, z 133-170, so the scan covers that
with a margin. Rectangles are capped at 1024 cells by the client itself.
"""
import glob
import io
import json
import os
import subprocess
import sys
import collections

# This file lives in .local/qa/, so the repository root is THREE levels up. The first
# version used two and wrote every output into a path that does not exist, which the
# client reported as exit 2 and the script mis-read as "no evidence".
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT = os.path.join(REPO, "tools", "qa", "rimbridge_readonly.py")
LOG = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow",
                   "Ludeon Studios", "RimWorld by Ludeon Studios", "Player.log")
OUTDIR = os.path.join(REPO, ".local", "qa", "live")

PID = sys.argv[1] if len(sys.argv) > 1 else None
if not PID:
    print("usage: scan-facility.py <rimworld pid>")
    raise SystemExit(1)

# The camera's own view rect, with a margin, in 1024-cell tiles.
# **16x16 tiles, not 32x32.** The wide scan truncated: the client caps evidence size, so whole
# tiles' cells were dropped and two runs disagreed about what the facility contained. 256-cell
# tiles stay well inside the cap, and a scan that silently loses rooms is worse than a slow one.
RECTS = []
for _rx in range(124, 184, 16):
    for _rz in range(124, 180, 16):
        RECTS.append((_rx, _rz, 16, 16))

# Everything that is not scenery. Plants, filth, rock and chunks are noise here.
SKIP_PREFIX = ("Plant_", "Filth_", "Chunk", "Mote_")
SKIP_EXACT = {"Granite", "Sandstone", "Limestone", "Marble", "Slate", "Steel", "WoodLog"}

found = collections.defaultdict(list)
cells_read = 0

for index, (x, z, w, h) in enumerate(RECTS):
    out = os.path.join(OUTDIR, "scan-%d-%d.json" % (x, z))
    code = subprocess.call(
        [sys.executable, CLIENT, "--pid", PID, "--log", LOG, "--output", out,
         "--connect", "--select", "ping", "--rect", "%d,%d,%d,%d" % (x, z, w, h)],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if not os.path.isfile(out):
        print("  rect %d,%d: no evidence written (exit %d)" % (x, z, code))
        continue
    data = json.load(io.open(out, encoding="utf-8"))
    for call in data.get("calls", []):
        if call.get("tool") != "rimworld/get_cells_info":
            continue
        result = call.get("result") or {}
        cells = result.get("cells") or []
        cells_read += len(cells)
        for cell in cells:
            pos = cell.get("position") or cell.get("cell") or {}
            cx = pos.get("x", cell.get("x"))
            cz = pos.get("z", cell.get("z"))
            for thing in (cell.get("things") or []):
                name = thing.get("defName") or thing.get("DefName") or ""
                if not name or name.startswith(SKIP_PREFIX) or name in SKIP_EXACT:
                    continue
                found[name].append((cx, cz))

print("")
print("cells read: %d" % cells_read)
print("distinct non-scenery defs: %d" % len(found))
print("")

INTEREST = ("Generator", "Battery", "Conduit", "Door", "CommsConsole", "Table",
            "Bench", "Smithy", "Stove", "Shelf", "Bed", "Lamp", "Heater", "GlowPod",
            "Cooler", "Vent", "Switch", "Sun", "Turret", "Wall")


def interesting(name):
    return any(word.lower() in name.lower() for word in INTEREST)


print("=== POWER AND DOORS (what the owner said they had to add) ===")
for name in sorted(found):
    if not any(w in name for w in ("Generator", "Battery", "Conduit", "Door", "Switch")):
        continue
    spots = sorted(found[name])
    print("  %-30s %3d   %s" % (name, len(spots),
                                " ".join("(%s,%s)" % s for s in spots[:14])))

print("")
print("=== EVERY OTHER DEVICE ===")
for name in sorted(found):
    if any(w in name for w in ("Generator", "Battery", "Conduit", "Door", "Switch")):
        continue
    if name.startswith("Wall") or name in ("Granite",):
        continue
    spots = sorted(found[name])
    print("  %-30s %3d   %s" % (name, len(spots),
                                " ".join("(%s,%s)" % s for s in spots[:10])))

payload = dict((name, sorted(spots)) for name, spots in found.items())
summary = os.path.join(OUTDIR, "facility-layout.json")
io.open(summary, "w", encoding="utf-8", newline="").write(
    json.dumps(payload, indent=1, sort_keys=True))
print("")
print("full layout written to %s" % os.path.relpath(summary, REPO))
