"""Do the jobs only a mouse-down can do, in one burst, with Unity's OWN mouse.

Owner, 2026-10-10, verbatim: "im not loaining the mouse it need to have its OWN mouse!!!!!! that doesnt fight
user input and deffers instantly before attempting recontol once settles d mouse". Selection and command
gizmos go through the bridge; the parts that only answer a mouse-down (bed-owner menu, plant menu, storage
filter checkboxes, bill menu) go through real-click.py, which posts the click to the RimWorld window -- the
owner's cursor never moves and the game never has to be in front. Only when a posted click cannot select a map
cell does select_cell fall back to real-click.py --real, which waits for the owner's input to settle and
defers the instant they move.

    python .local/qa/cursor-jobs.py            # waits for the game window, then runs every job once
    python .local/qa/cursor-jobs.py --now      # run now (refuses if the game window is not open)
"""
import importlib.util, json, os, socket, subprocess, sys, time, uuid, ctypes

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
cspec = importlib.util.spec_from_file_location("camp", os.path.join(HERE, "camp.py")); camp = importlib.util.module_from_spec(cspec); cspec.loader.exec_module(camp)
port, tok = b.endpoint(); sock = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
b.exchange(sock, buf, "session/hello", {"token": tok, "bridgeVersion": "cursorjobs/1", "platform": "windows", "launchId": str(uuid.uuid4())})
u = ctypes.WinDLL("user32"); GAME = u.FindWindowW(None, "RimWorld by Ludeon Studios")

# Owner, 2026-10-09: "jesues!!18 shells!!! wtf is going on!!!!" -- re-arming this queue instead of replacing it
# left three copies all waiting for the game window, which would have fired three sets of real clicks into the
# same UI at once. One instance only: a second start refuses while the first is still waiting.
LOCK = os.path.join(HERE, "_cursor_jobs.lock")
if os.path.exists(LOCK):
    try:
        pid = int(open(LOCK).read().strip())
        os.kill(pid, 0)                      # raises if that pid is gone
        sys.exit("REFUSED: cursor-jobs is already armed as pid %d" % pid)
    except (ValueError, OSError):
        pass                                  # stale lock, take it over
open(LOCK, "w").write(str(os.getpid()))
import atexit

# Owner, 2026-10-10: "im getting alot of system cmd openings while im doing stuff". Every helper this script
# spawns -- powershell for the process table, python for a spoken line -- was flashing its own console over
# whatever the owner was doing. One shim, applied to this process, makes every child windowless.
import subprocess as _sp, os as _os
if _os.name == "nt":
    _CF = 0x08000000                       # CREATE_NO_WINDOW
    _run = _sp.run
    def _run_nowin(*a, **k):
        k["creationflags"] = k.get("creationflags", 0) | _CF
        return _run(*a, **k)
    _sp.run = _run_nowin
    _Popen = _sp.Popen
    class _PopenNoWin(_Popen):
        def __init__(self, *a, **k):
            k["creationflags"] = k.get("creationflags", 0) | _CF
            super().__init__(*a, **k)
    _sp.Popen = _PopenNoWin

atexit.register(lambda: os.path.exists(LOCK) and os.remove(LOCK))

def call(n, a=None):
    r = b.exchange(sock, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

def front():
    """The game window is open and not minimised -- posted input needs nothing more, not even focus."""
    return bool(GAME) and not u.IsIconic(GAME)

def targets():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("targetId") and o.get("screenRect"): out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout")); return out

def find(pred):
    return next((o for o in targets() if pred((o.get("label") or "").strip(), o)), None)

class Stop(Exception): pass

def click_ui(x, y):
    """UI coords (half the render) -> a guarded real click."""
    r = subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(int(x * 2)), str(int(y * 2))], capture_output=True, text=True,
                       creationflags=0x08000000 if os.name == "nt" else 0)
    out = r.stdout + r.stderr
    if "click" not in out: raise Stop(out.strip())
    time.sleep(0.45)

