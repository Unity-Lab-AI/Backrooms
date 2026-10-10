"""Install a minified thing: python .local/qa/install.py SRC_X SRC_Z "title text" DST_X DST_Z
Cycles clicks on the source cell until the inspect text contains the title, clicks the Install (or
Reinstall at...) gizmo icon (20 UI units above its label), then the destination cell in the same view."""
import importlib.util, os, re, subprocess, sys, time
sx, sz, title, dx, dz = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", ".local/qa/empire.py"); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
def f(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = f(v, k)
            if r is not None: return r
e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection")
# camera on the source only: the destination is placed with click_cell, which needs no camera
e.call("rimworld/jump_camera_to_cell", {"x": sx, "z": sz}); time.sleep(0.5)
cam = e.call("rimworld/get_camera_state"); x0, x1, z0, z1 = (f(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
px = lambda x, z: (int((x - x0 + 0.5) * 1600 / (x1 - x0 + 1)), int((z1 - z + 0.5) * 856 / (z1 - z0 + 1)))
a = px(sx, sz)
for _ in range(8):
    subprocess.run([sys.executable, ".local/qa/game-click.py", str(a[0]), str(a[1])], capture_output=True); time.sleep(0.4)
    if any(title in e.plain(x["label"]) for x in e.layout()): break
else: sys.exit("could not select " + title)
g = e.find(e.layout(), lambda t: t == "Install" or t.startswith("Reinstall"))
r = g["screenRect"]
subprocess.run([sys.executable, ".local/qa/game-click.py", str(int((r["x"] + r["width"] / 2) * 1600 / 1920)), str(int((r["y"] - 20) * 1600 / 1920))], capture_output=True); time.sleep(0.6)
# no keyboard panning: system-wide W/A/S/D typed into the owner's own messages (2026-10-09, "stop fighting
# me"). The camera was framed on source + destination before selecting, so both are already on screen.
# the camera glides after a keyboard pan: wait until two reads agree, then aim (clicking on the first read
# put generators a cell off, 2026-10-09)
prev = None
for _ in range(10):
    time.sleep(0.4)
    cam = e.call("rimworld/get_camera_state"); cur = tuple(f(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
    if cur == prev: break
    prev = cur
x0, x1, z0, z1 = cur
# place with the game's own click on the exact cell (bridge click_cell): pixel aim drifted by a cell or two
e.call("rimworld/click_cell", {"x": dx, "z": dz}); time.sleep(0.6)
e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection")
o = subprocess.run([sys.executable, ".local/qa/find-things.py", "Blueprint_Install", str(dx - 3), str(dz - 3), str(dx + 4), str(dz + 4)], capture_output=True, text=True, env=dict(os.environ, ALL="1")).stdout
print(o.strip() or "no blueprint")
import re as _re
cells = [tuple(map(int, m)) for m in _re.findall(r"\((\d+), (\d+)\)", o)]
# exact = a blueprint whose lower-left corner is the destination (2x2 things anchor bottom-left here)
print("EXACT" if (dx, dz) in cells and not any(c[0] < dx and abs(c[1] - dz) <= 1 for c in cells) else "OFF")
