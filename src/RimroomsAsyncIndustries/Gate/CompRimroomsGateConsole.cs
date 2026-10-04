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
            // Only existing Core objects carry this component now. The custom RR_GateConsole
            // it used to also describe was retired in 0.9.0-dev, so there is no second shape
            // left to validate.
            if (!typeof(Building_WorkTable).IsAssignableFrom(parentDef.thingClass) &&
                !typeof(Building_CommsConsole).IsAssignableFrom(parentDef.thingClass))
            { yield return "Native Rimrooms station requires an existing worktable or communications console."; }
        }
    }

    /// <summary>Pairs the powered bill console with its nearest machine gate.</summary>
    public sealed class CompRimroomsGateConsole : ThingComp
    {
        private Thing linkedGate;
        private bool assemblyBillCreated;

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
        /// The bills **this** mode suspended, by Core's own unique load id, so returning to normal
        /// operation un-suspends exactly those.
        ///
        /// Recorded rather than inferred: a bill the player had already suspended must stay
        /// suspended, and guessing from the current state cannot tell the two apart.
        /// </summary>
        private List<string> suspendedByGateControl = new List<string>();

        /// <summary>Whether this component is running the gate rather than its ordinary job.</summary>
        public bool IsGateControl { get { return gateControl && linkedGate != null; } }
        public Building_WorkTable WorkTable { get { return parent as Building_WorkTable; } }
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
            return parent.Spawned && parent.Faction == Faction.OfPlayer &&
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
            if (linkedGate != expectedGate || HasAssemblyJob) { return false; }
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
                // A station is bound to its gate explicitly, by the player, through the
                // designation UI. It used to fall back to hunting for the nearest
                // RR_MachineGate on the map; that def was retired in 0.9.0-dev and the guess
                // it made was never the right answer anyway once two gates could exist.
                return null;
            }
        }

        /// <summary>
        /// What this station is, what it is bound to, and which job it is currently doing.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"we also need to be making sure all mod
        /// ingame decriptions and informational informations for everything is properly in the
        /// cards like the game does currently"*, and the standard the row sets is *"What it is,
        /// what it needs, and why it is not working when it is not."*
        ///
        /// ## The gap the audit found
        ///
        /// **This comp had no inspect card at all.** The gate has one, the beacon has one, and
        /// the station — which is the thing a player actually clicks on to run a gate — had
        /// nothing. Every piece of state below was readable only by noticing *which label one of
        /// the gizmos happened to be showing*: a station bound to no gate looked exactly like a
        /// station bound to one, and a machining table silently holding every ordinary bill
        /// suspended looked exactly like a machining table doing its day job.
        ///
        /// That last one is the sharp edge. `SetGateControl` suspends every unrelated bill on the
        /// bench, which is correct and was asked for — *"so other things arnt available"* — but a
        /// player who left it in gate control a week ago and cannot work out why nothing is being
        /// crafted has no way to find out from the bench itself.
        ///
        /// ## Dormant on anything nobody bound
        ///
        /// Returns null with no binding and no mode set, so a comms console or machining table in
        /// an ordinary colony reads exactly as it always did. Same rule as every other comp this
        /// mod puts on existing content.
        /// </summary>
        public override string CompInspectStringExtra()
        {
            var lines = new List<string>();
            if (linkedGate == null)
            {
                // Silent unless the branch exists. An unbound bench is not a broken bench, and a
                // colony that has never opened Operations should not be told about gates at all.
                RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
                if (campaign == null) { return null; }
                lines.Add("RR_NativeGate_StationUnbound".Translate().ToString());
            }
            else
            {
                lines.Add("RR_NativeGate_StationBound".Translate(linkedGate.LabelShortCap).ToString());
                // **WHY NOTHING IS BEING CRAFTED, said on the bench rather than left to be
                // deduced.** Gate control holds the ordinary bills suspended by design; without
                // this line that design is indistinguishable from a fault.
                lines.Add((gateControl ? "RR_NativeGate_StationGateControl"
                    : "RR_NativeGate_StationNormalOp").Translate().ToString());
            }
            return lines.Count == 0 ? null : string.Join("\n", lines.ToArray());
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
                    suspendedByGateControl.Add(bill.GetUniqueLoadID());
                }
                return;
            }

            foreach (Bill bill in table.BillStack.Bills)
            {
                if (bill == null || !suspendedByGateControl.Contains(bill.GetUniqueLoadID()))
                { continue; }
                bill.suspended = false;
            }
            suspendedByGateControl.Clear();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref linkedGate, "rr_gateConsoleLinkedGate");
            Scribe_Values.Look(ref assemblyBillCreated, "rr_gateAssemblyBillCreated", false);
            Scribe_Values.Look(ref gateControl, "rr_gateConsoleGateControl", false);
            Scribe_Collections.Look(ref suspendedByGateControl, "rr_gateConsoleSuspendedBills",
                LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            { suspendedByGateControl = suspendedByGateControl ?? new List<string>(); }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
        }

        /// <summary>
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
            // **NOT AVAILABLE ON A BENCH DOING ITS DAY JOB.** Owner: *"can toggle between normal
            // op and gate op depending whats wanted"*. The two modes are exclusive in both
            // directions: gate control suspends the ordinary bills, and normal operation withdraws
            // the gate recipe.
            return gate != null && !gate.AssemblyComplete && console.IsGateControl;
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
