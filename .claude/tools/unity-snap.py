"""Post an annotated game screenshot to the stream's REPRESENTATION panel -- Unity circling things
and scribbling notes over the game in her own handwriting.

    python .claude/tools/unity-snap.py X Z W H "caption" [--mark X Z "note"]... [--arrow X Z "note"]...

X Z W H is the map rect to shoot (cells). --mark circles a cell and writes the note beside it.
Owner (2026-10-08): "you can even post game screenshots highlighted things that happen with your hand
writting drawn over top" / "like circle things and write messsages". Notes reach the stream: keep them
clean (CONSTRAINTS: THE STREAM IS CLEAN).
"""
import time, base64, io, json, os, random, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def studio_token():
    """Per-session token the studio server writes for its local helpers (needed for every POST)."""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".studio-token"),
                  encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""

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


def _mark_highlight():
    """The webcam panel shows a highlight for at most ~20 s, then cam-director.py puts Unity back up (owner,
    2026-10-09: "leave the profile pic of ur up more and the slide show highlights just intermittently for liek
    20 second max so it settle on a new you doing things")."""
    try:
        import json as _j, time as _t
        _j.dump({"ts": _t.time()}, open(os.path.join(ROOT, ".claude", ".cam-highlight.json"), "w"))
    except Exception:
        pass


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
    # Owner, 2026-10-13: "the highlights she does on the screen captures are just all the same resolution and zoom and no
    # one can see them whats being pointed out ... the text needs to be like 50% bigger and properly aligned in the image
    # ... zoomed in possibly screencapturues with text not cut off in the display window". So: the shot ZOOMS on the
    # marks (a tight box around them, never her whole rect), the frame is sized for the panel, the notes are numbered
    # callouts kept inside the frame, and the caption plus a numbered legend sit in a band under the picture that the
    # panel always shows -- nothing drawn where the panel crops.
    MAX_W, MAX_H = 20, 11                      # cells: wider than this and a colonist is a dot
    if marks:
        xs = [m[0] for m in marks]; zs = [m[1] for m in marks]
        bx0, bx1, bz0, bz1 = min(xs) - 4, max(xs) + 4, min(zs) - 3, max(zs) + 3
        if bx1 - bx0 + 1 < 14: c = (bx0 + bx1) // 2; bx0, bx1 = c - 7, c + 6
        if bz1 - bz0 + 1 < 8: c = (bz0 + bz1) // 2; bz0, bz1 = c - 4, c + 3
        x, z, w, h = bx0, bz0, min(MAX_W, bx1 - bx0 + 1), min(MAX_H, bz1 - bz0 + 1)
    elif w > MAX_W or h > MAX_H:
        cx, cz = x + w // 2, z + h // 2
        w, h = min(w, MAX_W), min(h, MAX_H); x, z = cx - w // 2, cz - h // 2
    im = shoot(x, z, w, h)
    FRAME_W = 1120                             # twice the overlay panel's width: readable after the panel halves it
    im = im.resize((FRAME_W, max(1, int(im.size[1] * FRAME_W / max(1, im.size[0])))), Image.LANCZOS)
    W, H = im.size
    cw, ch = W / w, H / h
    d = ImageDraw.Draw(im)
    badge = ImageFont.truetype(FONT, 52)
    for n, (mx, mz, note) in enumerate(marks):
        px = (mx - x + 0.5) * cw
        py = (z + h - mz - 0.5) * ch
        col = INK[n % len(INK)]
        r = max(cw, ch) * 1.6
        wobbly_circle(d, px, py, r, col)
        # a numbered badge beside the circle, clamped inside the frame; the words go in the legend below
        bx = px + r + 8 if px < W * 0.7 else px - r - 70
        by = min(max(6, py - 34), H - 70)
        bx = min(max(6, bx), W - 70)
        d.ellipse((bx, by, bx + 62, by + 62), fill=(0, 0, 0), outline=col, width=4)
        d.text((bx + 18, by + 2), str(n + 1), font=badge, fill=col)
    # the band: caption (50 % bigger than before, wrapped to the frame) + the legend "1 note / 2 note"
    cap_font = ImageFont.truetype(FONT, 70); leg_font = ImageFont.truetype(FONT, 50)
    def wrap(txt, font, width):
        words, lines, cur = txt.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if d.textlength(t, font=font) <= width: cur = t
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
        return lines or [""]
    cap_lines = wrap(caption, cap_font, W - 48)
    leg_lines = [ln for n, (_, _, note) in enumerate(marks) for ln in wrap("%d  %s" % (n + 1, note), leg_font, W - 48)]
    band_h = 24 + len(cap_lines) * 82 + len(leg_lines) * 60 + 16
    canvas = Image.new("RGB", (W, H + band_h), (12, 10, 14))
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas)
    y = H + 16
    for ln in cap_lines:
        text(d, (24, y), ln, 70, INK[0]); y += 82
    for n, ln in enumerate(leg_lines):
        text(d, (24, y), ln, 50, INK[min(len(INK) - 1, int(ln.split()[0]) - 1) if ln[:1].isdigit() else 1]); y += 60
    im = canvas
    buf = io.BytesIO(); im.save(buf, "PNG")
    req = urllib.request.Request("http://127.0.0.1:4317/api/cam",
                                 data=json.dumps({"png": base64.b64encode(buf.getvalue()).decode(),
                                                  "caption": caption}).encode(),
                                 headers={"Content-Type": "application/json", "X-Studio-Token": studio_token()})
    print(urllib.request.urlopen(req, timeout=60).read().decode())
    _mark_highlight()
    # owner: "keep a colonist in view at all times" -- hand the camera back to the crew; but in a fight the
    # camera goes back on the enemy (owner, 2026-10-09: "focus on the fucking action no t the fucking middle of
    # the base"): step.py --hostiles writes .claude/.fight.json with the framed rect every slice
    fight = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".fight.json")
    try: f = json.load(open(fight))
    except Exception: f = {}
    if f.get("rect") and time.time() - f.get("ts", 0) < 90:
        subprocess.run([sys.executable, BRIDGE, "call", "rimworld/frame_cell_rect", json.dumps(f["rect"])], capture_output=True, timeout=60)
        return
    subprocess.run([sys.executable, BRIDGE, "call", "rimworld/set_camera_zoom", json.dumps({"zoomRange": "Close"})], capture_output=True, timeout=60)
    subprocess.run([sys.executable, BRIDGE, "call", "rimworld/jump_camera_to_pawn", json.dumps({"pawnName": "Unity"})], capture_output=True, timeout=60)


if __name__ == "__main__":
    main()
