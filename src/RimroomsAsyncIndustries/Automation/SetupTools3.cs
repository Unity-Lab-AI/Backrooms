using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Open-ground (Crashlanded) camp tools. Owner, 2026-10-13: "it never auto unforbid all the starting materials and
    /// never copped wood to build starting structures rooms" -- a crash start has no rooms, so every setup tool that
    /// looked for an indoor room refused and she looped. These work beside the crew on open ground.
    ///   {"cmd":"unforbid"}                         every forbidden item on seen ground is unforbidden
    ///   {"cmd":"chop","count":"300"}               trees nearest the crew marked to chop until their wood covers count
    ///   {"cmd":"shelter","w":"7","h":"5"}          a wood-walled room (inside w x h) with a door and roof, by the crew
    ///   {"cmd":"stockpile_camp","mode":"food|nofood"}  nofood = the Main store OVER the supply pile at the camp anchor;
    ///                                              food = a 6x6 beside it. Then {"cmd":"storage_room"} walls and roofs it
    ///   {"cmd":"camp"} / {"cmd":"camp","x":"..","z":".."}   the camp anchor (CampAnchor.cs): read, set, recompute
    /// </summary>
    internal static class SetupTools3
    {
        // Owner, 2026-10-13: "she is all over the place instead of correctly building camp right where her supplies
        // and they dropped in on". These anchored on the crew's average position at the moment of the call; the crew
        // scatters, so the builds did. The camp anchor (CampAnchor: the supply drop, saved with the map) is the point.
        private static IntVec3 CrewCentre(Map map) => CampAnchor.Get(map);

        private static bool Open(Map map, IntVec3 c) =>
            c.InBounds(map) && !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null &&
            // a planned or half-built thing is taken ground (run 3, 2026-10-13 22:02: the second shelter was laid THROUGH the
            // first's planned walls -- owner: "shes building building over top of building")
            !c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame) &&
            !RoomSite.Geyser(map, c) &&                                        // a room over a geyser cooks whoever enters (owner, run 4)
            map.zoneManager.ZoneAt(c) == null && !c.Roofed(map) && c.GetTerrain(map).affordances != null &&
            c.GetTerrain(map).affordances.Contains(TerrainAffordanceDefOf.Heavy);

        private static int Arg(Dictionary<string, string> a, string key, int dflt, int min, int max)
        {
            return a.TryGetValue(key, out string s) && int.TryParse(s, out int v) ? Math.Max(min, Math.Min(max, v)) : dflt;
        }

        public static string Unforbid(Map map)
        {
            int n = 0;
            foreach (Thing t in map.listerThings.AllThings.ToList())
            {
                if (t.def.category != ThingCategory.Item || !t.Spawned || map.fogGrid.IsFogged(t.Position)) continue;
                if (!t.IsForbidden(Faction.OfPlayer)) continue;
                t.SetForbidden(false, false); n++;
            }
            return n == 0 ? "ok: nothing forbidden on seen ground" : "ok: " + n + " items unforbidden -- haulers can take them now";
        }

        public static string Chop(Map map, Dictionary<string, string> a)
        {
            int want = Arg(a, "count", 300, 25, 3000);
            IntVec3 home = CrewCentre(map);
            if (!home.IsValid) return "refused: no free colonist on this map";
            int queued = 0, marked = 0;
            foreach (Designation d in map.designationManager.AllDesignations.Where(d => d.def == DesignationDefOf.HarvestPlant).ToList())
                if (d.target.Thing is Plant p && p.def.plant.IsTree) queued += p.YieldNow();
            if (queued >= want) return "ok: " + queued + " wood already marked to chop (wanted " + want + ") -- someone needs PlantCut work on";
            foreach (Plant p in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant).OfType<Plant>()
                                     .Where(p => p.def.plant.IsTree && p.def.plant.harvestedThingDef == ThingDefOf.WoodLog &&
                                                 !map.fogGrid.IsFogged(p.Position) && map.zoneManager.ZoneAt(p.Position) == null &&
                                                 p.YieldNow() > 0 && map.designationManager.DesignationOn(p) == null)
                                     .OrderBy(p => p.Position.DistanceToSquared(home)).Take(200))
            {
                if (queued >= want) break;
                map.designationManager.AddDesignation(new Designation(p, DesignationDefOf.HarvestPlant));
                queued += p.YieldNow(); marked++;
            }
            return marked == 0 ? "refused: no grown tree near the crew to chop"
                               : "ok: " + marked + " trees marked to chop, about " + queued + " wood (wanted " + want + ") -- someone needs PlantCut work on";
        }

        public static string Shelter(Map map, Dictionary<string, string> a)
        {
            int w = Arg(a, "w", 7, 3, 15), h = Arg(a, "h", 5, 3, 15);
            IntVec3 home = CrewCentre(map);
            if (!home.IsValid) return "refused: no free colonist on this map";
            ThingDef wall = ThingDefOf.Wall, door = ThingDefOf.Door, wood = ThingDefOf.WoodLog;
            // x,z given: that is the inside corner and the only place tried (the test run's shelter ignored x,z and
            // landed 50 cells from where she planned it); otherwise the nearest open patch to the camp anchor.
            IntVec3 asked = new IntVec3(Arg(a, "x", -1, -1, 9999), 0, Arg(a, "z", -1, -1, 9999));
            // one shelter at a time: planned, unbuilt walls near the camp mean a room is already on its way; a second box
            // needs x,z on purpose or force true (run 3: a 5x4 "for the bench" went in while the 7x5 stood unbuilt)
            bool force = a.TryGetValue("force", out string fo) && fo.StartsWith("t", StringComparison.OrdinalIgnoreCase);
            RimroomsCampComponent camp = map.GetComponent<RimroomsCampComponent>();
            // one SHELTER at a time: the shelter this command planned must stand before a second one (run 4: the first guard
            // counted the storage room's walls and blocked the shelter that belongs beside it)
            if (!asked.InBounds(map) && !force && camp != null && camp.Unbuilt(camp.shelterBox))
                return "refused for now: the shelter planned at " + camp.shelterBox.minX + "," + camp.shelterBox.minZ + " (" + camp.shelterBox.Width + "x" + camp.shelterBox.Height +
                       ") is still being built -- let it stand (time running, Construction on, wood in stock); a second one on purpose: shelter x z, or force true";
            IEnumerable<IntVec3> corners = asked.InBounds(map)
                ? new[] { new IntVec3(asked.x - 1, 0, asked.z - 1) }
                : GenRadial.RadialCellsAround(home, 25f, true);
            // the outer box is (w+2) x (h+2): walls on the ring, the door mid-south, roof over the inside
            foreach (IntVec3 corner in corners)
            {
                var ring = new List<IntVec3>(); var inside = new List<IntVec3>(); bool ok = true;
                for (int dx = 0; dx < w + 2 && ok; dx++)
                    for (int dz = 0; dz < h + 2 && ok; dz++)
                    {
                        IntVec3 c = new IntVec3(corner.x + dx, 0, corner.z + dz);
                        if (!Open(map, c)) { ok = false; break; }
                        bool edge = dx == 0 || dz == 0 || dx == w + 1 || dz == h + 1;
                        (edge ? ring : inside).Add(c);
                    }
                if (!ok) continue;
                IntVec3 doorCell = new IntVec3(corner.x + 1 + w / 2, 0, corner.z);
                if (!ring.All(c => GenConstruct.CanPlaceBlueprintAt(c == doorCell ? door : wall, c, Rot4.North, map, false, null, null, wood).Accepted))
                    continue;
                foreach (IntVec3 c in ring) GenConstruct.PlaceBlueprintForBuild(c == doorCell ? door : wall, c, map, Rot4.North, Faction.OfPlayer, wood);
                // the camp is Home: colonists only fight fires and clean inside the Home area (run 3: 47 fire cells with no Home)
                foreach (IntVec3 c in ring.Concat(inside)) map.areaManager.Home[c] = true;
                if (camp != null) camp.shelterBox = CellRect.FromCellList(ring);
                foreach (IntVec3 c in inside) map.areaManager.BuildRoof[c] = true;
                int cost = (ring.Count - 1) * wall.CostStuffCount + door.CostStuffCount;
                return "ok: shelter planned, inside " + w + "x" + h + " from " + (corner.x + 1) + "," + (corner.z + 1) +
                       ", door at " + doorCell.x + "," + doorCell.z + ", roof marked; needs about " + cost +
                       " wood (chop if short) and Construction work on. When it stands: beds, then stove";
            }
            return asked.InBounds(map)
                ? "refused: the " + (w + 2) + "x" + (h + 2) + " box with its inside corner at " + asked.x + "," + asked.z + " is not open buildable ground -- pick another corner or leave x,z out"
                : "refused: no open " + (w + 2) + "x" + (h + 2) + " patch of buildable ground within 25 cells of the camp anchor " + home.x + "," + home.z;
        }

        public static string StockpileCamp(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("mode", out string mode);
            mode = (mode ?? "food").ToLowerInvariant();
            string label = mode == "food" ? "Food store" : "Main store";
            if (map.zoneManager.AllZones.OfType<Zone_Stockpile>().Any(z => z.label == label))
                return "ok: " + label + " already exists";
            IntVec3 home = CrewCentre(map);
            if (!home.IsValid) return "refused: no free colonist on this map";
            if (mode != "food")
            {
                // "zone them in a storage zone": the main store is the supply pile itself, where it lies at the anchor
                List<Thing> pile = CampAnchor.SupplyPile(map, home);
                if (pile.Count > 0)
                {
                    CellRect box = CellRect.FromCellList(pile.Select(t => t.Position)).ExpandedBy(1).ClipInsideMap(map);
                    if (box.Width < 6 || box.Height < 6) box = new CellRect(box.CenterCell.x - 3, box.CenterCell.z - 3, Math.Max(6, box.Width), Math.Max(6, box.Height)).ClipInsideMap(map);
                    // run 3: the drop scatter was 17x22 and the store came out 432 cells -- a field, not a store; cap it at 12x12 around the pile's centre
                    if (box.Width > 12 || box.Height > 12) box = new CellRect(box.CenterCell.x - 6, box.CenterCell.z - 6, Math.Min(12, box.Width), Math.Min(12, box.Height)).ClipInsideMap(map);
                    var pileCells = box.Cells.Where(c => !map.fogGrid.IsFogged(c) && map.zoneManager.ZoneAt(c) == null && !RoomSite.Geyser(map, c) &&
                                                         (c.Standable(map) || c.GetFirstItem(map) != null) && c.GetEdifice(map) == null).ToList();
                    if (pileCells.Count >= 20)
                    {
                        var pz = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
                        map.zoneManager.RegisterZone(pz);
                        foreach (IntVec3 c in pileCells) pz.AddCell(c);
                        pz.settings.filter.SetAllowAll(null); pz.settings.filter.SetAllow(ThingCategoryDefOf.Foods, false); pz.settings.filter.SetAllow(ThingCategoryDefOf.Corpses, false);
                        pz.label = label;
                        return "ok: " + label + " over the supply pile at the camp anchor, " + pileCells.Count + " cells from " + box.minX + "," + box.minZ +
                               " (" + pile.Count + " item stacks already inside) -- next: storage_room to wall and roof it";
                    }
                }
            }
            foreach (IntVec3 corner in GenRadial.RadialCellsAround(home, 20f, true).Skip(9))
            {
                var cells = new List<IntVec3>();
                for (int dx = 0; dx < 6; dx++)
                    for (int dz = 0; dz < 6; dz++)
                    {
                        IntVec3 c = new IntVec3(corner.x + dx, 0, corner.z + dz);
                        if (c.InBounds(map) && !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null &&
                            map.zoneManager.ZoneAt(c) == null && map.areaManager.BuildRoof[c] == false) cells.Add(c);
                    }
                if (cells.Count < 30) continue;
                var zone = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
                map.zoneManager.RegisterZone(zone);
                foreach (IntVec3 c in cells) zone.AddCell(c);
                ThingFilter f = zone.settings.filter;
                if (mode == "food") { f.SetDisallowAll(); f.SetAllow(ThingCategoryDefOf.Foods, true); zone.settings.Priority = StoragePriority.Preferred; }
                else { f.SetAllowAll(null); f.SetAllow(ThingCategoryDefOf.Foods, false); f.SetAllow(ThingCategoryDefOf.Corpses, false); }
                zone.label = label;
                return "ok: " + label + " outdoors, " + cells.Count + " cells from " + corner.x + "," + corner.z +
                       " beside the camp anchor (open air: storage_room walls and roofs the main store; food goes under that roof)";
            }
            return "refused: no open 6x6 ground within 20 cells of the camp anchor " + home.x + "," + home.z;
        }
    }
}
