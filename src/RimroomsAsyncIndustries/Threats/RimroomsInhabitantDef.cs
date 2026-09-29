using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// What kind of person is found in a coordinate, and therefore when they may be placed.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"alla trhings are possible finding random
    /// pawns of disappering, findeding dead ones pasycholitc ones lost pawns all kinds of crazy
    /// variations as per the lore"*.
    ///
    /// The split matters more than the labels. <see cref="Dead"/> is **discoverable content**
    /// and is placed when the space is generated, because a body is scenery and finding one
    /// should not wait on a danger band. Everything else is a **living thing that acts**, and is
    /// paced by the escalation ladder on arrival — otherwise *"a first visit is always quiet"*
    /// would be a lie the moment somebody walked in.
    /// </summary>
    public enum InhabitantKind
    {
        /// <summary>Somebody who is simply here. Neutral, unexplained, and not yours.</summary>
        Wanderer = 0,

        /// <summary>Somebody who went missing — including, where there is a record, one of yours.</summary>
        Missing = 1,

        /// <summary>A body, and whatever they were carrying. Content, not a threat.</summary>
        Dead = 2,

        /// <summary>Hostile and unstable. This is what the encounter cap exists for.</summary>
        Psychotic = 3,

        /// <summary>A survivor who can be brought home. The reason to enter, not only to endure.</summary>
        Survivor = 4,

        /// <summary>
        /// Somebody wearing the name and clothes of a colonist who is **alive right now**.
        ///
        /// The owner's *"echos of thier inhabitance in weird ways"*. Deliberately not a copy of
        /// somebody you lost — that is the <see cref="Missing"/> family and it is a different,
        /// sadder feeling. An echo is uncanny precisely because the real one is standing in
        /// your base at the same moment.
        /// </summary>
        Echo = 5,
    }

    /// <summary>
    /// One family of people that can be found inside a coordinate.
    ///
    /// ## No new pawn kinds, ever
    ///
    /// M2 is currently **deleting** this mod's five legacy `RR_*Staff` PawnKindDefs under the
    /// existing-content policy, so authoring new ones here would reopen the exact category that
    /// is being closed. Every inhabitant is generated from a `PawnKindDef` the loaded game
    /// already ships, chosen by name with a fallback chain, so a Core-only install and a
    /// 274-mod profile both work and neither needs this mod to know what it has.
    ///
    /// ## Held to rules that were frozen before any of this was written
    ///
    /// * **Readable warning, learnable rule, at least one countermeasure, no unavoidable
    ///   instant failure** — the threat rules recorded in `THREAT_DESIGN_SHEETS.md`.
    /// * **An inhabitant may never decide anything about a gate.** `PortalTraversalPolicy` is
    ///   the single chokepoint that enforces it, and nothing here goes near it: anything found
    ///   in a coordinate leaves only carried out by the branch's own people.
    /// * **The escalation ladder caps how many may act at once**, guarantees half of every
    ///   coordinate is quiet, and makes a first visit quiet outright.
    /// </summary>
    public sealed class RimroomsInhabitantDef : Def
    {
        /// <summary>What this family is, and therefore when it may appear.</summary>
        public InhabitantKind kind = InhabitantKind.Wanderer;

        /// <summary>Shallowest depth this family may appear at.</summary>
        public int minDepth = 2;

        /// <summary>Deepest depth. Zero or less means no ceiling.</summary>
        public int maxDepth;

        /// <summary>
        /// Lowest ladder band at which this family may be placed. Ignored for
        /// <see cref="InhabitantKind.Dead"/>, which is content rather than an encounter.
        /// </summary>
        public CoordinatePressureLadder.Band minBand = CoordinatePressureLadder.Band.Unsettled;

        /// <summary>Relative likelihood against other families legal in the same situation.</summary>
        public float weight = 1f;

        /// <summary>
        /// Pawn kinds to generate from, in order of preference. **Existing defs only.**
        /// The first one the loaded game actually has is used; if none resolve, the family is
        /// skipped rather than substituted, because a wanderer rendered as the wrong kind of
        /// person is worse than an empty room.
        /// </summary>
        public List<string> pawnKindDefNames = new List<string>();

        /// <summary>How many may appear at once, before the ladder's cap is applied.</summary>
        public IntRange count = IntRange.One;

        /// <summary>Chance this family appears at all on a given arrival.</summary>
        public float chance = 0.5f;

        /// <summary>
        /// Whether these are hostile to the player. Only ever true for
        /// <see cref="InhabitantKind.Psychotic"/>, and checked rather than assumed, because a
        /// hostile wanderer would break the warning-first rule.
        /// </summary>
        public bool hostile;

        /// <summary>
        /// Whether a body of this family carries what they had on them.
        /// The owner's *"findeding dead ones"* is a discovery, and a body with nothing on it
        /// is a prop rather than a find.
        /// </summary>
        public bool carriesBelongings = true;

        /// <summary>Keyed string announcing the find, or empty for no letter.</summary>
        public string letterLabelKey;
        public string letterTextKey;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (pawnKindDefNames == null || pawnKindDefNames.Count == 0)
            { yield return "RimroomsInhabitantDef " + defName + " names no pawn kinds."; }
            if (weight <= 0f)
            { yield return "RimroomsInhabitantDef " + defName + " has a non-positive weight."; }
            if (maxDepth > 0 && maxDepth < minDepth)
            { yield return "RimroomsInhabitantDef " + defName + " has maxDepth below minDepth."; }
            if (hostile && kind != InhabitantKind.Psychotic)
            {
                // The warning-first rule depends on a player being able to tell what is
                // dangerous. A hostile family that does not read as hostile breaks it.
                yield return "RimroomsInhabitantDef " + defName +
                    " is hostile but is not a Psychotic family, which breaks the warning-first rule.";
            }
        }
    }
}
