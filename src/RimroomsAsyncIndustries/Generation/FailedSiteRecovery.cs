using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Generation;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed partial class RimroomsCampaignComponent
    {
        private const string InitialSurveyTemplateId = "rr.survey.onboarding.v1";
        private const string InitialSurveyTitleKey = "RR_Company_InitialContract";
        private const string InitialCaseTitleKey = "RR_Company_InitialCase";
        private const string FailedSiteReplacementSuffix = ":fallback:1";

        private static readonly HashSet<string> ReplaceableGenerationFailures = new HashSet<string>(StringComparer.Ordinal)
        {
            "RR_Generation_ContentPlacementFailed",
            "RR_Generation_NoSafeRoomCell",
            "RR_Generation_NoReturnAnchorCell",
            "RR_Generation_NoReturnCell",
            "RR_Generation_UnreachableRoom",
            "RR_Generation_UnreachableRequiredCell",
            "RR_Generation_InvalidStartOrObjectiveCell",
            "RR_Generation_NonAdjacentRooms",
            "RR_Generation_CorridorOutOfBounds",
            "RR_Generation_WallOutOfBounds",
            "RR_Generation_WallOverlap"
        };

        /// <summary>
        /// Readdress the unresolved initial AI-01 survey once after a pristine, allowlisted
        /// geometry/content-placement failure. The old world object and map are never removed or edited.
        /// </summary>
        public CompanyActionResult ReaddressPristineInitialSurvey(string failedCoordinateId)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(StateFaultKey ?? "RR_Company_Inactive"); }
            if (scenarioId != "async_industries" || string.IsNullOrWhiteSpace(failedCoordinateId))
            { return CompanyActionResult.Refused("RR_Generation_ReaddressFailureNotEligible"); }

            List<CoordinateRecord> failedMatches = coordinates.Where(c => c != null && c.id == failedCoordinateId).ToList();
            if (failedMatches.Count != 1) { return CompanyActionResult.Refused("RR_Generation_ReaddressFailureNotEligible"); }
            CoordinateRecord failed = failedMatches[0];
            string receipt = failed.id + FailedSiteReplacementSuffix;

            List<ContractRecord> initialContracts = contracts.Where(c => c != null && c.templateId == InitialSurveyTemplateId &&
                c.titleKey == InitialSurveyTitleKey).ToList();
            List<CaseRecord> initialCases = cases.Where(c => c != null && c.titleKey == InitialCaseTitleKey).ToList();
            if (initialContracts.Count != 1 || initialCases.Count != 1)
            { return CompanyActionResult.Refused("RR_Generation_ReaddressFailureNotEligible"); }
            ContractRecord contract = initialContracts[0];
            CaseRecord caseRecord = initialCases[0];

            List<CoordinateRecord> replacementMatches = coordinates.Where(c => c != null && c.id == receipt).ToList();
            if (replacementMatches.Count > 1) { return CompanyActionResult.Refused("RR_Generation_ReaddressReplacementExistsMismatch"); }
            if (replacementMatches.Count == 1)
            {
                return IsExistingReplacement(failed, replacementMatches[0], contract, caseRecord, receipt)
                    ? CompanyActionResult.Existing()
                    : CompanyActionResult.Refused("RR_Generation_ReaddressReplacementExistsMismatch");
            }

            if (coordinates.Count != 1 || Find.WorldObjects.AllWorldObjects.OfType<RimroomsDestinationMapParent>().Count() >= 2)
            { return CompanyActionResult.Refused("RR_Generation_ReaddressSiteCapReached"); }

            if (!IsInitialSurveyUnsettled(failed, contract, caseRecord))
            { return CompanyActionResult.Refused("RR_Generation_ReaddressFailureNotEligible"); }

            RimroomsDestinationMapParent failedSite;
            Map failedMap;
            if (!TryGetReplaceableFailedSite(failed, out failedSite, out failedMap))
            {
                return ClassifyUnavailableFailedSite(failed);
            }

            if (!RequiredRecoveryContentAvailable())
            { return CompanyActionResult.Refused("RR_Generation_ReaddressContentRestore"); }

            if (!IsFailedSitePristine(failed, failedSite, failedMap, caseRecord))
            { return CompanyActionResult.Refused("RR_Generation_ReaddressSiteNotPristine"); }

            var replacement = new CoordinateRecord
            {
                id = receipt,
                label = "AI-01R",
                seed = CampaignSeed.Derive(campaignSeed, receipt, 1),
                generatorVersion = failed.generatorVersion,
                roomLibraryVersion = failed.roomLibraryVersion,
                status = CoordinateStatus.Discovered,
                rooms = new List<RoomRecord>()
            };
            if (!RoomLayoutPlanner.TryBuildSafeFallback(replacement, out List<RoomRecord> fallbackRooms))
            { return CompanyActionResult.Refused("RR_Generation_ReaddressFallbackInvalid"); }

            // Commit only after every eligibility, custody, content and geometry check has passed.
            replacement.rooms = fallbackRooms;
            failed.status = CoordinateStatus.Unavailable;
            coordinates.Add(replacement);
            contract.coordinateId = replacement.id;
            caseRecord.coordinateId = replacement.id;
            RecordEvent("RR_Event_SiteReaddressed", receipt, failed.id, replacement.id);
            return CompanyActionResult.Applied();
        }

        private bool IsInitialSurveyUnsettled(CoordinateRecord failed, ContractRecord contract, CaseRecord caseRecord)
        {
            if (failed == null || contract == null || caseRecord == null || contract.coordinateId != failed.id ||
                caseRecord.coordinateId != failed.id || contract.status != ContractStatus.Accepted ||
                contract.completedTick >= 0 || !string.IsNullOrEmpty(contract.settlementOperationId) || caseRecord.closed ||
                caseRecord.evidenceIds == null || caseRecord.evidenceIds.Count != 0 ||
                contracts.Any(c => c != null && c != contract && c.coordinateId == failed.id) ||
                cases.Any(c => c != caseRecord && c != null && c.coordinateId == failed.id) ||
                evidence.Any(e => e != null && (e.coordinateId == failed.id || e.caseId == caseRecord.id)))
            { return false; }

            return !ledger.Any(entry => entry != null && (entry.relatedId == contract.id ||
                entry.operationId == contract.id + ":survey-payment" || entry.operationId == contract.id + ":survey-bonus"));
        }

        private static bool TryGetReplaceableFailedSite(CoordinateRecord failed,
            out RimroomsDestinationMapParent parent, out Map map)
        {
            parent = failed == null ? null : failed.site as RimroomsDestinationMapParent;
            map = null;
            if (failed == null || failed.status != CoordinateStatus.Unavailable || parent == null ||
                parent.def == null || parent.def.defName != "RR_BackroomsSite" || parent.CoordinateId != failed.id ||
                !Find.WorldObjects.Contains(parent) || !parent.GenerationAttempted || parent.LayoutReady ||
                string.IsNullOrWhiteSpace(parent.GenerationFailureKey) ||
                !ReplaceableGenerationFailures.Contains(parent.GenerationFailureKey) || !parent.HasMap)
            { return false; }

            map = parent.Map;
            return map != null && map.Parent == parent && Find.Maps.Contains(map);
        }

        private static CompanyActionResult ClassifyUnavailableFailedSite(CoordinateRecord failed)
        {
            RimroomsDestinationMapParent parent = failed == null ? null : failed.site as RimroomsDestinationMapParent;
            if (parent == null || !parent.GenerationAttempted || parent.LayoutReady)
            { return CompanyActionResult.Refused("RR_Generation_ReaddressFailureNotEligible"); }

            // Only explicitly allowlisted geometry/content-placement failures with all required
            // Defs present may use a replacement coordinate. Unknown, missing-Def, and source
            // failures require package/source diagnosis; retrying at a new seed cannot repair them.
            return CompanyActionResult.Refused("RR_Generation_ReaddressContentRestore");
        }

        private bool IsFailedSitePristine(CoordinateRecord failed, RimroomsDestinationMapParent parent,
            Map map, CaseRecord initialCase)
        {
            if (failed == null || parent == null || map == null || initialCase == null ||
                failed.rooms == null || failed.rooms.Any(room => room == null || room.surveyed) ||
                !Find.WorldObjects.Contains(parent) || !Find.Maps.Contains(map) ||
                map.listerThings == null || map.listerThings.AllThings == null)
            { return false; }

            RimroomsExpeditionComponent expeditions = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsExpeditionComponent>();
            RimroomsEvidenceCreationComponent creation = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsEvidenceCreationComponent>();
            if (creation == null || creation.FaultKey != null || creation.Attempts.Count != 0) { return false; }
            if (expeditions == null || expeditions.Records.Any(run => run == null ||
                run.CoordinateId == failed.id || run.Destination == map))
            { return false; }

            HashSet<string> failedExpeditionIds = new HashSet<string>(StringComparer.Ordinal);
            foreach (ExpeditionRecord run in expeditions.Records.Where(run => run != null && run.CoordinateId == failed.id))
            { failedExpeditionIds.Add(run.ExpeditionId); }
            if (expeditions.InterruptedTransfers.Any(transfer => transfer == null || transfer.Source == map ||
                (transfer.Pawn != null && PawnOrCorpseHeldMap(transfer.Pawn) == map) ||
                failedExpeditionIds.Contains(transfer.expeditionId)))
            { return false; }

            if (failed.rooms.Any(room => room == null || room.surveyed) || initialCase.evidenceIds.Count != 0 ||
                evidence.Any(record => record != null && (record.CoordinateId == failed.id || record.caseId == initialCase.id)) ||
                map.listerThings.AllThings.Any(thing => thing == null || thing is Pawn || thing is Corpse))
            { return false; }

            foreach (Pawn pawn in Find.WorldPawns.AllPawnsAliveOrDead)
            {
                if (pawn == null) { return false; }
                if (PawnOrCorpseHeldMap(pawn) == map) { return false; }
            }

            var holderVisits = new HashSet<IThingHolder>();
            foreach (Thing thing in map.listerThings.AllThings)
            {
                if (ThingHolderContainsPawnOrCorpse(thing as IThingHolder, holderVisits)) { return false; }
            }

            // A failed initial site must not leave any evidence item, registered or loose, that
            // could be rebound to the replacement. The scan covers maps, world pawns, world-object
            // holders and the expedition recovery holder; uncertainty fails closed.
            return !AnyPhysicalRouteRecording(expeditions);
        }

        private static Map PawnOrCorpseHeldMap(Pawn pawn)
        {
            return pawn == null ? null : pawn.Dead ? pawn.Corpse?.MapHeld : pawn.MapHeld;
        }

        private static bool ThingHolderContainsPawnOrCorpse(IThingHolder holder, HashSet<IThingHolder> visited)
        {
            if (holder == null || !visited.Add(holder)) { return false; }
            try
            {
                ThingOwner owner = holder.GetDirectlyHeldThings();
                if (owner != null)
                {
                    foreach (Thing thing in owner)
                    {
                        if (thing is Pawn || thing is Corpse) { return true; }
                        if (thing is IThingHolder child && ThingHolderContainsPawnOrCorpse(child, visited)) { return true; }
                    }
                }
                var children = new List<IThingHolder>();
                holder.GetChildHolders(children);
                return children.Any(child => ThingHolderContainsPawnOrCorpse(child, visited));
            }
            catch (Exception)
            {
                return true;
            }
        }

        private static bool AnyPhysicalRouteRecording(RimroomsExpeditionComponent expeditions)
        {
            try
            {
                if (Find.Maps == null || Find.WorldPawns == null || Find.WorldObjects == null) { return true; }
                var visited = new HashSet<IThingHolder>();
                foreach (Map map in Find.Maps)
                {
                    if (map == null || map.listerThings == null) { return true; }
                    foreach (Thing thing in map.listerThings.AllThings)
                    { if (ThingOrHolderContainsRouteRecording(thing, visited)) { return true; } }
                }
                foreach (Pawn pawn in Find.WorldPawns.AllPawnsAliveOrDead)
                { if (pawn == null || ThingHolderContainsRouteRecording(pawn, visited)) { return true; } }
                foreach (IThingHolder holder in Find.WorldObjects.AllWorldObjects.OfType<IThingHolder>())
                { if (ThingHolderContainsRouteRecording(holder, visited)) { return true; } }
                RimroomsEvidenceCreationComponent creation = Current.Game.GetComponent<RimroomsEvidenceCreationComponent>();
                if (creation == null || ThingHolderContainsRouteRecording(creation, visited)) { return true; }
                return expeditions == null || ThingHolderContainsRouteRecording(expeditions, visited);
            }
            catch (Exception)
            {
                return true;
            }
        }

        private static bool ThingOrHolderContainsRouteRecording(Thing thing, HashSet<IThingHolder> visited)
        {
            if (thing == null) { return true; }
            if (CompRouteEvidence.IsEvidenceCarrierPresence(thing)) { return true; }
            return ThingHolderContainsRouteRecording(thing as IThingHolder, visited);
        }

        private static bool ThingHolderContainsRouteRecording(IThingHolder holder, HashSet<IThingHolder> visited)
        {
            if (holder == null || !visited.Add(holder)) { return false; }
            try
            {
                ThingOwner owner = holder.GetDirectlyHeldThings();
                if (owner != null)
                {
                    foreach (Thing thing in owner)
                    { if (ThingOrHolderContainsRouteRecording(thing, visited)) { return true; } }
                }
                var children = new List<IThingHolder>();
                holder.GetChildHolders(children);
                return children.Any(child => ThingHolderContainsRouteRecording(child, visited));
            }
            catch (Exception)
            {
                return true;
            }
        }

        private static bool RequiredRecoveryContentAvailable()
        {
            string[] siteThings =
            {
                "ChemfuelPoweredGenerator", "Chemfuel", "HiddenConduit",
                "SimpleResearchBench", "RR_FieldRecorder", "GlowPod",
                "RR_SealedEvidenceCase", "TextBook", "RR_QuietPursuer",
                "Door", "Autodoor", "CommsConsole", "TableMachining", "Battery", "WoodFiredGenerator",
                "Stool", "Table1x2c", "DiningChair", "PlantPot", "Shelf", "StandingLamp", "Heater"
            };
            string[] siteTerrains = { "Concrete", "WaterDeep", "MetalTile", "PavedTile" };
            return DefDatabase<WorldObjectDef>.GetNamedSilentFail("RR_BackroomsSite") != null &&
                DefDatabase<MapGeneratorDef>.GetNamedSilentFail("RR_BackroomsGeneration") != null &&
                DefDatabase<GenStepDef>.GetNamedSilentFail("RR_BackroomsLayout") != null &&
                ThingDefOf.Wall != null && ThingDefOf.Steel != null && CompRouteEvidence.NativeCarrierDef != null &&
                siteThings.All(name => DefDatabase<ThingDef>.GetNamedSilentFail(name) != null) &&
                siteTerrains.All(name => DefDatabase<TerrainDef>.GetNamedSilentFail(name) != null);
        }

        private bool IsExistingReplacement(CoordinateRecord failed, CoordinateRecord replacement,
            ContractRecord contract, CaseRecord caseRecord, string receipt)
        {
            if (!TryGetReplaceableFailedSite(failed, out _, out _)) { return false; }
            if (failed == null || replacement == null || contract == null || caseRecord == null ||
                failed.status != CoordinateStatus.Unavailable || replacement.id != receipt ||
                replacement.label != "AI-01R" || replacement.seed != CampaignSeed.Derive(campaignSeed, receipt, 1) ||
                !Enum.IsDefined(typeof(CoordinateStatus), replacement.status) ||
                (replacement.status == CoordinateStatus.Ready && replacement.site == null) ||
                replacement.generatorVersion != failed.generatorVersion ||
                replacement.roomLibraryVersion != failed.roomLibraryVersion ||
                contract.coordinateId != replacement.id || caseRecord.coordinateId != replacement.id ||
                contracts.Any(c => c != null && c != contract && c.coordinateId == failed.id) ||
                cases.Any(c => c != null && c != caseRecord && c.coordinateId == failed.id) ||
                evidence.Any(e => e != null && e.coordinateId == failed.id))
            { return false; }

            if (replacement.site != null)
            {
                RimroomsDestinationMapParent owner = replacement.site as RimroomsDestinationMapParent;
                if (owner == null || owner.def == null || owner.def.defName != "RR_BackroomsSite" ||
                    owner.CoordinateId != replacement.id || !Find.WorldObjects.Contains(owner) ||
                    (owner.HasMap && (owner.Map == null || owner.Map.Parent != owner || !Find.Maps.Contains(owner.Map))))
                { return false; }
            }

            var expected = new CoordinateRecord { id = receipt, label = "AI-01R", seed = replacement.seed,
                generatorVersion = replacement.generatorVersion, roomLibraryVersion = replacement.roomLibraryVersion };
            if (!RoomLayoutPlanner.TryBuildSafeFallback(expected, out List<RoomRecord> expectedRooms) ||
                replacement.rooms == null || expectedRooms.Count != replacement.rooms.Count ||
                replacement.rooms.Any(room => room == null || room.links == null))
            { return false; }
            return expectedRooms.All(a => replacement.rooms.Any(b => b != null && a.index == b.index &&
                a.familyId == b.familyId && a.x == b.x && a.z == b.z && a.width == b.width && a.height == b.height &&
                a.links.OrderBy(i => i).SequenceEqual(b.links.OrderBy(i => i))));
        }
    }
}
