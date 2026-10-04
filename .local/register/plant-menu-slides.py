# -*- coding: utf-8 -*-
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

# (label, path, old, new)

# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    ("THE DEFECT THE OWNER SAW: the menu goes back to opening on slide one", BACKGROUND,
     "            currentIndex = RimroomsSlideArt.RandomIndex(slides.Count);\n"
     "            lastExpansionHoverAt = Time.unscaledTime;",
     "            currentIndex = 0;\n"
     "            lastExpansionHoverAt = Time.unscaledTime;"),

    ("and the SETTINGS RESET goes back to it, the second route to slide one forever", BACKGROUND,
     "            currentIndex = RimroomsSlideArt.RandomIndex(slides.Count);\n"
     "            lastExpansionHoverAt = protectNativeExpansionPreview",
     "            currentIndex = 0;\n"
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


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


def run(target):
    return subprocess.call([sys.executable, target],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


print("clean run first, so a plant that 'fails' cannot be a pre-existing fault")
code = run(PROOF)
print("  %-46s exit %d" % (PROOF, code))
if code != 0:
    print("ABORTED: the proof does not pass clean")
    sys.exit(2)
print("")

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    hits = original.count(old)
    if hits != 1:
        print("PLANT SETUP BROKEN (%d matches, need exactly 1): %s" % (hits, label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = run(PROOF)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    if io.open(path, encoding="utf-8").read() != original:
        sys.stderr.write("FATAL: %s not restored -- CHECK BY HAND\n" % path)
        sys.exit(3)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s (exit %d)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
