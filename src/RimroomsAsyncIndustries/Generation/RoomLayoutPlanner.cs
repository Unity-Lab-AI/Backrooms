using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Where the rooms of a coordinate go, before any map exists.
    ///
    /// ## Owner direction, 2026-09-30, verbatim
    ///
    /// *"and everything doesnt have to be square rooms and rectangle halways and u can use walls
    /// as pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms and
    /// this can propigate depper with the wild variatiosn of material typeds in all items
    /// equaipment walls floors lights furnature and benches that are found everywher deeper in
    /// with wild random events and layouts and spawns to find and loot!!!!!!"*
    ///
    /// ## What replaced what
    ///
    /// Until 0.12.49-dev this was a **hard-coded 3x3 grid of eight slots** at a fixed 19-cell
    /// spacing, producing 6 to 8 rooms of 10 to 16 cells on a 60x60 map. Every one of those
    /// numbers was a constant.
    ///
    /// The slot grid is now a **function of depth**, and so is everything derived from it:
    ///
    ///     depth   slots     spacing   room span   rooms
    ///       1      6x6         48        38        36      a grand hall, then a maze
    ///       2      7x7         41        30        49
    ///       3+     8x8         36        26        60      a warren, at the room cap
    ///
    /// **The grid used to reach 10x10 and that left 83% of a deep map as bare rock.** A finer grid
    /// fills LESS space, because the rock between rooms is a fixed <see cref="SlotGap"/> per
    /// boundary and more slots means more boundaries. See <see cref="MaxSlotsPerAxis"/>, which is
    /// the owner's *"FILL THE SPACE WITH ROOMS"* read against these constants.
    ///
    /// **Depth 1 is thirty-five rooms of thirty-eight cells, and one hall of eighty-six.** The hall
    /// is the owner's *"grand large spaces"* and *"the main spanw room"*; it takes two slots and it
    /// is the only room that does. Everything past it is well under half its size, which is what
    /// *"going deeping in can mean the numner of branch hallways and rooms distancing from the
    /// main portal spawn"* asks for. *"leas than 60-100 romms"* is held by
    /// <see cref="MaxRooms"/>, and a handful of the slots go to sealed vaults that no corridor
    /// reaches — see <see cref="SealedFamily"/>.
    ///
    /// **The table above was wrong for a whole checkpoint**, describing the 3x3 grid this file
    /// had already stopped using -- and the same staleness in `MaxRoomSpan`, which is the ceiling
    /// the hall has to pass, is what stopped every coordinate generating. See
    /// <see cref="WidestRoomSpan"/>. **A table of numbers in a comment is a claim, and this one
    /// is checked against the constants beside it.**
    ///
    /// The shape is a **serpentine chain** through the slot grid, so consecutive rooms are always
    /// grid neighbours and the chain is connected without needing a search. Dead-end spur rooms
    /// hang off it from the slots the chain did not use.
    ///
    /// Pure planning: no map, world object, crew, random-global state or coordinate mutation.
    /// </summary>
    internal static class RoomLayoutPlanner
    {
        internal const int PlannerVersion = 3;
        /// <summary>
        /// How many whole layouts are attempted before the safe fallback is taken.
        ///
        /// **Three because each candidate is a complete, deterministic maze**, so a
        /// second attempt is a different seed rather than a retry of the same one --
        /// and `check-planner-layouts.py` measures `refused 0/200` at every depth, so
        /// the first candidate is accepted essentially always. This is the depth of
        /// the net, not a quality dial: raising it would hide a planner that had
        /// started failing, which is exactly what `fellback` exists to show.
        /// </summary>
        internal const int CandidateBudget = 3;
        internal const int FallbackCandidate = 3;

        /// <summary>
        /// Free cells kept between the slot grid and the map edge.
        ///
        /// **FOURTEEN WAS THROWING AWAY A FIFTH OF EVERY MAP.** A margin of 14 on all four sides
        /// leaves 272 of 300 usable per axis — 82% of the area — and the owner walked the result:
        /// *"not have so much empty rock space where nothing exists"*. Six is what the geometry
        /// actually needs: the innermost slot centre is `Margin + spacing / 2`, so the widest room
        /// the planner can place in it still lands eight cells clear of the edge, and corridor
        /// walls two cells beyond that. `WithinMap` is the gate that proves it per layout.
        /// </summary>
        internal const int Margin = 6;

        /// <summary>Rock left between neighbouring rooms, which is what corridors run through.</summary>
        internal const int SlotGap = 10;

        // Fewest and most slots per axis, mapped from depth 1 upward. A section header rather than
        // a summary: it describes the pair below it, and a <summary> belongs to one member.
        /// <summary>
        /// Slots per axis at depth 1, and **the number that made the first walked level feel
        /// like a warehouse.**
        ///
        /// At 3 this was a nine-slot grid on a 300x300 map and rooms came out eighty cells
        /// across; the owner walked it and said *"not enough rooms"*. At 6 the first level is a
        /// thirty-six-slot grid with rooms about thirty-four across, and the deepest levels reach
        /// <see cref="MaxSlotsPerAxis"/> -- so **deeper is more rooms, smaller and tighter**,
        /// which is what *"the numner of branch hallways and rooms distancing from the main
        /// portal spawn"* describes.
        /// </summary>
        internal const int MinSlotsPerAxis = 6;

        /// <summary>
        /// Slots per axis at the deepest coordinate, and **ten was the reason a deep level was 83%
        /// bare rock.**
        ///
        /// Owner, 2026-10-03: *"not have so much empty rock space where nothing exists ... DO YOU
        /// UNDERSTAND WHAT A MAZE MEANS AND TO FILL THE SPACE WITH ROOMS"*. Measured against the
        /// arithmetic rather than guessed at: the fraction of a slot a room occupies is
        /// `(1 - SlotGap / spacing)²`, and spacing is the map divided by the slot count. **So a
        /// finer grid fills less space, not more** — the rock between rooms is a fixed ten cells
        /// per boundary and more boundaries means more rock. At ten slots the span had fallen to
        /// sixteen cells against a twenty-seven-cell spacing and roomfill measured **17.1%**; at
        /// eight it is twenty-six against thirty-six.
        ///
        /// This also settles what looked like two contradictory directions. *"leas than 60-100
        /// romms"* asks for fewer, larger rooms and *"FILL THE SPACE WITH ROOMS"* asks for less
        /// bare rock — and they are **the same instruction**, because fewer larger rooms is what
        /// fills a fixed map.
        ///
        /// **RAISED FROM 8 TO 9 AT 0.12.98-dev, on owner direction, and the measurement is why
        /// it was safe.** Asked whether the deep bands should reach the *"60-100"* they were
        /// originally specified at, the owner chose the middle: eighty. Nine slots is what affords
        /// it — eighty-one slots against a ceiling of eighty rooms, with the one over plus the
        /// sealed vaults coming out of the same budget.
        ///
        /// **Measured over 200 seeds at seven depths before it was kept.** Depth 1 and 2 did not
        /// move at all, because their slot counts are below the ceiling either way; depth 3 went
        /// from 60 rooms to 63 and its room fill went **up**, 44.9% to 47.1%; depth 4 and deeper
        /// reach the full eighty at 42.6% fill, 2.3 points below where they were. `refused 0/200`
        /// and `fellback 0` at every band, degree rose from 5.22 to 5.49, and back-to-back pairs
        /// rose from 3,115 to 3,194.
        ///
        /// **The cost is in the span, which is the honest trade:** the widest room at depth 4 and
        /// deeper falls from 62 cells to 54. That is *"going deeping in can mean the numner of
        /// branch hallways and rooms distancing from the main portal spawn"* arriving in the
        /// numbers — deeper is more rooms, smaller and tighter — and it is why the grand rooms
        /// and the shallow bands were left alone.
        ///
        /// Deeper is still more rooms and tighter ones — 6, 7, 8, then 9 — and it still stops
        /// before the point where another slot costs more rock than it adds room: at ten the span
        /// had fallen to sixteen cells and fill measured 17.1%.
        /// </summary>
        internal const int MaxSlotsPerAxis = 9;

        /// <summary>
        /// The ceiling, and it is **eighty** since 0.12.98-dev.
        ///
        /// The owner named *"leas than 60-100 romms"*; it sat at the bottom of that band
        /// at 60 and, asked directly, they chose the middle. Reached at depth 4 and deeper, where
        /// eighty-one slots are available; the shallow bands never approach it because their grids
        /// are smaller on purpose.
        /// </summary>
        internal const int MaxRooms = 80;

        /// <summary>
        /// Cells between pillars inside a room. Chosen against
        /// <c>RoofCollapseUtility.RoofMaxSupportDistance</c>, which is **6.9**, so a lattice at
        /// this spacing keeps every roofed cell within reach of something that holds roof.
        /// </summary>
        internal const int PillarSpacing = 6;

        /// <summary>
        /// A room only gets pillars once it is wider than a roof can span unaided -- twice 6.9,
        /// rounded down. Below that the room is a room; above it, it is a hall.
        /// </summary>
        internal const int PillarThreshold = 13;

        /// <summary>Exactly one of each of these, and index 0 is always the threshold.</summary>
        private static readonly string[] UniqueFamilies = { "threshold_room", "office_copy", "return_gallery" };

        /// <summary>Filled in along the chain, as many times as the chain is long.</summary>
        private static readonly string[] ChainFamilies = { "survey_lobby", "service_passage", "borrowed_corridor" };

        /// <summary>Dead ends hanging off the chain, one link each.</summary>
        private static readonly string[] SpurFamilies = { "storage_nook", "utility_room" };

        /// <summary>
        /// The family of a room with **no links at all**, which you reach by mining.
        ///
        /// ## Owner direction, 2026-10-03, verbatim
        ///
        /// *"and we should have doors that lead no where but to an ore or gem vein, and veins
        /// leading to other rooms so insentive to mine things out to find isolated undiscorvered
        /// rooms when mining and deconsturcting wals and sucvh"*, and from the same day
        /// *"room connected to like 0 - 10 other rooms"*.
        ///
        /// **The degree spec explicitly allows zero and nothing could produce it**, because a
        /// zero-link room is one `CandidateIsSafe` refuses: it proves every room's centre reachable
        /// across carved floor, and a sealed room has no floor leading to it. The owner's later
        /// direction is what makes zero legal rather than broken — *"isolated undiscorvered
        /// rooms"* are **meant** to have no way in, and the way in is a pick.
        ///
        /// So the reachability proof now asks its question of rooms that **claim** a route. A room
        /// with links must be walkable to; a room with none is a vault, and the rock around it is
        /// `Mineable` like all the fill, so it is reachable in the only sense this room wants to be.
        /// </summary>
        internal const string SealedFamily = "sealed_vault";

        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)
        {
            selected = null;
            for (int candidate = 0; candidate < CandidateBudget; candidate++)
            {
                List<RoomRecord> rooms = Build(coordinate, candidate);
                if (CandidateIsSafe(rooms, DepthOf(coordinate), CoordinateMotif.For(coordinate)))
                { selected = rooms; return true; }
            }
            List<RoomRecord> fallback = Build(coordinate, FallbackCandidate);
            if (!CandidateIsSafe(fallback, DepthOf(coordinate), CoordinateMotif.For(coordinate)))
            { return false; }
            selected = fallback;
            return true;
        }

        internal static bool TryBuildSafeFallback(CoordinateRecord coordinate, out List<RoomRecord> fallback)
        {
            fallback = null;
            if (coordinate == null || string.IsNullOrWhiteSpace(coordinate.Id) || coordinate.Seed < 0 ||
                coordinate.GeneratorVersion < 1 || coordinate.roomLibraryVersion < 1)
            { return false; }
            List<RoomRecord> candidate = Build(coordinate, FallbackCandidate);
            if (!CandidateIsSafe(candidate, DepthOf(coordinate), CoordinateMotif.For(coordinate)))
            { return false; }
            fallback = candidate;
            return true;
        }

        internal static int IdentifyCandidate(CoordinateRecord coordinate)
        {
            for (int candidate = 0; candidate <= FallbackCandidate; candidate++)
            {
                List<RoomRecord> rooms = Build(coordinate, candidate);
                if (coordinate.Rooms.Count != rooms.Count) { continue; }
                bool same = rooms.All(a => coordinate.Rooms.Any(b => a.index == b.index && a.familyId == b.familyId &&
                    a.x == b.x && a.z == b.z && a.width == b.width && a.height == b.height && a.links.OrderBy(i => i).SequenceEqual(b.links.OrderBy(i => i))));
                if (same) { return candidate; }
            }
            return -1; // Existing saved graph: never relabel it as a newly selected candidate.
        }

        /// <summary>A coordinate's depth, floored at one, in one place so every reader agrees.</summary>
        internal static int DepthOf(CoordinateRecord coordinate)
        {
            return coordinate == null || coordinate.Depth < 1 ? 1 : coordinate.Depth;
        }

        /// <summary>Slots per axis for this depth. Deeper means more, smaller rooms.</summary>
        internal static int SlotsPerAxis(int depth)
        {
            int slots = MinSlotsPerAxis + (depth < 1 ? 0 : depth - 1);
            if (slots < MinSlotsPerAxis) { return MinSlotsPerAxis; }
            return slots > MaxSlotsPerAxis ? MaxSlotsPerAxis : slots;
        }

        /// <summary>Centre-to-centre distance between neighbouring slots.</summary>
        internal static int SlotSpacing(int slots)
        {
            return (DestinationService.MapWidth - Margin * 2) / slots;
        }

        /// <summary>The default span of a room in a slot of this size, always even.</summary>
        internal static int SlotRoomSpan(int spacing)
        {
            int span = spacing - SlotGap;
            if (span % 2 != 0) { span--; }
            return span < 8 ? 8 : span;
        }

        /// <summary>How far either side of the default a room's span may vary, in cells.</summary>
        internal const int SpanVariation = 6;

        /// <summary>
        /// The widest span this planner can actually produce, at its coarsest slot grid.
        ///
        /// **THIS IS WHY NO COORDINATE WOULD GENERATE AFTER 0.12.61-dev.**
        /// `DestinationService.ValidateRooms` refuses any room wider than this, and the number it
        /// was reading was <see cref="SlotRoomSpan"/> alone -- the span of a room that fills one
        /// slot and does not vary. By then the planner was producing two rooms that are wider by
        /// construction:
        ///
        ///   * the grand hall spans **two** slots less the gap -- 80 cells at depth 1, against a
        ///     ceiling of 34, so **candidates 0, 1 and 2 were rejected every single time**;
        ///   * <see cref="VariedRoomSpan"/> may add up to <see cref="SpanVariation"/>, so the
        ///     fallback candidate was rejected whenever any one of its rooms rolled wider --
        ///     which, over twenty-odd rooms, is every time in practice.
        ///
        /// All four candidates refused, `TrySelect` returned false, and the player got
        /// *"No safe first-site layout was found within the bounded attempt limit"* with nothing
        /// in the log. The opening stops at that point, so the door was never marked and no edge
        /// was ever registered -- which is exactly the owner's report: *"this run through the door
        /// is not blue and i dont see the backrooms is there and cant portal to it"*.
        ///
        /// **The ceiling is a statement about the planner, so the planner is where it belongs.**
        /// A validator carrying its own copy of a number the planner decides is the same defect
        /// as the literal 19 that this file already removed once, and as the light count that
        /// stopped generation for thirty-nine checkpoints.
        /// </summary>
        internal static int WidestRoomSpan
        {
            get
            {
                int spacing = SlotSpacing(MinSlotsPerAxis);
                int hall = spacing * 2 - SlotGap;
                int varied = SlotRoomSpan(spacing) + SpanVariation;
                return hall > varied ? hall : varied;
            }
        }

        /// <summary>
        /// This room's span, varied from the default by its own slot.
        ///
        /// Owner: *"it needs to be more maze liek"*. **A grid of identical boxes reads as a grid
        /// however many boxes you add.** Unequal ones read as rooms, and the gap between a small
        /// room and its slot becomes more rock, which is more wall to walk around.
        ///
        /// Seeded from the slot, so a coordinate is the same place every time it is visited --
        /// the record system, the revisit check and every saved route depend on that.
        ///
        /// Always even, because the door placement puts a doorway at the midpoint of each side,
        /// and never below eight, because a room has to hold a doorway on each wall and a walk
        /// between them.
        /// </summary>
        internal static int VariedRoomSpan(int spacing, IntVec2 slot, int seed, int depth)
        {
            int baseline = SlotRoomSpan(spacing);
            int reach = SpanVariation < baseline / 3 ? SpanVariation : baseline / 3;
            // **AND THE VARIATION MAY NEVER EAT THE CORRIDOR LANE.** Two neighbours both rolled
            // to their widest leave `SlotGap - 2 * reach` cells of rock between them, and the
            // narrowest corridor is `2 * NarrowestCorridorHalfWidth + 1` cells wide including its
            // walls. Below that the pair gets no route at all -- the step is declined, the level
            // comes out smaller, and nothing says why. It had never bitten because the numbers
            // happened to leave exactly five cells at every depth the planner produced; it bit
            // the moment the slot grid changed, which is the definition of a constraint that was
            // being satisfied by luck.
            int lane = SlotGap - (2 * NarrowestCorridorHalfWidth + 1);
            if (reach > lane) { reach = lane; }
            if (reach < 1) { return baseline; }
            int offset = DestinationService.StableHash(seed, "span:" + slot.x + "," + slot.z, depth)
                % (reach * 2 + 1) - reach;
            int span = baseline + offset;
            if (span % 2 != 0) { span--; }
            return span < 8 ? 8 : span;
        }

        /// <summary>Where a slot's centre sits on the map.</summary>
        internal static int SlotCenter(int index, int spacing)
        {
            return Margin + spacing / 2 + spacing * index;
        }

        /// <summary>
        /// The pillar cells inside a room, and **the single place this is decided.**
        ///
        /// Both the generator, which spawns them, and <see cref="CandidateIsSafe"/>, which has to
        /// prove the room is still walkable with them in it, call this. Two places deriving the
        /// same lattice independently is precisely the defect that stopped every coordinate
        /// generating from 0.7.8-dev to 0.12.47-dev.
        ///
        /// **Never on the centre cross.** Doors and corridors meet a room at the midpoint of each
        /// wall, so the centre row and centre column are left completely clear: a straight walk
        /// from any doorway to any other cannot be blocked by a pillar, whatever the room's size.
        /// </summary>
        internal static IEnumerable<IntVec3> PillarCells(RoomRecord room)
        {
            CellRect bounds = room.Bounds;
            if (bounds.Width <= PillarThreshold && bounds.Height <= PillarThreshold)
            { yield break; }
            IntVec3 center = bounds.CenterCell;
            for (int x = bounds.minX + PillarSpacing; x <= bounds.maxX - PillarSpacing; x += PillarSpacing)
            {
                for (int z = bounds.minZ + PillarSpacing; z <= bounds.maxZ - PillarSpacing; z += PillarSpacing)
                {
                    if (x == center.x || z == center.z) { continue; }
                    yield return new IntVec3(x, 0, z);
                }
            }
        }

        /// <summary>Links walked before a room counts as one level deeper, for shaping.</summary>
        /// <remarks>
        /// **THREE BECAME TWO WITH THE DEGREE WORK, and the probe is why.** A room's shaping band
        /// is its distance from the hall divided by this, and the degree work collapsed those
        /// distances: a five-connected maze has a short diameter, so almost every room landed in
        /// band 0 and `RockIntrusionCells` declined it. Measured: rooms with any rock shaped at
        /// all fell from 83.5% to 42.2% at depth 1, purely as a side effect of better
        /// connectivity. At two, the hall and its immediate neighbours still read as square --
        /// which is the arrival, and the thing everything past it is supposed to contrast with --
        /// and the rest comes apart again.
        /// </remarks>
        internal const int LinksPerShapeBand = 2;

        /// <summary>The most distance can add to a room's shaping depth.</summary>
        internal const int MaximumShapeBand = 4;

        /// <summary>
        /// The depth this room is SHAPED at: the coordinate's own, plus how far it is from the
        /// spawn hall.
        ///
        /// Owner: *"you can have back to back roomes and mazes of halways of varied widtchs and
        /// lengs ... triangle, octangones, rombones, all the geomentry"*, and *"not just doors on
        /// 4 cosides of nothing but square rooms"*.
        ///
        /// **Every shape system in this file refused to run at depth 1**, so the level the owner
        /// walked was all rectangles with identical corridors. The hall and its neighbours should
        /// stay square -- that is the arrival, and it is meant to read as the one built thing --
        /// and everything past it should come apart. Distance is what says which is which.
        ///
        /// **Called by both readers.** The generator carves rock from it and `CandidateIsSafe`
        /// proves the room walkable against it; a shaped room the validator believed was square
        /// is the defect that stopped every coordinate generating for thirty-nine checkpoints,
        /// wearing a prettier outline.
        /// </summary>
        internal static int ShapeDepthOf(IReadOnlyList<RoomRecord> rooms, RoomRecord room, int depth)
        {
            if (rooms == null || room == null) { return depth; }
            int hops = HopsTo(rooms, room.index);
            if (hops < 0) { return depth; }
            int band = hops / LinksPerShapeBand;
            if (band > MaximumShapeBand) { band = MaximumShapeBand; }
            return depth + band;
        }

        /// <summary>Links from the threshold room to this one, or -1 when unreachable.</summary>
        private static int HopsTo(IReadOnlyList<RoomRecord> rooms, int roomIndex)
        {
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int index = 0; index < rooms.Count; index++)
            {
                if (rooms[index] != null) { byIndex[rooms[index].index] = rooms[index]; }
            }
            if (!byIndex.ContainsKey(0)) { return -1; }
            var seen = new Dictionary<int, int> { { 0, 0 } };
            var pending = new Queue<int>();
            pending.Enqueue(0);
            while (pending.Count > 0)
            {
                int current = pending.Dequeue();
                if (current == roomIndex) { return seen[current]; }
                RoomRecord room;
                if (!byIndex.TryGetValue(current, out room) || room.links == null) { continue; }
                for (int index = 0; index < room.links.Count; index++)
                {
                    int next = room.links[index];
                    if (seen.ContainsKey(next) || !byIndex.ContainsKey(next)) { continue; }
                    seen[next] = seen[current] + 1;
                    pending.Enqueue(next);
                }
            }
            int found;
            return seen.TryGetValue(roomIndex, out found) ? found : -1;
        }

        /// <summary>How many distinct forms a room can take.</summary>
        internal const int ShapeForms = 7;

        /// <summary>
        /// The one roll every shape decision in a room is drawn from.
        ///
        /// Lifted out so <see cref="ShapeFormOf"/> and <see cref="RockIntrusionCells"/> cannot
        /// drift: they are the carver and the measurement of the same choice, and a probe that
        /// re-derived this would be the third copy of a rule in this generator rather than the
        /// second. The third copy is what the layout probe's own refusal diagnostic turned out to
        /// be holding, and every reason it printed was wrong because of it.
        /// </summary>
        internal static int ShapeRollFor(RoomRecord room, int depth)
        {
            if (room == null) { return 0; }
            int roll = DestinationService.StableHash(room.index * 31 + depth,
                (room.familyId ?? "") + ":shape", depth);
            return roll < 0 ? ~roll : roll;
        }

        /// <summary>
        /// Which of the seven forms this room takes: the motif's, or its own.
        ///
        /// **Named rather than inlined so it can be MEASURED.** Owner, 2026-10-03: *"repeated
        /// patternes in variations"*. Whether a floor reads as a pattern with variations or as
        /// noise is a number — the share of rooms on the motif — and before this existed
        /// nothing in the battery could see it, exactly as nothing could see the average degree
        /// before the probe was taught to count links. `check-planner-layouts.py` reads this.
        /// </summary>
        internal static int ShapeFormOf(RoomRecord room, int depth, CoordinateMotif motif)
        {
            return motif.ShapeFor(ShapeRollFor(room, depth));
        }

        /// <summary>
        /// The rock left standing inside a room, shaped by the coordinate's own **motif**.
        ///
        /// Owner, 2026-10-03: *"repeated patternes in variations"*. The seven forms below have
        /// existed for some time and **every room rolled its own, independently of every other
        /// room** — which does not make a pattern, it makes noise. A floor where one room is a
        /// wedge, the next has bays and the next is a cross reads as damage rather than as
        /// architecture. The motif is the shape the floor tends toward; see
        /// <see cref="CoordinateMotif"/> for why its grip falls with depth.
        ///
        /// <paramref name="motif"/> must be the SAME motif the reachability proof used. Both
        /// derive it from the coordinate rather than passing it along a chain, so neither can be
        /// handed a different one.
        ///
        /// Cells inside a room that are left as solid rock, so the room is not a rectangle.
        ///
        /// ## Owner direction, 2026-09-30, verbatim
        ///
        /// *"and everything doesnt have to be square rooms and rectangle halways"*.
        ///
        /// ## Why rock in the corners rather than a different rectangle
        ///
        /// The room's `Bounds` has to stay a rect: the validator bounds-checks it, the doors are
        /// placed at the midpoint of each side, the corridors aim at `CenterCell`, and the pillar
        /// lattice is laid out across it. Changing the rect would mean changing all four.
        ///
        /// So the rect stays and the **carve** changes. Rock is left standing inside the room, and
        /// it is left **only in the corners** -- never on the centre cross, never at an edge
        /// midpoint. That single restriction buys four things at once:
        ///
        ///   * every doorway still opens onto clear floor;
        ///   * a straight walk from any doorway to any other is still clear, so **no shape can
        ///     ever disconnect a room** and no candidate is rejected for having one;
        ///   * the pillar lattice needs no special case, because rock already holds roof; and
        ///   * the intrusions are `Mineable`, so a player who wants the rectangle can dig for it.
        ///
        /// **Shallow coordinates barely deform.** Depth 1 gets nothing, for the same reason
        /// <see cref="Derange"/> leaves it alone: the yellow rooms read as a place precisely
        /// because they are monotonous, and the wrongness is something the player travels toward.
        ///
        /// **Decided here and nowhere else**, like <see cref="PillarCells"/>: the generator leaves
        /// these cells uncarved and <see cref="CandidateIsSafe"/> marks them unwalkable, and two
        /// independent derivations of one rule is the defect that cost this project thirty-nine
        /// checkpoints.
        /// </summary>
        internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth,
            CoordinateMotif motif)
        {
            // **Never the grand hall.** It is the room the player arrives in and the one meant to
            // read as built, which is the same reason `FalseOpening` leaves it alone.
            if (room == null || room.index == 0 || depth <= 1) { yield break; }
            CellRect bounds = room.Bounds;
            // The interior only. The perimeter is wall and the ring inside it is the walkway that
            // keeps every doorway reachable -- **and that ring is why every form below is safe**:
            // it is a complete loop around the room whatever the middle does.
            int insetX = bounds.minX + 2;
            int insetZ = bounds.minZ + 2;
            int extentX = bounds.maxX - 2;
            int extentZ = bounds.maxZ - 2;
            if (extentX - insetX < 4 || extentZ - insetZ < 4) { yield break; }

            IntVec3 center = bounds.CenterCell;
            int roll = ShapeRollFor(room, depth);

            // How far a mass reaches in, growing with depth and never past the centre cross.
            int reach = System.Math.Min((depth - 1) * 2,
                System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);
            if (reach < 1) { yield break; }

            // The quadrants, which stop one clear cell short of the cross on both axes. A form
            // that fills whole quadrants therefore cannot touch the cross, so it needs no
            // per-cell check of its own.
            int westTo = center.x - 2;
            int eastFrom = center.x + 2;
            int southTo = center.z - 2;
            int northFrom = center.z + 2;
            bool roomy = westTo - insetX >= 3 && extentX - eastFrom >= 3
                && southTo - insetZ >= 3 && extentZ - northFrom >= 3;

            // A plain room is a form too. Owner: *"all the geomentry and mixetrues"* -- a floor
            // where every room is deranged is as uniform as one where none is.
            //
            // **AND WHICH FORM IS THE MOTIF'S MOST OF THE TIME.** This was `roll % ShapeForms`
            // alone: an independent draw per room, so seven good shapes added up to noise. The
            // motif holds hardest at depth 1 and loosens all the way down, which is one number
            // producing both the monotonous yellow floors and the incoherent deep ones.
            int form = ShapeFormOf(room, depth, motif);
            if (!roomy && form != 0) { form = 0; }

            bool east = (roll / 7) % 2 == 0;
            bool north = (roll / 11) % 2 == 0;

            if (form == 1 || form == 2 || form == 3)
            {
                // ELL: one quadrant. TEE: two on one side. CROSS: all four.
                for (int quadrant = 0; quadrant < 4; quadrant++)
                {
                    bool quadrantEast = quadrant == 1 || quadrant == 2;
                    bool quadrantNorth = quadrant >= 2;
                    if (form == 1 && (quadrantEast != east || quadrantNorth != north)) { continue; }
                    if (form == 2 && quadrantNorth != north) { continue; }
                    int fromX = quadrantEast ? eastFrom : insetX;
                    int toX = quadrantEast ? extentX : westTo;
                    int fromZ = quadrantNorth ? northFrom : insetZ;
                    int toZ = quadrantNorth ? extentZ : southTo;
                    for (int x = fromX; x <= toX; x++)
                    {
                        for (int z = fromZ; z <= toZ; z++) { yield return new IntVec3(x, 0, z); }
                    }
                }
                yield break;
            }

            if (form == 4)
            {
                // WEDGE: a right triangle in one quadrant, hypotenuse facing the middle. The
                // owner asked for triangles; this is one.
                int fromX = east ? eastFrom : insetX;
                int toX = east ? extentX : westTo;
                int fromZ = north ? northFrom : insetZ;
                int toZ = north ? extentZ : southTo;
                int width = toX - fromX;
                int height = toZ - fromZ;
                for (int dx = 0; dx <= width; dx++)
                {
                    for (int dz = 0; dz <= height; dz++)
                    {
                        // Measured from the corner of the room, so the solid part is the corner
                        // and the diagonal face looks into the room.
                        if (dx * height + dz * width > width * height) { continue; }
                        int x = east ? extentX - dx : insetX + dx;
                        int z = north ? extentZ - dz : insetZ + dz;
                        yield return new IntVec3(x, 0, z);
                    }
                }
                yield break;
            }

            if (form == 5)
            {
                // PARTITION: a stub wall in from one side, stopping two clear cells short of the
                // cross. Narrows and a dead-end alcove inside a single room.
                bool alongX = (roll / 13) % 2 == 0;
                int thickness = reach > 2 ? 2 : 1;
                if (alongX)
                {
                    int at = north ? northFrom + (extentZ - northFrom) / 2
                        : insetZ + (southTo - insetZ) / 2;
                    int fromX = east ? eastFrom : insetX;
                    int toX = east ? extentX : westTo;
                    for (int z = at; z < at + thickness && z <= extentZ; z++)
                    {
                        for (int x = fromX; x <= toX; x++) { yield return new IntVec3(x, 0, z); }
                    }
                }
                else
                {
                    int at = east ? eastFrom + (extentX - eastFrom) / 2
                        : insetX + (westTo - insetX) / 2;
                    int fromZ = north ? northFrom : insetZ;
                    int toZ = north ? extentZ : southTo;
                    for (int x = at; x < at + thickness && x <= extentX; x++)
                    {
                        for (int z = fromZ; z <= toZ; z++) { yield return new IntVec3(x, 0, z); }
                    }
                }
                yield break;
            }

            if (form == 6)
            {
                // BAYS: alternating blocks along one wall, which reads as a row of alcoves rather
                // than as damage.
                bool alongX = (roll / 17) % 2 == 0;
                int period = reach + 2;
                if (alongX)
                {
                    int fromZ = north ? northFrom : insetZ;
                    int toZ = System.Math.Min(north ? extentZ : southTo, fromZ + reach - 1);
                    for (int x = insetX; x <= extentX; x++)
                    {
                        if (x == center.x || (x - insetX) % period >= period / 2) { continue; }
                        for (int z = fromZ; z <= toZ; z++)
                        {
                            if (z == center.z) { continue; }
                            yield return new IntVec3(x, 0, z);
                        }
                    }
                }
                else
                {
                    int fromX = east ? eastFrom : insetX;
                    int toX = System.Math.Min(east ? extentX : westTo, fromX + reach - 1);
                    for (int z = insetZ; z <= extentZ; z++)
                    {
                        if (z == center.z || (z - insetZ) % period >= period / 2) { continue; }
                        for (int x = fromX; x <= toX; x++)
                        {
                            if (x == center.x) { continue; }
                            yield return new IntVec3(x, 0, z);
                        }
                    }
                }
                yield break;
            }

            // CORNERS, the original form, and still a good one: which corners are filled decides
            // between a trapezoid, a rhombus and an octagon.
            int corners = 1 + roll % 15;
            for (int index = 0; index < 4; index++)
            {
                if ((corners & (1 << index)) == 0) { continue; }
                bool cornerEast = index == 1 || index == 2;
                bool cornerNorth = index >= 2;
                // Each corner mass is a quarter-ellipse, so the edge it presents to the room is
                // curved rather than another right angle.
                for (int dx = 0; dx < reach; dx++)
                {
                    for (int dz = 0; dz < reach; dz++)
                    {
                        if (dx * dx + dz * dz > reach * reach) { continue; }
                        int x = cornerEast ? extentX - dx : insetX + dx;
                        int z = cornerNorth ? extentZ - dz : insetZ + dz;
                        // The centre cross is inviolable: it is what guarantees every doorway
                        // reaches every other doorway whatever shape the corners take.
                        if (x == center.x || z == center.z) { continue; }
                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }
                        if (z <= bounds.minZ + 1 || z >= bounds.maxZ - 1) { continue; }
                        yield return new IntVec3(x, 0, z);
                    }
                }
            }
        }

        /// <summary>
        /// Half the width of the corridor between two rooms, so hallways are not all one size.
        ///
        /// Two gives a three-cell walkway, three gives five. Derived from the two rooms' own
        /// indices so it is stable across a reload, and **shared with
        /// <see cref="CandidateIsSafe"/>** for the usual reason.
        ///
        /// **A corridor on a ROAD is always the wide one**, whatever the roll says, because that
        /// is most of what makes a road read as one. See <see cref="OnRoad"/>.
        /// </summary>
        internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth,
            IReadOnlyList<RoomRecord> rooms)
        {
            if (first == null || second == null || depth <= 1) { return 2; }
            if (OnRoad(first, second, rooms)) { return 3; }
            int roll = DestinationService.StableHash(first.index * 101 + second.index,
                "corridor:width", depth);
            if (roll < 0) { roll = ~roll; }
            return roll % 3 == 0 ? 3 : 2;
        }

        /// <summary>
        /// Whether this corridor is a stretch of **road**: a straight run that carries on past at
        /// least one of its two ends.
        ///
        /// ## Owner direction, 2026-10-03, verbatim
        ///
        /// *"so its more rooma corradors facilites infastructure roads neighborrs hood malls
        /// shoopping centers military"*.
        ///
        /// ## Why a road is not a kind of room
        ///
        /// The queue row for that direction worked this out about itself: *"roads and neighborrs
        /// hood in particular are not room shapes at all — they are arrangements of rooms,
        /// which is a layout feature rather than a dressing one."* A single room called a roadway
        /// is a room with lane markings in it. **A road is three or more rooms in a line with one
        /// wide corridor running through all of them**, and you can only see it from the layout.
        ///
        /// ## Derived from the graph, stored nowhere
        ///
        /// A pair is a road segment when its two centres share an axis **and** one of them carries
        /// a third link continuing that same line outward. That is a question about the saved graph
        /// and nothing else — so the carver, the reachability proof and the probe all get the same
        /// answer with no new save field and no chance of disagreeing. A `bool isRoad` on
        /// `RoomRecord` would have needed a schema migration and would have been a second
        /// derivation of something the links already say.
        /// </summary>
        internal static bool OnRoad(RoomRecord first, RoomRecord second,
            IReadOnlyList<RoomRecord> rooms)
        {
            if (first == null || second == null || rooms == null) { return false; }
            IntVec3 a = first.Bounds.CenterCell;
            IntVec3 b = second.Bounds.CenterCell;
            bool alongX = a.z == b.z && a.x != b.x;
            bool alongZ = a.x == b.x && a.z != b.z;
            if (!alongX && !alongZ) { return false; }
            return ContinuesPast(second, first, rooms, alongX)
                || ContinuesPast(first, second, rooms, alongX);
        }

        /// <summary>
        /// Whether <paramref name="through"/> carries a link that continues the line beyond it,
        /// away from <paramref name="from"/>.
        /// </summary>
        private static bool ContinuesPast(RoomRecord from, RoomRecord through,
            IReadOnlyList<RoomRecord> rooms, bool alongX)
        {
            if (through.links == null) { return false; }
            IntVec3 near = from.Bounds.CenterCell;
            IntVec3 hub = through.Bounds.CenterCell;
            for (int index = 0; index < through.links.Count; index++)
            {
                RoomRecord onward = null;
                for (int at = 0; at < rooms.Count; at++)
                {
                    if (rooms[at] != null && rooms[at].index == through.links[index])
                    { onward = rooms[at]; break; }
                }
                if (onward == null || onward == from) { continue; }
                IntVec3 far = onward.Bounds.CenterCell;
                if (alongX)
                {
                    // Same row, and on the far side of the hub from where we came.
                    if (far.z != hub.z) { continue; }
                    if (near.x < hub.x ? far.x > hub.x : far.x < hub.x) { return true; }
                    continue;
                }
                if (far.x != hub.x) { continue; }
                if (near.z < hub.z ? far.z > hub.z : far.z < hub.z) { return true; }
            }
            return false;
        }

        /// <summary>
        /// One straight length of a corridor: its floor, its two walls, and which axis it runs
        /// along.
        ///
        /// A corridor is a **list** of these rather than a single rect, because the owner asked for
        /// corridors that bend — *"make sure hallways and corradors and shit arent all straight"* —
        /// and a bend is more than one leg. An orthogonal pair is one leg; a diagonal pair is three,
        /// out of the room, along the rock lane, and back in. See <see cref="BentLegs"/>.
        /// </summary>
        internal struct CorridorLeg
        {
            internal CellRect Floor;
            internal CellRect WallLow;
            internal CellRect WallHigh;
            internal bool AlongX;
        }

        /// <summary>
        /// **THE ONE PLACE A CORRIDOR'S SHAPE IS DECIDED.**
        ///
        /// ## Why this exists
        ///
        /// The shape of a corridor was derived **three times, independently**:
        /// `GenStep_BackroomsDestination.BuildCorridors` carved it, `CandidateIsSafe` modelled it
        /// to prove the level walkable, and `ValidateRooms`/`AreNeighbourRooms` decided which
        /// pairs could have one. This file's own comments name that pattern as the defect that
        /// cost the project thirty-nine checkpoints — *"two readers deriving one rule
        /// independently"* — and it is the reason `PillarCells`, `SharesWall`, `DoorOpening`,
        /// `RockIntrusionCells` and `CorridorHalfWidthBetween` all already exist as single
        /// authorities. The corridor itself was the one that never got the same treatment.
        ///
        /// **Extracted deliberately before any bend is added**, so the behaviour change lands in
        /// one function instead of three. The extraction itself changes nothing: the ranges here
        /// are the ranges both readers already computed, which was checked term by term —
        /// `[min(maxX) + 1, max(minX) - 1]` inclusive in both, and the carver's
        /// `offset ∈ [-halfWidth + 1, halfWidth - 1]` is the validator's `dz ∈ [-reach, reach]`
        /// with `reach = halfWidth - 1`.
        ///
        /// ## Three outcomes, and the list length is which one
        ///
        /// **One leg** — the pair shares a row or a column, so the corridor is the straight run it
        /// always was, at the width the pair rolled.
        ///
        /// **Three legs** — the pair stands one slot apart on *each* axis, so the route bends
        /// through the rock lane between them. <see cref="BentLegs"/> owns that, including the
        /// reason a bend cannot simply turn a corner between the two centres.
        ///
        /// **No legs** — there is no corridor to carve. Either the pair is back to back, and the
        /// doorway in the wall they share is the route (carving between their centres would cut a
        /// hole through that wall and make them one room), or a bend was asked for and every
        /// candidate route ran into a room. `BuildMaze` prunes a link that gets no route, so an
        /// empty list never leaves a graph edge standing with nothing underneath it.
        /// </summary>
        internal static List<CorridorLeg> CorridorLegs(RoomRecord first, RoomRecord second, int depth,
            IReadOnlyList<RoomRecord> rooms)
        {
            var legs = new List<CorridorLeg>();
            if (first == null || second == null || SharesWall(first, second)) { return legs; }
            int halfWidth = CorridorHalfWidthBetween(first, second, depth, rooms);
            CellRect a = first.Bounds;
            CellRect b = second.Bounds;
            IntVec3 centreA = a.CenterCell;
            IntVec3 centreB = b.CenterCell;

            bool alongX;
            int line;
            if (TryStraightCorridor(first, second, out alongX, out line))
            {
                if (alongX)
                {
                    int fromX = Math.Min(a.maxX, b.maxX) + 1;
                    int toX = Math.Max(a.minX, b.minX) - 1;
                    if (toX < fromX) { return legs; }
                    legs.Add(LegAlongX(fromX, toX, line, halfWidth));
                }
                else
                {
                    int fromZ = Math.Min(a.maxZ, b.maxZ) + 1;
                    int toZ = Math.Max(a.minZ, b.minZ) - 1;
                    if (toZ < fromZ) { return legs; }
                    legs.Add(LegAlongZ(line, fromZ, toZ, halfWidth));
                }
                // **THE CLEARANCE TEST APPLIES TO A STRAIGHT RUN TOO.** It never used to, because
                // a straight corridor only ever joined grid-adjacent slots and the gap between
                // them holds nothing. `TryStraightCorridor` can now join a pair that merely
                // overlaps on one axis, and the shape test `AreNeighbourRooms` performs says
                // nothing about what stands between them -- two rooms in the same row two slots
                // apart would be carved straight through the room in the middle. Nothing proposes
                // such a pair today; this is what makes that a fact rather than a hope.
                if (!LegsClearEveryRoom(legs, rooms)) { legs.Clear(); }
                if (halfWidth > NarrowestCorridorHalfWidth && legs.Count == 0)
                {
                    // One retry narrower, for the same reason a bend gets one: a lane pinched by
                    // a widened room is a width problem rather than a routing problem.
                    legs.Add(alongX
                        ? LegAlongX(Math.Min(a.maxX, b.maxX) + 1, Math.Max(a.minX, b.minX) - 1,
                            line, NarrowestCorridorHalfWidth)
                        : LegAlongZ(line, Math.Min(a.maxZ, b.maxZ) + 1,
                            Math.Max(a.minZ, b.minZ) - 1, NarrowestCorridorHalfWidth));
                    if (!LegsClearEveryRoom(legs, rooms)) { legs.Clear(); }
                }
                if (legs.Count > 0) { return legs; }
                // **A BLOCKED STRAIGHT RUN FALLS THROUGH TO THE LANES RATHER THAN GIVING UP.**
                // Two rooms in the same row two slots apart share a centre line, so the straight
                // branch claims the pair and then the clearance test refuses it, because the room
                // between them is in the way. Returning here would make such a pair permanently
                // unlinkable -- which is the four-neighbour ceiling again, wearing the straight
                // branch as a disguise. The lane router goes around.
            }
            return BentLegs(first, second, depth, rooms);
        }

        /// <summary>
        /// **WHERE A STRAIGHT CORRIDOR MEETS TWO ROOMS, AND THE ONE PLACE THAT IS DECIDED.**
        ///
        /// ## What this replaced, and the two defects it closes at once
        ///
        /// A straight corridor used to need the two **centres** to share a row or a column, which
        /// is a far stronger condition than "a straight corridor fits". Two consequences, both
        /// owner-reported:
        ///
        /// **1. The grand hall could only ever lead out of its own two ends.** The hall spans two
        /// slots, so its centre sits *between* them — 58 at depth 1, which is no slot's centre. A
        /// room directly above the hall therefore shared neither axis with it and the link was
        /// refused, so the maze walk could leave the hall along one row and nowhere else. When a
        /// reserved vault happened to block that row's one remaining step, the walk ended with the
        /// hall alone and the candidate was thrown away. Owner, 2026-10-03: *"starts locations of
        /// main grand rooms can be anywhere on the map and lead anywhere in multiple differetn
        /// varied ways"*.
        ///
        /// **2. Every door in the game sat at the exact midpoint of its wall.** Owner, same day:
        /// *"non default fdoor possitions in rooms so doors are not just on each side, can have
        /// doors al over"*. That was not a door-placement rule to be loosened — it was this
        /// condition's shadow. A corridor could only run along a shared centre line, so the only
        /// cell it could ever meet a wall at was that wall's midpoint.
        ///
        /// ## The rule
        ///
        /// Two rooms separated on one axis, whose extents **overlap** on the other by at least
        /// three cells, can be joined by one straight run. The line it runs along is the first of
        /// these that lies inside both rooms, corners excluded:
        ///
        ///   * the first room's centre line — so every pair that worked before works identically,
        ///     which is what makes this a generalisation rather than a change;
        ///   * the second room's centre line — this is the hall's case, and the door it produces is
        ///     off-centre on the hall's wall and dead centre on the small room's;
        ///   * the middle of the overlap, when neither centre is inside it.
        ///
        /// Read by `CorridorLegs` to carve it, by <see cref="DoorOpening"/> to open the two cells it
        /// arrives at, and by <see cref="AreNeighbourRooms"/> to answer whether the pair is legal at
        /// all. **Three readers, one rule** — the same reason `PillarCells`, `SharesWall` and
        /// `CorridorLegs` itself exist, and the defect this file has paid for most often.
        /// </summary>
        internal static bool TryStraightCorridor(RoomRecord first, RoomRecord second,
            out bool alongX, out int line)
        {
            alongX = false;
            line = 0;
            if (first == null || second == null) { return false; }
            CellRect a = first.Bounds;
            CellRect b = second.Bounds;
            if (a.Overlaps(b)) { return false; }
            IntVec3 centreA = a.CenterCell;
            IntVec3 centreB = b.CenterCell;

            if (a.maxX < b.minX || b.maxX < a.minX)
            {
                int low = Math.Max(a.minZ, b.minZ) + 1;
                int high = Math.Min(a.maxZ, b.maxZ) - 1;
                if (high < low) { return false; }
                alongX = true;
                line = centreA.z >= low && centreA.z <= high ? centreA.z
                    : centreB.z >= low && centreB.z <= high ? centreB.z : (low + high) / 2;
                return true;
            }
            if (a.maxZ < b.minZ || b.maxZ < a.minZ)
            {
                int low = Math.Max(a.minX, b.minX) + 1;
                int high = Math.Min(a.maxX, b.maxX) - 1;
                if (high < low) { return false; }
                alongX = false;
                line = centreA.x >= low && centreA.x <= high ? centreA.x
                    : centreB.x >= low && centreB.x <= high ? centreB.x : (low + high) / 2;
                return true;
            }
            return false;
        }

        /// <summary>One straight leg running east-west, from the one formula that shapes a leg.</summary>
        private static CorridorLeg LegAlongX(int fromX, int toX, int centreZ, int halfWidth)
        {
            return new CorridorLeg
            {
                AlongX = true,
                Floor = CellRect.FromLimits(fromX, centreZ - halfWidth + 1, toX, centreZ + halfWidth - 1),
                WallLow = CellRect.FromLimits(fromX, centreZ - halfWidth, toX, centreZ - halfWidth),
                WallHigh = CellRect.FromLimits(fromX, centreZ + halfWidth, toX, centreZ + halfWidth),
            };
        }

        /// <summary>One straight leg running north-south, from the same formula.</summary>
        private static CorridorLeg LegAlongZ(int centreX, int fromZ, int toZ, int halfWidth)
        {
            return new CorridorLeg
            {
                AlongX = false,
                Floor = CellRect.FromLimits(centreX - halfWidth + 1, fromZ, centreX + halfWidth - 1, toZ),
                WallLow = CellRect.FromLimits(centreX - halfWidth, fromZ, centreX - halfWidth, toZ),
                WallHigh = CellRect.FromLimits(centreX + halfWidth, fromZ, centreX + halfWidth, toZ),
            };
        }

        /// <summary>
        /// The narrowest a corridor is ever cut: a three-cell walkway between two walls.
        ///
        /// A bent route has to fit inside the rock lane between two slots, and that lane is only
        /// <see cref="SlotGap"/> cells wide before <see cref="VariedRoomSpan"/> eats into it from
        /// both sides. So a bend asks for the width the pair rolled and then narrows until it
        /// fits, rather than refusing a bend because one roll wanted five cells.
        /// </summary>
        internal const int NarrowestCorridorHalfWidth = 2;

        /// <summary>
        /// **A CORRIDOR THAT BENDS, AND IT RUNS IN THE ROCK LANE RATHER THAN BETWEEN CENTRES.**
        ///
        /// ## Owner direction, 2026-10-03, verbatim
        ///
        /// *"and make sure hallways and corradors and shit arent all straight.. its suppose to be
        /// a lsd trip when it comes to archeteture and shit, repeated patternes in variations, u
        /// -turns, multiple coices on directions to take in every rooms"*, and from the same day
        /// *"room connected to like 0 - 10 other rooms"*.
        ///
        /// **Those are one job, not two.** Straight-only carving is precisely *why* a link had to
        /// join grid-adjacent slots: `AreNeighbourRooms` demanded the two centres share a row or a
        /// column because the carver could only run along one axis. A slot has four orthogonal
        /// neighbours, so the measured max degree was **4** at every depth and the average **2.2
        /// to 2.4** — one way in, one way out, which is what the owner walked and called a string
        /// of pearls. Bending the corridor is what makes a diagonal link possible, and a diagonal
        /// link is what turns a room into a junction.
        ///
        /// ## Why the bend cannot be a corner between the two centres
        ///
        /// Worked at depth 1, where slots sit 45 apart and rooms are about 34 across: an L between
        /// the diagonal pair (0,0) and (1,1) leaves (36,36), runs toward x = 81 and goes **straight
        /// through the room at slot (1,0)**, which occupies x 64..98. A dogleg between centres is
        /// not merely absent from this generator, it is unsafe — and a corridor that opens into the
        /// side of a room is the unreachable-room class that cost this project thirty-nine
        /// checkpoints.
        ///
        /// So a bend runs in a **rock lane**, and a lane is defined by a room's own wall rather
        /// than by the slot grid: the lane beside a room's east wall is the line whose low wall
        /// lands one cell past it. That matters for more than tidiness — it means a route needs
        /// nothing but the two rooms' rects to compute, so no reader has to be told the slot
        /// spacing and no reader can be told a different one.
        ///
        /// ## Seven forms, because one bend shape is a signature
        ///
        /// Owner, 2026-10-03, asked at the fork and answered as *more*: *"it shouldnt just be one
        /// option there needs to be wide varying variations of all types so dont limit yourself"*.
        /// So <see cref="RouteForms"/> holds every form the lane grid admits —
        ///
        ///   * **two elbows** through a lane beside the FIRST room, one per axis;
        ///   * **two elbows** through a lane beside the SECOND room, which reach the same pair of
        ///     rooms by a visibly different route;
        ///   * **two five-leg routes**, out to a lane, across a cross-lane, back down another lane.
        ///     These are what reach a slot **two away**, which is what lifts the degree ceiling
        ///     past the eight a diagonal can manage;
        ///   * **one u-turn**, which leaves the room through the wall facing *away* from where it
        ///     is going and doubles back. The owner asked for *"u -turns"* by name and this is the
        ///     literal article: a corridor that starts by going the wrong way.
        ///
        /// The order is rotated by the pair's own hash, so which form a given pair gets is as
        /// varied as everything else here and is the same on every revisit.
        ///
        /// ## Why the corner is square
        ///
        /// Each leg overruns its turn by `halfWidth - 1`, so a corner is a full block of floor. The
        /// reachability flood is four-directional and a corner that met only diagonally would read
        /// as connected to a person and as sealed to the check.
        ///
        /// ## Safety is proved, not reasoned about
        ///
        /// Every rect of every leg — floor and both walls — must miss **every room's bounds**, and
        /// the route is refused outright if any does not. That is deliberately stricter than it
        /// needs to be: a corridor wall sharing a cell with a room wall is harmless by itself, but
        /// a room's doorway sits on that same wall, and a corridor wall landing on a doorway
        /// **seals the room** — the unreachable-room class that cost this project thirty-nine
        /// checkpoints. The strict test costs a minority of candidates and buys the guarantee
        /// outright, and seven forms at two widths are tried before a pair is given up on.
        /// </summary>
        private static List<CorridorLeg> BentLegs(RoomRecord first, RoomRecord second, int depth,
            IReadOnlyList<RoomRecord> rooms)
        {
            var none = new List<CorridorLeg>();
            if (rooms == null) { return none; }
            CellRect a = first.Bounds;
            CellRect b = second.Bounds;
            IntVec3 centreA = a.CenterCell;
            IntVec3 centreB = b.CenterCell;
            if (a.Overlaps(b)) { return none; }

            int roll = DestinationService.StableHash(first.index * 211 + second.index,
                "corridor:bend", depth);
            if (roll < 0) { roll = ~roll; }
            int widest = CorridorHalfWidthBetween(first, second, depth, rooms);
            var points = new List<IntVec3>();

            for (int attempt = 0; attempt < RouteForms; attempt++)
            {
                int form = (roll + attempt) % RouteForms;
                for (int halfWidth = widest; halfWidth >= NarrowestCorridorHalfWidth; halfWidth--)
                {
                    BuildRouteWaypoints(points, a, b, centreA, centreB, halfWidth, form);
                    if (points.Count < 2) { continue; }
                    List<CorridorLeg> candidate = LegsAlongWaypoints(points, halfWidth);
                    if (candidate.Count > 0 && LegsClearEveryRoom(candidate, rooms))
                    { return candidate; }
                }
            }
            return none;
        }

        /// <summary>How many shapes a bent corridor can take. See <see cref="BentLegs"/>.</summary>
        internal const int RouteForms = 7;

        /// <summary>The lane line beside a rect, whose near wall lands one cell past that wall.</summary>
        private static int LaneBeyond(int wall, bool forward, int halfWidth)
        {
            return forward ? wall + 1 + halfWidth : wall - 1 - halfWidth;
        }

        /// <summary>
        /// The turning points of one route form, as orthogonal waypoints.
        ///
        /// The first and last are the cells just **outside** each room's wall, so the route meets
        /// the doorway without ever entering the room; everything between is a lane crossing.
        /// <see cref="LegsAlongWaypoints"/> turns them into legs.
        /// </summary>
        private static void BuildRouteWaypoints(List<IntVec3> points, CellRect a, CellRect b,
            IntVec3 centreA, IntVec3 centreB, int halfWidth, int form)
        {
            points.Clear();
            bool eastward = centreB.x > centreA.x;
            bool northward = centreB.z > centreA.z;

            // Where the route leaves and arrives, one cell outside each wall.
            int leaveX = eastward ? a.maxX + 1 : a.minX - 1;
            int leaveZ = northward ? a.maxZ + 1 : a.minZ - 1;
            int arriveX = eastward ? b.minX - 1 : b.maxX + 1;
            int arriveZ = northward ? b.minZ - 1 : b.maxZ + 1;

            switch (form)
            {
                case 0: // elbow, along the lane beside the FIRST room's side wall
                {
                    int lane = LaneBeyond(eastward ? a.maxX : a.minX, eastward, halfWidth);
                    points.Add(new IntVec3(leaveX, 0, centreA.z));
                    points.Add(new IntVec3(lane, 0, centreA.z));
                    points.Add(new IntVec3(lane, 0, centreB.z));
                    points.Add(new IntVec3(arriveX, 0, centreB.z));
                    return;
                }
                case 1: // elbow, along the lane beside the FIRST room's end wall
                {
                    int lane = LaneBeyond(northward ? a.maxZ : a.minZ, northward, halfWidth);
                    points.Add(new IntVec3(centreA.x, 0, leaveZ));
                    points.Add(new IntVec3(centreA.x, 0, lane));
                    points.Add(new IntVec3(centreB.x, 0, lane));
                    points.Add(new IntVec3(centreB.x, 0, arriveZ));
                    return;
                }
                case 2: // elbow, along the lane beside the SECOND room instead
                {
                    int lane = LaneBeyond(eastward ? b.minX : b.maxX, !eastward, halfWidth);
                    points.Add(new IntVec3(leaveX, 0, centreA.z));
                    points.Add(new IntVec3(lane, 0, centreA.z));
                    points.Add(new IntVec3(lane, 0, centreB.z));
                    points.Add(new IntVec3(arriveX, 0, centreB.z));
                    return;
                }
                case 3:
                {
                    int lane = LaneBeyond(northward ? b.minZ : b.maxZ, !northward, halfWidth);
                    points.Add(new IntVec3(centreA.x, 0, leaveZ));
                    points.Add(new IntVec3(centreA.x, 0, lane));
                    points.Add(new IntVec3(centreB.x, 0, lane));
                    points.Add(new IntVec3(centreB.x, 0, arriveZ));
                    return;
                }
                case 4: // five legs: out to a lane, across a cross-lane, down a lane beside B
                {
                    int laneOut = LaneBeyond(eastward ? a.maxX : a.minX, eastward, halfWidth);
                    int cross = LaneBeyond(northward ? a.maxZ : a.minZ, northward, halfWidth);
                    int laneIn = LaneBeyond(eastward ? b.minX : b.maxX, !eastward, halfWidth);
                    points.Add(new IntVec3(leaveX, 0, centreA.z));
                    points.Add(new IntVec3(laneOut, 0, centreA.z));
                    points.Add(new IntVec3(laneOut, 0, cross));
                    points.Add(new IntVec3(laneIn, 0, cross));
                    points.Add(new IntVec3(laneIn, 0, centreB.z));
                    points.Add(new IntVec3(arriveX, 0, centreB.z));
                    return;
                }
                case 5: // five legs, the other way round
                {
                    int laneOut = LaneBeyond(northward ? a.maxZ : a.minZ, northward, halfWidth);
                    int cross = LaneBeyond(eastward ? a.maxX : a.minX, eastward, halfWidth);
                    int laneIn = LaneBeyond(northward ? b.minZ : b.maxZ, !northward, halfWidth);
                    points.Add(new IntVec3(centreA.x, 0, leaveZ));
                    points.Add(new IntVec3(centreA.x, 0, laneOut));
                    points.Add(new IntVec3(cross, 0, laneOut));
                    points.Add(new IntVec3(cross, 0, laneIn));
                    points.Add(new IntVec3(centreB.x, 0, laneIn));
                    points.Add(new IntVec3(centreB.x, 0, arriveZ));
                    return;
                }
                default: // **THE U-TURN.** Owner: *"u -turns"*.
                {
                    // It leaves through the wall facing AWAY from the destination, runs out to the
                    // lane on the wrong side, along a cross-lane, and comes back. A player walking
                    // it goes the wrong way first and the corridor turns them around, which is the
                    // thing the word means.
                    int wrongWayX = eastward ? a.minX - 1 : a.maxX + 1;
                    int laneAway = LaneBeyond(eastward ? a.minX : a.maxX, !eastward, halfWidth);
                    int cross = LaneBeyond(northward ? a.maxZ : a.minZ, northward, halfWidth);
                    int laneIn = LaneBeyond(eastward ? b.minX : b.maxX, !eastward, halfWidth);
                    points.Add(new IntVec3(wrongWayX, 0, centreA.z));
                    points.Add(new IntVec3(laneAway, 0, centreA.z));
                    points.Add(new IntVec3(laneAway, 0, cross));
                    points.Add(new IntVec3(laneIn, 0, cross));
                    points.Add(new IntVec3(laneIn, 0, centreB.z));
                    points.Add(new IntVec3(arriveX, 0, centreB.z));
                    return;
                }
            }
        }

        /// <summary>
        /// Waypoints into legs, with every interior end overrunning its turn so each corner is a
        /// solid block of floor.
        ///
        /// The two **termini** are not extended, because they sit one cell outside a room's wall
        /// and extending them would put corridor floor inside the room. Every other end is, for
        /// the four-directional-flood reason in <see cref="BentLegs"/>.
        ///
        /// Returns nothing at all if any consecutive pair is not a single orthogonal step. A route
        /// that is not orthogonal is not a route this carver can cut, and saying so by returning
        /// nothing is what lets the caller try the next form.
        /// </summary>
        private static List<CorridorLeg> LegsAlongWaypoints(List<IntVec3> points, int halfWidth)
        {
            var legs = new List<CorridorLeg>();
            int reach = halfWidth - 1;
            for (int index = 0; index + 1 < points.Count; index++)
            {
                IntVec3 from = points[index];
                IntVec3 to = points[index + 1];
                bool alongX = from.z == to.z;
                bool alongZ = from.x == to.x;
                if (alongX == alongZ) { legs.Clear(); return legs; }
                int start = alongX ? from.x : from.z;
                int end = alongX ? to.x : to.z;
                int step = end >= start ? 1 : -1;
                if (index != 0) { start -= step * reach; }
                if (index + 2 != points.Count) { end += step * reach; }
                int low = Math.Min(start, end);
                int high = Math.Max(start, end);
                legs.Add(alongX
                    ? LegAlongX(low, high, from.z, halfWidth)
                    : LegAlongZ(from.x, low, high, halfWidth));
            }
            return legs;
        }

        /// <summary>
        /// Whether every rect of every leg misses every room, and stays on the map.
        ///
        /// The one safety gate on a bent route. See <see cref="BentLegs"/> for why it tests the
        /// walls as strictly as the floor.
        /// </summary>
        private static bool LegsClearEveryRoom(List<CorridorLeg> legs, IReadOnlyList<RoomRecord> rooms)
        {
            // **ONE RECT AROUND THE WHOLE ROUTE FIRST.** Seven forms at two widths, each tested
            // against sixty rooms and five legs of three rects, is 12,600 overlap tests for a
            // single pair -- and this is asked once per candidate link by the braid and again by
            // both readers. The envelope answers almost every room in one test and changes no
            // verdict: a room that misses the envelope cannot touch a leg inside it.
            int minX = int.MaxValue;
            int minZ = int.MaxValue;
            int maxX = int.MinValue;
            int maxZ = int.MinValue;
            for (int index = 0; index < legs.Count; index++)
            {
                CorridorLeg leg = legs[index];
                if (!RectOnMap(leg.Floor) || !RectOnMap(leg.WallLow) || !RectOnMap(leg.WallHigh))
                { return false; }
                if (leg.WallLow.minX < minX) { minX = leg.WallLow.minX; }
                if (leg.WallLow.minZ < minZ) { minZ = leg.WallLow.minZ; }
                if (leg.WallHigh.maxX > maxX) { maxX = leg.WallHigh.maxX; }
                if (leg.WallHigh.maxZ > maxZ) { maxZ = leg.WallHigh.maxZ; }
            }
            if (legs.Count == 0) { return false; }
            CellRect envelope = CellRect.FromLimits(minX, minZ, maxX, maxZ);

            for (int other = 0; other < rooms.Count; other++)
            {
                if (rooms[other] == null) { continue; }
                CellRect bounds = rooms[other].Bounds;
                if (!envelope.Overlaps(bounds)) { continue; }
                for (int index = 0; index < legs.Count; index++)
                {
                    CorridorLeg leg = legs[index];
                    if (leg.Floor.Overlaps(bounds) || leg.WallLow.Overlaps(bounds) ||
                        leg.WallHigh.Overlaps(bounds))
                    { return false; }
                }
            }
            return true;
        }

        /// <summary>One clear cell inside the map edge, which is what the room bound check uses.</summary>
        private static bool RectOnMap(CellRect rect)
        {
            return rect.minX >= 1 && rect.minZ >= 1 &&
                rect.maxX < DestinationService.MapWidth - 1 &&
                rect.maxZ < DestinationService.MapHeight - 1;
        }

        /// <summary>
        /// The cells of a corridor that may hold a lamp or dressing: the two outermost rows of each
        /// leg's floor, never a centre line.
        ///
        /// A corridor is a route, and the reasoning that reserves a room's route cross applies to
        /// the whole of a corridor's length. Lifted out of `BuildCorridors` so the rule travels
        /// with the shape it describes.
        ///
        /// **IT TAKES THE WHOLE ROUTE, AND IT HAS TO.** At a bend, one leg's outermost floor row
        /// crosses the next leg's **centre line** — so a per-leg reading of this rule would hand
        /// the dressing a cell in the middle of the route and furnish the corner of the corridor,
        /// the exact thing the side-cell rule exists to prevent. A cell that is any other leg's
        /// floor is therefore not a side cell, whichever leg offered it.
        /// </summary>
        internal static IEnumerable<IntVec3> CorridorSideCells(List<CorridorLeg> legs)
        {
            if (legs == null) { yield break; }
            for (int index = 0; index < legs.Count; index++)
            {
                CorridorLeg leg = legs[index];
                CellRect floor = leg.Floor;
                if (leg.AlongX ? floor.Height < 3 : floor.Width < 3) { continue; }
                int from = leg.AlongX ? floor.minX : floor.minZ;
                int to = leg.AlongX ? floor.maxX : floor.maxZ;
                for (int along = from; along <= to; along++)
                {
                    IntVec3 low = leg.AlongX
                        ? new IntVec3(along, 0, floor.minZ) : new IntVec3(floor.minX, 0, along);
                    IntVec3 high = leg.AlongX
                        ? new IntVec3(along, 0, floor.maxZ) : new IntVec3(floor.maxX, 0, along);
                    if (!OnAnotherLegFloor(legs, index, low)) { yield return low; }
                    if (!OnAnotherLegFloor(legs, index, high)) { yield return high; }
                }
            }
        }

        private static bool OnAnotherLegFloor(List<CorridorLeg> legs, int skip, IntVec3 cell)
        {
            for (int index = 0; index < legs.Count; index++)
            {
                if (index == skip) { continue; }
                if (legs[index].Floor.Contains(cell)) { return true; }
            }
            return false;
        }

        private static List<RoomRecord> Build(CoordinateRecord coordinate, int candidate)
        {
            bool fallback = candidate == FallbackCandidate;
            int seed = DestinationService.StableHash(coordinate.Seed, coordinate.Id + ":rooms:" + candidate,
                PlannerVersion + coordinate.GeneratorVersion + DestinationService.GetRoomLibraryVersion(coordinate));
            int depth = fallback ? 1 : Math.Max(1, coordinate.Depth);
            int slots = SlotsPerAxis(depth);
            int spacing = SlotSpacing(slots);
            int span = SlotRoomSpan(spacing);

            // The serpentine, kept for the FALLBACK CANDIDATE ONLY: row-major with alternating
            // direction, so consecutive entries are always grid neighbours. It is the layout
            // taken when all three real candidates are refused, and the thing you fall back to
            // should be the thing with the fewest ways to be surprising.
            var order = new List<IntVec2>();
            for (int row = 0; row < slots; row++)
            {
                for (int column = 0; column < slots; column++)
                {
                    int x = row % 2 == 0 ? column : slots - 1 - column;
                    order.Add(new IntVec2(x, row));
                }
            }

            if (fallback) { return BuildSerpentine(coordinate, order, spacing, seed, depth); }
            return BuildMaze(coordinate, slots, spacing, seed, depth);
        }

        /// <summary>How many adjacent pairs the maze walk left unlinked get linked back.</summary>
        internal const int BraidRarity = 3;

        /// <summary>
        /// A randomised depth-first maze over the slot grid, grown from the hall, then braided.
        ///
        /// ## What this replaced, and the owner described it exactly
        ///
        /// *"all the backrooms so far are just one lone strain of perals arangement that snakes
        /// back and forth across the map like one series line... i want them to be mazes like
        /// xcrazy like all levels mazes do you unerstand!"*
        ///
        /// The spine was a **serpentine**: the slot grid walked row-major with alternating
        /// direction, room N linked to room N-1. One line that snakes back and forth, by
        /// construction and by its own comment. Dead ends were hung off it afterwards, so the
        /// topology was a corridor with alcoves -- which reads as a single route however many
        /// rooms it has, because it is one.
        ///
        /// ## Why a depth-first maze, and why braided
        ///
        /// The carve order at each slot is rotated by that slot's own hash, so the walk turns
        /// unpredictably instead of sweeping, and it branches everywhere. Every visited slot links
        /// to the slot the walk arrived from, so the result is a **spanning tree** -- connected by
        /// construction, which is exactly what `CandidateIsSafe` has to prove, with no
        /// pathfinding anywhere in the planner.
        ///
        /// **Then the braid, which is what makes it a maze rather than a tree.** A pure tree has
        /// exactly one route between any two rooms: walk it wrong and you backtrack. Linking back
        /// one in <see cref="BraidRarity"/> of the adjacent pairs the walk left alone gives loops,
        /// junctions that lie, and corridors that rejoin somewhere unexpected.
        ///
        /// ## The invariant this is built to respect
        ///
        /// **Every link is between grid-adjacent slots.** `AreGridNeighbors` requires linked
        /// rooms' centres to share a row or a column, and `BuildCorridors` carves straight between
        /// those centres. A maze over the SLOT GRID satisfies that for free -- which is why the
        /// maze is over slots and not over cells.
        ///
        /// Deterministic throughout: every choice comes from `DestinationService.StableHash` over
        /// the coordinate's own seed, so a level is the same maze every time it is visited.
        /// </summary>
        private static List<RoomRecord> BuildMaze(CoordinateRecord coordinate, int slots,
            int spacing, int seed, int depth)
        {
            var rooms = new List<RoomRecord>();
            // **THE GRAND HALL YOU ARRIVE IN, AND THEN THE MAZE.** Owner: *"the normal yellow
            // backrooms look isnt the whole floor but the main spanw room"*. The threshold takes
            // TWO adjacent slots, so at depth 1 it is about eighty cells across while everything
            // past it is a third of that.
            // **WHERE THE HALL IS, DRAWN FROM THE SEED.** Owner, 2026-10-03, verbatim: *"and
            // starting room is not to always be in bottom left of map, starts locations of main
            // grand rooms can be anywhere on the map and lead anywhere in multiple differetn
            // varied ways"*.
            //
            // This was `new IntVec2(0, 0)` and `new IntVec2(1, 0)` -- **two literals**, and
            // `SlotCenter(0)` is `Margin + spacing / 2`, the lowest cell on both axes. So every
            // coordinate this mod has ever generated opened in the same corner, and the owner
            // walked enough of them to notice.
            //
            // **The orientation is drawn too, and that costs nothing**: `MakeHall` has always
            // asked `first.z == second.z` and swapped its long and short spans accordingly, so a
            // vertical hall was supported and had simply never been reachable. `WidestRoomSpan`
            // is unaffected either way -- it is the max of the two spans, and the long span is
            // the same number in both orientations.
            //
            // Clamped so the second slot is on the grid, and derived from the coordinate's own
            // seed like every other generated property, so a revisit is the same place.
            int hallDraw = DestinationService.StableHash(seed, "hall:slot", depth);
            if (hallDraw < 0) { hallDraw = ~hallDraw; }
            bool hallHorizontal = (hallDraw / 7) % 2 == 0;
            int hallSpanX = hallHorizontal ? 2 : 1;
            int hallSpanZ = hallHorizontal ? 1 : 2;
            var hallFirst = new IntVec2(
                hallDraw % Math.Max(1, slots - hallSpanX + 1),
                (hallDraw / 13) % Math.Max(1, slots - hallSpanZ + 1));
            var hallSecond = new IntVec2(
                hallFirst.x + (hallHorizontal ? 1 : 0),
                hallFirst.z + (hallHorizontal ? 0 : 1));
            rooms.Add(MakeHall(coordinate, hallFirst, hallSecond, spacing, seed, depth));

            // slotOf[slot] is the room index standing in it, or absent.
            var slotOf = new Dictionary<IntVec2, int> { { hallFirst, 0 }, { hallSecond, 0 } };
            var hops = new Dictionary<int, int> { { 0, 0 } };

            // The walk. An explicit stack rather than recursion: a ten-by-ten grid is a hundred
            // frames deep in the worst case and this runs during map generation.
            // **THE WALK GROWS FROM BOTH HALVES OF THE HALL, and it has to.**
            //
            // This was `{ hallSecond }` alone, which worked only because the hall was pinned to
            // slots (0,0)-(1,0). The moment the hall could be anywhere, **1.5% of seeds produced
            // a one-room level** -- caught by `check-planner-layouts.py` reporting
            // `RR_Generation_InvalidRoomGraph -- 1 rooms` and the `fellback` column rising from 0,
            // which then handed those seeds the serpentine: a string of pearls, the exact defect
            // being fixed.
            //
            // The cause is the hall's geometry. Its centre sits BETWEEN its two slot centres, so
            // `AreNeighbourRooms` -- which demands linked centres share a row or a column --
            // declines every step off the hall's own axis. A horizontal hall landing in the last
            // two columns leaves `hallSecond` with no legal step at all: east is off the grid,
            // west is the hall itself, and north and south are declined. The walk ends with one
            // room.
            //
            // Pushing both halves fixes it without clamping the hall away from the edges, which
            // would have reintroduced a positional bias -- the opposite of what was asked. And it
            // is the better shape regardless: owner, 2026-10-03, *"starts locations of main grand
            // rooms can be anywhere on the map and lead anywhere in multiple differetn varied
            // ways"*. A grand hall should lead out of both its ends.
            // **THE SEALED SLOTS, CHOSEN BEFORE THE WALK SO THE WALK CANNOT ENTER THEM.** Owner:
            // *"insentive to mine things out to find isolated undiscorvered rooms"*. A vault has to
            // be unreachable by corridor, and the cheapest way to guarantee that is to make the
            // walk and both braids blind to the slot — nothing can link to a slot that was never
            // in `slotOf` when the links were made. The room goes in afterwards.
            //
            // They double as obstacles while the walk is running, which is free maze quality: a
            // blocked slot forces the walk around it. If enough of them blocked the walk into a
            // level too small to be legal, `ValidateRooms` refuses the candidate and the next one
            // is tried — it fails closed, and `fellback` in `check-planner-layouts.py` is where
            // that would show.
            var sealedSlots = new List<IntVec2>();
            int sealedTarget = SealedRoomCount(slots);
            for (int attempt = 0; attempt < slots * slots && sealedSlots.Count < sealedTarget; attempt++)
            {
                int draw = DestinationService.StableHash(seed, "sealed:" + attempt, depth);
                if (draw < 0) { draw = ~draw; }
                var reserved = new IntVec2(draw % slots, (draw / 31) % slots);
                if (slotOf.ContainsKey(reserved) || sealedSlots.Contains(reserved)) { continue; }
                sealedSlots.Add(reserved);
            }

            // The arrival hall is grand room one; the walk may make up to
            // `GrandRoomsPerLevel(depth) - 1` more.
            int grandRooms = 1;
            var stack = new List<IntVec2> { hallFirst, hallSecond };
            IntVec2[] directions =
            {
                new IntVec2(1, 0), new IntVec2(0, 1), new IntVec2(-1, 0), new IntVec2(0, -1),
            };
            // **THE VAULTS ARE TAKEN OUT OF THE BUDGET, NOT LEFT TO COMPETE FOR IT.** The walk is
            // bounded by `MaxRooms` and from depth 3 onward it reaches that bound, so a vault
            // appended afterwards was silently dropped every time -- `deg0` read 0.0% at depth 3
            // and deeper while the slots had been reserved and the rock left standing. Measured,
            // not reasoned about: the probe printed the zero.
            int budget = Math.Max(1, MaxRooms - sealedSlots.Count);

            while (stack.Count > 0 && rooms.Count < budget)
            {
                IntVec2 current = stack[stack.Count - 1];
                // The rotation is what stops this being a sweep. Taken from the slot itself, so
                // the same coordinate always turns the same way.
                int turn = DestinationService.StableHash(seed,
                    "maze:" + current.x + "," + current.z, depth);
                if (turn < 0) { turn = ~turn; }

                bool advanced = false;
                for (int step = 0; step < directions.Length; step++)
                {
                    IntVec2 direction = directions[(turn + step) % directions.Length];
                    var next = new IntVec2(current.x + direction.x, current.z + direction.z);
                    if (next.x < 0 || next.z < 0 || next.x >= slots || next.z >= slots) { continue; }
                    if (slotOf.ContainsKey(next) || sealedSlots.Contains(next)) { continue; }

                    int parent = slotOf[current];

                    // **MORE THAN ONE GRAND ROOM, AND THEY ARE MADE *INSIDE* THE WALK.** Owner,
                    // 2026-10-03: *"starts locations of main grand rooms can be anywhere on the
                    // map and lead anywhere in multiple differetn varied ways"* -- plural.
                    //
                    // Placed here rather than seeded alongside the hall before the walk, and the
                    // reason is connectivity. The walk skips any slot already in `slotOf`, so two
                    // independent seeds can never merge: their components stay separate, and
                    // `ValidateRooms` refuses a disconnected graph, which hands the seed the
                    // fallback serpentine -- *"one lone strain of perals"*, the exact defect being
                    // fixed. The braid that follows only links one adjacent pair in three, so it
                    // cannot be relied on to join them either.
                    //
                    // Made as the walk steps into the slot, the grand room is linked to its parent
                    // **by construction**, and it passes through the same two legality gates below
                    // as any other room. If its geometry breaks the link -- which a two-slot
                    // centre can, exactly as the hall's does -- the whole step is declined and the
                    // slot is reached later from a different parent.
                    IntVec2 grandSecond = IntVec2.Invalid;
                    RoomRecord room = null;
                    if (grandRooms < GrandRoomsPerLevel(depth) && GrandRoomHere(seed, next, depth))
                    {
                        // Extended along the direction of travel, so a grand room always lies
                        // across the way the walk was already going and reads as a space opening
                        // up rather than as a room that happens to be wide.
                        var beyond = new IntVec2(next.x + direction.x, next.z + direction.z);
                        bool roomy = beyond.x >= 0 && beyond.z >= 0 && beyond.x < slots
                            && beyond.z < slots && !slotOf.ContainsKey(beyond)
                            && !sealedSlots.Contains(beyond);
                        if (roomy)
                        {
                            grandSecond = beyond;
                            // The same placeholder family every other maze room gets, so
                            // `AssignMazeFamilies` treats a grand room exactly as it treats the
                            // rest. Naming a family here would both duplicate that pass's
                            // decisions and risk minting a second room of a family something
                            // downstream expects exactly one of.
                            room = MakeGrandRoom(coordinate, rooms.Count, "survey_lobby",
                                next, beyond, spacing);
                        }
                    }
                    if (room == null)
                    {
                        grandSecond = IntVec2.Invalid;
                        room = MakeRoom(coordinate, rooms.Count, "survey_lobby", next, spacing,
                            VariedRoomSpan(spacing, next, seed, depth), seed, false, depth);
                    }
                    // **THE SAME QUESTION `ValidateRooms` WILL ASK.** `AreGridNeighbors` requires
                    // a linked pair's centres to share a row or a column, because `BuildCorridors`
                    // carves straight between them. The hall spans two slots, so its centre sits
                    // BETWEEN them -- 58 at depth 1, which is no slot's centre -- and a step from
                    // the hall in any direction but along its own row produces a link the
                    // validator refuses. **That one link made every maze candidate illegal**, and
                    // the fallback serpentine quietly caught every seed while the probe reported
                    // no refusals at all.
                    //
                    // Declined rather than forced: the slot stays unvisited and is reached later
                    // from a different parent, which is a thing a maze can do and a line cannot.
                    if (!AreNeighbourRooms(rooms[parent], room)) { continue; }
                    // **AND THE ROUTE HAS TO EXIST, not merely be a legal shape.** The walk builds
                    // the spanning tree, so a tree edge with no corridor under it is a level that
                    // cannot be carved -- and `PruneUnroutableLinks` deliberately refuses to touch
                    // a non-diagonal link, because taking one away is what would disconnect the
                    // place. Asking here is what makes that refusal safe.
                    if (CorridorLegs(rooms[parent], room, depth, rooms).Count == 0 &&
                        !SharesWall(rooms[parent], room))
                    { continue; }
                    rooms.Add(room);
                    slotOf[next] = room.index;
                    hops[room.index] = hops[parent] + 1;
                    Link(rooms, room.index, parent);
                    stack.Add(next);
                    if (grandSecond.IsValid)
                    {
                        // **BOTH SLOTS, AND BOTH ENDS ON THE STACK.** Claiming only the first
                        // would let the walk place a second room inside this one's footprint;
                        // pushing only the first is what pinned the old hall to leading out of one
                        // row, which is the half of *"lead anywhere in multiple differetn varied
                        // ways"* that a grand room exists to answer.
                        slotOf[grandSecond] = room.index;
                        stack.Add(grandSecond);
                        grandRooms++;
                    }
                    advanced = true;
                    break;
                }
                if (!advanced) { stack.RemoveAt(stack.Count - 1); }
            }

            // **THE BRAID.** Adjacent rooms the walk left unconnected, linked back one in three.
            // Without this the maze is a tree and there is exactly one route between any two
            // rooms; with it there are loops and junctions that lie. Ordered by slot so the set
            // of braids is the same on every visit.
            var slotList = new List<IntVec2>(slotOf.Keys);
            slotList.Sort(delegate (IntVec2 left, IntVec2 right)
            {
                if (left.z != right.z) { return left.z - right.z; }
                return left.x - right.x;
            });
            for (int index = 0; index < slotList.Count; index++)
            {
                IntVec2 slot = slotList[index];
                int here = slotOf[slot];
                // East and north only: every pair is then considered exactly once.
                for (int side = 0; side < 2; side++)
                {
                    var next = side == 0
                        ? new IntVec2(slot.x + 1, slot.z) : new IntVec2(slot.x, slot.z + 1);
                    int there;
                    if (!slotOf.TryGetValue(next, out there) || there == here) { continue; }
                    if (rooms[here].links.Contains(there)) { continue; }
                    int roll = DestinationService.StableHash(seed,
                        "braid:" + slot.x + "," + slot.z + ":" + side, depth);
                    if (roll < 0) { roll = ~roll; }
                    if (!SlotIsJunction(seed, slot, depth) && roll % BraidRarity != 0) { continue; }
                    // The corridor builder needs the two centres to share an axis, which the
                    // hall's two-slot span can break. `AreNeighbourRooms` is the same question
                    // `ValidateRooms` will ask, so a braid it would refuse is never made.
                    if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }
                    Link(rooms, here, there);
                }
            }

            // **THE NEIGHBOURHOOD: a block of rooms wall to wall off one hub, formed WHILE
            // THE ROOMS CAN STILL MOVE.** Owner, same
            // direction, *"neighborrs hood"*, and from the vein direction *"so u can find back to
            // back rooms"*.
            //
            // The push loop above rolls per room independently, so back-to-back pairs are scattered
            // -- measured at 190 to 310 per depth, and not one of them is a *block*. A
            // neighbourhood is a cluster: several rooms pressed against one hub so they share walls
            // with it and sit a single doorway apart, which is what a terrace of houses off a
            // street actually is.
            //
            // Every move still goes through `PushAgainst`, so every move still has to satisfy all
            // four of its conditions or be undone -- on the map, nothing overlapped, no existing
            // link's route or shape broken, and `SharesWall` agreeing afterwards. **This chooses
            // which rooms to offer; it relaxes nothing.**
            //
            // **AND IT RUNS HERE, BEFORE THE DIAGONAL AND REACH BRAIDS, WHICH THE PROBE INSISTED
            // ON.** Written after them it measured as a no-op: the largest wall-to-wall group came
            // out at 3 with it and 3 without. A room holding five or six links cannot slide at
            // all, because `PushAgainst` undoes any move that carries one of them past
            // `FurthestLinkedCentres` -- so by the time a hub was picked, nothing around it was
            // mobile. At this point a room holds about two and a half links and a push lands; the
            // braids that follow route to where the rooms ended up. That is the right order
            // anyway, because the arrangement is part of the layout rather than a nudge applied to
            // a finished one.
            int blockDraw = DestinationService.StableHash(seed, "neighbourhood:hub", depth);
            if (blockDraw < 0) { blockDraw = ~blockDraw; }
            var hubSlot = new IntVec2(blockDraw % slots, (blockDraw / 11) % slots);
            int hub;
            if (slotOf.TryGetValue(hubSlot, out hub) && hub != 0 && rooms[hub].links != null)
            {
                // Its own linked neighbours only. Pressing an unlinked room against the hub would
                // make two rooms share a wall with no doorway in it, which is a sealed pair rather
                // than a terrace.
                // **LEAST-CONNECTED FIRST.** `PushAgainst` undoes a move that breaks an
                // existing link's route or carries one past `FurthestLinkedCentres`, and a move is
                // most of a room's own span -- so the more links a room holds the likelier it is
                // to snap straight back. Offered in whatever order the link list happened to be
                // in, the hopeless ones shifted the geometry before the mobile ones were tried.
                var terrace = new List<RoomRecord>();
                for (int index = 0; index < rooms[hub].links.Count; index++)
                {
                    int neighbour = rooms[hub].links[index];
                    if (neighbour == 0 || neighbour == hub) { continue; }
                    RoomRecord mover = rooms.FirstOrDefault(r => r != null && r.index == neighbour);
                    if (mover == null || mover.links == null || SharesWall(mover, rooms[hub]))
                    { continue; }
                    terrace.Add(mover);
                }
                terrace.Sort((left, right) => left.links.Count != right.links.Count
                    ? left.links.Count - right.links.Count
                    : left.index - right.index);
                for (int index = 0; index < terrace.Count; index++)
                { PushAgainst(rooms, terrace[index], rooms[hub], depth); }
            }

            // **THE DIAGONAL BRAID, AND IT IS WHAT ANSWERS THE DEGREE COMPLAINT.** Owner,
            // 2026-10-03: *"room connected to like 0 - 10 other rooms"* and *"multiple coices on
            // directions to take in every rooms"*. Measured before this existed: average degree
            // **2.2 to 2.4**, maximum **4**, at every depth -- one way in and one way out, which
            // is a line with rooms on it however the walk turned.
            //
            // The ceiling was geometric rather than a tuning: a link had to join grid-adjacent
            // slots because the carver ran along one axis, so four neighbours was all a slot had.
            // `BentLegs` lifted that, so the four DIAGONAL neighbours are reachable too and the
            // ceiling is eight.
            //
            // North-east and south-east only, so each diagonal pair is considered exactly once --
            // the same reason the orthogonal braid above takes east and north alone.
            //
            // **Routability is asked here as well as proved later.** A diagonal whose lane is
            // blocked by a wide room gets no link rather than a link that the prune pass has to
            // take back, which keeps the family assignment below reading a graph that is already
            // settled. The prune is still the authority, because `ShapeDepthOf` shifts as links
            // are added and the readers compute the route from the finished graph.
            for (int index = 0; index < slotList.Count; index++)
            {
                IntVec2 slot = slotList[index];
                int here = slotOf[slot];
                for (int side = 0; side < 2; side++)
                {
                    var next = side == 0
                        ? new IntVec2(slot.x + 1, slot.z + 1)
                        : new IntVec2(slot.x + 1, slot.z - 1);
                    int there;
                    if (!slotOf.TryGetValue(next, out there) || there == here) { continue; }
                    if (rooms[here].links.Contains(there)) { continue; }
                    int roll = DestinationService.StableHash(seed,
                        "diagonal:" + slot.x + "," + slot.z + ":" + side, depth);
                    if (roll < 0) { roll = ~roll; }
                    if (!SlotIsJunction(seed, slot, depth) && roll % DiagonalBraidRarity != 0)
                    { continue; }
                    if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }
                    if (CorridorLegs(rooms[here], rooms[there], depth, rooms).Count == 0) { continue; }
                    Link(rooms, here, there);
                }
            }

            // **THE REACH BRAID: links to a slot TWO AWAY, which is what passes eight.** Owner,
            // 2026-10-03, answering the degree-ceiling fork: *"it shouldnt just be one option
            // there needs to be wide varying variations of all types so dont limit yourself"*.
            //
            // A diagonal lifts the ceiling from four to eight and no further, because eight is all
            // the neighbours a slot has. The five-leg route forms in `BentLegs` go out to a lane,
            // across a cross-lane and back down another, so they arrive at a slot the pair are not
            // adjacent to at all -- and that is the only thing that reaches the owner's ten.
            //
            // **Deliberately rare.** A long corridor costs rock, and a floor where every room
            // reaches every room two away is an open plan rather than a maze. `ReachBraidRarity`
            // is higher than either braid above it, so these read as the odd long run that goes
            // somewhere unexpected -- which is what they are for.
            //
            // Every offset with a span of two, each considered once from the lower-left of the
            // pair, so no pair is offered twice.
            IntVec2[] reaches =
            {
                new IntVec2(2, 0), new IntVec2(0, 2), new IntVec2(2, 1), new IntVec2(2, -1),
                new IntVec2(1, 2), new IntVec2(-1, 2), new IntVec2(2, 2), new IntVec2(2, -2),
            };
            for (int index = 0; index < slotList.Count; index++)
            {
                IntVec2 slot = slotList[index];
                int here = slotOf[slot];
                for (int side = 0; side < reaches.Length; side++)
                {
                    var next = new IntVec2(slot.x + reaches[side].x, slot.z + reaches[side].z);
                    int there;
                    if (!slotOf.TryGetValue(next, out there) || there == here) { continue; }
                    if (rooms[here].links.Contains(there)) { continue; }
                    int roll = DestinationService.StableHash(seed,
                        "reach:" + slot.x + "," + slot.z + ":" + side, depth);
                    if (roll < 0) { roll = ~roll; }
                    if (roll % ReachBraidRarity != 0) { continue; }
                    if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }
                    if (CorridorLegs(rooms[here], rooms[there], depth, rooms).Count == 0) { continue; }
                    Link(rooms, here, there);
                }
            }

            // **THERE IS NO ROAD BRAID, AND THAT IS A MEASUREMENT RATHER THAN AN OMISSION.**
            // Owner, 2026-10-03: *"so its more rooma corradors facilites infastructure roads
            // neighborrs hood malls shoopping centers military"*.
            //
            // One was written here -- pick a row or column, link every occupied slot along it --
            // and the probe was taught to report the longest straight run of linked rooms before
            // and after it. **The numbers were identical: 6 to 8 either way, which at depth 3 and
            // deeper is the entire slot row.** At an average of five links per room the braids
            // already join almost every adjacent collinear pair, so a line across the level exists
            // by arithmetic and forcing one adds nothing. Deleted rather than kept as insurance: a
            // pass whose effect nobody can measure is a pass nobody can defend.
            //
            // **What was missing was never the run. It was that the run did not LOOK like a
            // road.** Every corridor along it was whatever width its own pair rolled, so a
            // through-line read as a chain of ordinary hallways. `OnRoad` is the answer and it is
            // a question about the finished graph: a corridor whose straight run carries on past
            // either end is always cut at the wide half-width. See `CorridorHalfWidthBetween`.

            AssignMazeFamilies(rooms, hops, seed);

            // **THE VAULTS GO IN AFTER EVERY LINK HAS BEEN MADE**, which is what makes them
            // sealed: nothing can have linked to a slot that was not in `slotOf` while the walk
            // and the braids were running, and nothing links to anything afterwards.
            //
            // Their family is set here rather than by `AssignMazeFamilies`, which decides by link
            // count and would read a vault as a dead end and hand it a spur family -- and
            // `CandidateIsSafe` asserts a spur family has exactly one link.
            for (int index = 0; index < sealedSlots.Count && rooms.Count < MaxRooms; index++)
            {
                IntVec2 slot = sealedSlots[index];
                RoomRecord vault = MakeRoom(coordinate, rooms.Count, SealedFamily, slot, spacing,
                    VariedRoomSpan(spacing, slot, seed, depth), seed, false, depth);
                // A reserved slot is nobody else's, but `Derange` can widen a vault past its own
                // slot and a neighbour can have been widened toward it. An overlap is refused by
                // `ValidateRooms` outright, so the vault is simply not placed.
                if (rooms.Any(other => other != null && other.Bounds.Overlaps(vault.Bounds)))
                { continue; }
                rooms.Add(vault);
            }

            // **BACK TO BACK, AND NO LONGER ONLY A DEAD END.** Owner: *"and you can have back to
            // back roomes"*, and again on 2026-10-03 *"so u can find back to back rooms"*.
            //
            // This was restricted to rooms with exactly one link, on the reasoning that *"a room
            // with one link cannot re-route anything by moving"* -- true, and it was the only
            // guarantee available while nothing checked whether a move broke somebody's corridor.
            // **The degree work then made the restriction bite**: with an average of five links a
            // level has few dead ends left, and the measured back-to-back count fell from 131 to
            // 23. A feature the owner asked for twice was quietly shrinking as a side effect of a
            // different feature, which the probe printed and nobody would otherwise have seen.
            //
            // `PushAgainst` now proves the move itself: on the map, no room overlapped, **no
            // existing route broken**, and the two rooms really share a wall afterwards -- or it
            // is undone. That holds whatever the link count is, so the link count stops being the
            // condition and the push is offered to every room.
            for (int index = 1; index < rooms.Count; index++)
            {
                if (rooms[index].links.Count < 1) { continue; }
                int roll = DestinationService.StableHash(seed,
                    "backtoback:" + rooms[index].x + "," + rooms[index].z, depth);
                if (roll < 0) { roll = ~roll; }
                if (roll % 3 != 0) { continue; }
                // Which neighbour it goes wall to wall with is drawn too, so a well-connected
                // room is not always pushed against the first link it happens to hold.
                int host = rooms[index].links[(roll / 7) % rooms[index].links.Count];
                if (host == 0) { continue; }
                PushAgainst(rooms, rooms[index], rooms[host], depth);
            }

            PruneUnroutableLinks(rooms, depth);
            return rooms;
        }

        /// <summary>
        /// One slot in this many is a **junction**, and takes every link it can rather than rolling
        /// for each.
        ///
        /// Owner: *"multiple coices on directions to take in every rooms"* and *"room connected to
        /// like 0 - 10 other rooms"*. A single braid rarity moves every room to the same new
        /// average and leaves the *range* as narrow as it was; what the owner asked for is a
        /// spread. A junction slot is the top of it — four orthogonal neighbours and four
        /// diagonals, so eight ways out of one room — and a vault is the bottom, at none.
        /// </summary>
        internal const int JunctionRarity = 8;

        /// <summary>Whether this slot takes every link available to it. See <see cref="JunctionRarity"/>.</summary>
        private static bool SlotIsJunction(int seed, IntVec2 slot, int depth)
        {
            int roll = DestinationService.StableHash(seed, "junction:" + slot.x + "," + slot.z, depth);
            if (roll < 0) { roll = ~roll; }
            return roll % JunctionRarity == 0;
        }

        /// <summary>
        /// How many sealed vaults a coordinate carries, scaled to the slot grid so a deep level
        /// with a hundred slots hides more than a shallow one with thirty-six.
        ///
        /// Always at least one, because *"isolated undiscorvered rooms"* with none of them is the
        /// feature not existing.
        /// </summary>
        internal static int SealedRoomCount(int slots)
        {
            int count = slots * slots / 25;
            return count < 1 ? 1 : count;
        }

        /// <summary>How many of the diagonal pairs the walk left alone are linked back.</summary>
        /// <remarks>
        /// At 2, about half of them. A maze needs walls as much as it needs junctions: link every
        /// diagonal and the floor becomes an open plan with pillars in it, which reads no more
        /// like a maze than a single line does. Half gives junctions that offer a real choice and
        /// leaves enough rock standing to get lost in -- and it leaves the **spread** that
        /// *"0 - 10 other rooms"* asks for, rather than moving every room to the same new number.
        /// </remarks>
        internal const int DiagonalBraidRarity = 2;

        /// <summary>
        /// How rare a link to a slot **two away** is. See the reach braid in <see cref="BuildMaze"/>.
        /// </summary>
        /// <remarks>
        /// Higher than either braid above it on purpose. A five-leg route is a long corridor and
        /// costs rock the rooms could have had; a floor where every room reaches every room two
        /// away is an open plan with pillars in it. At one in five these read as the occasional
        /// long run that arrives somewhere you did not expect, which is the whole point of them.
        /// </remarks>
        internal const int ReachBraidRarity = 5;

        /// <summary>
        /// **NO GRAPH EDGE MAY STAND WITHOUT A ROUTE UNDERNEATH IT**, and this is what guarantees
        /// it after every room has stopped moving.
        ///
        /// A diagonal link is routed through the rock lane between its two rooms, and two things
        /// decided after the braid can take that lane away: `PushAgainst` slides a dead-end room
        /// out of its slot and into somebody's lane, and `ShapeDepthOf` shifts as links are added,
        /// which changes the width the pair asks for. So the braid's routability test is a
        /// courtesy and **this is the authority** — it runs last, against the finished geometry,
        /// and asks exactly the question `CandidateIsSafe` and `BuildCorridors` will ask.
        ///
        /// **It can only ever remove a diagonal, so it cannot disconnect the level.** Every
        /// orthogonal pair either shares a wall, in which case the doorway is the route, or has a
        /// straight run between its centres by construction; the spanning tree the walk built is
        /// entirely orthogonal. Diagonals exist only on top of it.
        ///
        /// A room that loses its last diagonal is simply a room with fewer ways out. It keeps the
        /// family it was given, which is deliberate: `CandidateIsSafe` asserts that a
        /// `storage_nook` or `utility_room` **has** one link, not that a one-link room must be one
        /// of those.
        /// </summary>
        private static void PruneUnroutableLinks(List<RoomRecord> rooms, int depth)
        {
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null || room.links == null) { continue; }
                for (int at = room.links.Count - 1; at >= 0; at--)
                {
                    int otherIndex = room.links[at];
                    if (otherIndex <= room.index) { continue; }
                    RoomRecord other = rooms.FirstOrDefault(r => r != null && r.index == otherIndex);
                    if (other == null || SharesWall(room, other)) { continue; }
                    int legDepth = Math.Max(ShapeDepthOf(rooms, room, depth),
                        ShapeDepthOf(rooms, other, depth));
                    if (CorridorLegs(room, other, legDepth, rooms).Count > 0) { continue; }
                    // **TAKEN OUT, THEN PUT BACK IF THE PLACE FELL APART.** This refused to touch
                    // anything whose centres shared an axis, on the reasoning that the spanning
                    // tree is entirely non-diagonal so removing only diagonals cannot disconnect
                    // the level. True, and too coarse: the reach braid makes links two slots apart
                    // ALONG an axis, and the neighbourhood push can leave one of those with no
                    // route. The clause skipped it, `CandidateIsSafe` then refused the whole
                    // layout, and the probe printed `link 2-6 has no route under it`.
                    //
                    // Asking directly is exact and easier to reason about: remove the edge, and
                    // keep the removal only if every room still claiming a route can still be
                    // reached from the threshold. A load-bearing link stays and the candidate is
                    // refused -- which is correct, and the next candidate answers it.
                    room.links.RemoveAt(at);
                    other.links.Remove(room.index);
                    if (LinkedGraphIsWhole(rooms)) { continue; }
                    room.links.Insert(at > room.links.Count ? room.links.Count : at, otherIndex);
                    other.links.Add(room.index);
                }
            }
        }

        /// <summary>
        /// Whether every room that claims a route can still be reached from the threshold.
        ///
        /// The same question `DestinationService.ValidateRooms` asks of a saved graph, asked here
        /// of one being built, so a removal cannot produce a layout the validator would refuse. A
        /// room with no links is a sealed vault and is deliberately not expected to be reachable
        /// across floor -- see <see cref="SealedFamily"/>.
        /// </summary>
        private static bool LinkedGraphIsWhole(List<RoomRecord> rooms)
        {
            var byIndex = new Dictionary<int, RoomRecord>();
            for (int index = 0; index < rooms.Count; index++)
            {
                if (rooms[index] != null) { byIndex[rooms[index].index] = rooms[index]; }
            }
            if (!byIndex.ContainsKey(0)) { return false; }
            var seen = new HashSet<int> { 0 };
            var pending = new Queue<int>();
            pending.Enqueue(0);
            while (pending.Count > 0)
            {
                RoomRecord current;
                if (!byIndex.TryGetValue(pending.Dequeue(), out current) || current.links == null)
                { continue; }
                for (int index = 0; index < current.links.Count; index++)
                {
                    if (seen.Add(current.links[index])) { pending.Enqueue(current.links[index]); }
                }
            }
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null || room.links == null || room.links.Count == 0) { continue; }
                if (!seen.Contains(room.index)) { return false; }
            }
            return true;
        }

        /// Who each room is, once the maze exists.
        ///
        /// The three unique families are unique because something depends on there being exactly
        /// one: the gate anchor, the evidence book, and the way out. `ValidateRooms` refuses a
        /// graph that has two of any of them or none of `service_passage`.
        ///
        /// **The way home is the deepest room the walk reached**, which in a maze is a genuinely
        /// distant place rather than the end of a line. **Every dead end becomes a storage nook or
        /// a utility room**, because a maze has dead ends in quantity and that is precisely what
        /// those two families are -- and `CandidateIsSafe` asserts both of them have exactly one
        /// link, which a dead end does by definition.
        /// </summary>
        private static void AssignMazeFamilies(List<RoomRecord> rooms, Dictionary<int, int> hops,
            int seed)
        {
            rooms[0].familyId = UniqueFamilies[0];
            if (rooms.Count < 2) { return; }

            int deepest = 1;
            for (int index = 1; index < rooms.Count; index++)
            {
                int far;
                int best;
                if (!hops.TryGetValue(index, out far)) { continue; }
                if (!hops.TryGetValue(deepest, out best) || far > best) { deepest = index; }
            }

            // The office copy is never the way home and never the hall, and it is a room with
            // more than one link where one exists: the evidence book should be somewhere a crew
            // passes through rather than at the end of a cul-de-sac.
            int office = -1;
            for (int offset = 0; offset < rooms.Count; offset++)
            {
                int index = 1 + (Math.Abs(seed / 23) + offset) % Math.Max(1, rooms.Count - 1);
                if (index == deepest || rooms[index].links.Count < 2) { continue; }
                office = index;
                break;
            }
            if (office < 0) { office = deepest == 1 && rooms.Count > 2 ? 2 : 1; }

            for (int index = 1; index < rooms.Count; index++)
            {
                if (index == deepest) { rooms[index].familyId = UniqueFamilies[2]; continue; }
                if (index == office) { rooms[index].familyId = UniqueFamilies[1]; continue; }
                if (rooms[index].links.Count == 1)
                {
                    rooms[index].familyId = SpurFamilies[index % SpurFamilies.Length];
                    continue;
                }
                rooms[index].familyId = ChainFamilies[Math.Abs(seed / 7 + index) % ChainFamilies.Length];
            }

            // `service_passage` must appear at least once: the generator's climate room is
            // FirstOrDefault(utility_room) ?? First(service_passage), and the second half of that
            // throws when there is none. `ValidateRooms` refuses the graph as well.
            bool hasPassage = false;
            for (int index = 0; index < rooms.Count; index++)
            {
                if (rooms[index].familyId == "service_passage") { hasPassage = true; break; }
            }
            if (hasPassage) { return; }
            for (int index = 1; index < rooms.Count; index++)
            {
                if (index == deepest || index == office || rooms[index].links.Count == 1) { continue; }
                rooms[index].familyId = "service_passage";
                return;
            }
            // A maze of nothing but dead ends and two unique rooms is not a maze this can happen
            // to at any depth the planner produces, but if it ever did, the passage has to exist.
            for (int index = 1; index < rooms.Count; index++)
            {
                if (index == deepest || index == office) { continue; }
                rooms[index].familyId = "service_passage";
                return;
            }
        }

        /// <summary>
        /// The old serpentine, kept for the fallback candidate alone. See <see cref="BuildMaze"/>
        /// for why it is no longer what a level looks like.
        /// </summary>
        private static List<RoomRecord> BuildSerpentine(CoordinateRecord coordinate,
            List<IntVec2> order, int spacing, int seed, int depth)
        {
            int chainLength = MinSlotsPerAxis * MinSlotsPerAxis * 2 / 3;
            if (chainLength < 6) { chainLength = 6; }
            if (chainLength > MaxRooms * 2 / 3) { chainLength = MaxRooms * 2 / 3; }
            if (chainLength > order.Count) { chainLength = order.Count; }

            var rooms = new List<RoomRecord>();
            var taken = new HashSet<IntVec2>();
            for (int index = 0; index < order.Count && rooms.Count < chainLength; index++)
            {
                IntVec2 slot = order[index];
                if (!taken.Add(slot)) { continue; }
                string family = ChainFamilyFor(rooms.Count, chainLength, seed);
                rooms.Add(MakeRoom(coordinate, rooms.Count, family, slot, spacing,
                    VariedRoomSpan(spacing, slot, seed, depth), seed, true, depth));
            }
            for (int index = 1; index < rooms.Count; index++) { Link(rooms, index - 1, index); }
            if (AreNeighbourRooms(rooms[0], rooms[rooms.Count - 1]) &&
                !rooms[0].links.Contains(rooms.Count - 1))
            { Link(rooms, rooms.Count - 1, 0); }
            return rooms;
        }

        /// <summary>
        /// Index 0 is the threshold, the last chain room is the way home, and one room in the
        /// middle is the office copy.""" Everything else cycles the repeating families.
        ///
        /// The three unique families are unique because something depends on there being exactly
        /// one: the gate anchor, the evidence book, and the way out.
        /// </summary>
        private static string ChainFamilyFor(int index, int chainLength, int seed)
        {
            if (index == 0) { return UniqueFamilies[0]; }
            if (index == chainLength - 1) { return UniqueFamilies[2]; }
            int officeAt = 1 + Math.Abs(seed / 23) % Math.Max(1, chainLength - 2);
            if (index == officeAt) { return UniqueFamilies[1]; }
            // service_passage must appear at least once: the generator's climate room is
            // FirstOrDefault(utility_room) ?? First(service_passage), and the second half of that
            // throws when there is none.
            if (index == 1 && officeAt != 1) { return "service_passage"; }
            if (index == 2 && officeAt == 1) { return "service_passage"; }
            return ChainFamilies[Math.Abs(seed / 7 + index) % ChainFamilies.Length];
        }

        /// <summary>
        /// The room you arrive in: one grand space across two slots, and the only one.
        ///
        /// Owner: *"the normal yellow backrooms look isnt the whole floor but the main spanw
        /// room"*, and earlier *"making the 0 level rooms be grand large spaces"*. Both are true
        /// of this room and neither is true of the rest of the level.
        ///
        /// Centred between the two slot centres and spanning both, so the corridor from the next
        /// chain room meets it exactly where it would have met a one-slot room -- the second
        /// slot's centre is inside these bounds.
        ///
        /// No `Derange`, no span variation: this is the one room that is meant to read as built,
        /// so that everything beyond it reads as not.
        /// </summary>
        private static RoomRecord MakeHall(CoordinateRecord coordinate, IntVec2 first,
            IntVec2 second, int spacing, int seed, int depth)
        {
            // The arrival hall is grand room number one. It keeps index 0 and the threshold
            // family because `DestinationService` validates both: `byIndex[0].familyId` must be
            // `threshold_room`, and `GenStep_BackroomsDestination` takes `First(...)` of that
            // family to find where a crossing lands.
            return MakeGrandRoom(coordinate, 0, UniqueFamilies[0], first, second, spacing);
        }

        /// <summary>
        /// A room spanning **two** adjacent slots rather than one, which is what makes it grand.
        ///
        /// ## Owner direction, 2026-10-03, verbatim
        ///
        /// *"starts locations of main grand rooms can be anywhere on the map and lead anywhere in
        /// multiple differetn varied ways"* — **plural**. One hall was the arrival; the level is
        /// supposed to contain several large spaces.
        ///
        /// ## Grand is the SPAN, never the family
        ///
        /// This was the whole design question, and the answer came from what already depends on
        /// the hall. `DestinationService` requires room **index 0** to carry `threshold_room`, and
        /// `GenStep_BackroomsDestination` resolves a crossing's landing cell with
        /// `First(room =&gt; room.familyId == "threshold_room")`. **A second room of that family
        /// would be a second candidate for the place a player arrives**, decided by list order.
        ///
        /// So additional grand rooms take an ordinary family from <see cref="FamilyFor"/> and are
        /// grand purely by size. Nothing downstream needs teaching, no def changes, and the
        /// properties that follow from size follow automatically: they are wide enough to need
        /// <see cref="PillarCells"/>, and unlike the arrival hall they are **not** exempt from
        /// <see cref="RockIntrusionCells"/>, so they come out as large irregular spaces rather
        /// than as big rectangles.
        ///
        /// `WidestRoomSpan` is unaffected by the count: it is the maximum of the long and short
        /// spans, and the long span is this same number however many rooms use it.
        /// </summary>
        private static RoomRecord MakeGrandRoom(CoordinateRecord coordinate, int index,
            string family, IntVec2 first, IntVec2 second, int spacing)
        {
            int centerX = (SlotCenter(first.x, spacing) + SlotCenter(second.x, spacing)) / 2;
            int centerZ = (SlotCenter(first.z, spacing) + SlotCenter(second.z, spacing)) / 2;
            bool horizontal = first.z == second.z;
            int longSpan = Even(spacing * 2 - SlotGap, spacing * 2);
            int shortSpan = Even(SlotRoomSpan(spacing), spacing);
            int width = horizontal ? longSpan : shortSpan;
            int height = horizontal ? shortSpan : longSpan;
            return new RoomRecord
            {
                index = index,
                familyId = family,
                x = centerX - width / 2,
                z = centerZ - height / 2,
                width = width,
                height = height,
                links = new List<int>(),
            };
        }

        /// <summary>
        /// How many grand rooms a level has, the arrival hall included.
        ///
        /// **It falls with depth, and that is the shallow look rather than a convenience bound.**
        /// Owner: *"the normal yellow backrooms look isnt the whole floor but the main spanw
        /// room"*, and *"going deeping in can mean the numner of branch hallways and rooms
        /// distancing from the main portal spawn"*. The first band is the fewest, largest spaces
        /// a player will see; deeper is more rooms, smaller and tighter, until the only grand
        /// space left is the one they arrived in.
        ///
        /// Three is the most the geometry affords at depth 1 without crowding out the maze: each
        /// grand room costs **two** of thirty-six slots, and <see cref="SealedRoomCount"/> is
        /// already taking some.
        /// </summary>
        internal static int GrandRoomsPerLevel(int depth)
        {
            if (depth <= 1) { return 3; }
            if (depth == 2) { return 2; }
            return 1;
        }

        /// <summary>
        /// Whether the walk should try to make the room it is about to place a grand one.
        ///
        /// Drawn from the slot, so the same coordinate makes the same choice on every visit, and
        /// **it is only ever a request**: the caller still has to find a free slot to extend into
        /// and the resulting room still has to satisfy every link check an ordinary room does. A
        /// refusal costs nothing — the slot takes an ordinary room instead.
        /// </summary>
        private static bool GrandRoomHere(int seed, IntVec2 slot, int depth)
        {
            int draw = DestinationService.StableHash(seed, "grand:" + slot.x + "," + slot.z, depth);
            if (draw < 0) { draw = ~draw; }
            return draw % 5 == 0;
        }

        private static RoomRecord MakeRoom(CoordinateRecord coordinate, int index, string family,
            IntVec2 slot, int spacing, int span, int seed, bool fallback, int depth)
        {
            int width = span;
            int height = span;
            if (!fallback)
            {
                // Family proportions, scaled to the slot rather than written as cell counts.
                if (family == "service_passage") { width = span * 3 / 4; }
                else if (family == "borrowed_corridor")
                {
                    bool lengthwise = (seed / 7 + index) % 2 == 0;
                    if (lengthwise) { height = span * 3 / 5; } else { width = span * 3 / 5; }
                }
                else if (family == "storage_nook" || family == "utility_room")
                { width = span * 2 / 3; height = span * 2 / 3; }
                // **Proportions come apart with distance, not with a library version.**
                // Owner: *"odd variers walls and contructions making narrows , expansies"*. This
                // used to wait on `GetRoomLibraryVersion >= 2`, which is a content revision
                // rather than a statement about where in the maze a room is.
                if (DestinationService.GetRoomLibraryVersion(coordinate) >= 2)
                { Derange(coordinate, ref width, ref height, seed, index, span); }
            }
            width = Even(width, span);
            height = Even(height, span);
            int centerX = SlotCenter(slot.x, spacing);
            int centerZ = SlotCenter(slot.z, spacing);
            return new RoomRecord
            {
                index = index,
                familyId = family,
                x = centerX - width / 2,
                z = centerZ - height / 2,
                width = width,
                height = height,
                links = new List<int>(),
            };
        }

        /// <summary>The chain room a spur slot can hang off, or -1 when it touches none.</summary>
        private static int ChainNeighbourOf(List<RoomRecord> rooms, int chainLength, IntVec2 slot,
            int slots, int spacing)
        {
            int centerX = SlotCenter(slot.x, spacing);
            int centerZ = SlotCenter(slot.z, spacing);
            for (int index = 0; index < chainLength && index < rooms.Count; index++)
            {
                IntVec3 other = rooms[index].Bounds.CenterCell;
                if ((other.x == centerX && Math.Abs(other.z - centerZ) == spacing) ||
                    (other.z == centerZ && Math.Abs(other.x - centerX) == spacing))
                { return index; }
            }
            return -1;
        }

        /// <summary>
        /// Whether these two rooms are a shape a corridor can join.
        ///
        /// **A DIAGONAL PAIR IS NOW ONE OF THEM, and that is the whole of the degree change.**
        /// This function returned false for anything off-axis because `BuildCorridors` could only
        /// carve along one axis — so a slot's four orthogonal neighbours were the only links in
        /// existence and max degree was **4** at every depth. <see cref="BentLegs"/> removed that
        /// constraint, so an equal-magnitude offset on both axes — one slot across and one slot
        /// up, the rooms whose lane midpoint is real rock — is admissible too, and a slot has
        /// eight such neighbours rather than four.
        ///
        /// Kept to the **shape** question deliberately. Whether a route actually fits is
        /// `CorridorLegs`' answer and it needs the whole room list to give it; asking two
        /// questions in one function here is how this file ended up with a rule derived twice.
        /// `DestinationService.AreGridNeighbors` asks the identical question of the saved graph and
        /// the two must agree.
        /// </summary>
        internal static bool AreNeighbourRooms(RoomRecord first, RoomRecord second)
        {
            if (first == null || second == null) { return false; }
            if (first.Bounds.Overlaps(second.Bounds)) { return false; }
            IntVec3 a = first.Bounds.CenterCell;
            IntVec3 b = second.Bounds.CenterCell;
            // **THE ONE BOUND, AND IT IS THE PLANNER'S OWN COARSEST GEOMETRY RATHER THAN A
            // PREFERENCE.** With seven lane route forms almost any pair of rooms could be joined
            // by a corridor that goes far enough, and *"a room joined to everything"* is what the
            // graph ceiling in `ValidateRooms` exists to refuse. Two of the widest slots this
            // planner can produce is the reach, so the braid's furthest proposal -- two slots --
            // is admissible at every depth and nothing beyond it is.
            if (Math.Abs(a.x - b.x) > FurthestLinkedCentres ||
                Math.Abs(a.z - b.z) > FurthestLinkedCentres)
            { return false; }
            bool alongX;
            int line;
            if (TryStraightCorridor(first, second, out alongX, out line)) { return true; }
            // Off-axis on both, and within reach: the lane router has a form for it. Whether a
            // route actually fits is `CorridorLegs`' answer and it needs the whole room list to
            // give it -- asking two questions in one function here is how this file ended up with
            // a rule derived twice.
            return a.x != b.x && a.z != b.z;
        }

        /// <summary>
        /// The furthest apart two linked rooms' centres may be, in cells: two of the coarsest slots
        /// this planner can produce. See <see cref="AreNeighbourRooms"/>.
        /// </summary>
        internal static int FurthestLinkedCentres
        {
            get { return SlotSpacing(MinSlotsPerAxis) * 2; }
        }

        /// <summary>
        /// Pulls a room's proportions away from the tidy defaults, harder the deeper the
        /// coordinate sits, and sometimes straight out of the player's own colony.
        ///
        /// **Shallow coordinates barely move.** The yellow rooms read as a place precisely
        /// because they are monotonous and regular, and deranging them would throw away the
        /// image the whole setting rests on. The wrongness is something the player travels
        /// toward.
        ///
        /// **Clamped to the slot, not to a constant.** The old version clamped to 8..17 because
        /// rooms sat 19 cells apart; the spacing is now a function of depth, so the clamp is too.
        /// The clamp is what keeps *"deranged"* from collapsing into *"broken"*.
        /// </summary>
        private static void Derange(CoordinateRecord coordinate, ref int width, ref int height,
            int seed, int roomIndex, int span)
        {
            // **PROPORTIONS COME APART WITH DISTANCE, NOT ONLY WITH DEPTH.** Owner: *"odd variers
            // walls and contructions making narrows , expansies"*. This returned immediately at
            // depth 1, so every room on a first level kept its family's tidy proportions.
            //
            // The room's chain index IS its distance here: the serpentine is built in order from
            // the threshold, so room N is N links along it. The link graph does not exist yet at
            // this point -- rooms are made first and joined afterwards -- so the index is both
            // the only distance available and the correct one.
            int band = roomIndex / LinksPerShapeBand;
            if (band > MaximumShapeBand) { band = MaximumShapeBand; }
            int depth = coordinate.Depth + band;
            if (depth <= 1) { return; }

            int roll = DestinationService.StableHash(seed, "derange:" + roomIndex, depth);
            if (roll < 0) { roll = ~roll; }

            // An echoed room: take the proportions of something the branch actually built,
            // snapshotted when this coordinate was discovered. Deeper spaces do it more often.
            IReadOnlyList<int> echoed = coordinate.EchoedRoomSizes;
            int echoChance = Math.Min(50, (depth - 1) * 12);
            if (echoed != null && echoed.Count >= 2 && roll % 100 < echoChance)
            {
                width = Clamp(echoed[roll % echoed.Count], span);
                height = Clamp(echoed[(roll / 7) % echoed.Count], span);
                return;
            }

            // A hallway. Owner direction 2026-09-29: "its weirtd and lots of halways and
            // halway/rooms and facilitys and noraml like rooms".
            int hallChance = Math.Min(35, (depth - 1) * 9);
            if ((roll / 3) % 100 < hallChance)
            {
                bool lengthwise = ((roll / 5) % 2) == 0;
                int longSide = span;
                int shortSide = Math.Max(8, span / 3);
                width = Clamp(lengthwise ? longSide : shortSide, span);
                height = Clamp(lengthwise ? shortSide : longSide, span);
                return;
            }

            // Otherwise: stretch. The spread grows with depth AND with the slot, so a deep room
            // can be a long corridor or a near-square hall where a shallow one is always a hall.
            int spread = Math.Min(span / 3, depth * Math.Max(1, span / 12));
            if (spread < 1) { spread = 1; }
            width = Clamp(width + (roll % (spread * 2 + 1)) - spread, span);
            height = Clamp(height + ((roll / 11) % (spread * 2 + 1)) - spread, span);
        }

        /// <summary>Keeps a dimension inside what this depth's slot can hold.</summary>
        private static int Clamp(int value, int span)
        {
            if (value < 8) { return 8; }
            return value > span ? span : value;
        }

        /// <summary>
        /// Rooms are an even number of cells across so <c>CellRect.CenterCell</c> lands where
        /// doors and corridors expect it, whatever the room's size.
        /// </summary>
        private static int Even(int value, int span)
        {
            int clamped = Clamp(value, span);
            if (clamped % 2 != 0) { clamped--; }
            return clamped < 8 ? 8 : clamped;
        }

        private static void Link(List<RoomRecord> rooms, int a, int b)
        {
            if (rooms[a].links.Contains(b)) { return; }
            rooms[a].links.Add(b);
            rooms[b].links.Add(a);
        }

        /// <summary>
        /// Prove this layout walkable before any map exists.
        ///
        /// <paramref name="motif"/> is **the coordinate's own**, because the rock shapes it
        /// decides are the rock the generator will leave standing: a validator proving a square
        /// room the carver then shapes is a validator proving a different room, which is the
        /// defect class that stopped every coordinate generating for thirty-nine checkpoints.
        /// </summary>
        private static bool CandidateIsSafe(List<RoomRecord> rooms, int depth, CoordinateMotif motif)
        {
            if (!DestinationService.ValidateRooms(rooms, out _)) { return false; }
            // Project the exact boundary walls, one-cell openable doors, three-cell corridors and
            // the pillar lattice. A bounded floor check before any engine map/content state
            // exists, so a layout that seals a room off never reaches a map.
            var floor = new bool[DestinationService.MapWidth, DestinationService.MapHeight];
            foreach (RoomRecord room in rooms)
            {
                foreach (IntVec3 cell in room.Bounds.Cells)
                {
                    bool edge = cell.x == room.Bounds.minX || cell.x == room.Bounds.maxX || cell.z == room.Bounds.minZ || cell.z == room.Bounds.maxZ;
                    floor[cell.x, cell.z] = !edge || DoorOpening(room, rooms, cell);
                }
                // The pillars, from the SAME function the generator spawns them from.
                foreach (IntVec3 pillar in PillarCells(room))
                { floor[pillar.x, pillar.z] = false; }
                // And the rock left standing in the corners, from the same function again.
                // The SAME shaping depth the generator will carve with. Passing the
                // coordinate's own depth here while the generator used a per-room one would be
                // a validator proving a room that is not the room that gets built.
                foreach (IntVec3 rock in RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth), motif))
                { floor[rock.x, rock.z] = false; }
            }
            foreach (RoomRecord room in rooms)
            {
                foreach (int linked in room.links.Where(index => index > room.index))
                {
                    RoomRecord other = rooms[linked];
                    // The width, the shaping depth and the back-to-back test all live inside
                    // `CorridorLegs` now, so this loop no longer needs the two centres it used to
                    // compute the ranges from. The pair's own shaping depth still decides the
                    // width -- a corridor near the hall stays the plain three cells and one deep
                    // in the maze may narrow or open out -- it is just asked for in one place.
                    // **THE SAME SHAPE THE CARVER WILL CUT, from the one authority.** A
                    // back-to-back pair returns no legs: the doorway in the shared wall is the
                    // route, and the floor grid already carries it. This loop used to rebuild the
                    // ranges itself, which meant a corridor the validator proved and a corridor
                    // the generator carved were two independent derivations of one rule -- the
                    // defect this file has paid for repeatedly. See `CorridorLegs`.
                    foreach (CorridorLeg leg in CorridorLegs(room, other,
                        Math.Max(ShapeDepthOf(rooms, room, depth),
                            ShapeDepthOf(rooms, other, depth)), rooms))
                    {
                        foreach (IntVec3 cell in leg.Floor.Cells)
                        {
                            if (cell.x < 0 || cell.z < 0 ||
                                cell.x >= DestinationService.MapWidth ||
                                cell.z >= DestinationService.MapHeight)
                            { continue; }
                            floor[cell.x, cell.z] = true;
                        }
                    }
                }
            }
            IntVec3 start = rooms[0].Bounds.CenterCell;
            var seen = new HashSet<IntVec3> { start };
            var pending = new Queue<IntVec3>();
            pending.Enqueue(start);
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            while (pending.Count > 0)
            {
                IntVec3 cell = pending.Dequeue();
                foreach (IntVec3 direction in directions)
                {
                    IntVec3 next = cell + direction;
                    if (next.x >= 0 && next.z >= 0 && next.x < DestinationService.MapWidth && next.z < DestinationService.MapHeight &&
                        floor[next.x, next.z] && seen.Add(next)) { pending.Enqueue(next); }
                }
            }
            // **A ROOM THAT CLAIMS A ROUTE MUST HAVE ONE; A VAULT CLAIMS NONE.** This read
            // `rooms.All(...)`, and that is why the degree spec's explicit **0** case was
            // unbuildable -- an unlinked room has no floor leading to it by design, and this
            // clause is the thing that refused it. Owner: *"insentive to mine things out to find
            // isolated undiscorvered rooms when mining and deconsturcting wals"*.
            //
            // **The guarantee is not weakened.** The defect this clause exists to catch is a room
            // the generator believed it had connected and had not, and every such room has links
            // -- that is what believing it was connected means. `SealedFamily` is the only family
            // the planner ever gives zero links, it is given them deliberately, and the rock
            // around it is `Mineable` like all the fill.
            return rooms.All(room => room.links.Count == 0 || seen.Contains(room.Bounds.CenterCell)) &&
                rooms.Where(room => room.familyId == "utility_room" || room.familyId == "storage_nook").All(room => room.links.Count == 1) &&
                rooms.Where(room => room.familyId == SealedFamily).All(room => room.links.Count == 0);
        }

        /// <summary>
        /// Slide this room until its wall meets the other's, along whichever axis they are
        /// already separated on.
        ///
        /// Only moved, never resized, so every property the planner already proved about the
        /// room -- its span is even, its doorways sit at its wall midpoints, its pillar lattice
        /// clears the centre cross -- survives the move untouched.
        ///
        /// Refuses a diagonal pair, because two rooms offset on both axes have no wall to share.
        ///
        /// ## Wall against wall, and the move is put back if it does not work
        ///
        /// **The first draft moved the room onto its host's wall column and left it there.** Two
        /// of its four branches overlapped the host by exactly one cell -- which `ValidateRooms`
        /// refuses outright -- and the other two abutted, which the old `SharesWall` did not
        /// recognise, so the pair got neither a corridor nor a doorway and the spur was sealed.
        /// **Every push killed the candidate, one way or the other, and no coordinate generated.**
        ///
        /// So it lands one cell clear, each room keeping its own wall, and then **three things
        /// are checked and the move is undone if any of them fails**:
        ///
        ///   * it is still on the map;
        ///   * <see cref="SharesWall"/> agrees, so the readers that skip the corridor and the
        ///     reader that opens the doorway all see the same pair;
        ///   * **it has not landed on a third room.** A spur only has one link, so the move
        ///     cannot re-route the spine -- but the slot it leaves is not the slot it arrives in,
        ///     and the arrival may belong to somebody else.
        ///
        /// Undone rather than refused in advance, because the position is the only thing that
        /// decides any of it, and a room that goes back where it was is simply a room that is
        /// not back to back with anything.
        /// </summary>
        private static void PushAgainst(List<RoomRecord> rooms, RoomRecord mover, RoomRecord anchorRoom,
            int depth)
        {
            if (rooms == null || mover == null || anchorRoom == null) { return; }
            CellRect a = mover.Bounds;
            CellRect b = anchorRoom.Bounds;
            bool verticalOverlap = a.minZ <= b.maxZ && b.minZ <= a.maxZ;
            bool horizontalOverlap = a.minX <= b.maxX && b.minX <= a.maxX;
            int originalX = mover.x;
            int originalZ = mover.z;
            if (verticalOverlap && a.minX > b.maxX) { mover.x = b.maxX + 1; }
            else if (verticalOverlap && a.maxX < b.minX) { mover.x = b.minX - a.Width - 1; }
            else if (horizontalOverlap && a.minZ > b.maxZ) { mover.z = b.maxZ + 1; }
            else if (horizontalOverlap && a.maxZ < b.minZ) { mover.z = b.minZ - a.Height - 1; }
            else { return; }

            bool onMap = mover.Bounds.minX >= 1 && mover.Bounds.minZ >= 1 &&
                mover.Bounds.maxX < DestinationService.MapWidth - 1 &&
                mover.Bounds.maxZ < DestinationService.MapHeight - 1;
            bool collides = rooms.Any(other => other != mover && mover.Bounds.Overlaps(other.Bounds));
            // **AND IT MAY NOT LAND IN SOMEBODY ELSE'S CORRIDOR.** A fourth condition, added with
            // the lane router. The three above ask whether the room's new position is legal; none
            // of them asks whether it broke a route that was already there, and a dead end sliding
            // into a lane is exactly how it would. The link whose route it blocked may be a
            // spanning-tree edge, which `PruneUnroutableLinks` deliberately refuses to remove --
            // so the level would simply fail to generate, with the reason three steps upstream of
            // where it showed.
            bool blocksARoute = !EveryLinkRoutes(rooms, mover, depth);
            if (onMap && !collides && !blocksARoute && SharesWall(mover, anchorRoom)) { return; }
            mover.x = originalX;
            mover.z = originalZ;
        }

        /// <summary>
        /// Whether every link in the graph still has a corridor or a shared wall under it.
        ///
        /// Asked after a room moves. See <see cref="PushAgainst"/>.
        /// </summary>
        private static bool EveryLinkRoutes(List<RoomRecord> rooms, RoomRecord mover, int depth)
        {
            // **ONLY THE LINKS THE MOVER COULD POSSIBLY HAVE BROKEN.** The one thing that changed
            // is where this room is, and a corridor it cannot reach cannot have been blocked by
            // it. Without the filter this is every link re-routed through seven forms on every
            // push attempt, which is the whole level's routing done sixty times over.
            IntVec3 at = mover.Bounds.CenterCell;
            int span = FurthestLinkedCentres * 2;
            for (int index = 0; index < rooms.Count; index++)
            {
                RoomRecord room = rooms[index];
                if (room == null || room.links == null) { continue; }
                IntVec3 here = room.Bounds.CenterCell;
                if (room != mover && (Math.Abs(here.x - at.x) > span || Math.Abs(here.z - at.z) > span))
                { continue; }
                for (int link = 0; link < room.links.Count; link++)
                {
                    if (room.links[link] <= room.index) { continue; }
                    RoomRecord other = rooms.FirstOrDefault(r => r != null && r.index == room.links[link]);
                    if (other == null) { continue; }
                    // **THE SHAPE GATE TOO, not only the route**, because the shape gate is what
                    // `ValidateRooms` asks and a move that fails it refuses the whole layout. A
                    // push slides a room by most of its own span, which is enough to carry a
                    // reach-braid link past `FurthestLinkedCentres` -- measured, as a candidate
                    // refusal reading *"is not a shape a corridor can join"* at 106 cells against
                    // a stated 96. Asking only about the route missed it entirely, because the
                    // route was still perfectly carvable.
                    if (!AreNeighbourRooms(room, other)) { return false; }
                    if (SharesWall(room, other)) { continue; }
                    if (CorridorLegs(room, other, depth, rooms).Count == 0) { return false; }
                }
            }
            return true;
        }

        /// <summary>
        /// Whether these two rooms stand wall against wall, with no rock between them to run a
        /// corridor through.
        ///
        /// **ABUTTING, NOT OVERLAPPING, and the first draft had it the other way round.** It
        /// tested `a.maxX == b.minX` -- one shared wall column belonging to both rooms -- and
        /// `CellRect.Overlaps` is **inclusive on both edges**, so a pair like that overlaps by
        /// RimWorld's own reckoning. `ValidateRooms` has refused overlapping rooms since the
        /// first version of the layout, so **every back-to-back pair made the whole candidate
        /// illegal** and no coordinate would generate.
        ///
        /// So the two rooms each keep their own wall and stand one cell apart: room A's east wall
        /// at `a.maxX`, room B's west wall at `a.maxX + 1`. Which is what a wall between two
        /// rooms in a building looks like anyway, and it leaves the overlap rule intact.
        ///
        /// **And then there is nothing more to decide.** `DoorOpening`'s existing rule already
        /// covers it: `other.Bounds.minX > room.Bounds.maxX` is true of an abutting neighbour, so
        /// each room opens the midpoint of its own wall, and `ValidateRooms` guarantees through
        /// `AreGridNeighbors` that linked rooms' centres share a row or a column -- so the two
        /// midpoints are the same cell on the shared axis and the openings meet. No second rule,
        /// no shared-cell arithmetic, nothing new to keep in agreement.
        ///
        /// This is still **the single place the condition is decided** -- `BuildCorridors` skips
        /// the pair and `CandidateIsSafe` skips modelling a corridor for it -- for the same
        /// reason `PillarCells` is: two readers deriving one rule independently is the defect
        /// that stopped every coordinate generating for thirty-nine checkpoints.
        /// </summary>
        internal static bool SharesWall(RoomRecord first, RoomRecord second)
        {
            if (first == null || second == null) { return false; }
            CellRect a = first.Bounds;
            CellRect b = second.Bounds;
            bool verticalOverlap = a.minZ <= b.maxZ && b.minZ <= a.maxZ;
            bool horizontalOverlap = a.minX <= b.maxX && b.minX <= a.maxX;
            if ((a.maxX + 1 == b.minX || b.maxX + 1 == a.minX) && verticalOverlap) { return true; }
            if ((a.maxZ + 1 == b.minZ || b.maxZ + 1 == a.minZ) && horizontalOverlap) { return true; }
            return false;
        }

        /// <summary>
        /// Whether this perimeter cell is a doorway, and **it asks `TryStraightCorridor` rather
        /// than assuming a wall midpoint.**
        ///
        /// Owner, 2026-10-03: *"non default fdoor possitions in rooms so doors are not just on each
        /// side, can have doors al over"*. The four tests below used to read
        /// `cell.z == room.Bounds.CenterCell.z`, which put every door at the exact centre of its
        /// wall — and that was not a choice, it was forced: a corridor could only run along a line
        /// both centres shared, so the midpoint was the only cell one could arrive at. Now the
        /// corridor names the line it runs along and the door is wherever that line meets the wall.
        ///
        /// **A diagonal link opens two doors and that is deliberate.** The elbow leaves through one
        /// of the two walls facing the other room and which one is settled while the route is
        /// built, after trying both; re-deriving that choice here would be a second derivation of
        /// `BentLegs`, which is the defect this file keeps paying for. So both cells open, and the
        /// one the corridor does not use is a door with rock behind it — the owner's own *"odd
        /// contructions of doors walls corners deadends doors to now where"*, which
        /// <see cref="FalseOpening"/> already builds on purpose. It costs nothing: the cell is on
        /// the room's own perimeter and what lies past it is solid, so no route is added or taken
        /// away and `CandidateIsSafe` proves the same level either way.
        /// </summary>
        internal static bool DoorOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            CellRect bounds = room.Bounds;
            IntVec3 centre = bounds.CenterCell;
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                bool alongX;
                int line;
                if (TryStraightCorridor(room, other, out alongX, out line))
                {
                    if (alongX)
                    {
                        if (other.Bounds.minX > bounds.maxX && cell.x == bounds.maxX && cell.z == line) { return true; }
                        if (other.Bounds.maxX < bounds.minX && cell.x == bounds.minX && cell.z == line) { return true; }
                        continue;
                    }
                    if (other.Bounds.minZ > bounds.maxZ && cell.z == bounds.maxZ && cell.x == line) { return true; }
                    if (other.Bounds.maxZ < bounds.minZ && cell.z == bounds.minZ && cell.x == line) { return true; }
                    continue;
                }
                if (other.Bounds.minX > bounds.maxX && cell.x == bounds.maxX && cell.z == centre.z) { return true; }
                if (other.Bounds.maxX < bounds.minX && cell.x == bounds.minX && cell.z == centre.z) { return true; }
                if (other.Bounds.minZ > bounds.maxZ && cell.z == bounds.maxZ && cell.x == centre.x) { return true; }
                if (other.Bounds.maxZ < bounds.minZ && cell.z == bounds.minZ && cell.x == centre.x) { return true; }
            }
            // **A BACK-TO-BACK PAIR NEEDS NO EXTRA RULE HERE.** The tests above ask whether the
            // neighbour lies strictly beyond this room's edge, and an abutting neighbour's near
            // edge is `maxX + 1`, which is strictly beyond `maxX`. `TryStraightCorridor` answers
            // for such a pair as well -- they are separated on one axis and overlap on the other,
            // which is exactly what standing wall to wall means -- so **both rooms read the same
            // line out of the same function and their two openings are the same cell.** That is
            // what makes them meet, rather than an assumption about where their centres are: since
            // `TryStraightCorridor` the two centres need not share an axis at all.
            //
            // The first draft added a second rule and a `SharedDoorCell` to go with it, computed
            // from the overlap of two rooms whose edges were equal. Both are gone: the edges are
            // no longer equal, there is nothing left for it to compute, and **two rules deciding
            // one doorway is the defect this file keeps paying for.**
            return FalseOpening(room, rooms, cell);
        }

        /// <summary>One wall in this many with nothing behind it opens anyway.</summary>
        internal const int FalseOpeningRarity = 3;

        /// <summary>
        /// A doorway onto solid rock.
        ///
        /// Owner: *"odd contructions of doors walls corners deadends doors to now where not just
        /// doors on 4 cosides of nothing but square rooms"*. The rule above IS that complaint
        /// written as code -- an opening exists only at the midpoint of a wall facing a linked
        /// room, so every room was a box with up to four doors dead centre.
        ///
        /// **A wall with no link behind it may open anyway**, offset from the centre so it does
        /// not read as another corridor that failed to arrive. Beyond it is rock.
        ///
        /// ## Why this is safe to decide here
        ///
        /// It **adds a dead end and removes no route**. The cell is on the room's own perimeter
        /// and the cell past it is rock, so reachability is untouched -- which is the only thing
        /// `CandidateIsSafe` is proving. And both the validator and the generator reach it
        /// through `DoorOpening`, so the wall that is proved is the wall that is built. A second
        /// derivation of one rule is the defect that cost thirty-nine checkpoints.
        ///
        /// **Never on the threshold hall.** That is where a player arrives and the one room meant
        /// to read as built; the maze starts after it.
        ///
        /// Offset by a third of the wall rather than any cell, so it still looks like somebody
        /// put a door there, which is what makes it unsettling rather than merely broken.
        /// </summary>
        internal static bool FalseOpening(RoomRecord room, IReadOnlyList<RoomRecord> rooms, IntVec3 cell)
        {
            if (room == null || room.index == 0) { return false; }
            CellRect bounds = room.Bounds;
            // Corners are structure, never openings.
            bool onEastWall = cell.x == bounds.maxX;
            bool onWestWall = cell.x == bounds.minX;
            bool onNorthWall = cell.z == bounds.maxZ;
            bool onSouthWall = cell.z == bounds.minZ;
            int walls = (onEastWall ? 1 : 0) + (onWestWall ? 1 : 0)
                + (onNorthWall ? 1 : 0) + (onSouthWall ? 1 : 0);
            if (walls != 1) { return false; }

            int side = onEastWall ? 0 : onWestWall ? 1 : onNorthWall ? 2 : 3;
            // A wall that already carries a real doorway is left alone: two openings in one wall
            // reads as a mistake rather than as a door that goes nowhere.
            foreach (int index in room.links)
            {
                RoomRecord other = rooms.First(r => r.index == index);
                if (side == 0 && other.Bounds.minX > bounds.maxX) { return false; }
                if (side == 1 && other.Bounds.maxX < bounds.minX) { return false; }
                if (side == 2 && other.Bounds.minZ > bounds.maxZ) { return false; }
                if (side == 3 && other.Bounds.maxZ < bounds.minZ) { return false; }
            }

            int roll = DestinationService.StableHash(room.index * 17 + side,
                (room.familyId ?? "") + ":falsedoor", side);
            if (roll < 0) { roll = ~roll; }
            if (roll % FalseOpeningRarity != 0) { return false; }

            // A third along the wall, not the middle: the middle is where a real door goes.
            bool horizontal = side >= 2;
            int low = horizontal ? bounds.minX : bounds.minZ;
            int high = horizontal ? bounds.maxX : bounds.maxZ;
            if (high - low < 4) { return false; }
            int at = low + (high - low) / 3;
            return horizontal ? cell.x == at : cell.z == at;
        }
    }
}
