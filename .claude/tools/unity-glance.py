"""A picture with every line: the game exactly as the stream sees it now, Unity's line scribbled on it.

    python .claude/tools/unity-glance.py "caption"

Owner, 2026-10-08: *"and make some images more offten like as much as you talk"*. unity-say.py runs
this after each spoken line. Unlike unity-snap.py it never moves the camera -- it shoots the current
view -- so it can run on every line without fighting play.py's framing. The caption is a spoken
line that already passed the stream filter (THE STREAM IS CLEAN).
"""
import base64, io, json, os, subprocess, sys, textwrap, urllib.request
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRIDGE = os.path.join(ROOT, ".local", "qa", "bridge.py")
FONT = "C:/Windows/Fonts/Inkfree.ttf"
PINK = (255, 70, 160)


def _mark_highlight():
    """The webcam panel shows a highlight for at most ~20 s, then cam-director.py puts Unity back up (owner,
    2026-10-09: "leave the profile pic of ur up more and the slide show highlights just intermittently for liek
    20 second max so it settle on a new you doing things")."""
    try:
        import json as _j, time as _t
        _j.dump({"ts": _t.time()}, open(os.path.join(ROOT, ".claude", ".cam-highlight.json"), "w"))
    except Exception:
        pass

def call(tool, args=None):
    o = subprocess.run([sys.executable, BRIDGE, "call", tool, json.dumps(args or {})],
                       capture_output=True, text=True, timeout=60).stdout
    try: return json.loads(o[o.find("{"):])
    except Exception: return {}


def find(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = find(v, k)
            if r is not None: return r
    return None


def highlight(im, marks):
    """Owner, 2026-10-09: "maore hhighlighting in game images" -- ring every colonist in view with their
    name, ring hostiles in red, and draw any --mark x,z,label the caller passes (plans, builds)."""
    cam = call("rimworld/get_camera_state")
    x0, x1, z0, z1 = (find(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
    if None in (x0, x1, z0, z1): return
    W, H = im.size; cw = W / (x1 - x0 + 1.0); ch = H / (z1 - z0 + 1.0)
    def px(x, z): return ((x - x0 + 0.5) * cw, (z1 - z + 0.5) * ch)
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, 22); r = max(10, cw * 0.8)
    def ring(x, z, label, col):
        if not (x0 <= x <= x1 and z0 <= z <= z1): return
        cx, cy = px(x, z)
        for w in (5, 3):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(0, 0, 0) if w == 5 else col, width=w)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): d.text((cx + r + 2 + dx, cy - 12 + dy), label, font=f, fill=(0, 0, 0))
        d.text((cx + r + 2, cy - 12), label, font=f, fill=col)
    mine = set()
    for c in call("rimworld/list_colonists").get("colonists", []):
        p = c.get("position") or {}
        if "x" in p: ring(p["x"], p["z"], c.get("name", ""), PINK); mine.add((p["x"], p["z"]))
    o = subprocess.run([sys.executable, os.path.join(ROOT, ".local", "qa", "live-hostiles.py")], capture_output=True, text=True, timeout=60).stdout
    try:
        import ast
        for x, z in ast.literal_eval(o.strip() or "[]"):
            if (x, z) not in mine: ring(x, z, "HOSTILE", (255, 40, 40))
    except Exception: pass
    for x, z, label in marks: ring(x, z, label, (90, 220, 255))


def main():
    args = sys.argv[1:]; marks = []
    while "--mark" in args:
        i = args.index("--mark"); x, z, *lab = args[i + 1].split(",", 2); marks.append((int(x), int(z), lab[0] if lab else ""))
        del args[i:i + 2]
    caption = " ".join(args).strip()
    o = subprocess.run([sys.executable, BRIDGE, "call", "rimworld/take_screenshot", "{}"],
                       capture_output=True, text=True, timeout=120).stdout
    path = json.loads(o[o.find("{"):]).get("path")
    if not path:
        return
    im = Image.open(path).convert("RGB")
    im.thumbnail((1024, 1024))
    try: highlight(im, marks)
    except Exception: pass
    W, H = im.size
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 34)
    lines = textwrap.wrap(caption, 52)[:3]
    y = H - 24 - 40 * len(lines)
    for line in lines:
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            d.text((22 + dx, y + dy), line, font=f, fill=(0, 0, 0))
        d.text((22, y), line, font=f, fill=PINK)
        y += 40
    buf = io.BytesIO(); im.save(buf, "PNG")
    req = urllib.request.Request("http://127.0.0.1:4317/api/cam",
                                 data=json.dumps({"png": base64.b64encode(buf.getvalue()).decode(),
                                                  "caption": caption}).encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=60).read()
    _mark_highlight()


if __name__ == "__main__":
    main()
