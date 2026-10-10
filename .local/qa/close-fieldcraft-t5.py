# -*- coding: utf-8 -*-
"""Close the superseded Fieldcraft T5 row: the owner chose a second subject."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Fieldcraft T5 is superseded and needs a new subject if it is to exist.**",
     " -- **IT EXISTS 0.12.99-dev AS `RR_Fieldcraft_StandingRelief`, AND THE NEW SUBJECT IS THE "
     "OWNER'S CHOICE AT A SECOND FORK.** This row said the owner approved *a tier, not that "
     "particular number*. Asked again, they picked **the long handover**: `ReliefGraceTicks` 1250 to "
     "**2500**, half an in-game hour to a full one. "
     "**THE OPTIONS WERE MEASURED BEFORE THEY WERE OFFERED, which is the only reason they were "
     "honest.** Every constant in this branch's own subject area was enumerated -- "
     "`GateOperatorRelief`, `CrossForNeed`, `ExpeditionCargo`, `GateWatch`, `CrewPlanner` -- and "
     "**exactly two unclaimed knobs existed**. The other was `CrossForNeed`'s stranding margins "
     "(`AssumedLegTicks`, `AssumedNeedTicks`), which would have made this **the only project in the "
     "tree that buys utility with safety**: those margins exist so nobody is sealed in a maze. That "
     "cost was printed in the option rather than discovered afterwards, and the owner took the other "
     "one. **The third option offered was no tier at all**, recorded with its reason as five "
     "branches already are -- so the choice was a real three-way and not a prompt for a yes. "
     "**It is the right branch for the subject.** Fieldcraft already owns the return drill, the "
     "rescue training and the relief watch; the hand-off at a console is the same question -- getting "
     "people where they need to be without the window paying for it. "
     "**AND THE COST IS STATED RATHER THAN BURIED: it softens a factor 1.1 NAMES.** Workforce is one "
     "of the four things that decide how long a gate holds, and an empty chair is now forgiven for "
     "twice as long. **It is still bounded and the bound still carries its reason** -- a gate holding "
     "a connection with nobody at the controls at all is precisely what the grace exists to forbid, "
     "and doubling a grace is not removing one. Genuine abandonment is still an emergency; it takes "
     "an hour to become one. **Visible where the player already looks**, because the gate's pane "
     "prints who is holding it and how many stations could. "
     "**ONE PLACE DECIDES THE GRACE.** `CompRimroomsGate.ReliefGrace()` is read by the tick that "
     "counts absence, and the two comments that explain why a window is not cut immediately now "
     "point at it rather than quoting the constant -- the counter and its own explanation would "
     "otherwise disagree about when a gate drops, which is this project's most repeated defect. "
     "**THREE INSTRUMENTS WERE RESTATED OUT LOUD, and this is the third restatement this session.** "
     "`proof-research-tier5.py` asserted *four* projects and *five* absences and listed Fieldcraft "
     "among the declined; it asserts five and four now, and **the retired `DECLINED` entry is kept "
     "as a comment rather than deleted** so a later reader learns the branch was once declined and "
     "why. **Claim 2.1 is untouched and still load-bearing:** there is no crew cap, so *the fourth "
     "hand* remains impossible -- and if a cap ever returns, that claim fails and somebody is told "
     "rather than left to build a second Fieldcraft tier for it. **Plant suite 37's "
     "revive-a-Fieldcraft-tier plant was retired** too, because a plant that plants legitimate code "
     "proves nothing; three faults aimed at the tier that now exists replaced it, 24 of 24 caught. "
     "**Docs in the same commit:** the chart's tier and branch tables (five branches reach band 5, "
     "44 projects), the sweep's own outcome row for candidate 5, the wiki's band-5 table, and "
     "`gates.md`, which now tells a reader the grace exists at all -- half an hour, doubled by the "
     "project, and never unattended."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:52], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
