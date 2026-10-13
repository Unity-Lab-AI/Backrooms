using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// The input scan: game state -> sensor keys, under the Ladder v2 names so the book's rungs and the brain's
    /// training data carry over. Read straight from the game, never through the bridge. A key that cannot be read
    /// is left OUT (never a fake 0), so a rung that needs it stays quiet.
    ///
    /// Every member used here was found by name and signature in the decompiled 1.6 Assembly-CSharp
    /// (.local/decomp/roofscan) or is already called by the Rimrooms mod, unless a comment says UNVERIFIED.
    ///
    /// Cadence classes (docs/RIMPLC_DESIGN.md 3.4): fast every scan, normal every 4th, slow every 16th.
    /// Semantics that differ from the bridge-fed gates.py are noted per key (for the parity read, design 9 step 4).
    /// </summary>
    public static class Sensors
    {
        public const int TicksPerDay = 60000;
        public const int TicksPerQuadrum = 900000;
        private const int ThreatLetterMaxAge = 2 * TicksPerDay;

        private static readonly string[] ThreatLetterDefs = { "ThreatBig", "ThreatSmall" };
        private static readonly string[] NeverHuntDefs = { "Boomalope", "Thrumbo", "Elephant", "Rhinoceros", "Megasloth" };
        private static readonly string[] MountDefs = { "Elephant", "Horse", "Dromedary", "Muffalo", "Thrumbo" };

        private static readonly Dictionary<string, string> Resources = new Dictionary<string, string>
        {
            { "Steel", "steel" }, { "ComponentIndustrial", "components" }, { "ComponentSpacer", "adv_components" },
            { "Plasteel", "plasteel" }, { "Uranium", "uranium" }, { "Gold", "gold" }, { "Silver", "silver" },
            { "Chemfuel", "chemfuel" }, { "Cloth", "cloth" },
        };

        private static readonly Dictionary<string, string> DesignationKeys = new Dictionary<string, string>
        {
            { "Hunt", "designations_hunt" }, { "Tame", "designations_tame" }, { "HarvestPlant", "designations_harvest" },
            { "Mine", "designations_mine" }, { "CutPlant", "designations_cut" },
        };

        // alert_<key> -> the Core alert class that raises it. Language independent, unlike the label match in
        // gates.ALERT_MATCH. Class names verified (decomp, RimWorld/Alert_*.cs).
        private static readonly Dictionary<string, string> AlertClasses = new Dictionary<string, string>
        {
            { "low_food", "Alert_LowFood" }, { "starv", "Alert_StarvationColonists" }, { "hypotherm", "Alert_Hypothermia" },
            { "heatstroke", "Alert_Heatstroke" }, { "low_medicine", "Alert_LowMedicine" }, { "warm_clothes", "Alert_NeedWarmClothes" },
            { "need_research", "Alert_NeedResearchProject" }, { "idle", "Alert_ColonistsIdle" },
            { "colonist_needs_rescue", "Alert_ColonistNeedsRescuing" }, { "needs_tend", "Alert_ColonistNeedsTend" },
            { "life_threat", "Alert_LifeThreateningHediff" },
        };

        private static FieldInfo activeAlertsField;

        /// <summary>The player's home map with the most free colonists on it; the current map when there is no home.</summary>
        public static Map HomeMap()
        {
            List<Map> maps = Find.Maps;
            if (maps == null || maps.Count == 0) return null;
            Map best = null;
            int bestCount = -1;
            foreach (Map m in maps)
            {
                if (!m.IsPlayerHome) continue;
                int n = m.mapPawns.FreeColonistsSpawnedCount;
                if (n > bestCount) { best = m; bestCount = n; }
            }

            return best ?? Find.CurrentMap;
        }

        // ------------------------------------------------------------------------------------------------ fast

        /// <summary>Clock, crew, health, hostiles, letters. Every scan.</summary>
        public static void ReadFast(Dictionary<string, object> st, Map home, HashSet<int> lettersSeen)
        {
            TickManager tm = Find.TickManager;
            int ticks = tm.TicksGame;
            st["paused"] = tm.Paused;
            // gates.py measured ticks moving by reading twice; here the cause is read directly
            st["ticks_moving"] = !tm.Paused;
            st["day"] = Math.Round(ticks / (double)TicksPerDay, 2);
            // the clock the ton / tof timers count in (gates.py has no tick read and uses day * 60000)
            st["ticks"] = (double)ticks;
            st["quadrum_index"] = (double)(ticks / TicksPerQuadrum % 4);
            st["map_count"] = (double)Find.Maps.Count;
            WindowStack ws = Find.WindowStack;
            if (ws != null) st["dialog_open"] = ws.NonImmediateDialogWindowOpen;
            // UNVERIFIED in the decomp (UnityEngine, not Assembly-CSharp): Application.isFocused
            st["game_foreground"] = Application.isFocused;
            st["home_on_screen"] = home != null && Find.CurrentMap == home;
            // the HUD is hidden while screenshot mode (F11) is on: Find.ScreenshotModeHandler (verified, decomp Find.cs / UIRoot.cs)
            try
            {
                ScreenshotModeHandler shot = Find.ScreenshotModeHandler;
                if (shot != null) st["hud_visible"] = !shot.Active;
            }
            catch (Exception) { }

            List<Pawn> crew = PawnsFinder.AllMaps_FreeColonistsSpawned;
            int downed = 0, drafted = 0, able = 0, armed = 0, bleeding = 0, tend = 0, sick = 0;
            bool mental = false;
            double lowestHealth = 1.0;
            var maps = new HashSet<Map>();
            foreach (Pawn p in crew)
            {
                if (p.Map != null) maps.Add(p.Map);
                if (p.Downed) downed++;
                if (p.Drafted) drafted++;
                if (p.InMentalState) mental = true;
                if (!p.Downed && !p.Dead && !p.InMentalState)
                {
                    able++;
                    if (!p.WorkTagIsDisabled(WorkTags.Violent) && p.equipment?.Primary != null) armed++;
                }

                Pawn_HealthTracker h = p.health;
                if (h == null) continue;
                if (h.summaryHealth != null) lowestHealth = Math.Min(lowestHealth, h.summaryHealth.SummaryHealthPercent);
                if (h.hediffSet != null)
                {
                    if (h.hediffSet.BleedRateTotal > 0f) bleeding++;
                    if (h.hediffSet.HasTendableHediff()) tend++;
                    if (h.hediffSet.AnyHediffMakesSickThought) sick++;
                }
            }

            st["colonists"] = (double)crew.Count;
            st["colony_exists"] = crew.Count > 0;
            st["downed_count"] = (double)downed;
            st["drafted_count"] = (double)drafted;
            st["mental_break"] = mental;
            st["away_maps"] = (double)Math.Max(0, maps.Count - 1);
            // same rule as gates.py (not downed, dead or in a mental state) ...
            st["able_shooters"] = (double)able;
            // ... and the one the bridge could not see: capable of violence and holding a weapon
            st["able_shooters_armed"] = (double)armed;
            if (crew.Count > 0)
            {
                // the owner's "float switch on health bars": the worst colonist's overall health, 0..1
                st["lowest_health_pct"] = Math.Round(lowestHealth, 3);
                st["bleeding_count"] = (double)bleeding;
                st["needs_tend_count"] = (double)tend;
                // direct game reads; gates.py had only the (UNVERIFIED) alert labels for these
                st["alert_bleeding"] = bleeding > 0;
                st["alert_needs_tend"] = tend > 0;
                st["alert_sickness"] = sick > 0;
            }

            if (home != null)
            {
                int hostile = 0, foreigners = 0;
                Faction player = Faction.OfPlayer;
                IReadOnlyList<Pawn> all = home.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < all.Count; i++)
                {
                    Pawn p = all[i];
                    if (p.Dead) continue;
                    if (p.RaceProps != null && p.RaceProps.Humanlike && p.Faction != player && !p.IsPrisonerOfColony) foreigners++;
                    if (!p.Downed && p.HostileTo(player) && GenHostility.IsActiveThreatToPlayer(p)) hostile++;
                }

                // the threat API replaces the bridge's "humanlike crowd while a threat letter vouches for it"
                st["hostile_pawns_listed"] = (double)hostile;
                st["hostiles_on_map"] = (double)hostile;
                st["hostile_threat"] = GenHostility.AnyHostileActiveThreatToPlayer(home);
                st["humanlikes_not_ours"] = (double)foreigners;
            }

            LetterStack stack = Find.LetterStack;
            if (stack != null)
            {
                List<Letter> letters = stack.LettersListForReading;
                var labels = new List<object>();
                var defs = new List<object>();
                int unseen = 0;
                bool threat = false, quest = false, empire = false;
                foreach (Letter l in letters)
                {
                    string label = l.Label.RawText ?? string.Empty;
                    // the body too, so letter_matches ("heat wave", "monolith") can read what the letter says;
                    // the quest/empire tests below still read the label alone
                    string body = string.Empty;
                    if (l is ChoiceLetter cl) { try { body = " " + (cl.Text.RawText ?? string.Empty); } catch (Exception) { } }
                    string def = l.def?.defName ?? string.Empty;
                    labels.Add(label + body);
                    defs.Add(def);
                    if (ThreatLetterDefs.Contains(def) && ticks - l.arrivalTick <= ThreatLetterMaxAge) threat = true;
                    if (lettersSeen != null && lettersSeen.Contains(l.ID)) continue;
                    unseen++;
                    if (label.ToLowerInvariant().Contains("quest") || def.Contains("Quest")) quest = true;
                    Faction f = l.relatedFaction;
                    if (f != null && ((f.Name ?? string.Empty).ToLowerInvariant().Contains("empire") || f.def?.defName == "Empire")) empire = true;
                }

                st["letters"] = (double)unseen;
                st["letter_labels"] = labels;
                st["letter_defs"] = defs;
                st["threat_letter"] = threat;
                st["quest_letter"] = quest;
                st["empire_letter"] = empire;
            }
        }

        // ------------------------------------------------------------------------------------------------ normal

        /// <summary>Stores, zones, buildings, designations, animals, weapons, alerts, temperature. Every 4th scan.</summary>
        public static void ReadNormal(Dictionary<string, object> st, Map home, double crew)
        {
            ReadAlerts(st);
            int colonyAnimals = 0, colonyMechs = 0;
            foreach (Map m in Find.Maps)
            {
                colonyAnimals += m.mapPawns.SpawnedColonyAnimals.Count;
                colonyMechs += m.mapPawns.SpawnedColonyMechs.Count;
            }

            st["colony_animals"] = (double)colonyAnimals;
            st["colony_mechs"] = (double)colonyMechs;
            if (home == null) return;

            st["outdoor_temp"] = Math.Round(home.mapTemperature.OutdoorTemp, 1);

            // stores: ResourceCounter counts what is in storage, not everything inside the camp rectangle the bridge
            // swept (a known parity difference, design 9 step 4)
            int meals = 0, raw = 0, wood = 0, med = 0;
            var res = Resources.Values.Distinct().ToDictionary(k => k, k => 0);
            ResourceCounter rc = home.resourceCounter;
            foreach (KeyValuePair<ThingDef, int> kv in rc.AllCountedAmounts)
            {
                string d = kv.Key.defName;
                int n = kv.Value;
                if (d.StartsWith("Meal")) meals += n;
                else if (d.StartsWith("Raw") || d.StartsWith("Meat_")) raw += n;   // meat is food (2026-10-13 audit)
                else if (d == "WoodLog") wood += n;
                else if (d.Contains("Medicine")) med += n;
                else if (Resources.TryGetValue(d, out string key)) res[key] += n;
                else if (d.Contains("Leather")) res["cloth"] += n;
            }

            st["meals"] = (double)meals;
            st["raw_food"] = (double)raw;
            st["wood"] = (double)wood;
            st["medicine"] = (double)med;
            foreach (var kv in res) st[kv.Key] = (double)kv.Value;
            // Core's own nutrition total (Alert_LowFood uses it) over 1.6 nutrition per colonist per day (gates.py)
            st["days_of_food"] = Math.Round(rc.TotalHumanEdibleNutrition / (1.6 * Math.Max(1.0, crew)), 2);

            // zones and areas
            int growing = 0, stockpile = 0, storeCells = 0, roofed = 0;
            bool foodStore = false, mainStore = false;
            foreach (Zone z in home.zoneManager.AllZones)
            {
                string label = (z.label ?? string.Empty).ToLowerInvariant();
                if (z is Zone_Growing) growing += z.CellCount;
                if (z is Zone_Stockpile) stockpile += z.CellCount;
                bool food = label.Contains("food"), main = label.Contains("main");
                foodStore |= food;
                mainStore |= main;
                if (food || main)
                {
                    foreach (IntVec3 cell in z.cells)
                    {
                        storeCells++;
                        if (home.roofGrid.Roofed(cell)) roofed++;
                    }
                }
            }

            st["growing_cells"] = (double)growing;
            st["stockpile_cells"] = (double)stockpile;
            st["food_store"] = foodStore;
            st["main_store"] = mainStore;
            if (storeCells > 0)
            {
                st["store_roofed_fraction"] = roofed / (double)storeCells;
                st["unroofed_store_cells"] = (double)(storeCells - roofed);
            }

            if (home.areaManager.Home != null) st["home_cells"] = (double)home.areaManager.Home.TrueCount;

            // buildings: counted per building object (the bridge sweep had to merge touching cells). The def-name
            // tests are carried over from gates.BUILDING_KEYS; the substrings Embrasure, Grav, Throne, Ship_ and the
            // names PodLauncher, TransportPod, Battery, WindTurbine, GeothermalGenerator are UNVERIFIED against 1.6 defs.
            int stoves = 0, benches = 0, turrets = 0, beds = 0, launchers = 0, pods = 0, grav = 0, ship = 0, gens = 0, embr = 0, defence = 0;
            bool comms = false, throne = false, battery = false;
            foreach (Building b in home.listerBuildings.allBuildingsColonist)
            {
                if (b.def.IsFrame || b.def.IsBlueprint) continue;
                string d = b.def.defName;
                string cls = b.GetType().FullName;
                if (d == "FueledStove" || d == "ElectricStove") stoves++;
                if (cls == "RimWorld.Building_ResearchBench" || d == "SimpleResearchBench" || d == "HiTechResearchBench") benches++;
                if (d == "CommsConsole" || cls == "RimWorld.Building_CommsConsole") comms = true;
                if (d.Contains("Turret")) turrets++;
                if (b is Building_Bed) beds++;
                if (d.Contains("Throne")) throne = true;
                if (d == "PodLauncher") launchers++;
                if (d == "TransportPod") pods++;
                if (d.Contains("Grav")) grav++;
                if (d.StartsWith("Ship_")) ship++;
                if (d.Contains("Generator") || d == "WindTurbine" || d == "GeothermalGenerator") gens++;
                if (d == "Battery") battery = true;
                if (d.Contains("Embrasure")) embr++;
                if (d.Contains("Turret") || d == "Sandbags" || d == "Barricade" || d.Contains("Embrasure")) defence++;
            }

            st["stoves"] = (double)stoves;
            st["research_benches"] = (double)benches;
            st["comms_console"] = comms;
            st["turrets"] = (double)turrets;
            st["embrasures"] = (double)embr;
            st["beds"] = (double)beds;
            st["throne"] = throne;
            st["pod_launchers"] = (double)launchers;
            st["transport_pods"] = (double)pods;
            st["grav_parts"] = (double)grav;
            st["ship_parts"] = (double)ship;
            st["power_generators"] = (double)gens;
            st["has_power"] = gens > 0 || battery;
            st["defences_built"] = defence > 0;

            st["blueprints"] = (double)home.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint).Count;
            st["fire_cells"] = (double)home.listerThings.ThingsOfDef(ThingDefOf.Fire).Count;
            st["corpses"] = (double)home.listerThings.ThingsInGroup(ThingRequestGroup.Corpse).Count;
            st["berry_bushes"] = (double)(CountDef(home, "Plant_Berry") + CountDef(home, "Plant_Strawberry_Wild"));
            st["healroot_plants"] = (double)(CountDef(home, "Plant_Healroot") + CountDef(home, "Plant_HealrootWild"));

            var desig = DesignationKeys.Values.ToDictionary(k => k, k => 0);
            foreach (Designation dg in home.designationManager.AllDesignations)
            {
                if (dg.def != null && DesignationKeys.TryGetValue(dg.def.defName, out string key)) desig[key]++;
            }

            foreach (var kv in desig) st[kv.Key] = (double)kv.Value;

            // animals on the home map: wild (no faction) game, the dangerous ones, and mount candidates
            int wild = 0, danger = 0, mounts = 0;
            IReadOnlyList<Pawn> pawns = home.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.RaceProps == null || !p.RaceProps.Animal) continue;
                string d = p.def.defName;
                if (MountDefs.Contains(d)) mounts++;
                if (p.Faction != null) continue;
                if (NeverHuntDefs.Contains(d) || d.StartsWith("Bear_")) danger++;
                else wild++;
            }

            st["wild_game"] = (double)wild;
            st["danger_animals_near"] = (double)danger;
            st["mount_candidates"] = (double)mounts;

            // weapons lying on the map (the lister holds spawned things only, so worn/equipped weapons are not counted);
            // junk = awful or poor quality, read from the quality comp instead of the label
            int weapons = 0, junk = 0;
            foreach (Thing t in home.listerThings.ThingsInGroup(ThingRequestGroup.Weapon))
            {
                weapons++;
                if (t.TryGetQuality(out QualityCategory q) && q <= QualityCategory.Poor) junk++;
            }

            st["loose_weapons"] = (double)weapons;
            st["junk_weapons"] = (double)junk;

            // 2026-10-13 audit: three rungs read these and nothing measured them
            int billRows = 0;
            foreach (Building_WorkTable w in home.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>()) billRows += w.BillStack.Count;
            st["bill_rows"] = (double)billRows;
            List<Pawn> crewHere = home.mapPawns.FreeColonistsSpawned.ToList();
            if (crewHere.Count > 0)
            {
                // the plan: Firefighter..Cooking at 1, nothing a pawn can do left at 0
                string[] first = { "Firefighter", "Patient", "Doctor", "PatientBedRest", "BasicWorker", "Warden", "Handling", "Cooking" };
                st["grid_matches_plan"] = crewHere.All(p => p.workSettings == null || !p.workSettings.EverWork ||
                    DefDatabase<WorkTypeDef>.AllDefsListForReading.Where(w => w.visible && !p.WorkTypeIsDisabled(w))
                        .All(w => p.workSettings.GetPriority(w) != 0 && (!first.Contains(w.defName) || p.workSettings.GetPriority(w) == 1)));
            }
            List<Zone_Growing> fields = home.zoneManager.AllZones.OfType<Zone_Growing>().ToList();
            if (fields.Count > 0) st["fields_all_default_crop"] = fields.Count > 1 && fields.Select(z => z.GetPlantDefToGrow()).Distinct().Count() == 1;
            // map and world conditions, any mod's included: condition_<defname> true while active
            var conds = new List<object>();
            foreach (GameCondition gc in home.gameConditionManager.ActiveConditions.Concat(Find.World.gameConditionManager.ActiveConditions))
            {
                conds.Add(gc.def.defName);
                string ck = "condition_" + gc.def.defName.ToLowerInvariant();
                if (Validate.KeyRule.IsMatch(ck)) st[ck] = true;
            }
            st["game_conditions"] = conds;
            // wall_gaps is not measured: the perimeter rung stays disabled rather than fed a fixed 0
        }

        private static int CountDef(Map map, string defName)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            return def == null ? 0 : map.listerThings.ThingsOfDef(def).Count;
        }

        /// <summary>
        /// Active alerts. AlertsReadout.activeAlerts is private (verified, decomp); this reads it by reflection, read
        /// only, no Harmony (the design's named fallback, 4.4). Absent when there is no play UI.
        /// </summary>
        private static void ReadAlerts(Dictionary<string, object> st)
        {
            List<Alert> active;
            try
            {
                AlertsReadout readout = Find.Alerts;
                if (readout == null) return;
                if (activeAlertsField == null)
                {
                    activeAlertsField = typeof(AlertsReadout).GetField("activeAlerts", BindingFlags.Instance | BindingFlags.NonPublic);
                }

                active = activeAlertsField?.GetValue(readout) as List<Alert>;
            }
            catch (Exception)
            {
                return;
            }

            if (active == null) return;
            var labels = new List<object>();
            var classes = new HashSet<string>();
            foreach (Alert a in active)
            {
                classes.Add(a.GetType().Name);
                string label;
                try { label = a.GetLabel() ?? string.Empty; }
                catch (Exception) { label = string.Empty; }
                labels.Add(label);
            }

            st["alerts"] = labels;
            st["alert_classes"] = classes.Cast<object>().ToList();
            foreach (var kv in AlertClasses)
            {
                // merged with the direct health reads of the fast class by OR (see RimPLCGameComponent.Merge)
                st["alert_" + kv.Key] = classes.Contains(kv.Value);
            }

            // no Core class known for rotting food: the label match from gates.ALERT_MATCH (UNVERIFIED label)
            st["alert_food_rot"] = labels.Any(l => ((string)l).ToLowerInvariant().Contains("rot"));
        }

        // ------------------------------------------------------------------------------------------------ slow

        /// <summary>Wealth, research, damage, mood, caravans, titles. Every 16th scan.</summary>
        public static void ReadSlow(Dictionary<string, object> st, Map home)
        {
            ResearchManager rm = Find.ResearchManager;
            if (rm != null)
            {
                ResearchProjectDef cur = rm.GetProject();
                st["research_queue_empty"] = cur == null;
                ResearchProjectDef shipBasics = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("ShipBasics");
                if (shipBasics != null) st["ship_research_done"] = shipBasics.IsFinished;
                if (cur != null) st["research_current"] = cur.defName;
                foreach (ResearchProjectDef r in DefDatabase<ResearchProjectDef>.AllDefsListForReading)
                {
                    st["research_" + r.defName.ToLowerInvariant()] = r.IsFinished;
                }
            }

            List<Pawn> crew = PawnsFinder.AllMaps_FreeColonistsSpawned;
            double mood = double.MaxValue;
            int seniority = -1;
            foreach (Pawn p in crew)
            {
                Need_Mood m = p.needs?.mood;
                if (m != null) mood = Math.Min(mood, m.CurLevel);
                if (ModsConfig.RoyaltyActive && p.royalty?.MostSeniorTitle?.def != null)
                {
                    seniority = Math.Max(seniority, p.royalty.MostSeniorTitle.def.seniority);
                }
            }

            if (mood < double.MaxValue) st["lowest_mood"] = Math.Round(mood, 2);
            // raw RoyalTitleDef.seniority, not the 0-7 rank table of mark title_rank, so it gets its own key
            if (ModsConfig.RoyaltyActive && crew.Count > 0) st["title_seniority"] = (double)Math.Max(0, seniority);
            st["caravan_out"] = Find.WorldObjects.Caravans.Any(c => c.IsPlayerControlled);

            if (home == null) return;
            st["wealth"] = Math.Round(home.wealthWatcher.WealthTotal, 0);
            // explore_done (2026-10-13 critic: only the bridge reply ever set it): no fog frontier -- a fogged walkable
            // cell touching seen walkable ground -- within 30 cells of any colonist. Far mountain pockets do not count.
            bool frontier = false;
            foreach (Pawn p in home.mapPawns.FreeColonistsSpawned)
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(p.Position, 30f, true))
                {
                    if (!c.InBounds(home) || !home.fogGrid.IsFogged(c) || !c.Walkable(home)) continue;
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 n = c + d;
                        if (n.InBounds(home) && !home.fogGrid.IsFogged(n) && n.Walkable(home)) { frontier = true; break; }
                    }
                    if (frontier) break;
                }
                if (frontier) break;
            }
            if (home.mapPawns.FreeColonistsSpawnedCount > 0) st["explore_done"] = !frontier;
            int damaged = 0;
            foreach (Building b in home.listerBuildings.allBuildingsColonist)
            {
                if (b.def.useHitPoints && !b.def.IsFrame && b.HitPoints < b.MaxHitPoints) damaged++;
            }

            // per building (the bridge sweep could only compare cells of the same def)
            st["buildings_damaged"] = (double)damaged;
        }

        // ------------------------------------------------------------------------------------------------ on demand

        private static Dictionary<string, ThingDef> thingsByKey;

        /// <summary>The key a thing def is counted under: count_ + its defName in lower case (null when the name does not fit a key).</summary>
        public static string CountKey(ThingDef d)
        {
            string k = "count_" + d.defName.ToLowerInvariant();
            return Validate.KeyRule.IsMatch(k) ? k : null;
        }

        /// <summary>The key an alert class raises: alert_ + its class name in lower case without the Alert_ prefix.</summary>
        public static string AlertKey(string className)
        {
            string n = (className ?? string.Empty).ToLowerInvariant();
            return "alert_" + (n.StartsWith("alert_", StringComparison.Ordinal) ? n.Substring(6) : n);
        }

        public static ThingDef ThingByKey(string key)
        {
            if (thingsByKey == null)
            {
                var d = new Dictionary<string, ThingDef>();
                foreach (ThingDef t in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    string k = CountKey(t);
                    if (k != null && !d.ContainsKey(k)) d[k] = t;
                }

                thingsByKey = d;
            }

            return thingsByKey.TryGetValue(key, out ThingDef def) ? def : null;
        }

        /// <summary>
        /// Keys the rungs name by def (the editor's def pickers), read every scan for the keys asked for only:
        ///   count_&lt;thingdef&gt;  items on the home map: the stack total; buildings, plants and pawns: how many
        ///   alert_&lt;class&gt;     true while an alert of that class is active (alerts read on the normal cadence)
        /// A def that is not loaded (another mod, an inactive DLC) leaves its key unmeasured, never 0.
        /// </summary>
        public static void ReadDemand(Dictionary<string, object> st, Map home, ICollection<string> keys, Dictionary<string, object> normal)
        {
            if (keys == null || keys.Count == 0) return;
            HashSet<string> active = null;
            if (normal != null && normal.TryGetValue("alert_classes", out object ac) && ac is List<object> classes)
            {
                active = new HashSet<string>(classes.Select(c => AlertKey(c as string)));
            }

            foreach (string k in keys)
            {
                if (k.StartsWith("count_", StringComparison.Ordinal))
                {
                    ThingDef def = home == null ? null : ThingByKey(k);
                    if (def == null) continue;
                    List<Thing> things = home.listerThings.ThingsOfDef(def);
                    st[k] = def.category == ThingCategory.Item ? (double)things.Sum(t => t.stackCount) : (double)things.Count;
                }
                else if (k.StartsWith("alert_", StringComparison.Ordinal) && active != null && !normal.ContainsKey(k))
                {
                    st[k] = active.Contains(k);
                }
            }
        }

        // ------------------------------------------------------------------------------------------------ chain inputs

        /// <summary>
        /// gates._chain_inputs, run after the marks are in the state: who can fight, the odds, who is hurt. Unlike the
        /// bridge, RimPLC reads health directly (bleed rate, tendable injuries, downed), so hurt and bleeding are measured.
        /// </summary>
        public static void ChainInputs(Dictionary<string, object> st)
        {
            if (st.TryGetValue("hostiles_on_map", out object h) && Engine.IsNumber(h) && Engine.ToDouble(h) > 0 &&
                st.TryGetValue("able_shooters", out object a) && Engine.IsNumber(a))
            {
                st["fight_ratio"] = Math.Round(Engine.ToDouble(a) / Engine.ToDouble(h), 2);
            }

            bool alertsRead = st.ContainsKey("alert_bleeding") || st.ContainsKey("alerts");
            bool crewRead = st.ContainsKey("downed_count");
            if (alertsRead || st.ContainsKey("mark_pawn_bleeding"))
            {
                st["pawn_bleeding"] = Flag(st, "alert_bleeding") || Flag(st, "alert_life_threat") || Flag(st, "mark_pawn_bleeding");
            }

            if (crewRead || alertsRead || st.ContainsKey("mark_colonist_hurt"))
            {
                st["colonist_hurt"] = (st.TryGetValue("downed_count", out object d) && Engine.Truthy(d)) ||
                                      Flag(st, "alert_needs_tend") || Flag(st, "pawn_bleeding") || Flag(st, "mark_colonist_hurt");
            }
        }

        private static bool Flag(Dictionary<string, object> st, string key)
        {
            return st.TryGetValue(key, out object v) && Engine.Truthy(v);
        }
    }
}
