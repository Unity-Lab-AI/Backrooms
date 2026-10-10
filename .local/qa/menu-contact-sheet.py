# -*- coding: utf-8 -*-
"""Contact sheet of the shipped menu slides, so they can be described from sight.

Writing a description of a picture nobody looked at is fabrication, and it would sit on a published
page under a heading that says what each asset is. Four across, labelled, small enough to read in
one go.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

SRC = "Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/*.png"
OUT = "artifacts/menu-contact-sheet.png"
COLS = 3
WIDTH = 420
LABEL = 16
PAD = 4


def main():
    paths = sorted(glob.glob(SRC))
    if not paths:
        print("REFUSED: no menu slides found")
        return 1
    tile_h = int(WIDTH * 941 / 1672.0)
    rows = (len(paths) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * (WIDTH + PAD * 2), rows * (tile_h + PAD * 2 + LABEL)),
                      (18, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        image = Image.open(path).convert("RGB").resize((WIDTH, tile_h), Image.LANCZOS)
        x = (i % COLS) * (WIDTH + PAD * 2) + PAD
        y = (i // COLS) * (tile_h + PAD * 2 + LABEL) + PAD
        sheet.paste(image, (x, y))
        draw.text((x, y + tile_h + 2), os.path.basename(path)[8:-4], fill=(235, 235, 235))
    sheet.save(OUT)
    print("wrote %s %dx%d from %d slides" % ((OUT,) + sheet.size + (len(paths),)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
