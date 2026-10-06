using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    /// <summary>
    /// Core's own <see cref="Book"/>, with the two places a book stops listening to its comps
    /// put back.
    ///
    /// **Owner report, 2026-10-06, verbatim:** *"the starting journals still arnot correct(need to
    /// figure this out for generating ones purchased too) both are named wrong and have differ
    /// information in the "i" write up saying incorrectly that one is about nutrition and the
    /// othert is about aiming."*
    ///
    /// ## THE CAUSE WAS READ OUT OF THE SHIPPED ASSEMBLY, AND IT IS NOT WHAT IT LOOKED LIKE
    ///
    /// It looked like a missing feature. `CompRouteEvidence.TransformLabel` has returned
    /// `RR_Evidence_CompanyBookLabel` for a company-issued book since the owner answered
    /// *"Mark the company-issued ones"*. **It was never once called.**
    ///
    /// `ThingWithComps` runs the comp label chain in two places:
    ///
    /// ```csharp
    /// public override string LabelNoCount
    /// {
    ///     get
    ///     {
    ///         string text = base.LabelNoCount;
    ///         if (comps != null)
    ///         { for (...) { text = comps[i].TransformLabel(text); } }
    ///         return text;
    ///     }
    /// }
    /// ```
    ///
    /// **`Verse.Book` overrides both of them and never calls base:**
    ///
    /// ```csharp
    /// public override string LabelNoCount => title + GenLabel.LabelExtras(this, true, true);
    /// public override string LabelNoParenthesis => title;
    /// public override string DescriptionFlavor => DescriptionDetailed;
    /// ```
    ///
    /// So on a book, **no comp can change the label and no comp can reach the description at
    /// all** -- `ThingWithComps.DescriptionFlavor` is where `GetDescriptionPart()` is collected,
    /// and `Book` replaces it with its own generated text. The transform was dead code sitting in
    /// a file that read as though the feature worked.
    ///
    /// **And the wrong subjects are generated, not authored.** `Book.GenerateBook` resolves the
    /// title through `GrammarResolver` with `BookComp.Props.nameMaker`, and `AppendDoerRules`
    /// feeds it a topic for every `BookOutcomeDoer` on the def. Core's `TextBook` carries skill
    /// doers, so *nutrition* and *aiming* are Cooking and Shooting wearing their topic words.
    /// **Nothing was mis-authored and nothing was broken.** Repurposing an existing item kept its
    /// identity as well as its model -- the same lesson as the comms console coming back facing
    /// north because a cell read carries no rotation.
    ///
    /// ## WHY A SUBCLASS, AND WHY NOT THE FOUR OBVIOUS ALTERNATIVES
    ///
    /// | Candidate | Why it fails |
    /// |---|---|
    /// | Set `title` on the instance | `private string title;` on `Verse.Book`. **A subclass cannot reach a private field of its base**, and there is no setter |
    /// | Patch `TextBook`'s `nameMaker` / `descriptionMaker` | Retitles **every** textbook in the game, including one a player bought to teach Shooting |
    /// | A new `ThingDef` for the journal | **Re-opens a decision the owner already made.** `RR_RouteRecording` was exactly that and the owner's answer was *"Fold it into the record book crews already carry"* |
    /// | Reflection into the private field | Fragile across game versions, and `GenerateBook`, `LabelNoCount`, `LabelNoParenthesis` and `DescriptionDetailed` are **all virtual**: Core published an extension point and this uses it |
    ///
    /// ## THE LABEL REPAIR IS GENERIC AND THE DESCRIPTION REPLACEMENT IS NOT, DELIBERATELY
    ///
    /// The label override **restores the chain Core skipped** rather than hard-coding our own
    /// string: it asks every comp, in order, exactly as `ThingWithComps` would. So another mod's
    /// comp on a book starts working too, and an ordinary textbook is unchanged because our own
    /// transform returns its input untouched when the book is not company-issued.
    ///
    /// The description does **not** append -- it replaces, and only for a company-issued book.
    /// Appending would leave Core's generated sentence about nutrition sitting above ours, which
    /// is the exact text the owner reported. **A correction printed under a falsehood is still a
    /// falsehood on the card.** Every other book keeps Core's description byte for byte.
    ///
    /// ## WHAT THIS CLASS DELIBERATELY DOES NOT DO
    ///
    /// **It holds no state.** Everything it reads lives in `CompRouteEvidence` or the campaign
    /// record, so `ExposeData` is untouched and a save written before this class existed loads
    /// without a migration -- a `thingClass` swap on a def is save-safe only while that is true.
    ///
    /// **It leaves Core's reading outcome alone.** A field journal full of observations plausibly
    /// teaches something, the experience curve is Core's own balance, and suppressing it would
    /// mean subclassing `CompBook` to clear a `protected` list. So the title now says what the
    /// book **is**, while the stat panel still says, honestly, what reading it **does**.
    ///
    /// **One risk, named rather than hidden:** `thingClass` is single-valued, so a second mod
    /// patching `TextBook`'s class would win or lose by load order. None of the owner's 294 ships
    /// a book -- `register-query.py find book` returns zero rows -- and a checker asserts our
    /// class is the one on the def, so a future profile change reports itself instead of silently
    /// reverting to Core's generated names.
    /// </summary>
    public class RimroomsRecordBook : Book
    {
        /// <summary>
        /// The company's record comp, or null on an ordinary book.
        ///
        /// Resolved through <see cref="ThingWithComps.GetComp{T}"/> on every call rather than
        /// cached, because `Book` already caches `CompBook` in a field that a `thingClass` swap
        /// must not shadow, and a label getter is not a hot path.
        /// </summary>
        private CompRouteEvidence Record { get { return GetComp<CompRouteEvidence>(); } }

        /// <summary>
        /// Core's generated title, then the comp chain `Book` skipped.
        ///
        /// This is `ThingWithComps.LabelNoParenthesis`' body applied to `Book`'s title, which is
        /// what `Book` would have produced had it called base.
        /// </summary>
        public override string LabelNoParenthesis
        {
            get
            {
                string text = base.LabelNoParenthesis;
                List<ThingComp> parts = AllComps;
                for (int index = 0; index < parts.Count; index++)
                {
                    ThingComp part = parts[index];
                    if (part != null) { text = part.TransformLabel(text); }
                }
                return text;
            }
        }

        /// <summary>
        /// The transformed name plus the extras `Book` appends.
        ///
        /// **Built from the transformed name rather than by transforming the finished string**,
        /// so quality and damage survive. `TransformLabel` replaces what it is given, and a comp
        /// handed `"theory of nutrition (good)"` would have returned a label with the quality
        /// thrown away -- which is a second defect to ship while fixing the first.
        /// </summary>
        public override string LabelNoCount
        {
            get
            {
                return LabelNoParenthesis
                    + GenLabel.LabelExtras(this, includeHp: true, includeQuality: true);
            }
        }

        /// <summary>
        /// The company's own write-up on a company book, and Core's on everything else.
        ///
        /// **`DescriptionDetailed` is the single override that covers both surfaces**, because
        /// `Book.DescriptionFlavor` returns `DescriptionDetailed` and calls it virtually. One
        /// override, two readers -- rather than two overrides that can disagree.
        /// </summary>
        public override string DescriptionDetailed
        {
            get
            {
                CompRouteEvidence record = Record;
                return record != null && record.IsCompanyIssued
                    ? record.CompanyDescription
                    : base.DescriptionDetailed;
            }
        }
    }
}
