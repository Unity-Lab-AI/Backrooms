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

        public static string Explore(Map map)
        {
            List<Room> fogged = IndoorRooms(map).Where(r => FoggedShare(map, r) > 0.3f).ToList();
            if (fogged.Count == 0) return "ok: every indoor room is explored";
            var notes = new List<string>();
            var taken = new HashSet<int>();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                Room target = fogged.Where(r => !taken.Contains(r.ID))
                                    .OrderBy(r => Centre(r).DistanceToSquared(p.Position))
                                    .FirstOrDefault(r => p.CanReach(Centre(r), PathEndMode.OnCell, Danger.Deadly));
                if (target == null) continue;
                taken.Add(target.ID);
                IntVec3 dest = Centre(target);
                p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, dest), JobTag.Misc);
                notes.Add(p.LabelShort + " -> room " + target.ID + " (" + dest.x + "," + dest.z + ")");
            }
            return notes.Count == 0
                ? "refused: " + fogged.Count + " fogged rooms but none reachable by an idle colonist"
                : "ok: exploring " + string.Join("; ", notes) + " -- the game must be running for them to walk";
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
