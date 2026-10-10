#!/usr/bin/env python3
"""Ad-hoc direct-mode RimBridge client for live inspection.

Owner-directed, 2026-09-30: *"you can use the api mod you have that we installed last so u can
see wtf rimworld is doing"*. Scratch tool, `.local/` only -- the shipped QA client
`tools/qa/rimbridge_readonly.py` keeps its fixed allowlist.

Usage:
    python .local/qa/bridge.py list
    python .local/qa/bridge.py call <tool> '<json args>'
"""
import json
import re
import socket
import sys
import time
import uuid
from pathlib import Path

LOG = Path.home() / "AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
PROTOCOL = "gabp/1"
CLIENT = "RimroomsLiveInspect/1"
TIMEOUT = 45.0


def endpoint():
    text = LOG.read_text(encoding="utf-8", errors="replace")
    port = None
    token = None
    for line in text.splitlines():
        m = re.match(r"^\[RimBridge\] GABP server running standalone on port (\d+)\s*$", line)
        if m:
            port = int(m.group(1))
        m = re.match(r"^\[RimBridge\] Bridge token:\s*(\S+)\s*$", line)
        if m:
            token = m.group(1)
    if port is None or token is None:
        raise SystemExit("no live standalone bridge in the log")
    return port, token


def send(sock, method, params):
    rid = str(uuid.uuid4())
    body = json.dumps({"v": PROTOCOL, "id": rid, "type": "request",
                       "method": method, "params": params}).encode("utf-8")
    sock.sendall(("Content-Length: %d\r\nContent-Type: application/json\r\n\r\n"
                  % len(body)).encode("ascii") + body)
    return rid


def frame(sock, buf, deadline):
    def more():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SystemExit("bridge timed out")
        sock.settimeout(remaining)
        data = sock.recv(65536)
        if not data:
            raise SystemExit("bridge closed the connection")
        buf.extend(data)

    while b"\r\n\r\n" not in buf:
        more()
    split = buf.index(b"\r\n\r\n")
    headers = dict(
        (k.strip().lower(), v.strip())
        for k, v in (line.split(":", 1) for line in bytes(buf[:split]).decode("ascii").split("\r\n"))
    )
    length = int(headers["content-length"])
    start = split + 4
    while len(buf) < start + length:
        more()
    payload = bytes(buf[start:start + length])
    del buf[:start + length]
    return json.loads(payload.decode("utf-8"))


def exchange(sock, buf, method, params):
    rid = send(sock, method, params)
    deadline = time.monotonic() + TIMEOUT
    while True:
        message = frame(sock, buf, deadline)
        if message.get("type") == "event":
            continue
        if message.get("id") != rid:
            continue
        if message.get("error") is not None:
            raise SystemExit("bridge error: " + json.dumps(message["error"])[:2000])
        return message.get("result")


def main():
    port, token = endpoint()
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=TIMEOUT) as sock:
        sock.settimeout(TIMEOUT)
        exchange(sock, buf, "session/hello", {"token": token, "bridgeVersion": CLIENT,
                                              "platform": "windows", "launchId": str(uuid.uuid4())})
        if sys.argv[1] == "list":
            listed = exchange(sock, buf, "tools/list", {})
            tools = listed.get("tools") if isinstance(listed, dict) else listed
            needle = sys.argv[2].lower() if len(sys.argv) > 2 else ""
            for tool in tools:
                name = tool.get("name", "")
                if needle in name.lower():
                    print(name)
            return
        if sys.argv[1] == "scan":
            minx, minz, maxx, maxz = [int(v) for v in sys.argv[2:6]]
            blocked = {}
            terrain = {}
            roofs = {}
            total = 0
            for x in range(minx, maxx + 1):
                for z in range(minz, maxz + 1):
                    total += 1
                    r = exchange(sock, buf, "tools/call",
                                 {"name": "rimworld/get_cell_info", "arguments": {"x": x, "z": z}})
                    c = r["cell"]
                    terrain[c["terrainDefName"]] = terrain.get(c["terrainDefName"], 0) + 1
                    roofs[str(c["roofDefName"])] = roofs.get(str(c["roofDefName"]), 0) + 1
                    for d in c["solidThingDefs"]:
                        blocked.setdefault(d, []).append((x, z))
            print("cells scanned: %d" % total)
            print("terrain: %s" % sorted(terrain.items(), key=lambda kv: -kv[1]))
            print("roof: %s" % sorted(roofs.items(), key=lambda kv: -kv[1]))
            for d, cells in sorted(blocked.items(), key=lambda kv: -len(kv[1])):
                print("BLOCKED %-22s %4d cells  e.g. %s" % (d, len(cells), cells[:6]))
            return
        name = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(exchange(sock, buf, "tools/call", {"name": name, "arguments": args}),
                         indent=1)[:60000])


# Guarded, because this module is now IMPORTED as well as run. `facility-diff.py` reuses
# `endpoint` and `exchange` rather than copying them, and an unguarded `main()` meant the
# import executed a tools/call using the IMPORTER's argv -- which asked the bridge for a
# tool named `RR_AsyncIndustriesStart`.
if __name__ == "__main__":
    main()
