using System.Collections.Generic;
using System.Linq;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The kinds of thing a player can do to satisfy a corporation request.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"never offer only one path but multiple success
    /// routes"*.
    ///
    /// The kinds exist so that "two routes" means something. Two ways of delivering the same
    /// object to the same shelf is **one route wearing two hats**, and a rule that counted it as
    /// two would be satisfied by text rather than by design. Hence the load-bearing rule in
    /// <see cref="RimroomsRequestDef.ConfigErrors"/>: at least two routes, **of at least two
    /// different kinds**.
    /// </summary>
    public enum SuccessRouteKind
    {
        /// <summary>Bring the thing back.</summary>
        Deliver = 0,

        /// <summary>Bring the *record* back instead of the thing. Analysis rather than salvage.</summary>
        Document = 1,

        /// <summary>Satisfy it with a different item of the same capability.</summary>
        Substitute = 2,

        /// <summary>Buy the shortfall through procurement rather than recovering it.</summary>
        Purchase = 3,

        /// <summary>A staff account, where a crew saw what a record would have shown.</summary>
        Testify = 4,

        /// <summary>Refuse the stated task and complete a related one the corporation also wants.</summary>
        Redirect = 5,
    }

    /// <summary>
    /// One way to succeed at a request.
    ///
    /// Deliberately declarative. A route says *what satisfies it*, never *how to check it*, so
    /// that a route can be read off a card before the player accepts anything — which is the
    /// point of promising routes at all.
    /// </summary>
    public sealed class RimroomsSuccessRoute
    {
        public SuccessRouteKind kind = SuccessRouteKind.Deliver;

        /// <summary>Keyed string shown on the card. Never raw text: this is player-facing.</summary>
        public string labelKey;

        /// <summary>Keyed string explaining what this route asks for.</summary>
        public string descriptionKey;

        /// <summary>Deliver, Substitute and Purchase: what, and how many.</summary>
        public string thingDefName;
        public int count = 1;

        /// <summary>Document and Testify: which completed log satisfies it.</summary>
        public string logKind;

        /// <summary>Redirect: the project or request accepted in place of this one.</summary>
        public string redirectTo;

        /// <summary>
        /// True when this route was added from branch capability rather than authored in XML.
        /// Derived routes are shown differently and, critically, **never counted toward the
        /// two-route floor** — see <see cref="RimroomsRequestDef.ConfigErrors"/>.
        /// </summary>
        [Unsaved(false)]
        public bool derived;

        public IEnumerable<string> ConfigErrors(string owner)
        {
            if (string.IsNullOrEmpty(labelKey))
            { yield return owner + ": a success route needs a labelKey; a player reads it on the card."; }
            if (string.IsNullOrEmpty(descriptionKey))
            { yield return owner + ": a success route needs a descriptionKey."; }
            if (count < 1) { yield return owner + ": a route asking for fewer than one of something asks for nothing."; }

            bool wantsThing = kind == SuccessRouteKind.Deliver || kind == SuccessRouteKind.Substitute
                || kind == SuccessRouteKind.Purchase;
            if (wantsThing && string.IsNullOrEmpty(thingDefName))
            { yield return owner + ": a " + kind + " route must name what it wants."; }

            bool wantsLog = kind == SuccessRouteKind.Document || kind == SuccessRouteKind.Testify;
            if (wantsLog && string.IsNullOrEmpty(logKind))
            { yield return owner + ": a " + kind + " route must name which log satisfies it."; }

            if (kind == SuccessRouteKind.Redirect && string.IsNullOrEmpty(redirectTo))
            { yield return owner + ": a Redirect route must name what it redirects to."; }
        }
    }

    /// <summary>
    /// A corporation request: something the company asks a branch to do.
    ///
    /// **This is the offer shape the campaign chart calls step 4**, built before any request
    /// content exists, so that the first request ever written has to satisfy the absolutes rather
    /// than being retrofitted to them.
    ///
    /// Two owner absolutes are enforced here **at def load**, in addition to
    /// `tools/check-campaign-absolutes.py`. Two layers is deliberate: the checker catches a bad
    /// def before it ships, and `ConfigErrors` catches one that arrives from a patch, another mod
    /// or a hand edit after shipping.
    ///
    /// | Absolute | Enforced by |
    /// |---|---|
    /// | *"never offer only one path but multiple success routes"* | two authored routes of two different kinds |
    /// | *"missions and quests and offeres and trades are never time senstive"* | **there is no expiry field to set** |
    ///
    /// The second one is enforced by absence, which is the strongest way available: a deadline
    /// cannot be configured onto a request because the shape has nowhere to put one.
    /// </summary>
    public sealed class RimroomsRequestDef : Def
    {
        /// <summary>Which campaign arc this belongs to. See `docs/CAMPAIGN_CHART.md`.</summary>
        public int arc = 1;

        /// <summary>
        /// Part of the fixed tutorial line rather than generated. The tutorial requests are
        /// ordered and taught once each; everything after the hinge is generated.
        /// </summary>
        public bool tutorial;

        /// <summary>Order within the tutorial line. Ignored for generated requests.</summary>
        public int tutorialOrder;

        public long paymentUsd;
        public long bonusUsd;

        /// <summary>Requests that must be complete before this one is offered.</summary>
        public List<string> prerequisiteRequests = new List<string>();

        /// <summary>
        /// The authored floor. **At least two, of at least two different kinds.** Branch
        /// capability may add more at runtime, but never fewer, and a derived route can never
        /// substitute for one of these.
        /// </summary>
        public List<RimroomsSuccessRoute> successRoutes = new List<RimroomsSuccessRoute>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(label))
            { yield return "A request must have a label; a player reads it on the card."; }
            if (string.IsNullOrEmpty(description))
            { yield return "A request must have a description."; }
            if (paymentUsd < 0 || bonusUsd < 0)
            { yield return "A request cannot pay a negative amount."; }

            if (successRoutes == null || successRoutes.Count < 2)
            {
                yield return "A request must offer at least TWO success routes. Owner direction: "
                    + "\"never offer only one path but multiple success routes\".";
                yield break;
            }

            // The rule that makes the count mean something. Two Deliver routes differing only in
            // which shelf the item lands on is one route wearing two hats.
            int kinds = successRoutes.Select(route => route.kind).Distinct().Count();
            if (kinds < 2)
            {
                yield return "A request's routes must be of at least two different kinds; "
                    + successRoutes.Count + " routes were all " + successRoutes[0].kind
                    + ", which is one route written twice.";
            }

            for (int index = 0; index < successRoutes.Count; index++)
            {
                foreach (string error in successRoutes[index].ConfigErrors(defName + " route " + index))
                { yield return error; }
            }

            if (prerequisiteRequests != null && prerequisiteRequests.Contains(defName))
            { yield return "A request cannot require itself; it could never be offered."; }
        }

        /// <summary>The tutorial line in order. Sorted ordinally after the declared order.</summary>
        public static List<RimroomsRequestDef> TutorialLine()
        {
            return DefDatabase<RimroomsRequestDef>.AllDefsListForReading
                .Where(definition => definition.tutorial)
                .OrderBy(definition => definition.tutorialOrder)
                .ThenBy(definition => definition.defName, System.StringComparer.Ordinal)
                .ToList();
        }

        public static List<RimroomsRequestDef> AllInOrder()
        {
            return DefDatabase<RimroomsRequestDef>.AllDefsListForReading
                .OrderBy(definition => definition.arc)
                .ThenBy(definition => definition.tutorialOrder)
                .ThenBy(definition => definition.defName, System.StringComparer.Ordinal)
                .ToList();
        }
    }
}
