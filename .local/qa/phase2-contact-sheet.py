# -*- coding: utf-8 -*-
"""Build a contact sheet of the phase2 source art so it can be examined in one look.

Alpha is composited over a magenta/grey checkerboard: anything that reads as a
flat rectangle instead of a cut-out silhouette has no usable transparency, which
is the single most important fact about a RimWorld gameplay texture.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

TILE = 300
COLS = 4
PAD = 4
LABEL = 14
SRC = "assets/source/phase2/*.png"
OUT = "artifacts/phase2-contact-sheet.png"


def checker(size, square=12):
    board = Image.new("RGB", (size, size), (210, 210, 210))
    d = ImageDraw.Draw(board)
    for y in range(0, size, square):
        for x in range(0, size, square):
            if ((x // square) + (y // square)) % 2:
                d.rectangle([x, y, x + square - 1, y + square - 1], fill=(255, 0, 170))
    return board


def main():
    paths = sorted(glob.glob(SRC))
    if not paths:
        print("REFUSED: no source art matched %s" % SRC)
        return 1
    rows = (len(paths) + COLS - 1) // COLS
    cell = TILE + PAD * 2
    sheet = Image.new("RGB", (COLS * cell, rows * (cell + LABEL)), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        img = Image.open(p)
        has_alpha = img.mode in ("RGBA", "LA")
        img = img.convert("RGBA").resize((TILE, TILE), Image.LANCZOS)
        back = checker(TILE)
        back.paste(img, (0, 0), img)
        cx = (i % COLS) * cell + PAD
        cy = (i // COLS) * (cell + LABEL) + PAD
        sheet.paste(back, (cx, cy))
        tag = "%d %s%s" % (i + 1, os.path.basename(p)[3:-4], "" if has_alpha else " [NO ALPHA]")
        draw.text((cx, cy + TILE + 2), tag, fill=(240, 240, 240))
    sheet.save(OUT)
    print("wrote %s  %dx%d  from %d source images" % ((OUT,) + sheet.size + (len(paths),)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
