using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A researcher crossing a gate to study a contained entity on the other side.
    ///
    /// Thematically this is the most apt family in the whole work layer: a company that
    /// reaches unstable spaces through a machine gate, holds what it finds, and learns from
    /// it. A containment facility on the far side of a portal is the premise of the mod, and
    /// until now nobody would walk to one.
    ///
    /// ## Anomaly content, and it degrades rather than claiming support
    ///
    /// `DarkStudy` is an Anomaly work type — `WorkTypeDefOf` declares it `[MayRequireAnomaly]`
    /// — so `GetNamedSilentFail("DarkStudy")` returns null without the expansion and this
    /// provider is simply unavailable. Never a missing-def exception, never a claim the
    /// install cannot honour. The same pattern childcare uses for Biotech.
    ///
    /// Core's own giver agrees: `WorkGiver_DarkStudyInteract.ShouldSkip` is exactly
    /// `return !ModsConfig.AnomalyActive;`.
    ///
    /// The profile's position on the expansion, read from the register before writing this:
    /// row **8 Anomaly** is *"optional native anomaly touchpoints; Rimrooms supplies its own
    /// Core threat, evidence, and containment loops"*, so the campaign must stay whole
    /// without it — which is exactly what an unavailable provider gives. Rows **138 Move Your
    /// Monolith** (a layout utility, explicitly *"not a Rimrooms gate or navigation system"*),
    /// **140 Name Your Entities** (display naming only; stable Rimrooms ids stay separate) and
    /// **39 Anomaly Research Asteroid** (optional expedition content, no adapter planned) were
    /// checked and none of them touches this route.
    ///
    /// ## Core hands the candidate half over directly
    ///
    /// This is the cleanest split in the work layer so far, because Core's own scanner already
    /// takes an explicit map:
    ///
    /// <code>
    /// public override IEnumerable&lt;Thing&gt; PotentialWorkThingsGlobal(Pawn pawn)
    ///     =&gt; Find.StudyManager.GetStudiableThingsAndPlatforms(pawn.Map);
    /// </code>
    ///
    /// and `GetStudiableThingsAndPlatforms` is a **pure read** of a per-map cache that returns
    /// an empty set for a map it does not know and mutates nothing. So asking it about a map
    /// nobody is standing on is fair, cheap and exact — no reimplementation, and no risk of
    /// touching Core's scan state from a remote probe.
    ///
    /// Likewise `CompStudiable.EverStudiable()` and `CurrentlyStudiable()` read the studied
    /// thing, its parent holder, its own comps and the global tick. **Neither takes a pawn and
    /// neither reads any worker's map**, so both are safe from here. That was checked in
    /// source rather than assumed, because they are the whole substance of the question.
    ///
    /// What is deliberately left to arrival: `pawn.CanReserve` on both the platform *and* the
    /// held pawn, and the identity check that a pawn is not sent to study itself. All three
    /// are pawn-specific.
    /// </summary>
    public sealed class DarkStudyProvider : ConnectedDeploymentProvider
    {
        /// <summary>How many studiable things one remote candidate pass may look at.</summary>
        private const int MaximumStudiablesPerMap = 12;

        public override string ProviderId
        { get { return ConnectedDeploymentProviders.DarkStudy; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_DarkStudyLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("DarkStudy"); } }

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
            HashSet<Thing> studiables = Studiables(map);
            if (studiables == null || studiables.Count == 0) { return false; }

            // A rotating window over an unindexed collection. The set is small in practice, but
            // the standing rule is a window and never a prefix, so the start offset rotates per
            // worker and a second pass picks up the wrap rather than always re-reading the
            // front of the set. Re-enumerating a HashSet is cheap and allocates nothing.
            int windowStart = ConnectedWorkScan.WindowStart(studiables.Count,
                MaximumStudiablesPerMap, pawn);
            int examined = 0;
            int position = 0;
            foreach (Thing candidate in studiables)
            {
                if (position++ < windowStart) { continue; }
                if (examined >= MaximumStudiablesPerMap) { break; }
                examined++;
                if (CandidateStudiable(candidate, map, pawn, work)) { return true; }
            }
            if (examined < MaximumStudiablesPerMap && windowStart > 0)
            {
                int wrapped = 0;
                foreach (Thing candidate in studiables)
                {
                    if (wrapped++ >= windowStart) { break; }
                    if (examined >= MaximumStudiablesPerMap) { break; }
                    examined++;
                    if (CandidateStudiable(candidate, map, pawn, work)) { return true; }
                }
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            HashSet<Thing> studiables = Studiables(pawn.Map);
            if (studiables == null || studiables.Count == 0) { return false; }
            // Not windowed, deliberately: a window that missed the one studiable entity would
            // release the deployment while there was still work to do and plan the worker
            // straight back across the gate.
            foreach (Thing candidate in studiables)
            {
                if (!CandidateStudiable(candidate, pawn.Map, pawn, null)) { continue; }
                // Core reserves both the platform and the thing held on it, so both must be
                // free before this counts as work the worker can actually start.
                Thing subject = Subject(candidate);
                if (subject == null || subject == pawn) { continue; }
                if (!pawn.CanReserve(candidate)) { continue; }
                if (subject != candidate && !pawn.CanReserve(subject)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether this thing on this explicit map is worth crossing a gate for.
        ///
        /// A null <paramref name="work"/> means the question is being asked locally, where the
        /// observed-area record is not the right instrument — the same convention the care
        /// providers use.
        /// </summary>
        private static bool CandidateStudiable(Thing candidate, Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (candidate == null || candidate.Destroyed || !candidate.Spawned ||
                candidate.Map != map)
            { return false; }
            // The faction form, not the pawn form: the pawn form consults the pawn's allowed
            // area in its current map, which is the wrong map here.
            if (candidate.IsForbidden(Faction.OfPlayer)) { return false; }
            if (candidate.Position.Fogged(map)) { return false; }

            Thing subject = Subject(candidate);
            if (subject == null || subject == pawn) { return false; }

            CompStudiable studiable = subject.TryGetComp<CompStudiable>();
            // Core dereferences this comp without a null check, relying on the study manager's
            // cache only ever holding studiable things. Checked here anyway: a remote probe
            // that threw would take down an unrelated work scan.
            if (studiable == null || studiable.KnowledgeCategory == null) { return false; }
            if (!studiable.EverStudiable()) { return false; }
            if (!studiable.CurrentlyStudiable()) { return false; }

            if (work != null &&
                !work.ObservedAreaAllows(pawn, map, candidate.Position))
            { return false; }
            return true;
        }

        /// <summary>
        /// What is actually being studied. A holding platform is the work target, but the
        /// studiable thing is the entity held on it — exactly the substitution Core makes in
        /// `HasJobOnThing` before it looks for the comp. An empty platform is not work.
        /// </summary>
        private static Thing Subject(Thing candidate)
        {
            var platform = candidate as Building_HoldingPlatform;
            return platform != null ? platform.HeldPawn : candidate;
        }

        /// <summary>
        /// Core's own studiable set for that map. A pure read of a per-map cache which returns
        /// an empty set for a map it does not know, so it is safe to ask about any map.
        /// </summary>
        private static HashSet<Thing> Studiables(Map map)
        {
            return Find.StudyManager == null ? null : Find.StudyManager.GetStudiableThingsAndPlatforms(map);
        }
    }
}
