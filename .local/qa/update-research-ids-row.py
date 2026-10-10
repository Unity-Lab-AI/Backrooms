# -*- coding: utf-8 -*-
"""Append evidence to the research-IDs row: its research half is finished, and the reason it stays
partial is now a different one."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

KEY = "Research IDs across tiers T0–T6 and the nine branches"

EVIDENCE = (
    " -- **THE RESEARCH HALF IS FINISHED 0.12.99-dev, AND THE REASON THIS ROW STAYS `[~]` IS NOW A "
    "DIFFERENT ONE.** The sentence that kept it partial was *" + Q + "the decision is the owner's "
    "... no project def is written until they pick" + Q + "*. **They picked** -- *" + Q + "All six, "
    "including the fourth crew member" + Q + "* -- and five of the six are built: **Facilities T5, "
    "Measurement T5, Spatial T5, Entities T5 as `MaxEventsPerOpening` only, and Spatial T6**, whose "
    "palette blocker was answered by authoring the sixth band rather than shipping the limitation. "
    "**The sixth was superseded by the owner's own later direction** -- Fieldcraft T5 was the crew "
    "cap, and there is no cap -- so it is recorded as needing a new subject rather than quietly "
    "dropped, and it is the one open row left in the queue. "
    "**So the tree is T0 to T6 across nine branches, 43 projects, and the shape is ragged on "
    "purpose:** four branches reach band 5, one reaches band 6, and the five absences are each a "
    "finding written beside the tier they are absent from. **Proven rather than asserted:** proofs "
    "60, 61 and 62 with plant suites 37 and 38 behind them, 40 of 40 planted faults caught, the "
    "capability bijection still exact, and the vanilla mirror regenerated to 43 paired defs inside "
    "vanilla's own cost range. "
    "**WHAT KEEPS IT PARTIAL IS THE OTHER HALF OF ITS OWN TITLE: the entity family sheets.** "
    "`THREAT_DESIGN_SHEETS.md` carries the authoring sheet and two worked families -- RR-D-001 The "
    "Borrowed Corridor and RR-ENT-001 The Quiet Pursuer -- and says of itself that they *" + Q + "cover "
    "only the vertical slice" + Q + "* and that the rest *" + Q + "remain open design work" + Q + "*, "
    "with an explicit instruction not to *" + Q + "mark the full threat backlog complete" + Q + "*. "
    "**That is content design and it needs the owner**, which is the honest reason for the marker "
    "rather than the stale one it was carrying."
)


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [~] ") and KEY in l]
    if len(hits) != 1:
        print("REFUSED: the row matched %d time(s)" % len(hits))
        return 1
    if EVIDENCE[:60] in text:
        print("already appended")
        return 1
    lines[hits[0]] = lines[hits[0]].rstrip() + EVIDENCE
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("research-IDs row updated; still partial, for the entity family sheets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
