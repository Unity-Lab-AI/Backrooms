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
NOTICE = SRC + "/Presentation/RimroomsGenerationNotice.cs"
PANE = SRC + "/UI/OperationsPortalNetwork.cs"
KEYS = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed"
        "/RR_Generation.xml")

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


NL = chr(10)
HISTORY = SRC + "/Gate/GateConnectionHistory.cs"
EXPEDITIONS = SRC + "/UI/OperationsExpeditions.cs"

PLANTS = [
    # ------------------- the close-out, planted four ways it could silently stop
    #
    # Owner, 2026-10-05: *"the notice needs to appear before the map bagins to load then close out
    # with a normalization notice"*. Each of these is a way the pair quietly becomes a half.
    ("THE HOLD NEVER CLOSES OUT -- the promise is made and never answered", NOTICE,
     "                    showExtraUIInfo: true, forceHideUI: false, "
     "callback: ShowNormalization)));",
     "                    showExtraUIInfo: true, forceHideUI: false)));"),

    ("the close-out starts forcing a pause, contradicting its own text", NOTICE,
     "            absorbInputAroundWindow = true;" + NL
     + "            closeOnClickedOutside = false;" + NL
     + "            closeOnAccept = true;",
     "            absorbInputAroundWindow = true;" + NL
     + "            forcePause = true;" + NL
     + "            closeOnClickedOutside = false;" + NL
     + "            closeOnAccept = true;"),

    ("the close-out's draw loses its IMGUI guard", NOTICE,
     "            using (RimroomsWindowState.Clean()) { Draw(inRect); }" + NL
     + "        }" + NL
     + NL
     + "        private void Draw(Rect inRect)" + NL
     + "        {" + NL
     + "            float textHeight = Text.CalcHeight(notice, inRect.width);",
     "            Draw(inRect);" + NL
     + "        }" + NL
     + NL
     + "        private void Draw(Rect inRect)" + NL
     + "        {" + NL
     + "            float textHeight = Text.CalcHeight(notice, inRect.width);"),

    ("the hold and its close-out stop sharing one key-scoping rule, so they tone differently",
     NOTICE,
     "            return Toned(DefaultNormalizationKey);",
     '            return "RR_Generation_NormalNotice".Translate();'),

    # The two paths whose exemptions were wrong. Both revert to generating a 300x300 map behind an
    # unexplained freeze, which is the failure the whole feature exists to prevent.
    ("DIALLING A REMEMBERED ADDRESS STOPS ANNOUNCING, the way it used to", HISTORY,
     "                    Presentation.RimroomsGenerationNotice.Announce(" + NL
     + "                        CoordinateOfEntry(entry, campaign), delegate",
     "                    RunDial(" + NL
     + "                        CoordinateOfEntry(entry, campaign), delegate"),

    ("DISPATCHING A CREW stops announcing", EXPEDITIONS,
     "                Presentation.RimroomsGenerationNotice.Announce(coordinate, delegate"
     + NL + "                { ShowResult(trips.Dispatch(gate, coordinate, dispatching)); });",
     "                ShowResult(trips.Dispatch(gate, coordinate, dispatching));"),

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
    # ------------------------------------------------------- the generation freeze, told in time
    # Re-aimed when the close-out added a `callback` argument to the queue call. The anchors now
    # stop at the line they are about rather than carrying the whole argument list, so adding
    # another named argument cannot break them a second time.
    ("THE NOTICE IS QUEUED AFTER THE FREEZE INSTEAD OF BEFORE IT", NOTICE,
     "            Find.WindowStack.Add(new Dialog_RimroomsGenerationNotice(NoticeText(), () =>"
     + NL
     + "                LongEventHandler.QueueLongEvent(work, LongEventKey, false, null,",
     "            work();" + NL + "            if (false) LongEventHandler.QueueLongEvent(null,"),

    ("the work stops running inside a long event, so the freeze is unexplained again", NOTICE,
     "                LongEventHandler.QueueLongEvent(work, LongEventKey, false, null,",
     "                Dummy(work, LongEventKey, false, null,"),

    ("THE NOTICE FIRES ON EVERY CROSSING, so it becomes the nuisance instead of the warning",
     NOTICE,
     "            return coordinate != null && coordinate.Site == null;",
     "            return coordinate != null;"),

    ("and it stops firing at all, because a re-entry test swallows a first build", NOTICE,
     "            return coordinate != null && coordinate.Site == null;",
     "            return false;"),

    ("the pane stops announcing before the laboratory address is taken", PANE,
     "                Presentation.RimroomsGenerationNotice.Announce(opening, () =>\n"
     "                    ShowResult(PortalAddressService.RegisterLaboratoryAddress(opened, opening)));",
     "                ShowResult(PortalAddressService.RegisterLaboratoryAddress(opened, opening));"),

    ("THE BACKDROP STOPS BEING THE MOD'S OWN ART", NOTICE,
     "            backdrop = RimroomsSlideArt.RandomSlide();",
     "            backdrop = null;"),

    ("and the backdrop stops filling the screen", NOTICE,
     "                GUI.DrawTexture(RimroomsSlideArt.FullScreenRect(backdrop), backdrop,",
     "                GUI.DrawTexture(inRect, backdrop,"),

    # **THE WORST ONE, AND IT IS SILENT.** Unity's IMGUI state is process-wide. A leaked
    # zero-alpha `GUI.color` from any of 294 other mods makes a frameless full-screen window draw
    # nothing at all -- so the player sees a frozen game with no notice on it, which is the exact
    # failure the feature exists to prevent, arriving through the feature.
    # Scoped to the HOLD window specifically. Both windows guard their draw with the identical
    # line, so the bare line stopped being unique the moment the close-out was added -- and an
    # ambiguous anchor stops its whole suite rather than planting the wrong half.
    ("THE WINDOW DRAWS WITH WHATEVER GUI STATE IT INHERITED", NOTICE,
     "            using (RimroomsWindowState.Clean()) { Draw(inRect); }" + NL
     + "        }" + NL
     + NL
     + "        private void Draw(Rect inRect)" + NL
     + "        {" + NL
     + "            if (backdrop != null)",
     "            Draw(inRect);" + NL
     + "        }" + NL
     + NL
     + "        private void Draw(Rect inRect)" + NL
     + "        {" + NL
     + "            if (backdrop != null)"),

    ("the per-scenario tone is gone, so every opening reads the same", NOTICE,
     "                if (scoped.CanTranslate()) { key = scoped; }",
     "                if (false) { key = scoped; }"),

    ("and the scenario is no longer consulted at all", NOTICE,
     "            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;",
     "            ScenPart_RimroomsStart part = null;"),

    ("THE COMPANY NOTICE LOSES THE WORDS THAT SAY THE PAUSE IS EXPECTED", KEYS,
     "This is expected.",
     "Something has gone wrong."),

    ("and the owner's rejected placeholder wording comes back", KEYS,
     "THE HOLD IS EXPECTED",
     "Time has froze due to mass distortions, please wait"),
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
