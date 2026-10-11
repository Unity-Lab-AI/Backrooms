using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A crafter crossing a gate to actually *run* a bill on the other side.
    ///
    /// ## The gap this closes
    ///
    /// The carry family has delivered ingredients to a remote bill since 0.5.7-dev, but
    /// **nobody was ever sent to work the bench.** A coordinate with a stove, a bill and a
    /// pile of delivered ingredients produced nothing at all unless a colonist happened to be
    /// standing there for some other reason. The material arrived and sat.
    ///
    /// ## Why a deployment is the *correct* shape here, not a workaround
    ///
    /// The carry family's record pinned the rule that makes this work:
    ///
    /// * `WorkGiver_DoBill.ClosestUnfinishedThingForBill` validates
    ///   `((UnfinishedThing)t).Creator == pawn`.
    /// * `Bill_ProductionWithUft` binds `BoundUft` to a `BoundWorker`, and only that worker
    ///   resumes it.
    ///
    /// A half-made thing belongs to exactly one colonist. That is precisely why the *carry*
    /// family must never touch one — it would be hauling something nobody on either map is
    /// allowed to finish. But a **deployed** worker stands on the bill's own map and runs
    /// Core's own `WorkGiver_DoBill` locally, creating and finishing its *own* unfinished
    /// thing, on one map, exactly as Core intends. The deployment shape sidesteps the trap by
    /// construction rather than working around it.
    ///
    /// ## One provider per work type, because Core makes that distinction itself
    ///
    /// This is not five copies of one idea. `WorkGiver_DoBill.StartOrResumeBillJob` contains:
    ///
    /// <code>
    /// if (bill.recipe.requiredGiverWorkType != null &amp;&amp;
    ///     bill.recipe.requiredGiverWorkType != def.workType) { continue; }
    /// </code>
    ///
    /// and a bench belongs to a work type only through its `WorkGiverDef.fixedBillGiverDefs`.
    /// A single "bill work" provider would have to declare one `WorkType`, and a pawn with
    /// cooking enabled but smithing disabled would then be pulled across a gate for smithing
    /// it cannot do. So each work type that has bill work gets its own provider, its own
    /// priority pair, and its own place in the player's work settings — which is also how the
    /// player already expects to control it.
    ///
    /// ## The bench set is read from the defs, never from a list of names
    ///
    /// `BenchDefs` unions the `fixedBillGiverDefs` of **every** `WorkGiverDef` in the loaded
    /// game whose `workType` is this provider's and whose giver class is `WorkGiver_DoBill` or
    /// a subclass. That is a capability match against live data, so a mod that adds a bench to
    /// an existing work type is picked up with no code here and no mention of its name — which
    /// is the standing rule for this project, applied one level deeper than usual.
    ///
    /// Profile rows read before writing this, per the owner's standing rule that the prep work
    /// is where mod facts live:
    ///
    /// * **246 Vanilla Furniture Expanded - Factory** — bill-driven factory benches. Its
    ///   benches arrive through their own `WorkGiverDef`s, so they are covered automatically
    ///   *if* their work type is one that exists here. A mod introducing a wholly new work
    ///   type with its own bill givers is **not** covered; that is a named limit, not a claim.
    /// * **53 Big Little Mod Patch** links furniture and workbenches across mods. Because the
    ///   bench set is computed from defs at runtime, anything it links is included with no
    ///   action here and nothing of its is copied or patched.
    /// * **260 While You Are Nearby** raises the priority of *nearby* work when vanilla would
    ///   pick something distant. It reorders which target a scanning giver chooses; this is a
    ///   `NonScanJob` giver with a single candidate, so there is nothing for it to reorder.
    ///   Its effect, if any, is to make a colonist prefer local work — which is already this
    ///   family's own rule, since the planning giver sits below every local giver.
    /// * **67 Compact Work Tab** is presentation only and its page states added work types
    ///   work; this adds work *givers* to existing types, which is a weaker change.
    /// * **96 Fueled Crematoriums** and any other fuelled bench matter because Core hands out
    ///   a *refuel* job instead of the bill when `CompRefuelable.HasFuel` is false. This
    ///   provider therefore requires `UsableForBillsAfterFueling()`, so nobody crosses a gate
    ///   for a bench that only needs fuel — the fuel carry family already owns that route.
    /// * **83 Dubs Rimatomics** and **194 Rimefeller** keep their own production systems. This
    ///   provider matches Core's `PotentialBillGiver` group and Core's own bill types, so a
    ///   separate modded system is neither claimed nor broken. It simply is not this work.
    ///
    /// None of those is a dependency and every one may be absent.
    /// </summary>
    public sealed class BillWorkProvider : ConnectedDeploymentProvider
    {
        private readonly string providerId;
        private readonly string workTypeDefName;
        private readonly string labelKey;

        /// <summary>
        /// Cached bench defs for this provider's work type. Built once after the defs are
        /// loaded, because it cannot be built in a static initialiser that runs before them.
        /// </summary>
        private HashSet<ThingDef> benchDefs;
        private bool benchDefsBuilt;

        internal BillWorkProvider(string providerId, string workTypeDefName, string labelKey)
        {
            this.providerId = providerId;
            this.workTypeDefName = workTypeDefName;
            this.labelKey = labelKey;
        }

        public override string ProviderId { get { return providerId; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return labelKey; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail(workTypeDefName); } }

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
            HashSet<ThingDef> benches = BenchDefs();
            if (benches.Count == 0) { return false; }

            List<Thing> givers = map.listerThings.ThingsInGroup(ThingRequestGroup.PotentialBillGiver);
            if (givers.Count == 0) { return false; }
            // A rotating window, never a prefix, per the standing scan rule.
            int windowStart = ConnectedWorkScan.WindowStart(givers.Count,
                ConnectedBillScan.MaximumGiversPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < givers.Count; position++)
            {
                if (examined >= ConnectedBillScan.MaximumGiversPerMap) { break; }
                examined++;
                Thing giver = givers[position];
                if (giver == null || !benches.Contains(giver.def)) { continue; }
                if (!ConnectedBillScan.UsableGiver(giver, map)) { continue; }
                if (!((IBillGiver)giver).UsableForBillsAfterFueling()) { continue; }
                if (!work.ObservedAreaAllows(pawn, map, ConnectedBillScan.ApproachCell(giver)))
                { continue; }
                if (AnyWorkableBill(giver, map, pawn)) { return true; }
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            HashSet<ThingDef> benches = BenchDefs();
            if (benches.Count == 0) { return false; }
            Map map = pawn.Map;
            // Not windowed, deliberately. A window that missed the one workable bench would
            // release the deployment while there was still work to do and plan the worker
            // straight back across the gate — the exact thrash the record exists to prevent.
            List<Thing> givers = map.listerThings.ThingsInGroup(ThingRequestGroup.PotentialBillGiver);
            for (int index = 0; index < givers.Count; index++)
            {
                Thing giver = givers[index];
                if (giver == null || !benches.Contains(giver.def)) { continue; }
                if (!ConnectedBillScan.UsableGiver(giver, map)) { continue; }
                if (!((IBillGiver)giver).UsableForBillsAfterFueling()) { continue; }
                // Here the pawn overloads mean what they say, because this is the pawn's map.
                if (giver.IsForbidden(pawn) || !pawn.CanReserve(giver)) { continue; }
                if (giver.def.hasInteractionCell &&
                    !pawn.CanReserveSittableOrSpot(giver.InteractionCell, false))
                { continue; }
                if (AnyWorkableBill(giver, map, pawn)) { return true; }
            }
            return false;
        }

        /// <summary>
        /// Whether this giver holds a bill this worker could start, asked with the rules that
        /// are fair to ask from anywhere.
        ///
        /// Each test here was checked against Core rather than assumed:
        ///
        /// * <c>requiredGiverWorkType</c> — a fact about the recipe, compared against this
        ///   provider's own work type exactly as Core compares it against `def.workType`.
        /// * <c>nextTickToSearchForIngredients</c> — Core's own throttle, which it pushes
        ///   forward when a search fails. It is **read** and never written; writing Core's
        ///   scan state from a remote probe is forbidden, and reading it here means a bill
        ///   that just failed for somebody does not immediately pull somebody else across.
        /// * <c>PawnAllowedToStartAnew</c> — reads the bill's pawn restriction, its
        ///   slaves-only / mechs-only flags and the pawn's own skill level against
        ///   <c>allowedSkillRange</c>. Every one is a fact about the bill and the worker's
        ///   identity; **none reads the worker's map**, so it is safe from here. This is the
        ///   check that stops a bill restricted to one colonist, or to a skill band, from
        ///   dragging the wrong worker through a gate.
        /// * <c>FirstSkillRequirementPawnDoesntSatisfy</c> — the recipe's own skill minimum
        ///   against the pawn's skills. Also map-independent.
        ///
        /// Deliberately left to Core on arrival: <c>TryFindBestBillIngredients</c>, every
        /// reservation, the interaction cell, the pawn form of the forbidden check, and the
        /// whole unfinished-thing resolution.
        /// </summary>
        private bool AnyWorkableBill(Thing giver, Map map, Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (workType == null) { return false; }
            BillStack stack = ((IBillGiver)giver).BillStack;
            if (stack == null) { return false; }
            // A rotating window over the stack, so suspended or unworkable bills at the top
            // cannot hide a workable one further down.
            int windowStart = ConnectedWorkScan.WindowStart(stack.Count,
                ConnectedBillScan.MaximumBillsPerGiver, pawn);
            int examined = 0;
            for (int index = windowStart; index < stack.Count; index++)
            {
                if (examined >= ConnectedBillScan.MaximumBillsPerGiver) { break; }
                examined++;
                Bill bill = stack[index];
                if (!ConnectedBillScan.OrdinaryProductionBill(bill, giver, map)) { continue; }
                if (bill.recipe.requiredGiverWorkType != null &&
                    bill.recipe.requiredGiverWorkType != workType)
                { continue; }
                if (Find.TickManager != null &&
                    Find.TickManager.TicksGame <= bill.nextTickToSearchForIngredients)
                { continue; }
                if (!bill.PawnAllowedToStartAnew(pawn)) { continue; }
                if (bill.recipe.FirstSkillRequirementPawnDoesntSatisfy(pawn) != null) { continue; }
                // The approximate half, and the one that stops a permanently futile trip. See
                // ConnectedBillScan.EveryIngredientPresent for why it is necessary rather than
                // sufficient, and why Core's own throttle cannot cover this case.
                if (!ConnectedBillScan.EveryIngredientPresent(bill, giver)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Every bench def that carries bill work of this provider's work type, unioned from
        /// the loaded `WorkGiverDef`s rather than named here.
        ///
        /// Only `fixedBillGiverDefs` is read. The `billGiversAll*` flags exist for pawn and
        /// corpse bill givers — surgery — which is Doctor work and belongs to the tending
        /// family; `UsableGiver` refuses a pawn or corpse giver outright for the same reason.
        /// </summary>
        private HashSet<ThingDef> BenchDefs()
        {
            if (benchDefsBuilt) { return benchDefs; }
            var found = new HashSet<ThingDef>();
            WorkTypeDef workType = WorkType;
            if (workType != null)
            {
                List<WorkGiverDef> givers = DefDatabase<WorkGiverDef>.AllDefsListForReading;
                for (int index = 0; index < givers.Count; index++)
                {
                    WorkGiverDef definition = givers[index];
                    if (definition == null || definition.workType != workType) { continue; }
                    if (definition.giverClass == null ||
                        !typeof(WorkGiver_DoBill).IsAssignableFrom(definition.giverClass))
                    { continue; }
                    if (definition.fixedBillGiverDefs == null) { continue; }
                    for (int position = 0; position < definition.fixedBillGiverDefs.Count; position++)
                    {
                        ThingDef bench = definition.fixedBillGiverDefs[position];
                        if (bench != null) { found.Add(bench); }
                    }
                }
            }
            benchDefs = found;
            // Only cached once a work type actually resolved. Caching an empty set because the
            // defs were not loaded yet would make the provider permanently dead.
            benchDefsBuilt = workType != null;
            return benchDefs;
        }
    }
}
