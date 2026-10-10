#!/usr/bin/env python3
"""List things on the map whose defName contains any given word, in one bridge session.

`bridge.py call` truncates at 60k characters, which a 32x32 cell read exceeds, so this talks to
the socket directly and reads the map in tiles.

Usage: python .local/qa/find-things.py Stove,Shelf,Bed [x0 z0 x1 z1]
"""
import importlib.util, json, os, socket, sys, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

def unwrap(r):
    for k in ("result", "structuredContent"):
        if isinstance(r, dict) and k in r: r = r[k]
    if isinstance(r, dict) and "content" in r and isinstance(r["content"], list):
        for c in r["content"]:
            if c.get("type") == "text":
                try: return json.loads(c["text"])
                except Exception: pass
    return r

words = sys.argv[1].split(",")
x0, z0, x1, z1 = (int(v) for v in sys.argv[2:6]) if len(sys.argv) > 5 else (0, 0, 300, 300)
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsFind/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    hits = {}
    for x in range(x0, x1, 32):
        for z in range(z0, z1, 32):
            r = unwrap(b.exchange(s, buf, "tools/call", {"name": "rimworld/get_cells_info", "arguments": {"x": x, "z": z, "width": min(32, x1 - x), "height": min(32, z1 - z)}}))
            for c in (r or {}).get("cells", []):
                for t in c.get("things", []):
                    n = t.get("defName", "")
                    if any(w.lower() in n.lower() for w in words):
                        hits.setdefault(n, []).append((c["x"], c["z"]))
for n, cells in sorted(hits.items()):
    print(n, len(cells), cells if os.environ.get("ALL") else cells[:12])
