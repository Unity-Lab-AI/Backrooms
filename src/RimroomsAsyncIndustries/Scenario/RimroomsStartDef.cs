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
        /// <summary>
        /// Whether this start begins already in communication with the parent corporation.
        ///
        /// True for Async Industries, which *"starts with this tech research and other basic gate
        /// techs it needs to operate and begin researching and gate operations at basic levels"*.
        /// False for the Store and Solo/Group starts, which have to reach contact - and until
        /// they do, there is no clean-up team and no rescue. That absence is what makes those two
        /// openings frightening.
        /// </summary>
        public bool beginsInCorporationContact;

        public string defaultCompanyName;
        public int mapSize = 60;
        // The `mapGenerator` field was retired at 0.12.46-dev. Owner direction: **"the map
        // generator is not our mod"**. Core's Base_Player generates the tile the player
        // picked and the facility is added onto it by two gen steps patched into that
        // generator; nothing here chooses a generator any more.
        public TerrainDef outdoorTerrain;
        public TerrainDef floorTerrain;
        public ThingDef wallStuff;
        public IntVec3 arrivalCell;
        public IntVec3 stockCell;
        public List<RimroomsRoomPlan> rooms = new List<RimroomsRoomPlan>();
        public List<IntVec3> doors = new List<IntVec3>();
        public List<RimroomsBuildingPlan> buildings = new List<RimroomsBuildingPlan>();
        public List<RimroomsConduitPlan> conduits = new List<RimroomsConduitPlan>();

        /// <summary>
        /// Wall runs replaced with something else once the rooms are built -- the viewing walls.
        ///
        /// **Owner direction, 2026-10-01, verbatim:** *"it now weays looks like a working
        /// "machine" that should be designed intelligently with like ballistic glass  walls for
        /// viewing the machine remotely and safely with security zones and shit and lab rooms and
        /// shit i mean wtf is this this is a 50million dollar facilty"*.
        ///
        /// **Named as STRINGS, not as `ThingDef`s, and that is the whole point of the field.** A
        /// `ThingDef` field is a hard cross-reference resolved at load: a def that is not present
        /// discards the **entire** containing def and everything that referenced it. That is
        /// exactly what cost the seventh launch -- one bad `Class` attribute took `Door` and
        /// `Autodoor` out of the game and produced **587 red lines**, and the game never left the
        /// main menu. Glass walls come from an Optional mod, so they are resolved at runtime with
        /// `GetNamedSilentFail` and the run falls back to an ordinary wall when nothing matches.
        /// A profile without that mod gets a solid viewing wall and a working facility.
        /// </summary>
        public List<RimroomsWallRunPlan> glazing = new List<RimroomsWallRunPlan>();

        /// <summary>
        /// Free-standing wall cells inside a room: the columns that hold a big roof up.
        ///
        /// **A roof is only supported within 6.9 cells of a wall, and an unsupported one
        /// collapses when a pawn deconstructs the wall holding it** -- on top of whoever is
        /// standing there. The gate hall is twenty cells across, so its middle is out of range of
        /// every perimeter wall it has, and `proof-startplacement.py` refuses a layout like that
        /// for exactly that reason. It caught this facility on its first authoring.
        ///
        /// A column is not furniture: it is structure, so it is listed apart from
        /// <see cref="buildings"/> and takes the start's own `wallStuff`. It also happens to be
        /// what a hall for a large machine actually looks like.
        /// </summary>
        public List<IntVec3> pillars = new List<IntVec3>();

        /// <summary>
        /// Which of this start's doors are automatic, for the security airlocks.
        ///
        /// Every cell here must also be in <see cref="doors"/>: this marks a door's kind, it does
        /// not add one. An airlock is two doors in series through a vestibule, and both being
        /// automatic is what makes it read as a controlled threshold rather than two doors.
        /// </summary>
        public List<IntVec3> autodoors = new List<IntVec3>();
        public List<RimroomsStockPlan> stock = new List<RimroomsStockPlan>();
        public List<RimroomsStaffRole> roles = new List<RimroomsStaffRole>();
        /// <summary>
        /// The starting people begin **inside a Backrooms coordinate**, alongside the surface map
        /// rather than on it.
        ///
        /// **Reworked in 0.12.2-dev.** It used to mean *the starting map is a coordinate*, which
        /// could never carry a registered exit: `RimroomsPortalNetwork.Register` requires the
        /// Backrooms side of a connection to be a `RimroomsDestinationMapParent`, and the starting
        /// map always belongs to a player `Settlement` because `Game.InitNewGame` demands one.
        ///
        /// Now the surface map is an ordinary map with a small shell and one door on it, a real
        /// coordinate is generated beside it, and <see cref="SoloGroupOpening"/> moves everybody
        /// inside after registering the way out. So an inside start **does** declare a layout —
        /// just a very small one.
        /// </summary>
        public bool insideStart;

        /// <summary>
        /// Which of this start's doors is the way out of the Backrooms.
        ///
        /// Named here rather than guessed. A start that placed two doors and let the opening pick
        /// one would put the exit somewhere different depending on scan order, and the player
        /// would have no way to know which door mattered.
        /// </summary>
        public IntVec3 emergenceDoorCell = IntVec3.Invalid;

        /// <summary>How deep the coordinate is. Higher is deeper; depth 1 is the yellow rooms.</summary>
        public int insideStartDepth = 1;

        /// <summary>
        /// How many places this company may hold open at once, or **0 to use the game's own
        /// colony limit**.
        ///
        /// **Owner direction, 2026-09-30, verbatim:** *"dont let them go more than 5 remember the
        /// games mechanics and limits built in ... they should gett a warning this gate is blocked
        /// your holding open too many gates, but per scerio styled"*, and *"5 is the limit of
        /// other colonies available so a backrooms level should be one colonly bacskicly in my
        /// thinking"*.
        ///
        /// *"Per scerio styled"* is why this lives on the start def rather than being a constant:
        /// a start can be given a tighter or looser budget than another. Zero means defer to
        /// <c>Prefs.MaxNumberOfPlayerSettlements</c>, the player's own 1-to-5 slider, which is the
        /// *"limits built in"* the direction points at. See
        /// <see cref="Portals.OpenMapBudget"/>.
        /// </summary>
        public int openMapBudget;

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
            if (mapSize < 40 || mapSize > 300) { yield return "Invalid headquarters reference size."; }
            if (outdoorTerrain == null || floorTerrain == null || wallStuff == null) { yield return "Missing headquarters terrain/material."; }
            // Five was the Async Industries roster written as a rule for every start. The
            // Store opens with three ordinary people and the solo/group start with as few
            // as one, so the real rule is "at least one, and no more than the company
            // recognises". A start with no roles has nobody to assign work to.
            if (roles == null || roles.Count < 1 || roles.Count > 5)
            { yield return "A start needs between one and five distinct starting roles."; }
            if (rooms == null || buildings == null || stock == null || doors == null || conduits == null)
            { yield return "Missing headquarters layout/stock list."; }
            if (rooms != null && rooms.Count < 1)
            { yield return "Every start needs at least one room on its surface map."; }
            if (autodoors != null && doors != null)
            {
                foreach (IntVec3 cell in autodoors)
                {
                    if (!doors.Contains(cell))
                    { yield return "An autodoor cell must also be listed in doors: " + cell; }
                }
            }
            if (glazing != null)
            {
                foreach (RimroomsWallRunPlan run in glazing)
                {
                    if (run == null || run.length < 1 || run.length > mapSize)
                    { yield return "Invalid glazed wall run."; continue; }
                    if (run.thingDefNames == null || run.thingDefNames.Count < 1)
                    { yield return "A glazed wall run must name at least one candidate def."; }
                }
            }
            if (insideStart && (insideStartDepth < 1 || insideStartDepth > 9))
            { yield return "Inside start depth must be between 1 and 9."; }
            // The way out has to be one of this start's own doors. A cell that is not in the
            // doors list has no door generated at it, so the opening would find nothing to mark
            // and the start would have no registered exit at all -- which is the one thing the
            // owner's direction says it must have at 100%.
            // An inside start MUST name one. Any other start MAY -- and naming one is what
            // gives it a natural gate at 0.12.45-dev. Either way the cell has to be one of this
            // start's own doors, because a cell that is not in the doors list has no door
            // generated at it and the opening would find nothing to mark.
            if (insideStart && !emergenceDoorCell.IsValid)
            { yield return "An inside start must name an emergenceDoorCell."; }
            if (emergenceDoorCell.IsValid && (doors == null || !doors.Contains(emergenceDoorCell)))
            { yield return "emergenceDoorCell must be one of this start's own doors."; }
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

    /// <summary>
    /// A straight run of wall cells to be replaced after the rooms are built.
    ///
    /// Candidates are tried in order and the first def the game has actually loaded wins, so an
    /// Optional mod's glass is used when it is there and an ordinary wall stands in when it is
    /// not. Nothing here is a cross-reference; see <see cref="RimroomsStartDef.glazing"/> for why
    /// that matters more than it looks.
    /// </summary>
    public sealed class RimroomsWallRunPlan
    {
        public IntVec3 start;
        public int length;
        public bool alongX = true;
        public List<string> thingDefNames = new List<string>();
        public List<string> stuffDefNames = new List<string>();

        public IntVec3 CellAt(int step)
        { return start + new IntVec3(alongX ? step : 0, 0, alongX ? 0 : step); }
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
