"""Remove one faction row from Create World by its label, through the bridge (no real input)."""
import json, re, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
def call(n, a):
    return subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", n, json.dumps(a)],
                          capture_output=True, text=True, encoding="utf-8").stdout
out = call("rimworld/get_ui_layout", {})
pat = re.compile(r'"targetId":\s*"([^"]+)",\s*"kind":\s*"([^"]+)",\s*"source":\s*"([^"]*)",\s*"label":\s*("[^"]*"|null)', re.S)
els = [(m.group(1), m.group(2), m.group(4)) for m in pat.finditer(out)]
for i, (tid, kind, label) in enumerate(els):
    if label == json.dumps(sys.argv[1]) and kind == "label":
        btn = next((t for t, k, l in els[i + 1:i + 3] if k == "icon_button"), None)
        if not btn: sys.exit("no trash button after " + sys.argv[1])
        r = call("rimworld/click_ui_target", {"targetId": btn})
        print(sys.argv[1], "->", re.search(r'"message":\s*"([^"]*)"', r).group(1))
        break
else:
    sys.exit("not on the page: " + sys.argv[1])
