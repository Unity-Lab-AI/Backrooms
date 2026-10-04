using System.Linq;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Dialling somewhere nobody asked for.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"and we need a Random address option not just company requested task and quests at
    /// specific xcorrdinates"*
    ///
    /// ## What was missing
    ///
    /// **Every coordinate in the game arrived because something named it.** A request names one,
    /// a quest names one, a contract names one, and a natural doorway is discovered by walking
    /// into it. There was no way for a player to decide *"I want to go and look"* — the gate was
    /// a delivery chute for work the company had already specified, which is the opposite of what
    /// a machine that opens doors to anywhere should feel like.
    ///
    /// A random dial is the player choosing exploration over errands, and it is the thing that
    /// makes a second and third gate worth having: owner, same message, *"up to three differnt
    /// operational gates that can call any address"*.
    ///
    /// ## Random, and the same place forever afterwards
    ///
    /// The **dial** is unpredictable; the **place** is not. The address is composed from a
    /// monotonic index — how many unknown addresses this branch has already dialled — so
    /// `CampaignServices.CreateDiscoveredCoordinate` derives its seed from the branch's own seed
    /// and that index, exactly as every other discovery does. Dial the same slot again and you
    /// get the same place; reload and it is still there. **Nothing here touches `Rand`**, which
    /// is what keeps a coordinate reproducible across a save.
    ///
    /// ## It creates an address, not a map
    ///
    /// No map is generated until somebody crosses, which is the standing mitigation on the
    /// open-map budget: *"discovering gates is free"*. So dialling costs a player nothing but the
    /// decision, and the cost arrives when they open it.
    /// </summary>
    internal static class PortalRandomDial
    {
        /// <summary>The prefix every unknown-address discovery id carries.</summary>
        internal const string DialPrefix = "unknown:";

        /// <summary>
        /// Deepest a blind dial reaches.
        ///
        /// Six, matching the natural-doorway cap the owner set — *"MaximumNaturalDepth 3 to 6"*.
        /// A blind dial is not a way to skip the depth ladder; it is a way to pick a rung at
        /// random. The draw is weighted toward the shallow end because a player who dials into a
        /// depth-six space with a starting crew has not had an adventure, they have had an
        /// accident.
        /// </summary>
        internal const int DeepestBlindDial = 6;

        /// <summary>How many unknown addresses this branch has dialled.</summary>
        internal static int DialledCount(RimroomsCampaignComponent campaign)
        {
            if (campaign == null) { return 0; }
            return campaign.Coordinates.Count(record => record != null && record.Id != null
                && record.Id.Contains(DialPrefix));
        }

        /// <summary>
        /// Dial an address nobody specified, and hand back the coordinate it resolves to.
        ///
        /// Refusals come from `CreateDiscoveredCoordinate` rather than being restated here — the
        /// branch being inactive, the coordinate ceiling, a malformed id. This adds no condition
        /// of its own, because *"not just company requested task and quests"* means the player
        /// may do this whenever the branch could discover anything at all.
        /// </summary>
        internal static CompanyActionResult Dial(RimroomsCampaignComponent campaign,
            out CoordinateRecord coordinate)
        {
            coordinate = null;
            if (campaign == null) { return CompanyActionResult.Refused("RR_Company_Inactive"); }
            int index = DialledCount(campaign);
            string discoveryId = DialPrefix + index.ToString("0000");
            int depth = BlindDepth(campaign, index);
            return campaign.CreateDiscoveredCoordinate(discoveryId, depth, out coordinate);
        }

        /// <summary>
        /// The depth a blind dial lands on, weighted toward the shallow end.
        ///
        /// Drawn from the branch's own seed and the dial index, so the slot a player is about to
        /// dial is already decided and dialling it twice cannot reroll it. The weighting is the
        /// square of a uniform draw, which puts roughly half the dials at depths one and two and
        /// leaves the deepest as a genuine rarity rather than a coin flip.
        /// </summary>
        internal static int BlindDepth(RimroomsCampaignComponent campaign, int index)
        {
            int draw = CampaignSeed.Derive(campaign.BranchSeed, "dial:depth:" + index, 1);
            if (draw < 0) { draw = ~draw; }
            int span = draw % (DeepestBlindDial * DeepestBlindDial);
            int depth = 1;
            while ((depth + 1) * (depth + 1) <= span && depth < DeepestBlindDial) { depth++; }
            return depth;
        }
    }
}
