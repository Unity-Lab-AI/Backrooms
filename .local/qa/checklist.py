"""The empire checklist: every standing order the owner has given, checked again on every pass.

    python .local/qa/checklist.py                 # measure the base live, print FIX / LOOK / ok for every order
    python .local/qa/checklist.py --looked KEY    # record that a judgement item was inspected just now
    python .local/qa/checklist.py --follow "text" # queue a follow-up (e.g. wall a cell once its cooler is gone)
    python .local/qa/checklist.py --verified N    # drop follow-up N after seeing it done in game

Owner, 2026-10-09: "now make sure everything ive evr told you to do is a running check list that is never
complete and is always checking all things are done wto keep your empire moveing up".

It NEVER reports done. Each run:
  * MEASURED items read the live map (one bridge session) and the newest save (rotations) and list each
    problem by cell -- FIX lines are work to do now;
  * JUDGEMENT items can't be measured; the three least recently inspected print as INSPECT NOW, and
    --looked KEY stamps one as inspected (state in .claude/.checklist.json), so every item comes round again;
  * the first FIX becomes the stream's "now" goal (.claude/.stream-goals.json), so the goals the viewers
    hear are the real work.
empire.py does the fixing for the orders a script can fix (stock, self-tend, hunt, arms, abilities, drop
zone). This file is the full list. Every owner quote is in .local/qa/owner-quotes.txt.
"""
import importlib.util, json, os, re, socket, sys, time, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STATE = os.path.join(ROOT, ".claude", ".checklist.json")
GOALS = os.path.join(ROOT, ".claude", ".stream-goals.json")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
BASE = (100, 62, 200, 142)
FREEZER = (161, 83, 171, 97)
PERISH = re.compile(r"^(Meal|Raw|Meat_|Hay|Kibble|Milk|Egg|Plant.*Leaves|Berries|Corn|Rice|Potato|Ambrosia|Wort|MedicineHerbal|Healroot|Pemmican)")
DIRS = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}   # hot side of a cooler / over-wall cooler faces its rotation

# Judgement orders, owner's words. KEY: (owner quote, what to look at)
JUDGE = {
    "walls": ("fix all rooms with holes in walls / still holes in outer ball missing doors and shit",
              "walk the outer wall on screen; every gap is a door"),
    "paths": ("door in correct place no blocked pathing", "every room reachable; no wall across a hall"),
    "halls": ("you need to figure out you halls and whats suppose to have roof and not ... hallways that end nowhere",
              "halls roofed, every hall ends at a door"),
    "embrasure": ("you have holes in you embrasure fortifications / and a bunch without power so u can t shoot out",
                  "bastions closed and every remote embrasure powered"),
    "interior-embrasure": ("3 places with stupid embracers 1x1 in interior walls that do nothing replace with marble when u can",
                           "no 1x1 embrasure in an interior wall"),
    "power-area": ("nothing without power need one power gen place not spead all over and not not organized",
                   "every generator in the one power yard"),
    "bedrooms": ("where are all the bed rooms? why are people sleeping in the proisons", "a bedroom per colonist; cells for prisoners only"),
    "research": ("you should be upgrade the old benches and putting the research shit like multi analizers and computer",
                 "hi-tech benches, multi-analyzer, comms console"),
    "crops": ("you need to start making cash crops of all kinds", "growing zones for every cash crop that grows here"),
    "trade": ("start making money in tradeding and calling traders selling all ur junk / you need bulk good trader",
              "comms console: call or wait for a bulk trader, sell junk"),
    "silver-steel": ("order some silver from the company / better mine steel or order some", "silver and steel orders open or landed"),
    "storage-rooms": ("need a vault and storage rooms with lots of shelves / fix the freezer shit is stored wrong",
                      "a silver/valuables vault and shelf-lined storerooms; freezer shelves food only"),
    "prison-climate": ("prison need ac and heat and vents and stuff, i told you all rooms keep at it",
                       "every prison cell on a heater + cooler cluster"),
    "hospitality": ("need to start making money nneed guests and products to sell them in seles zone have u even used hospitality tab",
                    "Hospitality tab set; guest beds; sales area stocked"),
    "meals": ("cook bill maintained at 50 rather than 10", "kitchen bills on do-until 50"),
    "meds": ("meds in hospital", "medicine shelved in the hospital"),
    "fight": ("you need to mobilize when attacked and fight not run / never letting someone melle person or animal get close",
              "raid.py block ready; GUNS list current"),
    "camera": ("when under attack u need to focus on the action / maore hhighlighting in game images",
               "step.py --hostiles in fights; stream shots ringed"),
    "chat": ("make sure u always inguage with joins to stream and people are talking to you answe r them always",
             "chat-watch.py running; every line answered; a 'bear with me' line before every long job (\"NEVER FUCKING IGNORE CHAT TELL THEM IF U HAVE TO PROCESS SOMETHING\")"),
    "goals": ("dont forget to try and ask questions about what youu next move should be based on your over all goals",
              ".claude/.stream-goals.json question fresh"),
    "long-goal": ("if they done answer just keep toward your goals of empire world domination and space warfare",
                  "next step toward ship/empire on the roadmap"),
    "sustain": ("maintain ur colonists' needs / maintain and watch your resources", "moods, food days, rest"),
    "dissection": ("make the dissection room somewhere else and make that a path to the rest of the prisons", "the prison path is open"),
    "altar-wall": ("make a straight wall north of edge wall of the alter room / with door in it", "the wall and its door are built"),
}


