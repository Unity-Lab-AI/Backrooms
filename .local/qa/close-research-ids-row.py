# -*- coding: utf-8 -*-
"""Close the research-IDs row: its second half, the entity family sheets, is written."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

KEY = "Research IDs across tiers T0–T6 and the nine branches"

EVIDENCE = (
    " -- **THE SECOND HALF IS WRITTEN 0.12.99-dev AND THE ROW CLOSES.** Owner direction at the fork: "
    "author the broad family sheets, build nothing. "
    "**Sixteen family sheets, and the split between them is the whole point.** **Eleven are "
    "implemented** and their sheets describe what the shipped defs and code actually do -- somebody "
    "who is simply here, somebody who went missing, somebody who can come home, somebody who has "
    "stopped being somebody, what is left, the caretaker who will not leave with you, the echo of a "
    "colonist who is alive right now, an animal that is in here, the building acting, a transmission "
    "with a name in it, and the objects' own testimony. **Five are specified and NOT built**, and "
    "they say so in those words with the question the owner would have to answer first: pursuit as a "
    "family rather than one entity, altered arrivals, containment escape, hostile world-side sites, "
    "and late-game space threats. "
    "**EVERY FAMILY WAS MEASURED, NOT REMEMBERED.** Each sheet's bands, depths, counts and chances "
    "come from the def files; each behaviour from the code. `RR_Inhabitant_Dead*` is placed at "
    "**generation** and at band `Quiet` because *" + Q + "finding one should not wait on a danger "
    "band, and a corpse does not act" + Q + "*; everything that acts is placed on arrival against "
    "the band at that moment. Nothing in these sheets is a creature I invented. "
    "**AND THE SHARED RULES ARE WRITTEN ONCE.** A `family contract` section carries what every "
    "family inherits -- the quiet first visit, half the rooms bare by count, three things at once as "
    "an absolute, two events per opening, the threshold excluded from every effect, existing "
    "`PawnKindDef`s only, hostility enforced in code, seed-derived and never `Rand`, and nothing "
    "ever lured to a gate. **No sheet restates any of it**, because a rule written twice is a rule "
    "that disagrees with itself the first time one copy is edited. "
    "**The document's own status line was corrected rather than left flattering.** It called itself "
    "*" + Q + "pre-code design contract" + Q + "* and said later entities *" + Q + "need their own "
    "completed sheets before their Defs are implemented" + Q + "*. Eleven families earned their "
    "sheets **after** the content, and that is recorded as a departure rather than presented as the "
    "plan; the rule still binds the five unbuilt ones. "
    "**AND AUDITING THE TRAVERSAL RULE THE SHEETS CITE FOUND TWO REAL FAULTS, which is why this row "
    "cost more than a document.** The frozen gate header is repeated at the top of six design "
    "documents and paraphrased in the **published** Workshop copy, and one of its four clauses -- "
    "*" + Q + "everything else comes back ONLY because one of our pawns physically carried it "
    "through" + Q + "* -- has been false since the incursion exception and is more false since "
    "outbound crossing. Corrected in all seven, with the other three clauses left word for word. "
    "**THE SECOND FAULT WAS CODE, AND IT WAS MINE FROM THIS SESSION: a prisoner could cross a "
    "gate.** A prisoner of the colony keeps their **original faction** -- `HostFaction` is what "
    "becomes yours -- so `OutboundCrossingFailureKey`'s *" + Q + "not ours" + Q + "* clause was "
    "**true** for one, and a prisoner neither downed nor in a mental state passed every other "
    "clause. `FindAtDoorstep` **prefers a hostile faction**, so a captured raider standing near an "
    "open gate was transferred into the coordinate. **Invariant 17 forbids exactly that** -- *" + Q
    + "a prisoner can never cross a gate" + Q + "* -- `WorldExit` has always refused one, and "
    "`CargoFailureKey` only ever let one cross **in somebody's arms**. A **quest lodger** was the "
    "same hole with a worse outcome: losing one fails a quest the player never chose to fail. Four "
    "named clauses now refuse, each asserted separately, with `IsSlave` named even though the "
    "faction test already covers it -- **a rule that holds by accident of another clause stops "
    "holding when that clause moves.** "
    "**Checker 29 had NO plant suite**, the second instrument found in that state this session. "
    "Plant suite 42, 15 of 15 caught -- **and it found two more substring-weak rules and two bad "
    "plants of mine**: the once-per-opening bound passed a rename to `...Unused` because the new "
    "name CONTAINS the old one, and one plant edited a `///` comment instead of the code it meant "
    "to break, which is the second time that exact mistake has been made in a plant this session."
)


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [~] ") and KEY in l]
    if len(hits) != 1:
        print("REFUSED: the row matched %d partial row(s)" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[len("- [~] "):].rstrip(), EVIDENCE)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("research-IDs row closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
