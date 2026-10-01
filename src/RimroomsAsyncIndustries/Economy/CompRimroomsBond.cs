using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
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

        // **`TransformLabel` is GONE from this comp, because it never ran.** `Verse.Book`
        // overrides `LabelNoCount` as `title + GenLabel.LabelExtras(...)` and never walks
        // `comps`, so the method meant to name a bond was unreachable from the day it was
        // written: every bond showed a random novel title and its quality, which is exactly what
        // the owner reported. The label now comes from `Book_RimroomsBond`, the carrier's
        // `thingClass`. Keeping a method that cannot be called would be worse than the bug,
        // because it reads like the problem is solved.

        /// <summary>
        /// The two actions a player needs on a piece of paper they are holding: put it back, and
        /// make several into fewer.
        ///
        /// On the comp, because a `Book` is a selectable item and `ThingWithComps.GetGizmos`
        /// walks its comps — which is the only surface that reaches a bond on a floor. Before
        /// this, the single caller of `RedeemBondsInRadius` was a credit beacon, so a player
        /// without one had no way to put a bond back anywhere. Owner: *"the bonds i pull out i
        /// dont sdeem to be able to put them back in and and to combine them"*.
        /// </summary>
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo inherited in base.CompGetGizmosExtra()) { yield return inherited; }
            if (!IsBond || parent == null || !parent.Spawned) { yield break; }

            yield return new Command_Action
            {
                defaultLabel = "RR_Bond_DepositLabel".Translate(faceValue.ToString("N0")),
                defaultDesc = "RR_Bond_DepositDesc".Translate(),
                icon = parent.def.uiIcon,
                action = delegate { Show(BondHandling.Deposit(parent)); }
            };
            yield return new Command_Action
            {
                defaultLabel = "RR_Bond_CombineLabel".Translate(),
                defaultDesc = "RR_Bond_CombineDesc".Translate(),
                icon = parent.def.uiIcon,
                action = delegate { Show(BondHandling.Combine(parent)); }
            };
        }

        /// <summary>Says what happened, by the refusal's own key. Never silent.</summary>
        private void Show(CompanyActionResult result)
        {
            if (result.Success) { return; }
            Messages.Message((result.MessageKey ?? "RR_Bond_NoneInRange").Translate(),
                parent, MessageTypeDefOf.RejectInput, false);
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
