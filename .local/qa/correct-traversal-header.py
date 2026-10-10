# -*- coding: utf-8 -*-
"""Correct the one clause of the frozen traversal header that the code stopped honouring.

**The header is repeated verbatim at the top of six design documents and paraphrased in the
published Workshop copy, and one of its four clauses is now false.** Parsed clause by clause against
`PortalTraversalPolicy`, which is the single chokepoint and the authority:

    1. "Nothing but this company's own pawns crosses a gate UNDER ITS OWN WILL"
       STILL TRUE. `MayApproachThresholdForTraversal` is false for everything, nothing on the far
       side is ever given a threshold as a destination, and the policy argues this clause explicitly.

    2. "an open gate is never an objective, lure, spawn target, raid route or attack trigger"
       STILL TRUE. This is the half of invariant #1 that was KEPT when the owner rewrote it.

    3. "Everything else comes back ONLY because one of our pawns physically carried it through"
       FALSE since 2026-09-29, and more false since 2026-10-06. A hostile that followed a crew to
       the far doorway may come through it once, and anything standing on your own map may walk out.

    4. the pacing sentence
       STILL TRUE.

So clause 3 is replaced and the other three are left **word for word**, because a frozen rule is not
a paragraph to be rewritten when one sentence of it ages. The owner's own words for the change are
quoted rather than summarised.

**WORKSHOP_COPY.md is the worst instance and is corrected too**: it is player-facing published copy
reading *"nothing crosses a gate under its own will"*, which a reader takes as *nothing ever comes
through*. That is a promise the mod no longer keeps.
"""
import io
import sys

NL = chr(10)

STALE = ("Everything else comes back only because one of our pawns physically carried it through by "
         "ordinary work, including people and monstrosities that are genuinely downed, dead or "
         "imprisoned.")

FRESH = ("Everything else reaches the near side only because one of our pawns physically carried it "
         "through by ordinary work, including people and monstrosities that are genuinely downed, "
         "dead or imprisoned -- **with two owner-directed exceptions, both decided at the one "
         "chokepoint and nowhere else.** A hostile that followed a crew to the far doorway may come "
         "through it once, on an advanced machine, in the worst coordinates (2026-09-29). And "
         "**anything standing on your own map may walk out through an open gate** -- owner, "
         "2026-10-06: *\"not anyone in base, but anyone on your map.. a enemy can break in and cross "
         "the gate to get valuables and members\"*, then *\"hold up now friendlys can too\"*. "
         "Neither is a lure: the gate is never a destination for anybody who is not ours, and both "
         "cross because they were already at a threshold that happened to be open.")

DOCS = [
    "docs/CAMPAIGN_CONTENT_CATALOG.md",
    "docs/GAME_DESIGN.md",
    "docs/PROCEDURAL_SPACE_CONTRACT.md",
    "docs/SCENARIOS.md",
    "docs/SCENARIO_SETUP_AND_PORTAL_NETWORK.md",
    "docs/THREAT_DESIGN_SHEETS.md",
]

WORKSHOP = "docs/WORKSHOP_COPY.md"
WORKSHOP_STALE = "[b]nothing crosses a gate under its own will[/b]"
WORKSHOP_FRESH = ("[b]nothing is ever lured through a gate[/b] -- a gate is never a destination for "
                  "anything that is not yours, though what is already standing at an open threshold "
                  "can cross it")


def main():
    changed = 0
    for path in DOCS:
        text = io.open(path, encoding="utf-8-sig").read()
        if text.count(STALE) != 1:
            print("REFUSED: %s holds the stale clause %d time(s)" % (path, text.count(STALE)))
            return 1
        io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(STALE, FRESH, 1))
        print("corrected %s" % path)
        changed += 1

    text = io.open(WORKSHOP, encoding="utf-8-sig").read()
    if text.count(WORKSHOP_STALE) != 1:
        print("REFUSED: %s holds the published clause %d time(s)"
              % (WORKSHOP, text.count(WORKSHOP_STALE)))
        return 1
    io.open(WORKSHOP, "w", encoding="utf-8", newline=NL).write(
        text.replace(WORKSHOP_STALE, WORKSHOP_FRESH, 1))
    print("corrected %s (published copy)" % WORKSHOP)
    changed += 1
    print("%d document(s) corrected; three of the four clauses untouched" % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
