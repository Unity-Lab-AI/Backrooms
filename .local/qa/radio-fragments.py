# -*- coding: utf-8 -*-
"""Radio fragments: an event with people in it.

## The row this closes, verbatim from `docs/TODO.md`

*"Add repeated missing-person mysteries with radio fragments, missing crews,
delayed return, witness conflict, reappearance/death, rescue, and case
closure."* -- **Open: radio fragments.** Everything else in that row closed and
was archived; this one named item stayed.

## And the direction it serves

Owner, 2026-10-04: *"remember lsd unnerving feeling with all things ie events
random spanwns, enemies, allies, nuetrals"*, and earlier *"even wild waky carzxzy
creepy things when u add places and events"*.

**All seven existing events are environmental.** Lights, cold, damp, moved
objects, a noise. Not one of them has a person in it, and three of the owner's
own named examples are people -- *"a room with a lost person"*, *"a room full of
bodies"*. The inhabitant families cover people who are *there*; nothing covered a
person who is **not**.

## What makes it unnerving is whose voice it is

A fragment of transmission is only atmosphere if it comes from nobody. This one
names **somebody the branch knows**: a colonist who is at home right now, or
somebody on the lost-pawn register. The owner's phrase for that is *"echos of
thier inhabitance in weird ways"*, and it is the same move the `Echo` inhabitant
family makes -- the uncanniness is the recognition, not the noise.

Drawn with `CampaignSeed.Derive` off the coordinate seed and the opening, never
`Rand`, so the same opening always carries the same voice.

## It costs nothing, which the fairness rules require

`RimroomsAnomalyEventDef`'s own frozen table: readable warning, learnable rule, a
countermeasure, no unavoidable failure. A fragment damages nobody, destroys
nothing and blocks no route -- it is `Presence` with a name on it. And like every
event now, it leaves a trace in the coordinate that outlives the letter.
"""
import io
import sys

NL = chr(10)

EVENTDEF = "src/RimroomsAsyncIndustries/Threats/RimroomsAnomalyEventDef.cs"
SERVICE = "src/RimroomsAsyncIndustries/Threats/AnomalyEventService.cs"
DEFS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsAnomalyEventDefs/RR_AnomalyEvents.xml"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_AnomalyEvents.xml"
GENERATION_KEYED = \
    "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Generation.xml"

