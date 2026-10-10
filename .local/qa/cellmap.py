"""ASCII map of a rect: python .local/qa/cellmap.py file.json -- letters: B battery, G generator, C cooler,
D door, # wall, E embrasure, - conduit, lowercase = blueprint/frame, . open, x impassable."""
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8")); r = d["rect"]
KEYS = [("Battery", "B"), ("Generator", "G"), ("Cooler", "C"), ("Door", "D"), ("Embrasure", "E"),
        ("Wall", "#"), ("Conduit", "-"), ("Vent", "V")]
g = {}
for c in d["cells"]:
    ch = "." if c["walkable"] else "x"
    names = [t["defName"] for t in c["things"] if not t["isBlueprint"] and not t["isFrame"]]
    bp = (c.get("blueprintBuildDefs") or []) + (c.get("frameBuildDefs") or [])
    for k, s in KEYS:
        if any(k.lower() in n.lower() for n in names): ch = s; break
        if any(k.lower() in n.lower() for n in bp): ch = s.lower() if s.isalpha() else {"#": "w", "-": "~"}.get(s, s); break
    g[(c["x"], c["z"])] = ch
for z in range(r["z"] + r["height"] - 1, r["z"] - 1, -1):
    print("%3d " % z + "".join(g.get((x, z), "?") for x in range(r["x"], r["x"] + r["width"])))
print("    " + "".join(str(x % 10) for x in range(r["x"], r["x"] + r["width"])))
