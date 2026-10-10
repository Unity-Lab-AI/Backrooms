"""List blueprint/frame defs per cell over a rect: python .local/qa/blueprints.py x z w h"""
import json, subprocess, sys
x, z, w, h = map(int, sys.argv[1:5])
out = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/get_cells_info",
                      json.dumps({"x": x, "z": z, "width": w, "height": h})], capture_output=True, text=True).stdout
for c in json.loads(out[out.find("{"):])["cells"]:
    b = c.get("blueprintBuildDefs") or []; f = c.get("frameBuildDefs") or []
    s = [d for d in c.get("solidThingDefs") or [] if not d.startswith(("Plant_", "Filth"))]
    if b or f or s: print(c["x"], c["z"], "bp=", b, "frame=", f, "solid=", s)
