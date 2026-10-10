# -*- coding: utf-8 -*-
"""Close the second batch: stated bounds, the notice's entry points, and two launch-blocked rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSURES = [
    ('**"so dont limit yourself"**',
     "**MADE ENFORCEABLE 0.12.98-dev rather than left as an instruction nobody could check. "
     "`check-stated-bounds.py` is checker 24.** Measured first: **121 numeric caps in the source, "
     "47 with no stated reason at all** — so the instruction was being honoured by habit and "
     "nothing else. "
     "**Scoped to where a bound can refuse CONTENT:** `Generation/`, `Portals/` and `Gate/`, which "
     "is 44 caps and where 8 were bare. All eight now carry reasons **read out of their own use "
     "rather than invented** — the tile search's 512 is a bound on *work* and `Math.Min(count, …)` "
     "means a small world is searched exhaustively; `CandidateBudget = 3` is the depth of a net "
     "that `refused 0/200` says is never needed; `MaximumPendingCrossings` guards a **saved** list "
     "from growing a save file for ever; `DoubleWidthMaxBodySize = 2.5` clears a muffalo at 2.0 and "
     "a dromedary at 2.2 with room rather than sitting on either number. "
     "**`ConnectedWork/` is out of scope and that is a decision, not laziness:** its thirty "
     "`Maximum*` constants are per-tick scan windows under one shared policy (invariant 5), and "
     "thirty paragraphs saying the same thing is how **a checker starts crying wolf** — which this "
     "project has recorded about its own rules twice. The rule refuses an empty scope outright, so "
     "it cannot pass by finding nothing, and a planted deletion fails it."),

    ('**Defer the result chain on the three tick-driven paths so they can announce too.**',
     "**CLOSED 0.12.98-dev, and the row's own premise was wrong about two of its three.** It said "
     "each needs its continuation moved inside the long event. **Two of them needed nothing of the "
     "kind, because they were never ticks:** `DialRememberedAddress` is reached from a "
     "`FloatMenuOption` delegate, and expedition `Dispatch` from a button whose result is read "
     "**inside** the callback — which is precisely where a long event is legal. Both now announce, "
     "each with a claim and a plant. **The exemptions had been written describing the method "
     "instead of reading the caller**, which is the half-wiring `check-call-coverage.py` exists to "
     "refuse, and it is the checker that named both files. "
     "**The third is genuinely not a deferral problem and is now recorded as what it is:** the "
     "found-door path cannot ask *is a map about to be built*, because `Discover` **mints** the "
     "coordinate — and a found door may record a way **out**, which generates no map at all. "
     "Announcing a hold that never comes is the notice becoming the nuisance, which this feature is "
     "explicitly scoped against. Covering it needs a *predicate* for \"this door will mint a "
     "place\", which is design and not a wrapper."),

    ('**"when first loading a new backrooms on gate enter and or using the operations tab machine',
     "**CLOSED 0.12.98-dev. Every path a player can CLICK now announces before the freeze and "
     "closes out after it.** Five of them: the Operations pane's two openings, the gate's own "
     "address gizmo, dialling a remembered address, and dispatching a crew. The last two were the "
     "gate-enter half the row was holding open, and they were never ticks. "
     "**What remains uncovered is two paths a player cannot click**, both recorded with reasons in "
     "`tools/call-coverage.json`: a job toil, where a pawn surveying a found door resolves it "
     "mid-job and the job reads the result, and new-game setup, where there is no frame to draw on "
     "and no game yet to freeze. **Neither is the entry point the owner named.**"),
]

RECLASSIFY = [
    ('**"remember lsd unnerving feeling with all things"**',
     "**RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own words.** It already records "
     "the mechanism as *built and enforced* at 0.12.88-dev and says it stays open because **only a "
     "launch judges a feeling.** That is the definition of the post-completion test phase rather "
     "than of open work: there is nothing left to build, and the next step is the owner reading a "
     "spawn and saying whether it lands."),

    ('Bound active map count, pawn/thing count, graph search, event evaluation,',
     "**RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own words.** It says in its own "
     "text: *\"Bounding is done; profiling is not and cannot be\"*, and that profiling a "
     "long-running save **requires launching the game, which only the owner does.** Every scan is "
     "already a bounded rotating window rather than a prefix, with roughly thirty budgets. **A row "
     "whose only remaining step is an owner launch belongs in the test phase**, not in the working "
     "queue where it reads as something somebody could pick up."),
]


def main():
    text = io.open(TODO, encoding="utf-8").read()
    lines = text.split(NL)
    done = 0
    missed = []

    for phrase, evidence in CLOSURES:
        hits = [i for i, l in enumerate(lines)
                if l.startswith(("- [ ] ", "- [~] ")) and phrase in l]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        lines[hits[0]] = "- [x] " + lines[hits[0]][6:].rstrip() + " — " + evidence
        done += 1

    for phrase, evidence in RECLASSIFY:
        hits = [i for i, l in enumerate(lines)
                if l.startswith(("- [ ] ", "- [~] ")) and phrase in l]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        lines[hits[0]] = "- [T] " + lines[hits[0]][6:].rstrip() + " — " + evidence
        done += 1

    if missed:
        for phrase, count in missed:
            print("NOT TOUCHED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("%d row(s) closed or reclassified" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
