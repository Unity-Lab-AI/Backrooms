# -*- coding: utf-8 -*-
"""Repair the plant entries a bash heredoc mangled by turning \\n into real newlines.

Fourth time this session. The rule already written in NOW.md is: **use a file, not a heredoc, for
any script containing escapes or apostrophes.** This is that file.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

NL = "\\n"          # the two characters backslash-n, which is what the source needs
lines = io.open(PATH, encoding="utf-8").read().split("\n")
out = []
index = 0
while index < len(lines):
    line = lines[index]

    # 1. ForceGen: a string broken across three physical lines.
    if 'public void ForceGen()' in line:
        out.append('     "        public void ForceGen() '
                   '{ Find.GameInitData.mapGeneratorDef = null; }' + NL + NL + '"')
        index += 3
        continue

    # 2. the mapGenerator re-add, broken across two lines
    if '<mapGenerator>RR_Headquarters</mapGenerator>' in line and line.strip().startswith('"'):
        out.append('     "    <mapGenerator>RR_Headquarters</mapGenerator>' + NL
                   + '    <arrivalCell>(30, 0, 23)</arrivalCell>",')
        index += 2
        continue

    # 3. the dropped genstep line
    if '<li>RR_HeadquartersFacility</li>' in line and line.strip().startswith('"'):
        out.append('     "      <li>RR_HeadquartersFacility</li>' + NL + '", "", PROOF),')
        index += 2
        continue

    # 4. the null-check removal, broken across two lines
    if 'if (start == null) { return; }' in line and line.strip().startswith('"'):
        out.append('     "            if (start == null) { return; }' + NL
                   + '            HeadquartersSetupComponent receipt",')
        index += 2
        continue

    # 5. the terrain flatten, two multi-line strings
    if 'foreach (CellRect rect in HeadquartersLayout.Rooms(start, offset))' in line \
            and line.strip().startswith('"'):
        out.append('     "            foreach (CellRect rect in HeadquartersLayout.Rooms(start, '
                   'offset))" + CHR_NL + "            {" + CHR_NL + '
                   '"                foreach (IntVec3 cell in rect.Cells)",')
        out.append('     "            foreach (IntVec3 cell in map.AllCells) '
                   '{ map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }" + CHR_NL')
        out.append('     + "            foreach (CellRect rect in HeadquartersLayout.Rooms('
                   'start, offset))" + CHR_NL + "            {" + CHR_NL')
        out.append('     + "                foreach (IntVec3 cell in rect.Cells)",')
        index += 7
        continue

    out.append(line)
    index += 1

text = "\n".join(out)
# One shared newline constant, so the repaired entries read as intent rather than as escapes.
text = text.replace('PATCHFILE = "Mod/Rimrooms',
                    'CHR_NL = chr(10)\nPATCHFILE = "Mod/Rimrooms', 1)
io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("plant escapes repaired")
