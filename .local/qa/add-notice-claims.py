# -*- coding: utf-8 -*-
"""Claims for the generation-freeze notice and the loading backdrop.

Appended to proof-menu-slides.py, which already owns the mod's menu art, so the
art and the screens that use it are proved in one place.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-menu-slides.py"

CLAIMS = '''
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
      and "LongEventHandler.QueueLongEvent(work, LongEventKey, false, null)));" in notice_source,
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

check("THE BACKDROP IS THE MOD'S OWN ART, drawn at random from the same list the menu reads",
      "backdrop = RimroomsSlideArt.RandomSlide();" in notice_source
      and "RimroomsSlideArt.FullScreenRect(backdrop)" in notice_source,
      "-- owner: *\\"so we need those mod images made for the menu to also use them randomly for "
      "load screen backgrounds\\"*. **The same list, not a second scan** -- a second folder scan "
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
      and 'string scoped = DefaultNoticeKey + "_" + part.startDef.defName;' in notice_source
      and "if (scoped.CanTranslate()) { key = scoped; }" in notice_source,
      "-- owner: *\\"propely keep it toned to the experience we are trying to make per scenrio "
      "type\\"*. The company reads an instrument; somebody alone in the dark does not. "
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
          "RR_Generation_FreezeAcknowledge")),
      "-- three shipped openings, three tones, plus the generic notice and the short line Core's "
      "own wait box carries through the freeze itself")

check("the notice says the pause is EXPECTED, which is the load-bearing half of the direction",
      all(word in generation_keys for word in (
          "THE HOLD IS EXPECTED", "This is expected.", "It will start again"))
      and "mass distortions" not in generation_keys,
      "-- a player who reads it should stop worrying rather than start. **The owner's own example "
      "wording is deliberately absent**: they gave *\\"Time has froze due to mass distortions, "
      "please wait\\"* and said *\\"but noit that\\"* in the same sentence, so the sense survives "
      "-- time has stopped, something enormous is the cause, waiting is correct -- and the words "
      "do not")

'''

text = io.open(PROOF, encoding="utf-8").read()
gate = "if failures:"
if text.count(gate) != 1:
    print("exit gate not found exactly once (%d)" % text.count(gate))
    sys.exit(1)
at = text.index(gate)
io.open(PROOF, "w", encoding="utf-8", newline=NL).write(text[:at] + CLAIMS + text[at:])
print("eight notice claims inserted before the exit gate")
