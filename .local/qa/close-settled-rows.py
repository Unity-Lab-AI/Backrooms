# -*- coding: utf-8 -*-
"""Close the open rows the owner's twelve answers settle, each against the answer that settles it.

The decisions and their evidence are recorded in the section above these; this closes the rows
that were waiting on them so the queue stops showing work nobody can pick up.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSURES = [
    ('**"theri 300x300 gate ie the stargate mode',
     "**CLOSED 0.12.98-dev. The one number that was short of the spec is no longer short.** Owner, "
     "asked directly: *\"Raise to 80 as a middle\"* — so `MaxRooms` is **80** and the grid is "
     "**9×9**, reached at depth 4 and deeper, with depth 1 and 2 untouched because the shallow "
     "look is fewer and bigger on purpose. Measured over 200 seeds: `refused 0/200`, `fellback 0`, "
     "depth-3 fill **up** to 47.1%, degree up to 5.49. "
     "Everything else on the row was already built or superseded by measurement: **300×300** ships, "
     "the three unique families are enforced by the validator, the others repeat, and the "
     "*\"10×10 grid at the existing 19-cell spacing\"* half is **superseded** — ten slots measured "
     "**17.1% room fill** because the rock between slots is fixed per boundary, so a finer grid "
     "fills *less*. **Nothing on this row is open any more.**"),

    ('**A real domain, not a `github.io` path.**',
     "**CLOSED AS A DECISION 0.12.98-dev.** Owner: *\"Not yet — leave it on the github.io path\"*. "
     "**And the cost of waiting is zero:** every link the site emits is relative so it follows "
     "whatever domain serves it, `CNAME.example` documents the file, and `check-doc-conformance` "
     "already refuses a malformed `CNAME`. When a domain arrives the work is **one file and two "
     "DNS records**, not a rewrite. Re-opened by the owner saying they have one, not by time "
     "passing."),

    ('Repo, site and the Steam Workshop page driven through Playwright.',
     "**CLOSED AS A DECISION WITH A TRIGGER 0.12.98-dev.** Owner: *\"Not yet — ask again when the "
     "mod is ready to publish\"*. **Nothing in this project touches Steam**: no Playwright, no "
     "account access, no page, no collection. The standing rule that Steam automation needs "
     "explicit permission is unchanged and was honoured by asking. **The question gets asked "
     "again at publication readiness** — it is a trigger, not a forgotten row."),

    ('**Migration decision or declared development-save break**',
     "**DECIDED AND CLOSED 0.12.98-dev.** Owner: *\"Development-save break is allowed — declare "
     "it\"*, which matches what they said earlier and have not changed: *\"we dont have other "
     "peoples saves we just publish it all and update it as we go fixing bugs\"*. **So: saves may "
     "break between development versions, no migration is owed, and the old build is preserved so "
     "a save can be opened by the build that wrote it.** This unblocks removing the one remaining "
     "legacy def — the hidden analysis bench that new starts do not spawn, that cannot be built, "
     "and that no company job uses. **The obligation begins at first publication, not now.**"),

    ('**A `Backrooms` PlanetLayer as a design question, not a capacity one.**',
     "**CLOSED 0.12.98-dev.** Owner: *\"Don't add one — close all three\"*. The measurement that "
     "informed it stands recorded: the five-map cap is **not layer-aware**, our coordinate maps "
     "**already** do not count against Core's settlement limit, and `OpenMapBudget` counts them "
     "deliberately instead — so a layer buys no capacity and adds a navigable world surface a "
     "player would expect to work."),

    ('**Measure before any of it:**',
     "**CLOSED 0.12.98-dev — the measurement is no longer needed.** It was the precondition for "
     "adding a layer, and the owner decided against adding one. **A measurement that can change "
     "no decision is not work**, and leaving it open would read as something somebody should go "
     "and do."),

    ('**The cap itself stays five until the owner says otherwise.**',
     "**CLOSED 0.12.98-dev — it stays, and that is now a decision rather than a default.** The "
     "owner was asked about the layer and declined it; the cap was never the thing in question. "
     "**And it is not really five:** `OpenMapBudget` reads the player's own "
     "`MaxNumberOfPlayerSettlements`, so a player who moves that slider moves the allowance, with "
     "a floor of two because a branch needs somewhere to live and somewhere to go."),
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
    if missed:
        for phrase, count in missed:
            print("NOT CLOSED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
