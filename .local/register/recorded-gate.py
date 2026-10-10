# -*- coding: utf-8 -*-
"""A discovered natural gate could never be entered, because entering required a player mark.

Owner: *"when i went to send my pawn through that door with a click, it said somthing like : this
address is already being used"*.

`IsLiveGate` is `IsDesignated` **and** an edge. `IsDesignated` means *the player marked this door
as a way home*, and it also demands `parent.Faction == Faction.OfPlayer` and an **ordinary branch
map** -- none of which is ever true of a door generated inside a coordinate.

So for a frontier door, after a successful discovery:

  * the edge exists and is a real `PortalConnectionKind.Natural` connection;
  * `IsLiveGate` is **false**, so the *"Enter the gate"* option is never offered;
  * `ShouldBeLitNow` is false, so the door **stops glowing**; and
  * `IsFrontierCandidate` is now false too -- `Evaluate` returns `RR_Frontier_AlreadyRecorded`,
    *"that door is already a remembered address"*, which is the message the owner read as
    *"this address is already being used"*.

**A way onward worked exactly once and then went dark and dead.** Every piece of the crossing was
built, registered and correct, and one condition meant for a different kind of door kept it out of
reach. Sixth instance in this run of the same shape.

## The fix

`IsLiveGate` keeps its meaning untouched, because `PortalAddressService` and the emergence rules
depend on it being *"the player marked this and it is on a map they own"*. A second, weaker
question is added -- **is this door an endpoint of a live edge at all** -- and the appearance and
the crossing menu ask that instead. A recorded gate glows and can be walked through whether
anybody marked it or not, which is what a natural gate is.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")

# ------------------------------------------------------------ the weaker question
PROP_ANCHOR = u"""        /// <summary>
        /// A marked door on a branch map that the portal network actually has an edge for."""

PROP = u'''        /// <summary>
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

''' + PROP_ANCHOR

EDITS = [
    (PROP_ANCHOR, PROP),

    # The appearance asks the weaker question too.
    (u"        public bool ShouldBeLitNow() { return IsLiveGate || frontierGate; }",
     u"        public bool ShouldBeLitNow() { return IsLiveGate || recordedGate || frontierGate; }"),

    (u"""            // A way onward is a natural gate that nobody has written down yet, and it is
            // already permanently open. Cached here so Core's glower can ask cheaply.
            frontierGate = IsFrontierGate;
            bool live = IsLiveGate || frontierGate;""",
     u"""            // A way onward is a natural gate that nobody has written down yet, and it is
            // already permanently open. Cached here so Core's glower can ask cheaply.
            frontierGate = IsFrontierGate;
            // **AND ONE THAT HAS BEEN WRITTEN DOWN IS STILL A GATE.** `IsLiveGate` needs a player
            // mark, which a door inside a coordinate never has, so a discovered way onward used
            // to stop glowing the moment it started working.
            recordedGate = IsRecordedGate;
            bool live = IsLiveGate || recordedGate || frontierGate;"""),

    (u"""        /// Recomputed on the same interval as the rest of the appearance, in
        /// <see cref="CompTickInterval"/>.
        /// </summary>
        private bool frontierGate;""",
     u"""        /// Recomputed on the same interval as the rest of the appearance, in
        /// <see cref="CompTickInterval"/>.
        /// </summary>
        private bool frontierGate;

        /// <summary>
        /// Whether this door is an endpoint of a live edge, as of the last appearance refresh.
        /// Cached for the same reason <see cref="frontierGate"/> is: Core asks `ShouldBeLitNow`
        /// whenever it likes, and answering walks the whole edge list.
        /// </summary>
        private bool recordedGate;"""),

    # And the crossing menu offers the gate for a recorded edge, marked or not.
    (u"""            if (!IsLiveGate)
            {
                foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }
                yield break;
            }
            PortalConnectionRecord edge = EdgeFor();""",
     u"""            // **A RECORDED GATE IS A GATE, MARKED OR NOT.** `IsLiveGate` needs a player
            // mark and an ordinary branch map, so a discovered way onward inside a coordinate was
            // never offered a crossing however correctly its edge was registered.
            if (!IsLiveGate && !IsRecordedGate)
            {
                foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }
                yield break;
            }
            PortalConnectionRecord edge = EdgeFor();"""),
]

text = io.open(COMP, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:66]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(COMP, "w", encoding="utf-8", newline="").write(text)
print("a recorded gate glows and can be walked through without a mark")
