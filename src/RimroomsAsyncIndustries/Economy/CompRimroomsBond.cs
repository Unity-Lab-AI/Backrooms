using System;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>Properties for the bearer-bond marker. The face value lives per instance.</summary>
    public sealed class CompProperties_RimroomsBond : CompProperties
    {
        public CompProperties_RimroomsBond()
        {
            compClass = typeof(CompRimroomsBond);
        }
    }

    /// <summary>
    /// A company bearer bond: physical, hauled, stored in a vault, and losable.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"we want also to be able to store the
    /// corprate credits(dollars since 1990 america?) in like company bonds or something that can
    /// be used easily and reposed with out leaveing a dead item or thing u are using"*, and on
    /// whether they can burn or be stolen, *"Yes — physical means physical"*.
    ///
    /// ## Three layers of money, and this is the bridge
    ///
    /// Physical valuables — silver, gold, jade, ivory — are **untouched vanilla**, and a vault
    /// full of them works exactly as it always did. The company account is the existing branch
    /// ledger: audited, weightless, and impossible to steal because it is not anywhere. A bond
    /// is the bridge between them, and it is the only one of the three that can burn.
    ///
    /// That is the whole trade-off and it is why the ledger still exists. Liquidity costs risk.
    ///
    /// ## "without leaveing a dead item"
    ///
    /// Redeeming a bond **destroys it**. There is no spent husk, no zero-value certificate
    /// cluttering a stockpile, and no object whose only remaining purpose is to be hauled to a
    /// bin. The paper is the value; when the value goes, the paper goes.
    ///
    /// ## Repurposed, not invented
    ///
    /// The bond is a Core <c>Novel</c> carrying this comp — a printed document, which is what a
    /// bearer instrument physically is. **No new item, no new texture.** A `Novel` without this
    /// comp stamped is still an ordinary novel and reads as one, so the repurposing costs the
    /// player nothing and takes nothing away.
    /// </summary>
    public sealed class CompRimroomsBond : ThingComp
    {
        /// <summary>Saved. Zero means this is an ordinary book, not a bond.</summary>
        private long faceValue;

        public long FaceValue { get { return faceValue; } }

        public bool IsBond { get { return faceValue > 0L; } }

        /// <summary>
        /// Stamps a face value, once. A bond is never revalued: every route that could rewrite
        /// a face value would be a route to print money, and there is no legitimate reason for
        /// one to exist.
        /// </summary>
        public void Issue(long value)
        {
            if (faceValue != 0L || value <= 0L) { return; }
            faceValue = value;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref faceValue, "rr_bondFaceValue", 0L);
        }

        /// <summary>
        /// Keeps bonds of different values from merging, and keeps a bond from merging with an
        /// ordinary book.
        ///
        /// `Novel` has a stack limit of one, so today nothing would merge anyway. This is here
        /// because that is a fact about a Core def rather than a guarantee: a mod that raises a
        /// book's stack limit would otherwise silently turn two bonds of different values into
        /// one, and the quieter of the two would simply cease to exist.
        /// </summary>
        public override bool AllowStackWith(Thing other)
        {
            if (!base.AllowStackWith(other)) { return false; }
            return faceValue == BondService.FaceValueOf(other);
        }

        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            if (faceValue <= 0L) { return; }
            CompRimroomsBond split = piece == null ? null : piece.TryGetComp<CompRimroomsBond>();
            if (split != null) { split.Issue(faceValue); }
        }

        public override string TransformLabel(string label)
        {
            if (!IsBond) { return label; }
            return "RR_Bond_Label".Translate(CreditDenominations.ShortName(faceValue));
        }

        public override string CompInspectStringExtra()
        {
            if (!IsBond) { return null; }
            return "RR_Bond_Inspect".Translate(faceValue.ToString("N0")).ToString();
        }

        public override string GetDescriptionPart()
        {
            if (!IsBond) { return null; }
            return "RR_Bond_Description".Translate(faceValue.ToString("N0")).ToString();
        }
    }
}
