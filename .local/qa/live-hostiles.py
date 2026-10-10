"""Live non-colonist humans on the map (corpses excluded). python .local/qa/live-hostiles.py"""
import json, os, re, subprocess, sys
o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/list_colonists", "{}"], capture_output=True, text=True, encoding="utf-8").stdout
mine = {(c["position"]["x"], c["position"]["z"]) for c in json.loads(o[o.find("{"):]).get("colonists", [])}
f = subprocess.run([sys.executable, ".local/qa/find-things.py", "Human", "0", "0", "300", "300"], capture_output=True, text=True, env=dict(os.environ, ALL="1")).stdout
cells = [tuple(map(int, m)) for line in f.splitlines() if line.startswith("Human ") for m in re.findall(r"\((\d+), (\d+)\)", line)]
print([c for c in cells if c not in mine])
