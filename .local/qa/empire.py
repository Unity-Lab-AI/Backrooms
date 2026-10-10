"""Maintain the empire: one pass of the standing orders, enforced by code instead of by memory.

    python .local/qa/empire.py            # check everything, fix what it can, report the rest
    python .local/qa/empire.py --dry      # report only
    python .local/qa/empire.py --grid     # also read every heater and cooler's power grid (slow, ~1 min)

Owner, 2026-10-08: "ther is so so so so sooooooo much ive told you to do that you havent even set it
to be done yet" / "no not the todo agent file and scripts of how to fucking maintatain emp[ire to
the stars" / "and so much more". Run it every play loop (after play.py). Each check is one owner
direction; the docstring of each says which.

  STOCK   keep steel, components, medicine, wood and cloth above a floor: order from the company
          (Operations -> Procurement) when low and no order for that item is still open.
          ("you have no compnaetns", "use steel and order steel from the company")
  DROPZONE the receiving stockpile stays at Normal (the delivery fix is staged, 2026-10-09).
  SELFTEND every colonist allowed to self-tend.
  GRID    every heater and cooler on a live grid (runs every pass).
  ARMS    every colonist carries a gun: an unarmed one picks up a loose gun from the map.
          ("make sure everyone has their sidearm and maine rifle")
  HUNT    wild animals inside the base walls get Hunt orders; caravan/visitor pack animals are left alone.
          ("hunt the wild animals in ur base perimeter")
  FOOD    perishables (meals, raw food, meat, plant matter) outside the freezer are reported for hauling.
          ("you are still storing shit in hallways and have pershables in wrong places")
  POWER   every powered building is on a live grid (power-audit.py; every pass).
          ("you have shit all over your base that doesnt have power")
  ABILITY leader and moral-guide abilities used on cooldown (abilities.py).
  CHAT    viewer chat is read every slice by stream-beat.py and play.py stops on it.

STANDING ORDERS that are judgement, not a script -- re-read before every build (docs/PLAYSCRIPT.md):
  walls complete, no holes; outer-wall gaps are doors; no blocked paths; embrasures fixed and powered;
  one organised power-generation area; HVAC = one heater + one cooler per cluster, <=3 over-wall vents,
  rotated correctly, hot side outdoors, halls included; hi-tech research benches and analyzers after
  Microelectronics; powered lamps, never torches; bedrooms for colonists, cells only for prisoners;
  perishables in the freezer, nothing stored in hallways; cash crops of every kind; call traders and
  sell everything not needed; fight with the camera on the action; never walk the line toward a raid.
Everything is clicked through the real UI (RimBridge layout targets + game-click.py), never by
editing the save.
"""

import importlib.util, json, os, re, socket, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
DRY = "--dry" in sys.argv
FRAME_PER_UI = 1600 / 1920.0          # eyes frame px per RimWorld UI unit (3840 client, UI scale 2)

STOCK = [  # (thingDef, menu label, floor, order quantity)
    ("Steel", "Steel - Steel", 800, 2000),   # conduit, walls, generators all eat steel
    ("ComponentIndustrial", "Industrial components - ComponentIndustrial", 25, 100),
    ("MedicineIndustrial", "Industrial medicine - MedicineIndustrial", 15, 60),
    ("WoodLog", "Wood logs - WoodLog", 600, 1500),   # winter: generators burn it, trees stop growing
    ("Cloth", "Cloth - Cloth", 100, 400),
    # food: winter left 10 colonists with 3 stacks of meals (2026-10-08); survival packs never spoil
    ("MealSurvivalPack", "Packaged survival meals - MealSurvivalPack", 60, 300),
]
DROP_CELL = (131, 86)                  # a cell of Stockpile zone 1, the receiving stockpile

spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)


def call(tool, args=None):
    o = subprocess.run([PY, os.path.join(HERE, "bridge.py"), "call", tool, json.dumps(args or {})],
                       capture_output=True, text=True, encoding="utf-8").stdout
    try: return json.loads(o[o.find("{"):])
    except Exception: return {}


