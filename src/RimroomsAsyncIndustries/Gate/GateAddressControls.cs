using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// Setting the gate's address and opening it — on the door, with pawn controls.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"and everything that the machine needs to start up should be able to do in the worlkd
    /// from the devices themselfes with pawns controls and actrions not just in the opetaions
    /// tab,, ie setting the cordinace and all of those things need  to show"*
    ///
    /// ## What was still only in the panel
    ///
    /// A designated gate already offered eleven commands on the door — history, a blind dial,
    /// abort, crossing, equipment links, the run fallback, cutoff, kill switch, operator,
    /// calibrate, staff. **The two it did not offer were the two the owner named.** Choosing
    /// which place this gate dials, and opening it. Both existed only as buttons in
    /// `OperationsPortalNetwork`, which is the pane the same message calls a text wall.
    ///
    /// So a player could build the machine, crew it and calibrate it entirely from the world, and
    /// then had to go and find a tab to tell it where to point.
    ///
    /// ## Nothing is reimplemented
    ///
    /// `PortalAddressService.RegisterLaboratoryAddress` and `BeginSpinUp` are the same calls the
    /// pane makes, in the same order, with the same freeze notice in front of the one that
    /// generates a map. The pane is not replaced and keeps working; this is a second **surface**
    /// on one authority, which is the opposite of a second derivation of one rule.
    ///
    /// ## The freeze notice is legal here for the same reason it is legal there
    ///
    /// `RimroomsGenerationNotice.Announce` needs a caller that is not waiting on a return value,
    /// because the work has to move into a long event for the warning to draw first. A gizmo
    /// action returns void, exactly like the pane's button callback — and unlike a tick or a
    /// `CompanyActionResult` method, which is why the gate-enter path still cannot do this.
    ///
    /// ## Disabled with a reason, never hidden
    ///
    /// Owner's standing complaint was *"ive done like 50 things in a row and its still not
    /// opening"*. A command that vanishes when it cannot run teaches a player nothing; one that
    /// greys out and says why is the answer to the question they are already asking. Same rule as
    /// the board-up command and the panel's own `DrawAction`.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>The laboratory addresses remembered on this door.</summary>
        private List<PortalConnectionRecord> RememberedAddresses()
        {
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault)
            { return new List<PortalConnectionRecord>(); }
            return network.Connections
                .Where(edge => edge != null && edge.Kind == PortalConnectionKind.Laboratory &&
                    edge.First != null && edge.First.Anchor == parent)
                .ToList();
        }

        /// <summary>Setting where this gate points, and opening it, from the door.</summary>
        private IEnumerable<Gizmo> AddressGizmos()
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign == null || !campaign.CanOperate) { yield break; }

            var setAddress = new Command_Action
            {
                defaultLabel = "RR_GateAddress_SetLabel".Translate(),
                defaultDesc = "RR_GateAddress_SetDesc".Translate(),
                icon = parent.def.uiIcon,
                action = OpenAddressChoiceMenu,
            };
            // A branch that has discovered nothing has nowhere to point. Said rather than hidden,
            // because *"no addresses yet"* is the thing a player needs to hear in order to go and
            // get one -- the blind dial beside this command is how.
            if (campaign.Coordinates.Count == 0)
            { setAddress.Disable("RR_GateAddress_NoneKnown".Translate()); }
            yield return setAddress;

            List<PortalConnectionRecord> remembered = RememberedAddresses();
            var open = new Command_Action
            {
                defaultLabel = "RR_GateAddress_OpenLabel".Translate(remembered.Count.ToString()),
                defaultDesc = "RR_GateAddress_OpenDesc".Translate(),
                icon = parent.def.uiIcon,
                action = OpenConnectionChoiceMenu,
            };
            // **THE ORDER OF THESE REFUSALS IS THE ORDER A PLAYER MEETS THEM.** No address first,
            // because it is the one that is not about the machine at all; then the two states in
            // which an opening is already happening, which read as *"you have already done this"*
            // rather than as a fault.
            if (remembered.Count == 0)
            { open.Disable("RR_GateAddress_NoAddressSet".Translate()); }
            else if (IsOpening)
            { open.Disable("RR_GateAddress_AlreadyOpen".Translate()); }
            else if (IsSpinningUp)
            { open.Disable("RR_GateAddress_AlreadyRamping".Translate()); }
            yield return open;
        }

        /// <summary>
        /// Which place this gate points at.
        ///
        /// **The address code, never the raw id.** Owner, 2026-10-04: *"we dont need things like
        /// long string corrdinates list in the operations panel thing like that arnet needed only
        /// like the !A-01 address code is needed to be displayed to thew player"*. The same rule
        /// applies harder on a float menu, where there is no room for a tooltip to carry the
        /// internal identifier.
        /// </summary>
        private void OpenAddressChoiceMenu()
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign == null) { return; }
            var options = new List<FloatMenuOption>();
            foreach (CoordinateRecord record in campaign.Coordinates)
            {
                if (record == null) { continue; }
                CoordinateRecord captured = record;
                options.Add(new FloatMenuOption(
                    "RR_GateAddress_Option".Translate(captured.AddressCode,
                        captured.Depth.ToString()),
                    delegate
                    {
                        // The notice goes before the freeze, and a gizmo action is a caller that
                        // is not waiting on a return value -- which is the condition
                        // `Announce` needs in order to put the work in a long event.
                        Presentation.RimroomsGenerationNotice.Announce(captured, () =>
                            ShowOrderResult(
                                PortalAddressService.RegisterLaboratoryAddress(this, captured)));
                    }));
            }
            if (options.Count == 0) { return; }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>
        /// Which remembered address to bring up.
        ///
        /// Routed through `BeginSpinUp` rather than straight to the opening, so there is exactly
        /// one way a laboratory gate opens whichever surface started it. Owner direction,
        /// 2026-09-29: opening is *"a ramp up process that takes a bit of time"*.
        /// </summary>
        private void OpenConnectionChoiceMenu()
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            List<PortalConnectionRecord> remembered = RememberedAddresses();
            var options = new List<FloatMenuOption>();
            foreach (PortalConnectionRecord address in remembered)
            {
                PortalConnectionRecord captured = address;
                CoordinateRecord place = campaign == null ? null
                    : campaign.Coordinates.FirstOrDefault(record => record != null
                        && record.Id == captured.CoordinateId);
                string code = place == null ? captured.CoordinateId : place.AddressCode;
                options.Add(new FloatMenuOption("RR_GateAddress_OpenOption".Translate(code),
                    delegate { ShowOrderResult(BeginSpinUp(captured.Id)); }));
            }
            if (options.Count == 0) { return; }
            Find.WindowStack.Add(new FloatMenu(options));
        }
    }
}
