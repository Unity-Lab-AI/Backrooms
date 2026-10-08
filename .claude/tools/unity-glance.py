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


def main():
    caption = " ".join(sys.argv[1:]).strip()
    o = subprocess.run([sys.executable, BRIDGE, "call", "rimworld/take_screenshot", "{}"],
                       capture_output=True, text=True, timeout=120).stdout
    path = json.loads(o[o.find("{"):]).get("path")
    if not path:
        return
    im = Image.open(path).convert("RGB")
    im.thumbnail((1024, 1024))
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


if __name__ == "__main__":
    main()
