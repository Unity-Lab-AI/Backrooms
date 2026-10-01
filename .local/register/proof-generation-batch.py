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

# A family fixture written as a bare statement, at the indent the switch arms use. Its ABSENCE is
# the claim that every decoration became a `Decorate` call; see that claim for why the obvious
# shorter string was wrong.
BARE_FIXTURE = chr(10) + " " * 28 + "Place(map, room, coordinate,"
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
      # BOTH of them. `StuffFor` and `StuffForRoom` each compute a wild material and each must
      # return it; a plant that neutered one was satisfied by the other still containing the
      # line. The same two-call-sites gap as the AllComps.Add claim and the span-evenness claim.
      and materials.count("if (wild != null) { return wild; }") >= 2,
      "-- a generation pass must never fail over a furnishing choice; it falls to the palette and "
      "then to Core's own default")

check("THE PALETTE REACHES THE DEPTH-SCALED DRESSING, NOT ONLY THE FAMILY FIXTURES",
      content.count("GenStuff.DefaultStuffFor") == 0,
      "-- TryPlace places the archetype dressing, which is the benches, equipment and loot the "
      "owner means by *\"found everywher deeper in\"*, and it was taking Core's default material "
      "while the family fixtures a few lines below took the coordinate's palette. The content "
      "that was supposed to vary was the one content that could not")

check("WALLS ARE NO LONGER ONE OF TWO NAMED MATERIALS, AND ARE CHOSEN PER ROOM",
      "CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index)" in genstep
      # **MEASURED PER ROOM, NOT PER COORDINATE.** This claim used to require
      # `coordinate.Depth <= CoherentDepth`, which short-circuited the whole of level 0 to the
      # band's wood -- so every room on a 300-cell map read as one corridor, and that is the
      # level the owner walked. It caught exactly that when the call changed and the gate did
      # not: a proof earning its keep.
      and "int wallDepth = RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth);" in genstep
      and "wallDepth <= CoordinateMaterials.CoherentDepth" in genstep
      and "BuildRoomWalls(room, coordinate.Rooms, map, wallDef, roomWallStuff);" in genstep,
      "-- BackroomsPalette names exactly two wall materials across five bands, WoodLog or Steel, "
      "which is a hard-coded pair where every other material in the place is drawn from whatever "
      "the profile offers")

check("AND StuffForRoom ACTUALLY MEASURES THE ROOM",
      "int effective = RoomArchetypeService.EffectiveDepth(coordinate, room, depth);" in materials,
      "-- it takes a room and must use it. A plant replaced the measurement with the "
      "coordinate's own depth and every other claim about per-room walls still held, because "
      "they checked the call and not what the callee does with it")

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
print("THE CONDUIT BLOWOUT THAT STOPPED EVERY 300x300 COORDINATE")
print("-" * 78)

# The sixth launch: SpawnNativeConduit threw RR_Generation_ContentPlacementFailed, so
# MarkLayoutReady never ran, so SoloGroupOpening stopped at step 2 again and the Store's back door
# was never marked. An unmarked door is an ordinary steel door, which is everything the owner
# reported: *"its not blue!!! it doesnt have a light aura, and it in no way is a portal"*.
#
# The cause, measured: the grid carpeted every powered room with conduit. At 12x12 rooms that was
# ~100 cells. At depth 1 a service_passage is 60x80, so ContractedBy(1) is 4,524 cells against
# MaxNativePowerConduits = 512 -- an EIGHTFOLD blowout on the first powered room, every time.
cap = re.search(r"const\s+int\s+MaxNativePowerConduits\s*=\s*(\d+)", genstep)

# Read the grid method's own BODY. The first version of this named the two retired symbols, so a
# plant that re-carpeted using different names walked straight past it. What is forbidden is the
# SHAPE -- flattening whole rects into conduit cells -- not the old variable name.
grid_at = genstep.find("private static HashSet<IntVec3> SpawnNativePowerNetwork(")
grid_body = genstep[grid_at:genstep.find(chr(10) + "        }" + chr(10), grid_at)] \
    if grid_at >= 0 else ""
