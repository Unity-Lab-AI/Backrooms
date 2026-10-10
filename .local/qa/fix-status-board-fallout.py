# -*- coding: utf-8 -*-
"""Four legitimate refusals from the status-board and board-up work.

1. The vocabulary rule: "portal" and "doorway" are banned words in this package.
2. `proof-playing-and-help` asserts no readout authors a colour -- it needs the
   same named, conditional exception the checker got.
3. `proof-starts` asserted the old per-step line format.
4. A plant anchored on a line the board replaced.
"""
import io
import re
import sys

NL = chr(10)

GATE_KEYS = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Gate.xml"
PORTAL_KEYS = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"
HELP_PROOF = ".local/register/proof-playing-and-help.py"
STARTS_PROOF = ".local/register/proof-starts.py"
PLANT = ".local/register/plant-startplacement.py"

# ------------------------------------------------------------------- 1. the vocabulary rule
# "portal" names the thing the mod replaced; "doorway" is the word the glossary reserves against
# "door" and "threshold". The checker is right and the strings were written carelessly.
STRING_FIXES = [
    (GATE_KEYS,
     "and the fifth is the margin for a doorway somebody walks through without planning to."
     "\\n\\nStand one of the others down first, or board up a natural portal to free a slot.",
     "and the fifth is the margin for a natural door somebody walks through without planning to."
     "\\n\\nStand one of the others down first, or board up a natural door to free a slot."),
    (PORTAL_KEYS,
     "Send a colonist to nail {0} wood across this doorway.",
     "Send a colonist to nail {0} wood across this door."),
    (PORTAL_KEYS,
     "This cannot be undone. A doorway that has been boarded up still says where it used to "
     "lead, but it does not lead there any more.",
     "This cannot be undone. A door that has been boarded up still says where it used to lead, "
     "but it does not lead there any more."),
    (PORTAL_KEYS,
     "This doorway does not lead anywhere that is being held open.",
     "This door does not lead anywhere that is being held open."),
    (PORTAL_KEYS,
     "Nobody is free who can reach both the wood and this doorway.",
     "Nobody is free who can reach both the wood and this door."),
    (PORTAL_KEYS,
     "{0} boarded up the doorway. The place behind it is closed and a map slot is free.",
     "{0} boarded up the door. The place behind it is closed and a map slot is free."),
    (PORTAL_KEYS,
     "Let the gate pick somewhere. No request, no contract, nobody waiting at the other end.",
     "Let the gate choose somewhere. No request, no contract, nobody waiting at the other end."),
]

# ------------------------------------- 2. the proof needs the checker's conditional exception
HELP_OLD = '''STATE_GUARD = "RimroomsWindowState.cs"
for path in readouts:
    if os.path.basename(path) == STATE_GUARD:
        continue
    code = strip_cs_comments(read(path))
    if QUALIFIED_COLOUR.search(code) or re.search(r"\\bGUI\\s*\\.\\s*color\\s*=", code):
        offenders.append(os.path.basename(path))
check("no readout file authors a colour, the state guard aside", not offenders,
      "-- %s does; the player's own contrast and colourblind settings are the only ones that "
      "should apply to text" % ", ".join(offenders))'''

HELP_NEW = '''STATE_GUARD = "RimroomsWindowState.cs"
# **THE SECOND NAMED EXCEPTION, and it is conditional.** Owner direction 2026-10-04: *"on the
# machine tab its shows the different systems with green and red lights of whether
# complete/active"*. Two indicator colours, asked for by name.
#
# The rule's purpose is *do not impose a palette on text a player reads*, and a status light is
# not text -- but a light whose meaning is carried only by hue is worse than the paragraph it
# replaced, because the player's colourblind setting cannot help it. So this file may author
# exactly two named indicator colours, and only while Core's own checkbox glyph is drawn beside
# them. `check-display-style.py` polices the same pair from the other side.
INDICATOR_FILE = "OperationsGateSteps.cs"
unlit = []
for path in readouts:
    if os.path.basename(path) == STATE_GUARD:
        continue
    code = strip_cs_comments(read(path))
    if os.path.basename(path) == INDICATOR_FILE:
        if ("Widgets.CheckboxDraw(" not in code or "StatusLightComplete" not in code
                or "StatusLightIncomplete" not in code):
            unlit.append(os.path.basename(path))
        continue
    if QUALIFIED_COLOUR.search(code) or re.search(r"\\bGUI\\s*\\.\\s*color\\s*=", code):
        offenders.append(os.path.basename(path))
check("no readout file authors a colour, the state guard and the status lights aside",
      not offenders,
      "-- %s does; the player's own contrast and colourblind settings are the only ones that "
      "should apply to text" % ", ".join(offenders))

check("AND THE STATUS LIGHTS ARE NEVER THE ONLY CHANNEL",
      not unlit,
      "-- %s authors the two indicator colours without Core's checkbox glyph beside them. A light "
      "that means something by hue alone is unreadable to a colourblind player and no game "
      "setting can fix it" % ", ".join(unlit))'''

problems = 0

for path, old, new in STRING_FIXES:
    text = io.open(path, encoding="utf-8-sig").read()
    if new in text and old not in text:
        print("already fixed: %s" % old[:50])
        continue
    if text.count(old) != 1:
        print("STRING NOT UNIQUE (%d) in %s: %s" % (text.count(old), path.split("/")[-1], old[:60]))
        problems += 1
        continue
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new))
    print("reworded: %s" % old[:60])

text = io.open(HELP_PROOF, encoding="utf-8").read()
if "INDICATOR_FILE" in text:
    print("help proof already has the exception")
elif text.count(HELP_OLD) != 1:
    print("HELP PROOF BLOCK NOT FOUND (%d)" % text.count(HELP_OLD))
    problems += 1
else:
    io.open(HELP_PROOF, "w", encoding="utf-8", newline=NL).write(text.replace(HELP_OLD, HELP_NEW))
    print("help proof: conditional exception added")

if problems:
    sys.exit(1)