EDITS = [
    # ------------------------------------------------------------- the effect
    (EVENTDEF,
     "        /// <summary>Loose items are not where they were left.</summary>" + NL
     + "        Rearrangement = 4,",

     "        /// <summary>Loose items are not where they were left.</summary>" + NL
     + "        Rearrangement = 4," + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// A fragment of transmission arrives, in a voice the branch knows." + NL
     + "        ///" + NL
     + "        /// **The row this answers, verbatim:** *\"Add repeated missing-person mysteries"
     + NL
     + "        /// with radio fragments\"* -- the one named item left open in it after everything"
     + NL
     + "        /// else closed. And the direction it serves, owner 2026-10-04: *\"remember lsd"
     + NL
     + "        /// unnerving feeling with all things ie events random spanwns\"*."
     + NL
     + "        ///" + NL
     + "        /// **All seven events before this were environmental** -- lights, cold, damp,"
     + NL
     + "        /// moved objects, a noise. Not one had a person in it, while three of the owner's"
     + NL
     + "        /// own named examples are people. The inhabitant families cover somebody who is"
     + NL
     + "        /// *there*; nothing covered somebody who is **not**." + NL
     + "        ///" + NL
     + "        /// **The voice is somebody the branch knows**: a colonist at home right now, or"
     + NL
     + "        /// a name off the lost-pawn register. A fragment from nobody is just noise -- the"
     + NL
     + "        /// uncanniness is the recognition, which is the same move the `Echo` inhabitant"
     + NL
     + "        /// family makes." + NL
     + "        ///" + NL
     + "        /// Costs nothing, like <see cref=\"Presence\"/>: damages nobody, destroys nothing,"
     + NL
     + "        /// blocks no route. It is `Presence` with a name on it." + NL
     + "        /// </summary>" + NL
     + "        RadioFragment = 5,"),

    # ------------------------------------------- the effect always "happens", and names a voice
    (SERVICE,
     "                case AnomalyEffect.Rearrangement: return Rearrange(map, cells, magnitude);",

     "                case AnomalyEffect.Rearrangement: return Rearrange(map, cells, magnitude);"
     + NL
     + "                // A fragment needs nothing to act on, exactly like `Presence`: it is a"
     + NL
     + "                // transmission, not a change to the space. Returning true unconditionally"
     + NL
     + "                // is the honest answer -- `FireEffect` returns false to mean *the effect"
     + NL
     + "                // found nothing to do*, and this one never can." + NL
     + "                case AnomalyEffect.RadioFragment: return true;"),

    (SERVICE,
     "            Announce(map, coordinate, definition);",

     "            // **WHOSE VOICE IT IS, and it is somebody this branch knows.** A fragment from"
     + NL
     + "            // nobody is atmosphere; a fragment naming a colonist who is standing in the"
     + NL
     + "            // base right now is the owner's *\"echos of thier inhabitance in weird ways\"*."
     + NL
     + "            // Null for every other effect, and `Announce` then behaves exactly as before."
     + NL
     + "            Announce(map, coordinate, definition, VoiceFor(coordinate, definition));"),

    (SERVICE,
     "        private static void Announce(Map map, CoordinateRecord coordinate, RimroomsAnomalyEventDef definition)"
     + NL
     + "        {",

     "        /// <summary>" + NL
     + "        /// The name a radio fragment carries, or null for every other effect." + NL
     + "        ///" + NL
     + "        /// Prefers a **living colonist**, because the uncanny version is a voice whose"
     + NL
     + "        /// owner is in the base at the same moment. Falls back to the lost-pawn register,"
     + NL
     + "        /// which is the sadder reading and still a recognition. With neither -- a branch"
     + NL
     + "        /// with nobody at home and nobody lost -- there is no fragment at all, because a"
     + NL
     + "        /// transmission from a name nobody knows is the thing this is not."
     + NL
     + "        ///" + NL
     + "        /// Derived from the coordinate's seed and its opening count, never `Rand`, so the"
     + NL
     + "        /// same opening always carries the same voice and a reload cannot reroll who is"
     + NL
     + "        /// on the radio." + NL
     + "        /// </summary>" + NL
     + "        private static string VoiceFor(CoordinateRecord coordinate," + NL
     + "            RimroomsAnomalyEventDef definition)" + NL
     + "        {" + NL
     + "            if (definition == null || definition.effect != AnomalyEffect.RadioFragment)"
     + NL
     + "            { return null; }" + NL
     + "            RimroomsCampaignComponent campaign = Verse.Current.Game == null" + NL
     + "                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();"
     + NL
     + "            if (campaign == null) { return null; }" + NL
     + "            var voices = new List<string>();" + NL
     + "            foreach (StaffRecord member in campaign.Staff)" + NL
     + "            {" + NL
     + "                if (member != null && member.Employed && member.Pawn != null" + NL
     + "                    && !member.Pawn.Dead && !string.IsNullOrEmpty(member.Name))" + NL
     + "                { voices.Add(member.Name); }" + NL
     + "            }" + NL
     + "            if (voices.Count == 0)" + NL
     + "            {" + NL
     + "                foreach (string lost in campaign.LostPawnNames())" + NL
     + "                {" + NL
     + "                    if (!string.IsNullOrEmpty(lost)) { voices.Add(lost); }" + NL
     + "                }" + NL
     + "            }" + NL
     + "            if (voices.Count == 0) { return null; }" + NL
     + "            voices.Sort(System.StringComparer.Ordinal);" + NL
     + "            int draw = CampaignSeed.Derive(coordinate.Seed," + NL
     + "                \"radio:voice:\" + coordinate.Openings, 1);" + NL
     + "            if (draw < 0) { draw = ~draw; }" + NL
     + "            return voices[draw % voices.Count];" + NL
     + "        }" + NL
     + NL
     + "        private static void Announce(Map map, CoordinateRecord coordinate," + NL
     + "            RimroomsAnomalyEventDef definition, string voice = null)" + NL
     + "        {"),

    (SERVICE,
     "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + NL
     + "            Find.LetterStack.ReceiveLetter(" + NL
     + "                definition.letterLabelKey.Translate()," + NL
     + "                definition.letterTextKey.Translate(),",

     "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + NL
     + "            // A voice is passed only when there is one. `Translate` ignores an extra"
     + NL
     + "            // argument a string has no placeholder for, so the other seven events read"
     + NL
     + "            // exactly as they did." + NL
     + "            Find.LetterStack.ReceiveLetter(" + NL
     + "                definition.letterLabelKey.Translate()," + NL
     + "                voice == null ? definition.letterTextKey.Translate()" + NL
     + "                    : definition.letterTextKey.Translate(voice),"),
]

