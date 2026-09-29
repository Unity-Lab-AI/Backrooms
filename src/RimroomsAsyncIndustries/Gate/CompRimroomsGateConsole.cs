using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Gate
{
    public sealed class CompProperties_RimroomsGateConsole : CompProperties
    {
        public bool nativeProvider;
        public CompProperties_RimroomsGateConsole() { compClass = typeof(CompRimroomsGateConsole); }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
            if (nativeProvider)
            {
                if (!typeof(Building_WorkTable).IsAssignableFrom(parentDef.thingClass) &&
                    !typeof(Building_CommsConsole).IsAssignableFrom(parentDef.thingClass))
                { yield return "Native Rimrooms station requires an existing worktable or communications console."; }
                yield break;
            }
            if (parentDef.thingClass != typeof(Building_WorkTable))
            { yield return "RR_GateConsole must use Building_WorkTable for native bills."; }
            if (parentDef.size.x != 1 || parentDef.size.z != 1)
            { yield return "RR_GateConsole must use a 1x1 footprint."; }
        }
    }

    /// <summary>Pairs the powered bill console with its nearest machine gate.</summary>
    public sealed class CompRimroomsGateConsole : ThingComp
    {
        private Thing linkedGate;
        private bool assemblyBillCreated;
        public Building_WorkTable WorkTable { get { return parent as Building_WorkTable; } }
        public bool NativeProvider { get { return ((CompProperties_RimroomsGateConsole)props).nativeProvider; } }
        public Thing LinkedGate { get { return linkedGate; } }
        public bool HasAssemblyJob
        {
            get
            {
                return parent.Spawned && parent.Map.mapPawns.AllPawnsSpawned.Any(p =>
                    p.CurJob != null && p.CurJob.bill != null && p.CurJob.bill.recipe != null &&
                    p.CurJob.bill.recipe.defName == "RR_AssembleMachineGate" &&
                    p.CurJob.GetTarget(TargetIndex.A).Thing == parent);
            }
        }

        public bool CanBindToGate(Thing gate)
        {
            return NativeProvider && parent.Spawned && parent.Faction == Faction.OfPlayer &&
                gate != null && gate.Spawned && gate.Map == parent.Map && gate.Faction == Faction.OfPlayer &&
                gate.TryGetComp<CompRimroomsGate>() != null && (linkedGate == null || linkedGate == gate);
        }

        public bool BindToGate(Thing gate)
        {
            if (!CanBindToGate(gate)) { return false; }
            linkedGate = gate;
            return true;
        }

        public bool ClearNativeBinding(Thing expectedGate)
        {
            if (!NativeProvider || linkedGate != expectedGate || HasAssemblyJob) { return false; }
            CompRimroomsGate gate = linkedGate == null ? null : linkedGate.TryGetComp<CompRimroomsGate>();
            if (gate != null && gate.IsOpening) { return false; }
            // Suspend unfinished installation work before releasing its exact provider link.
            if (WorkTable != null)
            {
                foreach (Bill_Production bill in WorkTable.BillStack.Bills.OfType<Bill_Production>()
                    .Where(b => b.recipe != null && b.recipe.defName == "RR_AssembleMachineGate"))
                { bill.suspended = true; }
            }
            linkedGate = null;
            assemblyBillCreated = false;
            return true;
        }

        public CompRimroomsGate Gate
        {
            get
            {
                if (!parent.Spawned || parent.Map == null) { return null; }
                if (linkedGate != null && linkedGate.Spawned && linkedGate.Map == parent.Map)
                { return linkedGate.TryGetComp<CompRimroomsGate>(); }
                if (NativeProvider) { return null; }
                ThingDef gateDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_MachineGate");
                if (gateDef == null) { return null; }
                linkedGate = parent.Map.listerBuildings.AllBuildingsColonistOfDef(gateDef)
                    .OrderBy(t => t.Position.DistanceToSquared(parent.Position)).FirstOrDefault();
                return linkedGate == null ? null : linkedGate.TryGetComp<CompRimroomsGate>();
            }
        }

        /// <summary>
        /// The corporate catalogue is reached from this console, because the console is already
        /// the thing a branch talks to the company through. **No new building and no new UI
        /// window** was added for it -- a gizmo and a float menu, which is the lightest surface
        /// that can carry three separate locks legibly.
        /// </summary>
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            foreach (Gizmo gizmo in Procurement.CorporateSupplyGizmos.For(parent))
            { yield return gizmo; }
            foreach (Gizmo gizmo in Procurement.CreditWithdrawalGizmo.For(parent))
            { yield return gizmo; }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref linkedGate, "rr_gateConsoleLinkedGate");
            Scribe_Values.Look(ref assemblyBillCreated, "rr_gateAssemblyBillCreated", false);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!NativeProvider) { EnsureAssemblyBill(); }
        }

        public void EnsureAssemblyBill()
        {
            Building_WorkTable table = WorkTable;
            if (table == null || table.BillStack == null) { return; }
            if (NativeProvider && Gate == null) { return; }
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RR_AssembleMachineGate");
            if (recipe == null) { return; }
            Bill_Production existing = table.BillStack.Bills.OfType<Bill_Production>()
                .FirstOrDefault(b => b.recipe == recipe);
            if (existing != null)
            {
                existing.repeatMode = BillRepeatModeDefOf.RepeatCount;
                existing.repeatCount = 1;
                if (NativeProvider && Gate != null) { existing.suspended = Gate.AssemblyComplete; }
                else if (Gate != null && Gate.AssemblyComplete) { existing.suspended = true; }
                assemblyBillCreated = true;
                return;
            }
            if (assemblyBillCreated && Gate != null && Gate.AssemblyComplete) { return; }
            Bill_Production bill = new Bill_Production(recipe)
            {
                repeatMode = BillRepeatModeDefOf.RepeatCount,
                repeatCount = 1,
                suspended = Gate != null && Gate.AssemblyComplete
            };
            table.BillStack.AddBill(bill);
            assemblyBillCreated = true;
        }

        public void MarkAssemblyBillComplete()
        {
            Building_WorkTable table = WorkTable;
            if (table == null || table.BillStack == null) { return; }
            foreach (Bill_Production bill in table.BillStack.Bills.OfType<Bill_Production>()
                .Where(b => b.recipe != null && b.recipe.defName == "RR_AssembleMachineGate"))
            {
                bill.suspended = true;
                bill.repeatMode = BillRepeatModeDefOf.RepeatCount;
                bill.repeatCount = 1;
            }
            assemblyBillCreated = true;
        }
    }

    /// <summary>Completes the one-shot assembly state only after Core's native bill consumes its ingredients and work finishes.</summary>
    public sealed class RecipeWorker_RimroomsGateAssembly : RecipeWorker
    {
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            CompRimroomsGateConsole console = thing == null ? null : thing.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate gate = console == null ? null : console.Gate;
            return gate != null && !gate.AssemblyComplete;
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            if (billDoer == null || billDoer.CurJob == null || billDoer.CurJob.bill == null ||
                billDoer.CurJob.bill.recipe == null || billDoer.CurJob.bill.recipe.defName != "RR_AssembleMachineGate")
            { return; }
            Thing billGiver = billDoer.CurJob.GetTarget(TargetIndex.A).Thing;
            CompRimroomsGateConsole console = billGiver == null ? null : billGiver.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate gate = console == null ? null : console.Gate;
            if (gate == null) { return; }
            CompanyActionResult result = gate.CompleteAssemblyFromBill(billGiver, billDoer.CurJob.bill.recipe);
            if (result.Success) { console.MarkAssemblyBillComplete(); }
        }
    }
}
