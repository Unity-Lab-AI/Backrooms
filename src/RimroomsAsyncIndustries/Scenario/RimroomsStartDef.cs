using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>RR-SCEN: original startup data; the campaign services own ongoing rules.</summary>
    public sealed class RimroomsStartDef : Def
    {
        public string scenarioId;
        public int scenarioVersion = 1;
        /// <summary>The name offered at setup. The player may replace it; every start can.</summary>
        public string defaultCompanyName;
        public int mapSize = 60;
        public MapGeneratorDef mapGenerator;
        public TerrainDef outdoorTerrain;
        public TerrainDef floorTerrain;
        public ThingDef wallStuff;
        public IntVec3 arrivalCell;
        public IntVec3 stockCell;
        public List<RimroomsRoomPlan> rooms = new List<RimroomsRoomPlan>();
        public List<IntVec3> doors = new List<IntVec3>();
        public List<RimroomsBuildingPlan> buildings = new List<RimroomsBuildingPlan>();
        public List<RimroomsConduitPlan> conduits = new List<RimroomsConduitPlan>();
        public List<RimroomsStockPlan> stock = new List<RimroomsStockPlan>();
        public List<RimroomsStaffRole> roles = new List<RimroomsStaffRole>();
        public long initialFundingUsd = 50000000L;
        public long dailyWageUsd = 5000L;
        public long dailyOverheadUsd = 25000L;
        public long surveyRewardUsd = 5000000L;
        public long surveyBonusUsd = 1000000L;

        /// <summary>
        /// Company projects this start begins with already finished.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"all starts have same tech tree just
        /// differnt starting researches finished based on scenerio"*.
        ///
        /// So a start declares **only this**. It never declares a tree, and it cannot: the
        /// branch is seeded from every `RimroomsProjectDef` the game has loaded, so the tree
        /// is identical for every start **by construction** rather than by three lists being
        /// kept in agreement by hand. Adding a project later reaches every scenario at once,
        /// and a scenario that forgot to list it cannot exist.
        ///
        /// A name here that matches no project is reported and skipped rather than failing a
        /// start: a player should not lose a new colony because a scenario named a project
        /// that a content update renamed.
        /// </summary>
        public List<string> completedProjects = new List<string>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrWhiteSpace(scenarioId) || scenarioVersion < 1) { yield return "Missing scenario identity/version."; }
            if (mapSize < 40 || mapSize > 300 || mapGenerator == null) { yield return "Invalid headquarters size/generator."; }
            if (outdoorTerrain == null || floorTerrain == null || wallStuff == null) { yield return "Missing headquarters terrain/material."; }
            if (roles == null || roles.Count != 5) { yield return "Async Industries requires five distinct starting roles."; }
            if (rooms == null || buildings == null || stock == null || doors == null || conduits == null)
            { yield return "Missing headquarters layout/stock list."; }
            if (roles != null)
            {
                var ids = new HashSet<string>();
                foreach (RimroomsStaffRole role in roles)
                {
                    if (role == null || string.IsNullOrWhiteSpace(role.id) || role.skills == null || role.workTypes == null)
                    { yield return "Invalid headquarters staff role."; continue; }
                    if (!ids.Add(role.id)) { yield return "Starting role IDs must be unique."; }
                    foreach (SkillRequirement skill in role.skills)
                    { if (skill == null || skill.skill == null || skill.minLevel < 0 || skill.minLevel > 20) { yield return "Invalid staff skill floor."; } }
                    foreach (WorkTypeDef work in role.workTypes)
                    { if (work == null) { yield return "Unresolved staff work type."; } }
                }
            }
            if (initialFundingUsd < 0 || dailyWageUsd < 0 || dailyOverheadUsd < 0 || surveyRewardUsd < 0 || surveyBonusUsd < 0)
            { yield return "Starting account amounts must not be negative."; }
        }
    }

    public sealed class RimroomsRoomPlan
    {
        public int x;
        public int z;
        public int width;
        public int height;
        public bool roofed = true;
        public bool floor = true;
        public CellRect Rect { get { return new CellRect(x, z, width, height); } }
    }

    public sealed class RimroomsBuildingPlan
    {
        public ThingDef thing;
        public ThingDef stuff;
        public IntVec3 cell;
        public int rotation;
        public bool medical;
        public float fuelFraction;
        public float batteryFraction;
    }

    public sealed class RimroomsConduitPlan
    {
        public IntVec3 start;
        public int length;
        public bool alongX = true;
    }

    public sealed class RimroomsStockPlan
    {
        public ThingDef thing;
        public ThingDef stuff;
        public int count;
    }

    public sealed class RimroomsStaffRole
    {
        public string id;
        public PawnKindDef kind;
        public List<SkillRequirement> skills = new List<SkillRequirement>();
        public List<WorkTypeDef> workTypes = new List<WorkTypeDef>();
        public bool mustFight;
    }
}
