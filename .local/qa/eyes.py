#!/usr/bin/env python3
"""Look at the running game: capture through the bridge, downscale, print a readable path.

Owner direction, 2026-10-07: *"with the rimbridge i dont think u can see very well so im thinking
on top of rimbridge u use something like playwrite so u can see the game too"*. Playwright drives
browsers and RimWorld is a Unity binary, so the capability it asked for is screen capture plus a
raw pointer -- and `rimworld/take_screenshot` was in the bridge's 125 tools the whole time,
unused, while `NOW.md` claimed the page could not be seen.

A raw capture is ~6 MB at this resolution, too large to hand to a reader, so every shot is
downscaled here and written beside the raw file. The raw is kept: a downscale can hide a
one-pixel-wide element, and the reason to look at all is to find what the metadata omits.

Usage:
    python .local/qa/eyes.py                       # full screen
    python .local/qa/eyes.py --clip <targetId>     # crop to a window or ui element
    python .local/qa/eyes.py --name landing-tile   # fixed file stem
"""
import importlib.util
import json
import os
import socket
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.join(HERE, "evidence", "eyes")
# Every file this writes carries the QA prefix. The owner keeps 31 saves back to August and
# screenshots beside them; nothing of theirs is ever a candidate for being overwritten.
PREFIX = "RRQA-eyes-"
READ_WIDTH = 1600

_spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
_bridge = importlib.util.module_from_spec(_spec)
sys.modules["rr_bridge"] = _bridge
_spec.loader.exec_module(_bridge)


def capture(arguments):
    port, token = _bridge.endpoint()
    buf = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=_bridge.TIMEOUT) as sock:
        sock.settimeout(_bridge.TIMEOUT)
        _bridge.exchange(sock, buf, "session/hello",
                         {"token": token, "bridgeVersion": "RimroomsEyes/1",
                          "platform": "windows", "launchId": str(uuid.uuid4())})
        return _bridge.exchange(sock, buf, "tools/call",
                                {"name": "rimworld/take_screenshot", "arguments": arguments})


def downscale(raw_path, stem):
    from PIL import Image
    if not os.path.isdir(EVIDENCE):
        os.makedirs(EVIDENCE)
    image = Image.open(raw_path)
    width, height = image.size
    out = os.path.join(EVIDENCE, stem + ".png")
    if width > READ_WIDTH:
        scale = READ_WIDTH / float(width)
        image = image.resize((READ_WIDTH, max(1, int(round(height * scale)))), Image.LANCZOS)
    image.convert("RGB").save(out)
    return out, (width, height), image.size


def os_capture(stem):
    """The screen as Windows sees it, for the moments the bridge cannot answer.

    `take_screenshot` runs on the game's main thread, and during a load that thread is busy for
    minutes -- which is exactly when the loading screen is on. The desktop capture needs
    nothing from the game.
    """
    from PIL import ImageGrab
    if not os.path.isdir(EVIDENCE):
        os.makedirs(EVIDENCE)
    image = ImageGrab.grab()
    width, height = image.size
    out = os.path.join(EVIDENCE, stem + ".png")
    if width > READ_WIDTH:
        image = image.resize((READ_WIDTH, max(1, int(round(height * READ_WIDTH / float(width))))))
    image.convert("RGB").save(out)
    print("os capture      : %dx%d" % (width, height))
    print("READ THIS      : %s  (%dx%d)" % (out, image.size[0], image.size[1]))
    return 0


def main(argv):
    stem = PREFIX + time.strftime("%H%M%S")
    arguments = {"suppressMessage": True, "includeTargets": True}
    rest = list(argv)
    use_os = False
    while rest:
        flag = rest.pop(0)
        if flag == "--clip" and rest:
            arguments["clipTargetId"] = rest.pop(0)
            arguments["clipPadding"] = 8
        elif flag == "--name" and rest:
            stem = PREFIX + rest.pop(0)
        elif flag == "--os":
            use_os = True
        else:
            print(__doc__)
            return 1
    if use_os:
        return os_capture(stem)
    arguments["fileName"] = stem

    result = capture(arguments)
    if not result.get("success"):
        print("capture refused: %s" % json.dumps(result)[:800])
        return 1

    raw = result["path"]
    out, raw_size, read_size = downscale(raw, stem)

    state = ((result.get("screenTargets") or {}).get("uiState") or {})
    print("programState   : %s" % state.get("programState"))
    print("hasCurrentGame : %s" % state.get("hasCurrentGame"))
    print("topWindowType  : %s" % state.get("topWindowType"))
    print("windowCount    : %s" % state.get("windowCount"))
    print("raw            : %s  (%dx%d, %.1f MB)"
          % (raw, raw_size[0], raw_size[1], result.get("sizeBytes", 0) / 1048576.0))
    print("READ THIS      : %s  (%dx%d)" % (out, read_size[0], read_size[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
