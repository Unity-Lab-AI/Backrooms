"""Click a screen point, then type into the top-level window under that point -- refusing every
key unless that same window is still foreground.  python field-type.py X Y "<text>" """
import ctypes, sys, time
from ctypes import wintypes
u=ctypes.WinDLL("user32"); ctypes.windll.shcore.SetProcessDpiAwareness(2)
u.WindowFromPoint.argtypes=[wintypes.POINT]; u.WindowFromPoint.restype=wintypes.HWND
u.GetAncestor.argtypes=[wintypes.HWND, ctypes.c_uint]; u.GetAncestor.restype=wintypes.HWND
x,y,text=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
h=u.GetAncestor(u.WindowFromPoint(wintypes.POINT(x,y)),2)
b=ctypes.create_unicode_buffer(256); u.GetWindowTextW(h,b,256); print("target:",b.value)
u.keybd_event(0x12,0,0,0); u.SetForegroundWindow(h); u.keybd_event(0x12,0,2,0); time.sleep(0.3)
u.SetCursorPos(x,y); time.sleep(0.15); u.mouse_event(2,0,0,0,0); time.sleep(0.05); u.mouse_event(4,0,0,0,0); time.sleep(0.3)
for c in text:
    if u.GetAncestor(u.GetForegroundWindow(),2)!=h: print("lost focus, stopped"); sys.exit(2)
    vk=u.VkKeyScanW(ord(c)); sh=(vk>>8)&1; v=vk&0xff
    if sh: u.keybd_event(0x10,0,0,0)
    u.keybd_event(v,0,0,0); time.sleep(0.02); u.keybd_event(v,0,2,0)
    if sh: u.keybd_event(0x10,0,2,0)
    time.sleep(0.03)
print("typed")
