# -*- coding: utf-8 -*-
"""Restore the six 2026-10-04 provenance rows I discarded with `git checkout`.

They were uncommitted work from the art pass and I reverted the file to HEAD
while restoring a hand-made test edit. The content is reproduced verbatim from
the diff that was read before the revert; every field was identical across the
six except the record id, the title and the asset path.
"""
import io
import csv
import os
import sys

NL = chr(10)
PATH = "docs/research/provenance-register.csv"
SLIDES = "Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu"

NEW = [
    ("RR_Menu_PanicJunction", "No Way Back"),
    ("RR_Menu_LightsOut", "Do Not Let Go"),
    ("RR_Menu_EmptyCinema", "The Audience"),
    ("RR_Menu_FamiliarStranger", "Someone From Home"),
    ("RR_Menu_BreachedVault", "The Room Behind the Seam"),
    ("RR_Menu_RedTrail", "Keep Moving"),
]

RECORD = "../../outputs/menu-art-2026-10-04-revised/prompts-and-provenance.json"
NOTES = ("Text-only built-in image_gen; no input images; native resolution; no transformations. "
         "New composition. Earlier realistic candidates and reference-based duplicate pilot "
         "rejected, not packaged. Exact prompt and SHA-256 in linked record. No gameplay asset "
         "or behavior change.")

# The 2026-09-29 batch, which had no row at all. Steam's AI-content disclosure is per asset.
RETRO = [
    ("RR_Menu_CorridorEncounter", "Corridor encounter"),
    ("RR_Menu_IndustrialGateLogistics", "Industrial gate logistics"),
    ("RR_Menu_LaboratoryOperations", "Laboratory operations"),
    ("RR_Menu_SilentRecovery", "Silent recovery"),
]
RETRO_NOTES = ("Built-in image_gen; no input images or borrowed frames; native resolution, not "
               "4K; no baked title or version. **Registered retroactively on 2026-10-04**: this "
               "image shipped from 0.3.0-dev onward with no row here, which Steam's AI-content "
               "disclosure requires per asset. Found when the twelve shipped slides were counted "
               "against the eight rows; proof-menu-slides.py now refuses a slide without one.")

rows = list(csv.reader(io.open(PATH, encoding="utf-8-sig")))
header = rows[0]
body = [r for r in rows[1:] if r]
present = set(r[0] for r in body)

for name, title in NEW:
    record = "RR-MENU-" + name
    if record in present:
        continue
    body.append([
        record,
        "Original menu and generation-notice artwork",
        title,
        "Operator (AI-assisted original asset; built-in image_gen)",
        "",
        RECORD,
        "Lead visually inspected final image; native overlay/crop/profile acceptance pending",
        "Existing shared menu and pre-generation notice background pool",
        "Original PNG, 1672x941; copied unchanged",
        "Original generated project art; no blanket MIT or third-party asset license claim",
        RECORD,
        "Preserve project provenance; no copied provider assets",
        "../../Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/" + name + ".png",
        "Included in the shipped development package; staged and published 0.12.84-dev",
        NOTES,
    ])

template = None
for r in body:
    if r[0] == "RR-MENU-RR_Menu_FieldSurvey_v2":
        template = list(r)
        break
if template is None:
    print("no 2026-09-29 template row to follow")
    sys.exit(1)

for name, label in RETRO:
    record = "RR-MENU-" + name
    if record in set(r[0] for r in body):
        continue
    row = list(template)
    row[0] = record
    row[2] = label
    row[5] = "../../outputs/menu-art-2026-09-29/prompts-and-provenance.json"
    row[10] = "../../LICENSE; ../../outputs/menu-art-2026-09-29/prompts-and-provenance.json"
    row[12] = "../../Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/" + name + ".png"
    row[13] = "Included in the shipped development package"
    row[14] = RETRO_NOTES
    body.append(row)

with io.open(PATH, "w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle, lineterminator=NL)
    writer.writerow(header)
    for row in body:
        writer.writerow(row)

shipped = sorted(n[:-4] for n in os.listdir(SLIDES) if n.lower().endswith(".png"))
registered = set(r[0][len("RR-MENU-"):] for r in body if r[0].startswith("RR-MENU-"))
missing = [n for n in shipped if n not in registered]
print("register rows: %d" % len(body))
print("shipped slides: %d, unregistered: %s" % (len(shipped), missing or "none"))
if missing:
    sys.exit(1)
