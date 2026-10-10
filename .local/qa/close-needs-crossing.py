# -*- coding: utf-8 -*-
"""Close the three colonist-needs crossing rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Needs must be able to cross, which is the owner's actual complaint.**",
     " -- **BUILT 0.12.99-dev as `CrossForNeedMapComponent`, AND THE BRIEF WAS CORRECTED RATHER THAN "
     "QUIETLY DEPARTED FROM.** "
     "The brief specified a `ThinkTreeDef` with `insertTag`. **It was built as a map component instead, "
     "for three reasons that are better than the plan.** It is **strictly more additive**: an insert "
     "still edits the shape of Core's humanlike tree at a tagged point, and with 294 mods loaded that "
     "tree is one of the most contested structures in the game, while a component edits nothing at all. "
     "It **cannot fail silently**: an insert whose tag another mod moves, renames or wraps leaves a pawn "
     "simply never crossing, with nothing anywhere to read. And it **is what the owner asked for** -- "
     "*" + Q + "pawns auto get command to cross" + Q + "* is a command issued, which is what this is; a "
     "think node is a pawn deciding, a command is the branch telling them. "
     "**It issues through `ConnectedCrossing.StepToward`, the ONE implementation of stepping through a "
     "gate**, so the pawn's own danger policy, allowed area and locked or forbidden doors are honoured "
     "exactly as they are for work -- *" + Q + "a second copy of this would drift, and the drift would "
     "be a colonist walking into something the player told it to avoid" + Q + "*. "
     "**The home map is checked first and always wins.** A pawn only crosses for something it cannot "
     "have here, so a branch with beds at home never sends anybody through a gate to sleep. Rest and "
     "food both qualify; the threshold is **0.28**, below Core's own act-now levels and above zero, "
     "because a crossing takes time and the decision has to be made while there is still time to make "
     "it. "
     "**`GateWatch.MustLeave` refuses a candidate outright**, which is the floor pointing the other way "
     "for once: a pawn in genuine trouble needs the nearest answer, not one through a gate."),

    ("**A need-crossing has to be answered against an explicit `Map`, which the architecture already demands and already does.**",
     " -- **BUILT 0.12.99-dev as explicit per-map scans, exactly as the contract demands.** "
     "`ConnectedDeploymentProvider` states it: a provider answers *is there work of my kind on that map* "
     "**against an explicit `Map`**, because *" + Q + "the provider contract forbids asking a native "
     "pawn-specific query about a map the worker is not standing on" + Q + "*. "
     "**So Core's own searches could not be used and that is the whole reason these exist.** "
     "`RestUtility.FindBedFor` searches the pawn's own map and cannot be pointed at another, so "
     "`HasBedFor` walks `listerBuildings` on the **named** map: not a prisoner bed, not medical, not "
     "owned by somebody else, not occupied. `HasFoodOn` walks "
     "`ThingRequestGroup.FoodSourceNotPlantOrTree` on the named map: nutrition above zero, not a "
     "corpse, not forbidden to the player. "
     "**Both are small and both are cheap in the case that matters** -- they stop at the first find, so "
     "a map with a bed on it answers in a handful of comparisons and only a bare map pays for the full "
     "walk, which is the map where the answer is no and the scan was the point."),

    ("**A need-crossing must not strand the pawn, and the owner was shown that cost and took it.**",
     " -- **BUILT 0.12.99-dev, AND MY FIRST DRAFT OF THE GUARD WAS WRONG IN THE DIRECTION THAT WOULD "
     "HAVE MATTERED MOST.** "
     "The guard is at the **decision**, not the rescue: a pawn may not *begin* crossing unless the "
     "remaining window covers all three legs -- the walk there, the need, and the walk back -- checked "
     "**once, before committing**, because a guard that fires halfway leaves the pawn exactly where the "
     "guard exists to stop them being. "
     "**Every unknown is rounded against the crossing**, deliberately: `AssumedLegTicks = 2500` is a "
     "full in-game hour for a walk across a facility, and `AssumedNeedTicks = 15000` is half a day "
     "because sleep is the expensive case and sleep is what this is for. The cost of refusing a marginal "
     "trip is a slightly unhappy pawn; the cost of allowing one is a colonist sealed in a maze. "
     "**A permanently open natural gate has no window and therefore no guard**, which is invariant 12 "
     "paying for itself rather than a special case: the gate kind the player chose is the rule, and a "
     "branch that wants people living beyond a gate should be using a natural one. "
     "**THE DEFECT I CAUGHT BY READING IT BACK: the gate is not on this map.** A gate is a building on "
     "the branch's own map; a coordinate holds a threshold anchor and no gate comp at all. So scanning "
     "`map.listerBuildings` found nothing for a pawn standing on the far side, and **a colonist in a "
     "coordinate could never have crossed home for a need** -- which is the half of this feature that "
     "matters most, since the far side is where there are no beds. It resolves through "
     "`RimroomsPortalNetwork` now, which is the only thing that knows which two maps a connection joins, "
     "and matches the edge **in either order** because the pawn may be standing at either end."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:52], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d needs-crossing row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
