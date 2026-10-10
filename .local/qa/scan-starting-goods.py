# -*- coding: utf-8 -*-
"""Tally every thing on the live player map and diff it against what the start granted.

Owner, 2026-10-02: *"im not correctly starting weith my set up prepare carfully goods and the
scenerios starting good... my preparecarfully mod food did not appear and the starting scenerio
supplies of food did not appear and should start scenerio with survival meals not simple meals
and should be like 100 to start besides whats set in prepare carfully so check the current game
and whats on the map versus what they were suppose to start with verses how to fix it properly"*

So this answers the measurable half: WHAT IS ACTUALLY ON THE MAP. It tallies every thing in a
band around the colonists and prints the counts, so the scenario's `ScenPart_StartingThing_Defined`
list can be diffed against reality instead of assumed.

**Read-only.** It shells the allowlisted read client, which is the only thing in this repository
permitted to touch a process the owner started, and that client only ever reads.

Tiles are 16x16. The wide scan truncates: the client caps evidence size, so whole tiles' cells get
dropped and two runs disagree about what the map contains. A scan that silently loses rooms is
worse than a slow one -- that is recorded in `scan-facility.py` and is not re-learned here.
"""

import collections
import glob
import io
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT = os.path.join(REPO, "tools", "qa", "rimbridge_readonly.py")
LOG = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow",
                   "Ludeon Studios", "RimWorld by Ludeon Studios", "Player.log")
OUTDIR = os.path.join(REPO, ".local", "qa", "live-goods")

PID = sys.argv[1] if len(sys.argv) > 1 else None
if not PID:
    print("usage: scan-starting-goods.py <rimworld pid> [x0 z0 x1 z1]")
    raise SystemExit(1)

if len(sys.argv) >= 6:
    X0, Z0, X1, Z1 = (int(value) for value in sys.argv[2:6])
else:
    # The colonists stand at roughly (147-150, 151). A Store shop is 50x50 offset onto the
    # player's own map, so a 96-cell band around them covers the shop and its surroundings.
    X0, Z0, X1, Z1 = 100, 104, 196, 200

if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)
for stale in glob.glob(os.path.join(OUTDIR, "*.json")):
    os.remove(stale)

RECTS = [(x, z, 16, 16)
         for x in range(X0, X1, 16)
         for z in range(Z0, Z1, 16)]

# Terrain-ish noise. Everything else is reported, because the question is what IS there.
SKIP_PREFIX = ("Plant_", "Filth_", "Chunk", "Mote_")

tally = collections.Counter()
stacks = collections.defaultdict(list)
cells_read = 0
failed = []

print("scanning %d tiles over x %d-%d, z %d-%d" % (len(RECTS), X0, X1, Z0, Z1))
for x, z, width, height in RECTS:
    out = os.path.join(OUTDIR, "scan-%d-%d.json" % (x, z))
    code = subprocess.call(
        [sys.executable, CLIENT, "--pid", PID, "--log", LOG, "--output", out,
         "--connect", "--select", "ping", "--rect", "%d,%d,%d,%d" % (x, z, width, height)],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if not os.path.isfile(out):
        failed.append((x, z, code))
        continue
    data = json.load(io.open(out, encoding="utf-8"))
    for call in data.get("calls", []):
        if call.get("tool") != "rimworld/get_cells_info":
            continue
        for cell in (call.get("result") or {}).get("cells") or []:
            cells_read += 1
            for thing in cell.get("things") or []:
                name = thing.get("defName") or thing.get("def") or "?"
                if name.startswith(SKIP_PREFIX):
                    continue
                count = thing.get("stackCount") or 1
                tally[name] += count
                stacks[name].append((cell.get("x"), cell.get("z"), count))

lines = []
lines.append(u"cells read: %d   tiles failed: %d" % (cells_read, len(failed)))
for x, z, code in failed:
    lines.append(u"  tile %d,%d exit %d" % (x, z, code))
lines.append(u"")
lines.append(u"%-34s %8s %6s" % ("DEF", "TOTAL", "STACKS"))
lines.append(u"-" * 52)
for name, total in tally.most_common():
    lines.append(u"%-34s %8d %6d" % (name, total, len(stacks[name])))

lines.append(u"")
lines.append(u"FOOD AND MEALS SPECIFICALLY")
lines.append(u"-" * 52)
food = [name for name in tally
        if "Meal" in name or "Food" in name or name in ("Pemmican", "Kibble",
                                                        "RawPotatoes", "RawRice",
                                                        "RawCorn", "RawBerries",
                                                        "InsectJelly", "Chocolate",
                                                        "Milk", "EggChickenUnfertilized")]
if not food:
    lines.append(u"NONE. No meal or food item of any kind is on this map.")
else:
    for name in sorted(food):
        lines.append(u"%-34s %8d  at %s" % (name, tally[name], stacks[name][:6]))

path = os.path.join(REPO, ".local", "qa", "live-goods-report.txt")
io.open(path, "w", encoding="utf-8", newline="").write(u"\n".join(lines))
print(u"\n".join(lines).encode("ascii", "replace").decode("ascii"))
print()
print("report: %s" % path)
