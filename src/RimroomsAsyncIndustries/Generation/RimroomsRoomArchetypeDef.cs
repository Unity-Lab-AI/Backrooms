using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// How a furniture slot decides what fills it.
    ///
    /// **Capability, not a name.** The owner asked for *"lots of furnature and equipment and
    /// different types of rooms and materials of all types from labs, to workshops, to
    /// nursaries, to everything imanginable and every variation of them"*, and a hand-written
    /// list of defNames could never deliver that: it would cover Core, miss every DLC, miss all
    /// 274 profile mods, and rot the first time anything was renamed.
    ///
    /// So a slot says *what kind of thing it wants* and the game answers. A profile that adds a
    /// new workbench puts that workbench in Backrooms workshops the day it is installed,
    /// without this mod knowing it exists.
    /// </summary>
    public enum RoomSlotKind
    {
        /// <summary>Exactly the definitions named, in order of preference.</summary>
        Explicit = 0,

        /// <summary>Anything the game treats as a work table.</summary>
        WorkTable = 1,

        /// <summary>Any humanlike bed.</summary>
        Bed = 2,

        /// <summary>Any table.</summary>
        Table = 3,

        /// <summary>Anything sittable.</summary>
        Seat = 4,

        /// <summary>Anything with storage settings — shelves, racks, containers.</summary>
        Storage = 5,

        /// <summary>Anything that emits light.</summary>
        Light = 6,

        /// <summary>Anything that produces art, which is how Core marks decorative pieces.</summary>
        Art = 7,

        /// <summary>Any member of a named thing category, item or building alike.</summary>
        CategoryMember = 8,
    }

    /// <summary>One slot in a room: what kind of thing, how many, and how likely.</summary>
    public sealed class RoomFurnitureSlot
    {
        /// <summary>What decides the contents.</summary>
        public RoomSlotKind kind = RoomSlotKind.Explicit;

        /// <summary>Candidate definitions for <see cref="RoomSlotKind.Explicit"/>.</summary>
        public List<string> defNames;

        /// <summary>Category for <see cref="RoomSlotKind.CategoryMember"/>.</summary>
        public ThingCategoryDef category;

        /// <summary>How many to place. Rolled per room from the room's own seed.</summary>
        public IntRange count = IntRange.One;

        /// <summary>Chance this slot appears at all, so two rooms of one archetype differ.</summary>
        public float chance = 1f;

        /// <summary>Place the thing minified, as salvage rather than as a fixture.</summary>
        public bool minified;

        /// <summary>Stack size when the chosen definition is an item rather than a building.</summary>
        public IntRange stackCount = IntRange.One;
    }

    /// <summary>
    /// A kind of room that can appear inside a coordinate, and what tends to be in it.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"lots of furnature and equipment and different
    /// types of rooms and materials of all types from labs, to workshops, to nursaries, to
    /// everything imanginable and every variation of them and even wild waky carzxzy creepy
    /// things"*, with the preceding clarification that the yellow rooms are only the shallow
    /// look and *"further in it gets very varied and weird"*.
    ///
    /// ## Depth is what decides whether an archetype can appear
    ///
    /// Each archetype declares the depth band it belongs to. **The shallow yellow rooms stay
    /// deliberately sparse** — that emptiness *is* the look, and filling them with laboratory
    /// equipment would destroy the exact image the setting rests on. Density and strangeness
    /// climb with depth instead.
    ///
    /// ## Variations come from rolling, not from authoring
    ///
    /// *"every variation of them"* is answered by every slot carrying a count range and an
    /// appearance chance, both rolled from the room's own seed. Two laboratories in the same
    /// coordinate are built from the same archetype and are not the same room, and the same
    /// room is identical every time it is loaded.
    /// </summary>
    public sealed class RimroomsRoomArchetypeDef : Def
    {
        /// <summary>Shallowest depth this archetype may appear at.</summary>
        public int minDepth = 2;

        /// <summary>Deepest depth this may appear at. Zero or less means no ceiling.</summary>
        public int maxDepth;

        /// <summary>Relative likelihood against other archetypes legal at the same depth.</summary>
        public float weight = 1f;

        /// <summary>
        /// Structural families this archetype may dress. Empty means any.
        /// A threshold room is where the player arrives and is left alone on purpose.
        /// </summary>
        public List<string> familyIds;

        /// <summary>What tends to be in it.</summary>
        public List<RoomFurnitureSlot> slots = new List<RoomFurnitureSlot>();

        /// <summary>
        /// Which kinds of place this room belongs to, from <see cref="CoordinateMotif.Themes"/>.
        ///
        /// ## Owner direction, 2026-10-03, verbatim
        ///
        /// *"so its more rooma corradors facilites infastructure roads neighborrs hood malls
        /// shoopping centers military"*, and at the fork *"option 3 but keep it not limited to my
        /// examples i want you to expand and expound on everything in a lsd way"*.
        ///
        /// ## This is the axis that turns sixteen kinds into a place
        ///
        /// Every archetype was drawn per room against its own weight alone, so a coordinate held
        /// a classroom beside a weapons locker beside a nursery — **a list of rooms rather than
        /// somewhere.** A coordinate now draws one theme and an archetype carrying it is
        /// <see cref="CoordinateMotif.ThemeWeightFactor"/> times likelier, so the floor reads as
        /// an institution, a market, a barracks, a neighbourhood.
        ///
        /// **A bias, never a filter**, and that is deliberate: a market coordinate holding
        /// nothing but shops is a themed level rather than a Backrooms level. The wrongness needs
        /// the one laboratory in the shopping centre.
        ///
        /// Empty means the archetype fits anywhere and is never penalised for saying so — the
        /// tags buy coherence, they are not a tax on not declaring one.
        /// </summary>
        public List<string> themes;

        /// <summary>
        /// The highest tech level this archetype will ever produce.
        ///
        /// A **ceiling, not a target.** What a coordinate actually produces rises with the
        /// branch's own research and how deep the space is — the owner's *"higher the gete
        /// quality and rtesarch levels and tech and stuff"* — but it never exceeds what the
        /// archetype itself declares, so a def that says it deals in industrial goods is still
        /// telling the truth.
        /// </summary>
        public TechLevel maxTechLevel = TechLevel.Archotech;

        /// <summary>
        /// Marks an archetype as one of the owner's *"wild waky carzxzy creepy things"*.
        /// Kept as a flag rather than a separate def type so the escalation ladder can later
        /// cap how many of them a single coordinate may hold without reworking this.
        /// </summary>
        public bool anomalous;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (slots == null || slots.Count == 0)
            { yield return "RimroomsRoomArchetypeDef " + defName + " has no slots, so it dresses nothing."; }
            if (weight <= 0f)
            { yield return "RimroomsRoomArchetypeDef " + defName + " has a non-positive weight."; }
            if (maxDepth > 0 && maxDepth < minDepth)
            { yield return "RimroomsRoomArchetypeDef " + defName + " has maxDepth below minDepth."; }
            // **A THEME THE MOTIF CANNOT DRAW IS A TAG THAT DOES NOTHING.** A typo here would be
            // completely silent otherwise: the archetype would simply never get its bias, and a
            // coordinate meant to read as a market would hold shops at the same rate as
            // everything else. Caught at load, by name, where somebody can fix it.
            if (themes != null)
            {
                for (int index = 0; index < themes.Count; index++)
                {
                    if (System.Array.IndexOf(CoordinateMotif.Themes, themes[index]) >= 0) { continue; }
                    yield return "RimroomsRoomArchetypeDef " + defName + " declares theme '"
                        + themes[index] + "', which is not one of CoordinateMotif.Themes.";
                }
            }
        }
    }
}
