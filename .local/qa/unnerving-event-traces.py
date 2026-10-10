# -*- coding: utf-8 -*-
"""A trace on every event, and the strings it leaves behind.

Same rule as the inhabitant tells: **each trace states a plain fact that cannot
be true**, not an adjective. `docs/UNIVERSE_ADAPTATION.md` -- *"Ordinary
industrial interiors become uncanny through exact changes"*. The lights going out
is not uncanny; the switches being found already flipped is.

  * presence      -- the recorder keeps a gap nobody was there for
  * lights fail   -- the switches were already off when somebody checked
  * cold snap     -- frost on the inside of a wall with nothing behind it
  * seepage       -- the stain is dry and it was not here on the way in
  * rearrangement -- things are stacked in an order somebody chose
  * deep cold     -- the floor is cold through boots that were warm a room ago
  * blackout      -- every bulb intact, every one dark

The `traceKey` resolves `RR_Clue_Label_<key>` and `RR_Clue_Text_<key>`, the same
pair an ordinary room clue uses. `RR_Clue_Text_*` takes two format arguments --
room number and variant -- because the clue record passes both; the event traces
use the room number and ignore the variant, which a keyed string may do.
"""
import io
import os
import re
import sys

NL = chr(10)
DEFS_DIR = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsAnomalyEventDefs"
KEYED_DIR = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed"

# event defName -> trace key fragment
TRACES = {
    "RR_Anomaly_Presence": "AnomalyPresence",
    "RR_Anomaly_LightsFail": "AnomalyLightsFail",
    "RR_Anomaly_ColdSnap": "AnomalyColdSnap",
    "RR_Anomaly_Seepage": "AnomalySeepage",
    "RR_Anomaly_Rearrangement": "AnomalyRearrangement",
    "RR_Anomaly_DeepCold": "AnomalyDeepCold",
    "RR_Anomaly_Blackout": "AnomalyBlackout",
}

STRINGS = [
    "  <!-- EVENT TRACES. Owner, 2026-10-04: \"remember lsd unnerving feeling with all things ie",
    "       events random spanwns\". A letter scrolls away; these stay in the coordinate and in",
    "       the Atlas. Each states a plain fact that cannot be true, per UNIVERSE_ADAPTATION.md:",
    "       the lights going out is not uncanny, the switches being found already off is. -->",
    "  <RR_Clue_Label_AnomalyPresence>Room {0}: a gap in the recording</RR_Clue_Label_AnomalyPresence>",
    "  <RR_Clue_Text_AnomalyPresence>The route recorder kept running through room {0} and kept "
    "nothing. The interval is the right length and there is no one on it.</RR_Clue_Text_AnomalyPresence>",
    "  <RR_Clue_Label_AnomalyLightsFail>Room {0}: the switches were already off"
    "</RR_Clue_Label_AnomalyLightsFail>",
    "  <RR_Clue_Text_AnomalyLightsFail>Every light in room {0} went out at once. The switches "
    "were found in the off position, and nobody on the crew had reached them."
    "</RR_Clue_Text_AnomalyLightsFail>",
    "  <RR_Clue_Label_AnomalyColdSnap>Room {0}: frost on an inside wall</RR_Clue_Label_AnomalyColdSnap>",
    "  <RR_Clue_Text_AnomalyColdSnap>Room {0} lost its heat. The frost formed on the inside face "
    "of a wall with another room behind it.</RR_Clue_Text_AnomalyColdSnap>",
    "  <RR_Clue_Label_AnomalySeepage>Room {0}: a stain that is already dry</RR_Clue_Label_AnomalySeepage>",
    "  <RR_Clue_Text_AnomalySeepage>Room {0} is dirtier than the crew left it. The stain is dry "
    "and it is not on the way-in recording.</RR_Clue_Text_AnomalySeepage>",
    "  <RR_Clue_Label_AnomalyRearrangement>Room {0}: things stacked in an order"
    "</RR_Clue_Label_AnomalyRearrangement>",
    "  <RR_Clue_Text_AnomalyRearrangement>Loose items in room {0} are not where they were put "
    "down. They are stacked, by size, against one wall.</RR_Clue_Text_AnomalyRearrangement>",
    "  <RR_Clue_Label_AnomalyDeepCold>Room {0}: cold coming up through the floor"
    "</RR_Clue_Label_AnomalyDeepCold>",
    "  <RR_Clue_Text_AnomalyDeepCold>The floor of room {0} is cold through boots that were warm "
    "a room ago. The air above it is not.</RR_Clue_Text_AnomalyDeepCold>",
    "  <RR_Clue_Label_AnomalyBlackout>Room {0}: every bulb intact, every one dark"
    "</RR_Clue_Label_AnomalyBlackout>",
    "  <RR_Clue_Text_AnomalyBlackout>Room {0} and everything around it went dark. Not one bulb "
    "is broken and not one of them lights.</RR_Clue_Text_AnomalyBlackout>",
]

