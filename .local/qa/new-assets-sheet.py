# -*- coding: utf-8 -*-
"""Contact sheet of the gate frames and the journal, on a checkerboard so alpha is visible.

These were authored by another party and have never been looked at here. Describing them on a
published page without looking would be fabrication.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

ROOT = "Mod/Rimrooms - Async Industries/1.6/Textures/Things"
OUT = "artifacts/new-assets-sheet.png"
TILE = 190
COLS = 6
PAD = 4
LABEL = 13


def checker(size, square=10):
    board = Image.new("RGB", (size, size), (200, 200, 200))
    d = ImageDraw.Draw(board)
    for y in range(0, size, square):
        for x in range(0, size, square):
            if ((x // square) + (y // square)) % 2:
                d.rectangle([x, y, x + square - 1, y + square - 1], fill=(110, 110, 120))
    return board


def main():
    paths = sorted(glob.glob(ROOT + "/Building/Rimrooms/Gates/*.png")) + \
        sorted(glob.glob(ROOT + "/Item/Rimrooms/Journal/*.png"))
    if not paths:
        print("REFUSED: nothing found")
        return 1
    cell = TILE + PAD * 2
    rows = (len(paths) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * cell, rows * (cell + LABEL)), (20, 20, 24))
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        img = Image.open(path).convert("RGBA")
        img.thumbnail((TILE, TILE), Image.LANCZOS)
        back = checker(TILE)
        back.paste(img, ((TILE - img.size[0]) // 2, (TILE - img.size[1]) // 2), img)
        x = (i % COLS) * cell + PAD
        y = (i // COLS) * (cell + LABEL) + PAD
        sheet.paste(back, (x, y))
        draw.text((x, y + TILE + 1), os.path.basename(path)[3:-4], fill=(240, 240, 240))
    sheet.save(OUT)
    print("wrote %s %dx%d from %d files" % ((OUT,) + sheet.size + (len(paths),)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
