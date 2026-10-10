# -*- coding: utf-8 -*-
"""Record the owner's direction that the wiki reads as though the company loop is the whole game."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — an unexplored room offers no work, and exploring is a thing you order (2026-10-06)"

S = NL.join([
"### Owner direction — a coordinate is a map you can use for anything, and the wiki says otherwise (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06):** *" + Q + "this part of the wiki soiunds like thats all "
"to do what about making prisons back there, storage, isolated saferooms, guest quarters from mods, "
"industrial uses and mateerial harvesting, mining, anything and everything.. remember profiting, u "
"can have a nugget farm in a isolated gate seed if wanted" + Q + "*",
"",
"**And verbatim on the exact passage, quoted back by the owner to identify it:**",
"",
"> *" + Q + "Then / In the field, record a route, a distortion and an entity observation. / Come "
"home before the window closes. / Analyse the recording at a bound laboratory. Analysis is pawn "
"work over time. / Have a second person review the finished report. / Spend the insight on a "
"company project. / That loop is the game. Nothing in it is timed except the connection "
"itself." + Q + "*",
"",
"**THE CAPABILITY IS THERE AND THE DOCUMENT IS WRONG, which was measured before any of it was "
"written.** `research/WORK_TYPE_COVERAGE_AUDIT.md`: **21 of the 23 work types have a cross-gate "
"deployment** -- Warden, Mining, Growing, Hauling, Construction, Handling, Hunting, Fishing, "
"Research, Childcare, Cleaning, PlantCutting, Firefighter, BasicWorker, Doctor, DarkStudy and all "
"five bill families. The two that never will are `Patient` and `PatientBedRest`, which are states "
"rather than jobs. `OwnsMap` returns true for a registered coordinate, so connected work reaches "
"it. And `CompRimroomsCreditBeacon` reads `parent.Map` with **no headquarters restriction**, so a "
"beacon sells from a coordinate: *" + Q + "u can have a nugget farm in a isolated gate seed if "
"wanted" + Q + "* is true today and nothing says so anywhere a player would look.",
"",
"**The mod's own source already said the intent out loud.** `SoloGroupOpening`: *" + Q + "A group "
"that would rather stay down there, mine the rock and grow food under thick roof is playing "
"correctly and nothing nudges them" + Q + "*. So the wiki contradicts the code's stated design, "
"which is the worst direction for that disagreement to run.",
"",
"- [ ] **The wiki must stop saying the company loop is the game.** The owner quoted the line back: "
"*" + Q + "That loop is the game" + Q + "*. It is **one** loop -- the company's contract loop -- "
"and `docs/wiki/backrooms.md` repeats the same framing in its own words, *" + Q + "The point of a "
"crossing is a record" + Q + "*. Both are reader-facing pages held to the 360-character wall, so "
"this is a rewrite of the framing rather than a sentence appended under it.",
"- [ ] **Document using a coordinate for every purpose the owner named**, in their words: "
"*" + Q + "making prisons back there, storage, isolated saferooms, guest quarters from mods, "
"industrial uses and mateerial harvesting, mining, anything and everything" + Q + "*. Each has a "
"mechanism already shipped and none of them is written down: a coordinate is an owned map, so "
"stockpiles, cells, beds, benches and designations behave exactly as they do at home, and the "
"deployment families carry a worker across to do the job. **Named with its practical cost where it "
"has one** -- a coordinate is roofed, so growing needs sun lamps and power.",
"- [ ] **Guest quarters need the honest limit stated, not a promise.** The owner named them "
"specifically: *" + Q + "guest quarters from mods" + Q + "*. "
"`RimroomsDestinationMapParent` is a `MapParent` and **not** a `Settlement`, and faction visitors "
"and caravans arrive at a settlement -- so a coordinate does not receive guests. Hospitality is "
"register row 270, whose disposition is *" + Q + "optional native guest economy; not a "
"cross-company visit system" + Q + "*. **So guest content belongs on the surface base and works "
"there as it always did**, and saying that is more use than implying a coordinate will fill with "
"visitors.",
"- [ ] **Profiting from a coordinate must be documented.** Owner: *" + Q + "remember "
"profiting" + Q + "*. Measured: `CompRimroomsCreditBeacon` rides on Core's `OrbitalTradeBeacon` "
"and reads `parent.Map`, so a beacon built in a coordinate sells what is in its radius and the "
"credits post to the ledger. **And everything taken out of a coordinate is marked odd**, which "
"`ValuablesExchange` pays **x1.5** for against x0.85 for ordinary valuables -- so harvesting down "
"there is the better-paid half of the economy and the page that explains odd goods never connects "
"the two.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "a coordinate is a map you can use for anything" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("coordinate-uses direction recorded, 4 rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
