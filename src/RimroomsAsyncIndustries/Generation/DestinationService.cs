using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>RR-SPACE: create or retrieve one finite, persisted machine-linked site.</summary>
    public static class DestinationService
    {
        // Owner direction, 2026-09-30: *"theri 300x300 gate"*, and *"making the 0 level rooms
        // be grand large spaces"*. A 60x60 coordinate could not hold a grand anything -- its
        // whole room grid was three slots at 19 cells. See RoomLayoutPlanner for what scales
        // with this and what it costs.
        public const int MapWidth = 300;
        public const int MapHeight = 300;
        private const int WorldTileCandidateBudget = 512;
        private static readonly IntVec3 MapSize = new IntVec3(MapWidth, 1, MapHeight);
        private static readonly string[] PreferredBiomeNames =
        {
            "TemperateForest", "TemperateSwamp", "TemperateSwampyForest"
        };

        // **Exactly one of each, because something depends on there being exactly one:** the
        // gate anchor, the evidence book, and the way out. Owner direction, 2026-09-30, on a
        // warren of up to sixty rooms: threshold / office / return stay unique, the rest repeat.
        private static readonly string[] UniqueFamilies =
        {
            "threshold_room", "office_copy", "return_gallery"
        };

        // At least one, and then as many as the chain is long. `service_passage` is required
        // rather than optional because the generator's climate room is
        // FirstOrDefault(utility_room) ?? First(service_passage), and the second half throws
        // when there is none.
        private static readonly string[] AtLeastOnceFamilies = { "service_passage" };

        private static readonly string[] RepeatingFamilies =
        {
            "survey_lobby", "service_passage", "borrowed_corridor", "storage_nook", "utility_room",
            // The sealed vault, which has no links at all and is found by mining. See
            // `RoomLayoutPlanner.SealedFamily`.
            "sealed_vault"
        };

        public static CompanyActionResult EnsureSite(
            RimroomsCampaignComponent campaign,
            CoordinateRecord coordinate,
            out Map map,
            out IntVec3 entry)
        {
            map = null;
            entry = IntVec3.Invalid;
            if (campaign == null || !campaign.CanOperate || coordinate == null ||
                campaign.Coordinates.Count(record => ReferenceEquals(record, coordinate)) != 1 ||
                string.IsNullOrWhiteSpace(coordinate.Id) || coordinate.Seed < 0 ||
                coordinate.GeneratorVersion < 1)
            {
                return CompanyActionResult.Refused("RR_Generation_InvalidRequest");
            }

            // **A deliberate release is exempt, and nothing else is.** A coordinate the player
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
            }

            if (!EnsureRoomGraph(coordinate, out string graphFailure))
            {
                return Fail(coordinate, null, graphFailure);
            }
            // **The one place a coordinate map is ever generated, so the one place the budget
            // must be unavoidable.** NaturalFrontierService refuses at the doorway, which is
            // where a player should be told; this is the backstop for every other route in --
            // a machine gate, a saved address, a recovery path. See Portals/OpenMapBudget.
            //
            // Only when a NEW map would be made. A coordinate that already has its site is being
            // recalled, not opened, and refusing that would lock a player out of a place they are
            // standing next to.
            if (coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother)
            { return CompanyActionResult.Refused(Portals.OpenMapBudget.BlockedKey); }
            int fingerprint = ComputeFingerprint(coordinate);

            RimroomsDestinationMapParent parent = coordinate.Site as RimroomsDestinationMapParent;
            if (coordinate.Site != null)
            {
                if (parent == null || parent.CoordinateId != coordinate.Id ||
                    parent.GeneratorVersion != coordinate.GeneratorVersion ||
                    parent.RoomLibraryVersion != GetRoomLibraryVersion(coordinate) ||
                    parent.LayoutFingerprint != fingerprint || !Find.WorldObjects.Contains(parent))
                {
                    return Fail(coordinate, parent, "RR_Generation_OwnerMismatch");
                }

                if (parent.HasMap)
                {
                    map = parent.Map;
                    if (!ValidateExistingMap(coordinate, parent, map, fingerprint, out string existingFailure))
                    {
                        map = null;
                        return Fail(coordinate, parent, existingFailure);
                    }
                    coordinate.status = CoordinateStatus.Ready;
                    coordinate.lastFailureKey = null;
                    entry = parent.EntryCell;
                    return CompanyActionResult.Existing();
                }

                // A Ready record whose map was removed is a recovery case, never a reroll.
                if (coordinate.Status == CoordinateStatus.Ready ||
                    coordinate.Rooms.Any(room => room != null && room.Surveyed) ||
                    parent.LayoutReady || parent.GenerationAttempted)
                {
                    return Fail(coordinate, parent, "RR_Generation_PreviouslyOpenedMapMissing");
                }
            }
            else
            {
                if (coordinate.Status == CoordinateStatus.Ready)
                {
                    return Fail(coordinate, null, "RR_Generation_OwnerMissing");
                }
                WorldObjectDef ownerDef = DefDatabase<WorldObjectDef>.GetNamedSilentFail("RR_BackroomsSite");
                if (ownerDef == null)
                {
                    return Fail(coordinate, null, "RR_Generation_OwnerDefMissing");
                }
                PlanetTile tile = FindUniqueTile(coordinate);
                if (!tile.Valid)
                {
                    return Fail(coordinate, null, "RR_Generation_NoFreeTile");
                }
                parent = WorldObjectMaker.MakeWorldObject(ownerDef) as RimroomsDestinationMapParent;
                if (parent == null || !parent.InitializeCoordinate(coordinate.Id, coordinate.GeneratorVersion,
                    GetRoomLibraryVersion(coordinate), fingerprint))
                {
                    return Fail(coordinate, parent, "RR_Generation_OwnerDefMismatch");
                }
                parent.Tile = tile;
                parent.RecordGenerationPlan(RoomLayoutPlanner.IdentifyCandidate(coordinate), RoomContentBuilder.ContentVersion);
                coordinate.site = parent;
                try
                {
                    Find.WorldObjects.Add(parent);
                }
                catch (Exception error)
                {
                    Log.Error("[Rimrooms][Generation] Could not register the destination owner; graph retained: " + error);
                    if (!Find.WorldObjects.Contains(parent)) { coordinate.site = null; }
                    return Fail(coordinate, parent, "RR_Generation_OwnerRegistrationFailed");
                }
            }

            if (parent == null || !parent.Tile.Valid ||
                Find.WorldObjects.MapParentAt(parent.Tile) != parent || Current.Game.FindMap(parent.Tile) != null)
            {
                return Fail(coordinate, parent, "RR_Generation_OwnerMismatch");
            }

            WorldObjectDef suggestedParentDef = DefDatabase<WorldObjectDef>.GetNamedSilentFail("RR_BackroomsSite");
            if (suggestedParentDef == null)
            {
                return Fail(coordinate, parent, "RR_Generation_OwnerDefMissing");
            }

            parent.BeginGenerationAttempt();
            try
            {
                using (Core.RimroomsDiagnostics.Measure("destination-generate"))
                { map = GetOrGenerateMapUtility.GetOrGenerateMap(parent.Tile, MapSize, suggestedParentDef); }
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Generation] Destination generation stopped; site and room graph retained: " + error);
                map = parent.Map;
                return Fail(coordinate, parent, "RR_Generation_MapBuildFailed");
            }

            if (map == null)
            {
                map = null;
                return Fail(coordinate, parent, parent.GenerationFailureKey ?? "RR_Generation_MapBuildFailed");
            }
            if (!ValidateExistingMap(coordinate, parent, map, fingerprint, out string mapFailure))
            {
                map = null;
                return Fail(coordinate, parent, mapFailure);
            }

            coordinate.status = CoordinateStatus.Ready;
            coordinate.lastFailureKey = null;
            // The place exists again, so the exemption is spent. Leaving it set would let a real
            // broken reference through on some later load, which is the thing the guard above is
            // for -- an exemption that outlives its reason is a hole.
            coordinate.releasedByPlayer = false;
            entry = parent.EntryCell;
            return CompanyActionResult.Applied();
        }

        internal static bool EnsureRoomGraph(CoordinateRecord coordinate, out string failureKey)
        {
            failureKey = null;
            if (coordinate == null || string.IsNullOrWhiteSpace(coordinate.Id) || coordinate.Seed < 0)
            {
                failureKey = "RR_Generation_InvalidCoordinate";
                return false;
            }
            if (coordinate.rooms == null || coordinate.rooms.Count == 0)
            {
                if (coordinate.Site != null || coordinate.Status != CoordinateStatus.Discovered)
                { failureKey = "RR_Generation_InvalidRoomGraph"; return false; }
                List<RoomRecord> selected;
                if (!RoomLayoutPlanner.TrySelect(coordinate, out selected))
                { failureKey = "RR_Generation_NoSafeCandidate"; return false; }
                // Candidate selection and geometry checks above are pure. This is the first graph commit.
                coordinate.rooms = selected;
            }
            if (!ValidateRoomGraph(coordinate, out failureKey)) { return false; }
            return true;
        }

        internal static bool ValidateRoomGraph(CoordinateRecord coordinate, out string failureKey)
        {
            return ValidateRooms(coordinate == null ? null : coordinate.rooms, out failureKey);
        }

        internal static bool ValidateRooms(List<RoomRecord> rooms, out string failureKey)
        {
            failureKey = null;
            if (rooms == null || rooms.Count < 6 || rooms.Count > RoomLayoutPlanner.MaxRooms ||
                rooms.Any(room => room == null))
            {
                failureKey = "RR_Generation_InvalidRoomGraph";
                return false;
            }

            // Check uniqueness before ToDictionary: malformed saved records must refuse
            // cleanly rather than throwing during preflight.
            if (rooms.Select(room => room.index).Distinct().Count() != rooms.Count ||
                rooms.Any(room => room.index < 0 || room.index >= rooms.Count))
            {
                failureKey = "RR_Generation_InvalidRoomGraph";
                return false;
            }
            var byIndex = rooms.ToDictionary(room => room.index, room => room);
            if (!byIndex.ContainsKey(0) || byIndex[0].familyId != "threshold_room")
            {
                failureKey = "RR_Generation_InvalidRoomGraph";
                return false;
            }
            foreach (string family in UniqueFamilies)
            {
                if (rooms.Count(room => room.familyId == family) != 1)
                {
                    failureKey = "RR_Generation_InvalidRoomGraph";
                    return false;
                }
            }
            foreach (string family in AtLeastOnceFamilies)
            {
                if (rooms.Count(room => room.familyId == family) < 1)
                {
                    failureKey = "RR_Generation_InvalidRoomGraph";
                    return false;
                }
            }

            foreach (RoomRecord room in rooms)
            {
                // Room spans are a function of depth now, so the bound is the widest slot the
                // planner can produce rather than the old hard-coded 16. Still even, because
                // CellRect.CenterCell is where every door and corridor is aimed.
                if (room.index < 0 || room.index >= rooms.Count || room.width < 8 ||
                    room.width > MaxRoomSpan || room.width % 2 != 0 ||
                    room.height < 8 || room.height > MaxRoomSpan || room.height % 2 != 0 ||
                    room.links == null || room.links.Distinct().Count() != room.links.Count ||
                    !KnownFamily(room.familyId) || !WithinMap(room.Bounds) ||
                    rooms.Any(other => other != room && room.Bounds.Overlaps(other.Bounds)))
                {
                    failureKey = "RR_Generation_InvalidRoomGraph";
                    return false;
                }
                foreach (int linkedIndex in room.links)
                {
                    RoomRecord linked;
                    if (!byIndex.TryGetValue(linkedIndex, out linked) || linked.links == null ||
                        !linked.links.Contains(room.index) ||
                        !AreGridNeighbors(room, linked))
                    {
                        failureKey = "RR_Generation_InvalidRoomGraph";
                        return false;
                    }
                }
            }

            var visited = new HashSet<int>();
            var pending = new Queue<int>();
            pending.Enqueue(0);
            while (pending.Count > 0)
            {
                int current = pending.Dequeue();
                if (!visited.Add(current)) { continue; }
                foreach (int neighbor in byIndex[current].links) { pending.Enqueue(neighbor); }
            }
            int directedEdges = rooms.Sum(room => room.links.Count);
            // **THE CEILING HERE FORBADE A MAZE, AND THAT IS WHY EVERY LEVEL WAS A LINE.**
            //
            // It was `directedEdges > 2 * rooms.Count`. A connected graph needs `n - 1` edges, so
            // a ceiling of `n` allowed **exactly one more: one loop, in the whole level, at every
            // depth.** The serpentine spine with a single closing ring was not a choice the
            // generator made -- it was the only shape this clause would accept, and every braided
            // maze candidate was refused with this key while the fallback caught every seed.
            //
            // Owner: *"i want them to be mazes like xcrazy like all levels mazes do you unerstand!
            // lsd crazy shaped mazes"*.
            //
            // A ceiling still belongs here, because **every edge is one carved corridor** and an
            // unbounded graph would carve the map to gravel. But the honest number is the
            // geometry's own: a link joins a slot to a slot within reach -- four orthogonal
            // neighbours, four diagonals, and the eight span-two offsets `RoomLayoutPlanner`'s
            // five-leg route forms reach -- so a grid graph cannot exceed eight undirected edges
            // per room, and `AreNeighbourRooms` refuses anything further. This is less a
            // loosening than a statement of what the slot grid can produce -- and it still refuses
            // what the clause was written to refuse: links between distant rooms, a duplicated
            // edge set, a room joined to everything. See `MaximumUndirectedEdgesPerRoom`.
            //
            // **The floor is untouched.** `visited.Count != rooms.Count` and the `n - 1` minimum
            // are what guarantee one connected place, and they are the half of this check that
            // was always doing the work.
            // **A SEALED VAULT IS NOT A DISCONNECTED LEVEL, and the difference is whether the room
            // claims a route.** This was `visited.Count != rooms.Count`, which refused any room the
            // BFS over links could not reach -- correct while every room had links, and the exact
            // clause that made the degree spec's *"0 - 10"* unbuildable at its lower end. Owner,
            // 2026-10-03: *"insentive to mine things out to find isolated undiscorvered rooms when
            // mining and deconsturcting wals"*.
            //
            // So the question is asked of rooms that have links: every one of them must be in the
            // same connected piece as the threshold. A room with none is a vault and is reached by
            // digging. The edge floor follows it -- a connected piece of `linked` rooms needs
            // `linked - 1` edges, not `rooms - 1` -- and the ceiling still counts every room,
            // because a vault is still a room the map has to hold.
            int linkedRooms = rooms.Count(room => room.links.Count > 0);
            if (!visited.Contains(0) ||
                rooms.Any(room => room.links.Count > 0 && !visited.Contains(room.index)) ||
                directedEdges < 2 * (linkedRooms - 1) ||
                directedEdges > 2 * MaximumUndirectedEdgesPerRoom * rooms.Count)
            {
                failureKey = "RR_Generation_InvalidRoomGraph";
                return false;
            }
            return true;
        }

        /// <summary>
        /// The most corridors a room may carry, and it is the slot grid's own limit.
        ///
        /// **RAISED FROM TWO TO EIGHT AT 0.12.82-dev, and the number is still the geometry's
        /// rather than a preference.** A link joins a slot to a slot within reach: four orthogonal
        /// neighbours, four diagonal ones, and the eight offsets with a span of two that
        /// `RoomLayoutPlanner`'s five-leg route forms can reach. Sixteen candidate neighbours is
        /// eight undirected edges per room. At two this clause refused every braided maze that
        /// used the links it had just been given — which is the same way the ceiling before it
        /// forbade a maze outright, and the reason that one is quoted at length below.
        ///
        /// It still refuses what it was written to refuse: links between distant rooms, a
        /// duplicated edge set, and a room joined to everything. The floor — `visited.Count` and
        /// the `n - 1` minimum — is untouched and is the half that guarantees one connected place.
        /// </summary>
        private const int MaximumUndirectedEdgesPerRoom = 8;

        internal static int ComputeFingerprint(CoordinateRecord coordinate)
        {
            unchecked
            {
                uint hash = 2166136261;
                Mix(ref hash, coordinate.Id);
                Mix(ref hash, coordinate.Seed);
                Mix(ref hash, coordinate.GeneratorVersion);
                Mix(ref hash, GetRoomLibraryVersion(coordinate));
                foreach (RoomRecord room in coordinate.rooms.OrderBy(room => room.index))
                {
                    Mix(ref hash, room.index);
                    Mix(ref hash, room.familyId);
                    Mix(ref hash, room.x);
                    Mix(ref hash, room.z);
                    Mix(ref hash, room.width);
                    Mix(ref hash, room.height);
                    foreach (int link in room.links.OrderBy(value => value)) { Mix(ref hash, link); }
                }
                return (int)(hash & 0x7fffffff);
            }
        }

        internal static int GetRoomLibraryVersion(CoordinateRecord coordinate)
        {
            return coordinate == null ? 0 : coordinate.roomLibraryVersion;
        }

        internal static bool ValidateExistingMap(
            CoordinateRecord coordinate,
            RimroomsDestinationMapParent parent,
            Map map,
            int fingerprint,
            out string failureKey)
        {
            using (Core.RimroomsDiagnostics.Measure("route-validation"))
            { return ValidateExistingMapCore(coordinate, parent, map, fingerprint, out failureKey); }
        }

        private static bool ValidateExistingMapCore(CoordinateRecord coordinate, RimroomsDestinationMapParent parent,
            Map map, int fingerprint, out string failureKey)
        {
            failureKey = null;
            if (parent == null || map == null || map.Parent != parent || map.Tile != parent.Tile ||
                map.Size.x != MapWidth || map.Size.z != MapHeight || map.Size.y != 1)
            {
                failureKey = "RR_Generation_MapSizeOrOwnerMismatch";
                return false;
            }
            if (!parent.LayoutReady || parent.LayoutFingerprint != fingerprint ||
                !ValidateCell(map, parent.EntryCell) || !ValidateCell(map, parent.ReturnCell) ||
                !ValidateCell(map, parent.OfficeEvidenceCell) || parent.ReturnAnchor == null ||
                parent.ReturnAnchor.Destroyed || parent.ReturnAnchor.Map != map ||
                !(parent.ContentVersion == 4
                    ? parent.ReturnAnchor is RimWorld.Building_Door && parent.ReturnAnchor.def.defName == "Door"
                    : parent.ContentVersion < 4 && parent.ReturnAnchor.def.defName == "RR_ReturnAnchor"))
            {
                failureKey = parent.GenerationFailureKey ?? "RR_Generation_IncompleteLayout";
                return false;
            }

            if (!Reachable(map, parent.EntryCell, parent.ReturnCell) ||
                !Reachable(map, parent.EntryCell, parent.OfficeEvidenceCell))
            {
                failureKey = "RR_Generation_UnreachableRequiredCell";
                return false;
            }
            return true;
        }

        private static bool KnownFamily(string family)
        {
            return UniqueFamilies.Contains(family) || RepeatingFamilies.Contains(family);
        }

        private static bool WithinMap(CellRect bounds)
        {
            return bounds.Width >= 3 && bounds.Height >= 3 && bounds.minX >= 1 && bounds.minZ >= 1 &&
                bounds.maxX < MapWidth - 1 && bounds.maxZ < MapHeight - 1;
        }

        /// <summary>
        /// The widest room the planner can produce, **asked of the planner rather than rebuilt
        /// here.**
        ///
        /// This used to compute `SlotRoomSpan(SlotSpacing(MinSlotsPerAxis))`, which is the span
        /// of a room that fills one slot exactly. It was a true sentence when it was written and
        /// stopped being one the moment the planner gained a two-slot grand hall and a varied
        /// span: the ceiling said 34 while the hall was 80, so **every candidate layout was
        /// refused and no coordinate could generate at all.**
        ///
        /// See <see cref="RoomLayoutPlanner.WidestRoomSpan"/> for the whole account. The rule
        /// stays enforced here -- a room wider than the planner can produce is still a refusal --
        /// but the number comes from the one place that knows it.
        /// </summary>
        private static int MaxRoomSpan
        {
            get { return RoomLayoutPlanner.WidestRoomSpan; }
        }

        /// <summary>
        /// Whether a link between these two rooms is one a corridor can actually be built for.
        ///
        /// **The literal 19 is gone.** It was the old fixed slot spacing, and the spacing is a
        /// function of depth now -- a validator carrying a constant the planner no longer uses is
        /// the same defect class as the light count. The requirement the corridor builder really
        /// has is this: the centres share a row or a column, and the bounds do not overlap, so
        /// there is a straight run of rock between them to carve.
        /// </summary>
        /// <summary>
        /// Whether a saved graph's link is a shape a corridor can join — **and it is now the
        /// planner's own answer rather than a copy of it.**
        ///
        /// This held its own arithmetic (`a.x == b.x` or `a.z == b.z`, centres only) while
        /// `RoomLayoutPlanner.AreNeighbourRooms` held the identical arithmetic separately. **Two
        /// independent derivations of one rule, which is the defect that cost this project
        /// thirty-nine checkpoints** — and it was live: the planner's half had to grow to admit
        /// bent corridors and the generalised straight run, and had this not been collapsed the
        /// validator would have refused every graph the planner had just learned to build, on
        /// load, for every saved coordinate.
        ///
        /// So the planner decides and this asks. The question is still the right one for a
        /// validator: a graph edge whose two rooms no corridor can join is a graph that cannot be
        /// carved, whatever produced it.
        /// </summary>
        private static bool AreGridNeighbors(RoomRecord first, RoomRecord second)
        {
            return RoomLayoutPlanner.AreNeighbourRooms(first, second);
        }

        private static PlanetTile FindUniqueTile(CoordinateRecord coordinate)
        {
            PlanetLayer surface = Find.WorldGrid.Surface;
            if (surface == null || surface.TilesCount < 1) { return PlanetTile.Invalid; }
            int count = surface.TilesCount;
            int start = StableHash(coordinate.Seed, coordinate.Id + ":world-owner", coordinate.GeneratorVersion) % count;
            int stride = FindCoprimeStride(count);
            PlanetTile firstValidFallback = PlanetTile.Invalid;
            int candidatesToCheck = Math.Min(count, WorldTileCandidateBudget);
            for (int offset = 0; offset < candidatesToCheck; offset++)
            {
                int tileIndex = (int)(((long)start + (long)offset * stride) % count);
                PlanetTile candidate = new PlanetTile(tileIndex, surface);
                if (!candidate.Valid || Find.WorldObjects.AnyWorldObjectAt(candidate) ||
                    Current.Game.FindMap(candidate) != null || !TileFinder.IsValidTileForNewSettlement(candidate))
                {
                    continue;
                }

                if (!firstValidFallback.Valid) { firstValidFallback = candidate; }
                Tile tile = Find.WorldGrid[candidate];
                if (tile.PrimaryBiome != null && PreferredBiomeNames.Contains(tile.PrimaryBiome.defName))
                {
                    return candidate;
                }
            }
            // Temperate forest/swamp sites are preferred, but any Core-approved,
            // unoccupied land tile in the bounded sample is an acceptable fallback.
            return firstValidFallback;
        }

        private static int FindCoprimeStride(int tileCount)
        {
            if (tileCount <= 1) { return 1; }
            int stride = tileCount / 2 + 1;
            while (GreatestCommonDivisor(stride, tileCount) != 1)
            {
                stride++;
                if (stride >= tileCount) { stride = 1; }
            }
            return stride;
        }

        private static int GreatestCommonDivisor(int first, int second)
        {
            while (second != 0)
            {
                int remainder = first % second;
                first = second;
                second = remainder;
            }
            return Math.Abs(first);
        }

        internal static int StableHash(int seed, string key, int version)
        {
            unchecked
            {
                uint hash = 2166136261;
                hash = (hash ^ (uint)seed) * 16777619;
                hash = (hash ^ (uint)version) * 16777619;
                foreach (char character in key ?? string.Empty) { hash = (hash ^ character) * 16777619; }
                return (int)(hash & 0x7fffffff);
            }
        }

        private static void Mix(ref uint hash, int value)
        {
            unchecked
            {
                hash = (hash ^ (uint)value) * 16777619;
                hash = (hash ^ (uint)(value >> 16)) * 16777619;
            }
        }

        private static void Mix(ref uint hash, string value)
        {
            foreach (char character in value ?? string.Empty) { hash = (hash ^ character) * 16777619; }
            hash = (hash ^ 0xff) * 16777619;
        }

        private static bool ValidateCell(Map map, IntVec3 cell)
        {
            return cell.IsValid && cell.InBounds(map) && cell.Standable(map);
        }

        internal static bool CanTraverseRouteCell(Map map, IntVec3 cell)
        {
            if (!cell.InBounds(map)) { return false; }
            if (cell.Standable(map)) { return true; }
            Building_Door door = cell.GetEdifice(map) as Building_Door;
            return door != null && cell.Walkable(map) && !door.IsForbidden(Faction.OfPlayer) &&
                (door.Faction == Faction.OfPlayer || door.Faction == null);
        }

        private static bool Reachable(Map map, IntVec3 start, IntVec3 target)
        {
            if (!ValidateCell(map, start) || !ValidateCell(map, target)) { return false; }
            var seen = new HashSet<IntVec3>();
            var pending = new Queue<IntVec3>();
            pending.Enqueue(start);
            seen.Add(start);
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            while (pending.Count > 0)
            {
                IntVec3 current = pending.Dequeue();
                if (current == target) { return true; }
                foreach (IntVec3 direction in directions)
                {
                    IntVec3 next = current + direction;
                    if (CanTraverseRouteCell(map, next) && seen.Add(next)) { pending.Enqueue(next); }
                }
            }
            return false;
        }

        private static CompanyActionResult Fail(CoordinateRecord coordinate, RimroomsDestinationMapParent parent, string key)
        {
            if (coordinate != null)
            {
                coordinate.status = CoordinateStatus.Unavailable;
            }
            if (parent != null)
            {
                parent.MarkGenerationFailed(key);
                key = parent.GenerationFailureKey ?? key;
                if (coordinate != null) { coordinate.lastFailureKey = key; }
            }
            else if (coordinate != null) { coordinate.lastFailureKey = key; }
            return CompanyActionResult.Refused(key);
        }
    }
}
