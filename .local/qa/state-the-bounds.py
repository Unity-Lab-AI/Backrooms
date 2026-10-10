# -*- coding: utf-8 -*-
"""State the reason on every numeric cap in Generation/, Portals/ and Gate/ that had none.

Owner, verbatim: *"so dont limit yourself"* -- where a bound exists it has to be a bound the
geometry imposes and is **stated**, not one chosen for convenience. Eight caps in the three areas
where a bound can refuse CONTENT carried no reason at all, so nobody could tell them from a
convenience. Each reason below was read out of the constant's own use, not invented.
"""
import io
import sys

NL = chr(10)

EDITS = [
    ("src/RimroomsAsyncIndustries/Generation/DestinationService.cs",
     "        private const int WorldTileCandidateBudget = 512;",
     '        /// <summary>'
     + NL + '        /// How many planet tiles the unique-tile search will probe before giving up.'
     + NL + '        ///'
     + NL + '        /// **A bound on WORK, never on where a coordinate may live.** The walk starts'
     + NL + '        /// at a seeded offset and steps by a stride coprime with the tile count, so it'
     + NL + '        /// visits distinct tiles and would eventually cover the planet; this stops it'
     + NL + '        /// after 512 probes on a world where almost every tile is already taken.'
     + NL + '        /// `Math.Min(count, ...)` means a small world is searched exhaustively.'
     + NL + '        /// </summary>'
     + NL + "        private const int WorldTileCandidateBudget = 512;"),

    ("src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs",
     "        private const int MaxInitialFuelStacks = 16;",
     '        /// <summary>'
     + NL + '        /// Most stacks of fuel a generated coordinate will prime its generator with.'
     + NL + '        ///'
     + NL + '        /// **A refusal rather than a clamp**, which is the point: a fuel whose stack'
     + NL + '        /// size makes the authored run cost more than this many stacks is skipped'
     + NL + '        /// entirely rather than part-filled, because a generator holding a token'
     + NL + '        /// amount reads as broken where an unfuelled one reads as unfuelled.'
     + NL + '        /// </summary>'
     + NL + "        private const int MaxInitialFuelStacks = 16;"),

    ("src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs",
     "        internal const int CandidateBudget = 3;",
     '        /// <summary>'
     + NL + '        /// How many whole layouts are attempted before the safe fallback is taken.'
     + NL + '        ///'
     + NL + '        /// **Three because each candidate is a complete, deterministic maze**, so a'
     + NL + '        /// second attempt is a different seed rather than a retry of the same one --'
     + NL + '        /// and `check-planner-layouts.py` measures `refused 0/200` at every depth, so'
     + NL + '        /// the first candidate is accepted essentially always. This is the depth of'
     + NL + '        /// the net, not a quality dial: raising it would hide a planner that had'
     + NL + '        /// started failing, which is exactly what `fellback` exists to show.'
     + NL + '        /// </summary>'
     + NL + "        internal const int CandidateBudget = 3;"),

    ("src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs",
     "        private const int MaximumPendingCrossings = 256;",
     '        /// <summary>'
     + NL + '        /// Most crossings that may be in flight at once across the whole company.'
     + NL + '        ///'
     + NL + '        /// **A guard against an unbounded saved list, not a limit on play.** Only'
     + NL + '        /// non-terminal receipts count, so finished crossings never consume it, and'
     + NL + '        /// three gates moving a crew each is single digits. It exists because this'
     + NL + '        /// list is saved: a leak here would grow a save file for ever.'
     + NL + '        /// </summary>'
     + NL + "        private const int MaximumPendingCrossings = 256;"),

    ("src/RimroomsAsyncIndustries/Portals/PortalRouteSearch.cs",
     "        public const int MaximumOperationsPerAdvance = 1024;",
     '        /// <summary>'
     + NL + '        /// Most search operations one advance of the route search may spend.'
     + NL + '        ///'
     + NL + '        /// **A tick budget, so the search is resumable rather than long.** The search'
     + NL + '        /// keeps its own cursor and continues on the next advance, so this bounds how'
     + NL + '        /// much work a single frame does and never how far a route may reach.'
     + NL + '        /// </summary>'
     + NL + "        public const int MaximumOperationsPerAdvance = 1024;"),

    ("src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs",
     "        public const float DoubleWidthMaxBodySize = 2.5f;",
     '        /// <summary>'
     + NL + '        /// The body size a two-cell gate will pass, which is what lets pack animals'
     + NL + '        /// through: a muffalo is 2.0 and a dromedary 2.2, so 2.5 clears both with room'
     + NL + '        /// rather than sitting on top of either number.'
     + NL + '        /// </summary>'
     + NL + "        public const float DoubleWidthMaxBodySize = 2.5f;"),

    ("src/RimroomsAsyncIndustries/Portals/WorldExit.cs",
     "        internal const int WorldExitMaximumTiles = 20;",
     '        /// <summary>'
     + NL + '        /// The far end of the band a world exit lands in, measured in planet tiles'
     + NL + '        /// from the branch. Paired with the minimum above: near enough to be a place'
     + NL + '        /// the company could plausibly reach, far enough that coming out is a'
     + NL + '        /// relocation rather than a shortcut home.'
     + NL + '        /// </summary>'
     + NL + "        internal const int WorldExitMaximumTiles = 20;"),

    ("src/RimroomsAsyncIndustries/Gate/NativeGateServicing.cs",
     "        private const int ServiceCapacityTicks = 600000;",
     '        /// <summary>'
     + NL + '        /// A fully serviced gate\'s assembly life, and the denominator the condition'
     + NL + '        /// fraction is read against.'
     + NL + '        ///'
     + NL + '        /// **It is the full-tank figure rather than a deadline.** A gate restored to'
     + NL + '        /// this sits at 1.0, a saved gate that never had the field starts here, and'
     + NL + '        /// what the player sees is the fraction -- so nothing fails when it runs out,'
     + NL + '        /// the next opening is blocked until the assembly is serviced again.'
     + NL + '        /// </summary>'
     + NL + "        private const int ServiceCapacityTicks = 600000;"),
]


def main():
    failures = 0
    for path, old, new in EDITS:
        text = io.open(path, encoding="utf-8-sig").read()
        if text.count(old) != 1:
            print("REFUSED (%d matches): %s" % (text.count(old), old.strip()[:62]))
            failures += 1
            continue
        io.open(path, "w", encoding="utf-8-sig", newline=NL).write(text.replace(old, new, 1))
        print("stated: %s" % old.strip()[:70])
    print("")
    print("%d stated, %d refused" % (len(EDITS) - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
