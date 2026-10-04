using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    // Original arrangements of native runtime Defs. No source or assets from Core are redistributed.
    internal static class RoomContentBuilder
    {
        internal const int ContentVersion = 4;

        internal static void Populate(Map map, CoordinateRecord coordinate, IntVec3 entry, IntVec3 returnCell,
            IntVec3 officeEvidence, Thing anchor)
        {
            RoomContentMapComponent content = map.GetComponent<RoomContentMapComponent>();
            if (!content.BeginPopulation(coordinate.Id, ContentVersion))
            { throw new InvalidOperationException("RR_Generation_ContentAlreadyStarted"); }
            var reserved = new HashSet<IntVec3> { entry, returnCell, officeEvidence };
            foreach (IntVec3 cell in anchor.OccupiedRect().ExpandedBy(1).Cells) { reserved.Add(cell); }
            foreach (RoomRecord room in coordinate.Rooms)
            {
                // Keep the whole three-cell route cross clear. The existing center support remains.
                foreach (IntVec3 cell in room.Bounds.Cells)
                { if (OnRouteCross(room, cell)) { reserved.Add(cell); } }
            }
            foreach (RoomRecord room in coordinate.Rooms.OrderBy(r => r.index))
            {
                int seed = DestinationService.StableHash(coordinate.Seed, coordinate.Id + ":content:" + room.index, ContentVersion);
                int variant = seed % 3;
                Rand.PushState(seed);
                try
                {
                    PaintRoom(map, room, variant, coordinate.Depth, seed);
                    Thing landmark;
                    bool salvage = false;
                    switch (room.familyId)
                    {
                        case "threshold_room":
                            landmark = Place(map, room, coordinate, "Stool", reserved, seed, 0);
                            Decorate(map, room, coordinate, "Stool", reserved, seed, 1);
                            break;
                        case "survey_lobby":
                            landmark = Place(map, room, coordinate, "Table1x2c", reserved, seed, 0);
                            Decorate(map, room, coordinate, "DiningChair", reserved, seed, 1);
                            Decorate(map, room, coordinate, "PlantPot", reserved, seed, 2);
                            break;
                        case "office_copy":
                            landmark = Place(map, room, coordinate, "Table1x2c", reserved, seed, 0);
                            Decorate(map, room, coordinate, "DiningChair", reserved, seed, 1);
                            Decorate(map, room, coordinate, "Table1x2c", reserved, seed, 2);
                            Decorate(map, room, coordinate, "DiningChair", reserved, seed, 3);
                            if (variant == 2) { Decorate(map, room, coordinate, "PlantPot", reserved, seed, 4); }
                            break;
                        case "service_passage":
                            landmark = Place(map, room, coordinate, "Shelf", reserved, seed, 0);
                            Decorate(map, room, coordinate, "StandingLamp", reserved, seed, 1);
                            break;
                        case "borrowed_corridor":
                            landmark = Place(map, room, coordinate, "PlantPot", reserved, seed, 0);
                            Decorate(map, room, coordinate, "PlantPot", reserved, seed, 1);
                            break;
                        case "storage_nook":
                            Decorate(map, room, coordinate, "Shelf", reserved, seed, 0);
                            landmark = variant == 0 ? Place(map, room, coordinate, "Steel", reserved, seed, 1, false, 12) :
                                Place(map, room, coordinate, variant == 1 ? "Stool" : "DiningChair", reserved, seed, 1, true);
                            salvage = true;
                            break;
                        case "utility_room":
                            landmark = Place(map, room, coordinate, "StandingLamp", reserved, seed, 0);
                            Decorate(map, room, coordinate, "Stool", reserved, seed, 1);
                            break;
                        case "sealed_vault":
                            // **NOBODY HAS BEEN IN HERE**, which is the whole point of it: the
                            // room has no links and the only way in is a pick. Owner: *"insentive
                            // to mine things out to find isolated undiscorvered rooms"*. So it is
                            // dressed as a find rather than as a room somebody left -- a shelf
                            // with something still on it, and nothing arranged for sitting.
                            Decorate(map, room, coordinate, "Shelf", reserved, seed, 0);
                            landmark = variant == 0
                                ? Place(map, room, coordinate, "Steel", reserved, seed, 1, false, 35)
                                : Place(map, room, coordinate, variant == 1 ? "Gold" : "Plasteel",
                                    reserved, seed, 1, false, variant == 1 ? 20 : 15);
                            salvage = true;
                            break;
                        case "return_gallery":
                            landmark = Place(map, room, coordinate, "Stool", reserved, seed, 0);
                            Decorate(map, room, coordinate, "Stool", reserved, seed, 1);
                            if (variant != 0) { Decorate(map, room, coordinate, "PlantPot", reserved, seed, 2); }
                            break;
                        default: throw new InvalidOperationException("RR_Generation_InvalidRoomGraph");
                    }
                    // Deeper coordinates are dressed as a KIND of room on top of their
                    // structural family -- a laboratory, a workshop, a nursery. Depth 1
                    // is skipped inside Select, because the shallow yellow rooms stay
                    // sparse and that emptiness is the look.
                    //
                    // Dressing runs AFTER the family fixtures and the landmark, and
                    // never throws: the clue system, the power validation and the route
                    // cross all depend on what came before it, so decoration is not
                    // allowed to fail a generation that had already succeeded.
                    // "Quiet stretches are required content" -- a coordinate with something
                    // in every room fails the owner's direction however good each room is.
                    // The quiet rooms are chosen from the coordinate's own seed and by a
                    // count rather than by chance, so an unlucky run of rolls can never
                    // produce a space that presents something everywhere.
                    bool quiet = Threats.CoordinatePressureLadder.IsQuietRoom(
                        coordinate.Seed, room.index, coordinate.Rooms.Count);
                    if (!quiet) { DressRoom(map, room, coordinate, seed, reserved); }
                    content.AddClue(coordinate.Id, room, landmark, variant, salvage);
                }
                finally { Rand.PopState(); }
            }
            content.CompletePopulation();
        }

        /// <summary>
        /// The three-cell walk through the middle of a room, both ways, which nothing is ever
        /// placed on.
        ///
        /// **This is what actually keeps a room walkable**, and it is why the margin around a
        /// fixture can be a preference rather than a requirement -- see
        /// <see cref="FixtureCell"/>. Every doorway sits at the midpoint of a wall, so a clear
        /// cross from midpoint to midpoint is a clear walk between any two of them.
        ///
        /// **Exposed because the layout probe counts against it.** A room whose cross, pillars
        /// and rock between them leave no cell at all cannot take a landmark, and that failure
        /// aborted a whole level once. The probe asks this rather than re-deriving it; a second
        /// copy of a one-line rule is still a second derivation.
        /// </summary>
        internal static bool OnRouteCross(RoomRecord room, IntVec3 cell)
        {
            IntVec3 center = room.Bounds.CenterCell;
            return Math.Abs(cell.x - center.x) <= 1 || Math.Abs(cell.z - center.z) <= 1;
        }

        private static void PaintRoom(Map map, RoomRecord room, int variant, int depth, int seed)
        {
            bool utility = room.familyId == "service_passage" || room.familyId == "utility_room";
            // The look is chosen by how deep the coordinate sits rather than by a global
            // constant, because the owner's direction has two halves: the yellow carpet and
            // yellow wood walls are "the main backrooms look", and "further in it gets very
            // varied and weird". Depth 1 is always the yellow rooms; deeper bands diverge.
            BackroomsPalette.Look look = BackroomsPalette.For(depth, seed);
            TerrainDef baseFloor = look.floor;
            TerrainDef accent = look.accent;
            if (accent == null || baseFloor == null) { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }
            foreach (IntVec3 cell in room.Bounds.Cells)
            {
                Thing wall = cell.GetEdifice(map);
                if (wall != null && wall.def == ThingDefOf.Wall)
                {
                    // Utility spaces stay a shade off the room palette so the two read apart
                    // without relying on colour alone -- the stripe pattern below is the
                    // non-colour cue.
                    Color tint = look.wallColor;
                    if (utility) { tint = new Color(tint.r * 0.78f, tint.g * 0.82f, tint.b * 0.86f); }
                    wall.TryGetComp<CompColorable>()?.SetColor(tint);
                }
            }
            foreach (IntVec3 cell in room.Bounds.ContractedBy(1).Cells)
            {
                // Original floor inset/stripes establish room differences without a color-only cue.
                bool stripe = variant == 0 ? (cell.x - room.x) % 4 == 0 : variant == 1 ? (cell.z - room.z) % 4 == 0 :
                    cell.x == room.x + 2 || cell.z == room.z + 2 || cell.x == room.Bounds.maxX - 2 || cell.z == room.Bounds.maxZ - 2;
                BackroomsPalette.SetFloor(map, cell, stripe ? accent : baseFloor, look.floorColor);
            }
        }

        /// <summary>
        /// Dresses a room as a kind of place, using whatever the loaded game offers for each
        /// capability slot.
        ///
        /// Every failure here is silent by design. A slot nothing answers is skipped, a fixture
        /// that will not fit is skipped, and a room that ends up bare is a bare room. The
        /// alternative -- failing generation because a decorative shelf had nowhere to go --
        /// would take a working coordinate away from a player over scenery.
        /// </summary>
        private static void DressRoom(Map map, RoomRecord room, CoordinateRecord coordinate, int seed,
            HashSet<IntVec3> reserved)
        {
            int depth = coordinate.Depth;
            // Owner direction: "facilitys". A room inside a facility is dressed as whatever
            // its group is, not as its own roll, which is what turns three rooms into a
            // laboratory wing instead of three rooms that each happen to have a bench.
            // Resolving through the anchor means every member asks the same question and gets
            // the same answer, with nothing stored to fall out of step with the graph.
            int anchor = FacilityPlanner.AnchorFor(coordinate, room.index);
            RoomRecord dresser = room;
            if (anchor >= 0 && anchor != room.index)
            {
                for (int index = 0; index < coordinate.Rooms.Count; index++)
                {
                    RoomRecord candidate = coordinate.Rooms[index];
                    if (candidate != null && candidate.Index == anchor) { dresser = candidate; break; }
                }
            }
            // **Distance from the spawn hall counts as depth.** A room beside the hall is
            // dressed as the shallow yellow rooms always were; one a dozen links out is dressed
            // like somewhere several levels down. Owner: *"variations and oddity and events and
            // locations and places that vary more even on the first level"*.
            int dressingDepth = RoomArchetypeService.EffectiveDepth(coordinate, dresser, depth);
            RimroomsRoomArchetypeDef archetype =
                RoomArchetypeService.Select(dresser.familyId, dressingDepth, seed, dresser.index);
            if (archetype == null || archetype.slots == null) { return; }

            // Slots start well past the family fixtures' slot indices so the quadrant spread
            // does not stack dressing on top of the landmark.
            int slotIndex = 8;
            for (int index = 0; index < archetype.slots.Count; index++)
            {
                RoomFurnitureSlot slot = archetype.slots[index];
                if (!RoomArchetypeService.SlotAppears(slot, seed, index)) { continue; }
                ThingDef definition = RoomArchetypeService.Resolve(archetype, slot, seed, index, dressingDepth);
                if (definition == null) { continue; }

                int wanted = RoomArchetypeService.SlotCount(slot, seed, index);
                for (int made = 0; made < wanted; made++)
                {
                    int stack = 1;
                    if (definition.category == ThingCategory.Item)
                    {
                        int low = Math.Max(1, slot.stackCount.min);
                        int high = Math.Max(low, slot.stackCount.max);
                        stack = Math.Min(definition.stackLimit, low + (seed + made) % (high - low + 1));
                    }
                    Thing placed = TryPlace(map, room, coordinate, definition, reserved, seed + made * 7,
                        slotIndex++, slot.minified && definition.Minifiable, stack);
                    if (placed == null) { break; }
                }
            }
        }

        /// <summary>
        /// Places a fixture and returns null instead of throwing when it cannot.
        ///
        /// Deliberately a separate method rather than a flag on <see cref="Place"/>: the
        /// required content genuinely must fail generation loudly if it cannot be placed,
        /// because the clue system and the saved layout depend on it, and a shared code path
        /// with a "do not throw" switch is exactly how that guarantee gets lost later.
        /// </summary>
        /// <summary>
        /// Where a fixture would like to stand: anywhere in the room, not a corner.
        ///
        /// Owner, after walking the first level: *"the furnature is only in the four corners of
        /// the rooms that nots very random"*. **They were reading the code off the screen.** The
        /// anchor used to be one of exactly four cells -- each corner inset by two -- and every
        /// candidate cell was sorted by distance to it, so four slots cycling four quadrants
        /// filled the corners and left the middle bare.
        ///
        /// Deterministic, because a coordinate has to be the same place on every visit: drawn
        /// from the same seed and slot the rest of the placement already uses.
        ///
        /// **This only moves where the search starts.** The caller still walks every cell in the
        /// room, so a cramped room places exactly what it placed before.
        /// </summary>
        private static IntVec3 ScatterAnchor(RoomRecord room, int seed, int slot)
        {
            CellRect inner = room.Bounds.ContractedBy(2);
            if (inner.Width < 1 || inner.Height < 1) { inner = room.Bounds.ContractedBy(1); }
            if (inner.Width < 1 || inner.Height < 1) { return room.Bounds.CenterCell; }
            return new IntVec3(inner.minX + Scatter(seed, slot, "x", inner.Width), 0,
                inner.minZ + Scatter(seed, slot, "z", inner.Height));
        }

        /// <summary>A stable non-negative draw below <paramref name="bound"/>.</summary>
        private static int Scatter(int seed, int slot, string key, int bound)
        {
            if (bound < 1) { return 0; }
            int derived = Company.CampaignSeed.Derive(seed, key + ":" + slot, 1);
            if (derived < 0) { derived = -derived; }
            return derived % bound;
        }

        private static Thing TryPlace(Map map, RoomRecord room, CoordinateRecord coordinate,
            ThingDef definition,
            HashSet<IntVec3> reserved, int seed, int slot, bool minified, int count)
        {
            if (definition == null || count < 1) { return null; }
            if (count > definition.stackLimit) { count = definition.stackLimit; }
            Thing thing;
            try
            {
                // **The palette reaches the dressing now, and this was the worst of the three
                // gaps.** This path places the depth-scaled archetype dressing -- the benches,
                // the equipment, the loot, everything the owner means by *"found everywher deeper
                // in"* -- and it was taking Core's default material while the family fixtures a
                // few lines below took the coordinate's palette. So the content that was supposed
                // to vary was the one content that could not.
                //
                // StuffFor falls back to GenStuff.DefaultStuffFor when the palette has nothing
                // this fixture can be made of, so this is strictly wider than what it replaces.
                // The variant is what lets two identical fixtures in one room be different
                // materials deeper in. Built from the slot and the placement seed, both of which
                // are already deterministic per coordinate.
                thing = ThingMaker.MakeThing(definition,
                    CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));
                if (thing == null) { return null; }
                thing.TryGetComp<CompQuality>()?.SetQuality(QualityCategory.Normal, ArtGenerationContext.Outsider);
                if (definition.useHitPoints)
                { thing.HitPoints = Math.Max(1, (int)(thing.MaxHitPoints * (0.55f + (seed % 5) * 0.07f))); }
                if (minified)
                {
                    thing = thing.MakeMinified();
                    if (thing == null) { return null; }
                }
                thing.stackCount = count;
            }
            catch (Exception)
            {
                // A definition from an unknown mod can refuse to be made for reasons this mod
                // cannot anticipate. That is a skipped decoration, not a broken coordinate.
                return null;
            }

            IntVec3 preferred = ScatterAnchor(room, seed, slot);
            // All four facings, not two. A room where everything faces north or south reads
            // as arranged; the Backrooms are not arranged.
            Rot4 rotation = new Rot4(Scatter(seed, slot, "facing", 4));
            IntVec3 cell = FixtureCell(map, room, reserved, thing, rotation, preferred, null);
            if (!cell.IsValid) { return null; }
            GenSpawn.Spawn(thing, cell, map, rotation);
            if (!thing.Spawned || thing.Map != map) { return null; }
            thing.SetForbidden(false, false);
            return thing;
        }

        /// <summary>
        /// A cell in this room that will take this footprint: one with a walkable margin around
        /// it if there is one, and one without if there is not.
        ///
        /// ## Why the margin has to be a preference and not a requirement
        ///
        /// **A room with no margined cell aborted the whole level.** The margin rule refuses any
        /// cell whose footprint has an edifice within one, and every one of these is an edifice:
        /// the room's own perimeter wall, the pillar lattice, the rock left standing in the
        /// shaped corners, **and every fixture already placed in the room.** On top of that
        /// `Populate` reserves the three-cell route cross outright.
        ///
        /// So in a room at the minimum eight cells across, the margin and the reserved cross
        /// between them leave **exactly one** placeable cell -- and a family that places two
        /// fixtures took it with the first and threw on the second. 0.12.61-dev made that
        /// reachable at depth 1 for the first time, by varying room spans and letting `Derange`
        /// cut hallways on a first level.
        ///
        /// The throw reached `GenStep.Generate`, so **the level stopped being built halfway**:
        /// the owner got a Backrooms map with no finished content, `EnsureSite` reported failure,
        /// and `SoloGroupOpening` never marked the door or registered the edge. Their report was
        /// *"i see the backrooms is there but the gate natural door is not"* -- a furniture
        /// placement rule, two steps removed.
        ///
        /// **The margin was never what keeps the room walkable.** The reserved route cross is,
        /// and it is reserved separately and unconditionally. So a cell without a margin is a
        /// fixture against a wall, which is what furniture against a wall looks like.
        ///
        /// **One function, three callers.** `TryPlace` had its own copy of this loop; now it asks
        /// here, because two derivations of one rule is the defect this project keeps meeting.
        /// </summary>
        private static IntVec3 FixtureCell(Map map, RoomRecord room, HashSet<IntVec3> reserved,
            Thing thing, Rot4 rotation, IntVec3 preferred, HashSet<IntVec3> approach)
        {
            CellRect interior = room.Bounds.ContractedBy(1);
            IntVec3 withoutMargin = IntVec3.Invalid;
            foreach (IntVec3 cell in interior.Cells
                .OrderBy(c => c.DistanceToSquared(preferred)).ThenBy(c => c.x).ThenBy(c => c.z))
            {
                CellRect footprint = GenAdj.OccupiedRect(cell, rotation, thing.def.size);
                if (footprint.Cells.Any(c => !interior.Contains(c) || reserved.Contains(c) ||
                    !c.Standable(map) || c.GetEdifice(map) != null || c.GetFirstItem(map) != null))
                { continue; }
                // A landmark has to keep a way up to it; see RouteTrunk. Null for everything
                // else, which places exactly where it placed before.
                if (approach != null && !TouchesApproach(footprint, approach)) { continue; }
                // Keep a walkable margin around each fixture where the room allows one.
                if (!footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))
                { return cell; }
                // The first acceptable cell without a margin, kept in case nothing better turns
                // up. Still the one nearest the scatter anchor, because the ordering is the same.
                if (!withoutMargin.IsValid) { withoutMargin = cell; }
            }
            return withoutMargin;
        }

        /// <summary>
        /// Whether a cell in <paramref name="approach"/> lies orthogonally beside this footprint.
        ///
        /// Orthogonally, because that is the test `ValidatePlacedLayout` applies to a clue
        /// landmark -- `|dx| + |dz| == 1` against a footprint cell. A diagonal neighbour is not
        /// an approach there, so it is not one here either; two derivations of one rule is the
        /// defect this project keeps meeting.
        /// </summary>
        private static bool TouchesApproach(CellRect footprint, HashSet<IntVec3> approach)
        {
            foreach (IntVec3 cell in footprint.ExpandedBy(1).Cells)
            {
                if (!approach.Contains(cell)) { continue; }
                foreach (IntVec3 part in footprint.Cells)
                {
                    if (Math.Abs(cell.x - part.x) + Math.Abs(cell.z - part.z) == 1) { return true; }
                }
            }
            return false;
        }

        /// <summary>
        /// The part of the room's reserved route cross that is clear and joined up.
        ///
        /// ## Why the landmark has to touch this, and why that is new
        ///
        /// `ValidatePlacedLayout` requires every clue landmark to have a standable,
        /// entry-reachable cell orthogonally beside it, and **nothing was keeping one.** Every
        /// landmark this builder places is `PassThroughOnly`, so the landmark's own cell never
        /// counts and the approach is always a neighbour.
        ///
        /// Two correct decisions met and left a hole between them. `FixtureCell` relaxed its
        /// margin from a requirement to a preference -- rightly, because requiring one aborted
        /// whole levels -- and `DressRoom` places fixtures until one will not fit, so **the last
        /// cells it takes are the no-margin cells flush against whatever is already there.**
        /// Including every neighbour of the landmark. Dressing sixteen archetypes with loot at
        /// 0.12.69-dev is what made a room dense enough to reach that point.
        ///
        /// That is what stopped the owner's solo/group start: `RR_Generation_UnreachableRequiredCell`
        /// from the clue loop, so the level was never finished, so `EnsureSite` reported failure,
        /// so `SoloGroupOpening` never moved anybody inside and never registered the way out.
        /// Their report was *"i ended up in the world map with no connection to the back rooms"*
        /// -- a furniture placement rule, four steps removed.
        ///
        /// **The margin was never what kept a room walkable**, and `FixtureCell` says so and is
        /// right. It was read one step too far: the reserved cross keeps the ROOM walkable and
        /// says nothing about the landmark's own approach, which is off the cross by
        /// construction, because cross cells are reserved.
        ///
        /// So the approach is taken from the cross itself. Those cells are reserved outright and
        /// stay clear for the rest of generation, so a landmark beside one **cannot** be sealed
        /// in by anything placed later. The guarantee is structural rather than lucky.
        ///
        /// **Joined up, not merely on the cross.** A pillar or a stand of shaped rock can sever
        /// an arm, and a cell in a severed arm is standable and unreachable -- exactly the pair
        /// of properties the validator rejects. This walks out from the middle, so only cells
        /// continuous with the room's own trunk are offered.
        ///
        /// Empty when the room has no clear cross at all, and the caller then places the landmark
        /// the way it always did: refusing one would abort the level, which is the thing being
        /// fixed here.
        /// </summary>
        private static HashSet<IntVec3> RouteTrunk(Map map, RoomRecord room)
        {
            CellRect interior = room.Bounds.ContractedBy(1);
            var trunk = new HashSet<IntVec3>();
            IntVec3 start = interior.Cells
                .Where(cell => OnRouteCross(room, cell) && ClearTrunkCell(map, cell))
                .OrderBy(cell => cell.DistanceToSquared(room.Bounds.CenterCell))
                .ThenBy(cell => cell.x).ThenBy(cell => cell.z)
                .FirstOrDefault();
            if (!start.IsValid || !interior.Contains(start)) { return trunk; }

            var pending = new Queue<IntVec3>();
            trunk.Add(start);
            pending.Enqueue(start);
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            while (pending.Count > 0)
            {
                IntVec3 current = pending.Dequeue();
                for (int index = 0; index < directions.Length; index++)
                {
                    IntVec3 next = current + directions[index];
                    if (!interior.Contains(next) || !OnRouteCross(room, next)) { continue; }
                    if (!ClearTrunkCell(map, next) || !trunk.Add(next)) { continue; }
                    pending.Enqueue(next);
                }
            }
            return trunk;
        }

        /// <summary>
        /// A cross cell nothing is standing in. Asked of the map rather than of the reserved set,
        /// because the thing that disqualifies a cross cell is a pillar or the rock left in a
        /// shaped corner, and neither of those is reserved -- they were built.
        /// </summary>
        private static bool ClearTrunkCell(Map map, IntVec3 cell)
        {
            return cell.InBounds(map) && cell.Standable(map) && cell.GetEdifice(map) == null;
        }

        /// <summary>
        /// The room's landmark: the one fixture that has to exist, because
        /// <c>RoomContentMapComponent.AddClue</c> is handed it and the investigation chain reads
        /// it. Refused loudly if it cannot be placed.
        /// </summary>
        private static Thing Place(Map map, RoomRecord room, CoordinateRecord coordinate,
            string defName, HashSet<IntVec3> reserved,
            int seed, int slot, bool minified = false, int count = 1)
        {
            return PlaceFixture(map, room, coordinate, defName, reserved, seed, slot, minified,
                count, true);
        }

        /// <summary>
        /// Everything else in the room, and **a fixture that will not fit is simply not there.**
        ///
        /// This is `DressRoom`'s rule, applied where it was always missing. That method says it
        /// out loud -- *"a fixture that will not fit is skipped, and a room that ends up bare is
        /// a bare room. The alternative -- failing generation because a decorative shelf had
        /// nowhere to go -- would take a working coordinate away from a player over scenery"* --
        /// and then the family fixtures a few lines above it did exactly that.
        ///
        /// A second stool is a second stool. The clue is the landmark, the route is the reserved
        /// cross, and the power network is routed to whatever is actually there. **Nothing
        /// downstream counts these.**
        /// </summary>
        private static Thing Decorate(Map map, RoomRecord room, CoordinateRecord coordinate,
            string defName, HashSet<IntVec3> reserved,
            int seed, int slot, bool minified = false, int count = 1)
        {
            return PlaceFixture(map, room, coordinate, defName, reserved, seed, slot, minified,
                count, false);
        }

        private static Thing PlaceFixture(Map map, RoomRecord room, CoordinateRecord coordinate,
            string defName, HashSet<IntVec3> reserved,
            int seed, int slot, bool minified, int count, bool required)
        {
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (definition == null || count < 1 || count > definition.stackLimit)
            { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }
            // Row 1005. This was `definition.MadeFromStuff ? ThingDefOf.WoodLog : null`, which
            // made every stuffable fixture on every coordinate in the game wooden -- not the
            // def's own default, one hardcoded material. The palette is per coordinate and
            // derived from its seed, so a coordinate looks like somewhere and two coordinates
            // look different. See CoordinateMaterials.
            Thing thing = ThingMaker.MakeThing(definition,
                CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));
            thing.TryGetComp<CompQuality>()?.SetQuality(QualityCategory.Normal, ArtGenerationContext.Outsider);
            if (definition.useHitPoints) { thing.HitPoints = Math.Max(1, (int)(thing.MaxHitPoints * (0.65f + (seed % 4) * 0.08f))); }
            if (minified)
            {
                if (!definition.Minifiable) { throw new InvalidOperationException("RR_Generation_InvalidSalvageDef"); }
                thing = thing.MakeMinified();
                if (thing == null) { throw new InvalidOperationException("RR_Generation_InvalidSalvageDef"); }
            }
            thing.stackCount = count;
            IntVec3 preferred = ScatterAnchor(room, seed, slot);
            // All four facings, not two. A room where everything faces north or south reads
            // as arranged; the Backrooms are not arranged.
            Rot4 rotation = new Rot4(Scatter(seed, slot, "facing", 4));
            // **The landmark keeps a way up to it, and only the landmark needs one**: the clue
            // chain reads it and `ValidatePlacedLayout` demands a standable, reachable cell
            // orthogonally beside it. See RouteTrunk for what that cost the owner.
            //
            // Asked FIRST and fallen back from, never refused on: a cross-adjacent cell if the
            // room has one, otherwise wherever the landmark would have gone anyway. This can
            // move a landmark; it can never fail to place one that would have been placed.
            HashSet<IntVec3> trunk = required ? RouteTrunk(map, room) : null;
            IntVec3 cell = FixtureCell(map, room, reserved, thing, rotation, preferred,
                trunk != null && trunk.Count > 0 ? trunk : null);
            if (!cell.IsValid && trunk != null && trunk.Count > 0)
            { cell = FixtureCell(map, room, reserved, thing, rotation, preferred, null); }
            if (!cell.IsValid)
            {
                // Do not reroll or remove earlier placed content after a surprising runtime
                // Def/footprint failure. The landmark is refused loudly because the clue chain
                // reads it -- `ValidatePlacedLayout` requires exactly one clue per room -- and a
                // decoration is simply absent.
                if (required)
                {
                    // **SAY WHICH ROOM.** The last time this threw, the log carried the method
                    // and the key and nothing else, so the room it happened in had to be
                    // reasoned about from the arithmetic of every room it could have been. One
                    // line here is the difference between that and an answer.
                    Log.Warning("[Rimrooms][Generation] No cell for the landmark " + defName
                                + " in room " + room.index + " (" + room.familyId + ", "
                                + room.width + "x" + room.height + " at " + room.Bounds.CenterCell
                                + ") of a depth " + coordinate.Depth + " coordinate.");
                    throw new InvalidOperationException("RR_Generation_NoSafeRoomCell");
                }
                return null;
            }
            GenSpawn.Spawn(thing, cell, map, rotation);
            if (!thing.Spawned || thing.Map != map) { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
            thing.SetForbidden(false, false);
            // **And nothing else goes beside the landmark.** The same thing `Populate` already
            // does for the gate anchor, for the same reason: the ring it was placed with is the
            // ring it keeps. Without this, a cross-adjacent landmark still survives -- cross
            // cells are reserved -- but a landmark that had to fall back off the cross would be
            // sealed in by the next fixture that ran out of margined cells. Decorations are
            // allowed to be absent; a clue is not allowed to be unreachable.
            if (required)
            {
                foreach (IntVec3 ring in thing.OccupiedRect().ExpandedBy(1).Cells)
                { reserved.Add(ring); }
            }
            return thing;
        }
    }
}
