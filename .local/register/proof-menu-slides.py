# -*- coding: utf-8 -*-
"""Assert every menu slide will actually appear, and that the folder cannot fail silently.

The property this exists for
----------------------------
The slideshow scans its folder and keeps files whose name starts with `RR_Menu_`, so **a slide
added with any other name is loaded by nothing and shown to nobody** -- and no build, checker or
log would say so. That is exactly the failure class this project keeps finding: the whole request
surface read by nothing, five PawnKindDefs authored and unread, three dead gate accessors, two
menu textures reported unreferenced for months.

The art is produced separately from the code, which makes a naming mistake likely rather than
hypothetical. Four things have to hold:

  * **Every file in the slide folder carries the prefix.** Otherwise it silently never appears.
  * **Every file is on the package allowlist.** Otherwise it does not ship at all.
  * **Every file is a structurally complete PNG.** A truncated download is the obvious way for
    parallel art delivery to go wrong, and Unity would fail at load rather than at build.
  * **They share one aspect ratio.** `BackgroundRect` reads each image's own aspect, so mismatched
    slides letterbox differently and the crossfade between them reads as a bug.

Run from the repository root.
"""
import io
import os
import re
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
SLIDES = os.path.join(MOD, "Textures", "UI", "Menu")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# The prefix and folder are read out of the source, never restated here. If somebody renames
# either one, this proof follows them rather than quietly checking the old value.
menu_source = io.open(os.path.join(SRC, "Presentation", "RimroomsMenuBackground.cs"),
                      encoding="utf-8-sig").read()
folder_match = re.search(r'const\s+string\s+SlideFolder\s*=\s*"([^"]+)"', menu_source)
prefix_match = re.search(r'const\s+string\s+SlidePrefix\s*=\s*"([^"]+)"', menu_source)
check("the slide folder and prefix were read out of the source",
      folder_match is not None and prefix_match is not None,
      "-- without them this proof would be checking a remembered value")
if folder_match is None or prefix_match is None:
    print("\nPROOF FAILED: cannot locate the slide folder or prefix")
    sys.exit(1)

folder = folder_match.group(1)
prefix = prefix_match.group(1)
print("folder %r, prefix %r" % (folder, prefix))

check("the scan is a folder scan, not a hardcoded list",
      "GetAllInFolder" in menu_source,
      "-- new art would need a C# edit, which is the wrong shape for a parallel art track")
check("the scan is filtered by the prefix",
      "StartsWith(SlidePrefix" in menu_source,
      "-- ContentFinder resolves across EVERY loaded mod, so an unfiltered scan pulls another "
      "mod's menu art into this slideshow")
check("slides are ordered ordinally",
      "StringComparer.Ordinal" in menu_source,
      "-- invariant 26: running order would depend on the install")

# ---------------------------------------------------------------- the files themselves
check("the slide folder exists", os.path.isdir(SLIDES))
names = sorted(n for n in os.listdir(SLIDES) if n.lower().endswith(".png")) if os.path.isdir(SLIDES) else []
print("slides on disk: %d" % len(names))
check("at least two slides ship", len(names) >= 2, "-- one slide cannot crossfade with anything")

unprefixed = [n for n in names if not n.startswith(prefix)]
check("every file in the slide folder carries the prefix",
      not unprefixed,
      "-- %s: loaded by nothing, shown to nobody, and NOTHING ELSE WOULD SAY SO"
      % ", ".join(unprefixed))

allow = io.open(os.path.join(REPO, "tools", "package-files.json"), encoding="utf-8").read()
unlisted = [n for n in names
            if '"1.6/Textures/%s/%s"' % (folder, n) not in allow.replace("\\", "/")]
check("every slide is on the package allowlist",
      not unlisted,
      "-- %s: would not ship, and check-package-integrity.py refuses the build"
      % ", ".join(unlisted))

# ---------------------------------------------------------------- structural PNG validity
broken, aspects = [], {}
for name in names:
    raw = io.open(os.path.join(SLIDES, name), "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        broken.append("%s (bad signature)" % name)
        continue
    end = raw.rfind(b"IEND")
    if end < 0 or len(raw) - (end + 8) != 0:
        broken.append("%s (IEND is not the final chunk: truncated or padded)" % name)
        continue
    width, height = struct.unpack(">II", raw[16:24])
    if width <= 0 or height <= 0:
        broken.append("%s (%dx%d)" % (name, width, height))
        continue
    aspects[name] = (width, height, float(width) / height)

check("every slide is a structurally complete PNG",
      not broken,
      "-- %s: Unity fails at LOAD, not at build, so nothing here would catch it otherwise"
      % ", ".join(broken))

# One aspect, within a tolerance that allows a rounded pixel but not a different shape.
if aspects:
    values = [value[2] for value in aspects.values()]
    spread = max(values) - min(values)
    detail = ", ".join("%s %dx%d" % (n, v[0], v[1]) for n, v in sorted(aspects.items()))
    check("every slide shares one aspect ratio to within a rounded pixel",
          spread < 0.01,
          "-- spread %.4f across %s: BackgroundRect reads each image's OWN aspect, so mismatched "
          "slides letterbox differently and the crossfade reads as a bug" % (spread, detail))
    print("  aspects: %s" % detail)

# ---------------------------------------------------------------- provenance, for the release
# Steam requires AI-content disclosure, and original menu images are the ONE exception to this
# project's no-new-art rule. A provenance record is what makes both statements checkable rather
# than remembered at release time.
provenance = []
outputs = os.path.join(REPO, "outputs")
if os.path.isdir(outputs):
    for root, _dirs, files in os.walk(outputs):
        for name in files:
            if name == "prompts-and-provenance.json":
                provenance.append(os.path.join(root, name))
check("a provenance record ships for the generated menu art",
      bool(provenance),
      "-- Steam requires AI-content disclosure, and menu images are the one place this mod is "
      "allowed to add art at all; the record is what makes that auditable")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every slide will appear, ships, loads, and matches its neighbours")
