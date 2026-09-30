using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A builder crossing a gate to put a roof up, or take one down, on the other side.
    ///
    /// ## Why this is live now when it correctly was not before
    ///
    /// `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` audited every zone and area type and recorded
    /// `Area_BuildRoof` and `Area_NoRoof` as **not covered, and correctly so** — with the reason
    /// written down and a condition attached:
    ///
    /// * inside a Backrooms coordinate **every cell already carries thick rock roof**, so a
    ///   build-roof area there has nothing to do;
    /// * **roof removal inside the Backrooms is forbidden outright** by the world rule, and
    ///   `BackroomsContainment` keeps `Area_NoRoof` deliberately emptied there — covering it would
    ///   have been building the thing the world rule exists to prevent.
    ///
    /// The condition was *"revisit when the ordinary-map endpoint lands"*, and it landed at
    /// 0.6.9-dev: **a registered remote site is an ordinary world map reachable through a gate.**
    /// A colony map genuinely wants roofs built and genuinely has roofs worth removing, so the
    /// reason the row was closed has expired and the row is now real work.
    ///
    /// **Nothing here changes the Backrooms rule.** `BackroomsContainment` still empties
    /// `Area_NoRoof` on a coordinate every interval, so on a coordinate this provider finds an
    /// empty area and offers nobody a crossing. The rule keeps itself; this family simply has
    /// nothing to do where the rule applies.
    ///
    /// ## Its own family rather than a route on the finishing family, and the reason is a number
    ///
    /// The tidy answer was to add two routes to `ConstructionFinishingProvider`, which already
    /// crosses for `Construction`. That would have been **broken**, and the priority ladder is why:
    ///
    /// <code>
    /// BuildRoofs                                  100   (Core)
    /// RemoveRoofs                                  90   (Core)
    /// RR_ConnectedConstructionFinishingContinue     82   (ours)
    /// </code>
    ///
    /// The rule every family follows is that the **continuation** giver must outrank every local
    /// giver it travels for, or a worker part way to a gate is turned around by work that appeared
    /// at home while it walked. At 82 the finishing family is below both roof givers, so roof
    /// routes hung on it would have produced exactly that thrash. Raising 82 to beat them would
    /// have lifted *frame finishing* over roof work too — a behaviour change to a family that was
    /// tuned deliberately.
    ///
    /// So this is a third `Construction` family, continuation at **101** and planning at **1**,
    /// and the finishing and repair families keep their numbers.
    ///
    /// ## Both halves are facts about the map asked about
    ///
    /// Core's own givers read nothing else:
    ///
    /// <code>
    /// WorkGiver_BuildRoof.ShouldSkip   -> map.areaManager.BuildRoof.TrueCount == 0
    /// WorkGiver_RemoveRoof.ShouldSkip  -> map.areaManager.NoRoof.TrueCount == 0
    /// </code>
    ///
    /// and `Area.TrueCount`, `Area.ActiveCells`, `IntVec3.Roofed(map)` and
    /// `RoofCollapseUtility.WithinRangeOfRoofHolder(cell, map)` all take the map explicitly and
    /// take no pawn. So the candidate half asks Core's real questions rather than substituting for
    /// them, which is unusual in this layer and worth saying: the only thing left to arrival is
    /// the reservation against `ReservationLayerDefOf.Ceiling` and the reach.
    ///
    /// **`ConnectedToRoofHolder` is deliberately not asked from here.** It walks the roof grid
    /// from the cell and is the expensive half of Core's test; `WithinRangeOfRoofHolder` is a
    /// cheap radius check that always agrees when it refuses. Asking the cheap one remotely and
    /// leaving the thorough one to arrival is the same necessary-not-sufficient split every
    /// family uses.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py family "spatial construction"` — swept, and its standing position is
    /// that this mod adds no construction mechanic of its own and leaves native building alone.
    /// Nothing here builds, removes or reads a roof: it reads two areas and hands out no job, so a
    /// mod that changes roofing costs, roof types or collapse rules changes Core's answers on
    /// arrival and none of ours. There is no roof material named anywhere in this file.
    /// </summary>
    public sealed class RoofWorkProvider : ConnectedDeploymentProvider
    {
        /// <summary>
        /// How many marked cells one remote candidate pass may look at. Areas are cell sets and
        /// a player can paint a large one, so this is a window like every other route's.
        /// </summary>
        private const int MaximumCellsPerMap = 24;

        public override string ProviderId
        { get { return ConnectedDeploymentProviders.RoofWork; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_RoofWorkLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Construction"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn))
            { return false; }
            return AnyRoofToBuild(map, pawn, work) || AnyRoofToRemove(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            // Unwindowed, like every definitive half: releasing a deployment with a marked cell
            // left would plan the worker straight back across the gate.
            return AnyRoofToBuild(pawn.Map, pawn, null) || AnyRoofToRemove(pawn.Map, pawn, null);
        }

        /// <summary>
        /// A cell the player marked for a roof that has none, and that could hold one.
        ///
        /// `WithinRangeOfRoofHolder` is Core's own cheap refusal — a cell too far from anything
        /// that could support a roof can never be roofed — and it takes the map explicitly.
        /// </summary>
        private static bool AnyRoofToBuild(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            Area area = map.areaManager == null ? null : map.areaManager.BuildRoof;
            if (area == null || area.TrueCount == 0) { return false; }
            int examined = 0;
            foreach (IntVec3 cell in area.ActiveCells)
            {
                if (work != null && examined >= MaximumCellsPerMap) { break; }
                examined++;
                if (!cell.IsValid || !cell.InBounds(map) || cell.Fogged(map)) { continue; }
                if (cell.Roofed(map)) { continue; }
                if (!RoofCollapseUtility.WithinRangeOfRoofHolder(cell, map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                if (work == null &&
                    !pawn.CanReserve(cell, 1, -1, ReservationLayerDefOf.Ceiling))
                { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// A cell the player marked for no roof that has one.
        ///
        /// On a Backrooms coordinate this is always empty, because `BackroomsContainment` clears
        /// that area there every interval. The world rule keeps itself and this route simply
        /// finds nothing.
        /// </summary>
        private static bool AnyRoofToRemove(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            Area area = map.areaManager == null ? null : map.areaManager.NoRoof;
            if (area == null || area.TrueCount == 0) { return false; }
            int examined = 0;
            foreach (IntVec3 cell in area.ActiveCells)
            {
                if (work != null && examined >= MaximumCellsPerMap) { break; }
                examined++;
                if (!cell.IsValid || !cell.InBounds(map) || cell.Fogged(map)) { continue; }
                if (!cell.Roofed(map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                if (work == null &&
                    !pawn.CanReserve(cell, 1, -1, ReservationLayerDefOf.Ceiling))
                { continue; }
                return true;
            }
            return false;
        }
    }
}
