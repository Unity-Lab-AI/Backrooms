# -*- coding: utf-8 -*-
"""Planted faults against `proof-unnerving-register.py`.

## The one that matters most

*"a tell becomes an adjective"*. `docs/UNIVERSE_ADAPTATION.md` says the uncanny
comes from *"exact changes"* to the ordinary, and that is the whole difference
between a detail that works and one that asks the player to supply the feeling.
It is also the easiest thing in this package to lose by accident, because
*"something feels wrong here"* reads like writing and *"there is no dust on them
and nothing in this space has been swept"* reads like a note. The second one is
the product.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

DEF = "src/RimroomsAsyncIndustries/Threats/RimroomsInhabitantDef.cs"
COMP = "src/RimroomsAsyncIndustries/Threats/CompRimroomsSurvivor.cs"
SERVICE = "src/RimroomsAsyncIndustries/Threats/InhabitantService.cs"
FAMILIES = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsInhabitantDefs/RR_Inhabitants.xml"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Inhabitants.xml"
PROVIDERS = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml"
PROOF = ".local/register/proof-unnerving-register.py"
# The event half of the same register. Added 2026-10-04 with the traces themselves.
EVENTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsAnomalyEventDefs/RR_AnomalyEvents.xml"
EVENTDEF = "src/RimroomsAsyncIndustries/Threats/RimroomsAnomalyEventDef.cs"
EVENT_SERVICE = "src/RimroomsAsyncIndustries/Threats/AnomalyEventService.cs"
CONTENT = "src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs"
REGISTER = "src/RimroomsAsyncIndustries/Company/LostPawnRegister.cs"
GENERATION_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Generation.xml"
# The object half of the same register. Added 2026-10-05 with the fixture tells.
TELL_DEF = "src/RimroomsAsyncIndustries/Generation/RimroomsFixtureTellDef.cs"
TELL_COMP = "src/RimroomsAsyncIndustries/Generation/CompRimroomsFixtureTell.cs"
TELL_SERVICE = "src/RimroomsAsyncIndustries/Generation/FixtureTellService.cs"
BUILDER = "src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs"
TELL_DEFS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsFixtureTellDefs/RR_FixtureTells.xml"
TELL_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_FixtureTells.xml"
CHR_NL = chr(10)

PLANTS = [
    # ------------------------------------------------------- the tell exists and is readable
    ("A FAMILY LOSES ITS TELL", FAMILIES,
     "    <tellKey>RR_Inhabitant_EchoTell</tellKey>" + CHR_NL, "", PROOF),

    ("a tell points at a keyed string that does not exist", FAMILIES,
     "<tellKey>RR_Inhabitant_WandererTell</tellKey>",
     "<tellKey>RR_Inhabitant_WandererTellXX</tellKey>", PROOF),

    ("the load-time rule demanding a tell is removed", DEF,
     "            if (string.IsNullOrEmpty(tellKey))", "            if (false)", PROOF),

    # **THE PREP DOCUMENT'S RULE, AND THE EASIEST THING HERE TO LOSE BY ACCIDENT.**
    # "Something feels wrong here" reads like writing; "there is no dust on them" is the product.
    ("A TELL BECOMES AN ADJECTIVE instead of a fact", KEYED,
     "<RR_Inhabitant_WandererTell>There is no dust on them. Nothing in this space has been "
     "swept.</RR_Inhabitant_WandererTell>",
     "<RR_Inhabitant_WandererTell>There is something deeply unsettling about them."
     "</RR_Inhabitant_WandererTell>", PROOF),

    ("and a tell shrinks to a label", KEYED,
     "<RR_Inhabitant_MissingTell>Their clothes are in better repair than the day they went "
     "missing.</RR_Inhabitant_MissingTell>",
     "<RR_Inhabitant_MissingTell>Missing person.</RR_Inhabitant_MissingTell>", PROOF),

    # ------------------------------------------------------- the tell reaches the pawn
    ("THE TELL STOPS BEING READ OFF THE PAWN", COMP,
     "            string tell = InhabitantTell;", "            string tell = null;", PROOF),

    ("the tell drops below the passage offer on the card", COMP,
     "            string tell = InhabitantTell;" + CHR_NL
     + "            if (!string.IsNullOrEmpty(tell)) { lines.Add(tell); }" + CHR_NL
     + '            if (IsSurvivor) { lines.Add("RR_Survivor_Inspect".Translate().ToString()); }',
     '            if (IsSurvivor) { lines.Add("RR_Survivor_Inspect".Translate().ToString()); }'
     + CHR_NL
     + "            string tell = InhabitantTell;" + CHR_NL
     + "            if (!string.IsNullOrEmpty(tell)) { lines.Add(tell); }", PROOF),

    ("AN INHABITANT IS PLACED WITHOUT BEING MARKED, so nothing on it can be read", SERVICE,
     "            pawn.TryGetComp<CompRimroomsSurvivor>()?.MarkInhabitant(family.defName);"
     + CHR_NL, "", PROOF),

    # **THIS PLANT USED TO DELETE THE LINE, which is the plant above it.** Both carried the
    # same signature, which is why the table needed a dedupe loop bolted after it -- and
    # that loop is what made `check-plant-anchors.py` report no readable table. The claim
    # this is for is the ORDERING: marked before the spawn, so there is no frame in which
    # an inhabitant exists as an unexplained stranger. So it moves the line.
    ("THE MARK MOVES BELOW THE SPAWN, leaving a frame with no tell", SERVICE,
     "            pawn.TryGetComp<CompRimroomsSurvivor>()?.MarkInhabitant(family.defName);"
     + CHR_NL
     + "            if (family.kind == InhabitantKind.Survivor)",
     "            if (family.kind == InhabitantKind.Survivor)", PROOF),

    ("the family is resolved eagerly, so a removed family throws on load", COMP,
     "GetNamedSilentFail(inhabitantFamily)", "GetNamed(inhabitantFamily)", PROOF),

    ("the comp starts authoring a colour instead of text", COMP,
     "            var lines = new List<string>();",
     "            var lines = new List<string>(); GUI.color = new Color(1f, 0f, 0f);", PROOF),

    # ------------------------------------------------------------------- the ally relation
    ("THE ALLY FAMILY DISAPPEARS", FAMILIES,
     "    <friendly>true</friendly>" + CHR_NL, "", PROOF),

    ("the ally stops actually helping", SERVICE,
     "                LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(cell), map,",
     "                LordMaker.MakeNewLord(faction, HostileLordJob(band, cell, faction), map,",
     PROOF),

    ("AN ALLY IS GIVEN A HOSTILE FACTION", SERVICE,
     "                            && !candidate.HostileTo(Faction.OfPlayer)",
     "                            && candidate.HostileTo(Faction.OfPlayer)", PROOF),

    ("the friendly-relation rule stops being enforced at load", DEF,
     "            if (friendly && kind != InhabitantKind.Helper)", "            if (false)",
     PROOF),

    # ----------------------------------------------------------------------- the animals
    ("THE ANIMAL FAMILIES DISAPPEAR", FAMILIES,
     "    <kind>Fauna</kind>" + CHR_NL, "", PROOF),

    ("an animal family is made hostile", FAMILIES,
     "    <defName>RR_Inhabitant_FaunaWild</defName>",
     "    <defName>RR_Inhabitant_FaunaWild</defName>" + CHR_NL
     + "    <hostile>true</hostile>", PROOF),

    ("AND THE COMP STOPS REACHING ANIMALS, so their tell has nowhere to live", PROVIDERS,
     '        <xpath>Defs/ThingDef[@Name="AnimalThingBase"]/comps</xpath>' + CHR_NL
     + "        <value>" + CHR_NL
     + '          <li Class="RimroomsAsyncIndustries.Threats.CompProperties_RimroomsSurvivor" />'
     + CHR_NL
     + "        </value>",
     '        <xpath>Defs/ThingDef[@Name="AnimalThingBase"]/comps</xpath>' + CHR_NL
     + "        <value>" + CHR_NL
     + "          <li />" + CHR_NL
     + "        </value>", PROOF),

    # ------------------------------------------------- the one event with a person in it
    ("THE RADIO VOICE GOES BACK TO Rand, so a reload reseats who was on the radio", EVENT_SERVICE,
     '            int draw = CampaignSeed.Derive(coordinate.Seed,' + CHR_NL
     + '                "radio:voice:" + coordinate.Openings, 1);',
     "            int draw = Rand.Range(0, 9999);", PROOF),

    ("the voices stop being ordered before the draw", EVENT_SERVICE,
     "            voices.Sort(System.StringComparer.Ordinal);" + CHR_NL, "", PROOF),

    ("NAMING A LOST PERSON DELETES THE RECORD THAT THEY ARE LOST", EVENT_SERVICE,
     "                foreach (string lost in campaign.LostPawnNames())",
     "                foreach (string lost in new[] { campaign.TakeLostPawnName() })", PROOF),

    ("the non-destructive accessor is removed from the register", REGISTER,
     "        public List<string> LostPawnNames()", "        private List<string> Unused()",
     PROOF),

    ("THE FRAGMENT STOPS NAMING ANYBODY and fires as anonymous noise", EVENT_SERVICE,
     "            foreach (StaffRecord member in campaign.Staff)",
     "            foreach (StaffRecord member in new List<StaffRecord>())", PROOF),

    ("the fragment starts claiming it found nothing to do", EVENT_SERVICE,
     "                case AnomalyEffect.RadioFragment: return true;",
     "                case AnomalyEffect.RadioFragment: return false;", PROOF),

    # ========================================= the object half: items, equipment and benches
    ("AN OBJECT TELL LOSES ITS TEXT", TELL_DEFS,
     "    <tellKey>RR_FixtureTell_BenchQueuedText</tellKey>" + CHR_NL, "", PROOF),

    ("an object tell points at a keyed string that does not exist", TELL_DEFS,
     "<tellKey>RR_FixtureTell_LightSwitchedText</tellKey>",
     "<tellKey>RR_FixtureTell_LightSwitchedTextXX</tellKey>", PROOF),

    # **THE PREP DOCUMENT'S RULE AGAIN, and the easiest thing here to lose by accident.**
    ("AN OBJECT TELL BECOMES AN ADJECTIVE", TELL_KEYED,
     "The switch was found in the off position. The bulb is still warm.",
     "There is something deeply unsettling about this lamp.", PROOF),

    ("an object tell is cut down to a label", TELL_KEYED,
     "There is dust on everything in this space except this.", "No dust.", PROOF),

    ("A TELL REACHES THE SHALLOW YELLOW ROOMS", TELL_DEFS,
     "    <minDepth>2</minDepth>" + CHR_NL
     + "    <weight>1.2</weight>" + CHR_NL
     + "    <tellKey>RR_FixtureTell_LightSwitchedText</tellKey>",
     "    <minDepth>1</minDepth>" + CHR_NL
     + "    <weight>1.2</weight>" + CHR_NL
     + "    <tellKey>RR_FixtureTell_LightSwitchedText</tellKey>", PROOF),

    ("the load-time rule keeping tells out of the shallow rooms is removed", TELL_DEF,
     "            if (minDepth <= 1)", "            if (false)", PROOF),

    ("the load-time rule demanding tell text is removed", TELL_DEF,
     "                    \" has no tellKey, so nothing on the object says what is wrong with it.\";",
     "                    \" \";", PROOF),

    # ------------------------------------------- the tell is read off the object and survives
    ("THE OBJECT TELL STOPS BEING READABLE OFF THE OBJECT", TELL_COMP,
     "        public override string CompInspectStringExtra()",
     "        private string UnusedInspect()", PROOF),

    ("HAULING SILENTLY ERASES THE FACT", TELL_COMP,
     "        public override bool AllowStackWith(Thing other)",
     "        private bool UnusedAllowStackWith(Thing other)", PROOF),

    # ----------------------------------------------- derived, ordered, one shared rule
    ("WHICH OBJECT IS WRONG GOES BACK TO Rand", TELL_SERVICE,
     "            int roll = DestinationService.StableHash(coordinate.Seed, key, TellVersion);",
     "            int roll = Rand.Range(0, 9999);", PROOF),

    ("the tell candidates stop being ordered before the draw", TELL_SERVICE,
     "            legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));"
     + CHR_NL, "", PROOF),

    ("EVERY OBJECT STARTS CARRYING A TELL, burying the people and event beats", TELL_SERVICE,
     "        internal const int TellPercent = 12;",
     "        internal const int TellPercent = 100;", PROOF),

    ("THE ELIGIBILITY RULE IS COPIED INSTEAD OF SHARED", TELL_SERVICE,
     "!RoomArchetypeService.Placeable(definition)",
     "definition.category != ThingCategory.Item", PROOF),

    ("A DEFINITION THAT CANNOT CARRY A COMP IS GIVEN ONE ANYWAY", TELL_SERVICE,
     "                    || !typeof(ThingWithComps).IsAssignableFrom(definition.thingClass))",
     "                    || false)", PROOF),

    ("the comp attachment moves back to load time, before inheritance resolves", TELL_SERVICE,
     "    [StaticConstructorOnStartup]" + CHR_NL, "", PROOF),

    # ------------------------------------------------------- both placement paths reach it
    ("THE DRESSING PATH STOPS MARKING, so loot and benches go back to saying nothing",
     BUILDER,
     "            FixtureTellService.Mark(thing, coordinate, room, slot);" + CHR_NL
     + "            return thing;" + CHR_NL + "        }" + CHR_NL + CHR_NL
     + "        /// <summary>" + CHR_NL
     + "        /// A cell in this room that will take this footprint",
     "            return thing;" + CHR_NL + "        }" + CHR_NL + CHR_NL
     + "        /// <summary>" + CHR_NL
     + "        /// A cell in this room that will take this footprint", PROOF),

    # Re-aimed: the lines around the call moved when forbidding was added. The claim is the ORDER
    # -- a thing that failed to spawn is not an object anybody can read, so marking it first spends
    # one of the room's few tells on nothing -- so the anchor is the two statements whose order it
    # is about.
    ("MARKING MOVES ABOVE THE SPAWN, spending a tell on a thing that never appeared", BUILDER,
     "            thing.SetForbidden(true, false);" + CHR_NL
     + "            // **The dressing is where the owner's *\"items and equipment and production benches\"*",
     "            FixtureTellService.Mark(thing, coordinate, room, slot);" + CHR_NL
     + "            thing.SetForbidden(true, false);" + CHR_NL
     + "            // **The dressing is where the owner's *\"items and equipment and production benches\"*",
     PROOF),

    # ================================================= the same register, applied to events
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

    # **THIS PLANT CORRECTED ITS OWN CLAIM.** The first version moved the record below the
    # early return but kept it above the send, which satisfied an ordering claim that was
    # asking the wrong question. It now moves the record past the return entirely, which is
    # the real regression: a letterless event leaves nothing at all.
    ("THE TRACE IS WRITTEN BELOW THE LETTER EARLY RETURN, so a letterless event records nothing",
     EVENT_SERVICE,
     "            RecordTrace(map, coordinate, definition, focus);" + CHR_NL + CHR_NL
     + "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }",
     "            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }" + CHR_NL
     + "            RecordTrace(map, coordinate, definition, focus);", PROOF),

    ("an event trace is left unobserved, so it is invisible for ever", CONTENT,
     "                observed = true," + CHR_NL, "", PROOF),

    ("a repeatable event starts stacking identical traces", CONTENT,
     "            if (clues.Exists(existing => existing.id == key)) { return; }" + CHR_NL,
     "", PROOF),

    ("AND A TRACE IS ALLOWED INTO THE THRESHOLD ROOM", EVENT_SERVICE,
     '                room = coordinate.Rooms.FirstOrDefault(candidate => candidate.familyId != "threshold_room");',
     "                room = coordinate.Rooms.FirstOrDefault();", PROOF),

    # ------------------------------------------------------ no new content authored
    ("A FAMILY NAMES A PAWN KIND THIS MOD AUTHORED", FAMILIES,
     "      <li>Villager</li>", "      <li>RR_StaffResearcher</li>", PROOF),
]

# **NO POST-PROCESSING OF THE TABLE.** A list comprehension and a dedupe loop used to
# rewrite PLANTS after the literal, left over from a duplicate plant that has since been
# re-aimed. `tools/check-plant-anchors.py` parses the literal and reported
# `has no readable PLANTS table` -- a suite the battery cannot inspect is a suite that rots
# silently, which is the reason that checker exists. The table is a plain literal again.


for _plant in PLANTS:
    if len(_plant) != 5:
        sys.stderr.write("PLANT LIST MALFORMED: %r has %d field(s), not 5" + chr(10)
                         % (_plant[0], len(_plant)))
        sys.exit(2)


_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def write_verified(path, text):
    """Write, and do not believe it until it reads back identical. Retried both ways."""
    last = None
    for attempt in range(6):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.4 * (attempt + 1))
    sys.stderr.write("FATAL: could not write %s (%s) -- sentinel left in place on purpose\n"
                     % (path, last))
    sys.exit(3)


ORIGINALS = {path: io.open(path, encoding="utf-8").read()
             for path in sorted({plant[1] for plant in PLANTS})}

print("baseline -- the target must pass before anything is planted")
for command in sorted({plant[4] for plant in PLANTS}):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in ORIGINALS.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every target verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
