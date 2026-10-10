"""Wall-only map: W wall, D door, f frame, b blueprint, R rock/unwalkable, . open.

    python .local/qa/wall-map.py x0 z0 x1 z1
"""
import json, subprocess, sys
def call(t, a):
    o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", t, json.dumps(a)], capture_output=True, text=True).stdout
    return json.loads(o[o.find("{"):]) if "{" in o else {}
x0, z0, x1, z1 = map(int, sys.argv[1:5])
K = ("Wall", "Door", "Fence", "Embrasure", "Gate")
G = {}
for cz in range(z0, z1 + 1, 6):
    for cx in range(x0, x1 + 1, 6):
        r = call("rimworld/get_cells_info", {"x": cx, "z": cz, "width": min(6, x1 - cx + 1), "height": min(6, z1 - cz + 1)})
        for c in r.get("cells") or []:
            s = c.get("solidThingDefs") or []; bp = c.get("blueprintBuildDefs") or []; fr = c.get("frameBuildDefs") or []
            ch = "."
            if any(any(k in n for k in K) for n in s): ch = "D" if any("Door" in n for n in s) else "W"
            elif any(any(k in n for k in K) for n in fr): ch = "f"
            elif any(any(k in n for k in K) for n in bp): ch = "b"
            elif not c.get("walkable"): ch = "R"
            G[(c["x"], c["z"])] = ch
for z in range(z1, z0 - 1, -1):
    print("%4d " % z + "".join(G.get((x, z), " ") for x in range(x0, x1 + 1)))
print("     " + "".join(str(x % 10) for x in range(x0, x1 + 1)))
print("left:", sum(1 for v in G.values() if v in "bf"))
