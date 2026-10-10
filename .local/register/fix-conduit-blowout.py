# -*- coding: utf-8 -*-
"""The sixth launch: the coordinate still did not generate, and the cause is mine.

Owner, verbatim: *"its not blue!!! it doesnt have a light aura, and it in no way is a portal to
the back rooms.. wtf!!! im getting tired of this shit..."*

They are right, and the log says why. `SpawnNativeConduit` threw
`RR_Generation_ContentPlacementFailed`, so `MarkLayoutReady` never ran, so `SoloGroupOpening`
stopped at step 2 again and the Store's back door was never marked. **A door that was never marked
is an ordinary steel door.** Everything the owner reports follows from that one throw.

THE CAUSE, measured rather than guessed. `SpawnNativePowerNetwork` carpeted every powered room
with conduit:

    poweredRoomCoverage = rooms.Where(service_passage or utility_room)
                               .Select(room.Bounds.ContractedBy(1))

At 12x12 rooms that was 100 cells and nobody noticed. At depth 1 a service_passage is **60x80**,
so `ContractedBy(1)` is **4,524 cells** -- against `MaxNativePowerConduits = 512`. **An eightfold
blowout on the first powered room**, which means no 300x300 coordinate could ever generate. The
carpet was a trick sized for small rooms and the 300x300 change invalidated it.

THE FIX, and it is better than raising the cap. The carpet existed for one reason, stated in its
own comment: `RoomContentBuilder` adds another lamp to every powered room AFTER the grid is laid,
so the room was pre-wired to catch it. Wiring 4,524 cells to catch one lamp is the wrong shape at
any size.

So: wire the generator and the KNOWN consumers as before, then **after content placement, connect
whatever else turned up.** `ValidateNativePowerNetwork` already sweeps every `CompPowerTrader` on
the map to find them -- this uses the same sweep to *fix* them instead of only reporting them.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

text = io.open(GEN, encoding="utf-8").read()

EDITS = [
    # 1. Stop carpeting. Return the wired set so a later pass can route from it.
    ("""        private static void SpawnNativePowerNetwork(Map map, TerrainDef voidFloor, ThingDef conduitDef,
            CellRect generatorFootprint, IEnumerable<CellRect> consumerFootprints,
            IEnumerable<CellRect> poweredRoomCoverage)
        {""",
     """        /// <summary>
        /// Conduit from the generator to each known consumer, and nothing more.
        ///
        /// **This used to carpet every powered room with conduit, and that is what stopped every
        /// 300x300 coordinate from generating.** The carpet existed for one stated reason:
        /// `RoomContentBuilder` adds another lamp to each powered room *after* the grid is laid,
        /// so the room was pre-wired to catch it. At 12x12 rooms that was about a hundred cells.
        /// At depth 1 a service_passage is 60x80, so `ContractedBy(1)` is **4,524 cells** against
        /// a `MaxNativePowerConduits` cap of **512** — an eightfold blowout on the first powered
        /// room, every time.
        ///
        /// Wiring four thousand cells to catch one lamp is the wrong shape at any size. The lamp
        /// is picked up by <see cref="ConnectStrayConsumers"/> after content placement instead.
        ///
        /// Returns the wired set, so that later pass can route from the grid that exists.
        /// </summary>
        private static HashSet<IntVec3> SpawnNativePowerNetwork(Map map, TerrainDef voidFloor,
            ThingDef conduitDef, CellRect generatorFootprint, IEnumerable<CellRect> consumerFootprints)
        {"""),

    ("""            // RoomContentBuilder adds another Core lamp to every service/utility room after this
            // method. Wire each such room first so those later loads join the real native network.
            foreach (IntVec3 cell in poweredRoomCoverage.SelectMany(room => room.Cells)
                .Distinct().OrderBy(value => value.x).ThenBy(value => value.z))
            { SpawnNativeConduit(map, voidFloor, conduitDef, cell, wiredCells); }
        }""",
     """            return wiredCells;
        }

        /// <summary>
        /// Connect anything that draws power and is not on the generator's net yet.
        ///
        /// Run **after** `RoomContentBuilder.Populate`, because that is when the lamps and benches
        /// the archetype dressing places actually exist. This replaces pre-wiring whole rooms on
        /// the chance that something would land in them.
        ///
        /// Uses the same map-wide `CompPowerTrader` sweep `ValidateNativePowerNetwork` uses to
        /// *detect* the problem — so the thing that reports a stray consumer and the thing that
        /// fixes one agree by construction rather than by two people remembering the same rule.
        ///
        /// **Never throws.** A lamp that cannot be reached is a dark corner; the validation below
        /// reports it and the coordinate still exists. Losing the whole place over a conduit is
        /// what this checkpoint is fixing.
        /// </summary>
        private static void ConnectStrayConsumers(Map map, TerrainDef voidFloor, ThingDef conduitDef,
            HashSet<IntVec3> wiredCells, Thing generator)
        {
            CompPowerPlant plant = generator == null ? null : generator.TryGetComp<CompPowerPlant>();
            if (plant == null || wiredCells == null) { return; }
            // Ordered, so the routing is the same on a regenerated coordinate.
            List<Thing> consumers = map.listerThings.AllThings
                .Where(thing => thing != null && thing.Spawned && thing.Map == map &&
                    thing.TryGetComp<CompPowerTrader>() != null)
                .OrderBy(thing => thing.Position.x).ThenBy(thing => thing.Position.z)
                .ThenBy(thing => thing.def.defName, StringComparer.Ordinal)
                .ToList();
            for (int index = 0; index < consumers.Count; index++)
            {
                Thing consumer = consumers[index];
                CompPowerTrader power = consumer.TryGetComp<CompPowerTrader>();
                if (power == null || power.PowerNet == plant.PowerNet) { continue; }
                if (wiredCells.Count >= MaxNativePowerConduits) { return; }
                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells,
                    consumer.OccupiedRect());
                for (int step = 0; step < route.Count; step++)
                {
                    if (wiredCells.Count >= MaxNativePowerConduits) { return; }
                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);
                }
                map.powerNetManager.UpdatePowerNetsAndConnections_First();
            }
        }

        /// <summary>
        /// A conduit where one will fit, and silence where it will not.
        ///
        /// The throwing form is kept for the generator's own footprint and the known consumer
        /// routes, where a failure really is a generator fault. This form is for the opportunistic
        /// pass, where a cell that cannot take a conduit is a dark corner rather than a broken
        /// coordinate.
        /// </summary>
        private static void TrySpawnNativeConduit(Map map, TerrainDef voidFloor, ThingDef conduitDef,
            IntVec3 cell, HashSet<IntVec3> wiredCells)
        {
            if (!cell.InBounds(map) || map.terrainGrid.TerrainAt(cell) == voidFloor) { return; }
            if (!wiredCells.Add(cell)) { return; }
            Thing conduit = MakeBuilding(conduitDef, null);
            conduit.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(conduit, cell, map, Rot4.North);
        }"""),

    # 2. The call site: no coverage argument, keep the wired set.
    ("""                List<CellRect> poweredRoomCoverage = coordinate.Rooms
                    .Where(room => room.familyId == "service_passage" || room.familyId == "utility_room")
                    .Select(room => room.Bounds.ContractedBy(1)).ToList();
                SpawnNativePowerNetwork(map, voidFloor, conduitDef,
                    GenAdj.OccupiedRect(generatorCell, Rot4.North, generatorDef.size), consumerFootprints,
                    poweredRoomCoverage);""",
     """                HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(map, voidFloor, conduitDef,
                    GenAdj.OccupiedRect(generatorCell, Rot4.North, generatorDef.size), consumerFootprints);"""),

    # 3. The stray pass, after content placement and before validation.
    ("""                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);
                // Native spawn notifications are queued; rebuild connections now without ticking
                // the power simulation so readiness checks see the actual shared grid.
                map.powerNetManager.UpdatePowerNetsAndConnections_First();""",
     """                RoomContentBuilder.Populate(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);
                // Native spawn notifications are queued; rebuild connections now without ticking
                // the power simulation so readiness checks see the actual shared grid.
                map.powerNetManager.UpdatePowerNetsAndConnections_First();
                // Whatever the dressing just placed that draws power, wired now that it exists.
                // This is what replaced pre-wiring whole rooms on the chance something would land
                // in them -- see SpawnNativePowerNetwork.
                ConnectStrayConsumers(map, voidFloor, conduitDef, wiredCells, generator);
                map.powerNetManager.UpdatePowerNetsAndConnections_First();"""),
]

problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(GEN, "w", encoding="utf-8", newline="").write(text)
print("conduit blowout fixed: %d edits" % len(EDITS))
