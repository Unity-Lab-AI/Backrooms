# -*- coding: utf-8 -*-
"""Set to gate control: a component does its ordinary job or the gate's, and the player chooses.

Owner: *"we should have a set to gate control for these components so other things arnt available
and can toggle between normal op and gate op depending whats wanted.."*

## What it does

Every component bound to a gate -- the comms console and the machining table, which both carry
`CompRimroomsGateConsole` -- gets a switch. **It begins in normal operation**, so commissioning a
door still changes nothing about how the colony works, which is the other half of the complaint
that started this.

**In gate control:**

  * the component's **ordinary company functions are withdrawn** -- the corporate supply call, the
    credit withdrawal, the containment alarm and the corporation contact all stop being offered on
    a console that is running the gate;
  * on a machining table, **every bill that is not the gate assembly is suspended**, and exactly
    those bills are un-suspended when it goes back to normal. A bill the player had already
    suspended stays suspended, because it is recorded by id rather than by guessing.

**In normal operation:**

  * the **gate assembly recipe is not available** on the table, so nobody can start building a
    gate on a bench that is doing its day job;
  * **spin-up refuses**, naming the component that is still in normal operation.

So the two modes are genuinely exclusive in both directions, which is what *"so other things arnt
available"* and *"depending whats wanted"* ask for together.

## What Core-only cannot do, stated rather than pretended

A comms console's **own** Core gizmo cannot be removed without Harmony, and a battery cannot be
partitioned out of its power net. So gate control withdraws **our** functions and gates **our**
operations; it does not and cannot hide Core's comms button. The mode is still load-bearing --
the gate will not spin up or be assembled without it -- but a player in gate control can still
press Core's own call button, and that is a limit of staying Core-only rather than something
hidden here.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONSOLE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate",
                       "CompRimroomsGateConsole.cs")
SPINUP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "GateSpinUp.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed", "RR_Gate.xml")

# ------------------------------------------------------------- state and the switch
C_FIELD_OLD = u"        private bool assemblyBillCreated;"
C_FIELD_NEW = u'''        private bool assemblyBillCreated;

        /// <summary>
        /// Whether this component is running the gate instead of doing its ordinary job.
        ///
        /// Owner: *"we should have a set to gate control for these components so other things
        /// arnt available and can toggle between normal op and gate op depending whats
        /// wanted.."*.
        ///
        /// **Begins false.** Commissioning a door must not change how the colony works -- that
        /// was the other half of the complaint this came from, where binding queued a hundred
        /// steel of assembly work nobody asked for.
        /// </summary>
        private bool gateControl;

        /// <summary>
        /// The bills **this** mode suspended, by Core's own bill id, so returning to normal
        /// operation un-suspends exactly those.
        ///
        /// Recorded rather than inferred: a bill the player had already suspended must stay
        /// suspended, and guessing from the current state cannot tell the two apart.
        /// </summary>
        private List<int> suspendedByGateControl = new List<int>();

        /// <summary>Whether this component is running the gate rather than its ordinary job.</summary>
        public bool IsGateControl { get { return gateControl && linkedGate != null; } }'''

# ----------------------------------------------- the gizmo, and our functions withdrawn
C_GIZMO_OLD = u"""        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            foreach (Gizmo gizmo in Procurement.CorporateSupplyGizmos.For(parent))
            { yield return gizmo; }
            foreach (Gizmo gizmo in Procurement.CreditWithdrawalGizmo.For(parent))
            { yield return gizmo; }
            // The call that puts a branch on the corporation's books. Only ever appears on a
            // comms console, and only while the branch is out of contact.
            foreach (Gizmo gizmo in Company.ContainmentAlarmGizmo.For(parent))
            { yield return gizmo; }
            foreach (Gizmo gizmo in Company.CorporateContactGizmo.For(parent))
            { yield return gizmo; }
        }"""

C_GIZMO_NEW = u'''        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }

            // **THE SWITCH.** Offered only on a component actually bound to a gate: a button that
            // can only refuse is worse than no button.
            if (linkedGate != null)
            {
                bool running = gateControl;
                yield return new Command_Action
                {
                    defaultLabel = (running ? "RR_NativeGate_NormalOpLabel"
                        : "RR_NativeGate_GateControlLabel").Translate(),
                    defaultDesc = (running ? "RR_NativeGate_NormalOpDesc"
                        : "RR_NativeGate_GateControlDesc").Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { SetGateControl(!running); }
                };
            }

            // **ORDINARY COMPANY FUNCTIONS ARE WITHDRAWN IN GATE CONTROL.** Owner: *"so other
            // things arnt available"*. A console running the gate is not also taking deliveries,
            // paying out credit, raising the containment alarm or placing the corporation call.
            if (IsGateControl) { yield break; }

            foreach (Gizmo gizmo in Procurement.CorporateSupplyGizmos.For(parent))
            { yield return gizmo; }
            foreach (Gizmo gizmo in Procurement.CreditWithdrawalGizmo.For(parent))
            { yield return gizmo; }
            // The call that puts a branch on the corporation's books. Only ever appears on a
            // comms console, and only while the branch is out of contact.
            foreach (Gizmo gizmo in Company.ContainmentAlarmGizmo.For(parent))
            { yield return gizmo; }
            foreach (Gizmo gizmo in Company.CorporateContactGizmo.For(parent))
            { yield return gizmo; }
        }

        /// <summary>
        /// Put this component into gate control, or back to its ordinary job.
        ///
        /// On a machining table, entering gate control **suspends every bill that is not the gate
        /// assembly** and records which ones it suspended by Core's own bill id; leaving
        /// un-suspends exactly those. **A bill the player had already suspended stays
        /// suspended**, which is why the ids are recorded rather than the state inferred.
        /// </summary>
        public void SetGateControl(bool running)
        {
            if (gateControl == running) { return; }
            gateControl = running;
            Building_WorkTable table = WorkTable;
            if (table == null || table.BillStack == null) { return; }

            if (running)
            {
                suspendedByGateControl.Clear();
                foreach (Bill bill in table.BillStack.Bills)
                {
                    if (bill == null || bill.suspended) { continue; }
                    if (bill.recipe != null && bill.recipe.defName == "RR_AssembleMachineGate")
                    { continue; }
                    bill.suspended = true;
                    suspendedByGateControl.Add(bill.loadID);
                }
                return;
            }

            foreach (Bill bill in table.BillStack.Bills)
            {
                if (bill == null || !suspendedByGateControl.Contains(bill.loadID)) { continue; }
                bill.suspended = false;
            }
            suspendedByGateControl.Clear();
        }'''

C_SCRIBE_OLD = u"""            Scribe_Values.Look(ref assemblyBillCreated, "rr_gateAssemblyBillCreated", false);"""
C_SCRIBE_NEW = u"""            Scribe_Values.Look(ref assemblyBillCreated, "rr_gateAssemblyBillCreated", false);
            Scribe_Values.Look(ref gateControl, "rr_gateConsoleGateControl", false);
            Scribe_Collections.Look(ref suspendedByGateControl, "rr_gateConsoleSuspendedBills",
                LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            { suspendedByGateControl = suspendedByGateControl ?? new List<int>(); }"""

# ------------------------------- the recipe is unavailable outside gate control
C_RECIPE_OLD = u"""            CompRimroomsGateConsole console = thing == null ? null : thing.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate gate = console == null ? null : console.Gate;
            return gate != null && !gate.AssemblyComplete;"""
C_RECIPE_NEW = u"""            CompRimroomsGateConsole console = thing == null ? null : thing.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate gate = console == null ? null : console.Gate;
            // **NOT AVAILABLE ON A BENCH DOING ITS DAY JOB.** Owner: *"can toggle between normal
            // op and gate op depending whats wanted"*. The two modes are exclusive in both
            // directions: gate control suspends the ordinary bills, and normal operation withdraws
            // the gate recipe.
            return gate != null && !gate.AssemblyComplete && console.IsGateControl;"""

console = io.open(CONSOLE, encoding="utf-8").read()
C_EDITS = [(C_FIELD_OLD, C_FIELD_NEW), (C_GIZMO_OLD, C_GIZMO_NEW),
           (C_SCRIBE_OLD, C_SCRIBE_NEW), (C_RECIPE_OLD, C_RECIPE_NEW)]
problems = []
for old, _ in C_EDITS:
    if console.count(old) != 1:
        problems.append("%d of %r" % (console.count(old), old[:58]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM (console): %s" % problem)
    raise SystemExit(1)
for old, new in C_EDITS:
    console = console.replace(old, new, 1)
io.open(CONSOLE, "w", encoding="utf-8", newline="").write(console)
print("the switch, the withdrawal, the bill suspension and the recipe gate")

# ------------------------------------------------- spin-up refuses outside gate control
S_OLD = u"""            if (IsOpening) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }"""
S_NEW = u"""            if (IsOpening) { return CompanyActionResult.Refused("RR_Gate_AlreadyOpen"); }
            // **A COMPONENT DOING ITS ORDINARY JOB DOES NOT RUN A GATE.** Owner: *"we should have
            // a set to gate control for these components so other things arnt available and can
            // toggle between normal op and gate op depending whats wanted"*. Named rather than
            // silent: the player needs to know which switch is still the wrong way round.
            CompRimroomsGateConsole spinUpStation = nativeConsole == null
                ? null : nativeConsole.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGateConsole spinUpWorkshop = nativeAssemblyBench == null
                ? null : nativeAssemblyBench.TryGetComp<CompRimroomsGateConsole>();
            if (spinUpStation != null && !spinUpStation.IsGateControl)
            { return CompanyActionResult.Refused("RR_NativeGate_NotInGateControl"); }
            if (spinUpWorkshop != null && !spinUpWorkshop.IsGateControl)
            { return CompanyActionResult.Refused("RR_NativeGate_NotInGateControl"); }"""

spinup = io.open(SPINUP, encoding="utf-8").read()
if spinup.count(S_OLD) != 1:
    print("ANCHOR PROBLEM (spinup): %d" % spinup.count(S_OLD))
    raise SystemExit(1)
io.open(SPINUP, "w", encoding="utf-8", newline="").write(spinup.replace(S_OLD, S_NEW, 1))
print("spin-up refuses while a component is in normal operation")

# -------------------------------------------------------------------- the strings
K_ANCHOR = u"  <RR_NativeGate_MakeLabel>"
K_NEW = (u"  <RR_NativeGate_GateControlLabel>Set to gate control</RR_NativeGate_GateControlLabel>\n"
         u"  <RR_NativeGate_GateControlDesc>Hand this installation over to the gate. Its ordinary "
         u"company functions are withdrawn while it does, and on a machining table every bill "
         u"except the gate assembly is suspended until it returns to normal operation."
         u"</RR_NativeGate_GateControlDesc>\n"
         u"  <RR_NativeGate_NormalOpLabel>Return to normal operation</RR_NativeGate_NormalOpLabel>\n"
         u"  <RR_NativeGate_NormalOpDesc>Give this installation back to its ordinary work. The "
         u"bills gate control suspended are resumed, and the gate will not spin up or be "
         u"assembled until it is handed over again.</RR_NativeGate_NormalOpDesc>\n"
         u"  <RR_NativeGate_NotInGateControl>One of the gate's installations is still in normal "
         u"operation. Set the comms console and the machining table to gate control first."
         u"</RR_NativeGate_NotInGateControl>\n")

keyed = io.open(KEYED, encoding="utf-8-sig").read()
if keyed.count(K_ANCHOR) != 1:
    print("ANCHOR PROBLEM (keyed): %d" % keyed.count(K_ANCHOR))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    keyed.replace(K_ANCHOR, K_NEW + K_ANCHOR, 1))
print("five keyed strings written")
