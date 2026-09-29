using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// The last three work families — wardening, childcare and animal handling.
    ///
    /// All three are deployments, and all three lean hard on the rule that **a provider
    /// answers one question, not one Core work giver**. Core has fourteen warden givers, six
    /// childcare givers and eight handling givers; asking "is there warden work on that map"
    /// once, and letting Core's own givers pick which of the fourteen applies on arrival, is
    /// both correct and the only sane amount of code.
    ///
    /// Each work type resolves through `GetNamedSilentFail`, so a family whose work type does
    /// not exist in this install simply never offers anything. That matters here more than
    /// anywhere else: `Childcare` is Biotech content, and without Biotech the provider is
    /// unavailable rather than broken.
    /// </summary>
    internal static class CareScan
    {
        internal const int MaximumCandidates = 16;

        internal static bool WorkActive(Pawn pawn, WorkTypeDef workType)
        {
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        /// <summary>
        /// Whether any of these pawns on that map is a live candidate: really there, not
        /// fogged, and inside this worker's observed allowed area. Bounded.
        /// </summary>
        internal static bool AnyReachableCandidate(List<Pawn> pawns, Map map, Pawn worker,
            RimroomsConnectedWorkComponent work, System.Func<Pawn, bool> extra)
        {
            if (pawns == null || pawns.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(pawns.Count, MaximumCandidates, worker);
            int examined = 0;
            for (int position = windowStart; position < pawns.Count; position++)
            {
                if (examined >= MaximumCandidates) { break; }
                examined++;
                Pawn candidate = pawns[position];
                if (candidate == null || candidate.Destroyed || candidate.Dead ||
                    !candidate.Spawned || candidate.Map != map || candidate == worker)
                { continue; }
                if (candidate.PositionHeld.Fogged(map)) { continue; }
                if (extra != null && !extra(candidate)) { continue; }
                // Null work means the question is being asked locally, where the observed-area
                // record is not the right instrument.
                if (work != null && !work.ObservedAreaAllows(worker, map, candidate.PositionHeld))
                { continue; }
                return true;
            }
            return false;
        }
    }

    /// <summary>
    /// A warden crossing a gate to attend to prisoners or slaves held over there.
    ///
    /// One question: does that map hold somebody of ours in custody. Core has fourteen warden
    /// givers — feeding, chatting, converting, recruiting, releasing, enslaving, executing and
    /// more — and every one of them is driven by the **interaction mode the player set on that
    /// prisoner**. So the deployment justifies the crossing and Core picks which of the
    /// fourteen applies once the warden is standing there.
    ///
    /// **Prisoner food already reaches them.** The food carry family excluded prisoners from
    /// *feeding*, because `WardenFeedUtility` owns that route — but its eater test accepts any
    /// pawn whose `HostFaction` is the player, which is exactly what a prisoner is. So food
    /// gets carried to a map holding prisoners, and this provider sends the warden who hands
    /// it over. The two halves already fit without either knowing about the other.
    /// </summary>
    public sealed class WardenProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.Warden; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_WardenLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Warden"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return CareScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return AnyInCustody(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            return AnyInCustody(pawn.Map, pawn, null);
        }

        private static bool AnyInCustody(Map map, Pawn worker, RimroomsConnectedWorkComponent work)
        {
            if (map.mapPawns == null) { return false; }
            if (CareScan.AnyReachableCandidate(map.mapPawns.PrisonersOfColonySpawned, map, worker, work, null))
            { return true; }
            return CareScan.AnyReachableCandidate(map.mapPawns.SlavesOfColonySpawned, map, worker, work, null);
        }
    }

    /// <summary>
    /// A carer crossing a gate to a baby of ours over there.
    ///
    /// One question: is there a baby on that map. Core's six childcare givers cover taking a
    /// baby to safety, breastfeeding, bottle feeding, playing and teaching, and each has its
    /// own conditions; the deployment justifies the crossing and Core chooses.
    ///
    /// **Biotech content.** `Childcare` is a Biotech work type, so `GetNamedSilentFail` returns
    /// null without the expansion and this provider is simply unavailable — never a missing-def
    /// exception, and never a claim of support the install cannot honour.
    ///
    /// Worth stating plainly: a baby on the far side of a gate is an unusual and alarming
    /// situation, and this family exists so that somebody goes to it rather than so that it
    /// becomes routine. The deployment carries nobody — bringing a baby home is the casualty
    /// family's shape, and Core's own `BringBabyToSafety` runs locally once the carer arrives.
    /// </summary>
    public sealed class ChildcareProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.Childcare; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_ChildcareLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Childcare"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return CareScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return AnyBaby(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            return AnyBaby(pawn.Map, pawn, null);
        }

        private static bool AnyBaby(Map map, Pawn worker, RimroomsConnectedWorkComponent work)
        {
            if (map.mapPawns == null) { return false; }
            return CareScan.AnyReachableCandidate(map.mapPawns.FreeColonistsSpawned, map, worker, work,
                candidate => candidate.DevelopmentalStage.Baby());
        }
    }

    /// <summary>
    /// A handler crossing a gate to animals over there.
    ///
    /// **Designation-driven only, and that is a deliberate narrowing.** Core's `Handling` type
    /// has eight givers, but most of them — penning, milking, shearing, training, feeding
    /// patient animals — describe *continuous states* rather than a thing the player asked
    /// for. A handler crossing a gate because a far-side alpaca could theoretically be sheared
    /// would be constant, pointless traffic through a gate.
    ///
    /// So this family fires only on an explicit mark: **slaughter, tame, or release to the
    /// wild**. Those are things the player designated on that map, which puts this family with
    /// the fieldwork ones — nothing is inferred, and no designation means nobody goes. Once a
    /// handler is there, Core's own givers do whatever else that map needs, including the
    /// continuous work this provider would not have crossed for.
    /// </summary>
    public sealed class AnimalHandlingProvider : ConnectedDeploymentProvider
    {
        public override string ProviderId { get { return ConnectedDeploymentProviders.AnimalHandling; } }
        public override int ProviderVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_HandlingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Handling"); } }

        public override bool WorkerEligible(Pawn pawn)
        { return CareScan.WorkActive(pawn, WorkType); }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return Marked(map, DesignationDefOf.Slaughter, pawn, work) ||
                Marked(map, DesignationDefOf.Tame, pawn, work) ||
                Marked(map, DesignationDefOf.ReleaseAnimalToWild, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            Map map = pawn.Map;
            return FieldworkScan.AnyDesignation(map, DesignationDefOf.Slaughter) ||
                FieldworkScan.AnyDesignation(map, DesignationDefOf.Tame) ||
                FieldworkScan.AnyDesignation(map, DesignationDefOf.ReleaseAnimalToWild);
        }

        private static bool Marked(Map map, DesignationDef definition, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            Thing target = FieldworkScan.FirstDesignatedThing(map, definition, pawn, work);
            var animal = target as Pawn;
            return animal != null && !animal.Dead && animal.AnimalOrWildMan();
        }
    }
}
