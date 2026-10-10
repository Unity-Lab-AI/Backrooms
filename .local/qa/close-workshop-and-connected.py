# -*- coding: utf-8 -*-
"""Close the three Workshop write-up rows, and move two connected rows to the test phase.

LAW #0: every original word stays; evidence is appended and the status letter is the only
character changed in place.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

EDITS = [
    ("x", "**The mod page write-up**, linking to the site.",
     "**WRITTEN 0.12.99-dev. `docs/WORKSHOP_COPY.md` section 1.** Title, the short line Steam "
     "shows in a list, and the full body as pasteable markup. **This is the owner's own named "
     "alternative to automating Steam**, verbatim from the row that proposed it: *\"The "
     "alternative is a prepared write-up the owner pastes, which is far less work for whoever is "
     "not doing the clicking.\"* **Nothing here touches Steam** -- no Playwright, no account "
     "access, no page created. **The owner fills in exactly one thing: the site address**, left "
     "as a marked placeholder for the same reason `CNAME.example` is an example and the generated "
     "readme links the wiki by relative path -- a document must not claim a URL that may not "
     "serve. **The posting is the owner's act and is not done.**"),

    ("x", "**The collection**, with its own write-up, linking to the mod page and the site.",
     "**WRITTEN 0.12.99-dev. `docs/WORKSHOP_COPY.md` section 2.** And it answers the question a "
     "collection for a dependency-free mod actually raises, in its own text: **nothing in it is "
     "required, including nothing in it.** It exists because the reader's real question is *what "
     "did you build this against*, and the honest answer is a long list that is **advice to a mod "
     "manager, not an instruction to install anything**. Nothing is announced as tested, per D1, "
     "and the co-op section says plainly that RimWorld Together needs Harmony and that we need "
     "neither. **Two addresses are marked for the owner; the posting is the owner's act.**"),

    ("x", "**Both written from the same source as the site**, so three descriptions of one mod "
          "cannot disagree.",
     "**SATISFIED 0.12.99-dev, and two of the three are stronger than *derived* -- they are "
     "generated.** The public readme is built **from `About.xml`**, so the sentence a player reads "
     "in the mod list and the sentence on the repository are **one copy** rather than two that "
     "agree; and the site's reading order and page summaries are **imported** by the renderer "
     "rather than duplicated, which is the standing rule for anything two generators agree about. "
     "**A Workshop page cannot be generated, because Steam is not a file this repository writes** "
     "-- so the third is derived from the same two sources and from nothing else, with **each "
     "section's origin recorded beside it**: the opening is `About.xml`'s description, the play "
     "sections are the wiki's own pages, the honesty section is `WHATS_NEW.md`'s four statements "
     "so it cannot be softer than the repository's, and credits is the credits page sentence for "
     "sentence. **Anything in it that is not in one of those two sources is a defect**, and when "
     "`About.xml` changes the file is re-derived rather than patched."),

    ("T", "Implement cross-map job discovery, destination targets, route costs and reservations; "
          "preserve native per-pawn schedules and restrictions.",
     "**MOVED TO THE TEST PHASE 0.12.99-dev -- THE PARENTHETICAL WAS A 0.5.0-dev STATUS NOTE AND "
     "IS STALE.** It says discovery, destination targets, bounded routing, planning leases and "
     "real native destination reservations exist *\"and are proven for the storage-hauling family "
     "only; the other families are not implemented\"*. **Thirty-one families are implemented**, 23 "
     "of them deployments, and `research/WORK_TYPE_COVERAGE_AUDIT.md` shows every work type in "
     "Core and all five expansions either covered or decided against with its reason recorded -- "
     "plus, as of this batch, the thirteen work types the 294 profile adds. Native priorities, "
     "schedules and restrictions are preserved and the handling closed earlier. **The row's own "
     "last clause is what remains:** *\"runtime acceptance is open\"*, and only the owner launches."),

    ("T", "Implement connected-site scheduling/streaming and measure performance after an "
          "owner-launched build.",
     "**MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words.** It says *\"Scheduling and "
     "streaming ship. Measuring performance requires an owner-launched build, which is the one "
     "thing this project cannot do for itself.\"* **A row whose only remaining step is an owner "
     "launch does not belong in the working queue**, where it reads as something somebody could "
     "pick up today. Every scan in `ConnectedWork/` is already a bounded rotating window rather "
     "than a prefix, by invariant 5, with roughly thirty budgets -- so the bounding half is done "
     "and the measuring half is a launch."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    missed = []
    done = 0
    for status, phrase, evidence in EDITS:
        hits = [i for i, line in enumerate(lines)
                if line.lstrip().startswith(("- [ ] ", "- [~] ")) and phrase in line]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        index = hits[0]
        raw = lines[index]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[index] = "%s- [%s] %s -- %s" % (lead, status, raw.lstrip()[6:].rstrip(), evidence)
        done += 1
    if missed:
        for phrase, count in missed:
            print("NOT EDITED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("edited %d row(s)" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
