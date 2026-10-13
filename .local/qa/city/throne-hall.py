"""Throne hall layout (owner: throne at the head north facing south, table centred, light balls and
speakers, pews, all symmetrical on the rule of thirds). Interior x143-157, z99-107, mirrored on x150.
Re-runnable: already-placed items are rejected harmlessly. python .local/qa/city/throne-hall.py"""
import json, subprocess, sys
D = "architect-designator:"
ITEMS = [  # (designator, x, z, rotation)  rotation 0 N, 2 S
    ("furniture:build-throne", 150, 107, 2),
    ("ideology:build-loudspeaker", 148, 107, 2), ("ideology:build-loudspeaker", 152, 107, 2),
    ("ideology:build-lightball", 146, 107, 0), ("ideology:build-lightball", 154, 107, 0),
    ("furniture:build-brazier", 143, 107, 0), ("furniture:build-brazier", 157, 107, 0),
    ("furniture:build-brazier", 143, 99, 0), ("furniture:build-brazier", 157, 99, 0),
    ("furniture:build-table3x3c", 150, 103, 0),
] + [("ideology:build-pew", x, z, 0) for z in (100, 102, 104) for x in (145, 155)]
DEF = {"throne": "Throne", "loudspeaker": "Loudspeaker", "lightball": "LightBall", "brazier": "Brazier",
       "table3x3c": "Table3x3c", "pew": "Pew"}
for des, x, z, rot in ITEMS:
    # Skip a cell that already holds the item, built or blueprinted: placing again over a built one
    # lays a "replace stuff" blueprint and the crew tears it down to rebuild it.
    info = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/get_cell_info",
                           json.dumps({"x": x, "z": z})], capture_output=True, text=True, encoding="utf-8").stdout
    if '"%s' % DEF[des.split("build-")[1]] in info or '"Blueprint_%s' % DEF[des.split("build-")[1]] in info:
        print("have", des.split(":")[1], x, z); continue
    o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/apply_architect_designator",
                        json.dumps({"designatorId": D + des, "x": x, "z": z, "rotation": rot})],
                       capture_output=True, text=True, encoding="utf-8").stdout
    ok = '"acceptedCellCount": 1' in o
    print("ok  " if ok else "WAIT", des.split(":")[1], x, z)
