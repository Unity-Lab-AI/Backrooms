using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// Where a start's hand-authored layout actually sits on the map the player chose.
    ///
    /// ## Why this exists
    ///
    /// Owner direction, 2026-09-30, verbatim: *"the map size is selected on world seteup before
    /// world generation by the player and they select the tile they appear in so the store gets
    /// genreeate in that selected tiles map"*.
    ///
    /// **Until 0.12.45-dev the mod threw that choice away.** `ScenPart_RimroomsStart` did
    /// `Find.GameInitData.mapSize = startDef.mapSize`, forcing **50 for the Store and 60 for the
    /// others** — against RimWorld's smallest new-game option of 200. The owner's report was
    /// *"not the map i chose ... i was stuck in a super micro blocked in area"*, and it was
    /// literally accurate:
    ///
    ///     start             map      footprint   share of map   margin
    ///     Async             60x60    44x44       54%            8 cells
    ///     Furniture Store   50x50    34x30       41%            8 cells
    ///
    /// A 50x50 map is **2,500 cells against a default 250x250 map's 62,500** — one twenty-fifth
    /// the area, most of it one building. Nothing was sealed; every layout flood-fills to 100%
    /// reachable from its arrival cell. The map itself was the cage.
    ///
    /// ## What this changes, and what it deliberately does not
    ///
    /// The defs keep their coordinates. Rewriting roughly a hundred hand-placed cells across
    /// three starts would be a large diff with no way to check it, and the coordinates encode a
    /// deliberate layout — which room is the stockroom, which door is the back door. So the
    /// **layout is treated as relative** and this offsets it onto whatever map exists, centred.
    ///
    /// Every consumer must apply the same offset or the facility tears apart: rooms, doors,
    /// buildings, conduits, the arrival cell, the stock cell and the emergence door. That is why
    /// this is one shared helper rather than arithmetic at each call site.
    /// </summary>
    internal static class HeadquartersLayout
    {
        /// <summary>
        /// Free cells kept between the layout and the map edge. Core's own map edge is not
        /// buildable and mountains generate inward, so a layout flush to the border would be
        /// unreachable on one side.
        /// </summary>
        internal const int EdgeMargin = 8;

        /// <summary>
        /// The layout's own bounding box, in the coordinates the def is written in.
        ///
        /// Taken from the rooms alone. Buildings, doors and conduits are placed inside rooms by
        /// construction -- the generator throws if they are not -- so the rooms bound everything.
        /// </summary>
        internal static CellRect Extent(RimroomsStartDef start)
        {
            if (start == null || start.rooms == null || start.rooms.Count == 0)
            { return CellRect.Empty; }
            int minX = int.MaxValue, minZ = int.MaxValue, maxX = int.MinValue, maxZ = int.MinValue;
            foreach (RimroomsRoomPlan room in start.rooms)
            {
                CellRect rect = room.Rect;
                if (rect.minX < minX) { minX = rect.minX; }
                if (rect.minZ < minZ) { minZ = rect.minZ; }
                if (rect.maxX > maxX) { maxX = rect.maxX; }
                if (rect.maxZ > maxZ) { maxZ = rect.maxZ; }
            }
            return CellRect.FromLimits(minX, minZ, maxX, maxZ);
        }

        /// <summary>
        /// The smallest map this layout can sit on with its margins. Used by the setup page and
        /// by the generator's own guard, so the number a player is shown is the number enforced.
        /// </summary>
        internal static int MinimumMapSize(RimroomsStartDef start)
        {
            CellRect extent = Extent(start);
            int span = Mathf(extent.Width, extent.Height);
            return span + EdgeMargin * 2;
        }

        private static int Mathf(int a, int b) { return a > b ? a : b; }

        /// <summary>
        /// How far to shift every authored cell so the layout lands centred on this map.
        ///
        /// Clamped so the layout never crosses an edge even on a map barely large enough, and
        /// returns zero when the map is exactly the size the layout was authored against -- so a
        /// 60x60 map places the Async layout precisely where its coordinates say, unchanged.
        /// </summary>
        internal static IntVec3 Offset(RimroomsStartDef start, IntVec3 mapSize)
        {
            CellRect extent = Extent(start);
            if (!extent.IsEmpty)
            {
                int offsetX = (mapSize.x - extent.Width) / 2 - extent.minX;
                int offsetZ = (mapSize.z - extent.Height) / 2 - extent.minZ;
                // Never push the layout off an edge, and never pull it back past its own origin
                // on a map that is only just big enough.
                int maxX = mapSize.x - EdgeMargin - 1 - extent.maxX;
                int maxZ = mapSize.z - EdgeMargin - 1 - extent.maxZ;
                int minX = EdgeMargin - extent.minX;
                int minZ = EdgeMargin - extent.minZ;
                if (offsetX > maxX) { offsetX = maxX; }
                if (offsetZ > maxZ) { offsetZ = maxZ; }
                if (offsetX < minX) { offsetX = minX; }
                if (offsetZ < minZ) { offsetZ = minZ; }
                return new IntVec3(offsetX, 0, offsetZ);
            }
            return IntVec3.Zero;
        }

        /// <summary>Whether this map can hold this layout at all.</summary>
        internal static bool Fits(RimroomsStartDef start, IntVec3 mapSize)
        {
            CellRect extent = Extent(start);
            return extent.IsEmpty
                || (mapSize.x >= extent.Width + EdgeMargin * 2
                    && mapSize.z >= extent.Height + EdgeMargin * 2);
        }

        /// <summary>Every room rect, shifted.</summary>
        internal static List<CellRect> Rooms(RimroomsStartDef start, IntVec3 offset)
        {
            var found = new List<CellRect>();
            if (start == null || start.rooms == null) { return found; }
            foreach (RimroomsRoomPlan room in start.rooms)
            { found.Add(room.Rect.MovedBy(new IntVec2(offset.x, offset.z))); }
            return found;
        }
    }
}
