# -*- coding: utf-8 -*-
"""Stage five: let a place go, so a machine gate can aim deeper.

Owner direction, 2026-09-30:

    "yeah so if the player discovers and goes through a natural gate how do they turn them off to
     use the machine gates for more controll and aiming deeper?"
    "get 5 natural gates u cant use a machine gate"

and the chosen shape: **an Operations held-places list with a Release button.**

A CORRECTION THIS WORK FORCED. The previous checkpoint's record said discovering a gate was free
because no map was generated until somebody crossed. **That is wrong.**
`NaturalFrontierService.Discover` calls `PortalAddressService.RegisterNaturalAddress`, which calls
`DestinationService.EnsureSite` **immediately** -- because the natural edge is registered against
the far side's own `ReturnAnchor`, and that Thing does not exist until the map does. So a discovery
costs a slot the moment it is made, the budget check in `Discover` is load-bearing rather than
over-eager, and the owner's trap is real exactly as they described it.

WHAT RELEASE HAS TO BE, GIVEN THAT. The edge points at a Thing on the far side, so tearing the map
down kills the edge permanently. Release therefore:

  * remembers, on the surface door's own comp, which coordinate it led to;
  * removes the edges into that coordinate, which are about to become dangling anyway;
  * tears down the map and the world object and clears the coordinate's site;
  * marks the coordinate `releasedByPlayer`, which is the ONLY thing that can tell a deliberate
    release from the broken reference `EnsureSite` is right to refuse; and
  * keeps the coordinate record and its rooms, so re-opening returns to the SAME place.

Re-opening is a gizmo on the door that led there. Nothing is lost that the player was not told
about: the interior regenerates from its own seed, so anything left inside is gone.
"""
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


# ------------------------------------------------------------------ 1. the save field
edit(os.path.join(SRC, "Company", "CampaignRecords.cs"), [
    ("        internal int depth = 1;",
     """        internal int depth = 1;

        /// <summary>
        /// The player let this place go on purpose, and it may be regenerated.
        ///
        /// **This flag exists to answer one question that cannot otherwise be answered.**
        /// <see cref="Generation.DestinationService.EnsureSite"/> refuses to build a map for a
        /// coordinate that has no site but whose rooms have been surveyed, because *"a broken
        /// reference must not create a competing owner or replace an already explored graph"*.
        /// That is exactly right for a fault. It is exactly wrong for a deliberate release, and
        /// from the outside the two look identical: no site, rooms surveyed.
        ///
        /// So a release says so, in the save. Cleared the moment the place is generated again.
        /// </summary>
        internal bool releasedByPlayer;"""),
    ("            Scribe_Values.Look(ref depth, \"rr_depth\", 1);",
     "            Scribe_Values.Look(ref depth, \"rr_depth\", 1);\n"
     "            Scribe_Values.Look(ref releasedByPlayer, \"rr_releasedByPlayer\", false);"),
    ("        public CoordinateStatus Status { get { return status; } }",
     "        public CoordinateStatus Status { get { return status; } }\n"
     "        public bool ReleasedByPlayer { get { return releasedByPlayer; } }"),
])


# ------------------------------------------------------------------ 2. EnsureSite may rebuild it
edit(os.path.join(SRC, "Generation", "DestinationService.cs"), [
    ("""            if (coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||
                (coordinate.rooms != null && coordinate.rooms.Any(room => room != null && room.Surveyed)) ||
                Find.WorldObjects.AllWorldObjects.OfType<RimroomsDestinationMapParent>().Any(owner => owner.CoordinateId == coordinate.Id) ||
                Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id)))
            {
                // A broken reference must not create a competing owner or replace an already explored graph.
                return Fail(coordinate, null, "RR_Generation_OwnerMissing");
            }""",
     """            // **A deliberate release is exempt, and nothing else is.** A coordinate the player
            // let go has no site and surveyed rooms, which is byte-for-byte what a broken
            // reference looks like -- so the only honest way to tell them apart is that a release
            // wrote it down. See CoordinateRecord.releasedByPlayer.
            //
            // A competing owner or a live map still refuses even then: those are real conflicts
            // rather than an explored graph, and a release is required to have removed both.
            bool releasedAndRebuildable = coordinate.releasedByPlayer &&
                !Find.WorldObjects.AllWorldObjects.OfType<RimroomsDestinationMapParent>().Any(owner => owner.CoordinateId == coordinate.Id) &&
                !Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id);
            if (!releasedAndRebuildable && coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||
                (coordinate.rooms != null && coordinate.rooms.Any(room => room != null && room.Surveyed)) ||
                Find.WorldObjects.AllWorldObjects.OfType<RimroomsDestinationMapParent>().Any(owner => owner.CoordinateId == coordinate.Id) ||
                Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id)))
            {
                // A broken reference must not create a competing owner or replace an already explored graph.
                return Fail(coordinate, null, "RR_Generation_OwnerMissing");
            }"""),
])

print("stage five, part one: the flag and the regeneration path")
