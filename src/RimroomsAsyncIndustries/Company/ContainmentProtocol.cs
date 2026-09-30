using System.Collections.Generic;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The company's standing order for what happens when containment fails: **cut every open
    /// connection.**
    ///
    /// ## What "security procedures" turned out to mean
    ///
    /// Row 761 asks for *"containment rooms, security procedures, staff debrief, quarantine,
    /// alarm and escape response"*, and *"security procedures"* is the one item in it with no
    /// obvious shape. It was settled by looking for machinery that already exists rather than
    /// by inventing a system, and two things already existed:
    ///
    /// * `PersonnelRoles` has carried a **`security`** role since the hiring layer shipped,
    ///   scored on Shooting and Melee; and
    /// * `CompRimroomsGate.TriggerEmergencyCutoff()` is a public `CompanyActionResult` entry
    ///   point that closes a live connection **and starts the return window**, so one call
    ///   both shuts the door and brings the crew home.
    ///
    /// So a security procedure here is a **standing order the player sets once and the branch
    /// executes without being asked** — which is exactly what a procedure is, as against an
    /// order, and it is the only kind of security rule this mod can honour without inventing
    /// a guard AI. One order, because one is what the existing machinery supports honestly:
    /// *when something gets loose, do we slam the doors?*
    ///
    /// ## Why it is a setting and not just behaviour
    ///
    /// Cutting a connection is **consequential and irreversible for that opening**: it burns
    /// the return window, it strands nobody but it does hurry everybody, and a player running
    /// a long extraction may well decide that a rattling platform at home is the lesser
    /// problem. Invariant 28 wants every rule learnable, and a door that slams for reasons the
    /// player never agreed to is the opposite. So it is on by default — the safe reading — and
    /// it can be turned off, and the branch says which it is.
    ///
    /// ## What it deliberately does not do
    ///
    /// * **It never re-decides what a breach is.** <see cref="ContainmentWatch"/> reports that
    ///   Core's own `CompHoldingPlatformTarget.isEscaping` is set; nothing here forms a second
    ///   opinion about whether a subject is getting out.
    /// * **It never opens anything, moves anybody, or touches a subject.** It calls one
    ///   existing method on gates that are already open, and that method is the same one the
    ///   player's own cutoff button calls, so the two can never disagree.
    /// * **It fires once per breach**, not once per tick of a breach. A procedure that
    ///   re-triggered would re-enter emergency on a gate already in emergency; the guard is
    ///   `TriggerEmergencyCutoff`'s own `IsEmergency` test plus the latch here, so the letter
    ///   the player reads arrives once.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py family security`. The family is already swept, and its standing
    /// position is that this mod keeps its own threat and containment loops in Core terms and
    /// never requires a security mod to function. Nothing here reads a weapon, a turret, a
    /// faction or a defensive structure, so a profile full of security content changes nothing
    /// about it; and because the response is *cut the connection*, a branch with no security
    /// staff at all still gets the procedure, which is the point of a procedure.
    /// </summary>
    public static class ContainmentProtocol
    {
        /// <summary>
        /// Where the standing order lives. On the campaign component rather than in mod
        /// settings, because it is a decision this branch made in this save: a second colony
        /// in a second save may reasonably answer differently, and mod settings are shared
        /// across every save on the machine.
        /// </summary>
        public static bool CutOnBreach(RimroomsCampaignComponent campaign)
        { return campaign == null || campaign.CutConnectionsOnBreach; }

        /// <summary>
        /// Flip the standing order. Returns <see cref="CompanyActionResult.Existing"/> rather
        /// than refusing when the order is already what was asked for, so a double click is
        /// harmless and reads as harmless.
        /// </summary>
        public static CompanyActionResult SetCutOnBreach(RimroomsCampaignComponent campaign,
            bool cut)
        {
            if (campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Company_Unavailable"); }
            if (campaign.CutConnectionsOnBreach == cut) { return CompanyActionResult.Existing(); }
            campaign.SetCutConnectionsOnBreach(cut);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// The procedure itself, run from the company tick.
        ///
        /// Ordered so the cheap test comes first: the latch is a bool, and
        /// <see cref="ContainmentWatch.AnyBreach"/> reads a list that is built at most once
        /// per tick and is empty on any branch that holds nothing. A colony with no holding
        /// platform pays for one bool and one empty-list walk.
        /// </summary>
        public static void TickProcedure(RimroomsCampaignComponent campaign)
        {
            if (campaign == null || !campaign.CanOperate) { return; }
            bool breach = ContainmentWatch.AnyBreach();
            if (!breach)
            {
                // Rearmed only when nothing anywhere is getting out, so a second subject
                // starting to escape during the same incident does not slam the doors twice.
                campaign.ClearBreachResponded();
                return;
            }
            if (!CutOnBreach(campaign) || campaign.BreachResponded) { return; }
            campaign.NoteBreachResponded();
            Execute(campaign);
        }

        /// <summary>
        /// Cut every connection this company currently has open, and say so once.
        ///
        /// Also the body of the player's own **sound the alarm** button, so a manual alarm and
        /// an automatic one do exactly the same thing. Two code paths for "slam the doors"
        /// would be two chances to disagree about what that means.
        /// </summary>
        private static int Execute(RimroomsCampaignComponent campaign)
        {
            List<Map> maps = Find.Maps;
            if (maps == null) { return 0; }
            int cut = 0;
            for (int mapIndex = 0; mapIndex < maps.Count; mapIndex++)
            {
                Map map = maps[mapIndex];
                if (map == null || map.listerBuildings == null || !campaign.OwnsMap(map))
                { continue; }
                List<Building> buildings = map.listerBuildings.allBuildingsColonist;
                for (int index = 0; index < buildings.Count; index++)
                {
                    CompRimroomsGate gate = buildings[index].TryGetComp<CompRimroomsGate>();
                    if (gate == null || !gate.IsDesignated || !gate.IsOpening) { continue; }
                    // The player's own cutoff button calls this same method. It refuses a gate
                    // that is not open and leaves a gate already in emergency alone, so the
                    // count below is the number of connections this actually closed.
                    if (gate.TriggerEmergencyCutoff().Success) { cut++; }
                }
            }
            if (cut > 0)
            {
                Find.LetterStack.ReceiveLetter("RR_Letter_ContainmentCutLabel".Translate(),
                    "RR_Letter_ContainmentCutText".Translate(cut),
                    LetterDefOf.NegativeEvent);
            }
            return cut;
        }

        /// <summary>
        /// **Sound the alarm now.** The player-facing action, on the gate console beside the
        /// company call.
        ///
        /// A procedure a player can only wait for is not a procedure they can practise, and
        /// this is also the honest answer to *"alarm"* in row 761 as a **noun**: a thing the
        /// branch can pull. It refuses rather than silently doing nothing when there is
        /// nothing open, because a button that reports success while closing zero connections
        /// teaches a player that the alarm does not work.
        /// </summary>
        public static CompanyActionResult SoundTheAlarm(RimroomsCampaignComponent campaign)
        {
            if (campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Company_Unavailable"); }
            // Latched with the automatic path so the procedure cannot fire again on top of a
            // manual alarm for the same incident.
            campaign.NoteBreachResponded();
            return Execute(campaign) > 0
                ? CompanyActionResult.Applied()
                : CompanyActionResult.Refused("RR_Containment_NothingOpen");
        }
    }
}
