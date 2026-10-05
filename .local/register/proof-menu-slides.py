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


NEWLINE = chr(10)


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# The prefix and folder are read out of the source, never restated here. If somebody renames
# either one, this proof follows them rather than quietly checking the old value.
#
# **THEY MOVED, AND THIS PROOF CAUGHT IT THE SAME MINUTE.** The folder scan, the prefix and the
# ordering lived in `RimroomsMenuBackground`, which is a `UI_BackgroundMain` and therefore only
# ever exists for the main menu -- so when the owner asked for *"those mod images made for the
# menu to also use them randomly for load screen backgrounds"* they had to come out into a type
# anything can read. Both files are loaded and searched together: the constants may sit in either
# without this proof needing to know which, and the claims below still hold whichever one answers.
art_source = io.open(os.path.join(SRC, "Presentation", "RimroomsSlideArt.cs"),
                     encoding="utf-8-sig").read()
background_source = io.open(os.path.join(SRC, "Presentation", "RimroomsMenuBackground.cs"),
                            encoding="utf-8-sig").read()
menu_source = art_source + NEWLINE + background_source
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

# **THE MENU OPENED ON THE SAME PICTURE EVERY SINGLE TIME.** Owner, 2026-10-03: *"so we need those
# mod images made for the menu to also use them randomly for load screen backgrounds"*. The
# slideshow cycled perfectly and `currentIndex` was pinned to `0` in the constructor and reset to
# `0` again in `ApplySettings`, so the first thing anybody ever saw -- and the backdrop behind
# every load started from the menu -- was slide one of six, forever. Nothing here could see it,
# because every claim was about the scan and the crossfade.
check("THE STARTING SLIDE IS DRAWN, not pinned to the first one",
      "internal static int RandomIndex(int count)" in art_source
      and background_source.count("currentIndex = RimroomsSlideArt.RandomIndex(slides.Count);") == 2
      and "currentIndex = 0;" not in background_source,
      "-- BOTH places that set it: the constructor, and the settings reset that fires whenever the "
      "slideshow or reduced-motion is toggled. One without the other leaves a second route back "
      "to slide one")

check("and the draw is kept away from the game's seeded randomness",
      "Environment.TickCount" in art_source
      and "Rand." not in art_source,
      "-- every other number this mod draws comes from a coordinate's own seed so a place is the "
      "same place on every visit, and `Rand` during map generation is pushed and popped so a "
      "layout is reproducible. Which picture is behind a loading box is the one thing here that "
      "should differ run to run and that nothing may depend on")

check("the loading surfaces and the menu read ONE list",
      "internal static List<Texture2D> Slides()" in art_source
      and "return RimroomsSlideArt.Slides();" in background_source
      and "GetAllInFolder" not in background_source,
      "-- the owner's ask is explicitly *\"those mod images\"*, the same ones. A second folder "
      "scan with a second prefix and a second ordering would be two lists that agree until "
      "somebody adds a PNG")

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

# **AND IT HAS TO COVER EVERY SHIPPED SLIDE, WHICH THIS DID NOT NOTICE FOR FOUR OF THEM.** The
# claim above is satisfied by ONE provenance file existing anywhere under outputs/ -- so when the
# slide count went from six to twelve, four images from the 2026-09-29 batch were shipping with no
# row in the register at all and nothing failed. Steam's disclosure requirement is per asset, and
# the register is the artefact an audit would read. Found by counting twelve PNGs against eight
# rows, not by reading either.
register_path = os.path.join(REPO, "docs", "research", "provenance-register.csv")
registered = set()
if os.path.isfile(register_path):
    import csv as _csv
    for _row in _csv.reader(io.open(register_path, encoding="utf-8-sig")):
        if _row and _row[0].startswith("RR-MENU-"):
            registered.add(_row[0][len("RR-MENU-"):])
