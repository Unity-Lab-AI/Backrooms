"""Unity's own mouse and keyboard for RimWorld -- never the owner's cursor.

Owner, 2026-10-10, verbatim: "im not loaining the mouse it need to have its OWN mouse!!!!!! that doesnt fight
user input and deffers instantly before attempting recontol once settles d mouse".

Order of preference, for every helper that used to move the real pointer:

  1. the game bridge (rimworld/click_ui_target, click_cell, ...) -- callers do that before reaching here;
  2. POSTED input: mouse and key messages posted straight to the RimWorld window handle at CLIENT
     coordinates. No SetCursorPos, no global SendInput / mouse_event / keybd_event, no raising the window:
     the owner's cursor and focus are never touched, so there is nothing to fight;
  3. the real cursor, only when a caller asks for it explicitly (real=True), and only through the guard
     below: it waits until the owner's input has been idle for SETTLE_S, defers the instant the owner
     moves or types ("deferred: owner active"), aborts mid-gesture if the pointer is not where it was put,
     and never re-moves the cursor after the owner has taken it.

There is no loan flag. OWNER_LENT_MOUSE in the environment is ignored.

Coordinates passed to click/drag/wheel/hover are CLIENT pixels of the game window; the from_* helpers convert
the frames the older tools speak (eyes.py frame, bridge screenshot, screen pixels).
"""
import ctypes
import os
import sys
import time
from ctypes import wintypes

GAME_TITLE = "RimWorld by Ludeon Studios"
SETTLE_S = 3.0           # owner input must be idle this long before the real cursor is even considered
WAIT_S = 120.0           # how long a real-cursor gesture waits for the owner to settle before giving up
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_own_mouse.log")

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32")
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.WindowFromPoint.argtypes = [wintypes.POINT]
user32.WindowFromPoint.restype = wintypes.HWND
user32.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]
user32.GetAncestor.restype = wintypes.HWND

WM_MOUSEMOVE, WM_MOUSEWHEEL = 0x0200, 0x020A
WM_KEYDOWN, WM_KEYUP, WM_CHAR = 0x0100, 0x0101, 0x0102
BUTTONS = {  # name: (down msg, up msg, dblclk msg, MK_ flag, mouse_event down, mouse_event up)
    "left": (0x0201, 0x0202, 0x0203, 0x0001, 0x0002, 0x0004),
    "right": (0x0204, 0x0205, 0x0206, 0x0002, 0x0008, 0x0010),
    "middle": (0x0207, 0x0208, 0x0209, 0x0010, 0x0020, 0x0040),
}
MK_SHIFT, MK_CONTROL = 0x0004, 0x0008
VK_SHIFT, VK_CONTROL, VK_MENU = 0x10, 0x11, 0x12
MODS = {"shift": VK_SHIFT, "ctrl": VK_CONTROL, "alt": VK_MENU}


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------- the window and its frames

def game():
    """The visible RimWorld window, or None."""
    h = user32.FindWindowW(None, GAME_TITLE)
    return h if h and user32.IsWindowVisible(h) else None


def client_size(h=None):
    h = h or game()
    r = wintypes.RECT()
    user32.GetClientRect(h, ctypes.byref(r))
    return r.right, r.bottom


def from_screen(x, y, h=None):
    """Screen pixel -> client pixel of the game window."""
    h = h or game()
    p = wintypes.POINT(int(x), int(y))
    user32.ScreenToClient(h, ctypes.byref(p))
    return p.x, p.y


def to_screen(cx, cy, h=None):
    h = h or game()
    p = wintypes.POINT(int(cx), int(cy))
    user32.ClientToScreen(h, ctypes.byref(p))
    return p.x, p.y


def from_frame(fx, fy, frame_w=1600.0, h=None):
    """eyes.py frame (client area scaled to frame_w wide, same scale both axes) -> client pixel."""
    cw, _ = client_size(h)
    s = cw / float(frame_w)
    return int(fx * s), int(fy * s)


def from_shot(ix, iy, shot_h=2054.0, shot_w=3840.0, h=None):
    """Bridge screenshot pixel (shot_w x shot_h render of the client) -> client pixel."""
    cw, ch = client_size(h)
    return int(ix * cw / shot_w), int(iy * ch / shot_h)


def _lp(cx, cy):
    return ((int(cy) & 0xFFFF) << 16) | (int(cx) & 0xFFFF)


def _post(h, msg, wp, lp):
    if not user32.PostMessageW(h, msg, wp, lp):
        raise OSError("PostMessage failed (%d)" % ctypes.get_last_error())


# ---------------------------------------------------------------- modifier state for posted input

