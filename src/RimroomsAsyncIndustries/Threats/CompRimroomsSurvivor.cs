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
    /// ## It also carries WHAT a coordinate produced this person as, and the tell that
    /// goes with it
    ///
    /// **Owner direction, 2026-10-04, verbatim:** *"remember lsd unnerving feeling with
    /// all things ie events random spanwns, enemies, allies, nuetrals"*. Every inhabitant
    /// family now has one exact wrong detail, and this is where a player reads it --
    /// **on the pawn, for as long as the pawn exists.** The letters fire once and scroll
    /// away; `THREAT_DESIGN_SHEETS.md` wants *"a visible or otherwise accessible
    /// warning"* and forbids colour or sound as the only cue.
    ///
    /// **THE CLASS NAME IS NOW NARROWER THAN THE JOB, and that is recorded rather than
    /// renamed.** This comp already sits on the human race def, is carried dormant by
    /// every pawn in the game, is saved and already prints an inspect line -- a second
    /// comp on the same def would double the per-pawn cost across thousands of pawns to do
    /// the same job. Renaming would mean touching the patch that attaches it and buys no
    /// behaviour at all.
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

        /// <summary>
        /// Saved. The `RimroomsInhabitantDef` a coordinate produced this person as, or
        /// empty for everybody else in the game.
        ///
        /// Stored as a defName rather than a resolved def because this is saved on a pawn
        /// that can outlive a content change: a family removed from the package must leave
        /// the pawn standing and silent, not throw on load.
        /// </summary>
        private string inhabitantFamily;

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
            Scribe_Values.Look(ref inhabitantFamily, "rr_inhabitantFamily");
        }

        /// <summary>Marks what a coordinate produced this person as.</summary>
        public void MarkInhabitant(string familyDefName)
        {
            if (!string.IsNullOrEmpty(familyDefName)) { inhabitantFamily = familyDefName; }
        }

        /// <summary>The one exact wrong detail about this person, or null.</summary>
        public string InhabitantTell
        {
            get
            {
                if (string.IsNullOrEmpty(inhabitantFamily)) { return null; }
                RimroomsInhabitantDef family =
                    DefDatabase<RimroomsInhabitantDef>.GetNamedSilentFail(inhabitantFamily);
                if (family == null || string.IsNullOrEmpty(family.tellKey)) { return null; }
                return family.tellKey.Translate().ToString();
            }
        }

        public override string CompInspectStringExtra()
        {
            // **THE TELL COMES FIRST and it outlives the letter.** A player who dismissed
            // the announcement, or who is back a dozen openings later, reads here why this
            // person is wrong. The passage offer is state; the tell is what the thing IS.
            var lines = new List<string>();
            string tell = InhabitantTell;
            if (!string.IsNullOrEmpty(tell)) { lines.Add(tell); }
            if (IsSurvivor) { lines.Add("RR_Survivor_Inspect".Translate().ToString()); }
            return lines.Count == 0 ? null : string.Join("\n", lines.ToArray());
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
