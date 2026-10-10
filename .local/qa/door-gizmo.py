"""Gizmo on a door that has a conduit under it (cycles selection): python .local/qa/door-gizmo.py x z "<label prefix>"|__list__"""
import importlib.util, json, socket, sys, uuid
spec = importlib.util.spec_from_file_location("rr_bridge", ".local/qa/bridge.py"); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
x, z, want = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "x/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    b.exchange(s, buf, "tools/call", {"name": "rimworld/clear_selection", "arguments": {}})
    for _ in range(3):
        b.exchange(s, buf, "tools/call", {"name": "rimworld/click_cell", "arguments": {"x": x, "z": z, "button": "left"}})
        r = b.exchange(s, buf, "tools/call", {"name": "rimworld/list_selected_gizmos", "arguments": {}})
        pairs = []
        def walk(n):
            if isinstance(n, dict):
                if str(n.get("id", "")).startswith("selection-gizmo:") and "label" in n: pairs.append((n["id"], n["label"], n.get("disabledReason")))
                for v in n.values(): walk(v)
            elif isinstance(n, list):
                for v in n: walk(v)
        walk(r)
        if any("gate operator" in l for _, l, _ in pairs): break
    if want == "__list__":
        for _, l, d in pairs: print(l, "|", d or "")
        sys.exit(0)
    gid = next((g for g, l, _ in pairs if l.startswith(want)), None)
    if not gid: print("missing", want); sys.exit(1)
    out = json.dumps(b.exchange(s, buf, "tools/call", {"name": "rimworld/execute_gizmo", "arguments": {"gizmoId": gid}}))
    print(want, "->", "ok" if '"success": true' in out else out[:200])
