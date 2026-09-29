using System;
using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What the parent corporation puts in a crate, and the one place that decides it.
    ///
    /// Two things drop supplies on a branch: the clean-up team rebuilding a facility that lost
    /// everybody, and the unsolicited courier the corporation sends because it is watching an
    /// investment. **They are the same corporation with the same warehouse**, so they read one
    /// table at two scales rather than two tables that would drift apart the first time either
    /// was tuned.
    ///
    /// Every line is a Core `ThingDef`, asserted by `proof-facility-relief.py`. A renamed one
    /// would otherwise vanish from the crate without a word while the letter still promised it.
    /// </summary>
    public static class CompanySupplyDrop
    {
        /// <summary>A fresh start's worth. The clean-up team drops this at full scale.</summary>
        public static readonly KeyValuePair<string, int>[] Lines =
        {
            new KeyValuePair<string, int>("MealSurvivalPack", 30),
            new KeyValuePair<string, int>("MedicineIndustrial", 12),
            new KeyValuePair<string, int>("Steel", 300),
            new KeyValuePair<string, int>("ComponentIndustrial", 12),
            new KeyValuePair<string, int>("WoodLog", 200),
        };

        /// <summary>
        /// Appends the crate to a payload, scaled.
        ///
        /// A line that scales below one item is dropped entirely rather than rounded up to a
        /// token of itself: a crate containing a single component reads as an insult, and the
        /// corporation is many things but it is not petty.
        /// </summary>
        public static void Fill(List<Thing> payload, float scale)
        {
            if (payload == null || !(scale > 0f) || float.IsNaN(scale) || float.IsInfinity(scale))
            { return; }
            for (int index = 0; index < Lines.Length; index++)
            {
                KeyValuePair<string, int> line = Lines[index];
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(line.Key);
                if (def == null) { continue; }
                int remaining = (int)Math.Floor(line.Value * (double)scale);
                if (remaining < 1) { continue; }
                int limit = def.stackLimit > 0 ? def.stackLimit : remaining;
                while (remaining > 0)
                {
                    Thing stack = ThingMaker.MakeThing(def);
                    if (stack == null) { break; }
                    stack.stackCount = Math.Min(remaining, limit);
                    payload.Add(stack);
                    remaining -= stack.stackCount;
                }
            }
        }
    }
}
