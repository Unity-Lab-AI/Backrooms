"""Add a faction on Create World: Add... then the row's own button, through the bridge (no real input).
The layout capture truncates near the bottom of the Add list, so the row button is taken by position:
each row is label, info icon, row button."""
import json, re, subprocess, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
def call(n, a):
    return subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", n, json.dumps(a)],
                          capture_output=True, text=True, encoding="utf-8").stdout
pat = re.compile(r'"targetId":\s*"([^"]+)",\s*"kind":\s*"([^"]+)",\s*"source":\s*"([^"]*)",\s*"label":\s*("[^"]*"|null)', re.S)
def els(): return [(m.group(1), m.group(2), m.group(4)) for m in pat.finditer(call("rimworld/get_ui_layout", {}))]
e = els()
if not any(":2:" in t and l == json.dumps(sys.argv[1]) for t, k, l in e):
    # a RimWorld float menu shuts when the mouse is far from it, so park the game's own cursor on Add first
    # (a posted WM_MOUSEMOVE: the owner's real cursor never moves)
    import ctypes
    u = ctypes.WinDLL("user32"); g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
    u.PostMessageW(g, 0x0200, 0, (993 << 16) | 2419); time.sleep(0.4)
    add = next(t for t, k, l in e if l == '"Add..."'); call("rimworld/click_ui_target", {"targetId": add}); time.sleep(1); e = els()
for t, k, l in e:
    if ":2:" in t and l == json.dumps(sys.argv[1]):
        a, b, n = t.rsplit(":", 2)
        r = call("rimworld/click_ui_target", {"targetId": "%s:%s:%d" % (a, b, int(n) + 2)})
        print(sys.argv[1], "->", re.search(r'"message":\s*"([^"]*)"', r).group(1)); break
else:
    sys.exit("not in the Add list: " + sys.argv[1])
