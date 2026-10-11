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
    /// Where a thing came from. Three states rather than a boolean, because "not known to be
    /// odd" and "known to have come from outside" are different facts and only the second one
    /// is safe to rely on.
    /// </summary>
    public enum ThingOrigin
    {
        /// <summary>Never stamped. Treated as ordinary, but not *proven* ordinary.</summary>
        Unknown = 0,

        /// <summary>Came into existence inside a Backrooms coordinate. Odd.</summary>
        Backrooms = 1,

        /// <summary>Came into existence anywhere else. Permanently ordinary, wherever it goes.</summary>
        Outside = 2,
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
        /// <summary>Saved. Where this thing came into existence.</summary>
        private ThingOrigin origin;

        public ThingOrigin Origin
        {
            get { return origin; }
        }

        public bool IsOdd
        {
            get { return origin == ThingOrigin.Backrooms; }
        }

        /// <summary>
        /// Stamps where this thing came from, once. One-way on purpose: nothing in the game
        /// restamps a thing, because every route that could would also be a route to launder
        /// ordinary goods into odd ones or the reverse.
        /// </summary>
        public void StampOrigin(ThingOrigin value)
        {
            if (origin != ThingOrigin.Unknown || value == ThingOrigin.Unknown) { return; }
            origin = value;
        }

        /// <summary>Kept for callers that only care about the odd case.</summary>
        public void MarkOdd()
        {
            StampOrigin(ThingOrigin.Backrooms);
        }

        /// <summary>
        /// Stamps a thing the moment it first exists somewhere, which is what makes the origin
        /// model complete rather than only covering generated contents.
        ///
        /// **This is the whole rule, and it closes the laundering route by construction.**
        /// Anything that spawns anywhere other than a Backrooms coordinate is stamped
        /// <see cref="ThingOrigin.Outside"/> — permanently, wherever it is later carried. So by
        /// the time a colonist hauls a crate of cotton through a gate, that cotton is already
        /// *proven* ordinary and can never become odd.
        ///
        /// Which means anything that turns up on a Backrooms map still carrying
        /// <see cref="ThingOrigin.Unknown"/> genuinely came into existence there: rock mined out
        /// of its walls, material from a deconstructed partition, a plant cut in one of its
        /// rooms, meat butchered from something found in it. All of that is odd, and none of it
        /// was covered when only generated contents were marked.
        ///
        /// Skipped on respawn-after-load, because a saved thing already carries its answer.
        /// </summary>
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || origin != ThingOrigin.Unknown) { return; }
            Map map = parent == null ? null : parent.Map;
            if (map == null) { return; }
            // A coordinate still being generated is neither: its contents are left unstamped
            // here and stamped by the generation pass when it finishes, which is the one place
            // a coordinate's own furnishings and stock earn their mark.
            if (OddOriginService.IsGeneratingBackroomsMap(map)) { return; }
            StampOrigin(OddOriginService.IsBackroomsMap(map)
                ? ThingOrigin.Backrooms : ThingOrigin.Outside);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref origin, "rr_origin", ThingOrigin.Unknown);
            if (Scribe.mode == LoadSaveMode.LoadingVars && origin == ThingOrigin.Unknown)
            {
                // 0.7.2-dev and 0.7.3-dev saved a bare boolean. Read it so an early save does
                // not silently lose every mark it had earned.
                bool legacyOdd = false;
                Scribe_Values.Look(ref legacyOdd, "rr_oddOrigin", false);
                if (legacyOdd) { origin = ThingOrigin.Backrooms; }
            }
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
            return IsOdd == OddOriginService.IsOdd(other);
        }

        /// <summary>
        /// Carries the origin onto a piece split off this stack. Core calls this after the split
        /// and before the piece is placed, so the piece already exists and simply needs telling.
        /// Both directions: an ordinary piece split off on a coordinate must stay ordinary
        /// rather than be stamped by where it is next put down.
        /// </summary>
        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            if (origin == ThingOrigin.Unknown) { return; }
            CompRimroomsOddOrigin split = piece == null ? null : piece.TryGetComp<CompRimroomsOddOrigin>();
            if (split != null) { split.StampOrigin(origin); }
        }

        /// <summary>
        /// Adds the owner's "(odd)" to the thing's name. Keyed, so the word itself is a
        /// translation decision rather than a code one.
        /// </summary>
        public override string TransformLabel(string label)
        {
            if (!IsOdd) { return label; }
            return "RR_OddOrigin_Label".Translate(label);
        }

        public override string CompInspectStringExtra()
        {
            return IsOdd ? "RR_OddOrigin_Inspect".Translate().ToString() : null;
        }

        public override string GetDescriptionPart()
        {
            return IsOdd ? "RR_OddOrigin_Description".Translate().ToString() : null;
        }
    }
}