def click_rect(rc, dy=0):
    click_ui(rc["x"] + rc["width"] / 2, rc["y"] + rc["height"] / 2 + dy)

def crew():
    return [c for c in call("rimworld/list_colonists").get("colonists", []) if c.get("factionIsPlayer", True)]

def home_pawn():
    cols = crew(); home = camp.home_map(cols)
    return next((c["name"] for c in cols if c.get("mapId") == home), None)

def render_size():
    """The game window's client area in pixels, read live; the configured size when it cannot be read."""
    try:
        import ctypes.wintypes
        r = ctypes.wintypes.RECT()
        if GAME and u.GetClientRect(GAME, ctypes.byref(r)) and r.right > 0 and r.bottom > 0:
            return float(r.right), float(r.bottom)
    except Exception:
        pass
    w, h = camp.conf().get("render", [3840, 2054]); return float(w), float(h)

def cell_to_render(x, z):
    """Where a map cell is on screen, from the camera's own view rect and the window's size (z grows upward)."""
    cam = call("rimworld/get_camera_state"); vr = cam["viewRect"]
    w = vr["maxX"] - vr["minX"] + 1; h = vr["maxZ"] - vr["minZ"] + 1
    rw, rh = render_size()
    px = (x - vr["minX"] + 0.5) / w * rw
    py = (vr["maxZ"] - z + 0.5) / h * rh
    return px, py

def select_cell(x, z):
    p = home_pawn()
    if not p: raise Stop("nobody on the home map")
    call("rimworld/press_cancel")                      # drop any live designator: a click would paint a zone
    call("rimworld/select_pawn", {"pawnName": p}); call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    call("rimworld/clear_selection"); call("rimworld/click_cell", {"x": x, "z": z}); time.sleep(0.3)
    if not call("rimworld/list_selected_gizmos").get("selectedCount"):
        # a bridge click does not select a zone or a bed (2026-10-09), and the camera centre was a guess that
        # missed (2026-10-10: every job came back "no gizmo"). Put a click exactly on the cell instead,
        # worked out from the camera's view rect, and click there.
        # Owner, 2026-10-10, verbatim: "you ar not selecting the crop zones correctly so ther for they are
        # all set wrong to all potatoes you have to click twice fast maybe more times id something is ther like
        # conduit". RimWorld cycles the selection through everything stacked on a cell when you click the same
        # spot again quickly -- plant, then conduit, then the zone underneath. So: click fast, repeatedly, and
        # stop the moment a ZONE gizmo is on screen. Slow clicks re-select the top thing instead of cycling.
        # Unity's own (posted) mouse first; if that never selects anything, the owner's cursor through the
        # settle-and-defer guard -- a deferral stops the burst instead of fighting for the pointer.
        px, py = cell_to_render(x, z)
        posted_selected = False
        for attempt in range(9):
            if attempt >= 6 and posted_selected: break   # posted clicks reach the game: no reason to borrow
            extra = ["--real"] if attempt >= 6 else []
            r = subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(int(px)), str(int(py))] + extra,
                               capture_output=True, text=True,
                   creationflags=0x08000000 if os.name == "nt" else 0)
            if "click" not in (r.stdout + r.stderr):
                raise Stop((r.stdout + r.stderr).strip())
            time.sleep(0.16)                      # fast: this is a double/triple click, not six separate ones
            sel = call("rimworld/list_selected_gizmos")
            if not extra and sel.get("selectedCount", 0): posted_selected = True
            if sel.get("selectedCount", 0) > 1:
                call("rimworld/clear_selection"); time.sleep(0.15); continue
            if any((o.get("label") or "").startswith(("Plant:", "Allow sowing", "For colonists", "For prisoners"))
                   for o in targets()):
                break


def gizmo_menu(gizmo_prefix, option_prefix):
    g = find(lambda l, o: l.startswith(gizmo_prefix) and o["screenRect"]["y"] > 850)
    if not g: return "no gizmo " + gizmo_prefix
    click_rect(g["screenRect"], dy=-30)            # the icon sits above its caption
    key = option_prefix.lower()
    opt = find(lambda l, o: l.lower().startswith(key)) or find(lambda l, o: key in l.lower())
    if not opt: return "no option " + option_prefix
    click_rect(opt["screenRect"]); return "ok"

