using System.Linq;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// How much the branch can stand behind a record, as a band rather than a number.
    ///
    /// A percentage would invite a player to read precision that is not there. The question a
    /// player actually has is *can I sell this as a finding, or do I need to go back*, and four
    /// bands answer that.
    /// </summary>
    public enum EvidenceConfidence
    {
        /// <summary>Nobody has worked on it. A thing on a shelf is not a finding.</summary>
        Unverified = 0,

        /// <summary>Recorded, but thin, or still contradicted by one of the branch's own people.</summary>
        Weak = 1,

        /// <summary>Analysed and corroborated. The ordinary state of a finished record.</summary>
        Fair = 2,

        /// <summary>Analysed, corroborated and signed off, with nothing outstanding.</summary>
        Strong = 3,
    }

    /// <summary>
    /// Confidence scoring, derived from what the branch already knows.
    ///
    /// **Owner direction, verbatim:** *"Implement evidence provenance/custody/type/value/risk/
    /// confidence, sample storage, research value, sale value, client deliverable, archive, chain
    /// of custody, and destruction choice"*. Everything on that row shipped except **confidence
    /// scoring and a destruction workflow**, and both are here.
    ///
    /// ## Derived, never stored, and that is the whole design
    ///
    /// Confidence is a **function of the record**: how many observations it carries, whether the
    /// branch's own people agree about them, whether the disputes were settled, whether it was
    /// analysed, and whether a second pair of eyes endorsed it. Every one of those facts is
    /// already on the record and already saved.
    ///
    /// So storing a score would be a **second copy that could disagree with its own inputs** —
    /// settle a dispute and a stored score would still say *contradicted* until something
    /// remembered to recompute it. That is the same reasoning `CoordinateMaterials` gives for
    /// rebuilding a palette rather than saving one, and it is why nothing here is scribed and no
    /// save migration was needed.
    ///
    /// ## It is load-bearing, not a readout
    ///
    /// An unlock a player is told about that changes nothing is worse than no unlock. So
    /// confidence **moves the transfer price**: the corporation pays more for a finding the
    /// branch can stand behind than for a book somebody carried out of a room. See
    /// <see cref="ConfidenceValueFactor"/>. That is also the honest reading of the row's own
    /// pairing of *confidence* with *value* on one line.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Observations a record needs before it reads as more than an anecdote.
        ///
        /// Two, because one observation is a single person's account of a single thing and the
        /// whole investigation chain is built on crews corroborating each other.
        /// </summary>
        private const int ObservationsForFair = 2;

        /// <summary>
        /// How confident the branch is in this record.
        ///
        /// Walked from the bottom up rather than scored and bucketed, because each band has a
        /// stated reason and a player should be able to read the band and know which fact to go
        /// and fix.
        /// </summary>
        public EvidenceConfidence ConfidenceOf(EvidenceRecord record)
        {
            if (record == null) { return EvidenceConfidence.Unverified; }
            // A thing on a shelf is not a finding. `Located` and `Recovered` mean nobody has
            // worked on it, and `Missing` means the branch has not got it at all.
            if (record.Status != EvidenceStatus.Secured && record.Status != EvidenceStatus.Analyzed)
            { return EvidenceConfidence.Unverified; }

            int observations = record.Observations == null ? 0 : record.Observations.Count;
            if (observations == 0) { return EvidenceConfidence.Unverified; }

            // **An unsettled dispute caps it at Weak, whatever else is true.** Two of the
            // branch's own people contradicting each other on the record is the one thing that
            // cannot be made up for by volume -- which is exactly why `ReviewAnalysis` refuses to
            // sign off while one is outstanding. The two rules agree by construction.
            if (UnsettledDisputes(record).Any()) { return EvidenceConfidence.Weak; }

            if (record.Status != EvidenceStatus.Analyzed) { return EvidenceConfidence.Weak; }
            if (observations < ObservationsForFair) { return EvidenceConfidence.Weak; }

            // **A report whose detail did not survive cannot be Strong.** `DetailsUnavailable` is
            // an older save whose report kept its analyst and lost its observations; there is
            // nothing there to stand behind, which is the same thing that makes a review return
            // the record rather than endorse it.
            if (record.AnalysisReport != null && record.AnalysisReport.DetailsUnavailable)
            { return EvidenceConfidence.Weak; }

            // Signed off, by somebody who was not the analyst, and endorsed. Anything less is a
            // finished record nobody has checked, which is Fair and honestly so.
            return record.Reviewed && record.ReviewEndorsed
                ? EvidenceConfidence.Strong
                : EvidenceConfidence.Fair;
        }

        /// <summary>
        /// What confidence does to what the corporation will pay.
        ///
        /// Deliberately **never below one for a record the branch did the work on**: the
        /// multiplier rewards verification rather than punishing a thin record, because a penalty
        /// for handing over something unverified would push a player to sit on findings, and
        /// sitting on findings is what the containment charge already costs them for.
        /// </summary>
        public float ConfidenceValueFactor(EvidenceRecord record)
        {
            switch (ConfidenceOf(record))
            {
                case EvidenceConfidence.Strong: return 1.4f;
                case EvidenceConfidence.Fair: return 1.15f;
                default: return 1f;
            }
        }
    }
}
