"""Client for the mod's own automation component: every cursor-only job, done with no mouse and no screen.

Owner, 2026-10-10, verbatim: *"you need to fix that sahit so it doent ever need the fucking screeen and MY
DAMN MOUSE"* / *"build it into the mod if you have to"*. So it is built in:
`RimroomsAutomationComponent` reads a command file once a second and sets the field directly.

    python .local/qa/automate.py famine      # Gee off research onto food, the whole crew's grid for a famine
    python .local/qa/automate.py crops       # every camp field gets its own crop
    python .local/qa/automate.py nosow       # the far main-base plots stop sowing
    python .local/qa/automate.py bills       # simple meals until 30, butcher forever
    python .local/qa/automate.py camparea    # pin all three to the Camp area
    python .local/qa/automate.py all
    python .local/qa/automate.py raw '{"cmd":"set_work_priority","pawn":"Gee","work":"Cook","level":1}'

Results come back in the component's outbox, so nothing is reported as done on faith.
"""
import json, os, sys, time, uuid

CONFIG = os.path.expandvars(r"%USERPROFILE%/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config")
FOLDER = os.path.join(CONFIG, "RimroomsAutomation")
INBOX = os.path.join(FOLDER, "inbox.jsonl")
OUTBOX = os.path.join(FOLDER, "outbox.jsonl")
HERE = os.path.dirname(os.path.abspath(__file__))

# the nine camp fields, in the order they were drawn, with the crop each one is for
CROPS = [("Plant_Berry", 154, 116), ("Plant_Potato", 160, 116), ("Plant_Corn", 166, 116),
         ("Plant_Healroot", 154, 110), ("Plant_Rice", 160, 110), ("Plant_Cotton", 166, 110),
         ("Plant_Smokeleaf", 160, 159), ("Plant_Psychoid", 166, 159), ("Plant_Hops", 138, 158)]

# a famine grid: the researcher cooks and harvests until the larder is full again
FAMINE = [("Gee", "Research", 4), ("Gee", "Cook", 1), ("Gee", "PlantCutting", 1), ("Gee", "Hauling", 2),
          ("Scar", "PlantCutting", 1), ("Scar", "Cooking", 2), ("Scar", "Hauling", 2),
          ("Unity", "Hunting", 1), ("Unity", "PlantCutting", 1), ("Unity", "Hauling", 1)]

def map_arg(map_id):
    """The bridge names maps 'Map_<n>'; the mod's optional "map" field takes the bare uniqueID n."""
    m = str(map_id or "")
    return m[4:] if m.startswith("Map_") else m


def exchange(cmds, wait_s=40, map_id=None):
    """Send commands and return [(command, result or None)] in order, each result matched to ITS command.

    Every command carries its own "id"; the mod echoes it on the result line. A result line from an older build
    without the id field still matches, because the mod echoes the command text (with the id inside) as well.
    Nothing is taken from another caller's lines, from the inbox disappearing, or from a byte offset alone."""
    os.makedirs(FOLDER, exist_ok=True)
    tag = uuid.uuid4().hex[:10]
    sent = []
    for i, c in enumerate(cmds):
        c = dict(c)
        m = c.pop("map", map_id)
        # id and map go first, as quoted strings, so no bare value earlier on the line can swallow them
        c = dict({"id": "%s-%d" % (tag, i)}, **({"map": map_arg(m)} if m not in (None, "") else {}), **c)
        sent.append(c)
    lines = {c["id"]: json.dumps(c) for c in sent}
    echo = {i: l.replace('"', "'") + " -> " for i, l in lines.items()}
    before = os.path.getsize(OUTBOX) if os.path.exists(OUTBOX) else 0
    with open(INBOX, "a", encoding="utf-8") as f:
        for c in sent:
            f.write(lines[c["id"]] + "\n")
    got = {}
    t0 = time.time()
    while len(got) < len(sent) and time.time() - t0 < wait_s:
        time.sleep(1)
        if not os.path.exists(OUTBOX): continue
        if os.path.getsize(OUTBOX) < before: before = 0           # the outbox was rotated: read it whole
        with open(OUTBOX, encoding="utf-8", errors="replace") as f:
            f.seek(before); rows = f.read().splitlines()
        for row in rows:
            try: d = json.loads(row)
            except Exception: continue
            res = str(d.get("result", ""))
            rid = d.get("id")
            if rid in echo:
                got[rid] = res[len(echo[rid]):] if res.startswith(echo[rid]) else res.split(" -> ", 1)[-1]
            elif rid is None:
                rid = next((i for i, e in echo.items() if res.startswith(e)), None)
                if rid: got[rid] = res[len(echo[rid]):]
    return [(c, got.get(c["id"])) for c in sent]


def send(cmds, map_id=None):
    print("sending %d commands to %s" % (len(cmds), INBOX))
    out = exchange(cmds, map_id=map_id)
    for c, r in out:
        print("  ", "%s -> %s" % (c.get("cmd"), r if r is not None else "NO RESULT (is the mod staged and the game running?)")[:160])
    return out

def build(which):
    out = []
    if which in ("famine", "all"):
        out += [{"cmd": "set_work_priority", "pawn": p, "work": w, "level": l} for p, w, l in FAMINE]
    if which in ("crops", "all"):
        out += [{"cmd": "set_zone_plant", "x": x, "z": z, "plant": p} for p, x, z in CROPS]
    if which in ("nosow", "all"):
        try:
            bounds = json.load(open(os.path.join(HERE, "_ne_plots_bounds.json"), encoding="utf-8"))
            out += [{"cmd": "set_zone_sowing", "x": r["x0"] + 1, "z": r["z0"] + 1, "allow": False}
                    for r in bounds.values()]
        except Exception:
            pass
    if which in ("bills", "all"):
        out += [{"cmd": "add_bill", "x": 155, "z": 141, "recipe": "CookMealSimple", "count": 30},
                {"cmd": "add_bill", "x": 152, "z": 141, "recipe": "ButcherCorpseFlesh"}]
    if which in ("beds", "all"):
        out += [{"cmd": "set_bed_owner", "x": 159, "z": 151, "owner": "prisoner"}]
    if which in ("camparea", "all"):
        out += [{"cmd": "set_area", "pawn": p, "area": "Camp"} for p in ("Gee", "Scar", "Unity")]
    return out

if __name__ == "__main__":
    what = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    if what == "raw":
        send([json.loads(sys.argv[2])])
    else:
        cmds = build(what)
        if not cmds:
            raise SystemExit("nothing to send for '%s' -- try famine, crops, nosow, bills, beds, camparea, all" % what)
        send(cmds)
