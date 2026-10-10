"""Select the thing on a map cell with a guarded real click (game-click.py), from live camera bounds.
    python .local/qa/select-cell.py X Z"""
import json, re, subprocess, sys
x, z = int(sys.argv[1]), int(sys.argv[2])
def call(t, a):
    return subprocess.run([sys.executable, ".local/qa/bridge.py", "call", t, json.dumps(a)], capture_output=True, text=True).stdout
call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
o = call("rimworld/get_camera_state", {})
g = lambda k: int(re.search('"%s": (-?\d+)' % k, o).group(1))
x0, x1, z0, z1 = g("minX"), g("maxX"), g("minZ"), g("maxZ")
px = (x - x0 + 0.5) * 1600 / (x1 - x0 + 1); import ctypes as _c; from ctypes import wintypes as _w; _u=_c.windll.user32; _g=_u.FindWindowW(None,"RimWorld by Ludeon Studios"); _r=_w.RECT(); _u.GetClientRect(_g,_c.byref(_r)); FH = 1600.0 * _r.bottom / _r.right
py = (z1 - z + 0.5) * FH / (z1 - z0 + 1)
print(subprocess.run([sys.executable, ".local/qa/game-click.py", str(int(px)), str(int(py))], capture_output=True, text=True).stdout.strip())
