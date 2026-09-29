using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// Someone crossing a gate to put a downed person into a bed **on that same map**, rather
    /// than hauling them home through a gate first.
    ///
    /// The fifth travel-to-work provider, and the one real gap the rest-and-beds item turned
    /// up. It is deliberately the counterpart of the casualty family rather than a duplicate:
    ///
    /// * **Casualty family (0.5.2-dev)** — carries our own downed people **home** to a bed.
    ///   That is the right answer when the far side has no bed for them.
    /// * **This provider** — sends somebody across to tuck them into a bed **there**. That is
    ///   the right answer when the far side does have one, because an injured person taken
    ///   through a gate is one more crossing for somebody who cannot walk, and the traversal
    ///   contract prefers fewer.
    ///
    /// The two coexist safely: a worker may only hold one commitment at a time, and Core's own
    /// reservation on the patient settles which of two different workers gets there first.
    ///
    /// On arrival this issues nothing. Core's own `WorkGiver_RescueDowned` takes over — its
    /// `ShouldSkip` looks for a pawn of the worker's own faction that is downed and not in
    /// bed, which is exactly the situation that justified sending somebody — and it does the
    /// bed search, the reservation and the tucking with its own code.
    ///
    /// ## Why the candidate half looks the way it does
    ///
    /// Core's `WorkGiver_RescueDowned.HasJobOnThing` needs `CanRescueNow` **and** a bed from
    /// its protected `FindBed`. Neither can be asked remotely:
    ///
    /// * `HealthAIUtility.CanRescueNow` ends in `rescuer.CanReserveAndReach(patient, ...)`,
    ///   which is the rescuer's own map.
    /// * `RestUtility.FindBedFor` searches with `TraverseParms.For(traveler)` — a cross-map
    ///   reachability query if the traveller is our pawn, which is exactly what the two-halves
    ///   rule forbids.
    ///
    /// So the candidate half asks the questions that *are* fair about a map nobody stands on:
    /// facts about the patient, and facts about the beds on that map. `CanUseBedEver` takes a
    /// pawn and a `ThingDef` and touches no map at all; `AnyUnoccupiedSleepingSlot`,
    /// `Medical`, `ForPrisoners` and the burning check are all facts about the bed. The
    /// definitive question is Core's own, on arrival, through its own giver.
    /// </summary>
    public sealed class RescueInPlaceProvider : ConnectedDeploymentProvider
    {
        private const int MaximumDownedPerMap = 16;
        private const int MaximumBedsPerMap = 32;

        public override string ProviderId { get { return ConnectedDeploymentProviders.RescueInPlace; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_RescueInPlaceLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Doctor"); } }

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
            List<Pawn> downed = DownedOn(map);
            if (downed == null || downed.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(downed.Count, MaximumDownedPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < downed.Count; position++)
            {
                if (examined >= MaximumDownedPerMap) { break; }
                examined++;
                Pawn patient = downed[position];
                if (!CandidatePatient(patient, pawn, map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, patient.PositionHeld)) { continue; }
                // The whole point of going there instead of carrying them home: there has to
                // be a bed on that side. Without one, this is the casualty family's job.
                if (!AnyUsableBedOn(map, patient)) { continue; }
                return true;
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            List<Pawn> downed = DownedOn(pawn.Map);
            if (downed == null) { return false; }
            for (int index = 0; index < downed.Count; index++)
            {
                Pawn patient = downed[index];
                if (!CandidatePatient(patient, pawn, pawn.Map)) { continue; }
                // Core's own definitive rescue precondition, now that the rescuer is standing
                // on the right map. It ends in CanReserveAndReach, which is why it could not
                // be asked before.
                if (!HealthAIUtility.CanRescueNow(pawn, patient, false)) { continue; }
                // And Core's own bed search, with our pawn as the traveller, which is only
                // legitimate here.
                Building_Bed bed = RestUtility.FindBedFor(patient, pawn, true, false, patient.GuestStatus);
                if (bed == null) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>Core's own map-explicit downed-pawn accessor.</summary>
        private static List<Pawn> DownedOn(Map map)
        {
            return map.mapPawns == null ? null : map.mapPawns.SpawnedDownedPawns;
        }

        /// <summary>
        /// Facts about the patient only. Mirrors what Core's rescue giver wants, minus the two
        /// questions that need the rescuer's own map.
        /// </summary>
        private static bool CandidatePatient(Pawn patient, Pawn rescuer, Map map)
        {
            if (patient == null || patient.Destroyed || patient.Dead || !patient.Spawned ||
                patient.Map != map || patient == rescuer)
            { return false; }
            if (!patient.Downed) { return false; }
            // Core's own faction rule for an unforced rescue.
            if (patient.Faction != rescuer.Faction) { return false; }
            if (!HealthAIUtility.WantsToBeRescued(patient)) { return false; }
            // Already in a bed is already handled.
            if (patient.InBed()) { return false; }
            // Babies go through ChildcareUtility.SafePlaceForBaby, a different route with its
            // own rules. Left to Core entirely rather than half-reimplemented here.
            if (ChildcareUtility.CanSuckle(patient, out _)) { return false; }
            // The faction form of forbidden, never the pawn form, because the pawn form reads
            // the rescuer's allowed area in its current map.
            return !patient.IsForbidden(Faction.OfPlayer);
        }

        /// <summary>
        /// Whether that map holds a bed this patient could ever be put in. Explicit-map and
        /// patient-side only: <c>CanUseBedEver</c> takes a pawn and a `ThingDef` and touches
        /// no map, and everything else here is a fact about the bed itself. The real bed
        /// choice is Core's own `FindBedFor` on arrival.
        /// </summary>
        private static bool AnyUsableBedOn(Map map, Pawn patient)
        {
            List<Thing> beds = map.listerThings.ThingsInGroup(ThingRequestGroup.Bed);
            int examined = 0;
            for (int index = 0; index < beds.Count; index++)
            {
                if (examined >= MaximumBedsPerMap) { break; }
                examined++;
                var bed = beds[index] as Building_Bed;
                if (bed == null || bed.Destroyed || !bed.Spawned || bed.Map != map) { continue; }
                if (bed.IsBurning() || bed.IsForbidden(Faction.OfPlayer)) { continue; }
                if (bed.Position.Fogged(map)) { continue; }
                if (!bed.AnyUnoccupiedSleepingSlot) { continue; }
                // A prisoner bed is not somewhere our own downed colonist gets tucked into.
                if (bed.ForPrisoners) { continue; }
                if (!RestUtility.CanUseBedEver(patient, bed.def)) { continue; }
                return true;
            }
            return false;
        }
    }
}
