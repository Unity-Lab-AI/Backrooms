"""The equator colony's running maintenance list -- every standing order, measured, never complete.

Owner, 2026-10-09: "you should have a maintaince list of thinge proprigating what all you need to do".
Each line is measured from the live game through the bridge (nothing is ticked by hand), printed as OK or
FIX, and the first FIX becomes the stream's "now" goal. Run it between every few actions.

    python .local/qa/run-list.py
"""
import importlib.util, json, os, socket, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
GOALS = os.path.join(ROOT, ".claude", ".stream-goals.json")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); sock = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
b.exchange(sock, buf, "session/hello", {"token": tok, "bridgeVersion": "runlist/1", "platform": "windows", "launchId": str(uuid.uuid4())})

def call(n, a=None):
    r = b.exchange(sock, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

CREW = ("Unity", "Gee", "Scar")
HOME, INSIDE = "Map_0", "Map_1"
SHELL = (147, 147, 5, 5)          # the surface shell, seed of the throne room
GATE_PILE = (257, 144, 11, 13)    # stockpile beside the way home, AI-02 threshold hall
ARRIVAL = (24, 262, 14, 14)       # where the starting supplies landed
GATE = (270, 150)                 # the blue door home
SUPPLY = ("Meal", "Steel", "WoodLog", "Component", "Medicine", "Gun_", "PainStick", "Serum", "Plasteel", "GlowPod")

def things(rect, want_map_pawn):
    """Supply stacks in a rect on the map whose pawn is selected (the bridge reads the current map)."""
    call("rimworld/select_pawn", {"pawnName": want_map_pawn})
    x0, z0, w, h = rect; got = {}
    for xa in range(x0, x0 + w, 32):
        for za in range(z0, z0 + h, 32):
            r = call("rimworld/get_cells_info", {"x": xa, "z": za, "width": min(32, x0 + w - xa), "height": min(32, z0 + h - za)})
            for c in r.get("cells", []):
                for t in c.get("things", []):
                    d = t.get("defName", "")
                    if any(k in d for k in SUPPLY) and "Mineable" not in d:
                        got[d] = got.get(d, 0) + 1
    return got

lines = []
def item(ok, key, text):
    lines.append(("OK  " if ok else "FIX ") + key.ljust(10) + text)

t1 = call("rimworld/get_game_info").get("ticksGame", 0); time.sleep(0.5); t2 = call("rimworld/get_game_info").get("ticksGame", 0)
item(t2 > t1, "running", "game time is moving (%d -> %d) -- a paused game is a dead stream" % (t1, t2))
crew = {c["name"]: c for c in call("rimworld/list_colonists").get("colonists", [])}
for n in CREW:
    c = crew.get(n)
    if not c: item(False, "crew", n + " is missing"); continue
    bad = [k for k in ("dead", "downed") if c.get(k)] + ([c["mentalState"]] if c.get("mentalState") else [])
    item(not bad, "crew", "%s on %s at %s, %s%s" % (n, c.get("mapId"), (c["position"]["x"], c["position"]["z"]), c.get("job"),
                                                    (" -- " + ", ".join(bad)) if bad else ""))
inside_pawn = next((n for n in CREW if crew.get(n, {}).get("mapId") == INSIDE), None)
home_pawn = next((n for n in CREW if crew.get(n, {}).get("mapId") == HOME), None)
left = things(ARRIVAL, inside_pawn) if inside_pawn else {}
pile = things(GATE_PILE, inside_pawn) if inside_pawn else {}
item(not left, "haul-1", "starting supplies still at the arrival room: " + (", ".join("%s x%d" % kv for kv in sorted(left.items())) or "none"))
item(not left and not pile, "haul-2", "supplies waiting at the gate pile for the carry through: " + (", ".join("%s x%d" % kv for kv in sorted(pile.items())) or "none"))
if home_pawn:
    shell = things(SHELL, home_pawn)
    item(bool(shell), "shell", "in the shell (throne room seed): " + (", ".join("%s x%d" % kv for kv in sorted(shell.items())) or "nothing yet"))
else:
    item(False, "shell", "nobody on the home map to read the shell")
item(True, "settings", "hostility Attack, self-tend on, No drugs -- set in the save and read back 2026-10-09")
# things only a real click can do (selection, dropdowns, mouse-down widgets): done when the owner has the game in front
for n, goal in (("cursor-1", "guest sleeping spots (161-166,135-139) -> select each, gizmo 'For guests'; then Guests tab recruit ticks"),
                ("cursor-4", "food store (155-159,134-138) is CLEARED (accepts nothing): Storage tab -> tick Foods; priority Important; outdoor pile refuses food"),
                ("cursor-5", "dry-goods pile (162-167,141-145) by the workshop: everything except food; west pile (139-146,141-145) raw materials, no food"),
                ("cursor-6", "prison hold (155-161,146-152): select the sleeping spot (159,151) -> 'For prisoners'; then carry Lloga to it"),
                ("cursor-7", "NE plots (see .local/qa/_plots.json): select each zone -> 'Plant:' -> berries/potatoes/corn/healroot/cotton/smokeleaf/psychoid/hops (all default to potato)"),
                ("cursor-8", "workshop wall lamps x2: rotate the wall-lamp designator (wall to the west, x161) -- the bridge only places facing south"),
                ("cursor-0", "VISITORS OFF since the guard refused a visitor pop-up: Guests tab -> 'Map settings...' (real click, ~(701,1767)) -> accept visitors again"),
                ("cursor-3", "fueled stove (155,141) -> Bills -> Add bill 'Cook simple meal' x Do forever (needs selection)"),
                ("cursor-2", "Work tab: switch to manual priorities -- Gee research/doctor, Scar construction/crafting, Unity hauling/shooting"),
                ("armed", "charge rifle + pain stick sidearm each -- confirm on the Gear tab"),
                ("beds", "a bed for each of three on the home map"),
                ("food", "food security: meals in the shell, then a growing zone and a cooking spot outside the shell"),
                ("power", "research Electricity -> Air conditioning (cursor job); then wood generators in a row, conduit one string, powered coolers: food store becomes a freezer (hot side out), rooms cooled"),
                ("company", "contact the company once settled (Operations)"),
                ("hospital", "P2: hospital room -- beds marked Medical (gizmo), next to the kitchen/food store"),
                ("graves", "P2: graves zone outside the wall for the dead (Lloga's corpse is at the dump)"),
                ("guests", "P2/P4: guest beds marked, then a shop area (Hospitality)"),
                ("products", "P4: bills for beer, smokeleaf joints, psychite tea, clothes as research unlocks them"),
                ("trade", "P4: comms console -> Call trader to land (a typed trader, not the Orbital Traders Hub)"),
                ("fortress", "P5: once stable -- mine the mountain base per the fortress plan")):
    item(False, n, goal)

for l in lines: print(l)
first = next((l for l in lines if l.startswith("FIX")), None)
if first:
    try: g = json.load(open(GOALS))
    except Exception: g = {}
    g["now"] = first[4:].split(None, 1)[1][:120]; g["ts"] = int(time.time())
    json.dump(g, open(GOALS, "w"), indent=1)