undisclosed = sorted(n[:-4] for n in names if n[:-4] not in registered)
check("and EVERY shipped slide has its own row in the provenance register",
      os.path.isfile(register_path) and not undisclosed,
      "-- %d shipped, %d registered; undisclosed: %s"
      % (len(names), len(registered), ", ".join(undisclosed) or "none"))

print("")

# ======================================================================================
# THE GENERATION FREEZE, TOLD BEFORE IT HAPPENS
#
# Owner, 2026-10-03: *"we need a popup and notice in that portion of the machine gate
# connection step that pops up befgore the "freeze" of the generation telling the player
# "Time has froze due to mass distortions, please wait" but noit that i want u to make a
# universe of backrooms themed notcie of the pause that is expected and propely keep it toned
# to the experience we are trying to make per scenrio type"*.
#
# The freeze is real and unavoidable: `GenStep_BackroomsDestination` carves a 300x300 map
# inside Core's map generation, on the main thread. **An unexplained freeze reads as a crash.**
# ======================================================================================

notice_source = io.open(os.path.join(SRC, "Presentation", "RimroomsGenerationNotice.cs"),
                        encoding="utf-8-sig").read()
pane_source = io.open(os.path.join(SRC, "UI", "OperationsPortalNetwork.cs"),
                      encoding="utf-8-sig").read()
generation_keys = io.open(os.path.join(
    "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English", "Keyed",
    "RR_Generation.xml"), encoding="utf-8-sig").read()

check("THE NOTICE IS DRAWN BEFORE THE FREEZE, and the work moves into a long event",
      "internal static void Announce(CoordinateRecord coordinate, Action work)" in notice_source
      and "Find.WindowStack.Add(new Dialog_RimroomsGenerationNotice(NoticeText(), () =>"
      in notice_source
      and "LongEventHandler.QueueLongEvent(work, LongEventKey, false, null," in notice_source
      and "callback: ShowNormalization)));" in notice_source,
      "-- **the ordering is the whole requirement.** `EnsureSite` generates synchronously and "
      "hands the map back through an `out` parameter, so a window added immediately before it "
      "draws on the NEXT frame -- after the freeze it was warning about. The work therefore runs "
      "inside `QueueLongEvent`, which is the pattern Core itself uses for settling, and the "
      "warning is drawn and dismissed while the game can still draw")

check("and it is announced ONLY when a space is actually being built",
      "internal static bool ShouldAnnounce(CoordinateRecord coordinate)" in notice_source
      and "return coordinate != null && coordinate.Site == null;" in notice_source
      and "if (!ShouldAnnounce(coordinate)) { work(); return; }" in notice_source,
      "-- a coordinate that already has its site is being re-entered, not resolved, and there is "
      "no freeze to warn about. `Site == null` is read rather than tracked, so it cannot fall out "
      "of step with `EnsureSite`'s own branch on the same field. And when there is nothing to "
      "warn about the work runs **immediately and unchanged**, so a caller never has to ask which "
      "case it is in")

check("THE BUTTONS THAT CAN BUILD A MAP ACTUALLY CALL IT",
      pane_source.count("Presentation.RimroomsGenerationNotice.Announce(opening, () =>") == 2
      and "ShowResult(PortalAddressService.RegisterLaboratoryAddress(opened, opening))" in pane_source
      and "ShowResult(PortalAddressService.RegisterNaturalAddress(chosen, from, opening))"
      in pane_source,
      "-- DEFINED AND CALLED, at both of the Operations pane's openings. **A button callback is "
      "the one place this is legal**: a long event is only safe where nothing is waiting on a "
      "return value, and a method handing back a `CompanyActionResult` is not such a place, which "
      "is why this hooks the pane rather than `EnsureSite`")

# **TWO EXEMPTIONS WERE WRONG, and check-call-coverage.py is what exposed them.** Both were
# recorded as unable to announce; both are clicks. Asserted here so neither can quietly revert to
# generating a 300x300 map behind an unexplained freeze.
history_source = io.open(os.path.join(SRC, "Gate", "GateConnectionHistory.cs"),
                         encoding="utf-8-sig").read()
