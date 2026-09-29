using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A researcher crossing a gate to work at a bench on the other side.
    ///
    /// The second travel-to-work provider, and it exists to prove the shape generalises:
    /// there is no new record, no new job driver and no new JobDef here. Only the question
    /// "is there work of my kind over there" is answered differently.
    ///
    /// On arrival this provider issues nothing. Whatever research work giver is active on
    /// that map picks the bench up locally — Core's `WorkGiver_Researcher`, or a mod's
    /// replacement if one is installed. **That is the shape's compatibility property**, and
    /// it is why the research family needed no mod-specific adapter: because the work itself
    /// is never ours, a profile that changes how research is chosen, prioritised or
    /// presented changes nothing here.
    ///
    /// Profile rows read before writing this (per the owner's standing rule that the prep
    /// work is where mod facts live, and the reviews under `docs/research/reviews/mods/`):
    ///
    /// * **279 Research Whatever** auto-selects the cheapest project at a bench when none is
    ///   chosen. So `GetProject()` may be null when a trip is planned and non-null by the
    ///   time somebody arrives. That direction is harmless — an optimistic miss simply means
    ///   no trip was planned this pass, and planning retries on a cooldown.
    /// * **76 Do Your F-word Research** is a player float-menu prioritisation action, not a
    ///   research system, and automatic work never sees it.
    /// * **191 ResearchTree (Eheieh)** is a presentation and planning layer only.
    /// * **83 Dubs Rimatomics** keeps its **own** research table and screen, which is not
    ///   vanilla `ResearchManager` work. Because this provider matches Core exactly —
    ///   `ThingRequestGroup.ResearchBench`, a `Building_ResearchBench`, and
    ///   `CanBeResearchedAt` — a separate modded research system is neither claimed nor
    ///   broken. It is simply not this family's work.
    ///
    /// None of those is a dependency, and every one of them may be absent.
    /// </summary>
    public sealed class ResearchProvider : ConnectedDeploymentProvider
    {
        /// <summary>How many benches one remote candidate pass may look at.</summary>
        private const int MaximumBenchesPerMap = 16;

        public override string ProviderId
        { get { return ConnectedDeploymentProviders.Research; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_ResearchLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Research"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            // Research progress is global, not per-map, so "is there anything to research"
            // is one question asked once rather than a per-map search. This is also Core's
            // own first test, in both ShouldSkip and HasJobOnThing.
            ResearchProjectDef project = CurrentProject();
            if (project == null) { return false; }

            List<Thing> benches = map.listerThings.ThingsInGroup(ThingRequestGroup.ResearchBench);
            if (benches.Count == 0) { return false; }
            // A rotating window, never a prefix, per the standing scan rule.
            int windowStart = ConnectedWorkScan.WindowStart(benches.Count, MaximumBenchesPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < benches.Count; position++)
            {
                if (examined >= MaximumBenchesPerMap) { break; }
                examined++;
                if (CandidateBench(benches[position] as Building_ResearchBench, project, map, pawn, work))
                { return true; }
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            ResearchProjectDef project = CurrentProject();
            if (project == null) { return false; }
            // Not windowed, deliberately: a window that missed the one usable bench would
            // release the deployment while work remained and send the worker straight back
            // across the gate. Same reasoning and same cost as the construction provider.
            List<Thing> benches = pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.ResearchBench);
            for (int index = 0; index < benches.Count; index++)
            {
                var bench = benches[index] as Building_ResearchBench;
                if (bench == null || bench.Destroyed || !bench.Spawned) { continue; }
                if (bench.IsForbidden(pawn)) { continue; }
                if (!project.CanBeResearchedAt(bench, false)) { continue; }
                if (!pawn.CanReserve(bench)) { continue; }
                if (bench.def.hasInteractionCell && !pawn.CanReserveSittableOrSpot(bench.InteractionCell, false))
                { continue; }
                // Core asks this in the same speculative position, inside its own
                // HasJobOnThing. It is what stops an ideoligion that forbids researching
                // from leaving a deployed worker standing at a bench it may never use.
                if (!new HistoryEvent(HistoryEventDefOf.Researching,
                    pawn.Named(HistoryEventArgsNames.Doer)).Notify_PawnAboutToDo_Job())
                { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether this bench on this explicit map is worth crossing a gate for.
        ///
        /// `CanBeResearchedAt` is fair to ask remotely, and that was checked rather than
        /// assumed: it reads the bench's own def, its own `CompPowerTrader` power state, and
        /// its own linked facilities through `CompAffectedByFacilities`. Every one of those
        /// is a fact about the bench and the map it stands on. It consults no pawn and never
        /// touches the worker's map.
        ///
        /// What is deliberately left to arrival: `CanReserve`, `CanReserveSittableOrSpot` on
        /// the interaction cell, the pawn form of the forbidden check, and the researching
        /// history event. All four are pawn-and-map specific.
        /// </summary>
        private static bool CandidateBench(Building_ResearchBench bench, ResearchProjectDef project,
            Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (bench == null || bench.Destroyed || !bench.Spawned || bench.Map != map)
            { return false; }
            // The faction form, not the pawn form: the pawn form consults the pawn's allowed
            // area in its current map, which is the wrong map here.
            if (bench.IsForbidden(Faction.OfPlayer)) { return false; }
            if (bench.Position.Fogged(map)) { return false; }
            if (!project.CanBeResearchedAt(bench, false)) { return false; }
            // Where the worker would actually stand, when the bench has a seat.
            IntVec3 approach = bench.def.hasInteractionCell ? bench.InteractionCell : bench.Position;
            return work.ObservedAreaAllows(pawn, map, approach);
        }

        /// <summary>
        /// The project currently being researched, or null. Global state, so no map is
        /// involved and the answer is the same from anywhere.
        /// </summary>
        private static ResearchProjectDef CurrentProject()
        {
            return Find.ResearchManager == null ? null : Find.ResearchManager.GetProject();
        }
    }
}
