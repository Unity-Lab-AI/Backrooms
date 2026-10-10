import io

p = 'src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs'
s = io.open(p, encoding='utf-8').read()

# 1. Call the dressing pass after the family switch, before the clue is recorded.
old = '                    content.AddClue(coordinate.Id, room, landmark, variant, salvage);'
new = ('                    // Deeper coordinates are dressed as a KIND of room on top of their\n'
       '                    // structural family -- a laboratory, a workshop, a nursery. Depth 1\n'
       '                    // is skipped inside Select, because the shallow yellow rooms stay\n'
       '                    // sparse and that emptiness is the look.\n'
       '                    //\n'
       '                    // Dressing runs AFTER the family fixtures and the landmark, and\n'
       '                    // never throws: the clue system, the power validation and the route\n'
       '                    // cross all depend on what came before it, so decoration is not\n'
       '                    // allowed to fail a generation that had already succeeded.\n'
       '                    DressRoom(map, room, coordinate.Depth, seed, reserved);\n'
       '                    content.AddClue(coordinate.Id, room, landmark, variant, salvage);')
assert old in s
s = s.replace(old, new, 1)

# 2. Add the dressing pass and a tolerant placement helper.
old2 = '        private static Thing Place(Map map, RoomRecord room, string defName, HashSet<IntVec3> reserved,'
new2 = '''        /// <summary>
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
            RimroomsRoomArchetypeDef archetype = RoomArchetypeService.Select(room.familyId, depth, seed);
            if (archetype == null || archetype.slots == null) { return; }

            // Slots start well past the family fixtures' slot indices so the quadrant spread
            // does not stack dressing on top of the landmark.
            int slotIndex = 8;
            for (int index = 0; index < archetype.slots.Count; index++)
            {
                RoomFurnitureSlot slot = archetype.slots[index];
                if (!RoomArchetypeService.SlotAppears(slot, seed, index)) { continue; }
                ThingDef definition = RoomArchetypeService.Resolve(slot, seed, index);
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

        private static Thing Place(Map map, RoomRecord room, string defName, HashSet<IntVec3> reserved,'''
assert old2 in s
s = s.replace(old2, new2, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("dressing pass added")
