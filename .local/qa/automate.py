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
import json, os, sys, time

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

def send(cmds):
    os.makedirs(FOLDER, exist_ok=True)
    before = os.path.getsize(OUTBOX) if os.path.exists(OUTBOX) else 0
    with open(INBOX, "a", encoding="utf-8") as f:
        for c in cmds:
            f.write(json.dumps(c) + "\n")
    print("sent %d commands to %s" % (len(cmds), INBOX))
    # the component eats the file within a second of game time; wait for the results it writes back
    for _ in range(40):
        time.sleep(1)
        if not os.path.exists(INBOX):
            break
    else:
        print("the command file is still there -- is the mod staged into the game's Mods folder, and is the game running?")
        return
    time.sleep(1)
    if os.path.exists(OUTBOX):
        with open(OUTBOX, encoding="utf-8", errors="replace") as f:
            f.seek(before)
            for line in f:
                try: print("  ", json.loads(line).get("result", line.strip())[:160])
                except Exception: print("  ", line.strip()[:160])

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
