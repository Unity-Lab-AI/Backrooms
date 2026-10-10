"""Place climate buildings ROTATED through the real Architect UI, and verify each blueprint.

    python .local/qa/hvac-place.py ITEM ROTS "x,z x,z ..."

ITEM: overvent | overcooler | heater | wallheater
ROTS: clicks on the panel's rotate-right (E) arrow after selecting (rotation resets to North on every
      selection). North = 0, East = 1, South = 2, West = 3.
      over-wall vent: 0 on an east-west (horizontal) wall, 1 on a north-south (vertical) wall.
      over-wall cooler: hot side faces the rotation, cold side the opposite -- 0 = hot north / cold south,
      1 = hot east / cold west, 2 = hot south / cold north, 3 = hot west / cold east. Hot side outdoors.
Order matters: the camera moves first (moving it after selecting cancels placement), then the panel
selection, then the rotation clicks, then the cells. All cells must be in one view.
Owner, 2026-10-09: "you have to rotate things to place them correctly im not telling you again".
"""
import importlib.util, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
item, rots, cells = sys.argv[1], int(sys.argv[2]), [tuple(map(int, p.split(","))) for p in sys.argv[3].split()]
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
PY = sys.executable
GIZMO = {"overvent": ("Over-wall vent", "Over-wall vent"), "overcooler": ("Over-wall cooler...", "Over-wall cooler"),
         "heater": ("Heater", None), "wallheater": ("Wall heater", None),
         "utilitygen": ("Company utility generator", None), "cutoff": ("Emergency cutoff", None)}
CAT = {"utilitygen": "Power", "cutoff": "Power"}
BP = {"overvent": "Blueprint_Vent_Over", "overcooler": "Blueprint_Cooler_Over", "heater": "Blueprint_Heater", "wallheater": "Blueprint_WallHeater",
      "utilitygen": "Blueprint_RR_UtilityGenerator", "cutoff": "Blueprint_RR_EmergencyCutoff"}
def f(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = f(v, k)
            if r is not None: return r
def rclick(ix, iy): subprocess.run([PY, os.path.join(HERE, "raw-click.py"), str(int(ix)), str(int(iy))], capture_output=True); time.sleep(0.35)
def click_label(pred, above=0):
    el = next((x for x in e.layout() if pred(" ".join(e.plain(x["label"]).split()))), None)
    if not el: return False
    r = el["screenRect"]; rclick((r["x"] + r["width"] / 2) * 2, (r["y"] + r["height"] / 2 - above) * 2); return True
def has_bp(x, z):
    o = subprocess.run([PY, os.path.join(HERE, "find-things.py"), BP[item].replace("Blueprint_", ""), str(x), str(z), str(x + 1), str(z + 1)], capture_output=True, text=True).stdout
    return bool(o.strip())
e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection"); e.call("rimworld/close_main_tab")
cx = sum(c[0] for c in cells) / len(cells); cz = sum(c[1] for c in cells) / len(cells)
e.call("rimworld/jump_camera_to_cell", {"x": int(cx), "z": int(cz)}); time.sleep(0.4)
cam = e.call("rimworld/get_camera_state"); x0, x1, z0, z1 = (f(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
e.call("rimworld/open_main_tab", {"mainTabId": "main-tab:Architect"}); time.sleep(0.5)
g, opt = GIZMO[item]
for _ in range(3):   # the category toggles: click until its gizmos are showing
    if any(" ".join(e.plain(x["label"]).split()).startswith(g.rstrip(".")) for x in e.layout()): break
    cat = CAT.get(item, "Temperature")
    if not click_label(lambda t: t == cat): sys.exit("no category " + cat)
    time.sleep(0.5)
if not click_label(lambda t: t == g or t.startswith(g.rstrip(".")), above=22): sys.exit("no gizmo " + g)
time.sleep(0.5)
if opt and not click_label(lambda t: t == opt): sys.exit("no dropdown option " + opt)
time.sleep(0.4)
for _ in range(rots): rclick(273, 467)
done = []
for x, z in cells:
    ix = (x - x0 + 0.5) * 3840.0 / (x1 - x0 + 1); iy = (z1 - z + 0.5) * 2054.0 / (z1 - z0 + 1)
    rclick(ix, iy)
    if not has_bp(x, z): rclick(ix, iy)          # the first click after a focus change can be eaten
    done.append("%d,%d:%s" % (x, z, "OK" if has_bp(x, z) else "FAIL"))
e.call("rimworld/press_cancel"); e.call("rimworld/close_main_tab")
print(item, "rot", rots, " ".join(done))
