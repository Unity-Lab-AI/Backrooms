using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// Inventory section D (2026-10-13): pawn setup, trade, caravans, pods, quests, pens, power nets, storage, ideology
    /// roles/rituals, visitors (Hospitality), the Empire's stance, toxic
    /// buildup, the disease race and battery days. Normal cadence, each block guarded on its own; a key that cannot be read
    /// is left out, never a fake 0.
    /// Mod register checked before building (docs/research/mod-register-integration-fields-2026-09-29.csv): Simple
    /// sidearms (sidearms live in the inventory -- the setup check reads both), Wall Orbital Trade Beacon (beacons are
    /// counted by class, not def name), No Quests Without Comms (comms_consoles is read next to the quest counts),
    /// Hospitality (Continued) / Invite to Stay / Storefront and Real Faction Guest (guests read through vanilla guest
    /// state; guest beds by class name), the storage family (Adaptive/LWM/Warehouse/RimFridge: storage counted by
    /// Building_Storage, so modded shelves count), More filters for animals' pen (pens are the vanilla pen marker).
    /// All read-only: nothing here patches or changes another mod.
    /// </summary>
    public static class SensorsWorld
    {
        public static void Read(Dictionary<string, object> st, Map home, List<Pawn> crew)
        {
            if (home == null) return;
            Guard(() => Setup(st, crew));
            Guard(() => Trade(st, home));
            Guard(() => Caravans(st));
            Guard(() => Pods(st, home));
            Guard(() => Quests(st));
            Guard(() => Pens(st, home));
            Guard(() => PowerNets(st, home));
            Guard(() => Storage(st, home));
            Guard(() => Ideology(st, home));
            Guard(() => Visitors(st, home));
            Guard(() => Factions(st));
            Guard(() => Toxic(st, crew));
            Guard(() => Disease(st, crew));
            Guard(() => Batteries(st, home));
            Guard(() => Kitchen(st, home));
            Guard(() => Freezer(st, home));
            Guard(() => Towers(st, home));
            Guard(() => StoneBlocks(st, home));
            Guard(() => ResearchUpgrades(st, home));
            Guard(() => Prisoners(st, home));
            Guard(() => Traders(st, home));
            Guard(() => GatePosture(st, home));
        }

        private static void Guard(Action a)
        {
            try { a(); }
            catch (Exception) { }
        }

        private static int Count(Map home, string defName)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            return d == null ? -1 : home.listerThings.ThingsOfDef(d).Count;
        }

        /// <summary>
        /// pawns_unconfigured: colonists whose setup has never been complete. A pawn is set up when, at one scan, it is
        /// armed with a primary and a melee sidearm (violent pawns), hostility response Attack (violent pawns), self-tend
        /// on (pawns who can doctor), works at least one job, and has the no-drug policy (owner: "drugs are for
        /// hospitality guests"). Once set up, the pawn is remembered in the save (RimPLCGameComponent.ConfiguredPawns) so
        /// a dropped weapon later is the unarmed rung's job, not a "never configured" warning.
        /// </summary>
        private static void Setup(Dictionary<string, object> st, List<Pawn> crew)
        {
            RimPLCGameComponent comp = RimPLCGameComponent.Get();
            if (comp == null) return;
            int open = 0;
            foreach (Pawn p in crew)
            {
                string id = p.GetUniqueLoadID();
                if (comp.ConfiguredPawns.Contains(id)) continue;
                if (IsSetUp(p)) comp.ConfiguredPawns.Add(id);
                else open++;
            }
            st["pawns_unconfigured"] = (double)open;
        }

        public static bool IsSetUp(Pawn p)
        {
            bool violent = !p.WorkTagIsDisabled(WorkTags.Violent);
            if (violent)
            {
                if (p.equipment?.Primary == null) return false;
                bool melee = (p.equipment.AllEquipmentListForReading.Any(e => e.def.IsMeleeWeapon)) ||
                             (p.inventory?.innerContainer.Any(t => t.def.IsMeleeWeapon) ?? false);
                if (!melee) return false;
                if (p.playerSettings == null || p.playerSettings.hostilityResponse != HostilityResponseMode.Attack) return false;
            }
            if (!p.WorkTypeIsDisabled(WorkTypeDefOf.Doctor) && (p.playerSettings == null || !p.playerSettings.selfTend)) return false;
            if (p.workSettings == null || !p.workSettings.EverWork) return false;
            if (!DefDatabase<WorkTypeDef>.AllDefsListForReading.Any(w => w.visible && p.workSettings.GetPriority(w) > 0)) return false;
            // the policy label is what the player sees ("No drugs" in Core); a renamed policy needs the word "no"
            string drug = p.drugs?.CurrentPolicy?.label ?? "";
            if (drug.IndexOf("no", StringComparison.OrdinalIgnoreCase) < 0) return false;
            return true;
        }

        private static void Trade(Dictionary<string, object> st, Map home)
        {
            st["trade_ships_in_orbit"] = (double)home.passingShipManager.passingShips.Count;
            st["trade_beacons"] = (double)home.listerBuildings.allBuildingsColonist.Count(b => b is Building_OrbitalTradeBeacon);
            st["comms_consoles"] = (double)home.listerBuildings.allBuildingsColonist.Count(b => b is Building_CommsConsole);
            st["silver"] = (double)home.resourceCounter.Silver;
        }

        private static void Caravans(Dictionary<string, object> st)
        {
            List<Caravan> mine = Find.WorldObjects.Caravans.Where(c => c.IsPlayerControlled).ToList();
            st["caravans_out"] = (double)mine.Count;
            st["caravan_pawns_out"] = (double)mine.Sum(c => c.PawnsListForReading.Count(p => p.IsColonist));
        }

        private static void Pods(Dictionary<string, object> st, Map home)
        {
            int pods = Count(home, "TransportPod"), launchers = Count(home, "PodLauncher");
            if (pods >= 0) st["transport_pods"] = (double)pods;
            if (launchers >= 0) st["pod_launchers"] = (double)launchers;
        }

        private static void Quests(Dictionary<string, object> st)
        {
            List<Quest> qs = Find.QuestManager.QuestsListForReading;
            st["quests_active"] = (double)qs.Count(q => q.State == QuestState.Ongoing && !q.hidden);
            st["quests_offered"] = (double)qs.Count(q => q.State == QuestState.NotYetAccepted && !q.hidden);
        }

        private static void Pens(Dictionary<string, object> st, Map home)
        {
            int pens = 0, outside = 0;
            foreach (Building b in home.listerBuildings.allBuildingsColonist)
                if (b.TryGetComp<CompAnimalPenMarker>() != null) pens++;
            foreach (Pawn a in home.mapPawns.SpawnedColonyAnimals)
                if (AnimalPenUtility.NeedsToBeManagedByRope(a) && AnimalPenUtility.GetCurrentPenOf(a, false) == null) outside++;
            st["pen_markers"] = (double)pens;
            st["pen_animals_unpenned"] = (double)outside;
        }

        /// <summary>Conduit routing: power nets that have consumers but no live source (a cut or unrouted conduit).</summary>
        private static void PowerNets(Dictionary<string, object> st, Map home)
        {
            int nets = 0, dead = 0;
            foreach (PowerNet n in home.powerNetManager.AllNetsListForReading)
            {
                if (n.powerComps.Count == 0) continue;
                nets++;
                if (!n.HasActivePowerSource) dead++;
            }
            st["power_nets"] = (double)nets;
            st["power_nets_dead"] = (double)dead;
        }

        /// <summary>Stockpiles and storage buildings; how many have the same filter as the first (storage copy).</summary>
        private static void Storage(Dictionary<string, object> st, Map home)
        {
            List<Zone_Stockpile> piles = home.zoneManager.AllZones.OfType<Zone_Stockpile>().ToList();
            st["stockpiles"] = (double)piles.Count;
            st["storage_buildings"] = (double)home.listerBuildings.allBuildingsColonist.Count(b => b is Building_Storage);
            st["stockpiles_default_priority"] = (double)piles.Count(z => z.settings.Priority == StoragePriority.Normal);
        }

        private static void Ideology(Dictionary<string, object> st, Map home)
        {
            if (!ModsConfig.IdeologyActive) return;
            Ideo ideo = Faction.OfPlayer?.ideos?.PrimaryIdeo;
            if (ideo == null) return;
            List<Precept_Role> roles = ideo.RolesListForReading;
            st["ideo_roles"] = (double)roles.Count;
            st["ideo_roles_unassigned"] = (double)roles.Count(r => r.ChosenPawnSingle() == null);
            st["ideo_leader_assigned"] = roles.Any(r => r.def.leaderRole && r.ChosenPawnSingle() != null);
            st["ritual_spots"] = (double)Math.Max(0, Count(home, "RitualSpot"));
            st["ideo_rituals"] = (double)ideo.PreceptsListForReading.OfType<Precept_Ritual>().Count();
        }

        /// <summary>toxic_buildup_max: the worst colonist's ToxicBuildup severity, 0..1 (HediffDefOf.ToxicBuildup, verified
        /// decomp). 0 when nobody has any.</summary>
        private static void Toxic(Dictionary<string, object> st, List<Pawn> crew)
        {
            if (crew.Count == 0 || HediffDefOf.ToxicBuildup == null) return;
            float worst = 0f;
            foreach (Pawn p in crew)
            {
                Hediff h = p.health?.hediffSet?.GetFirstHediffOfDef(HediffDefOf.ToxicBuildup);
                if (h != null) worst = Math.Max(worst, h.Severity);
            }
            st["toxic_buildup_max"] = Math.Round(worst, 3);
        }

        /// <summary>worst_disease_margin: immunity minus severity of the worst visible immunizable disease a colonist is still
        /// racing (HediffComp_Immunizable.Immunity / FullyImmune, verified decomp). Below 0 the disease is ahead; 1 when no
        /// colonist is racing one. Toxic buildup is left out (its own key).</summary>
        private static void Disease(Dictionary<string, object> st, List<Pawn> crew)
        {
            if (crew.Count == 0) return;
            double margin = 1.0;
            foreach (Pawn p in crew)
            {
                if (p.health?.hediffSet == null) continue;
                foreach (Hediff h in p.health.hediffSet.hediffs)
                {
                    if (!h.Visible || h.def == HediffDefOf.ToxicBuildup || !(h is HediffWithComps hc)) continue;
                    HediffComp_Immunizable im = hc.TryGetComp<HediffComp_Immunizable>();
                    if (im == null || im.FullyImmune) continue;
                    margin = Math.Min(margin, im.Immunity - h.Severity);
                }
            }
            st["worst_disease_margin"] = Math.Round(margin, 3);
        }

        /// <summary>battery_days_stored: stored energy of the home map's batteries (CompPowerBattery.StoredEnergy, Wd,
        /// verified decomp) divided by what the powered consumers draw now (W), so days at this load. Left out when
        /// nothing draws power.</summary>
        private static void Batteries(Dictionary<string, object> st, Map home)
        {
            double stored = 0, draw = 0;
            foreach (Building b in home.listerBuildings.allBuildingsColonist)
            {
                CompPowerBattery bat = b.TryGetComp<CompPowerBattery>();
                if (bat != null) stored += bat.StoredEnergy;
                CompPowerTrader pt = b.TryGetComp<CompPowerTrader>();
                if (pt != null && pt.PowerOn && pt.PowerOutput < 0) draw += -pt.PowerOutput;
            }
            if (draw > 0) st["battery_days_stored"] = Math.Round(stored / draw, 2);
        }

        /// <summary>kitchen_tables_no_bill: built tables the Rimrooms kitchen command would bill, by its own test -- a table
        /// that can cook CookMealSimple with no meal bill, or one that can do ButcherCorpseFlesh without that bill.
        /// butcher_tables: built tables that butcher flesh (and cannot cook a simple meal), same test.</summary>
        private static void Kitchen(Dictionary<string, object> st, Map home)
        {
            RecipeDef meal = DefDatabase<RecipeDef>.GetNamedSilentFail("CookMealSimple");
            RecipeDef butcher = DefDatabase<RecipeDef>.GetNamedSilentFail("ButcherCorpseFlesh");
            if (meal == null && butcher == null) return;
            int open = 0, butchers = 0;
            foreach (Building_WorkTable t in home.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>())
            {
                if (meal != null && t.def.AllRecipes.Contains(meal))
                {
                    if (!t.BillStack.Bills.Any(b => b.recipe?.ProducedThingDef != null && b.recipe.ProducedThingDef.IsNutritionGivingIngestible)) open++;
                }
                else if (butcher != null && t.def.AllRecipes.Contains(butcher))
                {
                    butchers++;
                    if (!t.BillStack.Bills.Any(b => b.recipe == butcher)) open++;
                }
            }
            st["kitchen_tables_no_bill"] = (double)open;
            st["butcher_tables"] = (double)butchers;
        }

        /// <summary>The freezer, by the Rimrooms freezer command's own test: freezer_coolers = built coolers whose cold side
        /// (the cell north of the cooler, rotated) is an indoor room; freezer_coolers_warm = those set above 0 C (the command
        /// sets -5 C once built); cooler_planned = cooler blueprints and frames.</summary>
        private static void Freezer(Dictionary<string, object> st, Map home)
        {
            ThingDef cooler = DefDatabase<ThingDef>.GetNamedSilentFail("Cooler");
            if (cooler == null) return;
            int cold = 0, warm = 0;
            foreach (Building b in home.listerBuildings.AllBuildingsColonistOfDef(cooler))
            {
                Room r = (b.Position + IntVec3.North.RotatedBy(b.Rotation)).GetRoom(home);
                if (r == null || r.PsychologicallyOutdoors || r.UsesOutdoorTemperature) continue;
                cold++;
                CompTempControl tc = b.TryGetComp<CompTempControl>();
                if (tc != null && tc.TargetTemperature > 0f) warm++;
            }
            st["freezer_coolers"] = (double)cold;
            st["freezer_coolers_warm"] = (double)warm;
            int planned = cooler.blueprintDef == null ? 0 : home.listerThings.ThingsOfDef(cooler.blueprintDef).Count;
            planned += home.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame).Count(t => t.def.entityDefToBuild == cooler);
            st["cooler_planned"] = (double)planned;
        }

        /// <summary>The perimeter corners the Rimrooms tower command takes, read from the colony's own layout: the corners of
        /// the Home area's bounding box (corner_&lt;ne|nw|se|sw&gt;_x / _z). tower_&lt;corner&gt; is true when an embrasure
        /// stands, is framed or is planned within 8 cells of that corner (a tower, or perimeter embrasures already holding
        /// it). Left out with no Home area.</summary>
        private static void Towers(Dictionary<string, object> st, Map home)
        {
            Area ha = home.areaManager.Home;
            if (ha == null || ha.TrueCount == 0) return;
            int minX = int.MaxValue, minZ = int.MaxValue, maxX = int.MinValue, maxZ = int.MinValue;
            foreach (IntVec3 c in ha.ActiveCells)
            {
                minX = Math.Min(minX, c.x); maxX = Math.Max(maxX, c.x);
                minZ = Math.Min(minZ, c.z); maxZ = Math.Max(maxZ, c.z);
            }
            // planned: embrasure blueprints / frames near the corner (a tower the tower command has laid out)
            var plannedEmb = new List<IntVec3>();
            foreach (Thing t in home.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint).Concat(home.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame)))
                if (t.def.entityDefToBuild != null && t.def.entityDefToBuild.defName.Contains("Embrasure")) plannedEmb.Add(t.Position);
            // literal keys, one corner per block, so the checker (tools/rimplc-check.py) can see every key written
            IntVec3 ne = new IntVec3(maxX, 0, maxZ), nw = new IntVec3(minX, 0, maxZ), se = new IntVec3(maxX, 0, minZ), sw = new IntVec3(minX, 0, minZ);
            Room rne = TowerRoom(home, ne), rnw = TowerRoom(home, nw), rse = TowerRoom(home, se), rsw = TowerRoom(home, sw);
            st["corner_ne_x"] = (double)ne.x; st["corner_ne_z"] = (double)ne.z; st["tower_ne_built"] = rne != null; st["tower_ne"] = rne != null || plannedEmb.Any(e => e.InHorDistOf(ne, 8f));
            st["corner_nw_x"] = (double)nw.x; st["corner_nw_z"] = (double)nw.z; st["tower_nw_built"] = rnw != null; st["tower_nw"] = rnw != null || plannedEmb.Any(e => e.InHorDistOf(nw, 8f));
            st["corner_se_x"] = (double)se.x; st["corner_se_z"] = (double)se.z; st["tower_se_built"] = rse != null; st["tower_se"] = rse != null || plannedEmb.Any(e => e.InHorDistOf(se, 8f));
            st["corner_sw_x"] = (double)sw.x; st["corner_sw_z"] = (double)sw.z; st["tower_sw_built"] = rsw != null; st["tower_sw"] = rsw != null || plannedEmb.Any(e => e.InHorDistOf(sw, 8f));
            if (rne != null) { IntVec3 c = rne.Cells.First(); st["tower_ne_cell_x"] = (double)c.x; st["tower_ne_cell_z"] = (double)c.z; st["tower_ne_cooler"] = (double)CoolerState(home, rne); }
            if (rnw != null) { IntVec3 c = rnw.Cells.First(); st["tower_nw_cell_x"] = (double)c.x; st["tower_nw_cell_z"] = (double)c.z; st["tower_nw_cooler"] = (double)CoolerState(home, rnw); }
            if (rse != null) { IntVec3 c = rse.Cells.First(); st["tower_se_cell_x"] = (double)c.x; st["tower_se_cell_z"] = (double)c.z; st["tower_se_cooler"] = (double)CoolerState(home, rse); }
            if (rsw != null) { IntVec3 c = rsw.Cells.First(); st["tower_sw_cell_x"] = (double)c.x; st["tower_sw_cell_z"] = (double)c.z; st["tower_sw_cooler"] = (double)CoolerState(home, rsw); }
        }

        /// <summary>The tower the Rimrooms tower command builds, near a corner: a proper, fully roofed indoor room of 4-36 cells
        /// within 8 cells of the corner with at least one built embrasure in its walls. Plain wall embrasures with no such
        /// room do not count.</summary>
        private static Room TowerRoom(Map home, IntVec3 corner)
        {
            var seen = new HashSet<Room>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(corner, 8f, true))
            {
                if (!c.InBounds(home)) continue;
                Room r = c.GetRoom(home);
                if (r == null || !seen.Add(r)) continue;
                if (r.PsychologicallyOutdoors || !r.ProperRoom || r.OpenRoofCount > 0 || r.CellCount < 4 || r.CellCount > 36) continue;
                if (WallThings(home, r).Any(b => b.def.defName.Contains("Embrasure"))) return r;
            }
            return null;
        }

        private static IEnumerable<Building> WallThings(Map home, Room r)
        {
            var done = new HashSet<Building>();
            foreach (IntVec3 c in r.Cells)
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 n = c + d;
                    Building b = n.InBounds(home) ? n.GetEdifice(home) : null;
                    if (b != null && b.Faction == Faction.OfPlayer && done.Add(b)) yield return b;
                }
        }

        /// <summary>A tower room's cooler: 0 none (built or planned) in its walls, 1 planned, 2 built and powered, 3 built with no
        /// power.</summary>
        private static double CoolerState(Map home, Room r)
        {
            foreach (Building b in WallThings(home, r))
            {
                if (b.def.defName != "Cooler") continue;
                CompPowerTrader pt = b.TryGetComp<CompPowerTrader>();
                return pt == null || pt.PowerOn ? 2 : 3;
            }
            foreach (IntVec3 c in r.Cells)
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 n = c + d;
                    if (n.InBounds(home) && n.GetThingList(home).Any(t => (t.def.IsBlueprint || t.def.IsFrame) && t.def.entityDefToBuild?.defName == "Cooler")) return 1;
                }
            return 0;
        }

        /// <summary>stone_blocks: stone blocks of every kind in storage (ResourceCounter, things in the StoneBlocks category).</summary>
        private static void StoneBlocks(Dictionary<string, object> st, Map home)
        {
            int n = 0;
            foreach (KeyValuePair<ThingDef, int> kv in home.resourceCounter.AllCountedAmounts)
                if (kv.Key.thingCategories != null && kv.Key.thingCategories.Contains(ThingCategoryDefOf.StoneBlocks)) n += kv.Value;
            st["stone_blocks"] = (double)n;
        }

        // the Rimrooms research_next command's "build it the moment it is researched" list (SetupTools10.Upgrades)
        private static readonly string[] Upgrades = { "HiTechResearchBench", "MultiAnalyzer", "OrbitalTradeBeacon", "CommsConsole", "DrugLab" };

        /// <summary>research_upgrades_unbuilt / research_upgrades_missing: the upgrades research_next names -- researched
        /// and neither built nor planned (blueprint or frame) on the home map, by that command's own test.</summary>
        private static void ResearchUpgrades(Dictionary<string, object> st, Map home)
        {
            var missing = new List<object>();
            foreach (string name in Upgrades)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def == null || !def.IsResearchFinished) continue;
                bool have = home.listerBuildings.allBuildingsColonist.Any(b => b.def == def) ||
                            home.listerThings.AllThings.Any(t => (t.def.IsBlueprint || t.def.IsFrame) && t.def.entityDefToBuild == def);
                if (!have) missing.Add(name);
            }
            st["research_upgrades_unbuilt"] = (double)missing.Count;
            st["research_upgrades_missing"] = missing.ToList();
        }

        /// <summary>prisoners_new / prisoners_new_names: prisoners of the colony on the home map still on the default
        /// interaction (PrisonerInteractionModeDefOf.MaintainOnly, Pawn_GuestTracker's initial value, verified decomp) that
        /// RimPLC has never seen with a stance of their own. A prisoner whose mode is set to anything else is remembered in
        /// the save (RimPLCGameComponent.PrisonersSeen), so a stance the player or the playbook sets later -- maintain
        /// included -- is never counted again.</summary>
        private static void Prisoners(Dictionary<string, object> st, Map home)
        {
            RimPLCGameComponent comp = RimPLCGameComponent.Get();
            if (comp == null || PrisonerInteractionModeDefOf.MaintainOnly == null) return;
            var names = new List<object>();
            foreach (Pawn p in home.mapPawns.PrisonersOfColonySpawned)
            {
                if (p.guest == null) continue;
                string id = p.GetUniqueLoadID();
                if (comp.PrisonersSeen.Contains(id)) continue;
                if (p.guest.ExclusiveInteractionMode != PrisonerInteractionModeDefOf.MaintainOnly) { comp.PrisonersSeen.Add(id); continue; }
                names.Add(p.LabelShort);
            }
            st["prisoners_new"] = (double)names.Count;
            st["prisoners_new_names"] = names.ToList();
        }

        /// <summary>trader_caravans_on_map: non-hostile pawns on the home map carrying a trader kind (Pawn_TraderTracker.traderKind,
        /// verified decomp) -- a trader caravan the Rimrooms trade command can deal with.</summary>
        private static void Traders(Dictionary<string, object> st, Map home)
        {
            int n = 0;
            foreach (Pawn p in home.mapPawns.AllPawnsSpawned)
                if (p.trader?.traderKind != null && !p.HostileTo(Faction.OfPlayer)) n++;
            st["trader_caravans_on_map"] = (double)n;
        }

        /// <summary>gate_watch_posture: the Rimrooms gate's watch posture (0 Mild, 1 Balanced, 2 Strict) read by reflection from
        /// the comp named CompRimroomsGate (field watchPosture), so RimPLC keeps no Rimrooms reference. Left out with no gate
        /// (or no Rimrooms).</summary>
        private static void GatePosture(Dictionary<string, object> st, Map home)
        {
            foreach (Thing t in home.listerThings.AllThings)
            {
                if (!(t is ThingWithComps tw) || tw.AllComps == null) continue;
                foreach (ThingComp c in tw.AllComps)
                {
                    if (c.GetType().Name != "CompRimroomsGate") continue;
                    System.Reflection.FieldInfo f = c.GetType().GetField("watchPosture", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                    if (f == null) return;
                    st["gate_watch_posture"] = (double)Convert.ToInt32(f.GetValue(c));
                    return;
                }
            }
        }

        /// <summary>empire_hostile: the Empire (Royalty) is hostile to the player. FactionManager.OfEmpire (verified, decomp
        /// FactionManager.cs); with no Empire faction in the world the key is left out.</summary>
        private static void Factions(Dictionary<string, object> st)
        {
            Faction empire = Find.FactionManager?.OfEmpire;
            if (empire != null) st["empire_hostile"] = empire.HostileTo(Faction.OfPlayer);
        }

        /// <summary>Visitors and Hospitality guests. Guest beds by class name: Hospitality's Building_GuestBed
        /// (Hospitality.Building_GuestBed, verified in Hospitality (Continued)'s 1.7 Hospitality.dll; matched by name, so no
        /// Hospitality reference is compiled in).</summary>
        private static void Visitors(Dictionary<string, object> st, Map home)
        {
            int visitors = 0, guests = 0;
            foreach (Pawn p in home.mapPawns.AllPawnsSpawned)
            {
                if (!p.RaceProps.Humanlike || p.Faction == null || p.Faction.IsPlayer || p.IsPrisoner || p.IsSlave) continue;
                if (p.HostileTo(Faction.OfPlayer)) continue;
                visitors++;
                if (p.guest != null && p.guest.HostFaction == Faction.OfPlayer) guests++;
            }
            st["visitors"] = (double)visitors;
            st["hospitality_guests"] = (double)guests;
            st["guest_beds"] = (double)home.listerBuildings.allBuildingsColonist.Count(b =>
                b.def.thingClass != null && b.def.thingClass.Name.IndexOf("GuestBed", StringComparison.Ordinal) >= 0);
        }
    }
}
