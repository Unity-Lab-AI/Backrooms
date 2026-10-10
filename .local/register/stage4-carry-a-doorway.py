# -*- coding: utf-8 -*-
"""Stage four: a natural gate is an object you own. Destroy it and the route is gone; carry it and
the route comes with you.

Owner direction, 2026-09-30, verbatim:

    "so we need a way to deconstruct natural gates too i think"
    "and then u lose them forever but maybe allow minify move"
    "they are just doors too right that dont need the mechine gate systems"

The third is confirmed by live measurement, not inference: the natural gate in the owner's own
running game was a plain `RimWorld.Building_Door` in steel, already offering Deconstruct,
Uninstall, Reinstall and the emergence gizmo, with no power, console, calibration or assembly.

**Deconstruct already behaved as asked** -- `PortalDoorWarningMapComponent` warns with informed
consent, written to the owner's earlier words, and `RimroomsPortalNetwork.EndpointPresent` refuses
an edge whose anchor is destroyed. So the route is already lost forever when the door is.

**Uninstall did NOT behave as asked.** `EndpointPresent` also requires
`endpoint.Anchor.Position == endpoint.AnchorCell`, and `PortalEndpointRecord` says outright that
the cell is a deliberate snapshot so *"moving a door cannot silently redirect a saved route"*.
Correct under the old rule that naturals could not be moved; wrong now. So a move **re-anchors the
route explicitly**, and is refused while anybody is mid-crossing.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

RECORDS = os.path.join(SRC, "Portals", "PortalConnectionRecord.cs")
NETWORK = os.path.join(SRC, "Portals", "RimroomsPortalNetwork.cs")
CROSSING = os.path.join(SRC, "Portals", "PortalCrossingService.cs")
COMP = os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")
WARNING = os.path.join(SRC, "Portals", "PortalDoorWarning.cs")
KEYED = os.path.join(MOD, "Languages", "English", "Keyed", "RR_Portals.xml")


def edit(path, pairs):
    text = io.open(path, encoding="utf-8-sig" if path.endswith(".xml") else "utf-8").read()
    problems = []
    for old, _ in pairs:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:64]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in pairs:
        text = text.replace(old, new, 1)
    enc = "utf-8-sig" if path.endswith(".xml") else "utf-8"
    io.open(path, "w", encoding=enc, newline="").write(text)
    print("%s: %d edit(s)" % (os.path.basename(path), len(pairs)))


# ------------------------------------------------------------------ 1. the endpoint can re-anchor
edit(RECORDS, [(
    """        internal bool TryRepairApproach()""",
    """        /// <summary>
        /// Follow this endpoint's own door to where it has been reinstalled.
        ///
        /// ## Why this exists, and why it is not the thing the snapshot was guarding against
        ///
        /// **Owner direction, 2026-09-30, verbatim:** *"and then u lose them forever but maybe
        /// allow minify move"*.
        ///
        /// The comment above says the anchor cell is deliberately never refreshed, so *"moving a
        /// door cannot silently redirect a saved route"*. That was exactly right while the rule
        /// was that naturals could not be moved at all. It is still right about the danger: the
        /// thing to prevent is a route changing **silently**.
        ///
        /// So this is not a refresh. It is a **move**, and it has three properties the snapshot
        /// was protecting:
        ///
        ///   * it only ever follows the **same `Thing` instance**. A different door in the same
        ///     cell is not this endpoint and never becomes it, so a route cannot be captured by
        ///     rebuilding something that looks like it.
        ///   * it refuses unless the door is spawned, player-owned and on a map the branch owns,
        ///     which is the same test registration had to pass.
        ///   * the caller refuses it outright while a crossing is in flight, so nobody is ever
        ///     mid-transit through an endpoint that moves under them -- the guard invariant 55
        ///     exists for.
        ///
        /// Returns true when the endpoint actually moved, so the caller can report it.
        /// </summary>
        internal bool TryFollowMovedAnchor(Thing thing, IntVec3 approach)
        {
            if (thing == null || anchor == null || anchor != thing) { return false; }
            if (!thing.Spawned || thing.Destroyed || thing.Map == null) { return false; }
            if (!approach.IsValid || !approach.InBounds(thing.Map) ||
                !approach.AdjacentToCardinal(thing.Position)) { return false; }
            if (map == thing.Map && anchorCell == thing.Position && approachCell == approach)
            { return false; }
            map = thing.Map;
            anchorCell = thing.Position;
            approachCell = approach;
            return true;
        }

        internal bool TryRepairApproach()""")])


# ------------------------------------------------------------------ 2. a crossing in flight blocks it
edit(CROSSING, [(
    """        public IReadOnlyList<PortalCrossingReceipt> Receipts { get { return receipts.AsReadOnly(); } }""",
    """        public IReadOnlyList<PortalCrossingReceipt> Receipts { get { return receipts.AsReadOnly(); } }

        /// <summary>
        /// Whether anybody is part-way through this connection right now.
        ///
        /// Asked before a door is allowed to take its route with it. A receipt that is not
        /// terminal is a pawn mid-transfer, and moving an endpoint under one is precisely what
        /// invariant 55 forbids.
        /// </summary>
        public bool IsConnectionInFlight(string connectionId)
        {
            if (string.IsNullOrWhiteSpace(connectionId)) { return false; }
            return receipts.Any(receipt => receipt != null && !receipt.IsTerminal &&
                receipt.ConnectionId == connectionId);
        }""")])


# ------------------------------------------------------------------ 3. the network moves the edge
edit(NETWORK, [(
    """        private static bool EndpointPresent(PortalEndpointRecord endpoint)""",
    """        /// <summary>
        /// A door has been installed somewhere. If it is an endpoint of any connection, the
        /// connection follows it.
        ///
        /// **Owner direction, 2026-09-30:** *"maybe allow minify move"*. A natural gate is an
        /// ordinary door the player owns, so they may uninstall it, carry it and put it somewhere
        /// else -- and the way through should come with it rather than being quietly lost.
        ///
        /// Refused while a crossing is in flight, which is the one case where a moving endpoint
        /// could strand somebody. The door is already installed by the time this runs, so the
        /// refusal cannot un-move it; what it does is leave the route broken and visible rather
        /// than silently re-pointed under a traveller. That is the safer of the two, and the
        /// warning the player already confirmed told them a move was consequential.
        ///
        /// Returns how many connections moved, so the caller can tell the player.
        /// </summary>
        public int NotifyAnchorInstalled(Thing anchor)
        {
            if (anchor == null || !anchor.Spawned || anchor.Destroyed || HasStateFault) { return 0; }
            if (!OwnsMap(Campaign, anchor.Map)) { return 0; }
            IntVec3 approach = PortalAddressService.ApproachCellFor(anchor);
            PortalCrossingService crossings = Current.Game == null
                ? null : Current.Game.GetComponent<PortalCrossingService>();
            int moved = 0;
            for (int index = 0; index < connections.Count; index++)
            {
                PortalConnectionRecord edge = connections[index];
                if (edge == null || edge.First == null || edge.Second == null) { continue; }
                if (edge.First.Anchor != anchor && edge.Second.Anchor != anchor) { continue; }
                if (crossings != null && crossings.IsConnectionInFlight(edge.Id)) { continue; }
                bool changed = edge.First.TryFollowMovedAnchor(anchor, approach)
                    || edge.Second.TryFollowMovedAnchor(anchor, approach);
                if (changed) { moved++; }
            }
            if (moved > 0) { topologyRevision++; }
            return moved;
        }

        private static bool EndpointPresent(PortalEndpointRecord endpoint)""")])


# ------------------------------------------------------------------ 4. the comp reports its install
edit(COMP, [(
    """        public override void PostExposeData()""",
    """        /// <summary>
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

        public override void PostExposeData()""")])


# ------------------------------------------------------------------ 5. the warning tells them which
edit(WARNING, [(
    """            bool doomed = map.designationManager.DesignationOn(anchor, DesignationDefOf.Deconstruct) != null
                || map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall) != null;
            if (!doomed)""",
    """            // **Uninstall and deconstruct are no longer the same event**, owner direction
            // 2026-09-30: *"and then u lose them forever but maybe allow minify move"*. Taking a
            // doorway with you keeps the route; breaking it up does not. Telling the player the
            // same thing for both would be telling them something false about one of them.
            bool breaking = map.designationManager.DesignationOn(anchor, DesignationDefOf.Deconstruct) != null;
            bool carrying = map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall) != null;
            bool doomed = breaking || carrying;
            if (!doomed)"""),
    ("""            Thing subject = anchor;
            Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                "RR_Portals_RemoveWayInConfirm".Translate(),
                delegate { /* Confirmed. The designation stands and the work proceeds. */ },
                delegate { ClearDesignations(subject); },
                destructive: true,
                title: "RR_Portals_RemoveWayInTitle".Translate()));""",
     """            Thing subject = anchor;
            // Carrying it is not destructive, so it does not get the red confirmation that
            // teaches a player to click through warnings.
            Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                (breaking ? "RR_Portals_RemoveWayInConfirm" : "RR_Portals_MoveWayInConfirm").Translate(),
                delegate { /* Confirmed. The designation stands and the work proceeds. */ },
                delegate { ClearDesignations(subject); },
                destructive: breaking,
                title: (breaking ? "RR_Portals_RemoveWayInTitle" : "RR_Portals_MoveWayInTitle").Translate()));""")])


# ------------------------------------------------------------------ 6. the strings
edit(KEYED, [(
    "  <RR_Frontier_TooManyGatesHeld>",
    """  <!-- Owner direction, 2026-09-30: "and then u lose them forever but maybe allow minify move".
       Uninstalling a way through moves it; deconstructing it ends it. -->
  <RR_Portals_MoveWayInTitle>Move a way into the Backrooms</RR_Portals_MoveWayInTitle>
  <RR_Portals_MoveWayInConfirm>Uninstalling this door will take the way through with it. Your people will carry the doorway and the route it holds, and it will work again wherever it is reinstalled on this company's ground.\\n\\nIf anybody is part-way through it when it comes down, the route will be left broken instead of moved.</RR_Portals_MoveWayInConfirm>
  <RR_Portals_WayThroughMoved>{0} has been installed, and the way through came with it.</RR_Portals_WayThroughMoved>
  <RR_Frontier_TooManyGatesHeld>""")])

print("stage four applied")
