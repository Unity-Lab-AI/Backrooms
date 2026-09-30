using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// How many places this company may hold open at once.
    ///
    /// ## Owner direction, 2026-09-30, verbatim
    ///
    /// *"dont let them go more than 5 remember the games mechanics and limits built in if they
    /// find a gate to a world map tile or a deeper backrroms and they have 5 mpas they should
    /// gett a warning this gate is blocked your holding open too many gates, but per scerio
    /// styled"*
    ///
    /// and, clarifying where the number comes from:
    ///
    /// *"5 is the limit of other colonies available so a backrooms level should be one colonly
    /// bacskicly in my thinking"*
    ///
    /// ## Why a cap at all, and why not eviction
    ///
    /// <see cref="Generation.RimroomsDestinationMapParent.ShouldRemoveMapNow"/> returns **false,
    /// always** — a coordinate is a place you can go back to, so its map is never unloaded. That
    /// was free when a coordinate was 60x60. At **300x300** it is up to 90,000 cells carrying
    /// roughly 70,000 mineable rocks, and `MaximumCoordinates` is **512**.
    ///
    /// The owner's first answer was to evict the least recently used map. They replaced it with
    /// this, and it is better on every count: **nothing the player looted or built ever resets**,
    /// memory is bounded by construction rather than by a policy that runs later, and the limit
    /// is **diegetic** — *you are holding open too many gates* is a fact about the fiction, not an
    /// apology about memory.
    ///
    /// ## Why the number is read from Core and not written here
    ///
    /// <c>Prefs.MaxNumberOfPlayerSettlements</c> is a player option: a slider from **1 to 5**,
    /// default 5, which Core enforces in `SettleUtility` as
    /// <c>count &gt;= Prefs.MaxNumberOfPlayerSettlements</c>. That is the *"limits built in"* the
    /// owner is pointing at, so this reads it rather than hard-coding a 5 — a player who moves
    /// the slider to 3 gets 3, and a mod that raises it gets more.
    ///
    /// **Core cannot see a coordinate map.** Its own count is
    /// <c>map.IsPlayerHome &amp;&amp; map.Parent is Settlement</c>, plus gravship landings, and a
    /// <see cref="Generation.RimroomsDestinationMapParent"/> is neither. So this counts both:
    /// Core's settlements, and ours. *"A backrooms level should be one colonly bacskicly."*
    ///
    /// A scenario may override the budget, which is *"per scerio styled"*.
    /// </summary>
    internal static class OpenMapBudget
    {
        /// <summary>The refusal shown at a doorway that would open one map too many.</summary>
        internal const string BlockedKey = "RR_Frontier_TooManyGatesHeld";

        /// <summary>
        /// A company needs room for where it lives and one place beyond it, or the mod cannot
        /// function at all.
        ///
        /// **This floor is load-bearing, and it exists because of a bug it prevents.**
        /// `Prefs.MaxNumberOfPlayerSettlements` is a slider the player can set to **1**. The
        /// solo/group start opens a coordinate during `PostGameStart`, at which point the surface
        /// map already counts as one held place -- so with a budget of 1 the start's own opening
        /// would be refused and that scenario would fail on a clean new game.
        /// </summary>
        internal const int MinimumBudget = 2;

        /// <summary>
        /// The budget for this game: the scenario's own figure when it sets one, otherwise the
        /// player's colony limit, never below <see cref="MinimumBudget"/>.
        /// </summary>
        internal static int Budget
        {
            get
            {
                Scenario.ScenPart_RimroomsStart part = Scenario.ScenPart_RimroomsStart.Current;
                int scenario = part == null || part.startDef == null ? 0 : part.startDef.openMapBudget;
                int budget = scenario > 0 ? scenario : Prefs.MaxNumberOfPlayerSettlements;
                return Mathf.Max(MinimumBudget, budget);
            }
        }

        /// <summary>
        /// How many are held right now. A colony counts, and so does a Backrooms level, because
        /// both cost the same thing: a loaded map.
        /// </summary>
        internal static int Held
        {
            get
            {
                int held = 0;
                if (Find.Maps == null) { return 0; }
                foreach (Map map in Find.Maps)
                {
                    if (map == null) { continue; }
                    if (map.Parent is Generation.RimroomsDestinationMapParent) { held++; }
                    else if (map.IsPlayerHome && map.Parent is Settlement) { held++; }
                    else if (map.wasSpawnedViaGravShipLanding) { held++; }
                }
                return held;
            }
        }

        /// <summary>
        /// Whether one more place may be opened.
        ///
        /// **Asked before anything is created**, so a refusal costs the player nothing but the
        /// walk to the door.
        /// </summary>
        internal static bool CanOpenAnother { get { return Held < Budget; } }

        /// <summary>The numbers, for a message that tells the player where they stand.</summary>
        internal static string Describe()
        {
            return Held.ToString() + "/" + Budget.ToString();
        }
    }
}
