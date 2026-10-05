using System;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// How dangerous a particular coordinate has become, and the hard limits on how dangerous it
    /// is ever allowed to be.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"when u add places and events to proper
    /// balance levels of colony wealth and the like so that a solo group has ability to build
    /// and get supplies on backrroms instances and find a way out before dying from metting
    /// monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of
    /// all variations"*.
    ///
    /// **Owner direction, 2026-09-28, the rules this inherits:** a newly opened coordinate
    /// starts quiet; pressure rises only from saved observable causes, never from wall-clock
    /// time, a fresh draw per load, or the mere fact a gate is open; caps on simultaneous
    /// encounters where raising a cap is itself a recorded progression step; quiet stretches
    /// are required content; several open gates never sum into one escalating number; and
    /// reopening a known space resumes its saved pressure without rerolling up to punish a
    /// revisit or down to make one safe.
    ///
    /// ## Colony wealth is the pacing input, and it is the owner's choice
    ///
    /// The ladder specification had deliberately left *what pressure scales against* open. The
    /// owner has now answered it: **colony wealth**. That is the right answer for a RimWorld
    /// mod — it is the input the game's own storyteller uses, so a Backrooms coordinate paces
    /// against the same curve as everything else the player is facing, instead of running a
    /// private difficulty track beside it.
    ///
    /// **Wealth raises the ceiling; it never raises the floor.** A colony that gets rich makes
    /// deep spaces more dangerous, but it can never retroactively make a space the player
    /// already knows more dangerous than its own history earned — because the history terms are
    /// saved and the wealth term only ever caps them.
    ///
    /// ## What "so that a solo group has ability to ... find a way out before dying" means here
    ///
    /// It is an **acceptance condition on the arithmetic**, not a hope. Three guarantees are
    /// built into this file rather than left to tuning:
    ///
    /// 1. <see cref="MaxSimultaneousEncounters"/> is an **absolute** ceiling. No combination of
    ///    depth, wealth and history can exceed it.
    /// 2. <see cref="QuietRoomFraction"/> of a coordinate's rooms must present nothing at all.
    ///    A space with something in every room fails the direction however well balanced each
    ///    individual encounter is.
    /// 3. A first visit is always <see cref="Band.Quiet"/>. Whatever the colony is worth and
    ///    however deep the space, **walking in is never the dangerous part**.
    /// </summary>
    public static class CoordinatePressureLadder
    {
        /// <summary>The readable bands a coordinate can be in.</summary>
        public enum Band
        {
            /// <summary>Nothing is presented. Required content, not an absence of content.</summary>
            Quiet = 0,

            /// <summary>Signs that something is here. Still nothing that acts.</summary>
            Unsettled = 1,

            /// <summary>Something acts, singly, with a warning first.</summary>
            Active = 2,

            /// <summary>More than one thing acts, and the space stops being forgiving.</summary>
            Hostile = 3,
        }

        /// <summary>
        /// The most things that may ever act at once, at any depth, at any wealth, in any
        /// coordinate. **This is the number that keeps the owner's solo-survivability condition
        /// true**, so it is a constant rather than a curve.
        /// </summary>
        public const int MaxSimultaneousEncounters = 3;

        /// <summary>
        /// The share of a coordinate's rooms that must present nothing, whatever the band.
        /// *"Quiet stretches are required content"* — a space presenting something in every
        /// room fails, however good each individual encounter is.
        /// </summary>
        public const float QuietRoomFraction = 0.5f;

        /// <summary>Openings before history alone can push past <see cref="Band.Unsettled"/>.</summary>
        private const int OpeningsForActive = 3;

        /// <summary>Occupancy, in ticks, that counts as a full unit of operating history.</summary>
        private const int OccupancyUnitTicks = 180000;

        /// <summary>Colony wealth at which the wealth term is considered fully grown.</summary>
        private const float WealthCeiling = 400000f;

        /// <summary>
        /// The band a player can read, as a keyed label.
        ///
        /// The ladder has decided how hostile a space is since 0.8.4-dev -- it drives anomaly
        /// events and gates incursion -- and **was never shown to anybody.** The pacing was
        /// inferable only by being hurt by it, which is the opposite of invariant 28's learnable
        /// rule.
        ///
        /// Keys are literals rather than built from the enum name. A key assembled at run time
        /// cannot be checked in either direction, and this project has caught that pattern five
        /// times.
        /// </summary>
        public static string BandLabelKey(Band band)
        {
            switch (band)
            {
                case Band.Quiet: return "RR_Band_Quiet";
                case Band.Unsettled: return "RR_Band_Unsettled";
                case Band.Active: return "RR_Band_Active";
                case Band.Hostile: return "RR_Band_Hostile";
                default: return "RR_Band_Quiet";
            }
        }

        /// <summary>
        /// The band a coordinate is currently in.
        ///
        /// Every term is either fixed for the space or saved against it. **Nothing here reads
        /// the clock, rolls a number, or asks how many gates are open** — those were the three
        /// failure modes the owner named, and avoiding them is a property of this function
        /// rather than of its callers.
        /// </summary>
        public static Band BandFor(CoordinateRecord coordinate, float colonyWealth)
        {
            if (coordinate == null) { return Band.Quiet; }

            // A first visit is always quiet. Walking in is never the dangerous part, whatever
            // the colony is worth and however deep the space.
            if (coordinate.Openings <= 1) { return Band.Quiet; }

            float score = HistoryScore(coordinate);
            int ceiling = CeilingFor(coordinate.Depth, colonyWealth);

            int band = 0;
            if (score >= 1f) { band = 1; }
            if (score >= 2f) { band = 2; }
            if (score >= 3.5f) { band = 3; }
            return (Band)Mathf.Clamp(band, 0, ceiling);
        }

        /// <summary>
        /// What this coordinate's own history has earned, independent of the colony.
        ///
        /// Saved causes only: how many times it has been opened, and how long the branch's
        /// people have actually worked inside it. Both are things the player did, both are
        /// recorded, and **both survive a reload unchanged** — which is what makes a revisit
        /// resume rather than reroll.
        /// </summary>
        public static float HistoryScore(CoordinateRecord coordinate)
        {
            if (coordinate == null) { return 0f; }
            float openings = Mathf.Clamp01((coordinate.Openings - 1f) / OpeningsForActive) * 2f;
            float occupancy = Mathf.Clamp01(coordinate.OccupancyTicks / (float)OccupancyUnitTicks) * 1.5f;
            float depth = Mathf.Clamp01((coordinate.Depth - 1f) / 5f) * 1.5f;
            return openings + occupancy + depth;
        }

        /// <summary>
        /// The highest band this coordinate may reach, given how deep it is and what the colony
        /// is worth.
        ///
        /// **Wealth raises a ceiling, never a floor.** A colony that gets rich makes deep spaces
        /// able to become dangerous; it does not make a space the player already knows more
        /// dangerous than its own recorded history earned.
        ///
        /// A shallow space stays survivable no matter how rich the branch becomes, which is
        /// deliberate: the shallow Backrooms is where a solo start has to be able to operate.
        /// </summary>
        public static int CeilingFor(int depth, float colonyWealth)
        {
            if (depth <= 1) { return (int)Band.Unsettled; }
            float wealth = Mathf.Clamp01(colonyWealth / WealthCeiling);
            int byDepth = depth >= 4 ? 3 : 2;
            int byWealth = wealth >= 0.6f ? 3 : (wealth >= 0.25f ? 2 : 1);
            return Math.Min(byDepth, byWealth);
        }

        /// <summary>
        /// How many things may act at once in this coordinate right now. Never more than
        /// <see cref="MaxSimultaneousEncounters"/>, whatever the band works out to.
        /// </summary>
        public static int EncounterCapFor(CoordinateRecord coordinate, float colonyWealth)
        {
            Band band = BandFor(coordinate, colonyWealth);
            int byBand;
            switch (band)
            {
                case Band.Quiet: byBand = 0; break;
                case Band.Unsettled: byBand = 0; break;
                case Band.Active: byBand = 1; break;
                default: byBand = MaxSimultaneousEncounters; break;
            }

            // The branch's own earned cap narrows this further. The original direction required
            // that "raising a cap is itself a recorded progression step", so the cap starts at
            // one and only grows when the branch pushes deeper than it ever has -- never past
            // the absolute ceiling, which is what keeps the solo-survivability condition true.
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            int byProgression = campaign == null
                ? RimroomsCampaignComponent.OpeningEncounterCap : campaign.EncounterCap;
            return Math.Min(byBand, byProgression);
        }

        /// <summary>
        /// How many of a coordinate's rooms must present nothing at all, given its room count.
        /// At least one room is always quiet even in a tiny space.
        /// </summary>
        public static int RequiredQuietRooms(int roomCount)
        {
            if (roomCount <= 0) { return 0; }
            return Math.Max(1, Mathf.CeilToInt(roomCount * QuietRoomFraction));
        }

        /// <summary>
        /// Whether a given room in a coordinate is one of its required quiet rooms.
        ///
        /// **This is what turns "quiet stretches are required content" from a principle into a
        /// property of the generator.** The quiet rooms are chosen deterministically from the
        /// coordinate's own seed, so the same space always has the same empty rooms, and the
        /// count comes from <see cref="RequiredQuietRooms"/> rather than from chance — a run of
        /// unlucky rolls can never produce a coordinate with something in every room.
        ///
        /// Chosen by ranking every room's hash and taking the lowest, which distributes the
        /// quiet rooms through the space instead of clustering them at one end.
        /// </summary>
        public static bool IsQuietRoom(int coordinateSeed, int roomIndex, int roomCount)
        {
            if (roomCount <= 0) { return true; }
            int required = RequiredQuietRooms(roomCount);
            if (required >= roomCount) { return true; }
            int mine = RoomRank(coordinateSeed, roomIndex);
            int lower = 0;
            for (int other = 0; other < roomCount; other++)
            {
                if (other == roomIndex) { continue; }
                int rank = RoomRank(coordinateSeed, other);
                // Ties broken by index so the ordering is total and stable.
                if (rank < mine || (rank == mine && other < roomIndex)) { lower++; }
            }
            return lower < required;
        }

        private static int RoomRank(int coordinateSeed, int roomIndex)
        {
            int rank = Gen.HashCombineInt(coordinateSeed, roomIndex * 7919 + 0x5155);
            return rank < 0 ? ~rank : rank;
        }

        /// <summary>
        /// The colony wealth the ladder should pace against.
        ///
        /// Read from the **player's own maps**, not from the coordinate, because the point of
        /// the owner's direction is that the Backrooms paces against what the branch has built
        /// rather than against itself. A Backrooms map's own wealth is excluded: a coordinate
        /// full of generated furniture is not something the player earned, and counting it
        /// would make a space escalate simply because it was well stocked.
        /// </summary>
        public static float ColonyWealth()
        {
            float total = 0f;
            System.Collections.Generic.List<Map> maps = Find.Maps;
            if (maps == null) { return 0f; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map.wealthWatcher == null) { continue; }
                if (!map.IsPlayerHome) { continue; }
                if (Economy.OddOriginService.IsBackroomsMap(map)) { continue; }
                total += map.wealthWatcher.WealthTotal;
            }
            return total;
        }
    }
}
