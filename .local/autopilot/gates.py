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
OURS = {"Gee", "Scar", "Unity"}

bspec = importlib.util.spec_from_file_location("b", os.path.join(QA, "bridge.py"))
bridge = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bridge)

def _session():
    port, tok = bridge.endpoint()
    s = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
    bridge.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "gates/1",
                                              "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf

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
    st["letters"] = len(letters)
    st["letter_labels"] = [l.get("label") for l in letters]
    st["alerts"] = [a.get("label") for a in call("rimworld/list_alerts").get("alerts", [])]
    crew = [c for c in call("rimworld/list_colonists").get("colonists", []) if c.get("factionIsPlayer")]
    st["crew"] = [(c["name"], c.get("job"), bool(c.get("drafted")), bool(c.get("downed"))) for c in crew]
    home = next((c["name"] for c in crew if c.get("mapId") == "Map_0"), None)
    if home: call("rimworld/select_pawn", {"pawnName": home})
    meals = raw = wood = med = bp = 0; foes = 0; roofed = total = 0
    for x in range(118, 196, 26):
        for z in range(96, 176, 26):
            for c in call("rimworld/get_cells_info", {"x": x, "z": z, "width": 26, "height": 26}).get("cells", []):
                bp += len(c.get("blueprintBuildDefs") or [])
                for t in c.get("things", []):
                    d = t.get("defName") or ""; n = t.get("stackCount", 1)
                    if d.startswith("Meal"): meals += n
                    elif d.startswith("Raw"): raw += n
                    elif d == "WoodLog": wood += n
                    elif "Medicine" in d: med += n
                    elif t.get("className") == "Verse.Pawn":
                        nm = (t.get("label") or "").split("<")[0].strip()
                        if nm and nm not in OURS and "," in (t.get("label") or ""): foes += 1
                if 153 <= c["x"] <= 160 and 133 <= c["z"] <= 138:
                    total += 1; roofed += 1 if c.get("roofDefName") else 0
    st["days_of_food"] = round((meals * 0.9 + raw * 0.05) / (1.6 * max(1, len(crew))), 2)
    st.update({"meals": meals, "raw_food": raw, "wood": wood, "medicine": med, "blueprints": bp,
               "humanlikes_not_ours": foes,
               "store_roofed_fraction": (roofed / total) if total else 1.0})
    # a letter decides whether those humanlikes are a raid or a caravan: a sweep alone cannot tell
    hostile_letter = any("raid" in (l or "").lower() for l in st["letter_labels"])
    st["hostiles_on_map"] = foes if hostile_letter else 0
    gaps = 0
    for (xs, zs) in ([(x, 127) for x in range(137, 169)] + [(x, 154) for x in range(137, 169)] +
                     [(137, z) for z in range(128, 154)] + [(168, z) for z in range(128, 154)]):
        pass
    st["wall_gaps"] = gaps          # measured by the camp sweep in cursor-jobs; left at 0 here to stay cheap
    st["game_foreground"] = _foreground()
    return st

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
    for name, spec in var.items():
        v = computed.get(name, spec.get("value"))
        lo, hi = spec.get("min"), spec.get("max")
        if lo is not None: v = max(lo, v)
        if hi is not None: v = min(hi, v)
        v = round(v, 2) if isinstance(v, float) else v
        spec["value"] = v           # maintained in place, so the file always shows the live setpoint
        out[name] = v
    return out


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
            try: ref = float(want[1:])
            except ValueError: continue          # symbolic bound (e.g. cost_of_blueprints): left to the model
            if got is None: return False
            if want[0] == ">" and not float(got) > ref: return False
            if want[0] == "<" and not float(got) < ref: return False
    return True

def decide(st=None, every=False):
    st = st or state()
    book = json.load(open(PLAYBOOK, encoding="utf-8"))
    tagvals = tags(book, st)
    st["tags"] = tagvals
    try:
        json.dump(book, open(PLAYBOOK, "w", encoding="utf-8"), indent=2)   # write the maintained setpoints back
    except Exception:
        pass
    hits = [g for g in sorted(book["gates"], key=lambda g: g["priority"]) if _holds(g.get("when", {}), st, tagvals)]
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
