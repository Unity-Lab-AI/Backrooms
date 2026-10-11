"""Evaluate playbook.json against measured game state and hand back ONE action chain.

Owner, 2026-10-10, verbatim: *"all my things ive been tossing at you as instructions on how to play all need to
be put into the models undertstanding but not a text wall shit a actual logical guided logaica gates system of
porcess chains and actions for every thing uve ran into in the game"*.

So the rules stop being prose the model re-reasons over and become a lookup: `state()` measures the colony
through the bridge, `decide()` walks the gates in priority order and returns the first one whose conditions
hold, and the autopilot gets that single chain plus the always-gate instead of a wall.

    python .local/autopilot/gates.py            # what fires right now, and why
    python .local/autopilot/gates.py --all      # every gate that matches, in order
"""
import importlib.util, json, os, socket, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
QA = os.path.join(ROOT, ".local", "qa")
# the tracked copy under docs/ is the source of record; .local keeps a working copy for when docs is absent
PLAYBOOK = next((p for p in (os.path.join(ROOT, "docs", "playbook.gates.json"),
                             os.path.join(HERE, "playbook.json")) if os.path.exists(p)), None)
bspec = importlib.util.spec_from_file_location("b", os.path.join(QA, "bridge.py"))
bridge = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bridge)
cspec = importlib.util.spec_from_file_location("camp", os.path.join(QA, "camp.py"))
camp = importlib.util.module_from_spec(cspec); cspec.loader.exec_module(camp)

def _session():
    try:
        port, tok = bridge.endpoint()
    except SystemExit as e:                      # "no live standalone bridge": a condition, not a reason to exit
        raise RuntimeError(str(e))
    s = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
    bridge.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "gates/1",
                                              "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf

QA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".local", "qa")
LADDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch", "ladder.json")   # her edits
SETPOINTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch", "setpoints.json")   # measured, local

