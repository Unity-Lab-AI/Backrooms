using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// Founds a company branch on a colony that was not started on a Rimrooms scenario.
    ///
    /// Owner direction, 2026-10-08: *"the mod is active you can start it at any time"*. A save begun
    /// on vanilla Crashlanded had no way to reach the company at all: only
    /// <see cref="ScenPart_RimroomsStart"/> ever called <see cref="RimroomsCampaignComponent.InitializeBranch"/>.
    ///
    /// The branch takes the Async Industries start's company terms - corporation contact, the
    /// finished gate projects, funding, wages and the onboarding survey - because a branch founded
    /// on a working colony is the same company with the same books. It takes nothing physical: no
    /// facility, no grants, no relation reset. The colony as it stands is the headquarters and its
    /// free colonists are the staff, each given the role their skills fit best.
    /// </summary>
    public static class BranchFounding
    {
        public const string ScenarioId = "founded_branch";
        private const string TermsDefName = "RR_AsyncIndustriesStart";
        private const int MaxStaff = 20;

        /// <summary>Whether this map can found a branch now.</summary>
        public static bool Available(Map map)
        {
            RimroomsCampaignComponent company = Verse.Current.Game?.GetComponent<RimroomsCampaignComponent>();
            return map != null && map.IsPlayerHome && company != null && !company.HasBranch &&
                   ScenPart_RimroomsStart.Current == null;
        }

        public static CompanyActionResult Found(Map map)
        {
            if (!Available(map)) { return CompanyActionResult.Refused("RR_Founding_Unavailable"); }
            RimroomsStartDef terms = DefDatabase<RimroomsStartDef>.GetNamedSilentFail(TermsDefName);
            if (terms == null || terms.roles == null || terms.roles.Count == 0)
            { return CompanyActionResult.Refused("RR_Founding_Unavailable"); }

            List<Pawn> staff = map.mapPawns.FreeColonistsSpawned
                .Where(p => p.RaceProps.Humanlike && !p.IsSlave && p.Faction == Faction.OfPlayer)
                .Take(MaxStaff).ToList();
            if (staff.Count == 0) { return CompanyActionResult.Refused("RR_Founding_NoStaff"); }
            List<string> roles = staff.Select(p => BestRole(p, terms.roles)).ToList();

            RimroomsCampaignComponent company = Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            CompanyActionResult result = company.InitializeBranch(new BranchStartRequest
            {
                ScenarioId = ScenarioId,
                ScenarioVersion = 1,
                CompanyName = Faction.OfPlayer.Name,
                CampaignSeed = Find.World.info.Seed,
                Headquarters = map,
                Staff = staff,
                StaffRoles = roles,
                InitialFundingUsd = terms.initialFundingUsd,
                DailyWageUsd = terms.dailyWageUsd,
                DailyOverheadUsd = terms.dailyOverheadUsd,
                SurveyRewardUsd = terms.surveyRewardUsd,
                SurveyBonusUsd = terms.surveyBonusUsd,
                CompletedProjects = terms.completedProjects == null
                    ? new List<string>() : new List<string>(terms.completedProjects),
                BeginsInCorporationContact = terms.beginsInCorporationContact
            });
            if (result.Success)
            {
                Find.LetterStack.ReceiveLetter("RR_Founding_LetterTitle".Translate(),
                    "RR_Founding_LetterText".Translate(Faction.OfPlayer.Name, staff.Count), LetterDefOf.PositiveEvent);
            }
            return result;
        }

        // The role whose skill asks this pawn meets best; ties go to the role listed first.
        private static string BestRole(Pawn pawn, List<RimroomsStaffRole> roles)
        {
            RimroomsStaffRole best = roles[0];
            int bestScore = int.MinValue;
            foreach (RimroomsStaffRole role in roles)
            {
                if (role == null || string.IsNullOrWhiteSpace(role.id)) { continue; }
                if (role.mustFight && pawn.WorkTagIsDisabled(WorkTags.Violent)) { continue; }
                int score = 0;
                if (role.skills != null && pawn.skills != null)
                {
                    foreach (SkillRequirement need in role.skills)
                    {
                        if (need?.skill == null) { continue; }
                        score += pawn.skills.GetSkill(need.skill).Level;
                    }
                }
                if (score > bestScore) { bestScore = score; best = role; }
            }
            return best.id;
        }
    }
}
