# -*- coding: utf-8 -*-
"""Round two: the single-line orphans the first, weaker rule could not see.

The first detector matched a line that was exactly `/// </summary>` followed by `/// <summary>`.
`/// <summary>one line</summary>` twice over is the identical fault and never produces such a
line, so six more were hiding -- found only once the rule was rewritten to count `<summary>`
openings per doc block. **A rule is worth what its weakest shape catches.**

Entries are (path, a unique phrase inside the orphan, the declaration it belongs above). One entry
is a section header rather than a member's doc, and it is handled separately below.
"""
import io
import sys

NL = chr(10)

MOVES = [
    ("src/RimroomsAsyncIndustries/Company/CampaignRecords.cs",
     "Adds worked time inside this coordinate.",
     "        internal void NoteOccupancy(int ticks)"),
    ("src/RimroomsAsyncIndustries/Gate/GateSpinUp.cs",
     "A ramp is running toward an opening on this gate.",
     "        public bool IsSpinningUp"),
    ("src/RimroomsAsyncIndustries/Generation/RoomArchetypeService.cs",
     "Picks an archetype for a room, or null when the room should be left as it is.",
     "        public static RimroomsRoomArchetypeDef Select(string familyId, int depth, int seed,"),
    ("src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs",
     "Cells inside a room that are left as solid rock, so the room is not a rectangle.",
     "        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth,"),
    ("src/RimroomsAsyncIndustries/Scenario/RimroomsStartDef.cs",
     "The name offered at setup. The player may replace it; every start can.",
     "        public string defaultCompanyName;"),
]


def bounds(lines, needle):
    hits = [i for i, l in enumerate(lines) if needle in l and l.strip().startswith("///")]
    if len(hits) != 1:
        return None, None, "needle matched %d" % len(hits)
    at = hits[0]
    start = at
    while start >= 0 and "<summary>" not in lines[start]:
        start -= 1
    end = at
    while end < len(lines) and "</summary>" not in lines[end]:
        end += 1
    if start < 0 or end >= len(lines):
        return None, None, "not delimited"
    return start, end, None


def main():
    failures = 0
    for path, needle, decl in MOVES:
        lines = io.open(path, encoding="utf-8-sig").read().split(NL)
        start, end, why = bounds(lines, needle)
        if why:
            print("REFUSED  %-56s %s" % (needle[:54], why))
            failures += 1
            continue
        block = lines[start:end + 1]
        rest = lines[:start] + lines[end + 1:]
        if rest.count(decl) != 1:
            print("REFUSED  %-56s decl matched %d" % (needle[:54], rest.count(decl)))
            failures += 1
            continue
        at = rest.index(decl)
        io.open(path, "w", encoding="utf-8-sig", newline=NL).write(
            NL.join(rest[:at] + block + rest[at:]))
        print("moved %2d  %-54s -> %s" % (len(block), needle[:52], decl.strip()[:44]))
    print("")
    print("%d moved, %d refused" % (len(MOVES) - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
