using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    public sealed class CompProperties_RimroomsSurvivor : CompProperties
    {
        public CompProperties_RimroomsSurvivor()
        {
            compClass = typeof(CompRimroomsSurvivor);
        }
    }

    /// <summary>
    /// The interaction that turns *finding* a survivor into *gaining* one.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"lost pawns"*, in a list of what can be found
    /// inside a coordinate. 0.8.2-dev placed them — alive, neutral, and carryable out. This is
    /// the piece that was honestly marked missing: without it, a survivor was scenery you could
    /// pick up rather than a person you could save.
    ///
    /// ## Offering passage, not recruiting
    ///
    /// There is no negotiation, no recruitment chance and no prisoner step. Somebody who has
    /// been lost in the Backrooms and meets a team with a way out **wants to leave**, and making
    /// a player roll for that would be a worse story and a worse game.
    ///
    /// ## It is also what makes them able to leave at all
    ///
    /// This is the part that matters structurally. The traversal rule is absolute: **an
    /// inhabitant may never decide anything about a gate.** A survivor who has not joined is an
    /// inhabitant, so they cannot cross — the only way out for them is to be carried, exactly
    /// like anything else found down there.
    ///
    /// Joining makes them a colonist, and `PortalTraversalPolicy` then permits them to cross on
    /// their own, through the same single chokepoint everything else goes through. **Nothing
    /// here special-cases a gate**, and that is deliberate: the rule is enforced in one place
    /// and this feature is one more caller that obeys it rather than an exception to it.
    ///
    /// ## Dormant unless marked
    ///
    /// The comp sits on the human race def, so **every pawn in the game carries it**. It does
    /// nothing at all unless a coordinate marked this particular person as a survivor it
    /// produced — the same dormant-until-designated pattern the gate, emergence and credit
    /// beacon comps use on Core buildings.
    /// </summary>
    public sealed class CompRimroomsSurvivor : ThingComp
    {
        /// <summary>Saved. True only for somebody a coordinate produced as a survivor.</summary>
        private bool survivor;

        /// <summary>Saved. True once they have accepted passage, so the offer is not repeated.</summary>
        private bool joined;

        public bool IsSurvivor { get { return survivor && !joined; } }

        /// <summary>Marks this person as a survivor found in a coordinate.</summary>
        public void MarkSurvivor()
        {
            survivor = true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref survivor, "rr_survivor", false);
            Scribe_Values.Look(ref joined, "rr_survivorJoined", false);
        }

        public override string CompInspectStringExtra()
        {
            return IsSurvivor ? "RR_Survivor_Inspect".Translate().ToString() : null;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (!IsSurvivor) { yield break; }
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead) { yield break; }

            var offer = new Command_Action
            {
                defaultLabel = "RR_Survivor_Offer".Translate(),
                defaultDesc = "RR_Survivor_OfferDesc".Translate(),
                icon = TexCommand.ForbidOff,
                action = delegate { Accept(pawn); },
            };

            // Somebody has to actually be there to make the offer. A survivor cannot be
            // recruited from the other side of a gate by a player looking at a map.
            if (!AnyColonistPresent(pawn))
            { offer.Disable("RR_Survivor_NobodyHere".Translate()); }
            yield return offer;
        }

        private static bool AnyColonistPresent(Pawn survivorPawn)
        {
            Map map = survivorPawn.Map;
            if (map == null || map.mapPawns == null) { return false; }
            IReadOnlyList<Pawn> present = map.mapPawns.AllPawnsSpawned;
            if (present == null) { return false; }
            for (int index = 0; index < present.Count; index++)
            {
                Pawn candidate = present[index];
                if (candidate == null || candidate == survivorPawn) { continue; }
                if (candidate.IsColonist && !candidate.Dead && !candidate.Downed) { return true; }
            }
            return false;
        }

        private void Accept(Pawn pawn)
        {
            if (joined) { return; }
            joined = true;

            pawn.SetFaction(Faction.OfPlayer);
            // Guest status is cleared explicitly: a pawn generated without a faction can carry
            // guest state that would otherwise leave a new colonist reading as a visitor.
            if (pawn.guest != null) { pawn.guest.SetGuestStatus(null); }

            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign != null)
            { campaign.RecordEvent("RR_Event_SurvivorJoined", pawn.LabelShortCap, pawn.LabelShortCap); }

            Find.LetterStack.ReceiveLetter(
                "RR_Survivor_JoinedLabel".Translate(),
                "RR_Survivor_JoinedText".Translate(pawn.LabelShortCap),
                LetterDefOf.PositiveEvent,
                new TargetInfo(pawn.Position, pawn.Map));
        }
    }
}