def layout():
    """Full get_ui_layout (the CLI call truncates at 60k) -> list of elements with label/rect."""
    port, token = b.endpoint(); buf = bytearray(); out = []
    with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
        b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsEmpire/1", "platform": "windows", "launchId": str(uuid.uuid4())})
        r = b.exchange(s, buf, "tools/call", {"name": "rimworld/get_ui_layout", "arguments": {}})
    def walk(n):
        if isinstance(n, dict):
            if "targetId" in n and isinstance(n.get("label"), str): out.append(n)
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(r); return out


def plain(t): return re.sub(r"<[^>]+>", "", t or "")


def find(els, pred):
    return next((e for e in els if pred(plain(e["label"]))), None)


def click_el(e):
    """Actionable -> click_ui_target; otherwise a real click on its rect (float-menu entries)."""
    if e.get("actionable"):
        call("rimworld/click_ui_target", {"targetId": e["targetId"]}); return
    r = e["screenRect"]
    x = int((r["x"] + r["width"] / 2) * FRAME_PER_UI); y = int((r["y"] + r["height"] / 2) * FRAME_PER_UI)
    subprocess.run([PY, os.path.join(HERE, "game-click.py"), str(x), str(y)], capture_output=True)


def count(defname):
    o = subprocess.run([PY, os.path.join(HERE, "find-things.py"), defname, "0", "0", "300", "300"],
                       capture_output=True, text=True, env=dict(os.environ, ALL="1")).stdout
    # find-things lists cells; stack sizes come from get_cell_info on each
    cells = [tuple(map(int, m)) for line in o.splitlines() if line.split(" ")[0] == defname
             for m in re.findall(r"\((\d+), (\d+)\)", line)]
    total = 0
    for x, z in cells:
        info = json.dumps(call("rimworld/get_cell_info", {"x": x, "z": z}))
        for lab in re.findall(r'"label": "([^"]*)"', info):
            m = re.search(r" x(\d+)$", plain(lab))
            if m and defname.lower()[:4] in plain(lab).lower().replace(" ", "")[:12] + lab.lower(): total += int(m.group(1)); break
        else:
            total += 1 if cells else 0
    return total


def open_procurement():
    els = layout()
    if not find(els, lambda t: t.startswith("Item:")):
        subprocess.run([PY, os.path.join(HERE, "game-click.py"), "136", "841"], capture_output=True)
        els = layout()
        p = find(els, lambda t: t == "Procurement")
        if p: click_el(p); els = layout()
    return els


def open_orders(els):
    """Item names with a company order not yet fully delivered."""
    pend = set()
    for e in els:
        t = plain(e["label"])
        m = re.search(r"rocurement:\d+ — ([^:]+): .*still held", t)
        if m and " 0 still held" not in t: pend.add(m.group(1).strip().lower())
    return pend


def order(menu_label, qty):
    els = layout()
    item = find(els, lambda t: t.startswith("Item:"))
    if not item: return "no Item button"
    click_el(item); time.sleep(0.4)
    entry = find(layout(), lambda t: t == menu_label)
    if not entry: return "menu entry missing: " + menu_label
    click_el(entry); time.sleep(0.4)
    els = layout()
    q = find(els, lambda t: t == "Quantity to request")
    if not q: return "no quantity label"
    # the text field sits just under its label
    r = q["screenRect"]; x = int((r["x"] + 120) * FRAME_PER_UI); y = int((r["y"] + r["height"] + 16) * FRAME_PER_UI)
    subprocess.run([PY, os.path.join(HERE, "game-click.py"), str(x), str(y)], capture_output=True)
    if os.environ.get("OWNER_LENT_MOUSE") != "1":   # typing the quantity is real keyboard input: locked
        return "REFUSED: ordering types on the keyboard; ask the owner to lend it first"
    import ctypes
    u = ctypes.WinDLL("user32"); g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
    if u.GetForegroundWindow() != g: return "RimWorld not foreground"
    def k(v): u.keybd_event(v, 0, 0, 0); time.sleep(0.02); u.keybd_event(v, 0, 2, 0); time.sleep(0.02)
    k(0x24)
    for _ in range(25): k(0x2E)
    for ch in str(qty): k(ord(ch))
    time.sleep(0.3)
    for step in ("Create supplier quote", "Accept and pay", "Confirm"):
        e = find(layout(), lambda t, s=step: t.startswith(s))
        if not e: return "missing step: " + step
        click_el(e); time.sleep(0.5)
    return "ordered %d" % qty


