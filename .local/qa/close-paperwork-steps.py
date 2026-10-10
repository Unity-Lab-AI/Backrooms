# -*- coding: utf-8 -*-
"""Close journal steps 2, 3 and 4. Steps 5 to 9 stay open."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Step 2 -- the write-up kinds go on `RimroomsRequestDef` as data.**",
     " -- **BUILT 0.12.99-dev. `RimroomsWriteUpDef` is a Def, and the ellipsis in the owner's "
     "sentence is why.** "
     "*" + Q + "lab nots, research write up, investigation, analysis, ... what ever the task "
     "requires" + Q + "* names four and says the list is open, so a fifth kind must not need a "
     "recompile. That is the same reasoning `RimroomsGateEquipmentDef`, `RimroomsInhabitantDef` and "
     "`RimroomsAnomalyEventDef` already carry: this mod treats *a named kind of thing the player "
     "meets* as data. **Five ship** -- lab notes, investigation, analysis, research write-up, and a "
     "survey report for exploration to post. "
     "**THE ONE THING A NEW KIND CANNOT INVENT IS A PRECONDITION, and that asymmetry is deliberate "
     "rather than an oversight.** A precondition is a question asked of real saved state and that "
     "question is code, so `WriteUpPrecondition` is an enum: a new kind reuses any of the six for "
     "free, and a genuinely new *condition* costs a line. **An extension point that silently "
     "answered `true` would be worse than one that does not exist**, which is why the switch's "
     "`default` refuses. "
     "**Declared on the request, never inferred.** A quest called *" + Q + "Analysis of coordinate "
     "4-A" + Q + "* must not acquire an analysis write-up because something matched a word in its "
     "label, and a request's success routes are how it is *finished* rather than what has to be "
     "*filed*. `ConfigErrors` resolves every defName at load and refuses a duplicate, because a "
     "duplicate is a tally of *" + Q + "1 of 2" + Q + "* that can never reach 2 -- **a light that "
     "never comes on, which is the worst failure shape here: the player would see outstanding "
     "paperwork, assign somebody, and watch nothing happen for ever.** "
     "**And all five are reachable, which an instrument proved rather than a reading.** Checker 28 "
     "refused the batch with **three declared kinds no request asked for**, so lab notes went to "
     "`RR_Request_AssembleAndCalibrate` (the quest that *is* the gate steps), the survey report to "
     "`RR_Request_ClientSurvey` (whose own label is *" + Q + "a client wants a coordinate written "
     "up" + Q + "*), and the research write-up to `RR_Request_ChooseADirection`, the one tutorial "
     "request offering a Research route. **The fix for dead content is to reach it, not delete it.**"),

    ("**Step 3 -- the records desk, and the work giver that staffs it.**",
     " -- **BUILT 0.12.99-dev. `RR_RecordsDesk`, and the art rule held while the content rule bent.**"
     " `CONTENT_REUSE_POLICY.md` gains its **second approved exception**, after the original menu "
     "images, and the owner was shown the cost in the option text before choosing it. "
     "**The def carries Core's own `Things/Building/Furniture/Table1x2`, Core's graphic class, Core's "
     "stuff system and Core's damage corners.** One new def, zero new pixels -- because the record "
     "that retired the old custom items says *" + Q + "The breach was the ART, not the defs" + Q + "*, "
     "and checker 28 now refuses a non-Core texture on this def outright. "
     "**A plain `Building` rather than a `Building_WorkTable`, and the reason is a trap avoided.** A "
     "work table exists to carry a bill stack, and paperwork is not a bill: the job is driven by what "
     "a quest still owes, which the company record already knows. **A bill stack would be a second "
     "place saying the same thing, and a player could delete the bill for work the company is still "
     "waiting on.** No power either -- the owner's words are *" + Q + "the journals are taken to a "
     "table and written out" + Q + "*, and making it need a generator would mean losing power also "
     "stops a branch reporting, which punishes the wrong failure. "
     "**UNCAPPED, which is the owner's *" + Q + "u can have more than one" + Q + "* and is NOT the "
     "console's four.** Four is the owner's number for a **scarce shared** resource, a gate's window. "
     "A desk is neither scarce nor shared; it is a work station, and RimWorld has never capped one. "
     "`CanReserveSittableOrSpot` is what stops two colonists being sent to the same chair, so **the "
     "number of desks built is the number of pawns writing at once, with no rule to tune.** "
     "**The job is ordinary work and the floor is the gate's own.** `priorityInType` **90**, below "
     "calibration's 100 and reconditioning's 102, because a lapsed assembly blocks every expedition "
     "and a report blocks nothing until a player wants to send it. `RR_WriteUp` is **suspendable and "
     "casually interruptible** -- the exact opposite of `RR_OperateGate`, and the contrast is the "
     "decision: a gate window is something somebody might reasonably want held through discomfort, a "
     "report is not. **`GateWatch.MustLeave` is still asked in the `FailOn`, again every tick, and "
     "once more in the work giver before the job is even offered** -- because a pawn starved to death "
     "at a comms console, and a starved pawn at a desk is the same defect one subsystem over."),

    ("**Step 4 -- one writer, two readers, then the green light.**",
     " -- **BUILT 0.12.99-dev, AND THE RISK THE OWNER TOOK IS NOW SPENT RATHER THAN CARRIED.** "
     "*" + Q + "Both, and they must agree" + Q + "* was chosen with its cost printed in the option: "
     "two things holding one truth is *" + Q + "two derivations of one rule" + Q + "*. "
     "**`FileWriteUpAndStamp` is the single operation**: it advances `RequestRecord.writeUpsFiled` "
     "and stamps the book, **record first**, in one call. So a mismatch cannot be produced by the mod "
     "working normally -- only a foreign book, a hand-edited save, or damage. "
     "**The order is load-bearing and a plant proved it.** If the stamp fails, the branch has done "
     "the work and holds a book that disagrees, which reads as amber and says *re-issue one*. The "
     "reverse order would stamp a book for work the record never recorded -- **a book that claims "
     "something false** -- and checker 28 compares the two call positions to keep it that way. "
     "**Three states, and the third is what makes the design safe.** **dark**: write-ups "
     "outstanding. **green**: all filed, book present, in custody, and carrying at least the "
     "record's tally. **amber**: the record is complete and no agreeing book exists. **Amber is why "
     "the record is the authority** -- burn the book, lose it in a coordinate, leave it on a crew who "
     "did not come back, and the branch has lost a **deliverable rather than a month of work.** That "
     "is recoverable; the alternative is not. "
     "**The agreement test counts rather than trusting the stamp**, because a book stamped for the "
     "right quest with a smaller tally is a book from before the last write-up -- which is exactly "
     "the disagreement the owner asked to be visible instead of papered over. And `StampForQuest` "
     "only ever counts **up** for the same quest: a stale stamp from a resumed job would otherwise "
     "make a current book read as out of date and tell the player to fix nothing. "
     "**AND A BUG IN MY OWN LOGIC WAS CAUGHT BY READING IT BACK, NOT BY A TEST.** The first draft "
     "assigned `stampedQuestId` **before** testing whether the quest had changed, which made that "
     "branch dead code -- a book re-stamped for a *new* quest with a lower tally would have kept the "
     "old quest's count. "
     "**Custody is asked of one derivation, which required a refactor rather than a copy.** "
     "`EvidenceSettlement.HasArchivedCustody` took an `EvidenceRecord`, and a quest book is not one. "
     "Writing a second custody test would have been the very defect this row is about, so the rule "
     "was **extracted to a `Thing` form that both callers ask**, and checker 28 asserts there is "
     "exactly one. "
     "**Checker 28 is `check-quest-paperwork.py`, ten rules, and plant suite 36 is at 12 of 12 -- "
     "after finding two false greens in it.** One rule allowed 400 characters of slack around the "
     "`default:` refusal, so a plant that changed it to `default: return true;` passed on the "
     "original refusal further down. The other tested that the work giver *mentions* the desk, while "
     "the giver names it twice -- so a plant that pointed the **guard** at a different def entirely "
     "sailed through. **A guard that accepts any matching text in the vicinity is not reading the "
     "guard.**"),
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
    print("closed %d paperwork step(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
