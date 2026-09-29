using System;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// Properties for the odd-origin marker. Carries no configuration: a thing either came out
    /// of a Backrooms coordinate or it did not.
    /// </summary>
    public sealed class CompProperties_RimroomsOddOrigin : CompProperties
    {
        public CompProperties_RimroomsOddOrigin()
        {
            compClass = typeof(CompRimroomsOddOrigin);
        }
    }

    /// <summary>
    /// The mark a thing carries when it came out of a Backrooms coordinate, and the reason a
    /// player ever goes back in.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"we can add a flag to item from the back
    /// rooms like (odd) or something like that and have quests and missions and contracts and
    /// stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd) and the such
    /// for all things materials and resources ect ect that can give reason for the players to
    /// have to advance and excplore and haul and use the spaces iin the backrooms"*
    ///
    /// ## Why this shape
    ///
    /// Thirty-one cross-map work families already move real goods through a gate, and until now
    /// **nothing in the game asked for those goods by where they came from**. A contract that
    /// demands *odd* cotton cannot be filled from the colony stockpile at any price — only by
    /// going in, working the space and hauling it out. That turns the whole existing work engine
    /// into an economy, and it does it **without inventing a single item, texture or resource**,
    /// which is what keeps it inside <c>CONTENT_REUSE_POLICY.md</c>.
    ///
    /// ## The part that is easy to get wrong
    ///
    /// A marked stack must never merge with an unmarked one. If fifty odd cotton absorbs into
    /// fifty ordinary cotton the mark is laundered away, and — far worse — the reverse launders
    /// ordinary goods *into* odd ones, which would let a player satisfy every odd contract from
    /// their own fields. Core provides the exact hook for this and it is used here rather than
    /// worked around: <see cref="ThingComp.AllowStackWith"/> is consulted by
    /// <c>ThingWithComps.CanStackWith</c>, which gates <c>TryAbsorbStack</c>. Verified in source
    /// rather than assumed.
    ///
    /// The three other Core hooks this needs all exist too, so the feature needs no Harmony and
    /// no patch to a Core method:
    ///
    /// * <see cref="PostSplitOff"/> — a piece taken off an odd stack is odd. Without this,
    ///   splitting is a laundering route.
    /// * <see cref="TransformLabel"/> — the "(odd)" the owner asked for, as a keyed string so
    ///   the exact word is translatable and is not frozen by the code.
    /// * <see cref="PostExposeData"/> — one boolean, saved.
    ///
    /// ## Minified buildings
    ///
    /// The owner's own example is *"10 uninstalled electic stoves(odd)"* — a building, not a
    /// resource. Uninstalling wraps the building in a <see cref="MinifiedThing"/> and keeps the
    /// original <c>Thing</c> as its <c>InnerThing</c>, so the comp and its saved flag travel
    /// with it untouched. Reading the mark therefore has to look *through* a minified wrapper,
    /// which <see cref="OddOriginService.IsOdd"/> does.
    /// </summary>
    public sealed class CompRimroomsOddOrigin : ThingComp
    {
        /// <summary>Saved. True once the coordinate that produced this thing marked it.</summary>
        private bool odd;

        public bool IsOdd
        {
            get { return odd; }
        }

        /// <summary>
        /// Marks this thing as having come out of a Backrooms coordinate. One-way on purpose:
        /// nothing in the game clears the mark, because every route that could clear it would
        /// also be a route to launder ordinary goods into odd ones.
        /// </summary>
        public void MarkOdd()
        {
            odd = true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref odd, "rr_oddOrigin", false);
        }

        /// <summary>
        /// Refuses to merge a marked stack with an unmarked one, in either direction.
        ///
        /// Both directions matter and for different reasons. Odd absorbing ordinary would
        /// manufacture odd goods out of colony stock, which breaks the contract economy
        /// outright. Ordinary absorbing odd would quietly destroy goods the player crossed a
        /// gate to fetch, which is worse to be on the receiving end of.
        /// </summary>
        public override bool AllowStackWith(Thing other)
        {
            if (!base.AllowStackWith(other)) { return false; }
            return odd == OddOriginService.IsOdd(other);
        }

        /// <summary>
        /// Carries the mark onto a piece split off this stack. Core calls this after the split,
        /// so the piece already exists and simply needs telling.
        /// </summary>
        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            if (!odd) { return; }
            CompRimroomsOddOrigin split = piece == null ? null : piece.TryGetComp<CompRimroomsOddOrigin>();
            if (split != null) { split.MarkOdd(); }
        }

        /// <summary>
        /// Adds the owner's "(odd)" to the thing's name. Keyed, so the word itself is a
        /// translation decision rather than a code one.
        /// </summary>
        public override string TransformLabel(string label)
        {
            if (!odd) { return label; }
            return "RR_OddOrigin_Label".Translate(label);
        }

        public override string CompInspectStringExtra()
        {
            return odd ? "RR_OddOrigin_Inspect".Translate().ToString() : null;
        }

        public override string GetDescriptionPart()
        {
            return odd ? "RR_OddOrigin_Description".Translate().ToString() : null;
        }
    }
}
