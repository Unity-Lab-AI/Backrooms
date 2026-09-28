using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// RR-SCEN / RR-ECO: save-local foundation, inert until a scenario initializer exists.
    /// The constructor is called for every game, including existing non-Rimrooms saves.
    /// </summary>
    public sealed class RimroomsCampaignComponent : GameComponent
    {
        public const int CurrentSchemaVersion = 1;
        private int schemaVersion = CurrentSchemaVersion;
        private string branchId;
        private string scenarioId;

        public RimroomsCampaignComponent(Game game)
        {
            // Core requires this exact constructor. Never grant funds or spawn here.
        }

        public int SchemaVersion { get { return schemaVersion; } }
        public string BranchId { get { return branchId; } }
        public string ScenarioId { get { return scenarioId; } }
        public bool HasBranch { get { return !string.IsNullOrEmpty(branchId); } }
        public bool HasSupportedSchema { get { return schemaVersion == CurrentSchemaVersion; } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_schemaVersion", CurrentSchemaVersion, forceSave: true);
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_Values.Look(ref scenarioId, "rr_scenarioId");
        }
    }
}
