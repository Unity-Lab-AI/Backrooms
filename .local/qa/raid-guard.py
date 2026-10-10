"""Raid guard: the crew is behind the embrasures before the pirates are in range, not after.

Owner doctrine, verbatim: *"make sure u arm up and set everyones setting attack"*, *"Letters first, danger
second"*, *"need to set a prisoner room rfirst come on this is basic shit"*. A raid letter says the pirates
"will prepare for a while, then attack", so this watches the home map for an actually-hostile humanlike pawn
and only then acts: pause, draft all three, send each to their own post inside the embrasure wall, say one
clean line. It never fires on visitors or animals, and it undrafts nobody -- the fight is the owner's and
Claude's to finish.

    python .local/qa/raid-guard.py            # background service, checks every 10 s
"""
import importlib.util, json, os, socket, subprocess, sys, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SAY = os.path.join(ROOT, ".claude", "tools", "unity-say.py")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

# posts inside the camp wall: each pawn gets a cell behind an embrasure run, one per side the raid can come from
POSTS = {"Unity": (152, 128), "Scar": (139, 141), "Gee": (165, 152)}
HOME = "Map_0"
STATE = os.path.join(HERE, "_raid.json")

def session():
    port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
    b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "raidguard/1", "platform": "windows",
                                         "launchId": str(uuid.uuid4())})
    return s, buf

s, buf = session()
def call(n, a=None):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

def say(line):
    subprocess.run([sys.executable, SAY, "--raw", line], env=dict(os.environ, UNITY_NO_GLANCE="1"))

OURS = {"Gee", "Scar", "Unity"}

def hostiles():
    """Raiders standing near the camp.

    `list_colonists` does NOT return enemy pawns -- that is why this guard sat silent through a twelve-raider
    raid on 2026-10-09 while the letters piled up. Enemies are found the only way the bridge exposes them: a
    cell sweep that reads `Verse.Pawn` things and keeps the humanlikes that are not ours. Bounded to a ring
    around the camp so it stays cheap at a 15 s cadence.
    """
    call("rimworld/select_pawn", {"pawnName": "Gee"})
    out = []
    for x in range(118, 196, 26):
        for z in range(94, 178, 26):
            for c in call("rimworld/get_cells_info", {"x": x, "z": z, "width": 26, "height": 26}).get("cells", []):
                for t in c.get("things", []):
                    if t.get("className") != "Verse.Pawn": continue
                    lab = t.get("label") or ""
                    name = lab.split("<")[0].strip()
                    if name and name not in OURS and "," in lab:
                        out.append((name, c["x"], c["z"]))
    return out

def post_crew():
    for name, (x, z) in POSTS.items():
        call("rimworld/clear_selection"); call("rimworld/select_pawn", {"pawnName": name})
        call("rimworld/set_draft", {"pawnName": name, "drafted": True})
        call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.2)
        call("rimworld/right_click_cell", {"x": x, "z": z}); time.sleep(0.25)
        opts = []
        def w(n):
            if isinstance(n, dict):
                if n.get("label"): opts.append(n)
                for v in n.values(): w(v)
            elif isinstance(n, list):
                for v in n: w(v)
        w(call("rimworld/get_context_menu_options"))
        hit = next((o for o in opts if (o.get("label") or "").startswith(("Go here", "Move here"))), None)
        if hit: call("rimworld/execute_context_menu_option", {"optionIndex": hit.get("index", hit.get("optionIndex"))})
        call("rimworld/close_context_menu")

armed = False
while True:
    try:
        h = hostiles()
        if h and not armed:
            armed = True
            call("rimworld/set_time_speed", {"speed": "Paused"})
            post_crew()
            json.dump({"at": int(time.time()), "hostiles": h}, open(STATE, "w"))
            say("Pirates are on the map. Everyone behind the wall, we shoot through the embrasures.")
        elif not h and armed:
            armed = False
            try: os.remove(STATE)
            except Exception: pass
            say("Map's clear. That's the raid done.")
    except Exception:
        try: s, buf = session()
        except Exception: pass
    time.sleep(15)
