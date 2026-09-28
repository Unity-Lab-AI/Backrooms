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
        public CompProperties_RimroomsGateConsole() { compClass = typeof(CompRimroomsGateConsole); }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
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

        public CompRimroomsGate Gate
        {
            get
            {
                if (!parent.Spawned || parent.Map == null) { return null; }
                if (linkedGate != null && linkedGate.Spawned && linkedGate.Map == parent.Map)
                { return linkedGate.TryGetComp<CompRimroomsGate>(); }
                ThingDef gateDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_MachineGate");
                if (gateDef == null) { return null; }
                linkedGate = parent.Map.listerBuildings.AllBuildingsColonistOfDef(gateDef)
                    .OrderBy(t => t.Position.DistanceToSquared(parent.Position)).FirstOrDefault();
                return linkedGate == null ? null : linkedGate.TryGetComp<CompRimroomsGate>();
            }
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
            EnsureAssemblyBill();
        }

        public void EnsureAssemblyBill()
        {
            Building_WorkTable table = WorkTable;
            if (table == null || table.BillStack == null) { return; }
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RR_AssembleMachineGate");
            if (recipe == null) { return; }
            Bill_Production existing = table.BillStack.Bills.OfType<Bill_Production>()
                .FirstOrDefault(b => b.recipe == recipe);
            if (existing != null)
            {
                existing.repeatMode = BillRepeatModeDefOf.RepeatCount;
                existing.repeatCount = 1;
                if (Gate != null && Gate.AssemblyComplete) { existing.suspended = true; }
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
