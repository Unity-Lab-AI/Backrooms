using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Something is not where you left it.
    ///
    /// **Prep material, `UNIVERSE_ADAPTATION.md`, on how ordinary interiors become uncanny:**
    /// *"Use intentional spatial changes such as a shifted doorway, impossible adjacency,
    /// repeated hall, changed room dimensions, or **a feature that has moved since the last
    /// visit**."*
    ///
    /// Every other item on that list was built. This one was not, and it is the only one that
    /// **depends on the player's own memory** rather than on the geometry: the room is the
    /// room, the route is the route, and the workbench is four cells from where it was.
    ///
    /// ## Why this is not the rearrangement anomaly
    ///
    /// `RR_Anomaly_Rearrangement` moves **loose items during a session**, at depth four and
    /// above, and announces itself. This moves **fixtures between visits**, silently, and it
    /// works at any depth a coordinate has been opened twice.
    ///
    /// They are opposites on purpose. An anomaly you are told about is a thing that happened
    /// to you. A chair that is somewhere else is a thing that happened **while you were not
    /// there**, which is the older and worse idea.
    ///
    /// ## Nothing is told to the player
    ///
    /// No letter, no message, no alert. A player who never notices has lost nothing, and a
    /// player who does notice found it themselves. It is recorded in the company log, so the
    /// discovery is checkable after the fact rather than announced before it.
    ///
    /// This does not breach the warning-first rule: that rule governs **threats**, and a
    /// bench in a different corner cannot hurt anybody.
    ///
    /// ## What it will never touch
    ///
    /// - **Anything the player built or owns.** Moving somebody's own construction is not
    ///   uncanny, it is a bug report.
    /// - **The way back.** The return threshold is excluded, as it is from every other system
    ///   here.
    /// - **Doors, and anything on a room's edge.** Displacement happens strictly inside the
    ///   room interior the dressing pass already treats as safe, so a moved fixture can never
    ///   seal a route or block a doorway.
    /// </summary>
    public static class RevisitDisplacement
    {
        /// <summary>Most fixtures that may move on any one return. Deliberately small.</summary>
        private const int MaxMoved = 3;

        /// <summary>Openings after which a second fixture may move, and then a third.</summary>
        private const int OpeningsPerExtra = 3;

        /// <summary>Salt for the once-per-visit roll, distinct from the per-candidate ones.</summary>
        private const int VisitSalt = 6151;

        internal static void OnArrival(Map map, CoordinateRecord coordinate)
        {
            if (map == null || coordinate == null) { return; }
            // A first visit has no "last visit" to differ from.
            if (coordinate.Openings <= 1) { return; }

            // Not every return. An offline proof showed that with a normally dressed
            // coordinate this fired on *every single* visit, which is mechanical rather than
            // uncanny: a player would simply learn that returning moves things. The unease
            // depends on not being certain whether you misremembered, so roughly a third of
            // returns are left exactly as they were.
            //
            // **RR_Cap_CoordinateAtlas** (Spatial mapping and topology, tier 0) raises that share
            // from about a third to about a half. A branch that keeps a real atlas is wrong about
            // where things were less often — which is a reassurance rather than a fix, because
            // the space still moves them and the atlas only means you notice.
            Company.RimroomsCampaignComponent atlasCampaign = Current.Game == null
                ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            int quietShare = atlasCampaign != null && atlasCampaign.HasCapability("RR_Cap_CoordinateAtlas") ? 2 : 3;
            if (Roll(coordinate.Seed, coordinate.Openings, VisitSalt) % quietShare == 0) { return; }

            int wanted = Math.Min(MaxMoved, 1 + (coordinate.Openings - 2) / OpeningsPerExtra);
            if (wanted <= 0) { return; }

            var site = map.Parent as RimroomsDestinationMapParent;
            Thing threshold = site == null ? null : site.ReturnAnchor;

            List<Thing> candidates = Candidates(map, coordinate, threshold);
            if (candidates.Count == 0) { return; }

            int moved = 0;
            for (int index = 0; index < candidates.Count && moved < wanted; index++)
            {
                // Rolled per candidate from the coordinate's own seed and this visit number, so
                // the same return produces the same change on every machine and a reload does
                // not reroll it into a different room.
                int roll = Roll(coordinate.Seed, coordinate.Openings, index);
                if (roll % 3 != 0) { continue; }
                if (TryDisplace(map, coordinate, candidates[index], roll)) { moved++; }
            }

            if (moved > 0)
            {
                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                if (campaign != null && campaign.CanOperate)
                {
                    campaign.RecordEvent("RR_Event_ThingsMovedSinceLastVisit", coordinate.Id,
                        moved.ToString("N0"));
                }
            }
        }

        /// <summary>
        /// Generated fixtures only, in a stable order.
        ///
        /// Ownership is the whole test: anything generation placed has no faction, and
        /// anything the player built belongs to the player. That one check keeps a colonist's
        /// own work out of this without needing a list of what they might have built.
        /// </summary>
        private static List<Thing> Candidates(Map map, CoordinateRecord coordinate, Thing threshold)
        {
            var found = new List<Thing>();
            IReadOnlyList<RoomRecord> rooms = coordinate.Rooms;
            if (rooms == null) { return found; }

            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null) { continue; }
                if (string.Equals(room.FamilyId, "threshold_room", StringComparison.Ordinal)) { continue; }
                CellRect interior = room.Bounds.ContractedBy(1);
                foreach (IntVec3 cell in interior)
                {
                    if (!cell.InBounds(map)) { continue; }
                    List<Thing> here = cell.GetThingList(map);
                    for (int item = 0; item < here.Count; item++)
                    {
                        Thing thing = here[item];
                        if (!(thing is Building) || thing is Building_Door) { continue; }
                        if (thing == threshold || thing.Faction != null) { continue; }
                        if (thing.def == null || thing.def.size.x > 2 || thing.def.size.z > 2) { continue; }
                        if (thing.Position != cell) { continue; }
                        found.Add(thing);
                    }
                }
            }

            // Ordinal by position then id: def and list order vary with the mod list, and two
            // players returning to the same coordinate must find the same thing moved.
            found.Sort(delegate(Thing left, Thing right)
            {
                int byX = left.Position.x.CompareTo(right.Position.x);
                if (byX != 0) { return byX; }
                int byZ = left.Position.z.CompareTo(right.Position.z);
                return byZ != 0 ? byZ : left.thingIDNumber.CompareTo(right.thingIDNumber);
            });
            return found;
        }

        /// <summary>
        /// Puts one fixture somewhere else in its own room.
        ///
        /// It stays in the same room deliberately. A bench that has crossed the building is a
        /// glitch; a bench four cells from where it stood is a memory you no longer trust.
        /// </summary>
        private static bool TryDisplace(Map map, CoordinateRecord coordinate, Thing thing, int roll)
        {
            RoomRecord room = RoomOf(coordinate, thing.Position);
            if (room == null) { return false; }
            CellRect interior = room.Bounds.ContractedBy(1);
            if (interior.Area <= 1) { return false; }

            var open = new List<IntVec3>();
            foreach (IntVec3 cell in interior)
            {
                if (cell == thing.Position || !cell.InBounds(map) || !cell.Standable(map)) { continue; }
                if (cell.GetThingList(map).Count > 0) { continue; }
                if (!GenSpawn.CanSpawnAt(thing.def, cell, map, thing.Rotation, canWipeEdifices: false)) { continue; }
                open.Add(cell);
            }
            if (open.Count == 0) { return false; }
            open.Sort(delegate(IntVec3 left, IntVec3 right)
            {
                int byX = left.x.CompareTo(right.x);
                return byX != 0 ? byX : left.z.CompareTo(right.z);
            });

            IntVec3 destination = open[roll % open.Count];
            Rot4 rotation = thing.Rotation;
            try
            {
                thing.DeSpawn();
                GenSpawn.Spawn(thing, destination, map, rotation, WipeMode.Vanish);
                return thing.Spawned && thing.Position == destination;
            }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms][Generation] A fixture could not be displaced on return; "
                    + "it is left where it was: " + error.Message);
                if (!thing.Spawned && !thing.Destroyed)
                { GenSpawn.Spawn(thing, thing.Position, map, rotation, WipeMode.Vanish); }
                return false;
            }
        }

        private static RoomRecord RoomOf(CoordinateRecord coordinate, IntVec3 cell)
        {
            IReadOnlyList<RoomRecord> rooms = coordinate.Rooms;
            if (rooms == null) { return null; }
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room != null && room.Bounds.Contains(cell)) { return room; }
            }
            return null;
        }

        private static int Roll(int seed, int openings, int index)
        {
            unchecked
            {
                int value = seed;
                value = value * 31 + openings * 7919;
                value = value * 31 + index * 104729;
                return value == int.MinValue ? 0 : Math.Abs(value);
            }
        }
    }
}
