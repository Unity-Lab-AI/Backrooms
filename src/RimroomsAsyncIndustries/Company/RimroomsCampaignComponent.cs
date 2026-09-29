using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// RR-SCEN / RR-ECO: one branch per save, activated only by a scenario initializer.
    /// The constructor is called for every game, including existing non-Rimrooms saves.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent : GameComponent, IRenameable
    {
        public const int CurrentSchemaVersion = 2;
        // Bounded record growth. Visited coordinates are never removed to make room.
        internal const int MaximumCoordinates = 512;
        private int schemaVersion = CurrentSchemaVersion;
        private string branchId;
        /// <summary>
        /// What the player calls this company. Every start can build a full company and
        /// name it their own, so this is never derived from the scenario.
        /// </summary>
        private string companyName;
        private string scenarioId;
        private int scenarioVersion;
        private int campaignSeed;
        private bool initializationComplete;
        private string initializationReceipt;
        private Map headquarters;
        private int initializedTick;
        private long balanceUsd;
        private long dailyOverheadUsd;
        private int nextOperatingCostTick;
        private int researchInsights;

        /// <summary>
        /// Whether this branch is in communication with the parent corporation.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"clena up tema is only once u are in
        /// communication and working with the corporation Async industries starts with this tech
        /// research and other basic gate techs it needs to operate and begin researching and gate
        /// operations at basic levels but the other two scenerios need special treatment in theri
        /// layout and starts"*.
        ///
        /// **Contact is a state, not a scenario.** Async Industries begins with it true and can
        /// operate from the first minute. The Store and Solo/Group starts begin without it, and
        /// reaching it is what turns the corporation's attention - and its clean-up team - on.
        ///
        /// One-way by design: a branch that has been in contact stays in contact. A corporation
        /// that has seen a return on an investment does not forget about it, and losing contact
        /// would take the never-die guarantee away from a player who had earned it.
        /// </summary>
        private bool corporationContact;

        /// <summary>
        /// Capabilities this branch has earned, rebuilt from completed projects.
        ///
        /// Cached rather than computed per call because the read sites include a gate power
        /// property and a pursuer tick. Not saved: it is derived entirely from the project
        /// records, which are, so a load rebuilds it rather than trusting a second copy that
        /// could disagree with the first.
        /// </summary>
        private HashSet<string> capabilityCache;
        private List<LedgerEntry> ledger = new List<LedgerEntry>();
        private List<StaffRecord> staff = new List<StaffRecord>();
        private List<CompanyObligation> obligations = new List<CompanyObligation>();
        private List<ContractRecord> contracts = new List<ContractRecord>();
        private List<CoordinateRecord> coordinates = new List<CoordinateRecord>();
        private List<CaseRecord> cases = new List<CaseRecord>();
        private List<EvidenceRecord> evidence = new List<EvidenceRecord>();
        private List<ProjectRecord> projects = new List<ProjectRecord>();
        private List<CompanyEventRecord> events = new List<CompanyEventRecord>();
        private readonly Dictionary<string, LedgerEntry> ledgerIndex = new Dictionary<string, LedgerEntry>(StringComparer.Ordinal);
        private string stateFaultKey;

        public RimroomsCampaignComponent(Game game)
        {
            // Core requires this exact constructor. Never grant funds or spawn here.
        }

        public int SchemaVersion { get { return schemaVersion; } }

        /// <summary>
        /// The branch's own seed, read-only. Exposed so a deterministic draw can be made
        /// about a map that is not a generated coordinate and therefore has no
        /// <c>CoordinateRecord.Seed</c> of its own — an ordinary colony or world-site map.
        /// Read-only on purpose: nothing outside this component may reseed a branch. Named
        /// BranchSeed rather than CampaignSeed because the latter is the static derivation
        /// helper in this same namespace, and a property of that name silently shadowed it.
        /// </summary>
        public int BranchSeed { get { return campaignSeed; } }
        public string BranchId { get { return branchId; } }

        /// <summary>The player's own name for this company, or a neutral fallback.</summary>
        public string CompanyName
        {
            get
            {
                return string.IsNullOrWhiteSpace(companyName)
                    ? "RR_Company_UnnamedCompany".Translate().ToString() : companyName;
            }
        }

        // Core's own renaming interface, so the company renames through the same
        // dialog everything else in the game renames through.
        public string RenamableLabel
        {
            get { return CompanyName; }
            set { TrySetCompanyName(value); }
        }
        public string BaseLabel { get { return CompanyName; } }
        public string InspectLabel { get { return CompanyName; } }

        /// <summary>
        /// Normalise and accept a name. A blank or over-long entry leaves the existing
        /// name alone rather than clearing it, so the field can never end up empty.
        /// </summary>
        internal bool TrySetCompanyName(string value)
        {
            if (value == null) { return false; }
            string trimmed = value.Trim();
            if (trimmed.Length < 1 || trimmed.Length > MaximumCompanyNameLength) { return false; }
            companyName = trimmed;
            return true;
        }

        /// <summary>Bounded so a saved name cannot grow without limit.</summary>
        internal const int MaximumCompanyNameLength = 64;
        public string ScenarioId { get { return scenarioId; } }
        public bool HasBranch { get { return initializationComplete && !string.IsNullOrEmpty(branchId); } }
        public bool HasSupportedSchema { get { return schemaVersion == CurrentSchemaVersion; } }
        public bool CanOperate { get { return HasSupportedSchema && HasBranch && stateFaultKey == null; } }
        public string StateFaultKey { get { return stateFaultKey; } }
        public Map Headquarters { get { return headquarters; } }
        public long BalanceUsd { get { return balanceUsd; } }
        public int ResearchInsights { get { return researchInsights; } }

        /// <summary>
        /// Whether a completed project has granted this branch a named capability.
        ///
        /// **Every capability any project grants must be read by at least one source file**, and
        /// `proof-research-branches.py` asserts exactly that. An unlock a player is told about and
        /// that changes nothing is worse than no unlock: it is a lie on the card.
        /// </summary>
        public bool HasCapability(string capability)
        {
            if (string.IsNullOrEmpty(capability) || !CanOperate) { return false; }
            if (capabilityCache == null) { RebuildCapabilities(); }
            return capabilityCache.Contains(capability);
        }

        /// <summary>
        /// Recompute from the completed project records. Called when a project completes and
        /// whenever the cache is cold, including after a load.
        /// </summary>
        internal void RebuildCapabilities()
        {
            if (capabilityCache == null) { capabilityCache = new HashSet<string>(StringComparer.Ordinal); }
            capabilityCache.Clear();
            for (int index = 0; index < projects.Count; index++)
            {
                ProjectRecord record = projects[index];
                if (record == null || !record.Completed) { continue; }
                Investigation.RimroomsProjectDef definition =
                    DefDatabase<Investigation.RimroomsProjectDef>.GetNamedSilentFail(record.ResearchDefName);
                if (definition == null || definition.grantsCapabilities == null) { continue; }
                for (int slot = 0; slot < definition.grantsCapabilities.Count; slot++)
                {
                    string capability = definition.grantsCapabilities[slot];
                    if (!string.IsNullOrWhiteSpace(capability)) { capabilityCache.Add(capability); }
                }
            }
        }

        /// <summary>True once this branch is in communication with the parent corporation.</summary>
        public bool CorporationContact { get { return corporationContact; } }

        /// <summary>
        /// Establish contact. One-way: there is deliberately no method to take it back.
        /// </summary>
        public CompanyActionResult EstablishCorporationContact()
        {
            if (!CanOperate) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            if (corporationContact) { return CompanyActionResult.Existing(); }
            corporationContact = true;
            RecordEvent("RR_Event_CorporationContact", BranchId);
            return CompanyActionResult.Applied();
        }
        public IReadOnlyList<LedgerEntry> Ledger { get { return ledger; } }
        public IReadOnlyList<StaffRecord> Staff { get { return staff; } }
        public IReadOnlyList<CompanyObligation> Obligations { get { return obligations; } }
        public IReadOnlyList<ContractRecord> Contracts { get { return contracts; } }
        public IReadOnlyList<CoordinateRecord> Coordinates { get { return coordinates; } }
        public IReadOnlyList<CaseRecord> Cases { get { return cases; } }
        public IReadOnlyList<EvidenceRecord> Evidence { get { return evidence; } }
        public IReadOnlyList<ProjectRecord> Projects { get { return projects; } }
        public IReadOnlyList<CompanyEventRecord> Events { get { return events; } }

        public override void ExposeData()
        {
            base.ExposeData();
            // Version 1 is the only historical missing-field default; always write a version.
            Scribe_Values.Look(ref schemaVersion, "rr_schemaVersion", 1, forceSave: true);
            Scribe_Values.Look(ref branchId, "rr_branchId");
            // Additive; a save from before company naming loads with no name and
            // falls back to the neutral label. No schema bump, so older saves load.
            Scribe_Values.Look(ref companyName, "rr_companyName");
            Scribe_Values.Look(ref scenarioId, "rr_scenarioId");
            Scribe_Values.Look(ref scenarioVersion, "rr_scenarioVersion");
            Scribe_Values.Look(ref campaignSeed, "rr_campaignSeed");
            Scribe_Values.Look(ref initializationComplete, "rr_initializationComplete");
            Scribe_Values.Look(ref initializationReceipt, "rr_initializationReceipt");
            Scribe_References.Look(ref headquarters, "rr_headquarters");
            Scribe_Values.Look(ref initializedTick, "rr_initializedTick");
            Scribe_Values.Look(ref balanceUsd, "rr_balanceUsd");
            Scribe_Values.Look(ref dailyOverheadUsd, "rr_dailyOverheadUsd");
            Scribe_Values.Look(ref nextOperatingCostTick, "rr_nextOperatingCostTick");
            Scribe_Values.Look(ref researchInsights, "rr_researchInsights");
            Scribe_Values.Look(ref corporationContact, "rr_corporationContact", false);
            Scribe_Collections.Look(ref ledger, "rr_ledger", LookMode.Deep);
            Scribe_Collections.Look(ref staff, "rr_staff", LookMode.Deep);
            Scribe_Collections.Look(ref obligations, "rr_obligations", LookMode.Deep);
            Scribe_Collections.Look(ref contracts, "rr_contracts", LookMode.Deep);
            Scribe_Collections.Look(ref coordinates, "rr_coordinates", LookMode.Deep);
            Scribe_Collections.Look(ref cases, "rr_cases", LookMode.Deep);
            Scribe_Collections.Look(ref evidence, "rr_evidence", LookMode.Deep);
            Scribe_Collections.Look(ref projects, "rr_projects", LookMode.Deep);
            Scribe_Collections.Look(ref events, "rr_events", LookMode.Deep);
            ExposeRequests();
            ExposeSupplyContracts();
            ExposeCorporateSupply();
            ExposeFacilityRelief();
            ExposeSoloGroupHints();
            ExposeRemoteSites();
            ExposeLostPawns();
            ExposeEncounterProgression();
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                RestoreCollections();
                if (schemaVersion == 1)
                {
                    // The foundation could not initialize a branch or award funds.
                    // Preserve its scalar identities and leave ordinary saves inactive.
                    schemaVersion = 2;
                }
                ValidateSavedState();
            }
        }

        private void RestoreCollections()
        {
            ledger = ledger ?? new List<LedgerEntry>();
            staff = staff ?? new List<StaffRecord>();
            obligations = obligations ?? new List<CompanyObligation>();
            contracts = contracts ?? new List<ContractRecord>();
            coordinates = coordinates ?? new List<CoordinateRecord>();
            cases = cases ?? new List<CaseRecord>();
            evidence = evidence ?? new List<EvidenceRecord>();
            projects = projects ?? new List<ProjectRecord>();
            events = events ?? new List<CompanyEventRecord>();
        }

        private void ValidateSavedState()
        {
            ledgerIndex.Clear();
            stateFaultKey = null;
            if (!HasSupportedSchema) { return; }
            long runningBalance = 0;
            try
            {
                foreach (LedgerEntry entry in ledger)
                {
                    if (entry == null || string.IsNullOrEmpty(entry.operationId) || ledgerIndex.ContainsKey(entry.operationId))
                    {
                        stateFaultKey = "RR_Company_InvalidSave";
                        break;
                    }
                    ledgerIndex.Add(entry.operationId, entry);
                    runningBalance = checked(runningBalance + entry.amountUsd);
                    if (runningBalance < 0 || entry.balanceAfterUsd != runningBalance)
                    {
                        stateFaultKey = "RR_Company_InvalidSave";
                    }
                }
            }
            catch (OverflowException) { stateFaultKey = "RR_Company_InvalidSave"; }
            if (runningBalance != balanceUsd || researchInsights < 0 || dailyOverheadUsd < 0 ||
                (initializationComplete && (string.IsNullOrEmpty(branchId) || string.IsNullOrEmpty(initializationReceipt))))
            {
                stateFaultKey = "RR_Company_InvalidSave";
            }
            if (!UniqueRecords(staff, r => r.id) || !UniqueRecords(obligations, r => r.id) ||
                !UniqueRecords(contracts, r => r.id) || !UniqueRecords(coordinates, r => r.id) ||
                !UniqueRecords(cases, r => r.id) || !UniqueRecords(evidence, r => r.id) || !UniqueRecords(projects, r => r.id))
            {
                stateFaultKey = "RR_Company_InvalidSave";
            }
            // The request line carries payment operation ids, so a duplicate record is a
            // double-payment waiting to happen rather than a cosmetic problem.
            if (!RequestRecordsValid()) { stateFaultKey = "RR_Company_InvalidSave"; }
            foreach (StaffRecord member in staff)
            {
                if (member != null && member.dailyWageUsd < 0) { stateFaultKey = "RR_Company_InvalidSave"; }
            }
            foreach (CompanyObligation obligation in obligations)
            {
                if (obligation != null && obligation.amountUsd <= 0) { stateFaultKey = "RR_Company_InvalidSave"; }
            }
            ValidateRecordRelationships();
            if (stateFaultKey != null) { Log.Error("[Rimrooms][Save] Campaign integrity failed; company actions are disabled. Preserve the original save."); }
        }

        private void ValidateRecordRelationships()
        {
            // A lost physical reference is a gameplay recovery case. Broken logical owners or
            // invalid amounts are a save-integrity fault and must never award money/work.
            if (stateFaultKey != null) { return; }
            var coordinateIds = new HashSet<string>(coordinates.Select(c => c.id), StringComparer.Ordinal);
            var caseIds = new HashSet<string>(cases.Select(c => c.id), StringComparer.Ordinal);
            var pawnIds = new HashSet<string>(StringComparer.Ordinal);
            bool valid = staff.All(s => !string.IsNullOrWhiteSpace(s.pawnLoadId) && pawnIds.Add(s.pawnLoadId));
            // An odd-supply contract is branch-wide rather than tied to one coordinate: it
            // buys goods by origin, and any coordinate that produced them satisfies it. So it
            // legitimately carries no coordinate id, and requiring one would fault a valid save.
            valid &= contracts.All(c => (c.IsOddSupply ? string.IsNullOrEmpty(c.coordinateId)
                    : coordinateIds.Contains(c.coordinateId)) &&
                Enum.IsDefined(typeof(ContractStatus), c.status) &&
                c.basePaymentUsd >= 0 && c.bonusUsd >= 0 && !string.IsNullOrWhiteSpace(c.templateId) &&
                c.requiredCount >= 0 && c.deliveredCount >= 0);
            valid &= cases.All(c => coordinateIds.Contains(c.coordinateId) && c.evidenceIds != null &&
                c.evidenceIds.Count == c.evidenceIds.Distinct(StringComparer.Ordinal).Count() &&
                c.evidenceIds.All(id => evidence.Any(e => e.id == id && e.caseId == c.id)));
            valid &= evidence.All(e => coordinateIds.Contains(e.coordinateId) && caseIds.Contains(e.caseId) &&
                cases.Any(c => c.id == e.caseId && c.coordinateId == e.coordinateId && c.evidenceIds.Contains(e.id)) &&
                Enum.IsDefined(typeof(EvidenceStatus), e.status) && FiniteNonnegative(e.analysisWork) &&
                !string.IsNullOrWhiteSpace(e.itemLoadId));
            valid &= evidence.All(e => ValidObservationState(e, coordinates.FirstOrDefault(c => c.id == e.coordinateId)));
            valid &= projects.All(p => FiniteNonnegative(p.workDone) && !string.IsNullOrWhiteSpace(p.researchDefName) &&
                (!p.completed || p.insightCommitted) && (!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId)));
            valid &= projects.Count(p => p.insightCommitted && !p.completed) <= 1;
            foreach (CoordinateRecord coordinate in coordinates)
            {
                valid &= Enum.IsDefined(typeof(CoordinateStatus), coordinate.status) && coordinate.generatorVersion > 0 &&
                    coordinate.roomLibraryVersion > 0 && coordinate.rooms != null;
                if (coordinate.rooms == null) { continue; }
                var indices = new HashSet<int>();
                foreach (RoomRecord room in coordinate.rooms)
                {
                    if (room == null || room.index < 0 || !indices.Add(room.index) || room.width <= 0 || room.height <= 0 ||
                        string.IsNullOrWhiteSpace(room.familyId) || room.links == null) { valid = false; }
                }
                foreach (RoomRecord room in coordinate.rooms.Where(r => r != null && r.links != null))
                { valid &= room.links.All(index => index != room.index && indices.Contains(index)); }
            }
            if (!valid) { stateFaultKey = "RR_Company_InvalidSave"; }
        }

        private static bool FiniteNonnegative(float value)
        { return value >= 0f && !float.IsNaN(value) && !float.IsInfinity(value); }

        private static bool UniqueRecords<T>(IEnumerable<T> records, Func<T, string> getId) where T : class
        {
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (T record in records)
            {
                if (record == null) { return false; }
                string id = getId(record);
                if (string.IsNullOrWhiteSpace(id) || !ids.Add(id)) { return false; }
            }
            return true;
        }
    }
}
