"""Select a pawn and right-click a cell, then click the float-menu entry starting with a prefix.
python .local/qa/prio.py PAWN_ID X Z "Prioritize"   (no prefix -> list the entries)"""
import importlib.util, subprocess, sys, time
pid, x, z = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); pre = sys.argv[4] if len(sys.argv) > 4 else None
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", ".local/qa/empire.py"); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
def f(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = f(v, k)
            if r is not None: return r
e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection"); e.call("rimworld/select_pawn", {"pawnId": pid})
e.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
cam = e.call("rimworld/get_camera_state")
x0, x1, z0, z1 = (f(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
px = int((x - x0 + 0.5) * 1600 / (x1 - x0 + 1)); py = int((z1 - z + 0.5) * 856 / (z1 - z0 + 1))
subprocess.run([sys.executable, ".local/qa/game-click.py", str(px), str(py), "--right"], capture_output=True); time.sleep(0.6)
els = e.layout()
opts = [el for el in els if el.get("screenRect") and not e.plain(el["label"]).startswith("Beauty")]
if not pre:
    for el in opts: print(e.plain(el["label"])[:100])
else:
    el = next((el for el in opts if e.plain(el["label"]).startswith(pre)), None)
    print(("clicked: " + e.plain(el["label"])) if el else "no entry " + pre)
    if el: e.click_el(el)
