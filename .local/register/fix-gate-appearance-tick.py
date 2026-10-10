# -*- coding: utf-8 -*-
"""`CompTickRare` never fires on a door, so the gate was never painted. Not once. Ever.

Owner, verbatim: *"as you can see the back wall door is not correctly blue, is not correctly a
stargate portal to the back rooms and does not cortrectly have the blue light glow. so wtf is
going on here? are you even useing the stargate capabilities to for connections to the backrooms
and the map the pawns start on?"*

READ FROM THE RUNNING GAME FIRST, NOT FROM PROOFS. The owner's live session says:

    mapCount                 2            -- the Backrooms coordinate GENERATED
    letters                  1            -- "Branch authorization received", the welcome letter,
                                            which is only sent when SoloGroupOpening returns null
    cell (160,161)           Door         -- "Steel door (1x1)", the emergence door
    its gizmos               "Stop being a way home"   -> IsDesignated is TRUE
                             "Send somebody through"   -> there is a LIVE crossing
    exceptions in the log    0

**So the connection to the Backrooms exists and works.** The answer to *"are you even useing the
stargate capabilities"* is yes, and the live game proves it: the coordinate is there, the door is
marked, the edge is registered, and the crossing is offered. **Only the appearance was wrong.**

THE DEFECT, AND IT IS ONE WORD. `RefreshGateAppearance()` -- which sets the glow radius, the glow
colour, calls `CompGlower.UpdateLit`, and calls `CompColorable.SetColor` -- was called from
exactly one place:

    public override void CompTickRare() { base.CompTickRare(); RefreshGateAppearance(); }

`Verse.Thing.DoTick` dispatches on the def's ticker type:

    if (def.tickerType == TickerType.Normal)      { Tick(); ... TickInterval(tickDelta); }
    else if (def.tickerType == TickerType.Rare)   { TickRare(); }
    else if (def.tickerType == TickerType.Long)   { TickLong(); }

**Core's `DoorBase` declares `tickerType = Normal`, and `Door` and `Autodoor` inherit it.** A
Normal ticker gets `Tick()` and `TickInterval(delta)` and **never** `TickRare()`. So
`ThingWithComps.TickRare` never ran, so `CompTickRare` never ran, so **the only call site of the
only method that paints a gate has never executed on any door in any session.**

Every other line was right. `IThingGlower` is wired exactly as Core requires -- verified in
`CompGlower.ShouldBeLitNow`, which walks `AllComps` and takes one false as decisive.
`CompColorable.SetColor` calls `parent.Notify_ColorChanged()` itself. `UpdateLit` registers and
deregisters with the glow grid. The gate was simply never asked to look like one.

THE FIX, AND WHY IT IS THREE CALL SITES RATHER THAN ONE:

  * `CompTickInterval(int delta)` is what a Normal ticker actually gets, throttled with
    `Thing.IsHashIntervalTick(interval, delta)` -- Core's own interval-safe form, which is correct
    even though 1.6 varies a thing's update rate. `IsLiveGate` walks every portal edge, so doing
    it per tick on every door in a colony is not acceptable.
  * `CompTickRare()` is KEPT, because a modded door def may legitimately be a Rare ticker, and
    this comp is added to door defs rather than to one def we control.
  * `PostSpawnSetup` paints immediately, so loading a save shows a blue gate on the first frame
    instead of after an interval, and `Mark`/`Withdraw` repaint on the click rather than up to
    250 ticks later.

SWEPT. Three tick overrides exist in this package. `RouteMarkers.CompTickRare` sits on `GlowPod`
and `TextBook`, both of which really are `tickerType = Rare`, so it fires. `CompRimroomsGate` uses
`CompTick` and sits only on door defs, which are Normal, so it fires. **This was the only one
mismatched** -- and the mismatch was invisible because the comp and the def live in different
files and neither mentions the other.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")

OLD_TICK = u'''        /// <summary>Rare, because a gate going live is an event and not a per-frame question.</summary>
        public override void CompTickRare()
        {
            base.CompTickRare();
            RefreshGateAppearance();
        }'''

NEW_TICK = u'''        /// <summary>How often a gate is asked whether it should look like one.</summary>
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
        }'''

OLD_SPAWN = u'''            int moved = network.NotifyAnchorInstalled(parent);
            if (moved > 0)
            {
                Messages.Message("RR_Portals_WayThroughMoved".Translate(parent.LabelShortCap),
                    parent, MessageTypeDefOf.PositiveEvent, false);
            }
        }'''

NEW_SPAWN = u'''            int moved = network.NotifyAnchorInstalled(parent);
            if (moved > 0)
            {
                Messages.Message("RR_Portals_WayThroughMoved".Translate(parent.LabelShortCap),
                    parent, MessageTypeDefOf.PositiveEvent, false);
            }
        }

        /// <summary>
        /// Paint on arrival, including after a load.
        ///
        /// Without this a saved gate is an ordinary grey door until the next appearance interval
        /// comes round, which is up to 250 ticks of the player looking at the thing they are
        /// about to report as broken. The base call deliberately runs first and is allowed to
        /// return early; this is the one thing that must happen on every spawn.
        /// </summary>
        public override void PostPostMake()
        {
            base.PostPostMake();
        }'''

OLD_MARK_END = u'''            designated = true;
            branchId = campaign.BranchId;
            campaign.RecordEvent("RR_Event_EmergenceAnchorMarked", parent.GetUniqueLoadID());
            return CompanyActionResult.Applied();'''

NEW_MARK_END = u'''            designated = true;
            branchId = campaign.BranchId;
            campaign.RecordEvent("RR_Event_EmergenceAnchorMarked", parent.GetUniqueLoadID());
            // Painted on the click, not up to an interval later: a player who marks a door and
            // sees nothing change assumes the mark failed.
            RefreshGateAppearance();
            return CompanyActionResult.Applied();'''

OLD_WITHDRAW = u'''            designated = false;
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_EmergenceAnchorWithdrawn", parent.GetUniqueLoadID()); }
            return CompanyActionResult.Applied();'''

NEW_WITHDRAW = u'''            designated = false;
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_EmergenceAnchorWithdrawn", parent.GetUniqueLoadID()); }
            // Unpainted on the click, for the same reason.
            RefreshGateAppearance();
            return CompanyActionResult.Applied();'''

EDITS = [(OLD_TICK, NEW_TICK), (OLD_MARK_END, NEW_MARK_END), (OLD_WITHDRAW, NEW_WITHDRAW)]

text = io.open(COMP, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)

# PostSpawnSetup paints too -- added by rewriting its tail rather than appending a stub method.
SPAWN_OLD = u'''            if (respawningAfterLoad || parent == null || Current.Game == null) { return; }
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null) { return; }'''
SPAWN_NEW = u'''            // **Painted on every spawn, including after a load, and BEFORE the early return.**
            // A saved gate was an ordinary grey door until the next appearance interval came
            // round, which is up to 250 ticks of a player looking at the thing they are about to
            // report as broken.
            RefreshGateAppearance();
            if (respawningAfterLoad || parent == null || Current.Game == null) { return; }
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null) { return; }'''
if text.count(SPAWN_OLD) != 1:
    print("SPAWN ANCHOR PROBLEM: %d" % text.count(SPAWN_OLD))
    raise SystemExit(1)
text = text.replace(SPAWN_OLD, SPAWN_NEW, 1)

io.open(COMP, "w", encoding="utf-8", newline="").write(text)
print("gate appearance now runs on a ticker doors actually have")
