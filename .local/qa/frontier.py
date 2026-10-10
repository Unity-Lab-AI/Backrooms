"""Nearest-to-target explored walkable cell in a box, via bridge.  frontier.py X0 Z0 X1 Z1 TX TZ"""
import importlib.util, json, socket, sys, uuid, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "frontier/1", "platform": "windows", "launchId": str(uuid.uuid4())})
def call(n, a):
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a}); r = r.get("result", r)
    return r.get("structuredContent", r) if isinstance(r, dict) else r
x0, z0, x1, z1, tx, tz = map(int, sys.argv[1:7]); out = []
for xa in range(x0, x1 + 1, 32):
    for za in range(z0, z1 + 1, 32):
        w, h = min(32, x1 - xa + 1), min(32, z1 - za + 1)
        for c in call("rimworld/get_cells_info", {"x": xa, "z": za, "width": w, "height": h}).get("cells", []):
            if not c["fogged"] and c["walkable"] and not c["solidThingDefs"]: out.append((c["x"], c["z"]))
out.sort(key=lambda p: (p[0] - tx) ** 2 + (p[1] - tz) ** 2)
print(json.dumps(out[:5]))