def empty_zone_cell():
    """A cell of the receiving zone with nothing on it, so the click selects the zone itself."""
    for z in range(DROP_CELL[1] - 3, DROP_CELL[1] + 4):
        info = call("rimworld/get_cells_info", {"x": DROP_CELL[0] - 2, "z": z, "width": 14, "height": 1})
        for c in info.get("cells", []):
            if "Stockpile zone 1" in json.dumps(c.get("zone")) and c.get("thingCount", 1) == 0:
                return c["x"], c["z"]
    return DROP_CELL


def set_drop_priority(level):
    """Select the receiving zone and set its storage priority through the inspect pane."""
    x, z = empty_zone_cell()
    o = subprocess.run([PY, os.path.join(HERE, "click-cell.py"), str(x), str(z)], capture_output=True, text=True).stdout
    els = layout()
    # a full zone has no empty cell: the click picks the stack on it, and clicking the same cell
    # again cycles the selection (stack -> zone), so click until the Storage tab shows
    m = re.search(r"at frame (\d+) (\d+)", o)
    for _ in range(3):
        if not m or find(els, lambda t: t == "Storage" or t.startswith("Priority:")): break
        subprocess.run([PY, os.path.join(HERE, "game-click.py"), m.group(1), m.group(2)], capture_output=True)
        time.sleep(0.3); els = layout()
    pr = find(els, lambda t: t.startswith("Priority:"))
    for _ in range(2):                  # a tab that is already open closes on click: toggle until shown
        if pr: break
        tab = find(els, lambda t: t == "Storage")
        if not tab: break
        click_el(tab); time.sleep(0.3); els = layout()
        pr = find(els, lambda t: t.startswith("Priority:"))
    if not pr: return "no priority button"
    if plain(pr["label"]).endswith(level): call("rimworld/clear_selection"); return "already " + level
    click_el(pr); time.sleep(0.3)
    opt = find(layout(), lambda t: t == level)
    if opt: click_el(opt)
    call("rimworld/clear_selection")
    return "set " + level


def arms():
    """Unarmed colonists (read off the newest autosave) pick up loose guns on the map."""
    d = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves")
    f = max((os.path.join(d, n) for n in os.listdir(d) if n.lower().startswith("autosave")), key=os.path.getmtime)
    s = open(f, encoding="utf-8", errors="ignore").read()
    unarmed = []
    for c in call("rimworld/list_colonists").get("colonists", []):
        if not c.get("humanlike"): continue
        pid = c["pawnId"].replace("Thing_", ""); i = s.find("<id>%s</id>" % pid)
        if i < 0: continue
        j = s.find("<equipment>", i); k = s.find("</equipment>", j)
        # a gun carried as a sidearm (inventory) counts: Scar held a mace with her charge rifle in
        # her sidearms, and the old check sent her to pick up EMP grenades (2026-10-08)
        n = s.find("<inventory>", i); m = s.find("</inventory>", n)
        held = (j >= 0 and j - i <= 300000 and re.search(r"<def>Gun_", s[j:k])) or \
               (n >= 0 and n - i <= 300000 and re.search(r"<def>Gun_", s[n:m]))
        if not held: unarmed.append(c)
    loose = subprocess.run([PY, os.path.join(HERE, "find-things.py"), "Gun_", "0", "0", "300", "300"],
                           capture_output=True, text=True, env=dict(os.environ, ALL="1")).stdout
    guns = [tuple(map(int, m)) for line in loose.splitlines() if line.startswith("Gun_")
            for m in re.findall(r"\((\d+), (\d+)\)", line)]
    done = []
    for c, g in zip(unarmed, guns):
        if DRY: done.append("%s -> gun at %s" % (c["name"], g)); continue
        r = subprocess.run([PY, os.path.join(HERE, "equip.py"), c["name"], str(g[0]), str(g[1]), c["pawnId"]], capture_output=True, text=True)
        done.append(r.stdout.strip() or r.stderr.strip()[:80])
    left = [c["name"] for c in unarmed[len(guns):]]
    return done, left


