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
        /// Somebody who helps, and should not be able to.
        ///
        /// **Owner direction, 2026-10-04, verbatim:** *"they should be nutral, allies,
        /// and enemy in all differnt kinds and relations and scenrios"*, under the
        /// standing *"remember lsd unnerving feeling with all things"*.
        ///
        /// **An ally is the most unnerving of the three relations, not the friendliest.**
        /// A thing that attacks you is explicable. Somebody who has been down here long
        /// enough to be part of it, who takes your side against what else is in the
        /// space, and who **will not leave with you**, is not. They are generated into an
        /// existing non-hostile faction and given Core's own defend-the-area lord, so the
        /// help is real: they fight the psychotic families for you with ordinary AI.
        /// </summary>
        Helper = 6,

        /// <summary>
        /// An animal that is simply in here.
        ///
        /// **Owner direction, 2026-10-04, verbatim:** *"things that chase you are just
        /// npc pawns and wild animals and shit of the gasme"*. Animals reached the
        /// player only as a chaser until now, never as something found standing in a
        /// room. Unfactioned, like any wild animal anywhere -- the unnerving part is not
        /// that it is dangerous but that it is **in here**, and something had to bring it.
        /// </summary>
        Fauna = 7,

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

        /// <summary>
        /// **The one exact thing that is wrong about this encounter, readable on the
        /// pawn itself, forever.**
        ///
        /// Owner direction, 2026-10-04: *"remember lsd unnerving feeling with all things
        /// ie events random spanwns, enemies, allies, nuetrals"*. The mechanism comes
        /// from `docs/UNIVERSE_ADAPTATION.md`, which already said how the source's
        /// feeling is produced: *"Ordinary industrial interiors become uncanny through
        /// exact changes"*. The generator applies that to space; **nothing applied it to
        /// people**, and the owner's version of the complaint was *"zero weird events or
        /// people"*.
        ///
        /// **A letter is not a tell.** The letters this package writes are good, but they
        /// fire once and scroll away, and then the pawn is just a pawn -- a player who
        /// comes back next opening has nothing to read. `THREAT_DESIGN_SHEETS.md` requires
        /// *"a visible or otherwise accessible warning"* and forbids colour or sound as
        /// the only cue. This is that warning, on the thing, in text.
        /// </summary>
        public string tellKey;

        /// <summary>
        /// Whether this family takes the branch's side against what else is in the space.
        ///
        /// Only ever true for <see cref="InhabitantKind.Helper"/>, and checked rather
        /// than assumed for the same reason `hostile` is: a family whose relation does not
        /// match what it reads as breaks the warning-first rule in the other direction.
        /// </summary>
        public bool friendly;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (pawnKindDefNames == null || pawnKindDefNames.Count == 0)
            { yield return "RimroomsInhabitantDef " + defName + " names no pawn kinds."; }
            if (weight <= 0f)
            { yield return "RimroomsInhabitantDef " + defName + " has a non-positive weight."; }
            if (maxDepth > 0 && maxDepth < minDepth)
            { yield return "RimroomsInhabitantDef " + defName + " has maxDepth below minDepth."; }
            // **A FAMILY WITHOUT A TELL IS THE DEFECT THIS FIELD EXISTS FOR.** Owner,
            // 2026-10-04: the unnerving feeling applies to *"all things"*, and a family
            // whose uncanny detail exists only in a letter that has scrolled away has no
            // readable warning at all. Enforced at load so a new family cannot ship without
            // one -- which is how the seven that existed before this got away with it.
            if (string.IsNullOrEmpty(tellKey))
            {
                yield return "RimroomsInhabitantDef " + defName +
                    " has no tellKey, so nothing on the pawn says what is wrong with it.";
            }
            if (friendly && kind != InhabitantKind.Helper)
            {
                yield return "RimroomsInhabitantDef " + defName +
                    " is friendly but is not a Helper family, which breaks the warning-first rule.";
            }
            if (friendly && hostile)
            {
                yield return "RimroomsInhabitantDef " + defName +
                    " is both friendly and hostile.";
            }
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
