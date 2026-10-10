#!/usr/bin/env python3
"""Walk one drafted pawn toward a room through fog until it stands inside the room's rectangle.

Each step reads the map, picks the revealed walkable cell nearest the room's centre that has not
already failed, orders a move there, and plays a short burst. A step that leaves the pawn where it
was marks that cell as unreachable and the next one is tried.

Usage: python .local/qa/explore-to.py <pawn> <x> <z> <width> <height> [steps]
"""
import importlib.util, json, os, socket, sys, uuid, math
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
pawn, rx, rz, rw, rh = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
steps = int(sys.argv[6]) if len(sys.argv) > 6 else 30
cx, cz = rx + rw // 2, rz + rh // 2
port, token = b.endpoint(); buf = bytearray()
def call(s, name, args): return b.exchange(s, buf, "tools/call", {"name": name, "arguments": args})
def find(n, key):
    if isinstance(n, dict):
        if key in n: return n[key]
        for v in n.values():
            r = find(v, key)
            if r is not None: return r
    elif isinstance(n, list):
        for v in n:
            r = find(v, key)
            if r is not None: return r
    return None
def position(s):
    r = call(s, "rimworld/list_colonists", {})
    out = []
    def walk(n):
        if isinstance(n, dict):
            if n.get("name") == pawn and "position" in n: out.append((n["position"]["x"], n["position"]["z"], n.get("job")))
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(r)
    return out[0] if out else None
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsExplore/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    call(s, "rimworld/select_pawn", {"pawnName": pawn})
    call(s, "rimworld/set_draft", {"pawnName": pawn, "drafted": True})
    failed = set()
    for step in range(steps):
        px, pz, job = position(s)
        if rx <= px < rx + rw and rz <= pz < rz + rh:
            print("inside the room at", (px, pz), "after", step, "steps"); break
        # Read a window spanning the pawn and the room, in tiles the bridge accepts.
        x0, x1 = max(0, min(px, rx) - 10), min(299, max(px, rx + rw) + 10)
        z0, z1 = max(0, min(pz, rz) - 10), min(299, max(pz, rz + rh) + 10)
        best = None
        for tx in range(x0, x1 + 1, 32):
            for tz in range(z0, z1 + 1, 32):
                r = call(s, "rimworld/get_cells_info", {"x": tx, "z": tz, "width": min(32, x1 - tx + 1), "height": min(32, z1 - tz + 1)})
                for c in find(r, "cells") or []:
                    if c["fogged"] or not c["walkable"] or (c["x"], c["z"]) in failed: continue
                    if any("Wall" in t.get("defName", "") for t in c.get("things", [])): continue
                    d = math.hypot(c["x"] - cx, c["z"] - cz)
                    if best is None or d < best[0]: best = (d, c["x"], c["z"])
        if best is None: print("no revealed cell to aim at"); break
        call(s, "rimworld/select_pawn", {"pawnName": pawn})
        call(s, "rimworld/click_cell", {"x": best[1], "z": best[2], "button": "right"})
        call(s, "rimworld/play_for", {"durationMs": 4000, "speed": "Fast"})
        nx, nz, job = position(s)
        print("step", step, "aim", best[1:], "dist %.0f" % best[0], "pawn", (nx, nz), job)
        if (nx, nz) == (px, pz): failed.add((best[1], best[2]))
    call(s, "rimworld/set_draft", {"pawnName": pawn, "drafted": False})
