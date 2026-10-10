# -*- coding: utf-8 -*-
"""Repair line 72, mangled by a heredoc for the fifth time. Written as a file, as the rule says."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

lines = io.open(PATH, encoding="utf-8").read().split("\n")
out = []
index = 0
repaired = 0
while index < len(lines):
    line = lines[index]
    if "if (map.Tile != Find.GameInitData.startingTile) { return null; }" in line \
            and line.strip().startswith('"'):
        out.append('     "            if (map.Tile != Find.GameInitData.startingTile) '
                   '{ return null; }" + CHR_NL, "", PROOF),')
        index += 2
        repaired += 1
        continue
    out.append(line)
    index += 1

io.open(PATH, "w", encoding="utf-8", newline="").write("\n".join(out))
print("repaired %d entr(y/ies)" % repaired)
