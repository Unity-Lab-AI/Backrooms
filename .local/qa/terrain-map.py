"""Print a character map of terrain/things over a rectangle, in 6x6 bridge chunks (the bridge truncates at 60k).
    python .local/qa/terrain-map.py x0 z0 x1 z1
. soil/buildable  m mud/marsh  ~ water  # wall  D door  R rock  b building  T tree  c chunk  o other thing  F fog  w/d/B wall/door/other blueprint  , rich soil  s sand  f floor  Z zone
"""
import json, subprocess, sys
x0, z0, x1, z1 = map(int, sys.argv[1:5])
ROCKS = {"Granite","Limestone","Sandstone","Marble","Slate","MineableSteel","MineableComponentsIndustrial","MineableGold","MineableSilver","MineablePlasteel","MineableUranium","MineableJade"}
grid = {}
for cx in range(x0, x1 + 1, 6):
    for cz in range(z0, z1 + 1, 6):
        w = min(6, x1 - cx + 1); h = min(6, z1 - cz + 1)
        out = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/get_cells_info",
                              json.dumps({"x": cx, "z": cz, "width": w, "height": h})],
                             capture_output=True, text=True).stdout
        d = json.loads(out[out.find("{"):])
        for c in d.get("cells", []):
            t = (c.get("terrainDefName") or "")
            bp = c.get("blueprintBuildDefs") or []
            if bp: ch = "w" if "Wall" in bp else ("d" if any("Door" in b for b in bp) else "B")
            elif c.get("fogged"): ch = "F"
            elif any("Wall" in d for d in c.get("solidThingDefs") or []): ch = "#"
            elif any("Door" in d for d in c.get("solidThingDefs") or []): ch = "D"
            elif any(d in ROCKS for d in c.get("solidThingDefs") or []): ch = "R"
            elif any(not (d.startswith("Plant_") or d.startswith("Chunk") or d.startswith("Filth") or "Conduit" in d) for d in c.get("solidThingDefs") or []): ch = "b"
            elif any(d.startswith("Plant_Tree") for d in c.get("solidThingDefs") or []): ch = "T"
            elif any(d.startswith("Chunk") for d in c.get("solidThingDefs") or []): ch = "c"
            elif "Water" in t or "Ice" in t: ch = "~"
            elif "Mud" in t or "Marsh" in t: ch = "m"
            elif c.get("thingCount"): ch = "o"
            elif "Tile" in t or "Floor" in t or "Carpet" in t or "Concrete" in t or "Paved" in t or "Plank" in t or "Flagstone" in t: ch = "f"
            elif "Rich" in t: ch = ","
            elif "Sand" in t: ch = "s"
            elif c.get("zone"): ch = "Z"
            else: ch = "."
            grid[(c["x"], c["z"])] = ch
print("     " + "".join(str((x // 10) % 10) if x % 10 == 0 else " " for x in range(x0, x1 + 1)))
for z in range(z1, z0 - 1, -1):
    print("%4d " % z + "".join(grid.get((x, z), "?") for x in range(x0, x1 + 1)))