expeditions_source = io.open(os.path.join(SRC, "UI", "OperationsExpeditions.cs"),
                             encoding="utf-8-sig").read()

check("DIALLING A REMEMBERED ADDRESS ANNOUNCES, because a float menu is a click and not a tick",
      "Presentation.RimroomsGenerationNotice.Announce(" in history_source
      and "CoordinateOfEntry(entry, campaign)" in history_source
      and "private static CoordinateRecord CoordinateOfEntry(" in history_source,
      "-- `DialRememberedAddress` reaches `RegisterLaboratoryAddress` and so `EnsureSite`. It was "
      "declared exempt on the grounds that it was a tick; it is a `FloatMenuOption` delegate. The "
      "exemption had been written without reading the caller")

check("and DISPATCHING A CREW announces too, with the result read inside the continuation",
      "Presentation.RimroomsGenerationNotice.Announce(coordinate, delegate" in expeditions_source
      and "ShowResult(trips.Dispatch(gate, coordinate, dispatching));" in expeditions_source
      and "var dispatching = new List<Pawn>(selectedCrew);" in expeditions_source,
      "-- its exemption said the result is read by its caller, which described the method rather "
      "than the call: the result is read INSIDE the callback, which is where a long event is "
      "legal. The crew list is copied before the lambda because `selectedCrew` is pane state the "
      "player can still change and the dispatch now happens a frame or more later")

check("THE BACKDROP IS THE MOD'S OWN ART, drawn at random from the same list the menu reads",
      "backdrop = RimroomsSlideArt.RandomSlide();" in notice_source
      and "RimroomsSlideArt.FullScreenRect(backdrop)" in notice_source,
      "-- owner: *\"so we need those mod images made for the menu to also use them randomly for "
      "load screen backgrounds\"*. **The same list, not a second scan** -- a second folder scan "
      "with its own prefix and ordering would be two lists that agree until somebody adds a PNG. "
      "Drawn once per notice rather than per frame, so the picture does not flicker while it is "
      "being read")

# **THE MOST VULNERABLE DRAW IN THE MOD.** Unity's IMGUI state is process-wide: a mod that sets
# `GUI.color` and returns without restoring it leaves every later window painting in that colour,
# and at zero alpha painting nothing. That is the first bug a real launch of this package found.
# A full-screen image on a frameless window is the worst case for it -- an invisible backdrop on
# a window with no frame is an invisible window, so the player would be looking at a frozen game
# with no notice on it: the exact failure this feature exists to prevent, arriving through it.
check("AND THE DRAW IS GUARDED, because an invisible notice is worse than none",
      "using (RimroomsWindowState.Clean()) { Draw(inRect); }" in notice_source
      and "doWindowBackground = false;" in notice_source,
      "-- `check-display-style.py` refused this file until it was, and was right to")

check("THERE IS A TONE PER SCENARIO, and a fallback that still says the pause is expected",
      "ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;" in notice_source
      and 'string scoped = baseKey + "_" + part.startDef.defName;' in notice_source
      and "if (scoped.CanTranslate()) { key = scoped; }" in notice_source
      and "private static TaggedString Toned(string baseKey)" in notice_source
      and "return Toned(DefaultNoticeKey);" in notice_source
      and "return Toned(DefaultNormalizationKey);" in notice_source,
      "-- owner: *\"propely keep it toned to the experience we are trying to make per scenrio "
      "type\"*. The company reads an instrument; somebody alone in the dark does not. "
      "`Find.Scenario` persists in the save, so the tone is right mid-game and not only at setup. "
      "**`CanTranslate` rather than a table**, so a scenario added later gets its own tone by "
      "writing the string and nothing else")