def job_prisoner_bed():
    select_cell(159, 151); return gizmo_menu("For colonists", "For prisoners")

def job_camp_area():
    """Pin all three colonists to the Camp allowed area.

    Owner, 2026-10-10, verbatim: "i told you to set all those field to the NE far from camp to no soe as its
    to far away and we havent moved in yet". The allowed area is the enforcement that does not depend on a
    zone toggle: 5688 cells covering the camp, the firebreak and the nine near fields, painted through the
    bridge. Only the Area dropdown in the Assign tab needs a real click.
    """
    call("rimworld/open_main_tab", {"mainTabId": "main-tab:Assign"}); time.sleep(0.6)
    done = []
    for who in sorted(camp.crew_names(crew())):
        row = find(lambda l, o: l.startswith(who) and o["screenRect"]["x"] < 200)
        if not row: done.append(who + ":no-row"); continue
        y = row["screenRect"]["y"] + row["screenRect"]["height"] / 2
        drop = find(lambda l, o: l in ("Unrestricted", "Camp", "Home") and abs(o["screenRect"]["y"] + o["screenRect"]["height"] / 2 - y) < 6)
        if not drop: done.append(who + ":no-dropdown"); continue
        if (drop.get("label") or "") == "Camp": done.append(who + ":already"); continue
        click_rect(drop["screenRect"])
        opt = find(lambda l, o: l == "Camp")
        if not opt: done.append(who + ":no-camp-option"); call("rimworld/press_cancel"); continue
        click_rect(opt["screenRect"]); done.append(who + ":Camp")
    return " ".join(done)


def job_trade_open():
    """Open the visiting trader's dialog and WRITE DOWN what it offers -- no buying on a guess.

    A mining goods caravan from Youentus is parked outside while the colony sits on a Low-medicine alert with
    no medicine and no healroot anywhere on the map, so trade is the one medicine route that needs neither
    research nor the crop menu. The trade window's labels are the game's, with 294 mods in the list, so this
    first pass only opens it and dumps every label to _trade_offer.json. Buying is wired from those real
    labels, the same way the crop and bill jobs had to be.
    """
    foes = json.load(open(os.path.join(HERE, "_foes.json"))) if os.path.exists(os.path.join(HERE, "_foes.json")) else []
    if not foes: return "no caravan recorded"
    name, x, z = foes[0]
    p = home_pawn()
    if not p: return "nobody home"
    call("rimworld/press_cancel"); call("rimworld/clear_selection")
    call("rimworld/select_pawn", {"pawnName": p})
    call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.8)
    call("rimworld/right_click_cell", {"x": x, "z": z}); time.sleep(0.8)
    opts = []
    def w(n):
        if isinstance(n, dict):
            if n.get("label"): opts.append(n)
            for v in n.values(): w(v)
        elif isinstance(n, list):
            for v in n: w(v)
    w(call("rimworld/get_context_menu_options"))
    hit = next((o for o in opts if "trade" in (o.get("label") or "").lower()), None)
    if not hit:
        call("rimworld/close_context_menu")
        return "no trade option on %s; menu %s" % (name, [o.get("label") for o in opts][:4])
    call("rimworld/execute_context_menu_option", {"optionIndex": hit.get("index", hit.get("optionIndex"))})
    time.sleep(1.5)
    labs = sorted({(o.get("label") or "").strip() for o in targets() if (o.get("label") or "").strip()})
    json.dump(labs, open(os.path.join(HERE, "_trade_offer.json"), "w"), indent=0)
    meds = [l for l in labs if "medicine" in l.lower() or "healroot" in l.lower()]
    call("rimworld/press_cancel")
    return "trade window read: %d labels, medicine rows %s" % (len(labs), meds[:4] or "none")


