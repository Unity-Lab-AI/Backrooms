"""RimPLC: evaluate the ladder (docs/playbook.gates.json) against measured game state and hand back ONE action chain.

Owner, 2026-10-10, verbatim: *"all my things ive been tossing at you as instructions on how to play all need to
be put into the models undertstanding but not a text wall shit a actual logical guided logaica gates system of
porcess chains and actions for every thing uve ran into in the game"*.

Owner, 2026-10-12, verbatim: *"i think this is the whoole PLC like logic chain if this then this if heath level
reaches then this type of thing for the whole game properly layed out into a PLC that we will call RimPLC"*.

The ladder is laid out as a PLC:

  * INPUTS (sensors): `state()` reads the bridge once per scan; `derive()` turns those raw reads into measured
    keys. A key that cannot be read is left OUT of the state, never filled with a fake 0, so a rung that needs it
    stays quiet. The sensor table in the playbook (`sensors`) documents every key and its source.
  * TAGS: constants (safety limits, owner only) and variables (setpoints recomputed from the colony's size each
    scan, clamped to min/max, overridable by her with `ladder_set tag`).
  * MARKS: what the bridge cannot measure, set by her with `ladder_set mark` -- booleans or numbers. Numeric
    marks stay numbers. A boolean mark that was never set reads false; a numeric mark reads its `mark_defaults`
    value from the playbook, or stays unmeasured.
  * RUNGS: `when` (an AND of conditions) -> `then` (an ordered action chain), scanned by priority. A growth rung
    with `"latch": true` gets a done-latch: `mark_<id>_done: false` is added to its `when` and
    `ladder_set mark <id>_done true` is appended to its `then`, so a finished long-term rung stops hiding every
    rung ranked after it.

    python .local/autopilot/gates.py            # what fires right now, and why
    python .local/autopilot/gates.py --all      # every rung that matches, in order
"""
import importlib.util, json, math, os, re, socket, sys, time, uuid

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

QA_DIR = QA
LADDER = os.path.join(HERE, "scratch", "ladder.json")          # her edits: marks, tag overrides, her own rungs
SETPOINTS = os.path.join(HERE, "scratch", "setpoints.json")    # measured, local
ALERT_LOG = os.path.join(HERE, "scratch", "alert_labels.json")  # every alert label ever seen, to fix ALERT_MATCH

# ---------------------------------------------------------------------------------------------------------------
# Sensor tables. Every name here is either seen in a captured bridge reply (.local/qa/*.json) or marked UNVERIFIED.
# ---------------------------------------------------------------------------------------------------------------
TICKS_PER_DAY = 60000
TICKS_PER_QUADRUM = 900000
# vanilla LetterDefOf.ThreatBig / ThreatSmall (seen in the decompiled Verse.FogGrid.cs under .local/inspection-*);
# the captured list_letters reply carries the `letterDef` field (only "PositiveEvent" captured so far)
THREAT_LETTER_DEFS = ("ThreatBig", "ThreatSmall")
THREAT_LETTER_MAX_AGE = 2 * TICKS_PER_DAY     # a threat letter older than this no longer vouches for the crowd
# substring of an alert label (lower case) -> alert_<key>. UNVERIFIED: no list_alerts reply has been captured;
# the first live scans log every label to scratch/alert_labels.json and this table is fixed from that log.
ALERT_MATCH = {
    "low_food": "low food", "starv": "starv", "hypotherm": "hypotherm", "heatstroke": "heatstroke",
    "low_medicine": "medicine", "warm_clothes": "warm", "sickness": "sick", "need_research": "research",
    "idle": "idle", "colonist_needs_rescue": "rescue", "food_rot": "rot",
}
# defName -> resource key (sweep, summed by stackCount; stackCount is UNVERIFIED in captures, 1 per stack otherwise)
RESOURCES = {"Steel": "steel", "ComponentIndustrial": "components", "ComponentSpacer": "adv_components",
             "Plasteel": "plasteel", "Uranium": "uranium", "Gold": "gold", "Silver": "silver",
             "Chemfuel": "chemfuel", "Cloth": "cloth"}
