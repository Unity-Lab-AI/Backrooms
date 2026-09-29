using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Adapters
{
    /// <summary>
    /// Carrying real ingredients through a gate to a real bill, so a workbench stalled for
    /// want of leather on one side can be supplied from the other.
    ///
    /// What this family adds over ordinary hauling is the **trigger**, not the destination.
    /// Storage hauling moves an object when somewhere else is better storage for it; it has
    /// no opinion about what anyone wants to make. This family moves an object because a
    /// specific bill on a specific bench is short of it. That is the "physical ingredient
    /// logistics" half of the contract, and it is why the intent records the actual
    /// <see cref="Bill"/> rather than a recipe and a count.
    ///
    /// Nothing about crafting is reimplemented, and no bill is ever started from here. The
    /// ingredients are put into storage **inside the bill's own ingredient search radius**,
    /// and Core's own `WorkGiver_DoBill` on that map then finds them exactly as it finds
    /// anything else, allocates them with its own `TryFindBestBillIngredients`, and runs the
    /// recipe. The radius is what makes this different from dumping the goods in any old
    /// stockpile: Core's own ingredient validator rejects anything further from the bench
    /// than `bill.ingredientSearchRadius`, so a bill the player has deliberately kept tight
    /// is still supplied correctly.
    ///
    /// **The trap, avoided deliberately: `UnfinishedThing`.** A partly made thing is bound
    /// to one worker. Core's `ClosestUnfinishedThingForBill` requires
    /// `((UnfinishedThing)t).Creator == pawn`, and `Bill_ProductionWithUft` additionally
    /// binds `BoundUft` to a `BoundWorker`. So a different colonist can never resume
    /// somebody else's half-made work, and this family does not try: it delivers material
    /// and stops. A cross-gate worker that picked up a foreign unfinished thing would be
    /// carrying something nobody on either map is allowed to finish.
    ///
    /// Also deliberately not touched: `Bill_Medical` (a surgery needs the patient, which is
    /// the tending family's problem), and the autonomous and mech bill types, which are
    /// state machines with their own gathering phases. Only `Bill_Production` and its
    /// subclasses are supplied. Each of the others needs its own source review first.
    /// </summary>
    public sealed class ConnectedBillAdapter : ConnectedWorkAdapter
    {
        /// <summary>The bill no longer wants this. Not a failure; the material is real and here.</summary>
        internal const string BillSatisfiedKey = "RR_ConnectedWork_BillSatisfied";

        private const int MaximumBillGiversPerMap = 12;
        private const int MaximumBillsPerGiver = 8;
        private const int MaximumIngredientDefs = 12;
        private const int MaximumResourceCandidates = 24;
        private const int MaximumPresenceCandidates = 48;

        /// <summary>
        /// How far out a landing cell is looked for. The bill's own radius is honoured and
        /// is never exceeded, but it defaults to 999, so without a cap of our own a single
        /// planning pass would sweep an entire map's worth of cells.
        /// </summary>
        private const float MaximumDestinationRadius = 24f;

        public override string AdapterId { get { return ConnectedWorkAdapters.BillIngredients; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_BillLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            // Arriving to find the bill suspended, finished, deleted or already supplied is
            // a completed trip with a different ending. The goods are physically on this
            // side and in real hands, and ordinary hauling will put them away.
            if (failureKey == BillSatisfiedKey ||
                failureKey == "RR_ConnectedWork_NoStorageOnArrival")
            { return ConnectedWorkPhase.Completed; }
            return base.TerminalPhaseFor(failureKey);
        }

        public override ConnectedWorkIntent TryPlan(Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (work == null || !work.CanOperate || campaign == null || pawn == null || !pawn.Spawned ||
                pawn.Map == null || pawn.carryTracker == null || !campaign.OwnsMap(pawn.Map))
            { return null; }
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }

            Map home = pawn.Map;
            List<Map> connected = ConnectedWorkScan.ConnectedMaps(campaign, home, pawn);
            for (int index = 0; index < connected.Count; index++)
            {
                Map other = connected[index];
                if (work.DestinationRecentlyRefused(pawn, other)) { continue; }
                PortalRouteStep step;
                bool pending;
                if (!work.Routes.TryNextStep(home, other, out step, out pending)) { continue; }

                // Collect on the side the worker already stands on before crossing to
                // collect, the same one-crossing-beats-two rule the other families use.
                ConnectedWorkIntent fromHere = TryPlanSupply(pawn, work, home, other, step);
                if (fromHere != null) { return fromHere; }
                ConnectedWorkIntent fromThere = TryPlanSupply(pawn, work, other, home, step);
                if (fromThere != null) { return fromThere; }
            }
            return null;
        }

        public override string RevalidateAtFetchSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            if (source == null || source.Destroyed || !source.Spawned || pawn == null ||
                pawn.carryTracker == null || source.Map != pawn.Map ||
                source.GetUniqueLoadID() != intent.SourceThingLoadId || source.stackCount < 1)
            { return "RR_ConnectedWork_ObjectGone"; }
            // The bill may have been suspended, finished, deleted or supplied locally while
            // the worker walked here. Checking before the pickup avoids carrying leather
            // nobody wants any more.
            if (StillShort(intent, source.def) < 1) { return BillSatisfiedKey; }
            if (!HaulAIUtility.PawnCanAutomaticallyHaul(pawn, source, false))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            int wanted = Math.Min(intent.RequestedCount, source.stackCount);
            if (wanted < 1 || pawn.carryTracker.MaxStackSpaceEver(source.def) < 1)
            { return "RR_ConnectedWork_CannotCarry"; }
            if (!pawn.CanReserveAndReach(source, PathEndMode.ClosestTouch, pawn.NormalMaxDanger(), 1, wanted))
            { return "RR_ConnectedWork_ObjectUnavailable"; }
            return null;
        }

        public override Job FetchJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing source = intent == null ? null : intent.SourceThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.FetchJobDefName);
            if (definition == null || source == null || pawn == null || pawn.carryTracker == null)
            { return null; }
            int count = Math.Min(intent.RequestedCount, source.stackCount);
            count = Math.Min(count, pawn.carryTracker.MaxStackSpaceEver(source.def));
            // Never carry more than the bill is actually short of.
            int shortfall = StillShort(intent, source.def);
            if (shortfall > 0) { count = Math.Min(count, shortfall); }
            if (count < 1) { return null; }
            Job job = JobMaker.MakeJob(definition, source);
            job.count = count;
            return job;
        }

        public override string RevalidateAtStoreSide(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            if (intent == null || cargo == null || cargo != intent.Cargo || cargo.Destroyed ||
                cargo.GetUniqueLoadID() != intent.CargoLoadId)
            { return "RR_ConnectedWork_CargoGone"; }

            Bill bill = intent.Bill;
            Thing giver = intent.FinalTarget;
            if (!BillUsable(bill, giver, pawn.Map)) { return BillSatisfiedKey; }
            if (StillShort(intent, cargo.def) < 1) { return BillSatisfiedKey; }

            // Definitive: the worker is standing here, so reservation, reachability and this
            // pawn's own forbidden and area rules finally mean what they say.
            IntVec3 cell = DefinitiveCell(pawn, bill, giver, cargo);
            if (!cell.IsValid) { return "RR_ConnectedWork_NoStorageOnArrival"; }
            // Only the cell is recorded; the bench stays the final target, because the trip
            // is still for that bench. The plain-hauling resolve method would clear it.
            intent.RecordResolvedCellForTarget(cell);
            return null;
        }

        public override Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn)
        {
            Thing cargo = pawn == null || pawn.carryTracker == null ? null : pawn.carryTracker.CarriedThing;
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(ConnectedHaulingAdapter.DeliverJobDefName);
            if (definition == null || intent == null || cargo == null || cargo != intent.Cargo)
            { return null; }
            IntVec3 cell = intent.CandidateStoreCell;
            if (!cell.IsValid || !cell.InBounds(pawn.Map)) { return null; }
            Job job = JobMaker.MakeJob(definition, cargo, cell);
            job.count = cargo.stackCount;
            job.haulMode = HaulMode.ToCellStorage;
            return job;
        }

        // ----- candidate search, explicit-map only -----

        private ConnectedWorkIntent TryPlanSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map billMap, PortalRouteStep step)
        {
            if (step != null && step.Destination != null &&
                !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
            { return null; }

            List<Thing> givers = billMap.listerThings.ThingsInGroup(ThingRequestGroup.PotentialBillGiver);
            if (givers.Count == 0) { return null; }
            int windowStart = ConnectedWorkScan.WindowStart(givers.Count, MaximumBillGiversPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < givers.Count; position++)
            {
                if (examined >= MaximumBillGiversPerMap) { break; }
                examined++;
                Thing giver = givers[position];
                if (!UsableGiver(giver, billMap)) { continue; }
                ConnectedWorkIntent opened = TryPlanForGiver(pawn, work, fetchMap, billMap, giver, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// Every rule here reads the bill giver, its own map, or the player faction. None of
        /// them asks a pawn-specific native question about a map the worker is not on.
        /// </summary>
        private static bool UsableGiver(Thing giver, Map map)
        {
            var billGiver = giver as IBillGiver;
            if (billGiver == null || giver.Destroyed || !giver.Spawned || giver.Map != map)
            { return false; }
            if (giver is Pawn) { return false; }
            if (giver.Faction != Faction.OfPlayer) { return false; }
            if (giver.IsBurning() || giver.IsForbidden(Faction.OfPlayer)) { return false; }
            if (giver.Position.Fogged(map)) { return false; }
            // Core's own first question about a bill giver, and it is a fact about the
            // giver and its own map rather than about any pawn.
            return billGiver.BillStack != null && billGiver.BillStack.AnyShouldDoNow;
        }

        private ConnectedWorkIntent TryPlanForGiver(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map billMap, Thing giver, PortalRouteStep step)
        {
            BillStack stack = ((IBillGiver)giver).BillStack;
            int count = Math.Min(stack.Count, MaximumBillsPerGiver);
            for (int index = 0; index < count; index++)
            {
                Bill bill = stack[index];
                if (!BillUsable(bill, giver, billMap)) { continue; }
                ConnectedWorkIntent opened = TryPlanForBill(pawn, work, fetchMap, billMap, giver, bill, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// Whether this bill is one this family supplies, and wants doing at all.
        ///
        /// <c>ShouldDoNow()</c> is safe to ask about a remote bill, and that was verified
        /// rather than assumed: for a target-count bill it counts products through
        /// <c>Bill.Map</c>, which resolves to the **bill giver's** own map, never the
        /// worker's. It consults no pawn.
        /// </summary>
        private static bool BillUsable(Bill bill, Thing giver, Map expectedMap)
        {
            if (bill == null || giver == null || giver.Destroyed || !giver.Spawned ||
                giver.Map != expectedMap || bill.billStack == null ||
                bill.billStack.billGiver as Thing != giver)
            { return false; }
            // Only ordinary production bills. Medical, autonomous and mech bills have
            // requirements beyond ingredients and each needs its own review first.
            if (!(bill is Bill_Production)) { return false; }
            if (bill.recipe == null || bill.recipe.ingredients == null) { return false; }
            if (bill.suspended || bill.DeletedOrDereferenced) { return false; }
            return bill.ShouldDoNow();
        }

        private ConnectedWorkIntent TryPlanForBill(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map billMap, Thing giver, Bill bill, PortalRouteStep step)
        {
            List<IngredientCount> ingredients = bill.recipe.ingredients;
            for (int index = 0; index < ingredients.Count; index++)
            {
                IngredientCount ingredient = ingredients[index];
                if (ingredient == null || ingredient.filter == null) { continue; }
                List<ThingDef> allowed = ingredient.filter.AllowedThingDefs as List<ThingDef>;
                IEnumerable<ThingDef> defs = allowed ?? ingredient.filter.AllowedThingDefs;
                int seen = 0;
                foreach (ThingDef def in defs)
                {
                    if (seen >= MaximumIngredientDefs) { break; }
                    seen++;
                    if (def == null || !def.EverHaulable) { continue; }
                    if (!bill.IsFixedOrAllowedIngredient(def)) { continue; }
                    int shortfall = Shortfall(bill, giver, ingredient, def);
                    if (shortfall < 1) { continue; }
                    ConnectedWorkIntent opened = TryOpenSupply(pawn, work, fetchMap, billMap,
                        giver, bill, def, shortfall, step);
                    if (opened != null) { return opened; }
                }
            }
            return null;
        }

        /// <summary>
        /// How much more of this ingredient the bill needs than is already sitting inside its
        /// own search radius on its own map.
        ///
        /// Presence is counted across **every** def the ingredient allows, not just the one
        /// being considered for carrying. That matters: a recipe that accepts steel or
        /// plasteel, with plenty of steel by the bench, is not short of anything, and
        /// counting only plasteel would have sent somebody across a gate for nothing.
        /// </summary>
        private static int Shortfall(Bill bill, Thing giver, IngredientCount ingredient, ThingDef carried)
        {
            int required = ingredient.CountRequiredOfFor(carried, bill.recipe, bill);
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
                    // Core's own ingredient validator measures from the giver's Position,
                    // so this measures from exactly the same place.
                    if ((stack.Position - giver.Position).LengthHorizontalSquared > radiusSquared)
                    { continue; }
                    if (stack.IsForbidden(Faction.OfPlayer) || stack.Position.Fogged(map)) { continue; }
                    present += stack.stackCount;
                    if (present >= required) { return 0; }
                }
            }
            return required - present;
        }

        private ConnectedWorkIntent TryOpenSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map billMap, Thing giver, Bill bill, ThingDef def, int shortfall,
            PortalRouteStep step)
        {
            List<Thing> stacks = fetchMap.listerThings.ThingsOfDef(def);
            if (stacks.Count == 0) { return null; }
            int windowStart = ConnectedWorkScan.WindowStart(stacks.Count, MaximumResourceCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < stacks.Count; position++)
            {
                if (examined >= MaximumResourceCandidates) { break; }
                examined++;
                Thing stack = stacks[position];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != fetchMap ||
                    stack.stackCount < 1 || stack is Pawn || stack is Corpse)
                { continue; }
                if (!stack.def.EverHaulable || stack.IsForbidden(Faction.OfPlayer) || stack.IsBurning())
                { continue; }
                if (stack.Position.Fogged(fetchMap)) { continue; }
                if (!work.ObservedAreaAllows(pawn, fetchMap, stack.Position)) { continue; }
                // The bill's own filter, asked about the actual object rather than its def,
                // so quality and hit-point limits on the filter are respected.
                if (!bill.IsFixedOrAllowedIngredient(stack)) { continue; }

                int available = stack.stackCount - work.LeasedCount(stack);
                if (available < 1) { continue; }
                int carryable = pawn.carryTracker.MaxStackSpaceEver(stack.def);
                if (carryable < 1) { continue; }
                int quantity = Math.Min(Math.Min(available, carryable), shortfall);
                if (quantity < 1) { continue; }

                IntVec3 candidateCell = CandidateCell(pawn, work, bill, giver, stack, billMap);
                if (!candidateCell.IsValid) { continue; }

                ConnectedWorkIntent opened = work.Open(this, pawn, stack, billMap,
                    candidateCell, quantity, giver, step, bill);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// A storage cell inside the bill's own search radius, chosen against the bill map's
        /// own storage settings. `IsValidStorageFor(cell, map, thing)` is the only public
        /// map-explicit storage predicate — it is what Core's own haul-to-cell driver uses —
        /// so it is legitimate to ask it about a map the worker is not standing on.
        ///
        /// Cells only, deliberately. A stockpile and a shelf are both reached by cell, and
        /// they are what ingredients actually live in. A container such as a grave is not
        /// ingredient storage, and routing to one would also collide with the intent's
        /// final-target field, which here holds the bench.
        /// </summary>
        private static IntVec3 CandidateCell(Pawn pawn, RimroomsConnectedWorkComponent work,
            Bill bill, Thing giver, Thing sample, Map map)
        {
            float radius = Math.Min(bill.ingredientSearchRadius, MaximumDestinationRadius);
            if (radius < 1f) { radius = 1f; }
            float billRadiusSquared = bill.ingredientSearchRadius * bill.ingredientSearchRadius;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(giver.Position, radius, true))
            {
                if (!cell.InBounds(map)) { continue; }
                // Never outside what the bill itself will accept, even if our own cap is wider.
                if ((cell - giver.Position).LengthHorizontalSquared > billRadiusSquared) { continue; }
                if (!cell.IsValidStorageFor(map, sample)) { continue; }
                if (cell.Fogged(map)) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                return cell;
            }
            return IntVec3.Invalid;
        }

        /// <summary>
        /// The same search, on arrival, with the pawn-specific native checks that could not
        /// legitimately be asked while the worker was elsewhere.
        /// </summary>
        private static IntVec3 DefinitiveCell(Pawn pawn, Bill bill, Thing giver, Thing cargo)
        {
            Map map = pawn.Map;
            float radius = Math.Min(bill.ingredientSearchRadius, MaximumDestinationRadius);
            if (radius < 1f) { radius = 1f; }
            float billRadiusSquared = bill.ingredientSearchRadius * bill.ingredientSearchRadius;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(giver.Position, radius, true))
            {
                if (!cell.InBounds(map)) { continue; }
                if ((cell - giver.Position).LengthHorizontalSquared > billRadiusSquared) { continue; }
                if (!cell.IsValidStorageFor(map, cargo)) { continue; }
                if (cell.IsForbidden(pawn)) { continue; }
                if (!pawn.CanReserveAndReach(cell, PathEndMode.ClosestTouch, pawn.NormalMaxDanger()))
                { continue; }
                return cell;
            }
            return IntVec3.Invalid;
        }

        /// <summary>How much the recorded bill is still short of the recorded ingredient.</summary>
        private static int StillShort(ConnectedWorkIntent intent, ThingDef def)
        {
            Bill bill = intent == null ? null : intent.Bill;
            Thing giver = intent == null ? null : intent.FinalTarget;
            if (bill == null || giver == null || def == null) { return 0; }
            if (!BillUsable(bill, giver, giver.Map)) { return 0; }
            List<IngredientCount> ingredients = bill.recipe.ingredients;
            for (int index = 0; index < ingredients.Count; index++)
            {
                IngredientCount ingredient = ingredients[index];
                if (ingredient == null || ingredient.filter == null) { continue; }
                if (!ingredient.filter.Allows(def)) { continue; }
                return Shortfall(bill, giver, ingredient, def);
            }
            return 0;
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