def grids():
    """Every heater and cooler reads its grid line; any with no stored power and no excess is dead
    at night -- Rev and the last child died of hypothermia on such a grid (2026-10-08)."""
    o = subprocess.run([PY, os.path.join(HERE, "find-things.py"), "Heater,Cooler", "0", "0", "300", "300"],
                       capture_output=True, text=True, env=dict(os.environ, ALL="1")).stdout
    seen, dead = set(), []
    for line in o.splitlines():
        if line.split(" ")[0] not in ("Heater", "Cooler"): continue
        for x, z in (tuple(map(int, m)) for m in re.findall(r"\((\d+), (\d+)\)", line)):
            subprocess.run([PY, os.path.join(HERE, "click-cell.py"), str(x), str(z)], capture_output=True)
            g = next((plain(e["label"]) for e in layout() if "Grid excess" in plain(e["label"])), "")
            m = re.search(r"Grid excess: (-?\d+) W \((\d+) Wd stored\)", g)
            if not m: continue
            key = (m.group(1), m.group(2))
            if int(m.group(2)) == 0 and int(m.group(1)) <= 0: dead.append("%s(%d,%d)" % (line.split(" ")[0], x, z))
            seen.add(key)
    call("rimworld/clear_selection")
    return dead, sorted(seen)


def selftend():
    """Every colonist allowed to self-tend (owner, 2026-10-09: "everyone need set to self tend medoical" /
    "i told u self tend on everyones profile settings"). Reads the Health tab's checkbox pixel."""
    from PIL import Image
    shots = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots")
    fixed = []
    for c in call("rimworld/list_colonists").get("colonists", []):
        if not c.get("humanlike"): continue
        call("rimworld/clear_selection"); call("rimworld/select_pawn", {"pawnId": c["pawnId"]}); time.sleep(0.2)
        h = find(layout(), lambda t: t == "Health")
        if h: click_el(h); time.sleep(0.3)
        name = "st_%d" % int(time.time() * 1000)
        call("rimworld/take_screenshot", {"fileName": name})
        try: r, g, _ = Image.open(os.path.join(shots, name + ".png")).convert("RGB").getpixel((267, 987))
        except Exception: continue
        if g <= r and not DRY:
            subprocess.run([PY, os.path.join(HERE, "game-click.py"), "111", "411"], capture_output=True); fixed.append(c["name"])
    call("rimworld/clear_selection")
    return fixed


BASE = (100, 62, 200, 142)                # the walled base box
FREEZER = (161, 83, 171, 97)
PERISH = re.compile(r"^(Meal|Raw|Meat_|Hay|Kibble|Milk|Egg|Smokeleaf|Plant.*Leaves|Berries|Corn|Rice|Potato)")


def scan_base():
    """Every thing in the base box, one bridge session -> list of (defName, className, label, x, z)."""
    port, token = b.endpoint(); buf = bytearray(); out = []
    def unwrap(r):
        for k in ("result", "structuredContent"):
            if isinstance(r, dict) and k in r: r = r[k]
        if isinstance(r, dict) and "content" in r:
            for c in r["content"]:
                if c.get("type") == "text":
                    try: return json.loads(c["text"])
                    except Exception: pass
        return r
    with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
        b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsEmpire/1", "platform": "windows", "launchId": str(uuid.uuid4())})
        for x in range(BASE[0], BASE[2], 25):
            for z in range(BASE[1], BASE[3], 20):
                r = unwrap(b.exchange(s, buf, "tools/call", {"name": "rimworld/get_cells_info", "arguments": {"x": x, "z": z, "width": 25, "height": 20}}))
                for c in (r or {}).get("cells", []):
                    for t in c.get("things", []):
                        out.append((t.get("defName", ""), t.get("className", ""), t.get("label", ""), c["x"], c["z"]))
    return out


