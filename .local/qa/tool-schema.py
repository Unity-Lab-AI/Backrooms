#!/usr/bin/env python3
"""Print the input schema of named bridge tools, so a call is written from the contract.

`bridge.py list` prints names only, and a name does not say what a tool takes. Driving the game
means calling tools that ACT, and guessing an argument shape on something like `start_debug_game`
is how a QA session ends up doing something nobody asked for.

Usage:
    python .local/qa/tool-schema.py start_debug_game click_ui_target save_game
    python .local/qa/tool-schema.py --grep scenario
"""
import importlib.util
import json
import os
import socket
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
_bridge = importlib.util.module_from_spec(_spec)
sys.modules["rr_bridge"] = _bridge
_spec.loader.exec_module(_bridge)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    grep = None
    if argv[0] == "--grep":
        grep = argv[1].lower()
        wanted = []
    else:
        wanted = [a.lower() for a in argv]

    port, token = _bridge.endpoint()
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=_bridge.TIMEOUT) as sock:
        sock.settimeout(_bridge.TIMEOUT)
        _bridge.exchange(sock, buf, "session/hello",
                         {"token": token, "bridgeVersion": "RimroomsToolSchema/1",
                          "platform": "windows", "launchId": str(uuid.uuid4())})
        listed = _bridge.exchange(sock, buf, "tools/list", {})
        tools = listed.get("tools") if isinstance(listed, dict) else listed

    for tool in tools:
        name = tool.get("name", "")
        short = name.split("/")[-1].lower()
        blob = json.dumps(tool, ensure_ascii=False).lower()
        if grep is not None:
            if grep not in blob:
                continue
        elif short not in wanted and name.lower() not in wanted:
            continue
        print("=" * 78)
        print(name)
        description = (tool.get("description") or "").strip()
        if description:
            print("  %s" % description[:400])
        schema = tool.get("inputSchema") or tool.get("input_schema") or {}
        properties = schema.get("properties") or {}
        required = schema.get("required") or []
        if not properties:
            print("  (no arguments)")
        for key in sorted(properties):
            spec = properties[key] or {}
            mark = "*" if key in required else " "
            kind = spec.get("type", "?")
            enum = spec.get("enum")
            extra = (" one of %s" % enum) if enum else ""
            note = (spec.get("description") or "").strip()
            print("  %s%-26s %-8s%s" % (mark, key, kind, extra))
            if note:
                print("      %s" % note[:220])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
