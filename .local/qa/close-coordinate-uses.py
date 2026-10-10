# -*- coding: utf-8 -*-
"""Close the four coordinate-uses rows against the wiki pass that shipped."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**The wiki must stop saying the company loop is the game.**",
     " -- **FIXED 0.12.99-dev, ON THREE PAGES, BECAUSE THE FRAMING WAS IN THREE PLACES.** "
     "`first-hour.md` said *" + Q + "That loop is the game" + Q + "*; the line is gone and the five "
     "steps now end on the clock rule alone, followed by a section titled **That is the company's "
     "loop, not the game**. `backrooms.md` carried the same claim in its own words -- "
     "*" + Q + "The point of a crossing is a record" + Q + "* -- now *" + Q + "**One** point of a "
     "crossing is a record. It is the one the company pays for." + Q + "* And `index.md` undersold "
     "it at the front door with *" + Q + "paperwork about both" + Q + "*, which now carries "
     "**" + Q + "The contracts are a job, not the game" + Q + "**. "
     "**Finding the third one was the point of grepping rather than editing the page the owner "
     "quoted.** A reader who only ever opens the front door would still have been told the narrow "
     "version, and the two pages that agreed with each other were the reason the framing felt "
     "authoritative. `check-doc-conformance` passes with all three inside the 360-character wall."),

    ("**Document using a coordinate for every purpose the owner named**",
     " -- **WRITTEN 0.12.99-dev as `backrooms.md` §A coordinate is a map you can use, AND EVERY ROW "
     "OF IT WAS MEASURED FIRST.** "
     "A seven-row table covering the owner's list in their order: **a prison** (wardening crosses, "
     "and so does the food), **storage**, **an isolated safe room**, **a workshop** (all five bill "
     "families cross), **a mine**, **a farm**, **a field hospital**. "
     "**The headline number is read off the audit rather than asserted:** `WORK_TYPE_COVERAGE_AUDIT` "
     "shows **21 of the game's 23 work types cross a gate**, and the two that do not are `Patient` "
     "and `PatientBedRest` -- *" + Q + "things that happen to a pawn rather than jobs you "
     "assign" + Q + "*, which is a sentence a player can check against their own work tab. "
     "**The practical cost is stated where there is one**, which is what stops the section being a "
     "brochure: the roof is `RoofRockThick`, confirmed in `BackroomsContainment`, so there is no "
     "sunlight and anything that grows needs lamps **and the power to run them** -- and nothing "
     "drops through thick rock either, which is the same fact read as a benefit. "
     "**And the mod's own source had already said the intent out loud**, which is why this is a "
     "documentation fix and not a feature: `SoloGroupOpening` says a group that would rather "
     "*" + Q + "stay down there, mine the rock and grow food under thick roof is playing correctly "
     "and nothing nudges them" + Q + "*. The wiki had been contradicting the code's stated design, "
     "which is the worst direction for that disagreement to run."),

    ("**Guest quarters need the honest limit stated, not a promise.**",
     " -- **STATED 0.12.99-dev as a named limit rather than quietly omitted.** "
     "`backrooms.md` §Two honest limits opens with **" + Q + "No guests arrive" + Q + "**: a "
     "coordinate is not a settlement on the world map, so faction visitors and caravans have "
     "nowhere to travel to, and guest quarters plus any mod's hospitality content **belong at the "
     "surface base, where they work exactly as they always have.** "
     "`RimroomsDestinationMapParent` is a `MapParent`, not a `Settlement`, which is what that rests "
     "on, and register row 270's disposition agrees: *" + Q + "optional native guest economy; not a "
     "cross-company visit system" + Q + "*. "
     "**AND A CLAIM WAS NARROWED BEFORE IT SHIPPED, WHICH IS THE PART WORTH RECORDING.** The first "
     "draft said traders do not travel to a coordinate either. **That was not measured:** orbital "
     "trade is a map-scoped incident and nothing in this mod gates incidents on a destination map, "
     "so the sentence was an inference wearing the clothes of a fact. It now claims only visitors "
     "and caravans, which the `Settlement` check actually supports. **A wiki page is the one "
     "artefact where a confident guess is indistinguishable from a lie to the reader.**"),

    ("**Profiting from a coordinate must be documented.**",
     " -- **WRITTEN 0.12.99-dev as `backrooms.md` §Selling from down there, and the capability was "
     "already there and silent.** "
     "Measured: `CompRimroomsCreditBeacon` rides on Core's `OrbitalTradeBeacon` by patch and reads "
     "**`parent.Map`** with **no headquarters restriction** anywhere in the comp -- so a beacon "
     "designated in a coordinate sells everything valuable in its radius where it stands, straight "
     "into the company account. `OwnsMap` returns true for a registered coordinate, so connected "
     "work reaches it as well. **" + Q + "u can have a nugget farm in a isolated gate seed if "
     "wanted" + Q + " was true today and nothing anywhere a player looks said so.** "
     "**And the two halves of the economy are now connected on the page, which is the real finding.** "
     "`ValuablesExchange` pays **x1.5 for odd goods and x0.85 for ordinary valuables**, and "
     "everything carried out of a coordinate is marked odd -- so §Odd goods now ends by saying that "
     "a mine or a farm beyond a gate is **the better-paid half of the economy, not a detour from "
     "it**. The page explained the odd mark and the rates in separate sections and never once told "
     "the reader what they meant together."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:46], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d coordinate-uses row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
