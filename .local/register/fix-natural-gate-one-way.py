# -*- coding: utf-8 -*-
"""A natural gate is always open, can be closed once, and never re-opened. That is the 5 limit.

Owner, verbatim, three sentences that together are the whole rule:

    "the gate is a natural one and shouuld always be open.... i understand the machine gate
     opening and closing and will kill anyone standing near in front on start up. but the natural
     portals are open always right? except if minified and put elsewhere or in storage"

    "but remember we do need to be able to close natural portals u just can not re open them"

    "thats the whole 5 limit issue"

THREE CORRECTIONS, AND THE FIRST ONE CAUGHT A DEFECT BEFORE IT SHIPPED.

1. **No unstable vortex on a natural gate.** Their vortex fires inside `OpenStargate`, once per
   open, and their wormhole closes itself after about forty seconds idle
   (`IsReceivingGate && _ticksSinceBufferUnloaded > 2500 && !GateIsLoadingTransporter &&
   _sendBuffer.Empty()` -> `CloseStargate(true)`). A permanently-open natural gate is therefore
   **re-dialled every time their timeout closes it**, so with a vortex it would have detonated its
   own doorway roughly every forty seconds, for ever. **The owner caught that by knowing their own
   design, not by reading the code.** An empty pattern is also the honest fiction: a natural gate
   never opens, because it was always there.

2. **Releasing a natural place is PERMANENT.** The package shipped a re-open: the door remembered
   where it led and could open it again, and both the Operations copy and the confirmation said
   so. That is now wrong by owner direction. The gizmo, the method and the three strings that
   promised it are gone, and the copy says what is true -- *the way in closes and does not
   re-open.*

3. **And that is what the five-map limit is for.** Closing a place is how a slot is freed, and it
   has to cost something or it is not a choice. `OpenMapBudget` already counts; what changes is
   that the decision is now one-way, which is what makes the limit bite.

The door itself still obeys the earlier direction -- *"and then u lose them forever but maybe
allow minify move"* -- because minifying and reinstalling the door moves the route with it
through `NotifyAnchorInstalled`. **Moving a gate keeps it; closing its place spends it.**
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
BRIDGE = os.path.join(SRC, "Portals", "StargateBridge.cs")
COMP = os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed", "RR_Portals.xml")

# --------------------------------------------------------------------------- #
# 1. The attach call learns which kind of gate it is attaching.
# --------------------------------------------------------------------------- #
bridge = io.open(BRIDGE, encoding="utf-8").read()

B_EDITS = [
    (u"        internal static bool Attach(ThingWithComps door)\n"
     u"        {\n"
     u"            if (!Available || door == null) { return false; }",
     u"        /// <param name=\"naturalGate\">\n"
     u"        /// True for a way out that was always there, false for a machine a player dialled.\n"
     u"        /// **A natural gate gets no unstable vortex** -- see <see cref=\"SizedProps\"/>.\n"
     u"        /// </param>\n"
     u"        internal static bool Attach(ThingWithComps door, bool naturalGate)\n"
     u"        {\n"
     u"            if (!Available || door == null) { return false; }"),

    (u"                gate.Initialize(SizedProps(door.def));",
     u"                gate.Initialize(SizedProps(door.def, naturalGate));"),
]
problems = []
for old, _ in B_EDITS:
    if bridge.count(old) != 1:
        problems.append("bridge: %d of %r" % (bridge.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in B_EDITS:
    bridge = bridge.replace(old, new, 1)
io.open(BRIDGE, "w", encoding="utf-8", newline="").write(bridge)
print("bridge: Attach takes the gate kind")

# --------------------------------------------------------------------------- #
# 2. The emergence comp: natural attach, and the re-open is gone.
# --------------------------------------------------------------------------- #
comp = io.open(COMP, encoding="utf-8").read()

C_EDITS = [
    (u"            StargateBridge.Attach(near);\n"
     u"            if (far == null || far.Map == null) { return; }\n"
     u"            StargateBridge.Attach(far);",
     u"            // NATURAL on both ends: this is a way out that was always there, not a machine\n"
     u"            // a player dialled, so neither end carries an unstable vortex.\n"
     u"            StargateBridge.Attach(near, true);\n"
     u"            if (far == null || far.Map == null) { return; }\n"
     u"            StargateBridge.Attach(far, true);"),

    # The re-open gizmo.
    (u"""            // The place this door led to, while the company is not holding it open. Offered on
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
            };""",
     u"""            // **THERE IS NO RE-OPEN, AND THAT IS THE FIVE-MAP LIMIT.** Owner, verbatim:
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
            // its place spends it.**"""),
]
problems = []
for old, _ in C_EDITS:
    if comp.count(old) != 1:
        problems.append("comp: %d of %r" % (comp.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in C_EDITS:
    comp = comp.replace(old, new, 1)
io.open(COMP, "w", encoding="utf-8", newline="").write(comp)
print("comp: natural attach, re-open gizmo removed")

# --------------------------------------------------------------------------- #
# 3. The copy stops promising something that no longer happens.
# --------------------------------------------------------------------------- #
keyed = io.open(KEYED, encoding="utf-8").read()

OLD_EXPL = (u"  <RR_Release_Explanation>Releasing a place does not close the way to it. The door "
            u"stays permanently open and remembers where it led, and the place can be opened "
            u"again from that door. What is lost is everything left inside: the space is found "
            u"again as it is, not as you left it.</RR_Release_Explanation>")
NEW_EXPL = (u"  <RR_Release_Explanation>Releasing a place closes the way to it for good. A natural "
            u"gate is open from the moment it is found and stays open, and closing one is the "
            u"only way to free a slot - but it cannot be opened again, and everything left inside "
            u"is gone with it. The door remains, and still remembers where it led; it simply "
            u"leads nowhere now.</RR_Release_Explanation>")

OLD_CONFIRM = (u"  <RR_Release_Confirm>Stop holding {0} open?\\n\\nThe way in stays permanently "
               u"open and remembers where it led, so you can open this place again from the same "
               u"door. Everything left inside will be gone: {1} item(s), and anything your people "
               u"built there.</RR_Release_Confirm>")
NEW_CONFIRM = (u"  <RR_Release_Confirm>Close the way to {0}?\\n\\nTHIS CANNOT BE UNDONE. The gate "
               u"will not open again and this place cannot be reached from it a second time. "
               u"Everything left inside will be gone: {1} item(s), and anything your people built "
               u"there.\\n\\nThis frees one of your held places.</RR_Release_Confirm>")

K_EDITS = [(OLD_EXPL, NEW_EXPL), (OLD_CONFIRM, NEW_CONFIRM)]
problems = []
for old, _ in K_EDITS:
    if keyed.count(old) != 1:
        problems.append("keyed: %d of %r" % (keyed.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in K_EDITS:
    keyed = keyed.replace(old, new, 1)

# The three keys that promised a re-open go with the gizmo that used them.
for key in ("RR_Release_ReopenLabel", "RR_Release_ReopenDesc", "RR_Release_ReopenNoRoomDesc"):
    import re
    keyed = re.sub(r"[ \t]*<%s>.*?</%s>\r?\n" % (key, key), "", keyed, flags=re.S)
io.open(KEYED, "w", encoding="utf-8", newline="").write(keyed)
print("keyed: release copy says permanent, three re-open keys retired")
