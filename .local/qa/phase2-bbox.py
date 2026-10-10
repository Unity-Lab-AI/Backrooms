# -*- coding: utf-8 -*-
"""Tight bounding box at a real alpha threshold.

The first pass used PIL's getbbox(), which treats alpha 1 as present. A master carrying a
faint soft shadow therefore reports a box the size of the shadow, and the field analysis
bench -- which is visibly wider than it is tall -- came back 966x1130. A threshold is the
difference between measuring the object and measuring its halo.
"""
import glob
import os
import sys

from PIL import Image

SRC = "assets/source/phase2/*.png"


def tight(alpha, threshold):
    mask = alpha.point(lambda v: 255 if v > threshold else 0)
    return mask.getbbox()


def main():
    print("%-30s %13s %13s %13s" % ("asset", "a>0", "a>32", "a>128"))
    print("-" * 74)
    for p in sorted(glob.glob(SRC)):
        img = Image.open(p)
        name = os.path.basename(p)[3:-4]
        if img.mode not in ("RGBA", "LA"):
            print("%-30s %13s" % (name, "opaque"))
            continue
        alpha = img.convert("RGBA").split()[3]
        cells = []
        for threshold in (0, 32, 128):
            box = tight(alpha, threshold)
            if box is None:
                cells.append("empty")
                continue
            w, h = box[2] - box[0], box[3] - box[1]
            cells.append("%dx%d %.2f" % (w, h, w / float(h)))
        print("%-30s %13s %13s %13s" % (name, cells[0], cells[1], cells[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
