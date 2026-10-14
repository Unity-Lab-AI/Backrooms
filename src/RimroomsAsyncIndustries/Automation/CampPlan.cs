using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The camp planner: the ground around the camp read before anything is placed, so rooms get two doors on different
    /// sides, every door opens onto a lane kept clear by every later plan, rooms keep a gap between their rings, and the
    /// walls that flank a door go up only after the door stands.
    ///
    /// Owner, 2026-10-14, verbatim: "she only buildt one door on the main rooms and now she is blocked ina nd gonna dy come on
    /// she need dynamic planing and relationships on the map contours and what can be defensible and where exits and main
    /// defensive appraches to her camp/base are" and "why the fuck is she blocvking both sides of doors with walls".
    /// In run 5 the storage room's one door opened onto the shelter's wall and the shelter's door onto the storage room's
    /// wall: two rooms, two doors, both blocked, the crew sealed in.
    ///
    ///   {"cmd":"camp_plan"}   the survey: rock per side, the open front, the mountain back, the lanes kept clear
    ///   {"cmd":"free"}        every colonist who cannot reach the map edge gets a way out (a plan cancelled or a wall marked
    ///                         to deconstruct on the edge of the room they stand in)
    /// </summary>
    internal static class CampPlan
    {
        public static readonly IntVec3[] Dirs = { new IntVec3(0, 0, 1), new IntVec3(1, 0, 0), new IntVec3(0, 0, -1), new IntVec3(-1, 0, 0) };
        public static readonly string[] DirNames = { "north", "east", "south", "west" };
        private const int Reach = 30;        // how far the survey looks from the anchor
        private const int LaneLen = 3;       // cells outside a door kept clear

        private static bool Solid(Map map, IntVec3 c)
        {
            if (!c.InBounds(map)) return true;
            Building e = c.GetEdifice(map);
            return e != null && e.def.Fillage == FillCategory.Full && !(e is Building_Door);
        }

        /// <summary>Rock fraction per side (north, east, south, west) within Reach of the anchor.</summary>
        public static double[] Survey(Map map, IntVec3 anchor)
        {
            var frac = new double[4];
            for (int d = 0; d < 4; d++)
            {
                int solid = 0, n = 0;
                IntVec3 dir = Dirs[d];
                IntVec3 side = new IntVec3(dir.z, 0, dir.x);          // the perpendicular
                for (int k = 3; k <= Reach; k++)
                    for (int s = -8; s <= 8; s++)
                    {
                        IntVec3 c = anchor + dir * k + side * s;
                        if (!c.InBounds(map)) { solid++; n++; continue; }
                        if (map.fogGrid.IsFogged(c)) continue;
                        n++;
                        if (Solid(map, c)) solid++;
                    }
                frac[d] = n == 0 ? 1.0 : (double)solid / n;
            }
            return frac;
        }

        public static int Front(double[] frac) { int best = 0; for (int d = 1; d < 4; d++) if (frac[d] < frac[best]) best = d; return best; }
        public static int Back(double[] frac) { int best = 0; for (int d = 1; d < 4; d++) if (frac[d] > frac[best]) best = d; return best; }

        /// <summary>Is this cell inside a door lane some plan keeps clear?</summary>
        public static bool InLane(RimroomsCampComponent comp, IntVec3 c) => comp != null && comp.lanes != null && comp.lanes.Contains(c);

        /// <summary>A cell is open for a wall ring: open ground, no plan, no lane, no building (ours or rock) in the 8 cells around it.</summary>
        public static bool RingCellFree(Map map, RimroomsCampComponent comp, IntVec3 c)
        {
            if (!c.InBounds(map) || map.fogGrid.IsFogged(c) || !c.Standable(map) || c.GetEdifice(map) != null) return false;
            if (c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) return false;
            if (InLane(comp, c) || RoomSite.Geyser(map, c)) return false;
            TerrainDef terr = c.GetTerrain(map);
            if (terr.affordances == null || !terr.affordances.Contains(TerrainAffordanceDefOf.Heavy)) return false;
            // a one-cell gap from any other wall or plan: two rings side by side blocked each other's doors (run 5)
            foreach (IntVec3 o in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)))
            {
                if (!o.InBounds(map)) continue;
                if (o.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) return false;
                Building e = o.GetEdifice(map);
                if (e != null && e.Faction == Faction.OfPlayer) return false;
            }
            return true;
        }

        private static bool LaneOpen(Map map, RimroomsCampComponent comp, IntVec3 door, IntVec3 outward)
        {
            for (int k = 1; k <= LaneLen; k++)
            {
                IntVec3 c = door + outward * k;
                if (!c.InBounds(map) || Solid(map, c) || !c.Standable(map) || map.fogGrid.IsFogged(c)) return false;
                if (c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) return false;
                if (c.GetEdifice(map) != null) return false;
            }
            return true;
        }

        /// <summary>
        /// Up to two door cells on a ring, on different sides: the first on the side facing the open front (or the hint:
        /// the crew, the other room), the second on another side -- each with a clear lane outside it, reserved in the
        /// camp's lanes so no later plan walls it. Corner cells are never doors.
        /// </summary>
        public static List<IntVec3> DoorSites(Map map, RimroomsCampComponent comp, CellRect ring, IntVec3 hint, out List<IntVec3> lanes)
        {
            lanes = new List<IntVec3>();
            var doors = new List<IntVec3>();
            double[] frac = Survey(map, ring.CenterCell);
            int front = Front(frac);
            // side order: toward the hint first (if it is outside the ring), then the open front, then the rest by openness
            var order = new List<int>();
            if (hint.IsValid && !ring.Contains(hint))
            {
                int dx = hint.x - ring.CenterCell.x, dz = hint.z - ring.CenterCell.z;
                order.Add(Math.Abs(dx) >= Math.Abs(dz) ? (dx > 0 ? 1 : 3) : (dz > 0 ? 0 : 2));
            }
            foreach (int d in Enumerable.Range(0, 4).OrderBy(d => frac[d])) if (!order.Contains(d)) order.Add(d);
            foreach (int d in order)
            {
                if (doors.Count >= 2) break;
                IntVec3 outward = Dirs[d];
                // candidate cells along that side, nearest the side's middle first, corners excluded
                // never a corner, never beside a corner (owner, 2026-10-14: "one is on the corner with no corner wall"): at least
                // two wall cells between a door and the ring's corner, candidates from the side's middle outward
                var side = ring.EdgeCells.Where(c => (d == 0 && c.z == ring.maxZ) || (d == 2 && c.z == ring.minZ) || (d == 1 && c.x == ring.maxX) || (d == 3 && c.x == ring.minX))
                                         .Where(c => Math.Min(c.x - ring.minX, ring.maxX - c.x) >= 2 || Math.Min(c.z - ring.minZ, ring.maxZ - c.z) >= 2)
                                         .Where(c => !((c.x == ring.minX || c.x == ring.maxX) && (c.z == ring.minZ || c.z == ring.maxZ)))
                                         .Where(c => (d == 0 || d == 2) ? Math.Min(c.x - ring.minX, ring.maxX - c.x) >= 2 : Math.Min(c.z - ring.minZ, ring.maxZ - c.z) >= 2)
                                         .OrderBy(c => Math.Abs(c.x - ring.CenterCell.x) + Math.Abs(c.z - ring.CenterCell.z)).ToList();
                foreach (IntVec3 c in side)
                {
                    if (doors.Any(o => o.DistanceTo(c) < 3f)) continue;
                    if (!LaneOpen(map, comp, c, outward)) continue;
                    doors.Add(c);
                    for (int k = 1; k <= LaneLen; k++) lanes.Add(c + outward * k);
                    break;
                }
            }
            if (comp != null)
            {
                if (comp.lanes == null) comp.lanes = new List<IntVec3>();
                foreach (IntVec3 l in lanes) if (!comp.lanes.Contains(l)) comp.lanes.Add(l);
            }
            return doors;
        }

        /// <summary>
        /// Support columns for a roof: RimWorld holds a roof only within RoofMaxSupportDistance (6) cells of a wall or column,
        /// so an inside wider or taller than 12 gets a grid of columns at 12-cell spacing, 6 in from the walls (owner, 2026-10-14:
        /// "room is too big to support a roof without walls as columns in the middle and for big rooms need rows and columns of
        /// columns"). Returns how many were planned.
        /// </summary>
        public static int Supports(Map map, CellRect inside, ThingDef stuff)
        {
            const int reach = 6;
            if (inside.Width <= 2 * reach && inside.Height <= 2 * reach) return 0;
            ThingDef column = DefDatabase<ThingDef>.GetNamedSilentFail("Column") ?? ThingDefOf.Wall;
            var xs = new List<int>(); var zs = new List<int>();
            if (inside.Width > 2 * reach) for (int x = inside.minX + reach; x <= inside.maxX - reach + (2 * reach - 1); x += 2 * reach) { if (x > inside.maxX - 1) break; xs.Add(x); }
            else xs.Add(inside.CenterCell.x);
            if (inside.Height > 2 * reach) for (int z = inside.minZ + reach; z <= inside.maxZ - reach + (2 * reach - 1); z += 2 * reach) { if (z > inside.maxZ - 1) break; zs.Add(z); }
            else zs.Add(inside.CenterCell.z);
            int placed = 0;
            foreach (int x in xs)
                foreach (int z in zs)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map) || c.GetEdifice(map) != null || c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) continue;
                    if (!GenConstruct.CanPlaceBlueprintAt(column, c, Rot4.North, map, false, null, null, stuff).Accepted) continue;
                    GenConstruct.PlaceBlueprintForBuild(column, c, map, Rot4.North, Faction.OfPlayer, stuff);
                    placed++;
                }
            return placed;
        }

        /// <summary>The two ring cells beside a door along its wall: placed only once the door stands.</summary>
        public static List<IntVec3> Flanks(CellRect ring, IntVec3 door)
        {
            bool horizontal = door.z == ring.minZ || door.z == ring.maxZ;
            var a = horizontal ? new IntVec3(door.x - 1, 0, door.z) : new IntVec3(door.x, 0, door.z - 1);
            var b = horizontal ? new IntVec3(door.x + 1, 0, door.z) : new IntVec3(door.x, 0, door.z + 1);
            return new List<IntVec3> { a, b }.Where(c => ring.EdgeCells.Contains(c)).ToList();
        }

        /// <summary>The survey as a line for her and for the owner.</summary>
        public static string Report(Map map, Dictionary<string, string> a)
        {
            IntVec3 anchor = CampAnchor.Get(map);
            if (!anchor.IsValid) return "refused: no crew on this map";
            RimroomsCampComponent comp = map.GetComponent<RimroomsCampComponent>();
            double[] frac = Survey(map, anchor);
            int front = Front(frac), back = Back(frac);
            string sides = string.Join(", ", Enumerable.Range(0, 4).Select(d => DirNames[d] + " " + (int)Math.Round(frac[d] * 100) + "% rock"));
            int lanes = comp?.lanes?.Count ?? 0, flanks = comp?.FlankCount ?? 0;
            return "ok: camp at " + anchor.x + "," + anchor.z + " -- " + sides + "; the open FRONT is " + DirNames[front] + " (the raid's approach: barricades and the gun line go there), " +
                   "the BACK is " + DirNames[back] + " (rooms put their blind wall there); doors face the front and one other side, each with a " + LaneLen +
                   "-cell lane kept clear (" + lanes + " lane cells reserved); " + flanks + " door-flank walls wait for their doors to stand";
        }

        /// <summary>Everyone who cannot reach the map edge gets a way out.</summary>
        public static string Free(Map map, Dictionary<string, string> a)
        {
            var done = new List<string>();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.ToList())
            {
                if (p.Dead || !p.Spawned) continue;
                if (map.reachability.CanReachMapEdge(p.Position, TraverseParms.For(p))) continue;
                // the room they stand in (or a widening ring around them): its edge holds the plan or the wall to remove
                Room room = p.Position.GetRoom(map);
                IEnumerable<IntVec3> border = room != null && !room.PsychologicallyOutdoors
                    ? room.BorderCells
                    : GenRadial.RadialCellsAround(p.Position, 6f, true).Where(c => c.InBounds(map));
                int cancelled = 0; Building wall = null;
                foreach (IntVec3 c in border)
                {
                    foreach (Thing t in c.GetThingList(map).ToList())
                        if ((t.def.IsBlueprint || t.def.IsFrame) && t.Faction == Faction.OfPlayer) { t.Destroy(DestroyMode.Cancel); cancelled++; }
                    if (wall == null && c.GetEdifice(map) is Building b && b.Faction == Faction.OfPlayer && !(b is Building_Door) && b.def.Fillage == FillCategory.Full)
                        wall = b;
                }
                if (cancelled == 0 && wall != null && map.designationManager.DesignationOn(wall, DesignationDefOf.Deconstruct) == null)
                {
                    map.designationManager.AddDesignation(new Designation(wall, DesignationDefOf.Deconstruct));
                    done.Add(p.LabelShort + ": wall at " + wall.Position.x + "," + wall.Position.z + " marked to deconstruct");
                }
                else if (cancelled > 0)
                    done.Add(p.LabelShort + ": " + cancelled + " plan(s) on the room's edge cancelled");
                else
                    done.Add(p.LabelShort + ": trapped, and no wall or plan of ours on the edge -- mine or deconstruct by hand");
            }
            return done.Count == 0 ? "ok: nobody is walled in" : "ok: " + string.Join("; ", done) + " -- Construction on, time running, then plan the door again";
        }
    }
}
