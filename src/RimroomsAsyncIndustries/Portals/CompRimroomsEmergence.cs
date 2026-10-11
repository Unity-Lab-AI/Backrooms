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
    public partial class CompRimroomsEmergence : ThingComp, IThingGlower
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
        public bool ShouldBeLitNow() { return IsLiveGate || recordedGate || frontierGate; }

        /// <summary>
        /// Whether this door is an undiscovered way onward, as of the last appearance refresh.
        ///
        /// **Cached, because Core asks `ShouldBeLitNow` whenever it likes.**
        /// <see cref="NaturalFrontierService.IsFrontierCandidate"/> walks the coordinate list and
        /// the whole portal edge list, which is not a question to answer from inside a glower.
        /// Recomputed on the same interval as the rest of the appearance, in
        /// <see cref="CompTickInterval"/>.
        /// </summary>
        private bool frontierGate;

        /// <summary>
        /// Whether this door is an endpoint of a live edge, as of the last appearance refresh.
        /// Cached for the same reason <see cref="frontierGate"/> is: Core asks `ShouldBeLitNow`
        /// whenever it likes, and answering walks the whole edge list.
        /// </summary>
        private bool recordedGate;

        /// <summary>
        /// A door inside the Backrooms that leads somewhere else and has not been recorded yet.
        ///
        /// ## Why this exists at all, which is the whole defect
        ///
        /// Owner, after walking a finished level end to end: *"i never found any natural cates to
        /// the world map tiles or natural portals to deep into the backrroooms ... i just never
        /// found any other gates with option to \"walk through\""*.
        ///
        /// **`NaturalFrontierService.Discover` and `IsFrontierCandidate` had ZERO callers in the
        /// entire package.** The draw, the cap, the emergence share, the world-exit fallback, the
        /// guaranteed pair added last checkpoint, and every one of the twenty-odd
        /// `RR_Frontier_*` strings the player was meant to read -- all written, all correct, and
        /// **nothing ever asked a door whether it was a way onward.** It is the same defect that
        /// has now been found five times in this run: computing a value correctly and using it
        /// are two different facts.
        ///
        /// ## Why it glows before it is discovered
        ///
        /// A natural gate is permanently open -- invariant 12 -- so a door that leads elsewhere
        /// is already leading elsewhere before anybody writes it down. And the owner's own cue
        /// for a natural gate is the blue: *"i see the blue glow"*. A way onward that can only be
        /// found by right-clicking every door on a three-hundred-cell floor is a way onward
        /// nobody finds, which is exactly what happened.
        ///
        /// It is never a way home and never a machine gate: `Evaluate` refuses the threshold
        /// anchor, a player-built door and a designated gate before this can be true.
        /// </summary>
        public bool IsFrontierGate
        {
            get
            {
                if (IsDesignated || parent == null || !parent.Spawned) { return false; }
                // **INSIDE A COORDINATE ONLY, and a proof caught this.** `Evaluate` serves
                // ordinary maps too, under its own `worldfrontier:` origin -- so without this,
                // a door in an ancient structure on the player's own colony map would start
                // glowing blue the moment this mod was installed. `CONTENT_REUSE_POLICY.md`
                // forbids changing an existing colony by installing, and the claim *"no other
                // door in the game is affected"* is there to hold that line.
                //
                // A world frontier on an ordinary map is still found and still crossable; it
                // simply does not advertise itself with the Backrooms' own colour.
                if (!(parent.Map != null && parent.Map.Parent is RimroomsDestinationMapParent))
                { return false; }
                return NaturalFrontierService.IsFrontierCandidate(parent);
            }
        }

        /// <summary>
        /// Whether this door is an endpoint of a live portal edge, **marked or not.**
        ///
        /// ## Why this is not <see cref="IsLiveGate"/>
        ///
        /// `IsLiveGate` requires <see cref="IsDesignated"/>, which means *the player marked this
        /// door as a way home* -- and also demands the door belong to the player's faction and
        /// stand on an ordinary branch map. **None of that is ever true of a door generated
        /// inside a coordinate.**
        ///
        /// So a way onward, once discovered, had a real `Natural` edge and no way to use it: the
        /// crossing option was never offered, the glow went out, and asking again returned
        /// `RR_Frontier_AlreadyRecorded` -- which the owner read as *"this address is already
        /// being used"*. **It worked once and then went dark and dead.**
        ///
        /// Both questions are kept because both are needed. `PortalAddressService` and the
        /// emergence rules depend on `IsLiveGate` meaning the stronger thing; the appearance and
        /// the crossing menu only ever needed the weaker one.
        /// </summary>
        public bool IsRecordedGate
        {
            get
            {
                if (parent == null || !parent.Spawned || parent.Destroyed) { return false; }
                return EdgeFor() != null;
            }
        }

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
            // A way onward is a natural gate that nobody has written down yet, and it is
            // already permanently open. Cached here so Core's glower can ask cheaply.
            frontierGate = IsFrontierGate;
            // **AND ONE THAT HAS BEEN WRITTEN DOWN IS STILL A GATE.** `IsLiveGate` needs a player
            // mark, which a door inside a coordinate never has, so a discovered way onward used
            // to stop glowing the moment it started working.
            recordedGate = IsRecordedGate;
            bool live = IsLiveGate || recordedGate || frontierGate;
            // **THE EXPENSIVE ANSWER IS CACHED HERE AND THE CHEAP ONE RUNS FOUR TIMES A SECOND.**
            // `IsLiveGate` walks every edge in the portal network, which is why this method is
            // throttled to 250 ticks. The aura needs to move faster than that, so it reads this
            // cached answer rather than asking the network again. See `GateAura.cs`.
            auraLive = live;
            // UpdateLit is still the whole of it: Core registers or deregisters the light with the
            // glow grid itself, and ApplyAura calls it only when the value it would write differs
            // from the value it last wrote.
            ApplyAura();
            CompColorable colorable = parent.TryGetComp<CompColorable>();
            if (colorable != null)
            {
                if (live) { colorable.SetColor(LiveTintColor); }
                else if (colorable.Active) { colorable.Disable(); }
            }
        }

        // **NO STARGATE-MOD COMPONENT IS EVER PUT ON THIS DOOR.** Their gate logic only knows its
        // own `Building_Stargate`: it picks its own destination gate, starts no wormhole on a zero
        // countdown, runs its own float-menu and loading transit outside this company's receipts,
        // and a component added per instance is not rebuilt when a save loads. So a natural gate
        // stays an ordinary door with the blue glow, and every crossing goes through
        // `PortalTravelService.OrderCrossing`. Their mod keeps working on their own gates.

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
            if (parent == null) { return; }
            if (parent.IsHashIntervalTick(AppearanceInterval, delta))
            {
                RefreshGateAppearance();
                return;
            }
            // **The aura's own cadence, and it asks the network nothing.** It reads the cached
            // `auraLive` from the slow pass above plus the gate's own live state, so running it
            // sixteen times as often costs no extra edge walks. It writes to the glow grid only
            // when the colour or the quantised radius actually moved.
            if (parent.IsHashIntervalTick(AuraInterval, delta)) { ApplyAura(); }
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
            // **A RECORDED GATE IS A GATE, MARKED OR NOT.** `IsLiveGate` needs a player
            // mark and an ordinary branch map, so a discovered way onward inside a coordinate was
            // never offered a crossing however correctly its edge was registered.
            if (!IsLiveGate && !IsRecordedGate)
            {
                foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }
                yield break;
            }
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

        /// <summary>
        /// Walk through a way onward: record it, then cross it, in one order.
        ///
        /// ## The defect this closes
        ///
        /// Owner: *"i just never found any other gates with option to \"walk through\" adding them
        /// to the loaded maps of my game play through"*.
        ///
        /// **`NaturalFrontierService.Discover` had no callers.** Every refusal string the player
        /// was meant to read -- `RR_Frontier_LeadsNowhere`, `RR_Frontier_NoneLeftHere`,
        /// `RR_Frontier_TooManyGatesHeld`, twenty of them -- was written for a float menu that
        /// did not exist, and `RR_Frontier_Discovered` announced an event nothing could raise.
        ///
        /// ## Why discovering and crossing are one click
        ///
        /// They are one act. A player who walks a colonist to a door that is glowing blue has
        /// already decided; making them record it, then find it again in a list, then order a
        /// crossing is the dispatch console this project removed from the gate door for exactly
        /// the same reason.
        ///
        /// `Discover` is idempotent -- the coordinate id and the seed are derived from the
        /// doorway's position, and both the campaign record and the graph edge answer *"already
        /// exists"* on a replay -- so a second click on a door already recorded simply crosses it.
        ///
        /// Nothing is decided here. `Discover` applies the draw, the cap, the guarantee and every
        /// obstruction check; `PortalTraversalPolicy` decides who may cross. This is where the
        /// question is asked, not a second opinion about the answer.
        /// </summary>
        private IEnumerable<FloatMenuOption> FrontierOptions(Pawn selPawn)
        {
            if (!NaturalFrontierService.IsFrontierCandidate(parent)) { yield break; }
            // Shown as a disabled row with the reason, never hidden, for the same reason the
            // live-gate path does it: a name missing from a menu tells the player nothing.
            string refusal = RimroomsPortalCrossingService.EligibilityFailureKey(selPawn);
            if (refusal != null)
            {
                yield return new FloatMenuOption(
                    "RR_DoorCross_EnterRefused".Translate(refusal.Translate()), null);
                yield break;
            }
            yield return new FloatMenuOption("RR_Frontier_WalkThrough".Translate(), delegate
            {
                CompanyActionResult found = NaturalFrontierService.Discover(parent);
                if (!found.Success) { Show(found); return; }
                // Painted on the click, not up to an interval later, and for the same reason
                // marking a door is: a player who acts and sees nothing change assumes it failed.
                RefreshGateAppearance();

                // **A WAY OUT IS NOT A WAY DEEPER, AND THEY ARE RECORDED DIFFERENTLY.** A deeper
                // find mints a coordinate and registers a portal EDGE between this door and the
                // new place's threshold. A way out to the world saves a `WorldExitRecord` with a
                // planet tile and **registers no edge at all**, because leaving the Backrooms for
                // the world map is a caravan rather than a map-to-map crossing.
                //
                // The first draft asked `EdgeFor()` in both cases, so a world exit recorded
                // correctly and then reported *"surveying doors is unavailable until this branch
                // is operating"* -- which is not true and says nothing. The owner read it as
                // *"somthing about generationg the next world map or deeper backrroms"*, which
                // is precisely what it was.
                PortalConnectionRecord edge = EdgeFor();
                if (edge != null)
                {
                    Show(PortalTravelService.OrderCrossing(selPawn, edge));
                    return;
                }
                RimroomsCampaignComponent campaign = Campaign();
                if (campaign != null && campaign.WorldExitFor(parent) != null)
                {
                    // The SAME method the gizmo calls, which is the only thing in the package
                    // that reaches the leave routine -- see WalkOutToWorld.
                    Show(WalkOutToWorld());
                    return;
                }
                Show(CompanyActionResult.Refused("RR_Frontier_Unavailable"));
            });
        }

        /// <summary>
        /// Walk out of the Backrooms onto the world map, as a caravan.
        ///
        /// **THE ONLY THING IN THIS PACKAGE THAT REACHES THE LEAVE ROUTINE**, and therefore the
        /// only thing that can reach `CaravanExitMapUtility.ExitMapAndCreateCaravan`. The gizmo
        /// and the float-menu option both come here.
        ///
        /// `proof-world-exit.py` asserts there is exactly one caller of
        /// `LeaveThroughWorldExit`, and when the float menu added a second one it refused --
        /// correctly. Both callers were player clicks, so the narrowed stranded-crew guarantee
        /// in `WorldExit.cs` still held, but *"every caller is a player command"* is not
        /// something a source claim can decide and *"there is one caller"* is. **A weaker claim
        /// that can be checked beats a stronger one that cannot**, so this exists instead of the
        /// claim being relaxed.
        ///
        /// Nothing automatic can reach it: no tick, work giver, incident or scheduler calls
        /// either of the two UI paths above.
        /// </summary>
        private CompanyActionResult WalkOutToWorld()
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign == null || parent == null || campaign.WorldExitFor(parent) == null)
            { return CompanyActionResult.Refused("RR_WorldExit_DoorUnavailable"); }
            return campaign.LeaveThroughWorldExit(parent);
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
                    action = delegate { Show(WalkOutToWorld()); }
                };
            }

            if (parent.Faction != Faction.OfPlayer) { yield break; }
            // Never offered inside the Backrooms: a way out cannot come up in the place it
            // leads away from, and offering the command there would only ever refuse.
            if (!OrdinaryBranchMap(parent.Map)) { yield break; }

            // **BOARDING IT UP, ON THE DOOR, BY A PAWN, FOR WOOD.** Owner, 2026-10-04: *"the
            // closing of natural portals needs to be an option on the gate itself so pawns can
            // close it with like 25 wood to board it up which makes it close its map freeing up a
            // map from being open so others can be explored"*.
            //
            // Closing a place already existed in the Operations held-places pane. What the owner
            // objected to is where it lived -- the same direction says *"everything that the
            // machine needs to start up should be able to do in the worlkd from the devices
            // themselfes with pawns controls and actrions not just in the opetaions tab"*.
            //
            // Offered only when there is something behind the door to close, and **disabled with
            // its reason showing** rather than hidden when there is not: a command that vanishes
            // teaches nothing, and the reasons here are the interesting part -- somebody is still
            // inside, a crossing is in flight, there is no wood.
            RimroomsCampaignComponent boardCampaign = Campaign();
            if (boardCampaign != null
                && PortalBoardUp.PlaceBehind(boardCampaign, parent) != null)
            {
                string boardRefusal = PortalBoardUp.RefusalFor(boardCampaign, parent);
                var boardUp = new Command_Action
                {
                    defaultLabel = "RR_BoardUp_Label".Translate(PortalBoardUp.WoodCost),
                    defaultDesc = "RR_BoardUp_Desc".Translate(PortalBoardUp.WoodCost),
                    icon = parent.def.uiIcon,
                    action = delegate { Show(PortalBoardUp.Order(boardCampaign, parent)); }
                };
                if (boardRefusal != null)
                { boardUp.Disable(boardRefusal.Translate()); }
                yield return boardUp;
            }

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
