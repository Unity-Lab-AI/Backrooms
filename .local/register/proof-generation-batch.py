# -*- coding: utf-8 -*-
"""The 0.12.37-dev batch: material variety per coordinate, and two generation rows that were
already true.

Rows 1005 (material variety), 1011 (inhabitant families tiered by depth and wealth), 1101's
remaining half (mineable materials and recoverable floors).

1005 was a real defect and worse than the row said: every stuffable fixture on every coordinate
in the game was `ThingDefOf.WoodLog` -- not the def's own default, one hardcoded material.

1011 and 1101 close by proof. Both were already built, which is the fifth and sixth time in this
session a row turned out to be done; the habit of checking a row against the code before building
for it has now saved more work than it has cost.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError("unbalanced body for %r" % signature)


materials = strip_cs_comments(read(os.path.join(SRC, "Generation", "CoordinateMaterials.cs")))
content = strip_cs_comments(read(os.path.join(SRC, "Generation", "RoomContentBuilder.cs")))
genstep = strip_cs_comments(read(os.path.join(SRC, "Generation",
                                              "GenStep_BackroomsDestination.cs")))
inhabitants = strip_cs_comments(read(os.path.join(SRC, "Threats", "InhabitantService.cs")))
inhabitant_def = strip_cs_comments(read(os.path.join(SRC, "Threats",
                                                     "RimroomsInhabitantDef.cs")))

print("")
print("row 1005: a coordinate is made of something, and not always wood")
print("-" * 78)

check("the hardcoded WoodLog is gone from the placement helper",
      "ThingDefOf.WoodLog" not in content,
      "-- every stuffable fixture on every coordinate in the game was this one material")
# **RESTATED, and this claim was right to fail.** It asserted "per coordinate, not per room and
# not per item", with a rationale that was MINE: that per-item choice reads as noise. The owner
# overruled it in their own words -- *"this is wrong we want every type of wall and material for
# all things randomly"* -- while holding the other half fixed: *"but depth 0 in the backrroms is
# the standard yellow style"*. What is worth protecting is that SPLIT.
check("the material comes from the coordinate, and per fixture",
      "CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot)" in content
      and content.count("CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot)") == 2,
      "-- the variant is what lets two identical fixtures in one room be different materials "
      "deeper in, and BOTH placement helpers have to pass it or the dressing path silently goes "
      "back to one material per place")
check("the coordinate reaches both placement helpers",
      "Thing Place(Map map, RoomRecord room, CoordinateRecord coordinate," in content and
      "Thing TryPlace(Map map, RoomRecord room, CoordinateRecord coordinate," in content)
check("and every call site passes it",
      not re.search(r"Place\(map, room, (?!coordinate)", content),
      "-- one missed call site would not compile, but a future one might be added wrongly")

build = body_of(materials, "List<ThingDef> Build(CoordinateRecord coordinate)")
check("the palette is derived from the coordinate's own seed",
      "DestinationService.StableHash(coordinate.Seed," in build,
      "-- a coordinate is regenerated from its seed and two players must see the same place")
check("THE CANDIDATE LIST IS SORTED BY NAME BEFORE ANYTHING INDEXES INTO IT",
      'OrderBy(definition => definition.defName, StringComparer.Ordinal)' in build,
      "-- database order depends on which mods are installed and in what order; indexing it "
      "unsorted would change a coordinate's appearance when the player installs something "
      "unrelated, and give two players with different mod lists different materials from the "
      "same seed. This is the load-bearing line in the file")
check("no Rand call anywhere in the derivation",
      "Rand." not in materials,
      "-- a pure function of the seed cannot be perturbed by how many Rand calls happened "
      "earlier in generation, and the room-content pass has changed shape once already")
# **RESTATED TWICE.** First it asserted `PaletteSize = 3`, the flat constant the owner asked to
# remove. Then it asserted a palette that grows with depth -- which the owner ALSO overruled,
# because a growing palette is still a palette, and *"every type of wall and material for all
# things randomly"* is not a palette at all. The specification is a split, and this is it.
shallow = re.search(r"const\s+int\s+ShallowPaletteSize\s*=\s*(\d+)", materials)
coherent = re.search(r"const\s+int\s+CoherentDepth\s*=\s*(\d+)", materials)
wild_body = body_of(materials, "ThingDef WildStuffFor(ThingDef definition, CoordinateRecord coordinate, int variant)")

check("LEVEL ZERO IS THE STANDARD YELLOW STYLE, SHARING ONE NARROW PALETTE",
      coherent is not None and 1 <= int(coherent.group(1)) <= 2
      and shallow is not None and int(shallow.group(1)) <= 3
      and "if (depth > CoherentDepth)" in materials,
      "-- owner direction, verbatim: *\"but depth 0 in the backrroms is the standard yellow "
      "style\"*, and earlier *\"yellow carpet and yellow wood walls for the main backrooms "
      "look\"*. A level where the table, the shelf and the walls match is what makes the yellow "
      "rooms read as a place. CoherentDepth %s, palette %s"
      % (coherent.group(1) if coherent else "MISSING",
         shallow.group(1) if shallow else "MISSING"))

check("DEEPER IN, EVERY THING DRAWS FROM EVERY TYPE CORE ALLOWS IT",
      "GenStuff.AllowedStuffsFor(definition)" in wild_body
      and "allowed[Math.Abs(seed) % allowed.Count]" in wild_body,
      "-- owner correction, verbatim: *\"this is wrong we want every type of wall and material "
      "for all things randomly\"*. Not a palette down there at all: the full set for this "
      "particular def, indexed per fixture")

check("THE VARIANT REACHES THE HASH KEY, OR EVERY FIXTURE GETS ONE MATERIAL AGAIN",
      '":" + variant' in wild_body,
      "-- without it the derivation is per def rather than per fixture, and two tables in one "
      "room are the same material however wide the set is. A plant that deleted it walked past "
      "every other claim in this section")
check("the wild path is still a pure function of the seed",
      "DestinationService.StableHash(coordinate.Seed," in wild_body
      and "Rand." not in wild_body,
      "-- a coordinate is regenerated from its seed, so two players on one seed must see the "
      "same place")

check("AND IT IS STILL SORTED, SO A MOD LIST CANNOT CHANGE A COORDINATE",
      "OrderBy(candidate => candidate.defName, StringComparer.Ordinal)" in wild_body,
      "-- AllowedStuffsFor returns database order, which depends on which mods are installed and "
      "in what order. This is the load-bearing line in the whole file")

check("it honours Core's own opt-out even on the wild path",
      "allowedInStuffGeneration" in wild_body,
      "-- Core already marks the materials that should not turn up in generated content, which is "
      "why no exclusion list of ours is needed anywhere in this file")

check("a def Core allows nothing for falls through rather than failing",
      "if (allowed.Count == 0) { return null; }" in wild_body
      and "if (wild != null) { return wild; }" in materials,
      "-- a generation pass must never fail over a furnishing choice; it falls to the palette and "
      "then to Core's own default")

check("THE PALETTE REACHES THE DEPTH-SCALED DRESSING, NOT ONLY THE FAMILY FIXTURES",
      content.count("GenStuff.DefaultStuffFor") == 0,
      "-- TryPlace places the archetype dressing, which is the benches, equipment and loot the "
      "owner means by *\"found everywher deeper in\"*, and it was taking Core's default material "
      "while the family fixtures a few lines below took the coordinate's palette. The content "
      "that was supposed to vary was the one content that could not")

check("WALLS ARE NO LONGER ONE OF TWO NAMED MATERIALS, AND ARE CHOSEN PER ROOM",
      "CoordinateMaterials.StuffFor(wallDef, coordinate, room.Index)" in genstep
      and "coordinate.Depth <= CoordinateMaterials.CoherentDepth" in genstep
      and "BuildRoomWalls(room, coordinate.Rooms, map, wallDef, roomWallStuff);" in genstep,
      "-- BackroomsPalette names exactly two wall materials across five bands, WoodLog or Steel, "
      "which is a hard-coded pair where every other material in the place is drawn from whatever "
      "the profile offers")

check("and the surface band keeps its wood walls",
      "ThingDef wallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff"
      in genstep
      and "?? wallStuff);" in genstep,
      "-- depth 1 is the canonical look and the band's own choice is still the fallback "
      "everywhere, so a coordinate with no usable palette material for a wall is unchanged")

usable = body_of(materials, "bool Usable(ThingDef definition)")
check("only Core's own stuff is eligible, and Core's own opt-out is honoured",
      "stuffProps" in usable and "allowedInStuffGeneration" in usable,
      "-- Core already marks the materials that should not turn up in generated content, so no "
      "exclusion list of ours is needed")
check("nothing here names a material",
      not re.search(r'"(Steel|WoodLog|Plasteel|Granite|Marble|Cloth|Silver|Gold|Uranium|Jade|"'
                    r'Slate|Limestone|Sandstone)"', materials),
      "-- there is no list to fall out of date, and a mod that adds a stuffable material "
      "widens the palette without being known about")
check("this mod's own defs can never become fixture material",
      'StartsWith("RR_"' in usable,
      "-- a coordinate is furnished out of the world's materials, not ours")

# The overload that actually decides. The old lookup found the two-argument forwarder, whose
# body is one line, so both claims below were reading almost nothing.
stuff_for = body_of(materials,
                    "ThingDef StuffFor(ThingDef definition, CoordinateRecord coordinate, int variant)")
check("a fixture the palette cannot supply falls back to Core's own default",
      "GenStuff.DefaultStuffFor(definition)" in stuff_for,
      "-- a stuffable def with no material cannot be built, and a generation pass must not "
      "fail over a furnishing choice")
check("a fixture that takes no material gets none",
      "!definition.MadeFromStuff) { return null; }" in stuff_for)
check("the cache is scoped to one game",
      "cachedGeneration" in materials and "Current.Game" in materials,
      "-- a reload must not inherit a palette built against a previous def database, which a "
      "mod change could alter")

print("")
print("row 1011: inhabitant families are already tiered by depth and wealth")
print("-" * 78)

check("the def declares a depth range",
      "public int minDepth" in inhabitant_def and "public int maxDepth" in inhabitant_def)
check("and a pressure band floor",
      "public CoordinatePressureLadder.Band minBand" in inhabitant_def)
check("and a relative weight against the others legal in the same situation",
      "public float weight" in inhabitant_def)
legal = body_of(inhabitants, "List<RimroomsInhabitantDef> Legal(int depth,")
check("selection filters on depth",
      "family.minDepth <= depth" in legal,
      "-- 'tiered by depth' is this line")
check("WEALTH REACHES IT THROUGH THE LADDER, WHICH IS WHERE IT BELONGS",
      "CoordinatePressureLadder.ColonyWealth()" in inhabitants and
      "CoordinatePressureLadder.BandFor(coordinate, wealth)" in inhabitants,
      "-- the band is the ladder's own two-input answer, so 'tiered by wealth' is not a second "
      "wealth rule here; there is one and it lives in the ladder")
check("the encounter cap is the ladder's too",
      "CoordinatePressureLadder.EncounterCapFor(coordinate, wealth)" in inhabitants)
# Declaration AND use AND derivation. A first version of this checked only the call site, and a
# planted rename of the declaration left it matching -- the claim has to pin the whole chain.
check("EVERY VARIATION IS SEEDED from the coordinate",
      "private static int DestinationServiceSeed(CoordinateRecord coordinate)" in inhabitants and
      inhabitants.count("= DestinationServiceSeed(coordinate);") >= 2 and
      "Gen.HashCombineInt(coordinate.Seed," in inhabitants,
      "-- the row asks for 'every variation seeded', and this is it")

print("")
print("row 1101: the interior is strippable, floors included")
print("-" * 78)

check("rock is placed from the world's own natural rock types",
      "Find.World.NaturalRockTypesIn(map.Tile)" in genstep and "FillWithRock" in genstep,
      "-- the mineable half of the row, which already shipped")
check("floors are ordinary Core terrain, named not authored",
      'GetNamedSilentFail("Concrete")' in genstep and
      'GetNamedSilentFail("PavedTile")' in genstep,
      "-- Concrete and PavedTile both descend from Core's FloorBase, which sets "
      "layerable=true, and TerrainDef.Removable IS layerable -- so Core's own floor-removal "
      "designator works on a coordinate and returns the floor's costList materials. The "
      "recoverable-floors half needed no code because the floors were never special")
check("this mod authors no terrain of its own for a coordinate's floors",
      not re.search(r'GetNamedSilentFail\("RR_\w*(Floor|Terrain|Tile)', genstep),
      "-- an authored floor would be new gameplay content and would not be removable by "
      "Core's designator unless it were told to be")
check("the void floor is deliberately impassable terrain",
      'GetNamedSilentFail("WaterDeep")' in genstep,
      "-- which is also why removing a room floor is safe: Core's SetTerrain refuses to file "
      "an impassable terrain as under-terrain and substitutes the generator's own default, so "
      "stripping a floor cannot drop the player into the void")

print("")
print("the fifth launch: a light count took the whole coordinate down")
print("-" * 78)

# Owner, verbatim: *"i dont see a natural gate thats suppose to be on the back wall of one of the
# storage rooms so that they can eneter theri 300x300 gate ie the stargate mode that prcedurally
# generated the backrooms of diffent levels with thir natual gate spawns to different levels
# within"*.
#
# The door WAS there -- confirmed live, a steel Building_Door at (160, 161) with the emergence
# comp's "Mark as way home" gizmo enabled. It was never MARKED, because SoloGroupOpening stops at
# step 2 when the destination site fails, and the site failed on a light count.

check("THE LIGHT COUNT FORMULA IS GONE",
      "expectedPowerLights" not in genstep
      and 'room.familyId == "service_passage" || room.familyId == "utility_room")' not in
      genstep.replace('.Where(room => room.familyId == "service_passage" || room.familyId == "utility_room")', ""),
      "-- it required the number of things whose def == lightDef to equal "
      "Rooms.Count + Rooms.Count(service_passage or utility_room). The extra lamps in that sum "
      "are RoomContentBuilder's hard-coded StandingLamp, and BackroomsPalette switched lightDef "
      "to WallLamp at 0.7.8-dev. climateRoom requires at least one of those rooms to exist, so "
      "the shortfall was GUARANTEED and no coordinate generated for thirty-nine checkpoints")

check("the validator checks the lights that were ACTUALLY placed",
      "var placedLights = new List<Thing>();" in genstep
      and "placedLights.Add(light);" in genstep
      and "ValidateNativePowerNetwork(map, generator, climate, placedLights)" in genstep
      and "List<Thing> placedLights)" in genstep,
      "-- a list the caller built, rather than a number re-derived from the coordinate")

check("EVERY POWER CONSUMER ON THE MAP IS CHECKED, WHATEVER PLACED IT",
      "foreach (Thing thing in map.listerThings.AllThings)" in genstep
      and "thing.TryGetComp<CompPowerTrader>() != null) { consumers.Add(thing); }" in genstep,
      "-- this is the invariant a player can see: nothing here is dark or cold. It names no def "
      "and predicts no count, so a lamp any other code adds later is covered automatically")

# The BLOCK BODY, read on its own. A claim that a warning exists is not a claim that a throw
# does not -- that plant walked straight past the first version of this check, which asserted
# only that Log.Warning and "if (powerFault != null)" were both present. Sixth time this exact
# shape has defeated a claim in this project.
fault_at = genstep.find("if (powerFault != null)")
fault_body = genstep[fault_at:genstep.find(chr(10) + "                }", fault_at)] if fault_at >= 0 else ""
check("A POWER FAULT IS REPORTED AND NEVER FATAL",
      "string powerFault = ValidateNativePowerNetwork" in genstep
      and fault_at >= 0
      and "Log.Warning(" in fault_body
      and "throw" not in fault_body
      and "return null;" in genstep,
      "-- a coordinate with an unconnected heater is dark, cold and playable. A coordinate that "
      "does not exist costs the player the gate that leads to it, which is exactly what the "
      "fifth launch reported")

check("the structural validation is still fatal",
      "ValidatePlacedLayout(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);"
      in genstep
      and 'throw new InvalidOperationException("RR_Generation_UnreachableRoom")' in genstep,
      "-- a coordinate you cannot walk through really is broken, and weakening that would be "
      "trading one silent failure for another")

check("THE WALL LAMP IS MOUNTED ON A WALL, FACING IT",
      "FindWallAttachmentCell(" in genstep
      and "lightDef.building.isAttachment" in genstep
      and "GenSpawn.Spawn(light, lightCells[index], map, lightFacings[index]);" in genstep
      and "facing = Rot4.FromIntVec3(direction);" in genstep,
      "-- WallLamp draws with drawOffsetNorth (0,0,0.9), almost a full cell INTO the wall it is "
      "mounted on, so the rotation is the difference between a lamp on the wall and a lamp "
      "hanging over the floor")

check("it branches on the DEF rather than a def name",
      'lightDef.building != null && lightDef.building.isAttachment' in genstep
      and '"WallLamp"' not in genstep,
      "-- BackroomsPalette still falls back to StandingLamp, which stands on the floor and must "
      "keep doing so; naming WallLamp here would recreate the coupling that caused the outage")

check("a lamp mounts on the room's own wall, not on a door",
      "wall.def != wallDef) { continue; }" in genstep,
      "-- a door also holds up roof, and a lamp mounted on a door is mounted on nothing the "
      "moment it opens")

check("A ROOM WITH NOWHERE TO MOUNT FALLS BACK INSTEAD OF FAILING",
      "return IntVec3.Invalid;" in genstep
      and "if (!lightCell.IsValid)" in genstep
      and "lightCell = FindClearInteriorCell(map, room," in genstep,
      "-- the threshold room holds the gate anchor, the entry cell, the return cell and the "
      "anchor's whole expanded rect, so its wall-adjacent cells can all be reserved. A lamp on "
      "the floor is a cosmetic compromise; a coordinate that does not generate is not")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a coordinate has materials of its own, its inhabitants are tiered by depth "
      "and wealth, and its floors were always ordinary")
