"""Raise a Chrome window by title fragment and type/click into it, refusing any key unless that
window is foreground.  python safe-type.py "<title part>" click X Y | type "<text>" | enter | shot"""
import ctypes, sys, time
from ctypes import wintypes
u=ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
def find(part):
    r=[]
    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h,_):
        n=u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b=ctypes.create_unicode_buffer(n+1); u.GetWindowTextW(h,b,n+1)
            if part in b.value:
                rc=wintypes.RECT(); u.GetWindowRect(h,ctypes.byref(rc)); r.append(((rc.right-rc.left)*(rc.bottom-rc.top),h,b.value))
        return True
    u.EnumWindows(cb,0); r.sort(reverse=True); return r[0][1] if r else None
h=find(sys.argv[1])
if not h: print("window not found"); sys.exit(1)
def front():
    if u.GetForegroundWindow()!=h:
        u.keybd_event(0x12,0,0,0); u.SetForegroundWindow(h); u.keybd_event(0x12,0,2,0); time.sleep(0.25)
    return u.GetForegroundWindow()==h
if not front(): print("could not focus window"); sys.exit(2)
cmd=sys.argv[2]
if cmd=="click":
    x,y=int(sys.argv[3]),int(sys.argv[4]); u.SetCursorPos(x,y); time.sleep(0.15)
    if not front(): sys.exit(2)
    u.mouse_event(2,0,0,0,0); time.sleep(0.05); u.mouse_event(4,0,0,0,0)
elif cmd=="type":
    for c in sys.argv[3]:
        if not front(): print("lost focus, stopped"); sys.exit(2)
        vk=u.VkKeyScanW(ord(c)); sh=(vk>>8)&1; v=vk&0xff
        if sh: u.keybd_event(0x10,0,0,0)
        u.keybd_event(v,0,0,0); time.sleep(0.02); u.keybd_event(v,0,2,0)
        if sh: u.keybd_event(0x10,0,2,0)
        time.sleep(0.03)
elif cmd=="enter":
    if front(): u.keybd_event(0x0D,0,0,0); u.keybd_event(0x0D,0,2,0)
print("ok")