def hunt(things):
    """Wild animals inside the walls -> Hunt. Unnamed animal pawns only (tamed ones carry names with a
    digit or a given name), and none within 8 cells of a non-colonist human (caravan pack animals)."""
    mine = {(c["position"]["x"], c["position"]["z"]) for c in call("rimworld/list_colonists").get("colonists", [])}
    strangers = [(x, z) for d, k, l, x, z in things if k == "Verse.Pawn" and d in ("Human", "CreepJoiner") and (x, z) not in mine]
    picks = []
    for d, k, l, x, z in things:
        if k != "Verse.Pawn" or d in ("Human", "CreepJoiner"): continue
        if plain(l) != plain(l).split("<")[0] or any(ch.isdigit() for ch in l): continue
        if plain(l).lower() != d.lower().replace("_", " ") and not plain(l).lower().startswith(d.lower()[:4]): continue
        if any(abs(x - a) + abs(z - c) <= 8 for a, c in strangers): continue
        picks.append((d, x, z))
    if not DRY:
        for d, x, z in picks:
            call("rimworld/apply_architect_designator", {"designatorId": "architect-designator:orders:highlight-designator-tutortagnotset-4", "x": x, "z": z})
    return picks


def food_out_of_place(things):
    fx0, fz0, fx1, fz1 = FREEZER
    return sorted({(d, x, z) for d, k, l, x, z in things if PERISH.match(d) and not d.startswith("Plant_")
                   and not (fx0 <= x <= fx1 and fz0 <= z <= fz1)})


def main():
    report = []
    things = scan_base()
    report.append("HUNT ordered on: %s" % (hunt(things) or "-"))
    report.append("FOOD outside the freezer: %s" % (food_out_of_place(things) or "-"))
    o = subprocess.run([PY, os.path.join(HERE, "power-audit.py")], capture_output=True, text=True, timeout=1500).stdout
    report.append("POWER " + " | ".join(l for l in o.splitlines() if l.startswith(("UNPOWERED", "GRID"))))
    a = subprocess.run([PY, os.path.join(HERE, "abilities.py")], capture_output=True, text=True, timeout=600).stdout
    report.append("ABILITY " + " | ".join(a.splitlines()))
    report.append("SELFTEND turned on for: %s" % (selftend() or "- (all already on)"))
    if True:   # every pass: owner, 2026-10-09: "you have shit all over your base that doesnt have power"
        dead, seen = grids()
        report.append("GRID dead heaters/coolers: %s | grids seen (excess W, stored Wd): %s" % (dead or "-", seen))
    els = open_procurement()
    pending = open_orders(els)
    for defname, label, floor, qty in STOCK:
        have = count(defname)
        name = label.split(" - ")[0].lower()
        key = next((p for p in pending if p.split()[0] in name or name.split()[-1] in p), None)
        if have >= floor: report.append("STOCK %-22s %6d ok" % (defname, have)); continue
        if key: report.append("STOCK %-22s %6d low, order open (%s)" % (defname, have, key)); continue
        report.append("STOCK %-22s %6d low -> %s" % (defname, have, "would order %d" % qty if DRY else order(label, qty)))
    pending = open_orders(layout())
    call("rimworld/close_main_tab")
    want = "Normal"   # the delivery fix is staged (2026-10-09): the receiving zone stays Normal, shelves Preferred
    report.append("DROPZONE %s pending -> %s" % (sorted(pending) or "none", "would set " + want if DRY else set_drop_priority(want)))
    done, left = arms()
    report.append("ARMS equipped: %s | still unarmed (no loose gun): %s" % (done or "-", left or "-"))
    print("\n".join(report))


if __name__ == "__main__":
    main()
