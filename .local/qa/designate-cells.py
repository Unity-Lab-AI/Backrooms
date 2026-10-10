#!/usr/bin/env python3
"""Apply one designator to a list of cells in one bridge session, printing what took.

Usage: python .local/qa/designate-cells.py <designatorId> "x,z x,z ..."
"""
import importlib.util, json, os, socket, sys, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
did = sys.argv[1]; cells = [tuple(int(v) for v in p.split(",")) for p in sys.argv[2].split()]
port, token = b.endpoint(); buf = bytearray(); ok = 0
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsDesignate/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    for x, z in cells:
        r = b.exchange(s, buf, "tools/call", {"name": "rimworld/apply_architect_designator", "arguments": {"designatorId": did, "x": x, "z": z}})
        txt = json.dumps(r)
        if '"success": true' in txt and '"applied": 0' not in txt: ok += 1
        else: print("refused", x, z, txt[:160])
    b.exchange(s, buf, "tools/call", {"name": "rimworld/click_cell", "arguments": {"x": cells[0][0], "z": cells[0][1], "button": "right"}})
print("applied", ok, "of", len(cells))
