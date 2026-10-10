# -*- coding: utf-8 -*-
"""Light and dress the hallways, so a corridor carries what a room carries.

`BuildCorridors` now reports the cells one in from each corridor wall, and **nothing was using
them** -- which is the defect this run has produced five times already: computing a value
correctly and using it are two different facts. So the list is threaded out of `BuildShell` and
spent.

Owner: *"rooms as halways with the exact shit thats in the rooms"*.

A lamp every few cells, and a fixture here and there from the same families the rooms use. Never
on the centre line -- `BuildCorridors` does not report it -- so the route through a corridor is as
clear as a room's reserved cross, and a corridor only gets anything at all when it is wide enough
to have a side.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

EDITS = [
    # BuildShell hands the corridor sides back to Generate.
    (u"""        internal static void BuildShell(Map map, CoordinateRecord coordinate, TerrainDef concrete,
            TerrainDef voidFloor, ThingDef wallDef, ThingDef wallStuff)""",
     u"""        /// <summary>
        /// Carve the coordinate and return the cells along its corridor walls, so the hallways
        /// can be lit and dressed like the rooms they join.
        /// </summary>
        internal static List<IntVec3> BuildShell(Map map, CoordinateRecord coordinate,
            TerrainDef concrete,
            TerrainDef voidFloor, ThingDef wallDef, ThingDef wallStuff)"""),

    (u"""            PlaceNativeDoors(coordinate.Rooms, map);
        }""",
     u"""            PlaceNativeDoors(coordinate.Rooms, map);
            return corridorSides;
        }"""),

    (u"                BuildShell(map, coordinate, concrete, voidFloor, wallDef, wallStuff);",
     u"                List<IntVec3> corridorSides = BuildShell(map, coordinate, concrete,\n"
     u"                    voidFloor, wallDef, wallStuff);"),

    # Spent right after the pillar lamps, which is where lightDef and placedLights live.
    (u"""                SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted,
                    reservedProviderCells, placedLights);""",
     u"""                SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted,
                    reservedProviderCells, placedLights);

                // **AND THE HALLWAYS GET THE SAME TREATMENT.** Owner: *"rooms as halways with
                // the exact shit thats in the rooms"*. A corridor that is lit and furnished is
                // part of the building; one that is neither is a tunnel between beads, which is
                // what *"a string of pears"* was describing.
                DressCorridors(map, coordinate, corridorSides, lightDef, placedLights,
                    reservedProviderCells);"""),
]

TAIL_ANCHOR = u"""        /// <summary>
        /// Give this lamp a tone of its own."""

TAIL = u'''        /// <summary>How many cells of corridor wall per lamp.</summary>
        private const int CorridorLampSpacing = 7;

        /// <summary>How many cells of corridor wall per fixture.</summary>
        private const int CorridorFixtureSpacing = 11;

        /// <summary>
        /// Light and furnish the hallways, against their walls only.
        ///
        /// Owner: *"i see the whole map is almost like a string of pears. when it should just be
        /// basicly \\"rooms\\" as halways with the exact shit thats in the rooms"*.
        ///
        /// `BuildCorridors` reports the cells one in from each corridor wall and **never the
        /// centre line**, so everything placed here is against a wall and the route through the
        /// corridor stays as clear as a room's reserved cross. A three-cell corridor has no side
        /// to speak of and gets nothing; a five-cell one does.
        ///
        /// The fixtures are the families the rooms already use, so a hallway reads as more of the
        /// same building rather than as a themed set of its own -- which is the whole of the
        /// owner's correction.
        ///
        /// Silent on every failure, like `DressRoom`: a corridor that could not take a lamp is a
        /// dark stretch of corridor, and a coordinate must never be lost over scenery.
        /// </summary>
        private static void DressCorridors(Map map, CoordinateRecord coordinate,
            List<IntVec3> sides, ThingDef lightDef, List<Thing> placedLights,
            HashSet<IntVec3> reserved)
        {
            if (map == null || coordinate == null || sides == null || sides.Count == 0) { return; }
            // Ordered, so a regenerated coordinate dresses its corridors identically.
            sides.Sort(delegate (IntVec3 left, IntVec3 right)
            {
                if (left.z != right.z) { return left.z - right.z; }
                return left.x - right.x;
            });

            var fixtures = new List<ThingDef>();
            foreach (string name in new[] { "Shelf", "Stool", "PlantPot", "StandingLamp" })
            {
                ThingDef candidate = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (candidate != null) { fixtures.Add(candidate); }
            }

            for (int index = 0; index < sides.Count; index++)
            {
                IntVec3 cell = sides[index];
                if (!cell.InBounds(map) || reserved.Contains(cell)) { continue; }
                if (!cell.Standable(map) || cell.GetEdifice(map) != null) { continue; }
                if (cell.GetFirstItem(map) != null) { continue; }

                if (lightDef != null && index % CorridorLampSpacing == 0)
                {
                    Thing lamp = MakeBuilding(lightDef,
                        lightDef.MadeFromStuff ? ThingDefOf.Steel : null);
                    if (lamp == null) { continue; }
                    lamp.SetFaction(Faction.OfPlayer);
                    GenSpawn.Spawn(lamp, cell, map, Rot4.North);
                    if (!lamp.Spawned || lamp.Map != map) { continue; }
                    reserved.Add(cell);
                    placedLights.Add(lamp);
                    continue;
                }

                if (fixtures.Count == 0 || index % CorridorFixtureSpacing != 0) { continue; }
                int roll = DestinationService.StableHash(coordinate.Seed,
                    "corridorfixture:" + cell.x + "," + cell.z, 1);
                if (roll < 0) { roll = ~roll; }
                ThingDef definition = fixtures[roll % fixtures.Count];
                // Single-cell only: a wider footprint against a corridor wall is how a route
                // stops being a route.
                if (definition.size.x != 1 || definition.size.z != 1) { continue; }
                Thing fixture = ThingMaker.MakeThing(definition,
                    CoordinateMaterials.StuffFor(definition, coordinate, roll));
                if (fixture == null) { continue; }
                fixture.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(fixture, cell, map, Rot4.North);
                if (!fixture.Spawned || fixture.Map != map) { continue; }
                reserved.Add(cell);
                if (definition == lightDef) { placedLights.Add(fixture); }
            }
        }

''' + TAIL_ANCHOR

text = io.open(GEN, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:70]))
if text.count(TAIL_ANCHOR) != 1:
    problems.append("%d of TAIL_ANCHOR" % text.count(TAIL_ANCHOR))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
text = text.replace(TAIL_ANCHOR, TAIL, 1)
io.open(GEN, "w", encoding="utf-8", newline="").write(text)
print("corridors are lit and dressed, and the reported cells are spent")
