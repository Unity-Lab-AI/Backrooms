import os as _os, sys as _sys
# LOCKED (owner, 2026-10-09: "HOW MANY TIMES HAVE I SAID DONT FIGHT ME ... U WERE OPENING THE MICROSOFT STORE
# REPEADILEY USING HOTKEYS ... IF I TAKE THE FUCKING MOUSE OR KEEYS I HAVE TO BE ABLE TO TALK TO YOU"):
# real mouse/keyboard input only when the owner has just lent it, signalled by OWNER_LENT_MOUSE=1.
if _os.environ.get("OWNER_LENT_MOUSE") != "1":
    _sys.exit("REFUSED: real input is locked; ask the owner to lend the mouse first")
#!/usr/bin/env python3
"""Click the running game at a screen pixel, after proving the game owns the foreground.

The companion to `eyes.py`. The bridge cannot reach the main menu or the landing-tile page --
both draw through the entry/world UI root and report a 0x0 rect, so `get_ui_layout` enumerates
nothing and `click_ui_target` has no id to aim at. A screen pixel has no such problem.

THE REFUSAL IS THE POINT. A click is sent to whatever window owns the foreground, so a click
aimed at the game while something else is focused lands in the owner's work instead. This tool
raises RimWorld, re-reads the foreground window, and refuses if it is not the game. It never
clicks on faith.

Coordinates are given in the frame of the image `eyes.py` wrote (1600 wide by default), because
that is the frame of the picture being read. They are scaled to physical screen pixels here.

Usage:
    python .local/qa/hands.py 1270 424              # click, coordinates in the read image
    python .local/qa/hands.py --physical 3048 1018  # click, coordinates in screen pixels
    python .local/qa/hands.py --right 800 450       # right-click (work tab: raises a priority number)
    python .local/qa/hands.py --where               # print the foreground window and screen size
"""
import ctypes
import ctypes.wintypes as wintypes
import sys
import time

READ_WIDTH = 1600.0
GAME_TITLE = "RimWorld by Ludeon Studios"

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
SW_RESTORE = 9

KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP = 0x0002
INPUT_KEYBOARD = 1

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SetProcessDPIAware()


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
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(handle, _):
        length = user32.GetWindowTextLengthW(handle)
        if length:
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(handle, buffer, length + 1)
            if buffer.value == GAME_TITLE and user32.IsWindowVisible(handle):
                found.append(handle)
        return True

    user32.EnumWindows(visit, 0)
    return found[0] if found else None


def raise_game():
    """Bring the game forward and confirm it got there. Returns an error string, or None."""
    handle = find_game()
    if handle is None:
        return "no visible window titled %r -- is the game running?" % GAME_TITLE
    user32.ShowWindow(handle, SW_RESTORE)
    user32.SetForegroundWindow(handle)
    for _ in range(20):
        time.sleep(0.1)
        current, title = foreground_title()
        if current == handle:
            return None
    _, title = foreground_title()
    return ("the game did not take the foreground; it is still held by %r. "
            "Nothing was clicked." % printable(title))


class _KeyInput(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]


class _InputUnion(ctypes.Union):
    _fields_ = [("ki", _KeyInput), ("padding", ctypes.c_byte * 24)]


class _Input(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", _InputUnion)]


def type_text(text):
    """Send a string as unicode key events, which needs no keyboard-layout guessing.

    A search box is the only way to reach most of a storage filter -- the tree is thousands of
    rows behind a scroll view -- so typing is as load-bearing here as clicking.
    """
    for character in text:
        for flags in (KEYEVENTF_UNICODE, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP):
            event = _Input(type=INPUT_KEYBOARD,
                           union=_InputUnion(ki=_KeyInput(wVk=0, wScan=ord(character),
                                                          dwFlags=flags, time=0,
                                                          dwExtraInfo=None)))
            user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(event))
        time.sleep(0.02)


def click(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.08)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    physical = False
    rest = list(argv)
    if rest[0] == "--where":
        width, height = screen_size()
        handle, title = foreground_title()
        print("screen     : %dx%d" % (width, height))
        print("foreground : %r" % printable(title))
        print("game window: %s" % ("found" if find_game() else "NOT FOUND"))
        return 0
    hover = False
    if rest[0] == "--type" and len(rest) >= 2:
        problem = raise_game()
        if problem:
            print("refused: %s" % problem)
            return 1
        type_text(" ".join(rest[1:]))
        print("typed %r" % " ".join(rest[1:]))
        return 0
    if rest[0] == "--drag" and len(rest) == 5:
        # A press at one point, a sweep to another, a release: the gesture the schedule grid and
        # every paint-style control reads, which no sequence of single clicks reproduces.
        width, height = screen_size()
        scale = width / READ_WIDTH
        x1, y1, x2, y2 = [float(v) * scale for v in rest[1:5]]
        problem = raise_game()
        if problem:
            print("refused: %s" % problem)
            return 1
        user32.SetCursorPos(int(x1), int(y1))
        time.sleep(0.08)
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        steps = 24
        for step in range(1, steps + 1):
            user32.SetCursorPos(int(x1 + (x2 - x1) * step / steps), int(y1 + (y2 - y1) * step / steps))
            time.sleep(0.02)
        time.sleep(0.05)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print("dragged (%d, %d) -> (%d, %d)" % (x1, y1, x2, y2))
        return 0
    if rest[0] == "--hover":
        # Move the pointer and leave it: the way to read a tooltip is to hover, then capture.
        hover = True
        rest.pop(0)
    right = False
    if rest and rest[0] == "--right":
        right = True
        rest.pop(0)
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

    problem = raise_game()
    if problem:
        print("refused: %s" % problem)
        return 1

    if hover:
        user32.SetCursorPos(int(x), int(y))
        print("hovering (%d, %d) on a %dx%d screen" % (x, y, width, height))
        return 0
    if right:
        user32.SetCursorPos(int(x), int(y))
        time.sleep(0.08)
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        print("right-clicked (%d, %d) on a %dx%d screen" % (x, y, width, height))
        return 0
    click(x, y)
    print("clicked (%d, %d) on a %dx%d screen" % (x, y, width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
