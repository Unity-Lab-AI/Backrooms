# -*- coding: utf-8 -*-
"""Build .local/register/plant-menu-slides.py from the existing plant harness.

The PLANTS entries need a literal backslash-n inside generated C# anchors. Built
from a token and substituted, because an escape written through a shell heredoc
has been mangled eleven times in this repo and this was the twelfth.
"""
import io

NL = chr(10)
BS_N = chr(92) + "n"      # the two characters a backslash-n is
TOKEN = "@@NEWLINE@@"

src = io.open(".local/register/plant-setup-page-draws.py", encoding="utf-8").read()
head_end = src.index("# (label, path, old, new)")
tail_start = src.index("PLANTS = [")
plants_end = src.index(NL + "]" + NL, tail_start) + len(NL + "]" + NL)

HEADER = '''# -*- coding: utf-8 -*-
"""Plant a fault in the mod's own menu art and require `proof-menu-slides.py` to refuse it.

Plant a fault, run the target, require failure, restore. Verified writes. Clean run first.

**NO PLANT SUITE COVERED THE MENU ART AT ALL**, which is how the headline defect here lived as
long as it did: `currentIndex` was pinned to `0` in the constructor and reset to `0` again in the
settings handler, so the menu -- and the backdrop behind every load started from it -- opened on
slide one of six, every single time, forever. The slideshow cycled perfectly, every claim about
the folder scan and the crossfade held, and nothing in the battery could see it. The owner saw it.

The plants below cover that in both places, the shared list the loading surfaces read, the
deliberate avoidance of `Rand`, the prefix filter that keeps 294 other mods' menu art out of our
slideshow, the ordinal ordering, and the folder scan itself.
"""
import io
import os
import subprocess
import sys
import time

PROOF = ".local/register/proof-menu-slides.py"
SRC = "src/RimroomsAsyncIndustries"
ART = SRC + "/Presentation/RimroomsSlideArt.cs"
BACKGROUND = SRC + "/Presentation/RimroomsMenuBackground.cs"

'''

PLANTS = '''PLANTS = [
    ("THE DEFECT THE OWNER SAW: the menu goes back to opening on slide one", BACKGROUND,
     "            currentIndex = RimroomsSlideArt.RandomIndex(slides.Count);@@NEWLINE@@"
     "            lastExpansionHoverAt = Time.unscaledTime;",
     "            currentIndex = 0;@@NEWLINE@@"
     "            lastExpansionHoverAt = Time.unscaledTime;"),

    ("and the SETTINGS RESET goes back to it, the second route to slide one forever", BACKGROUND,
     "            currentIndex = RimroomsSlideArt.RandomIndex(slides.Count);@@NEWLINE@@"
     "            lastExpansionHoverAt = protectNativeExpansionPreview",
     "            currentIndex = 0;@@NEWLINE@@"
     "            lastExpansionHoverAt = protectNativeExpansionPreview"),

    ("the draw stops being a draw", ART,
     "            int draw = Environment.TickCount;",
     "            int draw = 0;"),

    ("THE DRAW REACHES FOR THE GAME'S SEEDED RANDOMNESS, which every generated place depends on",
     ART,
     "        internal static int RandomIndex(int count)",
     "        internal static int RandomIndexUnused(int count)"),

    ("the loading surfaces stop reading the menu's own list", ART,
     "        internal static List<Texture2D> Slides()",
     "        internal static List<Texture2D> SlidesUnused()"),

    ("and the menu stops asking for the shared list", BACKGROUND,
     "            return RimroomsSlideArt.Slides();",
     "            return new List<Texture2D>();"),

    ("THE PREFIX FILTER GOES, so another mod's menu art joins our slideshow", ART,
     "                        image.name.StartsWith(SlidePrefix, StringComparison.Ordinal))",
     "                        image.name != string.Empty)"),

    ("the ordinal ordering goes, so the running order depends on the install", ART,
     "                    .OrderBy(image => image.name, StringComparer.Ordinal)",
     "                    .OrderBy(image => image.width)"),

    ("the folder scan becomes a list, so new art would need a C# edit", ART,
     "ContentFinder<Texture2D>.GetAllInFolder(SlideFolder)",
     "System.Linq.Enumerable.Empty<Texture2D>()"),
]
'''

out = HEADER + src[head_end:tail_start] + PLANTS.replace(TOKEN, BS_N) + src[plants_end:]
io.open(".local/register/plant-menu-slides.py", "w", encoding="utf-8", newline=NL).write(out)
print("plant-menu-slides.py written, %d plants" % PLANTS.count('    ("'))
