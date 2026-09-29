using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>
    /// One work family's pair of givers: the high-priority one that only finishes a trip
    /// already committed to, and the low-priority one that only starts a new one.
    /// </summary>
    internal sealed class ConnectedWorkPriorityPair
    {
        internal readonly string LabelKey;
        internal readonly string ContinueDefName;
        internal readonly string PlanDefName;

        internal ConnectedWorkPriorityPair(string labelKey, string continueDefName, string planDefName)
        {
            LabelKey = labelKey;
            ContinueDefName = continueDefName;
            PlanDefName = planDefName;
        }
    }

    /// <summary>
    /// Player-tunable priorities for the cross-gate work givers, applied live.
    ///
    /// Why these are settings rather than fixed numbers: how eagerly a colonist should
    /// cross a gate to work is a *feel* judgement, and feel cannot be settled from source
    /// reading. Shipping them as constants would have meant the only way to change them
    /// was a rebuild — and by owner direction the one session where these numbers are
    /// finally judged is a live play session in which fixes must land **without a mod
    /// restart and reload**. Anything hardcoded is something that session cannot fix. So
    /// the numbers live here, adjustable while the game runs.
    ///
    /// Applied with public API only, no Harmony:
    /// <list type="bullet">
    /// <item><c>WorkGiverDef.priorityInType</c> is a writable field.</item>
    /// <item><c>WorkTypeDef.workGiversByPriority</c> is a public mutable list, built by
    /// Core's own <c>ResolveReferences</c> as that type's givers ordered by
    /// <c>priorityInType</c> descending. Re-sorting it is exactly what Core did.</item>
    /// <item><c>Pawn_WorkSettings.Notify_UseWorkPrioritiesChanged()</c> is public and sets
    /// the dirty flag that rebuilds each pawn's cached giver order.</item>
    /// </list>
    /// </summary>
    internal static class ConnectedWorkPriorities
    {
        internal const int MinimumPriority = 0;

        /// <summary>
        /// Above Core's highest construction giver (120) with headroom, so a family can be
        /// lifted over anything native if that is what play calls for.
        /// </summary>
        internal const int MaximumPriority = 130;

        /// <summary>
        /// The families, in the order they are shown. Adding a family later needs a row
        /// here and nothing else: the saved overrides are keyed by giver defName, so the
        /// settings format does not change.
        /// </summary>
        internal static readonly ConnectedWorkPriorityPair[] Families =
        {
            new ConnectedWorkPriorityPair("RR_Settings_FamilyHauling",
                "RR_ConnectedHaulingContinue", "RR_ConnectedHauling"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyCasualty",
                "RR_ConnectedCasualtyContinue", "RR_ConnectedCasualty"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyConstruction",
                "RR_ConnectedConstructionContinue", "RR_ConnectedConstruction"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyBill",
                "RR_ConnectedBillContinue", "RR_ConnectedBill"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyMedicine",
                "RR_ConnectedMedicineContinue", "RR_ConnectedMedicine"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyTending",
                "RR_ConnectedTendingContinue", "RR_ConnectedTending"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyResearch",
                "RR_ConnectedResearchContinue", "RR_ConnectedResearch"),
            new ConnectedWorkPriorityPair("RR_Settings_FamilyFinishing",
                "RR_ConnectedConstructionFinishingContinue", "RR_ConnectedConstructionFinishing")
        };

        // What the shipped XML said, captured once before anything is overwritten. The XML
        // stays the single source of truth for the defaults, so a default cannot drift out
        // of step with a duplicate copy in code.
        private static readonly Dictionary<string, int> shipped =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private static bool captured;

        internal static bool Captured { get { return captured; } }

        internal static void CaptureShipped()
        {
            if (captured) { return; }
            for (int index = 0; index < Families.Length; index++)
            {
                Remember(Families[index].ContinueDefName);
                Remember(Families[index].PlanDefName);
            }
            captured = shipped.Count > 0;
        }

        private static void Remember(string defName)
        {
            WorkGiverDef giver = DefDatabase<WorkGiverDef>.GetNamedSilentFail(defName);
            if (giver == null || shipped.ContainsKey(defName)) { return; }
            shipped[defName] = giver.priorityInType;
        }

        internal static int Shipped(string defName)
        {
            int value;
            return defName != null && shipped.TryGetValue(defName, out value) ? value : 0;
        }

        /// <summary>The value in force: the player's override if there is one, else the shipped one.</summary>
        internal static int Effective(RimroomsSettings settings, string defName)
        {
            int value;
            if (settings != null && settings.ConnectedWorkPriorities != null &&
                settings.ConnectedWorkPriorities.TryGetValue(defName, out value))
            { return Clamp(value); }
            return Clamp(Shipped(defName));
        }

        internal static void Set(RimroomsSettings settings, string defName, int value)
        {
            if (settings == null || defName == null) { return; }
            settings.ConnectedWorkPriorities = settings.ConnectedWorkPriorities ??
                new Dictionary<string, int>(StringComparer.Ordinal);
            int clamped = Clamp(value);
            // An override equal to the shipped value is not stored, so resetting a slider
            // by hand leaves no residue and a future change to the XML default is picked up.
            if (clamped == Clamp(Shipped(defName))) { settings.ConnectedWorkPriorities.Remove(defName); }
            else { settings.ConnectedWorkPriorities[defName] = clamped; }
        }

        internal static void ResetToShipped(RimroomsSettings settings)
        {
            if (settings == null || settings.ConnectedWorkPriorities == null) { return; }
            settings.ConnectedWorkPriorities.Clear();
        }

        /// <summary>
        /// Whether this family's plan giver had to be pushed below its continue giver. Shown
        /// to the player rather than silently corrected, so a slider that will not go where
        /// it was dragged explains itself.
        /// </summary>
        internal static bool WasClamped(RimroomsSettings settings, ConnectedWorkPriorityPair pair)
        {
            return pair != null &&
                Effective(settings, pair.PlanDefName) >= Effective(settings, pair.ContinueDefName);
        }

        private static int Clamp(int value)
        {
            if (value < MinimumPriority) { return MinimumPriority; }
            return value > MaximumPriority ? MaximumPriority : value;
        }

        /// <summary>
        /// Push the current values into the defs and make every pawn notice. Safe to call
        /// at startup with no game loaded, and safe to call repeatedly.
        /// </summary>
        internal static void Apply(RimroomsSettings settings)
        {
            CaptureShipped();
            if (!captured) { return; }
            var touched = new List<WorkTypeDef>();
            for (int index = 0; index < Families.Length; index++)
            {
                ConnectedWorkPriorityPair pair = Families[index];
                WorkGiverDef continueGiver = DefDatabase<WorkGiverDef>.GetNamedSilentFail(pair.ContinueDefName);
                WorkGiverDef planGiver = DefDatabase<WorkGiverDef>.GetNamedSilentFail(pair.PlanDefName);
                if (continueGiver == null || planGiver == null) { continue; }

                int continueValue = Effective(settings, pair.ContinueDefName);
                int planValue = Effective(settings, pair.PlanDefName);
                // The two-giver invariant, enforced here because it is not a preference:
                // if starting a trip outranked finishing one, a worker standing on the far
                // side with cargo in its hands could be handed a brand new trip instead of
                // completing the delivery, and the whole reason the pair exists collapses.
                if (planValue >= continueValue)
                { planValue = Math.Max(MinimumPriority, continueValue - 1); }

                continueGiver.priorityInType = continueValue;
                planGiver.priorityInType = planValue;
                Note(touched, continueGiver.workType);
                Note(touched, planGiver.workType);
            }
            for (int index = 0; index < touched.Count; index++) { Resort(touched[index]); }
            InvalidatePawnCaches();
        }

        private static void Note(List<WorkTypeDef> touched, WorkTypeDef workType)
        {
            if (workType != null && !touched.Contains(workType)) { touched.Add(workType); }
        }

        private static void Resort(WorkTypeDef workType)
        {
            if (workType.workGiversByPriority == null) { return; }
            // Core builds this list with a LINQ `orderby priorityInType descending`, which
            // is a **stable** sort, so givers sharing a priority keep their database order.
            // OrderByDescending is stable too. List.Sort is not, and using it here would
            // silently reshuffle equal-priority native givers — a change to unrelated
            // vanilla behaviour, caused by touching a Rimrooms setting.
            List<WorkGiverDef> sorted = workType.workGiversByPriority
                .OrderByDescending(giver => giver.priorityInType).ToList();
            workType.workGiversByPriority.Clear();
            workType.workGiversByPriority.AddRange(sorted);
        }

        /// <summary>
        /// Each pawn caches its own giver order, so changing a def is not enough. Covers
        /// every pawn that could be issued a job now: spawned on a map, or travelling in a
        /// caravan and able to arrive at one.
        /// </summary>
        private static void InvalidatePawnCaches()
        {
            if (Current.Game == null) { return; }
            List<Map> maps = Find.Maps;
            if (maps != null)
            {
                for (int index = 0; index < maps.Count; index++)
                {
                    if (maps[index] == null || maps[index].mapPawns == null) { continue; }
                    Refresh(maps[index].mapPawns.AllPawnsSpawned);
                }
            }
            if (Find.WorldObjects == null) { return; }
            List<Caravan> caravans = Find.WorldObjects.Caravans;
            if (caravans == null) { return; }
            for (int index = 0; index < caravans.Count; index++)
            {
                if (caravans[index] == null) { continue; }
                Refresh(caravans[index].PawnsListForReading);
            }
        }

        private static void Refresh(IReadOnlyList<Pawn> pawns)
        {
            if (pawns == null) { return; }
            for (int index = 0; index < pawns.Count; index++)
            {
                Pawn pawn = pawns[index];
                if (pawn == null || pawn.workSettings == null || !pawn.workSettings.EverWork) { continue; }
                pawn.workSettings.Notify_UseWorkPrioritiesChanged();
            }
        }
    }

    /// <summary>
    /// Records the shipped priorities and applies any saved overrides once the defs exist.
    /// Runs after def loading, which is the first moment the XML values are readable.
    /// </summary>
    [StaticConstructorOnStartup]
    internal static class ConnectedWorkPriorityStartup
    {
        static ConnectedWorkPriorityStartup()
        {
            ConnectedWorkPriorities.CaptureShipped();
            ConnectedWorkPriorities.Apply(RimroomsMod.Settings);
        }
    }
}
