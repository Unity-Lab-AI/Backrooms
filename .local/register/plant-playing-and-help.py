# -*- coding: utf-8 -*-
"""Plant a fault, run the check, require failure, restore. Verified writes.

**Every target is run clean before anything is planted.** That is the lesson of 0.12.39-dev: a
plant run there reported 17 of 17 caught and was worthless, because a syntax error had made the
proof exit non-zero unconditionally and every plant registered as caught. A perfect sweep against
a broken checker looks exactly like a perfect sweep.

Three targets, because this batch ships a proof and a checker rule:

  * `proof-playing-and-help.py` -- reachability, the tab's position, the keyboard path, the help
    pane and the play document
  * `tools/check-display-style.py` -- the new readability guard, planted with a real authored
    colour and a real out-of-range font in a real readout file
  * `tools/check-doc-conformance.py` -- planted with a real banned word and a real forbidden
    claim in `docs/PLAYING.md`, the document this batch added to the reader-facing set
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
WINDOW = SRC + "/UI/MainTabWindow_Operations.cs"
HELP = SRC + "/UI/OperationsHelp.cs"
BUTTON = "Mod/Rimrooms - Async Industries/1.6/Defs/MainButtonDefs/RR_MainButtons.xml"
HELP_KEYS = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Help.xml")
PATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_GlowPodMarker.xml"
DOC = "docs/PLAYING.md"
# **The reader-facing rules live on the wiki now.** `PLAYING.md` is the long-form
# working version behind it and is no longer held to the vocabulary rule, the wall rule
# or the row 791 claim guard -- which three plants below detected by going MISSED.
WIKI_DOC = "docs/wiki/troubleshooting.md"
CONF = "tools/check-doc-conformance.py"
STYLE = "tools/check-display-style.py"
PROOF = ".local/register/proof-playing-and-help.py"

# (label, path, old, new, command that must fail)

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
    # ------------------------------------------------------------------ row 821, reachability
    ("ARCHITECT GOES BACK TO BEING REACHABLE FROM NOWHERE", WINDOW,
     'OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Architect"));',
     "// nothing", PROOF),

    ("Assign stops opening from the company panel", WINDOW,
     'OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("Assign"));',
     "// nothing", PROOF),

    ("the world map stops opening from the company panel", WINDOW,
     'OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("World"));',
     "// nothing", PROOF),

    ("a colony control loses its keyed label",
     "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Operations.xml",
     "<RR_Operations_OpenArchitect>Open Architect</RR_Operations_OpenArchitect>\n  ", "", PROOF),

    ("a native tab is opened around Core's worker", WINDOW,
     "target.Worker.InterfaceTryActivate();",
     "Find.WindowStack.Add(target.TabWindow);", PROOF),

    ("an unavailable tab fails silently", WINDOW,
     'Messages.Message("RR_Operations_TabUnavailable".Translate(), MessageTypeDefOf.RejectInput, false);',
     "return;", PROOF),

    # ------------------------------------- row 821 + owner direction 2026-10-02, the tab swap
    # Re-aimed with the claim: Architect keeps far left, Operations sits in its old slot. Both
    # bounds are planted, because a one-sided claim passes a value that re-breaks the other end.
    ("THE TAB GOES BACK TO THE FAR RIGHT OF THE BAR", BUTTON,
     "<order>5</order>", "<order>95</order>", PROOF),

    ("THE TAB TAKES THE FAR-LEFT SLOT BACK OFF ARCHITECT", BUTTON,
     "<order>5</order>", "<order>0</order>", PROOF),

    ("the tab sorts level with Architect instead of after it", BUTTON,
     "<order>5</order>", "<order>1</order>", PROOF),

    ("the tab stops existing without a map", BUTTON,
     "<validWithoutMap>true</validWithoutMap>", "<validWithoutMap>false</validWithoutMap>",
     PROOF),

    ("a second main button appears unnoticed", BUTTON,
     "</Defs>",
     "  <MainButtonDef>\n    <defName>RR_Second</defName>\n    <label>Second</label>\n"
     "    <order>3</order>\n  </MainButtonDef>\n</Defs>", PROOF),

    ("A PATCH STARTS REWRITING CORE'S TAB BAR", PATCH,
     "<Patch>", "<Patch>\n  <!-- MainButtonDef -->", PROOF),

    ("code reorders a main button at runtime", WINDOW,
     "        private static void OpenNativeTab(MainButtonDef target)\n        {",
     "        private static void OpenNativeTab(MainButtonDef target)\n        {\n"
     "            if (target != null) { target.order = 3; }", PROOF),

    ("code hides a main button at runtime", WINDOW,
     "        private static void OpenNativeTab(MainButtonDef target)\n        {",
     "        private static void OpenNativeTab(MainButtonDef target)\n        {\n"
     "            MainButtonDef mainButton = target; mainButton.buttonVisible = false;", PROOF),

    # ------------------------------------------------------------------ rows 822/833, keyboard
    ("THE KEYBOARD PATH DISAPPEARS", BUTTON,
     "    <defaultHotKey>Backslash</defaultHotKey>\n", "", PROOF),

    ("the hotkey steals one Core already uses", BUTTON,
     "<defaultHotKey>Backslash</defaultHotKey>", "<defaultHotKey>F1</defaultHotKey>", PROOF),

    ("THE HOTKEY GOES BACK TO F12, WHICH HUGSLIB BINDS", BUTTON,
     "<defaultHotKey>Backslash</defaultHotKey>", "<defaultHotKey>F12</defaultHotKey>", PROOF),

    ("the hotkey steals the screenshot key", BUTTON,
     "<defaultHotKey>Backslash</defaultHotKey>", "<defaultHotKey>F10</defaultHotKey>", PROOF),

    ("help names the shipped key instead of the player's binding", HELP,
     "return self.hotKey.MainKeyLabel;", 'return "Backslash";', PROOF),

    ("an unset binding dereferences null", HELP,
     "if (self == null || self.hotKey == null)", "if (self == null)", PROOF),

    ("the player is no longer told where to rebind it", HELP,
     'listing.Label("RR_Help_KeyboardRebind".Translate());', "// nothing", PROOF),

    # ------------------------------------------------------------ rows 822/833, contrast + scale
    ("THE READABILITY GUARD IS UNWIRED", STYLE,
     "    check_readability(problems)\n", "", PROOF),

    ("the guard stops refusing authored colour", STYLE,
     'AUTHORED_COLOUR = (', 'AUTHORED_COLOUR_UNUSED = (', PROOF),

    ("the guard stops refusing an out-of-range font", STYLE,
     "CORE_FONTS = (", "CORE_FONTS_UNUSED = (", PROOF),

    # The guard itself, planted with a real authored colour in a real readout file. This is the
    # only plant that proves the rule would have caught the thing it exists for.
    ("ROW 822: A READOUT FILE AUTHORS ITS OWN COLOUR", HELP,
     "        private static void DrawHelp(Listing_Standard listing)\n        {",
     "        private static readonly UnityEngine.Color Warn = new UnityEngine.Color(1f, 0f, 0f);\n\n"
     "        private static void DrawHelp(Listing_Standard listing)\n        {", STYLE),

    ("ROW 822: a readout file paints over the player's palette", HELP,
     "            listing.Label(\"RR_Help_Heading\".Translate());",
     "            UnityEngine.GUI.color = UnityEngine.Color.red;\n"
     "            listing.Label(\"RR_Help_Heading\".Translate());", STYLE),

    ("ROW 833: a readout file sets a font outside Core's four", WINDOW,
     "                Text.Font = GameFont.Medium;", "                Text.Font = (GameFont)7;",
     STYLE),

    ("ROW 833: a readout file sets a pixel font size", WINDOW,
     "                Text.Font = GameFont.Medium;",
     "                Text.fontStyles[0].fontSize = 9;", STYLE),

    ("the same authored colour is caught by the proof's own reader", HELP,
     "        private static void DrawHelp(Listing_Standard listing)\n        {",
     "        private static readonly UnityEngine.Color Warn = new UnityEngine.Color(1f, 0f, 0f);\n\n"
     "        private static void DrawHelp(Listing_Standard listing)\n        {", PROOF),

    # ---------------------------------------------- the state guard, added 0.12.43-dev
    # The first real launch found the hole in the contrast rule: no window entry point reset
    # Unity's process-wide draw state, so the setup page drew its frame and an empty body with
    # nothing in the log. These plants are about that fix not regressing silently.
    ("THE STATE GUARD LOSES ITS RESTORE", "src/RimroomsAsyncIndustries/UI/RimroomsWindowState.cs",
     "            GUI.color = color;\n", "", PROOF),

    ("the state guard stops resetting the tint",
     "src/RimroomsAsyncIndustries/UI/RimroomsWindowState.cs",
     "GUI.color = Color.white;", "// no reset", PROOF),

    ("the state guard stops being disposable",
     "src/RimroomsAsyncIndustries/UI/RimroomsWindowState.cs",
     "IDisposable", "IEquatable<int>", PROOF),

    ("THE SETUP PAGE GOES BACK TO DRAWING UNGUARDED",
     "src/RimroomsAsyncIndustries/Scenario/Page_RimroomsCompanySetup.cs",
     "using (RimroomsWindowState.Clean())", "if (true)", PROOF),

    ("the operations tab goes back to drawing unguarded", WINDOW,
     "            using (RimroomsWindowState.Clean())\n", "", PROOF),

    ("the state guard chooses a colour instead of resetting",
     "src/RimroomsAsyncIndustries/UI/RimroomsWindowState.cs",
     "GUI.color = Color.white;", "GUI.color = Color.red;", STYLE),

    ("the state guard builds a colour",
     "src/RimroomsAsyncIndustries/UI/RimroomsWindowState.cs",
     "GUI.color = Color.white;", "GUI.color = new Color(1f, 1f, 1f, 0.5f);", STYLE),

    ("the checker stops policing the guard's own rules", STYLE,
     "            for needle, why in GUARD_REQUIRED:", "            for needle, why in []:",
     PROOF),

    ("the checker stops requiring the guard to exist", STYLE,
     "    if not guard_seen:", "    if False:", PROOF),

    ("the checker stops requiring every window to adopt it", STYLE,
     "    if unguarded:", "    if False and unguarded:", PROOF),

    ("the caller's font is never restored", WINDOW,
     "                Text.Font = previousFont;", "                // leaked", PROOF),

    # ---------------------------------------------------------------- rows 822/833, the help pane
    ("HELP IS ONLY REACHABLE ONCE YOU ALREADY HAVE A COMPANY", WINDOW,
     "                if (selectedPane == HelpPane)\n                {\n"
     "                    DrawHelp(listing);\n                }\n                else if",
     "                if", PROOF),

    ("help moves inside the company block", WINDOW,
     "            switch (selectedPane)\n            {",
     "            DrawHelp(listing);\n            switch (selectedPane)\n            {", PROOF),

    ("help drops off the pane list", WINDOW,
     ', "RR_UI_Help" };', " };", PROOF),

    ("a glossary term stops resolving", HELP_KEYS,
     "  <RR_Help_TermThreshold>", "  <RR_Help_TermThresholdX>", PROOF),

    ("the glossary stops defining the mod's own first word", HELP,
     '"RR_Help_TermGate", ', "", PROOF),

    ("THE HELP PANE STOPS SAYING THE BUILD IS UNPLAYED", HELP,
     'listing.Label("RR_Help_Untested".Translate());', "// nothing", PROOF),

    # ------------------------------------------------------------------- rows 1193/1220, the doc
    ("A WIKI PAGE LEAVES THE READER-FACING SET", CONF,
     '    os.path.join(WIKI, "troubleshooting.md"),\n', "", PROOF),

    ("the wall limit goes back to the one the owner superseded", CONF,
     "DOC_WALL_CHARS = 360", "DOC_WALL_CHARS = 700", PROOF),

    ("a wiki page is deleted and nothing notices", CONF,
     '    os.path.join(WIKI, "install.md"),\n', "", PROOF),

    # Re-aimed at 0.12.79-dev with the claim it plants against. The old anchor removed the
    # sentence *"No game has ever been launched from this repository"*, which the document stopped
    # saying because it stopped being true. The claim is the caveat, so the plant still turns the
    # caveat into the overclaim -- the same defect, aimed at the words that carry it now.
    ("the play document stops saying the mod is unplayed", DOC,
     "and it has not been played through",
     "and it has been played through and it works", PROOF),

    ("the play document claims to outrank the game's own readouts", DOC,
     "the game's own readouts are right and this page is wrong",
     "this page is the authority", PROOF),

    ("the play document stops recording the unbuilt remap", DOC,
     "**It does not remap RimWorld's own menus.**", "**Menus.**", PROOF),

    # F12 is named once in the document, on purpose. It was named twice at first, and this
    # plant passed by removing one of them while the claim stayed satisfied by the other --
    # the plant was weak, and so was writing the same fact in two places.
    ("the play document drops the keyboard path", DOC,
     "bound to **Backslash** by default", "reachable from the bottom bar", PROOF),

    ("the play document stops saying where to rebind it", DOC,
     "appears in your Key Bindings dialog", "is fixed", PROOF),

    # The reader-facing rules, planted in the document this batch just added to that set.
    ("ROW 791: A REAL SHARED-COLONY CLAIM LANDS IN A WIKI PAGE", WIKI_DOC,
     "\n## Reporting a problem",
     "\n\nTwo players run one shared colony together.\n\n## Reporting a problem", CONF),

    ("the retired vocabulary lands in a wiki page", WIKI_DOC,
     "A gate needs a registered coordinate to dial",
     "A portal needs a registered coordinate to dial", CONF),

    # DOC_WALL_CHARS is 700, so the filler has to clear 700 rendered characters in a single
    # paragraph. A first attempt came to roughly 590 and passed, which made the plant wrong
    # rather than the rule -- the same shape as the `maxTechLevel` replant at 0.12.37-dev.
    ("A WALL OF TEXT LANDS IN A WIKI PAGE", WIKI_DOC,
     "\n## Reporting a problem",
     "\n\n" + "The company account is a ledger in dollars and it pays quoted company costs such as staff wages and site fees and procurement orders and outstanding obligations, and it is never spawned as physical silver for somebody to haul across a map on foot, which is the whole distinction the two kinds of money exist to draw in the first place, and it is also the reason the ledger pane lists a written reason beside every movement rather than leaving a player to work out where the money went on their own." + "\n\n## Reporting a problem", CONF),
]


def write_verified(path, text):
    """Write, read back, compare. `io.open(w)` truncates before writing, so a failed write is
    not a no-op -- it leaves a planted fault on disk. That happened at 0.12.36-dev."""
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


# ------------------------------------------------------------------------------------------- #
# Every target, run clean, before a single fault is planted.
# ------------------------------------------------------------------------------------------- #
print("baseline -- each target must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
