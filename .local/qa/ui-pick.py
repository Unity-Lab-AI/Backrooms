"""Click a UI target with the game's own cursor parked on it (posted WM_MOUSEMOVE, never the owner's cursor), then
optionally pick a float-menu entry by label prefix.   ui-pick.py TARGET_ID|@label  [OPTION_PREFIX]"""
import importlib.util, socket, uuid, json, ctypes, time, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "pick/1", "platform": "windows", "launchId": str(uuid.uuid4())})
def call(n, a):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a}); r = r.get("result", r); return r.get("structuredContent", r)
def targets():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("targetId") and o.get("screenRect"): out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(call("rimworld/get_ui_layout", {})); return out
u = ctypes.WinDLL("user32"); g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
def park(r):
    x = int((r["x"] + r["width"] / 2) * 2); y = int((r["y"] + r["height"] / 2) * 2)
    u.PostMessageW(g, 0x0200, 0, (y << 16) | x); time.sleep(0.25)
key = sys.argv[1]; T = targets()
def inside(o, x, y):
    r = o["screenRect"]; return r["x"] <= x <= r["x"] + r["width"] and r["y"] <= y <= r["y"] + r["height"]
if key.startswith("pos:"):
    px, py = map(float, key[4:].split(","))
    t = next((o for o in T if o.get("actionable") and inside(o, px, py)), None)
else:
    t = next((o for o in T if (o["targetId"] == key) or (key.startswith("@") and (o.get("label") or "").startswith(key[1:]))), None)
if not t: sys.exit("no target " + key)
park(t["screenRect"]); print(call("rimworld/click_ui_target", {"targetId": t["targetId"]}).get("message")); time.sleep(0.5)
if len(sys.argv) > 2:
    T = targets(); opts = [o for o in T if (o.get("label") or "").startswith(sys.argv[2])]
    print("options seen:", sorted(set((o.get("label") or "")[:40] for o in T if o["targetId"].split(":")[2] != t["targetId"].split(":")[2]))[:20])
    if opts:
        park(opts[0]["screenRect"]); print(call("rimworld/click_ui_target", {"targetId": opts[0]["targetId"]}).get("message"))
    else: print("option not found")
