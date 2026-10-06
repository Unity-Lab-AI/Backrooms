using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// The rock a coordinate is carved out of, made worth digging.
    ///
    /// ## Owner direction, 2026-10-03, verbatim
    ///
    /// *"where there is mountain walls and no rooms areas minable need to have resources that you
    /// can mine like steel gold plasteel, gems, all of them, even underground resources that u can
    /// use deep drill with and chemfuel"*
    ///
    /// and, the same day:
    ///
    /// *"and we should have doors that lead no where but to an ore or gem vein, and veins leading
    /// to other rooms so insentive to mine things out to find isolated undiscorvered rooms when
    /// mining and deconsturcting wals and sucvh so u can find back to back rooms"*
    ///
    /// and, answering the density fork: *"option 2 but a bit more than vanilla like 3x more
    /// deposites than a default map"*.
    ///
    /// ## Why this cannot break a level, which is the whole reason it is shaped this way
    ///
    /// **Every cell this touches is rock before and rock after.** A vein replaces natural rock
    /// with ore-bearing natural rock; it never carves, never places a wall, never clears one. So
    /// no route changes, no room's doorway is affected, and `CandidateIsSafe`'s reachability proof
    /// is as true after this runs as before it. That is a deliberate design choice rather than a
    /// happy accident: the unreachable-room defect class cost this project thirty-nine checkpoints,
    /// and a feature that threads paths across the whole map is exactly the kind that would
    /// reintroduce it. **Routing freely is safe precisely because nothing here opens anything.**
    ///
    /// It runs **after** the rooms and corridors are carved, so the cells it can see are the cells
    /// that stayed rock.
    ///
    /// ## Nothing is named
    ///
    /// The ore list is read out of the game — every def that is a resource rock — rather than
    /// written down here. That covers the owner's *"all of them"*, it picks up whatever the other
    /// 294 mods add without an adapter, and it is a requirement of the standing *"rework mod to
    /// not need any depeancie mods"* direction: a hardcoded `MineableJade` would be this mod
    /// asserting what the game contains.
    /// </summary>
    internal static class OreVeinBuilder
    {
        /// <summary>
        /// How many times Core's own scatter density a coordinate gets.
        ///
        /// Owner: *"a bit more than vanilla like 3x more deposites than a default map"*. The
        /// multiplier is the owner's number; the thing it multiplies is read from Core at runtime
        /// by <see cref="CoreLumpsPer10kCells"/>, so this is the only figure here that is ours.
        /// </summary>
        internal const int VanillaDensityMultiple = 3;

        /// <summary>
        /// The density used when Core's own figure cannot be read for a map, in lumps per ten
        /// thousand cells.
        ///
        /// **A stated fallback rather than a silent one.** If this is ever used, the log says so
        /// once: a density that quietly stopped matching Core would be a number nobody could
        /// check, which is the defect class this file's own header warns about.
        ///
        /// **Ten is also Core's own default**, which is why the fallback being used on every map
        /// ever generated — see <see cref="CoreLumpsPer10kCells"/> — never looked like anything.
        /// </summary>
        internal const float FallbackLumpsPer10kCells = 10f;

        /// <summary>Cells in one scattered lump, which is what makes it read as a deposit.</summary>
        internal const int SmallestLump = 3;
        internal const int LargestLump = 10;

        /// <summary>How wide a vein is. One cell reads as a scratch; three reads as a seam.</summary>
        internal const int VeinHalfWidth = 1;

        /// <summary>
        /// How far a door-onto-nothing's vein reaches into the rock.
        ///
        /// Owner: *"doors that lead no where but to an ore or gem vein"*. Long enough that opening
        /// the door and digging is a decision, short enough that it is not a corridor.
        /// </summary>
        internal const int FalseDoorVeinReach = 14;

        /// <summary>
        /// Place the veins, then the scatter, then the deep resources.
        ///
        /// Order matters only for reading: a vein laid first keeps one ore along its whole length,
        /// which is what makes it legible as a vein rather than as luck.
        /// </summary>
        internal static void Place(Map map, CoordinateRecord coordinate, int depth)
        {
            if (map == null || coordinate == null || coordinate.Rooms == null) { return; }
            List<ThingDef> ores = ResourceRocks();
            if (ores.Count == 0) { return; }

            var oreCells = new HashSet<IntVec3>();
            PlaceVaultVeins(map, coordinate, ores, oreCells);
            PlaceFalseDoorVeins(map, coordinate, ores, oreCells);
            PlaceBetweenRoomVeins(map, coordinate, ores, oreCells);
            PlaceScatteredLumps(map, coordinate, ores, oreCells);
            PlaceDeepResources(map, coordinate, depth);
        }

        /// <summary>
        /// Every def in the loaded game that is a rock with a resource in it.
        ///
        /// Read rather than listed, for the reasons in the type summary.
        /// </summary>
        internal static List<ThingDef> ResourceRocks()
        {
            var found = new List<ThingDef>();
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def == null || def.building == null) { continue; }
                if (!def.building.isResourceRock || def.building.mineableThing == null) { continue; }
                if (!def.building.isNaturalRock) { continue; }
                found.Add(def);
            }
            found.SortBy(def => def.defName);
            return found;
        }

        /// <summary>
        /// Core's own scatter density for this map, in lumps per ten thousand cells.
        ///
        /// **Read from the game's own arithmetic, not copied.** The owner asked for three times
        /// vanilla, and the only honest reading of *vanilla* is whatever Core computes for itself —
        /// a constant here would be this mod's memory of a number Ludeon can change.
        ///
        /// ## THE SCAN THIS REPLACES NEVER WORKED, ON ANY PROFILE
        ///
        /// It walked `DefDatabase&lt;GenStepDef&gt;` looking for a step whose `genStep` is a
        /// `GenStep_ScatterLumpsMineable`, found none, and logged the stated fallback. The queue row
        /// recorded that as a mystery worth investigating on the owner's 294-mod profile — *"worth
        /// finding out why the scan missed it"*.
        ///
        /// **It missed nothing. There is no such def.** Measured out of the installed game: every
        /// `GenStepDef` in Core and all five expansions was enumerated, and the string
        /// `ScatterLumpsMineable` appears in **zero** def files. The class exists in the assembly and
        /// is **constructed in code**: `GenStep_RocksFromGrid.Generate` makes one, sets
        /// `countPer10kCellsRange` from `GetResourceBlotchesPer10KCellsForMap(map)`, and runs it. So
        /// the fallback was used on every map this mod has ever generated, including on a pure-Core
        /// install, and the log line was never evidence about the mod list.
        ///
        /// **The fallback was ten and Core's own default is ten**, which is why nothing ever looked
        /// wrong. A number that is right by coincidence is still a number nobody checked.
        ///
        /// ## And the real source is better than the one that was wanted
        ///
        /// `GetResourceBlotchesPer10KCellsForMap` is public, static, and reads the **tile's
        /// hilliness**: 4 flat, 8 small hills, 11 large hills, 15 mountainous, 16 impassable. So a
        /// coordinate now carries the ore density of the tile it sits under, the way an ordinary map
        /// does, instead of one figure everywhere. The owner's x3 multiplies that.
        ///
        /// **Guarded, because generation may never fail.** A map with no valid world tile throws on
        /// `TileInfo`, and a coordinate is reached through paths that do not all guarantee one. The
        /// stated fallback stays for exactly that case, and it says so once.
        /// </summary>
        internal static float CoreLumpsPer10kCells(Map map)
        {
            if (map != null)
            {
                try
                {
                    float blotches = GenStep_RocksFromGrid.GetResourceBlotchesPer10KCellsForMap(map);
                    if (blotches > 0f) { return blotches; }
                }
                catch (System.Exception exception)
                {
                    // Reported rather than swallowed: a density nobody can check is the defect this
                    // whole method exists to avoid, and a silent catch would recreate it.
                    Log.Message("[Rimrooms][Generation] Core's own blotch density could not be read "
                        + "for this map (" + exception.GetType().Name + "); coordinate ore density "
                        + "falls back to " + FallbackLumpsPer10kCells + " lumps per 10k cells before "
                        + "the owner's x" + VanillaDensityMultiple + ".");
                    return FallbackLumpsPer10kCells;
                }
            }
            Log.Message("[Rimrooms][Generation] No map to read Core's blotch density from; "
                + "coordinate ore density falls back to " + FallbackLumpsPer10kCells
                + " lumps per 10k cells before the owner's x" + VanillaDensityMultiple + ".");
            return FallbackLumpsPer10kCells;
        }

        /// <summary>
        /// A vein from every sealed vault to the nearest room that has a way in.
        ///
        /// Owner: *"veins leading to other rooms so insentive to mine things out to find isolated
        /// undiscorvered rooms when mining and deconsturcting wals"*. **This is the vault's reason
        /// to exist being made findable.** A room with no doors that nothing points at is not a
        /// secret, it is a room nobody will ever stand in; a seam of gold running out of its wall
        /// is an invitation.
        /// </summary>
        private static void PlaceVaultVeins(Map map, CoordinateRecord coordinate,
            List<ThingDef> ores, HashSet<IntVec3> oreCells)
        {
            foreach (RoomRecord vault in coordinate.Rooms)
            {
                if (vault == null || vault.familyId != RoomLayoutPlanner.SealedFamily) { continue; }
                RoomRecord nearest = null;
                int best = int.MaxValue;
                foreach (RoomRecord other in coordinate.Rooms)
                {
                    if (other == null || other == vault) { continue; }
                    if (other.familyId == RoomLayoutPlanner.SealedFamily) { continue; }
                    int span = Math.Abs(other.Bounds.CenterCell.x - vault.Bounds.CenterCell.x)
                        + Math.Abs(other.Bounds.CenterCell.z - vault.Bounds.CenterCell.z);
                    if (span >= best) { continue; }
                    best = span;
                    nearest = other;
                }
                if (nearest == null) { continue; }
                int draw = DestinationService.StableHash(coordinate.Seed,
                    "vein:vault:" + vault.index, 1);
                if (draw < 0) { draw = ~draw; }
                CarveVein(map, vault.Bounds.CenterCell, nearest.Bounds.CenterCell,
                    PickOre(ores, draw), draw, oreCells);
            }
        }

        /// <summary>
        /// A vein behind every doorway that opens onto nothing.
        ///
        /// Owner: *"and we should have doors that lead no where but to an ore or gem vein"*. The
        /// doorway already exists — `RoomLayoutPlanner.FalseOpening` has been putting one wall in
        /// three on a wall with no link behind it, offset from the centre so it does not read as a
        /// corridor that failed to arrive. **What was behind it was plain rock, so it read as a
        /// mistake.** Now it reads as a find.
        /// </summary>
        private static void PlaceFalseDoorVeins(Map map, CoordinateRecord coordinate,
            List<ThingDef> ores, HashSet<IntVec3> oreCells)
        {
            foreach (RoomRecord room in coordinate.Rooms)
            {
                if (room == null) { continue; }
                CellRect bounds = room.Bounds;
                foreach (IntVec3 cell in bounds.EdgeCells)
                {
                    // The REAL doorways are the ones a corridor arrives at, and those have a route
                    // behind them already. Only an opening `FalseOpening` put there is a door onto
                    // rock, and asking it directly is what keeps this from guessing.
                    if (!RoomLayoutPlanner.FalseOpening(room, coordinate.Rooms, cell)) { continue; }
                    IntVec3 outward = OutwardFrom(bounds, cell);
                    if (outward == IntVec3.Invalid) { continue; }
                    int draw = DestinationService.StableHash(coordinate.Seed,
                        "vein:door:" + room.index + ":" + cell.x + "," + cell.z, 1);
                    if (draw < 0) { draw = ~draw; }
                    int reach = 4 + draw % FalseDoorVeinReach;
                    IntVec3 target = cell + new IntVec3(outward.x * reach, 0, outward.z * reach);
                    CarveVein(map, cell, target, PickOre(ores, draw), draw, oreCells);
                }
            }
        }

        /// <summary>
        /// A vein between two rooms that a corridor does NOT join.
        ///
        /// Owner: *"veins leading to other rooms ... so u can find back to back rooms"*. A vein
        /// between two linked rooms teaches nothing — the corridor already goes there. A vein
        /// between two rooms with no route between them is a shortcut the player makes with a
        /// pick, and it is the only thing in the generator that rewards tunnelling rather than
        /// walking.
        /// </summary>
        private static void PlaceBetweenRoomVeins(Map map, CoordinateRecord coordinate,
            List<ThingDef> ores, HashSet<IntVec3> oreCells)
        {
            IReadOnlyList<RoomRecord> rooms = coordinate.Rooms;
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null || room.links == null) { continue; }
                for (int other = index + 1; other < rooms.Count; other++)
                {
                    RoomRecord second = rooms[other];
                    if (second == null) { continue; }
                    if (room.links.Contains(second.index)) { continue; }
                    IntVec3 from = room.Bounds.CenterCell;
                    IntVec3 to = second.Bounds.CenterCell;
                    // Near neighbours only. A seam across half the map is a tunnel, not a vein,
                    // and the point is a shortcut between two places that nearly touch.
                    if (Math.Abs(from.x - to.x) > RoomLayoutPlanner.FurthestLinkedCentres ||
                        Math.Abs(from.z - to.z) > RoomLayoutPlanner.FurthestLinkedCentres)
                    { continue; }
                    int draw = DestinationService.StableHash(coordinate.Seed,
                        "vein:between:" + room.index + ":" + second.index, 1);
                    if (draw < 0) { draw = ~draw; }
                    if (draw % BetweenRoomVeinRarity != 0) { continue; }
                    CarveVein(map, from, to, PickOre(ores, draw), draw, oreCells);
                }
            }
        }

        /// <summary>How rare a vein between two unlinked rooms is.</summary>
        /// <remarks>
        /// One pair in four. Every near pair would seam the whole level and make digging the
        /// obvious way to travel, which would quietly replace the maze the corridors make.
        /// </remarks>
        internal const int BetweenRoomVeinRarity = 4;

        /// <summary>
        /// Core's scatter, at the owner's multiple of it.
        ///
        /// Lumps rather than cells, because a single ore cell reads as a glitch. The lump centre
        /// and its size both come from the coordinate's own seed, so a revisit finds the same
        /// deposits — which every other generated property here already guarantees and a player
        /// who left a half-mined seam behind will notice immediately if it does not.
        /// </summary>
        private static void PlaceScatteredLumps(Map map, CoordinateRecord coordinate,
            List<ThingDef> ores, HashSet<IntVec3> oreCells)
        {
            float per10k = CoreLumpsPer10kCells(map) * VanillaDensityMultiple;
            int cells = map.Size.x * map.Size.z;
            int lumps = (int)(per10k * cells / 10000f);
            if (lumps < 1) { return; }
            for (int index = 0; index < lumps; index++)
            {
                int draw = DestinationService.StableHash(coordinate.Seed, "lump:" + index, 1);
                if (draw < 0) { draw = ~draw; }
                var centre = new IntVec3(draw % map.Size.x, 0, (draw / 31) % map.Size.z);
                if (!IsPlainRock(map, centre)) { continue; }
                ThingDef ore = PickOre(ores, draw / 7);
                int size = SmallestLump + (draw / 11) % (LargestLump - SmallestLump + 1);
                GrowLump(map, centre, ore, size, draw, oreCells);
            }
        }

        /// <summary>
        /// Deep resources under the coordinate, chemfuel among them.
        ///
        /// Owner: *"even underground resources that u can use deep drill with and chemfuel"*.
        /// **This is a different system from surface ore in Core and had to be treated as one.**
        /// A deep deposit is not a rock at all — it is a count in `Map.deepResourceGrid`, read by
        /// the deep drill and invisible until a ground-penetrating scanner finds it. So nothing
        /// above this method would ever have produced one, however much ore it placed.
        ///
        /// The candidates are every def Core marks as deep-drillable, which is where chemfuel
        /// comes from without naming it: `deepCommonality` is the game's own statement about what
        /// can be drilled, and reading it means a profile mod's deep resource is included too.
        /// </summary>
        private static void PlaceDeepResources(Map map, CoordinateRecord coordinate, int depth)
        {
            var candidates = new List<ThingDef>();
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def != null && def.deepCommonality > 0f) { candidates.Add(def); }
            }
            if (candidates.Count == 0) { return; }
            candidates.SortBy(def => def.defName);

            // Deeper coordinates hold more, which is the same curve everything else here follows
            // and is what makes living down there viable: the standing owner condition is that
            // *"a solo group has ability to build and get supplies on backrroms instances"*.
            int deposits = DeepDepositsPerCoordinate + depth;
            for (int index = 0; index < deposits; index++)
            {
                int draw = DestinationService.StableHash(coordinate.Seed, "deep:" + index, depth);
                if (draw < 0) { draw = ~draw; }
                ThingDef resource = PickDeep(candidates, draw);
                if (resource == null) { continue; }
                var centre = new IntVec3(draw % map.Size.x, 0, (draw / 37) % map.Size.z);
                int span = resource.deepLumpSizeRange.min
                    + draw % Math.Max(1, resource.deepLumpSizeRange.max - resource.deepLumpSizeRange.min + 1);
                int countPerCell = Math.Max(1, resource.deepCountPerCell);
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(centre, Math.Max(1, span) / 2f, true))
                {
                    if (!cell.InBounds(map)) { continue; }
                    map.deepResourceGrid.SetAt(cell, resource, countPerCell);
                }
            }
        }

        /// <summary>Deep deposits a coordinate carries before depth adds to it.</summary>
        internal const int DeepDepositsPerCoordinate = 4;

        /// <summary>
        /// One vein, from somewhere to somewhere, as an elbow through the rock.
        ///
        /// **It only ever replaces plain natural rock.** Floor, walls, doors, ore already placed
        /// and the rock left standing inside a room are all skipped, so a vein can be routed
        /// anywhere at all without a safety argument — which is the property that makes this whole
        /// file cheap. A vein that runs into a room simply stops being drawn there and picks up on
        /// the far side, which reads exactly as a seam the builders cut through.
        /// </summary>
        private static void CarveVein(Map map, IntVec3 from, IntVec3 to, ThingDef ore, int draw,
            HashSet<IntVec3> oreCells)
        {
            if (ore == null) { return; }
            bool xFirst = (draw / 3) % 2 == 0;
            var corner = xFirst ? new IntVec3(to.x, 0, from.z) : new IntVec3(from.x, 0, to.z);
            StreakBetween(map, from, corner, ore, oreCells);
            StreakBetween(map, corner, to, ore, oreCells);
        }

        private static void StreakBetween(Map map, IntVec3 from, IntVec3 to, ThingDef ore,
            HashSet<IntVec3> oreCells)
        {
            int steps = Math.Max(Math.Abs(to.x - from.x), Math.Abs(to.z - from.z));
            if (steps == 0) { steps = 1; }
            int stepX = to.x == from.x ? 0 : (to.x > from.x ? 1 : -1);
            int stepZ = to.z == from.z ? 0 : (to.z > from.z ? 1 : -1);
            for (int step = 0; step <= steps; step++)
            {
                var along = new IntVec3(from.x + stepX * step, 0, from.z + stepZ * step);
                for (int offset = -VeinHalfWidth; offset <= VeinHalfWidth; offset++)
                {
                    // Thickened across the run rather than along it, so the seam has a width.
                    var cell = stepX == 0
                        ? new IntVec3(along.x + offset, 0, along.z)
                        : new IntVec3(along.x, 0, along.z + offset);
                    SetOre(map, cell, ore, oreCells);
                }
            }
        }

        private static void GrowLump(Map map, IntVec3 centre, ThingDef ore, int size, int draw,
            HashSet<IntVec3> oreCells)
        {
            int placed = 0;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(centre, Math.Max(1f, size / 2f), true))
            {
                if (placed >= size) { return; }
                if (SetOre(map, cell, ore, oreCells)) { placed++; }
            }
        }

        /// <summary>
        /// Swap this cell's plain rock for ore-bearing rock, and report whether it took.
        ///
        /// The guard is the whole safety story: anything that is not plain natural rock is left
        /// exactly as it is.
        /// </summary>
        private static bool SetOre(Map map, IntVec3 cell, ThingDef ore, HashSet<IntVec3> oreCells)
        {
            if (!IsPlainRock(map, cell) || !oreCells.Add(cell)) { return false; }
            Building existing = cell.GetEdifice(map);
            if (existing != null) { existing.Destroy(DestroyMode.Vanish); }
            GenSpawn.Spawn(ThingMaker.MakeThing(ore), cell, map);
            return true;
        }

        /// <summary>Whether this cell holds natural rock with nothing already in it.</summary>
        private static bool IsPlainRock(Map map, IntVec3 cell)
        {
            if (!cell.InBounds(map)) { return false; }
            // Never the map's own edge: Core keeps the outermost ring, and a mineable there is a
            // hole in the world waiting to be dug.
            if (cell.x < 2 || cell.z < 2 || cell.x >= map.Size.x - 2 || cell.z >= map.Size.z - 2)
            { return false; }
            Building edifice = cell.GetEdifice(map);
            if (edifice == null || edifice.def == null || edifice.def.building == null) { return false; }
            if (!edifice.def.building.isNaturalRock) { return false; }
            return !edifice.def.building.isResourceRock;
        }

        /// <summary>Which way is out of the room from this perimeter cell.</summary>
        private static IntVec3 OutwardFrom(CellRect bounds, IntVec3 cell)
        {
            if (cell.x == bounds.maxX && cell.z != bounds.minZ && cell.z != bounds.maxZ)
            { return new IntVec3(1, 0, 0); }
            if (cell.x == bounds.minX && cell.z != bounds.minZ && cell.z != bounds.maxZ)
            { return new IntVec3(-1, 0, 0); }
            if (cell.z == bounds.maxZ && cell.x != bounds.minX && cell.x != bounds.maxX)
            { return new IntVec3(0, 0, 1); }
            if (cell.z == bounds.minZ && cell.x != bounds.minX && cell.x != bounds.maxX)
            { return new IntVec3(0, 0, -1); }
            return IntVec3.Invalid;
        }

        /// <summary>
        /// One ore, drawn against Core's own commonalities so a coordinate's spread matches what a
        /// player expects a mountain to hold.
        ///
        /// `mineableScatterCommonality` is the game's statement about how common a rock is; using
        /// it means steel is ordinary and plasteel is not, without this file holding an opinion
        /// about either.
        /// </summary>
        private static ThingDef PickOre(List<ThingDef> ores, int draw)
        {
            if (ores.Count == 0) { return null; }
            if (draw < 0) { draw = ~draw; }
            float total = 0f;
            for (int index = 0; index < ores.Count; index++)
            { total += CommonalityOf(ores[index]); }
            if (total <= 0f) { return ores[draw % ores.Count]; }
            float at = draw % 10000 / 10000f * total;
            for (int index = 0; index < ores.Count; index++)
            {
                at -= CommonalityOf(ores[index]);
                if (at <= 0f) { return ores[index]; }
            }
            return ores[ores.Count - 1];
        }

        private static float CommonalityOf(ThingDef def)
        {
            float commonality = def.building == null ? 0f : def.building.mineableScatterCommonality;
            return commonality > 0f ? commonality : 0.01f;
        }

        private static ThingDef PickDeep(List<ThingDef> candidates, int draw)
        {
            float total = 0f;
            for (int index = 0; index < candidates.Count; index++)
            { total += candidates[index].deepCommonality; }
            if (total <= 0f) { return candidates[draw % candidates.Count]; }
            float at = draw % 10000 / 10000f * total;
            for (int index = 0; index < candidates.Count; index++)
            {
                at -= candidates[index].deepCommonality;
                if (at <= 0f) { return candidates[index]; }
            }
            return candidates[candidates.Count - 1];
        }
    }
}
