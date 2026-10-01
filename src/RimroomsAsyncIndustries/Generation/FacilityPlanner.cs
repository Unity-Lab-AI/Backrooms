using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Threats;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Some places are bigger than a room.
    ///
    /// **Owner direction, verbatim:** *"facilitys"* — larger functional spaces, as distinct
    /// from rooms and corridors. Also *"lots of furnature and equipment and different types of
    /// rooms and materials of all types from labs, to workshops, to nursaries"*.
    ///
    /// ## A facility is a run of adjacent rooms that agree with each other
    ///
    /// Until now every room rolled its own kind independently, so a coordinate could put a
    /// laboratory bench in one room, a bed in the next and a smithy in the third. Each room
    /// was fine and **the place was nothing** — there was no laboratory, only a room with a
    /// bench in it.
    ///
    /// A facility picks a contiguous run of rooms off the coordinate's own graph and dresses
    /// **all of them as the same kind**. That is what turns three rooms into a laboratory
    /// wing, a dormitory block, a nursery. No new def type and no new content: it is the same
    /// archetypes, chosen once for a group instead of once per room.
    ///
    /// ## Why it makes deep coordinates worse rather than tidier
    ///
    /// The obvious worry is that coherence is the opposite of what this setting wants. It is
    /// not. **A recognisable institution that is wrong is far worse than a jumble**, because a
    /// jumble has nothing to violate. The existing derangement still applies on top: in a deep
    /// coordinate the archetype's family constraint lapses and its contents scale, so a
    /// three-room nursery turns up where no nursery could be, furnished at a tech level
    /// nobody there should have had. That is the shape the setting actually wants.
    ///
    /// ## What it never touches
    ///
    /// - **Depth 1.** The shallow yellow rooms are sparse and that emptiness is the look.
    /// - **The threshold room**, which is left undressed so the way back is never buried.
    /// - **Quiet rooms.** Those are required content and are never dressed at all, so a
    ///   facility is assembled only from rooms that were going to be dressed anyway. A
    ///   facility can therefore never reduce the number of quiet rooms.
    /// </summary>
    public static class FacilityPlanner
    {
        /// <summary>Smallest number of rooms that is a facility rather than a room.</summary>
        private const int MinRooms = 2;

        /// <summary>
        /// Largest.
        ///
        /// **This was four**, written when a level was a twenty-four-room line and four rooms was
        /// a sixth of it. A braided maze at depth 2 has forty-eight rooms, and the owner has asked
        /// for *"neighboorhoods and complexes"* by name -- which is a word for something bigger
        /// than four rooms. The condition it is still held to is theirs: a solo group has to be
        /// able to read the place and get out of it, which is why this is six and not twelve.
        /// </summary>
        private const int MaxRooms = 6;

        /// <summary>
        /// Share of eligible rooms that may end up inside a facility.
        ///
        /// Still under two thirds on purpose -- single rooms of their own kind are what a facility
        /// stands out against, and a floor that is nothing but institutions has no institutions.
        /// Raised from 0.45 with `MaxRooms`, because the owner asked for complexes and a maze has
        /// the room count to carry them.
        /// </summary>
        private const float EligibleShare = 0.6f;

        private static string cachedKey;
        private static Dictionary<int, int> cachedAnchors;

        /// <summary>
        /// The anchor room of the facility this room belongs to, or -1 when it stands alone.
        ///
        /// The anchor is simply the lowest room index in the group, so every room of a facility
        /// resolves to the same archetype without anything being stored: the assignment is
        /// derived from the coordinate's saved graph and seed, so it survives a save and a
        /// reload by being recomputed identically rather than by being written down.
        /// </summary>
        public static int AnchorFor(CoordinateRecord coordinate, int roomIndex)
        {
            Dictionary<int, int> anchors = Anchors(coordinate);
            int anchor;
            return anchors != null && anchors.TryGetValue(roomIndex, out anchor) ? anchor : -1;
        }

        private static Dictionary<int, int> Anchors(CoordinateRecord coordinate)
        {
            // **NO DEPTH GATE.** This read `coordinate.Depth <= 1`, so **a first level had no
            // facilities at all** -- no school, no hospital, no military post, no storage complex,
            // just rooms that each happened to have a bench. Owner: *"facilitys and buildings and
            // neighboorhoods and complexes and shools and hospitals and military and storages need
            // loot inside of them too"*.
            //
            // It is the fourth system found gated on the coordinate's own depth rather than on
            // distance from the arrival, and the rule that replaced it everywhere else applies
            // here: **distance from the spawn hall counts as depth.** The gate's intent -- the
            // yellow arrival stays sparse -- is kept and measured per room in `Plan`, which is
            // where the eligible set is decided.
            if (coordinate == null || coordinate.Rooms == null) { return null; }
            string key = coordinate.Id + ":" + coordinate.Seed + ":" + coordinate.Rooms.Count;
            if (string.Equals(key, cachedKey, StringComparison.Ordinal)) { return cachedAnchors; }
            cachedAnchors = Plan(coordinate);
            cachedKey = key;
            return cachedAnchors;
        }

        private static Dictionary<int, int> Plan(CoordinateRecord coordinate)
        {
            var anchors = new Dictionary<int, int>();
            IReadOnlyList<RoomRecord> rooms = coordinate.Rooms;
            int total = rooms.Count;
            if (total < MinRooms + 1) { return anchors; }

            // Only rooms that would have been dressed anyway. A facility never consumes a quiet
            // room, so the required-quiet guarantee is untouched by construction rather than by
            // a check somewhere else that could drift from it.
            var eligible = new HashSet<int>();
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int index = 0; index < total; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null) { continue; }
                byIndex[room.Index] = room;
                if (string.Equals(room.FamilyId, "threshold_room", StringComparison.Ordinal)) { continue; }
                if (CoordinatePressureLadder.IsQuietRoom(coordinate.Seed, room.Index, total)) { continue; }
                // **THE ARRIVAL STAYS SPARSE, AND THAT IS MEASURED PER ROOM.** This is the
                // property the old `coordinate.Depth <= 1` gate was protecting, kept -- the hall
                // and its immediate neighbours are never part of an institution, and everything
                // further out can be. The SAME function the archetypes, the inhabitants, the
                // events and the wall materials all read, so a room the dressing treats as deep
                // and the facility planner treats as shallow cannot exist.
                if (RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth) <= 1)
                { continue; }
                eligible.Add(room.Index);
            }
            if (eligible.Count < MinRooms) { return anchors; }

            int budget = Mathf.FloorToInt(eligible.Count * EligibleShare);
            if (budget < MinRooms) { return anchors; }

            // Ordinal order throughout. Def and dictionary order vary between machines, and a
            // coordinate must rebuild identically everywhere; this has been a live trap three
            // times in this code base.
            var ordered = new List<int>(eligible);
            ordered.Sort();

            var taken = new HashSet<int>();
            int spent = 0;
            for (int position = 0; position < ordered.Count && spent + MinRooms <= budget; position++)
            {
                int start = ordered[position];
                if (taken.Contains(start)) { continue; }

                int roll = Roll(coordinate.Seed, start, 7919);
                // Not every eligible room starts one. Roughly half do, which combined with the
                // budget keeps facilities a feature of a coordinate rather than its whole shape.
                if (roll % 2 == 0) { continue; }

                int wanted = MinRooms + (Roll(coordinate.Seed, start, 104729) % (MaxRooms - MinRooms + 1));
                wanted = Math.Min(wanted, budget - spent);
                if (wanted < MinRooms) { break; }

                List<int> group = Grow(byIndex, eligible, taken, start, wanted);
                if (group.Count < MinRooms) { continue; }

                group.Sort();
                int anchor = group[0];
                for (int member = 0; member < group.Count; member++)
                {
                    anchors[group[member]] = anchor;
                    taken.Add(group[member]);
                }
                spent += group.Count;
            }
            return anchors;
        }

        /// <summary>
        /// Walks the coordinate's own room graph outward from a starting room, taking only
        /// rooms that are eligible and unclaimed. Breadth first and ordinally sorted at every
        /// step, so the group is the same group on every machine.
        /// </summary>
        private static List<int> Grow(Dictionary<int, RoomRecord> byIndex, HashSet<int> eligible,
            HashSet<int> taken, int start, int wanted)
        {
            var group = new List<int> { start };
            var frontier = new List<int> { start };
            var seen = new HashSet<int> { start };

            while (group.Count < wanted && frontier.Count > 0)
            {
                var next = new List<int>();
                for (int index = 0; index < frontier.Count; index++)
                {
                    RoomRecord room;
                    if (!byIndex.TryGetValue(frontier[index], out room) || room.Links == null) { continue; }
                    var links = new List<int>(room.Links);
                    links.Sort();
                    for (int link = 0; link < links.Count; link++)
                    {
                        int candidate = links[link];
                        if (!seen.Add(candidate)) { continue; }
                        if (!eligible.Contains(candidate) || taken.Contains(candidate)) { continue; }
                        group.Add(candidate);
                        next.Add(candidate);
                        if (group.Count >= wanted) { return group; }
                    }
                }
                frontier = next;
            }
            return group;
        }

        /// <summary>A bounded, positive, deterministic roll from the coordinate's own seed.</summary>
        private static int Roll(int seed, int roomIndex, int salt)
        {
            unchecked
            {
                int value = seed;
                value = value * 31 + roomIndex;
                value = value * 31 + salt;
                return value == int.MinValue ? 0 : Math.Abs(value);
            }
        }
    }
}
