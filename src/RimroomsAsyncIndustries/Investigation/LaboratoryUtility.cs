using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Investigation
{
    internal static class LaboratoryUtility
    {
        internal static bool CanWork(Pawn pawn, Thing bench, RimroomsCampaignComponent campaign, int minimumSkill)
        {
            return campaign != null && campaign.CanOperate && pawn != null && !pawn.Dead && !pawn.Downed && pawn.Spawned &&
                pawn.Faction == Faction.OfPlayer && pawn.Map == campaign.Headquarters && pawn.skills != null &&
                !pawn.WorkTagIsDisabled(WorkTags.Intellectual) && !pawn.skills.GetSkill(SkillDefOf.Intellectual).TotallyDisabled &&
                pawn.skills.GetSkill(SkillDefOf.Intellectual).Level >= minimumSkill && bench != null && bench.Spawned &&
                bench.Map == pawn.Map && bench.Faction == Faction.OfPlayer && bench.def.defName == "RR_FieldAnalysisBench" &&
                !bench.IsForbidden(pawn) && bench.TryGetComp<CompPowerTrader>()?.PowerOn == true;
        }
        internal static bool IsAtBench(Pawn pawn, Thing bench)
        { return pawn != null && bench != null && pawn.Spawned && bench.Spawned && pawn.Map == bench.Map && pawn.Position == bench.InteractionCell; }
    }
}
