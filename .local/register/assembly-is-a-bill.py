# -*- coding: utf-8 -*-
"""The gate assembled itself the moment it was commissioned. The bill is the player's now.

Owner: *"the machining table to op[en the gate needs to be a bill currently they instantly try to
open the gate and build it and i have no say in the mattter even tho nothing is connected or built
yet and havent started the mission line yet"*.

## What was happening

`BindNativeInfrastructure` ended with `EnsureNativeAssemblyBill`, which called
`EnsureAssemblyBill`, which **added an unsuspended `Bill_Production` to the machining table's
stack.** So the instant a door was commissioned, crafters walked off to carry a hundred steel and
eight components and assemble the gate. No decision, no mission, nothing built -- which is exactly
the complaint.

**And the recipe's own description said otherwise the whole time:** *"Physically carry 100 steel
and 8 industrial components to the designated machining table, then complete the installation
assembly work. Designate the native door, communications console, battery and machining table in
Operations first."* That is an instruction to a player who adds the bill. The code added it for
them.

The recipe already carries `<recipeUsers><li>TableMachining</li></recipeUsers>`, so it has always
been in the table's own recipe list. **Nothing had to be built to give the player the choice; the
choice had been taken.**

## What it does instead

`SyncAssemblyBill` -- renamed, because *ensure* was the whole defect -- **never adds a bill.** It
only manages one the player added, and only in the one direction that cannot take a decision
away:

  * it **suspends** the bill once the gate is assembled, so a repeating bill does not spend
    another hundred steel on a gate that exists;
  * it **never un-suspends**, because a player who suspended a bill meant it;
  * it **never changes the repeat mode or count**, because those are theirs.

`MarkAssemblyBillComplete` keeps clamping a completed bill to a single count -- that one runs after
the work is finished, where there is no decision left to take.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONSOLE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate",
                       "CompRimroomsGateConsole.cs")
BINDING = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "NativeGateBinding.cs")

C_OLD = u"""        public void EnsureAssemblyBill()
        {
            Building_WorkTable table = WorkTable;
            if (table == null || table.BillStack == null) { return; }
            if (Gate == null) { return; }
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RR_AssembleMachineGate");
            if (recipe == null) { return; }
            Bill_Production existing = table.BillStack.Bills.OfType<Bill_Production>()
                .FirstOrDefault(b => b.recipe == recipe);
            if (existing != null)
            {
                existing.repeatMode = BillRepeatModeDefOf.RepeatCount;
                existing.repeatCount = 1;
                if (Gate != null) { existing.suspended = Gate.AssemblyComplete; }
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
        }"""

C_NEW = u'''        /// <summary>
        /// Keep a player's gate-assembly bill honest. **It never adds one.**
        ///
        /// ## What this used to do, and why it was wrong
        ///
        /// It was called `EnsureAssemblyBill`, and *ensure* was the whole defect: it **added an
        /// unsuspended `Bill_Production` to the machining table the instant a door was
        /// commissioned.** Crafters walked off to carry a hundred steel and eight components and
        /// assemble the gate with nothing connected, nothing built and no mission begun.
        ///
        /// Owner: *"the machining table to op[en the gate needs to be a bill currently they
        /// instantly try to open the gate and build it and i have no say in the mattter even tho
        /// nothing is connected or built yet and havent started the mission line yet"*.
        ///
        /// **The recipe's own description had said otherwise the whole time** -- *"Designate the
        /// native door, communications console, battery and machining table in Operations
        /// first"* is an instruction to a player who then adds the bill. And
        /// `RR_AssembleMachineGate` carries `recipeUsers: TableMachining`, so it has always been
        /// in the table's own list. Nothing had to be built to give the player the choice; **the
        /// choice had been taken.**
        ///
        /// ## The one direction it may act in
        ///
        /// Suspending a bill once the gate exists cannot take a decision away -- it stops a
        /// repeating bill spending another hundred steel on a gate that is already assembled. So
        /// that is all it does. It **never un-suspends**, because a player who suspended a bill
        /// meant it, and it **never touches the repeat mode or count**, because those are theirs.
        /// </summary>
        public void SyncAssemblyBill()
        {
            Building_WorkTable table = WorkTable;
            if (table == null || table.BillStack == null) { return; }
            if (Gate == null || !Gate.AssemblyComplete) { return; }
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RR_AssembleMachineGate");
            if (recipe == null) { return; }
            foreach (Bill_Production bill in table.BillStack.Bills.OfType<Bill_Production>()
                .Where(candidate => candidate.recipe == recipe))
            {
                bill.suspended = true;
                assemblyBillCreated = true;
            }
        }'''

B_OLD = u"""                workshop.EnsureAssemblyBill();
                if (assemblyComplete) { workshop.MarkAssemblyBillComplete(); }"""

B_NEW = u"""                // **THE BILL IS THE PLAYER'S.** This called `EnsureAssemblyBill`, which added
                // an unsuspended production bill the instant a door was commissioned, so the
                // gate assembled itself with nothing connected and no mission begun. The recipe
                // is on the machining table's own list; the player queues it when they are ready.
                workshop.SyncAssemblyBill();
                if (assemblyComplete) { workshop.MarkAssemblyBillComplete(); }"""

console = io.open(CONSOLE, encoding="utf-8").read()
if console.count(C_OLD) != 1:
    print("ANCHOR PROBLEM (console): %d" % console.count(C_OLD))
    raise SystemExit(1)
io.open(CONSOLE, "w", encoding="utf-8", newline="").write(console.replace(C_OLD, C_NEW, 1))
print("the console never adds a bill; it only suspends a finished one")

binding = io.open(BINDING, encoding="utf-8").read()
if binding.count(B_OLD) != 1:
    print("ANCHOR PROBLEM (binding): %d" % binding.count(B_OLD))
    raise SystemExit(1)
io.open(BINDING, "w", encoding="utf-8", newline="").write(binding.replace(B_OLD, B_NEW, 1))
print("commissioning no longer queues anybody's work")
