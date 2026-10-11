#!/usr/bin/env python3
"""Click the running game at a screen pixel with Unity's own mouse, never the owner's cursor.

The companion to `eyes.py`. The bridge cannot reach the main menu or the landing-tile page --
both draw through the entry/world UI root and report a 0x0 rect, so `get_ui_layout` enumerates
nothing and `click_ui_target` has no id to aim at. A screen pixel has no such problem.

UNITY'S OWN MOUSE. Every click, drag, hover and keystroke is posted straight to the RimWorld
window handle (own_mouse.py), so it can only ever reach the game, never raises the window, and
never moves the owner's cursor. --real falls back to the owner's cursor only after their input has
settled, and defers the instant they move.

Coordinates are given in the frame of the image `eyes.py` wrote (1600 wide by default), because
that is the frame of the picture being read. They are scaled to physical screen pixels here.

Usage:
    python .local/qa/hands.py 1270 424              # click, coordinates in the read image
    python .local/qa/hands.py --physical 3048 1018  # click, coordinates in screen pixels
    python .local/qa/hands.py --right 800 450       # right-click (work tab: raises a priority number)
    python .local/qa/hands.py --shift 800 450       # shift-click (also --ctrl)
    python .local/qa/hands.py --where               # print the foreground window and screen size
"""
import ctypes
import ctypes.wintypes as wintypes
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import own_mouse as om

READ_WIDTH = 1600.0
GAME_TITLE = om.GAME_TITLE

user32 = om.user32


def screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def printable(text):
    """A window title is arbitrary text and this console is cp1252.

    The first title this tool ever read was the terminal it was running in, whose spinner
    glyph killed the process before it could report anything.
    """
    return (text or "").encode("ascii", "replace").decode("ascii")


def foreground_title():
    handle = user32.GetForegroundWindow()
    if not handle:
        return None, ""
    length = user32.GetWindowTextLengthW(handle)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(handle, buffer, length + 1)
    return handle, buffer.value


def find_game():
    return om.game()


def _client(x, y):
    """Screen pixel -> game client pixel."""
    return om.from_screen(x, y)


def type_text(text):
    """Send a string as characters posted to the game, which needs no keyboard-layout guessing.

    A search box is the only way to reach most of a storage filter -- the tree is thousands of
    rows behind a scroll view -- so typing is as load-bearing here as clicking.
    """
    om.type_chars(text)


def click(x, y, real=False):
    return om.click(*_client(x, y), real=real)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    physical = False
    rest = [a for a in argv if a != "--real"]
    real = len(rest) != len(argv)
    if rest[0] == "--where":
        width, height = screen_size()
        handle, title = foreground_title()
        print("screen     : %dx%d" % (width, height))
        print("foreground : %r" % printable(title))
        print("game window: %s" % ("found" if find_game() else "NOT FOUND"))
        print("owner idle : %.1fs" % om.owner_idle_s())
        return 0
    if not find_game():
        print("refused: no visible window titled %r -- is the game running?" % GAME_TITLE)
        return 1
    hover = False
    if rest[0] == "--type" and len(rest) >= 2:
        try:
            type_text(" ".join(rest[1:]))
        except Exception as e:
            print("refused: %s" % e)
            return 1
        print("typed %r" % " ".join(rest[1:]))
        return 0
    if rest[0] == "--drag" and len(rest) == 5:
        # A press at one point, a sweep to another, a release: the gesture the schedule grid and
        # every paint-style control reads, which no sequence of single clicks reproduces.
        width, height = screen_size()
        scale = width / READ_WIDTH
        x1, y1, x2, y2 = [float(v) * scale for v in rest[1:5]]
        try:
            out = om.drag(*(_client(x1, y1) + _client(x2, y2)), real=real)
        except Exception as e:
            print("refused: %s" % e)
            return 1
        print(out)
        return 1 if out.startswith("deferred") else 0
    if rest[0] == "--hover":
        # Move the pointer and leave it: the way to read a tooltip is to hover, then capture.
        hover = True
        rest.pop(0)
    right = False
    if rest and rest[0] == "--right":
        right = True
        rest.pop(0)
    mods = []
    while rest and rest[0] in ("--shift", "--ctrl"):
        mods.append(rest.pop(0)[2:])
    if rest and rest[0] == "--physical":
        physical = True
        rest.pop(0)
    if len(rest) != 2:
        print(__doc__)
        return 1

    x, y = float(rest[0]), float(rest[1])
    width, height = screen_size()
    if not physical:
        scale = width / READ_WIDTH
        x, y = x * scale, y * scale
    if not (0 <= x < width and 0 <= y < height):
        print("refused: (%d, %d) is outside the %dx%d screen" % (x, y, width, height))
        return 1

    try:
        cx, cy = _client(x, y)
        if hover:
            out = om.hover(cx, cy, real=real)
        else:
            out = om.click(cx, cy, button="right" if right else "left", mods=mods, real=real)
    except Exception as e:
        print("refused: %s" % e)
        return 1
    if out.startswith("deferred"):
        print(out)
        return 1
    verb = "hovering" if hover else ("right-clicked" if right else "clicked")
    print("%s (%d, %d) on a %dx%d screen" % (verb, x, y, width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
