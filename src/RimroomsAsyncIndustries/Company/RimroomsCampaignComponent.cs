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
        /// <summary>
        /// How many discovered-but-never-entered coordinates the branch may hold at once.
        ///
        /// Coordinates live in three tiers. **Discovered** is the lifetime history, kept as the
        /// running summary below and never capped. **Retained** is every record a crew has been
        /// inside or that anything still points at: kept for good and never removed, so a revisit
        /// always returns to the same place. **Active** is the set with a loaded map, bounded by
        /// the open-map budget. Only the untouched frontier is bounded here, so the cap protects
        /// the save from a runaway frontier without ever ending exploration.
        /// </summary>
        internal const int MaximumUnvisitedCoordinates = 512;

        // Paid obligations folded out of the list once it grows long, as a count and a sum.
        private int foldedObligationCount;
        private long foldedObligationTotalUsd;

        /// <summary>How many paid obligations have been folded into the summary, and their total.</summary>
        public int FoldedObligationCount { get { return foldedObligationCount; } }
        public long FoldedObligationTotalUsd { get { return foldedObligationTotalUsd; } }

        // Lifetime discovery summary. Saved; an older save backfills from its records on load.
        private int coordinatesDiscoveredTotal;
        private int deepestDiscoveredDepth;

        // Lookup by id. Not saved: rebuilt from the list whenever it is cold or stale.
        private Dictionary<string, CoordinateRecord> coordinateIndex;
        private int coordinateIndexCount = -1;
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
        /// The branch's standing order for a containment failure: cut every open connection.
        ///
        /// **Defaults to true**, which is the safe reading and also the one a save written
        /// before this field existed gets for free — `Scribe_Values` hands back the default
        /// for a missing field, so an older save loads with the procedure armed rather than
        /// with a silently disarmed one. See <see cref="ContainmentProtocol"/>.
        /// </summary>
        private bool cutConnectionsOnBreach = true;

        /// <summary>
        /// Whether the procedure has already fired for the incident in progress. Latched so a
        /// second subject starting to escape during the same breach does not slam the doors a
        /// second time, and cleared only when nothing anywhere is getting out.
        ///
        /// Saved, because a save made mid-breach must reload mid-breach rather than re-firing
        /// the procedure and sending a second letter about connections that are already shut.
        /// </summary>
        private bool breachResponded;

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

        /// <summary>
        /// WHICH integrity check failed, in plain words, for the log and the pane.
        ///
        /// ## A FAULT THAT NAMES NO CAUSE IS THE ONE REFUSAL THIS MOD GOT WRONG
        ///
        /// About a dozen distinct conditions all set <see cref="stateFaultKey"/> to the same
        /// `RR_Company_InvalidSave`, and the only thing written to the log was *"Campaign integrity
        /// failed; company actions are disabled."* **A player whose company has switched itself off
        /// is given nothing to act on**, which is the exact opposite of what `troubleshooting.md`
        /// promises in its own first line: *"Every refusal in the game names its own cause. Read it
        /// -- the cause is the instruction."*
        ///
        /// Measured 2026-10-06: pinning a real fault in a real save took reading the save's XML by
        /// hand and re-running each condition outside the game, because nothing in the game would
        /// say which one it was. That is the cost this field removes.
        ///
        /// The player-facing key is unchanged, so no translation moves; this is additional detail
        /// beside it rather than a replacement for it.
        /// </summary>
        private string stateFaultDetail;

        /// <summary>Record a fault and keep the FIRST cause, which is the one nearest the data.</summary>
        private void Fault(string detail)
        {
            stateFaultKey = "RR_Company_InvalidSave";
            if (string.IsNullOrEmpty(stateFaultDetail)) { stateFaultDetail = detail; }
        }

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

        public bool CutConnectionsOnBreach { get { return cutConnectionsOnBreach; } }

        public bool BreachResponded { get { return breachResponded; } }

        // Written only through ContainmentProtocol, which owns every rule about when the
        // procedure runs. These are stores, not decisions.
        internal void SetCutConnectionsOnBreach(bool cut) { cutConnectionsOnBreach = cut; }

        internal void NoteBreachResponded() { breachResponded = true; }

        internal void ClearBreachResponded() { breachResponded = false; }

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
            Scribe_Values.Look(ref cutConnectionsOnBreach, "rr_cutConnectionsOnBreach", true);
            Scribe_Values.Look(ref breachResponded, "rr_breachResponded", false);
            Scribe_Values.Look(ref coordinatesDiscoveredTotal, "rr_coordinatesDiscoveredTotal", 0);
            Scribe_Values.Look(ref deepestDiscoveredDepth, "rr_deepestDiscoveredDepth", 0);
            Scribe_Values.Look(ref foldedObligationCount, "rr_foldedObligationCount", 0);
            Scribe_Values.Look(ref foldedObligationTotalUsd, "rr_foldedObligationTotalUsd", 0L);
            ExposeDebriefs();
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
            ExposeWorldExits();
            ExposeSupplyContracts();
            ExposeConsignmentMissions();
            ExposeCorporateSupply();
            ExposeFacilityRelief();
            ExposeClearSquad();
            ExposeFieldExposure();
            ExposeCertifications();
            ExposeRecordBookDelivery();
            ExposeQuestBookDelivery();
            ExposeQuestBookCollection();
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
            InvalidateCoordinateIndex();
            // A save from before the summary existed never removed a coordinate, so its records
            // are its whole discovery history.
            if (coordinatesDiscoveredTotal < coordinates.Count) { coordinatesDiscoveredTotal = coordinates.Count; }
            foreach (CoordinateRecord record in coordinates)
            {
                if (record != null && record.Depth > deepestDiscoveredDepth) { deepestDiscoveredDepth = record.Depth; }
            }
        }

        /// <summary>Every coordinate this branch has ever discovered, including any later replaced.</summary>
        public int CoordinatesDiscoveredTotal { get { return coordinatesDiscoveredTotal; } }

        /// <summary>The deepest coordinate this branch has ever discovered.</summary>
        public int DeepestDiscoveredDepth { get { return deepestDiscoveredDepth; } }

        internal void NoteCoordinateDiscovered(CoordinateRecord record)
        {
            if (record == null) { return; }
            if (coordinatesDiscoveredTotal < int.MaxValue) { coordinatesDiscoveredTotal++; }
            if (record.Depth > deepestDiscoveredDepth) { deepestDiscoveredDepth = record.Depth; }
        }

        internal void InvalidateCoordinateIndex()
        {
            coordinateIndex = null;
            coordinateIndexCount = -1;
        }

        /// <summary>The coordinate with this id, or null. Constant time after the first call.</summary>
        internal CoordinateRecord FindCoordinate(string id)
        {
            if (string.IsNullOrEmpty(id)) { return null; }
            if (coordinateIndex == null || coordinateIndexCount != coordinates.Count)
            {
                coordinateIndex = new Dictionary<string, CoordinateRecord>(StringComparer.Ordinal);
                foreach (CoordinateRecord record in coordinates)
                {
                    // First wins, matching the linear search this replaces.
                    if (record != null && record.id != null && !coordinateIndex.ContainsKey(record.id))
                    { coordinateIndex.Add(record.id, record); }
                }
                coordinateIndexCount = coordinates.Count;
            }
            CoordinateRecord found;
            return coordinateIndex.TryGetValue(id, out found) ? found : null;
        }

        /// <summary>
        /// Coordinates nobody has entered and nothing refers to: no map, never opened, not
        /// released, no surveyed room, and no contract or case naming them.
        /// </summary>
        private int CountUnvisitedCoordinates()
        {
            var referenced = new HashSet<string>(StringComparer.Ordinal);
            foreach (ContractRecord contract in contracts)
            { if (contract != null && !string.IsNullOrEmpty(contract.coordinateId)) { referenced.Add(contract.coordinateId); } }
            foreach (CaseRecord record in cases)
            { if (record != null && !string.IsNullOrEmpty(record.coordinateId)) { referenced.Add(record.coordinateId); } }
            int count = 0;
            foreach (CoordinateRecord record in coordinates)
            {
                if (record == null || record.site != null || record.openings > 0 || record.releasedByPlayer ||
                    record.status != CoordinateStatus.Discovered || referenced.Contains(record.id)) { continue; }
                if (record.rooms != null && record.rooms.Any(room => room != null && room.surveyed)) { continue; }
                count++;
            }
            return count;
        }

        private void ValidateSavedState()
        {
            ledgerIndex.Clear();
            stateFaultKey = null;
            stateFaultDetail = null;
            if (!HasSupportedSchema) { return; }
            long runningBalance = 0;
            try
            {
                foreach (LedgerEntry entry in ledger)
                {
                    if (entry == null || string.IsNullOrEmpty(entry.operationId) || ledgerIndex.ContainsKey(entry.operationId))
                    {
                        Fault(entry == null ? "a ledger entry is null"
                              : string.IsNullOrEmpty(entry.operationId)
                                  ? "a ledger entry has no operationId"
                                  : "two ledger entries share operationId '" + entry.operationId + "'");
                        break;
                    }
                    ledgerIndex.Add(entry.operationId, entry);
                    runningBalance = checked(runningBalance + entry.amountUsd);
                    if (runningBalance < 0 || entry.balanceAfterUsd != runningBalance)
                    {
                        Fault("ledger entry '" + entry.operationId + "' records a balance of "
                              + entry.balanceAfterUsd + " where the running total is " + runningBalance);
                    }
                }
            }
            catch (OverflowException) { Fault("the ledger total overflows a 64-bit balance"); }
            if (runningBalance != balanceUsd)
            { Fault("the balance is " + balanceUsd + " but the ledger sums to " + runningBalance); }
            if (researchInsights < 0) { Fault("researchInsights is negative (" + researchInsights + ")"); }
            if (dailyOverheadUsd < 0) { Fault("dailyOverheadUsd is negative (" + dailyOverheadUsd + ")"); }
            if (initializationComplete && (string.IsNullOrEmpty(branchId) || string.IsNullOrEmpty(initializationReceipt)))
            { Fault("the branch says it finished initialising but has no branchId or receipt"); }
            if (!UniqueRecords(staff, r => r.id)) { Fault("two staff records share an id"); }
            if (!UniqueRecords(obligations, r => r.id)) { Fault("two obligations share an id"); }
            if (!UniqueRecords(contracts, r => r.id)) { Fault("two contracts share an id"); }
            if (!UniqueRecords(coordinates, r => r.id)) { Fault("two coordinates share an id"); }
            if (!UniqueRecords(cases, r => r.id)) { Fault("two cases share an id"); }
            if (!UniqueRecords(evidence, r => r.id)) { Fault("two evidence records share an id"); }
            if (!UniqueRecords(projects, r => r.id)) { Fault("two project records share an id"); }
            // The request line carries payment operation ids, so a duplicate record is a
            // double-payment waiting to happen rather than a cosmetic problem.
            if (!RequestRecordsValid()) { Fault("the request line has a duplicate or malformed record"); }
            foreach (StaffRecord member in staff)
            {
                if (member != null && member.dailyWageUsd < 0)
                { Fault("staff record '" + member.id + "' has a negative daily wage"); }
            }
            foreach (CompanyObligation obligation in obligations)
            {
                if (obligation != null && obligation.amountUsd <= 0)
                { Fault("obligation '" + obligation.id + "' has an amount of " + obligation.amountUsd); }
            }
            ValidateRecordRelationships();
            if (stateFaultKey != null)
            {
                Log.Error("[Rimrooms][Save] Campaign integrity failed; company actions are disabled. "
                          + "Preserve the original save. Cause: "
                          + (stateFaultDetail ?? "not recorded, which is itself a defect"));
            }
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
            // ## THERE ARE THREE KINDS OF CONTRACT HERE, AND THIS TESTED FOR TWO
            //
            // **This condition disabled the whole company in any save holding a consignment
            // mission, and it was found by loading one.** The log said only *"Campaign integrity
            // failed"*, so the cost of finding it was reading the save's XML by hand.
            //
            // The old test was `c.IsOddSupply ? string.IsNullOrEmpty(c.coordinateId) : ...`, with
            // the comment: *"An odd-supply contract is branch-wide rather than tied to one
            // coordinate ... So it legitimately carries no coordinate id, and requiring one would
            // fault a valid save."* **That was true when it was written and stopped being true when
            // consignment missions landed at 0.12.41-dev**, because:
            //
            //   * `IsOddSupply` is `requiredThingDefName != "" && requiredCount > 0` -- it says
            //     nothing about the template, so a mission satisfies it;
            //   * `IsOddConsignment` is `IsOddSupply && requiredSurveyedRooms > 0`, so **every
            //     consignment mission IS an odd-supply contract**;
            //   * and a mission **names one coordinate on purpose**: its own record says *"A mission
            //     names one coordinate, wants goods that coordinate produced"*.
            //
            // So `IsNullOrEmpty(coordinateId)` was false for a legal record and the branch died.
            // Measured in a real save: `rr.mission.oddconsignment.v1`, coordinate set,
            // `requiredThingDefName=XER_MediumTableM`, `requiredCount=8`, `requiredSurveyedRooms=2`.
            //
            // **Mission is tested FIRST because it is the narrower kind.** Testing `IsOddSupply`
            // first is what hid a mission inside the broad case, and ordering the narrow test ahead
            // of the broad one is the only arrangement that cannot regress the same way.
            foreach (ContractRecord contract in contracts)
            {
                string template = contract.templateId ?? "(no template)";
                if (contract.IsOddConsignment)
                {
                    // A mission is about ONE place, so its coordinate must exist.
                    if (!coordinateIds.Contains(contract.coordinateId))
                    {
                        Fault("consignment mission '" + template + "' names coordinate '"
                              + (contract.coordinateId ?? "") + "', which is not in this save");
                    }
                }
                else if (contract.IsOddSupply)
                {
                    // A standing odd-supply demand is branch-wide and must name no coordinate.
                    if (!string.IsNullOrEmpty(contract.coordinateId))
                    {
                        Fault("odd-supply contract '" + template
                              + "' carries a coordinate id, which only a consignment mission may do");
                    }
                }
                else if (!coordinateIds.Contains(contract.coordinateId))
                {
                    Fault("contract '" + template + "' names coordinate '"
                          + (contract.coordinateId ?? "") + "', which is not in this save");
                }
                if (!Enum.IsDefined(typeof(ContractStatus), contract.status))
                { Fault("contract '" + template + "' has an unknown status"); }
                if (contract.basePaymentUsd < 0 || contract.bonusUsd < 0)
                { Fault("contract '" + template + "' has a negative payment"); }
                if (string.IsNullOrWhiteSpace(contract.templateId))
                { Fault("a contract has a blank templateId"); }
                if (contract.requiredCount < 0 || contract.deliveredCount < 0)
                { Fault("contract '" + template + "' has a negative count"); }
            }
            // Ids are unique by this point (checked above), so a lookup by id gives the same answer
            // the pairwise search did, without its quadratic cost on a long campaign.
            var evidenceById = new Dictionary<string, EvidenceRecord>(StringComparer.Ordinal);
            foreach (EvidenceRecord record in evidence) { evidenceById[record.id] = record; }
            var caseById = new Dictionary<string, CaseRecord>(StringComparer.Ordinal);
            foreach (CaseRecord record in cases) { caseById[record.id] = record; }
            valid &= cases.All(c => coordinateIds.Contains(c.coordinateId) && c.evidenceIds != null &&
                c.evidenceIds.Count == c.evidenceIds.Distinct(StringComparer.Ordinal).Count() &&
                c.evidenceIds.All(id => id != null && evidenceById.TryGetValue(id, out EvidenceRecord found) && found.caseId == c.id));
            valid &= evidence.All(e => coordinateIds.Contains(e.coordinateId) && caseIds.Contains(e.caseId) &&
                caseById.TryGetValue(e.caseId, out CaseRecord owner) && owner.coordinateId == e.coordinateId &&
                owner.evidenceIds != null && owner.evidenceIds.Contains(e.id) &&
                Enum.IsDefined(typeof(EvidenceStatus), e.status) && FiniteNonnegative(e.analysisWork) &&
                !string.IsNullOrWhiteSpace(e.itemLoadId));
            valid &= evidence.All(e => ValidObservationState(e, FindCoordinate(e.coordinateId)));
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
            if (!valid) { Fault("a record relationship is broken; see the conditions above"); }
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
