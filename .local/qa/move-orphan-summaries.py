# -*- coding: utf-8 -*-
"""Reunite orphaned <summary> blocks with the member each one actually documents.

Every entry below was matched by reading the orphan and the file's undocumented members: the
block describes a sibling that a later insertion separated it from. **Nothing is deleted** -- the
block moves, byte for byte, and the move is verified by re-reading the file afterwards.

Each entry is (path, first line of the orphan's `/// <summary>`, the declaration it belongs above).
Both anchors must match exactly once, or the entry refuses rather than guessing.
"""
import io
import sys

NL = chr(10)

MOVES = [
    ("src/RimroomsAsyncIndustries/ConnectedWork/ConnectedWorkRecords.cs",
     "The destination is an object rather than a cell",
     "        internal void RecordResolvedTarget(Thing target)"),
    ("src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs",
     "An interior cell with one of the room's own walls directly behind it",
     "        private static IntVec3 FindWallAttachmentCell(Map map, RoomRecord room, "
     "IntVec3 preferred,"),
    ("src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs",
     "Whether a wall attachment standing on this cell with this facing really is attached",
     "        private static bool WallAttachmentHolds(Map map, ThingDef def, IntVec3 cell, "
     "Rot4 facing)"),
    ("src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs",
     "Places a fixture and returns null instead of throwing when it cannot",
     "        private static Thing TryPlace(Map map, RoomRecord room, CoordinateRecord coordinate,"),
    ("src/RimroomsAsyncIndustries/Generation/RoomLayoutPlanner.cs",
     "Whether these two rooms share a wall, so there is no corridor between them",
     "        internal static bool AreNeighbourRooms(RoomRecord first, RoomRecord second)"),
    ("src/RimroomsAsyncIndustries/Portals/PortalConnectionRecord.cs",
     "Re-derive the approach cell when the saved one has been built over",
     "        internal bool TryRepairApproach()"),
    ("src/RimroomsAsyncIndustries/Threats/CoordinatePressureLadder.cs",
     "The band a coordinate is currently in",
     "        public static Band BandFor(CoordinateRecord coordinate, float colonyWealth)"),
    ("src/RimroomsAsyncIndustries/UI/OperationsEvidence.cs",
     "The interview: which of two accounts the company files",
     "        private static void DrawInterview(Listing_Standard listing, EvidenceRecord record,"),
    ("src/RimroomsAsyncIndustries/UI/OperationsPortalNetwork.cs",
     "The player-facing name of a connection kind",
     "        private static string KindLabelKey(PortalConnectionKind kind)"),
]


def block_bounds(lines, needle):
    """The orphan block containing `needle`: from its `/// <summary>` to its `/// </summary>`."""
    hits = [i for i, l in enumerate(lines) if needle in l and l.strip().startswith("///")]
    if len(hits) != 1:
        return None, None, "needle matched %d line(s)" % len(hits)
    at = hits[0]
    start = at
    while start >= 0 and lines[start].strip() != "/// <summary>":
        start -= 1
    end = at
    while end < len(lines) and lines[end].strip() != "/// </summary>":
        end += 1
    if start < 0 or end >= len(lines):
        return None, None, "block not delimited"
    # It must be the FIRST of a stacked pair: the next non-blank doc line opens another summary.
    after = end + 1
    while after < len(lines) and lines[after].strip() == "":
        after += 1
    if after >= len(lines) or lines[after].strip() != "/// <summary>":
        return None, None, "not a stacked pair (nothing follows it)"
    return start, end, None


def main():
    failures = 0
    for path, needle, decl in MOVES:
        text = io.open(path, encoding="utf-8-sig").read()
        lines = text.split(NL)
        start, end, why = block_bounds(lines, needle)
        if why:
            print("REFUSED  %-58s %s" % (needle[:56], why))
            failures += 1
            continue
        block = lines[start:end + 1]
        rest = lines[:start] + lines[end + 1:]
        if rest.count(decl) != 1:
            print("REFUSED  %-58s declaration matched %d time(s)"
                  % (needle[:56], rest.count(decl)))
            failures += 1
            continue
        at = rest.index(decl)
        out = rest[:at] + block + rest[at:]
        io.open(path, "w", encoding="utf-8-sig", newline=NL).write(NL.join(out))
        print("moved %2d lines  %-52s -> %s" % (len(block), needle[:50], decl.strip()[:46]))
    print("")
    print("%d moved, %d refused" % (len(MOVES) - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
