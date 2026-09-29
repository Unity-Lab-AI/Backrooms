using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    public sealed class CompanyActionResult
    {
        public bool Success { get; private set; }
        public bool AlreadyApplied { get; private set; }
        public string MessageKey { get; private set; }

        private CompanyActionResult(bool success, bool alreadyApplied, string messageKey)
        {
            Success = success;
            AlreadyApplied = alreadyApplied;
            MessageKey = messageKey;
        }

        public static CompanyActionResult Applied() { return new CompanyActionResult(true, false, null); }
        public static CompanyActionResult Existing() { return new CompanyActionResult(true, true, null); }
        public static CompanyActionResult Refused(string key) { return new CompanyActionResult(false, false, key); }
    }

    /// <summary>Scenario data enters the branch once, after physical setup succeeds.</summary>
    public sealed class BranchStartRequest
    {
        public string ScenarioId;
        public int ScenarioVersion;
        public string CompanyName;
        public int CampaignSeed;
        public Map Headquarters;
        public List<Pawn> Staff;
        public List<string> StaffRoles;
        public long InitialFundingUsd;
        public long DailyWageUsd;
        public long DailyOverheadUsd;
        /// <summary>Company projects this start begins with already finished.</summary>
        public List<string> CompletedProjects = new List<string>();
        public long SurveyRewardUsd;
        public long SurveyBonusUsd;
    }

    internal static class CampaignSeed
    {
        // Stable across processes and runtime versions; String.GetHashCode is unsuitable.
        internal static int Derive(int campaignSeed, string stableKey, int version)
        {
            unchecked
            {
                uint hash = 2166136261;
                hash = (hash ^ (uint)campaignSeed) * 16777619;
                hash = (hash ^ (uint)version) * 16777619;
                foreach (char character in stableKey)
                {
                    hash = (hash ^ character) * 16777619;
                }
                return (int)(hash & 0x7fffffff);
            }
        }
    }
}
