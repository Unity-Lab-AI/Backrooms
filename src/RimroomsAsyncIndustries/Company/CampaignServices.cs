using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Generation;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Every company project the loaded game has, as this branch's research list.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"all starts have same tech tree just
        /// differnt starting researches finished based on scenerio"*. Taken literally: the
        /// tree is built from the def database rather than from the scenario, so **it is the
        /// same tree for every start by construction**, and a scenario chooses only which of
        /// its entries begin finished.
        ///
        /// This replaces a single hardcoded `RR_GateTelemetry` record. That hardcoding meant a
        /// second project would have been invisible to every existing branch until somebody
        /// remembered to add it in three places; now adding one def reaches every start at
        /// once.
        ///
        /// Ordinal sort before anything is built, because def load order varies with the mod
        /// list and two players starting the same scenario must get the same branch.
        /// </summary>
        private static List<ProjectRecord> BuildProjectTree(string branchId, List<string> completed)
        {
            var finished = new HashSet<string>(StringComparer.Ordinal);
            if (completed != null)
            {
                for (int index = 0; index < completed.Count; index++)
                {
                    string name = completed[index];
                    if (string.IsNullOrWhiteSpace(name)) { continue; }
                    if (DefDatabase<Investigation.RimroomsProjectDef>.GetNamedSilentFail(name) == null)
                    {
                        Log.Warning("[Rimrooms][Company] Start names completed project '" + name +
                            "', which no longer exists; it is skipped and the branch begins without it.");
                        continue;
                    }
                    finished.Add(name);
                }
            }

            var definitions = new List<Investigation.RimroomsProjectDef>(
                DefDatabase<Investigation.RimroomsProjectDef>.AllDefsListForReading);
            definitions.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));

            var records = new List<ProjectRecord>();
            for (int index = 0; index < definitions.Count; index++)
            {
                Investigation.RimroomsProjectDef definition = definitions[index];
                if (definition == null || string.IsNullOrEmpty(definition.defName)) { continue; }
                bool done = finished.Contains(definition.defName);
                string projectId = branchId + ":project:" + definition.defName;
                records.Add(new ProjectRecord
                {
                    id = projectId,
                    researchDefName = definition.defName,
                    completed = done,
                    // A project that begins finished has had its insight paid for by whoever
                    // ran this branch before you. Leaving it uncommitted would offer the player
                    // a "start" button on work that is already done.
                    insightCommitted = done,
                    // **AND A PAID INSIGHT HAS A RECEIPT.** This field was never set, and
                    // `ValidateRecordRelationships` requires a committed insight to carry one --
                    // so every pre-completed project was a save-integrity fault, `stateFaultKey`
                    // was set during `InitializeBranch` itself, `CanOperate` went false and
                    // **every button in the mod refused.** Owner: *"it says : Company Records
                    // could not be reconsiled ... and none of our buttons work"*.
                    //
                    // Only the corporate start names completed projects -- the other two carry
                    // an empty list -- so it is the only start this ever broke, and it broke it
                    // on turn one, from the day it was written.
                    //
                    // The same format `InvestigationServices` writes when the player commits an
                    // insight, built from the record's own id so the two cannot drift.
                    insightOperationId = done ? projectId + ":insight" : null,
                    workDone = done ? definition.workRequired : 0f,
                });
            }
            return records;
        }

        public CompanyActionResult InitializeBranch(BranchStartRequest request)
        {
            if (!HasSupportedSchema) { return CompanyActionResult.Refused("RR_Company_UnsupportedSave"); }
            if (request == null || string.IsNullOrWhiteSpace(request.ScenarioId) || request.ScenarioVersion < 1)
            {
                return CompanyActionResult.Refused("RR_Company_InvalidStart");
            }
            string receipt = request.ScenarioId + ":v" + request.ScenarioVersion;
            // Accepted before anything else is committed, and never fatal: a rejected
            // name simply leaves the company unnamed until the player renames it.
            TrySetCompanyName(request.CompanyName);
            if (HasBranch)
            {
                return initializationReceipt == receipt && headquarters == request.Headquarters
                    ? CompanyActionResult.Existing() : CompanyActionResult.Refused("RR_Company_AlreadyStarted");
            }
            if (stateFaultKey != null || !string.IsNullOrEmpty(branchId) || ledger.Count != 0 || balanceUsd != 0)
            {
                return CompanyActionResult.Refused("RR_Company_InvalidSave");
            }
            if (request.Headquarters == null || request.Staff == null || request.StaffRoles == null ||
                request.Staff.Count == 0 || request.Staff.Count > 20 || request.Staff.Count != request.StaffRoles.Count ||
                request.InitialFundingUsd < 0 || request.DailyWageUsd < 0 || request.DailyOverheadUsd < 0 ||
                request.SurveyRewardUsd < 0 || request.SurveyBonusUsd < 0 ||
                request.Staff.Distinct().Count() != request.Staff.Count ||
                request.Staff.Any(p => p == null || p.Destroyed || p.Dead || p.Faction != Faction.OfPlayer || p.Map != request.Headquarters) ||
                request.StaffRoles.Any(string.IsNullOrWhiteSpace))
            {
                return CompanyActionResult.Refused("RR_Company_InvalidStart");
            }
            try
            {
                checked
                {
                    long dailyCost = request.DailyWageUsd * request.Staff.Count + request.DailyOverheadUsd;
                    long contractTotal = request.SurveyRewardUsd + request.SurveyBonusUsd;
                    if (dailyCost < 0 || contractTotal < 0) { return CompanyActionResult.Refused("RR_Company_InvalidAmount"); }
                }
            }
            catch (OverflowException) { return CompanyActionResult.Refused("RR_Company_InvalidAmount"); }

            int now = Find.TickManager.TicksGame;
            string newId = "rr-branch-" + Guid.NewGuid().ToString("N");
            var newStaff = new List<StaffRecord>();
            for (int i = 0; i < request.Staff.Count; i++)
            {
                Pawn pawn = request.Staff[i];
                newStaff.Add(new StaffRecord { id = newId + ":staff:" + (i + 1), pawn = pawn,
                    pawnLoadId = pawn.GetUniqueLoadID(), nameAtHire = pawn.LabelShortCap.ToString(),
                    role = request.StaffRoles[i], dailyWageUsd = request.DailyWageUsd, hiredTick = now });
            }
            string coordinateId = newId + ":coordinate:000001";
            var initialCoordinate = new CoordinateRecord { id = coordinateId, label = "AI-01",
                seed = CampaignSeed.Derive(request.CampaignSeed, "coordinate:000001", 1) };
            var initialCase = new CaseRecord { id = newId + ":case:000001", coordinateId = coordinateId,
                titleKey = "RR_Company_InitialCase" };
            var initialContract = new ContractRecord { id = newId + ":contract:000001", templateId = "rr.survey.onboarding.v1",
                titleKey = "RR_Company_InitialContract", coordinateId = coordinateId, status = ContractStatus.Accepted,
                basePaymentUsd = request.SurveyRewardUsd, bonusUsd = request.SurveyBonusUsd, acceptedTick = now };
            List<ProjectRecord> initialProjects = BuildProjectTree(newId, request.CompletedProjects);
            var initialLedger = new List<LedgerEntry>();
            if (request.InitialFundingUsd > 0)
            {
                initialLedger.Add(new LedgerEntry { operationId = newId + ":funding:initial", amountUsd = request.InitialFundingUsd,
                    balanceAfterUsd = request.InitialFundingUsd, reasonKey = "RR_Ledger_InitialFunding", relatedId = receipt, tick = now });
            }

            // Validate/build temporary records above, then commit the branch in one main-thread action.
            branchId = newId;
            scenarioId = request.ScenarioId;
            scenarioVersion = request.ScenarioVersion;
            campaignSeed = request.CampaignSeed;
            initializationReceipt = receipt;
            headquarters = request.Headquarters;
            initializedTick = now;
            balanceUsd = request.InitialFundingUsd;
            dailyOverheadUsd = request.DailyOverheadUsd;
            nextOperatingCostTick = now <= int.MaxValue - GenDate.TicksPerDay ? now + GenDate.TicksPerDay : int.MaxValue;
            staff = newStaff;
            ledger = initialLedger;
            coordinates.Add(initialCoordinate);
            cases.Add(initialCase);
            contracts.Add(initialContract);
            for (int index = 0; index < initialProjects.Count; index++) { projects.Add(initialProjects[index]); }
            // Contact is a state the start declares, not a property of the scenario def:
            // Async Industries opens on the corporation's books, the other two starts do
            // not and have to reach it. Set before validation so a branch is never briefly
            // initialised in a state its start did not ask for.
            corporationContact = request.BeginsInCorporationContact;
            initializationComplete = true;
            ValidateSavedState();
            RecordEvent("RR_Event_BranchStarted", receipt);
            Log.Message("[Rimrooms][Company] Initialized " + branchId + " scenario=" + scenarioId + " seed=" + campaignSeed);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Deterministic branch-local address for a newly discovered space. The id and
        /// seed derive from the branch seed and the caller's stable discovery id, so a
        /// replay returns the existing record instead of inventing a second coordinate.
        /// Generation still happens through the ordinary coordinate owner on first use.
        /// </summary>
        public CompanyActionResult CreateDiscoveredCoordinate(string discoveryId, out CoordinateRecord coordinate)
        { return CreateDiscoveredCoordinate(discoveryId, 1, out coordinate); }

        /// <summary>
        /// The longest discovery id this branch will accept, and **the number that capped the
        /// Backrooms at two levels deep.**
        ///
        /// A coordinate's id embeds its parent's entire id, so a discovery id grows by about
        /// eighty characters per level: 88 for the first step inward, **168 for the second**,
        /// which was refused with `RR_Company_InvalidRequest` -- *"that request is not valid for
        /// this branch"*. So `MaximumNaturalDepth`, the cap the owner designed, was never
        /// reachable, and *"have more natural portals guaranteeed so the backrooms never ends
        /// persay"* could not happen.
        ///
        /// **It is a named constant because its composer has to read it.** A validator and its
        /// caller carrying separate copies of one number is the defect that stopped every
        /// coordinate generating for thirty-nine checkpoints and refused every candidate layout
        /// two checkpoints ago. `NaturalFrontierService` asks this before composing an id, and
        /// shortens the parent rather than being refused.
        /// </summary>
        public const int MaximumDiscoveryIdLength = 128;

        /// <summary>
        /// As above, recording how deep the new space sits. Depth is counted in gates from
        /// the ordinary world and is what the palette and room library read to decide how
        /// strange a coordinate looks.
        /// </summary>
        public CompanyActionResult CreateDiscoveredCoordinate(string discoveryId, int depth, out CoordinateRecord coordinate)
        {
            coordinate = null;
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            if (string.IsNullOrWhiteSpace(discoveryId) ||
                discoveryId.Length > MaximumDiscoveryIdLength ||
                discoveryId.Any(character => char.IsWhiteSpace(character)))
            { return CompanyActionResult.Refused("RR_Company_InvalidRequest"); }
            string stableKey = "coordinate:discovery:" + discoveryId;
            string id = branchId + ":" + stableKey;
            CoordinateRecord existing = coordinates.FirstOrDefault(record => record.id == id);
            if (existing != null)
            {
                coordinate = existing;
                return CompanyActionResult.Existing();
            }
            if (coordinates.Count >= MaximumCoordinates) { return CompanyActionResult.Refused("RR_Company_CoordinateLimit"); }
            var created = new CoordinateRecord
            {
                id = id,
                label = "AI-" + (coordinates.Count + 1).ToString("00"),
                seed = CampaignSeed.Derive(campaignSeed, stableKey, 1),
                depth = depth < 1 ? 1 : depth,
                // Version 2 is what unlocks depth-driven and echoed room shapes. Coordinates
                // discovered before this stay at version 1 and plan exactly as they always did,
                // which is the whole reason this field exists.
                roomLibraryVersion = 2,
                echoedRoomSizes = Generation.ConstructionEchoComponent.SampleColonyRoomSizes()
            };
            coordinates.Add(created);
            ValidateSavedState();
            if (stateFaultKey != null)
            {
                // Never leave the branch in a faulted state because of an added record.
                coordinates.Remove(created);
                ValidateSavedState();
                return CompanyActionResult.Refused("RR_Company_InvalidSave");
            }
            coordinate = created;
            RecordEvent("RR_Event_CoordinateDiscovered", id, discoveryId);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Record that the company was renamed. Called after the game's own rename dialog
        /// has already applied the new name through the renameable setter.
        /// </summary>
        internal void NoteRenamed()
        {
            if (!CanOperate) { return; }
            RecordEvent("RR_Event_CompanyRenamed", branchId, CompanyName);
        }

        // RenameCompany was retired in 0.12.32-dev, by the wiring checker that found it had no
        // caller. It was not a missing feature -- it was a SECOND path to a change that already
        // works. `Dialog_RenameCompany` uses Core's `Dialog_Rename<T>`, whose accept sets
        // `RenamableLabel`, whose setter calls the same `TrySetCompanyName`; and its `OnRenamed`
        // calls `NoteRenamed()`, which records the same RR_Event_CompanyRenamed event. Identical
        // validation, identical record, one of them unreachable.
        //
        // Two entry points to one state change is how two validations drift apart, and the one
        // nobody uses is the one that drifts without anybody noticing.

        /// <summary>
        /// Whether this branch owns a loaded map: its headquarters, or a destination
        /// site held by one of its own coordinate records. This is the canonical
        /// answer. It is deliberately strict about a map that is no longer loaded,
        /// because a stale reference must never read as ownership.
        /// </summary>
        public bool OwnsMap(Map map)
        {
            if (map == null || !Find.Maps.Contains(map)) { return false; }
            if (headquarters == map) { return true; }
            RimroomsDestinationMapParent site = map.Parent as RimroomsDestinationMapParent;
            if (site != null)
            {
                return coordinates.Any(record => record != null &&
                    record.site == site && record.id == site.CoordinateId);
            }
            // Arc 5's third clause. A registered site is the branch's own place, so connected
            // work reaches it, a gate may anchor there and a way out may come up on it -- which
            // is *"people, supplies, signals, protection, and an exit plan"* stated as one
            // predicate rather than five features. A coordinate is checked above and returns
            // there either way, because a destination is never a base.
            return IsRegisteredRemoteSite(map);
        }

        internal CompanyActionResult PostTransaction(string operationId, long amountUsd, string reasonKey, string relatedId)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            if (string.IsNullOrWhiteSpace(operationId) || string.IsNullOrWhiteSpace(reasonKey) || amountUsd == 0)
            {
                return CompanyActionResult.Refused("RR_Company_InvalidAmount");
            }
            LedgerEntry existing;
            if (ledgerIndex.TryGetValue(operationId, out existing))
            {
                return existing.amountUsd == amountUsd && existing.reasonKey == reasonKey && existing.relatedId == relatedId
                    ? CompanyActionResult.Existing() : CompanyActionResult.Refused("RR_Company_ReceiptMismatch");
            }
            long nextBalance;
            try { nextBalance = checked(balanceUsd + amountUsd); }
            catch (OverflowException) { return CompanyActionResult.Refused("RR_Company_InvalidAmount"); }
            if (nextBalance < 0) { return CompanyActionResult.Refused("RR_Company_InsufficientFunds"); }
            var entry = new LedgerEntry { operationId = operationId, amountUsd = amountUsd, balanceAfterUsd = nextBalance,
                reasonKey = reasonKey, relatedId = relatedId, tick = Find.TickManager.TicksGame };
            ledger.Add(entry);
            ledgerIndex.Add(operationId, entry);
            balanceUsd = nextBalance;
            return CompanyActionResult.Applied();
        }

        public CompanyActionResult PayOutstandingObligations()
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            foreach (CompanyObligation obligation in obligations)
            {
                if (obligation.paid) { continue; }
                CompanyActionResult result = PostTransaction(obligation.id + ":payment", -obligation.amountUsd, obligation.reasonKey, obligation.id);
                if (!result.Success) { return result; }
                obligation.paid = true;
            }
            return CompanyActionResult.Applied();
        }

        public override void GameComponentTick()
        {
            using (Core.RimroomsDiagnostics.Measure("company-tick")) { TickCompany(); }
        }

        private void TickCompany()
        {
            if (!CanOperate) { return; }
            int now = Find.TickManager.TicksGame;
            if (now % 60 == 0) { UpdateEvidenceAndContracts(); }
            // Odd-supply demand rides the same cadence. Offering is interval-gated inside,
            // so this is a counter comparison almost every time it runs.
            if (now % 60 == 0) { UpdateOddSupplyContracts(); }
            // Consignment missions ride it too. Their own interval is three days rather
            // than one and their cap is one rather than three, both gated inside.
            if (now % 60 == 0) { UpdateOddConsignmentMissions(); }
            // The containment procedure. Same cadence as the clean-up team and for the same
            // reason: it has to land inside the window where a response still means something,
            // and it is cheap -- a latched bool, then a holder list that is built at most once
            // per tick and is empty on any branch holding nothing.
            if (now % 60 == 15) { ContainmentProtocol.TickProcedure(this); }
            // **The two research routes, kept in step.** Owner: *"Two genuine routes,
            // either works"*, so whichever one finishes, the other has to agree. Every
            // four seconds rather than every tick: it is a boolean comparison per project
            // and nobody can perceive four seconds against a project that took hours.
            if (now % MirrorInterval == 45) { SyncResearchMirror(); }
            // The clean-up team. Checked often enough to land inside Core's 400-tick
            // game-over countdown, and cheap: a bool, then a scan that stops at the
            // first living employee.
            if (now % 60 == 30) { TickFacilityRelief(); }
            // Offset from the relief so the two map scans never land together.
            if (now % 60 == 45) { TickRecordBookDelivery(); }
            // The mission line. Offered on contact, completed when a route comes true. Slow on
            // purpose: every check it runs is a scan, and no route in this mod can be satisfied
            // and un-satisfied inside four seconds.
            if (now % 240 == 90) { TickRequestLine(); }
            // The solo/group start has no request line, so this is the only guidance it
            // gets. Slow: these are thoughts, not business, and they fire once each.
            if (now % 250 == 125) { TickSoloGroupHints(); }
            if (now % 250 != 0 || now < nextOperatingCostTick || nextOperatingCostTick == int.MaxValue) { return; }
            // Bound catch-up work after a time jump; unpaid obligations remain explicit records.
            int days = 0;
            while (now >= nextOperatingCostTick && nextOperatingCostTick != int.MaxValue && days++ < 4)
            {
                string dayId = branchId + ":operation-day:" + nextOperatingCostTick;
                long wages = 0;
                try
                {
                    foreach (StaffRecord member in staff)
                    {
                        // A catch-up invoice must not bill a new arrival for cutoffs before its hire.
                        if (member.employed && member.hiredTick < nextOperatingCostTick && member.pawn != null && !member.pawn.Dead && !member.pawn.Destroyed)
                        {
                            wages = checked(wages + member.dailyWageUsd);
                        }
                    }
                }
                catch (OverflowException)
                {
                    stateFaultKey = "RR_Company_InvalidSave";
                    return;
                }
                AddObligation(dayId + ":payroll", "RR_Ledger_Payroll", wages, nextOperatingCostTick);
                AddObligation(dayId + ":overhead", "RR_Ledger_Overhead", dailyOverheadUsd, nextOperatingCostTick);
                // Arc 5: *"a remote base is a costly responsibility rather than free map
                // ownership"*. Its own obligation rather than folded into overhead, so the
                // player can see on the ledger what the places are costing them and decide
                // whether to keep them. Zero for a branch holding none, which is every branch
                // until somebody registers one.
                AddObligation(dayId + ":sites", "RR_Ledger_RemoteSites",
                    DailyRemoteSiteOverheadUsd, nextOperatingCostTick);
                // **Containment, on its own line for the same reason the sites are.** Owner:
                // *"Make ... contain/release ... choices visible with financial ...
                // consequences"*. A branch that contains everything it finds should be able to
                // watch itself going broke on the ledger and know exactly which line is doing
                // it. Zero until somebody decides to contain something.
                AddContainmentObligation(dayId, nextOperatingCostTick);
                nextOperatingCostTick = nextOperatingCostTick <= int.MaxValue - GenDate.TicksPerDay
                    ? nextOperatingCostTick + GenDate.TicksPerDay : int.MaxValue;
            }
            CompanyActionResult payment = PayOutstandingObligations();
            if (!payment.Success)
            {
                RecordEvent("RR_Event_OperatingArrears", branchId);
                // **Eviction, and it is a consequence rather than a clock.** §1.1 permits the
                // gate's window because it is *"the consequence of things the player controls"*;
                // this is built to the same test. A place goes only because the branch stopped
                // paying for it, the unpaid bill is on the ledger where the player can read it,
                // and paying clears it. **No time passing ever evicts anybody** -- a branch that
                // keeps paying keeps its places for ever.
                //
                // One per operating day, so a cash-flow problem never becomes a
                // campaign-ending event with no step in between. See `RemoteSiteTenure` for why
                // *term* is refused outright rather than built smaller.
                EvictOnePlace();
            }
        }

        private void AddObligation(string id, string reasonKey, long amount, int dueTick)
        {
            if (amount <= 0 || obligations.Any(o => o.id == id)) { return; }
            obligations.Add(new CompanyObligation { id = id, reasonKey = reasonKey, amountUsd = amount, dueTick = dueTick });
        }

        internal void RecordEvent(string messageKey, string relatedId, params string[] arguments)
        {
            events.Add(new CompanyEventRecord { tick = Find.TickManager.TicksGame, messageKey = messageKey,
                relatedId = relatedId, arguments = new List<string>(arguments ?? new string[0]) });
            // This is the recent activity feed. Ledger/case/contract history is retained separately.
            if (events.Count > 256) { events.RemoveRange(0, events.Count - 256); }
        }
    }
}
