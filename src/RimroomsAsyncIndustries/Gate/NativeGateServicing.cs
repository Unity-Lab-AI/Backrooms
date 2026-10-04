using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// Gate servicing: the assembly holds a condition that decays, how fast depends on how
    /// well the room is kept and whether it has power, and somebody skilled tops it back up.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"kinda like maintaince for growth vats
    /// questionable ethitcs so pawns dont have to always do it but there is a cool down dead
    /// zone where its fine"*, following *"maintained amounts of maintance and research on
    /// equipment but not crazy amounts"*.
    ///
    /// ## The reference, read properly
    ///
    /// *Questionable Ethics Enhanced* is **profile row 182**, and the owner was pointing at
    /// how **its cloning and organ vats** handle upkeep. Its own building description states
    /// the model plainly:
    ///
    /// > *"Requires regular maintenance by a skilled scientist and doctor. A sterile room will
    /// > significantly decrease the maintenance required. If the vat loses power, it will
    /// > rapidly lose maintenance."*
    ///
    /// Three ideas, and all three are better than a plain timer:
    ///
    /// 1. a condition that **decays continuously** rather than a countdown to a service date;
    /// 2. **the room modulates the decay** — keep it clean and the thing barely needs you;
    /// 3. **losing power degrades it fast**, so neglect compounds.
    ///
    /// Point 2 is the *"cool down dead zone where its fine"*. It is not a grace timer bolted
    /// on: it falls out of the model, because a well-kept room decays so slowly that nobody is
    /// called for a long stretch, and a filthy one calls somebody constantly. The player
    /// controls the dead zone by looking after the place.
    ///
    /// **Nothing of that mod is copied, referenced or depended on.** Its defs and assembly are
    /// untouched, this works with it absent, and the idea was read from its public description
    /// exactly as every other profile row has been. The register exists so that shapes proven
    /// elsewhere can inform the design without importing anything.
    ///
    /// ## How it connects to what is already here
    ///
    /// The model is worth having partly because it plugs into systems this mod already built,
    /// rather than sitting beside them:
    ///
    /// * **cleanliness** is maintained by the cleaning family, which already crosses a gate,
    ///   so a gate chamber on either side of a portal is kept by the same work;
    /// * **power** is the kill switch and the whole native power binding — throwing the cutoff
    ///   now has a cost beyond closing the gate, because an unpowered assembly degrades fast;
    /// * **skill** reuses the `Research` work type that calibration already uses, so no new
    ///   work type is added and the player's existing priorities keep meaning what they meant.
    ///
    /// ## Lapsing stops the next opening. It never slams one shut.
    ///
    /// A gate with no condition left **refuses to open**. It does **not** close an opening
    /// already running: ending one for a bookkeeping reason would strand whoever is on the far
    /// side, and the emergency-return window exists for real emergencies rather than for
    /// paperwork. The kill switch closes a gate on purpose; this decides whether one may be
    /// opened at all.
    ///
    /// ## What it costs
    ///
    /// Work time by a skilled colonist, and nothing else. No material is consumed, because the
    /// direction's ceiling is explicit — *"not crazy amounts"* — and a resource cost on a
    /// recurring chore is how maintenance systems turn into a tax.
    ///
    /// The work happens at the console, not the door. A door is a `Building_Door` that pawns
    /// path through constantly and reserving one for a long job would fight ordinary traffic;
    /// the console already has an interaction cell and a proven job pattern.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>Condition remaining, in ticks of ordinary wear. Ten days at full.</summary>
        private int serviceConditionTicks = -1;

        private const int ServiceCapacityTicks = 600000;

        /// <summary>
        /// Below this fraction, somebody is offered the work. Above it nobody is, which is
        /// what stops the continuous topping-up a "below full" test would cause.
        /// </summary>
        private const float ServiceRequestThreshold = 0.25f;

        /// <summary>Multiplier applied while the assembly has no power.</summary>
        private const float UnpoweredWearFactor = 8f;

        /// <summary>Extra multiplier while a connection is actually held open.</summary>
        private const float OpenWearFactor = 3f;

        public float ReconditionWorkRequired { get { return 1400f; } }

        /// <summary>
        /// How much of the reconditioning work a trained technician saves.
        ///
        /// `RR_Cert_ReserveTechnician` is earned by running the training bill at a machining
        /// table. Owner's row: *"certifications, training jobs"*.
        /// </summary>
        public const float TechnicianServiceFactor = 0.7f;

        /// <summary>
        /// The work this particular person needs to recondition the gate.
        ///
        /// **Asked per pawn rather than folded into the flat figure**, because that is what a
        /// certification is: a fact about somebody, not about the gate. The flat
        /// <see cref="ReconditionWorkRequired"/> stays exactly what it was, so an untrained
        /// branch services the gate on the same terms it always did and the training can only
        /// ever make it cheaper.
        /// </summary>
        public float ReconditionWorkFor(Pawn servicer)
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign == null || servicer == null) { return ReconditionWorkRequired; }
            return campaign.HasCertification(servicer, "RR_Cert_ReserveTechnician")
                ? ReconditionWorkRequired * TechnicianServiceFactor
                : ReconditionWorkRequired;
        }

        /// <summary>A gate that has never been serviced starts in full condition.</summary>
        public int ServiceConditionTicks
        { get { return serviceConditionTicks < 0 ? ServiceCapacityTicks : serviceConditionTicks; } }

        public float ServiceConditionFraction
        { get { return Mathf.Clamp01(ServiceConditionTicks / (float)ServiceCapacityTicks); } }

        public float ServiceConditionDays { get { return ServiceConditionTicks / (float)GenDate.TicksPerDay; } }

        /// <summary>No condition left. The gate will not open until it is reconditioned.</summary>
        public bool ServiceLapsed
        { get { return IsDesignated && ServiceConditionTicks <= 0; } }

        /// <summary>
        /// Whether anybody should be offered the work. False across the whole dead zone, which
        /// in a well-kept room is most of the time.
        /// </summary>
        public bool ServiceWanted
        {
            get
            {
                return IsDesignated && !IsOpening &&
                    ServiceConditionFraction < ServiceRequestThreshold;
            }
        }

        /// <summary>
        /// How fast condition is being lost right now, as a multiple of ordinary wear. Exposed
        /// because the player needs to see *why* a gate keeps needing attention, and the answer
        /// is almost always the room.
        /// </summary>
        public float ServiceWearFactor
        {
            get
            {
                float factor = RoomWearFactor();
                if (!NativeElectricalAvailable()) { factor *= UnpoweredWearFactor; }
                if (IsOpening && !IsEmergency) { factor *= OpenWearFactor; }
                return factor;
            }
        }

        /// <summary>
        /// Cleanliness of the room the assembly stands in, turned into a wear multiplier.
        ///
        /// Core's cleanliness runs from roughly -5 in a filth-covered room to about +2 in a
        /// sterile one. A sterile room wears at half rate and a filthy one at triple, which is
        /// the *"a sterile room will significantly decrease the maintenance required"* half of
        /// the model. Clamped at both ends so no room configuration can stop wear entirely or
        /// run it away.
        /// </summary>
        private float RoomWearFactor()
        {
            if (parent == null || !parent.Spawned || parent.Map == null) { return 1f; }
            Room room = parent.GetRoom();
            if (room == null || room.PsychologicallyOutdoors) { return 1f; }
            float cleanliness = room.GetStat(RoomStatDefOf.Cleanliness);
            // +2 sterile -> 0.5x, 0 neutral -> 1x, -5 filthy -> 3x.
            float factor = cleanliness >= 0f
                ? Mathf.Lerp(1f, 0.5f, Mathf.Clamp01(cleanliness / 2f))
                : Mathf.Lerp(1f, 3f, Mathf.Clamp01(-cleanliness / 5f));
            return Mathf.Clamp(factor, 0.5f, 3f);
        }

        internal void ExposeServicing()
        {
            Scribe_Values.Look(ref serviceConditionTicks, "rr_gateServiceConditionTicks", -1);
        }

        /// <summary>
        /// One tick of wear. The room stat is only sampled occasionally: `GetStat` walks the
        /// room's contents, and asking every tick for every gate would be real cost for an
        /// answer that changes slowly.
        /// </summary>
        internal void TickServicing()
        {
            if (!IsDesignated) { return; }
            if (serviceConditionTicks < 0) { serviceConditionTicks = ServiceCapacityTicks; }
            if (serviceConditionTicks <= 0) { serviceConditionTicks = 0; return; }
            if (Find.TickManager.TicksGame % ServiceSampleInterval != 0) { return; }
            int wear = Mathf.Max(1, Mathf.RoundToInt(ServiceWearFactor * ServiceSampleInterval));
            serviceConditionTicks = Mathf.Max(0, serviceConditionTicks - wear);
        }

        /// <summary>How often wear is applied, and how often the room is sampled.</summary>
        private const int ServiceSampleInterval = 250;

        /// <summary>
        /// Whether this pawn could recondition the assembly now. Mirrors the calibration gate
        /// so the two console jobs cannot disagree about who is allowed to stand there.
        /// </summary>
        public bool CanRecondition(Pawn pawn)
        {
            if (!ServiceWanted || pawn == null || pawn.Dead || pawn.Downed) { return false; }
            if (HasPortalOwnerFault) { return false; }
            Thing console = Console;
            return console != null && !console.Destroyed && console.Spawned &&
                pawn.Spawned && pawn.Map == console.Map;
        }

        /// <summary>Back to full condition in one visit, exactly as a vat top-up works.</summary>
        public CompanyActionResult CompleteReconditioning(Pawn pawn)
        {
            if (!CanRecondition(pawn)) { return CompanyActionResult.Refused("RR_NativeGate_ServiceNotWanted"); }
            serviceConditionTicks = ServiceCapacityTicks;
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_GateReconditioned", parent.GetUniqueLoadID()); }
            RecordGateActivity("RR_Gate_Reconditioned", CurrentOpeningId);
            return CompanyActionResult.Applied();
        }

        /// <summary>The servicing line for the gate's inspect string.</summary>
        internal string ServicingReadout()
        {
            if (!IsDesignated) { return null; }
            if (ServiceLapsed) { return "RR_Gate_ServiceLapsed".Translate().ToString(); }
            string days = ServiceConditionDays.ToString("F1");
            string wear = ServiceWearFactor.ToString("F1");
            return (ServiceWanted ? "RR_Gate_ServiceWanted" : "RR_Gate_ServiceFine")
                .Translate(days, wear).ToString();
        }
    }
}
