# -*- coding: utf-8 -*-
"""Close the per-row disposition row. The owner's reasoning is right and it is recorded here.

**Owner, 2026-10-05, verbatim:** *"we dont need to do this do we?:\"One job I can do: 199 of your
294 mods have no written verdict yet.\" as the Rimrooms Mod is stand alond only adding to it when
mopds are added? right?"*

**Right.** Checked rather than agreed with, and the check is what settles it.

LAW #0: the row's verbatim text is untouched; the reasoning is appended.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

PHRASE = ("For each workbook row, close its status with evidence: reviewed version, load-order "
          "placement, applicable DLC, behavior used/preserved, patch/adaptor/no-code reason, and "
          "result.")

EVIDENCE = (
    "**CLOSED 0.12.99-dev ON THE OWNER'S OWN REASONING, which is correct and was checked rather "
    "than agreed with.** Owner, verbatim: *\"we dont need to do this do we? ... as the Rimrooms Mod "
    "is stand alond only adding to it when mopds are added? right?\"* "
    "**Measured: 200 Provisional, 94 Settled, 295 parsed rows.** And the split is not arbitrary -- "
    "**a row is Settled exactly where somebody had a reason to look.** All 34 cross-gate work "
    "families, the five optional-mod detections, the storage and hauling family, the two Doors "
    "Expanded compat targets, the multiplayer page's row 196: every one of those is Settled because "
    "building or deciding against something *made* it settled. "
    "**Settling the other 200 from a desk would be inventing findings, and worse than that it would "
    "break D1.** Read what a disposition actually asks for: row 122's is *\"verify stack, weight, "
    "ownership, caravan, and RWT transfer behavior for mission cargo\"*. Those are **runtime** "
    "claims. Writing a verdict for them without a launch is precisely *\"do not announce "
    "compatibility until validation is complete\"* being broken, and the register's own policy says "
    "it in its own words: ***\"Researched\" does not mean \"integrated\"; \"loads\" does not mean "
    "\"compatible\"; \"optional\" does not mean tested.*** "
    "**And nothing depends on the 200 being settled.** The two obligations that consume dispositions "
    "-- the user-facing compatibility report and the release report -- both require *tested* "
    "evidence, and both are already in the test phase. "
    "**So the rule is the owner's sentence, and it is now the recorded rule:** a disposition gets "
    "settled **when something is built that touches that mod, or when a launch produces evidence "
    "about it** -- never as a bulk sweep. The LAW that the register is consulted *before* building "
    "is unchanged and is what keeps this honest: it is an input to work, not a backlog of work. "
    "**THE COUNT FOUND A REAL DEFECT ON THE WAY, which is the only reason the number was worth "
    "counting.** Three rows carried a `stance` of **Required** while `About.xml` has declared zero "
    "`modDependencies` since 0.12.86-dev. Both cards were already precise -- Harmony is *\"required "
    "only for the selected RWT co-op path, not solo Core play\"* and Vanilla Expanded Framework is "
    "*\"required by the selected Gravship Expanded chain; optional to the Core-only Rimrooms "
    "campaign\"* -- but **a one-word column cannot carry *required by something else***, so it said "
    "the opposite of its own card, in the column a reader filters on. **This is the "
    "needs-294-mods defect in the one place nobody had checked.** Harmony and VEF are now Optional "
    "with the qualifier left in their cards, the summary counts follow, **Core stays Required "
    "because Core is the game**, and `check-register-compliance.py` refuses any other Required row "
    "while the package declares no dependencies."
)


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, line in enumerate(lines)
            if line.lstrip().startswith(("- [ ] ", "- [~] ")) and PHRASE in line]
    if len(hits) != 1:
        print("row matched %d time(s); refusing" % len(hits))
        return 1
    index = hits[0]
    raw = lines[index]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[index] = "%s- [x] %s -- %s" % (lead, raw.lstrip()[6:].rstrip(), EVIDENCE)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed the per-row disposition row with the owner's reasoning recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
