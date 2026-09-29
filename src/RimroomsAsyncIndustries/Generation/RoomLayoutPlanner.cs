using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    // Pure first-slice planning: no map, world object, crew, random-global state or coordinate mutation.
    internal static class RoomLayoutPlanner
    {
        internal const int PlannerVersion = 2;
        internal const int CandidateBudget = 3;
        internal const int FallbackCandidate = 3;
        private static readonly int[,] Grid = { { 0, 0 }, { 1, 0 }, { 2, 0 }, { 2, 1 }, { 1, 1 }, { 0, 1 }, { 0, 2 }, { 1, 2 } };
        private static readonly string[] Families = { "threshold_room", "survey_lobby", "office_copy", "service_passage", "borrowed_corridor", "return_gallery" };

        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)
        {
            selected = null;
            for (int candidate = 0; candidate < CandidateBudget; candidate++)
            {
                List<RoomRecord> rooms = Build(coordinate, candidate);
                if (CandidateIsSafe(rooms)) { selected = rooms; return true; }
            }
            List<RoomRecord> fallback = Build(coordinate, FallbackCandidate);
            if (!CandidateIsSafe(fallback)) { return false; }
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
            if (!CandidateIsSafe(candidate)) { return false; }
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

        private static List<RoomRecord> Build(CoordinateRecord coordinate, int candidate)
        {
            bool fallback = candidate == FallbackCandidate;
            int seed = DestinationService.StableHash(coordinate.Seed, coordinate.Id + ":rooms:" + candidate,
                PlannerVersion + coordinate.GeneratorVersion + DestinationService.GetRoomLibraryVersion(coordinate));
            int count = fallback ? 6 : 6 + seed % 3;
            int rotation = fallback ? 0 : (seed / 3) % 4;
            bool mirror = !fallback && (seed / 13) % 2 != 0;
            var rooms = new List<RoomRecord>();
            for (int i = 0; i < count; i++)
            {
                int x = Grid[i, 0];
                int z = Grid[i, 1];
                if (mirror) { x = 2 - x; }
                for (int turn = 0; turn < rotation; turn++) { int oldX = x; x = 2 - z; z = oldX; }
                string family = i < 6 ? Families[i] : ((i == 6) == ((seed / 29) % 2 == 0) ? "storage_nook" : "utility_room");
                int width = 14;
                int height = 14;
                if (!fallback)
                {
                    if (family == "survey_lobby") { width = 16; height = 12; }
                    else if (family == "service_passage") { width = 10; height = 14; }
                    else if (family == "borrowed_corridor") { width = (seed / 7) % 2 == 0 ? 10 : 16; height = width == 10 ? 16 : 10; }
                    else if (i >= 6) { width = 12; height = 12; }
                    else if (family == "office_copy" && (seed / 17) % 2 == 0) { width = 16; height = 12; }
                }
                // Owner direction 2026-09-29: "the back rooms is random on crack and lsd creepy
                // horror flick", and "not just room shape echoes but echos of thier inhabitance".
                //
                // Only for coordinates on room library version 2 or later. Everything discovered
                // before this plans exactly as it always did, which is what roomLibraryVersion
                // exists for -- a saved graph is re-planned to verify its fingerprint, so
                // changing the shape of an existing coordinate would make it refuse to generate.
                if (!fallback && DestinationService.GetRoomLibraryVersion(coordinate) >= 2)
                { Derange(coordinate, ref width, ref height, seed, i); }

                if (rotation % 2 != 0) { int swap = width; width = height; height = swap; }
                rooms.Add(new RoomRecord { index = i, familyId = family, x = 9 + 19 * x - width / 2,
                    z = 9 + 19 * z - height / 2, width = width, height = height, links = new List<int>() });
            }
            for (int i = 1; i < 6; i++) { Link(rooms, i - 1, i); }
            // Ring candidates provide a short return-gallery exit; spine candidates require route retracing.
            if (fallback || seed % 2 == 0) { Link(rooms, 5, 0); }
            if (count >= 7) { Link(rooms, 6, 5); }
            if (count == 8) { Link(rooms, 7, 4); }
            return rooms;
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
        /// **Clamped to 8..17 always.** Rooms sit 19 cells apart on the planning grid, so
        /// anything wider would overlap its neighbour — and the candidate validator would then
        /// reject every layout and the coordinate would fall back to the plain one. The clamp
        /// is what keeps "deranged" from collapsing into "broken".
        /// </summary>
        private static void Derange(CoordinateRecord coordinate, ref int width, ref int height,
            int seed, int roomIndex)
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
                width = Clamp(echoed[roll % echoed.Count]);
                height = Clamp(echoed[(roll / 7) % echoed.Count]);
                return;
            }

            // A hallway. Owner direction 2026-09-29: "its weirtd and lots of halways and
            // halway/rooms and facilitys and noraml like rooms".
            //
            // Made deliberately rather than hoped for out of the stretch below: a corridor is
            // one of the two shapes the setting is actually built on, and leaving it to a
            // symmetric roll would produce one rarely and by accident. Long and narrow in one
            // axis, which the room dresser then fills as a corridor rather than as a hall.
            int hallChance = Math.Min(35, (depth - 1) * 9);
            if ((roll / 3) % 100 < hallChance)
            {
                bool lengthwise = ((roll / 5) % 2) == 0;
                int longSide = 15 + (roll % 3);
                int shortSide = 8 + ((roll / 13) % 2);
                width = Clamp(lengthwise ? longSide : shortSide);
                height = Clamp(lengthwise ? shortSide : longSide);
                return;
            }

            // Otherwise: stretch. The spread grows with depth, so a deep room can be a long
            // corridor or a near-square hall where a shallow one is always roughly a hall.
            int spread = Math.Min(5, depth);
            width = Clamp(width + (roll % (spread * 2 + 1)) - spread);
            height = Clamp(height + ((roll / 11) % (spread * 2 + 1)) - spread);
        }

        /// <summary>Keeps a dimension inside what the 19-cell planning grid can hold.</summary>
        private static int Clamp(int value)
        {
            return value < 8 ? 8 : (value > 17 ? 17 : value);
        }

        private static void Link(List<RoomRecord> rooms, int a, int b)
        { rooms[a].links.Add(b); rooms[b].links.Add(a); }

        private static bool CandidateIsSafe(List<RoomRecord> rooms)
        {
            if (!DestinationService.ValidateRooms(rooms, out _)) { return false; }
            // Project the exact boundary walls, one-cell openable doors, three-cell corridors and center support.
            // This is a bounded 60x60 floor check before any engine map/content state exists.
            var floor = new bool[DestinationService.MapWidth, DestinationService.MapHeight];
            foreach (RoomRecord room in rooms)
            {
                foreach (IntVec3 cell in room.Bounds.Cells)
                {
                    bool edge = cell.x == room.Bounds.minX || cell.x == room.Bounds.maxX || cell.z == room.Bounds.minZ || cell.z == room.Bounds.maxZ;
                    floor[cell.x, cell.z] = !edge || DoorOpening(room, rooms, cell);
                }
                IntVec3 center = room.Bounds.CenterCell;
                floor[center.x, center.z] = false;
            }
            foreach (RoomRecord room in rooms)
            {
                foreach (int linked in room.links.Where(index => index > room.index))
                {
                    RoomRecord other = rooms[linked];
                    IntVec3 a = room.Bounds.CenterCell;
                    IntVec3 b = other.Bounds.CenterCell;
                    if (a.z == b.z)
                    {
                        for (int x = Math.Min(room.Bounds.maxX, other.Bounds.maxX) + 1; x < Math.Max(room.Bounds.minX, other.Bounds.minX); x++)
                        { for (int dz = -1; dz <= 1; dz++) { floor[x, a.z + dz] = true; } }
                    }
                    else
                    {
                        for (int z = Math.Min(room.Bounds.maxZ, other.Bounds.maxZ) + 1; z < Math.Max(room.Bounds.minZ, other.Bounds.minZ); z++)
                        { for (int dx = -1; dx <= 1; dx++) { floor[a.x + dx, z] = true; } }
                    }
                }
            }
            IntVec3 start = rooms[0].Bounds.CenterCell + IntVec3.East;
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
            return rooms.All(room => seen.Contains(room.Bounds.CenterCell + IntVec3.East)) &&
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