def state():
    """Everything the gates ask about, measured -- never assumed."""
    s, buf = _session()
    def call(n, a=None):
        r = bridge.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
        return r.get("structuredContent", r) if isinstance(r, dict) else r
    st = {}
    t1 = call("rimworld/get_game_info").get("ticksGame"); time.sleep(1.2)
    st["ticks_moving"] = t1 != call("rimworld/get_game_info").get("ticksGame")
    ui = call("rimworld/get_ui_state")
    st["dialog_open"] = bool(ui.get("nonImmediateDialogWindowOpen") or ui.get("NonImmediateDialogWindowOpen"))
    letters = call("rimworld/list_letters").get("letters", [])
    # a letter counts once: after she has looked at the letters (listed, opened or dismissed), the ones present then
    # are handled -- the company's standing notices never go away and kept the rung on top forever (live, 10-10)
    try:
        seen = set(json.load(open(LADDER, encoding="utf-8")).get("letters_seen", []))
    except Exception:
        seen = set()
    st["letters"] = len([l for l in letters if l.get("id") not in seen])
    st["letter_labels"] = [l.get("label") for l in letters]
    st["alerts"] = [a.get("label") for a in call("rimworld/list_alerts").get("alerts", [])]
    every = call("rimworld/list_colonists").get("colonists", [])
    crew = [c for c in every if c.get("factionIsPlayer")]
    st["crew"] = [(c["name"], c.get("job"), bool(c.get("drafted")), bool(c.get("downed"))) for c in crew]
    ours = camp.crew_names(crew)
    home = camp.home_map(crew)
    st["home_map"] = home
    # the cell sweep can only read the map on screen. When that is not home, nothing is selected to switch to it
    # (a poll must never move the player's selection): the camp numbers stay unmeasured and the rungs that need
    # them do not fire this scan.
    try:
        here = call("rimworld/list_colonists", {"currentMapOnly": True}).get("colonists", [])
    except Exception:
        here = []
    on_home = any(c.get("mapId") == home for c in here)
    st["home_on_screen"] = on_home
    if on_home:
        meals = raw = wood = med = bp = 0; foes = 0; roofed = total = 0; power = defence = 0
        minx, minz, maxx, maxz = camp.camp_rect(crew, home)
        for x in range(minx, maxx + 1, 26):
            for z in range(minz, maxz + 1, 26):
                try:
                    cells = call("rimworld/get_cells_info", {"x": x, "z": z, "width": 26, "height": 26}).get("cells", [])
                except (Exception, SystemExit):
                    cells = []                   # a block past the map edge reads as empty, not as a failed scan
                for c in cells:
                    bp += len(c.get("blueprintBuildDefs") or [])
                    for t in c.get("things", []):
                        d = t.get("defName") or ""; n = t.get("stackCount", 1)
                        if d.startswith("Meal"): meals += n
                        elif d.startswith("Raw"): raw += n
                        elif d == "WoodLog": wood += n
                        elif "Medicine" in d: med += n
                        elif "Generator" in d or d in ("WindTurbine", "Battery", "GeothermalGenerator"): power += 1
                        elif "Turret" in d or d in ("Sandbags", "Barricade") or "Embrasure" in d: defence += 1
                        elif t.get("className") == "Verse.Pawn":
                            nm = (t.get("label") or "").split("<")[0].strip()
                            if nm and nm not in ours and "," in (t.get("label") or ""): foes += 1
                    # the stores are the cells inside a food/main stockpile zone, read off the cell itself
                    zone = json.dumps(c.get("zone") or "").lower()
                    if "food" in zone or "main" in zone:
                        total += 1; roofed += 1 if c.get("roofDefName") else 0
        st["days_of_food"] = round((meals * 0.9 + raw * 0.05) / (1.6 * max(1, len(crew))), 2)
        st.update({"meals": meals, "raw_food": raw, "wood": wood, "medicine": med, "blueprints": bp,
                   "humanlikes_not_ours": foes, "has_power": power > 0, "defences_built": defence > 0})
        if total: st["store_roofed_fraction"] = roofed / total
        # a letter decides whether those humanlikes are a raid or a caravan: a sweep alone cannot tell
        hostile_letter = any("raid" in (l or "").lower() for l in st["letter_labels"])
        st["hostiles_on_map"] = foes if hostile_letter else 0
    # wall_gaps is not measured here: the perimeter rung is disabled in the playbook rather than fed a fixed 0
    st["game_foreground"] = _foreground()
    # --- setup inputs (owner: "the whole logic gate chain like a plc ... use and edit on the fly") ---
    st["colony_exists"] = len(st["crew"]) > 0
    try:
        zl = [z.get("label") or "" for z in call("rimworld/list_zones").get("zones", [])]
    except Exception:
        zl = []
    st["food_store"] = any("food" in z.lower() for z in zl)
    st["main_store"] = any("main" in z.lower() for z in zl)
    st["explore_done"] = os.path.exists(os.path.join(QA_DIR, "_explore_done.flag"))
    # her own marks: a step the game cannot measure directly is marked done by her with ladder_set
    for k, v in (_ladder_file().get("marks") or {}).items():
        st["mark_" + k] = bool(v)
    for k in ("pawns_set", "assign_set", "beds_set", "stove_set", "bill_set"):
        st.setdefault("mark_" + k, False)
    return st

def _ladder_file():
    try:
        return json.load(open(LADDER, encoding="utf-8"))
    except Exception:
        return {}

def _foreground():
    try:
        import ctypes
        u = ctypes.WinDLL("user32"); g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
        return bool(g) and u.GetForegroundWindow() == g and not u.IsIconic(g)
    except Exception:
        return False