check("and every shipped scenario has its own notice, with the generic one behind them",
      all(("<" + key + ">") in generation_keys for key in (
          "RR_Generation_FreezeNotice",
          "RR_Generation_FreezeNotice_RR_AsyncIndustriesStart",
          "RR_Generation_FreezeNotice_RR_FurnitureStoreStart",
          "RR_Generation_FreezeNotice_RR_SoloGroupStart",
          "RR_Generation_FreezeEvent",
          "RR_Generation_FreezeAcknowledge",
          "RR_Generation_NormalNotice",
          "RR_Generation_NormalNotice_RR_AsyncIndustriesStart",
          "RR_Generation_NormalNotice_RR_FurnitureStoreStart",
          "RR_Generation_NormalNotice_RR_SoloGroupStart",
          "RR_Generation_NormalAcknowledge")),
      "-- three shipped openings, three tones, plus the generic notice and the short line Core's "
      "own wait box carries through the freeze itself")

# ======================================================================================
# THE CLOSE-OUT. Owner, 2026-10-05: *"the notice needs to appear before the map bagins to load
# then close out with a normalization notice"*. The hold notice makes a promise -- *nothing on
# this side advances until this finishes* -- and a promise with no close is a player wondering
# whether it ever did.
# ======================================================================================

check("THE HOLD IS CLOSED OUT, on Core's own completion callback rather than on a guess",
      "internal static void ShowNormalization()" in notice_source
      and "callback: ShowNormalization" in notice_source
      and "new Dialog_RimroomsNormalizationNotice(NormalizationText())" in notice_source,
      "-- `QueueLongEvent` takes a `callback` and invokes it after the event finishes, read out "
      "of `LongEventHandler` in the shipped assembly rather than assumed. Calling it at the end "
      "of `work` would run it while the event is still the thing on screen, and "
      "`ExecuteWhenFinished` fires when the WHOLE QUEUE drains -- a different moment the first "
      "time two events are ever queued together")

check("and the close-out is NOT the full-screen surface the hold notice uses",
      "internal sealed class Dialog_RimroomsNormalizationNotice : Window" in notice_source
      and "RimroomsSlideArt" not in notice_source.split(
          "internal sealed class Dialog_RimroomsNormalizationNotice")[1]
      and "forcePause" not in notice_source.split(
          "internal sealed class Dialog_RimroomsNormalizationNotice")[1],
      "-- the player has just been put somewhere new and **the first thing they should see is the "
      "place, not another picture of a corridor over the top of it.** It does not force a pause "
      "either: this notice says the freeze is over, and pausing to announce that time is moving "
      "again would be the notice contradicting its own text")

check("and its draw is guarded too",
      notice_source.count("using (RimroomsWindowState.Clean()) { Draw(inRect); }") == 2,
      "-- both windows, for the same process-wide IMGUI reason. Counted rather than searched, "
      "because one guarded window and one unguarded one is what a single `in` cannot tell apart")

check("every shipped scenario has a close-out in its own voice",
      all(phrase in generation_keys for phrase in (
          "TIME HAS NORMALIZED", "COORDINATE INDEXED", "THE SHOP IS BACK", "IT HAS SETTLED")),
      "-- each one answers its own hold notice: the company bills the interval, the shopkeeper "
      "counts the lights back on, the person alone checks their own hands. A generic *done* would "
      "have been the close-out that proves nobody read the pair together")

check("the notice says the pause is EXPECTED, which is the load-bearing half of the direction",
      all(word in generation_keys for word in (
          "THE HOLD IS EXPECTED", "This is expected.", "It will start again"))
      and "mass distortions" not in generation_keys,
      "-- a player who reads it should stop worrying rather than start. **The owner's own example "
      "wording is deliberately absent**: they gave *\"Time has froze due to mass distortions, "
      "please wait\"* and said *\"but noit that\"* in the same sentence, so the sense survives "
      "-- time has stopped, something enormous is the cause, waiting is correct -- and the words "
      "do not")

if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every slide will appear, ships, loads, and matches its neighbours")
