"""Post an annotated game screenshot to the stream's REPRESENTATION panel -- Unity circling things
and scribbling notes over the game in her own handwriting.

    python .claude/tools/unity-snap.py X Z W H "caption" [--mark X Z "note"]... [--arrow X Z "note"]...

X Z W H is the map rect to shoot (cells). --mark circles a cell and writes the note beside it.
Owner (2026-10-08): "you can even post game screenshots highlighted things that happen with your hand
writting drawn over top" / "like circle things and write messsages". Notes reach the stream: keep them
clean (CONSTRAINTS: THE STREAM IS CLEAN).
"""
import base64, io, json, os, random, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRIDGE = os.path.join(ROOT, ".local", "qa", "bridge.py")
FONT = "C:/Windows/Fonts/Inkfree.ttf"
INK = [(255, 70, 160), (255, 220, 60), (120, 220, 255)]


def shoot(x, z, w, h):
    # the rect must be on screen at the current zoom; frame it first (this also puts the stream's
    # view on what Unity is talking about)
    subprocess.run([sys.executable, BRIDGE, "call", "rimworld/frame_cell_rect",
                    json.dumps({"x": x, "z": z, "width": w, "height": h})], capture_output=True, timeout=60)
    # Full-screen shot + the camera's visible cell bounds; crop to the rect ourselves. (The bridge's
    # screenshot_cell_rect refuses whenever its padded rect does not fit the zoom.)
    def call(tool, args):
        o = subprocess.run([sys.executable, BRIDGE, "call", tool, json.dumps(args)],
                           capture_output=True, text=True, timeout=120).stdout
        return json.loads(o[o.find("{"):])
    cam = call("rimworld/get_camera_state", {})
    def find(n, k):
        if isinstance(n, dict):
            if k in n: return n[k]
            for v in n.values():
                r = find(v, k)
                if r is not None: return r
        return None
    vx0, vx1, vz0, vz1 = (find(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
    im = Image.open(call("rimworld/take_screenshot", {})["path"]).convert("RGB")
    W, H = im.size
    sx, sz = W / (vx1 - vx0 + 1), H / (vz1 - vz0 + 1)
    left, right = max(0, (x - vx0) * sx), min(W, (x + w - vx0) * sx)
    top, bottom = max(0, (vz1 + 1 - (z + h)) * sz), min(H, (vz1 + 1 - z) * sz)
    return im.crop((int(left), int(top), int(right), int(bottom)))


def wobbly_circle(d, cx, cy, r, color):
    pts = []
    for i in range(0, 380, 12):
        a = i / 180 * 3.14159
        rr = r * (1 + random.uniform(-0.06, 0.06))
        pts.append((cx + rr * __import__("math").cos(a), cy + rr * __import__("math").sin(a)))
    d.line(pts, fill=color, width=5, joint="curve")


def text(d, xy, s, size, color):
    f = ImageFont.truetype(FONT, size)
    x, y = xy
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        d.text((x + dx, y + dy), s, font=f, fill=(0, 0, 0))
    d.text((x, y), s, font=f, fill=color)


def main():
    a = sys.argv[1:]
    x, z, w, h, caption = int(a[0]), int(a[1]), int(a[2]), int(a[3]), a[4]
    marks = []
    i = 5
    while i < len(a):
        if a[i] == "--mark":
            marks.append((int(a[i + 1]), int(a[i + 2]), a[i + 3])); i += 4
        else:
            i += 1
    im = shoot(x, z, w, h)
    im.thumbnail((1024, 1024))
    W, H = im.size
    cw, ch = W / w, H / h
    d = ImageDraw.Draw(im)
    for n, (mx, mz, note) in enumerate(marks):
        px = (mx - x + 0.5) * cw
        py = (z + h - mz - 0.5) * ch
        col = INK[n % len(INK)]
        wobbly_circle(d, px, py, max(cw, ch) * 2.2, col)
        tx = px + max(cw, ch) * 2.6 if px < W * 0.6 else px - max(cw, ch) * 2.6 - len(note) * 15
        text(d, (max(8, tx), max(8, py - 20)), note, 34, col)
    text(d, (20, H - 70), caption, 46, INK[0])
    buf = io.BytesIO(); im.save(buf, "PNG")
    req = urllib.request.Request("http://127.0.0.1:4317/api/cam",
                                 data=json.dumps({"png": base64.b64encode(buf.getvalue()).decode(),
                                                  "caption": caption}).encode(),
                                 headers={"Content-Type": "application/json"})
    print(urllib.request.urlopen(req, timeout=60).read().decode())


if __name__ == "__main__":
    main()