problems = 0

# ------------------------------------------------------------------- traceKey on every event def
written = []
for name in sorted(os.listdir(DEFS_DIR)):
    if not name.lower().endswith(".xml"):
        continue
    path = os.path.join(DEFS_DIR, name)
    text = io.open(path, encoding="utf-8-sig").read()
    changed = False
    for event, trace in TRACES.items():
        anchor = "<defName>%s</defName>" % event
        if anchor not in text:
            continue
        if ("<traceKey>%s</traceKey>" % trace) in text:
            print("already traced: %s" % event)
            continue
        if text.count(anchor) != 1:
            print("EVENT NOT UNIQUE (%d): %s" % (text.count(anchor), event))
            problems += 1
            continue
        start = text.index(anchor)
        close = text.index("</RimroomsAsyncIndustries.Threats.RimroomsAnomalyEventDef>", start)
        text = text[:close] + ("  <traceKey>%s</traceKey>" % trace) + NL + "  " + text[close:]
        changed = True
        print("%-30s traceKey %s" % (event, trace))
    if changed:
        written.append((path, text))

# which events exist but got no trace?
present = set()
for name in sorted(os.listdir(DEFS_DIR)):
    if name.lower().endswith(".xml"):
        present.update(re.findall(r"<defName>(RR_Anomaly_[A-Za-z]+)</defName>",
                                  io.open(os.path.join(DEFS_DIR, name), encoding="utf-8-sig").read()))
untraced = sorted(present - set(TRACES))
if untraced:
    print("EVENTS WITH NO TRACE MAPPED: %s" % ", ".join(untraced))
    problems += 1

# ------------------------------------------------------------------------------ the keyed strings
keyed_path = None
for name in sorted(os.listdir(KEYED_DIR)):
    if name.lower().endswith(".xml") and "<RR_Clue_Label_" in io.open(
            os.path.join(KEYED_DIR, name), encoding="utf-8-sig").read():
        keyed_path = os.path.join(KEYED_DIR, name)
        break
if keyed_path is None:
    print("COULD NOT FIND THE FILE HOLDING RR_Clue_Label_*; nothing written")
    sys.exit(1)

keyed = io.open(keyed_path, encoding="utf-8-sig").read().split(NL)
if any("RR_Clue_Label_AnomalyPresence" in line for line in keyed):
    print("the event traces are already in the keyed file")
else:
    closing = [index for index, line in enumerate(keyed) if line.strip() == "</LanguageData>"]
    if len(closing) != 1:
        print("EXPECTED ONE </LanguageData> in %s, found %d"
              % (os.path.basename(keyed_path), len(closing)))
        problems += 1
    else:
        keyed = keyed[:closing[0]] + STRINGS + keyed[closing[0]:]
        print("added %d strings to %s" % (len(STRINGS), os.path.basename(keyed_path)))
        written.append((keyed_path, NL.join(keyed)))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path, text in written:
    io.open(path, "w", encoding="utf-8-sig", newline=NL).write(text)
    print("wrote %s" % os.path.basename(path))
