# -*- coding: utf-8 -*-
"""The strings for setting a gate's address and opening it from the door.

Owner direction, 2026-10-04, verbatim: *"and everything that the machine needs to
start up should be able to do in the worlkd from the devices themselfes with
pawns controls and actrions not just in the opetaions tab,, ie setting the
cordinace and all of those things need  to show"*.

**Vocabulary checked before writing, not after.** `check-info-cards.py` bans
*"portal"* -- the thing this mod replaced -- and reserves *"doorway"* against
*"door"* and *"threshold"*. Six strings broke that rule in the previous batch, so
every line below says **gate**, **connection**, **address** or **place**.

The refusals are written as answers to the question a player is already asking,
because these commands grey out rather than disappearing: *"ive done like 50
things in a row and its still not opening"* is what a vanishing button produces.
"""
import io
import sys

NL = chr(10)
PATH = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_NativeGate.xml"

ADDITIONS = [
    "  <RR_GateAddress_SetLabel>Set this gate's address</RR_GateAddress_SetLabel>",
    "  <RR_GateAddress_SetDesc>Choose which place this gate connects to. Remembering an address "
    "costs nothing and can be changed; a map is only built when somebody crosses."
    "</RR_GateAddress_SetDesc>",
    "  <RR_GateAddress_NoneKnown>This branch has no addresses yet. Dial an unknown address with "
    "this gate, or take a company request.</RR_GateAddress_NoneKnown>",
    "  <RR_GateAddress_Option>{0} — depth {1}</RR_GateAddress_Option>",
    "  <RR_GateAddress_OpenLabel>Open a connection ({0} remembered)</RR_GateAddress_OpenLabel>",
    "  <RR_GateAddress_OpenDesc>Bring up the connection to a remembered address. The assigned "
    "operator must stay on the powered console while it comes up.</RR_GateAddress_OpenDesc>",
    "  <RR_GateAddress_OpenOption>Open the connection to {0}</RR_GateAddress_OpenOption>",
    "  <RR_GateAddress_NoAddressSet>No address is remembered on this gate yet. Set one first."
    "</RR_GateAddress_NoAddressSet>",
    "  <RR_GateAddress_AlreadyOpen>This gate already holds an open connection."
    "</RR_GateAddress_AlreadyOpen>",
    "  <RR_GateAddress_AlreadyRamping>This gate is already coming up. Watch its readout, or "
    "abort.</RR_GateAddress_AlreadyRamping>",
]

text = io.open(PATH, encoding="utf-8-sig").read()
lines = text.split(NL)

first_key = ADDITIONS[0].strip()[1:ADDITIONS[0].strip().index(">")]
if any(line.strip().startswith("<%s>" % first_key) for line in lines):
    print("already present: %s" % first_key)
    sys.exit(0)

# Appended immediately before the closing tag rather than beside a sibling, because these ten
# are a new block with no existing partner to sit next to.
closing = [index for index, line in enumerate(lines) if line.strip() == "</LanguageData>"]
if len(closing) != 1:
    print("EXPECTED EXACTLY ONE </LanguageData>, found %d" % len(closing))
    sys.exit(1)

at = closing[0]
lines = lines[:at] + ADDITIONS + lines[at:]
io.open(PATH, "w", encoding="utf-8-sig", newline=NL).write(NL.join(lines))
print("added %d key(s) to %s" % (len(ADDITIONS), PATH.split("/")[-1]))
