using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// How wrong a coordinate is allowed to look, and how good the things in it are allowed to
    /// be.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"hallways can have furniture and produiction
    /// benches too remember things are almost completely fucking werid and crazy odd and scary
    /// looking the deeping in the backrooms and higher the gete quality and rtesarch levels and
    /// tech and stuff ec t ect"*.
    ///
    /// ## The correction that shaped this
    ///
    /// The previous checkpoint named a gap: archetypes were not constrained by structural
    /// family, so *"a hallway can be furnished as a nursery"*. **The owner's answer was that
    /// this is not a bug.** A production bench standing in a corridor is exactly right for the
    /// setting — the wrongness *is* the content.
    ///
    /// So nothing here constrains an archetype to a room type. Instead **coherence decays**:
    /// a shallow coordinate looks more or less like somewhere, and a deep one stops pretending.
    ///
    /// ## Two inputs, and the second is the owner's own
    ///
    /// * **Depth** — how far in the space sits.
    /// * **The branch's own advancement** — *"higher the gete quality and rtesarch levels and
    ///   tech"*. Research finished, and the laboratory gate's own research tier.
    ///
    /// The second one matters for a reason beyond flavour: it means **a deep space is worth
    /// coming back to later**. A coordinate visited early and revisited after a hundred hours
    /// of research is a different place, without anything having been authored twice.
    ///
    /// It also keeps the two axes honest. Depth is what the player chose to risk; research is
    /// what they earned. Neither alone should be able to max the place out.
    /// </summary>
    public static class SpaceSophistication
    {
        /// <summary>Research projects finished that count as a fully advanced branch.</summary>
        private const float ResearchCeiling = 40f;

        /// <summary>Depth at which the place has entirely stopped pretending.</summary>
        private const float DepthCeiling = 6f;

        /// <summary>
        /// 0 means a space that reads as somewhere real. 1 means anything may be anywhere.
        ///
        /// **Never reaches 1 at depth alone, and never at research alone.** Both are capped
        /// below the top so that neither a reckless player nor a patient one can max the place
        /// out without being both — depth is what you chose to risk, research is what you
        /// earned, and the worst of it wants both.
        /// </summary>
        public static float Derangement(int depth, RimroomsCampaignComponent campaign)
        {
            float byDepth = Mathf.Clamp01((depth - 1f) / DepthCeiling) * 0.65f;
            float byBranch = Advancement(campaign) * 0.45f;
            return Mathf.Clamp01(byDepth + byBranch);
        }

        /// <summary>
        /// How advanced the branch is, 0 to 1, from finished research and the gate's own tier.
        ///
        /// Read live rather than saved, deliberately. Unlike the room-shape echo — which had to
        /// be snapshotted because layout is re-planned against a saved fingerprint — **room
        /// contents are generated once and never re-derived**, so reading the branch's current
        /// state here cannot desynchronise anything.
        /// </summary>
        public static float Advancement(RimroomsCampaignComponent campaign)
        {
            float research = 0f;
            if (Find.ResearchManager != null)
            {
                int finished = 0;
                List<ResearchProjectDef> all = DefDatabase<ResearchProjectDef>.AllDefsListForReading;
                for (int index = 0; index < all.Count; index++)
                {
                    if (all[index] != null && all[index].IsFinished) { finished++; }
                }
                research = Mathf.Clamp01(finished / ResearchCeiling);
            }

            // The gate's own standing counts too -- the owner named gate quality alongside
            // research. A branch that has invested in its gate is further along than one that
            // has merely read a lot.
            float gate = 0f;
            if (campaign != null)
            {
                gate = Mathf.Clamp01(campaign.DeepestReached / DepthCeiling);
            }

            return Mathf.Clamp01(research * 0.75f + gate * 0.25f);
        }

        /// <summary>
        /// The highest tech level a coordinate will produce, which rises with the branch.
        ///
        /// **What you find scales with what you can understand.** A pre-industrial branch finds
        /// pre-industrial things; one that has gone deep and researched widely starts turning up
        /// spacer equipment. That is the owner's *"higher the gete quality and rtesarch levels
        /// and tech and stuff"*, and it is also what keeps a deep space worth revisiting.
        ///
        /// Never above the archetype's own declared ceiling — a def that says it deals in
        /// industrial goods is still telling the truth.
        /// </summary>
        public static TechLevel TechCeiling(TechLevel declared, int depth,
            RimroomsCampaignComponent campaign)
        {
            float advancement = Advancement(campaign);
            float depthShare = Mathf.Clamp01((depth - 1f) / DepthCeiling);
            float combined = Mathf.Clamp01(advancement * 0.6f + depthShare * 0.4f);

            TechLevel earned;
            if (combined >= 0.85f) { earned = TechLevel.Spacer; }
            else if (combined >= 0.6f) { earned = TechLevel.Industrial; }
            else if (combined >= 0.35f) { earned = TechLevel.Medieval; }
            else { earned = TechLevel.Neolithic; }

            return (int)earned < (int)declared ? earned : declared;
        }

        /// <summary>
        /// Whether a room in this coordinate should be dressed **without regard to what kind of
        /// room it structurally is** — a workshop in a corridor, a nursery in a service passage.
        ///
        /// Rolled per room from the room's own seed, so it is stable across reloads and some
        /// rooms in a deep coordinate still read as ordinary. A space where *everything* is
        /// wrong stops being unsettling and starts being noise; the contrast is what works.
        /// </summary>
        public static bool IgnoreRoomKind(int depth, RimroomsCampaignComponent campaign,
            int seed, int roomIndex)
        {
            float derangement = Derangement(depth, campaign);
            int roll = Gen.HashCombineInt(seed, roomIndex * 4409 + 0x574F4E47);
            if (roll < 0) { roll = ~roll; }
            return (roll % 1000) / 1000f < derangement;
        }

        /// <summary>
        /// How much more likely an anomalous archetype is in this coordinate. At full
        /// derangement the strange ones outweigh the ordinary ones rather than merely matching
        /// them, because by then the ordinary ones are the surprise.
        /// </summary>
        public static float AnomalousWeightFactor(int depth, RimroomsCampaignComponent campaign)
        {
            return 1f + Derangement(depth, campaign) * 3f;
        }
    }
}
