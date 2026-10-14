using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The commands the rebuilt RimPLC ladder drives (2026-10-13 inventory, section D). Owner: "cant u work on romplc or
    /// something lots of code and doc work". Each returns a read-back the model can check; nothing here clicks.
    ///   {"cmd":"build","def":"TorchLamp","x":"10","z":"20","rot":"0","stuff":"WoodLog"}   any architect def as a blueprint
    ///   {"cmd":"build_room","x":"..","z":"..","w":"5","h":"7","stuff":"WoodLog"}            walls + door + roof, inside w x h
    ///   {"cmd":"deconstruct","def":"CraftingSpot"} or x,z                                  designate Deconstruct
    ///   {"cmd":"harvest","what":"food|medicine|all"}                                       wild berries / healroot / agave
    ///   {"cmd":"tame","def":"Muffalo"}  {"cmd":"slaughter","def":"Chicken","count":"2"}    animal designations
    ///   {"cmd":"allow_area","x":"..","z":"..","w":"..","h":".."}                           unforbid a rectangle
    ///   {"cmd":"self_tend","pawn":"Gee|all","on":"true"}                                   playerSettings.selfTend
    ///   {"cmd":"schedule","pawn":"all","hours":"0-23","assignment":"Anything"}             timetable
    ///   {"cmd":"drug_policy","pawn":"all","policy":"No drugs"}                             assign a drug policy
    ///   {"cmd":"research","project":"Electricity"}                                         the current project
    ///   {"cmd":"bed_medical"|"bed_prisoner","x":"..","z":"..","on":"true"}                  bed use
    ///   {"cmd":"cooler_temp","x":"..","z":"..","celsius":"-5"}                             a cooler/heater target
    /// </summary>
    internal static class SetupTools4
    {
        private static int Int(Dictionary<string, string> a, string k, int dflt) =>
            a.TryGetValue(k, out string s) && int.TryParse(s, NumberStyles.Integer, CultureInfo.InvariantCulture, out int v) ? v : dflt;

        private static bool On(Dictionary<string, string> a) =>
            !a.TryGetValue("on", out string s) || s == null || !s.Trim().StartsWith("f", StringComparison.OrdinalIgnoreCase);

        private static List<Pawn> Crew(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("pawn", out string who);
            List<Pawn> all = map.mapPawns.FreeColonistsSpawned.ToList();
            if (string.IsNullOrEmpty(who) || who.Equals("all", StringComparison.OrdinalIgnoreCase)) return all;
            return all.Where(p => p.LabelShort.Equals(who, StringComparison.OrdinalIgnoreCase) ||
                                  (p.Name?.ToStringFull ?? "").IndexOf(who, StringComparison.OrdinalIgnoreCase) >= 0).ToList();
        }

        private static IntVec3 Cell(Dictionary<string, string> a) => new IntVec3(Int(a, "x", -1), 0, Int(a, "z", -1));

        public static string Build(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("def", out string defName);
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName ?? "");
            if (def == null || !def.BuildableByPlayer) return "refused: no buildable def " + defName;
            IntVec3 c = Cell(a);
            if (!c.InBounds(map)) return "refused: x,z outside the map";
            Rot4 rot = new Rot4(Math.Max(0, Math.Min(3, Int(a, "rot", 0))));
            ThingDef stuff = null;
            if (def.MadeFromStuff)
            {
                a.TryGetValue("stuff", out string sn);
                stuff = DefDatabase<ThingDef>.GetNamedSilentFail(sn ?? "") ?? GenStuff.DefaultStuffFor(def);
            }

            AcceptanceReport ok = GenConstruct.CanPlaceBlueprintAt(def, c, rot, map, false, null, null, stuff);
            if (!ok.Accepted) return "refused: " + def.defName + " cannot go at " + c.x + "," + c.z + ": " + (ok.Reason ?? "blocked");
            GenConstruct.PlaceBlueprintForBuild(def, c, map, rot, Faction.OfPlayer, stuff);
            return "ok: " + def.defName + (stuff != null ? " (" + stuff.defName + ")" : "") + " blueprint at " + c.x + "," + c.z +
                   " rot " + rot.AsInt + " -- needs material on site and Construction work on";
        }

        public static string BuildRoom(Map map, Dictionary<string, string> a)
        {
            int w = Math.Max(2, Math.Min(20, Int(a, "w", 5))), h = Math.Max(2, Math.Min(20, Int(a, "h", 7)));
            IntVec3 c0 = Cell(a);
            if (!c0.InBounds(map)) return "refused: x,z (the inside corner) outside the map";
            a.TryGetValue("stuff", out string sn);
            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(sn ?? "") ?? ThingDefOf.WoodLog;
            var ring = new List<IntVec3>();
            for (int dx = -1; dx <= w; dx++)
                for (int dz = -1; dz <= h; dz++)
                    if (dx == -1 || dz == -1 || dx == w || dz == h) ring.Add(new IntVec3(c0.x + dx, 0, c0.z + dz));
            IntVec3 door = new IntVec3(c0.x + w / 2, 0, c0.z - 1);
            int placed = 0, kept = 0, blocked = 0;
            foreach (IntVec3 c in ring)
            {
                if (!c.InBounds(map)) { blocked++; continue; }
                Building ed = c.GetEdifice(map);
                if (ed != null && (ed.def.passability == Traversability.Impassable || ed is Building_Door)) { kept++; continue; }
                ThingDef def = c == door ? ThingDefOf.Door : ThingDefOf.Wall;
                if (GenConstruct.CanPlaceBlueprintAt(def, c, Rot4.North, map, false, null, null, stuff).Accepted)
                {
                    GenConstruct.PlaceBlueprintForBuild(def, c, map, Rot4.North, Faction.OfPlayer, stuff);
                    placed++;
                }
                else blocked++;
            }

            for (int dx = 0; dx < w; dx++)
                for (int dz = 0; dz < h; dz++)
                {
                    IntVec3 c = new IntVec3(c0.x + dx, 0, c0.z + dz);
                    if (c.InBounds(map)) map.areaManager.BuildRoof[c] = true;
                }

            return (placed == 0 && kept == 0 ? "refused: " : "ok: ") + "room inside " + w + "x" + h + " from " + c0.x + "," + c0.z + ": " +
                   placed + " wall/door blueprints, " + kept + " existing walls kept, " + blocked + " blocked; door at " + door.x + "," + door.z + "; roof marked";
        }

        public static string Deconstruct(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("def", out string defName);
            IEnumerable<Building> targets;
            if (!string.IsNullOrEmpty(defName)) targets = map.listerBuildings.allBuildingsColonist.Where(b => b.def.defName == defName);
            else
            {
                Building ed = Cell(a).InBounds(map) ? Cell(a).GetEdifice(map) : null;
                targets = ed != null && ed.Faction == Faction.OfPlayer ? new[] { ed } : new Building[0];
            }

            int n = 0;
            foreach (Building b in targets.ToList())
            {
                if (!b.DeconstructibleBy(Faction.OfPlayer).Accepted || map.designationManager.DesignationOn(b, DesignationDefOf.Deconstruct) != null) continue;
                map.designationManager.AddDesignation(new Designation(b, DesignationDefOf.Deconstruct));
                n++;
            }

            return n == 0 ? "refused: nothing of ours to deconstruct there" : "ok: " + n + " marked to deconstruct";
        }

        public static string Harvest(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("what", out string what);
            what = (what ?? "all").ToLowerInvariant();
            int n = 0;
            foreach (Plant p in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant).OfType<Plant>().ToList())
            {
                if (!p.HarvestableNow || p.def.plant.IsTree || map.fogGrid.IsFogged(p.Position) || map.zoneManager.ZoneAt(p.Position) != null) continue;
                ThingDef yield = p.def.plant.harvestedThingDef;
                if (yield == null) continue;
                bool food = yield.IsNutritionGivingIngestible, med = yield.IsMedicine;
                if ((what == "food" && !food) || (what == "medicine" && !med) || (!food && !med)) continue;
                if (map.designationManager.DesignationOn(p) != null) continue;
                map.designationManager.AddDesignation(new Designation(p, DesignationDefOf.HarvestPlant));
                n++;
            }

            return n == 0 ? "ok: nothing wild and ripe to harvest (" + what + ")" : "ok: " + n + " wild plants marked to harvest -- someone needs Growing/PlantCut work on";
        }

        private static readonly string[] NeverTouch = { "Boomalope", "Boomrat", "Thrumbo", "Megasloth" };

        public static string Tame(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("def", out string defName);
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.Where(p => p.RaceProps.Animal && p.Faction == null && !p.Downed).ToList())
            {
                if (!string.IsNullOrEmpty(defName) && p.def.defName != defName) continue;
                if (NeverTouch.Contains(p.def.defName) || p.RaceProps.predator && p.BodySize > 1.2f) continue;
                if (!TameUtility.CanTame(p) || map.designationManager.DesignationOn(p) != null) continue;
                map.designationManager.AddDesignation(new Designation(p, DesignationDefOf.Tame));
                n++;
            }

            return n == 0 ? "ok: no safe animal to tame" + (defName != null ? " of " + defName : "") : "ok: " + n + " marked to tame -- someone needs Handling work on and food in hand";
        }

        public static string Slaughter(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("def", out string defName);
            int want = Math.Max(1, Int(a, "count", 1)), n = 0;
            foreach (Pawn p in map.mapPawns.SpawnedColonyAnimals.Where(p => p.def.defName == defName).OrderBy(p => p.ageTracker.AgeBiologicalYears).ToList())
            {
                if (n >= want) break;
                if (p.GetComp<CompMilkable>() != null && p.gender == Gender.Female) continue;   // never the milkers
                if (p.playerSettings?.RespectedMaster != null) continue;                        // never a bonded or ridden animal
                if (map.designationManager.DesignationOn(p, DesignationDefOf.Slaughter) != null) continue;
                map.designationManager.AddDesignation(new Designation(p, DesignationDefOf.Slaughter));
                n++;
            }

            return n == 0 ? "refused: no " + defName + " that may be slaughtered (milkers and bonded animals are kept)" : "ok: " + n + " " + defName + " marked to slaughter";
        }

        public static string AllowArea(Map map, Dictionary<string, string> a)
        {
            CellRect r = new CellRect(Int(a, "x", 0), Int(a, "z", 0), Math.Max(1, Int(a, "w", 1)), Math.Max(1, Int(a, "h", 1))).ClipInsideMap(map);
            int n = 0;
            foreach (IntVec3 c in r)
                foreach (Thing t in c.GetThingList(map).ToList())
                    if (t.def.category == ThingCategory.Item && t.IsForbidden(Faction.OfPlayer)) { t.SetForbidden(false, false); n++; }
            return "ok: " + n + " items unforbidden in " + r.Width + "x" + r.Height + " from " + r.minX + "," + r.minZ;
        }

        public static string SelfTend(Map map, Dictionary<string, string> a)
        {
            bool on = On(a);
            List<Pawn> crew = Crew(map, a);
            if (crew.Count == 0) return "refused: no such colonist";
            foreach (Pawn p in crew) if (p.playerSettings != null) p.playerSettings.selfTend = on;
            return "ok: self-tend " + (on ? "on" : "off") + " for " + string.Join(", ", crew.Select(p => p.LabelShort).ToArray());
        }

        public static string Schedule(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("assignment", out string an);
            TimeAssignmentDef def = DefDatabase<TimeAssignmentDef>.AllDefsListForReading
                .FirstOrDefault(d => d.defName.Equals(an ?? "Anything", StringComparison.OrdinalIgnoreCase) || d.label.Equals(an ?? "", StringComparison.OrdinalIgnoreCase));
            if (def == null) return "refused: assignment is one of " + string.Join(", ", DefDatabase<TimeAssignmentDef>.AllDefsListForReading.Select(d => d.defName).ToArray());
            int from = 0, to = 23;
            if (a.TryGetValue("hours", out string hs) && hs.Contains("-"))
            {
                string[] p = hs.Split('-');
                int.TryParse(p[0], out from); int.TryParse(p[1], out to);
            }

            List<Pawn> crew = Crew(map, a);
            if (crew.Count == 0) return "refused: no such colonist";
            foreach (Pawn p in crew)
                for (int hr = Math.Max(0, from); hr <= Math.Min(23, to); hr++) p.timetable?.SetAssignment(hr, def);
            return "ok: " + def.defName + " hours " + from + "-" + to + " for " + string.Join(", ", crew.Select(p => p.LabelShort).ToArray());
        }

        public static string DrugPolicyCmd(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("policy", out string want);
            DrugPolicy pol = Current.Game.drugPolicyDatabase.AllPolicies
                .FirstOrDefault(p => p.label.Equals(want ?? "No drugs", StringComparison.OrdinalIgnoreCase)) ??
                Current.Game.drugPolicyDatabase.AllPolicies.FirstOrDefault(p => p.label.IndexOf(want ?? "no drug", StringComparison.OrdinalIgnoreCase) >= 0);
            if (pol == null) return "refused: no drug policy " + want + " (have: " + string.Join(", ", Current.Game.drugPolicyDatabase.AllPolicies.Select(p => p.label).ToArray()) + ")";
            List<Pawn> crew = Crew(map, a);
            if (crew.Count == 0) return "refused: no such colonist";
            foreach (Pawn p in crew) if (p.drugs != null) p.drugs.CurrentPolicy = pol;
            return "ok: drug policy '" + pol.label + "' for " + string.Join(", ", crew.Select(p => p.LabelShort).ToArray());
        }

        public static string Research(Dictionary<string, string> a)
        {
            a.TryGetValue("project", out string want);
            ResearchProjectDef r = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(want ?? "") ??
                DefDatabase<ResearchProjectDef>.AllDefsListForReading.FirstOrDefault(p => p.label.Equals(want ?? "", StringComparison.OrdinalIgnoreCase));
            if (r == null) return "refused: no research project " + want;
            if (r.IsFinished) return "ok: " + r.label + " is already finished";
            if (!r.CanStartNow) return "refused: " + r.label + " cannot start yet (prerequisites or a bench it needs)";
            Find.ResearchManager.SetCurrentProject(r);
            return "ok: researching " + r.label + " -- someone needs Research work on at a bench";
        }

        public static string BedUse(Map map, Dictionary<string, string> a, bool prisoner)
        {
            Building_Bed bed = Cell(a).InBounds(map) ? Cell(a).GetThingList(map).OfType<Building_Bed>().FirstOrDefault() : null;
            if (bed == null) return "refused: no bed at " + Int(a, "x", -1) + "," + Int(a, "z", -1);
            bool on = On(a);
            if (prisoner) bed.ForPrisoners = on;
            else bed.Medical = on;
            return "ok: bed at " + bed.Position.x + "," + bed.Position.z + (prisoner ? " for prisoners " : " medical ") + (on ? "on" : "off");
        }

        public static string CoolerTemp(Map map, Dictionary<string, string> a)
        {
            IntVec3 c = Cell(a);
            CompTempControl comp = c.InBounds(map) ? c.GetThingList(map).Select(t => t.TryGetComp<CompTempControl>()).FirstOrDefault(x => x != null) : null;
            if (comp == null) return "refused: no cooler or heater at " + c.x + "," + c.z;
            if (!a.TryGetValue("celsius", out string cs) || !float.TryParse(cs, NumberStyles.Float, CultureInfo.InvariantCulture, out float tc)) return "refused: celsius is a number";
            comp.targetTemperature = Math.Max(-50f, Math.Min(50f, tc));
            return "ok: target " + comp.targetTemperature.ToString("0", CultureInfo.InvariantCulture) + "C at " + c.x + "," + c.z;
        }
    }
}
