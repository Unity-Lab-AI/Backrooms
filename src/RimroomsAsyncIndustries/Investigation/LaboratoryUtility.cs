using System.Linq;
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
            if (campaign == null || !campaign.CanOperate || pawn == null || pawn.Destroyed || pawn.Dead || pawn.Downed ||
                !pawn.Spawned || pawn.InMentalState || pawn.IsPrisoner || pawn.IsSlave || pawn.Faction != Faction.OfPlayer ||
                pawn.Map != campaign.Headquarters || pawn.skills == null || pawn.WorkTagIsDisabled(WorkTags.Intellectual)) { return false; }
            SkillRecord intellectual = pawn.skills.skills.FirstOrDefault(s => s.def == SkillDefOf.Intellectual);
            if (intellectual == null || intellectual.TotallyDisabled || intellectual.Level < minimumSkill) { return false; }
            RimroomsLaboratoryComponent laboratory = Current.Game == null ? null : Current.Game.GetComponent<RimroomsLaboratoryComponent>();
            return laboratory != null && laboratory.IsReadyBench(bench, campaign) && bench.Map == pawn.Map && !bench.IsForbidden(pawn);
        }
        internal static bool IsAtBench(Pawn pawn, Thing bench)
        { return pawn != null && bench != null && pawn.Spawned && bench.Spawned && pawn.Map == bench.Map && pawn.Position == bench.InteractionCell; }
    }
}
