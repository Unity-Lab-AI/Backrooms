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
    public class CompRimroomsEmergence : ThingComp, IThingGlower
    {
        /// <summary>
        /// The blue the owner asked for, as a **glow** colour.
        ///
        /// Alpha zero is the convention for a `ColorInt` handed to `CompGlower` -- their own
        /// stargate def uses `(115,171,224,0)` -- because a glower reads the channels and not the
        /// opacity.
        /// </summary>
        private static readonly ColorInt LiveGlowColor = new ColorInt(70, 130, 220, 0);

        /// <summary>
        /// The same blue as a **tint**, and it has to be opaque.
        ///
        /// **This is the defect the owner reported as a missing door.** `ColorInt.ToColor`
        /// divides every channel by 255 including alpha, so reusing the glow constant here
        /// painted the door with zero opacity: `Thing.DrawColor` returns what `CompColorable`
        /// holds, so the door was drawn fully transparent while its glower kept lighting the
        /// room. It was never destroyed -- the paused game showed it intact with 160 hit points.
        ///
        /// **A glow colour and a draw colour are not the same kind of colour**, and sharing one
        /// constant between them is what hid that.
        /// </summary>
        private static readonly Color LiveTintColor = new Color(70f / 255f, 130f / 255f,
            220f / 255f, 1f);
        private const float LiveGlowRadius = 6f;

        /// <summary>
        /// Whether Core should light this door.
        ///
        /// **This one method is why adding a glower to `Door` does not change any other door in
        /// the game.** `CompGlower.ShouldBeLitNow` walks every comp on its parent and asks any
        /// that implements <see cref="IThingGlower"/>; a single false from any of them keeps the
        /// glower dark and unregistered. So every ordinary door in every colony, and every door
        /// any other mod ships, carries an inert glower — refused by Core's own rule rather than
        /// by hoping the radius of zero is enough.
        /// </summary>
        public bool ShouldBeLitNow() { return IsLiveGate; }

        /// <summary>
        /// A marked door on a branch map that the portal network actually has an edge for.
        ///
        /// Stricter than <see cref="IsDesignated"/> on purpose: a door the player marked but
        /// which nothing leads through yet is a plan, not a gate, and lighting it blue would
        /// promise a way through that does not exist.
        /// </summary>
        public bool IsLiveGate
        {
            get
            {
                if (!IsDesignated || parent == null || Verse.Current.Game == null) { return false; }
                RimroomsPortalNetwork network = Verse.Current.Game.GetComponent<RimroomsPortalNetwork>();
                if (network == null || network.Connections == null) { return false; }
                IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
                for (int index = 0; index < edges.Count; index++)
                {
                    PortalConnectionRecord edge = edges[index];
                    if (edge == null) { continue; }
                    if ((edge.First != null && edge.First.Anchor == parent) ||
                        (edge.Second != null && edge.Second.Anchor == parent))
                    { return true; }
                }
                return false;
            }
        }

        /// <summary>
        /// Make the door read as a gate, or stop. Idempotent, and safe to call every rare tick.
        ///
        /// The colour and the radius are set through the per-instance overrides Core exposes, so
        /// nothing here edits a shared `CompProperties` — which would recolour every door at once.
        /// </summary>
        private void RefreshGateAppearance()
        {
            if (parent == null || !parent.Spawned) { return; }
            bool live = IsLiveGate;
            CompGlower glower = parent.TryGetComp<CompGlower>();
            if (glower != null)
            {
                glower.GlowRadius = live ? LiveGlowRadius : 0f;
                glower.GlowColor = LiveGlowColor;
                // UpdateLit is the whole of it: Core registers or deregisters the light with
                // the glow grid itself. There is no separate cache to dirty.
                glower.UpdateLit(parent.Map);
            }
            CompColorable colorable = parent.TryGetComp<CompColorable>();
            if (colorable != null)
            {
                if (live) { colorable.SetColor(LiveTintColor); }
                else if (colorable.Active) { colorable.Disable(); }
            }
        }

        /// <summary>
        /// **The Stargate mod's own gate, on both ends of this route, dialled by us.**
        ///
        /// Owner: *"we use the fucjkign stargate MOD but use a normal door"*, *"and connect them
        /// together to the backrooms and the map"*, *"we just use our own dialing converstion in
        /// the background"*, *"we still use the stargate mod as normal but we also use it for our
        /// backrroms purposes"*.
        ///
        /// Three steps, and none of them touches their mod:
        ///
        /// 1. **both ends get their component.** The far anchor stands inside a coordinate, which
        ///    is not an ordinary branch map, so it can never mark itself — the near side knows the
        ///    edge, so it attaches both. Core's transporter goes on with it, and that is what
        ///    makes colonists **haul the chosen materials to the door on their own**.
        /// 2. **we dial.** Their address space is a `PlanetTile`, and this company already knows
        ///    which door leads to which coordinate, so the conversion is reading the destination
        ///    map's own address. No DHD, no player input.
        /// 3. **it stays open**, because a natural gate is permanently open — invariant 12. Their
        ///    wormhole times out on its own, so re-dialling an idle gate is what keeps the route
        ///    a route rather than an appointment.
        ///
        /// Silent and harmless when the Stargate mod is absent: every call answers false and the
        /// Backrooms behave exactly as they did before.
        /// </summary>
        private void RefreshStargate()
        {
            if (!StargateBridge.Available || parent == null || !parent.Spawned) { return; }
            PortalConnectionRecord edge = EdgeFor();
            if (edge == null || !IsLiveGate) { return; }

            ThingWithComps near = parent;
            ThingWithComps far = FarAnchor(edge);
            // NATURAL on both ends: this is a way out that was always there, not a machine
            // a player dialled, so neither end carries an unstable vortex.
            StargateBridge.Attach(near, true);
            if (far == null)
            {
                // **The likeliest silent stop, and it used to say nothing.** A destination below
                // `DoorThresholdContentVersion` keeps a historical anchor that is not a door, so
                // `as ThingWithComps` yields null and the route has no far end to put a gate on.
                ReportGateState("the far end of this route is not a door, so no gate can be "
                                + "attached there");
                return;
            }
            if (far.Map == null)
            {
                ReportGateState("the far end is not on a loaded map");
                return;
            }
            StargateBridge.Attach(far, true);

            // Dialled only from this side, and only when nothing is already open. Their gate is
            // one-way by design, so dialling a receiving end would fight their own rule rather
            // than use it.
            if (StargateBridge.IsOpen(near)) { return; }
            if (StargateBridge.IsReceiving(near)) { ReportGateState("it is the receiving end"); return; }
            if (StargateBridge.IsHibernating(near))
            { ReportGateState("their mod has it hibernating, which means another stargate is on this map"); return; }
            if (StargateBridge.On(near) == null)
            { ReportGateState("their component did not attach to this door"); return; }
            if (!StargateBridge.Dial(near, far.Map, 0))
            { ReportGateState("the dial was refused"); }
        }

        /// <summary>Whether this gate has already explained itself once.</summary>
        private bool reportedGateState;

        /// <summary>
        /// Say, once, why a live natural gate is not showing a wormhole.
        ///
        /// **Every refusal in this path used to be silent**, which is correct for a colony
        /// without the Stargate mod and useless the moment something does not work. The owner's
        /// report -- *"i do not see the portal fx from stargate"* -- came with a log containing
        /// nothing at all, because this code was written to say nothing at all.
        ///
        /// `Log.Message`, not `Log.Error`: a gate that cannot dial is information, not a fault.
        /// Once per door, because this runs on a tick.
        /// </summary>
        private void ReportGateState(string reason)
        {
            if (reportedGateState) { return; }
            reportedGateState = true;
            Log.Message("[Rimrooms][Stargate] " + parent.LabelShortCap + " at "
                        + parent.Position + " is a live gate but is not showing a wormhole: "
                        + reason + ".");
        }

        /// <summary>The door at the other end of this route, as a thing that can carry comps.</summary>
        private ThingWithComps FarAnchor(PortalConnectionRecord edge)
        {
            if (edge == null) { return null; }
            Thing first = edge.First == null ? null : edge.First.Anchor;
            Thing second = edge.Second == null ? null : edge.Second.Anchor;
            Thing other = first == parent ? second : first;
            return other as ThingWithComps;
        }

        /// <summary>How often a gate is asked whether it should look like one.</summary>
        private const int AppearanceInterval = 250;

        /// <summary>
        /// **THIS, NOT `CompTickRare`, AND THE DIFFERENCE IS WHY NO GATE WAS EVER BLUE.**
        ///
        /// Owner, verbatim: *"the back wall door is not correctly blue ... does not cortrectly
        /// have the blue light glow"*. Everything else about the gate was working — the live
        /// session showed the coordinate generated, the door marked, the edge registered and the
        /// crossing offered — but `RefreshGateAppearance` had never executed once.
        ///
        /// `Verse.Thing.DoTick` dispatches on the def's ticker type: a `Normal` ticker gets
        /// `Tick()` and `TickInterval(delta)`, a `Rare` ticker gets `TickRare()`. **Core's
        /// `DoorBase` is `tickerType Normal`**, and `Door` and `Autodoor` inherit it, so
        /// `TickRare` is never called on them and `CompTickRare` never ran.
        ///
        /// Throttled with Core's own interval-safe `IsHashIntervalTick(interval, delta)` because
        /// 1.6 varies a thing's update rate — and because <see cref="IsLiveGate"/> walks every
        /// edge in the portal network, which is not a per-tick question for every door in a
        /// colony.
        /// </summary>
        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            if (parent == null || !parent.IsHashIntervalTick(AppearanceInterval, delta)) { return; }
            RefreshGateAppearance();
            // Same tick, same question. If the appearance and the wormhole were refreshed from
            // different places they could disagree about whether this is a gate.
            RefreshStargate();
        }

        /// <summary>
        /// Kept as well, and deliberately.
        ///
        /// This comp is attached to **door defs**, not to one def this package owns, so another
        /// mod's door may legitimately be a `Rare` ticker. Covering both costs nothing and means
        /// the appearance does not depend on a ticker type we do not control.
        /// </summary>
        public override void CompTickRare()
        {
            base.CompTickRare();
            RefreshGateAppearance();
            RefreshStargate();
        }

        /// <summary>
        /// Right-click the gate with a colonist selected and walk through it.
        ///
        /// **Owner direction, repeated and then repeated angrily:** *"ive said stargate mod
        /// repeaditly is how the gates work ... the pawns can walk from tmap to map like the
        /// stargate mod works but with normal does"*.
        ///
        /// The order and the job already existed and already did exactly that:
        /// `PortalTravelService.OrderCrossing` makes a real job that walks the pawn to the cell
        /// beside the door and crosses to the other map. **What was missing was the place a
        /// player looks for it.** It was only reachable by selecting pawns, selecting the door,
        /// clicking a gizmo and choosing from a float menu — which is a dispatch console, not a
        /// door you walk through.
        ///
        /// `CompFloatMenuOptions` is Core's own hook for *"right-click this with that colonist
        /// selected"*, and it is the same hook every piece of Core content uses for *go here and
        /// do this*. Nothing is decided here: the order is still
        /// <see cref="PortalTravelService.OrderCrossing"/> and the rule is still
        /// `PortalTraversalPolicy`, so invariant 1 holds — this is where the question is asked,
        /// not a second opinion about the answer.
        /// </summary>
        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption option in base.CompFloatMenuOptions(selPawn))
            { yield return option; }
            if (selPawn == null || parent == null || !parent.Spawned) { yield break; }
            if (!IsLiveGate) { yield break; }
            PortalConnectionRecord edge = EdgeFor();
            if (edge == null) { yield break; }
            // Refusals are shown as a disabled row with the reason, never hidden: a name missing
            // from a menu tells the player nothing, and "drafted" or "in transit" is something
            // they need told.
            string refusal = RimroomsPortalCrossingService.EligibilityFailureKey(selPawn);
            if (refusal != null)
            {
                yield return new FloatMenuOption(
                    "RR_DoorCross_EnterRefused".Translate(refusal.Translate()), null);
                yield break;
            }
            PortalConnectionRecord subject = edge;
            yield return new FloatMenuOption("RR_DoorCross_Enter".Translate(), delegate
            {
                Show(PortalTravelService.OrderCrossing(selPawn, subject));
            });
        }

        /// <summary>The live edge this door is an endpoint of, or null.</summary>
        private PortalConnectionRecord EdgeFor()
        {
            RimroomsPortalNetwork network = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.Connections == null) { return null; }
            IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
            for (int index = 0; index < edges.Count; index++)
            {
                PortalConnectionRecord edge = edges[index];
                if (edge == null) { continue; }
                if ((edge.First != null && edge.First.Anchor == parent) ||
                    (edge.Second != null && edge.Second.Anchor == parent))
                { return edge; }
            }
            return null;
        }

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
            // **Painted on every spawn, including after a load, and BEFORE the early return.**
            // A saved gate was an ordinary grey door until the next appearance interval came
            // round, which is up to 250 ticks of a player looking at the thing they are about to
            // report as broken.
            RefreshGateAppearance();
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

            // **THERE IS NO RE-OPEN, AND THAT IS THE FIVE-MAP LIMIT.** Owner, verbatim:
            // *"we do need to be able to close natural portals u just can not re open them"* and
            // *"thats the whole 5 limit issue"*.
            //
            // A door that led somewhere and no longer does keeps saying so, because a player
            // standing in front of it needs to know this was a way through and is spent -- but it
            // is a record, not an offer. Closing a place is how a slot is freed, and a decision
            // that can be undone is not a decision.
            //
            // The door itself is not spent: minifying and reinstalling it moves any route it
            // still carries, through `NotifyAnchorInstalled`. **Moving a gate keeps it; closing
            // its place spends it.**
        }

        // `Reopen` lived here until 0.12.59-dev. **Closing a natural portal
        // is one-way now** -- owner: *"we do need to be able to close
        // natural portals u just can not re open them"*, *"thats the whole
        // 5 limit issue"*. A slot is freed by a decision that cannot be
        // undone, because one that can be undone is not a decision.

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
            // Painted on the click, not up to an interval later: a player who marks a door and
            // sees nothing change assumes the mark failed.
            RefreshGateAppearance();
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
            // Unpainted on the click, for the same reason.
            RefreshGateAppearance();
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
