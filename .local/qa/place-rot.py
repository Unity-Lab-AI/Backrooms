"""Place a building ROTATED through the real UI (owner, 2026-10-09: "you have to rotate things to place them
correctly im not telling you again").

    python .local/qa/place-rot.py DESIGNATOR_ID ROTS "x,z x,z ..."

ROTS = clicks on the Architect panel's rotate-right (E) arrow: 1 = east-facing, 2 = south, 3 = west.
Over-wall vents on a north-south wall need 1. Coolers: the cold (blue) side faces the rotation
direction's opposite of the hot side -- check the ghost colour in a screenshot before relying on it.
Key presses do not rotate (they never reach the placement); the panel arrow does. The camera is moved
BEFORE selecting -- moving it after cancels placement. All cells must be in one view.
"""
import importlib.util, subprocess, sys, time
did, rots, cells = sys.argv[1], int(sys.argv[2]), [tuple(map(int, p.split(","))) for p in sys.argv[3].split()]
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", ".local/qa/empire.py"); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
def f(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = f(v, k)
            if r is not None: return r
e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection")
cx = sum(c[0] for c in cells) // len(cells); cz = sum(c[1] for c in cells) // len(cells)
e.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz}); time.sleep(0.3)
cam = e.call("rimworld/get_camera_state"); x0, x1, z0, z1 = (f(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
e.call("rimworld/open_main_tab", {"mainTabId": "main-tab:Architect"}); time.sleep(0.4)
e.call("rimworld/select_architect_designator", {"designatorId": did}); time.sleep(0.4)
for _ in range(rots):
    subprocess.run([sys.executable, ".local/qa/raw-click.py", "273", "467"], capture_output=True); time.sleep(0.3)
for x, z in cells:
    ix = (x - x0 + 0.5) * 3840.0 / (x1 - x0 + 1); iz = (z1 - z + 0.5) * 2054.0 / (z1 - z0 + 1)
    subprocess.run([sys.executable, ".local/qa/raw-click.py", str(int(ix)), str(int(iz))], capture_output=True); time.sleep(0.3)
e.call("rimworld/press_cancel"); e.call("rimworld/close_main_tab")
print("placed", len(cells))
