# -*- coding: utf-8 -*-
"""Close the five player-facing rows. Status changes and appended closure notes only.

Every anchor is asserted before anything is written and the write happens once, because a
`sub()` that throws part way leaves the file untouched and loses the edits before it silently.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "TODO.md")

original = io.open(PATH, encoding="utf-8").read()

HOWTO = (u"**WRITTEN 0.12.40-dev as `docs/PLAYING.md`.** The play document, written **once** for "
         u"the repository and the site as this row requires. `docs/HOWTO.md` documents the build "
         u"and keeps doing so. It opens with the caveat that governs everything under it -- **no "
         u"game has ever been launched from this repository**, so every instruction in it is a "
         u"structural claim about the code rather than a report of play -- and it says which side "
         u"wins on a disagreement: **the game's own readouts are right and the page is wrong**, "
         u"because the panes read live state and a sentence was written from source at one "
         u"checkpoint. Numbers appear only where the code fixes them. It joins `READER_FACING` in "
         u"`check-doc-conformance.py`, now **thirteen documents**, so the vocabulary rule, the "
         u"wall rule and the row 791 claim guard all apply to it -- and **both caught something "
         u"on the first run**: *\"on the Machine pane\"* tripped the banned phrase *\"the "
         u"machine\"*, and a denial of synchronised research tripped the claim guard because the "
         u"sentence splitter breaks on newlines and the negator was hard-wrapped onto the line "
         u"above. Record `implementation/PLAYER_FACING_IMPLEMENTATION.md`, proof "
         u"`proof-playing-and-help.py`. Was: ")

EDITS = [
    # ------------------------------------------------------------------- rows 1193 and 1220
    (u"- [ ] **\"eventually we will need to write a how to to the game paly and systems\"**",
     u"- [x] " + HOWTO
     + u"**\"eventually we will need to write a how to to the game paly and systems\"**"),

    (u"- [ ] **A player-facing how-to for the gameplay and systems**",
     u"- [x] **WRITTEN 0.12.40-dev as `docs/PLAYING.md`.** Same document as row 1193; one "
     u"deliverable, not two. See that row for what it says and why. Was: "
     u"**A player-facing how-to for the gameplay and systems**"),

    # ------------------------------------------------------------------------------- row 821
    (u"- [ ] Remap RimWorld's menus, tabs, and campaign views into the finished company-first "
     u"Company Command layout,",
     u"- [x] **CLOSED 0.12.40-dev, and the challenge in this row's own text is what decided "
     u"it.** The row asks two things and they are answered differently. **Reachability is "
     u"built**: the company panel now opens **all five surfaces this row names, in this row's "
     u"own order** -- Architect, Work, Assign, Research, World -- each through "
     u"`MainButtonDef.Worker.InterfaceTryActivate()`, the game's own button pressed on the "
     u"player's behalf, which is what preserves Core's research, tutorial and world-selection "
     u"behaviour. **Architect opened from nowhere in this package before this**, by any route: "
     u"`grep -rn \"Architect\" --include=*.cs src` returned nothing at all, while the handoff "
     u"claimed it was already reachable. **Company-first is built**: `RR_MainButtons.xml` moves "
     u"from `<order>95</order>` to `<order>0</order>`, left of Core's Architect at 1 -- it had "
     u"been sitting between Factions (90) and Menu (500), which is as far from first as the bar "
     u"allows. **The remap itself is deliberately NOT built**, exactly as this row says to "
     u"consider, and the absence is now asserted rather than assumed: the proof refuses a patch "
     u"against `MainButtonDef` and refuses any C# of ours that assigns through a "
     u"`MainButtonDef`-typed expression, because rewriting Core's bar through the def database "
     u"is the one route a Harmony-free mod still has. Remapping the base game's interface would "
     u"fight every interface mod in the register at once, and **reachability was the requirement "
     u"this row actually states**. Record `implementation/PLAYER_FACING_IMPLEMENTATION.md`. Was: "
     u"Remap RimWorld's menus, tabs, and campaign views into the finished company-first Company "
     u"Command layout,"),

    # ------------------------------------------------------------------------------- row 822
    (u"- [ ] Add tutorial/guide, help glossary, keyboard/controller paths as appropriate,",
     u"- [x] **CLOSED 0.12.40-dev.** **Tutorial and glossary:** a thirteenth Operations pane, "
     u"`Help`, holding the first-session sequence and a definition for every word this package "
     u"enforces -- gate, connection, threshold, coordinate, band, branch, request, contract, "
     u"dispatch, debrief, evidence, insight, facility, site. It draws **outside** the company "
     u"block and the tab is `validWithoutMap`, because **a glossary you need a running company "
     u"to open is not help**; the proof asserts both that it is drawn and that it is *not* drawn "
     u"from inside the company block, since that failure looks identical from the outside until "
     u"there is no company. **Keyboard path:** one XML field. "
     u"`KeyBindingDefGenerator.ImpliedKeyBindingDefs` emits a rebindable "
     u"`MainTab_RR_Operations` into the `MainTabs` category for any `MainButtonDef` that sets "
     u"`defaultHotKey`, so **Core's own machinery supplies the binding and this package authors "
     u"no `KeyBindingDef` at all**. The default is **F12, the only function key Core leaves "
     u"free** -- it takes Tab and F1-F9 for main tabs, F10 for a screenshot and F11 for "
     u"screenshot mode -- and the help pane prints the player's *live* binding through "
     u"`MainKeyLabel`, not the shipped one. **Colour, contrast and scale:** measured first, and "
     u"the answer was already true with nothing holding it true -- **not one file under `UI/` "
     u"authored a colour**, and the only font work in the folder is one `GameFont.Medium` "
     u"heading with the caller's font restored. So the position is that this package authors "
     u"**neither colour nor font size in anything a player reads text from**, which means the "
     u"player's own Options for scale, font and colourblind mode apply to it exactly as to the "
     u"base game; an option of ours would be a second, worse copy of a setting the game already "
     u"has. **That is now a checker**, not a claim: `check-display-style.py` gained "
     u"`check_readability()`. **Icons/tooltips and localization** were already measurable -- "
     u"`check-keyed-strings.py` reports every declared key resolving. Record "
     u"`implementation/PLAYER_FACING_IMPLEMENTATION.md`. Was: Add tutorial/guide, help glossary, "
     u"keyboard/controller paths as appropriate,"),

    # ------------------------------------------------------------------------------- row 833
    (u"- [ ] Tutorial, glossary, keyboard paths, contrast/scale, localization completeness.",
     u"- [x] **CLOSED 0.12.40-dev with row 822** -- same batch, same mechanisms, one "
     u"implementation record. The help pane carries the tutorial sequence and the glossary, the "
     u"keyboard path is Core's own generated binding on F12, and contrast and scale are the "
     u"**absence** of authored colour and authored font in every readout, held by a new rule in "
     u"`check-display-style.py`. Localization completeness was already measurable and still is. "
     u"Was: Tutorial, glossary, keyboard paths, contrast/scale, localization completeness."),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:80]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("five player-facing rows closed in one write")