def tags(book, st):
    """The PLC tag table: constants stay put, variables are recomputed from the empire's current size.

    Owner, 2026-10-10, verbatim: "with changaeable variables and constants as needed and maintained for a
    growing empire". So a colony of three and an empire of thirty read the same ladder and get different
    numbers, and the numbers are maintained here rather than scattered through the rungs.
    """
    tg = book.get("tags") or {}
    const = dict(tg.get("constants") or {})
    var = tg.get("variables") or {}
    n = max(1, len(st.get("crew") or []))
    computed = {
        "FOOD_MIN_DAYS": 2 + 0.4 * n,
        "FOOD_COMFORT_DAYS": 2 * (2 + 0.4 * n),
        "MEAL_BILL_TARGET": 10 * n,
        "WOOD_RESERVE": 60 * n,
        "MEDICINE_RESERVE": 2 * n,
        "BEDS_NEEDED": n + 1,
        "COOLERS_PER_ROOM": 1,
    }
    out = dict(const)
    for k, v in (_ladder_file().get("tags") or {}).items():     # her setpoint edits win over the computed ones
        if k in var: var[k]["override"] = v
    for name, spec in var.items():
        v = spec.get("override", computed.get(name, spec.get("value")))
        lo, hi = spec.get("min"), spec.get("max")
        if lo is not None: v = max(lo, v)
        if hi is not None: v = min(hi, v)
        v = round(v, 2) if isinstance(v, float) else v
        spec["value"] = v           # in memory only; the live setpoints are written to scratch/setpoints.json
        out[name] = v
    return out


def _bound(expr, st, tagvals):
    """A numeric bound: a number, a {TAG}, or a measured state/tag name. None when it cannot be resolved."""
    e = expr.strip()
    if e.startswith("{") and e.endswith("}"):
        e = e[1:-1].strip()
    try:
        return float(e)
    except ValueError:
        pass
    for src in (tagvals, st):
        v = src.get(e)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
    return None


def _holds(cond, st, tagvals=None):
    for key, want in cond.items():
        if key != "letter_matches" and key not in st:
            return False          # unmeasured is not the same as false: a gate cannot fire on a missing key
        got = st.get(key)
        if key == "letter_matches":
            if not any(str(want).lower() in (l or "").lower() for l in st.get("letter_labels", [])): return False
            continue
        if isinstance(want, bool):
            if bool(got) != want: return False
        elif isinstance(want, (int, float)):
            if got is None or got != want: return False
        elif isinstance(want, str) and want[:1] in "<>":
            ref = _bound(want[1:], st, tagvals or {})
            if ref is None:
                # an unresolved bound never passes silently: the rung does not fire and the reason is recorded
                st.setdefault("unresolved_conditions", []).append("%s %s" % (key, want))
                return False
            if got is None: return False
            if want[0] == ">" and not float(got) > ref: return False
            if want[0] == "<" and not float(got) < ref: return False
    return True

def decide(st=None, every=False):
    st = st or state()
    book = json.load(open(PLAYBOOK, encoding="utf-8"))
    tagvals = tags(book, st)
    st["tags"] = tagvals
    # the playbook under docs/ is canonical and never rewritten by a read; the live setpoints go machine-local
    try:
        os.makedirs(os.path.dirname(SETPOINTS), exist_ok=True)
        tmp = SETPOINTS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"tags": tagvals, "ts": time.time()}, f, indent=1)
        os.replace(tmp, SETPOINTS)
    except Exception:
        pass
    # open-ended (owner: "dont limit it leave it open ended for the full complete empire build not some starter
    # camp"): rungs she writes herself with ladder_set merge in every scan; hers replace a book rung of the same id
    mine = {g["id"]: g for g in (_ladder_file().get("gates") or []) if g.get("id") and "priority" in g}
    allg = [g for g in book["gates"] if g["id"] not in mine] + list(mine.values())
    # a rung marked disabled has an input nothing measures yet; it never fires, and the reason is kept on the state
    st["disabled_rungs"] = {g["id"]: g["disabled"] for g in allg if g.get("disabled")}
    allg = [g for g in allg if not g.get("disabled")]
    hits = [g for g in sorted(allg, key=lambda g: g["priority"]) if _holds(g.get("when", {}), st, tagvals)]
    return (hits if every else hits[:1] + [g for g in hits if g["id"] == "always"][:1]), st

if __name__ == "__main__":
    gates, st = decide(every="--all" in sys.argv)
    print("state:", json.dumps({k: v for k, v in st.items() if k != "crew"}, default=str))
    print("crew: ", st.get("crew"))
    for g in gates:
        print("\n== GATE %s (priority %d)" % (g["id"], g["priority"]))
        print("   why:", g.get("why", "")[:160])
        for i, step in enumerate(g["then"], 1): print("   %d. %s" % (i, step))
        for n in g.get("never", []): print("   NEVER:", n)
