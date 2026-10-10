"""The whole work grid, every pawn, read back from the game's own UI.

Owner, 2026-10-10: "set up all priorities this is the last time i telling you set it how ive told you every
day weve played all of them for every one using coopy paste to paste one to the tosthers then customize keep
all the 1s firsefiring through cooking".

So: every column from Firefight through Cook is 1 for everyone (that is the paste), then each pawn's own
columns after Cook are customised. The loop is closed on the game's own numbers -- `get_ui_layout` returns
each grid cell's rect AND its current digit, so nothing is guessed from pixels: read the digit, click once,
read again, repeat until it matches. Clicks go through real-click.py, which refuses unless RimWorld is in
front and stops the moment the owner moves the mouse.

    python .local/qa/work-grid.py           # wait for the game in front + an idle mouse, then set it all
    python .local/qa/work-grid.py --now     # right now (refuses if the game is not in front)
"""
import ctypes, importlib.util, json, os, re, socket, subprocess, sys, time, uuid
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); sock = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
b.exchange(sock, buf, "session/hello", {"token": tok, "bridgeVersion": "workgrid/1", "platform": "windows",
                                        "launchId": str(uuid.uuid4())})
u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
GAME = u.FindWindowW(None, "RimWorld by Ludeon Studios")

def call(n, a=None):
    r = b.exchange(sock, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

# every column, in the order the tab draws them (read off the rotated headers)
ORDER = ["Firefight", "Patient", "Doctor", "Maintain Vat", "Bed rest", "Capture", "Haul+", "Childcare",
         "Basic", "Warden", "Jailor", "Wait", "Sell", "Handle", "Entertain", "Cook", "Hunt", "Construct",
         "Grow", "Mine", "Plant cut", "Dissect", "Smith", "Tailor", "Training", "Art", "Craft", "Fish",
         "Nuclear", "Resource", "Haul", "Clean", "Dark study", "Research", "Cycle"]
PASTE = {c: 1 for c in ORDER[:ORDER.index("Cook") + 1]}      # Firefight through Cooking: all 1s, everyone
CUSTOM = {
    "Gee":   {"Grow": 1, "Research": 1, "Hunt": 2, "Plant cut": 2, "Construct": 2, "Fish": 2,
              "Resource": 2, "Haul": 3, "Clean": 3},
    "Scar":  {"Construct": 1, "Smith": 1, "Tailor": 1, "Craft": 1, "Art": 2, "Grow": 2, "Mine": 2,
              "Plant cut": 2, "Haul": 2, "Clean": 2},
    "Unity": {"Hunt": 1, "Mine": 1, "Haul": 1, "Plant cut": 1, "Construct": 2, "Grow": 2, "Clean": 2,
              "Resource": 2, "Fish": 2},
}

def front():
    return u.GetForegroundWindow() == GAME and not u.IsIconic(GAME)

def idle():
    a = wintypes.POINT(); u.GetCursorPos(ctypes.byref(a)); time.sleep(3)
    c = wintypes.POINT(); u.GetCursorPos(ctypes.byref(c)); return (a.x, a.y) == (c.x, c.y)

class Stop(Exception): pass

def click_ui(x, y):
    r = subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(int(x * 2)), str(int(y * 2))],
                       capture_output=True, text=True)
    if "click" not in (r.stdout + r.stderr): raise Stop((r.stdout + r.stderr).strip())
    time.sleep(0.2)

def grid():
    """{pawn: {column: (value, x, y)}} straight off the live tab."""
    call("rimworld/open_main_tab", {"mainTabId": "main-tab:Work"}); time.sleep(0.5)
    cells, rows = [], {}
    def walk(o):
        if isinstance(o, dict):
            lab, rc = o.get("label"), o.get("screenRect")
            if rc and isinstance(lab, str):
                m = re.match(r"^(\w+)<color", lab)
                if m and rc["x"] < 200: rows[m.group(1)] = round(rc["y"])
                elif lab in ("1", "2", "3", "4"):
                    cells.append((int(lab), round(rc["x"]), round(rc["y"]), rc["width"], rc["height"]))
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout"))
    xs = sorted({c[1] for c in cells})
    out = {}
    for name, ry in rows.items():
        out[name] = {}
        for val, x, y, w, h in cells:
            if abs(y - ry) <= 2 and x in xs:
                i = xs.index(x)
                if i < len(ORDER): out[name][ORDER[i]] = (val, x + w / 2, y + h / 2)
    return out

if "--now" not in sys.argv:
    while not (front() and idle()): time.sleep(1)
if not front(): sys.exit("REFUSED: RimWorld is not foreground (owner has the screen)")

g = grid()
print("rows:", {k: len(v) for k, v in g.items()})
changed = wrong = 0
for name, cells in g.items():
    want = dict(PASTE); want.update(CUSTOM.get(name, {}))
    for col, target in want.items():
        if col not in cells: continue
        for _ in range(5):
            val, cx, cy = cells[col]
            if val == target: break
            click_ui(cx, cy); changed += 1
            g2 = grid(); cells = g2.get(name, cells)
        else:
            wrong += 1; print("  STUCK", name, col, "wanted", target, "got", cells[col][0])
    print(name, "set")
final = grid()
print("clicks", changed, "stuck", wrong)
for name, cells in final.items():
    want = dict(PASTE); want.update(CUSTOM.get(name, {}))
    bad = {c: (cells[c][0], t) for c, t in want.items() if c in cells and cells[c][0] != t}
    print(name, "OK" if not bad else ("MISMATCH " + json.dumps(bad)))
json.dump({n: {c: v[0] for c, v in cells.items()} for n, cells in final.items()},
          open(os.path.join(HERE, "_work_grid.json"), "w"), indent=1)
call("rimworld/close_window", {"windowType": "RimWorld.MainTabWindow_Work"})
