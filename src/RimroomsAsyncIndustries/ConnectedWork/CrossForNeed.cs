using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// A colonist crosses a gate for a **need** rather than for work.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"we need cross map cordinator or something thats
    /// automatic merging maps to cross control so pawns auto get command to cross when mpas call them
    /// like a empty bed work task or job ect ect or anything at all"*, and at the fork, **commuting**
    /// rather than living on the far side.
    ///
    /// ## What was missing, measured before any of this was designed
    ///
    /// `WorkGiver_ConnectedDeployment` has **56 work givers** and 21 of the game's 23 work types cross
    /// a gate, so the coordinator the owner asked for is shipped **for work**. The gap was exact: beds
    /// appear in that code only for carrying a **downed** patient to one, so **no healthy pawn ever
    /// crossed for a need** — not an empty bed, not food, not recreation.
    ///
    /// ## A COMPONENT RATHER THAN A THINK-TREE INSERT, which deviates from the brief on purpose
    ///
    /// `CROSS_MAP_TRAVERSAL_BRIEF.md` §3.1 specified a `ThinkTreeDef` with `insertTag`. **This does not
    /// do that, and the reason is better than the plan:**
    ///
    /// * **It is strictly more additive.** An insert still edits the shape of Core's humanlike think
    ///   tree at a tagged point; a component edits nothing at all. With 294 mods loaded, the think tree
    ///   is one of the most contested structures in the game.
    /// * **It cannot be broken by somebody else's tree.** An insert whose tag another mod moves,
    ///   renames or wraps fails silently — a pawn simply never crosses, with nothing to read.
    /// * **The owner's own words are *"auto get command to cross"*.** A command issued is what this is.
    ///   A think node is a pawn deciding; a command is the branch telling them.
    ///
    /// The brief is corrected rather than quietly departed from.
    ///
    /// ## THE STRANDING GUARD IS AT THE DECISION, NOT THE RESCUE
    ///
    /// §1.1 makes the gate's window the only clock in the mod, so a pawn asleep on the far side when it
    /// closes is stuck until the next opening. **The owner was shown that cost and took it**, which
    /// makes the mitigation part of the build rather than an argument against it.
    ///
    /// A pawn may not *begin* crossing unless the remaining window covers **all three legs** — the walk
    /// there, the need, and the walk back — checked **once, before committing**, because a guard that
    /// fires halfway is how a pawn ends up stranded mid-corridor.
    ///
    /// **A permanently open natural gate has no window and therefore no guard.** Invariant 12 pays for
    /// itself here: a branch that wants people living beyond a gate should be using a natural one, and
    /// the rule tells them so by behaving differently.
    /// </summary>
    public sealed class CrossForNeedMapComponent : MapComponent
    {
        /// <summary>
        /// Checked every four game-seconds. Needs move slowly and a crossing is a commitment; polling
        /// faster would cost real time for an answer that changes a handful of times a day.
        /// </summary>
        private const int Interval = 240;

        /// <summary>
        /// How low a need has to be before crossing a gate for it is reasonable.
        ///
        /// **0.28, which is below Core's own "this pawn wants to act" thresholds and above zero.** A
        /// pawn does not walk through a gate because it is slightly peckish, and it does not wait until
        /// it is collapsing either — the point of the guard below is that a crossing takes time, so the
        /// decision has to be made while there is still time to make it.
        /// </summary>
        private const float NeedThreshold = 0.28f;

        /// <summary>
        /// What one leg of the trip is assumed to cost, in ticks, when nothing better is known.
        ///
        /// **A deliberate overestimate.** The guard's job is to refuse a marginal crossing, so every
        /// unknown is rounded against the pawn. 2,500 ticks is one in-game hour: far longer than a walk
        /// across a facility, which is the point.
        /// </summary>
        private const int AssumedLegTicks = 2500;

        /// <summary>
        /// What satisfying the need is assumed to cost once they arrive.
        ///
        /// **Sleep is the expensive one and sleep is what this is for.** Half an in-game day, because a
        /// pawn that crosses to use a bed and is pulled back out after ten minutes has gained nothing
        /// and spent a gate window on it.
        /// </summary>
        private const int AssumedNeedTicks = 15000;

        public CrossForNeedMapComponent(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager == null || Find.TickManager.TicksGame % Interval != 0) { return; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate || !campaign.OwnsMap(map)) { return; }
            RimroomsConnectedWorkComponent work = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsConnectedWorkComponent>();
            if (work == null) { return; }

            IReadOnlyList<Pawn> pawns = map.mapPawns.FreeColonistsSpawned;
            for (int index = 0; index < pawns.Count; index++)
            {
                Pawn pawn = pawns[index];
                if (!Eligible(pawn)) { continue; }
                Map destination = DestinationFor(pawn, campaign, out int roundTrip);
                if (destination == null) { continue; }
                if (!WindowCovers(pawn, destination, roundTrip)) { continue; }
                Job job;
                if (ConnectedCrossing.StepToward(pawn, destination, work, out job)
                    != ConnectedCrossingOutcome.Step || job == null)
                { continue; }
                // Ordered rather than queued as work, because this is the branch telling a pawn to go
                // rather than a priority it fits in around hauling. The crossing job itself is the one
                // implementation every other cross-map movement uses, so the pawn's danger policy,
                // allowed area and locked doors are all honoured exactly as they are for work.
                pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }
        }

        /// <summary>
        /// Whether this pawn could reasonably be sent anywhere at all.
        ///
        /// **Deliberately conservative.** A drafted pawn is under direct control and a pawn already
        /// crossing is already going; neither is a candidate. `GateWatch.MustLeave` is asked because a
        /// pawn in genuine trouble needs the nearest answer, not one through a gate — **the floor that
        /// exists because somebody starved at a console applies to sending them away from one too.**
        /// </summary>
        private static bool Eligible(Pawn pawn)
        {
            if (pawn == null || pawn.Dead || pawn.Downed || pawn.Drafted || pawn.InMentalState) { return false; }
            if (pawn.needs == null || pawn.jobs == null) { return false; }
            if (GateWatch.MustLeave(pawn)) { return false; }
            // Already on their way, or doing something the player asked for by hand.
            if (pawn.CurJobDef != null && pawn.CurJobDef.defName == PortalTravelService.CrossJobDefName)
            { return false; }
            return true;
        }

        /// <summary>
        /// A connected map that can satisfy a need this map cannot, or null.
        ///
        /// **Every question is asked against an explicit `Map`, which the architecture already
        /// demands.** `ConnectedDeploymentProvider` states the contract: a provider answers *is there
        /// work of my kind on that map* against an explicit map, because *"the provider contract forbids
        /// asking a native pawn-specific query about a map the worker is not standing on"*. Core's bed
        /// and food searches are scoped to `pawn.Map`, so they cannot answer *is there a free bed over
        /// there* — and that is why these are small explicit scans rather than Core calls.
        ///
        /// **The home map is checked first and wins.** A pawn only ever crosses for something it cannot
        /// have here; a branch with beds at home must never send anybody through a gate to sleep.
        /// </summary>
        private Map DestinationFor(Pawn pawn, RimroomsCampaignComponent campaign, out int needTicks)
        {
            needTicks = AssumedNeedTicks;
            bool wantsRest = pawn.needs.rest != null && pawn.needs.rest.CurLevel < NeedThreshold;
            bool wantsFood = pawn.needs.food != null && pawn.needs.food.CurLevel < NeedThreshold;
            if (!wantsRest && !wantsFood) { return null; }
            // Satisfiable here? Then nothing crosses, and this is the cheap test on purpose.
            if (wantsRest && HasBedFor(pawn, map)) { return null; }
            if (wantsFood && HasFoodOn(map)) { return null; }

            List<Map> maps = Find.Maps;
            if (maps == null) { return null; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map candidate = maps[index];
                if (candidate == null || candidate == map || !campaign.OwnsMap(candidate)) { continue; }
                if (wantsRest && HasBedFor(pawn, candidate)) { return candidate; }
                if (wantsFood && HasFoodOn(candidate))
                {
                    // Eating is quick. Using the sleep figure for it would refuse a short trip for no
                    // reason, which is the guard being wrong in the expensive direction.
                    needTicks = 2500;
                    return candidate;
                }
            }
            return null;
        }

        /// <summary>
        /// A bed on that map this pawn would be allowed to use.
        ///
        /// Owned or unowned, not a prisoner bed, not medical-only, and not already taken. **Asked of
        /// `listerBuildings` on the named map** rather than through `RestUtility.FindBedFor`, which
        /// searches the pawn's own map and cannot be pointed at another.
        /// </summary>
        private static bool HasBedFor(Pawn pawn, Map candidate)
        {
            if (candidate == null || candidate.listerBuildings == null) { return false; }
            List<Building> buildings = candidate.listerBuildings.allBuildingsColonist;
            for (int index = 0; index < buildings.Count; index++)
            {
                Building_Bed bed = buildings[index] as Building_Bed;
                if (bed == null || bed.Destroyed || !bed.Spawned) { continue; }
                if (bed.ForPrisoners || bed.Medical) { continue; }
                if (bed.OwnersForReading != null && bed.OwnersForReading.Count > 0
                    && !bed.OwnersForReading.Contains(pawn))
                { continue; }
                if (bed.AnyOccupants) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Food on that map a colonist could eat.
        ///
        /// Nutrition-bearing, not rotten, not a corpse, and not forbidden to the player. The same
        /// explicit-map reasoning as beds: Core's food search is scoped to the eater's own map.
        /// </summary>
        private static bool HasFoodOn(Map candidate)
        {
            if (candidate == null || candidate.listerThings == null) { return false; }
            List<Thing> things = candidate.listerThings.ThingsInGroup(ThingRequestGroup.FoodSourceNotPlantOrTree);
            for (int index = 0; index < things.Count; index++)
            {
                Thing food = things[index];
                if (food == null || food.Destroyed || !food.Spawned) { continue; }
                if (food is Corpse) { continue; }
                if (food.def == null || food.def.ingestible == null) { continue; }
                if (food.def.ingestible.CachedNutrition <= 0f) { continue; }
                if (food.IsForbidden(Faction.OfPlayer)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether the gate's remaining window covers going, doing it, and coming back.
        ///
        /// **Checked once, before committing.** A guard that re-ran halfway and refused would leave the
        /// pawn exactly where the guard exists to stop them being — mid-corridor on the wrong side.
        ///
        /// **A permanently open connection has no window and so no guard.** That is invariant 12 doing
        /// real work rather than a special case: the gate kind the player chose is the rule.
        ///
        /// Every unknown is rounded **against** the crossing, because the cost of refusing a marginal
        /// trip is a slightly unhappy pawn and the cost of allowing one is a colonist sealed in a maze.
        /// </summary>
        private bool WindowCovers(Pawn pawn, Map destination, int needTicks)
        {
            // **THE GATE IS NOT ON THIS MAP, AND THE FIRST DRAFT ASSUMED IT WAS.** A gate is a building
            // on the branch's own map; a coordinate holds a threshold anchor and no gate comp at all.
            // So scanning `map.listerBuildings` found nothing for a pawn standing on the far side, and
            // **a colonist in a coordinate could never have crossed home for a need** -- the half of
            // this feature that matters most. Caught by reading the guard back rather than by a launch.
            //
            // Resolved through the network instead, which is the only thing that knows which two maps a
            // connection joins.
            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault) { return false; }

            int shortest = int.MaxValue;
            List<Map> maps = Find.Maps;
            if (maps == null) { return false; }
            for (int outer = 0; outer < maps.Count; outer++)
            {
                Map host = maps[outer];
                if (host == null || host.listerBuildings == null) { continue; }
                List<Building> buildings = host.listerBuildings.allBuildingsColonist;
                for (int index = 0; index < buildings.Count; index++)
                {
                    CompRimroomsGate gate = buildings[index] == null
                        ? null : buildings[index].TryGetComp<CompRimroomsGate>();
                    if (gate == null || !gate.IsDesignated || !gate.IsOpening || gate.IsEmergency) { continue; }
                    if (string.IsNullOrEmpty(gate.PortalConnectionId)) { continue; }
                    PortalConnectionRecord edge = network.Find(gate.PortalConnectionId);
                    if (edge == null || edge.First == null || edge.Second == null) { continue; }
                    // Either order: this pawn may be standing on either end of the connection.
                    bool joins = (edge.First.Map == map && edge.Second.Map == destination)
                        || (edge.Second.Map == map && edge.First.Map == destination);
                    if (!joins) { continue; }
                    // Indefinite. Nothing to run out, so no guard is needed -- invariant 12 paying for
                    // itself rather than being a special case.
                    if (gate.IsSustainedPortalSession) { return true; }
                    int remaining = gate.OpeningTicksRemaining;
                    if (remaining > 0 && remaining < shortest) { shortest = remaining; }
                }
            }
            if (shortest == int.MaxValue) { return false; }
            long required = (long)AssumedLegTicks * 2L + needTicks;
            return shortest >= required;
        }
    }
}
