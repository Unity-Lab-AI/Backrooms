# -*- coding: utf-8 -*-
"""Close the four exploration rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**The exploration toggle, ordered like drafting.**",
     " -- **BUILT 0.12.99-dev, AND THE OWNER CHANGED THE DESIGN MID-BUILD FOR THE BETTER.** "
     "Verbatim, 2026-10-06: *" + Q + "survey should go hand in hand with the auto explore and person "
     "has task to write in journal when exploring each room for like 20 seconds" + Q + "*. **So the "
     "survey IS the journal task rather than a side effect of walking through**, which is a change of "
     "**cause** with the same **effect** -- and that distinction is what kept it small. "
     "`CompRimroomsExplorer` is the toggle, on `Human` by patch beside `CompRimroomsSurvivor`, "
     "**dormant on everybody who was not asked**. The gizmo appears only on a player colonist standing "
     "in a coordinate, because a toggle that can be switched on and does nothing is worse than one "
     "that is absent: the player would conclude the feature is broken. It uses **Core's own draft "
     "icon**, since drafting is the owner's comparison and the player already knows that button. No "
     "new art. "
     "**Toggling it ends the current job**, exactly as drafting does, so the order takes effect now "
     "rather than when the current haul finishes. "
     "`JobDriver_RRExploreRoom` walks to a cell in the room and writes for **`RoomSurveyTicks = "
     "1200`** -- sixty ticks a second, so **twenty seconds at normal speed**, the owner's own figure, "
     "with the conversion written down so nobody rediscovers it. "
     "**THE BOOK IS REQUIRED AND THAT IS THE POINT OF HAVING ONE.** No record book, no job, and the "
     "toggle switches itself off with a message naming the pawn -- *" + Q + "has no record book, so "
     "there is nothing to write a survey into" + Q + "*. An explorer without a book is a colonist on "
     "a walk, and silently walking a maze to no effect is **the exact shape of the flower-pot defect "
     "the owner reported**. "
     "**Marking is one derivation.** `FirstSliceSiteComponent` has marked rooms surveyed since long "
     "before this existed, so the rule was **extracted** to `MarkRoomSurveyed` and the job calls it: "
     "the same event line and the same field observation whether a player walks a crew through by hand "
     "or orders an explorer. **Two copies of the effect would have drifted the first time the event "
     "line changed.** "
     "**And the pawn is never trapped.** `GateWatch.MustLeave` in the `FailOn` and again every tick, "
     "and the job is **suspendable and casually interruptible** -- a survey is not a scarce window "
     "anybody is holding, so a pawn who needs to eat eats, and the toggle stays on so they resume."),

    ("**Completion is a real state, not a guess.**",
     " -- **BUILT 0.12.99-dev, AND IT IMMEDIATELY CAUGHT ME CREATING THE SOLO-START DEFECT A SECOND "
     "TIME.** "
     "Completion is **every room the planner authored that has a way in**, read off the room records "
     "-- *not* every cell unfogged, because a sealed pocket behind unmined rock would make completion "
     "unreachable and the owner's notice would never fire. "
     "**Sealed vaults are excluded on `Links.Count == 0`, the same test and the same reason as "
     "`ValidatePlacedLayoutCore`.** A vault is authored with no doors on purpose and is reached by "
     "mining; counting it would make any coordinate holding one permanently incomplete. "
     "**AND THE SURVEY WRITE-UP'S PRECONDITION HAD THE OTHER RULE, FOR ONE BUILD.** "
     "`WriteUpPrecondition.SurveyComplete` tested `room.Surveyed` on **every** room, so on a "
     "coordinate with a vault the write-up this entire feature exists to unlock **could never be "
     "written, with nothing anywhere saying why.** That is precisely the defect that killed the solo "
     "start -- the planner and the layout validator disagreeing about a vault -- reproduced one "
     "subsystem over, **and it was caught by writing the second rule down beside the first.** "
     "`Complete` is now `public static` and both callers ask it, so **the notice and the paperwork "
     "mean the same thing by construction.**"),

    ("**Exploration produces journal work when it completes.**",
     " -- **BUILT 0.12.99-dev, and it needed no new mechanism at all, which was the point of putting "
     "it in the journal brief rather than beside it.** "
     "`RR_WriteUp_Survey` is a `RimroomsWriteUpDef` with precondition `SurveyComplete`, declared in "
     "the same file as the owner's four named kinds and asked for by `RR_Request_ClientSurvey` -- "
     "whose own label is *" + Q + "a client wants a coordinate written up" + Q + "*. "
     "**ONE entry for a finished coordinate, not one per room**, which is the owner's own scoping: "
     "*" + Q + "and exploration need journal entry work stuff" + Q + "* narrowed by the next message "
     "to *" + Q + "once completed" + Q + "*. A write-up per room would bury a branch in paperwork for "
     "walking down a corridor -- **and the per-room work already exists as the twenty-second journal "
     "task**, so a second per-room report would be the same work charged twice. "
     "**It is written at the records desk like every other kind**, goes through the one writer, stamps "
     "the book, and lights the quest. So exploring a coordinate end to end produces a deliverable "
     "through machinery that was already built and tested."),

    ("**And the company pays for it.**",
     " -- **ALREADY WIRED 0.12.99-dev through the beacon return, and stating that is the row.** "
     "Owner: *" + Q + "can get $$$ form companty and such" + Q + "*. A completed survey is a "
     "deliverable, and `RR_Request_ClientSurvey` pays its `paymentUsd` when its book is collected out "
     "of a credit beacon's radius -- so **the exploration payout is the quest payout, not a second "
     "money path.** A separate reward would have been a second place that pays for one piece of work. "
     "**§1.2 is satisfied by the request rather than by anything added here**, and it is satisfied "
     "naturally: a survey has two genuine routes of different kinds, **Document** the finished map or "
     "**Testify** to what the crew saw where a record was lost, both already authored on that "
     "request. "
     "**§1.1 binds too: no clock on the survey**, however long the maze takes. The explore toggle has "
     "no timer, the write-up has no deadline, and a finished book may sit on a shelf indefinitely -- "
     "which is the same absolute the whole request system is built on and the reason there is nowhere "
     "in the shape to put an expiry."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:44], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d exploration row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
