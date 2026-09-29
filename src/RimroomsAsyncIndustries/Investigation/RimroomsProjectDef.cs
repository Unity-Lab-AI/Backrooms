using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    /// <summary>
    /// A company project: a rung on the ladder that decides what a gate can do.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"ie u need certain logs complete to operate
    /// the higher teri techs and shit and gate features and upgrades"*.
    ///
    /// Before this, a project cost **spendable insight** and nothing else. Insight is fungible:
    /// four analysed records of the same kind bought the same thing as four different ones, so
    /// nothing in the game ever asked what a branch had actually *learned*. The three log fields
    /// below ask exactly that, and they read data every evidence record has carried all along —
    /// `routeRecorded`, `distortionRecorded`, `entityRecorded` — which nothing had ever used as a
    /// prerequisite.
    ///
    /// Insight is still the cost. The logs are the **qualification**, and the difference matters:
    /// insight is spent and gone, while a log that has been completed stays completed. A tier
    /// already earned can never be lost by spending currency on the next one, which is the same
    /// rule `PortalWindowTier` already follows by counting completed projects rather than
    /// currency.
    /// </summary>
    public sealed class RimroomsProjectDef : Def
    {
        public int insightCost = 1;
        public float workRequired = 6000f;
        public int minimumIntellectual = 4;
        public bool unlocksSurveyedRoutePlanning;

        /// <summary>
        /// Analysed records carrying a route log that this project needs before it may begin.
        ///
        /// Counted over records at `Analyzed` status, so a record that was recovered and never
        /// analysed does not qualify — the log has to be **complete**, which is the owner's word.
        /// </summary>
        public int requiredRouteLogs;

        /// <summary>Analysed records carrying a distortion log. The space behaving wrongly.</summary>
        public int requiredDistortionLogs;

        /// <summary>Analysed records carrying an entity log. Something was down there.</summary>
        public int requiredEntityLogs;

        /// <summary>
        /// Projects that must be completed first.
        ///
        /// A ladder needs an order, and without this a branch with enough insight could complete
        /// the top rung first and skip every one below it. Named rather than inferred from the
        /// tier list, because the tier list belongs to the gate and a project may exist that is
        /// not on it.
        /// </summary>
        public List<string> prerequisiteProjects = new List<string>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (insightCost < 1 || workRequired <= 0f || float.IsNaN(workRequired) || float.IsInfinity(workRequired))
            { yield return "Company project needs a positive insight cost and finite work requirement."; }
            if (minimumIntellectual < 0 || minimumIntellectual > 20)
            { yield return "minimumIntellectual must be between 0 and 20."; }
            if (requiredRouteLogs < 0 || requiredDistortionLogs < 0 || requiredEntityLogs < 0)
            { yield return "A negative log requirement is not a requirement."; }
            if (prerequisiteProjects != null && prerequisiteProjects.Contains(defName))
            { yield return "A project cannot require itself; that rung can never be reached."; }
            if (prerequisiteProjects != null)
            {
                foreach (string name in prerequisiteProjects)
                {
                    if (string.IsNullOrWhiteSpace(name))
                    { yield return "An empty prerequisite name blocks the project forever."; }
                }
            }
        }
    }
}
