"""Type a path into the browser's Windows file dialog (only when a dialog titled Open is in front).
python .local/twitch/pick-file.py PATH"""
import ctypes, sys, time
from ctypes import wintypes
u = ctypes.WinDLL("user32")
PATH = sys.argv[1]
def title(h):
    n = u.GetWindowTextLengthW(h); b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1); return b.value
h = None
for _ in range(30):
    f = u.GetForegroundWindow()
    if title(f) in ("Open", "Open File"): h = f; break
    time.sleep(0.2)
if not h: sys.exit("REFUSED: no Open dialog in front (foreground %r)" % title(u.GetForegroundWindow()))
class KI(ctypes.Structure): _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
class INP(ctypes.Structure):
    class _U(ctypes.Union): _fields_ = [("ki", KI), ("pad", ctypes.c_byte * 32)]
    _anonymous_ = ("u",); _fields_ = [("type", wintypes.DWORD), ("u", _U)]
for ch in PATH:
    if u.GetForegroundWindow() != h: sys.exit("REFUSED: dialog lost focus")
    for fl in (4, 6):
        i = INP(type=1); i.ki = KI(0, ord(ch), fl, 0, 0); u.SendInput(1, ctypes.byref(i), ctypes.sizeof(INP))
    time.sleep(0.005)
u.keybd_event(0x0D, 0, 0, 0); u.keybd_event(0x0D, 0, 2, 0); print("picked", PATH)
