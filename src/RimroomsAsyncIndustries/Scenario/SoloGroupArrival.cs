using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// Where a solo or group opening actually wakes up, which is **not** beside the way out.
    ///
    /// **Owner report, 2026-10-06, verbatim:** *"and something i saw in the backrooms solo/group
    /// start... the natural gate needs to spawn in somewhere in the backrooms maze not in the main
    /// starting room(the solo start u have to find your way to get out not just have the natural
    /// exit gate right next to u in main backroom room at start it needs to be found in the
    /// unexplored rooms"*.
    ///
    /// ## THE PARTY MOVES, NOT THE GATE, AND THAT IS NOT A DODGE
    ///
    /// The owner describes moving the gate, and the effect they asked for is exactly what this
    /// produces -- but moving the anchor itself would break something unrelated and much larger.
    /// `GenStep_BackroomsDestination` places the threshold door in the `threshold_room` of **every**
    /// coordinate, and `parent.ReturnAnchor` is **every expedition's way home**. A crew that stepped
    /// through a machine gate arrives at that door and leaves by it. Relocating it to a random maze
    /// room would mean every ordinary expedition landing somewhere with no marked exit, which is a
    /// far worse version of the problem this row is about.
    ///
    /// **So the solo opening arrives deep instead.** The exit stays where the generator and the
    /// portal network both expect it, and the party wakes up a measured number of rooms away. From
    /// the player's chair the two are indistinguishable: *" it needs to be found in the unexplored
    /// rooms"* is literally true, and nothing else in the mod changes.
    ///
    /// ## ROOM DISTANCE, NEVER CELL DISTANCE
    ///
    /// The row states this and the reason is arithmetic: **a 300x300 coordinate can put a cell far
    /// away and still inside the room you woke up in.** A cell-distance rule would have passed its
    /// own test while handing the player the exit, which is the defect being fixed wearing a
    /// different hat.
    ///
    /// `RoomRecord.Links` is a real adjacency list, so this is a breadth-first search over the
    /// coordinate's own room graph and the distance is *rooms you must walk through*.
    ///
    /// ## AND THE EXIT HAS TO BE HIDDEN AS WELL AS DISTANT
    ///
    /// `MapGenerator.rootsToUnfog` already unfogs the threshold room at generation, for the
    /// expedition case where that is exactly right. Left alone, a party arriving deep would still
    /// see the exit room sitting revealed on the map from the first second -- distant, and not
    /// found. So the threshold room is refogged, and the arrival room is flood-unfogged instead.
    ///
    /// **It composes with the unexplored-work fix rather than duplicating it.** Room content is
    /// forbidden until its cell stops being fogged, so a refogged exit room is not merely unseen:
    /// nothing in it offers work either, and no pawn walks across the maze to tidy it.
    /// </summary>
    internal static class SoloGroupArrival
    {
        /// <summary>
        /// How many rooms must lie between the party and the way out, at minimum.
        ///
        /// **Three**, and the number is a floor rather than a target: the search takes the
        /// **farthest** room it can reach and only falls back toward this when the graph is small.
        /// Three is the point at which a player cannot see the exit room from the arrival room
        /// through a line of open doors, which is the thing the owner actually objected to.
        ///
        /// A coordinate too small to satisfy it is handled rather than refused -- see
        /// <see cref="ArrivalRoom"/>. **A guaranteed opening must not fail on a small maze**, and
        /// §1.1's solo guarantee is not negotiable against a nicety.
        /// </summary>
        public const int MinimumRoomsFromExit = 3;

        /// <summary>
        /// The room the party wakes in: the one farthest from the threshold room by room count.
        ///
        /// Returns null when the coordinate has no usable room graph, and the caller then keeps the
        /// generator's own entry cell. **Degrading to the old behaviour is correct**: an opening
        /// that is merely too easy is playable, and an opening that throws is not.
        /// </summary>
        internal static RoomRecord ArrivalRoom(CoordinateRecord coordinate)
        {
            if (coordinate == null || coordinate.Rooms == null || coordinate.Rooms.Count == 0)
            { return null; }

            RoomRecord threshold = null;
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int i = 0; i < coordinate.Rooms.Count; i++)
            {
                RoomRecord room = coordinate.Rooms[i];
                if (room == null) { continue; }
                byIndex[room.Index] = room;
                if (room.FamilyId == "threshold_room") { threshold = room; }
            }
            if (threshold == null) { return null; }

            // Breadth-first over `Links`, so depth is rooms traversed. Unreached rooms are left out
            // entirely rather than treated as infinitely far: a room with no path to the threshold
            // is not a harder arrival, it is an arrival with no way out at all.
            var depth = new Dictionary<int, int> { { threshold.Index, 0 } };
            var queue = new Queue<int>();
            queue.Enqueue(threshold.Index);
            RoomRecord best = null;
            int bestDepth = 0;
            while (queue.Count > 0)
            {
                int current = queue.Dequeue();
                RoomRecord room;
                if (!byIndex.TryGetValue(current, out room) || room == null) { continue; }
                int here = depth[current];
                if (here > bestDepth)
                {
                    bestDepth = here;
                    best = room;
                }
                IReadOnlyList<int> links = room.Links;
                if (links == null) { continue; }
                for (int i = 0; i < links.Count; i++)
                {
                    int next = links[i];
                    if (depth.ContainsKey(next) || !byIndex.ContainsKey(next)) { continue; }
                    depth[next] = here + 1;
                    queue.Enqueue(next);
                }
            }

            // **The floor is reported, never enforced by refusing.** A maze whose farthest room is
            // two away gives a two-room walk, and the log says so, because a quiet downgrade is how
            // a guarantee stops meaning anything. The alternative -- failing the opening -- would
            // trade the owner's survival guarantee for their preference about distance.
            if (best != null && bestDepth < MinimumRoomsFromExit)
            {
                Log.Message("[Rimrooms] Coordinate " + coordinate.Id + " is only " + bestDepth
                    + " room(s) deep, so the opening party arrives that far from the way out "
                    + "rather than the intended " + MinimumRoomsFromExit + ".");
            }
            return best;
        }

        /// <summary>
        /// A standable cell inside the arrival room, or an invalid cell if none is free.
        ///
        /// Searched from the centre outward so the party lands in the middle of a room rather than
        /// against a wall, and every candidate is checked for being **standable and unroofed by an
        /// edifice**, because a room record is a rectangle and the generator may have put a wall
        /// intrusion through it.
        /// </summary>
        internal static IntVec3 ArrivalCell(Map inside, RoomRecord room)
        {
            if (inside == null || room == null) { return IntVec3.Invalid; }
            CellRect bounds = room.Bounds;
            IntVec3 centre = bounds.CenterCell;
            if (Suitable(inside, centre)) { return centre; }
            // Ordinal order over the rectangle, so the chosen cell is identical on every reload of
            // the same seed. A set iterated in hash order would move the party between loads.
            foreach (IntVec3 cell in bounds.Cells)
            {
                if (Suitable(inside, cell)) { return cell; }
            }
            return IntVec3.Invalid;
        }

        private static bool Suitable(Map map, IntVec3 cell)
        {
            return cell.IsValid && cell.InBounds(map) && cell.Standable(map)
                && cell.GetEdifice(map) == null;
        }

        /// <summary>
        /// Hide the way out and reveal where the party woke up.
        ///
        /// Order matters and is deliberate: **unfog the arrival room first, then refog the exit
        /// room.** `FloodFillerFog.FloodUnfog` only spreads through cells that are *currently*
        /// fogged and stops at any edifice whose def makes fog -- walls and doors -- so it reveals
        /// one room and no more. Refogging afterwards cannot then take back a cell the party can
        /// actually see.
        ///
        /// **Skipped entirely when the two rooms are the same**, which is the small-maze fallback.
        /// Refogging the room the party is standing in would hide the floor under their feet.
        /// </summary>
        internal static void HideTheWayOut(Map inside, RoomRecord arrival, RoomRecord threshold)
        {
            if (inside == null || arrival == null || threshold == null) { return; }
            if (arrival.Index == threshold.Index) { return; }
            IntVec3 seed = ArrivalCell(inside, arrival);
            if (seed.IsValid && inside.fogGrid != null && inside.fogGrid.IsFogged(seed))
            { FloodFillerFog.FloodUnfog(seed, inside); }
            if (inside.fogGrid != null) { inside.fogGrid.Refog(threshold.Bounds); }
        }

        /// <summary>The coordinate's threshold room, for the caller's refog call.</summary>
        internal static RoomRecord ThresholdRoom(CoordinateRecord coordinate)
        {
            if (coordinate == null || coordinate.Rooms == null) { return null; }
            for (int i = 0; i < coordinate.Rooms.Count; i++)
            {
                RoomRecord room = coordinate.Rooms[i];
                if (room != null && room.FamilyId == "threshold_room") { return room; }
            }
            return null;
        }
    }
}