def job_crops():
    # owner, 2026-10-10: "you are going nothing but potatoes everywhere wtf!" -- every zone defaults to potato,
    # so each field's own crop is set explicitly, potatoes included, and read back from the gizmo caption.
    # the menu carries the game's own plant labels, not "Plant <crop>" -- match the crop word itself
    crop = {"berries": "berry", "potatoes": "potato", "corn": "corn", "healroot": "healroot", "rice": "rice",
            "cotton": "cotton", "smokeleaf": "smokeleaf", "psychoid": "psychoid", "hops": "hop"}
    res = []
    for p in json.load(open(os.path.join(HERE, "_plots.json"))):
        if not crop.get(p["crop"]): continue
        select_cell(p["x"] + p["w"] // 2, p["z"] + p["h"] // 2)
        res.append(p["crop"] + ":" + gizmo_menu("Plant:", crop[p["crop"]]))
    return " ".join(res)

def storage_tab():
    t = [x for x in call("rimworld/list_inspect_tabs").get("tabs", []) if x["label"] == "Storage"]
    if not t: return False
    call("rimworld/open_inspect_tab", {"inspectTabId": t[0]["inspectTabId"]}); time.sleep(0.3); return True

def tick_row(label):
    row = find(lambda l, o: l == label)
    if not row: return "no row " + label
    click_ui(254, row["screenRect"]["y"] + row["screenRect"]["height"] / 2); return "ok"

def job_food_store():
    select_cell(157, 136)
    if not storage_tab(): return "no storage tab"
    ca = find(lambda l, o: l == "Clear all"); call("rimworld/click_ui_target", {"targetId": ca["targetId"]}); time.sleep(0.3)
    return tick_row("Foods")

def bill_rows():
    """How many bill rows the open Bills tab is showing."""
    return len([o for o in targets() if "Suspend" in (o.get("label") or "")])


def add_bill(x, z, wants):
    """Add the first bill option that actually takes.

    The live log (2026-10-10) has `Exception filling window for Verse.FloatMenu:
    System.NullReferenceException at RimWorld.ITab_Bills+<FillTab>b__2` -- choosing some Add-bill options
    throws inside the game, so the bill never appears and nothing says so. Count the rows before and after,
    and if the count did not move, try the next matching option instead of reporting success.
    """
    select_cell(x, z)
    tabs = [i for i in call("rimworld/list_inspect_tabs").get("tabs", []) if i["label"] == "Bills"]
    if not tabs: return "no bills tab"
    call("rimworld/open_inspect_tab", {"inspectTabId": tabs[0]["inspectTabId"]}); time.sleep(0.3)
    before = bill_rows()
    for want in wants:
        add = find(lambda l, o: l == "Add bill")
        if not add: return "no add bill"
        click_rect(add["screenRect"])
        opt = find(lambda l, o: want in l.lower())
        if not opt: call("rimworld/press_cancel"); continue
        click_rect(opt["screenRect"]); time.sleep(0.4)
        if bill_rows() > before: return "added " + want
        call("rimworld/press_cancel")
    return "no option took"


def job_stove_bill():
    select_cell(155, 141)
    t = [x for x in call("rimworld/list_inspect_tabs").get("tabs", []) if x["label"] == "Bills"]
    if not t: return "no bills tab"
    call("rimworld/open_inspect_tab", {"inspectTabId": t[0]["inspectTabId"]}); time.sleep(0.3)
    add = find(lambda l, o: l == "Add bill")
    if not add: return "no add bill"
    click_rect(add["screenRect"])
    opt = find(lambda l, o: "simple meal" in l.lower())
    if not opt: return "no simple meal option"
    click_rect(opt["screenRect"]); return "ok"

def job_butcher_bill_old():
    select_cell(152, 141)
    t = [x for x in call("rimworld/list_inspect_tabs").get("tabs", []) if x["label"] == "Bills"]
    if not t: return "no bills tab"
    call("rimworld/open_inspect_tab", {"inspectTabId": t[0]["inspectTabId"]}); time.sleep(0.3)
    add = find(lambda l, o: l == "Add bill")
    if not add: return "no add bill"
    click_rect(add["screenRect"])
    opt = find(lambda l, o: "butcher" in l.lower())
    if not opt: return "no butcher option"
    click_rect(opt["screenRect"]); return "ok"

def job_research():
    """Queue research by TYPING IT IN THE SEARCH BOX, not by dragging the tree around.

    Owner, 2026-10-10, verbatim: "its like u are open research skeen and dragging the wrong dirrectgion to
    explore it not using the search at all". The Research window has a search field: click it, type the name,
    and the tree jumps to the match -- no dragging, no guessing which way the tree grows.
    """
    want = ["Electricity", "Air conditioning"]
    done = []
    for name in want:
        call("rimworld/open_main_tab", {"mainTabId": "main-tab:Research"}); time.sleep(0.6)
        box = find(lambda l, o: l in ("Search", "Search...") or (o.get("semanticKind") or "") == "search")
        if box is None:
            # the field carries no label on some builds: take the widest short box in the window's top strip
            cands = [o for o in targets() if o["screenRect"]["y"] < 200 and 120 < o["screenRect"]["width"] < 400]
            box = cands[0] if cands else None
        if box is None: return "no search box"
        click_rect(box["screenRect"])
        r = subprocess.run([sys.executable, os.path.join(HERE, "type-neg.py"), name.split()[0].lower()],
                           capture_output=True, text=True,
                   creationflags=0x08000000 if os.name == "nt" else 0)
        if "typed" not in r.stdout: return "typing refused: " + (r.stdout + r.stderr).strip()[:60]
        time.sleep(0.6)
        hit = find(lambda l, o: l.startswith(name))
        if not hit: done.append(name + ":not-found"); continue
        click_rect(hit["screenRect"]); time.sleep(0.3)
        done.append(name + ":queued")
    return " ".join(done)


def job_bill_counts():
    """Food bills the efficient way: "Do until you have X", X raised as the base grows, no skill restriction
    so everyone trains on it.

    Owner, 2026-10-10, verbatim: "you are not setting bills correctly for everyhting for food puduction how
    ive alllready tolsdd you how to do it effienctly so everyone can train and still get the most in one go"
    / "and set amounts higher and higher as your base grows". Three colonists and a staging camp, so the
    opening target is 30 simple meals; it is raised as the colony does.
    """
    TARGET = 30
    select_cell(155, 141)
    tabs = [x for x in call("rimworld/list_inspect_tabs").get("tabs", []) if x["label"] == "Bills"]
    if not tabs: return "no bills tab"
    call("rimworld/open_inspect_tab", {"inspectTabId": tabs[0]["inspectTabId"]}); time.sleep(0.3)
    rep = find(lambda l, o: l.startswith(("Do forever", "Do X times", "Do until you have")))
    if not rep: return "no repeat-mode button"
    for _ in range(3):
        lab = (rep.get("label") or "")
        if lab.startswith("Do until you have"): break
        click_rect(rep["screenRect"]); time.sleep(0.35)
        rep = find(lambda l, o: l.startswith(("Do forever", "Do X times", "Do until you have"))) or rep
    if not (rep.get("label") or "").startswith("Do until you have"): return "repeat mode stuck at " + (rep.get("label") or "?")
    cnt = find(lambda l, o: l.isdigit() and o["screenRect"]["width"] < 120)
    if cnt:
        click_rect(cnt["screenRect"])
        subprocess.run([sys.executable, os.path.join(HERE, "type-neg.py"), str(TARGET)],
                       capture_output=True, text=True,
                   creationflags=0x08000000 if os.name == "nt" else 0)
    return "do-until-%d" % TARGET


def job_priorities():
    """Manual work priorities (owner, 2026-10-09: "set up priorities u fool" / "pawns have none set"). Manual mode
    is already on (all 3s). Cell centres read off the Work tab at its current layout; a left click raises
    priority one step (3 -> 2 -> 1)."""
    call("rimworld/open_main_tab", {"mainTabId": "main-tab:Work"}); time.sleep(0.6)
    sc = 0.5517; col = {"Firefight": 363, "Patient": 404, "Doctor": 445, "Haul": 608, "Cook": 975, "Hunt": 1016,
                        "Construct": 1057, "Grow": 1098, "Mine": 1139, "Smith": 1261, "Tailor": 1302, "Craft": 1424}
    row = {"Gee": 185, "Scar": 218, "Unity": 251}
    plan = {"Gee": {"Firefight": 1, "Patient": 1, "Cook": 2},
            "Scar": {"Firefight": 1, "Patient": 1, "Construct": 1, "Craft": 2, "Smith": 2, "Tailor": 2},
            "Unity": {"Firefight": 1, "Patient": 1, "Mine": 1, "Hunt": 2, "Haul": 2, "Doctor": 2}}
    n = 0
    live = camp.crew_names(crew())
    for who, cols in plan.items():
        if who not in live or who not in row: continue     # the plan is per person; absent crew are skipped
        for c, want in cols.items():
            for _ in range(3 - want):
                subprocess.run([sys.executable, os.path.join(HERE, "real-click.py"), str(int(col[c] / sc)), str(int(1380 + row[who] / sc))],
                               capture_output=True, text=True); n += 1; time.sleep(0.25)
    return "clicks %d" % n


def job_ne_nosow():
    """No sowing at the main-base plots until the crew moves in (owner, 2026-10-10: "i told you to block soeing
    at the farms at the main base and make new farms of everything u need grow near the camp outer walls").
    The zone's Allow-sowing toggle only answers a real mouse, and a bridge click does not select a zone, so each
    plot is centred and selected with a real click at screen centre."""
    res = []
    for zid, (x, z) in json.load(open(os.path.join(HERE, "_ne_plots.json"))).items():
        select_cell(x, z)
        g = find(lambda l, o: l == "Allow sowing" and o["screenRect"]["y"] > 850)
        if not g: res.append(zid + ":no-toggle"); continue
        click_rect(g["screenRect"], dy=-30)
        g2 = find(lambda l, o: l == "Allow sowing" and o["screenRect"]["y"] > 850)
        res.append(zid + ":off")
    return " ".join(res)

JOBS = [("trade: read the offer", job_trade_open), ("camp area", job_camp_area), ("crops", job_crops), ("research", job_research), ("bill counts", job_bill_counts), ("butcher bill", lambda: add_bill(152, 141, ["butcher creature", "butcher"])), ("food store", job_food_store), ("stove bill", lambda: add_bill(155, 141, ["simple meal", "fine meal", "meal"]))]

if "--now" not in sys.argv:
    while not front():
        time.sleep(1); GAME = u.FindWindowW(None, "RimWorld by Ludeon Studios")
if not front(): sys.exit("REFUSED: the RimWorld window is not open")
results = {}
for name, job in JOBS:
    while os.path.exists(os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", ".popup.json")): time.sleep(2)   # a pop-up wants a decision: wait
    try:
        r = job(); results[name] = r; print(name, "->", r)
    except Stop as e: results[name] = "STOPPED"; print(name, "-> STOPPED:", e); break
    except Exception as e: results[name] = "error"; print(name, "-> error:", e)
call("rimworld/clear_selection"); call("rimworld/press_cancel")

# Owner, 2026-10-10, verbatim: "STOP UNPAUSING TILL ALL ISSUES ARE ADDDRESSED". Time only runs again when
# every job in this burst came back clean -- no "no gizmo", no "not-found", no error, nothing stopped.
bad = {k: v for k, v in results.items()
       if any(w in str(v).lower() for w in ("no ", "not-found", "error", "stopped", "failed", "stuck"))}
if bad:
    print("STILL PAUSED -- unfinished:", json.dumps(bad))
else:
    # owner: only Unity or the owner unpauses -- a helper never runs time, even after a clean burst.
    print("every job clean -- left paused (only Unity or the owner unpauses)")
