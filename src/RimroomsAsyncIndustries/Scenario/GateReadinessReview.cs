using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// Whether this start arrives able to raise a gate, stated on the setup page.
    ///
    /// ## Why this exists
    ///
    /// Owner question, 2026-09-30, verbatim: *"and shouldnt that page list the starting equipment
    /// and supplies added from the company to get a gate up quickly as building minified"*.
    ///
    /// The answer to the second half is **no, minified buildings are not needed** — the Async
    /// start's fixed facility already places a machining table, a communications console, a
    /// battery at half charge, three generators at half fuel and nine doors, all standing before
    /// the first tick. Handing the player a pile of furniture to plant instead would be worse and
    /// would break the premise that you arrive at a branch office that exists.
    ///
    /// **The question being asked at all is the defect.** The page listed the fixed facility and
    /// said *"Fixed prebuilt facility"*, then printed forty-three buildings grouped by type — and
    /// nowhere connected any of it to the gate. A player had to already know that a machining
    /// table plus a console plus a battery plus a door is what an opening requires.
    ///
    /// ## And the starts are not equal, which nothing said anywhere
    ///
    /// Counted across the three shipped starts:
    ///
    ///     start             doors  bench  console  battery  generator
    ///     Async Industries      9      1        1        1          3
    ///     Furniture Store       8      0        1        1          1
    ///     Solo or group         1      0        0        0          0
    ///
    /// **Two of three cannot raise a gate from what they arrive with.** For the solo start that is
    /// the design — you begin inside, the map itself is a coordinate, and found doors reach through
    /// depth 3 while the way out is guaranteed. For the Store it is at least a question. Either
    /// way, **a player deserves to be told before they press Start**, which is all this does.
    ///
    /// ## Read, never hardcoded
    ///
    /// The requirement comes out of the gate recipe itself — its ingredients and its
    /// `recipeUsers` — so retuning the recipe retunes this readout. Nothing here names a count or
    /// a bench, and a missing recipe is reported rather than assumed.
    /// </summary>
    internal static class GateReadinessReview
    {
        /// <summary>The recipe that turns designated equipment into a working gate.</summary>
        private const string AssemblyRecipe = "RR_AssembleMachineGate";

        /// <summary>One prerequisite, and how many of it this start arrives with.</summary>
        internal struct Prerequisite
        {
            public string LabelKey;
            public string Detail;
            public int Present;
        }

        /// <summary>
        /// The ingredient line for the assembly bill, as the recipe states it, or null when the
        /// recipe is missing. Null is reported on the page: a start whose assembly recipe has gone
        /// cannot raise a gate at all, and that is worth saying rather than omitting.
        /// </summary>
        internal static string AssemblyCost()
        {
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(AssemblyRecipe);
            if (recipe == null || recipe.ingredients == null || recipe.ingredients.Count == 0)
            { return null; }
            var parts = new List<string>();
            foreach (IngredientCount ingredient in recipe.ingredients)
            {
                if (ingredient == null || ingredient.filter == null) { continue; }
                ThingDef named = ingredient.filter.AllowedThingDefs.FirstOrDefault();
                if (named == null) { continue; }
                parts.Add(ingredient.GetBaseCount().ToString("N0") + " " + named.label);
            }
            return parts.Count == 0 ? null : string.Join(", ", parts);
        }

        /// <summary>The bench the recipe runs on, by label, or null when the recipe is missing.</summary>
        internal static ThingDef AssemblyBench()
        {
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(AssemblyRecipe);
            if (recipe == null || recipe.recipeUsers == null) { return null; }
            return recipe.recipeUsers.FirstOrDefault();
        }

        /// <summary>
        /// What a gate needs, and how much of each this start places.
        ///
        /// The bench comes from the recipe. The console, battery and power are the gate's own
        /// operating requirements — a designated gate needs a console to be staffed at, a battery
        /// to hold its return reserve, and something generating into that battery.
        /// </summary>
        internal static List<Prerequisite> Check(RimroomsStartDef start)
        {
            var found = new List<Prerequisite>();
            if (start == null) { return found; }

            found.Add(new Prerequisite
            {
                LabelKey = "RR_Setup_GateNeedsDoor",
                Detail = null,
                Present = start.doors == null ? 0 : start.doors.Count,
            });

            ThingDef bench = AssemblyBench();
            found.Add(new Prerequisite
            {
                LabelKey = "RR_Setup_GateNeedsBench",
                Detail = bench == null ? null : bench.label,
                Present = CountMatching(start, AcceptedBench),
            });

            found.Add(new Prerequisite
            {
                LabelKey = "RR_Setup_GateNeedsConsole",
                Detail = null,
                Present = CountMatching(start, AcceptedConsole),
            });

            found.Add(new Prerequisite
            {
                LabelKey = "RR_Setup_GateNeedsBattery",
                Detail = null,
                Present = CountOfNamed(start, "Battery"),
            });

            // Any generator, not a named one: a branch may be powered however the start chose.
            found.Add(new Prerequisite
            {
                LabelKey = "RR_Setup_GateNeedsPower",
                Detail = null,
                Present = start.buildings == null ? 0 : start.buildings.Count(plan =>
                    plan != null && plan.thing != null &&
                    plan.thing.HasComp(typeof(CompPowerPlant))),
            });

            return found;
        }

        private static int CountOf(RimroomsStartDef start, ThingDef definition)
        {
            if (start.buildings == null || definition == null) { return 0; }
            return start.buildings.Count(plan => plan != null && plan.thing == definition);
        }

        /// <summary>
        /// The same membership binding uses: the gate console component on a comms console type,
        /// so the company's own console counts as well as Core's.
        /// </summary>
        private static bool AcceptedConsole(ThingDef definition)
        {
            return definition != null && definition.thingClass != null &&
                typeof(Building_CommsConsole).IsAssignableFrom(definition.thingClass) &&
                definition.HasComp(typeof(Gate.CompRimroomsGateConsole));
        }

        /// <summary>Any bench the assembly recipe runs on, or the company's own bench.</summary>
        private static bool AcceptedBench(ThingDef definition)
        {
            if (definition == null) { return false; }
            if (definition.defName == Gate.RimroomsGateProviders.CompanyAssemblyBench) { return true; }
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(AssemblyRecipe);
            return recipe != null && recipe.recipeUsers != null && recipe.recipeUsers.Contains(definition);
        }

        private static int CountMatching(RimroomsStartDef start, System.Func<ThingDef, bool> accepts)
        {
            if (start.buildings == null) { return 0; }
            return start.buildings.Count(plan => plan != null && accepts(plan.thing));
        }

        private static int CountOfNamed(RimroomsStartDef start, string defName)
        {
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            return definition == null ? 0 : CountOf(start, definition);
        }
    }
}
