"""Left-click a map cell with the real mouse, mapping cell -> pixel from the live camera bounds.
    python .local/qa/click-cell.py X Z        (jumps the camera there first)
Right-clicks first to drop any live designator (a live designator turns the left-click into a build
order), then left-clicks to select. Both clicks go through game-click.py, so they only ever land
on RimWorld when it is the foreground window and the window under the point.
The bridge's click_cell does not select buildings or zones.
"""
import json, subprocess, sys
BR = ".local/qa/bridge.py"
def call(tool, args):
    o = subprocess.run([sys.executable, BR, "call", tool, json.dumps(args)], capture_output=True, text=True).stdout
    return json.loads(o[o.find("{"):])
def find(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = find(v, k)
            if r is not None: return r
    return None
x, z = int(sys.argv[1]), int(sys.argv[2])
# Clear the selection FIRST: with a pawn selected, the designator-dropping right-click below is a
# move order for that pawn (it sent Gee walking, 2026-10-08).
call("rimworld/clear_selection", {})
call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
cam = call("rimworld/get_camera_state", {})
x0, x1, z0, z1 = (find(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
# eyes frame: 1600 wide, height in proportion to the client (3840x2054 -> 856)
FW, FH = 1600, 856
px = int((x - x0 + 0.5) * FW / (x1 - x0 + 1))
py = int((z1 - z + 0.5) * FH / (z1 - z0 + 1))
for extra in (["--right"], []):
    r = subprocess.run([sys.executable, ".local/qa/game-click.py", str(px), str(py)] + extra, capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stdout + r.stderr)
print("clicked cell", x, z, "at frame", px, py)