def unwrap(r):
    for k in ("result", "structuredContent"):
        if isinstance(r, dict) and k in r: r = r[k]
    if isinstance(r, dict) and "content" in r:
        for c in r["content"]:
            if c.get("type") == "text":
                try: return json.loads(c["text"])
                except Exception: pass
    return r


def scan():
    """Every cell of the base box, one session -> {(x,z): cell dict}."""
    cells = {}; port, token = b.endpoint(); buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
        b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsChecklist/1", "platform": "windows", "launchId": str(uuid.uuid4())})
        for x in range(BASE[0], BASE[2], 25):
            for z in range(BASE[1], BASE[3], 20):
                r = unwrap(b.exchange(s, buf, "tools/call", {"name": "rimworld/get_cells_info", "arguments": {"x": x, "z": z, "width": min(25, BASE[2] - x), "height": min(20, BASE[3] - z)}}))
                for c in (r or {}).get("cells", []): cells[(c["x"], c["z"])] = c
        cols = unwrap(b.exchange(s, buf, "tools/call", {"name": "rimworld/list_colonists", "arguments": {}}))
    return cells, [c for c in (cols or {}).get("colonists", []) if c.get("humanlike")]


def defs(c): return [t.get("defName", "") for t in c.get("things", [])]
def kind(c):
    sd = c.get("solidThingDefs") or []; d = defs(c)
    if any("Door" in t or "Gate" in t for t in sd): return "door"
    if any("Wall" in t or "Embrasure" in t for t in sd) or any(t in ("Cooler", "Cooler_Over", "Vent", "Vent_Over") for t in d): return "wall"
    if not c.get("walkable", True): return "solid"
    return "in" if c.get("roofDefName") else "out"


def rooms(cells):
    rid, out = {}, []
    for p, c in cells.items():
        if kind(c) != "in" or p in rid: continue
        n = len(out); stack = [p]; rid[p] = n; cs = []
        while stack:
            q = stack.pop(); cs.append(q)
            for dx, dz in DIRS.values():
                nq = (q[0] + dx, q[1] + dz)
                if nq in cells and nq not in rid and kind(cells[nq]) == "in": rid[nq] = n; stack.append(nq)
        out.append(cs)
    return rid, out


def save_rots():
    d = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves")
    f = max((os.path.join(d, n) for n in os.listdir(d) if n.endswith(".rws")), key=os.path.getmtime)
    s = open(f, encoding="utf-8", errors="ignore").read(); rot = {}
    for m in re.finditer(r"<def>((?:Blueprint_|Frame_)?Cooler(?:_Over)?)</def>", s):
        blk = s[m.start():m.start() + 1500]; blk = blk[:blk.find("</thing>")] if "</thing>" in blk else blk
        p = re.search(r"<pos>\((\d+), \d+, (\d+)\)</pos>", blk); r = re.search(r"<rot>(\d)</rot>", blk)
        if p: rot[(int(p.group(1)), int(p.group(2)))] = int(r.group(1)) if r else 0
    return rot


