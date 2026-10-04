using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// What kind of thing a tell can be attached to, asked of the definition itself.
    ///
    /// **Asked rather than declared, for the same reason <see cref="RoomSlotKind"/> is.** A list
    /// of defNames would cover Core, miss every DLC, miss all 294 profile mods and rot the first
    /// time anything was renamed. A bench from a mod installed tomorrow is a bench today.
    ///
    /// The classes are deliberately coarse. A tell has to be true of the thing it is on, and
    /// *"the stool is worn through on one side only"* is true of any seat anybody ever shipped.
    /// Finer classes would mean more authored text saying the same thing.
    /// </summary>
    public enum FixtureClass
    {
        /// <summary>Anything placeable. Tells that are about the room rather than the object.</summary>
        Any = 0,

        /// <summary>Anything the game treats as a work table. The owner's *"production benches"*.</summary>
        Bench = 1,

        /// <summary>Anything sittable.</summary>
        Seat = 2,

        /// <summary>Any table.</summary>
        Table = 3,

        /// <summary>Any humanlike bed.</summary>
        Bed = 4,

        /// <summary>Anything with storage settings — shelves, racks, containers.</summary>
        Storage = 5,

        /// <summary>Anything that emits light.</summary>
        Light = 6,

        /// <summary>A haulable item. The owner's *"items"* and *"loot"*.</summary>
        Item = 7,

        /// <summary>Apparel or a weapon. The owner's *"equipment"*.</summary>
        Equipment = 8,
    }

    /// <summary>
    /// One exact wrong thing about an object found in a coordinate.
    ///
    /// ## The direction, and the half of it that had not been reached
    ///
    /// **Owner direction, 2026-10-04, verbatim:** *"remember lsd unnerving feeling with all things
    /// ie events random spanwns, enemies, allies, nuetrals, even all the crazy things ive mentioned
    /// in the past and anything u can find in the many many prep docs on the Backrooms Universe"*,
    /// and earlier, the sentence this file exists for: *"not just room shape echoes but echos of
    /// thier inhabitance in weird ways and items and equipment and production benches"*.
    ///
    /// 0.12.88-dev took the register to **people and events**. It did not reach objects, and the
    /// owner had already named objects specifically — *"items and equipment and production
    /// benches"*. A coordinate was full of things that were materially varied, correctly placed,
    /// and said nothing at all about who had been using them.
    ///
    /// ## The mechanism is the prep documents', not invented here
    ///
    /// `docs/UNIVERSE_ADAPTATION.md`: *"Ordinary industrial interiors become uncanny through exact
    /// changes."* **The uncanny is one exact change to something ordinary**, which is a testable
    /// property rather than a mood. So the same gate the inhabitant register is held to applies
    /// here: see <see cref="ConfigErrors"/> — **no tell may contain a mood adjective.** A bench
    /// that is *eerie* tells the player nothing. A bench whose *"bills are still queued for a meal
    /// nobody in this space could have ordered"* tells them something, and it is the same fact
    /// every time they come back to read it.
    ///
    /// ## Why most objects have no tell, and that is the design
    ///
    /// `CoordinatePressureLadder.IsQuietRoom` already establishes the rule this follows: *"quiet
    /// stretches are required content"*. A coordinate where every stool, shelf and steel stack has
    /// a sentence on it is not unnerving, it is a museum with too many placards — and it would
    /// bury the inhabitant and event tells that carry the sharper beats. See
    /// <see cref="FixtureTellService.TellPercent"/>: a small derived minority of placed objects
    /// carry one, chosen from the coordinate's own seed, so the same object in the same room says
    /// the same thing on every visit and the room next door says nothing.
    /// </summary>
    public sealed class RimroomsFixtureTellDef : Def
    {
        /// <summary>What kind of object this may be attached to.</summary>
        public FixtureClass appliesTo = FixtureClass.Any;

        /// <summary>
        /// Shallowest effective depth this tell may appear at.
        ///
        /// Two by default, and never one, for the same reason every room archetype declares
        /// `minDepth` of two or more: the shallow yellow rooms are monotonous on purpose and that
        /// emptiness **is** the look. A tell on a stool in the arrival hall would be the first
        /// thing a new player read, and it would spend the setting's one surprise immediately.
        ///
        /// Measured against <see cref="RoomArchetypeService.EffectiveDepth"/>, so a room a dozen
        /// links out on a first level qualifies and the hall it leads back to does not — the
        /// owner's *"variations and oddity ... even on the first level"*.
        /// </summary>
        public int minDepth = 2;

        /// <summary>Deepest depth. Zero or less means no ceiling.</summary>
        public int maxDepth;

        /// <summary>Relative likelihood against other tells legal for the same object.</summary>
        public float weight = 1f;

        /// <summary>
        /// **The one exact wrong fact, readable off the object itself, forever.**
        ///
        /// Keyed rather than inline so it is translatable, which is the same reason every
        /// inhabitant tell and event trace is keyed. Refused at load if absent: a tell def with
        /// no text is a def that silently does nothing, and seven inhabitant families shipped
        /// without a tell for exactly that reason before the field was made mandatory.
        /// </summary>
        public string tellKey;

        /// <summary>
        /// **Where the no-mood-adjective gate lives, and why it is not in this method.**
        ///
        /// The rule itself comes out of `docs/UNIVERSE_ADAPTATION.md` rather than out of taste: if
        /// the uncanny is *one exact change to something ordinary*, then a word that merely
        /// asserts the feeling is a tell that has given up on producing it. The lights going out
        /// is not uncanny; the switches being found already off is.
        ///
        /// It is enforced by `.local/register/proof-unnerving-register.py`, which reads the shipped
        /// `Keyed` XML directly, for two reasons. **It reads what ships** rather than what a
        /// particular language happens to have resolved. And `ConfigErrors` runs inside def
        /// loading, where asserting against resolved translation text would make the check depend
        /// on language-load order — a gate that fires for the wrong reason is worse than no gate,
        /// and this one is too valuable to make flaky.
        /// </summary>
        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (weight <= 0f)
            { yield return "RimroomsFixtureTellDef " + defName + " has a non-positive weight."; }
            if (maxDepth > 0 && maxDepth < minDepth)
            { yield return "RimroomsFixtureTellDef " + defName + " has maxDepth below minDepth."; }
            if (minDepth <= 1)
            {
                // The shallow yellow rooms stay plain. Enforced rather than trusted, because the
                // whole shallow look rests on it and a single def with minDepth 1 would reach
                // every arrival hall in the game.
                yield return "RimroomsFixtureTellDef " + defName +
                    " has minDepth " + minDepth + ", which would put a tell in the shallow rooms.";
            }
            if (string.IsNullOrEmpty(tellKey))
            {
                yield return "RimroomsFixtureTellDef " + defName +
                    " has no tellKey, so nothing on the object says what is wrong with it.";
            }
        }
    }
}
