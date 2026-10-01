using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// A bond's name is its value.
    ///
    /// **Owner direction, 2026-10-01, verbatim:** *"they need a name that is theri value and
    /// better description and value is not correct"*, and *"now the books as bonds just say
    /// noprmal the quality which is normal"*.
    ///
    /// ## Why the comp could not do it, and never could
    ///
    /// `CompRimroomsBond.TransformLabel` returned the bond's label and **never ran once.**
    /// `Verse.Book`, decompiled from the installed 1.6 assembly, overrides the label outright:
    ///
    /// <code>
    /// public override string LabelNoCount =>
    ///     title + GenLabel.LabelExtras(this, includeHp: true, includeQuality: true);
    /// </code>
    ///
    /// `ThingWithComps.LabelNoCount` is the thing that walks `comps` calling `TransformLabel`,
    /// and `Book` replaces it. So every bond ever issued showed a randomly generated novel title
    /// and the quality suffix from `LabelExtras` — exactly what the owner reported. **Built,
    /// correct, and never reached**, which is this project's most repeated defect shape: `Discover`
    /// had no callers, `IsLiveGate` needed a mark nobody could set, five content systems were
    /// switched off at depth 1.
    ///
    /// ## The label comes back by overriding it, not by reaching into Core
    ///
    /// The first attempt wrote `Book`'s private `title` field by reflection and
    /// **`check-compliance.py` refused it, correctly**: *"a `SetValue` into a game type is a
    /// game-assembly modification that no dependency list would show"*, which is a Ludeon-terms
    /// question and not only an architecture one. Its stated boundary is behaviour added through
    /// *"Core's own ThingComp, GameComponent, WorkGiver, JobDriver and **Def extension
    /// points**"*, and `thingClass` is one of those.
    ///
    /// So the carrier's `thingClass` becomes this subclass, assigned in
    /// <see cref="BondService"/>'s static constructor beside the comp it already adds there —
    /// the same Def-field mechanism, already compliant, already proven.
    ///
    /// **An ordinary novel is untouched.** Every member here defers to `base` unless the thing
    /// carries a stamped face value, and a `Book_RimroomsBond` satisfies every `is Book` test in
    /// the game. The description and the inspect line need nothing: `CompRimroomsBond` supplies
    /// them through `GetDescriptionPart` and `CompInspectStringExtra`, which **are** consulted.
    /// </summary>
    public class Book_RimroomsBond : Book
    {
        private CompRimroomsBond Bond
        {
            get
            {
                CompRimroomsBond bond = this.TryGetComp<CompRimroomsBond>();
                return bond != null && bond.IsBond ? bond : null;
            }
        }

        public override string LabelNoCount
        {
            get
            {
                CompRimroomsBond bond = Bond;
                if (bond == null) { return base.LabelNoCount; }
                // No `LabelExtras`: a bearer bond has no meaningful quality and the hit points of
                // the paper do not change what it is payable for. The quality suffix is the whole
                // of what the owner was shown where the value should have been.
                return "RR_Bond_Label".Translate(CreditDenominations.ShortName(bond.FaceValue));
            }
        }

        public override string LabelNoParenthesis
        {
            get
            {
                CompRimroomsBond bond = Bond;
                return bond == null
                    ? base.LabelNoParenthesis
                    : "RR_Bond_Label".Translate(CreditDenominations.ShortName(bond.FaceValue)).ToString();
            }
        }
    }

    /// <summary>
    /// A bond is worth what it says it is worth.
    ///
    /// **Owner direction, 2026-10-01, verbatim:** *"value is not correct"*. A `Novel` has
    /// `MarketValue 160`, so a bond for a million credits was a hundred and sixty silver of
    /// paper: worthless to a trader, invisible in colony wealth, and a lie on its own face.
    ///
    /// ## One credit is one silver of market value, and no new number is invented
    ///
    /// The mod already has an exchange rate and a second one would be the defect this project
    /// keeps meeting. `ValuablesExchange.UnitCreditsFor` buys ordinary goods at **0.85**, so a
    /// bond sold back through the company fetches 85% of its face — a spread, which is correct —
    /// while depositing it or banking it at a beacon returns the full face value. **Neither route
    /// prints money**, and that was checked before this stat was touched.
    ///
    /// ## Why a StatPart and not a stat base
    ///
    /// The face value lives **per instance**, so no entry on a def can express it. A `StatPart`
    /// is the one mechanism that reads the thing rather than the definition, and it is additive:
    /// `MarketValue`'s own parts are untouched and every other object in the game, in this mod
    /// and in every other, gets the same answer it got before.
    ///
    /// ## The consequence, stated rather than hidden
    ///
    /// Colony wealth counts market value, so holding a fortune as paper raises raid points in a
    /// way holding it in the ledger does not. **That is the trade the bond exists to offer**, and
    /// it is already written down in `CompRimroomsBond`: *"Liquidity costs risk."* Paper can burn,
    /// be stolen, and now a raider's arithmetic can see it too.
    /// </summary>
    public sealed class StatPart_RimroomsBondValue : StatPart
    {
        public override void TransformValue(StatRequest request, ref float value)
        {
            long face = FaceOf(request);
            if (face > 0L) { value = face; }
        }

        public override string ExplanationPart(StatRequest request)
        {
            long face = FaceOf(request);
            if (face <= 0L) { return null; }
            return "RR_Bond_ValueExplanation".Translate(face.ToString("N0")).ToString();
        }

        /// <summary>The face value behind a stat request, or zero for anything that is not a bond.</summary>
        private static long FaceOf(StatRequest request)
        {
            if (!request.HasThing) { return 0L; }
            CompRimroomsBond bond = request.Thing.TryGetComp<CompRimroomsBond>();
            return bond == null || !bond.IsBond ? 0L : bond.FaceValue;
        }
    }
}
