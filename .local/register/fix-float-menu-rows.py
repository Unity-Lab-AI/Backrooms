# -*- coding: utf-8 -*-
"""Rewrite the float menu rows that were written as sentences.

A float menu option is a thing the player picks. Core ends one with a full stop 7% of the
time, and its longest is 76 characters against a median of 19. Five of ours were paragraphs.

The kill switch row lost its instruction rather than having it shortened: the row now names
the condition, and the remedy moves to the button's own tooltip, which is the surface Core
uses for explanation and where there is room for it.
"""
import io
import glob
import os

KEYED = os.path.join("Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English", "Keyed")

REPLACEMENTS = [
    # key, old text, new text
    ("RR_GateHistory_Empty",
     u"This gate has not connected anywhere yet.",
     u"No connections yet"),
    ("RR_Supply_NoTiers",
     u"No catalogue tiers are defined.",
     u"No catalogue tiers open"),
    ("RR_Bond_BelowSmallest",
     u"That is less than the smallest bond denomination.",
     u"Below the smallest bond denomination"),
    ("RR_Generation_GateAccessOnly",
     u"Enter this coordinate through the gate.",
     u"Reachable only through a gate"),
    ("RR_Gate_NoKillSwitchCandidates",
     u"No power switch on this gate's circuit. Wire one into the line that feeds the gate and turn it on.",
     u"No power switch on this gate's circuit"),
    # The instruction the row used to carry, moved to the tooltip that explains the button.
    ("RR_Gate_KillSwitchDesc",
     u"Choose a power switch on this gate's own circuit as its emergency cutoff. Throwing that switch ends an opening at once and names itself as the cause. Only a switch that actually carries this gate's power can be chosen.",
     u"Choose a power switch on this gate's own circuit as its emergency cutoff. Throwing that switch ends an opening at once and names itself as the cause. Only a switch that actually carries this gate's power can be chosen. If there is none, wire one into the line that feeds the gate and turn it on."),
]

changed = 0
for path in sorted(glob.glob(os.path.join(KEYED, "*.xml"))):
    text = io.open(path, encoding="utf-8").read()
    before = text
    for key, old, new in REPLACEMENTS:
        marker = u"<%s>%s</%s>" % (key, old, key)
        if marker in text:
            text = text.replace(marker, u"<%s>%s</%s>" % (key, new, key), 1)
            print("  %-32s -> %r" % (key, new[:60]))
            changed += 1
    if text != before:
        io.open(path, "w", encoding="utf-8", newline="").write(text)

expected = len(REPLACEMENTS)
assert changed == expected, "replaced %d of %d; a string did not match exactly" % (changed, expected)
print("%d strings rewritten" % changed)
