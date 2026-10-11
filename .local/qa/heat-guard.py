"""Heat guard (owner, 2026-10-09: "one heat wave and your dead in 3 minutes"). Watches the letter stack; on a
heat wave, every colonist on the home map is ordered through the gate into the Backrooms (indoors ~60F), and
the stream is told. Runs in the background; checks every 5 s."""
import importlib.util, json, os, socket, subprocess, sys, time, uuid

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

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
def session():
    port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
    b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "heat/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf
s, buf = session()
def call(n, a=None):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r
cspec = importlib.util.spec_from_file_location("camp", os.path.join(HERE, "camp.py")); camp = importlib.util.module_from_spec(cspec); cspec.loader.exec_module(camp)
GATE = tuple(camp.conf()["gate"]); seen = set()    # the gate cell is configuration (.local/qa/_camp.json)
WAVE_MAX_S = 1200          # how long one heat wave keeps retrying the crew that has not crossed yet
RETRY_S = 60               # a pawn ordered through the gate is ordered again if still home after this
waves = {}                 # letter id -> (time the wave was first seen, home map then)
ordered = {}               # pawn name -> time it was last ordered through the gate
while True:
    try:
        for l in call("rimworld/list_letters").get("letters", []):
            lid = l.get("letterId") or l.get("id"); lab = (l.get("label") or "")
            if lid in seen: continue
            seen.add(lid)
            if "heat wave" in lab.lower():
                # home is fixed when the wave arrives, while the crew is still there: once they cross, the map
                # with most colonists is the Backrooms, not home
                waves[lid] = (time.time(), camp.home_map(call("rimworld/list_colonists").get("colonists", [])))
                subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "tools", "unity-say.py"),
                                "Heat wave, chat! Everybody into the backrooms right now, it is nice and cool in there. Go go go."])
        for lid, (t0, home_map) in list(waves.items()):
            home = [c for c in call("rimworld/list_colonists").get("colonists", [])
                    if c.get("factionIsPlayer", True) and c.get("mapId") == home_map]
            if not home:
                # verified: nobody is left on the home map
                print("heat wave: crew crossed through the gate", flush=True)
                del waves[lid]; ordered.clear(); continue
            if time.time() - t0 > WAVE_MAX_S:
                print("heat wave: gave up, still home: %d" % len(home), flush=True)
                del waves[lid]; ordered.clear(); continue
            for c in home:
                if time.time() - ordered.get(c["name"], 0) < RETRY_S: continue
                call("rimworld/select_pawn", {"pawnName": c["name"]})
                call("rimworld/set_draft", {"pawnName": c["name"], "drafted": False})
                call("rimworld/right_click_cell", {"x": GATE[0], "z": GATE[1]})
                r = call("rimworld/execute_context_menu_option", {"label": "Enter the gate"})
                ordered[c["name"]] = time.time()
                if isinstance(r, dict) and (r.get("isError") or r.get("success") is False):
                    print("heat wave: order refused for one pawn, retrying later", flush=True)
    except Exception as e:
        try: s, buf = session()
        except Exception: pass
    time.sleep(15)
