using System;
using RimroomsAsyncIndustries.Company;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// The one thing a whole coordinate has in common, and the thing its rooms vary **from**.
    ///
    /// ## Owner direction, 2026-10-03, verbatim
    ///
    /// *"repeated patternes in variations"*, and at the composition fork: *"option 3 but keep it
    /// not limited to my examples i want you to expand and expound on everything in a lsd way"*.
    ///
    /// ## What was wrong, measured rather than guessed
    ///
    /// Seven room shapes already existed in <see cref="RoomLayoutPlanner.RockIntrusionCells"/> —
    /// ell, tee, cross, wedge, partition, bays and plain — and **every room rolled its own,
    /// independently of every other room.** Independent rolls do not make a pattern; they make
    /// noise. A floor where one room is a wedge, the next has bays and the next is a cross reads
    /// as damage, and the owner's words for the thing they wanted instead are exact: *the same*
    /// pattern, *in variations*.
    ///
    /// The archetypes had the same shape of problem. Sixteen kinds of room, each drawn per room
    /// against its own weight, so a coordinate held a classroom beside a weapons locker beside a
    /// nursery — a list of rooms rather than a **place**.
    ///
    /// ## What a motif is
    ///
    /// One draw, from the coordinate's own seed, made once and read by everything:
    ///
    ///   * a **shape** every room tends toward, so the floor has an architecture;
    ///   * a **theme** the room kinds tend toward, so the floor is somewhere — an institution, a
    ///     market, a barracks, a neighbourhood;
    ///   * **how strongly either holds**, which falls with depth.
    ///
    /// **That last part is the whole design.** Shallow coordinates are strongly on-motif, which
    /// is what makes the yellow rooms read as a place at all: they are monotonous, and the
    /// monotony is the image the setting rests on. The deeper a space is, the more often a room
    /// departs from it — so the *"further in it gets very varied and weird"* curve is the same
    /// number, falling. A coordinate that was uniformly random at every depth could never
    /// produce either end of that.
    ///
    /// ## Why it is a struct with no state
    ///
    /// It is a **pure function of the saved record**, computed on demand rather than stored. So a
    /// revisit draws the identical motif without a save-schema field, and — the load-bearing
    /// part — `RoomLayoutPlanner.CandidateIsSafe` and
    /// `GenStep_BackroomsDestination` derive the same one independently and therefore model and
    /// carve the same rooms. A motif saved on one side and recomputed on the other would be two
    /// derivations of one rule, which is the defect this project has paid for most often.
    /// </summary>
    internal struct CoordinateMotif
    {
        /// <summary>
        /// The themes a coordinate can be built around, and the vocabulary an archetype tags
        /// itself with.
        ///
        /// **The owner's named kinds are in here and are not the whole of it**, by direction:
        /// *"but keep it not limited to my examples"*. *"facilites"* and *"infastructure"* and
        /// *"roads"* are `infrastructure`; *"neighborrs hood"* is `residential`; *"malls"* and
        /// *"shoopping centers"* are `market`; *"military"* is its own. The rest are the
        /// expansion that direction asked for.
        ///
        /// Ordered, and **never reordered** — the index is drawn from the coordinate's seed, so
        /// inserting a theme in the middle would re-theme every existing coordinate on load.
        /// Append only.
        /// </summary>
        internal static readonly string[] Themes =
        {
            "institution",
            "market",
            "military",
            "residential",
            "industry",
            "infrastructure",
            "leisure",
            "derelict",
        };

        /// <summary>The shape every room on this floor tends toward.</summary>
        internal int Shape;

        /// <summary>The kind of place this floor tends to be. One of <see cref="Themes"/>.</summary>
        internal string Theme;

        /// <summary>
        /// How often a room follows the motif rather than departing from it, out of a hundred.
        ///
        /// See the type summary: this falling with depth is what produces both the monotonous
        /// shallow floors and the incoherent deep ones from one mechanism.
        /// </summary>
        internal int Hold;

        /// <summary>Strongest and weakest the motif ever holds.</summary>
        internal const int StrongestHold = 85;
        internal const int WeakestHold = 25;

        /// <summary>How much of the hold one level of depth takes away.</summary>
        internal const int HoldLostPerDepth = 10;

        /// <summary>How much more likely an on-theme archetype is than an off-theme one.</summary>
        /// <remarks>
        /// A multiplier rather than a filter, deliberately. Filtering would make a market
        /// coordinate hold nothing but shops, which is a themed level rather than a Backrooms
        /// level — the wrongness needs the one laboratory in the shopping centre. Three is
        /// enough for a floor to read as somewhere and far too little to make it consistent.
        /// </remarks>
        internal const float ThemeWeightFactor = 3f;

        /// <summary>
        /// Draw this coordinate's motif. Cheap, pure, and identical on every call.
        /// </summary>
        internal static CoordinateMotif For(CoordinateRecord coordinate)
        {
            var motif = default(CoordinateMotif);
            int depth = RoomLayoutPlanner.DepthOf(coordinate);
            int seed = coordinate == null ? 0 : coordinate.Seed;
            string id = coordinate == null || coordinate.Id == null ? string.Empty : coordinate.Id;

            int draw = DestinationService.StableHash(seed, id + ":motif", depth);
            if (draw < 0) { draw = ~draw; }
            motif.Shape = draw % RoomLayoutPlanner.ShapeForms;
            motif.Theme = Themes[(draw / 13) % Themes.Length];
            int hold = StrongestHold - (depth - 1) * HoldLostPerDepth;
            motif.Hold = hold < WeakestHold ? WeakestHold : hold;
            return motif;
        }

        /// <summary>
        /// The motif a layout has when no coordinate is available.
        ///
        /// `Hold` of zero means every room rolls its own shape, which is exactly the behaviour
        /// that existed before motifs — so a caller that cannot supply a coordinate gets the old
        /// generator rather than a wrong one.
        /// </summary>
        internal static CoordinateMotif None
        {
            get
            {
                var motif = default(CoordinateMotif);
                motif.Theme = null;
                motif.Hold = 0;
                return motif;
            }
        }

        /// <summary>
        /// Which shape this room takes: the motif's, or its own.
        ///
        /// **Read by the carver and by the reachability proof**, which is why it lives here
        /// rather than inside either. The roll is the one `RockIntrusionCells` already computed
        /// for the room, divided down for an independent draw the way every other secondary
        /// choice in that file is — so no extra hashing and no second seed.
        /// </summary>
        internal int ShapeFor(int roll)
        {
            if (roll < 0) { roll = ~roll; }
            bool onMotif = (roll / 101) % 100 < Hold;
            return onMotif ? Shape : roll % RoomLayoutPlanner.ShapeForms;
        }

        /// <summary>
        /// How much to favour an archetype that carries this motif's theme.
        ///
        /// One for anything else, so an untagged archetype is never penalised — the tags are a
        /// bias toward coherence, not a requirement to declare one.
        /// </summary>
        internal float WeightFor(System.Collections.Generic.List<string> themes)
        {
            if (Theme == null || themes == null || themes.Count == 0) { return 1f; }
            for (int index = 0; index < themes.Count; index++)
            {
                if (string.Equals(themes[index], Theme, StringComparison.Ordinal))
                { return ThemeWeightFactor; }
            }
            return 1f;
        }
    }
}