check("THE WHOLE-ROOM CONDUIT CARPET IS GONE",
      grid_at >= 0
      and "poweredRoomCoverage" not in genstep
      and "ContractedBy(1)).ToList()" not in genstep
      and "SelectMany" not in grid_body,
      "-- wiring four thousand cells to catch one lamp is the wrong shape at any size, and at "
      "80x80 it made the coordinate impossible to generate rather than merely wasteful")

check("the grid hands back what it wired, so a later pass can route from it",
      "private static HashSet<IntVec3> SpawnNativePowerNetwork(" in genstep
      and "HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(" in genstep,
      "-- the carpet existed because the lamps the dressing adds did not exist yet; the answer is "
      "to wire them after they do, which needs the grid that was built")

stray_at = genstep.find("private static void ConnectStrayConsumers(")
stray_body = genstep[stray_at:genstep.find(chr(10) + "        }" + chr(10), stray_at)] \
    if stray_at >= 0 else ""
populate_at = genstep.find("RoomContentBuilder.Populate(map, coordinate, entryCell")
call_at = genstep.find("ConnectStrayConsumers(map, voidFloor, conduitDef, wiredCells, generator);")
check("ANYTHING THAT DRAWS POWER IS WIRED AFTER THE DRESSING PLACES IT",
      stray_at >= 0 and populate_at >= 0 and call_at >= 0 and populate_at < call_at,
      "-- the lamps and benches the archetype dressing places only exist after Populate. Wiring "
      "before that is guessing where they will land. Populate at %d, pass at %d"
      % (populate_at, call_at))

check("it finds them the same way the validator finds them",
      "TryGetComp<CompPowerTrader>() != null" in stray_body
      and "map.listerThings.AllThings" in stray_body,
      "-- the thing that REPORTS a stray consumer and the thing that FIXES one now agree by "
      "construction rather than by two people remembering the same rule")

check("THE STRAY PASS CAN NEVER COST THE COORDINATE",
      stray_at >= 0 and "throw" not in stray_body
      and "private static void TrySpawnNativeConduit(" in genstep
      and "TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);" in stray_body
      # The Try form CONTAINS the throwing form as a substring, so the naive test fails against
      # correct code. Strip the safe calls first and then look for a bare one. This claim fell
      # into the exact prefix trap it was written to close, which is the most on-the-nose lesson
      # this session has produced.
      and "SpawnNativeConduit(" not in stray_body.replace("TrySpawnNativeConduit(", ""),
      "-- a lamp that cannot be reached is a dark corner. Losing the whole place over a conduit "
      "is the defect this checkpoint exists to fix, and the throwing form is kept only for the "
      "generator's own footprint where a failure really is a generator fault")

check("and it still respects the conduit cap",
      stray_body.count("wiredCells.Count >= MaxNativePowerConduits") >= 2
      and cap is not None,
      "-- bounded, so a pathological map cannot carpet itself. Cap is %s"
      % (cap.group(1) if cap else "MISSING"))

# The arithmetic that caused it, so the shape cannot come back unnoticed.
MAPW, MARGIN, GAP, MINS = 300, 14, 10, 3
_spacing = (MAPW - MARGIN * 2) // MINS
_span = _spacing - GAP
if _span % 2:
    _span -= 1
