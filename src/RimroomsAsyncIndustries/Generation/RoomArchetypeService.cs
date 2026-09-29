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
        public static RimroomsRoomArchetypeDef Select(string familyId, int depth, int seed,
            int roomIndex)
        {
            if (depth <= 1 || string.IsNullOrEmpty(familyId)) { return null; }

            // The threshold is where a player arrives. It is left undressed on purpose, so the
            // way back is never buried under scenery.
            if (string.Equals(familyId, "threshold_room", StringComparison.Ordinal)) { return null; }

            Company.RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();

            // Owner direction 2026-09-29: "hallways can have furniture and produiction benches
            // too". A bench standing in a corridor is not a bug in this setting -- the
            // wrongness IS the content. So an archetype's declared family constraint is honoured
            // in a coherent space and LAPSES in a deranged one, rather than being removed
            // outright: a shallow coordinate still reads as somewhere, and a deep one stops
            // pretending.
            bool ignoreKind = SpaceSophistication.IgnoreRoomKind(depth, campaign, seed, roomIndex);

            List<RimroomsRoomArchetypeDef> legal = DefDatabase<RimroomsRoomArchetypeDef>
                .AllDefsListForReading
                .Where(archetype => archetype.minDepth <= depth
                    && (archetype.maxDepth <= 0 || archetype.maxDepth >= depth)
                    && (ignoreKind || archetype.familyIds == null || archetype.familyIds.Count == 0
                        || archetype.familyIds.Contains(familyId)))
                .ToList();
            if (legal.Count == 0) { return null; }

            // Sorted before rolling so the choice cannot depend on def load order, which is not
            // stable across mod lists and would make a coordinate look different on another
            // machine with the same seed.
            legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));

            // The stranger archetypes get heavier as a coordinate gets more deranged, until
            // they outweigh the ordinary ones rather than merely matching them -- by then the
            // ordinary ones are the surprise.
            float anomalousFactor = SpaceSophistication.AnomalousWeightFactor(depth, campaign);
            Func<RimroomsRoomArchetypeDef, float> weightOf = archetype =>
                Math.Max(0.0001f, archetype.weight) * (archetype.anomalous ? anomalousFactor : 1f);

            float total = legal.Sum(weightOf);
            int roll = Gen.HashCombineInt(seed, 0x41524348);
            if (roll < 0) { roll = ~roll; }
            float pick = (roll % 100000) / 100000f * total;
            for (int index = 0; index < legal.Count; index++)
            {
                pick -= weightOf(legal[index]);
                if (pick <= 0f) { return legal[index]; }
            }
            return legal[legal.Count - 1];
        }

        /// <summary>
        /// How often a slot in a deep coordinate is answered from the branch's own
        /// construction register rather than from the whole def database.
        ///
        /// Deliberately not all of them. The place copying you is unsettling **because the rest
        /// of the room is still strange** — if every fixture were something the player built,
        /// a deep coordinate would just read as a badly laid-out copy of their colony, and the
        /// effect would collapse into a joke.
        /// </summary>
        private const int EchoPercent = 40;

        /// <summary>
        /// Resolves one slot to a definition, or null when nothing in the loaded game answers it.
        /// A slot that cannot be filled is skipped rather than substituted: putting a bed in a
        /// room that asked for a workbench is worse than an emptier room.
        ///
        /// **In a deep coordinate some slots are answered from what the branch has actually
        /// built** — the owner's *"new equipement and rooms and shit going into the backrooms
        /// and build there or in the real world can start appearing in lower levels"*. The echo
        /// is tried first and falls straight through to the ordinary pool when the register
        /// holds nothing that fits the slot, so a young branch that has built almost nothing
        /// still gets fully dressed rooms.
        /// </summary>
        public static ThingDef Resolve(RimroomsRoomArchetypeDef archetype, RoomFurnitureSlot slot,
            int seed, int index, int depth)
        {
            if (slot == null) { return null; }

            // The archetype's declared tech level is a CEILING, not a target. What a coordinate
            // actually produces rises with the branch -- owner direction 2026-09-29, "higher the
            // gete quality and rtesarch levels and tech and stuff". A pre-industrial branch
            // finds pre-industrial things; one that has gone deep and researched widely starts
            // turning up spacer equipment, which is also what makes a deep space worth
            // revisiting later without anything being authored twice.
            //
            // This field had been declared on the def and never read. Wiring it here is what
            // turns it from dead data into the lever the owner asked for.
            Company.RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            TechLevel ceiling = archetype == null
                ? TechLevel.Archotech
                : SpaceSophistication.TechCeiling(archetype.maxTechLevel, depth, campaign);

            if (depth >= ConstructionEchoComponent.EchoFromDepth)
            {
                int roll = Gen.HashCombineInt(seed, index * 131 + 0x4543);
                if (roll < 0) { roll = ~roll; }
                if (roll % 100 < EchoPercent)
                {
                    ConstructionEchoComponent echo = ConstructionEchoComponent.Current;
                    ThingDef mirrored = echo == null ? null
                        : echo.Draw(candidate => Placeable(candidate)
                            && WithinTech(candidate, ceiling)
                            && (slot.kind == RoomSlotKind.Explicit
                                || slot.kind == RoomSlotKind.CategoryMember
                                || Matches(slot.kind, candidate)),
                            seed + index);
                    if (mirrored != null) { return mirrored; }
                }
            }

            List<ThingDef> candidates = Candidates(slot);
            if (candidates == null || candidates.Count == 0) { return null; }

            // Filtered rather than rejected: a slot whose whole pool is above the branch's
            // reach falls back to the unfiltered pool, because an empty room is a worse
            // outcome than a slightly anachronistic one.
            var affordable = new List<ThingDef>();
            for (int index2 = 0; index2 < candidates.Count; index2++)
            {
                if (WithinTech(candidates[index2], ceiling)) { affordable.Add(candidates[index2]); }
            }
            List<ThingDef> pool = affordable.Count > 0 ? affordable : candidates;

            int pick = Gen.HashCombineInt(seed, index * 31 + (int)slot.kind);
            if (pick < 0) { pick = ~pick; }
            return pool[pick % pool.Count];
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

        private static bool WithinTech(ThingDef definition, TechLevel ceiling)
        {
            return definition != null && (int)definition.techLevel <= (int)ceiling;
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
