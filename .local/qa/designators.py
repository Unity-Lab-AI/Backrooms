#!/usr/bin/env python3
"""Print designator ids and labels for an Architect category, optionally filtered.

`bridge.py` truncates a tools/call result at 60,000 characters, and a category listing with
dropdowns flattened is longer than that, so the JSON could not be parsed from its output. This
asks the bridge directly and walks the full result.

Usage:
    python .local/qa/designators.py power conduit
    python .local/qa/designators.py zone
"""
import importlib.util
import os
import socket
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
_bridge = importlib.util.module_from_spec(_spec)
sys.modules["rr_bridge"] = _bridge
_spec.loader.exec_module(_bridge)


def walk(node, out):
    if isinstance(node, dict):
        # A designator row carries its id under `id`; `designatorId` is the selection state's
        # field and names only whatever is currently selected.
        if str(node.get("id", "")).startswith("architect-designator:"):
            out.append((node.get("id"), node.get("label"), node.get("disabled"),
                        node.get("disabledReason")))
        for value in node.values():
            walk(value, out)
    elif isinstance(node, list):
        for value in node:
            walk(value, out)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    category = argv[0]
    needle = argv[1].lower() if len(argv) > 1 else ""
    port, token = _bridge.endpoint()
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=_bridge.TIMEOUT) as sock:
        sock.settimeout(_bridge.TIMEOUT)
        _bridge.exchange(sock, buf, "session/hello",
                         {"token": token, "bridgeVersion": "RimroomsDesignators/1",
                          "platform": "windows", "launchId": str(uuid.uuid4())})
        result = _bridge.exchange(sock, buf, "tools/call",
                                  {"name": "rimworld/list_architect_designators",
                                   "arguments": {"categoryId": "architect-category:" + category}})
    found = []
    walk(result, found)
    for designator, label, disabled, reason in found:
        text = "%s" % label
        if needle and needle not in text.lower() and needle not in str(designator).lower():
            continue
        flag = "  [disabled: %s]" % reason if disabled else ""
        print("%-64s %s%s" % (designator, text, flag))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
