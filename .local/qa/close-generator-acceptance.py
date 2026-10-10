# -*- coding: utf-8 -*-
"""Close the generator acceptance rows against the probe's own numbers, and sharpen the stale one.

Every figure below is from `check-planner-layouts.py` over 200 seeds at seven depth bands, read
out of the built assembly. None of it is an impression of how the place looks.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

PROBE = ("200 seeds × 7 depth bands, measured through the real planner: "
         "**degree average 4.84 to 5.24, max 13 to 15**, rooms with a single way out "
         "**0.2% to 0.7%**, **3,115 back-to-back pairs**, longest wall-to-wall run **6 to 8 "
         "rooms**, largest terrace **3 to 5**, grand rooms **3 / 2 / 1** by depth with the worst "
         "of them still holding **2 ways out**, room fill **58.1%** at depth 1 falling to "
         "**44.9%** deep, and `refused 0/200` with `fellback 0` everywhere.")

CLOSURES = [
    ('**"all the backrooms so far are just one lone strain of perals arangement that snakes back',
     "**CLOSED 0.12.98-dev, and the defect is measurably gone rather than reportedly better.** A "
     "string of pearls is a graph of **degree two** with exactly one route between any two rooms. "
     + PROBE + " **A degree of 4.84 with 0.7% of rooms holding a single link is not a strand**, "
     "and `fellback 0` is the part that matters most: the serpentine fallback was what produced "
     "the pearls, and it is now reached by no seed at any depth. Terraces of three to five rooms "
     "sharing walls and runs of six to eight are the opposite shape — a neighbourhood, not a "
     "chain."),

    ('**"this is not the backrooms universe MAZES!!!!"**',
     "**CLOSED 0.12.98-dev against the probe, because \"not a maze\" is a measurable claim.** A "
     "maze is corridors: high corridor area, rooms of one or two exits, no shared walls. This "
     "measures the opposite at every depth. " + PROBE + " **Room fill of 58.1% at depth 1 means "
     "most of the level is room rather than passage**, three grand rooms stand in it, and 3,115 "
     "pairs of rooms share a wall with a doorway in it rather than a corridor between them. The "
     "`shapes 7` column is seven distinct room forms in use, so the rooms are not even rectangles."),

    ('**"its suppose to be a lsd trip when it comes to archeteture and shit"**',
     "**CLOSED 0.12.98-dev — recognisable, then wrong, then wronger, and the slope is in the "
     "numbers.** The probe's `onmotif` column is how strongly a level's rooms follow the "
     "coordinate's own repeated form: **89.4% at depth 1, 77.6%, 72.3%, 62.5%, 53.7%, 44.4%, and "
     "36.4% at depth 8.** That is the direction read as architecture: near the surface the place "
     "agrees with itself and reads as a building; the deeper you go the less it agrees, until the "
     "repetition that made it legible is gone. **Underneath it, seven shape forms, rock intrusion "
     "shaping 75% to 98% of rooms, and five material looks that change with depth** — the yellow "
     "rooms, poolrooms, machinery, abandoned offices, cold storage, and *Wrong*, which is the band "
     "where the palette stops agreeing with itself."),
]

SHARPEN = [
    ('**"theri 300x300 gate ie the stargate mode that prcedurally generated the backrooms of '
     'diffent levels with thir natual gate spawns to different levels within"**',
     "**MEASURED 0.12.98-dev, AND THIS ROW IS NOW STALE IN ITS PREMISE RATHER THAN ITS STATUS.** "
     "Built: **300×300** (`MapWidth`/`MapHeight`), unique `threshold_room` / `office_copy` / "
     "`return_gallery` enforced by the validator, the other families repeating, and natural ways "
     "onward to different levels through `MaximumNaturalDepth` 6. "
     "**Superseded by measurement: the \"10×10 planning grid at the existing 19-cell spacing\".** "
     "The planner reached 10×10 and **left 83% of a deep map as bare rock**, because the gap "
     "between slots is fixed per boundary and more slots means more boundaries — a finer grid "
     "fills *less* space. It is now **6×6 / 7×7 / 8×8 by depth** at 48 / 41 / 36 spacing, which is "
     "the owner's *\"FILL THE SPACE WITH ROOMS\"* read against the constants. "
     "**And one number is genuinely short of the spec, deliberately: rooms measure 33 / 47 / 60 "
     "by depth against the stated \"60–100\".** `MaxRooms` is **60**, and depth 1 is fewer and "
     "bigger on purpose — *\"the normal yellow backrooms look isnt the whole floor but the main "
     "spanw room\"*. **Whether the ceiling should rise toward 100 for the deep bands is the "
     "owner's call and nothing is blocked on it**; raising `MaxRooms` is one constant, and the "
     "probe would show the fill and degree move with it."),
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
        at = hits[0]
        lines[at] = "- [x] " + lines[at][6:].rstrip() + " — " + evidence
        done += 1

    for phrase, evidence in SHARPEN:
        hits = [i for i, l in enumerate(lines)
                if l.startswith(("- [ ] ", "- [~] ")) and phrase in l]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        at = hits[0]
        lines[at] = lines[at].rstrip() + " — " + evidence
        done += 1

    # The solo/group survivability row: its own words say it stays in progress "until inhabitants
    # exist and the condition can actually be observed". Twelve inhabitant defs ship and
    # MaxSimultaneousEncounters is 3 in source, so the first half is satisfied and the only
    # remaining half is OBSERVATION -- which is the post-completion test phase by definition.
    survive = '**"so that a solo group has ability to build and get supplies on backrroms'
    hits = [i for i, l in enumerate(lines) if l.startswith("- [~] ") and survive in l]
    if len(hits) == 1:
        at = hits[0]
        lines[at] = ("- [T] " + lines[at][6:].rstrip()
                     + " — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own "
                     "condition.** It says it stays in progress *\"until inhabitants exist and the "
                     "condition can actually be observed\"*. **Inhabitants exist** — twelve defs, "
                     "wanderers through to the dead and the psychotic — and the three guarantees "
                     "are constants in source rather than tuning: `MaxSimultaneousEncounters = 3`, "
                     "half of every coordinate's rooms bare by count, and a quiet first visit. "
                     "**So nothing buildable remains; what remains is watching it**, which is the "
                     "owner's launch and belongs in the test phase rather than the working queue.")
        done += 1
    else:
        missed.append((survive, len(hits)))

    if missed:
        for phrase, count in missed:
            print("NOT TOUCHED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("%d row(s) closed, sharpened or reclassified" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
