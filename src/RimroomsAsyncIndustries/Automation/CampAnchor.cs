using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The camp has ONE anchor, and it is where the supplies landed.
    ///
    /// Owner, 2026-10-13, verbatim: "it looks like she is all over the place instead of correctly building camp right
    /// where her supplies and they dropped in on" and "first fucking thing she should build a base building around her
    /// starting supplies and zone them in a storage zone to get them ourt of the rain ... set up base in the drop location
    /// for a cmap before designing the main base". In the test run every setup command anchored on the crew's average
    /// position at the moment of the call, so the store landed at 146,120 and the shelter at 197,108.
    ///
    /// The anchor is saved with the map (a MapComponent: RimWorld makes one per map by itself), computed once from the
    /// loose starting items near the crew, and every setup command builds around it until the owner or the model moves it.
    /// </summary>
    public sealed class RimroomsCampComponent : MapComponent
    {
        public IntVec3 anchor = IntVec3.Invalid;
        public bool manual;
        // wall_swap: rock cells marked to mine that get a built wall the moment they are clear (WallSwap.cs)
        private List<IntVec3> pendingWalls = new List<IntVec3>();
        private List<string> pendingStuff = new List<string>();
        // the rooms the camp commands planned, so a second one is refused while the first stands unbuilt (run 4:
        // a shelter went through the storage room's wall count; a build_room went over a steam geyser)
        public CellRect shelterBox = CellRect.Empty;
        public CellRect storageBox = CellRect.Empty;

        /// <summary>Does this planned box still have a wall blueprint or frame on its ring?</summary>
        public bool Unbuilt(CellRect box)
        {
            if (box.Width == 0 || box.Height == 0) return false;
            foreach (IntVec3 c in box.EdgeCells)
                if (c.InBounds(map) && c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) return true;
            return false;
        }

        public RimroomsCampComponent(Map map) : base(map) { }

        public int PendingCount => pendingWalls?.Count ?? 0;

        public void Queue(IntVec3 c, ThingDef stuff)
        {
            if (pendingWalls == null) { pendingWalls = new List<IntVec3>(); pendingStuff = new List<string>(); }
            if (pendingWalls.Contains(c)) return;
            pendingWalls.Add(c); pendingStuff.Add(stuff.defName);
        }

        public override void MapComponentTick()
        {
            if (pendingWalls == null || pendingWalls.Count == 0 || Find.TickManager.TicksGame % 120 != 0) return;
            for (int i = pendingWalls.Count - 1; i >= 0; i--)
            {
                IntVec3 c = pendingWalls[i];
                if (!c.InBounds(map)) { Drop(i); continue; }
                Building e = c.GetEdifice(map);
                if (e != null && e.def.building != null && e.def.building.isNaturalRock) continue;        // still rock: not mined yet
                if (e != null || c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) { Drop(i); continue; }  // a wall or a plan stands
                ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(pendingStuff[i]) ?? ThingDefOf.Steel;
                if (GenConstruct.CanPlaceBlueprintAt(ThingDefOf.Wall, c, Rot4.North, map, false, null, null, stuff).Accepted)
                    GenConstruct.PlaceBlueprintForBuild(ThingDefOf.Wall, c, map, Rot4.North, Faction.OfPlayer, stuff);
                Drop(i);
            }
        }

        private void Drop(int i) { pendingWalls.RemoveAt(i); pendingStuff.RemoveAt(i); }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref anchor, "rr_campAnchor", IntVec3.Invalid);
            Scribe_Values.Look(ref manual, "rr_campManual", false);
            Scribe_Collections.Look(ref pendingWalls, "rr_pendingWalls", LookMode.Value);
            Scribe_Values.Look(ref shelterBox, "rr_shelterBox", CellRect.Empty);
            Scribe_Values.Look(ref storageBox, "rr_storageBox", CellRect.Empty);
            Scribe_Collections.Look(ref pendingStuff, "rr_pendingStuff", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (pendingWalls == null) pendingWalls = new List<IntVec3>();
                if (pendingStuff == null || pendingStuff.Count != pendingWalls.Count) pendingStuff = pendingWalls.Select(_ => "Steel").ToList();
            }
        }
    }

    /// <summary>What every room and zone placer must refuse: a steam geyser (and its 1-cell margin).</summary>
    internal static class RoomSite
    {
        public static bool Geyser(Map map, IntVec3 c)
        {
            if (!c.InBounds(map)) return false;
            foreach (IntVec3 o in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)).Concat(new[] { c }))
                if (o.InBounds(map) && o.GetThingList(map).Any(t => t.def == ThingDefOf.SteamGeyser)) return true;
            return false;
        }
    }

    internal static class CampAnchor
    {
        private const float PileRadius = 16f;     // the starting supplies lie within this of the anchor

        public static IntVec3 CrewCentre(Map map)
        {
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned.ToList();
            if (crew.Count == 0) return IntVec3.Invalid;
            return new IntVec3((int)crew.Average(p => p.Position.x), 0, (int)crew.Average(p => p.Position.z));
        }

        private static bool LooseItem(Map map, Thing t) =>
            t.def.category == ThingCategory.Item && t.Spawned && !map.fogGrid.IsFogged(t.Position) &&
            (t.Faction == null || t.Faction == Faction.OfPlayer) && t.def.EverHaulable;

        /// <summary>The saved anchor, or the one computed now and saved.</summary>
        public static IntVec3 Get(Map map)
        {
            RimroomsCampComponent comp = map.GetComponent<RimroomsCampComponent>();
            if (comp != null && comp.anchor.IsValid && comp.anchor.InBounds(map)) return comp.anchor;
            IntVec3 found = Compute(map);
            if (comp != null && found.IsValid) comp.anchor = found;
            return found;
        }

        /// <summary>
        /// Where the supplies are: the item-weighted centre of every loose item within 45 cells of the crew (the drop
        /// scatter), else the Home area's centre, else the crew's centre.
        /// </summary>
        public static IntVec3 Compute(Map map)
        {
            IntVec3 crew = CrewCentre(map);
            if (!crew.IsValid) return IntVec3.Invalid;
            List<Thing> items = map.listerThings.AllThings.Where(t => LooseItem(map, t) && t.Position.DistanceTo(crew) <= 45f).ToList();
            if (items.Count >= 5)
            {
                long n = items.Sum(t => (long)t.stackCount);
                double x = items.Sum(t => (double)t.Position.x * t.stackCount) / n, z = items.Sum(t => (double)t.Position.z * t.stackCount) / n;
                IntVec3 c = new IntVec3((int)Math.Round(x), 0, (int)Math.Round(z));
                if (c.InBounds(map)) return c;
            }
            List<IntVec3> home = map.areaManager.Home.ActiveCells.ToList();
            if (home.Count > 0) return new IntVec3((int)home.Average(c => c.x), 0, (int)home.Average(c => c.z));
            return crew;
        }

        /// <summary>The loose items around the anchor -- the pile the storage room goes around.</summary>
        public static List<Thing> SupplyPile(Map map, IntVec3 anchor, float radius = PileRadius) =>
            map.listerThings.AllThings.Where(t => LooseItem(map, t) && t.Position.DistanceTo(anchor) <= radius).ToList();

        /// <summary>
        ///   {"cmd":"camp"}                  where the camp anchor is, and how many supplies lie around it
        ///   {"cmd":"camp","x":"..","z":".."} move it (the owner's or the model's call)
        ///   {"cmd":"camp","auto":"true"}     recompute it from the supplies
        /// </summary>
        public static string Camp(Map map, Dictionary<string, string> a)
        {
            RimroomsCampComponent comp = map.GetComponent<RimroomsCampComponent>();
            if (a.TryGetValue("x", out string xs) && a.TryGetValue("z", out string zs) && int.TryParse(xs, out int x) && int.TryParse(zs, out int z))
            {
                IntVec3 at = new IntVec3(x, 0, z);
                if (!at.InBounds(map)) return "refused: x,z outside the map";
                // Run 5 (2026-10-14 00:29-00:35): `camp x z` walked the anchor one cell at a time to 150,176 -- thirty cells from the
                // supplies and into the mountain -- and every room was refused around it. The anchor is the DROP: a hand-set
                // point stays within 12 cells of where the supplies lie (or of the storage room once it is planned); force true overrides.
                bool forceMove = a.TryGetValue("force", out string fm) && fm.StartsWith("t", StringComparison.OrdinalIgnoreCase);
                IntVec3 drop = comp != null && comp.storageBox.Width > 0 ? comp.storageBox.CenterCell : Compute(map);
                if (!forceMove && drop.IsValid && at.DistanceTo(drop) > 12f)
                    return "refused: " + x + "," + z + " is " + (int)at.DistanceTo(drop) + " cells from the supplies at " + drop.x + "," + drop.z +
                           " -- the camp anchor stays within 12 cells of where the supplies lie (storage room, shelter and stove place themselves beside it); force true to override";
                if (comp != null) { comp.anchor = at; comp.manual = true; }
                return "ok: camp anchor set to " + x + "," + z + " -- every setup command builds around it now";
            }
            if (a.TryGetValue("auto", out string au) && au.StartsWith("t", StringComparison.OrdinalIgnoreCase) && comp != null)
            { comp.anchor = Compute(map); comp.manual = false; }
            IntVec3 anchor = Get(map);
            if (!anchor.IsValid) return "refused: no crew on this map, so no camp";
            List<Thing> pile = SupplyPile(map, anchor);
            CellRect box = pile.Count > 0 ? CellRect.FromCellList(pile.Select(t => t.Position)) : CellRect.SingleCell(anchor);
            return "ok: camp anchor " + anchor.x + "," + anchor.z + (comp != null && comp.manual ? " (set by hand)" : " (the supply drop)") +
                   "; " + pile.Count + " loose item stacks within " + (int)PileRadius + " cells, spread " + box.Width + "x" + box.Height +
                   " from " + box.minX + "," + box.minZ + "; crew centre " + CrewCentre(map).x + "," + CrewCentre(map).z;
        }

        /// <summary>
        /// The first thing: a roofed, walled store AROUND the supplies where they lie, with the stockpile zone inside, so
        /// nothing stays out in the rain and nothing has to be hauled across the map.
        ///   {"cmd":"storage_room"}  walls + door + roof around the supply pile at the anchor; the Main store zone covers the
        ///                            inside; trees inside are marked to chop; min inside 6x6, max 14x14
        /// </summary>
        /// <summary>The full-fill edifices (natural rock, a wall) inside a box -- the cells a store cannot use.</summary>
        private static List<IntVec3> Rock(Map map, CellRect box) =>
            box.Cells.Where(c => c.InBounds(map) && c.GetEdifice(map) is Building ed && ed.def.Fillage == FillCategory.Full && !(ed is Building_Door)).ToList();

        public static string StorageRoom(Map map, Dictionary<string, string> a)
        {
            IntVec3 anchor = Get(map);
            if (!anchor.IsValid) return "refused: no crew on this map";
            RimroomsCampComponent camp = map.GetComponent<RimroomsCampComponent>();
            bool force = a.TryGetValue("force", out string fo) && fo.StartsWith("t", StringComparison.OrdinalIgnoreCase);
            // Run 5 (2026-10-14 00:29-00:30): with a room already planned, a second call from a moved anchor answered "refused: rock"
            // and she re-fought a won fight for twenty minutes. A standing plan is reported, never re-planned (force true re-plans).
            if (!force && camp != null && camp.storageBox.Width > 0)
            {
                int planned = camp.storageBox.EdgeCells.Count(c => c.InBounds(map) && c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame));
                int standing = camp.storageBox.EdgeCells.Count(c => c.InBounds(map) && c.GetEdifice(map) is Building e && !(e.def.building != null && e.def.building.isNaturalRock));
                if (planned + standing > 0)
                    return "ok: the storage room is already planned at " + camp.storageBox.minX + "," + camp.storageBox.minZ + " (" + camp.storageBox.Width + "x" +
                           camp.storageBox.Height + ", " + planned + " walls planned, " + standing + " standing) -- nothing to re-plan; next: shelter beside it, then stove";
            }
            List<Thing> pile = SupplyPile(map, anchor);
            CellRect inside = pile.Count > 0 ? CellRect.FromCellList(pile.Select(t => t.Position)) : CellRect.CenteredOn(anchor, 3);
            inside = inside.ExpandedBy(1);
            // size: at least 6x6, at most 14x14, grown or shrunk around its own centre
            int w = Math.Max(6, Math.Min(14, inside.Width)), h = Math.Max(6, Math.Min(14, inside.Height));
            inside = new CellRect(inside.CenterCell.x - w / 2, inside.CenterCell.z - h / 2, w, h).ClipInsideMap(map);

            // Run 5 (2026-10-14 00:11-00:25): the supplies lay against a granite outcrop, every box held rock, and six refusals said "camp
            // x,z elsewhere or mine it first". The box slides off the rock by itself (up to 8 cells, the pile kept inside as far as it
            // goes), and what rock is left inside is marked to mine -- never a refusal for rock.
            List<IntVec3> rock = Rock(map, inside);
            string shifted = "";
            if (rock.Count > 0)
            {
                CellRect best = inside; int bestRock = rock.Count, bestKeep = pile.Count(t => inside.Contains(t.Position));
                for (int r = 1; r <= 8 && bestRock > 0; r++)
                    foreach (IntVec3 d in new[] { new IntVec3(r, 0, 0), new IntVec3(-r, 0, 0), new IntVec3(0, 0, r), new IntVec3(0, 0, -r), new IntVec3(r, 0, r), new IntVec3(-r, 0, r), new IntVec3(r, 0, -r), new IntVec3(-r, 0, -r) })
                    {
                        CellRect cand = new CellRect(inside.minX + d.x, inside.minZ + d.z, w, h);
                        if (cand.minX < 1 || cand.minZ < 1 || cand.maxX >= map.Size.x - 1 || cand.maxZ >= map.Size.z - 1) continue;
                        if (cand.ExpandedBy(2).Cells.Any(c => c.InBounds(map) && RoomSite.Geyser(map, c))) continue;
                        int cr = Rock(map, cand).Count, keep = pile.Count(t => cand.Contains(t.Position));
                        if (cr < bestRock && keep * 10 >= pile.Count * 6) { best = cand; bestRock = cr; bestKeep = keep; }
                    }
                if (best != inside)
                {
                    shifted = ", box moved " + (best.minX - inside.minX) + "," + (best.minZ - inside.minZ) + " to clear rock (" + bestKeep + " of " + pile.Count + " stacks still inside)";
                    inside = best; rock = Rock(map, inside);
                }
            }
            CellRect ring = inside.ExpandedBy(1).ClipInsideMap(map);

            ThingDef wall = ThingDefOf.Wall, door = ThingDefOf.Door, wood = ThingDefOf.WoodLog;
            int chop = 0, mined = 0;
            foreach (IntVec3 c in ring.ExpandedBy(1))
            {
                if (!c.InBounds(map)) continue;
                if (RoomSite.Geyser(map, c))
                    return "refused: a steam geyser at " + c.x + "," + c.z + " touches the pile's box -- leave its 5x5 for a geothermal generator; camp x,z elsewhere";
            }
            foreach (IntVec3 c in rock)
            {
                // rock still inside after the slide: mined out (mining is the one setup step that needs the clock -- the ladder's lock allows it)
                if (map.designationManager.DesignationAt(c, DesignationDefOf.Mine) == null)
                { map.designationManager.AddDesignation(new Designation(c, DesignationDefOf.Mine)); mined++; }
            }
            foreach (IntVec3 c in inside)
            {
                Plant p = c.GetPlant(map);
                if (p != null && p.def.plant.IsTree && map.designationManager.DesignationOn(p) == null)
                { map.designationManager.AddDesignation(new Designation(p, DesignationDefOf.HarvestPlant)); chop++; }
            }
            // the door faces the crew (or the anchor's north if the crew stands inside the box)
            IntVec3 crew = CrewCentre(map);
            IntVec3 doorCell;
            if (crew.IsValid && !inside.Contains(crew))
            {
                int dx = crew.x - inside.CenterCell.x, dz = crew.z - inside.CenterCell.z;
                doorCell = Math.Abs(dx) >= Math.Abs(dz)
                    ? new IntVec3(dx > 0 ? ring.maxX : ring.minX, 0, inside.CenterCell.z)
                    : new IntVec3(inside.CenterCell.x, 0, dz > 0 ? ring.maxZ : ring.minZ);
            }
            else doorCell = new IntVec3(inside.CenterCell.x, 0, ring.minZ);

            int walls = 0, doors = 0, kept = 0, blocked = 0;
            foreach (IntVec3 c in ring.EdgeCells)
            {
                if (inside.Contains(c)) continue;
                Building ed = c.GetEdifice(map);
                if (ed != null && (ed.def.passability == Traversability.Impassable || ed is Building_Door)) { kept++; continue; }
                if (c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame)) { kept++; continue; }
                ThingDef def = c == doorCell ? door : wall;
                if (!GenConstruct.CanPlaceBlueprintAt(def, c, Rot4.North, map, false, null, null, wood).Accepted) { blocked++; continue; }
                GenConstruct.PlaceBlueprintForBuild(def, c, map, Rot4.North, Faction.OfPlayer, wood);
                if (def == door) doors++; else walls++;
            }
            if (walls + doors == 0 && kept == 0) return "refused: nothing of the ring could be placed around " + anchor.x + "," + anchor.z;

            foreach (IntVec3 c in inside) map.areaManager.BuildRoof[c] = true;
            if (camp != null) camp.storageBox = ring;
            // the camp is Home from the first wall: fires inside it get fought, floors cleaned (run 3: no Home, 47 fire cells)
            foreach (IntVec3 c in ring) map.areaManager.Home[c] = true;

            // the stockpile covers the inside, over the supplies where they lie
            Zone_Stockpile store = map.zoneManager.AllZones.OfType<Zone_Stockpile>().FirstOrDefault(z => z.label == "Main store");
            if (store == null)
            {
                store = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
                map.zoneManager.RegisterZone(store);
                store.settings.filter.SetAllowAll(null);
                store.settings.filter.SetAllow(ThingCategoryDefOf.Corpses, false);
                store.label = "Main store";
            }
            int zoned = 0;
            foreach (IntVec3 c in inside)
            {
                if (map.zoneManager.ZoneAt(c) != null) continue;
                if (!c.Standable(map) && c.GetFirstItem(map) == null) continue;
                store.AddCell(c); zoned++;
            }
            int cost = walls * wall.CostStuffCount + doors * door.CostStuffCount;
            return "ok: storage room around the supplies -- inside " + w + "x" + h + " from " + inside.minX + "," + inside.minZ +
                   ", door at " + doorCell.x + "," + doorCell.z + ", " + walls + " walls + " + doors + " door planned (" + kept + " kept, " +
                   blocked + " blocked), roof marked, Main store covers " + zoned + " more cells (" + pile.Count + " item stacks inside)" +
                   shifted + (mined > 0 ? ", " + mined + " rock cell(s) inside marked to mine (needs time running and Mining on)" : "") +
                   (chop > 0 ? ", " + chop + " trees inside marked to chop" : "") + "; needs about " + cost +
                   " wood -- chop if short, keep Construction on; the supplies stay where they are and come under the roof";
        }
    }
}
