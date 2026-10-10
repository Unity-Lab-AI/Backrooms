# -*- coding: utf-8 -*-
"""The keyed strings for the gate-readiness block on the setup page.

Written as a file rather than a heredoc: the prose has apostrophes and the heredoc has mangled
them three times in this session.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                    "Keyed", "RR_StartupSetup.xml")

original = io.open(PATH, encoding="utf-8").read()

KEYS = u"""  <RR_Setup_GateHeading>Bringing a gate up, and whether this branch arrives able to</RR_Setup_GateHeading>
  <RR_Setup_GateCost>The assembly bill wants {0}, carried to the bench and worked by a crafter. Those are in the supplies below.</RR_Setup_GateCost>
  <RR_Setup_GateNoRecipe>The gate assembly recipe is missing from this build, so no gate can be assembled. This is a fault, not a setting.</RR_Setup_GateNoRecipe>
  <RR_Setup_GateNeedsDoor>a door to designate as the gate</RR_Setup_GateNeedsDoor>
  <RR_Setup_GateNeedsBench>a {0} to run the assembly on</RR_Setup_GateNeedsBench>
  <RR_Setup_GateNeedsConsole>a communications console for the operator to stand at</RR_Setup_GateNeedsConsole>
  <RR_Setup_GateNeedsBattery>a battery to hold the return reserve</RR_Setup_GateNeedsBattery>
  <RR_Setup_GateNeedsPower>something generating power into it</RR_Setup_GateNeedsPower>
  <RR_Setup_GatePresent>Standing already: {0} - {1}.</RR_Setup_GatePresent>
  <RR_Setup_GateAbsent>NOT here: {0}. You will have to build or buy one.</RR_Setup_GateAbsent>
  <RR_Setup_GateReady>Everything a gate needs is already standing. Designate the door, console, battery and bench on the Machine pane, then run the assembly bill.</RR_Setup_GateReady>
  <RR_Setup_GateNotReady>This branch does not arrive able to raise a gate. Missing: {0}. That may be the point of this opening rather than an oversight - the inside start begins in the Backrooms and looks for a way out - but it is worth knowing before you start.</RR_Setup_GateNotReady>
</LanguageData>"""

ANCHOR = u"</LanguageData>"

if original.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s)" % original.count(ANCHOR))
    raise SystemExit(1)
if u"RR_Setup_GateHeading" in original:
    print("already present")
    raise SystemExit(0)

io.open(PATH, "w", encoding="utf-8", newline="").write(original.replace(ANCHOR, KEYS, 1))
print("twelve gate-readiness keys added")
