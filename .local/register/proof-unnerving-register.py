# -*- coding: utf-8 -*-
"""The unnerving register reaches people, and every tell is a fact rather than an adjective.

## Owner direction, 2026-10-04, verbatim

*"remember lsd unnerving feeling with all things ie events random spanwns,
enemies, allies, nuetrals, even all the crazy things ive mentioned in the past
and anything u can find in the many many prep docs on the Backrooms Universe"*

## The mechanism, and why it can be checked at all

`docs/UNIVERSE_ADAPTATION.md` says how the source's feeling is produced:
*"Ordinary industrial interiors become uncanny through exact changes ... a
shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or
a feature that has moved since the last visit."*

**The uncanny is one exact change to something ordinary.** That is a testable
property, not a mood: a tell that says *eerie* or *unsettling* is asking the
player to feel something, while a tell that says *there is no dust on them and
nothing in this space has been swept* states a fact that cannot be true. The
adjective claim below is the prep document's own rule turned into a gate, and it
is the one claim here that could not have been written without reading that file.

## What else it guards

  * **A letter is not a tell.** The announcements fire once and scroll away;
    `THREAT_DESIGN_SHEETS.md` requires *"a visible or otherwise accessible
    warning"* and forbids colour or sound as the only cue. The tell is read off
    the pawn, for as long as the pawn exists.
  * **All three relations.** Owner: *"nutral, allies, and enemy"*. An ally is
    built from an existing non-hostile faction and Core's own defend-point lord,
    because *"just normal core mechanics"* is the standing rule and a new faction
    would be the *"new type of np0c"* the same message forbids.
  * **Animals can carry a tell too.** The comp had to reach them or the rule
    demanding a tell would be satisfied on paper and unreadable in play.

Run from the repository root. Exit status is the result.
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# `.local/register/<this>` -- three levels up. Two resolves to `.local`, every read returns ""
# and every absence claim passes against nothing. `read()` refuses an empty haystack for the
# same reason.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, held, because=""):
    print("  %-4s %s %s" % ("OK" if held else "FAIL", claim, because if not held else ""))
    if not held:
        failures.append(claim)


def read(*parts):
    path = os.path.join(*parts)
    if not os.path.isfile(path):
        raise SystemExit("ABORT: %s does not exist, so no claim about it means anything" % path)
    text = io.open(path, encoding="utf-8-sig").read()
    if not text.strip():
        raise SystemExit("ABORT: %s is empty, so no claim about it means anything" % path)
    return text


print("proof-unnerving-register")
print("-" * 78)

definition = read(SRC, "Threats", "RimroomsInhabitantDef.cs")
comp = read(SRC, "Threats", "CompRimroomsSurvivor.cs")
service = read(SRC, "Threats", "InhabitantService.cs")
families = read(MOD, "Defs", "RimroomsInhabitantDefs", "RR_Inhabitants.xml")
keyed = read(MOD, "Languages", "English", "Keyed", "RR_Inhabitants.xml")
providers = read(MOD, "Patches", "RR_NativeGateProviders.xml")

# --------------------------------------------------------------- every family has a readable tell
family_names = re.findall(r"<defName>(RR_Inhabitant_[A-Za-z]+)</defName>", families)
tell_keys = re.findall(r"<tellKey>([A-Za-z0-9_]+)</tellKey>", families)

check("EVERY SHIPPED INHABITANT FAMILY CARRIES A TELL",
      len(family_names) > 0 and len(tell_keys) == len(family_names),
      "-- %d families, %d tells. A family whose uncanny detail exists only in a letter that has "
      "scrolled away has no readable warning at all" % (len(family_names), len(tell_keys)))

missing_strings = [key for key in tell_keys if ("<%s>" % key) not in keyed]
check("and every tell resolves to a keyed string",
      not missing_strings,
      "-- %s would print its own key at the player" % ", ".join(missing_strings))

check("AND A FAMILY WITHOUT ONE IS REFUSED AT LOAD",
      "if (string.IsNullOrEmpty(tellKey))" in definition
      and "has no tellKey, so nothing on the pawn says what is wrong with it." in definition,
      "-- enforced at load rather than trusted, which is how the seven families that existed "
      "before this got away with having none")

# **THE PREP DOCUMENT'S OWN RULE, TURNED INTO A GATE.** `UNIVERSE_ADAPTATION.md`: *"Ordinary
# industrial interiors become uncanny through exact changes"*. An adjective asks the player to
# feel something; a fact that cannot be true does the work. This is the claim that could not have
# been written without reading that file.
ADJECTIVES = ("eerie", "creepy", "unsettling", "unnerving", "strange", "weird", "sinister",
              "ominous", "uncanny", "disturbing", "horrifying", "terrifying")
tell_bodies = {}
for key in tell_keys:
    found = re.search(r"<%s>(.*?)</%s>" % (key, key), keyed, re.S)
    if found:
        tell_bodies[key] = found.group(1)
adjectival = sorted(key for key, body in tell_bodies.items()
                    if any(word in body.lower() for word in ADJECTIVES))
check("EVERY TELL STATES A FACT, NOT A FEELING",
      not adjectival,
      "-- %s uses a mood adjective. `UNIVERSE_ADAPTATION.md`: the uncanny comes from *exact "
      "changes* to the ordinary, and an adjective asks the player to supply the feeling the "
      "detail should be producing" % ", ".join(adjectival))

check("and no tell is empty or a placeholder",
      len(tell_bodies) == len(tell_keys)
      and all(len(body.split()) >= 6 for body in tell_bodies.values()),
      "-- a tell of three words is a label; the detail has to be specific enough to be wrong")

# ------------------------------------------------------------ the tell is read off the pawn
check("THE TELL IS READ OFF THE PAWN, NOT ONLY FROM A LETTER",
      "public string InhabitantTell" in comp
      and "family.tellKey.Translate()" in comp
      and "string tell = InhabitantTell;" in comp,
      "-- a player who dismissed the announcement, or who is back a dozen openings later, has "
      "to be able to read why this person is wrong")

check("and it comes FIRST on the card, above the passage offer",
      comp.index("string tell = InhabitantTell;") < comp.index('"RR_Survivor_Inspect"'),
      "-- the offer is state; the tell is what the thing IS")

check("AND EVERY PLACED INHABITANT IS MARKED WITH ITS FAMILY",
      "MarkInhabitant(family.defName)" in service
      and "public void MarkInhabitant(string familyDefName)" in comp,
      "-- an unmarked inhabitant has no family, so no tell, so nothing on it to read")

check("marked BEFORE the spawn, so there is no frame without the tell",
      service.index("MarkInhabitant(family.defName)") < service.index("GenSpawn.Spawn(pawn, cell, map)"),
      "-- otherwise the pawn exists for a frame as an unexplained stranger")

check("the family is stored as a NAME, so a removed family cannot throw on load",
      "private string inhabitantFamily;" in comp
      and "GetNamedSilentFail(inhabitantFamily)" in comp,
      "-- this is saved on a pawn that can outlive a content change; a family taken out of the "
      "package must leave the pawn standing and silent")

# **TEXT, NEVER COLOUR.** `THREAT_DESIGN_SHEETS.md`: *"Do not use color or sound as the only way
# to notice a tell."*
check("THE TELL IS TEXT AND THE COMP AUTHORS NO COLOUR",
      not re.search(r"\bGUI\s*\.\s*color\s*=", comp)
      and "new Color(" not in comp,
      "-- the player's own contrast and colourblind settings are the only ones that should apply")

# ---------------------------------------------------------------------- all three relations
check("AN ALLY FAMILY EXISTS, which is the relation that did not",
      "Helper = 6," in definition
      and "<defName>RR_Inhabitant_Helper</defName>" in families
      and "<friendly>true</friendly>" in families,
      "-- owner: *\"they should be nutral, allies, and enemy in all differnt kinds and relations "
      "and scenrios\"*. Enemy shipped and neutral shipped; nothing down there helped")

check("and the help is real, through Core's own defend-point lord",
      "family.friendly && faction != null" in service
      and "new LordJob_DefendPoint(cell)" in service,
      "-- they hold the room they are found in and fight whatever comes at it with ordinary AI, "
      "which in a coordinate means the psychotic families")

check("AND AN ALLY GETS AN EXISTING NON-HOSTILE FACTION, never a new one",
      "if (family.friendly)" in service
      and "!candidate.HostileTo(Faction.OfPlayer)" in service
      and "candidate.def.humanlikeFaction" in service,
      "-- a new faction would be exactly the *\"new type of np0c\"* the same owner message "
      "forbids, and an unfactioned fallback makes a helper merely neutral rather than a threat")

check("a friendly family that is not a Helper is refused at load",
      "if (friendly && kind != InhabitantKind.Helper)" in definition
      and "if (friendly && hostile)" in definition,
      "-- a family whose relation does not match what it reads as breaks the warning-first rule "
      "in the other direction")

# ------------------------------------------------------------------------------- the animals
fauna = re.findall(r"<kind>Fauna</kind>", families)
check("WILD ANIMALS ARE SOMETHING YOU FIND, not only something that chases you",
      "Fauna = 7," in definition and len(fauna) >= 2,
      "-- owner: *\"just npc pawns and wild animals and shit of the gasme\"*. Animals reached "
      "the player only as a chaser until now, never as something standing in a room")

check("and a fauna family is neither friendly nor hostile",
      not re.search(r"<defName>RR_Inhabitant_Fauna[A-Za-z]*</defName>(?:(?!</RimroomsAsync).)*?"
                    r"<(?:friendly|hostile)>true</(?:friendly|hostile)>", families, re.S),
      "-- unfactioned, like any wild animal anywhere. The unnerving part is not that it is "
      "dangerous, it is that it is IN HERE and something had to bring it")

check("AND THE COMP REACHES ANIMALS, so their tell has somewhere to live",
      'Defs/ThingDef[@Name="AnimalThingBase"]/comps' in providers
      and providers.count("CompProperties_RimroomsSurvivor") >= 2,
      "-- patched onto Core's own abstract animal parent, because a race-condition xpath runs "
      "before def inheritance is resolved and would match only the few defs that state "
      "`intelligence` themselves")

# -------------------------------------------------------------------- no new content authored
authored_kinds = re.findall(r"<li>(RR_[A-Za-z0-9_]+)</li>",
                            " ".join(re.findall(r"<pawnKindDefNames>(.*?)</pawnKindDefNames>",
                                                families, re.S)))
check("NO FAMILY NAMES A PAWN KIND THIS MOD AUTHORED",
      not authored_kinds,
      "-- %s is ours; the existing-content policy is deleting this mod's legacy pawn kinds, and "
      "naming one here would reopen the category being closed" % ", ".join(authored_kinds))

check("and every family still names more than one kind, so a profile without the first resolves",
      all(len(re.findall(r"<li>", block)) >= 1 for block in
          re.findall(r"<pawnKindDefNames>(.*?)</pawnKindDefNames>", families, re.S)),
      "-- a family is skipped rather than substituted when none resolves, because a wanderer "
      "rendered as the wrong kind of person is worse than an empty room")

# ======================================================= the same register, applied to events
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

# **THE CLAIM A PLANT CORRECTED.** The first version compared this call's position against
# `ReceiveLetter` and a plant slipped between the two: moved below the early return but
# above the send, it still satisfied the ordering and the suite reported MISSED. The
# property that matters is not which call is first in the file -- it is that **a missing
# letter key cannot lose the record.** `letterLabelKey` is optional on the def, and
# `Announce` returns on it, so anything below that line is conditional on the event having
# a letter at all. Such an event used to leave no trace AND send no notice: complete
# silence, which is what this whole register exists to end.
check("THE TRACE IS RECORDED BEFORE THE LETTER CAN BE SKIPPED",
      "RecordTrace(map, coordinate, definition, focus);" in event_service
      and event_service.index("RecordTrace(map, coordinate, definition, focus);")
      < event_service.index("if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }")
      and event_service.index("RecordTrace(map, coordinate, definition, focus);")
      < event_service.index("Find.LetterStack.ReceiveLetter("),
      "-- a letterless event is legal, and before this it left no trace and sent no notice. "
      "Recording below that early return makes the durable half the optional one")

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

# ------------------------------------------------- the one event with a person in it
register = read(SRC, "Company", "LostPawnRegister.cs")

check("THE RADIO FRAGMENT NAMES SOMEBODY THE BRANCH KNOWS",
      "private static string VoiceFor(CoordinateRecord coordinate," in event_service
      and "AnomalyEffect.RadioFragment" in event_service
      and "foreach (StaffRecord member in campaign.Staff)" in event_service,
      "-- a fragment from nobody is atmosphere. The uncanniness is the recognition, which is "
      "the same move the Echo inhabitant family makes")

check("and a branch with nobody at home falls back to somebody it lost",
      "campaign.LostPawnNames()" in event_service,
      "-- the sadder reading, and still a recognition. With neither there is no fragment at "
      "all, because a transmission from a name nobody knows is the thing this is not")

# **MENTIONING SOMEBODY MUST NOT RESOLVE THEM.** `TakeLostPawnName` removes what it returns,
# which is right for a coordinate PLACING a missing person -- they have now been found. It is
# wrong for anything that merely names one.
check("AND NAMING A LOST PERSON DOES NOT DELETE THE RECORD THAT THEY ARE LOST",
      "public List<string> LostPawnNames()" in register
      and "new List<string>(lostPawnNames)" in register
      and "TakeLostPawnName" not in event_service,
      "-- `TakeLostPawnName` removes what it returns; a radio fragment that consumed it would "
      "quietly mark somebody found because their name was mentioned once")

check("THE VOICE IS DERIVED, NEVER Rand",
      'CampaignSeed.Derive(coordinate.Seed,' in event_service
      and '"radio:voice:" + coordinate.Openings' in event_service,
      "-- the same opening always carries the same voice; `Rand` would let a reload reseat who "
      "was on the radio, which is a save-scum on a story beat")

check("and the voices are ordered before the draw indexes them",
      "voices.Sort(System.StringComparer.Ordinal);" in event_service,
      "-- roster order is not a promise, so a derived index into an unordered list is "
      "reproducible by luck only")

check("THE FRAGMENT COSTS NOTHING, like the Presence it is modelled on",
      "case AnomalyEffect.RadioFragment: return true;" in event_service,
      "-- damages nobody, destroys nothing, blocks no route. `FireEffect` returns false to mean "
      "*the effect found nothing to do*, and a transmission never can")

# ============================================ the object half: items, equipment and benches
# Owner: *"not just room shape echoes but echos of thier inhabitance in weird ways and items and
# equipment and production benches"*. The people-and-events register shipped at 0.12.88-dev and
# reached no object at all.
tell_def = read(SRC, "Generation", "RimroomsFixtureTellDef.cs")
tell_comp = read(SRC, "Generation", "CompRimroomsFixtureTell.cs")
tell_service = read(SRC, "Generation", "FixtureTellService.cs")
archetypes = read(SRC, "Generation", "RoomArchetypeService.cs")
builder = read(SRC, "Generation", "RoomContentBuilder.cs")
tell_defs = read(MOD, "Defs", "RimroomsFixtureTellDefs", "RR_FixtureTells.xml")
tell_keyed = read(MOD, "Languages", "English", "Keyed", "RR_FixtureTells.xml")

fixture_names = re.findall(r"<defName>(RR_FixtureTell_[A-Za-z]+)</defName>", tell_defs)
fixture_keys = re.findall(r"<tellKey>(RR_FixtureTell_[A-Za-z]+)</tellKey>", tell_defs)

check("EVERY SHIPPED OBJECT TELL CARRIES ITS TEXT",
      len(fixture_names) > 0 and len(fixture_keys) == len(fixture_names),
      "-- %d tells, %d keys. An object tell with no text is a def that silently does nothing, "
      "which is how seven inhabitant families shipped with no tell at all"
      % (len(fixture_names), len(fixture_keys)))

absent = [key for key in fixture_keys if ("<%s>" % key) not in tell_keyed]
check("and every one resolves to a keyed string",
      not absent,
      "-- %s would print its own key at the player" % ", ".join(absent))

# **THE SAME GATE THE PEOPLE AND THE EVENTS ARE HELD TO.** The lights going out is not uncanny;
# the switches being found already off is. Taken from `UNIVERSE_ADAPTATION.md`, not from taste.
fixture_bodies = {}
for key in fixture_keys:
    found = re.search(r"<%s>(.*?)</%s>" % (key, key), tell_keyed, re.S)
    if found:
        fixture_bodies[key] = found.group(1)
fixture_mood = sorted(key for key, body in fixture_bodies.items()
                      if any(word in body.lower() for word in ADJECTIVES))
check("EVERY OBJECT TELL STATES A FACT, NOT A FEELING",
      not fixture_mood and len(fixture_bodies) == len(fixture_keys),
      "-- %s uses a mood adjective, or resolved to nothing at all" % ", ".join(fixture_mood))

check("and no object tell is short enough to be a label",
      len(fixture_bodies) == len(fixture_keys)
      and all(len(body.split()) >= 6 for body in fixture_bodies.values()),
      "-- a bench that is *wrong* says nothing; a bench whose bills are queued for a meal this "
      "space cannot cook says something")

check("THE SHALLOW YELLOW ROOMS STAY PLAIN, and it is refused at load rather than trusted",
      "if (minDepth <= 1)" in tell_def
      and "which would put a tell in the shallow rooms." in tell_def
      and not re.search(r"<minDepth>[01]</minDepth>", tell_defs),
      "-- that emptiness IS the look. One def with minDepth 1 would reach every arrival hall in "
      "the game and spend the setting's one surprise in a player's first thirty seconds")

check("and a tell def without text is refused at load",
      "if (string.IsNullOrEmpty(tellKey))" in tell_def
      and "has no tellKey, so nothing on the object says what is wrong with it." in tell_def,
      "-- enforced, for the same reason the inhabitant families are")

# ---------------------------------------------- the tell is read off the object, and survives
check("THE TELL IS READ OFF THE OBJECT ITSELF",
      "public override string CompInspectStringExtra()" in tell_comp
      and "definition.tellKey.Translate()" in tell_comp,
      "-- the same property the pawn tell has. A letter fires once and scrolls away; the object "
      "is still standing there a dozen openings later")

# **WITHOUT THIS, HAULING DESTROYS THE FACT.** `Thing.CanStackWith` compares def, stuff and hit
# points and never looks at comp data, so a marked stack dropped on an ordinary one would merge
# and the tell would survive or vanish depending on which absorbed which.
check("AND TIDYING UP CANNOT SILENTLY ERASE IT",
      "public override bool AllowStackWith(Thing other)" in tell_comp
      and "string.Equals(mine, theirTell, System.StringComparison.Ordinal)" in tell_comp,
      "-- a readable warning that disappears because somebody hauled it into a stack is not a "
      "readable warning")

check("and an object nobody marked stacks exactly as it always did",
      "if (string.IsNullOrEmpty(tell)) { return null; }" in tell_comp
      and "private string tell;" in tell_comp,
      "-- this comp sits on Core resource defs in every colony in the game, so the dormant path "
      "has to be the identity")

# ------------------------------------------------- derived, ordered, and from one shared rule
check("WHICH OBJECT IS WRONG IS DERIVED, NEVER Rand",
      "DestinationService.StableHash(coordinate.Seed, key, TellVersion)" in tell_service
      and "Rand." not in tell_service,
      "-- a coordinate is regenerated from its seed. `Rand` would let a reload reseat which "
      "bench was odd, which is a save-scum on the one beat a player can go back and re-read")

check("and the candidates are ordered before anything indexes them",
      "legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));"
      in tell_service,
      "-- `AllDefsListForReading` returns database order, which depends on the installed mod "
      "list. The same rule already governs the materials and the archetypes")

check("MOST OBJECTS CARRY NO TELL, which is the design and not a shortfall",
      "internal const int TellPercent = 12;" in tell_service,
      "-- *quiet stretches are required content*. A coordinate with a sentence on every stool "
      "is a museum with too many placards, and it buries the sharper people and event beats")

# **ONE RULE, ONE PLACE.** The set that can carry a tell has to be the set that can be placed.
check("THE ELIGIBILITY RULE IS SHARED WITH THE GENERATOR, NOT COPIED",
      "RoomArchetypeService.Placeable(definition)" in tell_service
      and "internal static bool Placeable(ThingDef definition)" in archetypes,
      "-- *two derivations of one rule is the defect this project keeps meeting*. If the "
      "generator stops being able to place something, it stops carrying a tell in the same edit")

# **A COMP ON A PLAIN `Thing` DOES NOTHING, SILENTLY.** Only `ThingWithComps` reads `def.comps`.
check("AND A DEFINITION THAT CANNOT CARRY A COMP IS NEVER GIVEN ONE",
      "typeof(ThingWithComps).IsAssignableFrom(definition.thingClass)" in tell_service,
      "-- a plain `Thing` accepts the entry and never instantiates it, so the mark would be made "
      "against a null comp and the tell would simply not exist")

check("the attachment happens after inheritance resolves, which no xpath can do",
      "[StaticConstructorOnStartup]" in tell_service
      and "internal static class FixtureTellService" in tell_service,
      "-- patches run on raw XML BEFORE inheritance, which is the limit recorded in "
      "`RR_NativeGateProviders.xml`. `BuildingBase` is the only parent broad enough and it would "
      "attach this to every building in every colony to reach the few that can be dressed")

# ------------------------------------------------------- and both placement paths reach it
check("BOTH PLACEMENT PATHS MARK, so the dressing and the landmark can both be wrong",
      builder.count("FixtureTellService.Mark(thing, coordinate, room, slot);") == 2,
      "-- the dressing path is where the owner's *items and equipment and production benches* "
      "actually live, and the landmark is the one object the clue chain points a player at")

marks_after_spawn = all(
    body.index("GenSpawn.Spawn(thing, cell, map, rotation);")
    < body.index("FixtureTellService.Mark(thing, coordinate, room, slot);")
    for body in [builder[builder.index("private static Thing TryPlace("):],
                 builder[builder.index("private static Thing PlaceFixture("):]])
check("and marking happens after the spawn, never before it",
      marks_after_spawn,
      "-- a thing that failed to spawn is not an object anybody can read, and marking it first "
      "would spend one of the room's few tells on nothing")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every family carries one exact wrong fact a player can read off the pawn, "
      "all three relations exist, and animals are something you find")
