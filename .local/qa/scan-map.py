"""Scan the current map through the bridge: doors, gates and notable things, with fog state. -> _scan.json"""
import json, os, subprocess, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
def call(n, a):
    return json.loads(subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", n, json.dumps(a)],
                                     capture_output=True, text=True, encoding="utf-8").stdout)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 250
doors, kinds, walk = [], collections.Counter(), 0
for x0 in range(0, N, 32):
    for z0 in range(0, N, 32):
        r = call("rimworld/get_cells_info", {"x": x0, "z": z0, "width": 32, "height": 32})
        for c in r.get("cells", []):
            if c.get("walkable") and not c.get("fogged"): walk += 1
            for t in c.get("things", []):
                d = t.get("defName") or t.get("def") or ""
                kinds[d] += 1
                if "door" in d.lower() or "gate" in d.lower() or "portal" in d.lower() or "Emerg" in d:
                    doors.append({"x": c["x"], "z": c["z"], "def": d, "label": t.get("label"), "fogged": c.get("fogged"), "id": t.get("thingId") or t.get("id")})
json.dump({"doors": doors, "kinds": kinds}, open(os.path.join(HERE, "_scan.json"), "w"), indent=1)
print("visible walkable", walk); print("doors/gates", len(doors))
for d in doors: print(d)
print(kinds.most_common(40))
