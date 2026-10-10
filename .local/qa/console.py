"""Gee uses the comms console: python .local/qa/console.py "Call <name prefix>" (no arg lists the options)."""
import importlib.util, subprocess, sys, time
arg = sys.argv[1] if len(sys.argv) > 1 else None
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", ".local/qa/empire.py"); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
def f(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = f(v, k)
            if r is not None: return r
e.call("rimworld/clear_selection"); e.call("rimworld/select_pawn", {"pawnId": "Thing_Human486"})
x, z = 143, 126
e.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
cam = e.call("rimworld/get_camera_state")
x0, x1, z0, z1 = (f(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
px = int((x - x0 + 0.5) * 1600 / (x1 - x0 + 1)); py = int((z1 - z + 0.5) * 856 / (z1 - z0 + 1))
subprocess.run([sys.executable, ".local/qa/game-click.py", str(px), str(py), "--right"], capture_output=True); time.sleep(0.6)
opts = [el for el in e.layout() if e.plain(el["label"]).startswith(("Call", "Not enough"))]
if not arg:
    for el in opts: print(e.plain(el["label"]))
else:
    el = next((el for el in opts if e.plain(el["label"]).startswith(arg)), None)
    print("clicked" if el else "no option", arg)
    if el: e.click_el(el)
