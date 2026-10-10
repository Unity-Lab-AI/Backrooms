# -*- coding: utf-8 -*-
"""Look at what was actually written into the package, at four times game size.

The cutter reports numbers. A number cannot tell you that a crop clipped a leg off or that the
carpet's mirror reads as a kaleidoscope, so the output gets looked at before it ships.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

ROOT = "Mod/Rimrooms - Async Industries/1.6/Textures"
SCALE = 4
OUT = "artifacts/phase2-cut-sheet.png"
COLS = 4
PAD = 6
LABEL = 14


def checker(size, square=16):
    board = Image.new("RGB", size, (205, 205, 205))
    d = ImageDraw.Draw(board)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if ((x // square) + (y // square)) % 2:
                d.rectangle([x, y, x + square - 1, y + square - 1], fill=(120, 120, 128))
    return board


def main():
    paths = [p for p in sorted(glob.glob(ROOT + "/**/*.png", recursive=True))
             if "UI" + os.sep not in p and "/UI/" not in p.replace(os.sep, "/")]
    if not paths:
        print("REFUSED: nothing cut yet")
        return 1
    cell = 256 * SCALE // 4 + PAD * 2
    rows = (len(paths) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * cell, rows * (cell + LABEL)), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGBA")
        w, h = img.size
        shown = img.resize((w, h), Image.NEAREST)
        back = checker((cell - PAD * 2, cell - PAD * 2))
        back.paste(shown, ((back.size[0] - w) // 2, (back.size[1] - h) // 2), shown)
        cx = (i % COLS) * cell + PAD
        cy = (i // COLS) * (cell + LABEL) + PAD
        sheet.paste(back, (cx, cy))
        draw.text((cx, cy + back.size[1] + 2),
                  "%s %dx%d" % (os.path.basename(p)[3:-4], w, h), fill=(240, 240, 240))
    sheet.save(OUT)
    print("wrote %s %dx%d from %d cut textures" % ((OUT,) + sheet.size + (len(paths),)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
