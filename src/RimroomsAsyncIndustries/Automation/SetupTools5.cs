using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Batch 2 of the rebuilt ladder's commands (2026-10-13 inventory section D; owner: "still open stuff go").
    ///   {"cmd":"equip","pawn":"Gee","x":"..","z":".."} or "def":"Gun_BoltActionRifle"; "sidearm":"true" carries it instead
    ///   {"cmd":"capture","pawn":"Gee"}                  the nearest downed enemy to a prisoner bed (one must exist)
    ///   {"cmd":"bill_count","x":"..","z":"..","recipe":"CookMealSimple","count":"50"}   raise an existing bill's target
    ///   {"cmd":"zone_create","kind":"stockpile|growing","x":"..","z":"..","w":"..","h":"..","priority":"Preferred","plant":"Plant_Corn"}
    ///   {"cmd":"roof_area","x":"..","z":"..","w":"..","h":"..","mode":"roof|noroof|clear"}
    ///   {"cmd":"mine","x":"..","z":"..","w":"..","h":".."}  natural rock designated to mine (cell or rectangle)
    ///   {"cmd":"home_area","x":"..","z":"..","w":"..","h":".."}  the Home area over a rectangle (mode remove clears)
    ///   {"cmd":"firebreak","w":"3"}                     cut plants in a ring that wide around the Home area
    ///   {"cmd":"pen","x":"..","z":"..","w":"..","h":".."}  fence ring + fence gate + animal pen marker
    ///   {"cmd":"bury"}                                  a grave blueprint near the camp edge (corpses get hauled in)
    ///   {"cmd":"ideo_role","role":"leader|moral guide","pawn":"Gee"}
    ///   {"cmd":"save_game","name":"Unity-..."}
    /// </summary>
    internal static class SetupTools5
    {
        private static int Int(Dictionary<string, string> a, string k, int d) =>
            a.TryGetValue(k, out string s) && int.TryParse(s, NumberStyles.Integer, CultureInfo.InvariantCulture, out int v) ? v : d;

        private static Pawn One(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("pawn", out string who);
            return map.mapPawns.FreeColonistsSpawned.FirstOrDefault(p => p.LabelShort.Equals(who ?? "", StringComparison.OrdinalIgnoreCase));
        }

        private static CellRect Rect(Map map, Dictionary<string, string> a) =>
            new CellRect(Int(a, "x", 0), Int(a, "z", 0), Math.Max(1, Int(a, "w", 1)), Math.Max(1, Int(a, "h", 1))).ClipInsideMap(map);

        public static string Equip(Map map, Dictionary<string, string> a)
        {
            Pawn p = One(map, a);
            if (p == null) return "refused: name the colonist (pawn)";
            ThingWithComps gun = null;
            IntVec3 c = new IntVec3(Int(a, "x", -1), 0, Int(a, "z", -1));
            if (c.InBounds(map)) gun = c.GetThingList(map).OfType<ThingWithComps>().FirstOrDefault(t => t.def.IsWeapon);
            if (gun == null)
            {
                a.TryGetValue("def", out string def);
                gun = map.listerThings.ThingsInGroup(ThingRequestGroup.Weapon).OfType<ThingWithComps>()
                         .Where(t => (string.IsNullOrEmpty(def) || t.def.defName == def) && !t.IsForbidden(p) && p.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some))
                         .OrderByDescending(t => t.def.IsRangedWeapon).ThenBy(t => t.Position.DistanceToSquared(p.Position)).FirstOrDefault();
            }

            if (gun == null) return "refused: no reachable weapon" + (c.InBounds(map) ? " at " + c.x + "," + c.z : "");
            bool sidearm = a.TryGetValue("sidearm", out string sa) && sa.StartsWith("t", StringComparison.OrdinalIgnoreCase);
            Job job = sidearm ? JobMaker.MakeJob(JobDefOf.TakeInventory, gun) : JobMaker.MakeJob(JobDefOf.Equip, gun);
            if (sidearm) job.count = 1;
            p.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            return "ok: " + p.LabelShort + " going to " + (sidearm ? "carry " : "equip ") + gun.LabelShort + " at " + gun.Position.x + "," + gun.Position.z;
        }

        public static string Capture(Map map, Dictionary<string, string> a)
        {
            Pawn p = One(map, a) ?? map.mapPawns.FreeColonistsSpawned.FirstOrDefault(x => !x.Downed && !x.Drafted);
            if (p == null) return "refused: no free colonist";
            Pawn target = map.mapPawns.AllPawnsSpawned.Where(x => x.Downed && x.RaceProps.Humanlike && x.HostileTo(Faction.OfPlayer) && !x.IsPrisonerOfColony)
                             .OrderBy(x => x.Position.DistanceToSquared(p.Position)).FirstOrDefault();
            if (target == null) return "ok: no downed enemy to capture";
            Building_Bed bed = RestUtility.FindBedFor(target, p, false, false, GuestStatus.Prisoner);
            if (bed == null) return "refused: no free prisoner bed -- bed_prisoner on a bed first";
            Job job = JobMaker.MakeJob(JobDefOf.Capture, target, bed);
            job.count = 1;
            p.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            return "ok: " + p.LabelShort + " capturing " + target.LabelShort + " to the bed at " + bed.Position.x + "," + bed.Position.z;
        }

        public static string BillCount(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("recipe", out string recipe);
            int want = Math.Max(1, Int(a, "count", 10)), n = 0;
            foreach (Building_WorkTable w in map.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>())
                foreach (Bill_Production b in w.BillStack.Bills.OfType<Bill_Production>())
                    if (b.recipe.defName == recipe)
                    {
                        b.repeatMode = BillRepeatModeDefOf.TargetCount;
                        b.targetCount = want;
                        n++;
                    }

            return n == 0 ? "refused: no bill for " + recipe + " -- add_bill first" : "ok: " + n + " " + recipe + " bill(s) now do until " + want;
        }

        public static string ZoneCreate(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("kind", out string kind);
            CellRect r = Rect(map, a);
            List<IntVec3> cells = r.Cells.Where(c => !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null && map.zoneManager.ZoneAt(c) == null).ToList();
            if (cells.Count == 0) return "refused: no free cells in that rectangle";
            Zone z;
            if ((kind ?? "stockpile") == "growing")
            {
                var g = new Zone_Growing(map.zoneManager);
                map.zoneManager.RegisterZone(g);
                foreach (IntVec3 c in cells.Where(c => c.GetFertility(map) > 0f)) g.AddCell(c);
                a.TryGetValue("plant", out string pl);
                ThingDef plant = DefDatabase<ThingDef>.GetNamedSilentFail(pl ?? "");
                if (plant?.plant != null) g.SetPlantDefToGrow(plant);
                z = g;
            }
            else
            {
                var s = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
                map.zoneManager.RegisterZone(s);
                foreach (IntVec3 c in cells) s.AddCell(c);
                if (a.TryGetValue("priority", out string pr) && Enum.TryParse(pr, true, out StoragePriority sp)) s.settings.Priority = sp;
                z = s;
            }

            if (a.TryGetValue("label", out string label) && !string.IsNullOrEmpty(label)) z.label = label;
            return "ok: " + z.label + " with " + z.Cells.Count + " cells from " + r.minX + "," + r.minZ;
        }

        public static string RoofArea(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("mode", out string mode);
            mode = mode ?? "roof";
            CellRect r = Rect(map, a);
            int set = 0, unsupported = 0;
            foreach (IntVec3 c in r)
            {
                if (mode == "roof")
                {
                    // Core only holds a roof within 6 cells of a wall or rock (test run 2026-10-13: a roof zone was drawn
                    // over open ground with no wall under it and called "a proper room"); mark only what can stand.
                    bool support = GenRadial.RadialCellsAround(c, 6f, true).Any(o => o.InBounds(map) && o.GetEdifice(map) != null &&
                        (o.GetEdifice(map).def.holdsRoof || (o.GetEdifice(map).def.building != null && o.GetEdifice(map).def.building.isNaturalRock)));
                    if (!support) { unsupported++; continue; }
                }
                map.areaManager.BuildRoof[c] = mode == "roof";
                map.areaManager.NoRoof[c] = mode == "noroof";
                set++;
            }
            if (mode == "roof" && set == 0)
                return "refused: no cell of that " + r.Width + "x" + r.Height + " has a wall or rock within 6 cells to hold a roof -- walls first (build_room / storage_room / shelter), then the roof";
            return "ok: " + mode + " over " + set + " cells of " + r.Width + "x" + r.Height + " from " + r.minX + "," + r.minZ +
                   (unsupported > 0 ? " (" + unsupported + " cells skipped: nothing within 6 cells to hold a roof)" : "");
        }

        /// <summary>
        ///   {"cmd":"mine","x":"..","z":".."}  or with "w","h"   natural rock designated to mine (the test run had no way to
        ///   dig a cell: she tried deconstruct on raw rock four times). Only rock and ore; walls are deconstruct, not mine.
        /// </summary>
        /// <summary>
        ///   {"cmd":"home_area","x":"..","z":"..","w":"..","h":".."}  the Home area over that rectangle (mode "remove" clears it).
        ///   Colonists fight fires, clean and haul only inside Home. Run 3 (2026-10-13 21:51-21:53): she hunted the Home
        ///   designator through the zone list four times and drew a growing zone over the burning cells instead.
        /// </summary>
        public static string HomeArea(Map map, Dictionary<string, string> a)
        {
            CellRect r = Rect(map, a);
            a.TryGetValue("mode", out string mode);
            bool on = !(mode ?? "").StartsWith("rem", StringComparison.OrdinalIgnoreCase);
            int n = 0;
            foreach (IntVec3 c in r) { if (map.areaManager.Home[c] != on) { map.areaManager.Home[c] = on; n++; } }
            return "ok: Home " + (on ? "added over " : "removed from ") + n + " cells of " + r.Width + "x" + r.Height + " from " + r.minX + "," + r.minZ +
                   " (Home now " + map.areaManager.Home.TrueCount + " cells)";
        }

        public static string Mine(Map map, Dictionary<string, string> a)
        {
            CellRect r = Rect(map, a);
            int marked = 0, already = 0, notRock = 0;
            foreach (IntVec3 c in r)
            {
                if (map.fogGrid.IsFogged(c)) { notRock++; continue; }
                Building ed = c.GetEdifice(map);
                bool rock = ed != null && (ed.def.mineable || (ed.def.building != null && ed.def.building.isNaturalRock));
                if (!rock) { notRock++; continue; }
                if (map.designationManager.DesignationAt(c, DesignationDefOf.Mine) != null) { already++; continue; }
                map.designationManager.AddDesignation(new Designation(c, DesignationDefOf.Mine));
                marked++;
            }
            if (marked == 0 && already == 0) return "refused: no natural rock in that " + r.Width + "x" + r.Height + " (a built wall is deconstruct; open ground needs nothing)";
            return "ok: " + marked + " rock cell(s) marked to mine" + (already > 0 ? ", " + already + " already marked" : "") +
                   (notRock > 0 ? ", " + notRock + " skipped (not rock)" : "") + " -- someone needs Mining work on";
        }

        /// <summary>
        /// The owner's "delete the east wall thats planned by cancle tool": every blueprint, frame and work designation in a rect
        /// is cancelled.  {"cmd":"cancel","x":"..","z":"..","w":"..","h":".."}
        /// </summary>
        public static string Cancel(Map map, Dictionary<string, string> a)
        {
            CellRect r = Rect(map, a);
            int plans = 0, desigs = 0;
            foreach (IntVec3 c in r)
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                    if (t.def.IsBlueprint || t.def.IsFrame) { t.Destroy(DestroyMode.Cancel); plans++; }
                foreach (Designation d in map.designationManager.AllDesignationsAt(c).ToList())
                { map.designationManager.RemoveDesignation(d); desigs++; }
            }
            if (plans + desigs == 0) return "refused: nothing planned or designated in that " + r.Width + "x" + r.Height + " from " + r.minX + "," + r.minZ;
            return "ok: cancelled " + plans + " planned building(s) and " + desigs + " designation(s) in " + r.Width + "x" + r.Height + " from " + r.minX + "," + r.minZ;
        }

        public static string Firebreak(Map map, Dictionary<string, string> a)
        {
            Area home = map.areaManager.Home;
            if (home == null || home.TrueCount == 0) return "refused: no home area";
            int width = Math.Max(1, Math.Min(6, Int(a, "w", 3))), n = 0;
            var ring = new HashSet<IntVec3>();
            foreach (IntVec3 c in home.ActiveCells)
                foreach (IntVec3 o in GenRadial.RadialCellsAround(c, width, true))
                    if (o.InBounds(map) && !home[o]) ring.Add(o);
            foreach (IntVec3 c in ring)
            {
                Plant p = c.GetPlant(map);
                if (p == null || map.designationManager.DesignationOn(p) != null) continue;
                map.designationManager.AddDesignation(new Designation(p, DesignationDefOf.CutPlant));
                n++;
            }

            return "ok: " + n + " plants marked to cut in a " + width + "-wide ring around Home";
        }

        public static string Pen(Map map, Dictionary<string, string> a)
        {
            ThingDef fence = DefDatabase<ThingDef>.GetNamedSilentFail("Fence"), gate = DefDatabase<ThingDef>.GetNamedSilentFail("FenceGate");
            ThingDef marker = DefDatabase<ThingDef>.GetNamedSilentFail("PenMarker");
            if (fence == null || gate == null) return "refused: no Fence/FenceGate defs";
            CellRect r = Rect(map, a);
            if (r.Width < 3 || r.Height < 3) return "refused: a pen needs at least 3x3";
            IntVec3 gateCell = new IntVec3(r.minX + r.Width / 2, 0, r.minZ);
            int placed = 0;
            foreach (IntVec3 c in r.EdgeCells)
            {
                ThingDef d = c == gateCell ? gate : fence;
                ThingDef stuff = d.MadeFromStuff ? ThingDefOf.WoodLog : null;
                if (GenConstruct.CanPlaceBlueprintAt(d, c, Rot4.North, map, false, null, null, stuff).Accepted)
                { GenConstruct.PlaceBlueprintForBuild(d, c, map, Rot4.North, Faction.OfPlayer, stuff); placed++; }
            }

            if (marker != null && GenConstruct.CanPlaceBlueprintAt(marker, r.CenterCell, Rot4.North, map).Accepted)
                GenConstruct.PlaceBlueprintForBuild(marker, r.CenterCell, map, Rot4.North, Faction.OfPlayer, null);
            return "ok: pen " + r.Width + "x" + r.Height + ": " + placed + " fence/gate blueprints, gate at " + gateCell.x + "," + gateCell.z + ", no roof";
        }

        public static string Bury(Map map, Dictionary<string, string> a)
        {
            ThingDef grave = DefDatabase<ThingDef>.GetNamedSilentFail("Grave");
            if (grave == null) return "refused: no Grave def";
            Area home = map.areaManager.Home;
            List<Pawn> crew = map.mapPawns.FreeColonistsSpawned.ToList();
            if (crew.Count == 0) return "refused: no colonists";
            IntVec3 centre = new IntVec3((int)crew.Average(p => p.Position.x), 0, (int)crew.Average(p => p.Position.z));
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, 30f, true).Skip(150))
            {
                if (home != null && home[c]) continue;
                if (GenConstruct.CanPlaceBlueprintAt(grave, c, Rot4.North, map).Accepted)
                {
                    GenConstruct.PlaceBlueprintForBuild(grave, c, map, Rot4.North, Faction.OfPlayer, null);
                    return "ok: grave blueprint at " + c.x + "," + c.z + " (outside the home area) -- corpses get hauled in once it is dug";
                }
            }

            return "refused: no spot for a grave within 30 cells of the crew";
        }

        public static string IdeoRole(Map map, Dictionary<string, string> a)
        {
            if (!ModsConfig.IdeologyActive) return "refused: Ideology is not active";
            Pawn p = One(map, a);
            if (p == null) return "refused: name the colonist (pawn)";
            a.TryGetValue("role", out string want);
            want = (want ?? "leader").ToLowerInvariant();
            Ideo ideo = p.Ideo;
            if (ideo == null) return "refused: " + p.LabelShort + " has no ideoligion";
            Precept_Role role = ideo.RolesListForReading.FirstOrDefault(r => r.def.label.ToLowerInvariant().Contains(want) || r.LabelCap.ToString().ToLowerInvariant().Contains(want));
            if (role == null) return "refused: no role like " + want + " (have: " + string.Join(", ", ideo.RolesListForReading.Select(r => r.LabelCap.ToString()).ToArray()) + ")";
            if (!role.RequirementsMet(p)) return "refused: " + p.LabelShort + " does not meet the " + role.LabelCap + " requirements";
            role.Assign(p, true);
            return "ok: " + p.LabelShort + " is now " + role.LabelCap;
        }

        public static string SaveGame(Dictionary<string, string> a)
        {
            a.TryGetValue("name", out string name);
            name = string.IsNullOrEmpty(name) ? "Unity-autosave" : name;
            if (!name.StartsWith("Unity", StringComparison.OrdinalIgnoreCase)) name = "Unity-" + name;   // never overwrite the owner's saves
            LongEventHandler.QueueLongEvent(() => GameDataSaveLoader.SaveGame(name), "SavingLongEvent", false, null);
            return "ok: saving as " + name;
        }
    }
}
