using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A hauler crossing a gate to load or empty a machine on the other side.
    ///
    /// ## The eleven givers this closes, and the one thing they all turned out to share
    ///
    /// `HaulingUpkeepProvider` enumerated thirty `Hauling` givers, covered the three Core
    /// container routes, and left eleven named rather than guessed at, with its reason
    /// written down: *"Each carries a pawn or a live subject into a machine, or moves an
    /// entity between platforms, and each needs its own source review of what that does to
    /// custody before a worker is sent across a gate to do it."*
    ///
    /// The source review was done, all eleven, and it produced a single finding that
    /// settles the custody question for every one of them:
    ///
    /// **NOT ONE OF THE ELEVEN CAN MOVE ANYTHING BETWEEN MAPS. Core forbids it itself.**
    ///
    /// | Giver | Core's own same-map constraint |
    /// |---|---|
    /// | `CarryToGrowthVat`, `CarryToGeneExtractor`, `CarryToSubcoreScanner` | `WorkGiver_CarryToBuilding.HasJobOnThing` returns false unless `selectedPawn.Map == pawn.Map` |
    /// | `HaulToGeneBank` | `FindGeneBank` requires `genepack.targetContainer.Map == genepack.Map`, and searches from `genepack.Position, genepack.Map` |
    /// | `HaulToGrowthVat` | `CanHaulSelectedThing` returns false unless `selectedThing.Map == pawn.Map`; `FindNutrition` searches `pawn.Position, pawn.Map` |
    /// | `HaulMechsToCharger` | candidates are `pawn.Map.mapPawns.SpawnedPawnsInFaction(pawn.Faction)` |
    /// | `EmptyWasteContainer` | the destination comes from `TryFindBestBetterStorageFor(..., pawn.Map, ...)` |
    /// | `HaulToBiosculpterPod` | `FindNutrition` searches `pawn.Position, pawn.Map` |
    /// | `TakeBioferriteOutOfHarvester` | the job is the building alone; nothing travels |
    /// | `TakeEntityToHoldingPlatform` | returns false unless `targetHolder.MapHeld == t.MapHeld` |
    /// | `TransferEntity` | both platforms are reserved by the same worker, and it refuses when `HeldPlatform == targetHolder` |
    ///
    /// So the shape is the ordinary deployment shape after all, and it is the *safest* of
    /// the families rather than the riskiest: **the worker crosses, and everything it
    /// touches is already on the far side.** A pawn carried into a growth vat was standing
    /// beside it before the hauler arrived and is standing beside it after. An entity moved
    /// between platforms moves between two platforms in one room.
    ///
    /// **Invariant 55 is therefore never engaged.** It rules that a transfer which can lose
    /// a pawn is a corruption rather than a threat, and it governs pawn transfers; there is
    /// no pawn transfer here to govern. That was the open question at the top of the queue
    /// and the answer is that Core had already closed it. It was read out of Core rather
    /// than assumed, because assuming it the other way is what left the row open.
    ///
    /// ## No expansion branch anywhere, and that is deliberate
    ///
    /// Seven of the eleven are Biotech, one is Ideology and three are Anomaly, and the
    /// obvious shape — three providers behind three `ModsConfig.XActive` gates — turned out
    /// to be the wrong one. Every route here degrades to *finds nothing* on its own:
    ///
    /// * the `ThingDefOf` fields it needs (`Genepack`, `GrowthVat`, `BiosculpterPod`,
    ///   `BioferriteHarvester`) are `MayRequire` fields, so they are **null** without their
    ///   expansion, and each is null-checked exactly as `HaulingUpkeepProvider` null-checks
    ///   `ThingDefOf.FermentingBarrel`;
    /// * every other route matches a `ThingRequestGroup` or a comp, and `ThingsInGroup`
    ///   returns an **empty list** for content that is not installed;
    /// * the classes and comps named here (`Building_Enterable`, `CompWasteProducer`,
    ///   `CompBiosculpterPod`, `Building_HoldingPlatform`, `CompHoldingPlatformTarget`)
    ///   all live in the always-present base assembly, so a type reference cannot fail to
    ///   resolve on a Core-only install.
    ///
    /// An expansion's absence is expressed as an empty world rather than a branch, which is
    /// both fewer moving parts and strictly more capable: the enterable route matches
    /// **`Building_Enterable`** and not the three shipped buildings, so a modded enterable
    /// is covered with nothing here naming it — the standing match-by-capability rule.
    /// `WorkGiver_CarryToBuilding` is itself an ungated abstract class in the base assembly;
    /// only its three subclasses carry `ShouldSkip => !ModsConfig.BiotechActive`, and they
    /// carry it because the three *buildings* are Biotech, not because the shape is.
    ///
    /// ## Where Core's answer could not be borrowed
    ///
    /// One check in the eleven is genuinely unusable from here.
    /// `JobGiver_GetEnergy_Charger.GetClosestCharger(mech, carrier, forced)` builds
    /// `TraverseParms.For(carrier)` and calls `carrier.CanReach`, so asking it about a map
    /// the carrier is not standing on is exactly the remote-reachability mistake this layer
    /// exists to avoid. The candidate half substitutes the **presence** of a charger on that
    /// map that `CanPawnChargeCurrently` accepts for that mech — necessary, not sufficient,
    /// and the real call is made on arrival by Core's own giver. The same substitution is
    /// used for a gene bank and for nutrition, for the same reason and with the same cost:
    /// an optimistic miss delays one pass, a false positive wastes one walk.
    ///
    /// By contrast `Pawn.ThreatDisabled(IAttackTargetSearcher)` **is** safe to call from
    /// here, which was checked rather than assumed: it reads the entity's own spawn state,
    /// duty, mind state, downed state and comps, and uses the passed searcher only for
    /// `mindState.duty.attackDownedIfStarving` and a roamer comparison. It reads no map and
    /// takes no reservation, so the capture route asks Core's own question outright.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py use RR-DLC` returns forty rows, and the instruction on all six
    /// expansion rows is one sentence repeated: *"Add conditional definitions and code only
    /// for DLC-specific extensions; do not make a DLC feature the sole route through the
    /// campaign."* This family is additive by construction — it is one more reason a hauler
    /// may cross, and the campaign never asks for it — so the base loop is untouched when
    /// every expansion is absent, which is the condition the row actually cares about.
    ///
    /// The rows that turn up under the machines themselves were read too. **51 Better Gene
    /// Inheritance**, **94 Force Xenogerm Implantation**, **112 Inject Genes** and **114
    /// Integrated Genes** all change what genes *do*; nothing here reads a gene, a xenotype
    /// or a genepack's contents — the questions are *"is this pack marked to auto-load"* and
    /// *"is there a bank with room"* — and `Building_GeneExtractor.CanAcceptPawn` is Core's
    /// own, so a mod that changes which pawns have extractable genes changes Core's answer
    /// rather than one of ours. Their shared watch is *"check pawn health/custody state,
    /// treatment choice, and transfer; preserve a vanilla fallback"*, and the custody
    /// finding above is that answer: no transfer occurs, and the fallback is Core doing all
    /// of the work on arrival.
    ///
    /// **39 Anomaly Research Asteroid** is optional off-site content whose watch asks that
    /// the no-DLC campaign path keep working; it adds no holding platform behaviour, and the
    /// containment routes here match `HoldingPlatformTarget` and `EntityHolder` by group, so
    /// a platform from any source is covered and none is required. **140 Name Your Entities**
    /// is display naming only and reads nothing this provider writes.
    ///
    /// None of those is a dependency, none is patched, and every one may be absent.
    /// </summary>
    public sealed class MachineLoadingProvider : ConnectedDeploymentProvider
    {
        /// <summary>
        /// Core's own margin before a growth vat is worth carrying food to, taken from
        /// `WorkGiver_HaulToGrowthVat.NutritionBuffer`. Below it the vat has enough.
        /// </summary>
        private const float VatNutritionBuffer = 2.5f;

        private const int MaximumPerRoute = 12;

        /// <summary>
        /// Enterables are matched out of the whole artificial-building lister, so the
        /// budget counts only the buildings that turn out to be enterable. A room full of
        /// ordinary walls must not exhaust the window before reaching a vat.
        /// </summary>
        private const int MaximumEnterablesPerMap = 8;

        public override string ProviderId
        { get { return ConnectedDeploymentProviders.MachineLoading; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_MachineLoadingLabel"; } }

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
            return map != null && pawn != null && work != null && WorkerEligible(pawn) &&
                AnyRoute(map, pawn, work);
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            // Not windowed, deliberately, exactly as every other provider's definitive half:
            // a bounded pass that missed the one loose entity would release the deployment
            // with work still standing and plan the worker straight back across the gate.
            return AnyRoute(pawn.Map, pawn, null);
        }

        /// <summary>
        /// The nine routes, cheapest and most often empty first so a Core-only install
        /// leaves almost immediately. `work == null` means the worker is standing on this
        /// map and the native pawn-specific answers mean what they say.
        /// </summary>
        private static bool AnyRoute(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map.listerThings == null) { return false; }
            return AnyWasteContainer(map, pawn, work) ||
                AnyHarvester(map, pawn, work) ||
                AnyCapturableEntity(map, pawn, work) ||
                AnyMisplacedEntity(map, pawn, work) ||
                AnyGenepack(map, pawn, work) ||
                AnyGrowthVatSupply(map, pawn, work) ||
                AnyBiosculpterPod(map, pawn, work) ||
                AnyUnchargedMech(map, pawn, work) ||
                AnyEnterable(map, pawn, work);
        }

        // ------------------------------------------------------------------ shared -- //

        /// <summary>
        /// The rotating-window walk every route here shares. A window and never a prefix,
        /// per <see cref="ConnectedWorkScan"/>: a prefix starves anything past the cap
        /// forever, and one branch can hold several maps at once.
        /// </summary>
        private static bool AnyInWindow(List<Thing> things, Pawn pawn,
            RimroomsConnectedWorkComponent work, int budget, Func<Thing, bool> candidate)
        {
            if (things == null || things.Count == 0) { return false; }
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(things.Count, budget, pawn);
            int examined = 0;
            for (int position = windowStart; position < things.Count; position++)
            {
                if (work != null && examined >= budget) { break; }
                examined++;
                if (candidate(things[position])) { return true; }
            }
            return false;
        }

        /// <summary>
        /// The tests every route repeats: the thing is really there, on the map asked
        /// about, not forbidden to the company, not hidden, and inside whatever allowed
        /// area this worker was last seen to have on that map.
        /// </summary>
        private static bool Present(Thing thing, Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (thing == null || thing.Destroyed || !thing.Spawned || thing.Map != map)
            { return false; }
            if (thing.IsForbidden(Faction.OfPlayer)) { return false; }
            if (thing.Position.Fogged(map)) { return false; }
            return work == null || work.ObservedAreaAllows(pawn, map, thing.Position);
        }

        /// <summary>
        /// Core refuses container work on a building marked for deconstruction or on fire.
        /// The designation is read from **the building's** own manager: Core reads
        /// `pawn.Map.designationManager` because in Core they are the same map, and here
        /// they are not.
        /// </summary>
        private static bool Operable(Thing building, Map map)
        {
            if (building.IsBurning()) { return false; }
            return map.designationManager == null ||
                map.designationManager.DesignationOn(building, DesignationDefOf.Deconstruct) == null;
        }

        // ----------------------------------------------------------- waste container -- //

        /// <summary>
        /// `EmptyWasteContainer`. A waste producer holding wastepacks Core considers
        /// extractable now.
        ///
        /// `CompWasteProducer.CanEmptyNow` is a fact about the comp and its parent — it
        /// refuses a gestator with a mech still in it and otherwise asks whether any
        /// wastepack is held — so it reads cleanly from here.
        ///
        /// Left to arrival: `pawn.CanReserve` against `ReservationLayerDefOf.Empty`, and
        /// `TryFindBestBetterStorageFor`, which takes the pawn and the pawn's map and picks
        /// where the waste goes. That is also why a modded store is used automatically
        /// without this family knowing it exists.
        /// </summary>
        private static bool AnyWasteContainer(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            return AnyInWindow(map.listerThings.ThingsInGroup(ThingRequestGroup.WasteProducer),
                pawn, work, MaximumPerRoute, delegate(Thing building)
            {
                if (!Present(building, map, pawn, work)) { return false; }
                CompWasteProducer producer = building.TryGetComp<CompWasteProducer>();
                if (producer == null || !producer.CanEmptyNow) { return false; }
                Thing waste = producer.Waste;
                if (waste == null || waste.stackCount <= 0) { return false; }
                return work != null || pawn.CanReserve(building, 1, -1,
                    ReservationLayerDefOf.Empty);
            });
        }

        // --------------------------------------------------------------- bioferrite -- //

        /// <summary>
        /// `TakeBioferriteOutOfHarvester`. The simplest of the eleven: Core's whole
        /// question is `unloadingEnabled`, `ReadyForHauling` and not burning, all of them
        /// facts about the building. `ReadyForHauling` is a floor of the harvester's own
        /// stored amount, so nothing here holds a number of its own.
        /// </summary>
        private static bool AnyHarvester(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            ThingDef harvesterDef = ThingDefOf.BioferriteHarvester;
            if (harvesterDef == null) { return false; }
            return AnyInWindow(map.listerThings.ThingsOfDef(harvesterDef), pawn, work,
                MaximumPerRoute, delegate(Thing thing)
            {
                var harvester = thing as Building_BioferriteHarvester;
                if (harvester == null || !harvester.unloadingEnabled ||
                    !harvester.ReadyForHauling)
                { return false; }
                if (!Present(harvester, map, pawn, work) || harvester.IsBurning())
                { return false; }
                return work != null || pawn.CanReserve(harvester);
            });
        }

        // ------------------------------------------------------- entity containment -- //

        /// <summary>
        /// `TakeEntityToHoldingPlatform`. Something the player has ordered onto a platform,
        /// lying there sedated or downed, with the platform empty and on the same map.
        ///
        /// Core's own same-map guard is the interesting line —
        /// `targetHolder.MapHeld != t.MapHeld` refuses outright — so the entity and its
        /// platform are always one room apart and the hauler is the only thing that travels.
        ///
        /// `ThreatDisabled` is asked here rather than left to arrival because it reads no
        /// map and takes no reservation, so the remote answer is the real answer. The order
        /// of the null tests matters: `CompHoldingPlatformTarget.EntityHolder` dereferences
        /// `targetHolder`, so it may only be read after `targetHolder` is known non-null,
        /// which is why Core's own giver tests them in exactly this sequence.
        /// </summary>
        private static bool AnyCapturableEntity(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (!pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
            { return false; }
            return AnyInWindow(
                map.listerThings.ThingsInGroup(ThingRequestGroup.HoldingPlatformTarget),
                pawn, work, MaximumPerRoute, delegate(Thing target)
            {
                if (!Present(target, map, pawn, work)) { return false; }
                CompHoldingPlatformTarget holding = target.TryGetComp<CompHoldingPlatformTarget>();
                if (holding == null || holding.targetHolder == null ||
                    holding.targetHolder.Destroyed ||
                    holding.targetHolder.MapHeld != target.MapHeld)
                { return false; }
                CompEntityHolder holder = holding.EntityHolder;
                if (holder == null || holder.HeldPawn != null) { return false; }
                var entity = target as Pawn;
                if (entity != null && !entity.ThreatDisabled(pawn)) { return false; }
                if (work != null) { return true; }
                return pawn.CanReserve(target) && pawn.CanReserve(holding.targetHolder);
            });
        }

        /// <summary>
        /// `TransferEntity`. An entity held on one platform while the player has pointed it
        /// at another. Core reaches it from the holder rather than the entity —
        /// `Building_HoldingPlatform.HeldPawn`, then that pawn's own target — and refuses
        /// when the platform it is on is already the one it is aimed at.
        /// </summary>
        private static bool AnyMisplacedEntity(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            return AnyInWindow(map.listerThings.ThingsInGroup(ThingRequestGroup.EntityHolder),
                pawn, work, MaximumPerRoute, delegate(Thing thing)
            {
                var platform = thing as Building_HoldingPlatform;
                if (platform == null || !Present(platform, map, pawn, work)) { return false; }
                Pawn held = platform.HeldPawn;
                if (held == null) { return false; }
                CompHoldingPlatformTarget holding = held.TryGetComp<CompHoldingPlatformTarget>();
                if (holding == null || holding.targetHolder == null ||
                    holding.targetHolder.Destroyed) { return false; }
                if (holding.HeldPlatform == holding.targetHolder) { return false; }
                if (holding.targetHolder.IsForbidden(Faction.OfPlayer)) { return false; }
                if (work != null) { return true; }
                return pawn.CanReserve(platform) && pawn.CanReserve(held) &&
                    pawn.CanReserve(holding.targetHolder);
            });
        }

        // ------------------------------------------------------------------ genepack -- //

        /// <summary>
        /// `HaulToGeneBank`. A genepack the player marked to auto-load, and a bank with
        /// room for it.
        ///
        /// Core resolves the bank two ways and both are readable from here: a pack with a
        /// `targetContainer` must find that container on its own map and not full, and a
        /// pack without one searches for any gene bank whose comp auto-loads and is not
        /// full. Only the second needs a substitute — `GenClosest.ClosestThingReachable`
        /// becomes the **presence** of such a bank on that map, because reachability is not
        /// ours to ask remotely.
        /// </summary>
        private static bool AnyGenepack(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            ThingDef genepackDef = ThingDefOf.Genepack;
            if (genepackDef == null) { return false; }
            List<Thing> packs = map.listerThings.ThingsOfDef(genepackDef);
            if (packs.Count == 0) { return false; }
            bool openBank = false;
            bool openBankKnown = false;
            return AnyInWindow(packs, pawn, work, MaximumPerRoute, delegate(Thing thing)
            {
                var pack = thing as Genepack;
                if (pack == null || !pack.AutoLoad) { return false; }
                if (!Present(pack, map, pawn, work)) { return false; }
                if (work == null && !pawn.CanReserve(pack)) { return false; }
                if (pack.targetContainer != null)
                {
                    if (pack.targetContainer.Destroyed ||
                        pack.targetContainer.Map != pack.Map) { return false; }
                    CompGenepackContainer named =
                        pack.targetContainer.TryGetComp<CompGenepackContainer>();
                    return named != null && !named.Full;
                }
                // Resolved once per pass, not once per pack: every untargeted pack asks the
                // same question of the same map.
                if (!openBankKnown)
                {
                    openBank = AnyOpenGeneBank(map, pawn, work);
                    openBankKnown = true;
                }
                return openBank;
            });
        }

        private static bool AnyOpenGeneBank(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            return AnyInWindow(map.listerThings.ThingsInGroup(ThingRequestGroup.GenepackHolder),
                pawn, work, MaximumPerRoute, delegate(Thing bank)
            {
                if (!Present(bank, map, pawn, work)) { return false; }
                CompGenepackContainer container = bank.TryGetComp<CompGenepackContainer>();
                if (container == null || container.Full || !container.autoLoad)
                { return false; }
                return work != null || pawn.CanReserve(bank);
            });
        }

        // ---------------------------------------------------------------- growth vat -- //

        /// <summary>
        /// `HaulToGrowthVat`. A vat short of food with food on the map, or a vat whose
        /// selected embryo is still lying on the floor.
        ///
        /// `NutritionNeeded`, `selectedEmbryo` and `innerContainer` are public state, and
        /// `CanAcceptNutrition` takes a thing rather than a pawn, so Core's own acceptance
        /// test is used verbatim instead of a guess about what a vat eats. The nutrition
        /// half substitutes presence for `GenClosest`; the embryo half needs no substitute
        /// at all, because Core's own condition is that the embryo is spawned on that map
        /// and unforbidden.
        /// </summary>
        private static bool AnyGrowthVatSupply(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            ThingDef vatDef = ThingDefOf.GrowthVat;
            if (vatDef == null) { return false; }
            return AnyInWindow(map.listerThings.ThingsOfDef(vatDef), pawn, work,
                MaximumPerRoute, delegate(Thing thing)
            {
                var vat = thing as Building_GrowthVat;
                if (vat == null || !Present(vat, map, pawn, work) || !Operable(vat, map))
                { return false; }
                if (work == null && !pawn.CanReserve(vat)) { return false; }
                if (vat.NutritionNeeded > VatNutritionBuffer && AnyNutritionFor(map, pawn, work,
                    vat.CanAcceptNutrition, vat.NutritionNeeded))
                { return true; }
                HumanEmbryo embryo = vat.selectedEmbryo;
                if (embryo == null || vat.innerContainer == null ||
                    vat.innerContainer.Contains(embryo)) { return false; }
                return Present(embryo, map, pawn, work) &&
                    (work != null || pawn.CanReserve(embryo));
            });
        }

        // --------------------------------------------------------- biosculpter pod -- //

        /// <summary>
        /// `HaulToBiosculpterPod`. A powered pod waiting for nutrition with auto-load on.
        ///
        /// Matched by **`CompBiosculpterPod`** rather than by the shipped building, so a
        /// modded pod carrying that comp is covered with nothing here naming it. Core's own
        /// giver is def-matched; the comp is the capability, and the comp is what every
        /// condition it tests actually lives on.
        ///
        /// `forced` is never true on this route — a deployment is planned, never
        /// player-forced — so Core's `!forced && !autoLoadNutrition` refusal reduces to
        /// requiring `autoLoadNutrition`, which is the honest reading of an unforced pass.
        /// </summary>
        private static bool AnyBiosculpterPod(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            ThingDef podDef = ThingDefOf.BiosculpterPod;
            if (podDef == null) { return false; }
            return AnyInWindow(
                map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial),
                pawn, work, MaximumEnterablesPerMap, delegate(Thing building)
            {
                CompBiosculpterPod pod = building.TryGetComp<CompBiosculpterPod>();
                if (pod == null) { return false; }
                if (!Present(building, map, pawn, work) || !Operable(building, map))
                { return false; }
                if (!pod.PowerOn || !pod.autoLoadNutrition) { return false; }
                if (pod.State != BiosculpterPodState.LoadingNutrition) { return false; }
                if (pod.RequiredNutritionRemaining <= 0f) { return false; }
                if (work == null && !pawn.CanReserve(building)) { return false; }
                return AnyNutritionFor(map, pawn, work, pod.CanAcceptNutrition, -1f);
            });
        }

        /// <summary>
        /// Food on that map the machine would accept. The presence substitute for Core's
        /// `FindNutrition`, which is a `GenClosest` from the worker's own position.
        ///
        /// <paramref name="nutritionCeiling"/> is Core's growth-vat-only rule that a single
        /// item may not carry more nutrition than the vat still needs; a negative value
        /// means the machine has no such rule, which is the biosculpter pod's case.
        /// </summary>
        private static bool AnyNutritionFor(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work, Func<Thing, bool> accepts,
            float nutritionCeiling)
        {
            return AnyInWindow(
                map.listerThings.ThingsInGroup(ThingRequestGroup.FoodSourceNotPlantOrTree),
                pawn, work, MaximumPerRoute, delegate(Thing food)
            {
                if (!Present(food, map, pawn, work)) { return false; }
                if (!accepts(food)) { return false; }
                if (nutritionCeiling >= 0f && food.def != null &&
                    food.def.GetStatValueAbstract(StatDefOf.Nutrition) > nutritionCeiling)
                { return false; }
                return work != null || pawn.CanReserve(food);
            });
        }

        // -------------------------------------------------------------- mech charger -- //

        /// <summary>
        /// `HaulMechsToCharger`. A colony mech that has shut itself down or gone down, with
        /// a charger on that map that would take it.
        ///
        /// The charger lookup is the one place Core's answer could not be borrowed — see
        /// the class note — so this is presence plus `CanPawnChargeCurrently`, which reads
        /// the charger's power, waste and current occupant and the mech's own kind. Every
        /// condition about the mech is Core's, including `GetMaxRechargeLimit`, which
        /// consults the mech's control group rather than a number of ours.
        /// </summary>
        private static bool AnyUnchargedMech(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            if (map.mapPawns == null || pawn.Faction == null) { return false; }
            List<Pawn> owned = map.mapPawns.SpawnedPawnsInFaction(pawn.Faction);
            if (owned == null || owned.Count == 0) { return false; }
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(owned.Count, MaximumPerRoute, pawn);
            int examined = 0;
            for (int position = windowStart; position < owned.Count; position++)
            {
                if (work != null && examined >= MaximumPerRoute) { break; }
                examined++;
                Pawn mech = owned[position];
                if (mech == null || mech == pawn || mech.Destroyed || !mech.Spawned ||
                    mech.Map != map) { continue; }
                if (mech.RaceProps == null || !mech.RaceProps.IsMechanoid ||
                    !mech.IsColonyMech) { continue; }
                if (!Present(mech, map, pawn, work)) { continue; }
                if (mech.needs != null && mech.needs.energy != null)
                {
                    if (!mech.Downed && !mech.needs.energy.IsLowEnergySelfShutdown)
                    { continue; }
                    MechanitorControlGroup group = mech.GetMechControlGroup();
                    if (group != null && MechWorkModeDefOf.SelfShutdown != null &&
                        group.WorkMode == MechWorkModeDefOf.SelfShutdown) { continue; }
                    if (mech.needs.energy.CurLevel >=
                        JobGiver_GetEnergy.GetMaxRechargeLimit(mech)) { continue; }
                }
                if (JobDefOf.MechCharge != null && mech.CurJobDef == JobDefOf.MechCharge)
                { continue; }
                if (work == null && !pawn.CanReserve(mech)) { continue; }
                if (AnyChargerFor(map, pawn, work, mech)) { return true; }
            }
            return false;
        }

        private static bool AnyChargerFor(Map map, Pawn pawn,
            RimroomsConnectedWorkComponent work, Pawn mech)
        {
            return AnyInWindow(map.listerThings.ThingsInGroup(ThingRequestGroup.MechCharger),
                pawn, work, MaximumPerRoute, delegate(Thing thing)
            {
                var charger = thing as Building_MechCharger;
                if (charger == null || !Present(charger, map, pawn, work)) { return false; }
                if (!charger.CanPawnChargeCurrently(mech)) { return false; }
                return work != null || pawn.CanReserve(charger);
            });
        }

        // ---------------------------------------------------------------- enterables -- //

        /// <summary>
        /// `CarryToGrowthVat`, `CarryToGeneExtractor` and `CarryToSubcoreScanner` — three
        /// givers, one route, because all three are `WorkGiver_CarryToBuilding` over a
        /// `Building_Enterable` and the class is what carries every condition.
        ///
        /// The condition worth spelling out is the last one, because it is easy to read
        /// backwards: a hauler is wanted **only when the subject cannot walk in by itself.**
        /// Core hands the job out when the selected pawn is a prisoner of the colony, is
        /// downed, cannot move, or has this giver's own work type disabled, and returns
        /// false otherwise — an able colonist walks to the vat on its own errand. The work
        /// type compared is the giver def's, which for both of this family's giver defs is
        /// `Hauling`, the same def <see cref="WorkType"/> returns, so the parity is exact.
        ///
        /// And this is where the custody finding lives: `selectedPawn.Map != pawn.Map`
        /// refuses the job outright, so the subject is on the far map before the hauler
        /// arrives and never crosses anything. What is left to arrival is the reservation
        /// and reach on both the building and the subject.
        /// </summary>
        private static bool AnyEnterable(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            List<Thing> buildings =
                map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            if (buildings.Count == 0) { return false; }
            int windowStart = work == null ? 0
                : ConnectedWorkScan.WindowStart(buildings.Count, MaximumEnterablesPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < buildings.Count; position++)
            {
                if (work != null && examined >= MaximumEnterablesPerMap) { break; }
                var enterable = buildings[position] as Building_Enterable;
                if (enterable == null) { continue; }
                // Only a real enterable spends the budget, so a map full of ordinary
                // buildings cannot exhaust the window before reaching one.
                examined++;
                if (!Present(enterable, map, pawn, work) || !Operable(enterable, map))
                { continue; }
                Pawn subject = enterable.SelectedPawn;
                if (subject == null || subject.Destroyed || subject.Map != map) { continue; }
                if (!enterable.CanAcceptPawn(subject).Accepted) { continue; }
                if (!NeedsCarrying(subject)) { continue; }
                if (work != null) { return true; }
                if (pawn.CanReserve(enterable) && pawn.CanReserve(subject)) { return true; }
            }
            return false;
        }

        /// <summary>Core's own test for a subject that will not walk in unaided.</summary>
        private static bool NeedsCarrying(Pawn subject)
        {
            if (subject.IsPrisonerOfColony || subject.Downed) { return true; }
            if (subject.health == null || subject.health.capacities == null) { return true; }
            if (!subject.health.capacities.CapableOf(PawnCapacityDefOf.Moving)) { return true; }
            WorkTypeDef hauling = DefDatabase<WorkTypeDef>.GetNamedSilentFail("Hauling");
            return hauling != null && subject.WorkTypeIsDisabled(hauling);
        }
    }
}
