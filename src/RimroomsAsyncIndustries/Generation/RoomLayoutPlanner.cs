using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Where the rooms of a coordinate go, before any map exists.
    ///
    /// ## Owner direction, 2026-09-30, verbatim
    ///
    /// *"and everything doesnt have to be square rooms and rectangle halways and u can use walls
    /// as pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms and
    /// this can propigate depper with the wild variatiosn of material typeds in all items
    /// equaipment walls floors lights furnature and benches that are found everywher deeper in
    /// with wild random events and layouts and spawns to find and loot!!!!!!"*
    ///
    /// ## What replaced what
    ///
    /// Until 0.12.49-dev this was a **hard-coded 3x3 grid of eight slots** at a fixed 19-cell
    /// spacing, producing 6 to 8 rooms of 10 to 16 cells on a 60x60 map. Every one of those
    /// numbers was a constant.
    ///
    /// The slot grid is now a **function of depth**, and so is everything derived from it:
    ///
    ///     depth   slots    spacing   room span   rooms
    ///       1      3x3        90         80        6      grand pillared halls
    ///       2      4x4        68         58       10
    ///       3      5x5        54         44       16
    ///       4      6x6        45         35       24
    ///       5      7x7        38         28       32
    ///       6      8x8        34         24       42      a warren
    ///
    /// **Depth 1 is six rooms eighty cells across.** That is the owner's *"grand large spaces"*,
    /// and it is also why the room count goes DOWN rather than up: a hall that size cannot fit in
    /// a 19-cell slot, and *"leas than 60-100 romms"* is satisfied at every depth by construction
    /// rather than by a cap.
    ///
    /// The shape is a **serpentine chain** through the slot grid, so consecutive rooms are always
    /// grid neighbours and the chain is connected without needing a search. Dead-end spur rooms
    /// hang off it from the slots the chain did not use.
    ///
    /// Pure planning: no map, world object, crew, random-global state or coordinate mutation.
    /// </summary>
    internal static class RoomLayoutPlanner
    {
        internal const int PlannerVersion = 3;
        internal const int CandidateBudget = 3;
        internal const int FallbackCandidate = 3;

        /// <summary>Free cells kept between the slot grid and the map edge.</summary>
        internal const int Margin = 14;

        /// <summary>Rock left between neighbouring rooms, which is what corridors run through.</summary>
        internal const int SlotGap = 10;

        /// <summary>Fewest and most slots per axis, mapped from depth 1 upward.</summary>
        internal const int MinSlotsPerAxis = 3;
        internal const int MaxSlotsPerAxis = 8;

        /// <summary>The ceiling the owner named: *"leas than 60-100 romms"*.</summary>
        internal const int MaxRooms = 60;

        /// <summary>
        /// Cells between pillars inside a room. Chosen against
        /// <c>RoofCollapseUtility.RoofMaxSupportDistance</c>, which is **6.9**, so a lattice at
        /// this spacing keeps every roofed cell within reach of something that holds roof.
        /// </summary>
        internal const int PillarSpacing = 6;

        /// <summary>
        /// A room only gets pillars once it is wider than a roof can span unaided -- twice 6.9,
        /// rounded down. Below that the room is a room; above it, it is a hall.
        /// </summary>
        internal const int PillarThreshold = 13;

        /// <summary>Exactly one of each of these, and index 0 is always the threshold.</summary>
        private static readonly string[] UniqueFamilies = { "threshold_room", "office_copy", "return_gallery" };

        /// <summary>Filled in along the chain, as many times as the chain is long.</summary>
        private static readonly string[] ChainFamilies = { "survey_lobby", "service_passage", "borrowed_corridor" };

        /// <summary>Dead ends hanging off the chain, one link each.</summary>
        private static readonly string[] SpurFamilies = { "storage_nook", "utility_room" };

        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)
        {
            selected = null;
            for (int candidate = 0; candidate < CandidateBudget; candidate++)
            {
                List<RoomRecord> rooms = Build(coordinate, candidate);
                if (CandidateIsSafe(rooms, DepthOf(coordinate))) { selected = rooms; return true; }
            }
            List<RoomRecord> fallback = Build(coordinate, FallbackCandidate);
            if (!CandidateIsSafe(fallback, DepthOf(coordinate))) { return false; }
            selected = fallback;
            return true;
        }

        internal static bool TryBuildSafeFallback(CoordinateRecord coordinate, out List<RoomRecord> fallback)
        {
            fallback = null;
            if (coordinate == null || string.IsNullOrWhiteSpace(coordinate.Id) || coordinate.Seed < 0 ||
                coordinate.GeneratorVersion < 1 || coordinate.roomLibraryVersion < 1)
            { return false; }
            List<RoomRecord> candidate = Build(coordinate, FallbackCandidate);
            if (!CandidateIsSafe(candidate, DepthOf(coordinate))) { return false; }
            fallback = candidate;
            return true;
        }

        internal static int IdentifyCandidate(CoordinateRecord coordinate)
        {
            for (int candidate = 0; candidate <= FallbackCandidate; candidate++)
            {
                List<RoomRecord> rooms = Build(coordinate, candidate);
                if (coordinate.Rooms.Count != rooms.Count) { continue; }
                bool same = rooms.All(a => coordinate.Rooms.Any(b => a.index == b.index && a.familyId == b.familyId &&
                    a.x == b.x && a.z == b.z && a.width == b.width && a.height == b.height && a.links.OrderBy(i => i).SequenceEqual(b.links.OrderBy(i => i))));
                if (same) { return candidate; }
            }
            return -1; // Existing saved graph: never relabel it as a newly selected candidate.
        }

        /// <summary>A coordinate's depth, floored at one, in one place so every reader agrees.</summary>
        internal static int DepthOf(CoordinateRecord coordinate)
        {
            return coordinate == null || coordinate.Depth < 1 ? 1 : coordinate.Depth;
        }

        /// <summary>Slots per axis for this depth. Deeper means more, smaller rooms.</summary>
        internal static int SlotsPerAxis(int depth)
        {
            int slots = MinSlotsPerAxis + (depth < 1 ? 0 : depth - 1);
            if (slots < MinSlotsPerAxis) { return MinSlotsPerAxis; }
            return slots > MaxSlotsPerAxis ? MaxSlotsPerAxis : slots;
        }

        /// <summary>Centre-to-centre distance between neighbouring slots.</summary>
        internal static int SlotSpacing(int slots)
        {
            return (DestinationService.MapWidth - Margin * 2) / slots;
        }

        /// <summary>The default span of a room in a slot of this size, always even.</summary>
        internal static int SlotRoomSpan(int spacing)
        {
            int span = spacing - SlotGap;
            if (span % 2 != 0) { span--; }
            return span < 8 ? 8 : span;
        }

        /// <summary>Where a slot's centre sits on the map.</summary>
        internal static int SlotCenter(int index, int spacing)
        {
            return Margin + spacing / 2 + spacing * index;
        }

        /// <summary>
        /// The pillar cells inside a room, and **the single place this is decided.**
        ///
        /// Both the generator, which spawns them, and <see cref="CandidateIsSafe"/>, which has to
        /// prove the room is still walkable with them in it, call this. Two places deriving the
        /// same lattice independently is precisely the defect that stopped every coordinate
        /// generating from 0.7.8-dev to 0.12.47-dev.
        ///
        /// **Never on the centre cross.** Doors and corridors meet a room at the midpoint of each
        /// wall, so the centre row and centre column are left completely clear: a straight walk
        /// from any doorway to any other cannot be blocked by a pillar, whatever the room's size.
        /// </summary>
        internal static IEnumerable<IntVec3> PillarCells(RoomRecord room)
        {
            CellRect bounds = room.Bounds;
            if (bounds.Width <= PillarThreshold && bounds.Height <= PillarThreshold)
            { yield break; }
            IntVec3 center = bounds.CenterCell;
            for (int x = bounds.minX + PillarSpacing; x <= bounds.maxX - PillarSpacing; x += PillarSpacing)
            {
                for (int z = bounds.minZ + PillarSpacing; z <= bounds.maxZ - PillarSpacing; z += PillarSpacing)
                {
                    if (x == center.x || z == center.z) { continue; }
                    yield return new IntVec3(x, 0, z);
                }
            }
        }

        /// <summary>
        /// Cells inside a room that are left as solid rock, so the room is not a rectangle.
        ///
        /// ## Owner direction, 2026-09-30, verbatim
        ///
        /// *"and everything doesnt have to be square rooms and rectangle halways"*.
        ///
        /// ## Why rock in the corners rather than a different rectangle
        ///
        /// The room's `Bounds` has to stay a rect: the validator bounds-checks it, the doors are
        /// placed at the midpoint of each side, the corridors aim at `CenterCell`, and the pillar
        /// lattice is laid out across it. Changing the rect would mean changing all four.
        ///
        /// So the rect stays and the **carve** changes. Rock is left standing inside the room, and
        /// it is left **only in the corners** -- never on the centre cross, never at an edge
        /// midpoint. That single restriction buys four things at once:
        ///
        ///   * every doorway still opens onto clear floor;
        ///   * a straight walk from any doorway to any other is still clear, so **no shape can
        ///     ever disconnect a room** and no candidate is rejected for having one;
        ///   * the pillar lattice needs no special case, because rock already holds roof; and
        ///   * the intrusions are `Mineable`, so a player who wants the rectangle can dig for it.
        ///
        /// **Shallow coordinates barely deform.** Depth 1 gets nothing, for the same reason
        /// <see cref="Derange"/> leaves it alone: the yellow rooms read as a place precisely
        /// because they are monotonous, and the wrongness is something the player travels toward.
        ///
        /// **Decided here and nowhere else**, like <see cref="PillarCells"/>: the generator leaves
        /// these cells uncarved and <see cref="CandidateIsSafe"/> marks them unwalkable, and two
        /// independent derivations of one rule is the defect that cost this project thirty-nine
        /// checkpoints.
        /// </summary>
        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)
        {
            if (room == null || depth <= 1) { yield break; }
            CellRect bounds = room.Bounds;
            // The interior only. The perimeter is wall and the ring inside it is the walkway that
            // keeps every doorway reachable.
            int insetX = bounds.minX + 2;
            int insetZ = bounds.minZ + 2;
            int extentX = bounds.maxX - 2;
            int extentZ = bounds.maxZ - 2;
            if (extentX - insetX < 4 || extentZ - insetZ < 4) { yield break; }

            IntVec3 center = bounds.CenterCell;
            // How far a corner mass reaches in, growing with depth and never past the centre
            // cross. Clamped to a third of the room so a shape can never eat the middle.
            int reach = System.Math.Min((depth - 1) * 2, System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);
            if (reach < 1) { yield break; }

            int roll = DestinationService.StableHash(room.index * 31 + depth,
                (room.familyId ?? "") + ":shape", depth);
            if (roll < 0) { roll = ~roll; }
            // Which corners are filled. Four bits, and never all four of a small room.
            int corners = 1 + roll % 15;

            for (int index = 0; index < 4; index++)
            {
                if ((corners & (1 << index)) == 0) { continue; }
                bool east = index == 1 || index == 2;
                bool north = index >= 2;
                // Each corner mass is a quarter-ellipse, so the edge it presents to the room is
                // curved rather than another right angle.
                for (int dx = 0; dx < reach; dx++)
                {
                    for (int dz = 0; dz < reach; dz++)
                    {
                        if (dx * dx + dz * dz > reach * reach) { continue; }
                        int x = east ? extentX - dx : insetX + dx;
                        int z = north ? extentZ - dz : insetZ + dz;
                        // The centre cross is inviolable: it is what guarantees every doorway
                        // reaches every other doorway whatever shape the corners take.
                        if (x == center.x || z == center.z) { continue; }
                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }
                        if (z <= bounds.minZ + 1 || z >= bounds.maxZ - 1) { continue; }
                        yield return new IntVec3(x, 0, z);
                    }
                }
            }
        }

        /// <summary>
        /// Half the width of the corridor between two rooms, so hallways are not all one size.
        ///
        /// Two gives a three-cell walkway, three gives five. Derived from the two rooms' own
        /// indices so it is stable across a reload, and **shared with
        /// <see cref="CandidateIsSafe"/>** for the usual reason.
        /// </summary>
        internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)
        {
            if (first == null || second == null || depth <= 1) { return 2; }
            int roll = DestinationService.StableHash(first.index * 101 + second.index,
                "corridor:width", depth);
            if (roll < 0) { roll = ~roll; }
            return roll % 3 == 0 ? 3 : 2;
        }

        private static List<RoomRecord> Build(CoordinateRecord coordinate, int candidate)
        {
            bool fallback = candidate == FallbackCandidate;
            int seed = DestinationService.StableHash(coordinate.Seed, coordinate.Id + ":rooms:" + candidate,
                PlannerVersion + coordinate.GeneratorVersion + DestinationService.GetRoomLibraryVersion(coordinate));
            int depth = fallback ? 1 : Math.Max(1, coordinate.Depth);
            int slots = SlotsPerAxis(depth);
            int spacing = SlotSpacing(slots);
            int span = SlotRoomSpan(spacing);

            // The serpentine: row-major with alternating direction, so consecutive entries are
            // always grid neighbours and the chain needs no pathfinding to be connected.
            var order = new List<IntVec2>();
            for (int row = 0; row < slots; row++)
            {
                for (int column = 0; column < slots; column++)
                {
                    int x = row % 2 == 0 ? column : slots - 1 - column;
                    order.Add(new IntVec2(x, row));
                }
            }

            // Two thirds of the grid, so there is always rock left between the arms of the chain.
            int chainLength = fallback ? MinSlotsPerAxis * MinSlotsPerAxis * 2 / 3 : order.Count * 2 / 3;
            if (chainLength < 6) { chainLength = 6; }
            if (chainLength > MaxRooms) { chainLength = MaxRooms; }
            if (chainLength > order.Count) { chainLength = order.Count; }

            var rooms = new List<RoomRecord>();
            var taken = new HashSet<IntVec2>();
            for (int index = 0; index < chainLength; index++)
            {
                IntVec2 slot = order[index];
                taken.Add(slot);
                string family = ChainFamilyFor(index, chainLength, seed);
                rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing, span, seed, fallback, depth));
            }
            for (int index = 1; index < chainLength; index++) { Link(rooms, index - 1, index); }

            // Dead ends, from slots the chain walked past. Bounded by MaxRooms so a deep
            // coordinate cannot grow without limit.
            if (!fallback)
            {
                for (int index = 0; index < order.Count && rooms.Count < MaxRooms; index++)
                {
                    IntVec2 slot = order[index];
                    if (taken.Contains(slot)) { continue; }
                    int host = ChainNeighbourOf(rooms, chainLength, slot, slots, spacing);
                    if (host < 0) { continue; }
                    if (DestinationService.StableHash(seed, "spur:" + slot.x + "," + slot.z, depth) % 3 != 0)
                    { continue; }
                    taken.Add(slot);
                    string family = SpurFamilies[rooms.Count % SpurFamilies.Length];
                    rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing, span, seed, false, depth));
                    Link(rooms, rooms.Count - 1, host);
                }
            }

            // A ring, when the chain's ends happen to be neighbours: a short way back rather than
            // retracing the whole route. Spine candidates deliberately do not get one.
            if (fallback || seed % 2 == 0)
            {
                if (AreNeighbourRooms(rooms[0], rooms[chainLength - 1]) &&
                    !rooms[0].links.Contains(chainLength - 1))
                { Link(rooms, chainLength - 1, 0); }
            }
            return rooms;
        }

        /// <summary>
        /// Index 0 is the threshold, the last chain room is the way home, and one room in the
        /// middle is the office copy. Everything else cycles the repeating families.
        ///
        /// The three unique families are unique because something depends on there being exactly
        /// one: the gate anchor, the evidence book, and the way out.
        /// </summary>
        private static string ChainFamilyFor(int index, int chainLength, int seed)
        {
            if (index == 0) { return UniqueFamilies[0]; }
            if (index == chainLength - 1) { return UniqueFamilies[2]; }
            int officeAt = 1 + Math.Abs(seed / 23) % Math.Max(1, chainLength - 2);
            if (index == officeAt) { return UniqueFamilies[1]; }
            // service_passage must appear at least once: the generator's climate room is
            // FirstOrDefault(utility_room) ?? First(service_passage), and the second half of that
            // throws when there is none.
            if (index == 1 && officeAt != 1) { return "service_passage"; }
            if (index == 2 && officeAt == 1) { return "service_passage"; }
            return ChainFamilies[Math.Abs(seed / 7 + index) % ChainFamilies.Length];
        }

        private static RoomRecord MakeRoom(CoordinateRecord coordinate, int index, string family,
            IntVec2 slot, int spacing, int span, int seed, bool fallback, int depth)
        {
            int width = span;
            int height = span;
            if (!fallback)
            {
                // Family proportions, scaled to the slot rather than written as cell counts.
                if (family == "service_passage") { width = span * 3 / 4; }
                else if (family == "borrowed_corridor")
                {
                    bool lengthwise = (seed / 7 + index) % 2 == 0;
                    if (lengthwise) { height = span * 3 / 5; } else { width = span * 3 / 5; }
                }
                else if (family == "storage_nook" || family == "utility_room")
                { width = span * 2 / 3; height = span * 2 / 3; }
                if (DestinationService.GetRoomLibraryVersion(coordinate) >= 2)
                { Derange(coordinate, ref width, ref height, seed, index, span); }
            }
            width = Even(width, span);
            height = Even(height, span);
            int centerX = SlotCenter(slot.x, spacing);
            int centerZ = SlotCenter(slot.z, spacing);
            return new RoomRecord
            {
                index = index,
                familyId = family,
                x = centerX - width / 2,
                z = centerZ - height / 2,
                width = width,
                height = height,
                links = new List<int>(),
            };
        }

        /// <summary>The chain room a spur slot can hang off, or -1 when it touches none.</summary>
        private static int ChainNeighbourOf(List<RoomRecord> rooms, int chainLength, IntVec2 slot,
            int slots, int spacing)
        {
            int centerX = SlotCenter(slot.x, spacing);
            int centerZ = SlotCenter(slot.z, spacing);
            for (int index = 0; index < chainLength && index < rooms.Count; index++)
            {
                IntVec3 other = rooms[index].Bounds.CenterCell;
                if ((other.x == centerX && Math.Abs(other.z - centerZ) == spacing) ||
                    (other.z == centerZ && Math.Abs(other.x - centerX) == spacing))
                { return index; }
            }
            return -1;
        }

        private static bool AreNeighbourRooms(RoomRecord first, RoomRecord second)
        {
            IntVec3 a = first.Bounds.CenterCell;
            IntVec3 b = second.Bounds.CenterCell;
            if (a.x == b.x) { return !first.Bounds.Overlaps(second.Bounds) && a.z != b.z; }
            if (a.z == b.z) { return !first.Bounds.Overlaps(second.Bounds) && a.x != b.x; }
            return false;
        }

        /// <summary>
        /// Pulls a room's proportions away from the tidy defaults, harder the deeper the
        /// coordinate sits, and sometimes straight out of the player's own colony.
        ///
        /// **Shallow coordinates barely move.** The yellow rooms read as a place precisely
        /// because they are monotonous and regular, and deranging them would throw away the
        /// image the whole setting rests on. The wrongness is something the player travels
        /// toward.
        ///
        /// **Clamped to the slot, not to a constant.** The old version clamped to 8..17 because
        /// rooms sat 19 cells apart; the spacing is now a function of depth, so the clamp is too.
        /// The clamp is what keeps *"deranged"* from collapsing into *"broken"*.
        /// </summary>
        private static void Derange(CoordinateRecord coordinate, ref int width, ref int height,
            int seed, int roomIndex, int span)
        {
            int depth = coordinate.Depth;
            if (depth <= 1) { return; }

            int roll = DestinationService.StableHash(seed, "derange:" + roomIndex, depth);
            if (roll < 0) { roll = ~roll; }

            // An echoed room: take the proportions of something the branch actually built,
            // snapshotted when this coordinate was discovered. Deeper spaces do it more often.
            IReadOnlyList<int> echoed = coordinate.EchoedRoomSizes;
            int echoChance = Math.Min(50, (depth - 1) * 12);
            if (echoed != null && echoed.Count >= 2 && roll % 100 < echoChance)
            {
                width = Clamp(echoed[roll % echoed.Count], span);
                height = Clamp(echoed[(roll / 7) % echoed.Count], span);
                return;
            }

            // A hallway. Owner direction 2026-09-29: "its weirtd and lots of halways and
            // halway/rooms and facilitys and noraml like rooms".
            int hallChance = Math.Min(35, (depth - 1) * 9);
            if ((roll / 3) % 100 < hallChance)
            {
                bool lengthwise = ((roll / 5) % 2) == 0;
                int longSide = span;
                int shortSide = Math.Max(8, span / 3);
                width = Clamp(lengthwise ? longSide : shortSide, span);
                height = Clamp(lengthwise ? shortSide : longSide, span);
                return;
            }

            // Otherwise: stretch. The spread grows with depth AND with the slot, so a deep room
            // can be a long corridor or a near-square hall where a shallow one is always a hall.
            int spread = Math.Min(span / 3, depth * Math.Max(1, span / 12));
            if (spread < 1) { spread = 1; }
            width = Clamp(width + (roll % (spread * 2 + 1)) - spread, span);
            height = Clamp(height + ((roll / 11) % (spread * 2 + 1)) - spread, span);
        }

        /// <summary>Keeps a dimension inside what this depth's slot can hold.</summary>
        private static int Clamp(int value, int span)
        {
            if (value < 8) { return 8; }
            return value > span ? span : value;
        }

        /// <summary>
        /// Rooms are an even number of cells across so <c>CellRect.CenterCell</c> lands where
        /// doors and corridors expect it, whatever the room's size.
        /// </summary>
        private static int Even(int value, int span)
        {
            int clamped = Clamp(value, span);
            if (clamped % 2 != 0) { clamped--; }
            return clamped < 8 ? 8 : clamped;
        }

        private static void Link(List<RoomRecord> rooms, int a, int b)
        {
            if (rooms[a].links.Contains(b)) { return; }
            rooms[a].links.Add(b);
            rooms[b].links.Add(a);
        }

        private static bool CandidateIsSafe(List<RoomRecord> rooms, int depth)
        {
            if (!DestinationService.ValidateRooms(rooms, out _)) { return false; }
            // Project the exact boundary walls, one-cell openable doors, three-cell corridors and
            // the pillar lattice. A bounded floor check before any engine map/content state
            // exists, so a layout that seals a room off never reaches a map.
            var floor = new bool[DestinationService.MapWidth, DestinationService.MapHeight];
            foreach (RoomRecord room in rooms)
            {
                foreach (IntVec3 cell in room.Bounds.Cells)
                {
                    bool edge = cell.x == room.Bounds.minX || cell.x == room.Bounds.maxX || cell.z == room.Bounds.minZ || cell.z == room.Bounds.maxZ;
                    floor[cell.x, cell.z] = !edge || DoorOpening(room, rooms, cell);
                }
                // The pillars, from the SAME function the generator spawns them from.
                foreach (IntVec3 pillar in PillarCells(room))
                { floor[pillar.x, pillar.z] = false; }
                // And the rock left standing in the corners, from the same function again.
                foreach (IntVec3 rock in RockIntrusionCells(room, depth))
                { floor[rock.x, rock.z] = false; }
            }
            foreach (RoomRecord room in rooms)
            {
                foreach (int linked in room.links.Where(index => index > room.index))
                {
                    RoomRecord other = rooms[linked];
                    IntVec3 a = room.Bounds.CenterCell;
                    IntVec3 b = other.Bounds.CenterCell;
                    // The same width the generator will carve, from the shared function.
                    int reach = CorridorHalfWidthBetween(room, other, depth) - 1;
                    if (a.z == b.z)
                    {
                        for (int x = Math.Min(room.Bounds.maxX, other.Bounds.maxX) + 1; x < Math.Max(room.Bounds.minX, other.Bounds.minX); x++)
                        { for (int dz = -reach; dz <= reach; dz++) { floor[x, a.z + dz] = true; } }
                    }
                    else
                    {
                        for (int z = Math.Min(room.Bounds.maxZ, other.Bounds.maxZ) + 1; z < Math.Max(room.Bounds.minZ, other.Bounds.minZ); z++)
                        { for (int dx = -reach; dx <= reach; dx++) { floor[a.x + dx, z] = true; } }
                    }
                }
            }
            IntVec3 start = rooms[0].Bounds.CenterCell;
            var seen = new HashSet<IntVec3> { start };
            var pending = new Queue<IntVec3>();
            pending.Enqueue(start);
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            while (pending.Count > 0)
            {
                IntVec3 cell = pending.Dequeue();
                foreach (IntVec3 direction in directions)
                {
                    IntVec3 next = cell + direction;
                    if (next.x >= 0 && next.z >= 0 && next.x < DestinationService.MapWidth && next.z < DestinationService.MapHeight &&
                        floor[next.x, next.z] && seen.Add(next)) { pending.Enqueue(next); }
                }
            }
            return rooms.All(room => seen.Contains(room.Bounds.CenterCell)) &&
                rooms.Where(room => room.familyId == "utility_room" || room.familyId == "storage_nook").All(room => room.links.Count == 1);
        }

        internal static bool DoorOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                if (other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.maxX < room.Bounds.minX && cell.x == room.Bounds.minX && cell.z == room.Bounds.CenterCell.z) { return true; }
                if (other.Bounds.minZ > room.Bounds.maxZ && cell.z == room.Bounds.maxZ && cell.x == room.Bounds.CenterCell.x) { return true; }
                if (other.Bounds.maxZ < room.Bounds.minZ && cell.z == room.Bounds.minZ && cell.x == room.Bounds.CenterCell.x) { return true; }
            }
            return false;
        }
    }
}
