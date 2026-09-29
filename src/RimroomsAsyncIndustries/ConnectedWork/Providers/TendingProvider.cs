using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A doctor crossing a gate to treat someone who stays where they are.
    ///
    /// This is the half of tending that is **not** carrying a person home. The casualty
    /// family built in 0.5.2-dev brings our own downed people back to a bed; this one leaves
    /// the patient exactly where they are and sends the doctor instead. Both are wanted: a
    /// patient already in a bed on the other side should be treated there, not dragged
    /// through a gate first.
    ///
    /// The third travel-to-work provider, and again no new record, driver or JobDef. On
    /// arrival it issues nothing and Core's own tend givers take the patient up locally.
    ///
    /// Every candidate rule below is a fact about the **patient**, which is what makes this
    /// family fit the shape so cleanly — Core's own `WorkGiver_Tend.HasJobOnThing` is almost
    /// entirely patient-side already, with only the reservation being doctor-specific:
    ///
    /// * <c>map.mapPawns.SpawnedPawnsWithAnyHediff</c> is the same map-explicit accessor
    ///   Core's own `PotentialWorkThingsGlobal` uses, so no wider sweep is needed.
    /// * <c>HealthAIUtility.ShouldBeTendedNowByPlayer</c> reads the patient's own
    ///   `playerSettings.medCare`, its prisoner execution mode, its slaughter designation and
    ///   its own hediffs. No doctor, no map.
    /// * <c>WorkGiver_Tend.GoodLayingStatusForTend</c> reduces, for a humanlike patient who
    ///   is not the doctor, to `patient.InBed()`. A fact about the patient.
    /// * the mutant medical-care entitlement and the aggro-mental-state exclusion are both
    ///   read straight off the patient, as Core reads them.
    ///
    /// Left to arrival, because they are doctor-and-map specific: the reservation, and the
    /// pawn form of any access question.
    ///
    /// Profile rows read first, per the owner's rule that the prep work is where mod facts
    /// live. Rows 209 Smart Medicine, 193 ReTend, 225 TendYourself, 113 Injured Carry,
    /// 126 Medical IVs, 109 Hospital and 34 Animal Medical Bed all carry the same recorded
    /// disposition: optional, **no Rimrooms adapter**, and Rimrooms must keep its own care
    /// route working with every one of them absent. This provider satisfies that by
    /// construction — because it never issues the tend job, whatever tending behaviour is
    /// active on the destination map is what happens.
    /// </summary>
    public sealed class TendingProvider : ConnectedDeploymentProvider
    {
        /// <summary>How many patients one remote candidate pass may look at.</summary>
        private const int MaximumPatientsPerMap = 24;

        public override string ProviderId { get { return ConnectedDeploymentProviders.Tending; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_TendingLabel"; } }

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
            List<Pawn> patients = PatientsOn(map);
            if (patients == null || patients.Count == 0) { return false; }
            // A rotating window, never a prefix, per the standing scan rule.
            int windowStart = ConnectedWorkScan.WindowStart(patients.Count, MaximumPatientsPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < patients.Count; position++)
            {
                if (examined >= MaximumPatientsPerMap) { break; }
                examined++;
                Pawn patient = patients[position];
                if (!CandidatePatient(patient, pawn, map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, patient.PositionHeld)) { continue; }
                return true;
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            // Not windowed, deliberately: a window that missed the one patient would release
            // the deployment while someone still needed treating, and send the doctor back
            // across the gate. Same reasoning as the other providers.
            List<Pawn> patients = PatientsOn(pawn.Map);
            if (patients == null) { return false; }
            for (int index = 0; index < patients.Count; index++)
            {
                Pawn patient = patients[index];
                if (!CandidatePatient(patient, pawn, pawn.Map)) { continue; }
                // The one genuinely doctor-specific question in Core's own giver.
                if (!pawn.CanReserve(patient, 1, -1, null, false)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Core's own map-explicit patient accessor, the same one
        /// <c>WorkGiver_Tend.PotentialWorkThingsGlobal</c> uses. Asking this map for its own
        /// hediff-carrying pawns is a fact about that map.
        /// </summary>
        private static List<Pawn> PatientsOn(Map map)
        {
            return map.mapPawns == null ? null : map.mapPawns.SpawnedPawnsWithAnyHediff;
        }

        /// <summary>
        /// Every rule here is a fact about the patient or its own map. None of them asks a
        /// doctor-and-map question, which is why this is legitimate for a map the doctor is
        /// not standing on. Mirrors Core's `WorkGiver_Tend.HasJobOnThing` minus the
        /// reservation.
        /// </summary>
        private static bool CandidatePatient(Pawn patient, Pawn doctor, Map map)
        {
            if (patient == null || patient.Destroyed || patient.Dead || !patient.Spawned ||
                patient.Map != map || patient == doctor)
            { return false; }
            // For a humanlike patient who is not the doctor this reduces to InBed(), so a
            // doctor is never sent through a gate for somebody wandering around.
            if (!WorkGiver_Tend.GoodLayingStatusForTend(patient, doctor)) { return false; }
            if (!HealthAIUtility.ShouldBeTendedNowByPlayer(patient)) { return false; }
            if (patient.IsMutant && patient.mutant != null && patient.mutant.Def != null &&
                !patient.mutant.Def.entitledToMedicalCare)
            { return false; }
            // Core's own exclusion: someone in an aggressive mental state is not treated
            // unless their aggression is scaria.
            if (patient.InAggroMentalState && (patient.health == null ||
                patient.health.hediffSet == null ||
                !patient.health.hediffSet.HasHediff(HediffDefOf.Scaria)))
            { return false; }
            return true;
        }
    }
}
