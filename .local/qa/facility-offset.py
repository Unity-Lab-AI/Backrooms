# -*- coding: utf-8 -*-
"""Where the authored facility actually sits on the live map.

**The first live snapshot read 2,116 cells of unexplored mountain**, because the authored layout is
in its own coordinates and `GenStep_Headquarters` **offsets it onto whatever map the player chose**.
The owner's map is 300x300, the layout's footprint is 44x44 at (8, 8), and the facility is therefore
at **(128, 128)** -- which is exactly where their camera was sitting.

The arithmetic is reimplemented from `HeadquartersLayout.Offset`, which cannot be imported across
the language boundary. **So it is quoted here line for line and the live offset is CONFIRMED against
the game rather than trusted:** `confirm()` reads the cell where the authored gate console should
be and checks the right thing is standing on it. A reimplementation nobody checks is the second
copy that drifts.

    int offsetX = (mapSize.x - extent.Width) / 2 - extent.minX;
    int offsetZ = (mapSize.z - extent.Height) / 2 - extent.minZ;
    int maxX = mapSize.x - EdgeMargin - 1 - extent.maxX;     // EdgeMargin = 8
    int minX = EdgeMargin - extent.minX;
    clamp offsetX into [minX, maxX], same for Z
"""
import importlib.util
import os
import socket

HERE = os.path.dirname(os.path.abspath(__file__))
EDGE_MARGIN = 8


def extent(plan):
    """The authored footprint as (minX, minZ, maxX, maxZ), inclusive, from the rooms alone.

    `HeadquartersLayout.Extent` takes it from the rooms, because buildings, doors and conduits are
    placed inside rooms by construction and the generator throws if they are not.
    """
    rooms = plan["rooms"]
    if not rooms:
        return None
    min_x = min(r[0] for r in rooms)
    min_z = min(r[1] for r in rooms)
    max_x = max(r[0] + r[2] - 1 for r in rooms)
    max_z = max(r[1] + r[3] - 1 for r in rooms)
    return min_x, min_z, max_x, max_z


def offset(plan, map_size):
    box = extent(plan)
    if box is None:
        return 0, 0
    min_x, min_z, max_x, max_z = box
    width = max_x - min_x + 1
    height = max_z - min_z + 1
    off_x = (map_size - width) // 2 - min_x
    off_z = (map_size - height) // 2 - min_z
    off_x = min(off_x, map_size - EDGE_MARGIN - 1 - max_x)
    off_z = min(off_z, map_size - EDGE_MARGIN - 1 - max_z)
    off_x = max(off_x, EDGE_MARGIN - min_x)
    off_z = max(off_z, EDGE_MARGIN - min_z)
    return off_x, off_z


def bridge():
    spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def map_width(client, sock, buf):
    """The live map's width, found by binary search on what `get_cells_info` will answer.

    There is no tool that reports the map size, and guessing it would put the whole read in the
    wrong place -- which is exactly what happened once already.
    """
    low, high = 60, 600
    while low < high:
        mid = (low + high + 1) // 2
        answer = client.exchange(sock, buf, "tools/call", {
            "name": "rimworld/get_cells_info",
            "arguments": {"x": mid - 1, "z": 1, "width": 1, "height": 1}})
        if answer.get("success") and (answer.get("cells") or []):
            low = mid
        else:
            high = mid - 1
    return low


def live_offset(plan, probe_cell=None, probe_expect=None):
    """The offset, confirmed against the live map rather than only computed.

    Returns (offset_x, offset_z, map_width, confirmation) where confirmation is a human-readable
    statement of what was found at the probe cell. **A computed offset that is never checked is a
    silent mis-aim**, and the cost of being wrong is reading a facility that is not there and
    reporting every authored building as deleted -- which is the output the first run produced.
    """
    client = bridge()
    port, token = client.endpoint()
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=client.TIMEOUT) as sock:
        client.exchange(sock, buf, "session/hello",
                        {"token": token, "client": {"name": client.CLIENT, "version": "1"}})
        width = map_width(client, sock, buf)
        off_x, off_z = offset(plan, width)
        note = "map %d wide, offset (%d, %d)" % (width, off_x, off_z)
        if probe_cell is not None:
            cell = (probe_cell[0] + off_x, probe_cell[1] + off_z)
            answer = client.exchange(sock, buf, "tools/call", {
                "name": "rimworld/get_cells_info",
                "arguments": {"x": cell[0], "z": cell[1], "width": 1, "height": 1}})
            found = []
            for entry in (answer.get("cells") or []):
                for thing in (entry.get("things") or []):
                    if isinstance(thing, dict) and thing.get("defName"):
                        found.append(thing["defName"])
            note += "; probe (%d, %d) holds %s" % (cell[0], cell[1], found or "nothing")
            if probe_expect and probe_expect not in found:
                note += "  <-- EXPECTED %s, SO THE OFFSET IS WRONG" % probe_expect
        return off_x, off_z, width, note
