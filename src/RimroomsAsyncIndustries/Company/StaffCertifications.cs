using System.Collections.Generic;
using RimroomsAsyncIndustries.Personnel;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>What one person has been trained to do, and when.</summary>
    public sealed class CertificationRecord : IExposable
    {
        internal string crewLoadId;
        internal string crewName;
        internal string certificationDefName;
        internal int earnedTick = -1;

        public string Name { get { return crewName; } }
        public string CertificationDefName { get { return certificationDefName; } }
        public int EarnedTick { get { return earnedTick; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref crewLoadId, "rr_certCrewLoadId");
            Scribe_Values.Look(ref crewName, "rr_certCrewName");
            Scribe_Values.Look(ref certificationDefName, "rr_certDefName");
            Scribe_Values.Look(ref earnedTick, "rr_certEarnedTick", -1);
        }
    }

    /// <summary>
    /// The branch's register of who has been trained to do what.
    ///
    /// **Owner direction, verbatim:** *"Add configurable company roles, staff schedules,
    /// certifications, training jobs, field history, trust/stress/exposure and equipment
    /// familiarity; preserve pawn autonomy and vanilla skill/trait systems"*.
    ///
    /// ## Shaped exactly like the exposure register, for the same reasons
    ///
    /// Identity is the pawn's **load id string**, never a `Pawn` field. A colonist who leaves,
    /// dies or is captured must not be held alive by the branch's paperwork — the reasoning that
    /// retired every live reference from `LostPawnRegister`'s design and that
    /// <see cref="ExposureRecord"/> already follows. A name is carried alongside purely so a
    /// readout can still say who, after they are gone.
    ///
    /// Unbounded on purpose: what a branch has trained its people to do is the thing the player
    /// built, and discarding the oldest would make a veteran look like a novice.
    ///
    /// ## Every certification this ships is read by something
    ///
    /// That rule is `RimroomsProjectDef`'s and it is the one worth keeping: *"an unlock a player
    /// is told about and that changes nothing is worse than no unlock: it is a lie on the card."*
    /// `proof-certifications.py` asserts that every shipped certification defName appears in a
    /// source file that acts on it. Three ship, each with one named consumer:
    ///
    /// | Certification | What reads it |
    /// |---|---|
    /// | `RR_Cert_GateOperator` | `GateSpinUp` — a trained operator dials faster |
    /// | `RR_Cert_FieldAnalyst` | `EvidenceReview` — qualifies to sign off a report |
    /// | `RR_Cert_ReserveTechnician` | `NativeGateServicing` — reconditioning is less work |
    ///
    /// **Security and medical logistics have no certification, deliberately.** There is no
    /// existing surface that would act on one, and a fourth and fifth card promising nothing is
    /// exactly what the project tree refuses by leaving transport and orbital support without a
    /// tier 0. Stated rather than padded.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        private List<CertificationRecord> certifications = new List<CertificationRecord>();

        internal void ExposeCertifications()
        {
            Scribe_Collections.Look(ref certifications, "rr_certifications", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && certifications == null)
            { certifications = new List<CertificationRecord>(); }
        }

        /// <summary>Everything this branch has trained anybody to do.</summary>
        public IReadOnlyList<CertificationRecord> Certifications { get { return certifications; } }

        /// <summary>Whether this person holds this certification.</summary>
        public bool HasCertification(Pawn pawn, string certificationDefName)
        {
            if (pawn == null || certifications == null
                || string.IsNullOrEmpty(certificationDefName)) { return false; }
            string loadId = pawn.GetUniqueLoadID();
            for (int index = 0; index < certifications.Count; index++)
            {
                CertificationRecord record = certifications[index];
                if (record == null) { continue; }
                if (record.crewLoadId != loadId) { continue; }
                if (string.Equals(record.certificationDefName, certificationDefName,
                    System.StringComparison.Ordinal))
                { return true; }
            }
            return false;
        }

        /// <summary>
        /// Every certification this person holds, resolved, in a stable order.
        ///
        /// A def that has left the package is skipped rather than throwing, which is why the
        /// record stores a name: a save outlives a content change.
        /// </summary>
        public List<RimroomsCertificationDef> CertificationsOf(Pawn pawn)
        {
            var held = new List<RimroomsCertificationDef>();
            if (pawn == null || certifications == null) { return held; }
            string loadId = pawn.GetUniqueLoadID();
            List<RimroomsCertificationDef> all = RimroomsCertificationDef.AllInOrder();
            for (int index = 0; index < all.Count; index++)
            {
                RimroomsCertificationDef candidate = all[index];
                if (candidate == null) { continue; }
                if (HasCertification(pawn, candidate.defName)) { held.Add(candidate); }
            }
            return held;
        }

        /// <summary>
        /// Records that somebody finished the training.
        ///
        /// **Idempotent, and that is the honest answer to a bill being run twice.** The recipe is
        /// an ordinary repeatable bill and `RecipeDef.AvailableOnNow` is asked about the *bench*,
        /// not about the pawn, so there is no way to withdraw it from one particular person who is
        /// already trained. A repeat therefore records nothing new — a set, not a counter — and
        /// the message is only sent the first time, so the player is never told twice that
        /// somebody qualified.
        /// </summary>
        internal CompanyActionResult GrantCertification(Pawn pawn, RimroomsCertificationDef certification)
        {
            if (pawn == null || certification == null)
            { return CompanyActionResult.Refused("RR_Cert_Unavailable"); }
            certifications = certifications ?? new List<CertificationRecord>();
            if (HasCertification(pawn, certification.defName))
            { return CompanyActionResult.Existing(); }

            certifications.Add(new CertificationRecord
            {
                crewLoadId = pawn.GetUniqueLoadID(),
                crewName = pawn.LabelShortCap,
                certificationDefName = certification.defName,
                earnedTick = Find.TickManager == null ? 0 : Find.TickManager.TicksGame,
            });
            RecordEvent("RR_Event_Certified", pawn.LabelShortCap, pawn.LabelShortCap,
                certification.LabelCap);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// How much a trained operator takes off the dial, applied **once**.
        ///
        /// Shallower than the branch's per-connection familiarity discount and deliberately not
        /// compounding, for the reason <see cref="OperatorExposureFactor"/> already states: a
        /// person is not a record. They have been trained or they have not, and the training does
        /// not deepen with repetition the way a filed report teaches the branch.
        ///
        /// **It stacks with exposure rather than replacing it**, because the two are different
        /// facts — having been taught the procedure, and having personally walked that address.
        /// Both land above the floor, which is what keeps a well-worn route quick and never free.
        /// </summary>
        public const float OperatorCertificationFactor = 0.85f;

        /// <summary>
        /// The dial discount a trained operator earns, or 1 for none.
        ///
        /// Returns a multiplier rather than applying anything, so the gate stays the only thing
        /// that decides what spin-up work is — there is exactly one place that arithmetic lives.
        /// </summary>
        public float CertificationDialFactor(Pawn gateOperator)
        {
            return HasCertification(gateOperator, "RR_Cert_GateOperator")
                ? OperatorCertificationFactor : 1f;
        }
    }
}

