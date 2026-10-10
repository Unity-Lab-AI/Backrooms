# -*- coding: utf-8 -*-
"""Close the four prisoner-crossing rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**A prisoner of the colony may cross a gate, and custody crosses with them.**",
     " -- **BUILT 0.12.99-dev. One new derivation replaced four faction tests, and the faction test "
     "was the whole fault.** `RimroomsPortalCrossingService.InOurCare` asks *does this colony hold "
     "this pawn* -- faction **or** custody -- and the work gate, the ordered gate and eligibility "
     "all read it. **A prisoner of the colony carries somebody else's faction while `HostFaction` "
     "is yours, so `Faction != Faction.OfPlayer` was never a test of whose pawn it is**, and that "
     "single fact produced both of the day's faults: it let a prisoner out through the egress path "
     "and locked them out of every other crossing. "
     "**CUSTODY SURVIVES THE CROSSING, AND THE PLACE THAT COULD BREAK IT IS THE ARRIVAL LORD.** "
     "`GateEgress.GiveArrivalLord` returns early for a prisoner of the colony: **a Lord makes an "
     "actor out of a transferred pawn**, so an assault lord would have a captured raider attack the "
     "coordinate and a defend lord would have them stand guard over it -- either way the player "
     "loses somebody they had taken, through a mechanism they never clicked. With no lord the pawn "
     "falls back to the prisoner behaviour it already had: it looks for a prison bed, and wardening "
     "is one of the twenty-one work types that cross. **A coordinate prison works because nothing "
     "there does anything.** "
     "**And the letter is its own case**, keyed on custody rather than hostility, because the "
     "hostile text says *" + Q + "they came for what you keep there" + Q + "* and the friendly one "
     "says *" + Q + "whatever happens to them in there happened on your watch" + Q + "* -- **both "
     "are lies about somebody still in your hands.** A captured raider is hostile by faction and is "
     "not acting hostile at all."),

    ("**Walking out to the WORLD is a different act and stays refused, and the distinction needs "
     "stating rather than assuming.**",
     " -- **KEPT, AND ITS REASONING REWRITTEN 0.12.99-dev.** `WorldExit.TravellersAt` cited "
     "invariant 17 -- *" + Q + "a prisoner can never cross a gate" + Q + "* -- which is the rule the "
     "owner just overruled, so the refusal would have been standing on a dead reason. **It stands on "
     "its own now: that path calls `PassToWorld`.** It is the one place in the mod that reaches "
     "Core's caravan formation, and a pawn handed to the world pool is alive and no longer the "
     "player's. **The owner's words are *" + Q + "cross path back" + Q + "*; a caravan is not a path "
     "back.** Taking a prisoner along would be losing them rather than sending them."),

    ("**Two judgement calls inside this that the owner did not name, both stated so they can be "
     "redirected.**",
     " -- **BOTH MADE AND BOTH RECORDED IN THE CODE THAT MAKES THEM, 0.12.99-dev.** A **quest "
     "lodger** stays refused in both the eligibility test and the outbound policy: a guest on loan "
     "whose safety is a quest condition is not the owner's subject here, and losing one fails a "
     "quest the player never chose to fail -- **which is the reasoning the prisoner ban claimed and "
     "did not have**, because nothing is lost by moving somebody who remains in your hands. A "
     "**slave** is admitted alongside a prisoner: a slave's faction IS the player's, so refusing "
     "the more-owned category while admitting the less-owned one is a rule nobody could read a "
     "reason for. **Neither is a direction and both are one line to change** if the owner wants "
     "them the other way."),

    ("**Every instrument and document that asserts the old ban has to be restated out loud, and "
     "this is the fifth such restatement this session.**",
     " -- **SIX PLACES, ALL RESTATED RATHER THAN QUIETLY EDITED, 0.12.99-dev.** "
     "**Checker 29** gained a four-clause custody refusal hours earlier and now asserts the "
     "opposite: it requires the old clauses to be **absent** (*" + Q + "the old rule coming back as "
     "a tidy-up" + Q + "*), requires the no-lord line in `GateEgress`, and requires `InOurCare` to "
     "exist -- rules 11 and 12, with its header and its PASS line rewritten. "
     "**`proof-crossing-pack`'s claim was literally titled *" + Q + "Prison Labor's axis" + Q + "*** "
     "and asserted the register's settled line by construction; it is inverted, and it now asserts "
     "the shape of the gate rather than duplicating checker 29's rule. "
     "**Plant suite 42's four custody plants planted the owner's own design**, which proves "
     "nothing, so they are re-aimed at what replaced it: the ban returning, the lodger clause going, "
     "the arrival lord being handed to a prisoner, and `InOurCare` being disabled. 15 of 15 caught. "
     "**The register itself is corrected** -- row 288 called the ban *" + Q + "settled" + Q + "* and "
     "a settled line the owner has overruled is worse than an open question. Its measurement was "
     "right and only its conclusion was wrong, so the measurement is kept and the conclusion "
     "inverted, with the mechanism named: rows 273 Locks, 169 Prison Commons, 175 Prisoners Dont "
     "Have Keys and 41 Area Unlocker. "
     "**`CONNECTED_COLONY_PORTALS.md` said *" + Q + "there is no path through the design where it "
     "flips" + Q + "*** and the owner has now flipped two parts of it; both are tabled there with "
     "their verbatim direction, *prisoners* is out of the never-crosses list, and what did **not** "
     "change is stated beside it -- nothing is ever lured, and the world-tile walk is still refused. "
     "**And the wiki says it where a player reads it**: a prisoner can cross if your zoning and the "
     "door allow it, and they stay your prisoner on the other side."),
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
    print("closed %d prisoner row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
