# -*- coding: utf-8 -*-
"""An event leaves something behind that a player can read, afterwards.

## Owner direction, 2026-10-04, verbatim

*"remember lsd unnerving feeling with all things ie events random spanwns,
enemies, allies, nuetrals ..."* -- and the earlier one it restates, *"even wild
waky carzxzy creepy things when u add places and events"*.

## The gap

An anomaly event fires, sends one letter, runs its effect for a while and ends.
**Nothing in the game then says it happened.** The letter scrolls away; the
coordinate's record carries no trace; a crew that arrives next opening walks
through a space that was rearranged, went dark or went cold and finds no sign of
it. That is the same defect the inhabitant tell just fixed for people -- the
warning exists only in a notification -- and `THREAT_DESIGN_SHEETS.md` asks for
both *"a visible or otherwise accessible warning"* and *"a recorded outcome"*.

## Built on the clue mechanism that already exists, not a new one

`RoomContentMapComponent` already stores `RoomClueRecord`s: located, saved,
labelled from a keyed string, drawn on the map, listed per coordinate in the
Atlas and offered a *locate* button. A room's furniture already leaves clues
this way. **An event leaving one is the same thing happening for a different
reason**, so it reuses the record rather than inventing a parallel store.

Two small extensions were genuinely needed:

  * `AddClue` dereferences `landmark.Position`, and an event has no landmark
    thing. An overload takes a cell.
  * An event clue is **observed on arrival**, because the crew lived through it.
    The tick that marks ordinary clues observed requires a landmark and a
    surveyed room, and would never mark one.

The owner's *"echos of thier inhabitance in weird ways"* is the phrase for this:
the trace is what is left of something that happened to somebody.
"""
import io
import sys

NL = chr(10)

CONTENT = "src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs"
EVENTS = "src/RimroomsAsyncIndustries/Threats/AnomalyEventService.cs"
EVENTDEF = "src/RimroomsAsyncIndustries/Threats/RimroomsAnomalyEventDef.cs"

EDITS = [
    # ------------------------------------------- a clue that needs no landmark thing
    (CONTENT,
     "        internal void CompletePopulation() { populationComplete = true; }",

     "        /// <summary>" + NL
     + "        /// A clue left by something that **happened** rather than something that is here."
     + NL
     + "        ///" + NL
     + "        /// **Owner direction, 2026-10-04:** *\"remember lsd unnerving feeling with all"
     + NL
     + "        /// things ie events random spanwns\"*, restating *\"even wild waky carzxzy creepy"
     + NL
     + "        /// things when u add places and events\"*. An anomaly event used to fire one"
     + NL
     + "        /// letter and leave nothing: the notification scrolled away, the coordinate"
     + NL
     + "        /// recorded no trace, and a crew arriving next opening walked through a space"
     + NL
     + "        /// that had gone dark or been rearranged with no sign of it."
     + NL
     + "        ///" + NL
     + "        /// Two things differ from an ordinary clue and both are the reason this overload"
     + NL
     + "        /// exists at all:" + NL
     + "        ///" + NL
     + "        /// * **No landmark thing.** `AddClue` reads `landmark.Position`; an event has"
     + NL
     + "        ///   nothing to point at, so the cell is passed instead. The map label and the"
     + NL
     + "        ///   locate button already skip a clue whose landmark is null, so it degrades to"
     + NL
     + "        ///   a listed trace rather than breaking either surface." + NL
     + "        /// * **Observed on arrival.** The crew lived through it. `MapComponentTick` marks"
     + NL
     + "        ///   an ordinary clue observed only once its landmark is unfogged in a surveyed"
     + NL
     + "        ///   room, so it would never mark this one and the trace would be invisible"
     + NL
     + "        ///   forever." + NL
     + "        /// </summary>" + NL
     + "        internal void AddEventClue(string id, int roomIndex, string effectKey, IntVec3 cell)"
     + NL
     + "        {" + NL
     + "            if (string.IsNullOrEmpty(effectKey)) { return; }" + NL
     + "            string key = id + \":room:\" + roomIndex + \":event:\" + effectKey;" + NL
     + "            // One trace per event per room. A repeatable event that fires twice in the"
     + NL
     + "            // same room has left the same mark, and two identical lines in the Atlas read"
     + NL
     + "            // as a bug rather than as emphasis." + NL
     + "            if (clues.Exists(existing => existing.id == key)) { return; }" + NL
     + "            clues.Add(new RoomClueRecord" + NL
     + "            {" + NL
     + "                id = key," + NL
     + "                roomIndex = roomIndex," + NL
     + "                family = effectKey," + NL
     + "                variant = 0," + NL
     + "                landmark = null," + NL
     + "                originCell = cell," + NL
     + "                salvage = false," + NL
     + "                observed = true," + NL
     + "            });" + NL
     + "        }" + NL
     + NL
     + "        internal void CompletePopulation() { populationComplete = true; }"),

    # ------------------------------------------- the def names the trace it leaves
    (EVENTDEF,
     "        public string letterLabelKey;" + NL
     + "        public string letterTextKey;",

     "        public string letterLabelKey;" + NL
     + "        public string letterTextKey;" + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// The key fragment for the trace this event leaves in the coordinate."
     + NL
     + "        ///" + NL
     + "        /// **Owner direction, 2026-10-04:** the unnerving register applies to *\"all"
     + NL
     + "        /// things ie events random spanwns\"*. A letter is not a record -- it fires once"
     + NL
     + "        /// and scrolls away, and `THREAT_DESIGN_SHEETS.md` asks for a *\"recorded"
     + NL
     + "        /// outcome\"* as well as a readable warning." + NL
     + "        ///" + NL
     + "        /// Resolves `RR_Clue_Label_<traceKey>` and `RR_Clue_Text_<traceKey>`, which is the"
     + NL
     + "        /// same pair an ordinary room clue uses, so the Atlas listing and the on-map"
     + NL
     + "        /// label need no knowledge that this one came from an event." + NL
     + "        /// </summary>" + NL
     + "        public string traceKey;"),

    # the config error: an event without a trace leaves nothing behind
    (EVENTDEF,
     "        public override IEnumerable<string> ConfigErrors()" + NL
     + "        {",

     "        public override IEnumerable<string> ConfigErrors()" + NL
     + "        {" + NL
     + "            // **AN EVENT THAT LEAVES NOTHING BEHIND IS AN EVENT NOBODY CAN CONFIRM"
     + NL
     + "            // HAPPENED.** Enforced at load, for the same reason the inhabitant tell is:"
     + NL
     + "            // the five events that existed before this each announced once and left no"
     + NL
     + "            // record at all, and nothing objected." + NL
     + "            if (string.IsNullOrEmpty(traceKey))" + NL
     + "            {" + NL
     + "                yield return \"RimroomsAnomalyEventDef \" + defName +" + NL
     + "                    \" has no traceKey, so nothing in the coordinate records that it "
     + "happened.\";" + NL
     + "            }"),
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
    print("%-32s patched %s" % (path.split("/")[-1], old.strip().split(NL)[0][:46]))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
