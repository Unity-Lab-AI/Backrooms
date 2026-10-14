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
        public static string Explore(Map map) => Explore(map, new Dictionary<string, string>());

        public static string Explore(Map map, Dictionary<string, string> a)
        {
            FogGrid fog = map.fogGrid;
            var targets = new List<IntVec3>();
            foreach (Building b in map.listerBuildings.allBuildingsColonist.Concat(map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial).OfType<Building>()))
            {
                if (!(b is Building_Door) && !b.def.IsDoor && b.def.defName.IndexOf("door", StringComparison.OrdinalIgnoreCase) < 0) continue;
                if (!GenAdj.CellsAdjacent8Way(b).Any(c => c.InBounds(map) && fog.IsFogged(c))) continue;
                // v3: a forbidden door with fog behind it is a door nobody went through -- "it never went through EVERY
                // DOOR". Unforbid it so the walk below can use it; a door that is not ours stays as it is.
                if (b.Faction == Faction.OfPlayer && b.IsForbidden(Faction.OfPlayer)) b.SetForbidden(false, false);
                targets.Add(b.Position);
            }
            // the fog frontier: fogged, walkable cells right next to seen ground. Every one counts -- the old "every 6th
            // cell" sampling dropped small frontiers entirely (test run 2026-10-13: explore reported nothing left while
            // fogged rooms sat beside explored floor), so a frontier of five cells never became a target. The list is
            // kept short by distance instead: the 400 nearest the camp anchor.
            IntVec3 campAt = CampAnchor.Get(map);
            var frontier = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                if (!fog.IsFogged(c) || !c.Walkable(map)) continue;
                if (!GenAdj.CardinalDirections.Any(d => { IntVec3 n = c + d; return n.InBounds(map) && !fog.IsFogged(n) && n.Walkable(map); })) continue;
                frontier.Add(c);
            }
            if (campAt.IsValid) frontier = frontier.OrderBy(c => c.DistanceToSquared(campAt)).ToList();
            targets.AddRange(frontier.Take(400));
            targets = targets.Distinct().ToList();
            if (targets.Count == 0)
            {
                // v3: rooms that are still fogged but sealed (no door, no walkable frontier): dig the shortest way in
                string dug = DigIntoSealedRooms(map, a);
                return dug ?? "ok: nothing left to explore -- no fogged door, fog frontier or sealed fogged room";
            }

            var notes = new List<string>();
            var claimed = new HashSet<IntVec3>();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.Where(Core.PawnOrderEligibility.FreeForAutonomousOrders))
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
                ? "refused: " + targets.Count + " places left to explore but no free colonist can reach one right now (drafted, ordered, hungry or exhausted colonists are left alone)"
                : "ok: exploring, " + targets.Count + " places left (doors + fog edge): " + string.Join("; ", notes) + " -- the game must run for them to walk";
        }

        /// <summary>
        /// For each indoor room that is still mostly fogged and has no walkable way in, find the shortest run of
        /// mineable cells from explored, walkable floor into it (breadth-first over at most 12 cells of rock/wall)
        /// and designate those cells for mining. Owner: "it never went through EVERY DOOR" -- some hidden rooms have
        /// no door at all.
        /// </summary>
        private static string DigIntoSealedRooms(Map map, Dictionary<string, string> a)
        {
            // only rooms near the crew: on an open-ground start the far mountain pockets are not "exploring", and
            // digging across the map into them is the late mountain-base job (2026-10-13: she dug into room 79,
            // two hundred cells from the crash site)
            // v3 (owner: "the map is even on screen becsue it never went through EVERY DOOR"): every fogged indoor room
            // counts, nearest the crew first -- the 40-cell cut-off left rooms 360/367/407 (996 cells) fogged for ever
            // while this reported nothing left. A room half seen through a doorway is still unexplored (share > 0.5).
            List<IntVec3> crew = map.mapPawns.FreeColonistsSpawned.Select(p => p.Position).ToList();
            if (crew.Count == 0) return null;
            var sealedRooms = IndoorRooms(map).Where(r => FoggedShare(map, r) > 0.5f)
                .OrderBy(r => crew.Min(c => c.DistanceToSquared(Centre(r)))).ToList();
            if (sealedRooms.Count == 0) return null;
            var notes = new List<string>();
            // digging into fogged mountain rooms is a later-game move (run 4, 2026-10-13: keep-playing's auto-explore marked mountain cells
            // to mine on day 0 with no camp); it happens only when asked for: explore dig true (the ladder's late explore rung says so)
            if (!(a.TryGetValue("dig", out string dg) && dg.StartsWith("t", StringComparison.OrdinalIgnoreCase)))
                return "ok: no doors left; " + sealedRooms.Count + " fogged room(s) remain sealed in rock -- dig into them later with explore dig true (after the camp stands)";

            foreach (Room room in sealedRooms.Take(5))
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
                        if (depth[cur] >= MaxDigCells || !IsMineable(map, n)) continue;
                        depth[n] = depth[cur] + 1; prev[n] = cur; queue.Enqueue(n);
                    }
                }
                if (!found.IsValid) { notes.Add("room " + room.ID + " (" + room.CellCount + " cells): no dig path within " + MaxDigCells + " cells"); continue; }
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
            return "ok: no doors left; " + sealedRooms.Count + " fogged room(s) remain, digging into the nearest " + Math.Min(5, sealedRooms.Count) + " -- " + string.Join("; ", notes) + " (someone needs Mining and Construction work on)";
        }

        /// <summary>Rock or wall a dig-in may cross. 12 reached only pockets beside the base; a mountain room sits deeper.</summary>
        private const int MaxDigCells = 24;

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
            // a room with a quarter of its roof still to come is a room (the store was 89 % roofed when the food rotted
            // outside, run 5 2026-10-14); food only ever goes on ROOFED cells of it
            List<Room> candidates = IndoorRooms(map).Where(r => FoggedShare(map, r) < 0.2f && r.OpenRoofCount * 4 <= r.CellCount &&
                                                                 !r.ContainedBeds.Any()).ToList();
            Zone_Stockpile oldFood = mode == "food" ? SetupTools3.Store(map, "Food store") : null;
            Zone_Stockpile mainStore = SetupTools3.Store(map, "Main store");
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
                                 .ThenBy(r => r.CellCount).FirstOrDefault(r => r.Cells.Count(c => FreeFloor(map, c) && map.roofGrid.Roofed(c)) >= 4 ||
                                                                               (mainStore != null && mainStore.cells.Any(c => c.GetRoom(map) == r)));
            }
            else
            {
                room = candidates.OrderByDescending(r => r.Cells.Count(c => FreeFloor(map, c))).FirstOrDefault();
            }
            if (room == null) return "refused: no explored, roofed room without beds -- explore first";
            if (oldFood != null && oldFood.cells.Count(c => c.GetRoom(map) == room) * 5 >= oldFood.cells.Count * 4)
                return "ok: Food store is already inside room " + room.ID + " (" + oldFood.cells.Count(c => map.roofGrid.Roofed(c)) + " of " + oldFood.cells.Count +
                       " cells roofed; the rest roof with the room)";
            List<IntVec3> cells = room.Cells.Where(c => FreeFloor(map, c) && (mode != "food" || map.roofGrid.Roofed(c))).ToList();
            if (mode == "food" && cells.Count < 4)
            {
                // the Main store fills the room: the food store is a corner carved out of it (owner, run 5: food rotting in an
                // open zone outside while the main store sat roofed)
                string carved = SetupTools3.CarveFoodStore(map, room);
                if (carved == null) return "refused: room " + room.ID + " has no free roofed floor and no Main store corner to carve";
                if (oldFood != null) { int n = oldFood.cells.Count; oldFood.Delete(); carved += "; the open-air Food store (" + n + " cells) is deleted -- haulers carry its food in"; }
                return carved;
            }
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
            string moved = "";
            if (mode == "food" && oldFood != null) { int n = oldFood.cells.Count; oldFood.Delete(); moved = "; the open-air Food store (" + n + " cells) is deleted -- haulers carry its food in"; }
            return "ok: " + zone.label + " in room " + room.ID + ", " + cells.Count + " cells, " +
                   (room.Temperature < 5f ? "cold" : "room temperature") + ", filter " + mode + moved;
        }

        public static string Beds(Map map)
        {
            List<Pawn> without = map.mapPawns.FreeColonistsSpawned.Where(p => p.ownership?.OwnedBed == null).ToList();
            if (without.Count == 0) return "ok: everyone has a bed";
            ThingDef bed = ThingDefOf.Bed;
            ThingDef stuff = GenStuff.DefaultStuffFor(bed);

            // sleeping places already coming: free built colonist beds nobody owns yet, and bed blueprints or frames
            // still waiting to be built -- so repeating this command does not plan the same beds again
            int freeBuilt = map.listerBuildings.allBuildingsColonist.OfType<Building_Bed>()
                .Count(b => b.ForColonists && !b.Medical && b.def.building != null && b.def.building.bed_humanlike &&
                            b.SleepingSlotsCount > b.OwnersForReading.Count);
            int planned = map.listerThings.AllThings.Count(t =>
                t.Faction == Faction.OfPlayer && (t.def.IsBlueprint || t.def.IsFrame) &&
                t.def.entityDefToBuild is ThingDef built && built.IsBed && built.building != null && built.building.bed_humanlike);
            int needed = without.Count - freeBuilt - planned;
            if (needed <= 0)
            {
                return "ok: no new beds needed -- " + freeBuilt + " free bed(s) and " + planned +
                       " planned for " + string.Join(", ", without.Select(p => p.LabelShort));
            }

            var placed = new List<string>();
            List<Room> rooms = IndoorRooms(map).Where(r => r.OpenRoofCount == 0 && FoggedShare(map, r) < 0.2f)
                                               .OrderByDescending(r => r.ContainedBeds.Count()).ToList();
            foreach (Room r in rooms)
            {
                if (!RoomDesign.IsRoom(map, r)) continue;
                // RoomDesign (owner, 2026-10-13: "she just fills the room with beds no ryhme or reason and blocks the doors"):
                // beds along the walls, head to the wall, foot into the room, never on a door lane; far corners first
                while (placed.Count < needed)
                {
                    RoomDesign.Slot s = RoomDesign.Place(map, r, bed, stuff, true);
                    if (s == null) break;
                    placed.Add(s.Cell.x + "," + s.Cell.z);
                }
                if (placed.Count >= needed) break;
            }
            if (placed.Count > 0)
                return "ok: bed blueprints at " + string.Join(" ", placed) + " for " + string.Join(", ", without.Select(p => p.LabelShort)) +
                       " (against the walls, clear of the door)";
            // No usable room. Do not send her exploring: a crash site has no rooms until one is built. If a shelter is
            // already planned or under construction, say so; otherwise plan one at the camp anchor now.
            Thing pending = map.listerThings.AllThings.FirstOrDefault(t => t.Faction == Faction.OfPlayer && (t.def.IsBlueprint || t.def.IsFrame) &&
                                                                          t.def.entityDefToBuild == ThingDefOf.Wall);
            if (pending != null)
                return "refused: no finished roofed room yet -- walls are still planned or being built near " + pending.Position.x + "," + pending.Position.z +
                       " (keep Construction on, chop wood if short); beds once the room stands. Do not call beds again until then";
            string shelter = SetupTools3.Shelter(map, new Dictionary<string, string>());
            return shelter.StartsWith("ok")
                ? "refused for now: no roofed room, so a shelter was planned at the camp -- " + shelter.Substring(4) + "; beds once it stands"
                : "refused: no roofed room and no shelter could be planned (" + shelter + ") -- camp x,z elsewhere or build_room by hand";
        }
    }
}
