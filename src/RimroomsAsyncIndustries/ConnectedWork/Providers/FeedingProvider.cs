using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// Someone crossing a gate to feed a patient who cannot feed themselves.
    ///
    /// The fourth travel-to-work provider, and like the others it issues nothing on arrival:
    /// Core's own `WorkGiver_FeedPatient` takes the patient up locally, finds the food with
    /// `FoodUtility.TryFindBestFoodSourceFor` and runs the feeding.
    ///
    /// Core's own `WorkGiver_FeedPatient.HasJobOnThing` is, like tending, almost entirely
    /// patient-side — which is why this fitted the shape:
    ///
    /// * <c>map.mapPawns.SpawnedHungryPawns</c> is the same map-explicit accessor Core's own
    ///   `PotentialWorkThingsGlobal` uses.
    /// * <c>FeedPatientUtility.IsHungry</c> reads the patient's own food need against its own
    ///   hunger threshold.
    /// * <c>FeedPatientUtility.ShouldBeFed</c> reads the patient's posture, its bed, its
    ///   faction or host faction, whether its race eats, its slaughter designation and
    ///   whether it should seek medical rest. Every one is a fact about the patient.
    /// * <c>WardenFeedUtility.ShouldBeFed</c> excludes prisoners, who are fed by wardens
    ///   through a different route entirely.
    /// * babies are excluded, as Core excludes them.
    ///
    /// Left to arrival: the reservation, which is the one doctor-and-map question.
    ///
    /// **One extra requirement this provider has that the others do not: food must already be
    /// on that map.** A feeder is useless without something to feed with, and unlike research
    /// or construction there is no partial-credit version of the job — Core's feeding giver
    /// simply finds no food source and does nothing. Sending somebody across a gate to stand
    /// next to a hungry patient with an empty larder would be the parked-worker case for
    /// real, so the presence of edible food on the destination map is part of the candidate
    /// test rather than left to hope. Getting the food there is the carry family's job.
    /// </summary>
    public sealed class FeedingProvider : ConnectedDeploymentProvider
    {
        /// <summary>How many hungry patients one remote candidate pass may look at.</summary>
        private const int MaximumPatientsPerMap = 24;

        /// <summary>How many food stacks one presence check may look at.</summary>
        private const int MaximumFoodCandidates = 32;

        public override string ProviderId { get { return ConnectedDeploymentProviders.PatientFeeding; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_FeedingLabel"; } }

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
            List<Pawn> hungry = HungryOn(map);
            if (hungry == null || hungry.Count == 0) { return false; }
            int windowStart = ConnectedWorkScan.WindowStart(hungry.Count, MaximumPatientsPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < hungry.Count; position++)
            {
                if (examined >= MaximumPatientsPerMap) { break; }
                examined++;
                Pawn patient = hungry[position];
                if (!CandidatePatient(patient, pawn, map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, patient.PositionHeld)) { continue; }
                // No point going without something to feed them with.
                if (!AnyEdibleFoodOn(map, patient)) { continue; }
                return true;
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            List<Pawn> hungry = HungryOn(pawn.Map);
            if (hungry == null) { return false; }
            for (int index = 0; index < hungry.Count; index++)
            {
                Pawn patient = hungry[index];
                if (!CandidatePatient(patient, pawn, pawn.Map)) { continue; }
                if (!pawn.CanReserve(patient, 1, -1, null, false)) { continue; }
                // The definitive question about food is Core's own, and it is legitimate here
                // because the feeder is standing on this map: the getter is this pawn.
                Thing source;
                ThingDef definition;
                if (!FoodUtility.TryFindBestFoodSourceFor(pawn, patient,
                    patient.needs.food.CurCategory == HungerCategory.Starving,
                    out source, out definition, canRefillDispenser: false, canUseInventory: true,
                    canUsePackAnimalInventory: true, allowForbidden: false, allowCorpse: true,
                    allowSociallyImproper: false, allowHarvest: false, forceScanWholeMap: false,
                    ignoreReservations: false, calculateWantedStackCount: false, allowVenerated: true))
                { continue; }
                return true;
            }
            return false;
        }

        /// <summary>Core's own map-explicit hungry-pawn accessor.</summary>
        private static List<Pawn> HungryOn(Map map)
        {
            return map.mapPawns == null ? null : map.mapPawns.SpawnedHungryPawns;
        }

        /// <summary>
        /// Every rule here is a fact about the patient, mirroring Core's own
        /// `WorkGiver_FeedPatient.HasJobOnThing` minus the reservation and the food search.
        /// </summary>
        private static bool CandidatePatient(Pawn patient, Pawn feeder, Map map)
        {
            if (patient == null || patient.Destroyed || patient.Dead || !patient.Spawned ||
                patient.Map != map || patient == feeder)
            { return false; }
            if (patient.DevelopmentalStage.Baby()) { return false; }
            if (!FeedPatientUtility.IsHungry(patient)) { return false; }
            // Reduces to: lying down, in a bed we own, our faction or our guest, eats food,
            // not designated for slaughter, and should be resting for medical reasons.
            if (!FeedPatientUtility.ShouldBeFed(patient)) { return false; }
            // Prisoners are fed by wardens through a different route; Core excludes them here
            // for anything that is not a colony mech, and so does this.
            if (WardenFeedUtility.ShouldBeFed(patient) && !feeder.IsColonyMech) { return false; }
            return true;
        }

        /// <summary>
        /// Whether that map holds anything this patient would actually eat. Explicit-map and
        /// patient-side only: <c>WillEat</c> with no getter asks about the eater and the def,
        /// so it is fair to ask about a map nobody is standing on. The definitive search is
        /// Core's own on arrival.
        /// </summary>
        private static bool AnyEdibleFoodOn(Map map, Pawn patient)
        {
            List<Thing> food = map.listerThings.ThingsInGroup(ThingRequestGroup.FoodSourceNotPlantOrTree);
            int examined = 0;
            for (int index = 0; index < food.Count; index++)
            {
                if (examined >= MaximumFoodCandidates) { break; }
                examined++;
                Thing thing = food[index];
                if (thing == null || thing.Destroyed || !thing.Spawned || thing.Map != map) { continue; }
                if (thing.IsForbidden(Faction.OfPlayer) || thing.Position.Fogged(map)) { continue; }
                if (!patient.WillEat(thing.def, null, true, true)) { continue; }
                return true;
            }
            return false;
        }
    }
}
