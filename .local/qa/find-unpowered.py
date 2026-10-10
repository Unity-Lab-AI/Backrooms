"""Find the game's flashing 'no power' bolt over buildings, and name the cells.

Pans the camera across a rectangle at a fixed zoom, screenshots each view, finds the bolt's
orange-yellow pixels clustered into an icon, and converts each to a map cell from the camera's own
viewRect. Prints the cell and what stands on it.

    python .local/qa/find-unpowered.py x0 z0 x1 z1
The bolt flashes, so each view is shot twice and the hits merged.
"""
import json, subprocess, sys, time, glob, os
from PIL import Image

BR = ".local/qa/bridge.py"


def call(tool, args):
    out = subprocess.run([sys.executable, BR, "call", tool, json.dumps(args)],
                         capture_output=True, text=True).stdout
    return json.loads(out[out.find("{"):]) if "{" in out else {}


def shot():
    subprocess.run([sys.executable, ".local/qa/eyes.py"], capture_output=True)
    return max(glob.glob(".local/qa/evidence/eyes/RRQA-eyes-*.png"), key=os.path.getmtime)


def bolts(path):
    im = Image.open(path).convert("RGB")
    px = im.load()
    hits = []
    for y in range(70, 860, 2):
        for x in range(0, 1340, 2):
            if x < 370 and y > 700:      # inspect pane
                continue
            r, g, b = px[x, y]
            if r > 215 and 130 < g < 205 and b < 80 and r - g > 30:
                hits.append((x, y))
    clusters = []
    for p in hits:
        for c in clusters:
            if abs(c[0] - p[0]) < 14 and abs(c[1] - p[1]) < 14:
                c[2] += 1
                break
        else:
            clusters.append([p[0], p[1], 1])
    return [(c[0], c[1]) for c in clusters if c[2] >= 4]


def main():
    x0, z0, x1, z1 = map(int, sys.argv[1:5])
    call("rimworld/clear_selection", {})
    call("rimworld/set_camera_zoom", {"rootSize": 14})
    found = {}
    for cz in range(z0 + 10, z1 + 10, 20):
        for cx in range(x0 + 18, x1 + 18, 36):
            call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
            time.sleep(0.5)
            rect = call("rimworld/get_camera_state", {}).get("viewRect") or {}
            if not rect:
                continue
            for _ in range(2):
                for (sx, sy) in bolts(shot()):
                    x = rect["minX"] + sx / 1600.0 * rect["width"]
                    z = rect["maxZ"] + 1 - sy / 900.0 * rect["height"]
                    cell = (int(x), int(z))
                    if x0 <= cell[0] <= x1 and z0 <= cell[1] <= z1:
                        found[cell] = True
                time.sleep(0.35)
    for cell in sorted(found):
        info = call("rimworld/get_cell_info", {"x": cell[0], "z": cell[1]})
        things = [t.get("label") for t in (info.get("things") or [])
                  if t.get("label") and "onduit" not in t.get("label")]
        print(cell, things)


if __name__ == "__main__":
    main()