class _Held:
    """Hold modifier keys for the game's input queue only.

    Posted messages carry MK_SHIFT/MK_CONTROL, but the game may also read GetKeyState, so the key state of
    the game's thread is set for the duration and restored after. The owner's own keyboard state is never
    pressed: nothing global is injected.
    """

    def __init__(self, h, mods):
        self.h, self.vks = h, [MODS[m] for m in (mods or ())]
        self.attached = False

    def __enter__(self):
        if not self.vks:
            return self
        tid = user32.GetWindowThreadProcessId(self.h, None)
        me = kernel32.GetCurrentThreadId()
        self.pair = (me, tid)
        self.attached = bool(user32.AttachThreadInput(me, tid, True))
        if self.attached:
            st = (ctypes.c_ubyte * 256)()
            user32.GetKeyboardState(st)
            for vk in self.vks:
                st[vk] |= 0x80
            user32.SetKeyboardState(st)
        for vk in self.vks:
            _post(self.h, WM_KEYDOWN, vk, _key_lp(vk, False))
        time.sleep(0.03)
        return self

    def __exit__(self, *exc):
        if not self.vks:
            return False
        time.sleep(0.03)
        for vk in reversed(self.vks):
            _post(self.h, WM_KEYUP, vk, _key_lp(vk, True))
        if self.attached:
            st = (ctypes.c_ubyte * 256)()
            user32.GetKeyboardState(st)
            for vk in self.vks:
                st[vk] &= 0x7F
            user32.SetKeyboardState(st)
            user32.AttachThreadInput(self.pair[0], self.pair[1], False)
        return False


def _mk(mods):
    f = 0
    for m in mods or ():
        f |= {"shift": MK_SHIFT, "ctrl": MK_CONTROL}.get(m, 0)
    return f


# ---------------------------------------------------------------- posted mouse (the default path)

def _need_game():
    h = game()
    if not h:
        raise RuntimeError("RimWorld window not found")
    if user32.IsIconic(h):
        raise RuntimeError("RimWorld is minimised")
    return h


def _in_client(h, cx, cy):
    cw, ch = client_size(h)
    if not (0 <= cx < cw and 0 <= cy < ch):
        raise RuntimeError("(%d, %d) is outside the %dx%d game client" % (cx, cy, cw, ch))


def hover(cx, cy, real=False):
    if real:
        return _real_gesture([("move", cx, cy)])
    h = _need_game(); _in_client(h, cx, cy)
    _post(h, WM_MOUSEMOVE, 0, _lp(cx, cy))
    return "hover %d %d" % (cx, cy)


def click(cx, cy, button="left", double=False, mods=(), real=False):
    """Click at a client pixel. Posted unless real=True."""
    if real:
        return _real_gesture([("move", cx, cy)] + [("click", button)] * (2 if double else 1), mods)
    h = _need_game(); _in_client(h, cx, cy)
    down, up, dbl, mk, _, _ = BUTTONS[button]
    flags = _mk(mods); lp = _lp(cx, cy)
    with _Held(h, mods):
        _post(h, WM_MOUSEMOVE, flags, lp); time.sleep(0.04)
        _post(h, down, flags | mk, lp); time.sleep(0.05)
        _post(h, up, flags, lp)
        if double:
            time.sleep(0.06)
            _post(h, dbl, flags | mk, lp); time.sleep(0.05)
            _post(h, up, flags, lp)
        time.sleep(0.04)
    return "click %d %d" % (cx, cy)