NEVER_HUNT_DEFS = ("Boomalope", "Thrumbo", "Elephant", "Rhinoceros", "Megasloth")   # plus Bear_*
MOUNT_DEFS_DEFAULT = ("Elephant", "Horse", "Dromedary", "Muffalo", "Thrumbo")
# designation defName -> key. The field shape {defName, targetCell, targetThingDefName} is captured; these vanilla
# DesignationDef names are UNVERIFIED (only Deconstruct and SkilledBuilder3 have been seen).
DESIGNATIONS = {"Hunt": "designations_hunt", "Tame": "designations_tame", "HarvestPlant": "designations_harvest",
                "Mine": "designations_mine", "CutPlant": "designations_cut"}
# buildings counted as distinct objects: a multi-cell building is listed on every cell it covers and the cell reply
# has no thing id, so adjacent cells of the same def are merged into one object (two touching beds read as one)
BUILDING_KEYS = {
    "stoves": lambda d, c: d in ("FueledStove", "ElectricStove"),
    "research_benches": lambda d, c: c == "RimWorld.Building_ResearchBench" or d in ("SimpleResearchBench", "HiTechResearchBench"),
    "comms_console": lambda d, c: d == "CommsConsole" or c == "RimWorld.Building_CommsConsole",
    "turrets": lambda d, c: "Turret" in d and not d.startswith(("Blueprint_", "Frame_")),
    "beds": lambda d, c: c in ("RimWorld.Building_Bed", "Hospitality.Building_GuestBed"),
    "throne": lambda d, c: "Throne" in d and not d.startswith(("Blueprint_", "Frame_")),
    "pod_launchers": lambda d, c: d == "PodLauncher",
    "transport_pods": lambda d, c: d == "TransportPod",
    "grav_parts": lambda d, c: "Grav" in d and not d.startswith(("Blueprint_", "Frame_")),
    "ship_parts": lambda d, c: d.startswith("Ship_"),
    "power_generators": lambda d, c: "Generator" in d and not d.startswith(("Blueprint_", "Frame_"))
                                     or d in ("WindTurbine", "GeothermalGenerator"),
}
BOOL_BUILDINGS = ("comms_console", "throne")


def _session():
    try:
        port, tok = bridge.endpoint()
    except SystemExit as e:                      # "no live standalone bridge": a condition, not a reason to exit
        raise RuntimeError(str(e))
    s = socket.create_connection(("127.0.0.1", port), timeout=120); buf = bytearray()
    bridge.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "gates/2",
                                              "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf


def state():
    """Everything the rungs ask about, measured -- never assumed. Reads only; never moves the player's selection."""
    s, buf = _session()
    def call(n, a=None):
        r = bridge.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
        return r.get("structuredContent", r) if isinstance(r, dict) else r
    def opt(n, a=None):
        try:
            return call(n, a)
        except (Exception, SystemExit):
            return None
    raw = {}
    raw["game_info"] = call("rimworld/get_game_info"); time.sleep(1.2)
    gi2 = call("rimworld/get_game_info")
    raw["ticks_moving"] = raw["game_info"].get("ticksGame") != gi2.get("ticksGame")
    raw["bridge"] = opt("rimbridge/get_bridge_status")
    raw["ui"] = call("rimworld/get_ui_state")
    raw["letters"] = call("rimworld/list_letters")
    raw["alerts"] = opt("rimworld/list_alerts")
    raw["colonists"] = call("rimworld/list_colonists")
    raw["here"] = opt("rimworld/list_colonists", {"currentMapOnly": True})
    raw["zones"] = opt("rimworld/list_zones")
    raw["areas"] = opt("rimworld/list_areas")
    crew = [c for c in (raw["colonists"] or {}).get("colonists", []) if c.get("factionIsPlayer")]
    home = camp.home_map(crew)
    here = (raw["here"] or {}).get("colonists", []) if isinstance(raw["here"], dict) else []
    if any(c.get("mapId") == home for c in here):
        # the cell sweep can only read the map on screen; when that is not home nothing is switched (a poll must
        # never move the player's selection) and every sweep key stays unmeasured this scan
        cells = []
        minx, minz, maxx, maxz = camp.camp_rect(crew, home)
        for x in range(minx, maxx + 1, 26):
            for z in range(minz, maxz + 1, 26):
                r = opt("rimworld/get_cells_info", {"x": x, "z": z, "width": 26, "height": 26})
                cells.extend((r or {}).get("cells", []) if isinstance(r, dict) else [])   # past the edge reads empty
        raw["cells"] = cells
    raw["foreground"] = _foreground()
    raw["explore_done"] = os.path.exists(os.path.join(QA_DIR, "_explore_done.flag"))
    st = derive(raw, _ladder_file())
    _log_alert_labels(st.get("alerts") or [])
    return st


