#!/usr/bin/env python3
"""Print the current selection's inspect lines, which is the game telling you what it thinks.

A gate's inspect card names the exact step it is waiting on, and reading it beats reading a
pane that has to be scrolled. Shell quoting mangles a regex for this, so it lives in a file.

Usage:
    python .local/qa/inspect.py
    python .local/qa/inspect.py 159 169      # select that cell first
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
    port, token = _bridge.endpoint()
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=_bridge.TIMEOUT) as sock:
        sock.settimeout(_bridge.TIMEOUT)
        _bridge.exchange(sock, buf, "session/hello",
                         {"token": token, "bridgeVersion": "RimroomsInspect/1",
                          "platform": "windows", "launchId": str(uuid.uuid4())})
        if len(argv) >= 2:
            _bridge.exchange(sock, buf, "tools/call",
                             {"name": "rimworld/clear_selection", "arguments": {}})
            _bridge.exchange(sock, buf, "tools/call",
                             {"name": "rimworld/click_cell",
                              "arguments": {"x": int(argv[0]), "z": int(argv[1]), "button": "left"}})
        result = _bridge.exchange(sock, buf, "tools/call",
                                  {"name": "rimworld/get_selection_semantics", "arguments": {}})

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("label", "inspectString") and isinstance(value, str):
                    print("%s: %s" % (key, value))
                elif key == "inspectStringLines" and isinstance(value, list):
                    for line in value:
                        print("  | %s" % line)
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