namespace RimroomsAsyncIndustries.Personnel
{
    /// <summary>
    /// Records a certification against the pawn who finished the training bill.
    ///
    /// **One class for every certification.** The recipe is matched to its certification through
    /// <see cref="RimroomsCertificationDef.ForRecipe"/>, so shipping another one is a def edit and
    /// no new code — the same reason `RimroomsGateEquipmentDef` describes roles in data rather
    /// than in a type per role.
    ///
    /// Modelled directly on `RecipeWorker_RimroomsGateAssembly`, which is this package's existing
    /// answer to *a bill completing has to change company state*.
    /// </summary>
    public sealed class RecipeWorker_RimroomsCertification : RecipeWorker
    {
        /// <summary>
        /// Whether the bill is offered at all.
        ///
        /// Asked of the **bench**, not of a pawn — that is Core's signature and it is the reason
        /// <see cref="Company.RimroomsCampaignComponent.GrantCertification"/> has to be
        /// idempotent rather than this refusing a trained person. What this can honestly answer
        /// is whether the branch exists to hold the record at all.
        /// </summary>
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            Company.RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            return campaign != null && campaign.CanOperate
                && RimroomsCertificationDef.ForRecipe(recipe) != null;
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            if (billDoer == null) { return; }
            RimroomsCertificationDef certification = RimroomsCertificationDef.ForRecipe(recipe);
            if (certification == null) { return; }
            Company.RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            if (campaign == null) { return; }

            Company.CompanyActionResult result =
                campaign.GrantCertification(billDoer, certification);
            // Announced only when it actually recorded something new. A repeatable bill run twice
            // must not tell the player somebody qualified twice.
            if (!result.Success || result.AlreadyApplied) { return; }
            Messages.Message(
                "RR_Cert_Earned".Translate(billDoer.LabelShortCap, certification.LabelCap),
                billDoer, MessageTypeDefOf.PositiveEvent, false);
        }
    }
}
