# -*- coding: utf-8 -*-
"""Close journal steps 5, 6, 7 and 8. Step 9 stays open."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Step 5 -- the branch ledger, listing every accepted quest.**",
     " -- **BUILT 0.12.99-dev in the Operations requests pane, and the owner's premise was exactly "
     "right: nothing ever prevented several quests at once.** "
     "`requests` is a list; the tutorial line simply hands out one at a time. **What was missing was "
     "the index**, which is now a row per accepted quest carrying its label, *N of M filed*, and the "
     "light. "
     "**Accepted quests only, which is what makes it a ledger rather than a second offer board** -- "
     "the pane above it is already that, and a ledger answers one question: *what has this branch "
     "taken on, and what does each one still need from me.* "
     "**Every row carries the NEXT STEP as well as the state**, because a status line only helps "
     "somebody who already knows the procedure exists. That is the lesson the record book's own "
     "inspect card learned when the owner reported *" + Q + "it was confusing at what i was suppose "
     "to do with it" + Q + "* -- so green says haul it into a beacon radius, amber says the work is "
     "filed and no book agrees, and dark names the next write-up and says to assign somebody. "
     "**And it is silent when there is nothing to say.** No accepted quest wanting paperwork, no "
     "section at all: a heading over an empty list is the permanent furniture that teaches a player "
     "to stop reading a pane."),

    ("**Step 6 -- the quest-bound click actions.**",
     " -- **BUILT 0.12.99-dev. Three actions, and each appears only when it can be taken.** "
     "**Write up: <kind>** sends the pawn to the nearest **reservable** desk, naming what is about to "
     "be written. **File this in the records archive** hauls it to a shelf a gate links in the "
     "archive role. **Send this to the company** appears only while the light is green. "
     "**Absent rather than greyed out, deliberately.** An option that shows up disabled with an "
     "explanation is a sentence the player reads on every right-click for the rest of the campaign, "
     "which is the opposite of the owner's *" + Q + "keep it very concise asnd to the point" + Q + "*. "
     "**NONE OF THEM INVENTS A JOB.** *Write up here* is the same work giver's job, ordered rather "
     "than scheduled; the other two are Core hauling. **So a player who leaves everything to work "
     "priorities gets the identical outcome more slowly, and nothing behaves differently because it "
     "was clicked.** "
     "**The archive target is asked of the gate links rather than of the nearest shelf**, because "
     "`HasArchivedCustody` reads custody from those links -- offering the nearest *shelf* would send "
     "a pawn across the base to a container that does not count. And reservation is checked **before** "
     "the option is offered, so when every desk is taken the option is absent instead of present and "
     "futile."),

    ("**Step 7 -- the book goes back by beacon radius.**",
     " -- **BUILT 0.12.99-dev, and it cost nothing new, which is why it was the recommended option.** "
     "It reuses the contract `ValuablesExchange` and Core's `OrbitalTradeBeacon` already have -- *what "
     "is in the circle is what is on the table* -- so a player learns no new idea and Core already "
     "draws the radius. **The facility ships eight beacons** where the owner placed them, so the "
     "delivery surface was on the map before this existed. "
     "**Three properties follow from using a radius rather than a courier or a gate.** The **player** "
     "controls the timing, and **§1.1 binds: there is no deadline on a write-up, ever** -- a finished "
     "book may sit on a shelf indefinitely. It **cannot pay twice**, because settlement runs through "
     "`PostTransaction` on the request's own operation id and that idempotence is not re-implemented "
     "here, it is **asked**. And a book inside a radius by accident is still a choice the player made, "
     "the same as anything left in a trade beacon's circle -- with a letter naming every quest that "
     "went, so it is never silent. "
     "**The light is the gate and it is asked, not re-derived.** `LightFor` already decides whether "
     "the paperwork is complete, the book exists, agrees and is in custody; re-testing those four "
     "conditions in the sweep would be a second derivation of the one question this subsystem is "
     "about. "
     "**A refused payment does not take the book** -- the player would otherwise lose the deliverable "
     "and the money, and the next sweep retries with it still green. The stamp is cleared **before** "
     "the book is destroyed, so nothing can ever find a half-collected book. "
     "**And the beacon's radius is now a public property rather than two readers of `Props.radius`**, "
     "which is the same one-derivation rule applied to a number."),

    ("**Step 8 -- a new book per accepted quest, by drop.**",
     " -- **BUILT 0.12.99-dev through the SAME drop path, which is the whole point.** The same "
     "`DropPodUtility.DropThingsNear` call, the same relief drop cell and the same company-issued "
     "marking `RecordBookDelivery` already uses -- **one delivery mechanism in this mod rather than a "
     "second place to fix the next time a drop lands somewhere wrong.** "
     "**Driven by the record rather than fired at acceptance, and that is not laziness.** "
     "`AcceptRequest` could have dropped a book inline in one line. Asking *does every quest that "
     "wants paperwork have a book* on the company tick instead handles **three** cases where firing "
     "at acceptance handles one: a drop that failed, a book burned a week later, and a save loaded "
     "from before this existed. **The condition is what matters, not the moment.** "
     "**It is not a tap.** `BookFor` decides, so a book already stamped for that quest is the answer "
     "-- a player cannot farm books by cancelling and re-accepting, and the corporation does not send "
     "a second for one left on a shelf. **And a quest with no paperwork gets no book**, which is most "
     "of them. "
     "**One pod per company tick, deliberately.** Accepting four quests should land four pods over "
     "four ticks rather than one crate of four identical-looking books, because each is bound to its "
     "own quest and a player sorting that pile is the opposite of helpful. "
     "**Stamped at a tally of zero when it is made**, so the book is bound from the moment it exists "
     "and nothing ever has to scan for an unbound book to adopt later. **That added a second "
     "`StampForQuest` call site and checker 28 refused the batch for it** -- correctly. Reading it "
     "showed the call was legitimate, so **the rule became stronger rather than looser**: any number "
     "of places may bind a book, and **every one must pass the record's own `WriteUpsFiled.Count`**, "
     "never a literal. That is the invariant that actually keeps the record authoritative, and the "
     "caller count never was. Plant suite 36 is **14 of 14**."),
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
    print("closed %d journal step(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