_passage = (_span * 3 // 4) - ((_span * 3 // 4) % 2)
_carpet = (_passage - 2) * (_span - 2)
check("the arithmetic that caused it is recorded, not just the fix",
      cap is not None and _carpet > int(cap.group(1)),
      "-- one powered room at depth 1 is %d cells contracted by one, against a cap of %s. Any "
      "future per-room area pass has the same problem and this is the number that proves it"
      % (_carpet, cap.group(1) if cap else "MISSING"))

print("")
print("THE SCALE SWEEP: THE CONDUIT CAP IS SIZED FOR THE MAP IT IS ON")
print("-" * 78)

# Owner: *"its suppose to be built and working 100% we finished the build yesterday!"* -- correct,
# and the right answer was to stop finding these one launch at a time. Every constant in the
# generation path was sized against a 300x300 map, 80-cell rooms and 42 rooms.
#
# Two more would have killed a coordinate, both the same family as the light count at 0.12.48-dev
# and the conduit carpet at 0.12.52-dev: a number written against the old scale that no proof can
# see has stopped fitting.
#
# THIS CLAIM MODELS THE ROUTING AND COMPARES IT TO THE CAP THE SOURCE HOLDS, so the cap cannot
# silently stop fitting again. FindConduitRoute BFSes from the whole wired set, so routes share a
# spine and the total is far below the sum of the distances -- which is why the answer is about
# 1,600 rather than tens of thousands.
from collections import deque as _deque

_CAP = re.search(r"const\s+int\s+MaxNativePowerConduits\s*=\s*(\d+)", genstep)
_MAPW = re.search(r"const\s+int\s+MapWidth\s*=\s*(\d+)",
                  read(os.path.join(SRC, "Generation", "DestinationService.cs")))
_PL = read(os.path.join(SRC, "Generation", "RoomLayoutPlanner.cs"))


def _planner_const(name):
    found = re.search(r"const\s+int\s+%s\s*=\s*(\d+)" % name, _PL)
    return int(found.group(1)) if found else None


def _conduits_needed(depth, mapw, margin, gap, mins, maxs, maxrooms):
    slots = max(mins, min(maxs, mins + max(0, depth - 1)))
    spacing = (mapw - margin * 2) // slots
    span = spacing - gap
    if span % 2:
        span -= 1
    span = max(8, span)
    order = []
    for row in range(slots):
        for col in range(slots):
            order.append((col if row % 2 == 0 else slots - 1 - col, row))
    chain = max(6, min(maxrooms, min(len(order), len(order) * 2 // 3)))
    rooms = [order[i] for i in range(chain)]

    def centre(index):
        return margin + spacing // 2 + spacing * index

    walk = set()
    for sx, sz in rooms:
        cx, cz = centre(sx), centre(sz)
        for x in range(cx - span // 2 + 1, cx + span // 2):
            for z in range(cz - span // 2 + 1, cz + span // 2):
                walk.add((x, z))
    for i in range(1, chain):
        a, b = rooms[i - 1], rooms[i]
        ax, az, bx, bz = centre(a[0]), centre(a[1]), centre(b[0]), centre(b[1])
        if az == bz:
            for x in range(min(ax, bx), max(ax, bx) + 1):
                for dz in (-1, 0, 1):
                    walk.add((x, az + dz))
        else:
            for z in range(min(az, bz), max(az, bz) + 1):
                for dx in (-1, 0, 1):
                    walk.add((ax + dx, z))
    # One lamp per room plus a heater, and then the same again to stand in for whatever the
    # depth-scaled dressing adds. If it fits at double, it fits.
    consumers = [(centre(sx), centre(sz) + 2) for sx, sz in rooms]
    consumers.append((centre(rooms[0][0]) - 2, centre(rooms[0][1])))
    consumers += [(centre(sx) + 3, centre(sz) - 3) for sx, sz in rooms]
    wired = set([(centre(rooms[0][0]) + 2, centre(rooms[0][1]))])
    for target in consumers:
        if target in wired:
            continue
        previous = {}
        pending = _deque(wired)
        seen = set(wired)
        hit = None
        while pending:
            cell = pending.popleft()
            if cell == target:
                hit = cell
                break
            for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (cell[0] + step[0], cell[1] + step[1])
                if near in seen or near not in walk:
                    continue
                seen.add(near)
                previous[near] = cell
                pending.append(near)
        if hit is None:
            continue
        cell = hit
        while cell in previous:
            wired.add(cell)
            cell = previous[cell]
    return chain, len(wired)


_margin = _planner_const("Margin")
_gap = _planner_const("SlotGap")
_mins = _planner_const("MinSlotsPerAxis")
_maxs = _planner_const("MaxSlotsPerAxis")
_maxrooms = _planner_const("MaxRooms")
_readable = (_CAP is not None and _MAPW is not None and None not in
             (_margin, _gap, _mins, _maxs, _maxrooms))
check("every constant this sizing needs was found in the source",
      _readable,
      "-- a renamed constant must fail here rather than be silently skipped, or this claim would "
      "pass by modelling nothing")

if _readable:
    _cap = int(_CAP.group(1))
    _worst = 0
    # Depth 1 and the deepest band only. Depth 1 is the trap -- it fitted under the old cap by
    # forty cells, so the first level a player opened would have generated and every one below it
    # died. The deepest band is the worst case. The depths between are interpolations, and each
    # one costs a flood fill on every single plant run.
    print("     depth rooms  conduits needed  cap")
    for _depth in (1, _maxs - _mins + 1):
        _rooms, _needed = _conduits_needed(_depth, int(_MAPW.group(1)), _margin, _gap,
                                           _mins, _maxs, _maxrooms)
        _worst = max(_worst, _needed)
        print("     %5d %5d %16d %4d" % (_depth, _rooms, _needed, _cap))
    check("THE CONDUIT CAP FITS EVERY DEPTH, WITH DOUBLE THE CONSUMERS",
          _worst <= _cap,
          "-- worst case %d against a cap of %d. 512 was sized for 60x60: depth 1 fitted under it "
          "by forty cells and every level below died, which is the worst failure mode there is "
          "because it looks fixed" % (_worst, _cap))
    check("and it is not absurdly oversized either",
          _cap <= _worst * 6,
          "-- headroom is %.1fx. A cap so large it can never bind is not a cap"
          % (float(_cap) / max(1, _worst)))

check("NOTHING IN THE WIRING CAN DESTROY A COORDINATE ANY MORE",
      "if (!destination.IsValid) { return new List<IntVec3>(); }" in genstep
      and "if (!previous.TryGetValue(cursor, out predecessor)) { return new List<IntVec3>(); }"
      in genstep,
      "-- a consumer the conduit cannot reach is a dark corner. Both of these threw, and a throw "
      "here destroyed the whole place: the exact defect that cost the fifth and sixth launches")

check("the known-consumer routes use the non-throwing placement too",
      "SpawnNativeConduit(" not in
      genstep.split("foreach (CellRect consumer in consumerFootprints)")[1].split("}")[0]
      .replace("TrySpawnNativeConduit(", ""),
      "-- the throwing form is now reserved for the generator's own footprint, where a failure "
      "really is a generator fault")

check("and both loops stop at the cap rather than passing it",
      genstep.count("if (wiredCells.Count >= MaxNativePowerConduits) { break; }") >= 2,
      "-- stopping the wiring is the degradation; throwing was the bug")

# ------------------------------------------- furniture must never cost a level
# **A FURNITURE PLACEMENT RULE STOPPED A LEVEL BEING BUILT.** `Place` refused any cell whose
# footprint had an edifice within one, and the room's wall, its pillar lattice, the rock in its
# shaped corners, the lamp on every pillar and every fixture already placed are all edifices --
# on top of the three-cell route cross, which `Populate` reserves outright. A room could be left
# with one placeable cell, the first fixture took it, and the second threw out of
# `GenStep.Generate`. The owner got a Backrooms map with no content and a door that was never
# marked: *"i see the backrooms is there but the gate natural door is not"*.
check("THE WALKABLE MARGIN IS A PREFERENCE, NOT A REQUIREMENT",
      "private static IntVec3 FixtureCell(" in content
      and "IntVec3 withoutMargin = IntVec3.Invalid;" in content
      and "if (!withoutMargin.IsValid) { withoutMargin = cell; }" in content
      and "return withoutMargin;" in content
      # **THE BRANCH, not just the machinery it feeds.** A plant restored the hard `continue` and
      # left every line above it untouched, so the fallback still existed and was simply never
      # reached. Computing a value and using it are two different facts, for the fourth time.
      and "if (!footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
      in content
      and "{ return cell; }" in content
      and "if (footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
      not in content,
      "-- the reserved route cross is what keeps a room walkable, and it is reserved separately "
      "and unconditionally. A fixture with no margin is a fixture against a wall")

check("and ONE function finds the cell, for every caller",
      content.count("FixtureCell(map, room, reserved, thing, rotation, preferred)") == 2
      and content.count("OrderBy(c => c.DistanceToSquared(preferred))") == 1,
      "-- `TryPlace` kept its own copy of the search loop. Two derivations of one rule is the "
      "defect that cost this project thirty-nine checkpoints")

check("ONLY THE LANDMARK IS REQUIRED; EVERY OTHER FIXTURE IS SCENERY",
      "private static Thing Decorate(" in content
      and "count, false);" in content
      and "count, true);" in content
      and 'if (required)' in content
      and content.count("Decorate(map, room, coordinate,") >= 12,
      "-- `ValidatePlacedLayout` requires exactly one clue per room and the clue is the "
      "landmark, so that one is refused loudly. A second stool is a second stool, and "
      "`DressRoom` four lines below already said so: *\"failing generation because a decorative "
      "shelf had nowhere to go would take a working coordinate away from a player over "
      "scenery\"*")

check("and no family fixture other than a landmark still throws",
      content.count("landmark = Place(map, room, coordinate,") == 7
      and BARE_FIXTURE not in content
      and "{ Place(map, room, coordinate," not in content,
      "-- scoped to a BARE statement, because the absence of "
      "`Place(map, room, coordinate, \"Shelf\"...)` is NOT the claim: that string is a substring "
      "of `service_passage`'s own landmark, and the first draft of this claim refused correct "
      "code because of it. Thirty-seventh instance of the scoping trap. What has to be gone is a "
      "family fixture whose result nobody keeps -- those are the twelve that could throw and had "
      "no reason to")

check("A LANDMARK REFUSAL SAYS WHICH ROOM",
      "No cell for the landmark " in content
      and "room.familyId" in content and "room.width" in content,
      "-- last time this threw, the log carried the method and a key and nothing else, so the "
      "room had to be reasoned about from the arithmetic of every room it could have been")

check("and the route cross is derived in exactly one place",
      "internal static bool OnRouteCross(" in content
      and "if (OnRouteCross(room, cell)) { reserved.Add(cell); } }" in content
      and "Math.Abs(cell.x - center.x) <= 1 || Math.Abs(cell.z - center.z) <= 1" in content,
      "-- the layout probe counts placeable cells against it, so a second copy of the rule would "
      "let the probe and the generator disagree about what is reserved. **These two claims were "
      "deleted by a fix script that sliced between two anchors without reading what was between "
      "them**, and the plant suite is what noticed")

# -------------------------------------------------- two transmitters on one cell
# Core refuses the second transmitter on a cell and leaves its own bookkeeping inconsistent, so
# `PowerConnectionMaker.TryConnectToAnyPowerNet` threw out of `Map.FinalizeInit` and then out of
# every Update for the rest of the session. Hundreds of them in the owner's log.
check("A CONDUIT IS NEVER PUT ON A CELL THAT ALREADY TRANSMITS",
      "private static bool AlreadyTransmits(Map map, IntVec3 cell)" in genstep
      and "thing.def.EverTransmitsPower" in genstep
      and genstep.count("if (AlreadyTransmits(map, cell)) { return; }") == 2,
      "-- BOTH spawn paths, because `wiredCells` is this generator's own bookkeeping and cannot "
      "see a transmitter somebody else put there. Several mods in the owner's profile attach a "
      "hidden conduit under a powered building, and the lamps this generator puts on every "
      "pillar are powered buildings")

check("and it asks Core's own property rather than naming a def",
      "List<Thing> things = cell.GetThingList(map);" in genstep
      and 'GetNamedSilentFail("HiddenConduit")' in genstep,
      "-- `EverTransmitsPower` is the same property `PowerNetManager` registers on, so this "
      "cannot disagree with the thing that refuses the duplicate. The point is that we did not "
      "put the other transmitter there, so we cannot know its def")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a coordinate has materials of its own, its inhabitants are tiered by depth "
      "and wealth, and its floors were always ordinary")
