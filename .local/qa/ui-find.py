"""Full (untruncated) get_ui_layout; print targets whose label contains any given word.
    python .local/qa/ui-find.py Machining,Microelectronics [--click Label]"""
import importlib.util, json, os, socket, sys, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
words = sys.argv[1].split(","); click = sys.argv[sys.argv.index("--click") + 1] if "--click" in sys.argv else None
port, token = b.endpoint(); buf = bytearray()
with socket.create_connection(("127.0.0.1", port), timeout=b.TIMEOUT) as s:
    b.exchange(s, buf, "session/hello", {"token": token, "bridgeVersion": "RimroomsUiFind/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    r = b.exchange(s, buf, "tools/call", {"name": "rimworld/get_ui_layout", "arguments": {}})
    found = []
    def walk(n):
        if isinstance(n, dict):
            if "targetId" in n and isinstance(n.get("label"), str): found.append(n)
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(r)
    hit = None
    for e in found:
        if any(w.lower() in e["label"].lower() for w in words):
            print(e["targetId"], e.get("kind"), repr(e["label"][:60]), "actionable=%s" % e.get("actionable"))
            if click and e["label"].strip() == click and e.get("actionable"): hit = e
    if hit:
        r = b.exchange(s, buf, "tools/call", {"name": "rimworld/click_ui_target", "arguments": {"targetId": hit["targetId"]}})
        print("clicked", hit["targetId"], json.dumps(r)[:200])
