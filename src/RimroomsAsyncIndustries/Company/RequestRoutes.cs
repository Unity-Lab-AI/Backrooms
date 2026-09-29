using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Procurement;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The routes a request actually offers this branch, right now.
    ///
    /// **Owner answer at the fork, 2026-09-29: *"1 and 3"*** — a fixed set per request family
    /// **and** an authored floor plus derived extras. Those are the same answer at two strengths,
    /// and both halves matter:
    ///
    /// * **The authored floor is what makes the absolute unbreakable.** Every family declares at
    ///   least two routes of different kinds in XML, checked at def load and by the checker. A
    ///   branch with nothing can always see two ways through.
    /// * **The derived extras are what make a developed branch feel developed.** A branch with a
    ///   supply catalogue can buy the shortfall. A branch whose crew actually saw the thing can
    ///   testify to it. Neither is available to a branch that has not built toward it.
    ///
    /// **A derived route can never substitute for an authored one.** They are added on top and
    /// marked, and the floor is counted before they exist. That ordering is the whole safety
    /// property: if deriving ever returned nothing — no catalogue, no witnesses, a broken save —
    /// the request still offers two ways through.
    /// </summary>
    public static class RequestRoutes
    {
        /// <summary>
        /// Authored routes first, then whatever this branch's capability adds.
        ///
        /// Sorted ordinally within each group, never by list order or hash order, because this is
        /// a list a player reads and picks from.
        /// </summary>
        public static List<RimroomsSuccessRoute> Available(RimroomsRequestDef definition,
            RimroomsCampaignComponent campaign)
        {
            var routes = new List<RimroomsSuccessRoute>();
            if (definition == null) { return routes; }

            // The floor. Taken exactly as authored, and never filtered by capability: a route a
            // player cannot currently take is still a route they can see and work toward, which
            // is more useful than a card that quietly shrinks when the branch is poor.
            if (definition.successRoutes != null)
            {
                routes.AddRange(definition.successRoutes
                    .OrderBy(route => (int)route.kind)
                    .ThenBy(route => route.labelKey, System.StringComparer.Ordinal));
            }

            foreach (RimroomsSuccessRoute extra in Derived(definition, campaign))
            {
                // Never duplicate a kind the family already authored for the same thing. An extra
                // that repeats an authored route adds a line to the card and nothing else.
                if (routes.Any(existing => existing.kind == extra.kind &&
                    existing.thingDefName == extra.thingDefName)) { continue; }
                routes.Add(extra);
            }
            return routes;
        }

        /// <summary>
        /// Extras this branch has earned. Deliberately few and deliberately concrete: each one
        /// corresponds to a thing the player built, bought or learned.
        /// </summary>
        private static IEnumerable<RimroomsSuccessRoute> Derived(RimroomsRequestDef definition,
            RimroomsCampaignComponent campaign)
        {
            if (campaign == null || !campaign.CanOperate) { yield break; }

            foreach (RimroomsSuccessRoute authored in definition.successRoutes ?? new List<RimroomsSuccessRoute>())
            {
                // PURCHASE. A branch whose corporate catalogue carries the wanted thing may buy
                // the shortfall instead of recovering it. Checked against the catalogue rather
                // than against the account, because affording it is the player's problem and a
                // route they cannot currently pay for is still a route.
                if (!string.IsNullOrEmpty(authored.thingDefName) &&
                    authored.kind != SuccessRouteKind.Purchase &&
                    CatalogueCarries(authored.thingDefName))
                {
                    yield return new RimroomsSuccessRoute
                    {
                        kind = SuccessRouteKind.Purchase,
                        labelKey = "RR_Route_PurchaseLabel",
                        descriptionKey = "RR_Route_PurchaseDesc",
                        thingDefName = authored.thingDefName,
                        count = authored.count,
                        derived = true,
                    };
                }

                // TESTIFY. A branch that has completed a log of the right kind has somebody who
                // can speak to it. The log is the evidence that a crew was actually there.
                if (!string.IsNullOrEmpty(authored.logKind) &&
                    authored.kind != SuccessRouteKind.Testify &&
                    CompletedLogs(campaign, authored.logKind) > 0)
                {
                    yield return new RimroomsSuccessRoute
                    {
                        kind = SuccessRouteKind.Testify,
                        labelKey = "RR_Route_TestifyLabel",
                        descriptionKey = "RR_Route_TestifyDesc",
                        logKind = authored.logKind,
                        derived = true,
                    };
                }
            }
        }

        /// <summary>
        /// Whether the parent corporation's catalogue carries a thing.
        ///
        /// **Internal because the eligibility filter asks the same question** and two
        /// copies of it would eventually disagree about what is orderable. One source,
        /// two callers -- the derived-route half here and `CanTakeRoute` in
        /// `RequestGeneration.cs`.
        /// </summary>
        internal static bool CatalogueCarries(string thingDefName)
        {
            foreach (RimroomsProcurementCatalogDef entry in
                DefDatabase<RimroomsProcurementCatalogDef>.AllDefsListForReading)
            {
                if (entry != null && entry.thingDefName == thingDefName) { return true; }
            }
            return false;
        }

        private static int CompletedLogs(RimroomsCampaignComponent campaign, string logKind)
        {
            switch ((logKind ?? "").ToLowerInvariant())
            {
                case "route": return campaign.CompletedLogCount(RimroomsCampaignComponent.LogKind.Route);
                case "distortion": return campaign.CompletedLogCount(RimroomsCampaignComponent.LogKind.Distortion);
                case "entity": return campaign.CompletedLogCount(RimroomsCampaignComponent.LogKind.Entity);
                default: return 0;
            }
        }

        /// <summary>
        /// The floor, counted without any capability at all.
        ///
        /// Used by the offline proof. If this ever returns fewer than two distinct kinds for a
        /// shipped request, the absolute is broken no matter what deriving would have added.
        /// </summary>
        public static int AuthoredKinds(RimroomsRequestDef definition)
        {
            if (definition == null || definition.successRoutes == null) { return 0; }
            return definition.successRoutes.Select(route => route.kind).Distinct().Count();
        }
    }
}
