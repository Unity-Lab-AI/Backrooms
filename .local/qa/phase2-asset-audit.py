# -*- coding: utf-8 -*-
"""Measure what the phase2 source art would need before a game could load it.

Three questions a filename cannot answer:
  1. Does the carpet tile? A terrain texture that does not wrap seams into a grid.
  2. How much of each cut-out is actually ink? A sprite that is 90% empty wastes
     an atlas slot and reads tiny in game at the size its footprint allows.
  3. What is the tight bounding box? That is the real aspect ratio, and it is what
     decides whether an object is a 1x1, a 2x1 or a 3x1 on the ground.
"""
import glob
import os
import sys

from PIL import Image, ImageChops

SRC = "assets/source/phase2/*.png"
CARPET = "assets/source/phase2/RR_FadedInstitutionalCarpet.png"


def seam_error(img, band=24):
    """Mean absolute difference between opposite edges. 0 = wraps perfectly."""
    img = img.convert("RGB")
    w, h = img.size
    left = img.crop((0, 0, band, h))
    right = img.crop((w - band, 0, w, h))
    top = img.crop((0, 0, w, band))
    bottom = img.crop((0, h - band, w, h))

    def diff(a, b):
        d = ImageChops.difference(a, b)
        px = list(d.getdata())
        return sum(sum(p) for p in px) / float(len(px) * 3)

    return diff(left, right), diff(top, bottom)


def main():
    paths = sorted(glob.glob(SRC))
    if not paths:
        print("REFUSED: no source art matched %s" % SRC)
        return 1
    print("%-34s %11s %7s %13s" % ("asset", "tight box", "ink%", "box aspect"))
    print("-" * 70)
    for p in paths:
        img = Image.open(p)
        name = os.path.basename(p)[3:-4]
        if img.mode not in ("RGBA", "LA"):
            print("%-34s %11s %7s %13s" % (name, "opaque", "100.0", "terrain"))
            continue
        alpha = img.convert("RGBA").split()[3]
        box = alpha.getbbox()
        bw, bh = box[2] - box[0], box[3] - box[1]
        opaque = sum(1 for v in alpha.getdata() if v > 8)
        ink = 100.0 * opaque / float(img.size[0] * img.size[1])
        print("%-34s %5dx%-5d %6.1f%% %13s" % (name, bw, bh, ink, "%.2f : 1" % (bw / float(bh))))

    print()
    carpet = Image.open(CARPET)
    lr, tb = seam_error(carpet)
    print("carpet seam error  left/right %.2f   top/bottom %.2f   (0 = tiles cleanly, >6 shows a grid)" % (lr, tb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
