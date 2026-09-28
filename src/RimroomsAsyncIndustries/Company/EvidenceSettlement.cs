using System.Linq;
using RimroomsAsyncIndustries.Expedition;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed partial class RimroomsCampaignComponent
    {
        private bool HasSecuredEvidenceCase(EvidenceRecord record)
        {
            ExpeditionRecord source = Current.Game.GetComponent<RimroomsExpeditionComponent>().Records
                .FirstOrDefault(r => r.ExpeditionId == record.sourceExpeditionId);
            return source != null && source.Cargo.Any(c => c.Item != null && !c.Item.Destroyed &&
                c.Item.def.defName == "RR_SealedEvidenceCase" && c.Item.MapHeld == headquarters);
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
                    HasSecuredEvidenceCase(record))
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
