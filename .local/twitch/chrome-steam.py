"""Drive ONE window: the owner's Chrome tab on the Steam collection edit page (owner, 2026-10-08:
"edfit it directly" / "page is open"). Every action re-checks that the foreground window is that
tab and that it is the window under the point; anything else refuses.

    python .local/twitch/chrome-steam.py shot OUT.png        raise + screenshot the window (client area)
    python .local/twitch/chrome-steam.py click X Y           click at client-area pixel X Y
    python .local/twitch/chrome-steam.py type "text"         type unicode text into the focused field
    python .local/twitch/chrome-steam.py key ctrl+a|del|enter|tab|end
    python .local/twitch/chrome-steam.py wheel X Y N         scroll N notches (neg = down)
"""
import ctypes, sys, time
from ctypes import wintypes
from PIL import ImageGrab

u = ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
u.WindowFromPoint.argtypes = [wintypes.POINT]; u.WindowFromPoint.restype = wintypes.HWND
u.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]; u.GetAncestor.restype = wintypes.HWND
TITLE_MUST = ("Steam", "Google Chrome")

def find():
    found = []
    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        n = u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1)
            if all(t in b.value for t in TITLE_MUST) and "Twitch" not in b.value: found.append(h)
        return True
    u.EnumWindows(cb, 0)
    if not found: sys.exit("REFUSED: no Chrome window on a Steam Community page")
    return found[0]

def raise_(h):
    if u.GetForegroundWindow() != h:
        u.keybd_event(0x12, 0, 0, 0); u.SetForegroundWindow(h); u.keybd_event(0x12, 0, 2, 0); time.sleep(0.4)
    if u.GetForegroundWindow() != h: sys.exit("REFUSED: could not bring the Steam tab to the front")

def origin(h):
    cr = wintypes.RECT(); u.GetClientRect(h, ctypes.byref(cr))
    o = wintypes.POINT(0, 0); u.ClientToScreen(h, ctypes.byref(o))
    return o.x, o.y, cr.right, cr.bottom

def safe(h, x, y):
    return u.GetForegroundWindow() == h and u.GetAncestor(u.WindowFromPoint(wintypes.POINT(x, y)), 2) == h

class KI(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
class INP(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KI), ("pad", ctypes.c_byte * 32)]
    _anonymous_ = ("u",); _fields_ = [("type", wintypes.DWORD), ("u", _U)]

def uni(ch):
    for flags in (0x0004, 0x0004 | 0x0002):   # KEYEVENTF_UNICODE, then key-up
        i = INP(type=1); i.ki = KI(0, ord(ch), flags, 0, 0)
        u.SendInput(1, ctypes.byref(i), ctypes.sizeof(INP))

def vk(code, down=True): u.keybd_event(code, 0, 0 if down else 2, 0)

def main():
    a = sys.argv[1:]; h = find(); raise_(h); ox, oy, w, ht = origin(h)
    if a[0] == "shot":
        ImageGrab.grab(bbox=(ox, oy, ox + w, oy + ht), all_screens=True).save(a[1]); print(a[1], w, ht)
    elif a[0] == "click":
        x, y = ox + int(a[1]), oy + int(a[2])
        if not safe(h, x, y): sys.exit("REFUSED: Steam tab not foreground / not under point")
        u.SetCursorPos(x, y); time.sleep(0.1); u.mouse_event(2, 0, 0, 0, 0); time.sleep(0.05); u.mouse_event(4, 0, 0, 0, 0)
        print("clicked", a[1], a[2])
    elif a[0] == "type":
        for ch in a[1]:
            if u.GetForegroundWindow() != h: sys.exit("REFUSED mid-text: focus changed")
            if ch == "\n":
                vk(0x10); vk(0x0D); vk(0x0D, False); vk(0x10, False)   # shift+enter keeps it a newline
            else:
                uni(ch)
            time.sleep(0.004)
        print("typed", len(a[1]))
    elif a[0] == "key":
        combo = a[1].split("+"); mods = {"ctrl": 0x11, "shift": 0x10}; keys = {"l": 0x4C, "a": 0x41, "del": 0x2E, "enter": 0x0D, "tab": 0x09, "end": 0x23, "home": 0x24}
        for m in combo[:-1]: vk(mods[m])
        vk(keys[combo[-1]]); vk(keys[combo[-1]], False)
        for m in reversed(combo[:-1]): vk(mods[m], False)
        print("key", a[1])
    elif a[0] == "wheel":
        x, y = ox + int(a[1]), oy + int(a[2])
        if not safe(h, x, y): sys.exit("REFUSED: not under point")
        u.SetCursorPos(x, y)
        for _ in range(abs(int(a[3]))): u.mouse_event(0x0800, 0, 0, (120 if int(a[3]) > 0 else -120) & 0xFFFFFFFF, 0)
        print("wheel", a[3])

if __name__ == "__main__":
    main()
