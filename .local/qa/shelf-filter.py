"""Set a shelf's storage filter through the real Storage tab: select it, Clear all, tick the named rows.

    python .local/qa/shelf-filter.py X Z "Foods" ["Herbal medicine" ...]      # only these
    python .local/qa/shelf-filter.py X Z --except "Foods"                    # Allow all, then untick these

Rows are found by label in the UI layout; the checkbox sits at the row's right end. A row hidden in a
collapsed category is reached through the tab's search box. Prints the pane after, as a screenshot crop.
"""
import importlib.util, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
x, z, rows = sys.argv[1], sys.argv[2], sys.argv[3:]
EXCEPT = bool(rows) and rows[0] == "--except"
if EXCEPT: rows = rows[1:]
sys.argv = ["x", "--dry"]
s = importlib.util.spec_from_file_location("e", os.path.join(HERE, "empire.py")); e = importlib.util.module_from_spec(s); s.loader.exec_module(e)
PY = sys.executable
def raw(ux, uy): subprocess.run([PY, os.path.join(HERE, "raw-click.py"), str(int(ux * 2)), str(int(uy * 2))], capture_output=True); time.sleep(0.4)
e.call("rimworld/clear_selection")
subprocess.run([PY, os.path.join(HERE, "click-cell.py"), x, z], capture_output=True); time.sleep(0.4)
for _ in range(5):
    els = e.layout()
    if e.find(els, lambda t: t == "Clear all"): break
    st = e.find(els, lambda t: t == "Storage")
    if not st:   # an item or plant on the cell took the click: clicking again cycles the selection
        subprocess.run([PY, os.path.join(HERE, "click-cell.py"), x, z], capture_output=True); time.sleep(0.4); continue
    e.click_el(st); time.sleep(0.5)
ca = e.find(e.layout(), lambda t: t == ("Allow all" if EXCEPT else "Clear all"))
if not ca: sys.exit("no filter pane")
e.click_el(ca); time.sleep(0.4)
for row in rows:
    el = e.find(e.layout(), lambda t, r=row: t.strip() == r)
    if not el: print("row not visible:", row); continue
    r = el["screenRect"]; cx, cy = r["x"] + r["width"] + 20, r["y"] + r["height"] / 2   # the checkbox is drawn past the label rect
    def px():
        n = "px_%d" % int(time.time() * 1000); e.call("rimworld/take_screenshot", {"fileName": n})
        from PIL import Image
        return Image.open(os.path.join(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots"), n + ".png")).convert("RGB").getpixel((int(cx * 2), int(cy * 2)))
    before = px()
    for _ in range(3):                       # the first click after a focus change is often eaten
        raw(cx, cy)
        if px() != before: break
name = "filt_%d" % int(time.time() * 1000)
e.call("rimworld/take_screenshot", {"fileName": name})
from PIL import Image
shots = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots")
Image.open(os.path.join(shots, name + ".png")).crop((0, 600, 700, 1600)).save(os.path.join(HERE, "shots", "filter.png"))
print("pane at .local/qa/shots/filter.png")
