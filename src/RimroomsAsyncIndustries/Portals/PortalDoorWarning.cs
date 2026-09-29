using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// Warns before somebody deconstructs a way into the Backrooms.
    ///
    /// **Owner answer, 2026-09-29, verbatim:** *"we with minify i guess dont worry about it, can we
    /// at least do a rim style pop up warning ull lose valuable access to the backrooms and will
    /// have to find your own way back in"*.
    ///
    /// ## This deliberately relaxes an earlier direction
    ///
    /// The direction before it was *"natruals can not be destoryed or moved"*. The owner's answer
    /// is *"dont worry about it"* — so this mod does **not** fight Core over destructibility. It
    /// could not do so honestly anyway: Core decides both at the **def** level
    /// (`def.destroyable`, `def.building.IsDeconstructible`), and changing those would make every
    /// door in every colony indestructible for every player and every other mod.
    ///
    /// So the rule became **informed consent instead of prohibition**. A player may close their own
    /// way in. They may not do it by accident. That sits better with *"this is all open eneded they
    /// can play how they choose"* than a prohibition would have.
    ///
    /// ## Why a map sweep and not a comp on every door
    ///
    /// The obvious shape is a comp on `Door` that ticks and watches for the designation. It would
    /// also mean **every door in every colony** running this check forever, to catch something that
    /// happens perhaps twice in a playthrough.
    ///
    /// The connection list is small, bounded by the branch's own coordinate cap, and knows exactly
    /// which doors matter. So the sweep reads from there instead, on a slow cadence, and colonies
    /// with no portals in them do nothing at all.
    /// </summary>
    public sealed class PortalDoorWarningMapComponent : MapComponent
    {
        /// <summary>Slow on purpose. A designation sits until a colonist reaches it.</summary>
        private const int SweepInterval = 120;

        /// <summary>
        /// Doors already warned about, so cancelling and re-designating asks again but leaving a
        /// designation standing does not nag. Not saved: a reload may ask once more, which is the
        /// harmless direction for this to fail in.
        /// </summary>
        private readonly HashSet<int> warned = new HashSet<int>();

        public PortalDoorWarningMapComponent(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % SweepInterval != 0) { return; }
            if (map == null || map.designationManager == null) { return; }
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null) { return; }

            IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
            for (int index = 0; index < edges.Count; index++)
            {
                PortalConnectionRecord edge = edges[index];
                if (edge == null) { continue; }
                // A laboratory gate is a machine the branch built and may unbuild. Nothing is lost
                // that cannot be rebuilt, so it gets no warning: warning about ordinary
                // construction is how a player learns to click through warnings.
                if (edge.Kind == PortalConnectionKind.Laboratory) { continue; }
                Consider(edge.First);
                Consider(edge.Second);
            }
        }

        private void Consider(PortalEndpointRecord endpoint)
        {
            Thing anchor = endpoint == null ? null : endpoint.Anchor;
            if (anchor == null || !anchor.Spawned || anchor.Destroyed || anchor.Map != map) { return; }
            bool doomed = map.designationManager.DesignationOn(anchor, DesignationDefOf.Deconstruct) != null
                || map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall) != null;
            if (!doomed)
            {
                // Cleared by hand or carried out; either way the next designation asks again.
                warned.Remove(anchor.thingIDNumber);
                return;
            }
            if (!warned.Add(anchor.thingIDNumber)) { return; }

            Thing subject = anchor;
            Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                "RR_Portals_RemoveWayInConfirm".Translate(),
                delegate { /* Confirmed. The designation stands and the work proceeds. */ },
                delegate { ClearDesignations(subject); },
                destructive: true,
                title: "RR_Portals_RemoveWayInTitle".Translate()));
        }

        /// <summary>
        /// Cancelling the dialog cancels the order. Nothing else is touched — the door, the
        /// connection and the coordinate are all left exactly as they were.
        /// </summary>
        private void ClearDesignations(Thing anchor)
        {
            if (anchor == null || anchor.Destroyed || anchor.Map != map || map.designationManager == null)
            { return; }
            Designation deconstruct = map.designationManager.DesignationOn(anchor, DesignationDefOf.Deconstruct);
            if (deconstruct != null) { map.designationManager.RemoveDesignation(deconstruct); }
            Designation uninstall = map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall);
            if (uninstall != null) { map.designationManager.RemoveDesignation(uninstall); }
            warned.Remove(anchor.thingIDNumber);
        }
    }
}
