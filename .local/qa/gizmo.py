#!/usr/bin/env python3
"""Select the thing at a cell and run its gizmo with this exact label, by the id the bridge lists.

Usage: python .local/qa/gizmo.py <x> <z> "<label>"
"""
import importlib.util, json, os, socket, sys, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
x, z, label = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsGizmo/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    b.exchange(s, buf, "tools/call", {"name": "rimworld/clear_selection", "arguments": {}})
    b.exchange(s, buf, "tools/call", {"name": "rimworld/click_cell", "arguments": {"x": x, "z": z, "button": "left"}})
    r = b.exchange(s, buf, "tools/call", {"name": "rimworld/list_selected_gizmos", "arguments": {}})
    pairs = []
    def walk(n):
        if isinstance(n, dict):
            if str(n.get("id", "")).startswith("selection-gizmo:") and "label" in n: pairs.append((n["id"], n["label"]))
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(r)
    gid = next((g for g, l in pairs if l == label), None)
    if gid is None:
        print("no gizmo %r at (%d,%d); have: %s" % (label, x, z, [l for _, l in pairs])); sys.exit(1)
    out = json.dumps(b.exchange(s, buf, "tools/call", {"name": "rimworld/execute_gizmo", "arguments": {"gizmoId": gid}}))
    print(label, "->", "ok" if '"success": true' in out else out[:200])
