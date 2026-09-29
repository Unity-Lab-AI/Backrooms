using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>What an anomalous event actually does.</summary>
    public enum AnomalyEffect
    {
        /// <summary>A sound and a notice, and nothing else. Atmosphere with no mechanical cost.</summary>
        Presence = 0,

        /// <summary>Every light in the space switches off. Flicking them back on is the answer.</summary>
        LightsFail = 1,

        /// <summary>The space gets cold. Clothing, a heater, or leaving is the answer.</summary>
        ColdSnap = 2,

        /// <summary>The place is filthier than it was. The cleaning family already crosses gates.</summary>
        Seepage = 3,

        /// <summary>Loose items are not where they were left.</summary>
        Rearrangement = 4,
    }

    /// <summary>
    /// Something that happens in a coordinate, as opposed to something that is in one.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"even wild waky carzxzy creepy things when u
    /// add places and events"*. 0.7.9-dev built the **places**. This is the **events** half,
    /// which was named as outstanding rather than quietly dropped.
    ///
    /// ## Every effect has an answer, because the threat rules require one
    ///
    /// The frozen rules are: readable warning, learnable rule, at least one countermeasure, no
    /// unavoidable instant failure. So no effect here damages anybody, destroys anything, or
    /// blocks a route:
    ///
    /// | Effect | The answer |
    /// |---|---|
    /// | Lights fail | flick them back on — vanilla's own switch |
    /// | Cold snap | clothing, a heater, or leave |
    /// | Seepage | the cleaning family, which already crosses a gate |
    /// | Rearrangement | nothing is lost; it is somewhere else |
    /// | Presence | nothing to answer. It is a noise. |
    ///
    /// **The threshold room and the way back are never touched by any event**, at all, ever.
    /// That is the "no unavoidable instant failure" rule made concrete rather than promised:
    /// whatever happens, walking back out is still possible.
    /// </summary>
    public sealed class RimroomsAnomalyEventDef : Def
    {
        /// <summary>What it does.</summary>
        public AnomalyEffect effect = AnomalyEffect.Presence;

        /// <summary>Shallowest depth this may happen at.</summary>
        public int minDepth = 2;

        /// <summary>Deepest depth. Zero or less means no ceiling.</summary>
        public int maxDepth;

        /// <summary>Lowest ladder band at which this may happen.</summary>
        public CoordinatePressureLadder.Band minBand = CoordinatePressureLadder.Band.Unsettled;

        /// <summary>Relative likelihood against other events legal in the same situation.</summary>
        public float weight = 1f;

        /// <summary>How long the effect lasts, in ticks, where the effect has a duration.</summary>
        public int durationTicks = 30000;

        /// <summary>Magnitude, read differently per effect: degrees, filth count, items moved.</summary>
        public int magnitude = 1;

        /// <summary>
        /// Whether this event may happen more than once in the same coordinate.
        /// A one-shot is recorded against the coordinate so a revisit does not replay it, which
        /// is the same resume-rather-than-reroll rule the escalation ladder follows.
        /// </summary>
        public bool repeatable;

        /// <summary>Keyed strings for the notice. Required — the warning rule depends on it.</summary>
        public string letterLabelKey;
        public string letterTextKey;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(letterLabelKey) || string.IsNullOrEmpty(letterTextKey))
            {
                // Not a style preference. An event a player is not told about cannot satisfy
                // the readable-warning rule, and a silent effect reads as a bug.
                yield return "RimroomsAnomalyEventDef " + defName +
                    " has no letter keys, so it cannot satisfy the readable-warning rule.";
            }
            if (weight <= 0f)
            { yield return "RimroomsAnomalyEventDef " + defName + " has a non-positive weight."; }
            if (maxDepth > 0 && maxDepth < minDepth)
            { yield return "RimroomsAnomalyEventDef " + defName + " has maxDepth below minDepth."; }
        }
    }
}
