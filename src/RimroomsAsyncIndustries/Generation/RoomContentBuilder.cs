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
        internal const int ContentVersion = 2;

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
                    PaintRoom(map, room, variant);
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
                    content.AddClue(coordinate.Id, room, landmark, variant, salvage);
                }
                finally { Rand.PopState(); }
            }
            content.CompletePopulation();
        }

        private static void PaintRoom(Map map, RoomRecord room, int variant)
        {
            bool utility = room.familyId == "service_passage" || room.familyId == "utility_room";
            string name = utility ? "MetalTile" : "PavedTile";
            TerrainDef accent = DefDatabase<TerrainDef>.GetNamedSilentFail(name);
            TerrainDef carpet = DefDatabase<TerrainDef>.GetNamedSilentFail("RR_FadedInstitutionalCarpet");
            if (accent == null || carpet == null) { throw new InvalidOperationException("RR_Generation_RequiredCoreOrSiteDefMissing"); }
            foreach (IntVec3 cell in room.Bounds.Cells)
            {
                Thing wall = cell.GetEdifice(map);
                if (wall != null && wall.def == ThingDefOf.Wall)
                { wall.TryGetComp<CompColorable>()?.SetColor(utility ? new Color(0.61f, 0.65f, 0.62f) : new Color(0.77f, 0.73f, 0.51f)); }
            }
            foreach (IntVec3 cell in room.Bounds.ContractedBy(1).Cells)
            {
                // Original floor inset/stripes establish room differences without a color-only cue.
                bool stripe = variant == 0 ? (cell.x - room.x) % 4 == 0 : variant == 1 ? (cell.z - room.z) % 4 == 0 :
                    cell.x == room.x + 2 || cell.z == room.z + 2 || cell.x == room.Bounds.maxX - 2 || cell.z == room.Bounds.maxZ - 2;
                if (stripe) { map.terrainGrid.SetTerrain(cell, accent); }
                else if (!utility) { map.terrainGrid.SetTerrain(cell, carpet); }
            }
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
