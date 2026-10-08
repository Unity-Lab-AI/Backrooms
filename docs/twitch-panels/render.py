"""Renders the Twitch link panels (320x110) in the stream overlay's style.
    python docs/twitch-panels/render.py
Each PNG is uploaded as a panel image on twitch.tv and set to link to its URL (docs/TWITCH_PANELS.md)."""
from PIL import Image, ImageDraw, ImageFont
import os
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 320, 110
PINK = (255, 79, 163); INK = (255, 224, 239); LILAC = (201, 167, 255); BG = (10, 7, 13)
sub = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
sym = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", 44)
LINK, WAIT = "\U0001F517", "\u23F3"
PANELS = [("site", "Mod site & wiki", "rimrooms async industries", LINK),
          ("install", "Install guide", "how to set it up", LINK),
          ("modlist", "Mod list", "every mod in the pack", LINK),
          ("source", "Source code", "github repo", LINK),
          ("bugs", "Report a bug", "github issues", LINK),
          ("workshop", "Workshop", "coming soon", WAIT)]
for key, title, caption, glyph in PANELS:
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for y in range(0, H, 3): d.line([(0, y), (W, y)], fill=(16, 11, 19))
    d.rounded_rectangle([2, 2, W - 3, H - 3], radius=10, outline=PINK, width=3)
    d.rounded_rectangle([7, 7, W - 8, H - 8], radius=7, outline=(90, 30, 64), width=1)
    d.rounded_rectangle([16, 18, 88, 90], radius=10, fill=(30, 10, 26), outline=PINK, width=2)
    bb = d.textbbox((0, 0), glyph, font=sym)
    d.text((52 - (bb[2] - bb[0]) / 2 - bb[0], 54 - (bb[3] - bb[1]) / 2 - bb[1]), glyph, font=sym,
           fill=LILAC if glyph == WAIT else PINK)
    size = 34
    while True:   # shrink the title until it fits beside the icon
        f = ImageFont.truetype("C:/Windows/Fonts/Inkfree.ttf", size)
        if d.textlength(title, font=f) <= W - 104 - 14 or size <= 18: break
        size -= 1
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): d.text((104 + dx, 24 + dy), title, font=f, fill=(80, 20, 50))
    d.text((104, 24), title, font=f, fill=INK)
    d.text((106, 70), caption.upper(), font=sub, fill=LILAC)
    im.save(os.path.join(HERE, "panel-%s.png" % key))
print("rendered", len(PANELS))
