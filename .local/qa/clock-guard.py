"""Keep the clock running. A frozen game builds nothing, chops nothing, and starves the colony quietly.

Twice on 2026-10-09 the game was found paused with the crew's positions identical across checks -- once at
tick 928145, once at 1105629 -- while the colony had 0.2 days of food. The written order ("pause to SET things
up, then run time again in the same turn") was not enough on its own, so this enforces it in code.

It will NOT unpause when there is a reason to be paused:
  * a dialog is open and absorbing input (somebody has to answer it)
  * a raid letter is live (the owner may be posting the crew by hand)
Otherwise, if ticks do not move across two reads, it sets time running again and says so in the log.

    python .local/qa/clock-guard.py        # background service, checks about every 20 s
"""
import importlib.util, os, socket, time, uuid

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


HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

def session():
    port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
    b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "clockguard/1",
                                         "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf

s, buf = session()
def call(n, a=None):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r

def stamp():
    return time.strftime("%H:%M:%S")

while True:
    try:
        t1 = call("rimworld/get_game_info").get("ticksGame")
        time.sleep(3)
        t2 = call("rimworld/get_game_info").get("ticksGame")
        if t1 is not None and t1 == t2:
            ui = call("rimworld/get_ui_state")
            dialog = bool(ui.get("nonImmediateDialogWindowOpen") or ui.get("NonImmediateDialogWindowOpen"))
            letters = [l.get("label") or "" for l in call("rimworld/list_letters").get("letters", [])]
            raid = any("raid" in l.lower() for l in letters)
            if dialog:
                print(stamp(), "frozen at", t1, "-- a dialog is open, leaving it alone", flush=True)
            elif raid:
                print(stamp(), "frozen at", t1, "-- a raid letter is live, leaving it to the owner", flush=True)
            else:
                ok = call("rimworld/set_time_speed", {"speed": "Fast"}).get("success")
                print(stamp(), "frozen at", t1, "with nothing to answer -- running time again:", ok, flush=True)
    except Exception as e:
        print(stamp(), "bridge hiccup:", str(e)[:80], flush=True)
        try: s, buf = session()
        except Exception: pass
    time.sleep(20)
