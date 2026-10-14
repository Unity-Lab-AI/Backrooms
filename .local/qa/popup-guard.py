"""Pop-up guard (owner, 2026-10-09: "make sure pops ups dont monkey wrentch everything"). Every 3 s: if a dialog
that swallows input is open, a harmless one (naming, plain notice with only OK/Close) is accepted at once through
the bridge; anything that asks for a real decision is left alone, written to .claude/.popup.json for Claude, and
announced on stream once. Click scripts check .claude/.popup.json and wait while it is set."""
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

# Run 5 (owner, 2026-10-13: "its not working she frooze"): the game window was MINIMIZED. A minimized Unity window
# stops presenting frames, so OBS held the last frame on stream, every screenshot timed out and the Crashlanded intro
# dialog sat unseen while the game waited on it. Every pass: a minimized RimWorld window is restored WITHOUT taking
# focus and pushed to the bottom of the z-order -- it keeps rendering behind whatever the owner is doing and never
# covers his desktop (owner: "i cant see my desktop when tabbing out of it").
import ctypes
_u32 = ctypes.windll.user32 if os.name == "nt" else None
if _u32 is not None:
    _u32.FindWindowW.restype = ctypes.c_void_p
    _u32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
    _u32.IsIconic.argtypes = [ctypes.c_void_p]
    _u32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
    _u32.SetWindowPos.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
def unminimize_game():
    """True when the game window was minimized and has just been restored behind the owner's windows."""
    if _u32 is None: return False
    h = _u32.FindWindowW(None, "RimWorld by Ludeon Studios")
    if not h or not _u32.IsIconic(h): return False
    _u32.ShowWindow(h, 4)                                                    # SW_SHOWNOACTIVATE: restore, no focus
    _u32.SetWindowPos(h, ctypes.c_void_p(1), 0, 0, 0, 0, 0x0010 | 0x0002 | 0x0001)   # HWND_BOTTOM, NOACTIVATE|NOMOVE|NOSIZE
    return True
FLAG = os.path.join(ROOT, ".claude", ".popup.json"); SAY = os.path.join(ROOT, ".claude", "tools", "unity-say.py")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
def session():
    port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
    b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "popup/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf
