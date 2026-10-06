using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Investigation;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What the corporation asks for after it stops naming things.
    ///
    /// ## The owner's decision, and what each half of it governs
    ///
    /// ***"Both — filter picks the family, card never shrinks."*** Two rules at two different
    /// levels, and conflating them was the mistake the question was asked to avoid:
    ///
    /// | Level | Rule | Lives in |
    /// |---|---|---|
    /// | **Eligibility** | a family is offered only if the branch can take **two routes of two different kinds** | here |
    /// | **The card** | shows the **full authored floor, unfiltered**, plus derived extras | `RequestRoutes.Available`, untouched |
    ///
    /// Net effect: *you never see a request you cannot finish, and the request you do see never
    /// hides a route from you.* Nothing from 0.11.1-dev is reversed.
    ///
    /// ## Why the filter has to be able to refuse
    ///
    /// **Invariant 136.** A filter whose every clause is trivially true is a hollow knob that
    /// looks like a feature, and this project has deleted four research projects and three
    /// hollow tier-2 constants for exactly that. So each clause below names something a branch
    /// can genuinely lack:
    ///
    /// | Route | Takeable when | Refuses when |
    /// |---|---|---|
    /// | Deliver, Substitute | the branch holds one, or the catalogue carries it | a thing it has never seen and cannot order |
    /// | Purchase | the catalogue carries it **and** the branch is in contact | before contact, procurement does not exist |
    /// | Document | the branch has visited a coordinate | you cannot document a place you have never been |
    /// | Testify | a living employee witnessed that kind | no crew has seen one |
    /// | Research | the project exists, is unfinished, and **qualifies** | short of the logs its tier demands |
    /// | Redirect | the target project or request exists | a def that is not installed |
    ///
    /// The qualification clause reuses <see cref="ProjectQualificationFailureKey"/> rather than
    /// re-deriving it, so the filter can never disagree with the research screen about whether a
    /// project is reachable.
    ///
    /// ## And why the pace has no clock
    ///
    /// The next request appears when the open one is resolved, and never otherwise. **Two offer
    /// clocks were retired in 0.11.0-dev** and none is coming back: chart §1.1 says the only clock
    /// is the gate. Variety comes from asking for the **least-asked** eligible family first, not
    /// from a timer.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How many times this family has been put on the table, ever.
        ///
        /// Counts resolved and open alike, so a family the branch turned down is not immediately
        /// asked again ahead of one it has never seen.
        /// </summary>
        private int TimesAsked(string defName)
        {
            int count = 0;
            for (int index = 0; index < requests.Count; index++)
            {
                RequestRecord record = requests[index];
                if (record != null && record.requestDefName == defName) { count++; }
            }
            return count;
        }

        /// <summary>
        /// Whether the branch could actually pursue one route right now.
        ///
        /// **This is the filter's teeth.** Every arm can refuse; see the table on this class.
        /// </summary>
        internal bool CanTakeRoute(RimroomsSuccessRoute route)
        {
            if (route == null) { return false; }
            switch (route.kind)
            {
                case SuccessRouteKind.Deliver:
                case SuccessRouteKind.Substitute:
                    // Either the branch has some, or it can order some. A generated request
                    // naming a thing it has never seen and cannot buy is a dead card.
                    return OwnedThingCount(route.thingDefName) > 0 ||
                        RequestRoutes.CatalogueCarries(route.thingDefName);

                case SuccessRouteKind.Purchase:
                    // Buying goes through the parent corporation's catalogue, which a branch that
                    // has not made contact does not have.
                    return corporationContact && RequestRoutes.CatalogueCarries(route.thingDefName);

                case SuccessRouteKind.Document:
                    // A log is written about somewhere the crew has been.
                    return coordinates.Count > 0;

                case SuccessRouteKind.Testify:
                    // Somebody has to have seen it, and still be here to say so.
                    return LivingWitnessCount(route.logKind) > 0;

                case SuccessRouteKind.Research:
                    return ProjectReachable(route.projectDefName);

                case SuccessRouteKind.Redirect:
                    return RedirectTargetExists(route.redirectTo);

                default:
                    return false;
            }
        }

        /// <summary>
        /// Whether a project is something this branch could start and has not finished.
        ///
        /// **Already finished is NOT reachable.** A Research route against a completed project is
        /// satisfied the moment it is offered, and a request that pays for work already done is a
        /// button that prints money. The baseline mechanism in <see cref="RouteBaseline"/> guards
        /// the general case; this refuses the specific one before it is ever offered.
        ///
        /// Qualification is asked of <see cref="ProjectQualificationFailureKey"/>, the same
        /// function the research screen uses, so the two can never disagree.
        /// </summary>
        private bool ProjectReachable(string projectDefName)
        {
            if (string.IsNullOrEmpty(projectDefName)) { return false; }
            RimroomsProjectDef definition =
                DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(projectDefName);
            if (definition == null) { return false; }
            if (ProjectCompleted(projectDefName)) { return false; }
            return ProjectQualificationFailureKey(definition) == null;
        }

        /// <summary>Whether a redirect names something that exists to be redirected to.</summary>
        private bool RedirectTargetExists(string redirectTo)
        {
            if (string.IsNullOrEmpty(redirectTo)) { return false; }
            if (DefDatabase<RimroomsProjectDef>.GetNamedSilentFail(redirectTo) != null) { return true; }
            return DefDatabase<RimroomsRequestDef>.GetNamedSilentFail(redirectTo) != null;
        }

        /// <summary>
        /// Whether a generated family may be put on the table.
        ///
        /// **Two routes, of two different kinds, that this branch can actually take.** The same
        /// shape as the rule `RimroomsRequestDef.ConfigErrors` enforces on the authored floor, but
        /// asked of the branch rather than of the def: the def rule guarantees the offer is
        /// *well formed*, this one guarantees it is *answerable*.
        /// </summary>
        internal bool FamilyEligible(RimroomsRequestDef definition)
        {
            if (definition == null || definition.tutorial || definition.successRoutes == null)
            { return false; }
            var kinds = new HashSet<SuccessRouteKind>();
            int takeable = 0;
            List<RimroomsSuccessRoute> ordered = OrderedRoutes(definition);
            for (int index = 0; index < ordered.Count; index++)
            {
                if (!CanTakeRoute(ordered[index])) { continue; }
                takeable++;
                kinds.Add(ordered[index].kind);
            }
            return takeable >= 2 && kinds.Count >= 2;
        }

        /// <summary>Every generated family this branch could be asked for right now, in order.</summary>
        public List<RimroomsRequestDef> EligibleFamilies()
        {
            var eligible = new List<RimroomsRequestDef>();
            List<RimroomsRequestDef> all = RimroomsRequestDef.AllInOrder();
            for (int index = 0; index < all.Count; index++)
            {
                if (FamilyEligible(all[index])) { eligible.Add(all[index]); }
            }
            return eligible;
        }

        /// <summary>
        /// Ask for the next thing, once the branch is past the hinge.
        ///
        /// **Least-asked first**, so the company works through the range of what it wants instead
        /// of repeating whichever family happens to be cheapest. Ties are broken ordinally and
        /// then by the branch's own seed, so the same branch asked at the same point always gets
        /// the same request — a save reloaded twice does not produce two different campaigns.
        /// </summary>
        private void OfferNextGeneratedRequest()
        {
            if (!corporationContact) { return; }
            // **ONE OFFER AWAITING AN ANSWER, NOT ONE JOB IN HAND.** This read `OpenRequest`, which
            // is offered **or accepted**, so accepting a job stopped the company ever offering
            // another until it was finished -- a branch could hold exactly one, and the owner asked
            // for *"ability to accept more than one quests at a time"*. The question being asked
            // one at a time is the part worth keeping; how many obligations the player has taken on
            // is their business.
            if (OfferedRequest != null) { return; }
            // Nothing is generated until the company has stopped naming things. Before the hinge
            // the tutorial line owns the one open slot.
            if (!PastTheHinge) { return; }

            List<RimroomsRequestDef> eligible = EligibleFamilies();
            if (eligible.Count == 0) { return; }

            int fewest = int.MaxValue;
            for (int index = 0; index < eligible.Count; index++)
            {
                int asked = TimesAsked(eligible[index].defName);
                if (asked < fewest) { fewest = asked; }
            }
            List<RimroomsRequestDef> freshest = eligible
                .Where(definition => TimesAsked(definition.defName) == fewest)
                .OrderBy(definition => definition.defName, System.StringComparer.Ordinal)
                .ToList();
            if (freshest.Count == 0) { return; }

            // Invariant 26: the list is sorted ordinally before anything is rolled against it.
            int roll = CampaignSeed.Derive(campaignSeed, "request-generation:" + requests.Count, 1);
            // **The tie is where the branch's own situation gets to speak.** Owner: *"Generate
            // bounded story variations from client/faction, coordinate, staffing, discovered
            // rules, company tier, previous outcomes, opening duration, and available
            // equipment"*. Four of those reached generation in 0.12.12-dev through
            // `CanTakeRoute`; company tier, previous outcome, opening duration and the world's
            // faction pressure did not, and this is where they land.
            //
            // **Least-asked-first is untouched**, because that is the fairness rule that stops
            // the company repeating its cheapest request forever. The weighting applies inside
            // the tie, which is exactly where this line was choosing arbitrarily.
            RimroomsRequestDef chosen = DrawWeightedFamily(freshest, roll);
            if (chosen == null) { return; }
            OfferRequest(chosen);
        }
    }
}
