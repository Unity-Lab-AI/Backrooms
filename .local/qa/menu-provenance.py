# -*- coding: utf-8 -*-
"""Give every shipped menu image a provenance row, and correct the six new ones.

Four of the twelve slides had no row at all -- the 2026-09-29 batch. Steam
requires AI-content disclosure per asset and this register is the auditable
artefact, so four shipped images were undisclosed and nothing could see it:
`proof-menu-slides.py` only checked that *some* provenance file existed
anywhere under outputs/. The claim is tightened in the same change.
"""
import io
import csv
import os
import sys

NL = chr(10)
PATH = "docs/research/provenance-register.csv"
SLIDES = "Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu"

# The 2026-09-29 batch, recorded against the record that produced them.
MISSING = [
    ("RR_Menu_CorridorEncounter", "Corridor encounter"),
    ("RR_Menu_IndustrialGateLogistics", "Industrial gate logistics"),
    ("RR_Menu_LaboratoryOperations", "Laboratory operations"),
    ("RR_Menu_SilentRecovery", "Silent recovery"),
]

rows = list(csv.reader(io.open(PATH, encoding="utf-8-sig")))
header = rows[0]
body = rows[1:]
existing = set(r[0] for r in body if r)

template = None
for r in body:
    if r and r[0] == "RR-MENU-RR_Menu_FieldSurvey_v2":
        template = list(r)
        break
if template is None:
    print("no template row to follow")
    sys.exit(1)

added = 0
for name, label in MISSING:
    record = "RR-MENU-" + name
    if record in existing:
        continue
    row = list(template)
    row[0] = record
    row[2] = label
    row[5] = "../../outputs/menu-art-2026-09-29/prompts-and-provenance.json"
    row[10] = ("../../LICENSE; "
               "../../outputs/menu-art-2026-09-29/prompts-and-provenance.json")
    row[12] = "../../Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/" + name + ".png"
    row[13] = "Included in the shipped development package"
    row[14] = ("Built-in image_gen; no input images or borrowed frames; native resolution, not "
               "4K; no baked title or version. **Registered retroactively on 2026-10-04**: this "
               "image shipped from 0.3.0-dev onward with no row here, which Steam's AI-content "
               "disclosure requires per asset. Found when the twelve shipped slides were counted "
               "against the eight rows; `proof-menu-slides.py` now refuses a slide without one.")
    body.append(row)
    added += 1

# The six 2026-10-04 rows were written before this publication and say so. They are being
# staged and cascaded now, so the cell stops being true the moment that happens.
corrected = 0
for row in body:
    if not row or not row[0].startswith("RR-MENU-"):
        continue
    if row[13] == "Added to local copyable package; not staged or published in this task":
        row[13] = "Included in the shipped development package; staged and published 0.12.84-dev"
        corrected += 1

io.open(PATH, "w", encoding="utf-8", newline="").write("")
with io.open(PATH, "w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle, lineterminator=NL)
    writer.writerow(header)
    for row in body:
        writer.writerow(row)

shipped = sorted(n[:-4] for n in os.listdir(SLIDES) if n.lower().endswith(".png"))
registered = set(r[0][len("RR-MENU-"):] for r in body if r and r[0].startswith("RR-MENU-"))
missing = [n for n in shipped if n not in registered]
print("added %d row(s), corrected %d distribution cell(s)" % (added, corrected))
print("shipped slides: %d, registered: %d, unregistered: %s"
      % (len(shipped), len(registered), missing or "none"))
if missing:
    sys.exit(1)
