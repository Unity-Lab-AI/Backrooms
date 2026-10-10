using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Setup tools that do the spatial part for the model. Owner, 2026-10-10: "is it just too dumb to do this" /
    /// "go" -- the local model decides WHAT (explore, store food, beds); this code decides WHERE, because picking
    /// valid cells (not fogged, not walls, roofed, free) is exactly what a small model gets wrong.
    ///   {"cmd":"rooms"}                          every indoor room: id, cells, roofed, fogged %, beds, centre
    ///   {"cmd":"explore"}                         each idle colonist walks to the nearest unexplored room
    ///   {"cmd":"stockpile_room","mode":"food|nofood","room":"<id>|auto"}  zone a whole explored room, filter set
    ///   {"cmd":"beds"}                            a bed blueprint for every colonist without one
    /// </summary>
    internal static class SetupTools
    {
        private static IEnumerable<Room> IndoorRooms(Map map)
        {
            return map.regionGrid.AllRooms.Where(r => r != null && !r.PsychologicallyOutdoors && !r.IsDoorway &&
                                                      !r.TouchesMapEdge && r.CellCount >= 4 && r.CellCount < 2500);
        }

        private static float FoggedShare(Map map, Room r)
        {
            int f = 0, n = 0;
            foreach (IntVec3 c in r.Cells) { n++; if (map.fogGrid.IsFogged(c)) f++; }
            return n == 0 ? 0f : (float)f / n;
        }

        private static bool FreeFloor(Map map, IntVec3 c)
        {
            return c.InBounds(map) && !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null &&
                   map.zoneManager.ZoneAt(c) == null;
        }

        private static IntVec3 Centre(Room r)
        {
            List<IntVec3> cells = r.Cells.ToList();
            int x = (int)cells.Average(c => c.x), z = (int)cells.Average(c => c.z);
            return cells.OrderBy(c => Math.Abs(c.x - x) + Math.Abs(c.z - z)).First();
        }

        public static string Rooms(Map map)
        {
            var sb = new StringBuilder();
            foreach (Room r in IndoorRooms(map).OrderBy(r => r.ID))
            {
                IntVec3 c = Centre(r);
                bool roofed = r.OpenRoofCount == 0;
                sb.AppendFormat("room {0}: {1} cells, {2}, fogged {3:P0}, beds {4}, free floor {5}, centre {6},{7}; ",
                    r.ID, r.CellCount, roofed ? "roofed" : "OPEN ROOF", FoggedShare(map, r), r.ContainedBeds.Count(),
                    r.Cells.Count(x => FreeFloor(map, x)), c.x, c.z);
            }
            return sb.Length == 0 ? "no indoor rooms found" : sb.ToString();
        }

        /// <summary>
        /// Explore EVERYTHING (owner: "exploring is not finished ... it never went through EVERY DOOR"). Targets are
        /// every door that touches fog, then every reachable fogged cell beside explored ground (the fog frontier),
        /// inside and outside. Each idle colonist gets a QUEUE of the nearest unclaimed targets, so one call walks
        /// several doors; the result says how much frontier is left, and the caller repeats until it is zero.
        /// </summary>
        public static string Explore(Map map)
        {
            FogGrid fog = map.fogGrid;
            var targets = new List<IntVec3>();
            foreach (Building b in map.listerBuildings.allBuildingsColonist.Concat(map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial).OfType<Building>()))
            {
                if (!(b is Building_Door) && !b.def.IsDoor && b.def.defName.IndexOf("door", StringComparison.OrdinalIgnoreCase) < 0) continue;
                if (GenAdj.CellsAdjacent8Way(b).Any(c => c.InBounds(map) && fog.IsFogged(c))) targets.Add(b.Position);
            }
            // the fog frontier: fogged, walkable cells right next to seen ground, sampled so the list stays short
            int step = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                if (!fog.IsFogged(c) || !c.Walkable(map)) continue;
                if (!GenAdj.CardinalDirections.Any(d => { IntVec3 n = c + d; return n.InBounds(map) && !fog.IsFogged(n) && n.Walkable(map); })) continue;
                if (++step % 6 == 0) targets.Add(c);
            }
            targets = targets.Distinct().ToList();
            if (targets.Count == 0)
            {
                // v3: rooms that are still fogged but sealed (no door, no walkable frontier): dig the shortest way in
                string dug = DigIntoSealedRooms(map);
                return dug ?? "ok: nothing left to explore -- no fogged door, fog frontier or sealed fogged room";
            }

            var notes = new List<string>();
            var claimed = new HashSet<IntVec3>();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.Where(p => !p.Downed && !p.InMentalState))
            {
                List<IntVec3> mine = targets.Where(t => !claimed.Contains(t))
                                            .OrderBy(t => t.DistanceToSquared(p.Position))
                                            .Where(t => p.CanReach(t, PathEndMode.Touch, Danger.Some))
                                            .Take(5).ToList();
                if (mine.Count == 0) continue;
                foreach (IntVec3 t in mine) claimed.Add(t);
                p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, mine[0]), JobTag.Misc);
                foreach (IntVec3 t in mine.Skip(1))
                    p.jobs.jobQueue.EnqueueLast(JobMaker.MakeJob(JobDefOf.Goto, t), JobTag.Misc);
                notes.Add(p.LabelShort + " -> " + mine.Count + " stops from " + mine[0].x + "," + mine[0].z);
            }
            return notes.Count == 0
                ? "refused: " + targets.Count + " places left to explore but none reachable right now"
                : "ok: exploring, " + targets.Count + " places left (doors + fog edge): " + string.Join("; ", notes) + " -- the game must run for them to walk";
        }

        /// <summary>
        /// For each indoor room that is still mostly fogged and has no walkable way in, find the shortest run of
        /// mineable cells from explored, walkable floor into it (breadth-first over at most 12 cells of rock/wall)
        /// and designate those cells for mining. Owner: "it never went through EVERY DOOR" -- some hidden rooms have
        /// no door at all.
        /// </summary>
        private static string DigIntoSealedRooms(Map map)
        {
            var sealedRooms = IndoorRooms(map).Where(r => FoggedShare(map, r) > 0.8f).ToList();
            if (sealedRooms.Count == 0) return null;
            var notes = new List<string>();
            foreach (Room room in sealedRooms.Take(3))
            {
                var goal = new HashSet<IntVec3>(room.Cells);
                var prev = new Dictionary<IntVec3, IntVec3>();
                var depth = new Dictionary<IntVec3, int>();
                var queue = new Queue<IntVec3>();
                foreach (IntVec3 c in room.Cells)
                {
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 n = c + d;
                        if (!n.InBounds(map) || goal.Contains(n) || depth.ContainsKey(n)) continue;
                        if (!IsMineable(map, n)) continue;
                        depth[n] = 1; prev[n] = c; queue.Enqueue(n);
                    }
                }
                IntVec3 found = IntVec3.Invalid;
                while (queue.Count > 0 && !found.IsValid)
                {
                    IntVec3 cur = queue.Dequeue();
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 n = cur + d;
                        if (!n.InBounds(map) || depth.ContainsKey(n) || goal.Contains(n)) continue;
                        if (!map.fogGrid.IsFogged(n) && n.Standable(map)) { found = cur; break; }   // reached seen floor
                        if (depth[cur] >= 12 || !IsMineable(map, n)) continue;
                        depth[n] = depth[cur] + 1; prev[n] = cur; queue.Enqueue(n);
                    }
                }
                if (!found.IsValid) { notes.Add("room " + room.ID + ": no dig path within 12 cells"); continue; }
                int marked = 0;
                for (IntVec3 c = found; !goal.Contains(c); c = prev[c])
                {
                    Building wall = c.GetEdifice(map);
                    bool natural = wall != null && (wall.def.mineable || (wall.def.building != null && wall.def.building.isNaturalRock));
                    if (natural && map.designationManager.DesignationAt(c, DesignationDefOf.Mine) == null)
                    {
                        map.designationManager.AddDesignation(new Designation(c, DesignationDefOf.Mine)); marked++;
                    }
                    else if (!natural && wall != null && map.designationManager.DesignationOn(wall, DesignationDefOf.Deconstruct) == null)
                    {
                        map.designationManager.AddDesignation(new Designation(wall, DesignationDefOf.Deconstruct)); marked++;
                    }
                    if (!prev.ContainsKey(c)) break;
                }
                notes.Add("room " + room.ID + ": " + marked + " cells marked to mine or deconstruct in");
            }
            return "ok: no doors left, digging into sealed fogged rooms -- " + string.Join("; ", notes) + " (someone needs Mining and Construction work on)";
        }

        private static bool IsMineable(Map map, IntVec3 c)
        {
            Building ed = c.GetEdifice(map);
            // rock is mined; a built wall is deconstructed -- either way it opens a way in
            return ed != null && (ed.def.mineable || (ed.def.building != null && ed.def.building.isNaturalRock) ||
                                  (ed.Faction == Faction.OfPlayer || ed.Faction == null) && ed.def.passability == Traversability.Impassable);
        }

        public static string StockpileRoom(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("mode", out string mode);
            mode = (mode ?? "food").ToLowerInvariant();
            a.TryGetValue("room", out string want);
            List<Room> candidates = IndoorRooms(map).Where(r => FoggedShare(map, r) < 0.2f && r.OpenRoofCount == 0 &&
                                                                 !r.ContainedBeds.Any()).ToList();
            Room room;
            if (!string.IsNullOrEmpty(want) && want != "auto" && int.TryParse(want, out int id))
            {
                room = IndoorRooms(map).FirstOrDefault(r => r.ID == id);
                if (room == null) return "refused: no indoor room " + id;
            }
            else if (mode == "food")
            {
                // a cooled room first (the freezer), else the smallest roofed explored room without beds
                room = candidates.OrderByDescending(r => r.Temperature < 5f)
                                 .ThenBy(r => r.CellCount).FirstOrDefault(r => r.Cells.Count(c => FreeFloor(map, c)) >= 4);
            }
            else
            {
                room = candidates.OrderByDescending(r => r.Cells.Count(c => FreeFloor(map, c))).FirstOrDefault();
            }
            if (room == null) return "refused: no explored, roofed room without beds -- explore first";
            List<IntVec3> cells = room.Cells.Where(c => FreeFloor(map, c)).ToList();
            if (cells.Count == 0) return "refused: room " + room.ID + " has no free explored floor";

            var zone = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
            map.zoneManager.RegisterZone(zone);
            foreach (IntVec3 c in cells) zone.AddCell(c);
            ThingFilter f = zone.settings.filter;
            if (mode == "food")
            {
                f.SetDisallowAll();
                f.SetAllow(ThingCategoryDefOf.Foods, true);
                zone.settings.Priority = StoragePriority.Preferred;
                zone.label = "Food store";
            }
            else
            {
                f.SetAllowAll(null);
                f.SetAllow(ThingCategoryDefOf.Foods, false);
                f.SetAllow(ThingCategoryDefOf.Corpses, false);
                zone.label = "Main store";
            }
            return "ok: " + zone.label + " in room " + room.ID + ", " + cells.Count + " cells, " +
                   (room.Temperature < 5f ? "cold" : "room temperature") + ", filter " + mode;
        }

        public static string Beds(Map map)
        {
            List<Pawn> without = map.mapPawns.FreeColonistsSpawned.Where(p => p.ownership?.OwnedBed == null).ToList();
            if (without.Count == 0) return "ok: everyone has a bed";
            ThingDef bed = ThingDefOf.Bed;
            ThingDef stuff = GenStuff.DefaultStuffFor(bed);
            var placed = new List<string>();
            foreach (Room r in IndoorRooms(map).Where(r => r.OpenRoofCount == 0 && FoggedShare(map, r) < 0.2f)
                                               .OrderByDescending(r => r.ContainedBeds.Count()))
            {
                foreach (IntVec3 c in r.Cells.Where(x => FreeFloor(map, x)))
                {
                    if (placed.Count >= without.Count) break;
                    Rot4 rot = Rot4.South;
                    if (GenConstruct.CanPlaceBlueprintAt(bed, c, rot, map, false, null, null, stuff).Accepted)
                    {
                        GenConstruct.PlaceBlueprintForBuild(bed, c, map, rot, Faction.OfPlayer, stuff);
                        placed.Add(c.x + "," + c.z);
                    }
                }
                if (placed.Count >= without.Count) break;
            }
            return placed.Count == 0
                ? "refused: no free roofed, explored floor fits a bed -- explore first"
                : "ok: bed blueprints at " + string.Join(" ", placed) + " for " + string.Join(", ", without.Select(p => p.LabelShort));
        }
    }
}
