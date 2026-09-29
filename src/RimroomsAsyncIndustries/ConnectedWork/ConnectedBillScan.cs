using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// The facts about bills that both bill families need, in one place.
    ///
    /// Two families ask about the same bills from opposite directions:
    ///
    /// * the **carry** family (`ConnectedBillAdapter`) asks *is this bill short of something
    ///   I could bring it*, to justify hauling material through a gate;
    /// * the **work** family (`BillWorkProvider`) asks *does this bill have what it needs
    ///   already*, to justify sending a worker through a gate to run it.
    ///
    /// Those are the same primitives read in opposite senses, so they live here rather than
    /// being written twice. A second copy of the ingredient-counting rule would be a second
    /// place for it to be subtly wrong.
    ///
    /// Everything in this class is a **candidate-half** question: it reads the bill, the bill
    /// giver, and the giver's own map. Nothing here asks a pawn-specific native question, so
    /// every method is safe to call about a map no worker is standing on. The pawn-and-map
    /// specific rules — reservations, the interaction cell, the pawn form of the forbidden
    /// check, and `TryFindBestBillIngredients` itself — are deliberately absent and are left
    /// to Core on arrival.
    /// </summary>
    internal static class ConnectedBillScan
    {
        /// <summary>How many bill givers one remote pass may look at.</summary>
        internal const int MaximumGiversPerMap = 12;

        /// <summary>How many bills on one giver are considered.</summary>
        internal const int MaximumBillsPerGiver = 8;

        /// <summary>How many allowed defs of a single ingredient are counted.</summary>
        internal const int MaximumIngredientDefs = 12;

        /// <summary>How many stacks of one def are counted when testing presence.</summary>
        internal const int MaximumPresenceCandidates = 48;

        /// <summary>
        /// Whether this thing is a bill giver worth considering on that explicit map.
        ///
        /// Every rule reads the giver, its own map, or the player faction. The forbidden test
        /// uses the **faction** overload on purpose: the pawn overload consults the pawn's
        /// allowed area in the pawn's *current* map, which is the wrong map here.
        /// </summary>
        internal static bool UsableGiver(Thing giver, Map map)
        {
            var billGiver = giver as IBillGiver;
            if (billGiver == null || giver.Destroyed || !giver.Spawned || giver.Map != map)
            { return false; }
            // A pawn or a corpse can be a bill giver for surgery. That is Doctor work and
            // belongs to the tending family, which owns the patient's presence and custody.
            if (giver is Pawn || giver is Corpse) { return false; }
            if (giver.Faction != Faction.OfPlayer) { return false; }
            if (giver.IsBurning() || giver.IsForbidden(Faction.OfPlayer)) { return false; }
            if (giver.Position.Fogged(map)) { return false; }
            // Core's own first question about a bill giver, and a fact about the giver and
            // its own map rather than about any pawn.
            return billGiver.BillStack != null && billGiver.BillStack.AnyShouldDoNow;
        }

        /// <summary>
        /// Whether this bill is one either bill family handles at all.
        ///
        /// **The type test is `is Bill_Production` *and not* `is Bill_Autonomous`, and that
        /// second half is load-bearing.** The class hierarchy is:
        ///
        /// <code>
        /// Bill_Autonomous : Bill_Production
        /// Bill_Mech       : Bill_Autonomous
        /// </code>
        ///
        /// so an `is Bill_Production` test on its own **admits** autonomous and mech bills.
        /// The carry family's record said both were deliberately out of scope while its code
        /// let them straight through; this is where that is actually enforced. Both are state
        /// machines with their own gathering phases — `Bill_Autonomous.State`, a mech
        /// gestator's waste producer — and supplying or staffing one correctly means
        /// understanding its phase, which has not been reviewed.
        ///
        /// `Bill_Medical` is excluded by the same test, since it derives from `Bill` directly:
        /// a surgery needs the patient present, which is the tending family's problem.
        /// `Bill_ProductionWithUft` **is** included, because it is an ordinary production bill
        /// whose unfinished thing is handled by Core on arrival.
        ///
        /// <c>ShouldDoNow()</c> is safe to ask about a remote bill, verified rather than
        /// assumed: for a target-count bill it counts products through <c>Bill.Map</c>, which
        /// resolves to the **bill giver's** own map, never any worker's. It consults no pawn.
        /// </summary>
        internal static bool OrdinaryProductionBill(Bill bill, Thing giver, Map expectedMap)
        {
            if (bill == null || giver == null || giver.Destroyed || !giver.Spawned ||
                giver.Map != expectedMap || bill.billStack == null ||
                bill.billStack.billGiver as Thing != giver)
            { return false; }
            if (!(bill is Bill_Production) || bill is Bill_Autonomous) { return false; }
            if (bill.recipe == null || bill.recipe.ingredients == null) { return false; }
            if (bill.suspended || bill.DeletedOrDereferenced) { return false; }
            return bill.ShouldDoNow();
        }

        /// <summary>
        /// How much of this ingredient the bill still lacks within its own search radius, or
        /// zero if it lacks nothing.
        ///
        /// Presence is counted across **every** def the ingredient allows, not just the one
        /// used as the count basis. That matters: a recipe that accepts steel or plasteel,
        /// with plenty of steel by the bench, is not short of anything, and counting only
        /// plasteel would report a shortage and send somebody across a gate for nothing —
        /// repeatedly, because the situation is stable.
        ///
        /// The required count comes from `IngredientCount.CountRequiredOfFor`, so a
        /// small-volume ingredient and a bill-specific count are both Core's numbers.
        /// </summary>
        internal static int Shortfall(Bill bill, Thing giver, IngredientCount ingredient, ThingDef basis)
        {
            if (bill == null || giver == null || ingredient == null || basis == null) { return 0; }
            int required = ingredient.CountRequiredOfFor(basis, bill.recipe, bill);
            if (required < 1) { return 0; }
            Map map = giver.Map;
            if (map == null) { return 0; }
            float radius = bill.ingredientSearchRadius;
            float radiusSquared = radius * radius;
            int present = 0;
            int seen = 0;
            foreach (ThingDef def in ingredient.filter.AllowedThingDefs)
            {
                if (seen >= MaximumIngredientDefs) { break; }
                seen++;
                if (def == null || !bill.IsFixedOrAllowedIngredient(def)) { continue; }
                List<Thing> stacks = map.listerThings.ThingsOfDef(def);
                int checkedStacks = 0;
                for (int index = 0; index < stacks.Count; index++)
                {
                    if (checkedStacks >= MaximumPresenceCandidates) { break; }
                    checkedStacks++;
                    Thing stack = stacks[index];
                    if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != map)
                    { continue; }
                    // Core's own ingredient validator measures from the giver's Position, so
                    // this measures from exactly the same place.
                    if ((stack.Position - giver.Position).LengthHorizontalSquared > radiusSquared)
                    { continue; }
                    if (stack.IsForbidden(Faction.OfPlayer) || stack.Position.Fogged(map)) { continue; }
                    present += stack.stackCount;
                    if (present >= required) { return 0; }
                }
            }
            return required - present;
        }

        /// <summary>
        /// Whether every ingredient this recipe needs already has *something* acceptable
        /// standing within the bill's search radius on the giver's own map.
        ///
        /// **This is a necessary condition, not a sufficient one, and that is deliberate.**
        /// Deciding for certain whether a bill can start means running
        /// `TryFindBestBillIngredients`, which allocates across substitutable defs, respects
        /// the pawn's own reachability and forbidden rules, and is exactly the kind of
        /// expensive pawn-and-map specific question the candidate half may never ask about a
        /// remote map. Core runs it for real on arrival and decides.
        ///
        /// What this test is for is the failure that would otherwise be permanent: a
        /// coordinate holding a bench, a live bill and **no materials at all** would look
        /// like work forever. Core's own throttle cannot save us there —
        /// `nextTickToSearchForIngredients` is only pushed forward when a pawn actually
        /// tries and fails, and on a map with nobody standing on it nobody ever tries. So
        /// without this the family would walk a cook across a gate, find nothing, release the
        /// deployment, and plan the identical trip again.
        ///
        /// A false positive here costs one wasted walk. A false negative costs one planning
        /// delay. The asymmetry is why the test is cheap and approximate rather than exact.
        /// </summary>
        internal static bool EveryIngredientPresent(Bill bill, Thing giver)
        {
            if (bill == null || bill.recipe == null || giver == null) { return false; }
            List<IngredientCount> ingredients = bill.recipe.ingredients;
            if (ingredients == null) { return true; }
            for (int index = 0; index < ingredients.Count; index++)
            {
                IngredientCount ingredient = ingredients[index];
                if (ingredient == null) { continue; }
                ThingDef basis = CountBasis(bill, ingredient);
                // No allowed def at all means the player has filtered this ingredient down to
                // nothing, which Core will also refuse. Not our shortage to solve.
                if (basis == null) { return false; }
                if (Shortfall(bill, giver, ingredient, basis) > 0) { return false; }
            }
            return true;
        }

        /// <summary>
        /// The def used as the basis for "how many are required", which for a small-volume
        /// ingredient is not simply the ingredient's count. The first def the bill actually
        /// allows is used, because that is the cheapest def Core could satisfy it with and
        /// the count is asked per def.
        /// </summary>
        private static ThingDef CountBasis(Bill bill, IngredientCount ingredient)
        {
            int seen = 0;
            foreach (ThingDef def in ingredient.filter.AllowedThingDefs)
            {
                if (seen >= MaximumIngredientDefs) { break; }
                seen++;
                if (def != null && bill.IsFixedOrAllowedIngredient(def)) { return def; }
            }
            return null;
        }

        /// <summary>
        /// Where a worker would actually stand to use this giver. Used for the observed-area
        /// test, so the cell asked about is the cell the work happens from.
        /// </summary>
        internal static IntVec3 ApproachCell(Thing giver)
        {
            return giver != null && giver.def != null && giver.def.hasInteractionCell
                ? giver.InteractionCell : giver.Position;
        }
    }
}
