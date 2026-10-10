"""Set a cooler/heater's target temperature with its -18/-2/+2/+18 gizmos.  python .local/qa/set-temp.py X Z TARGET_F"""
import importlib.util, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
x, z, want = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
e.call("rimworld/clear_selection")
def read():
    for l in e.layout():
        m = re.search(r"Target temperature: (-?\d+)F", e.plain(l["label"]))
        if m: return int(m.group(1))
for _ in range(4):
    subprocess.run([PY, os.path.join(HERE, "click-cell.py"), x, z], capture_output=True); time.sleep(0.3)
    if read() is not None: break
def press(lbl):
    el = e.find(e.layout(), lambda t: t.strip() == lbl); r = el["screenRect"]
    subprocess.run([PY, os.path.join(HERE, "raw-click.py"), str(int((r["x"] + r["width"] / 2) * 2)), str(int((r["y"] - 20) * 2))], capture_output=True); time.sleep(0.35)
for _ in range(30):
    t = read()
    if t is None: sys.exit("not a climate building")
    d = want - t
    if d == 0: break
    press("-18F" if d <= -18 else "+18F" if d >= 18 else "-2F" if d < 0 else "+2F")
print(x, z, "target", read())
e.call("rimworld/clear_selection")
