using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// The bounded-scan rules every adapter family shares. One implementation, because
    /// the rotating-window rule is subtle enough that a per-family copy would drift and
    /// the drift would be invisible: a scan that reads a fixed prefix looks identical
    /// to a correct one until the fifth gate opens.
    ///
    /// The rule: a bounded scan examines a *window* that moves, never a prefix. A
    /// prefix means anything past the cap is starved forever, and this branch can hold
    /// many gates at once. Deterministic with no randomness, so a reload cannot change
    /// what a pass sees.
    /// </summary>
    internal static class ConnectedWorkScan
    {
        /// <summary>How many connected maps one planning pass may look at.</summary>
        internal const int MaximumConnectedMapsPerPass = 4;

        /// <summary>
        /// A deterministic rotating offset over <paramref name="count"/> positions.
        /// Different workers and successive passes start in different places, so the
        /// whole collection is covered over time.
        /// </summary>
        internal static int RotationOffset(int count, Pawn pawn)
        {
            if (count <= 1 || pawn == null) { return 0; }
            long turn = Find.TickManager.TicksGame / RimroomsConnectedWorkComponent.PlanningCooldownTicks;
            int offset = (int)((turn + pawn.thingIDNumber) % count);
            return offset < 0 ? offset + count : offset;
        }

        /// <summary>
        /// Where a window of <paramref name="budget"/> items should start so it always
        /// fits inside <paramref name="count"/> and still reaches every position across
        /// successive passes. A pass therefore spends its whole budget instead of being
        /// cut short near the end of the collection.
        /// </summary>
        internal static int WindowStart(int count, int budget, Pawn pawn)
        {
            return count <= budget ? 0 : RotationOffset(count - budget + 1, pawn);
        }

        /// <summary>
        /// The branch's other loaded maps, from a rotating start so no connected space
        /// can sit permanently past the cap.
        /// </summary>
        internal static List<Map> ConnectedMaps(RimroomsCampaignComponent campaign, Map home, Pawn pawn)
        {
            var result = new List<Map>();
            if (campaign == null || home == null) { return result; }
            List<Map> maps = Find.Maps;
            if (maps.Count == 0) { return result; }
            int start = RotationOffset(maps.Count, pawn);
            for (int step = 0; step < maps.Count && result.Count < MaximumConnectedMapsPerPass; step++)
            {
                Map map = maps[(start + step) % maps.Count];
                if (map == home || !campaign.OwnsMap(map)) { continue; }
                result.Add(map);
            }
            return result;
        }
    }
}
