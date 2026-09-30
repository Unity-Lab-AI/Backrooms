using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    public class CompProperties_RimroomsEmergence : CompProperties
    {
        public CompProperties_RimroomsEmergence() { compClass = typeof(CompRimroomsEmergence); }
    }

    /// <summary>
    /// A door the player has chosen as the place a way out of the Backrooms comes up.
    ///
    /// ## Why this has to be a designation and can never be automatic
    ///
    /// 0.6.3-dev established that **a door the player built is never automatically a
    /// frontier**, because turning somebody's own wall door into a permanent way into the
    /// Backrooms would change an existing colony just by installing this mod — which
    /// `CONTENT_REUSE_POLICY.md` forbids outright.
    ///
    /// Emergence runs the other direction: the way out arrives **at** the player's own map.
    /// So the same rule applies with more force, not less. Nothing here ever picks a door.
    /// The player marks one, and only a marked door can ever be the far end of a way out.
    ///
    /// ## Dormant until marked, and it costs nothing until then
    ///
    /// This comp sits on every Core `Door` and `Autodoor`, added by an additive patch beside
    /// the existing gate comp, and holds two fields. Until somebody marks a door it does
    /// nothing at all, offers one gizmo, and takes part in no scan.
    ///
    /// ## What a mark is allowed to mean
    ///
    /// A marked door must stay on an **ordinary branch-owned map**. Marking a door inside a
    /// Backrooms coordinate is refused: a way out has to come up somewhere that is not the
    /// place it leads away from, and the containment rule already says a coordinate has no
    /// outside. The branch id is recorded at the moment of marking so a mark cannot be
    /// inherited by another company through a saved map.
    /// </summary>
    public class CompRimroomsEmergence : ThingComp
    {
        private bool designated;
        private string branchId;

        /// <summary>
        /// The place this door led to, while that place is not being held open.
        ///
        /// **Written at release, read at re-open.** A natural gate is permanently open and is
        /// never closed — what a release lets go of is the space behind it. The edge that recorded
        /// the pairing has to be removed, because every endpoint of it lives on the map being torn
        /// down, so the pairing is written here instead. Without it the door would become an
        /// ordinary marked door and the place behind it would be unreachable for ever.
        /// </summary>
        private string shelvedCoordinateId;

        /// <summary>
        /// Whether this door is a usable way home right now. Every clause is checked live
        /// rather than trusted from the saved flag, so a door that was marked and then
        /// deconstructed, moved to another map, or left behind by a different company stops
        /// being an anchor without anything having to notice and clear it.
        /// </summary>
        public bool IsDesignated
        {
            get
            {
                if (!designated || parent == null || !parent.Spawned || parent.Destroyed) { return false; }
                if (parent.Faction != Faction.OfPlayer) { return false; }
                if (!OrdinaryBranchMap(parent.Map)) { return false; }
                RimroomsCampaignComponent campaign = Campaign();
                return campaign != null && campaign.CanOperate && campaign.BranchId == branchId;
            }
        }

        /// <summary>Where a traveller stands on this side. The same rule every threshold uses.</summary>
        public IntVec3 ApproachCell
        { get { return parent == null ? IntVec3.Invalid : PortalAddressService.ApproachCellFor(parent); } }

        /// <summary>
        /// Installed. If this door carries a way through, the way through came with it.
        ///
        /// **Not on load.** `respawningAfterLoad` means the door is being restored where it
        /// already was, and a saved route is already pointing at that cell. Re-anchoring then
        /// would turn every load into a move.
        /// </summary>
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || parent == null || Current.Game == null) { return; }
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null) { return; }
            int moved = network.NotifyAnchorInstalled(parent);
            if (moved > 0)
            {
                Messages.Message("RR_Portals_WayThroughMoved".Translate(parent.LabelShortCap),
                    parent, MessageTypeDefOf.PositiveEvent, false);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref designated, "rr_emergenceDesignated", false);
            Scribe_Values.Look(ref branchId, "rr_emergenceBranchId");
            Scribe_Values.Look(ref shelvedCoordinateId, "rr_emergenceShelvedCoordinate");
        }

        /// <summary>The place this door led to, while it is shelved. Null when it is open.</summary>
        internal string ShelvedCoordinateId { get { return shelvedCoordinateId; } }

        /// <summary>Called by the release, while the edge still says where this door led.</summary>
        internal void RememberShelvedPlace(string coordinateId)
        {
            if (!string.IsNullOrWhiteSpace(coordinateId)) { shelvedCoordinateId = coordinateId; }
        }

        /// <summary>Called when the place is open again, so the door stops offering to re-open it.</summary>
        internal void ForgetShelvedPlace() { shelvedCoordinateId = null; }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            // A natural way out is a door too, and a player may order somebody through it.
            foreach (Gizmo gizmo in DoorCrossingGizmo.For(parent)) { yield return gizmo; }
            if (parent == null || !parent.Spawned) { yield break; }

            // A recorded way out to the world, offered BEFORE the faction and ordinary-map checks
            // below: the door this appears on stands inside a Backrooms coordinate and generation
            // places it with no faction at all, so both of those checks would reject it.
            //
            // This is the only player-facing route into Core's caravan formation, and it is a
            // click. Nothing automatic can reach it -- see WorldExit.cs for the narrowed
            // stranded-crew guarantee that depends on exactly that.
            RimroomsCampaignComponent worldExitCampaign = Campaign();
            if (worldExitCampaign != null && worldExitCampaign.WorldExitFor(parent) != null)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_WorldExit_LeaveLabel".Translate(),
                    defaultDesc = "RR_WorldExit_LeaveDesc".Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { Show(worldExitCampaign.LeaveThroughWorldExit(parent)); }
                };
            }

            if (parent.Faction != Faction.OfPlayer) { yield break; }
            // Never offered inside the Backrooms: a way out cannot come up in the place it
            // leads away from, and offering the command there would only ever refuse.
            if (!OrdinaryBranchMap(parent.Map)) { yield break; }

            bool marked = IsDesignated;
            yield return new Command_Action
            {
                defaultLabel = (marked ? "RR_Emergence_WithdrawLabel" : "RR_Emergence_MarkLabel").Translate(),
                defaultDesc = (marked ? "RR_Emergence_WithdrawDesc" : "RR_Emergence_MarkDesc").Translate(),
                icon = parent.def.uiIcon,
                action = delegate { Show(marked ? Withdraw() : Mark()); }
            };

            // The place this door led to, while the company is not holding it open. Offered on
            // the door rather than only in Operations because this is where a player is standing
            // when they wonder why the door no longer goes anywhere.
            if (string.IsNullOrWhiteSpace(shelvedCoordinateId)) { yield break; }
            RimroomsCampaignComponent reopenCampaign = Campaign();
            CoordinateRecord shelved = reopenCampaign == null ? null
                : reopenCampaign.Coordinates.FirstOrDefault(record => record != null &&
                    record.Id == shelvedCoordinateId);
            if (shelved == null) { yield break; }
            bool room = OpenMapBudget.CanOpenAnother;
            yield return new Command_Action
            {
                defaultLabel = "RR_Release_ReopenLabel".Translate(),
                defaultDesc = (room ? "RR_Release_ReopenDesc" : "RR_Release_ReopenNoRoomDesc")
                    .Translate(OpenMapBudget.Describe()),
                icon = parent.def.uiIcon,
                // Disabled rather than hidden when there is no room: a player at their limit
                // needs to see that this is the thing they are at the limit of.
                Disabled = !room,
                disabledReason = room ? null : "RR_Release_ReopenNoRoomDesc".Translate(OpenMapBudget.Describe()),
                action = delegate { Show(Reopen(reopenCampaign, shelved)); }
            };
        }

        /// <summary>
        /// Open the shelved place again, through the same registration path that first created it.
        ///
        /// Nothing bespoke: `RegisterNaturalAddress` generates the site and registers the edge,
        /// exactly as it did at discovery. The coordinate record and its rooms were kept, so the
        /// place that comes back is the same place -- the same rooms in the same shape. **Its
        /// contents are not**, because the interior is generated from the seed, and the player was
        /// told that before they released it.
        /// </summary>
        private CompanyActionResult Reopen(RimroomsCampaignComponent campaign, CoordinateRecord shelved)
        {
            if (campaign == null || shelved == null) { return CompanyActionResult.Refused("RR_Release_UnknownPlace"); }
            if (!OpenMapBudget.CanOpenAnother)
            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }
            CompanyActionResult registered = PortalAddressService.RegisterNaturalAddress(
                parent, ApproachCell, shelved);
            // Only forgotten once the place is genuinely back. A failed re-open must leave the
            // door still offering to try, or a transient refusal would strand the place for ever.
            if (registered.Success) { ForgetShelvedPlace(); }
            return registered;
        }

        /// <summary>
        /// Mark this door as the place a way out comes up. Refused rather than silently
        /// ignored when the door is not somewhere a way out could arrive.
        /// </summary>
        public CompanyActionResult Mark()
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign == null || !campaign.CanOperate)
            { return CompanyActionResult.Refused("RR_Emergence_InvalidState"); }
            if (parent == null || !parent.Spawned || parent.Destroyed || parent.Faction != Faction.OfPlayer)
            { return CompanyActionResult.Refused("RR_Emergence_DoorUnavailable"); }
            if (!OrdinaryBranchMap(parent.Map))
            { return CompanyActionResult.Refused("RR_Emergence_OrdinaryMapRequired"); }
            IntVec3 approach = ApproachCell;
            if (!approach.IsValid || !approach.InBounds(parent.Map) || !approach.Standable(parent.Map))
            { return CompanyActionResult.Refused("RR_Emergence_ApproachBlocked"); }
            if (designated && campaign.BranchId == branchId) { return CompanyActionResult.Applied(); }
            designated = true;
            branchId = campaign.BranchId;
            campaign.RecordEvent("RR_Event_EmergenceAnchorMarked", parent.GetUniqueLoadID());
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Stop this door being a way home.
        ///
        /// **A way out that already came up here is deliberately left alone.** Withdrawing the
        /// mark says "no more ways out here", not "close the one that exists" — a saved edge
        /// is evidence of a place somebody found, and silently deleting it would strand
        /// anything relying on it. Removing an existing edge is a separate, explicit act.
        /// </summary>
        public CompanyActionResult Withdraw()
        {
            if (!designated) { return CompanyActionResult.Applied(); }
            designated = false;
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_EmergenceAnchorWithdrawn", parent.GetUniqueLoadID()); }
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// An ordinary map this branch owns — never a Backrooms coordinate. This is the one
        /// test that makes "a way out comes up somewhere else" true by construction.
        /// </summary>
        internal static bool OrdinaryBranchMap(Map map)
        {
            if (map == null || map.Parent is RimroomsDestinationMapParent) { return false; }
            RimroomsCampaignComponent campaign = Campaign();
            return campaign != null && campaign.CanOperate && campaign.OwnsMap(map);
        }

        /// <summary>Every door on any loaded map this branch could bring a way out up at.</summary>
        internal static List<CompRimroomsEmergence> Anchors()
        {
            var found = new List<CompRimroomsEmergence>();
            List<Map> maps = Find.Maps;
            if (maps == null) { return found; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (!OrdinaryBranchMap(map) || map.listerBuildings == null) { continue; }
                foreach (Building building in map.listerBuildings.allBuildingsColonist)
                {
                    CompRimroomsEmergence anchor = building.TryGetComp<CompRimroomsEmergence>();
                    if (anchor != null && anchor.IsDesignated) { found.Add(anchor); }
                }
            }
            return found;
        }

        private static RimroomsCampaignComponent Campaign()
        {
            return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
        }

        private static void Show(CompanyActionResult result)
        {
            if (result == null) { return; }
            if (result.Success)
            {
                Messages.Message("RR_Emergence_Updated".Translate(), MessageTypeDefOf.TaskCompletion, false);
                return;
            }
            Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false);
        }
    }
}
