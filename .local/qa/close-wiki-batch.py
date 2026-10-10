# -*- coding: utf-8 -*-
"""Close the wiki-accuracy, art and doc-comment batch: evidence appended, marker flipped to [x].

The archiver then moves each row to FINALIZED.md and `verify-archive-move.py` proves the transfer
byte for byte. Nothing is deleted here and no description is altered -- the closure note is
appended to the row's own text, which is what "change the status ONLY" means in practice.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

# (unique opening phrase of the row, the closure evidence appended to it)
CLOSURES = [
    ('**"reword the write ups on the wiki"**',
     "**CLOSED 0.12.98-dev. All thirteen pages rewritten from source**, not from a neighbouring "
     "page and not from a doc comment. Six claims were not stale but **wrong**: the free ways "
     "through stop at depth 6 and not 3, the corporation teaches with six requests plus the hinge "
     "and never stops asking, research is nine branches across five bands, `interface.md` listed "
     "13 of 14 panes, `first-hour.md` promised eleven goals and gave six, and `company.md` "
     "advertised selling a bond at 85% which the code refuses on purpose. **Eight claims were "
     "verified correct and recorded as correct** so a later pass does not undo them."),
    ('**"is generic horshit stalle as fuck"**',
     "**CLOSED 0.12.98-dev, and the diagnosis held.** The fix was naming the thing: the two "
     "absolutes the wiki had never mentioned -- **the only clock is the gate** and **every job has "
     "two or more success routes of different kinds** -- are now on the front page and in three "
     "more. Added with them: the window ladder, contact as a branch state, the eight arcs, and "
     "that no research prerequisite is satisfied by time passing."),
    ('**"nothing weve done written up in it over the last few days"**',
     "**CLOSED 0.12.98-dev.** The nine absent systems are written: three gates, the random dial, "
     "the open-map allowance, boarding up for 25 wood, certification and its three training "
     "bills, Release being permanent and losing stock, a stranded crew surviving and being "
     "fetched, the room scale per depth, and the five deep-level materials."),
    ('**The rules the rewrite still has to obey**',
     "**HELD, AND ONE OF THEM BIT 0.12.98-dev.** `check-campaign-absolutes` refused two pages for "
     "the word *deadline* where the prose was **denying** deadlines. The rule scopes a "
     "120-character window against a precise denial allowlist and its own comment warns that "
     "widening it is how a rule stops meaning anything -- **so the prose was reworded and the rule "
     "left alone.** Vocabulary, the wall ceiling, no dev names, no dependency claims, nothing "
     "announced as tested and no build-repo reference all pass."),
    ('**`gates.md` tells players the free doors stop at depth 3.',
     "**CLOSED 0.12.98-dev, page and root cause.** The page says depth 6. `MaximumNaturalDepth` "
     "now carries **one** `<summary>` with the current value first and the superseded three "
     "recorded inside it."),
    ('**`company.md` says the corporation asks for six things.',
     "**CLOSED 0.12.98-dev, and the framing was wrong too.** `CAMPAIGN_CHART.md` is the authority: "
     "six requests teach, the seventh is **the hinge**, and everything after is generated. **It "
     "never stops asking -- it stops teaching.**"),
    ('**`company.md` says four research tiers.',
     "**CLOSED 0.12.98-dev, from the authority rather than the XML.** `CAMPAIGN_CHART.md` §3 is "
     "**nine branches across five progression bands**, all named, and it overrules `ROADMAP.md`'s "
     "T0-T6 by its own opening clause. The page carries the chart's names and the linkage rule "
     "that nothing requires time to have passed."),
    ('**`company.md` advertises selling a bond at 85%',
     "**CLOSED 0.12.98-dev.** The page now says a bond banks at full value and that the company "
     "declines to buy one, with the 85% put where it belongs: ordinary valuables."),
    ('**`interface.md` is the pane-by-pane reference and it is missing a pane.**',
     "**CLOSED 0.12.98-dev.** Places is listed, and **the count is gone from the prose** so the "
     "table cannot go stale the next time a pane lands."),
    ('**`first-hour.md` promises eleven goals and documents six.**',
     "**CLOSED 0.12.98-dev.** All eleven, in the game's own labels, as a table."),
    ('**THE ONE REPORTED "IT WILL NOT OPEN" FAILURE',
     "**CLOSED 0.12.98-dev.** Steps 4 and 8 have their own section in `first-hour.md`, a row in "
     "the troubleshooting table, and `troubleshooting.md`'s *\"every box is ticked\"* section now "
     "**answers with gate control instead of sending the reader to the address.**"),
    ('**A permanent, irreversible, item-destroying action ships with no wiki page at all.**',
     "**CLOSED 0.12.98-dev.** `company.md` and `troubleshooting.md` both carry it: permanent, what "
     "is left behind, the refusals, and that a found place is recoverable from the door that found "
     "it."),
    ('**Certification is the gap that dead-ends a player',
     "**CLOSED 0.12.98-dev.** The three bills, their skill floors and the crafting-spot route are "
     "in `first-hour.md`, `company.md` and the troubleshooting table."),
    ('**"making sure the wiki is accurate not the old shit"**',
     "**CLOSED 0.12.98-dev.** Thirteen of thirteen pages rewritten from the code and the design "
     "authority. **Every count left in the wiki is fixed by an authority** -- nine branches, five "
     "bands, eleven checks, three gates, three crew, three starts -- and `SCENARIOS.md` records "
     "the outpost, town-distortion and company-crisis openings as *\"not promised release "
     "features\"*, so three starts is the final design rather than an interim number."),
    ('**"old wordings that are being copied and pasten from weeks ago"**',
     "**CLOSED 0.12.98-dev, upstream included.** `SCENARIOS.md` still asserted the superseded "
     "2026-10-01 *\"declared requirements\"* position in **three** places -- the exact premise "
     "behind the dependency lie -- and is corrected with the supersession recorded. The source "
     "side is the doc-comment sweep below."),
    ('**"use our slide art as a banner or something /background"**',
     "**CLOSED 0.12.98-dev. All twelve slides used**, assigned by subject, with exactly one repeat "
     "and a stated reason: the two gate pages share the gate slide."),
    ('**"to where text writing is not fighting the art to be read"**',
     "**CLOSED 0.12.98-dev, structurally rather than by opacity.** **No text is drawn over art "
     "anywhere** -- the band sits above the prose and the heading below it, so there is no overlay "
     "a later edit can mistune. Marked decorative so a screen reader skips it, real pixel "
     "dimensions so nothing jumps while it loads, and a deeper crop at narrow widths."),
    ('**The art has to actually reach the published site**',
     "**CLOSED 0.12.98-dev, AND THE PREDICTION WAS RIGHT IN THE WORST WAY.** The first version "
     "referenced the package's own slides at `../1.6/Textures/...` for zero duplication: every "
     "path resolved on disk, the audit passed, twelve refs went level -- and **every banner was a "
     "404 in the browser**, because **Pages serves `/docs` as the site root** and nothing above it "
     "is served at any URL. The art is now **copied into `docs/assets/art/`** and referenced "
     "site-relative. **The guard that was missing is the one that mattered: a published page may "
     "not reference a path that climbs out of the site**, proved by planting the exact bug that "
     "shipped. Read back over HTTP: pages, cover and banners all 200."),
    ('**"make sure the preview image is prominate becasue thats what mod loaders see"**',
     "**CLOSED 0.12.98-dev.** `About/Preview.png` leads the front page as the cover, uncropped, "
     "with a real `alt` because unlike the banners it is content rather than decoration. Verified "
     "200 on the live site."),
    ('**Clear all 29 stacked `<summary>` blocks',
     "**CLOSED 0.12.98-dev, and there were MORE than 29.** Every one repaired by **reuniting the "
     "orphan with the member it documents** (fifteen moves), merging a true duplicate (six), or "
     "dropping a block only once its every word provably survived on the correct member (two). "
     "`check-doc-comments.py` is checker **22** and shipped in the same commit, as this row "
     "required. **Its first version was too weak and a plant walked through it**: it matched a "
     "line that was exactly `/// </summary>` followed by `/// <summary>`, so the one-line "
     "`<summary>x</summary>` form was invisible -- and rewriting it to count openings per doc "
     "block **immediately found six more real faults**. Proved alive against both shapes. Zero "
     "remain; build clean."),
    ('**And the standing lesson, because this one generalises past comments:**',
     "**RECORDED 0.12.98-dev in `NOW.md` as a standing lesson**, with the second half it earned "
     "the same day: *an on-disk audit cannot see a deployment fault.* The battery line now ends "
     "with reading the published site over HTTP."),
]


def main():
    text = io.open(TODO, encoding="utf-8").read()
    lines = text.split(NL)
    closed = 0
    missed = []
    for phrase, evidence in CLOSURES:
        hits = [i for i, l in enumerate(lines)
                if l.startswith(("- [ ] ", "- [~] ")) and phrase in l]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        at = hits[0]
        body = lines[at]
        marker = body[:6]
        lines[at] = "- [x] " + body[6:].rstrip() + " — " + evidence
        closed += 1
        del marker
    if missed:
        for phrase, count in missed:
            print("NOT CLOSED (%d matches): %s" % (count, phrase[:70]))
        print("")
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