def measured(cells, cols):
    rid, rs = rooms(cells); fix = []
    # HVAC: hot side outdoors
    rot = save_rots()
    for (x, z), c in cells.items():
        for d in defs(c):
            if re.fullmatch(r"(Blueprint_|Frame_)?Cooler(_Over)?", d):
                if (x, z) not in rot: continue          # placed after the last save: checked next pass
                dx, dz = DIRS[rot[(x, z)]]; h = cells.get((x + dx, z + dz))
                if h and kind(h) == "in":
                    fix.append(("hvac-hot", "%s (%d,%d) blows its heat into a roofed room at (%d,%d)" % (d, x, z, x + dx, z + dz)))
    # HVAC: every room conditioned, big rooms get more coolers
    def units_near(cs):
        n = {"cool": 0, "heat": 0, "vent": 0}; seen = set()
        for x, z in cs:
            for dx, dz in [(0, 0)] + list(DIRS.values()):
                p = (x + dx, z + dz)
                if p in seen or p not in cells: continue
                seen.add(p)
                for d in defs(cells[p]):
                    if "Cooler" in d: n["cool"] += 1
                    elif "Heater" in d: n["heat"] += 1
                    elif "Vent" in d: n["vent"] += 1
        return n
    for cs in rs:
        if len(cs) < 6: continue
        xs = [p[0] for p in cs]; zs = [p[1] for p in cs]; box = (min(xs), min(zs), max(xs), max(zs))
        # embrasure towers leak air: never conditioned (owner, 2026-10-09: "embrasures leak air dont condition")
        if any("Embrasure" in d for x, z in cs for dx, dz in DIRS.values() if (x + dx, z + dz) in cells for d in defs(cells[(x + dx, z + dz)])): continue
        u = units_near(cs)
        if not any(u.values()):
            fix.append(("hvac-room", "room %s size %d has no heater, cooler or vent" % (box, len(cs))))
        elif len(cs) >= 120 and u["cool"] < max(1, len(cs) // 120) and u["vent"] == 0:
            fix.append(("hvac-big", "room %s size %d has %d cooler(s): needs %d" % (box, len(cs), u["cool"], len(cs) // 120)))
    # walls: a roofed room cell touching open unroofed ground = a hole
    holes = sorted({(x + dx, z + dz) for cs in rs if len(cs) >= 6 for x, z in cs for dx, dz in DIRS.values()
                    if (x + dx, z + dz) in cells and kind(cells[(x + dx, z + dz)]) == "out"})
    if holes: fix.append(("holes", "%d open edge cells on roofed rooms, e.g. %s" % (len(holes), holes[:8])))
    # storage: nothing stored in hallways; perishables in the freezer; non-food out of it; all storage in beacon range
    beacons = [p for p, c in cells.items() if "OrbitalTradeBeacon" in defs(c)]
    store = [p for p, c in cells.items() if "Stockpile" in json.dumps(c.get("zone")) or any(d.startswith("Shelf") for d in defs(c))]
    hall = {i for i, cs in enumerate(rs) if len(cs) >= 6 and min(max(p[0] for p in cs) - min(p[0] for p in cs), max(p[1] for p in cs) - min(p[1] for p in cs)) <= 1}
    inhall = [p for p in store if rid.get(p) in hall]
    if inhall: fix.append(("hall-storage", "%d storage cells in hallways, e.g. %s" % (len(inhall), inhall[:6])))
    far = [p for p in store if not any(rid.get(p) == rid.get(q) and (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 <= 7.9 ** 2 for q in beacons)]
    if far: fix.append(("beacon", "%d storage cells outside trade-beacon range, e.g. %s" % (len(far), far[:6])))
    fx0, fz0, fx1, fz1 = FREEZER
    infz = lambda p: fx0 <= p[0] <= fx1 and fz0 <= p[1] <= fz1
    food = sorted({(d, x, z) for (x, z), c in cells.items() for d in defs(c) if PERISH.match(d) and not infz((x, z))})
    if food: fix.append(("food", "%d perishables outside the freezer, e.g. %s" % (len(food), food[:5])))
    junk = sorted({(d, x, z) for (x, z), c in cells.items() if infz((x, z)) for t in c.get("things", []) for d in [t.get("defName", "")]
                   if t.get("className", "").endswith("ThingWithComps") or d in ("Steel", "WoodLog", "Cloth", "Silver", "ComponentIndustrial")
                   if not PERISH.match(d) and not d.startswith(("Shelf", "Corpse"))})
    if junk: fix.append(("freezer-junk", "%d non-freezer things in the freezer, e.g. %s" % (len(junk), junk[:5])))
    # no torches; no simple research benches once hi-tech exists; generators in one place
    alld = [(d, p) for p, c in cells.items() for d in defs(c)]
    torches = [p for d, p in alld if d.startswith("TorchLamp") or d == "Torch"]
    if torches: fix.append(("torches", "torches at %s" % torches[:6]))
    simple = [p for d, p in alld if d == "SimpleResearchBench"]
    if simple: fix.append(("research", "%d simple research bench cells still standing, e.g. %s" % (len(simple), simple[:4])))
    gens = sorted({p for d, p in alld if "Generator" in d and not d.startswith(("Blueprint", "Frame"))})
    if gens:
        xs = [p[0] for p in gens]; zs = [p[1] for p in gens]
        if max(xs) - min(xs) > 16 or max(zs) - min(zs) > 16:
            fix.append(("power-area", "generators spread over %s..%s, not one yard: %s" % ((min(xs), min(zs)), (max(xs), max(zs)), gens[:8])))
    # main pathing (owner/chat, 2026-10-09: "fix main pathing all around"): walk from the throne room to every
    # room; a room nobody can reach, or one whose walk is 2.2x the straight distance, is a pathing fix
    from collections import deque
    start = (150, 103); dist = {start: 0}; dq = deque([start])
    walk = lambda p: p in cells and cells[p].get("walkable", True) and kind(cells[p]) in ("in", "out", "door")
    while dq:
        q = dq.popleft()
        for dx, dz in DIRS.values():
            n = (q[0] + dx, q[1] + dz)
            if n not in dist and walk(n): dist[n] = dist[q] + 1; dq.append(n)
    for cs in rs:
        if len(cs) < 6 or not any(64 <= z <= 136 and 108 <= x <= 192 for x, z in cs): continue
        xs = [p[0] for p in cs]; zs = [p[1] for p in cs]; box = (min(xs), min(zs), max(xs), max(zs))
        d = min((dist[p] for p in cs if p in dist), default=None)
        md = min(abs(x - start[0]) + abs(z - start[1]) for x, z in cs)
        if d is None: fix.append(("path", "room %s cannot be reached from the throne room" % (box,)))
        elif md > 8 and d > md * 2.2: fix.append(("path", "room %s is a %.1fx detour (%d steps for %d straight)" % (box, d / md, d, md)))
    # fortifications after a fight (owner, 2026-10-09: "fix the destroyed fortifications and walls and
    # embrasures"): any wall/embrasure/door/fence below 80% of its kind's best hit points
    import collections
    hp = collections.defaultdict(list)
    for p, cl in cells.items():
        for t in cl.get("things", []):
            dn = t.get("defName", "")
            if t.get("hitPoints") and re.search(r"Wall|Embrasure|Door|Fence|Gate|Turret|Barricade|Sandbag", dn) and not dn.startswith(("Blueprint", "Frame")):
                hp[(dn, t.get("stuffDefName"))].append((t["hitPoints"], p))
    hurt = [(dn, p) for (dn, _), v in hp.items() for h, p in v if h < max(x for x, _ in v) * 0.8]
    if hurt: fix.append(("damaged", "%d damaged fortifications (repair them), e.g. %s" % (len(hurt), hurt[:6])))
    # a bedroom with a gap merges into its hall and the outdoor-edge check never sees it (owner, 2026-10-09:
    # "your beds all still have holes in them"): flood each bed's floor and flag any room past 60 cells
    def flood(seed, cap=200):
        k0 = kind(cells[seed]); seen = {seed}; st = [seed]
        while st and len(seen) < cap:
            q = st.pop()
            for dx, dz in DIRS.values():
                n = (q[0] + dx, q[1] + dz)
                if n in cells and n not in seen and kind(cells[n]) == k0: seen.add(n); st.append(n)
        return seen
    done_beds = set()
    for d, p in alld:
        if not re.fullmatch(r"(Bed|DoubleBed|RoyalBed|HospitalBed|BedGuest)", d) or p in done_beds: continue
        f = flood(p); done_beds |= f
        if len(f) > (180 if d == "HospitalBed" else 60):   # a ward is a big room on purpose
            xs = [q[0] for q in f]; zs = [q[1] for q in f]
            fix.append(("bed-room-open", "%s at %s sits in a %d+ cell space %s: a wall gap or missing door" % (d, p, len(f), (min(xs), min(zs), max(xs), max(zs)))))
    # bedrooms: a bed per colonist outside the prison
    beds = [p for d, p in alld if re.fullmatch(r"(Bed|DoubleBed|RoyalBed|.*Bedroll.*|HospitalBed)", d)]
    if len(beds) < len(cols): fix.append(("bedrooms", "%d bed cells for %d colonists" % (len(beds), len(cols))))
    # hostiles never hidden: a fight is on screen (camera) -- the play loop handles it; drafted with melee?
    return fix


def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"looked": {}}
    if "--looked" in sys.argv:
        k = sys.argv[sys.argv.index("--looked") + 1]
        if k not in JUDGE: sys.exit("unknown key; keys: " + " ".join(JUDGE))
        st["looked"][k] = int(time.time()); json.dump(st, open(STATE, "w"), indent=1); print("looked", k); return
    st.setdefault("follow", [])
    if "--follow" in sys.argv:
        st["follow"].append(sys.argv[sys.argv.index("--follow") + 1]); json.dump(st, open(STATE, "w"), indent=1); print("queued"); return
    if "--verified" in sys.argv:
        print("verified:", st["follow"].pop(int(sys.argv[sys.argv.index("--verified") + 1]))); json.dump(st, open(STATE, "w"), indent=1); return
    cells, cols = scan()
    for i, t in enumerate(st["follow"]): print("FOLLOW %d %s" % (i, t))
    fix = measured(cells, cols)
    for k, line in fix: print("FIX   %-18s %s" % (k, line))
    due = sorted(JUDGE, key=lambda k: st["looked"].get(k, 0))
    for k in due[:3]:
        q, what = JUDGE[k]; print("LOOK  %-18s %s   (\"%s\")" % (k, what, q))
    print("CHECKLIST %d to fix, %d judgement items, oldest look %s -- the list never closes" % (
        len(fix), len(JUDGE), time.strftime("%H:%M", time.localtime(st["looked"].get(due[0], 0))) if st["looked"].get(due[0]) else "never"))
    st["last"] = {"ts": int(time.time()), "fix": [k for k, _ in fix]}
    json.dump(st, open(STATE, "w"), indent=1)
    if fix and os.path.exists(GOALS):   # the stream hears the real work
        WORDS = {"hvac-hot": "turning air conditioners so their heat blows outside", "hvac-room": "putting heating and cooling in every room",
                 "hvac-big": "adding coolers to the big rooms", "holes": "closing every gap in the fortress walls",
                 "bed-room-open": "sealing up the bedrooms", "hall-storage": "clearing storage out of the hallways",
                 "beacon": "getting every shelf inside trade-beacon range", "food": "moving food into the freezer",
                 "freezer-junk": "clearing junk out of the freezer", "torches": "swapping torches for real lamps",
                 "research": "upgrading the research benches", "power-area": "pulling the generators into one power yard",
                 "bedrooms": "building bedrooms for everyone"}
        g = json.load(open(GOALS)); g["now"] = WORDS.get(fix[0][0], "fixing up the fortress")
        json.dump(g, open(GOALS, "w"))


if __name__ == "__main__":
    main()