def drag(x0, y0, x1, y1, button="left", steps=24, real=False):
    if real:
        seq = [("move", x0, y0), ("down", button)]
        seq += [("move", x0 + (x1 - x0) * i // steps, y0 + (y1 - y0) * i // steps) for i in range(1, steps + 1)]
        return _real_gesture(seq + [("up", button)])
    h = _need_game(); _in_client(h, x0, y0); _in_client(h, x1, y1)
    down, up, _, mk, _, _ = BUTTONS[button]
    _post(h, WM_MOUSEMOVE, 0, _lp(x0, y0)); time.sleep(0.04)
    _post(h, down, mk, _lp(x0, y0)); time.sleep(0.05)
    for i in range(1, steps + 1):
        _post(h, WM_MOUSEMOVE, mk, _lp(x0 + (x1 - x0) * i // steps, y0 + (y1 - y0) * i // steps))
        time.sleep(0.02)
    time.sleep(0.05)
    _post(h, up, 0, _lp(x1, y1))
    return "dragged (%d, %d) -> (%d, %d)" % (x0, y0, x1, y1)


def wheel(cx, cy, clicks, real=False):
    if real:
        return _real_gesture([("move", cx, cy)] + [("wheel", 1 if clicks > 0 else -1)] * abs(int(clicks)))
    h = _need_game(); _in_client(h, cx, cy)
    sx, sy = to_screen(cx, cy, h)                 # WM_MOUSEWHEEL carries screen coordinates
    _post(h, WM_MOUSEMOVE, 0, _lp(cx, cy)); time.sleep(0.03)
    for _ in range(abs(int(clicks))):
        delta = (120 if clicks > 0 else -120) & 0xFFFF
        _post(h, WM_MOUSEWHEEL, delta << 16, _lp(sx, sy)); time.sleep(0.12)
    return "wheel %d" % clicks


# ---------------------------------------------------------------- posted keyboard

def _key_lp(vk, up):
    scan = user32.MapVirtualKeyW(vk, 0) & 0xFF
    lp = 1 | (scan << 16)
    if up:
        lp |= (1 << 30) | (1 << 31)
    return lp


def key(vk, mods=()):
    """One virtual-key press posted to the game; the game's own message loop turns it into text."""
    h = _need_game()
    with _Held(h, mods):
        _post(h, WM_KEYDOWN, vk, _key_lp(vk, False)); time.sleep(0.03)
        _post(h, WM_KEYUP, vk, _key_lp(vk, True)); time.sleep(0.04)


def type_keys(text):
    """Type text as virtual keys (what RimWorld's numeric fields answer); shifted characters hold shift."""
    for c in text:
        if c == "-":
            key(0xBD); continue
        v = user32.VkKeyScanW(ord(c))
        if v == -1 or v == 0xFFFF:
            type_chars(c); continue
        key(v & 0xFF, ("shift",) if (v >> 8) & 1 else ())


def type_chars(text):
    """Type text as WM_CHAR, no layout guessing (search boxes)."""
    h = _need_game()
    for c in text:
        _post(h, WM_CHAR, ord(c), 1); time.sleep(0.03)


def clear_field(n=30):
    """End, then n Backspaces: empties a focused text field without needing Ctrl+A."""
    key(0x23)
    for _ in range(n):
        key(0x08)


# ---------------------------------------------------------------- the owner's real cursor (guarded fallback)

def _cursor():
    p = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y


def owner_idle_s():
    """Seconds since the last real keyboard or mouse input on this machine."""
    li = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    if not user32.GetLastInputInfo(ctypes.byref(li)):
        return 0.0
    return ((kernel32.GetTickCount() - li.dwTime) & 0xFFFFFFFF) / 1000.0


def wait_owner_settled(settle=SETTLE_S, timeout=WAIT_S):
    """True once input has been idle for `settle` seconds AND the pointer has not moved in that time.

    Defers instantly while the owner is active and says so once. False on timeout: the caller gives up.
    """
    start = time.time()
    last_pos, still_since = _cursor(), time.time()
    said = False
    while True:
        pos = _cursor()
        if pos != last_pos:
            last_pos, still_since = pos, time.time()
        if owner_idle_s() >= settle and time.time() - still_since >= settle:
            return True
        if not said:
            log("deferred: owner active")
            said = True
        if time.time() - start > timeout:
            return False
        time.sleep(0.25)


class OwnerActive(Exception):
    pass


def _real_gesture(steps, mods=()):
    """Run a gesture on the real cursor, only while the owner is idle, aborting the moment they move.

    The pointer is put back where the owner left it when the gesture completes untouched; if the owner took
    it mid-gesture, it is left exactly where they put it.
    """
    h = _need_game()
    if not wait_owner_settled():
        log("deferred: owner active -- gave up waiting for the mouse to settle")
        return "deferred: owner active"
    if user32.GetForegroundWindow() != h:
        return "deferred: RimWorld is not in front (the real cursor never raises it)"
    home = _cursor()
    expect = home
    held = []
    for vk in [MODS[m] for m in (mods or ())]:
        user32.keybd_event(vk, 0, 0, 0); held.append(vk)
    try:
        for step in steps:
            if _cursor() != expect or user32.GetForegroundWindow() != h:
                raise OwnerActive()
            if step[0] == "move":
                sx, sy = to_screen(step[1], step[2], h)
                if user32.GetAncestor(user32.WindowFromPoint(wintypes.POINT(sx, sy)), 2) != h:
                    raise RuntimeError("the window under (%d, %d) is not RimWorld" % (sx, sy))
                user32.SetCursorPos(sx, sy); expect = (sx, sy); time.sleep(0.03)
            elif step[0] in ("click", "down", "up"):
                b = BUTTONS[step[1]]
                if step[0] in ("click", "down"):
                    user32.mouse_event(b[4], 0, 0, 0, 0); held.append(("btn", b[5]))
                    time.sleep(0.05)
                if step[0] in ("click", "up"):
                    held = [x for x in held if x != ("btn", b[5])]
                    user32.mouse_event(b[5], 0, 0, 0, 0); time.sleep(0.06)
            elif step[0] == "wheel":
                user32.mouse_event(0x0800, 0, 0, (120 if step[1] > 0 else -120) & 0xFFFFFFFF, 0); time.sleep(0.12)
        if _cursor() == expect:
            user32.SetCursorPos(*home)            # untouched: give the pointer back where the owner left it
        return "real %s done" % steps[-1][0]
    except OwnerActive:
        log("deferred: owner active -- stopped mid-gesture, cursor left where the owner put it")
        return "deferred: owner active"
    finally:
        for x in reversed(held):
            if isinstance(x, tuple):
                user32.mouse_event(x[1], 0, 0, 0, 0)
            else:
                user32.keybd_event(x, 0, 2, 0)


def run(fn, *a, **k):
    """Call a helper and turn its outcome into a printed line and an exit code for the CLI wrappers."""
    try:
        out = fn(*a, **k)
    except Exception as e:
        print("REFUSED: %s" % e)
        return 1
    print(out)
    return 1 if str(out).startswith("deferred") else 0


if __name__ == "__main__":
    print(__doc__)
    print("owner idle %.1fs, game %s" % (owner_idle_s(), "found" if game() else "NOT FOUND"))
    sys.exit(0)
