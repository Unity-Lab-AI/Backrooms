# -*- coding: utf-8 -*-
"""Extend the unnerving-register proof to events, and plant against it.

An event used to fire one letter and leave nothing. The claims below hold the
same three properties for events that the inhabitant tells already have -- it
exists, it is readable afterwards, and it states a fact rather than a feeling --
plus two that are specific to something that happens rather than something that
is there: the record is written **before** the letter, and the threshold room
never carries one.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-unnerving-register.py"
PLANTS = ".local/register/plant-unnerving-register.py"

PROOF_ANCHOR = 'print("")' + NL + "if failures:"

NEW_CLAIMS = '''# ======================================================= the same register, applied to events
events = read(MOD, "Defs", "RimroomsAnomalyEventDefs", "RR_AnomalyEvents.xml")
event_service = read(SRC, "Threats", "AnomalyEventService.cs")
event_def = read(SRC, "Threats", "RimroomsAnomalyEventDef.cs")
content = read(SRC, "Generation", "RoomContentMapComponent.cs")
generation_keyed = read(MOD, "Languages", "English", "Keyed", "RR_Generation.xml")

event_names = re.findall(r"<defName>(RR_Anomaly_[A-Za-z]+)</defName>", events)
trace_keys = re.findall(r"<traceKey>([A-Za-z0-9_]+)</traceKey>", events)

check("EVERY EVENT LEAVES A TRACE IN THE COORDINATE",
      len(event_names) > 0 and len(trace_keys) == len(event_names),
      "-- %d events, %d traces. An event that leaves nothing behind is one nobody can confirm "
      "happened: the letter scrolls away and the coordinate records nothing"
      % (len(event_names), len(trace_keys)))

absent = [key for key in trace_keys
          if ("<RR_Clue_Label_%s>" % key) not in generation_keyed
          or ("<RR_Clue_Text_%s>" % key) not in generation_keyed]
check("and every trace resolves BOTH a label and a description",
      not absent,
      "-- %s would print its own key in the Atlas. The clue record asks for both halves"
      % ", ".join(absent))

check("AND AN EVENT WITHOUT ONE IS REFUSED AT LOAD",
      "if (string.IsNullOrEmpty(traceKey))" in event_def
      and "has no traceKey, so nothing in the coordinate records that it happened."
      in event_def,
      "-- the five events that shipped before this each announced once and left no record, and "
      "nothing objected")

# Same gate as the inhabitant tells: the lights going out is not uncanny, the switches being
# found already off is.
trace_bodies = {}
for key in trace_keys:
    found = re.search(r"<RR_Clue_Text_%s>(.*?)</RR_Clue_Text_%s>" % (key, key),
                      generation_keyed, re.S)
    if found:
        trace_bodies[key] = found.group(1)
mood = sorted(key for key, body in trace_bodies.items()
              if any(word in body.lower() for word in ADJECTIVES))
check("EVERY EVENT TRACE STATES A FACT, NOT A FEELING",
      not mood and len(trace_bodies) == len(trace_keys),
      "-- %s uses a mood adjective, or resolved to nothing at all" % ", ".join(mood))

check("THE TRACE IS RECORDED BEFORE THE LETTER IS SENT",
      "RecordTrace(map, coordinate, definition, focus);" in event_service
      and event_service.index("RecordTrace(map, coordinate, definition, focus);")
      < event_service.index("Find.LetterStack.ReceiveLetter("),
      "-- the letter is the half that can fail, on a missing key or a suppressed notification. "
      "Ordering it first would make the durable record the optional one")

check("and the trace is observed on arrival, because the crew lived through it",
      "internal void AddEventClue(" in content
      and "observed = true," in content,
      "-- `MapComponentTick` marks an ordinary clue observed only once its landmark is unfogged "
      "in a surveyed room. An event has no landmark, so it would never be marked and the trace "
      "would be invisible for ever")

check("ONE TRACE PER EVENT PER ROOM, not one per firing",
      "if (clues.Exists(existing => existing.id == key)) { return; }" in content,
      "-- a repeatable event that fires twice in one room has left the same mark; two identical "
      "lines in the Atlas read as a bug rather than as emphasis")

# **THE WAY BACK IS NEVER TOUCHED.** `RimroomsAnomalyEventDef`'s own doc states it as a rule:
# whatever happens, walking back out is still possible. A trace in the threshold room would be
# the first thing to erode it.
check("AND THE THRESHOLD ROOM NEVER CARRIES A TRACE",
      event_service.count('familyId != "threshold_room"') >= 2,
      "-- the threshold and the way back are never touched by any event, which is the "
      "no-unavoidable-failure rule made concrete rather than promised")

check("a trace with no room under its focus cell is still recorded somewhere",
      "room = coordinate.Rooms.FirstOrDefault(candidate => candidate.familyId != "
      '"threshold_room");' in event_service,
      "-- the coordinate still had the event; losing the record because a cell lookup missed "
      "would be the silent half of this failing")

'''

PLANT_ANCHOR = (
    "    # ------------------------------------------------------ no new content authored")

NEW_PLANTS = '''    # ================================================= the same register, applied to events
    ("AN EVENT LOSES ITS TRACE", EVENTS,
     "    <traceKey>AnomalyRearrangement</traceKey>" + CHR_NL, "", PROOF),

    ("a trace points at a label that does not exist", EVENTS,
     "<traceKey>AnomalyPresence</traceKey>", "<traceKey>AnomalyPresenceXX</traceKey>", PROOF),

    ("the load-time rule demanding a trace is removed", EVENTDEF,
     "            if (string.IsNullOrEmpty(traceKey))", "            if (false)", PROOF),

    ("AN EVENT TRACE BECOMES AN ADJECTIVE", GENERATION_KEYED,
     "<RR_Clue_Text_AnomalyLightsFail>Every light in room {0} went out at once. The switches "
     "were found in the off position, and nobody on the crew had reached them."
     "</RR_Clue_Text_AnomalyLightsFail>",
     "<RR_Clue_Text_AnomalyLightsFail>Room {0} went dark. It was deeply unsettling."
     "</RR_Clue_Text_AnomalyLightsFail>", PROOF),

    ("THE TRACE IS WRITTEN AFTER THE LETTER, making the durable record the optional half",
     EVENT_SERVICE,
     "            RecordTrace(map, coordinate, definition, focus);" + CHR_NL + CHR_NL
     + "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + CHR_NL
     + "            Find.LetterStack.ReceiveLetter(",
     "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + CHR_NL
     + "            RecordTrace(map, coordinate, definition, focus);" + CHR_NL
     + "            Find.LetterStack.ReceiveLetter(", PROOF),

    ("an event trace is left unobserved, so it is invisible for ever", CONTENT,
     "                observed = true," + CHR_NL, "", PROOF),

    ("a repeatable event starts stacking identical traces", CONTENT,
     "            if (clues.Exists(existing => existing.id == key)) { return; }" + CHR_NL,
     "", PROOF),

    ("AND A TRACE IS ALLOWED INTO THE THRESHOLD ROOM", EVENT_SERVICE,
     '                room = coordinate.Rooms.FirstOrDefault(candidate => candidate.familyId != "threshold_room");',
     "                room = coordinate.Rooms.FirstOrDefault();", PROOF),

'''

PLANT_CONSTS = (
    'PROOF = ".local/register/proof-unnerving-register.py"' + NL
    + "# The event half of the same register. Added 2026-10-04 with the traces themselves." + NL
    + 'EVENTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsAnomalyEventDefs/RR_AnomalyEvents.xml"'
    + NL
    + 'EVENTDEF = "src/RimroomsAsyncIndustries/Threats/RimroomsAnomalyEventDef.cs"' + NL
    + 'EVENT_SERVICE = "src/RimroomsAsyncIndustries/Threats/AnomalyEventService.cs"' + NL
    + 'CONTENT = "src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs"' + NL
    + 'GENERATION_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Generation.xml"'
)

problems = 0

text = io.open(PROOF, encoding="utf-8").read()
if "EVERY EVENT LEAVES A TRACE IN THE COORDINATE" in text:
    print("the event claims are already present")
elif text.count(PROOF_ANCHOR) != 1:
    print("PROOF ANCHOR NOT UNIQUE (%d)" % text.count(PROOF_ANCHOR))
    problems += 1
else:
    io.open(PROOF, "w", encoding="utf-8", newline=NL).write(
        text.replace(PROOF_ANCHOR, NEW_CLAIMS + PROOF_ANCHOR))
    print("added 9 event claims to %s" % PROOF.split("/")[-1])

text = io.open(PLANTS, encoding="utf-8").read()
if "AN EVENT LOSES ITS TRACE" in text:
    print("the event plants are already present")
else:
    old = 'PROOF = ".local/register/proof-unnerving-register.py"'
    if text.count(old) != 1:
        print("PLANT CONSTANT NOT UNIQUE (%d)" % text.count(old))
        problems += 1
    elif text.count(PLANT_ANCHOR) != 1:
        print("PLANT ANCHOR NOT UNIQUE (%d)" % text.count(PLANT_ANCHOR))
        problems += 1
    else:
        text = text.replace(old, PLANT_CONSTS)
        text = text.replace(PLANT_ANCHOR, NEW_PLANTS + PLANT_ANCHOR)
        io.open(PLANTS, "w", encoding="utf-8", newline=NL).write(text)
        print("added 8 event plants to %s" % PLANTS.split("/")[-1])

if problems:
    print("%d problem(s)" % problems)
    sys.exit(1)
