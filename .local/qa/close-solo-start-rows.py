# -*- coding: utf-8 -*-
"""Close the solo/group two-map rows: measured as built, and now guarded.

These four rows were a DESIGN DECISION RECORD written as open rows, which is why they sat open
while the work shipped. Every step of `SoloGroupOpening.Open` exists, in the stated order, and
`proof-startplacement.py` already held the headline claim. What was missing was an assertion that
the retired design cannot come back, which is now two claims and two plants.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSURES = [
    ('**"Two maps at start, coordinate is real"**',
     "**MEASURED AS BUILT AND NOW GUARDED, 0.12.98-dev.** `SoloGroupOpening.Open` does all five "
     "steps in the stated order: a stable coordinate from the branch, its map through "
     "`DestinationService.EnsureSite` — the same path every gate destination uses — the surface "
     "door marked, the connection registered through `PortalAddressService."
     "RegisterEmergenceAddress`, and the party moved inside **last**, so a failure above leaves "
     "everybody standing safely on the surface instead of sealed in with no way home. "
     "**It is also idempotent**, which the row did not ask for: every step answers *already done*, "
     "so a retry after a partial failure finishes the job rather than building a second one. "
     "`proof-startplacement.py` holds it and says so in its own headline."),
    ('**This supersedes the earlier answer**',
     "**THE CONSTRAINT IS STILL REAL AND IS NOW ASSERTED, 0.12.98-dev.** The reasoning was sound "
     "and nothing had been checking it: `GenStep_InsideStart` and `RR_InsideStart` are retired, "
     "archived at `docs/implementation/historical-content/0.12.0-dev/"
     "RETIRED_GENSTEP_INSIDESTART.md`, and **no instrument refused their return** until now. "
     "Two claims added — none in the stripped source, none in the shipped defs — each with a "
     "plant that reintroduces it as real code and a real def element. **A reappearance would not "
     "have looked like a bug**: a solo start would work right up to the moment somebody tried to "
     "register a way home."),
    ('**What this reworks from 0.12.0-dev:**',
     "**CONFIRMED COMPLETE 0.12.98-dev.** Zero references to `GenStep_InsideStart` or "
     "`RR_InsideStart` anywhere in source or the package. `insideStart` now means exactly what "
     "the row says — *the starting people begin in a coordinate* — and it is read in four places: "
     "the setup page's summary line, the def's own validation, the depth the coordinate is created "
     "at, and the single branch that decides whether anybody is moved inside."),
    ('**The cost, stated plainly:**',
     "**STANDS AS THE RECORDED TRADE 0.12.98-dev.** The surface tile is the player's chosen one. "
     "Nothing has changed to revisit it, and the row is the record rather than a task."),
    ('**"this is all open eneded they can play how they choose"**',
     "**HELD, AND IT IS IN THE CODE RATHER THAN ONLY IN THE QUEUE, 0.12.98-dev.** "
     "`SoloGroupOpening`'s own *what it does not decide* section carries the owner's words and the "
     "consequence: the exit exists and is permanently open, and **a group that would rather stay "
     "down there, mine the rock and grow food under thick roof is playing correctly and nothing "
     "nudges them.** The wiki says the same thing in a player's words — no deadlines, and using "
     "the way out is a choice."),
]


def main():
    text = io.open(TODO, encoding="utf-8").read()
    lines = text.split(NL)
    closed = 0
    missed = []
    for phrase, evidence in CLOSURES:
        hits = [i for i, l in enumerate(lines)
                if l.startswith(("- [ ] ", "- [~] ")) and phrase in l]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        at = hits[0]
        lines[at] = "- [x] " + lines[at][6:].rstrip() + " — " + evidence
        closed += 1
    if missed:
        for phrase, count in missed:
            print("NOT CLOSED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
