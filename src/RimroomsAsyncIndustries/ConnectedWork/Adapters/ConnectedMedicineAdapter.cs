using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Adapters
{
    /// <summary>
    /// Carrying real medicine through a gate to a patient who has none on their side.
    ///
    /// The other half of tending, and the first family whose cargo is **consumed by the
    /// work** rather than stored, sold or built with. That difference is smaller than it
    /// looks in implementation and much larger in reasoning, which is why it gets its own
    /// adapter rather than being folded into hauling.
    ///
    /// The hook is one specific Core fact, and it is what makes the family possible at all:
    /// <c>HealthAIUtility.FindBestMedicine</c> searches
    /// <c>patient.MapHeld.listerThings.ThingsInGroup(ThingRequestGroup.Medicine)</c> — **the
    /// patient's map, not the doctor's**. So getting medicine onto the patient's map is
    /// exactly and only what is needed; the doctor then finds it through Core's own search
    /// with no help from us. There is no radius to respect either, unlike a bill: Core's
    /// search is map-wide.
    ///
    /// **Medicine is optional to tending, and that shapes the whole family.** Core's
    /// `WorkGiver_Tend.JobOnThing` falls through to `MakeJob(TendPatient, patient)` with no
    /// medicine at all when none is found. So this family never decides *whether* someone
    /// gets treated — only how well. A trip that arrives late has cost nothing but a walk,
    /// and a trip that never happens still leaves the patient tended.
    ///
    /// Three patient-side rules are honoured rather than reinvented, all read straight from
    /// `FindBestMedicine` and `Medicine`:
    ///
    /// * a patient whose `medCare` is `NoCare` or `NoMeds` wants no medicine, so none is
    ///   carried for them;
    /// * <c>Medicine.GetMedicineCountToFullyHeal(patient)</c> is the count, never a number of
    ///   ours;
    /// * <c>medCare.AllowsMedicine(def)</c> decides which medicine qualifies, so a patient set
    ///   to herbal-or-worse never has glitterworld medicine hauled across a gate for them.
    ///
    /// Profile rows read first, per the owner's standing rule. Row **209 Smart Medicine**
    /// matters most here: it sources medicine from pawn and patient inventories and adds
    /// field tending, so with it installed a doctor may already have medicine in hand and
    /// this family's trip becomes unnecessary. That is harmless — an unnecessary plan is not
    /// made, because the shortage test only counts what is on the patient's map, and if the
    /// doctor's own inventory covers it Core simply tends without touching our delivery.
    /// Its review's disposition is "optional medical-care QoL, no Rimrooms adapter, retain
    /// our own care route", which is satisfied. Rows 193 ReTend, 225 TendYourself,
    /// 126 Medical IVs, 109 Hospital and 34 Animal Medical Bed are likewise optional with no
    /// adapter, and none of them is a dependency.
    /// </summary>
    public sealed class ConnectedMedicineAdapter : ConnectedWorkAdapter
    {
        /// <summary>The patient no longer needs it. Not a failure; the medicine is real and here.</summary>
        internal const string PatientSuppliedKey = "RR_ConnectedWork_PatientSupplied";

        private const int MaximumPatientsPerMap = 24;
        private const int MaximumMedicineCandidates = 24;
        private const int MaximumPresenceCandidates = 48;

        public override string AdapterId { get { return ConnectedWorkAdapters.MedicineSupply; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_MedicineLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            // Arriving to find the patient healed, dead, moved or already supplied is a
            // completed trip with a different ending. The medicine is physically on this side
            // and in real hands, and ordinary hauling will put it away.
            if (failureKey == PatientSuppliedKey ||
                failureKey == "RR_ConnectedWork_NoStorageOnArrival")
            { return ConnectedWorkPhase.Completed; }
            return base.TerminalPhaseFor(failureKey);
        }

        public override ConnectedWorkIntent TryPlan(Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (work == null || !work.CanOperate || campaign == null || pawn == null || !pawn.Spawned ||
                pawn.Map == null || pawn.carryTracker == null || !campaign.OwnsMap(pawn.Map))
            { return null; }
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }

            Map home = pawn.Map;
            List<Map> connected = ConnectedWorkScan.ConnectedMaps(campaign, home, pawn);
            for (int index = 0; index < connected.Count; index++)
            {
                Map other = connected[index];
                if (work.DestinationRecentlyRefused(pawn, other)) { continue; }
                PortalRouteStep step;
                bool pending;
                if (!work.Routes.TryNextStep(home, other, out step, out pending)) { continue; }
                if (step != null && step.Destination != null &&
                    !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
                { continue; }

                // Collect on the side the worker already stands on first: one crossing beats two.
                ConnectedWorkIntent fromHere = TryPlanSupply(pawn, work, home, other, step);
                if (fromHere != null) { return fromHere; }
                ConnectedWorkIntent fromThere = TryPlanSupply(pawn, work, other, home, step);
                if (fromThere != null) { return fromThere; }
            }
            return null;
        }

        public override string RevalidateAtFetchSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            if (source == null || source.Destroyed || !source.Spawned || pawn == null ||
                pawn.carryTracker == null || source.Map != pawn.Map ||
                source.GetUniqueLoadID() != intent.SourceThingLoadId || source.stackCount < 1)
            { return "RR_ConnectedWork_ObjectGone"; }
            // The patient may have been treated, healed, moved or died while the worker
            // walked here. Checking before the pickup avoids carrying medicine nobody needs.
            if (StillNeeded(intent, source.def) < 1) { return PatientSuppliedKey; }
            if (!HaulAIUtility.PawnCanAutomaticallyHaul(pawn, source, false))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            int wanted = Math.Min(intent.RequestedCount, source.stackCount);
            if (wanted < 1 || pawn.carryTracker.MaxStackSpaceEver(source.def) < 1)
            { return "RR_ConnectedWork_CannotCarry"; }
            if (!pawn.CanReserveAndReach(source, PathEndMode.ClosestTouch, pawn.NormalMaxDanger(), 1, wanted))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            return null;
        }

        public override Job FetchJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.FetchJobDefName);
            if (definition == null || source == null || pawn == null || pawn.carryTracker == null)
            { return null; }
            int count = Math.Min(intent.RequestedCount, source.stackCount);
            count = Math.Min(count, pawn.carryTracker.MaxStackSpaceEver(source.def));
            int needed = StillNeeded(intent, source.def);
            if (needed > 0) { count = Math.Min(count, needed); }
            if (count < 1) { return null; }
            Job job = JobMaker.MakeJob(definition, source);
            job.count = count;
            return job;
        }

        public override string RevalidateAtStoreSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (intent == null || cargo == null || cargo != intent.Cargo || cargo.Destroyed ||
                cargo.GetUniqueLoadID() != intent.CargoLoadId)
            { return "RR_ConnectedWork_CargoGone"; }
            if (StillNeeded(intent, cargo.def) < 1) { return PatientSuppliedKey; }

            // Definitive native storage choice, on the map the worker is standing on. Core's
            // medicine search is map-wide, so any storage this map accepts will be found.
            IntVec3 cell;
            if (!StoreUtility.TryFindBestBetterStorageFor(cargo, pawn, pawn.Map,
                StoragePriority.Unstored, pawn.Faction, out cell, out IHaulDestination _))
            { return "RR_ConnectedWork_NoStorageOnArrival"; }
            if (!cell.IsValid) { return "RR_ConnectedWork_NoStorageOnArrival"; }
            // Only the cell is recorded; the patient stays the final target, because the trip
            // is still for them. The plain-hauling resolve method would clear it.
            intent.RecordResolvedCellForTarget(cell);
            return null;
        }

        public override Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.DeliverJobDefName);
            if (definition == null || intent == null || cargo == null || cargo != intent.Cargo)
            { return null; }
            IntVec3 cell = intent.CandidateStoreCell;
            if (!cell.IsValid || !cell.InBounds(pawn.Map)) { return null; }
            Job job = JobMaker.MakeJob(definition, cargo, cell);
            job.count = cargo.stackCount;
            job.haulMode = HaulMode.ToCellStorage;
            return job;
        }

        // ----- candidate search, explicit-map only -----

        private ConnectedWorkIntent TryPlanSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map patientMap, PortalRouteStep step)
        {
            List<Pawn> patients = patientMap.mapPawns == null
                ? null : patientMap.mapPawns.SpawnedPawnsWithAnyHediff;
            if (patients == null || patients.Count == 0) { return null; }
            int windowStart = ConnectedWorkScan.WindowStart(patients.Count, MaximumPatientsPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < patients.Count; position++)
            {
                if (examined >= MaximumPatientsPerMap) { break; }
                examined++;
                Pawn patient = patients[position];
                if (!WantsMedicine(patient, patientMap)) { continue; }
                if (!work.ObservedAreaAllows(pawn, patientMap, patient.PositionHeld)) { continue; }
                ConnectedWorkIntent opened = TryPlanForPatient(pawn, work, fetchMap, patientMap,
                    patient, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// Whether this patient wants medicine at all. Every rule is a fact about the patient
        /// and is read from the same places Core reads it.
        /// </summary>
        private static bool WantsMedicine(Pawn patient, Map map)
        {
            if (patient == null || patient.Destroyed || patient.Dead || !patient.Spawned ||
                patient.Map != map || patient.playerSettings == null)
            { return false; }
            if (!HealthAIUtility.ShouldBeTendedNowByPlayer(patient)) { return false; }
            // `FindBestMedicine` returns null outright for NoCare and NoMeds, so carrying
            // anything for such a patient would be a trip whose delivery is never consulted.
            MedicalCareCategory care = patient.playerSettings.medCare;
            if (care == MedicalCareCategory.NoCare || care == MedicalCareCategory.NoMeds)
            { return false; }
            // `AllowsMedicine` throws on an undefined category rather than returning false,
            // so an unexpected value is treated as "no medicine" instead of as an exception.
            if (!Enum.IsDefined(typeof(MedicalCareCategory), care)) { return false; }
            return Medicine.GetMedicineCountToFullyHeal(patient) > 0;
        }

        private ConnectedWorkIntent TryPlanForPatient(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map patientMap, Pawn patient, PortalRouteStep step)
        {
            List<Thing> available = fetchMap.listerThings.ThingsInGroup(ThingRequestGroup.Medicine);
            if (available.Count == 0) { return null; }
            MedicalCareCategory care = patient.playerSettings.medCare;
            int shortfall = Shortfall(patient, patientMap, care);
            if (shortfall < 1) { return null; }

            int windowStart = ConnectedWorkScan.WindowStart(available.Count, MaximumMedicineCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < available.Count; position++)
            {
                if (examined >= MaximumMedicineCandidates) { break; }
                examined++;
                Thing stack = available[position];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != fetchMap ||
                    stack.stackCount < 1)
                { continue; }
                if (!stack.def.EverHaulable || stack.IsForbidden(Faction.OfPlayer) || stack.IsBurning())
                { continue; }
                if (stack.Position.Fogged(fetchMap)) { continue; }
                // The patient's own medical-care setting decides which medicine qualifies, so
                // a patient on herbal-or-worse never has glitterworld medicine hauled for them.
                if (!care.AllowsMedicine(stack.def)) { continue; }
                if (!work.ObservedAreaAllows(pawn, fetchMap, stack.Position)) { continue; }

                int free = stack.stackCount - work.LeasedCount(stack);
                if (free < 1) { continue; }
                int carryable = pawn.carryTracker.MaxStackSpaceEver(stack.def);
                if (carryable < 1) { continue; }
                int quantity = Math.Min(Math.Min(free, carryable), shortfall);
                if (quantity < 1) { continue; }

                ConnectedWorkIntent opened = work.Open(this, pawn, stack, patientMap,
                    IntVec3.Invalid, quantity, patient, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// How much more allowed medicine the patient needs than is already on their own map.
        ///
        /// Presence is counted across every medicine def the patient's care setting allows,
        /// not just one, for the same reason the bill family counts across every allowed
        /// ingredient: a patient with plenty of herbal medicine beside them is not short of
        /// anything, and counting only industrial medicine would have sent somebody across a
        /// gate for nothing, repeatedly.
        /// </summary>
        private static int Shortfall(Pawn patient, Map map, MedicalCareCategory care)
        {
            int required = Medicine.GetMedicineCountToFullyHeal(patient);
            if (required < 1) { return 0; }
            List<Thing> present = map.listerThings.ThingsInGroup(ThingRequestGroup.Medicine);
            int held = 0;
            int checkedStacks = 0;
            for (int index = 0; index < present.Count; index++)
            {
                if (checkedStacks >= MaximumPresenceCandidates) { break; }
                checkedStacks++;
                Thing stack = present[index];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != map)
                { continue; }
                if (stack.IsForbidden(Faction.OfPlayer) || stack.Position.Fogged(map)) { continue; }
                if (!care.AllowsMedicine(stack.def)) { continue; }
                held += stack.stackCount;
                if (held >= required) { return 0; }
            }
            return required - held;
        }

        /// <summary>How much the recorded patient still needs of this medicine.</summary>
        private static int StillNeeded(ConnectedWorkIntent intent, ThingDef def)
        {
            var patient = intent == null ? null : intent.FinalTarget as Pawn;
            if (patient == null || def == null) { return 0; }
            Map map = patient.MapHeld;
            if (map == null || !WantsMedicine(patient, map)) { return 0; }
            MedicalCareCategory care = patient.playerSettings.medCare;
            if (!care.AllowsMedicine(def)) { return 0; }
            return Shortfall(patient, map, care);
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
