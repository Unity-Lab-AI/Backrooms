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
    /// Carrying real food through a gate to people who have none on their side.
    ///
    /// The eighth adapter, and the one that matters most for keeping anybody alive on the far
    /// side of a gate. Its trigger is deliberately narrow: **there are hungry people on that
    /// map and nothing there they will eat.** Not "somewhere else is better storage for this
    /// meal", which is all ordinary hauling ever asks.
    ///
    /// That narrowness is the point. Storage hauling would never move food to a map that has
    /// no better storage for it, so without this family a colonist on the far side of a gate
    /// can starve beside an empty larder while the pantry at home is full.
    ///
    /// ## Why a hungry pawn does not walk through a gate to eat
    ///
    /// This was considered and **decided against**, rather than deferred, and the reasoning is
    /// recorded here so it is not quietly reversed later:
    ///
    /// 1. **Eating is a need, not work.** Core's `JobGiver_GetFood` is a
    ///    `ThinkNode_JobGiver` in the think tree, not a `WorkGiver`. Every family in this mod
    ///    rides Core's own `JobGiver_Work`; reaching a need would mean patching Core's think
    ///    tree, which this project's standing method avoids and which is the most
    ///    conflict-prone thing to touch across a 294-mod profile.
    /// 2. **A laboratory gate can close mid-journey.** The duration ladder means an opening is
    ///    finite until high tech. Sending a *starving* pawn on a multi-map walk risks
    ///    stranding it on the far side with no food and no way back — strictly worse than
    ///    being hungry at home, and it kills colonists rather than wasting a walk.
    /// 3. **The logistical answer solves the real problem.** If people are over there, food
    ///    should be over there. That is this family, and it carries no such risk.
    ///
    /// ## What Core decides, and we do not
    ///
    /// * <c>map.mapPawns.SpawnedHungryPawns</c> is Core's own map-explicit hungry-pawn list,
    ///   the same one `WorkGiver_FeedPatient` uses.
    /// * <c>Pawn.WillEat(ThingDef)</c> with no getter decides whether a given eater would
    ///   touch a given food at all — ideology, title, teetotalling and race food rules
    ///   included. Never reimplemented, and never overridden.
    /// * Nutrition, meal quality, rot and preference ordering stay entirely Core's. This
    ///   family chooses *that food should be there*, never *what anybody eats*.
    ///
    /// ## Profile rows, read first
    ///
    /// * **125 Meals On Wheels** — its review establishes something different from what the
    ///   name suggests: colonists may take meals **from animals or other pawns** when other
    ///   food is unavailable. It is a food-*sourcing* convenience, not meal delivery, so it
    ///   does not overlap this family. Its recorded disposition explicitly warns not to rely
    ///   on it for expedition or outpost ration accounting, which is another reason this
    ///   family exists rather than leaning on it.
    /// * **269 Gastronomy** — a restaurant, waiter and register layer requiring Cash Register.
    ///   Optional cafeteria content with **unresolved rights** (the Workshop text refers to
    ///   GPL while the continuation repository declares CC BY-NC-ND), so its code and art must
    ///   not be adapted and no adapter is built. Company meals must work without it, and they
    ///   do: this family moves raw and cooked food, and never touches dining or service.
    /// * **195 RimFridge** — refrigerated storage. Reached as an ordinary haul destination
    ///   through `IHaulDestination`, which the container route already covers; nothing
    ///   special is needed here.
    /// * **229 Tradable Meals** is trade-only. **93 Food Poisoning Stack Fix** and
    ///   **48 Bed Rest For Food Poisoning** act on hediffs after eating, not on food logistics.
    ///
    /// None is a dependency and every one may be absent.
    /// </summary>
    public sealed class ConnectedFoodAdapter : ConnectedWorkAdapter
    {
        /// <summary>They have food now. Not a failure; what was carried is real and here.</summary>
        internal const string FedKey = "RR_ConnectedWork_AlreadyFed";

        private const int MaximumHungryPerMap = 24;
        private const int MaximumFoodCandidates = 24;
        private const int MaximumPresenceCandidates = 48;

        /// <summary>
        /// How many meals to aim at per trip. A carry is one stack in one pair of hands, so
        /// this is not a ration plan — it is a cap that stops one worker promising to feed a
        /// whole map from a single trip, while still making the trip worth taking.
        /// </summary>
        private const int MealsPerTrip = 4;

        public override string AdapterId { get { return ConnectedWorkAdapters.FoodSupply; } }
        public override int AdapterVersion { get { return 1; } }
        public override string LabelKey { get { return "RR_ConnectedWork_FoodLabel"; } }

        public override ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        {
            if (failureKey == FedKey || failureKey == "RR_ConnectedWork_NoStorageOnArrival")
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
                if (step != null && step.Destination != null &&
                    !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
                { continue; }

                // Collect on the side the worker already stands on first: one crossing beats two.
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
            if (!StillHungry(intent, source.def)) { return FedKey; }
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
            // Deliberately *not* refused when they are no longer hungry. Food keeps, and a map
            // with people on it is a map that will be hungry again shortly; setting the meals
            // down in storage there is the right outcome either way. Only a genuinely absent
            // destination ends this trip.
            IntVec3 cell;
            if (!StoreUtility.TryFindBestBetterStorageFor(cargo, pawn, pawn.Map,
                StoragePriority.Unstored, pawn.Faction, out cell, out IHaulDestination _) ||
                !cell.IsValid)
            { return "RR_ConnectedWork_NoStorageOnArrival"; }
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
            Map fetchMap, Map hungryMap, PortalRouteStep step)
        {
            List<Pawn> hungry = hungryMap.mapPawns == null
                ? null : hungryMap.mapPawns.SpawnedHungryPawns;
            if (hungry == null || hungry.Count == 0) { return null; }
            int windowStart = ConnectedWorkScan.WindowStart(hungry.Count, MaximumHungryPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < hungry.Count; position++)
            {
                if (examined >= MaximumHungryPerMap) { break; }
                examined++;
                Pawn eater = hungry[position];
                if (!OursAndHungry(eater, hungryMap)) { continue; }
                if (!work.ObservedAreaAllows(pawn, hungryMap, eater.PositionHeld)) { continue; }
                // Only a genuine shortage justifies a trip: if there is already something
                // there this eater would eat, nothing crosses.
                if (AnyEdibleFoodOn(hungryMap, eater)) { continue; }
                ConnectedWorkIntent opened = TryOpenSupply(pawn, work, fetchMap, hungryMap, eater, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// Whether this hungry pawn is one this company feeds. Patient-side facts only.
        ///
        /// Deliberately limited to our own people and our guests: a wild animal or a hostile
        /// being hungry on the far side of a gate is not a logistics problem, and hauling food
        /// to it would be feeding the Backrooms.
        /// </summary>
        private static bool OursAndHungry(Pawn eater, Map map)
        {
            if (eater == null || eater.Destroyed || eater.Dead || !eater.Spawned ||
                eater.Map != map || eater.needs == null || eater.needs.food == null)
            { return false; }
            if (!eater.RaceProps.EatsFood) { return false; }
            if (eater.Faction != Faction.OfPlayer && eater.HostFaction != Faction.OfPlayer)
            { return false; }
            return FeedPatientUtility.IsHungry(eater);
        }

        private ConnectedWorkIntent TryOpenSupply(Pawn pawn, RimroomsConnectedWorkComponent work,
            Map fetchMap, Map hungryMap, Pawn eater, PortalRouteStep step)
        {
            List<Thing> available = fetchMap.listerThings.ThingsInGroup(ThingRequestGroup.FoodSourceNotPlantOrTree);
            if (available.Count == 0) { return null; }
            int windowStart = ConnectedWorkScan.WindowStart(available.Count, MaximumFoodCandidates, pawn);
            int examined = 0;
            for (int position = windowStart; position < available.Count; position++)
            {
                if (examined >= MaximumFoodCandidates) { break; }
                examined++;
                Thing stack = available[position];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != fetchMap ||
                    stack.stackCount < 1 || stack is Pawn)
                { continue; }
                if (!stack.def.EverHaulable || stack.IsForbidden(Faction.OfPlayer) || stack.IsBurning())
                { continue; }
                if (stack.Position.Fogged(fetchMap)) { continue; }
                // Core decides what this eater will touch, including ideology, title,
                // teetotalling and race rules. Never our own judgement.
                if (!eater.WillEat(stack.def, null, true, true)) { continue; }
                if (!work.ObservedAreaAllows(pawn, fetchMap, stack.Position)) { continue; }
                // Taking the last of the food from the side we are standing on would simply
                // move the starvation, so a stack that is the only thing feeding people here
                // is left alone.
                if (!SafeToTakeFrom(fetchMap, stack, eater)) { continue; }

                int free = stack.stackCount - work.LeasedCount(stack);
                if (free < 1) { continue; }
                int carryable = pawn.carryTracker.MaxStackSpaceEver(stack.def);
                if (carryable < 1) { continue; }
                int quantity = Math.Min(Math.Min(free, carryable), MealsPerTrip);
                if (quantity < 1) { continue; }

                ConnectedWorkIntent opened = work.Open(this, pawn, stack, hungryMap,
                    IntVec3.Invalid, quantity, eater, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// Whether food may be taken from this map without creating the same shortage here.
        ///
        /// A map with nobody hungry on it can always spare food. A map that does have hungry
        /// people may only give away food if something else there would feed them, so the
        /// last meal on a map never leaves it.
        /// </summary>
        private static bool SafeToTakeFrom(Map fetchMap, Thing stack, Pawn eater)
        {
            List<Pawn> hungryHere = fetchMap.mapPawns == null
                ? null : fetchMap.mapPawns.SpawnedHungryPawns;
            if (hungryHere == null || hungryHere.Count == 0) { return true; }
            int examined = 0;
            for (int index = 0; index < hungryHere.Count; index++)
            {
                if (examined >= MaximumHungryPerMap) { break; }
                examined++;
                Pawn local = hungryHere[index];
                if (!OursAndHungry(local, fetchMap)) { continue; }
                if (AnyEdibleFoodOtherThan(fetchMap, local, stack)) { continue; }
                return false;
            }
            return true;
        }

        private static bool AnyEdibleFoodOn(Map map, Pawn eater)
        {
            return AnyEdibleFoodOtherThan(map, eater, null);
        }

        private static bool AnyEdibleFoodOtherThan(Map map, Pawn eater, Thing excluded)
        {
            List<Thing> food = map.listerThings.ThingsInGroup(ThingRequestGroup.FoodSourceNotPlantOrTree);
            int examined = 0;
            for (int index = 0; index < food.Count; index++)
            {
                if (examined >= MaximumPresenceCandidates) { break; }
                examined++;
                Thing thing = food[index];
                if (thing == null || thing == excluded || thing.Destroyed || !thing.Spawned ||
                    thing.Map != map)
                { continue; }
                if (thing.IsForbidden(Faction.OfPlayer) || thing.Position.Fogged(map)) { continue; }
                if (!eater.WillEat(thing.def, null, true, true)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>Whether the recorded eater still has nothing there it would eat.</summary>
        private static bool StillHungry(ConnectedWorkIntent intent, ThingDef def)
        {
            var eater = intent == null ? null : intent.FinalTarget as Pawn;
            if (eater == null || def == null) { return false; }
            Map map = eater.MapHeld;
            if (map == null || !OursAndHungry(eater, map)) { return false; }
            if (!eater.WillEat(def, null, true, true)) { return false; }
            return !AnyEdibleFoodOn(map, eater);
        }

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
    }
}
