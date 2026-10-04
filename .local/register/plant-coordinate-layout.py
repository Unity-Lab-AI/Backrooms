# -*- coding: utf-8 -*-
"""Plant a fault, run the coordinate-layout proof, require exit 1, restore. Verified writes."""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
PLANNER = SRC + "/Generation/RoomLayoutPlanner.cs"
MOTIF = SRC + "/Generation/CoordinateMotif.cs"
SERVICE = SRC + "/Generation/DestinationService.cs"
GEN = SRC + "/Generation/GenStep_BackroomsDestination.cs"
CONTAIN = SRC + "/Generation/BackroomsContainment.cs"
ROOFS = "Mod/Rimrooms - Async Industries/1.6/Defs/RoofDefs/RR_Roofs.xml"
PATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_StartGenSteps.xml"
BUDGET = SRC + "/Portals/OpenMapBudget.cs"
FRONTIER = SRC + "/Portals/NaturalFrontierService.cs"
STARTDEF = SRC + "/Scenario/RimroomsStartDef.cs"
PARENT = SRC + "/Generation/RimroomsDestinationMapParent.cs"
RELEASE = SRC + "/Generation/CoordinateRelease.cs"
RECORDS = SRC + "/Company/CampaignRecords.cs"
EMERGENCE = SRC + "/Portals/CompRimroomsEmergence.cs"
PLACES = SRC + "/UI/OperationsHeldPlaces.cs"
OPTABS = SRC + "/UI/MainTabWindow_Operations.cs"
ADDRESS = SRC + "/Portals/PortalAddressService.cs"
NETWORK = SRC + "/Portals/RimroomsPortalNetwork.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"
PROOF = ".local/register/proof-coordinate-layout.py"
NL = chr(10)


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    # ------------------------------------------------------------------ the size
    ("THE COORDINATE SHRINKS BACK TO 60x60", SERVICE,
     "public const int MapWidth = 300;", "public const int MapWidth = 60;"),

    ("a coordinate stops being square", SERVICE,
     "public const int MapHeight = 300;", "public const int MapHeight = 260;"),

    # ------------------------------------------------------------------ the geometry
    ("THE MARGIN GOES NEGATIVE AND ROOMS FALL OFF THE MAP", PLANNER,
     "internal const int Margin = 6;", "internal const int Margin = -60;"),

    ("the slot gap closes and rooms share a wall", PLANNER,
     "internal const int SlotGap = 10;", "internal const int SlotGap = 0;"),

    ("ROOM SPANS STOP BEING EVEN AND DOORS MISS THE SLOT CENTRE", PLANNER,
     "            if (span % 2 != 0) { span--; }" + NL, ""),

    ("depth stops changing the slot grid", PLANNER,
     "internal const int MaxSlotsPerAxis =", "internal const int MaxSlotsPerAxisUnused ="),

    # The SECOND span source. Deleting the evenness guard from one of them used to pass, because
    # the claim counted a string that exists in both.
    ("THE VARIED SPAN STOPS BEING EVEN, so doors miss the slot centre", PLANNER,
     "            int span = baseline + offset;" + NL
     + "            if (span % 2 != 0) { span--; }" + NL,
     "            int span = baseline + offset;" + NL),

    ("rooms stop varying in size, so the level is a grid of identical boxes again", PLANNER,
     "VariedRoomSpan(spacing, slot, seed, depth)", "SlotRoomSpan(spacing)"),

    ("THE GRAND THRESHOLD HALL IS LOST", PLANNER,
     "rooms.Add(MakeHall(coordinate, hallFirst, hallSecond, spacing, seed, depth));", ""),

    # **RE-AIMED 2026-10-03, at the regression that actually happened.** This mutated
    # `{ hallSecond }` into `{ hallFirst }` on the premise that starting "inside the hall" was the
    # fault. That premise is obsolete: **both** slots are the hall, and the walk now starts from
    # both on purpose -- owner, *"starts locations of main grand rooms can be anywhere on the map
    # and lead anywhere in multiple differetn varied ways"*.
    #
    # The live regression is dropping one half, and it is not hypothetical: growing from
    # `hallSecond` alone worked only while the hall was pinned to slots (0,0)-(1,0). Once the hall
    # could land anywhere, a horizontal hall in the last two columns left that slot with no legal
    # step -- east off-grid, west the hall itself, north and south declined by
    # `AreNeighbourRooms` -- and **1.5% of seeds produced a one-room level** that fell back to the
    # serpentine, which is the string of pearls this whole line of work exists to remove.
    ("THE MAZE GROWS FROM ONLY ONE HALF OF THE HALL AGAIN", PLANNER,
     "            var stack = new List<IntVec2> { hallFirst, hallSecond };",
     "            var stack = new List<IntVec2> { hallSecond };"),

    ("the hall goes back to a hardcoded corner", PLANNER,
     "            int hallDraw = DestinationService.StableHash(seed, \"hall:slot\", depth);",
     "            int hallDraw = 0;"),

    # ------------------------------------------------------- the maze itself
    # Owner: *"all the backrooms so far are just one lone strain of perals arangement that snakes
    # back and forth across the map like one series line... i want them to be mazes like xcrazy"*.
    ("THE SPINE GOES BACK TO BEING A LINE THAT SNAKES", PLANNER,
     "            return BuildMaze(coordinate, slots, spacing, seed, depth);",
     "            return BuildSerpentine(coordinate, order, spacing, seed, depth);"),

    ("the walk sweeps instead of turning, so it is a line again", PLANNER,
     "                int turn = DestinationService.StableHash(seed," + chr(10)
     + '                    "maze:" + current.x + "," + current.z, depth);',
     "                int turn = 0;" + chr(10)
     + '                string unusedMazeKey = "maze:" + current.x + "," + current.z;'),

    ("THE BRAID IS GONE, so the maze is a tree with one route through it", PLANNER,
     "                    if (!SlotIsJunction(seed, slot, depth) && roll % BraidRarity != 0) { continue; }",
     "                    if (true) { continue; }"),

    ("the graph ceiling goes back to allowing a tree plus one loop", SERVICE,
     "                directedEdges > 2 * MaximumUndirectedEdgesPerRoom * rooms.Count)",
     "                directedEdges > 2 * rooms.Count)"),

    ("the walk stops declining a step the validator would refuse", PLANNER,
     "                    if (!AreNeighbourRooms(rooms[parent], room)) { continue; }" + chr(10), ""),

    ("A BENT ROUTE IS CARVED WITHOUT BEING PROVED CLEAR OF EVERY ROOM", PLANNER,
     "if (candidate.Count > 0 && LegsClearEveryRoom(candidate, rooms))",
     "if (candidate.Count > 0)"),

    ("the maze goes back to one branch in three", PLANNER,
     "                    if (!SlotIsJunction(seed, slot, depth) && roll % BraidRarity != 0) { continue; }",
     "                    if (roll % 3 != 0) { continue; }"),

    ("THE WARREN STOPS TIGHTENING INWARD", PLANNER,
     "internal const int MaxRooms = 60;", "internal const int MaxRooms = 6;"),

    # The first level stops being a maze and goes back to a handful of halls.
    ("THE FIRST LEVEL GOES BACK TO A WAREHOUSE", PLANNER,
     "internal const int MinSlotsPerAxis = 6;", "internal const int MinSlotsPerAxis = 3;"),

    # ---------------------------------------- the formulas the proof's model only copies
    ("the spacing formula stops dividing by the slot count", PLANNER,
     "return (DestinationService.MapWidth - Margin * 2) / slots;",
     "return DestinationService.MapWidth - Margin * 2;"),

    ("a slot centre stops accounting for the slot index", PLANNER,
     "return Margin + spacing / 2 + spacing * index;",
     "return Margin + spacing / 2;"),

    ("the span stops leaving a gap for a corridor", PLANNER,
     "int span = spacing - SlotGap;", "int span = spacing;"),

    ("THE SERPENTINE STOPS ALTERNATING AND THE CHAIN JUMPS THE GRID", PLANNER,
     "int x = row % 2 == 0 ? column : slots - 1 - column;", "int x = column;"),

    ("THE FALLBACK SERPENTINE IS NEVER REACHED, so there is no safety net", PLANNER,
     "            if (fallback) { return BuildSerpentine(coordinate, order, spacing, seed, depth); }",
     "            if (false) { return BuildSerpentine(coordinate, order, spacing, seed, depth); }"),

    ("the slot count stops rising with depth", PLANNER,
     "int slots = MinSlotsPerAxis + (depth < 1 ? 0 : depth - 1);",
     "int slots = MinSlotsPerAxis;"),

    # ------------------------------------------------------------------ the pillars
    ("THE PILLAR LATTICE OPENS PAST CORE'S ROOF SUPPORT DISTANCE", PLANNER,
     "internal const int PillarSpacing = 6;", "internal const int PillarSpacing = 20;"),

    ("a pillar lattice tight enough to seal a room", PLANNER,
     "internal const int PillarSpacing = 6;", "internal const int PillarSpacing = 1;"),

    ("small rooms start getting pillars they do not need", PLANNER,
     "internal const int PillarThreshold = 13;", "internal const int PillarThreshold = 4;"),

    ("A PILLAR LANDS ON THE CENTRE CROSS AND CAN BLOCK A DOORWAY", PLANNER,
     "                    if (x == center.x || z == center.z) { continue; }" + NL, ""),

    ("THE GENERATOR DERIVES ITS OWN LATTICE INSTEAD OF SHARING ONE", GEN,
     "foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))",
     "foreach (IntVec3 pillar in new List<IntVec3> { room.Bounds.CenterCell })"),

    # The pillar LAMPS stop sharing the lattice, so lamps hang where no pillar is.
    ("THE PILLAR LAMPS DERIVE THEIR OWN LATTICE", GEN,
     "                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))" + NL
     + "                {" + NL
     + "                    for (int side = 0; side < directions.Length; side++)",
     "                foreach (IntVec3 pillar in new List<IntVec3> { room.Bounds.CenterCell })" + NL
     + "                {" + NL
     + "                    for (int side = 0; side < directions.Length; side++)"),

    ("the pillar lamps are never hung at all", GEN,
     "                SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted," + NL
     + "                    reservedProviderCells, placedLights);", ""),

    # ------------------------------------------------------------ doors to nowhere
    ("DOORS TO NOWHERE ARE NEVER OPENED", PLANNER,
     "            return FalseOpening(room, rooms, cell);", "            return false;"),

    ("a false door moves to the centre, where a real door goes", PLANNER,
     "            int at = low + (high - low) / 3;", "            int at = (low + high) / 2;"),

    ("the threshold hall grows a door to nowhere", PLANNER,
     "            if (room == null || room.index == 0) { return false; }",
     "            if (room == null) { return false; }"),

    ("A FALSE OPENING IS ALLOWED ON A CORNER, which cuts the room open", PLANNER,
     "            if (walls != 1) { return false; }", "            if (walls < 1) { return false; }"),

    ("a wall that already has a real door gets a second opening", PLANNER,
     "                if (side == 0 && other.Bounds.minX > bounds.maxX) { return false; }",
     "                if (false) { return false; }"),

    # ------------------------------------------------------------------- lamp tones
    ("LAMPS GO BACK TO ALL BEING THE SAME COLOUR", GEN,
     "                        TintLamp(lamp, coordinate, room, pillar);", ""),

    ("the dim lamp becomes a dark one", GEN,
     "                    glower.GlowRadius = glower.GlowRadius * 2f / 3f;",
     "                    glower.GlowRadius = 0;"),

    # ---------------------------------------------------------- back to back rooms
    # **THE SHAPE OF THE DEFECT THAT SHIPPED.** A back-to-back pair whose bounds share a wall
    # column OVERLAPS, because `CellRect.Overlaps` is inclusive on both edges, and
    # `ValidateRooms` has refused overlapping rooms since the first layout. Every pair made the
    # whole candidate illegal, all four candidates were refused, and the player got a letter
    # saying no safe layout was found with nothing in the log.
    ("BACK-TO-BACK ROOMS OVERLAP INSTEAD OF ABUTTING, so no candidate is ever legal", PLANNER,
     "            if ((a.maxX + 1 == b.minX || b.maxX + 1 == a.minX) && verticalOverlap)",
     "            if ((a.maxX == b.minX || b.maxX == a.minX) && verticalOverlap)"),

    ("the push puts the room on its host's wall column rather than beside it", PLANNER,
     "            if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX + 1; }",
     "            if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX; }"),

    ("THE PUSH IS NEVER PUT BACK, so a spur lands on top of a third room", PLANNER,
     "            if (onMap && !collides && !blocksARoute && SharesWall(mover, anchorRoom)) { return; }" + NL
     + "            mover.x = originalX;" + NL
     + "            mover.z = originalZ;" + NL,
     "            return;" + NL),

    ("the collision test is dropped and only the map bound is checked", PLANNER,
     "            bool collides = rooms.Any(other => other != mover && mover.Bounds.Overlaps(other.Bounds));",
     "            bool collides = false;"),

    # **BOTH RE-AIMED 2026-10-03, and they had collapsed into ONE fault.** These deleted the
    # back-to-back skip from the carver and from the validator separately, because each kept its
    # own copy. The skip now lives once inside `CorridorLegs`, so deleting it is a single fault --
    # and planting it twice would have proved nothing the second time. The first keeps that fault
    # at its new home; the second is re-aimed at a genuinely different one, the validator ceasing
    # to model the corridor at all, which is the divergence the old pair was really guarding.
    ("a corridor is carved through the shared wall, merging the two rooms", PLANNER,
     "            if (first == null || second == null || SharesWall(first, second)) { return legs; }",
     "            if (first == null || second == null) { return legs; }"),

    ("the validator stops modelling the corridor the generator will carve", PLANNER,
     "                            floor[cell.x, cell.z] = true;", ""),

    ("rooms stop being pushed together at all", PLANNER,
     "                PushAgainst(rooms, rooms[index], rooms[host], depth);" + chr(10), ""),

    ("the push goes back to only ever moving a dead end, so back-to-back pairs collapse", PLANNER,
     "                if (rooms[index].links.Count < 1) { continue; }",
     "                if (rooms[index].links.Count != 1) { continue; }"),

    ("THE PUSH STOPS CHECKING WHETHER IT BROKE SOMEBODY ELSE'S CORRIDOR", PLANNER,
     "bool blocksARoute = !EveryLinkRoutes(rooms, mover, depth);",
     "bool blocksARoute = false;"),

    ("and the moved room is allowed to carry a link past the stated reach", PLANNER,
     "                    if (!AreNeighbourRooms(room, other)) { return false; }" + chr(10), ""),

    # -------------------------------------------- the ceiling the hall has to pass
    # **NOTHING COULD REACH THIS BEFORE.** `MaxRoomSpan` recomputed the span of a room filling
    # one slot -- 34 at depth 1 -- while the grand hall spans two slots and is 80.
    ("THE VALIDATOR RECOMPUTES THE WIDEST SPAN INSTEAD OF ASKING THE PLANNER", SERVICE,
     "            get { return RoomLayoutPlanner.WidestRoomSpan; }",
     "            get { return RoomLayoutPlanner.SlotRoomSpan("
     + "RoomLayoutPlanner.SlotSpacing(RoomLayoutPlanner.MinSlotsPerAxis)); }"),

    ("the planner's ceiling forgets the two-slot hall", PLANNER,
     "                return hall > varied ? hall : varied;",
     "                return varied;"),

    ("and it forgets that a span may vary upward", PLANNER,
     "                int varied = SlotRoomSpan(spacing) + SpanVariation;",
     "                int varied = SlotRoomSpan(spacing);"),

    ("THE SPINE EATS THE WHOLE ROOM BUDGET AND THE DEEP LEVELS LOSE EVERY BRANCH", PLANNER,
     "            if (chainLength > MaxRooms * 2 / 3) { chainLength = MaxRooms * 2 / 3; }",
     "            if (chainLength > MaxRooms) { chainLength = MaxRooms; }"),

    ("the lone centre support comes back", GEN,
     "                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))",
     "                PlaceWall(map, room.Bounds.CenterCell, wallDef, wallStuff);" + NL
     + "                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))"),

    # ------------------------------------------------------------------ the constants that went
    ("THE FIXED 19-CELL SPACING COMES BACK INTO THE VALIDATOR", SERVICE,
     "            return RoomLayoutPlanner.AreNeighbourRooms(first, second);",
     "            IntVec3 a = first.Bounds.CenterCell;" + NL
     + "            IntVec3 b = second.Bounds.CenterCell;" + NL
     + "            return Math.Abs(a.x - b.x) == 19 || Math.Abs(a.z - b.z) == 19;"),

    ("the hard-coded slot table comes back", PLANNER,
     "        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)",
     "        private static readonly int[,] Grid = { { 0, 0 }, { 1, 0 } };" + NL + NL
     + "        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)"),

    ("the room clamp goes back to a literal", PLANNER,
     "        private static int Clamp(int value, int span)",
     "        private static int ClampUnused(int value, int span)"),

    ("the family split reverts to required and optional", SERVICE,
     "        private static readonly string[] UniqueFamilies =",
     "        private static readonly string[] RequiredFamilies = { \"x\" };" + NL + NL
     + "        private static readonly string[] UniqueFamilies ="),

    ("service_passage stops being guaranteed", SERVICE,
     'AtLeastOnceFamilies = { "service_passage" }', 'AtLeastOnceFamilies = { "survey_lobby" }'),

    # ------------------------------------------------------------------ the rock fill cost
    ("REGION REBUILDING RUNS DURING THE 90,000-CELL ROCK FILL", GEN,
     "            map.regionAndRoomUpdater.Enabled = false;" + NL, ""),

    ("a throw mid-fill would leave region updates switched off", GEN,
     "            finally { map.regionAndRoomUpdater.Enabled = updaterWasEnabled; }",
     "            finally { }"),

    # ------------------------------------------------------------------ no cave-ins
    ("THE BACKROOMS START CAVING IN AGAIN", ROOFS,
     "<canCollapse>false</canCollapse>", "<canCollapse>true</canCollapse>"),

    ("the coordinate roof stops being overhead mountain", ROOFS,
     "<isThickRoof>true</isThickRoof>", "<isThickRoof>false</isThickRoof>"),

    ("the coordinate roof def is renamed out from under the accessor", ROOFS,
     "<defName>RR_RoofBackroomsOverhead</defName>", "<defName>RR_RoofSomethingElse</defName>"),

    ("CORE'S OWN MOUNTAIN ROOF GETS PATCHED FOR EVERY COLONY", PATCH,
     "</Patch>",
     "  <Operation Class=\"PatchOperationAdd\">" + NL
     + "    <xpath>Defs/RoofDef[defName=\"RoofRockThick\"]</xpath>" + NL
     + "    <value><canCollapse>false</canCollapse></value>" + NL
     + "  </Operation>" + NL + NL + "</Patch>"),

    ("the generator goes back to Core's collapsing roof", GEN,
     "RoofDef overheadRoof = BackroomsContainmentMapComponent.OverheadRoof;",
     "RoofDef overheadRoof = RoofDefOf.RoofRockThick;"),

    ("the accessor loses its fallback", CONTAIN,
     "                    ?? RoofDefOf.RoofRockThick;", "                    ;"),

    ("THE FILE GOES BACK TO CALLING A CAVE-IN ACCEPTABLE", CONTAIN,
     "    /// ## And it does not collapse either, which this file used to get wrong",
     "    /// produces rubble and a collapse exactly as it does under any mountain" + NL
     + "    /// ## And it does not collapse either, which this file used to get wrong"),
    # ------------------------------------------------------ rooms are not rectangles
    ("ROOMS GO BACK TO BEING PLAIN RECTANGLES", PLANNER,
     "            if (room == null || room.index == 0 || depth <= 1) { yield break; }",
     "            if (room != null) { yield break; }"),

    # **THE PROBE MEASURED THE OLD SHAPING RUNNING THE WHOLE TIME** -- 89% of depth-1 rooms
    # carried rock at 7% of their interior -- so the amount was never the problem and the obvious
    # guess, more reach, would only have produced rounder squares. There was exactly ONE form.
    # Owner: *"they were all just square rooms again..wtf dont u know any other compbinations"*.
    ("THERE IS ONLY ONE ROOM FORM AGAIN", PLANNER,
     "            int form = ShapeFormOf(room, depth, motif);",
     "            int form = 0;"),

    # **THE MOTIF IS WHAT MAKES SEVEN SHAPES A PATTERN RATHER THAN NOISE.** Owner:
    # *"repeated patternes in variations"*. Rolling each room independently is not a fault a
    # legality check can see -- every form is safe by construction -- so it needs its own
    # claim and its own plant, measured by the probe rather than argued about.
    ("THE MOTIF STOPS HOLDING, so every room rolls its own shape and the floor is noise",
     MOTIF,
     "            return onMotif ? Shape : roll % RoomLayoutPlanner.ShapeForms;",
     "            return roll % RoomLayoutPlanner.ShapeForms;"),

    ("and the motif stops loosening with depth, so a deep floor is as monotonous as level one",
     MOTIF,
     "            int hold = StrongestHold - (depth - 1) * HoldLostPerDepth;",
     "            int hold = StrongestHold;"),

    ("THE COORDINATE STOPS HAVING A THEME, so a floor is a list of rooms again", MOTIF,
     "            motif.Theme = Themes[(draw / 13) % Themes.Length];",
     "            motif.Theme = null;"),

    ("the form count collapses to the corner masses", PLANNER,
     "        internal const int ShapeForms = 7;",
     "        internal const int ShapeForms = 1;"),

    ("the grand hall starts being deranged like every other room", PLANNER,
     "            if (room == null || room.index == 0 || depth <= 1) { yield break; }",
     "            if (room == null || depth <= 1) { yield break; }"),

    ("the generator stops leaving any rock standing inside a room", GEN,
     "                    if (intrusions.Contains(cell)) { continue; }" + NL, ""),

    ("THE CENTRE CROSS STARTS GETTING FILLED IN", PLANNER,
     "                        if (x == center.x || z == center.z) { continue; }" + NL, ""),

    ("a corner mass starts reaching into the wall ring", PLANNER,
     "                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }" + NL,
     ""),

    ("the corner reach stops being clamped to a third of the room", PLANNER,
     "            int reach = System.Math.Min((depth - 1) * 2," + NL
     + "                System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);",
     "            int reach = (depth - 1) * 2;"),

    ("SHALLOW COORDINATES START DEFORMING TOO", PLANNER,
     "            if (room == null || room.index == 0 || depth <= 1) { yield break; }",
     "            if (room == null || room.index == 0) { yield break; }"),

    ("the planner stops modelling the rock it leaves standing", PLANNER,
     "                foreach (IntVec3 rock in RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth), motif))" + NL
     + "                { floor[rock.x, rock.z] = false; }" + NL, ""),

    # The two readers stop agreeing: the validator proves a square room and the generator
    # carves a shaped one. The defect that cost thirty-nine checkpoints, in a new place.
    ("THE VALIDATOR AND THE GENERATOR SHAPE DIFFERENTLY", PLANNER,
     "RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth), motif)",
     "RockIntrusionCells(room, depth, motif)"),

    # And the other half of the same defect: the same shaping depth, a DIFFERENT motif. The
    # validator would prove a floor shaped to one pattern and the carver cut another.
    ("THE VALIDATOR SHAPES TO A DIFFERENT MOTIF THAN THE CARVER", PLANNER,
     "RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth), motif)",
     "RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth), CoordinateMotif.None)"),

    ("shape stops reaching the first level at all", PLANNER,
     "            int band = hops / LinksPerShapeBand;", "            int band = 0;"),

    ("AN UNCARVED CELL LOSES ITS ROOF AND OPENS A HOLE IN THE WORLD", GEN,
     "                    map.roofGrid.SetRoof(cell, overheadRoof);" + NL
     + "                    if (intrusions.Contains(cell)) { continue; }",
     "                    if (intrusions.Contains(cell)) { continue; }" + NL
     + "                    map.roofGrid.SetRoof(cell, overheadRoof);"),

    # **RE-AIMED 2026-10-03.** The width was read in the carver; it is read inside `CorridorLegs`
    # now, which is the only place that needs it. Same fault, new home.
    ("HALLWAYS GO BACK TO ONE WIDTH", PLANNER,
     "            int halfWidth = CorridorHalfWidthBetween(first, second, depth, rooms);",
     "            int halfWidth = 2;"),

    # ------------------------------------------------- roads, blocks, and the exact prune
    ("A ROAD STOPS BEING WIDE, so a through-line reads as ordinary hallways", PLANNER,
     "            if (OnRoad(first, second, rooms)) { return 3; }" + chr(10), ""),

    ("and a road is no longer recognised as a run that carries on past its ends", PLANNER,
     "            return ContinuesPast(second, first, rooms, alongX)" + chr(10)
     + "                || ContinuesPast(first, second, rooms, alongX);",
     "            return false;"),

    ("THE NEIGHBOURHOOD BLOCK IS NEVER FORMED", PLANNER,
     "                { PushAgainst(rooms, terrace[index], rooms[hub], depth); }",
     "                { }"),

    ("and it stops offering the mobile rooms first, so every push snaps back", PLANNER,
     "                terrace.Sort((left, right) => left.links.Count != right.links.Count" + chr(10)
     + "                    ? left.links.Count - right.links.Count" + chr(10)
     + "                    : left.index - right.index);" + chr(10), ""),

    ("THE PRUNE GOES BACK TO GUESSING WHICH EDGES THE TREE OWNS", PLANNER,
     "                    if (LinkedGraphIsWhole(rooms)) { continue; }",
     "                    if (a.x == b.x || a.z == b.z) { continue; }"),

    ("and a removal that disconnects the level is no longer put back", PLANNER,
     "                    if (LinkedGraphIsWhole(rooms)) { continue; }" + chr(10), ""),

    # **RE-AIMED 2026-10-03 at the divergence that is still POSSIBLE.** There is one width now,
    # so "the planner models a width the generator does not carve" cannot be planted by changing a
    # number. What can still diverge is the **shaping depth** each reader passes in: the carver
    # feeding the coordinate's own depth instead of the pair's would hand the authority a
    # different question and get a different corridor back.
    ("the generator asks for a corridor at the wrong shaping depth", GEN,
     "                        Math.Max(RoomLayoutPlanner.ShapeDepthOf(rooms, room, depth)," + NL
     + "                            RoomLayoutPlanner.ShapeDepthOf(rooms, other, depth))," + NL
     + "                        rooms);",
     "                        depth," + NL + "                        rooms);"),

    # ------------------------------------------------------ the open-map budget
    ("THE BUDGET GETS HARD-CODED INSTEAD OF READING THE GAME'S LIMIT", BUDGET,
     "int budget = scenario > 0 ? scenario : Prefs.MaxNumberOfPlayerSettlements;",
     "int budget = scenario > 0 ? scenario : 5;"),

    ("the scenario override stops being consulted", BUDGET,
     "int budget = scenario > 0 ? scenario : Prefs.MaxNumberOfPlayerSettlements;",
     "int budget = Prefs.MaxNumberOfPlayerSettlements;"),

    ("the per-scenario field is removed from the start def", STARTDEF,
     "        public int openMapBudget;", "        public int openMapBudgetUnused;"),

    ("THE BUDGET FLOOR GOES AND A SLIDER AT 1 BREAKS THE SOLO START", BUDGET,
     "internal const int MinimumBudget = 2;", "internal const int MinimumBudget = 1;"),

    ("the floor is defined but not applied", BUDGET,
     "return Mathf.Max(MinimumBudget, budget);", "return budget;"),

    ("a Backrooms level stops counting against the budget", BUDGET,
     "                    if (map.Parent is Generation.RimroomsDestinationMapParent) { held++; }" + NL,
     ""),

    ("colonies stop counting against the budget", BUDGET,
     "                    else if (map.IsPlayerHome && map.Parent is Settlement) { held++; }" + NL,
     ""),

    ("A GATE IS BLOCKED ONLY AFTER A COORDINATE HAS ALREADY BEEN MINTED", FRONTIER,
     "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }" + NL
     + "            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);",
     "            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);" + NL
     + "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }"),

    ("THE BUDGET STARTS CLOSING THE LAST DOOR HOME", FRONTIER,
     "            if (source != null)" + NL + "            {" + NL
     + "                CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);",
     "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }" + NL
     + "            if (source != null)" + NL + "            {" + NL
     + "                CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);"),

    ("the doorway stops checking the budget at all", FRONTIER,
     "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }" + NL, ""),

    ("the map-generation backstop goes", SERVICE,
     "            if (coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(Portals.OpenMapBudget.BlockedKey); }" + NL, ""),

    ("RECALLING AN ALREADY-GENERATED COORDINATE STARTS BEING REFUSED", SERVICE,
     "if (coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother)",
     "if (!Portals.OpenMapBudget.CanOpenAnother)"),

    ("the player is never told why the gate refused", KEYED,
     "<RR_Frontier_TooManyGatesHeld>", "<RR_Frontier_TooManyGatesHeldUnused>"),

    ("WAYS ONWARD GO BACK TO TWO PER LEVEL", FRONTIER,
     "internal const int MinimumFrontiersPerCoordinate = 4;",
     "internal const int MinimumFrontiersPerCoordinate = 2;"),

    ("the ceiling on ways onward disappears", FRONTIER,
     "            int allowed = MinimumFrontiersPerCoordinate + rooms / RoomsPerExtraFrontier;" + NL
     + "            return allowed > MaximumFrontiersPerCoordinate ? MaximumFrontiersPerCoordinate : allowed;",
     "            return MinimumFrontiersPerCoordinate + rooms / RoomsPerExtraFrontier;"),

    ("the gate count starts reading depth instead of the size of the place", FRONTIER,
     "int rooms = coordinate == null || coordinate.Rooms == null ? 0 : coordinate.Rooms.Count;",
     "int rooms = coordinate == null ? 0 : coordinate.Depth;"),

    ("THE NATURAL CHAIN GOES BACK TO THREE BANDS", FRONTIER,
     "internal const int MaximumNaturalDepth = 6;", "internal const int MaximumNaturalDepth = 3;"),

    ("a coordinate map starts unloading itself and taking the player's work with it", PARENT,
     "            alsoRemoveWorldObject = false;" + NL + "            return false;",
     "            alsoRemoveWorldObject = false;" + NL + "            return true;"),

    # ------------------------------------------------------ letting a place go
    ("THE DISCOVERY-COSTS-A-SLOT FACT STOPS HOLDING", ADDRESS,
     "DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry)",
     "DestinationService.EnsureSiteUnused(campaign, coordinate, out siteMap, out siteEntry)"),

    ("a release stops being written to the save", RECORDS,
     '            Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);' + NL,
     ""),

    ("THE EXPLORED-GRAPH GUARD STOPS EXEMPTING A DELIBERATE RELEASE", SERVICE,
     "            if (!releasedAndRebuildable && coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||",
     "            if (coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||"),

    ("THE EXEMPTION STARTS BYPASSING A LIVE MAP TOO", SERVICE,
     "                !Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id);",
     "                true;"),

    ("THE EXEMPTION OUTLIVES ITS REASON", SERVICE,
     "            coordinate.releasedByPlayer = false;" + NL, ""),

    ("THE EDGES ARE REMOVED BEFORE THE DOORS ARE TOLD WHERE THEY LED", RELEASE,
     "                RememberOn(edge.First, coordinate, map);" + NL
     + "                RememberOn(edge.Second, coordinate, map);" + NL,
     ""),

    ("THE MAP IS TORN DOWN BEFORE THE EDGES ARE REMOVED", RELEASE,
     "            for (int index = 0; index < shelved.Count; index++)" + NL
     + "            { network.ForgetConnection(shelved[index].Id); }",
     "            Current.Game.DeinitAndRemoveMap(map, false);" + NL
     + "            for (int index = 0; index < shelved.Count; index++)" + NL
     + "            { network.ForgetConnection(shelved[index].Id); }"),

    ("a release discards the graph, so the place comes back different", RELEASE,
     "            coordinate.status = CoordinateStatus.Discovered;",
     "            coordinate.rooms = null;"),

    ("the pairing is written onto the map being destroyed", RELEASE,
     "            if (anchor == null || anchor.Destroyed || anchor.Map == null || anchor.Map == releasing)",
     "            if (anchor == null || anchor.Destroyed || anchor.Map == null)"),

    ("RELEASING THE HEADQUARTERS BECOMES POSSIBLE", RELEASE,
     '            if (campaign.Headquarters == map) { return "RR_Release_Headquarters"; }' + NL, ""),

    ("A PLACE WITH PEOPLE IN IT BECOMES RELEASABLE", RELEASE,
     '            { return "RR_Release_CrewInside"; }', '            { }'),

    ("a prisoner or an animal stops counting as somebody inside", RELEASE,
     "pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony))",
     "pawn.Faction == Faction.OfPlayer && pawn.RaceProps.Humanlike))"),

    ("A PLACE SOMEBODY IS CROSSING INTO BECOMES RELEASABLE", RELEASE,
     '                    if (crossings.IsConnectionInFlight(edge.Id)) { return "RR_Release_CrossingInFlight"; }' + NL,
     ""),

    ("the network gains a second, wider removal", NETWORK,
     "            connections.Remove(edge);",
     "            connections.Remove(edge);" + NL
     + "            connections.RemoveAll(other => other == null);"),

    ("THE DOOR STOPS REMEMBERING WHERE IT LED", EMERGENCE,
     '            Scribe_Values.Look(ref shelvedCoordinateId, "rr_emergenceShelvedCoordinate");' + NL,
     ""),

    ("the release stops telling the door anything", RELEASE,
     "            emergence.RememberShelvedPlace(coordinate.Id);",
     "            emergence.ForgetShelvedPlace();"),

    # **RE-OPENING IS GONE, SO THESE PLANTS INVERTED.** Owner: *"we do need to be able to
    # close natural portals u just can not re open them"*, *"thats the whole 5 limit
    # issue"*. They used to break the SHAPE of a re-open; each one now RESTORES a way to
    # re-open and requires the proof to refuse it. Replaced rather than deleted, so the
    # count stays honest.
    ("THE REOPEN METHOD COMES BACK", EMERGENCE,
     "        // `Reopen` lived here until 0.12.59-dev.",
     "        private CompanyActionResult Reopen(CoordinateRecord shelved)" + NL
     + "        { return PortalAddressService.RegisterNaturalAddress("
     + "parent, ApproachCell, shelved); }" + NL + NL
     + "        // `Reopen` lived here until 0.12.59-dev."),

    ("THE REOPEN GIZMO COMES BACK", EMERGENCE,
     "            bool marked = IsDesignated;",
     "            bool marked = IsDesignated;" + NL
     + "            yield return new Command_Action { defaultLabel = "
     + chr(34) + "RR_Release_ReopenLabel" + chr(34) + ".Translate() };"),

    ("the door stops remembering where it led, so a spent gate looks like any door",
     EMERGENCE,
     "internal string ShelvedCoordinateId { get { return shelvedCoordinateId; } }",
     "internal string ShelvedCoordinateIdUnused { get { return shelvedCoordinateId; } }"),

    ("THE HELD-PLACES PANE IS NEVER DISPATCHED TO", OPTABS,
     "                case 12: DrawHeldPlaces(listing, campaign); break;" + NL, ""),

    ("the help pane index is left behind and help opens the places list", OPTABS,
     "        private const int HelpPane = 13;", "        private const int HelpPane = 12;"),

    ("the pane stops showing the colonies that fill the budget", PLACES,
     "                listing.Label(\"RR_Release_ColonyRow\".Translate(colonies[index].Parent.Label));",
     "                continue;"),

    ("A RELEASE STOPS BEING CONFIRMED", PLACES,
     "                            destructive: true,", "                            destructive: false,"),

    ("A FAILED RELEASE BECOMES SILENT", PLACES,
     '                Messages.Message("RR_Release_Failed".Translate(label, refusal.Translate()),',
     '                Messages.Message("".Translate(),'),

    ("a release refusal loses its keyed string", KEYED,
     "<RR_Release_CrewInside>", "<RR_Release_CrewInsideUnused>"),

    ("the places pane label is never written", KEYED,
     "<RR_UI_Places>", "<RR_UI_PlacesUnused>"),


    # ------------------------------------------------------ the bend, the degree and the vaults
    ("CORRIDORS GO BACK TO BEING ALL STRAIGHT", PLANNER,
     "            return BentLegs(first, second, depth, rooms);",
     "            return legs;"),

    ("THE ROUTE FORMS COLLAPSE TO ONE, so every bend in the game is the same shape", PLANNER,
     "                int form = (roll + attempt) % RouteForms;",
     "                int form = 0;"),

    ("THE U-TURN IS GONE, so no corridor ever leaves a room the wrong way", PLANNER,
     "                    int wrongWayX = eastward ? a.minX - 1 : a.maxX + 1;",
     "                    int wrongWayX = eastward ? a.maxX + 1 : a.minX - 1;"),

    ("the route terminus is extended into the room it is supposed to stop outside of", PLANNER,
     "                if (index != 0) { start -= step * reach; }",
     "                start -= step * reach;"),

    ("THE REACH BRAID IS GONE, so the degree ceiling falls back to a diagonal's eight", PLANNER,
     "                    if (roll % ReachBraidRarity != 0) { continue; }",
     "                    if (true) { continue; }"),

    ("THE STRAIGHT RUN STOPS BEING PROVED CLEAR, so a corridor is carved through a room", PLANNER,
     "                if (!LegsClearEveryRoom(legs, rooms)) { legs.Clear(); }" + NL
     + "                if (halfWidth > NarrowestCorridorHalfWidth && legs.Count == 0)",
     "                if (halfWidth > NarrowestCorridorHalfWidth && legs.Count == 0)"),

    ("A GRAPH EDGE IS LEFT STANDING WITH NO CORRIDOR UNDER IT", PLANNER,
     "            PruneUnroutableLinks(rooms, depth);" + NL, ""),

    ("the walk takes a step it cannot carve, so the spanning tree is a lie", PLANNER,
     "                    if (CorridorLegs(rooms[parent], room, depth, rooms).Count == 0 &&" + NL
     + "                        !SharesWall(rooms[parent], room))" + NL
     + "                    { continue; }" + NL, ""),

    ("THE DIAGONAL BRAID IS GONE, so max degree falls back to the slot grid's four", PLANNER,
     "                    if (!SlotIsJunction(seed, slot, depth) && roll % DiagonalBraidRarity != 0)" + NL
     + "                    { continue; }",
     "                    if (true) { continue; }"),

    ("the junction slot stops applying to the diagonals, so the degree spread narrows", PLANNER,
     "                    if (!SlotIsJunction(seed, slot, depth) && roll % DiagonalBraidRarity != 0)",
     "                    if (roll % DiagonalBraidRarity != 0 || false)"),

    ("THE REACHABILITY PROOF REFUSES A SEALED ROOM AGAIN, so degree 0 is unbuildable", PLANNER,
     "            return rooms.All(room => room.links.Count == 0 || seen.Contains(room.Bounds.CenterCell)) &&",
     "            return rooms.All(room => seen.Contains(room.Bounds.CenterCell)) &&"),

    ("a sealed vault is allowed to carry links, so it is just an ordinary room", PLANNER,
     "                rooms.Where(room => room.familyId == SealedFamily).All(room => room.links.Count == 0);",
     "                rooms.Where(room => room.familyId == SealedFamily).All(room => room.links.Count >= 0);"),

    ("THE WALK IS ALLOWED INTO A RESERVED SLOT, so nothing is ever sealed", PLANNER,
     "if (slotOf.ContainsKey(next) || sealedSlots.Contains(next)) { continue; }",
     "if (slotOf.ContainsKey(next)) { continue; }"),

    ("the vaults stop being reserved from the room budget and are silently dropped", PLANNER,
     "            int budget = Math.Max(1, MaxRooms - sealedSlots.Count);",
     "            int budget = MaxRooms;"),

    ("THE VALIDATOR CALLS A SEALED VAULT A DISCONNECTED LEVEL", SERVICE,
     "            if (!visited.Contains(0) ||" + NL
     + "                rooms.Any(room => room.links.Count > 0 && !visited.Contains(room.index)) ||" + NL
     + "                directedEdges < 2 * (linkedRooms - 1) ||",
     "            if (visited.Count != rooms.Count ||" + NL
     + "                directedEdges < 2 * (rooms.Count - 1) ||"),

    # ---------------------------------------------------------------- the door, off the midpoint
    ("EVERY DOOR GOES BACK TO THE EXACT MIDDLE OF ITS WALL", PLANNER,
     "&& cell.z == line) { return true; }",
     "&& cell.z == room.Bounds.CenterCell.z) { return true; }"),

    ("the straight run stops preferring the first room's own centre line", PLANNER,
     "                line = centreA.z >= low && centreA.z <= high ? centreA.z" + NL
     + "                    : centreB.z >= low && centreB.z <= high ? centreB.z : (low + high) / 2;",
     "                line = (low + high) / 2;"),

    # ------------------------------------------------------------- the lane, and filling the map
    ("THE SPAN VARIATION IS ALLOWED TO EAT THE CORRIDOR LANE", PLANNER,
     "            if (reach > lane) { reach = lane; }" + NL, ""),

    ("THE SLOT GRID GOES BACK TO TEN PER AXIS AND A DEEP LEVEL IS BARE ROCK AGAIN", PLANNER,
     "internal const int MaxSlotsPerAxis = 8;", "internal const int MaxSlotsPerAxis = 10;"),

    ("the margin goes back to throwing away a fifth of every map", PLANNER,
     "internal const int Margin = 6;", "internal const int Margin = 14;"),
]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the target must pass before anything is planted")
code = subprocess.call([sys.executable, PROOF],
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
print("  exit %d  %s" % (code, PROOF))
if code != 0:
    sys.stderr.write("BASELINE BROKEN: the proof already fails, so every plant would register "
                     "as caught and the run would prove nothing.\n")
    sys.exit(2)
print("")

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, PROOF],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
