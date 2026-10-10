"""Where are the non-colonist humans (raiders)? python .local/qa/hostiles.py"""
import json, subprocess, sys, re
def call(t, a={}):
    o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", t, json.dumps(a)], capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(o[o.find("{"):]) if "{" in o else {}
mine = {(c["position"]["x"], c["position"]["z"]) for c in call("rimworld/list_colonists").get("colonists", [])}
o = subprocess.run([sys.executable, ".local/qa/find-things.py", "Human"], capture_output=True, text=True,
                   env=dict(__import__("os").environ, ALL="1")).stdout
cells = [tuple(map(int, m)) for m in re.findall(r"\((\d+), (\d+)\)", o)]
print([c for c in cells if c not in mine])
