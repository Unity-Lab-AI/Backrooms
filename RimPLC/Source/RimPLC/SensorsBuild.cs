using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// Inputs the rebuilt ladder reads (2026-10-13 rebuild, inventory section C): crew setup, buildings, power, rooms,
    /// storage, camp terrain and the perimeter. Normal cadence. Each block is guarded on its own -- one unreadable value
    /// (a mod's odd def, a 1.7 API change) leaves that block's keys out and never the rest; a key that cannot be read is
    /// left out, never a fake 0, so a rung that needs it stays quiet.
    /// pawns_unconfigured and inventory section D are read by SensorsWorld (called at the end of Read).
    /// </summary>
    public static class SensorsBuild
    {
        public static void Read(Dictionary<string, object> st, Map home)
        {
            if (home == null) return;
            List<Pawn> crew = home.mapPawns.FreeColonistsSpawned.ToList();
            Guard(() => Crew(st, home, crew));
            Guard(() => Buildings(st, home));
            Guard(() => Power(st, home));
            Guard(() => Rooms(st, home));
            Guard(() => Storage(st, home, crew));
            Guard(() => Camp(st, home));
            Guard(() => Perimeter(st, home));
            Guard(() => Screen(st, home));
            SensorsWorld.Read(st, home, crew);   // section D + pawns_unconfigured
        }

        private static void Guard(Action a)
        {
            try { a(); }
            catch (Exception) { }
        }

        private static void Crew(Dictionary<string, object> st, Map home, List<Pawn> crew)
        {
            int armorless = 0, flee = 0, noSidearm = 0, unarmed = 0, sharing = 0, noBedroom = 0, kids = 0, lovers = 0, resOnly = 0;
            int bestPlants = 0;
            foreach (Pawn p in crew)
            {
                bool violent = !p.WorkTagIsDisabled(WorkTags.Violent);
                if (p.GetStatValue(StatDefOf.ArmorRating_Sharp) < 0.3f) armorless++;
                if (p.playerSettings != null && p.playerSettings.hostilityResponse != HostilityResponseMode.Attack) flee++;
                bool melee = (p.equipment?.AllEquipmentListForReading.Any(e => e.def.IsMeleeWeapon) ?? false) ||
                             (p.inventory?.innerContainer.Any(t => t.def.IsMeleeWeapon) ?? false);
                if (violent && !melee) noSidearm++;
                if (violent && p.equipment?.Primary == null) unarmed++;
                Building_Bed bed = p.ownership?.OwnedBed;
                Room own = p.ownership?.OwnedRoom;
                if (bed == null || own == null) noBedroom++;
                else if (own.Role == RoomRoleDefOf.Barracks) sharing++;
                if (p.DevelopmentalStage.Juvenile()) kids++;
                Pawn partner = LovePartnerRelationUtility.ExistingLovePartner(p);
                if (partner != null && !p.relations.DirectRelationExists(PawnRelationDefOf.Spouse, partner)) lovers++;
                if (p.skills != null) bestPlants = Math.Max(bestPlants, p.skills.GetSkill(SkillDefOf.Plants).Level);
                if (p.workSettings != null && p.workSettings.EverWork && p.workSettings.GetPriority(WorkTypeDefOf.Research) == 1 &&
                    DefDatabase<WorkTypeDef>.AllDefsListForReading.Where(w => w != WorkTypeDefOf.Research && w.visible && !p.WorkTypeIsDisabled(w))
                                                                  .All(w => p.workSettings.GetPriority(w) == 0)) resOnly++;
            }
            st["colonists_without_armor"] = (double)armorless;
            st["flee_hostility_count"] = (double)flee;
            st["pawns_flee"] = (double)flee;
            st["pawns_without_sidearm"] = (double)noSidearm;
            st["unarmed_colonists"] = (double)unarmed;
            st["pawns_sharing_bedroom"] = (double)sharing;
            st["colonists_without_bedroom"] = (double)noBedroom;
            st["children"] = (double)kids;
            st["lovers_unmarried"] = (double)(lovers / 2);        // each couple is seen from both sides
            if (crew.Count > 0) st["best_plants_skill"] = (double)bestPlants;
            st["researchers_only_research"] = (double)resOnly;
            st["prisoners"] = (double)home.mapPawns.PrisonersOfColonySpawnedCount;
        }

        private static void Buildings(Dictionary<string, object> st, Map home)
        {
            Count(st, home, "simple_benches", "SimpleResearchBench");
            Count(st, home, "hitech_benches", "HiTechResearchBench");
            Count(st, home, "multi_analyzers", "MultiAnalyzer");
            Count(st, home, "torch_lamps", "TorchLamp");
            ThingDef mono = DefDatabase<ThingDef>.GetNamedSilentFail("VoidMonolith");
            if (mono != null) st["monolith"] = home.listerThings.ThingsOfDef(mono).Count > 0;
            Guard(() => { if (ModsConfig.AnomalyActive && Find.Anomaly != null) st["monolith_level"] = (double)Find.Anomaly.Level; });
        }

        private static void Count(Dictionary<string, object> st, Map home, string key, string defName)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (d != null) st[key] = (double)home.listerBuildings.AllBuildingsColonistOfDef(d).Count();
        }

        private static void Power(Dictionary<string, object> st, Map home)
        {
            int unpoweredConsumers = 0, unpoweredBuildings = 0, unpoweredEmbr = 0;
            double produced = 0, consumed = 0;
            foreach (Building b in home.listerBuildings.allBuildingsColonist)
            {
                CompPowerTrader pt = b.TryGetComp<CompPowerTrader>();
                if (pt == null) continue;
                if (pt.PowerOutput > 0) { produced += pt.PowerOutput; continue; }
                consumed += -pt.PowerOutput;
                if (pt.PowerNet == null) unpoweredConsumers++;
                if (pt.PowerNet == null || !pt.PowerNet.HasActivePowerSource || !pt.PowerOn) unpoweredBuildings++;
                if (!pt.PowerOn && b.def.defName.Contains("Embrasure")) unpoweredEmbr++;
            }
            st["unpowered_consumers"] = (double)unpoweredConsumers;
            st["unpowered_buildings"] = (double)unpoweredBuildings;
            st["unpowered_embrasures"] = (double)unpoweredEmbr;
            if (consumed > 0) st["power_margin_pct"] = Math.Round(produced / consumed * 100.0, 0);
        }

        private static void Rooms(Dictionary<string, object> st, Map home)
        {
            int outOfTemp = 0, unfloored = 0, holes = 0;
            foreach (Room r in home.regionGrid.AllRooms)
            {
                if (r == null || r.PsychologicallyOutdoors || r.IsDoorway || !r.ProperRoom || r.Role == null || r.Role == RoomRoleDefOf.None) continue;
                float t = r.Temperature;
                if (t < 10f || t > 35f) outOfTemp++;
                if (r.OpenRoofCount > 0) holes++;
                foreach (IntVec3 c in r.Cells)
                {
                    TerrainDef td = c.GetTerrain(home);
                    if (td == null || !td.IsFloor || td.natural) unfloored++;   // natural rock counts until smoothed
                }
            }
            st["rooms_out_of_temp"] = (double)outOfTemp;
            st["unfloored_room_cells"] = (double)unfloored;
            st["room_wall_holes"] = (double)holes;
            bool lit = true, any = false;
            foreach (Building b in home.listerBuildings.allBuildingsColonist.Where(x => x is Building_ResearchBench))
            {
                any = true;
                if (home.glowGrid.GroundGlowAt(b.InteractionCell) < 0.5f) lit = false;
            }
            if (any) st["lab_lit"] = lit;
        }

        private static void Storage(Dictionary<string, object> st, Map home, List<Pawn> crew)
        {
            st["loose_items_unstored"] = (double)home.listerHaulables.ThingsPotentiallyNeedingHauling().Count;
            Area homeArea = home.areaManager.Home;
            IntVec3 centre = crew.Count == 0 ? IntVec3.Invalid
                : new IntVec3((int)crew.Average(p => p.Position.x), 0, (int)crew.Average(p => p.Position.z));
            st["forbidden_items"] = (double)home.listerThings.AllThings.Count(t =>
                t.def.EverHaulable && t.Spawned && t.IsForbidden(Faction.OfPlayer) && !home.fogGrid.IsFogged(t.Position) &&
                ((homeArea != null && homeArea[t.Position]) || (centre.IsValid && t.Position.InHorDistOf(centre, 30f))));
        }

        private static void Camp(Dictionary<string, object> st, Map home)
        {
            Area homeArea = home.areaManager.Home;
            if (homeArea != null)
            {
                st["camp_water_cells"] = (double)homeArea.ActiveCells.Count(c =>
                {
                    TerrainDef td = home.terrainGrid.TerrainAt(c);
                    return td != null && (td.IsWater || td.defName.Contains("Marsh") || td.defName.Contains("Mud"));
                });
            }
            st["blueprints_against_rock"] = (double)home.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint).Count(bp =>
                bp.def.entityDefToBuild is ThingDef ed && IsWall(ed) &&
                GenAdj.CardinalDirections.Any(d => { IntVec3 n = bp.Position + d; return n.InBounds(home) && n.GetEdifice(home)?.def.mineable == true; }));
        }

        private static bool IsWall(ThingDef d) =>
            d != null && (d == ThingDefOf.Wall || d.defName.IndexOf("Wall", StringComparison.OrdinalIgnoreCase) >= 0);

        /// <summary>Gaps in the defended ring: open walkable cells on the Home area's outer boundary (no wall, door or
        /// embrasure), and boundary gaps next to an embrasure.</summary>
        private static void Perimeter(Dictionary<string, object> st, Map home)
        {
            Area ha = home.areaManager.Home;
            if (ha == null || ha.TrueCount == 0) return;
            int gaps = 0, embGaps = 0;
            foreach (IntVec3 c in ha.ActiveCells)
            {
                bool edge = GenAdj.CardinalDirections.Any(d => { IntVec3 n = c + d; return !n.InBounds(home) || !ha[n]; });
                if (!edge) continue;
                Building ed = c.GetEdifice(home);
                bool closed = ed != null && (IsWall(ed.def) || ed is Building_Door || ed.def.defName.Contains("Embrasure"));
                if (closed || !c.Walkable(home)) continue;
                gaps++;
                if (GenAdj.AdjacentCells8WayRandomized().Any(o => { IntVec3 n = c + o; return n.InBounds(home) && n.GetEdifice(home)?.def.defName.Contains("Embrasure") == true; }))
                    embGaps++;
            }
            st["wall_gaps"] = (double)gaps;
            st["embrasure_gaps"] = (double)embGaps;
        }

        private static void Screen(Dictionary<string, object> st, Map home)
        {
            st["window_fullscreen"] = UnityEngine.Screen.fullScreen;
            CellRect view = Find.CameraDriver.CurrentViewRect;
            st["camera_on_colonist"] = Find.CurrentMap == home && home.mapPawns.FreeColonistsSpawned.Any(p => view.Contains(p.Position));
        }
    }
}
