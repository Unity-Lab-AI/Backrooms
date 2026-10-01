# -*- coding: utf-8 -*-
"""Rows 1193, 1220, 821, 822, 833: the words a player reads and how they reach them.

Five rows, one family. What each one asks for, and what this file asserts about it:

  * **1193, 1220** -- *"eventually we will need to write a how to to the game paly and systems"*,
    written **once** for the repository and the site. `docs/PLAYING.md` is that document, and it
    joins the reader-facing set so the vocabulary rule, the wall rule and the row 791 claim guard
    all apply to it. The claim that matters most is the caveat: no game has ever been launched
    from this repository, so every play instruction is a structural claim about the code and the
    document has to say so in its own words.

  * **821** -- *"Remap RimWorld's menus, tabs, and campaign views into the finished company-first
    Company Command layout ... Keep every relevant Architect, Work, Assign, Research, World, map,
    building, and pawn action reachable"*. Two halves, and they are asserted differently.
    **Reachability is built**: all five named surfaces open from the company panel, where until
    0.12.40-dev **Architect -- the first one the row names -- opened from nowhere in this package
    at all**. **The remap is deliberately not built**, and the absence is asserted: nothing in
    this package may patch, reorder or replace Core's own main buttons.

  * **822, 833** -- *"tutorial/guide, help glossary, keyboard/controller paths ...
    color/contrast/readability options, scalable UI"*. The keyboard path is Core's own machinery:
    `KeyBindingDefGenerator.ImpliedKeyBindingDefs` emits a rebindable `MainTab_RR_Operations` for
    any `MainButtonDef` that sets `defaultHotKey`, so setting one field buys a binding in the
    player's own Key Bindings dialog and costs this package no def. Contrast and scale are the
    **absence** of authored colour and authored font in every readout, which is why they are
    asserted here and checked by `check-display-style.py` rather than merely described.

The two facts about Core that this all rests on were measured, not remembered:

    Core main button orders   Architect 1, Work 10, Schedule 20, Assign 30, Animals 40,
                              Wildlife 50, Research 60, Quests 65, World 70, History 80,
                              Factions 90, Menu 500
    Core main tab hotkeys     Tab, F1..F9   (F10 screenshot, F11 screenshot mode, F12 free)

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
KEYED = os.path.join(MOD, "1.6", "Languages", "English", "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def flatten(text):
    """Whitespace-normalised and lowered.

    A hard-wrapped document splits a phrase across a newline and a literal search then finds
    nothing. That was the defect -- not the document -- when `MULTIPLAYER.md` was reported as
    missing a sentence it contained, and it is the reason every document search below is flat.
    """
    return re.sub(r"\s+", " ", text).lower()


window = strip_cs_comments(read(os.path.join(SRC, "UI", "MainTabWindow_Operations.cs")))
help_pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsHelp.cs")))
button_xml = read(os.path.join(MOD, "1.6", "Defs", "MainButtonDefs", "RR_MainButtons.xml"))
help_keys = read(os.path.join(KEYED, "RR_Help.xml"))
operations_keys = read(os.path.join(KEYED, "RR_Operations.xml"))
playing = read(os.path.join(REPO, "docs", "PLAYING.md"))
playing_flat = flatten(playing)
conformance = read(os.path.join(REPO, "tools", "check-doc-conformance.py"))
display_style = read(os.path.join(REPO, "tools", "check-display-style.py"))

# --------------------------------------------------------------------------------------------
print("")
print("row 821, the built half: every surface the row names opens from the company panel")
print("-" * 90)

# The row's own list, in its own order. Each must be opened by name from the tab window, and
# each must go through the game's own worker rather than any surface of ours.
for tab in ("Architect", "Work", "Assign", "Research", "World"):
    if tab == "Research":
        # Core ships a DefOf for this one, so the named lookup would be the worse spelling.
        opened = "OpenNativeTab(MainButtonDefOf.Research)" in window
    else:
        opened = ('OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("%s"))' % tab) \
            in window
    check("%s opens from the company panel" % tab, opened,
          "-- row 821 names it; reachability is the requirement the row actually states")

check("every colony control has a keyed label",
      all(("RR_Operations_Open%s" % tab) in operations_keys
          for tab in ("Architect", "Work", "Assign", "Research", "World")),
      "-- a button whose label does not resolve reads as its own key to the player")

check("a native tab is opened through the game's own worker",
      "target.Worker.InterfaceTryActivate();" in window,
      "-- pressing Core's button is what keeps research, tutorial and world-selection behaviour; "
      "calling the window directly would skip all three")

check("an unavailable tab is refused in words",
      'Messages.Message("RR_Operations_TabUnavailable".Translate()' in window,
      "-- some tabs do not exist in the world view, and silence there is indistinguishable from "
      "a broken button")

# --------------------------------------------------------------------------------------------
print("")
print("row 821, company-first: the tab is first on the bar, and Core's bar is untouched")
print("-" * 90)

root = ET.fromstring(button_xml.lstrip(u"﻿"))
definitions = root.findall("MainButtonDef")
check("this package ships exactly one main button", len(definitions) == 1,
      "-- found %d" % len(definitions))

order = definitions[0].findtext("order")
# Core's Architect is order 1 and is its leftmost real button. Company-first means lower.
check("the company tab sorts left of Architect",
      order is not None and int(order) < 1,
      "-- order is %r; Core's Architect is 1, so anything above that is not company-first. It "
      "shipped at 95 until 0.12.40-dev, between Factions and Menu, the far right of the bar"
      % order)

check("the tab exists without a map",
      definitions[0].findtext("validWithoutMap") == "true",
      "-- the help pane is reachable from the main menu, which is where a player who has not "
      "started yet actually is")

# The unbuilt half of row 821, asserted as an absence. A patch against Core's own main buttons
# would be the invasive reading of "remap", and it is the reading the row itself challenges.
patch_files = glob.glob(os.path.join(MOD, "1.6", "Patches", "*.xml"))
patched = [os.path.basename(p) for p in patch_files if "MainButtonDef" in read(p)]
check("nothing patches Core's main buttons", not patched,
      "-- %s does; remapping the base game's tab bar would fight every interface mod installed, "
      "and reachability was the requirement" % ", ".join(patched))

# And no C# of ours may reorder, hide or replace one at runtime either -- the same invasion by
# another route, and the one a Harmony-free mod could still reach through the def database.
# Found by **type**, not by variable name. A first version matched lines that mentioned
# "MainButton" and a planted `target.order = 3;` walked past it -- the parameter is declared
# `MainButtonDef target` on a different line, which is exactly how this would really be written.
# So: collect every identifier declared or parameterised as a MainButtonDef, add the DefOf, and
# refuse an assignment through any of them.
runtime_writes = []
for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
    code = strip_cs_comments(read(path))
    if "MainButtonDef" not in code:
        continue
    holders = set(re.findall(r"\bMainButtonDef\s+([A-Za-z_][A-Za-z0-9_]*)", code))
    holders.discard("target")  # re-added below; kept explicit so the set is never empty by luck
    holders.update(re.findall(r"\bMainButtonDef\s+([A-Za-z_][A-Za-z0-9_]*)", code))
    for name in sorted(holders) + ["MainButtonDefOf.Research", "MainButtonDefOf.Architect"]:
        for match in re.finditer(re.escape(name) + r"\s*\.\s*[A-Za-z_][A-Za-z0-9_]*\s*=(?!=)",
                                 code):
            line_start = code.rfind("\n", 0, match.start()) + 1
            end = code.find("\n", match.start())
            runtime_writes.append("%s: %s"
                                  % (os.path.basename(path), code[line_start:end].strip()))
check("no code of ours rewrites a main button at runtime", not runtime_writes,
      "-- %s. Reordering or hiding Core's buttons through the def database is the same invasion "
      "as a patch, by the one route a Harmony-free mod can still reach" % "; ".join(runtime_writes))

# --------------------------------------------------------------------------------------------
print("")
print("rows 822 and 833: the keyboard path is Core's own generator, and the key is a free one")
print("-" * 90)

hot_key = definitions[0].findtext("defaultHotKey")
check("the tab ships a default hotkey", hot_key is not None,
      "-- without it KeyBindingDefGenerator emits nothing and the tab has no keyboard path at all")

# Core uses Tab and F1..F9 for its own main tabs, F10 for TakeScreenshot and F11 for
# ToggleScreenshotMode. Taking any of those would silently steal a binding a player already has.
# **Widened after the first real launch, and the widening is the point.** This used to allow
# F12 on the grounds that Core leaves it free -- which is true, and was measured against the
# wrong population. **HugsLib binds F12 to "Publish log file"**, and every one of F1 through F12
# is bound somewhere across Core plus the 288 installed mods. Register row 85 says *"avoid
# overriding hotkeys."*
#
# So no function key at all. The profile cannot be read from here -- another player has a
# different mod list -- but "no function key" is portable, and it is the rule that would have
# stopped 0.12.40-dev shipping the collision.
CORE_TAKEN = ("Tab", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11")
FUNCTION_KEY = re.compile(r"^F\d+$")
check("the default hotkey is not one Core already uses",
      hot_key not in CORE_TAKEN,
      "-- %r is taken by Core" % hot_key)
check("THE DEFAULT HOTKEY IS NOT A FUNCTION KEY AT ALL",
      hot_key is not None and not FUNCTION_KEY.match(hot_key),
      "-- %r is a function key. Core takes Tab and F1-F9 for main tabs, F10 and F11 for "
      "screenshots, and HugsLib takes F12 for Publish log file. Every F-key is bound somewhere "
      "in a 288-mod profile, so a function key is a collision waiting to be reported" % hot_key)

check("the keyboard line reads the player's live binding, not the shipped default",
      "self.hotKey.MainKeyLabel" in help_pane,
      "-- the binding is rebindable in Key Bindings, so help naming the shipped key would be "
      "wrong for anybody who rebound it")

check("a missing binding is stated rather than crashed through",
      "self.hotKey == null" in help_pane and "RR_Help_KeyboardUnbound" in help_keys,
      "-- hotKey is [Unsaved] and is filled in by Core's generator, so it is null whenever "
      "defaultHotKey was never set")

check("the player is told where to rebind it",
      'listing.Label("RR_Help_KeyboardRebind".Translate());' in help_pane
      and "<RR_Help_KeyboardRebind>" in help_keys,
      "-- a key present in the file is not a claim that anything draws it; the first version of "
      "this claim read the keyed file only and a plant that deleted the call passed")

# --------------------------------------------------------------------------------------------
print("")
print("rows 822 and 833: contrast and scale are an absence, and the absence has a checker")
print("-" * 90)

# Each of these three is written against the *definition* rather than the name, because the
# name is a substring of its own definition and of any renaming of it. All three were planted
# and all three passed on the first attempt: `def check_readability(` satisfies a probe for
# `check_readability(problems)`, and `AUTHORED_COLOUR` matches `AUTHORED_COLOUR_UNUSED`. A claim
# that a symbol is *mentioned* is not a claim that it is *used*.
check("the readability guard exists and is wired into the run",
      "def check_readability(problems):" in display_style
      and "\n    check_readability(problems)" in display_style,
      "-- a function nobody calls is the defect class check-wiring.py exists for, and the call "
      "has to be matched with its indentation or the definition satisfies the probe")

check("the guard refuses an authored colour",
      "AUTHORED_COLOUR = (" in display_style
      and "for pattern, what in AUTHORED_COLOUR:" in display_style
      and r"Color(?:32|Int)?\s*\(" in display_style)

check("the guard refuses a font Core does not offer",
      "CORE_FONTS = (" in display_style and "if value in CORE_FONTS:" in display_style
      and "AUTHORED_FONT_SIZE.search(code)" in display_style)

# The claim itself, measured here rather than trusted from the checker. Two readers are better
# than one when the thing being asserted is an absence.
readouts = sorted(glob.glob(os.path.join(SRC, "UI", "*.cs")))
check("there are readout files to hold", len(readouts) >= 15,
      "-- found %d" % len(readouts))
offenders = []
# The qualifier is not optional decoration. `new UnityEngine.Color(...)` is the spelling a file
# without `using UnityEngine;` has to use, and an unqualified pattern let exactly that plant
# through both this reader and the checker.
QUALIFIED_COLOUR = re.compile(r"\bnew\s+(?:[A-Za-z_][A-Za-z0-9_]*\s*\.\s*)*Color(?:32|Int)?\s*\(")
# `RimroomsWindowState.cs` is the one named exception, added 0.12.43-dev after the FIRST REAL
# LAUNCH found the hole in this rule: the company setup page drew its title and both buttons and
# an entirely empty body, with nothing in the log, because Unity's draw state is process-wide and
# **not one of this package's six window entry points reset any of it**. Authoring no colour was
# true and was never the whole claim -- authoring nothing is not the same as assuming nothing.
# Resetting to white imposes no palette; white is the absence of a tint.
STATE_GUARD = "RimroomsWindowState.cs"
for path in readouts:
    if os.path.basename(path) == STATE_GUARD:
        continue
    code = strip_cs_comments(read(path))
    if QUALIFIED_COLOUR.search(code) or re.search(r"\bGUI\s*\.\s*color\s*=", code):
        offenders.append(os.path.basename(path))
check("no readout file authors a colour, the state guard aside", not offenders,
      "-- %s does; the player's own contrast and colourblind settings are the only ones that "
      "should apply to text" % ", ".join(offenders))

guard = read(os.path.join(SRC, "UI", STATE_GUARD))
check("THE STATE GUARD EXISTS AND RESTORES WHAT IT FOUND",
      "GUI.color = Color.white;" in guard and "GUI.color = color;" in guard
      and "IDisposable" in guard,
      "-- a guard that reset without restoring would make this package the mod that breaks the "
      "next one, which is the exact failure it exists to fix")

unguarded_windows = [os.path.basename(path)
                     for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True))
                     if "override void DoWindowContents" in strip_cs_comments(read(path))
                     and "RimroomsWindowState.Clean()" not in strip_cs_comments(read(path))]
check("EVERY WINDOW ENTRY POINT USES THE GUARD", not unguarded_windows,
      "-- %s does not. One unguarded draw is one window that can render invisibly with nothing "
      "in the log, and it will be the one a player sees first"
      % ", ".join(unguarded_windows))

# Definition AND the loop that walks it AND the branch that acts on it. A table survives
# `for needle, why in []:` completely intact, and this claim passed against exactly that plant --
# the fourth batch in a row that shape has defeated a claim here.
check("the checker polices the guard rather than exempting it",
      "GUARD_REQUIRED = (" in display_style
      and "for needle, why in GUARD_REQUIRED:" in display_style
      and "GUARD_FORBIDDEN = (" in display_style
      and "for pattern, what in GUARD_FORBIDDEN:" in display_style
      and "if not guard_seen:" in display_style,
      "-- a named exception with no rules of its own is a hole, not an exception")

check("the checker requires every window to adopt the guard",
      "unguarded = []" in display_style and "if unguarded:" in display_style,
      "-- the adoption sweep is what catches a NEW window added later without the guard, which "
      "is the way this regression will actually come back")

fonts = set()
for path in readouts:
    fonts.update(m.group(1).strip()
                 for m in re.finditer(r"Text\s*\.\s*Font\s*=\s*([^;]+);", strip_cs_comments(read(path))))
# A bare local name is a restore, not a choice. Tested as a whole identifier with `GameFont`
# excluded, because allowing anything *containing* "Font" let `(GameFont)7` -- a font size
# outside Core's four, which is precisely what this claim forbids -- pass unnoticed.
authored = sorted(f for f in fonts
                  if f not in ("GameFont.Tiny", "GameFont.Small", "GameFont.Medium",
                               "GameFont.Large")
                  and not (re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", f) and "GameFont" not in f))
check("no readout file sets a font Core does not offer", not authored,
      "-- %s" % ", ".join(authored))

check("the caller's font is restored",
      "Text.Font = previousFont;" in window,
      "-- leaving Medium set leaks this mod's heading size into every window drawn afterwards")

# --------------------------------------------------------------------------------------------
print("")
print("rows 822 and 833: the help pane, and it works before there is a company")
print("-" * 90)

check("help is a pane on the company tab", '"RR_UI_Help"' in window)
check("the help pane label resolves", "<RR_UI_Help>" in help_keys)

# The pane must be drawn *outside* DrawCompany. Being inside it would make the glossary
# unreachable until the player already has a running branch, which is backwards.
check("help draws without a campaign component",
      "if (selectedPane == HelpPane)" in window and "DrawHelp(listing);" in window,
      "-- a glossary you need a running company to open is not help")
check("help is not drawn from inside the company block",
      "DrawHelp" not in window.split("private void DrawCompany")[-1],
      "-- being inside DrawCompany is exactly the failure above, and it looks identical from "
      "the outside until there is no company")

check("the glossary is a list, not a paragraph",
      "GlossaryKeys" in help_pane,
      "-- fourteen terms, each its own resolved key, so check-keyed-strings.py can see them")

glossary = re.findall(r'"(RR_Help_Term[A-Za-z]+)"', help_pane)
check("every glossary term resolves",
      glossary and all(("<%s>" % term) in help_keys for term in glossary),
      "-- missing: %s" % ", ".join(t for t in glossary if ("<%s>" % t) not in help_keys))

# The words the mod insists on. `check-info-cards.py` bans the retired vocabulary everywhere the
# game displays text; a glossary that did not define the replacements would leave the player
# holding enforced words with no explanation of them.
for term in ("Gate", "Connection", "Threshold", "Coordinate"):
    check("the glossary defines %s" % term.lower(), ("RR_Help_Term%s" % term) in help_pane,
          "-- it is a word this package enforces, so it is a word it owes a definition for")

check("the help pane says the build is unplayed",
      "RR_Help_Untested" in help_pane and "<RR_Help_Untested>" in help_keys,
      "-- help that describes behaviour nobody has observed, without saying so, is the defect "
      "docs/MULTIPLAYER.md was written to avoid")

# --------------------------------------------------------------------------------------------
print("")
print("rows 1193 and 1220: the play document, once, and honest about what it is")
print("-" * 90)

check("the play document exists", os.path.isfile(os.path.join(REPO, "docs", "PLAYING.md")))

# **The play document is the wiki now.** Owner, 2026-10-01: *"laying out the full wiki of the
# dame how to play how to set it all up rimsort all of it"*. `PLAYING.md` is the long-form
# working version behind it, and this claim follows the role rather than the filename.
#
# **Stronger than it was**, in two ways: every page is required rather than one document, so
# adding a page without supervising it fails; and these are held to a 360-character wall where
# `PLAYING.md` was held to 700.
WIKI_PAGES = ("index", "install", "first-hour", "scenarios", "gates", "backrooms", "company",
              "interface", "mods", "multiplayer", "troubleshooting", "links", "credits")
missing_pages = [name for name in WIKI_PAGES
                 if not os.path.isfile(os.path.join(REPO, "docs", "wiki", name + ".md"))]
unsupervised = [name for name in WIKI_PAGES
                if ('os.path.join(WIKI, "%s.md")' % name) not in conformance]

check("THE PLAY DOCUMENTATION IS A WIKI, AND EVERY PAGE OF IT EXISTS",
      not missing_pages,
      "-- missing: %s" % ", ".join(missing_pages))

check("and every page of it is held to the reader-facing rules",
      not unsupervised,
      "-- unsupervised: %s. The vocabulary rule, the wall rule and the row 791 claim guard all "
      "hang off that set, so a page outside it is a page nothing reads"
      % ", ".join(unsupervised))

check("and the wall limit is tighter than the old document was held to",
      "DOC_WALL_CHARS = 360" in conformance,
      "-- owner: *\"public facing documnets ARE NOT to be text walls get to each point in as "
      "short a way as possible\"*. It was 700")

check("and the long-form version points at it rather than competing with it",
      "wiki/index.md" in playing,
      "-- one canonical place, not two drifting copies")

check("it says no game has ever been launched",
      "no game has ever been launched from this repository" in playing_flat,
      "-- the load-bearing sentence of the whole document")

check("it says the game's readouts outrank it",
      "the game's own readouts are right and this page is wrong" in playing_flat,
      "-- a play document written from source at one checkpoint must not be the authority over "
      "live state")

check("it distinguishes itself from the build how-to",
      "howto.md" in playing_flat
      and ("built" in playing_flat or "building" in playing_flat),
      "-- HOWTO.md already exists and is about building; two documents with one job is how the "
      "wrong one gets read. **Re-aimed 2026-10-01**: the header was rewritten to point at the "
      "wiki, so the property is asserted rather than the old sentence quoted")

check("THE PLAY DOCUMENTATION EXISTS ONCE, AND THIS POINTS AT IT",
      "wiki/index.md" in playing_flat
      and os.path.isfile(os.path.join(REPO, "docs", "wiki", "index.md")),
      "-- one canonical place, not two drifting copies. The requirement has not changed; the "
      "canonical place has. **Putting the old wording back to satisfy a claim would be writing "
      "documentation for the checker instead of the reader**")

check("it records that Core's menus are deliberately not remapped",
      "does not remap rimworld's own menus" in playing_flat,
      "-- row 821 challenges its own premise, and the answer belongs where a player can read it")

check("it tells the player how to reach the tab",
      ("bound to **%s** by default" % hot_key).lower() in playing_flat
      and "key bindings" in playing_flat,
      "-- the claim reads the SHIPPED key out of the def rather than naming one, because the "
      "document now mentions F12 as history ('an earlier build took it') and a search for the "
      "key name alone passed on that mention after the binding sentence was deleted")

check("it states the contrast and scale position",
      "set no colour and no text size of their own" in playing_flat)

for topic in ("gate", "connection", "threshold", "coordinate", "band", "request", "contract",
              "insight", "site", "debrief"):
    check("the play document covers %s" % topic, topic in playing_flat)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every surface row 821 names opens from the company panel, the company tab is "
      "first and Core's bar is untouched, the keyboard path is Core's own, contrast and scale are "
      "an absence with a checker behind it, and the play document says what it is")
