using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Chooses what kind of room a space is, and resolves its slots against whatever the loaded
    /// game actually offers.
    ///
    /// ## Nothing here names a piece of furniture it hopes exists
    ///
    /// Every capability slot is answered by asking the def database a question — *is this a work
    /// table, a bed, something sittable, something with storage* — so the answer includes Core,
    /// every DLC the player owns, and all 274 profile mods. That is the only way to honour
    /// *"everything imanginable and every variation of them"* without a list that rots.
    ///
    /// The resolved candidate lists are **cached per session**, because asking the whole def
    /// database eight questions for every slot in every room of every generated coordinate
    /// would be real cost for an answer that cannot change while the game is running.
    ///
    /// ## Everything is rolled from the room's own seed
    ///
    /// Selection, counts and appearance chances all come from the seed already used for room
    /// content, so **a coordinate is identical every time it is loaded** and two rooms sharing an
    /// archetype are still different rooms.
    /// </summary>
    public static class RoomArchetypeService
    {
        private static readonly Dictionary<RoomSlotKind, List<ThingDef>> capabilityCache =
            new Dictionary<RoomSlotKind, List<ThingDef>>();
        private static readonly Dictionary<string, List<ThingDef>> categoryCache =
            new Dictionary<string, List<ThingDef>>(StringComparer.Ordinal);

        /// <summary>
        /// Largest footprint a generated fixture may have. A three-by-three machine dropped into
        /// a Backrooms room seals the route cross and strands whoever walked in.
        /// </summary>
        private const int MaxFixtureSide = 2;

        /// <summary>
        /// Picks an archetype for a room, or null when the room should be left as it is.
        ///
        /// **Depth 1 always returns null.** The shallow yellow rooms stay sparse because that
        /// emptiness *is* the look; filling them with laboratory equipment would destroy the
        /// exact image the setting rests on.
        /// </summary>
        public static RimroomsRoomArchetypeDef Select(string familyId, int depth, int seed)
        {
            if (depth <= 1 || string.IsNullOrEmpty(familyId)) { return null; }

            // The threshold is where a player arrives. It is left undressed on purpose, so the
            // way back is never buried under scenery.
            if (string.Equals(familyId, "threshold_room", StringComparison.Ordinal)) { return null; }

            List<RimroomsRoomArchetypeDef> legal = DefDatabase<RimroomsRoomArchetypeDef>
                .AllDefsListForReading
                .Where(archetype => archetype.minDepth <= depth
                    && (archetype.maxDepth <= 0 || archetype.maxDepth >= depth)
                    && (archetype.familyIds == null || archetype.familyIds.Count == 0
                        || archetype.familyIds.Contains(familyId)))
                .ToList();
            if (legal.Count == 0) { return null; }

            // Sorted before rolling so the choice cannot depend on def load order, which is not
            // stable across mod lists and would make a coordinate look different on another
            // machine with the same seed.
            legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));

            float total = legal.Sum(archetype => Math.Max(0.0001f, archetype.weight));
            int roll = Gen.HashCombineInt(seed, 0x41524348);
            if (roll < 0) { roll = ~roll; }
            float pick = (roll % 100000) / 100000f * total;
            for (int index = 0; index < legal.Count; index++)
            {
                pick -= Math.Max(0.0001f, legal[index].weight);
                if (pick <= 0f) { return legal[index]; }
            }
            return legal[legal.Count - 1];
        }

        /// <summary>
        /// Resolves one slot to a definition, or null when nothing in the loaded game answers it.
        /// A slot that cannot be filled is skipped rather than substituted: putting a bed in a
        /// room that asked for a workbench is worse than an emptier room.
        /// </summary>
        public static ThingDef Resolve(RoomFurnitureSlot slot, int seed, int index)
        {
            if (slot == null) { return null; }
            List<ThingDef> candidates = Candidates(slot);
            if (candidates == null || candidates.Count == 0) { return null; }
            int roll = Gen.HashCombineInt(seed, index * 31 + (int)slot.kind);
            if (roll < 0) { roll = ~roll; }
            return candidates[roll % candidates.Count];
        }

        /// <summary>Whether a slot appears in this particular room.</summary>
        public static bool SlotAppears(RoomFurnitureSlot slot, int seed, int index)
        {
            if (slot == null) { return false; }
            if (slot.chance >= 1f) { return true; }
            int roll = Gen.HashCombineInt(seed, index * 977 + 13);
            if (roll < 0) { roll = ~roll; }
            return (roll % 1000) / 1000f < slot.chance;
        }

        /// <summary>How many of a slot appear, rolled from the room's seed.</summary>
        public static int SlotCount(RoomFurnitureSlot slot, int seed, int index)
        {
            if (slot == null) { return 0; }
            int low = Math.Max(0, slot.count.min);
            int high = Math.Max(low, slot.count.max);
            if (high == low) { return low; }
            int roll = Gen.HashCombineInt(seed, index * 613 + 7);
            if (roll < 0) { roll = ~roll; }
            return low + roll % (high - low + 1);
        }

        private static List<ThingDef> Candidates(RoomFurnitureSlot slot)
        {
            if (slot.kind == RoomSlotKind.Explicit)
            {
                var explicitDefs = new List<ThingDef>();
                if (slot.defNames == null) { return explicitDefs; }
                for (int index = 0; index < slot.defNames.Count; index++)
                {
                    ThingDef found = DefDatabase<ThingDef>.GetNamedSilentFail(slot.defNames[index]);
                    if (found != null) { explicitDefs.Add(found); }
                }
                return explicitDefs;
            }

            if (slot.kind == RoomSlotKind.CategoryMember)
            {
                if (slot.category == null) { return null; }
                List<ThingDef> cached;
                if (categoryCache.TryGetValue(slot.category.defName, out cached)) { return cached; }
                cached = slot.category.DescendantThingDefs.Where(Placeable).ToList();
                cached.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));
                categoryCache[slot.category.defName] = cached;
                return cached;
            }

            List<ThingDef> byCapability;
            if (capabilityCache.TryGetValue(slot.kind, out byCapability)) { return byCapability; }
            byCapability = DefDatabase<ThingDef>.AllDefsListForReading
                .Where(candidate => Placeable(candidate) && Matches(slot.kind, candidate))
                .ToList();
            // Ordinal sort so the candidate list does not depend on def load order, which
            // changes with the mod list and would make the same seed produce different rooms.
            byCapability.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));
            capabilityCache[slot.kind] = byCapability;
            return byCapability;
        }

        private static bool Matches(RoomSlotKind kind, ThingDef definition)
        {
            switch (kind)
            {
                case RoomSlotKind.WorkTable:
                    return definition.IsWorkTable;
                case RoomSlotKind.Bed:
                    return definition.building != null && definition.building.bed_humanlike
                        && definition.IsBed;
                case RoomSlotKind.Table:
                    return definition.IsTable;
                case RoomSlotKind.Seat:
                    return definition.building != null && definition.building.isSittable;
                case RoomSlotKind.Storage:
                    return definition.building != null
                        && definition.building.fixedStorageSettings != null;
                case RoomSlotKind.Light:
                    return definition.HasComp(typeof(CompGlower));
                case RoomSlotKind.Art:
                    return definition.HasComp(typeof(CompArt));
                default:
                    return false;
            }
        }

        /// <summary>
        /// Whether a definition is safe to drop into a generated room at all.
        ///
        /// The footprint cap is the load-bearing one. A large machine placed in a Backrooms room
        /// can seal the route cross, and the whole point of a coordinate is that somebody has to
        /// be able to walk back out of it.
        /// </summary>
        private static bool Placeable(ThingDef definition)
        {
            if (definition == null || definition.defName == null) { return false; }
            if (definition.destroyable == false) { return false; }
            if (definition.size.x > MaxFixtureSide || definition.size.z > MaxFixtureSide) { return false; }
            if (definition.category == ThingCategory.Building)
            {
                if (definition.building == null) { return false; }
                if (definition.building.isNaturalRock || definition.building.isResourceRock) { return false; }
                // A door or a wall in the middle of a room changes the layout rather than
                // dressing it, and the layout is saved and validated elsewhere.
                if (definition.building.isEdifice && !definition.Minifiable) { return false; }
                if (definition.building.isAttachment) { return false; }
                if (definition.building.turretGunDef != null) { return false; }
                return definition.BuildableByPlayer || definition.Minifiable;
            }
            if (definition.category == ThingCategory.Item)
            {
                return definition.EverHaulable && !definition.IsCorpse;
            }
            return false;
        }
    }
}
