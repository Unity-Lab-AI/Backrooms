# -*- coding: utf-8 -*-
"""Claims and plants for the object half of the unnerving register.

0.12.88-dev took the register to **people and events**. It did not reach
**objects**, and the owner had already named objects specifically:

    *"not just room shape echoes but echos of thier inhabitance in weird ways and
    items and equipment and production benches"*

So a coordinate was full of things that were materially varied, correctly placed,
and said nothing at all about who had been using them.

Four ways that could be lost, and every one of them is silent:

  * the tell is drawn with `Rand`, so a reload reseats which bench was wrong --
    and the one thing a player is supposed to be able to do with a tell is walk
    back and read it again;
  * the candidate list is indexed unsorted, so the same seed says different
    things on a machine with a different mod list;
  * the comp is attached to defs that cannot carry comps, so the mark is made
    against a null comp and the tell simply never exists;
  * a marked stack merges with an unmarked one and the fact is destroyed by
    hauling.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-unnerving-register.py"
PLANTS = ".local/register/plant-unnerving-register.py"

PROOF_ANCHOR = 'print("")' + NL + "if failures:"

NEW_CLAIMS = '''# ============================================ the object half: items, equipment and benches
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

'''

PLANT_ANCHOR = (
    "    # ================================================= the same register, applied to events")

NEW_PLANTS = '''    # ========================================= the object half: items, equipment and benches
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
     "                    \\" has no tellKey, so nothing on the object says what is wrong with it.\\";",
     "                    \\" \\";", PROOF),

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

    ("MARKING MOVES ABOVE THE SPAWN, spending a tell on a thing that never appeared", BUILDER,
     "            GenSpawn.Spawn(thing, cell, map, rotation);" + CHR_NL
     + "            if (!thing.Spawned || thing.Map != map) { return null; }" + CHR_NL
     + "            thing.SetForbidden(false, false);",
     "            FixtureTellService.Mark(thing, coordinate, room, slot);" + CHR_NL
     + "            GenSpawn.Spawn(thing, cell, map, rotation);" + CHR_NL
     + "            if (!thing.Spawned || thing.Map != map) { return null; }" + CHR_NL
     + "            thing.SetForbidden(false, false);", PROOF),

'''

PLANT_CONST = (
    'GENERATION_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/'
    'Keyed/RR_Generation.xml"' + NL
    + '# The object half of the same register. Added 2026-10-05 with the fixture tells.' + NL
    + 'TELL_DEF = "src/RimroomsAsyncIndustries/Generation/RimroomsFixtureTellDef.cs"' + NL
    + 'TELL_COMP = "src/RimroomsAsyncIndustries/Generation/CompRimroomsFixtureTell.cs"' + NL
    + 'TELL_SERVICE = "src/RimroomsAsyncIndustries/Generation/FixtureTellService.cs"' + NL
    + 'BUILDER = "src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs"' + NL
    + 'TELL_DEFS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsFixtureTellDefs/'
    'RR_FixtureTells.xml"' + NL
    + 'TELL_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/'
    'RR_FixtureTells.xml"'
)

problems = 0

text = io.open(PROOF, encoding="utf-8").read()
if "EVERY SHIPPED OBJECT TELL CARRIES ITS TEXT" in text:
    print("the fixture claims are already present")
elif text.count(PROOF_ANCHOR) != 1:
    print("PROOF ANCHOR NOT UNIQUE (%d)" % text.count(PROOF_ANCHOR))
    problems += 1
else:
    io.open(PROOF, "w", encoding="utf-8", newline=NL).write(
        text.replace(PROOF_ANCHOR, NEW_CLAIMS + PROOF_ANCHOR))
    print("added 18 fixture-tell claims")

text = io.open(PLANTS, encoding="utf-8").read()
if "AN OBJECT TELL LOSES ITS TEXT" in text:
    print("the fixture plants are already present")
else:
    old = ('GENERATION_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/'
           'Keyed/RR_Generation.xml"')
    if text.count(old) != 1:
        print("PLANT CONSTANT NOT UNIQUE (%d)" % text.count(old))
        problems += 1
    elif text.count(PLANT_ANCHOR) != 1:
        print("PLANT ANCHOR NOT UNIQUE (%d)" % text.count(PLANT_ANCHOR))
        problems += 1
    else:
        text = text.replace(old, PLANT_CONST)
        text = text.replace(PLANT_ANCHOR, NEW_PLANTS + PLANT_ANCHOR)
        io.open(PLANTS, "w", encoding="utf-8", newline=NL).write(text)
        print("added 17 fixture-tell plants")

if problems:
    print("%d problem(s)" % problems)
    sys.exit(1)
