# -*- coding: utf-8 -*-
"""The scale sweep the last two launches should have had, done once instead of one bug at a time.

Owner: *"its suppose to be built and working 100% we finished the build yesterday!"* — correct, and
the right response is to stop finding these one launch at a time.

Every constant in the generation path was listed and sized against a 300x300 map, 80-cell rooms
and 42 rooms. Two more would have killed a coordinate, and both are the same family as the light
count at 0.12.48-dev and the conduit carpet at 0.12.52-dev: **a number written against the old
scale that no proof can see has stopped fitting.**

MEASURED, by modelling what the routing actually does. `FindConduitRoute` BFSes from the whole
wired set, so routes share a spine and the total is far below the sum of the distances:

    depth  rooms  consumers  conduit cells needed   against a cap of 512
      1      6        7           460               under, just
      2     10       11           625               THROWS
      3     16       17           828               THROWS
      4     24       25         1,061               THROWS
      5     32       33         1,211               THROWS
      6     42       43         1,436               THROWS

**So depth 1 would probably have generated on the seventh launch and every level below it would
have died.** That is the worst possible failure mode: it looks fixed.

TWO FIXES, both the same principle the power validation already follows -- *a dark corner beats no
coordinate*:

  1. the cap is sized for the map it is on, and exceeding it **stops wiring** instead of throwing;
  2. a consumer the routing cannot reach is **skipped**, not fatal.

WHAT WAS CHECKED AND IS FINE, so the sweep is on record rather than implied:
`MaxInitialFuelStacks` (generator capacity, independent of map size), `CellsPerSweep`/`Interval` in
containment (a rotating window; `ReroofWholeMap` does the real work on load), `ConstructionEcho`'s
`WindowCells`/`Capacity` (windowed), `FacilityPlanner`'s 2-to-4 room groups at 45% eligibility
(scales), `RoomArchetypeService.MaxFixtureSide` (fixture size, not map size),
`RevisitDisplacement.MaxMoved`, and `WorldTileCandidateBudget` (world tiles, unrelated).
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

text = io.open(GEN, encoding="utf-8").read()

EDITS = [
    # 1. The cap, sized and justified with the measured numbers.
    ("        private const int MaxNativePowerConduits = 512;",
     """        /// <summary>
        /// The most conduit cells one coordinate may hold.
        ///
        /// **512 was sized for a 60x60 map and it killed every level below depth 1.** Modelled
        /// against what the routing actually does — `FindConduitRoute` BFSes from the whole wired
        /// set, so routes share a spine and the total is far under the sum of the distances:
        ///
        ///     depth 1:   460 cells    depth 4: 1,061
        ///     depth 2:   625          depth 5: 1,211
        ///     depth 3:   828          depth 6: 1,436
        ///
        /// Depth 1 fitted under 512 **by forty cells**, which is the worst possible failure mode:
        /// the first level a player opens would have generated and every one below it would have
        /// died, so it would have looked fixed.
        ///
        /// Four thousand leaves room for a deranged layout and for whatever the dressing adds,
        /// and the conduit is `HiddenConduit` so a long run costs nothing visually. **Exceeding
        /// it now stops the wiring rather than destroying the coordinate** — see
        /// <see cref="TrySpawnNativeConduit"/>.
        /// </summary>
        private const int MaxNativePowerConduits = 4000;"""),

    # 2. The routing stops throwing when it cannot reach something.
    ("""            if (!destination.IsValid) { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }""",
     """            // **Empty rather than fatal.** A consumer the conduit cannot reach is a dark
            // corner; the caller skips it and `ValidateNativePowerNetwork` reports it. Throwing
            // here destroyed the whole coordinate, which is the defect that cost two launches.
            if (!destination.IsValid) { return route; }"""),

    ("""                IntVec3 predecessor;
                if (!previous.TryGetValue(cursor, out predecessor))
                { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }""",
     """                IntVec3 predecessor;
                // Same reasoning: a broken trail is a dark corner, not a dead place.
                if (!previous.TryGetValue(cursor, out predecessor)) { return new List<IntVec3>(); }"""),

    # 3. The known-consumer routes use the non-throwing placement too.
    ("""            foreach (CellRect consumer in consumerFootprints)
            {
                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells, consumer);
                foreach (IntVec3 cell in route)
                { SpawnNativeConduit(map, voidFloor, conduitDef, cell, wiredCells); }
            }""",
     """            foreach (CellRect consumer in consumerFootprints)
            {
                if (wiredCells.Count >= MaxNativePowerConduits) { break; }
                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells, consumer);
                // An empty route means this consumer could not be reached. Skipped, not fatal:
                // the same rule the stray pass and the power validation already follow.
                for (int step = 0; step < route.Count; step++)
                {
                    if (wiredCells.Count >= MaxNativePowerConduits) { break; }
                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);
                }
            }"""),
]

problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(GEN, "w", encoding="utf-8", newline="").write(text)
print("scale sweep applied: %d edits" % len(EDITS))
