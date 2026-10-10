# -*- coding: utf-8 -*-
"""Close journal step 9: variety after the tutorial, and the quest half of the wiki."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Step 9 -- variety after the tutorial, and the wiki for the quest half.**",
     " -- **CLOSED 0.12.99-dev, AND THE VARIETY WAS ALREADY THERE. WHAT WAS MISSING IS THAT A BRANCH "
     "COULD ONLY EVER HOLD ONE JOB.** "
     "**The row's premise was a conflation of two systems.** The three templates it names -- "
     "`rr.survey.onboarding.v1`, `rr.mission.oddconsignment.v1`, `rr.supply.odd.v1` -- are "
     "`ContractRecord` template ids built in code. The **request** line is the XML one, and it "
     "already carries **18 generated families across arcs 4 to 8**, offered **least-asked-first** "
     "with ties broken ordinally and then by the branch seed. `proof-request-generation.py` has been "
     "asserting the per-arc family counts all along. So *" + Q + "a variety to choose from after the "
     "inital tutorial like quests" + Q + "* was built; nobody had measured that it was. "
     "**THE REAL DEFECT, FOUND BY READING THE OFFER GUARD:** both offer routines refused while "
     "`OpenRequest != null`, and `Open` is *offered **or** accepted*. **So accepting a job stopped "
     "the company offering anything else until it was finished or cancelled -- a branch could hold "
     "exactly one job, ever.** That contradicts the owner's own direction in the journal brief: "
     "*" + Q + "with ability to accept more than one quests at a time" + Q + "*. "
     "**And it made two shipped features unreachable rather than merely unused.** The paperwork "
     "ledger lists *" + Q + "every accepted quest" + Q + "* and could never list more than one. The "
     "parallel records desks -- built hours earlier in this same batch, with claims so two writers "
     "cannot take the same page -- had **nothing to be parallel about**. **A feature whose "
     "precondition is impossible is a feature nobody can report as broken**, which is why this was "
     "found by reading a guard rather than by playing. "
     "**ONE OFFER AT A TIME IS KEPT, AND THAT HALF WAS ALWAYS RIGHT.** The offer routine's own "
     "comment says a second simultaneous offer *" + Q + "would turn a tutorial that teaches one "
     "system per step into a list of chores" + Q + "* -- which is reasoning about **questions**, not "
     "about obligations. So `OfferedRequest` is the new guard, `AcceptedRequests` is the new list, "
     "and **the tutorial line keeps the stricter `OpenRequest` test** because it is a sequence where "
     "each step teaches what the next needs. "
     "**The save-validity rule had the same restriction and it was worse:** it counted `record.Open` "
     "and returned `open <= 1`, so **a save holding two accepted jobs would have been judged "
     "invalid**. It counts offers now. "
     "**AND THE PANE COULD NOT HAVE SHOWN A SECOND ONE EITHER.** It drew `campaign.OpenRequest`, one "
     "record. It now draws the offer first -- the only one asking a question -- then every accepted "
     "job in acceptance order, through the **same** method, which already shows the Accept button "
     "only on an offer. One routine, so the two cannot disagree about how a request reads. The "
     "density ratchet is unmoved at 123 because it counts distinct keys rather than instances. "
     "**TWO PROOF CLAIMS WERE ENFORCING THE DEFECT AND ARE RESTATED OUT LOUD.** *" + Q + "only one "
     "request is ever open" + Q + "* and *" + Q + "a save may hold at most one open request" + Q + "* "
     "both passed on code that limited a branch to one job; the worry they named was *two payouts*, "
     "which was never what they tested -- two accepted jobs are two jobs, which is the thing being "
     "asked for. They now assert one **offer**, plus the absence of the old open-or-accepted test, "
     "**because that reading would come back looking like a tidy-up.** "
     "**`proof-request-generation.py` HAD NO PLANT SUITE**, which is how a claim went a whole life "
     "without anybody breaking it on purpose. Plant suite 41, 9 of 9 caught -- **and it immediately "
     "found another weak rule of mine**: the least-asked-first claim tested only that `TimesAsked` "
     "appeared somewhere, and the body names it twice, so gutting the minimum scan left the filter "
     "standing and the claim passed while variety had become *whichever family is first*. Both "
     "halves of the derivation are asserted now. "
     "**The wiki's quest half is written, and only now**, which is what the row asked -- *" + Q + "a "
     "page describing an unbuilt quest is a published lie" + Q + "*. `wiki/company.md` gains the "
     "eighteen families, least-asked-first, one question at a time with as many jobs as you like, no "
     "clock on any of it, two routes of two kinds, and cancellation being the player's right alone. "
     "The paperwork half of the same page landed with the desks."),
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
    print("closed %d step-9 row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
