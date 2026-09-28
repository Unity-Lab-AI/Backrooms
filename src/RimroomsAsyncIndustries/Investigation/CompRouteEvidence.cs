using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class CompProperties_RouteEvidence : CompProperties
    {
        public float analysisWorkRequired = 3000f;
        public CompProperties_RouteEvidence() { compClass = typeof(CompRouteEvidence); }
        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
            if (parentDef.stackLimit != 1) { yield return "Unique route evidence must have stackLimit 1."; }
            if (analysisWorkRequired <= 0f || float.IsNaN(analysisWorkRequired) || float.IsInfinity(analysisWorkRequired))
            { yield return "analysisWorkRequired must be finite and positive."; }
        }
    }

    public sealed class CompRouteEvidence : ThingComp
    {
        private string evidenceId;
        public string EvidenceId { get { return evidenceId; } }
        public float WorkRequired { get { return ((CompProperties_RouteEvidence)props).analysisWorkRequired; } }
        public bool Initialize(string id)
        {
            if (string.IsNullOrWhiteSpace(id) || (!string.IsNullOrEmpty(evidenceId) && evidenceId != id)) { return false; }
            evidenceId = id;
            return true;
        }
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref evidenceId, "rr_evidenceId");
        }
        public override string CompInspectStringExtra()
        {
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            EvidenceRecord record = campaign == null ? null : campaign.FindEvidence(evidenceId);
            return record == null ? "RR_Evidence_Unregistered".Translate().ToString()
                : "RR_Evidence_Inspect".Translate(("RR_EvidenceStatus_" + record.Status).Translate(),
                    (record.AnalysisWork / WorkRequired).ToString("P0")).ToString();
        }
        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption option in base.CompFloatMenuOptions(selPawn)) { yield return option; }
            if (selPawn == null || selPawn.Faction != Faction.OfPlayer || !parent.Spawned || selPawn.Map != parent.Map) { yield break; }
            yield return new FloatMenuOption("RR_UI_RecoverEvidence".Translate(selPawn.LabelShortCap), delegate
            {
                CompanyActionResult result = ExpeditionCargo.QueuePickup(selPawn, parent, 1);
                if (!result.Success) { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
            });
        }
    }
}