s, buf = session()
def call(n, a=None):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r); return r.get("structuredContent", r)
INSPECT_TABS = {"Health", "Needs", "Bio", "Social", "Gear", "Log", "Character", "Training", "Prisoner", "Guest"}
HARMLESS = ("Dialog_NamePlayerFactionAndSettlement", "Dialog_NamePlayerFaction", "Dialog_NamePlayerSettlement", "Dialog_MessageBox", "Dialog_Info")
IGNORE = ("MainTabWindow", "MiniMap", "ImmediateWindow", "Page_", "Dialog_Options", "WorldInspectPane", "MapPreview")
told = set(); since = {}
REFUSE = {"refuse", "reject", "decline", "ignore", "no", "deny", "don't pay", "do not pay", "send away", "turn away", "not now", "dismiss"}
KEEP = ("Dialog_Trade", "Dialog_FormCaravan", "Dialog_BillConfig", "Dialog_ManageAreas", "Dialog_Slider")
def buttons():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("targetId") and o.get("actionable") and o.get("label"): out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout")); return out
while True:
    try:
        if unminimize_game():
            print("game window was minimized -- restored behind the owner's windows (the stream and screenshots need its frames)", flush=True)
        st = call("rimworld/get_ui_state")
        wins = [w for w in st.get("windows", []) if w.get("absorbInputAroundWindow") and not any(k in (w.get("type") or "") for k in IGNORE)]
        if not wins:
            if os.path.exists(FLAG): os.remove(FLAG)
            since.clear()                      # the five-minute wait starts again for the next box
        for w in wins:
            t = w.get("type") or ""
            labs = [o.get("label") for o in buttons()]
            body = " ".join(l for l in labs if l and len(l) > 25).lower()
            visit = next((o for o in buttons() if any(w in (o.get("label") or "").lower() for w in ("always let them come", "assure safety", "let them come", "welcome", "you can stay"))), None)
            if visit and ("visit" in body or "guest" in body or "arrived" in body or "you can stay" in (visit.get("label") or "").lower()):
                # owner, 2026-10-09: "that one was to accept visitor if u refussed that pop up non will arrive until u set it in hospitality tab"
                call("rimworld/click_ui_target", {"targetId": visit["targetId"]}); print("visitors welcomed:", visit.get("label"), flush=True)
                subprocess.run([sys.executable, SAY, "fact: visitors arrived at the colony and I welcomed them in"], env=dict(os.environ, UNITY_NO_GLANCE="1"))
            elif (set(l for l in labs if l and len(l) <= 25) - INSPECT_TABS) <= {"OK", "Close", "Jump to location"} and                     set(l for l in labs if l) & {"OK", "Close"}:
                # an info-only window (a notice she opened, a letter body): its only real choice is Close/OK -- close
                # it so it cannot block her turn (live: the gate notice sat open seven minutes)
                btn = next(o for o in buttons() if o.get("label") in ("OK", "Close"))
                call("rimworld/click_ui_target", {"targetId": btn["targetId"]}); print("closed info window", t, flush=True)
            elif any(k in t for k in HARMLESS) and set(l for l in labs if l) & {"OK", "Close", "Accept", "Confirm"} and not set(labs) - {"OK", "Close", "Accept", "Confirm", "Randomize", None} - set(l for l in labs if l and len(l) > 25):
                btn = next(o for o in buttons() if o.get("label") in ("OK", "Close", "Accept", "Confirm"))
                call("rimworld/click_ui_target", {"targetId": btn["targetId"]}); print("accepted", t, flush=True)
            elif (any(any(w in (l or "").lower() for w in ("pay", "silver", "tribute", "give ", "hand over", "ransom")) for l in labs)
                  and next((o for o in buttons() if (o.get("label") or "").split(" (")[0].strip().lower() in REFUSE), None)
                  and not any(k in t for k in KEEP)):
                # only a DEMAND is refused (it asks us to pay or give); a free offer -- a joiner, a gift -- is left for Claude
                # owner, 2026-10-09: "anser them most are shit never pay them" -- refuse, decline, ignore; never pay
                btn = next(o for o in buttons() if (o.get("label") or "").split(" (")[0].strip().lower() in REFUSE)
                call("rimworld/click_ui_target", {"targetId": btn["targetId"]}); print("refused", t, btn.get("label"), flush=True)
                subprocess.run([sys.executable, SAY, "fact: someone demanded we pay them and I refused"], env=dict(os.environ, UNITY_NO_GLANCE="1"))
            elif (time.time() - since.setdefault(t, time.time()) > 300
                  and next((o for o in buttons() if any(k in (o.get("label") or "").lower() for k in ("you can stay", "can join", "let them join", "accept them"))), None)):
                # live, 10-10: a "can they stay?" box froze the game ten minutes while her turns went elsewhere; a free
                # extra colonist is the obvious yes for a crew of three, so after five minutes it is taken
                btn = next(o for o in buttons() if any(k in (o.get("label") or "").lower() for k in ("you can stay", "can join", "let them join", "accept them")))
                call("rimworld/click_ui_target", {"targetId": btn["targetId"]}); print("joiner accepted after 5 min", t, flush=True); since.pop(t, None)
                subprocess.run([sys.executable, SAY, "fact: someone asked to join the colony and I said yes, they can stay"], env=dict(os.environ, UNITY_NO_GLANCE="1"))
            else:
                json.dump({"ts": time.time(), "type": t, "text": [l for l in labs if l and len(l) > 25][:4], "options": [l for l in labs if l and len(l) <= 25][:12]}, open(FLAG, "w"))
                if t not in told:
                    told.add(t); print("needs a decision:", t, [l for l in labs if l][:8], flush=True)
                    subprocess.run([sys.executable, SAY, "fact: a choice just popped up in the game and I am thinking it over"], env=dict(os.environ, UNITY_NO_GLANCE="1"))
    except Exception:
        try: s, buf = session()
        except Exception: pass
    time.sleep(6)
