using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A hauler crossing a gate to work the *containers* on the other side.
    ///
    /// ## What this family is for, and what it deliberately is not
    ///
    /// `Hauling` is the largest work type in the game — thirty giver defs across Core and
    /// four expansions — and most of it was already handled. The carry families move material
    /// **through** a gate; what had no coverage at all was the set of givers that need a
    /// worker **standing on the far map**, operating a building that is not a bill bench.
    ///
    /// The thirty were enumerated and classified rather than skimmed:
    ///
    /// | Giver | Why it is not here |
    /// |---|---|
    /// | `HaulGeneral`, `HaulMerge` | the storage carry family's route |
    /// | `HaulCorpses` | the casualty carry family's route |
    /// | `DeliverResourcesToFrames`, `DeliverResourcesToBlueprints` | the construction supply family |
    /// | `Refuel`, `RearmTurrets` | the fuel carry family, which is one family for both |
    /// | `DoBillsCremate`, `DoBillsHaulCampfire` | bills; the bill families own them |
    /// | `HelpGatheringItemsForCaravan`, `LoadTransporters` | **semantically map-bound.** A caravan forms on, and a transport pod launches from, one specific map. Crossing a gate to load either would be loading the wrong departure |
    /// | `HaulToPortal` | Core's **own** map-portal system, which `CONNECTED_WORK_CORE_API.md` already established cannot serve this design. It is not our gate |
    /// | `Strip` | stripping a corpse or prisoner is custody-adjacent and needs its own review |
    /// | the Biotech, Ideology and Anomaly container givers | named below, not swept in |
    ///
    /// What is left, and what this provider answers, is three concrete Core routes where the
    /// state is an exact fact about a building on that map:
    ///
    /// 1. a **fermenting barrel** that wants wort, or that has beer ready;
    /// 2. an **egg box** holding eggs that can be taken out;
    /// 3. a **carrier** whose inventory the player marked to be unloaded.
    ///
    /// ## The DLC container givers are named, not silently omitted
    ///
    /// `HaulToGeneBank`, `HaulToGrowthVat`, `CarryToGrowthVat`, `CarryToGeneExtractor`,
    /// `CarryToSubcoreScanner`, `HaulMechsToCharger` and `EmptyWasteContainer` (Biotech),
    /// `HaulToBiosculpterPod` (Ideology), and `TakeBioferriteOutOfHarvester`,
    /// `TakeEntityToHoldingPlatform` and `TransferEntity` (Anomaly) are all real container
    /// work and all genuinely uncovered. Each carries a pawn or a live subject into a
    /// machine, or moves an entity between platforms, and each needs its own source review of
    /// what that does to custody before a worker is sent across a gate to do it. They are
    /// recorded as open rather than guessed at.
    ///
    /// ## Profile rows read before writing this
    ///
    /// The register flags eleven *Storage and recovered-material logistics* rows whose planned
    /// use implies Rimrooms builds something, and they were read first:
    ///
    /// * **157 OgreStack** changes stack sizes globally. Nothing here reads a stack size or a
    ///   count — the questions are "is this barrel fermented" and "does this box hold eggs" —
    ///   so a changed stack limit cannot change any answer. The one place a count appears is
    ///   Core's own `CompEggContainer.CanEmpty`, which compares against the comp's own
    ///   `minCountToEmpty` rather than anything of ours.
    /// * **122 LWM's Adaptive Deep Storage**, **259 Warehouse Storage**, **26 Adaptive Simple
    ///   Storage**, **195 RimFridge** add storage buildings. They are storage, not containers
    ///   this family operates, and the *destination* for emptied eggs is chosen by Core's own
    ///   `TryFindBestBetterStorageFor` on arrival — so a modded store is used automatically
    ///   and nothing here needs to know it exists.
    /// * **164 Pick Up And Haul** and **107 Haul to Stack** were closed as register rows in a
    ///   previous checkpoint: the connected families run their own driver rather than
    ///   `WorkGiver_HaulGeneral`, so there is no seam, and this provider hands out no hauling
    ///   job of its own either — it justifies a crossing and Core does the work.
    /// * **245 Vanilla Fix: Haul After Slaughter** and **93 Food Poisoning Stack Fix** are
    ///   corrections to vanilla hauling behaviour that this family never reimplements.
    /// * **87 Egg Incubator** adds egg-related content; because the egg route matches by
    ///   `CompEggContainer` rather than by a named building, a modded egg container with that
    ///   comp is covered with nothing naming it.
    ///
    /// None of those is a dependency, none is patched, and every one may be absent.
    /// </summary>
    public sealed class HaulingUpkeepProvider : ConnectedDeploymentProvider
    {
        private const int MaximumBarrelsPerMap = 12;
        private const int MaximumEggBoxesPerMap = 12;
        private const int MaximumCarriersPerMap = 8;

        /// <summary>
        /// How close the ambient temperature may come to ruining wort before this stops being
        /// worth a crossing. Core's own margin, taken from `WorkGiver_FillFermentingBarrel`.
        /// </summary>
        private const float TemperatureMargin = 2f;

        public override string ProviderId
        { get { return ConnectedDeploymentProviders.HaulingUpkeep; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_HaulingUpkeepLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Hauling"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            return AnyBarrel(map, pawn, work) || AnyEggBox(map, pawn, work) || AnyCarrier(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            // Not windowed, deliberately: a window that missed the one full egg box would
            // release the deployment while there was still work to do and plan the worker
            // straight back across the gate.
            return AnyBarrel(pawn.Map, pawn, null) || AnyEggBox(pawn.Map, pawn, null) ||
                AnyCarrier(pawn.Map, pawn, null);
        }

        // ------------------------------------------------------------------ barrels -- //

        /// <summary>
        /// A fermenting barrel that either has beer ready to take out, or has room for wort
        /// and wort on the map to put in.
        ///
        /// Both halves are facts about the barrel and its own map:
        /// `Building_FermentingBarrel.Fermented` and `SpaceLeftForWort` are public state, and
        /// the temperature test reads the barrel's `AmbientTemperature` against its own def's
        /// `CompProperties_TemperatureRuinable` — Core's own check, with Core's own margin,
        /// because carrying wort to a barrel that is about to ruin it is a wasted crossing.
        ///
        /// The deconstruct designation is read from **the barrel's** designation manager.
        /// Core reads `pawn.Map.designationManager` because in Core the barrel is on the
        /// pawn's map; here those are different maps and the barrel's is the right one.
        ///
        /// What is left to arrival: `pawn.CanReserve`, and `FindWort`, which is a
        /// `GenClosest.ClosestThingReachable` from the pawn's own position. The candidate half
        /// substitutes a **presence** test for wort on that map — necessary, not sufficient,
        /// exactly as the bill family does, because reachability is not ours to ask remotely.
        /// </summary>
        private static bool AnyBarrel(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            ThingDef barrelDef = ThingDefOf.FermentingBarrel;
            if (barrelDef == null || map.listerThings == null) { return false; }
            List<Thing> barrels = map.listerThings.ThingsOfDef(barrelDef);
            if (barrels.Count == 0) { return false; }
            bool wortPresent = WortPresent(map);

            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(barrels.Count, MaximumBarrelsPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < barrels.Count; position++)
            {
                if (work != null && examined >= MaximumBarrelsPerMap) { break; }
                examined++;
                var barrel = barrels[position] as Building_FermentingBarrel;
                if (barrel == null || barrel.Destroyed || !barrel.Spawned || barrel.Map != map)
                { continue; }
                if (barrel.IsBurning()) { continue; }
                if (barrel.IsForbidden(Faction.OfPlayer)) { continue; }
                if (barrel.Position.Fogged(map)) { continue; }
                if (map.designationManager != null &&
                    map.designationManager.DesignationOn(barrel, DesignationDefOf.Deconstruct) != null)
                { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, barrel.Position)) { continue; }

                if (barrel.Fermented)
                {
                    if (work == null && !pawn.CanReserve(barrel)) { continue; }
                    return true;
                }
                if (!wortPresent || barrel.SpaceLeftForWort <= 0) { continue; }
                if (!TemperatureSafe(barrel)) { continue; }
                if (work == null && !pawn.CanReserve(barrel)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>Core's own margin against a barrel whose contents would be ruined.</summary>
        private static bool TemperatureSafe(Building_FermentingBarrel barrel)
        {
            CompProperties_TemperatureRuinable properties =
                barrel.def.GetCompProperties<CompProperties_TemperatureRuinable>();
            if (properties == null) { return true; }
            float ambient = barrel.AmbientTemperature;
            return ambient >= properties.minSafeTemperature + TemperatureMargin &&
                ambient <= properties.maxSafeTemperature - TemperatureMargin;
        }

        private static bool WortPresent(Map map)
        {
            ThingDef wort = ThingDefOf.Wort;
            if (wort == null || map.listerThings == null) { return false; }
            List<Thing> stacks = map.listerThings.ThingsOfDef(wort);
            for (int index = 0; index < stacks.Count; index++)
            {
                Thing stack = stacks[index];
                if (stack == null || stack.Destroyed || !stack.Spawned || stack.Map != map)
                { continue; }
                if (stack.IsForbidden(Faction.OfPlayer) || stack.Position.Fogged(map)) { continue; }
                return true;
            }
            return false;
        }

        // ----------------------------------------------------------------- egg boxes -- //

        /// <summary>
        /// A container holding eggs that Core considers ready to empty.
        ///
        /// Matched by **`CompEggContainer`**, never by a named building, so a modded egg
        /// container carrying that comp is covered with nothing here naming it — the standing
        /// match-by-capability rule.
        ///
        /// `ContainedThing` and `CanEmpty` are facts about the comp; `CanEmpty` compares the
        /// stack against the comp's own `minCountToEmpty`, so a mod that changes stack sizes
        /// changes Core's number rather than one of ours.
        ///
        /// Left to arrival: `pawn.CanReserve`, and `TryFindBestBetterStorageFor`, which takes
        /// the pawn and the pawn's map and chooses where the eggs go. That is also why a
        /// modded storage building is used automatically without this family knowing it exists.
        /// </summary>
        private static bool AnyEggBox(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map.listerThings == null) { return false; }
            List<Thing> buildings = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            if (buildings.Count == 0) { return false; }
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(buildings.Count, MaximumEggBoxesPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < buildings.Count; position++)
            {
                if (work != null && examined >= MaximumEggBoxesPerMap) { break; }
                Thing building = buildings[position];
                if (building == null || building.Destroyed || !building.Spawned ||
                    building.Map != map)
                { continue; }
                CompEggContainer container = building.TryGetComp<CompEggContainer>();
                if (container == null) { continue; }
                // Only count a real candidate against the window, so a map full of ordinary
                // buildings does not exhaust the budget before reaching an egg box.
                examined++;
                if (container.ContainedThing == null || !container.CanEmpty) { continue; }
                if (building.IsForbidden(Faction.OfPlayer)) { continue; }
                if (building.Position.Fogged(map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, building.Position))
                { continue; }
                if (work == null && !pawn.CanReserve(building)) { continue; }
                return true;
            }
            return false;
        }

        // ------------------------------------------------------------------ carriers -- //

        /// <summary>
        /// A pack animal or other carrier the player marked to be unloaded.
        ///
        /// Core exposes this as a **map-parameterised list**,
        /// `map.mapPawns.SpawnedPawnsWhoShouldHaveInventoryUnloaded`, which is the same shape
        /// as the study manager's per-map cache: asking it about another map is exactly what
        /// it is for, and it reads no worker.
        ///
        /// This is the one route here that is genuinely player-driven — `UnloadEverything` is
        /// set by the player or by a caravan arriving — which puts it with the fieldwork
        /// families where nothing is inferred.
        /// </summary>
        private static bool AnyCarrier(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map.mapPawns == null) { return false; }
            List<Pawn> carriers = map.mapPawns.SpawnedPawnsWhoShouldHaveInventoryUnloaded;
            if (carriers == null || carriers.Count == 0) { return false; }
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(carriers.Count, MaximumCarriersPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < carriers.Count; position++)
            {
                if (work != null && examined >= MaximumCarriersPerMap) { break; }
                examined++;
                Pawn carrier = carriers[position];
                if (carrier == null || carrier.Destroyed || carrier.Dead || !carrier.Spawned ||
                    carrier.Map != map || carrier == pawn)
                { continue; }
                if (carrier.PositionHeld.Fogged(map)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, carrier.PositionHeld))
                { continue; }
                if (work == null && !pawn.CanReserve(carrier)) { continue; }
                return true;
            }
            return false;
        }
    }
}
