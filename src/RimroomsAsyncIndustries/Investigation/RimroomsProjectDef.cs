using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    // Company projects deliberately do not enter Core's globally selectable research tree.
    public sealed class RimroomsProjectDef : Def
    {
        public int insightCost = 1;
        public float workRequired = 6000f;
        public int minimumIntellectual = 4;
        public bool unlocksSurveyedRoutePlanning;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (insightCost < 1 || workRequired <= 0f || float.IsNaN(workRequired) || float.IsInfinity(workRequired))
            { yield return "Company project needs a positive insight cost and finite work requirement."; }
            if (minimumIntellectual < 0 || minimumIntellectual > 20)
            { yield return "minimumIntellectual must be between 0 and 20."; }
        }
    }
}
