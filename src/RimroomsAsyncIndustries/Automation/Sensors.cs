using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The PLC's input scan. Owner, 2026-10-13: "and you do know what and how a real PLC works right? ... sensors ...
    /// and a way to read it all" / "for everything in the game and everythign in all mods". Every list here is walked
    /// generically (all defs, all alerts, all conditions), so items, buildings, alerts and conditions added by any mod
    /// show up without naming them. Written to Config/RimroomsAutomation/sensors.json every ScanEveryTicks, and on the
    /// "sensors" command (a paused game does not tick). One reading per key; nothing here acts on the game.
    /// </summary>
    internal static class Sensors
    {
        public const int ScanEveryTicks = 600;

        public static string Write(Map map, string folder)
        {
            string json = Dump(map);
            Directory.CreateDirectory(folder);
            string path = Path.Combine(folder, "sensors.json");
            string tmp = path + ".tmp";
            File.WriteAllText(tmp, json);
            if (File.Exists(path)) File.Delete(path);
            File.Move(tmp, path);
            return "ok: sensors.json written, " + json.Length + " bytes";
        }

        private sealed class J
        {
            private readonly StringBuilder sb = new StringBuilder();
            private bool first = true;
            public J Open(char c) { Sep(); sb.Append(c); first = true; return this; }
            public J Close(char c) { sb.Append(c); first = false; return this; }
            public J Key(string k) { Sep(); Str(k); sb.Append(':'); first = true; return this; }
            public J Val(object v)
            {
                Sep();
                if (v == null) sb.Append("null");
                else if (v is bool b) sb.Append(b ? "true" : "false");
                else if (v is int || v is long) sb.Append(Convert.ToString(v, CultureInfo.InvariantCulture));
                else if (v is float || v is double)
                {
                    double d = Convert.ToDouble(v, CultureInfo.InvariantCulture);
                    sb.Append(double.IsNaN(d) || double.IsInfinity(d) ? "null" : Math.Round(d, 2).ToString(CultureInfo.InvariantCulture));
                }
                else Str(v.ToString());
                first = false; return this;
            }
            public J KV(string k, object v) { Key(k); return Val(v); }
            private void Sep() { if (!first) sb.Append(','); first = false; }
            private void Str(string s)
            {
                sb.Append('"');
                foreach (char c in s ?? "")
                {
                    if (c == '"' || c == '\\') sb.Append('\\').Append(c);
                    else if (c < ' ') sb.Append(' ');
                    else sb.Append(c);
                }
                sb.Append('"');
            }
            public override string ToString() => sb.ToString();
        }

        private static void Safe(J j, string key, Action body)
        {
            // one broken reading (a mod's odd def, an API change on 1.7) never loses the rest of the scan
            try { body(); }
            catch (Exception e) { j.KV(key + "_error", e.GetType().Name + ": " + e.Message); }
        }

        public static string Dump(Map map)
        {
            var j = new J();
            j.Open('{');
            j.KV("tick", Find.TickManager.TicksGame);
            j.KV("day", Find.TickManager.TicksGame / 60000);
            j.KV("paused", Find.TickManager.Paused);
            j.KV("map", map.uniqueID);
            Safe(j, "world", () =>
            {
                j.KV("season", GenLocalDate.Season(map).ToString());
                j.KV("hour", GenLocalDate.HourOfDay(map));
                j.KV("outdoor_temp", map.mapTemperature.OutdoorTemp);
                j.KV("weather", map.weatherManager.curWeather?.defName);
                j.KV("wealth", map.wealthWatcher.WealthTotal);
            });
            Safe(j, "conditions", () =>
            {
                j.Key("conditions").Open('[');
                foreach (GameCondition gc in map.gameConditionManager.ActiveConditions.Concat(Find.World.gameConditionManager.ActiveConditions))
                    j.Val(gc.def.defName);
                j.Close(']');
            });
            Safe(j, "items", () =>
            {
                // every item on seen ground, by def -- any mod's item included; stored = inside a stockpile or storage
                var all = new Dictionary<string, int>(); var stored = new Dictionary<string, int>(); int forbidden = 0;
                foreach (Thing t in map.listerThings.AllThings)
                {
                    if (t.def.category != ThingCategory.Item || !t.Spawned || map.fogGrid.IsFogged(t.Position)) continue;
                    all.TryGetValue(t.def.defName, out int n); all[t.def.defName] = n + t.stackCount;
                    if (t.IsInAnyStorage()) { stored.TryGetValue(t.def.defName, out int s); stored[t.def.defName] = s + t.stackCount; }
                    if (t.IsForbidden(Faction.OfPlayer)) forbidden++;
                }
                j.KV("items_forbidden", forbidden);
                j.Key("items").Open('{'); foreach (var kv in all.OrderBy(k => k.Key)) j.KV(kv.Key, kv.Value); j.Close('}');
                j.Key("items_stored").Open('{'); foreach (var kv in stored.OrderBy(k => k.Key)) j.KV(kv.Key, kv.Value); j.Close('}');
            });
            Safe(j, "buildings", () =>
            {
                var b = new Dictionary<string, int>(); int blueprints = 0, frames = 0;
                foreach (Building x in map.listerBuildings.allBuildingsColonist)
                { b.TryGetValue(x.def.defName, out int n); b[x.def.defName] = n + 1; }
                foreach (Thing t in map.listerThings.AllThings.Where(t => t.Faction == Faction.OfPlayer))
                { if (t.def.IsBlueprint) blueprints++; else if (t.def.IsFrame) frames++; }
                j.KV("blueprints", blueprints); j.KV("frames", frames);
                j.Key("buildings").Open('{'); foreach (var kv in b.OrderBy(k => k.Key)) j.KV(kv.Key, kv.Value); j.Close('}');
            });
            Safe(j, "bills", () =>
            {
                int rows = 0;
                j.Key("benches").Open('[');
                foreach (Building_WorkTable w in map.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>())
                {
                    rows += w.BillStack.Count;
                    j.Open('{').KV("def", w.def.defName).KV("x", w.Position.x).KV("z", w.Position.z).Key("bills").Open('[');
                    foreach (Bill bill in w.BillStack.Bills) j.Val(bill.recipe.defName + (bill.suspended ? " (suspended)" : ""));
                    j.Close(']').Close('}');
                }
                j.Close(']');
                j.KV("bill_rows", rows);
            });
            Safe(j, "research", () =>
            {
                ResearchProjectDef cur = CurrentResearch();
                j.KV("research_current", cur?.defName);
                j.KV("research_queue_empty", cur == null);
                j.Key("research_done").Open('[');
                foreach (ResearchProjectDef r in DefDatabase<ResearchProjectDef>.AllDefsListForReading.Where(r => r.IsFinished)) j.Val(r.defName);
                j.Close(']');
                ResearchProjectDef ship = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("ShipBasics");
                j.KV("ship_research_done", ship != null && ship.IsFinished);
            });
            Safe(j, "pawns", () =>
            {
                j.Key("pawns").Open('[');
                foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
                {
                    j.Open('{').KV("name", p.LabelShort).KV("x", p.Position.x).KV("z", p.Position.z)
                     .KV("downed", p.Downed).KV("drafted", p.Drafted).KV("mental", p.MentalStateDef?.defName)
                     .KV("mood", p.needs?.mood?.CurLevelPercentage).KV("food", p.needs?.food?.CurLevelPercentage)
                     .KV("rest", p.needs?.rest?.CurLevelPercentage).KV("bleeding", p.health?.hediffSet?.BleedRateTotal)
                     .KV("health", p.health?.summaryHealth?.SummaryHealthPercent)
                     .KV("weapon", p.equipment?.Primary?.def.defName).KV("job", p.CurJobDef?.defName);
                    j.Key("work").Open('{');
                    if (p.workSettings != null && p.workSettings.EverWork)
                        foreach (WorkTypeDef w in DefDatabase<WorkTypeDef>.AllDefsListForReading.Where(w => w.visible && !p.WorkTypeIsDisabled(w)))
                            j.KV(w.defName, p.workSettings.GetPriority(w));
                    j.Close('}');
                    j.Key("skills").Open('{');
                    if (p.skills != null)
                        foreach (SkillRecord s in p.skills.skills.Where(s => !s.TotallyDisabled))
                            j.KV(s.def.defName, s.Level + (s.passion == Passion.Major ? "++" : s.passion == Passion.Minor ? "+" : ""));
                    j.Close('}').Close('}');
                }
                j.Close(']');
                j.KV("colonists", map.mapPawns.FreeColonistsSpawnedCount);
                j.KV("prisoners", map.mapPawns.PrisonersOfColonySpawnedCount);
                j.KV("hostiles", map.mapPawns.AllPawnsSpawned.Count(p => !p.Dead && !p.Downed && p.HostileTo(Faction.OfPlayer)));
            });
            Safe(j, "rooms", () =>
            {
                j.Key("rooms").Open('[');
                foreach (Room r in map.regionGrid.AllRooms.Where(r => r != null && !r.PsychologicallyOutdoors && !r.IsDoorway && !r.TouchesMapEdge && r.CellCount < 2500))
                {
                    j.Open('{').KV("id", r.ID).KV("role", r.Role?.defName).KV("cells", r.CellCount).KV("temp", r.Temperature)
                     .KV("open_roof", r.OpenRoofCount).KV("beds", r.ContainedBeds.Count())
                     .KV("impressive", r.GetStat(RoomStatDefOf.Impressiveness)).Close('}');
                }
                j.Close(']');
            });
            Safe(j, "power", () =>
            {
                j.Key("power").Open('[');
                foreach (PowerNet net in map.powerNetManager.AllNetsListForReading)
                    j.Open('{').KV("gain_w", net.CurrentEnergyGainRate() / CompPower.WattsToWattDaysPerTick)
                     .KV("stored_wd", net.CurrentStoredEnergy()).KV("parts", net.powerComps.Count).Close('}');
                j.Close(']');
            });
            Safe(j, "zones", () =>
            {
                j.Key("zones").Open('[');
                foreach (Zone z in map.zoneManager.AllZones)
                {
                    j.Open('{').KV("label", z.label).KV("kind", z.GetType().Name).KV("cells", z.Cells.Count);
                    if (z is Zone_Growing g) j.KV("plant", g.GetPlantDefToGrow()?.defName);
                    j.Close('}');
                }
                j.Close(']');
            });
            Safe(j, "designations", () =>
            {
                j.Key("designations").Open('{');
                foreach (var g in map.designationManager.AllDesignations.GroupBy(d => d.def.defName)) j.KV(g.Key, g.Count());
                j.Close('}');
            });
            Safe(j, "alerts", () =>
            {
                j.Key("alerts").Open('[');
                foreach (string a in ActiveAlerts()) j.Val(a);
                j.Close(']');
            });
            Safe(j, "letters", () =>
            {
                j.Key("letters").Open('[');
                foreach (Letter l in Find.LetterStack.LettersListForReading)
                {
                    string text = (l as ChoiceLetter)?.Text.ToString() ?? "";
                    j.Open('{').KV("id", l.ID).KV("def", l.def?.defName).KV("label", l.Label.ToString())
                     .KV("text", text.Length > 400 ? text.Substring(0, 400) : text).Close('}');
                }
                j.Close(']');
            });
            Safe(j, "factions", () =>
            {
                j.Key("factions").Open('[');
                foreach (Faction f in Find.FactionManager.AllFactionsVisible.Where(f => !f.IsPlayer))
                    j.Open('{').KV("name", f.Name).KV("def", f.def.defName).KV("goodwill", f.PlayerGoodwill).KV("hostile", f.HostileTo(Faction.OfPlayer)).Close('}');
                j.Close(']');
            });
            j.Close('}');
            return j.ToString();
        }

        private static ResearchProjectDef CurrentResearch()
        {
            // the current project's accessor changed between versions; read whichever exists
            ResearchManager rm = Find.ResearchManager;
            MethodInfo m = typeof(ResearchManager).GetMethod("GetProject", BindingFlags.Public | BindingFlags.Instance, null, Type.EmptyTypes, null);
            if (m != null) return m.Invoke(rm, null) as ResearchProjectDef;
            FieldInfo f = typeof(ResearchManager).GetField("currentProj", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            return f?.GetValue(rm) as ResearchProjectDef;
        }

        private static IEnumerable<string> ActiveAlerts()
        {
            // the alerts readout keeps its active list private; every mod's alert lives in the same list
            object readout = (Find.UIRoot as UIRoot_Play)?.alerts;
            if (readout == null) yield break;
            FieldInfo f = readout.GetType().GetField("activeAlerts", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance);
            if (!(f?.GetValue(readout) is System.Collections.IEnumerable list)) yield break;
            foreach (object o in list)
                if (o is Alert a) yield return a.GetType().Name + ": " + a.GetLabel();
        }
    }
}
