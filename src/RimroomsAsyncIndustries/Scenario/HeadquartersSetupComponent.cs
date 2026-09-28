using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>RR-SCEN: physical setup receipt survives a refused company initialization.</summary>
    public sealed class HeadquartersSetupComponent : MapComponent
    {
        public string startDefName;
        public bool setupStarted;
        public bool setupComplete;
        public bool branchInitialized;
        public string failure;
        public List<Pawn> staff = new List<Pawn>();
        public List<string> staffRoles = new List<string>();
        public List<string> placedRecords = new List<string>();

        public HeadquartersSetupComponent(Map map) : base(map) { }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref startDefName, "rr_startDefName");
            Scribe_Values.Look(ref setupStarted, "rr_setupStarted");
            Scribe_Values.Look(ref setupComplete, "rr_setupComplete");
            Scribe_Values.Look(ref branchInitialized, "rr_branchInitialized");
            Scribe_Values.Look(ref failure, "rr_setupFailure");
            Scribe_Collections.Look(ref staff, "rr_startStaff", LookMode.Reference);
            Scribe_Collections.Look(ref staffRoles, "rr_startRoles", LookMode.Value);
            Scribe_Collections.Look(ref placedRecords, "rr_placedRecords", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                staff = staff ?? new List<Pawn>();
                staffRoles = staffRoles ?? new List<string>();
                placedRecords = placedRecords ?? new List<string>();
            }
        }
    }
}