NEW_EVENT = '''
  <!-- **AN EVENT WITH A PERSON IN IT.** Closes the one item left open in "Add repeated
       missing-person mysteries with radio fragments, missing crews, delayed return, witness
       conflict, reappearance/death, rescue, and case closure" - everything else in that row
       closed and was archived.

       Owner, 2026-10-04: "remember lsd unnerving feeling with all things ie events random
       spanwns". All seven events before this were environmental; three of the owner's own
       named examples are people.

       Costs nothing, like Presence: damages nobody, destroys nothing, blocks no route. Deep
       enough that it is not a first-visit event, and repeatable because "repeated
       missing-person mysteries" is the row's own word. -->
  <RimroomsAsyncIndustries.Threats.RimroomsAnomalyEventDef>
    <defName>RR_Anomaly_RadioFragment</defName>
    <label>a fragment of transmission</label>
    <description>Something comes through on a band nothing should be using, in a voice the branch knows.</description>
    <effect>RadioFragment</effect>
    <minDepth>3</minDepth>
    <minBand>Unsettled</minBand>
    <weight>1.1</weight>
    <durationTicks>1</durationTicks>
    <magnitude>1</magnitude>
    <repeatable>true</repeatable>
    <traceKey>AnomalyRadioFragment</traceKey>
    <letterLabelKey>RR_Anomaly_RadioFragmentLabel</letterLabelKey>
    <letterTextKey>RR_Anomaly_RadioFragmentText</letterTextKey>
  </RimroomsAsyncIndustries.Threats.RimroomsAnomalyEventDef>
'''

EVENT_STRINGS = [
    "  <RR_Anomaly_RadioFragmentLabel>A fragment of transmission</RR_Anomaly_RadioFragmentLabel>",
    "  <RR_Anomaly_RadioFragmentText>Something came through on a band nothing in the space "
    "should be using. Eleven seconds of it, and most of that is carrier. The voice gives a name "
    "and the name is {0}.</RR_Anomaly_RadioFragmentText>",
]

TRACE_STRINGS = [
    "  <RR_Clue_Label_AnomalyRadioFragment>Room {0}: eleven seconds of carrier"
    "</RR_Clue_Label_AnomalyRadioFragment>",
    "  <RR_Clue_Text_AnomalyRadioFragment>The recorder kept eleven seconds of transmission in "
    "room {0}. The band is one nothing in the space uses, and the name the voice gives belongs "
    "to somebody on the branch's own roster.</RR_Clue_Text_AnomalyRadioFragment>",
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old.strip().split(NL)[0][:72]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-32s patched %s" % (path.split("/")[-1], old.strip().split(NL)[0][:44]))

# -------------------------------------------------------------------------------- the def
defs = io.open(DEFS, encoding="utf-8-sig").read()
if "RR_Anomaly_RadioFragment" in defs:
    print("the radio fragment event already exists")
else:
    end = defs.rindex("</Defs>")
    defs = defs[:end] + NEW_EVENT + defs[end:]
    print("added RR_Anomaly_RadioFragment")

# ---------------------------------------------------------------------------- the strings
def insert_before_close(path, lines, marker):
    body = io.open(path, encoding="utf-8-sig").read().split(NL)
    if any(marker in line for line in body):
        print("already present in %s: %s" % (path.split("/")[-1], marker))
        return None
    closing = [index for index, line in enumerate(body) if line.strip() == "</LanguageData>"]
    if len(closing) != 1:
        print("EXPECTED ONE </LanguageData> in %s, found %d"
              % (path.split("/")[-1], len(closing)))
        return False
    body = body[:closing[0]] + lines + body[closing[0]:]
    print("added %d string(s) to %s" % (len(lines), path.split("/")[-1]))
    return NL.join(body)


event_keyed = insert_before_close(KEYED, EVENT_STRINGS, "RR_Anomaly_RadioFragmentLabel")
if event_keyed is False:
    problems += 1
trace_keyed = insert_before_close(GENERATION_KEYED, TRACE_STRINGS,
                                  "RR_Clue_Label_AnomalyRadioFragment")
if trace_keyed is False:
    problems += 1

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
io.open(DEFS, "w", encoding="utf-8-sig", newline=NL).write(defs)
print("wrote %s" % DEFS.split("/")[-1])
if event_keyed:
    io.open(KEYED, "w", encoding="utf-8-sig", newline=NL).write(event_keyed)
    print("wrote %s" % KEYED.split("/")[-1])
if trace_keyed:
    io.open(GENERATION_KEYED, "w", encoding="utf-8-sig", newline=NL).write(trace_keyed)
    print("wrote %s" % GENERATION_KEYED.split("/")[-1])
