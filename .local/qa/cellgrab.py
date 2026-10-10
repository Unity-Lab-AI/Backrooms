"""Fetch get_cells_info row by row (the bridge truncates ~60 KB) into one JSON:
    python .local/qa/cellgrab.py X Z W H out.json"""
import json, subprocess, sys
x, z, w, h, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cells = []
for zz in range(z, z + h):
    for xx in range(x, x + w, 20):
        o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/get_cells_info",
                            json.dumps({"x": xx, "z": zz, "width": min(20, x + w - xx), "height": 1})],
                           capture_output=True, text=True, encoding="utf-8").stdout
        cells += json.loads(o[o.find("{"):])["cells"]
json.dump({"rect": {"x": x, "z": z, "width": w, "height": h}, "cells": cells}, open(out, "w"))
