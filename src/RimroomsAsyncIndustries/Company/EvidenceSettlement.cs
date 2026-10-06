using System.Linq;
using RimroomsAsyncIndustries.Expedition;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Whether a record's book is in the branch's custody: **stored on a shelf linked to a
        /// gate as a records archive**.
        ///
        /// This used to ask whether the expedition that produced the record still had a
        /// `RR_SealedEvidenceCase` at headquarters. That was custody-by-receipt: the case was a
        /// custom item whose only job was to exist somewhere on the map, and it did not matter
        /// where the book itself had been put. Owner direction was *"things needed to be on
        /// shelves/records that computers and workbenches need to connect to"*, so custody is now
        /// **a place the book is**, which a player can see, reorganise and lose.
        ///
        /// The archive is a role in the gate's equipment links built in 0.10.8-dev, so a facility
        /// with several gates has several archives and a record is in custody when it reaches any
        /// of them. Not restricted to the gate that produced the record: the corporation cares
        /// that the paperwork is filed, not which door it came through.
        /// </summary>
        private bool HasArchivedCustody(EvidenceRecord record)
        {
            return record != null && HasArchivedCustody(record.item);
        }

        /// <summary>
        /// The same question asked of a thing rather than of a record.
        ///
        /// **Extracted so there is one derivation and not two.** The quest paperwork needs to know
        /// whether a *quest book* is filed, and a quest book is not an `EvidenceRecord` — it is a
        /// company-issued book stamped for a request. Writing a second custody test for it would
        /// have been *"two derivations of one rule"*, and the two would have drifted the first time
        /// somebody changed what an archive is.
        ///
        /// So the rule stays exactly where it was and both callers ask it: stored in a thing that
        /// this gate links in the `RR_Link_Archive` role, read through Core's own `StoringThing()`
        /// so a modded shelf counts and a vanilla one still works.
        /// </summary>
        internal bool HasArchivedCustody(Thing item)
        {
            if (item == null || item.Destroyed) { return false; }
            Thing store = item.StoringThing();
            if (store == null || store.Map != headquarters) { return false; }
            foreach (Building building in headquarters.listerBuildings.allBuildingsColonist)
            {
                Gate.CompRimroomsGate gate = building.TryGetComp<Gate.CompRimroomsGate>();
                if (gate == null || !gate.IsDesignated) { continue; }
                foreach (Thing linked in gate.LinkedEquipment)
                {
                    if (linked != store) { continue; }
                    Gate.RimroomsGateEquipmentDef role = Gate.RimroomsGateEquipmentDef.RoleFor(linked);
                    if (role != null && role.defName == "RR_Link_Archive") { return true; }
                }
            }
            return false;
        }

        private void UpdateEvidenceAndContracts()
        {
            RimroomsExpeditionComponent trips = Current.Game.GetComponent<RimroomsExpeditionComponent>();
            foreach (EvidenceRecord record in evidence)
            {
                if (record.item == null || record.item.Destroyed)
                {
                    if (record.analyzedTick < 0) { record.status = EvidenceStatus.Missing; }
                    if (record.analyzedTick < 0) { continue; }
                }
                ExpeditionRecord source = string.IsNullOrEmpty(record.sourceExpeditionId) ? null : trips.Records.FirstOrDefault(r => r.ExpeditionId == record.sourceExpeditionId);
                if (source == null)
                {
                    source = record.item == null ? null : trips.Records.FirstOrDefault(r => r.CoordinateId == record.coordinateId && r.Cargo.Any(c => c.Item == record.item));
                    if (source == null) { continue; }
                    record.sourceExpeditionId = source.ExpeditionId;
                    if (record.analyzedTick < 0) { record.status = EvidenceStatus.Recovered; }
                }
                if (record.analyzedTick < 0 && record.item != null && !record.item.Destroyed && record.item.MapHeld == headquarters &&
                    HasArchivedCustody(record))
                {
                    if (record.status != EvidenceStatus.Secured)
                    { RecordEvent("RR_Event_EvidenceSecured", record.id); }
                    record.status = EvidenceStatus.Secured;
                }
                else if (record.analyzedTick < 0 && record.status == EvidenceStatus.Secured)
                { record.status = EvidenceStatus.Recovered; }
                if (record.analyzedTick < 0 || !record.routeRecorded || !record.distortionRecorded) { continue; }
                foreach (ContractRecord contract in contracts.Where(c => c.coordinateId == record.coordinateId &&
                    c.templateId == "rr.survey.onboarding.v1" && (c.status == ContractStatus.Accepted || c.status == ContractStatus.Completed)))
                {
                    string operationId = contract.id + ":survey-payment";
                    if (contract.status == ContractStatus.Accepted)
                    {
                        CompanyActionResult result = contract.basePaymentUsd == 0 ? CompanyActionResult.Applied()
                            : PostTransaction(operationId, contract.basePaymentUsd, "RR_Ledger_SurveyPayment", contract.id);
                        if (!result.Success) { continue; }
                        contract.settlementOperationId = operationId;
                        contract.completedTick = Find.TickManager.TicksGame;
                        contract.status = ContractStatus.Completed;
                        CaseRecord linkedCase = cases.FirstOrDefault(c => c.id == record.caseId);
                        if (linkedCase != null) { linkedCase.closed = true; }
                        RecordEvent("RR_Event_SurveySettled", contract.id, contract.basePaymentUsd.ToString("N0"));
                    }
                    bool allReturned = source.InitialCrew.Count == 3 && source.InitialCrew.All(p => p != null && source.ReturnedCrew.Contains(p));
                    if (record.entityRecorded && allReturned && contract.bonusUsd > 0)
                    {
                        CompanyActionResult bonus = PostTransaction(contract.id + ":survey-bonus", contract.bonusUsd, "RR_Ledger_SurveyBonus", contract.id);
                        if (bonus.Success && !bonus.AlreadyApplied) { RecordEvent("RR_Event_SurveyBonus", contract.id, contract.bonusUsd.ToString("N0")); }
                    }
                }
            }
        }
    }
}
