# -*- coding: utf-8 -*-
"""Close the more-than-one-desk row."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**More than one write-up desk, for the same reason.**",
     " -- **CLOSED 0.12.99-dev, AND THE ROW'S OWN SENTENCE TURNED OUT TO BE THE FINDING.** "
     "It said this is *" + Q + "parallel by design rather than by accident" + Q + "*. **It was "
     "parallel by accident, and the accident was live.** The desk was already uncapped -- the def "
     "argues for it at length -- and the work giver already scanned every desk, so two colonists "
     "could sit down at once. **They would both write the same report**, because "
     "`TryFindWriteUpWork` returned the first outstanding write-up and knew nothing about who was "
     "already writing it. "
     "**AND THE SECOND SESSION DID NOT MERELY GO TO WASTE; IT LANDED ON THE WRONG REPORT.** The job "
     "re-derived its target every tick and carried its progress across, so the moment the first "
     "writer filed, the second's accumulated progress was tested against the **next** write-up's "
     "requirement -- and a pawn 900 ticks into a 1000-tick report instantly completed a 600-tick "
     "one. **One session of work, two reports filed**, silently, on a branch that looked busy and "
     "correct. "
     "**The repair has three parts and each is useless without the others.** The scan now takes a "
     "`Pawn` and excludes anything another pawn's active job says it is writing. The job **claims** "
     "the report it sat down to write, scribed, and `Resolve()` answers with the claim and never "
     "with a substitute -- so progress can no longer migrate. And the pawn-less overload was "
     "**deleted rather than kept for convenience**: it had no callers the moment it was written, and "
     "an overload that passes no pawn is a quiet way back to the behaviour that caused this. "
     "**A claim is read off the pawns rather than stored.** Nothing is reserved and there is no "
     "claim table to go stale: a pawn who dies, is drafted or is interrupted stops holding a claim "
     "by the only means that matters, which is no longer having the job. Same shape as "
     "`CompRimroomsGateConsole.HasAssemblyJob`. **The limitation is stated rather than hidden** -- a "
     "pawn with the job queued but not current holds no claim, so two can still be dispatched in the "
     "same instant; that is a wasted walk at worst, because the job pins its target at the desk and "
     "`FileWriteUp` is idempotent. "
     "**AND THE PREVIOUS COMMENT ON THAT FIELD ARGUED AGAINST THE FIX.** It said the target must be "
     "*" + Q + "derived, never carried on the job" + Q + "* because carrying it would be a second "
     "copy of a decision the record owns. **That is right about a decision and wrong about an "
     "identity:** which report I sat down to write is a fact about the pawn and cannot live anywhere "
     "else. The record still owns whether it is outstanding. "
     "**Rules 11 to 13 went into checker 28 rather than into a new instrument**, because its subject "
     "already IS this system -- one home, since two derivations of one rule is the defect this "
     "project keeps meeting. Plant suite 36 grew five plants, 20 of 20 caught, **and the plants "
     "found two weaknesses in my own rules**: a substring test that a rename to "
     "`unclaimedRequestId` passed because the new name CONTAINS the old one, and a per-pawn rule "
     "satisfied by **one** of the giver's two call sites while the other went stale. Both are "
     "word-bounded and counted now. "
     "**AND THE WHOLE PAPERWORK SYSTEM HAD NO WIKI AT ALL**, which `grep` settled: *records desk* "
     "appeared in no reader-facing page. `wiki/company.md` gains the section -- what paperwork is, "
     "that nothing is invented at a desk, that more than one desk is more than one writer, the "
     "three-state light, and that the record rather than the book is the authority."),
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
    print("closed %d desk row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
