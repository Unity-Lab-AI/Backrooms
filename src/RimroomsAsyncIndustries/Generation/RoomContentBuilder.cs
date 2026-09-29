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
                IntVec3 center = room.Bounds.CenterCell;
                // Keep the whole three-cell route cross clear. The existing center support remains.
                foreach (IntVec3 cell in room.Bounds.Cells)
                { if (Math.Abs(cell.x - center.x) <= 1 || Math.Abs(cell.z - center.z) <= 1) { reserved.Add(cell); } }
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
                            landmark = Place(map, room, "Stool", reserved, seed, 0);
                            Place(map, room, "Stool", reserved, seed, 1);
                            break;
                        case "survey_lobby":
                            landmark = Place(map, room, "Table1x2c", reserved, seed, 0);
                            Place(map, room, "DiningChair", reserved, seed, 1);
                            Place(map, room, "PlantPot", reserved, seed, 2);
                            break;
                        case "office_copy":
                            landmark = Place(map, room, "Table1x2c", reserved, seed, 0);
                            Place(map, room, "DiningChair", reserved, seed, 1);
                            Place(map, room, "Table1x2c", reserved, seed, 2);
                            Place(map, room, "DiningChair", reserved, seed, 3);
                            if (variant == 2) { Place(map, room, "PlantPot", reserved, seed, 4); }
                            break;
                        case "service_passage":
                            landmark = Place(map, room, "Shelf", reserved, seed, 0);
                            Place(map, room, "StandingLamp", reserved, seed, 1);
                            break;
                        case "borrowed_corridor":
                            landmark = Place(map, room, "PlantPot", reserved, seed, 0);
                            Place(map, room, "PlantPot", reserved, seed, 1);
                            break;
                        case "storage_nook":
                            Place(map, room, "Shelf", reserved, seed, 0);
                            landmark = variant == 0 ? Place(map, room, "Steel", reserved, seed, 1, false, 12) :
                                Place(map, room, variant == 1 ? "Stool" : "DiningChair", reserved, seed, 1, true);
                            salvage = true;
                            break;
                        case "utility_room":
                            landmark = Place(map, room, "StandingLamp", reserved, seed, 0);
                            Place(map, room, "Stool", reserved, seed, 1);
                            break;
                        case "return_gallery":
                            landmark = Place(map, room, "Stool", reserved, seed, 0);
                            Place(map, room, "Stool", reserved, seed, 1);
                            if (variant != 0) { Place(map, room, "PlantPot", reserved, seed, 2); }
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
                    if (!quiet) { DressRoom(map, room, coordinate.Depth, seed, reserved); }
                    content.AddClue(coordinate.Id, room, landmark, variant, salvage);
                }
                finally { Rand.PopState(); }
            }
            content.CompletePopulation();
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
        private static void DressRoom(Map map, RoomRecord room, int depth, int seed,
            HashSet<IntVec3> reserved)
        {
            RimroomsRoomArchetypeDef archetype = RoomArchetypeService.Select(room.familyId, depth, seed, room.index);
            if (archetype == null || archetype.slots == null) { return; }

            // Slots start well past the family fixtures' slot indices so the quadrant spread
            // does not stack dressing on top of the landmark.
            int slotIndex = 8;
            for (int index = 0; index < archetype.slots.Count; index++)
            {
                RoomFurnitureSlot slot = archetype.slots[index];
                if (!RoomArchetypeService.SlotAppears(slot, seed, index)) { continue; }
                ThingDef definition = RoomArchetypeService.Resolve(archetype, slot, seed, index, depth);
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
                    Thing placed = TryPlace(map, room, definition, reserved, seed + made * 7,
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
        private static Thing TryPlace(Map map, RoomRecord room, ThingDef definition,
            HashSet<IntVec3> reserved, int seed, int slot, bool minified, int count)
        {
            if (definition == null || count < 1) { return null; }
            if (count > definition.stackLimit) { count = definition.stackLimit; }
            Thing thing;
            try
            {
                thing = ThingMaker.MakeThing(definition,
                    definition.MadeFromStuff ? GenStuff.DefaultStuffFor(definition) : null);
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

            int quadrant = (seed % 4 + slot) % 4;
            IntVec3 preferred = new IntVec3(quadrant % 2 == 0 ? room.x + 2 : room.Bounds.maxX - 2, 0,
                quadrant < 2 ? room.z + 2 : room.Bounds.maxZ - 2);
            Rot4 rotation = slot % 2 == 0 ? Rot4.North : Rot4.South;
            CellRect interior = room.Bounds.ContractedBy(1);
            foreach (IntVec3 cell in interior.Cells
                .OrderBy(c => c.DistanceToSquared(preferred)).ThenBy(c => c.x).ThenBy(c => c.z))
            {
                CellRect footprint = GenAdj.OccupiedRect(cell, rotation, thing.def.size);
                if (footprint.Cells.Any(c => !interior.Contains(c) || reserved.Contains(c) ||
                    !c.Standable(map) || c.GetEdifice(map) != null || c.GetFirstItem(map) != null))
                { continue; }
                if (footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))
                { continue; }
                GenSpawn.Spawn(thing, cell, map, rotation);
                if (!thing.Spawned || thing.Map != map) { return null; }
                thing.SetForbidden(false, false);
                return thing;
            }
            return null;
        }

        private static Thing Place(Map map, RoomRecord room, string defName, HashSet<IntVec3> reserved,
            int seed, int slot, bool minified = false, int count = 1)
        {
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (definition == null || count < 1 || count > definition.stackLimit)
            { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }
            Thing thing = ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.WoodLog : null);
            thing.TryGetComp<CompQuality>()?.SetQuality(QualityCategory.Normal, ArtGenerationContext.Outsider);
            if (definition.useHitPoints) { thing.HitPoints = Math.Max(1, (int)(thing.MaxHitPoints * (0.65f + (seed % 4) * 0.08f))); }
            if (minified)
            {
                if (!definition.Minifiable) { throw new InvalidOperationException("RR_Generation_InvalidSalvageDef"); }
                thing = thing.MakeMinified();
                if (thing == null) { throw new InvalidOperationException("RR_Generation_InvalidSalvageDef"); }
            }
            thing.stackCount = count;
            int quadrant = (seed % 4 + slot) % 4;
            IntVec3 preferred = new IntVec3(quadrant % 2 == 0 ? room.x + 2 : room.Bounds.maxX - 2, 0,
                quadrant < 2 ? room.z + 2 : room.Bounds.maxZ - 2);
            Rot4 rotation = slot % 2 == 0 ? Rot4.North : Rot4.South;
            foreach (IntVec3 cell in room.Bounds.ContractedBy(1).Cells.OrderBy(c => c.DistanceToSquared(preferred)).ThenBy(c => c.x).ThenBy(c => c.z))
            {
                CellRect footprint = GenAdj.OccupiedRect(cell, rotation, thing.def.size);
                if (footprint.Cells.Any(c => !room.Bounds.ContractedBy(1).Contains(c) || reserved.Contains(c) || !c.Standable(map) ||
                    c.GetEdifice(map) != null || c.GetFirstItem(map) != null)) { continue; }
                // Keep a walkable margin around each fixture; native furniture never seals the room cross.
                if (footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null)) { continue; }
                GenSpawn.Spawn(thing, cell, map, rotation);
                if (!thing.Spawned || thing.Map != map) { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }
                thing.SetForbidden(false, false);
                return thing;
            }
            // Do not reroll or remove earlier placed content after a surprising runtime Def/footprint failure.
            throw new InvalidOperationException("RR_Generation_NoSafeRoomCell");
        }
    }
}
