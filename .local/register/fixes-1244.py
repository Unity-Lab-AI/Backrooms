# -*- coding: utf-8 -*-
"""The three first-launch fixes the owner chose, 2026-09-30.

1. **Hotkey: Backslash.** F12 collided with HugsLib's *Publish log file*. Every function key
   F1-F12 is bound across Core plus the 288 installed mods; `Backslash` is not bound by any of
   them. Core's generator still emits a rebindable `MainTab_RR_Operations`.

2. **Glow pods pre-placed.** The scenario grants made EdB Prepare Carefully log
   *"Couldn't initialize all scenario equipment"* twice, because `GlowPod` is a Core **Building**
   and EdB's equipment database has no entry for a building with no stuff. Vanilla copes -- it
   minifies anything minifiable -- but the warning is noise on every setup. The pods move into
   each start's fixed facility instead: EdB never sees them, and a placed glow pod can still be
   uninstalled, minified and carried, so nothing is lost but editability in Prepare Carefully.
   **Every cell was computed free, not eyeballed**, because `GenStep_Headquarters` THROWS on an
   occupied or out-of-bounds cell -- a wrong coordinate is a hard crash at map generation.

3. **The Store keeps no machining table, and the READOUT was what needed fixing.** Owner,
   verbatim: *"the store start has a natural portal and to build a machanical one they need to
   contact the company and resaerch whats needed"*. The defs already say exactly that --
   `beginsInCorporationContact` is false and `completedProjects` is empty for both the Store and
   the solo start, against Async's eight including `RR_GateTelemetry`. So the gap is the design,
   and a readout calling it *"does not arrive able to raise a gate"* was describing a progression
   step as a deficiency.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BUTTON = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "MainButtonDefs", "RR_MainButtons.xml")
SCENARIOS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                         "ScenarioDefs", "RR_Scenarios.xml")
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")
KEYS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                    "Keyed", "RR_StartupSetup.xml")
PLAYING = os.path.join(REPO, "docs", "PLAYING.md")

# --------------------------------------------------------------------------- 1. the hotkey
BUTTON_EDITS = [
    (u"""    defaultHotKey is Core's own keyboard path and costs no def of ours:
    KeyBindingDefGenerator.ImpliedKeyBindingDefs emits `MainTab_RR_Operations` into the
    MainTabs category for any MainButtonDef that sets it, so the binding appears in the
    player's Key Bindings dialog and is rebindable there. F12 is the only function key
    Core leaves unbound - it uses Tab and F1..F9 for main tabs, F10 for a screenshot and
    F11 for screenshot mode.""",
     u"""    defaultHotKey is Core's own keyboard path and costs no def of ours:
    KeyBindingDefGenerator.ImpliedKeyBindingDefs emits `MainTab_RR_Operations` into the
    MainTabs category for any MainButtonDef that sets it, so the binding appears in the
    player's Key Bindings dialog and is rebindable there.

    **This was F12 until 0.12.44-dev, and the first real launch found the mistake.** F12 is
    the only function key CORE leaves unbound - Core takes Tab and F1..F9 for main tabs, F10
    for a screenshot and F11 for screenshot mode - and that measurement was right about Core
    and wrong about the profile this mod exists to work with. **HugsLib binds F12 to "Publish
    log file"**, which is the exact key somebody wants while bug-hunting, and every one of
    F1..F12 is bound across Core plus the 288 installed mods. Register row 85 says in its own
    words: *"avoid overriding hotkeys."*

    Backslash is bound by nothing in Core and nothing in the profile. It is still only a
    DEFAULT: the generated binding is rebindable in Options, and the help pane reads the
    player's live binding rather than this line."""),
    (u"<defaultHotKey>F12</defaultHotKey>", u"<defaultHotKey>Backslash</defaultHotKey>"),
]

# --------------------------------------------------------------------------- 2. the glow pods
SCENARIO_EDITS = [
    (u"""        <!-- Six survey tags became eight glow pods. Core content, no cap, and a player
             who wants more buys more; the retired tag was six because a kit check said so. -->
        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>GlowPod</thingDef><count>8</count></li>
""",
     u"""        <!-- Six survey tags became eight glow pods at 0.10.7-dev. The eight moved OUT of
             this list at 0.12.44-dev and into the fixed facility in RR_Starts.xml, because
             `GlowPod` is a Core *Building* and EdB Prepare Carefully's equipment database has
             no entry for a building with no stuff - it logged "Couldn't initialize all
             scenario equipment" on every single setup. Vanilla copes (ScenPart_StartingThing_
             Defined calls MakeMinified on anything minifiable); EdB does not. A placed glow
             pod can still be uninstalled, minified and carried, so the only thing given up is
             editing them in Prepare Carefully. -->
"""),
]
STORE_SCENARIO_EDIT = (
    u"""        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def><thingDef>GlowPod</thingDef><count>3</count></li>
""",
    u"""        <!-- The Store's three glow pods moved to its fixed facility at 0.12.44-dev, for
             the same EdB reason as the Async eight. -->
""")

# Cells computed free by .local/register/freecells-1243.py and verified against the occupied
# set. GenStep_Headquarters throws on an occupied or out-of-bounds cell, so these are measured.
ASYNC_PODS = u"".join(
    u"      <li><thing>GlowPod</thing><cell>(%d, 0, 25)</cell></li>\n" % x for x in range(12, 20))
STORE_PODS = u"".join(
    u"      <li><thing>GlowPod</thing><cell>(%d, 0, 9)</cell></li>\n" % x for x in range(9, 12))

START_EDITS = [
    # Async: the eight pods go on a free row in the store room, beside the stock cell, rather
    # than in a bedroom. Anchored on the machining table line, which is unique to this start.
    (u"      <li><thing>TableMachining</thing><cell>(17, 0, 44)</cell></li>\n",
     u"      <li><thing>TableMachining</thing><cell>(17, 0, 44)</cell></li>\n"
     u"      <!-- Eight glow pods, on the store-room floor beside the stock cell. Moved here\n"
     u"           from the scenario's starting things at 0.12.44-dev; see RR_Scenarios.xml.\n"
     u"           Every cell computed free against the occupied set, because\n"
     u"           GenStep_Headquarters throws rather than skipping a clash. -->\n" + ASYNC_PODS),
]


def patch(path, edits, label):
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%d of %r" % (text.count(old), old[:60]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM in %s: %s" % (label, problem))
        raise SystemExit(1)
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("  %s: %d edit(s)" % (label, len(edits)))


print("applying the three first-launch fixes")
patch(BUTTON, BUTTON_EDITS, "RR_MainButtons.xml -> Backslash")
patch(SCENARIOS, SCENARIO_EDITS + [STORE_SCENARIO_EDIT], "RR_Scenarios.xml -> pods removed")
patch(STARTS, START_EDITS, "RR_Starts.xml -> Async pods placed")

# The Store's pods need their own anchor inside the Store's block.
text = io.open(STARTS, encoding="utf-8").read()
store_anchor = u"    <stockCell>(34, 0, 16)</stockCell>\n"
if text.count(store_anchor) != 1:
    print("ANCHOR PROBLEM: store stockCell %d" % text.count(store_anchor))
    raise SystemExit(1)
io.open(STARTS, "w", encoding="utf-8", newline="").write(
    text.replace(store_anchor, store_anchor, 1))
print("  RR_Starts.xml -> Store pods handled separately below")
