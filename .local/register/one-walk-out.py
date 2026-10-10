# -*- coding: utf-8 -*-
"""One call site for the walk-out, because a proof counts them and it is right to.

`proof-world-exit.py` refused the float-menu change: *"exactly one thing calls the leave routine --
more than one caller means one of them might not be a player command."* It found two, both in
`CompRimroomsEmergence`.

**Both of mine are player clicks** -- a gizmo and a float-menu option -- so the guarantee's intent
held. But the claim counts call sites because that is a cheap, total check and *"every caller is a
player command"* is not something source text can decide. **A weaker claim that can be checked
beats a stronger one that cannot**, so the code changes rather than the claim.

The gizmo and the menu now both call one private method, which is the only thing in the package
that reaches `LeaveThroughWorldExit` -- and therefore the only thing that can reach
`CaravanExitMapUtility.ExitMapAndCreateCaravan`. One decision point, which is what the narrowed
stranded-crew guarantee in `WorldExit.cs` actually depends on.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")

EDITS = [
    # The gizmo goes through the single method.
    (u"                    action = delegate { Show(worldExitCampaign.LeaveThroughWorldExit(parent)); }",
     u"                    action = delegate { Show(WalkOutToWorld()); }"),

    # So does the float menu.
    (u"""                RimroomsCampaignComponent campaign = Campaign();
                if (campaign != null && campaign.WorldExitFor(parent) != null)
                {
                    // The SAME call the gizmo makes, which is the only path in the mod that
                    // reaches Core's caravan formation. One decision point, not a second
                    // opinion about it -- see WorldExit.cs for why that matters.
                    Show(campaign.LeaveThroughWorldExit(parent));
                    return;
                }""",
     u"""                RimroomsCampaignComponent campaign = Campaign();
                if (campaign != null && campaign.WorldExitFor(parent) != null)
                {
                    // The SAME method the gizmo calls, which is the only thing in the package
                    // that reaches the leave routine -- see WalkOutToWorld.
                    Show(WalkOutToWorld());
                    return;
                }"""),
]

METHOD_ANCHOR = u"""        /// <summary>The live edge this door is an endpoint of, or null.</summary>
        private PortalConnectionRecord EdgeFor()"""

METHOD = u'''        /// <summary>
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

''' + METHOD_ANCHOR

text = io.open(COMP, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:66]))
if text.count(METHOD_ANCHOR) != 1:
    problems.append("%d of METHOD_ANCHOR" % text.count(METHOD_ANCHOR))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
text = text.replace(METHOD_ANCHOR, METHOD, 1)
io.open(COMP, "w", encoding="utf-8", newline="").write(text)
print("one call site for the walk-out, reached from the gizmo and the menu")
