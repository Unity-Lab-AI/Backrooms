using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Personnel
{
    public sealed class HiringPolicyDef : Def
    {
        public PawnKindDef candidateKind;
        public int maxOffers = 3;
        public int refreshTicks = 420000;
        public int offerTicks = 420000;
        public long onboardingUsd = 100000;
        public long dailyWageUsd = 5000;
        public bool Valid { get { return candidateKind != null && candidateKind.race != null &&
            candidateKind.race.race != null && candidateKind.race.race.Humanlike && maxOffers >= 1 && maxOffers <= 3 &&
            refreshTicks >= GenDate.TicksPerDay && offerTicks >= 1 && onboardingUsd > 0 && dailyWageUsd > 0; } }
        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (!Valid) { yield return "Rimrooms hiring policy requires a humanlike kind, 1-3 offers, positive quote/duration and at least one day between requests."; }
        }
    }

    public static class PersonnelRoles
    {
        private static readonly string[] ids = { "operations", "research", "engineering", "security", "medical_logistics" };
        public static IEnumerable<string> Ids { get { return ids; } }
        public static bool Valid(string role) { return role != null && ids.Contains(role); }
        public static string Recommend(Pawn pawn)
        {
            string best = "operations";
            float highest = -1f;
            foreach (string role in ids)
            {
                string[] names = SkillNames(role);
                float total = 0f;
                foreach (string name in names)
                {
                    SkillRecord skill = pawn.skills == null ? null : pawn.skills.skills.FirstOrDefault(s => s.def != null && s.def.defName == name);
                    if (skill != null && !skill.TotallyDisabled) { total += skill.Level; }
                }
                float score = total / names.Length;
                if (score > highest) { highest = score; best = role; }
            }
            return best;
        }
        private static string[] SkillNames(string role)
        {
            switch (role)
            {
                case "research": return new[] { "Intellectual" };
                case "engineering": return new[] { "Construction", "Crafting" };
                case "security": return new[] { "Shooting", "Melee" };
                case "medical_logistics": return new[] { "Medicine", "Cooking" };
                default: return new[] { "Social", "Intellectual" };
            }
        }
    }
}
