using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Replacing the mountain's stone walls with built ones without bringing the roof down.
    ///
    /// Owner, 2026-10-13, verbatim: "the main bas mining and construction work begins into the moutian makling sure of
    /// no collapses when repalacing stone mountain walls for like steel and other materials". A roofed cell stands
    /// while something that holds a roof (a wall, a column, natural rock) is within RoofCollapseUtility's support
    /// distance; mine the last holder of a cell and that cell's roof falls -- under a thick mountain roof that kills
    /// whoever stands there. So a cell of natural rock is only swapped when every roofed cell it supports keeps another
    /// holder after it is gone, and the built wall goes in the moment the cell is clear (RimroomsCampComponent lays the
    /// blueprint, saved with the map, so the swap survives a reload and the "mine then build" order never needs her).
    ///   {"cmd":"wall_swap","x":"..","z":"..","w":"..","h":"..","stuff":"Steel"}   natural rock in the rect designated to mine,
    ///          one cell at a time in a safe order; a built wall of that material is laid on each cell as it clears.
    ///          Unsafe cells are skipped and named: a column (build def Column) beside them first, then wall_swap again.
    /// </summary>
    internal static class WallSwap
    {
        private static bool HoldsRoof(Map map, IntVec3 c, IntVec3 except)
        {
            if (c == except || !c.InBounds(map)) return false;
            Building e = c.GetEdifice(map);
            return e != null && e.def.holdsRoof;
        }

        private static bool RockWall(Map map, IntVec3 c)
        {
            Building e = c.InBounds(map) ? c.GetEdifice(map) : null;
            return e != null && e.def.building != null && e.def.building.isNaturalRock;
        }

        /// <summary>Can this cell go without any roofed cell losing its last support?</summary>
        public static bool SafeToRemove(Map map, IntVec3 c, HashSet<IntVec3> alsoGone)
        {
            float d = RoofCollapseUtility.RoofMaxSupportDistance;
            foreach (IntVec3 r in GenRadial.RadialCellsAround(c, d, true))
            {
                if (!r.InBounds(map) || !r.Roofed(map)) continue;
                if (r == c) continue;                                     // the roof over the cell itself falls with the wall: fine, it is a wall
                bool held = GenRadial.RadialCellsAround(r, d, true).Any(o => !alsoGone.Contains(o) && HoldsRoof(map, o, c));
                if (!held) return false;
            }
            return true;
        }

        public static string Swap(Map map, Dictionary<string, string> a)
        {
            int x = Arg(a, "x", -1), z = Arg(a, "z", -1), w = Math.Max(1, Math.Min(20, Arg(a, "w", 1))), h = Math.Max(1, Math.Min(20, Arg(a, "h", 1)));
            if (x < 0 || z < 0) return "refused: x z (and w h) of the rock to swap are needed";
            CellRect rect = new CellRect(x, z, w, h).ClipInsideMap(map);
            a.TryGetValue("stuff", out string stuffName);
            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(string.IsNullOrEmpty(stuffName) ? "Steel" : stuffName);
            if (stuff == null || !stuff.IsStuff) return "refused: no stuff named " + stuffName + " (Steel, Plasteel, BlocksGranite, ...)";
            if (!ThingDefOf.Wall.stuffCategories.Any(sc => stuff.stuffProps != null && stuff.stuffProps.categories.Contains(sc)))
                return "refused: a wall cannot be made of " + stuff.label;
            RimroomsCampComponent comp = map.GetComponent<RimroomsCampComponent>();
            if (comp == null) return "refused: no camp component on this map";
            var gone = new HashSet<IntVec3>();
            int marked = 0, already = 0, notRock = 0, fogged = 0;
            var unsafeCells = new List<IntVec3>();
            foreach (IntVec3 c in rect)
            {
                if (map.fogGrid.IsFogged(c)) { fogged++; continue; }
                if (!RockWall(map, c)) { notRock++; continue; }
                if (map.designationManager.DesignationAt(c, DesignationDefOf.Mine) != null) { already++; continue; }
                if (!SafeToRemove(map, c, gone)) { unsafeCells.Add(c); continue; }
                map.designationManager.AddDesignation(new Designation(c, DesignationDefOf.Mine));
                gone.Add(c);
                comp.Queue(c, stuff);
                marked++;
            }
            if (marked == 0 && already == 0)
                return "refused: nothing to swap in that " + rect.Width + "x" + rect.Height +
                       (unsafeCells.Count > 0 ? " -- " + unsafeCells.Count + " rock cell(s) hold the last support of a roof: build def Column beside " +
                                                 unsafeCells[0].x + "," + unsafeCells[0].z + " first, then wall_swap again" : "") +
                       (notRock > 0 ? " (" + notRock + " not rock)" : "") + (fogged > 0 ? " (" + fogged + " fogged)" : "");
            return "ok: " + marked + " rock cell(s) marked to mine, each gets a " + stuff.label + " wall the moment it is clear (" + comp.PendingCount +
                   " queued on this map)" + (already > 0 ? ", " + already + " already marked" : "") +
                   (unsafeCells.Count > 0 ? "; " + unsafeCells.Count + " cell(s) SKIPPED -- they hold the last support of a roof: build def Column beside " +
                                            string.Join(" ", unsafeCells.Take(4).Select(u => u.x + "," + u.z)) + " first, then wall_swap again" : "") +
                   (notRock > 0 ? "; " + notRock + " not rock" : "") + " -- Mining and Construction on, and " +
                   (stuff.label) + " in stock";
        }

        private static int Arg(Dictionary<string, string> a, string k, int d) =>
            a.TryGetValue(k, out string s) && int.TryParse(s, out int v) ? v : d;
    }
}