def _payload(r, key):
    return (r or {}).get(key, []) if isinstance(r, dict) else []


def derive(raw, lf=None):
    """Raw bridge replies -> measured keys. Pure: feed it captured replies to check the ladder offline.

    raw keys (all optional): game_info, ticks_moving, bridge, ui, letters, alerts, colonists, here, zones, areas,
    cells (list of get_cells_info cells), foreground, explore_done. A missing raw read leaves its keys out.
    """
    lf = lf or {}
    st = {}
    # --- clock and session ---
    gi = raw.get("game_info") or {}
    if "ticks_moving" in raw: st["ticks_moving"] = bool(raw["ticks_moving"])
    tk = gi.get("ticksGame")
    if isinstance(tk, (int, float)) and not isinstance(tk, bool):
        st["day"] = round(tk / TICKS_PER_DAY, 2)
        st["quadrum_index"] = int(tk // TICKS_PER_QUADRUM) % 4     # a counter, NOT a season (latitude-dependent)
    if isinstance(gi.get("mapCount"), int): st["map_count"] = gi["mapCount"]
    # paused rides on the `state` block every bridge reply carries (captured: list_zones, designator replies)
    for src in (raw.get("bridge"), raw.get("zones"), raw.get("ui")):
        if isinstance(src, dict):
            blk = src.get("state") if isinstance(src.get("state"), dict) else src
            if isinstance(blk.get("paused"), bool):
                st["paused"] = blk["paused"]; break
    ui = raw.get("ui")
    if isinstance(ui, dict):
        st["dialog_open"] = bool(ui.get("nonImmediateDialogWindowOpen") or ui.get("NonImmediateDialogWindowOpen"))
    # --- letters: counted once (seen ids live in ladder.json); threats by letterDef, never by the word "raid" ---
    if raw.get("letters") is not None:
        letters = _payload(raw["letters"], "letters")
        seen = set(lf.get("letters_seen", []))
        unseen = [l for l in letters if l.get("id") not in seen]
        st["letters"] = len(unseen)
        st["letter_labels"] = [l.get("label") for l in letters]
        st["letter_defs"] = [l.get("letterDef") for l in letters]
        # a threat letter vouches for the crowd while it is recent, whether or not she has read it: reading a raid
        # letter must not make the raiders vanish from the ladder
        st["threat_letter"] = any(l.get("letterDef") in THREAT_LETTER_DEFS and
                                  (l.get("ageTicks") is None or l.get("ageTicks") <= THREAT_LETTER_MAX_AGE)
                                  for l in letters)
        st["quest_letter"] = any("quest" in (l.get("label") or "").lower() or "Quest" in (l.get("letterDef") or "")
                                 for l in unseen)
        st["empire_letter"] = any("empire" in (l.get("relatedFaction") or "").lower() for l in unseen)
    # --- alerts (labels logged; the match table is UNVERIFIED until the log is read) ---
    if raw.get("alerts") is not None:
        labels = [a.get("label") or "" for a in _payload(raw["alerts"], "alerts")]
        st["alerts"] = labels
        low = [l.lower() for l in labels]
        for key, sub in ALERT_MATCH.items():
            st["alert_" + key] = any(sub in l for l in low)
    # --- crew ---
    every = _payload(raw.get("colonists"), "colonists")
    crew = [c for c in every if c.get("factionIsPlayer") and c.get("humanlike", True) is not False]
    st["crew"] = [(c.get("name"), c.get("job"), bool(c.get("drafted")), bool(c.get("downed"))) for c in crew]
    if raw.get("colonists") is not None:
        st["colonists"] = len(crew)
        st["downed_count"] = sum(1 for c in crew if c.get("downed"))
        st["drafted_count"] = sum(1 for c in crew if c.get("drafted"))
        st["mental_break"] = any(c.get("mentalState") for c in crew)
        maps = {c.get("mapId") for c in crew if c.get("mapId")}
        st["away_maps"] = max(0, len(maps) - 1)
        # UNVERIFIED whether list_colonists ever lists animals, mechs or hostile pawns: only written when seen, so an
        # empty list never reads as a measured zero
        n_an = sum(1 for c in every if c.get("animal") and c.get("factionIsPlayer"))
        n_me = sum(1 for c in every if c.get("mechanoid") and c.get("factionIsPlayer"))
        n_ho = sum(1 for c in every if c.get("factionHostileToPlayer") and not c.get("dead") and not c.get("downed"))
        if n_an: st["colony_animals"] = n_an
        if n_me: st["colony_mechs"] = n_me
        if n_ho: st["hostile_pawns_listed"] = n_ho
    ours = camp.crew_names(crew)
    home = camp.home_map(crew)
    st["home_map"] = home
    here = _payload(raw.get("here"), "colonists")
    on_home = any(c.get("mapId") == home for c in here)
    st["home_on_screen"] = on_home
    # --- zones and areas ---
    if raw.get("zones") is not None:
        zones = _payload(raw["zones"], "zones")
        zl = [z.get("label") or "" for z in zones]
        st["growing_cells"] = sum(z.get("cellCount", 0) for z in zones if str(z.get("className", "")).endswith("Zone_Growing"))
        st["stockpile_cells"] = sum(z.get("cellCount", 0) for z in zones if str(z.get("className", "")).endswith("Zone_Stockpile"))
    else:
        zl = []
    st["food_store"] = any("food" in z.lower() for z in zl)
    st["main_store"] = any("main" in z.lower() for z in zl)
    areas = _payload(raw.get("areas"), "areas")
    hc = [a.get("cellCount") for a in areas if str(a.get("className", "")).endswith("Area_Home")]
    cells = raw.get("cells") if on_home else None
    if not hc and cells:     # every cell reply carries its areas with their cellCount (captured)
        hc = [a.get("cellCount") for c in cells[:50] for a in (c.get("areas") or [])
              if isinstance(a, dict) and str(a.get("className", "")).endswith("Area_Home")][:1]
    if hc and isinstance(hc[0], int): st["home_cells"] = hc[0]
    # --- the sweep: only when home is the map on screen ---
    if cells is not None:
        _sweep(st, cells, ours, crew)
    if "foreground" in raw: st["game_foreground"] = bool(raw["foreground"])
    st["colony_exists"] = len(st["crew"]) > 0
    if "explore_done" in raw: st["explore_done"] = bool(raw["explore_done"])
    # --- her own marks: numbers stay numbers, everything else is a boolean ---
    for k, v in (lf.get("marks") or {}).items():
        st["mark_" + k] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else bool(v)
    for k in ("pawns_set", "assign_set", "beds_set", "stove_set", "bill_set"):
        st.setdefault("mark_" + k, False)
    return st


def _sweep(st, cells, ours, crew):
    meals = raw_food = wood = med = bp = foes = roofed = total = defence = 0
    res = {k: 0 for k in set(RESOURCES.values())}
    berry = healroot = wild = danger = mounts = fire = corpses = embr = 0; battery = False
    desig = {k: 0 for k in DESIGNATIONS.values()}
    bcells = {k: set() for k in BUILDING_KEYS}
    mount_defs = MOUNT_DEFS_DEFAULT
    for c in cells:
        bp += len(c.get("blueprintBuildDefs") or [])
        for dg in c.get("designations") or []:
            k = DESIGNATIONS.get((dg or {}).get("defName") if isinstance(dg, dict) else None)
            if k: desig[k] += 1
        xy = (c.get("x"), c.get("z"))
        for t in c.get("things", []):
            d = t.get("defName") or ""; cl = t.get("className") or ""; n = t.get("stackCount", 1)
            for k, test in BUILDING_KEYS.items():
                if test(d, cl): bcells[k].add((d, xy))
            if d.startswith("Meal"): meals += n
            elif d.startswith("Raw"): raw_food += n
            elif d == "WoodLog": wood += n
            elif "Medicine" in d: med += n
            elif d in RESOURCES: res[RESOURCES[d]] += n
            elif "Leather" in d: res["cloth"] += n
            elif d in ("Plant_Berry", "Plant_Strawberry_Wild"): berry += 1     # Plant_Berry UNVERIFIED; the other captured
            elif d in ("Plant_Healroot", "Plant_HealrootWild"): healroot += 1
            elif d == "Fire": fire += 1
            elif "Corpse" in cl: corpses += 1
            elif cl == "Verse.Pawn":
                lab = t.get("label") or ""
                nm = lab.split("<")[0].strip()
                if "," in lab:            # humanlikes carry ", <title>" in their label (captured)
                    if nm and nm not in ours: foes += 1
                elif d != "Human":
                    if d in NEVER_HUNT_DEFS or d.startswith("Bear_"): danger += 1
                    else: wild += 1
                    if d in mount_defs: mounts += 1
            if d == "Battery": battery = True
            if "Embrasure" in d and not d.startswith(("Blueprint_", "Frame_")): embr += 1
            if (("Turret" in d or d in ("Sandbags", "Barricade") or "Embrasure" in d)
                    and not d.startswith(("Blueprint_", "Frame_"))): defence += 1
        # the stores are the cells inside a food/main stockpile zone, read off the cell itself
        zone = json.dumps(c.get("zone") or "").lower()
        if "food" in zone or "main" in zone:
            total += 1; roofed += 1 if c.get("roofDefName") else 0
    st["days_of_food"] = round((meals * 0.9 + raw_food * 0.05) / (1.6 * max(1, len(crew))), 2)
    st.update({"meals": meals, "raw_food": raw_food, "wood": wood, "medicine": med, "blueprints": bp,
               "humanlikes_not_ours": foes, "defences_built": defence > 0})
    st.update(res)
    st.update(desig)
    for k, cs in bcells.items():
        n = _objects(cs)
        st[k] = n > 0 if k in BOOL_BUILDINGS else n
    st["has_power"] = st["power_generators"] > 0 or battery
    st.update({"berry_bushes": berry, "healroot_plants": healroot, "danger_animals_near": danger,
               "mount_candidates": mounts, "fire_cells": fire, "corpses": corpses, "embrasures": embr,
               "wild_game": max(0, wild - st.get("colony_animals", 0))})
    if total:
        st["store_roofed_fraction"] = roofed / total
        st["unroofed_store_cells"] = total - roofed
    # hostiles: the crowd counts as hostile only while a recent threat letter vouches for it, or the colonist list
    # itself names hostile pawns
    st["hostiles_on_map"] = max(foes if st.get("threat_letter") else 0, st.get("hostile_pawns_listed", 0))
    # wall_gaps is not measured: the perimeter rung stays disabled rather than fed a fixed 0


def _objects(cs):
    """Count connected groups of same-def cells (a multi-cell building is listed on each of its cells)."""
    left = set(cs); n = 0
    while left:
        d, (x, z) = left.pop(); n += 1; stack = [(x, z)]
        while stack:
            px, pz = stack.pop()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                k = (d, (px + dx, pz + dz))
                if k in left: left.discard(k); stack.append(k[1])
    return n


def _log_alert_labels(labels):
    try:
        old = set(json.load(open(ALERT_LOG, encoding="utf-8")))
    except Exception:
        old = set()
    new = old | {l for l in labels if l}
    if new != old:
        try:
            os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
            json.dump(sorted(new), open(ALERT_LOG, "w", encoding="utf-8"), indent=1)
        except Exception:
            pass


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


def tags(book, st, lf=None):
    """The PLC tag table: constants stay put, variables are recomputed from the empire's current size.

    Owner, 2026-10-10, verbatim: "with changaeable variables and constants as needed and maintained for a
    growing empire". So a colony of three and an empire of thirty read the same ladder and get different
    numbers, and the numbers are maintained here rather than scattered through the rungs.
    """
    lf = _ladder_file() if lf is None else lf
    tg = book.get("tags") or {}
    const = dict(tg.get("constants") or {})
    var = tg.get("variables") or {}
    n = max(1, len(st.get("crew") or []))
    home = st.get("home_cells")
    computed = {
        "FOOD_MIN_DAYS": 2 + 0.4 * n,
        "FOOD_COMFORT_DAYS": 2 * (2 + 0.4 * n),
        "MEAL_BILL_TARGET": 10 * n,
        "WOOD_RESERVE": 60 * n,
        "MEDICINE_RESERVE": 2 * n,
        "BEDS_NEEDED": n + 1,
        "COOLERS_PER_ROOM": 1,
        "TURRET_TARGET": 2 + n // 3,
        "STOCK_CELLS": 30 + 15 * n,
        "COMPONENT_RESERVE": 5 + n,
        "STEEL_RESERVE": 150 * n,
        "AID_CALL_FOES": 2 * n,
        "MOUNT_TARGET": n,
    }
    if isinstance(home, (int, float)):
        computed["EMBRASURE_TARGET"] = int(4 * math.sqrt(home))
    out = dict(const)
    overrides = lf.get("tags") or {}
    pod_squad = None
    for name, spec in var.items():
        v = overrides[name] if name in overrides else computed.get(name, spec.get("value"))
        if name == "POD_FUEL" and name not in overrides and pod_squad is not None:
            v = 150 * pod_squad
        try:
            v = float(v) if not isinstance(v, (int, float)) or isinstance(v, bool) else v
        except (TypeError, ValueError):
            v = spec.get("value")
        lo, hi = spec.get("min"), spec.get("max")
        if lo is not None: v = max(lo, v)
        if hi is not None: v = min(hi, v)
        v = round(v, 2) if isinstance(v, float) else v
        spec["value"] = v           # in memory only; the live setpoints are written to scratch/setpoints.json
        out[name] = v
        if name == "POD_SQUAD": pod_squad = v
    return out


def latch_name(rid):
    """The done-mark of a latched rung: lowercase, underscores, at most 40 characters (ladder_set's mark rule)."""
    return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"


def _latched(g):
    """Apply a rung's done-latch: when gets mark_<id>_done false, then ends with setting it true."""
    if not g.get("latch"):
        return g
    g = dict(g); name = latch_name(g["id"])
    g["when"] = dict(g.get("when") or {}); g["when"].setdefault("mark_" + name, False)
    step = "ladder_set mark %s true" % name
    g["then"] = list(g.get("then") or [])
    if not any(step in s for s in g["then"]): g["then"].append(step)
    return g


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


OPS = (">=", "<=", "!=", ">", "<")


def _holds(cond, st, tagvals=None):
    tagvals = tagvals or {}
    for key, want in cond.items():
        if key == "letter_matches":
            if not any(str(want).lower() in (l or "").lower() for l in st.get("letter_labels", [])): return False
            continue
        if key in st:
            got = st.get(key)
        elif key in tagvals:           # a tag can gate a rung directly (e.g. CAVALRY_ENABLED: ">0")
            got = tagvals[key]
        else:
            return False          # unmeasured is not the same as false: a rung cannot fire on a missing key
        if isinstance(want, bool):
            if bool(got) != want: return False
        elif isinstance(want, (int, float)):
            if got is None or isinstance(got, bool) or got != want: return False
        elif isinstance(want, str) and want[:1] in "<>!":
            op = next(o for o in OPS if want.startswith(o)) if any(want.startswith(o) for o in OPS) else None
            if op is None:
                st.setdefault("unresolved_conditions", []).append("%s %s" % (key, want)); return False
            ref = _bound(want[len(op):], st, tagvals)
            if ref is None:
                # an unresolved bound never passes silently: the rung does not fire and the reason is recorded
                st.setdefault("unresolved_conditions", []).append("%s %s" % (key, want))
                return False
            if got is None or isinstance(got, bool) or not isinstance(got, (int, float)): return False
            g = float(got)
            if not {">": g > ref, "<": g < ref, ">=": g >= ref, "<=": g <= ref, "!=": g != ref}[op]: return False
        elif isinstance(want, str):
            if str(got) != want: return False
    return True


def explain(g, st, tagvals):
    """The measured values behind a rung's conditions, so she can say WHY it fired."""
    out = {}
    for k in (g.get("when") or {}):
        if k == "letter_matches":
            out[k] = g["when"][k]
        else:
            out[k] = st.get(k, tagvals.get(k, "unmeasured"))
    return out


def rungs(book, lf):
    """Book rungs plus hers (hers replace a book rung of the same id), latches applied."""
    mine = {g["id"]: g for g in (lf.get("gates") or []) if g.get("id") and "priority" in g}
    allg = [g for g in book["gates"] if g["id"] not in mine] + list(mine.values())
    return [_latched(g) for g in allg]


def decide(st=None, every=False, book=None, lf=None, write=True):
    lf = _ladder_file() if lf is None else lf
    st = st if st is not None else state()
    book = book or json.load(open(PLAYBOOK, encoding="utf-8"))
    tagvals = tags(book, st, lf)
    st["tags"] = tagvals
    if write:
        # the playbook under docs/ is canonical and never rewritten by a read; the live setpoints go machine-local
        try:
            os.makedirs(os.path.dirname(SETPOINTS), exist_ok=True)
            tmp = SETPOINTS + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"tags": tagvals, "ts": time.time()}, f, indent=1)
            os.replace(tmp, SETPOINTS)
        except Exception:
            pass
    allg = rungs(book, lf)
    # marks: numeric defaults from the book; a boolean mark nobody has set yet reads false
    for k, v in ((book.get("marks") or {}).get("defaults") or {}).items():
        st.setdefault("mark_" + k, v)
    for g in allg:
        for k, w in (g.get("when") or {}).items():
            if k.startswith("mark_") and isinstance(w, bool): st.setdefault(k, False)
    # grace: the empire rungs wait until the opening has had START_GRACE_DAYS (the `always` rung never waits)
    gfrom = tagvals.get("GRACE_FROM_PRIORITY")
    grace = tagvals.get("START_GRACE_DAYS")
    # a rung marked disabled has an input nothing measures yet; it never fires, and the reason is kept on the state
    st["disabled_rungs"] = {g["id"]: g["disabled"] for g in allg if g.get("disabled")}
    allg = [g for g in allg if not g.get("disabled")]
    known = set((book.get("sensors") or {}).keys())
    st["unknown_keys"] = sorted({k for g in allg for k in (g.get("when") or {})
                                 if k != "letter_matches" and not k.startswith(("mark_", "alert_")) and k not in known
                                 and k not in tagvals and k not in st})
    def ok(g):
        w = g.get("when", {})
        if (isinstance(gfrom, (int, float)) and isinstance(grace, (int, float)) and g["id"] != "always"
                and gfrom <= g["priority"] < 99):
            w = dict(w); w.setdefault("day", ">%s" % grace)
        return _holds(w, st, tagvals)
    hits = [g for g in sorted(allg, key=lambda g: g["priority"]) if ok(g)]
    for g in hits:
        g["matched"] = explain(g, st, tagvals)
    return (hits if every else hits[:1] + [g for g in hits if g["id"] == "always"][:1]), st


if __name__ == "__main__":
    gates, st = decide(every="--all" in sys.argv)
    print("state:", json.dumps({k: v for k, v in st.items() if k != "crew"}, default=str))
    print("crew: ", st.get("crew"))
    for g in gates:
        print("\n== RUNG %s (priority %s)" % (g["id"], g["priority"]))
        print("   why:", g.get("why", "")[:160])
        print("   matched:", json.dumps(g.get("matched", {}), default=str)[:200])
        for i, step in enumerate(g["then"], 1): print("   %d. %s" % (i, step))
        for n in g.get("never", []): print("   NEVER:", n)
