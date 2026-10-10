# -*- coding: utf-8 -*-
"""Stage five, part two: the network can forget an edge, and a door remembers where it led."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")


def edit(path, pairs):
    enc = "utf-8-sig" if path.endswith(".xml") else "utf-8"
    text = io.open(path, encoding="utf-8-sig").read()
    problems = []
    for old, _ in pairs:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:64]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in pairs:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding=enc, newline="").write(text)
    print("%s: %d edit(s)" % (os.path.basename(path), len(pairs)))


# ------------------------------------------------------------------ the network forgets an edge
edit(os.path.join(SRC, "Portals", "RimroomsPortalNetwork.cs"), [
    ("        private static bool EndpointPresent(PortalEndpointRecord endpoint)",
     """        /// <summary>
        /// Remove one connection, because the place at one end of it is being released.
        ///
        /// **This is the only removal this class has, and it is deliberately narrow.** The load
        /// path says outright that it must *"preserve malformed evidence. Never silently remove an
        /// edge or reconnect it to a similarly named replacement door/map."* That rule is about
        /// **silence** and about **faults** — an edge that looks broken is evidence and must be
        /// kept. This is neither: the player asked for it, and every endpoint of it is about to
        /// stop existing because the map it lives on is being torn down.
        ///
        /// Leaving it would be leaving a record pointing at nothing, which is this project's most
        /// expensive defect class.
        ///
        /// Returns true when an edge was actually removed.
        /// </summary>
        internal bool ForgetConnection(string connectionId)
        {
            if (string.IsNullOrWhiteSpace(connectionId) || HasStateFault) { return false; }
            PortalConnectionRecord edge;
            if (!connectionById.TryGetValue(connectionId, out edge) || edge == null) { return false; }
            connections.Remove(edge);
            connectionIdentity.Remove(edge);
            connectionById.Remove(connectionId);
            topologyRevision++;
            return true;
        }

        private static bool EndpointPresent(PortalEndpointRecord endpoint)"""),
])


# ------------------------------------------------------------------ the door remembers
edit(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"), [
    ("        private bool designated;\n        private string branchId;",
     """        private bool designated;
        private string branchId;

        /// <summary>
        /// The place this door led to, while that place is not being held open.
        ///
        /// **Written at release, read at re-open.** A natural gate is permanently open and is
        /// never closed — what a release lets go of is the space behind it. The edge that recorded
        /// the pairing has to be removed, because every endpoint of it lives on the map being torn
        /// down, so the pairing is written here instead. Without it the door would become an
        /// ordinary marked door and the place behind it would be unreachable for ever.
        /// </summary>
        private string shelvedCoordinateId;"""),
    ("            Scribe_Values.Look(ref branchId, \"rr_emergenceBranchId\");",
     "            Scribe_Values.Look(ref branchId, \"rr_emergenceBranchId\");\n"
     "            Scribe_Values.Look(ref shelvedCoordinateId, \"rr_emergenceShelvedCoordinate\");"),
    ("        public override IEnumerable<Gizmo> CompGetGizmosExtra()\n        {",
     """        /// <summary>The place this door led to, while it is shelved. Null when it is open.</summary>
        internal string ShelvedCoordinateId { get { return shelvedCoordinateId; } }

        /// <summary>Called by the release, while the edge still says where this door led.</summary>
        internal void RememberShelvedPlace(string coordinateId)
        {
            if (!string.IsNullOrWhiteSpace(coordinateId)) { shelvedCoordinateId = coordinateId; }
        }

        /// <summary>Called when the place is open again, so the door stops offering to re-open it.</summary>
        internal void ForgetShelvedPlace() { shelvedCoordinateId = null; }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {"""),
])

print("stage five, part two applied")
