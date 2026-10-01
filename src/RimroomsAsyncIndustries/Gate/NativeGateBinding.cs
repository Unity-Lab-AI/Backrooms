using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>Opt-in provider binding. Native objects retain ownership of their energy and behavior.</summary>
    public sealed partial class CompRimroomsGate
    {
        private int nativeBindingSchema = 1;
        private bool nativeDesignated;
        private string nativeBranchId;
        private Thing nativeConsole;
        private Thing nativeBattery;
        private Thing nativeAssemblyBench;
        private bool nativeOppositeEntrySide;
        private IntVec3 nativeBoundPosition = IntVec3.Invalid;
        private int nativeBoundRotation;
        private int nativeLastProcessedTick = -1;
        private double nativeEnergyDrawnWattDays;
        private int nativeOpeningSequence;
        private NativeEnergyDebitFault nativeEnergyDebit;
        private List<NativeEnergyDebitFault> nativeDebitHistory = new List<NativeEnergyDebitFault>();

        /// <summary>
        /// This door is an operable gate.
        ///
        /// **False for a run extension**, which is what keeps invariant 32 true: exactly one way a
        /// laboratory gate opens, and every entry point routes into it. An extension has no
        /// spin-up, no address, no console, no window and no operator, because as far as every
        /// other system in this mod is concerned it is not a gate -- it is part of one.
        /// </summary>
        public bool IsDesignated
        {
            get
            {
                return !IsRunExtension && NativeDoorProvider() &&
                    nativeBindingSchema == 1 && nativeDesignated;
            }
        }
        public bool OppositeEntrySide { get { return nativeOppositeEntrySide; } }
        public Thing LinkedBattery { get { return nativeBattery; } }
        public Thing AssemblyBench { get { return nativeAssemblyBench; } }
        /// <summary>
        /// The bound communications console. Exposed so the operations window can say **which**
        /// component is still in normal operation, rather than leaving the player to find a
        /// switch they were never told about -- see `MainTabWindow_Operations.GateOpeningBlockers`.
        /// </summary>
        public Thing LinkedConsole { get { return nativeConsole; } }
        public float NativeEnergyRequiredToOpenWattDays
        {
            get { return GateProps.openingWindowTicks * OpeningPowerDrawWatts * CompPower.WattsToWattDaysPerTick
                + GateProps.emergencyReturnCostWattDays; }
        }
        public float RecoveryEnergyRequiredWattDays
        { get { return NativeEnergyRequiredToOpenWattDays + GateProps.recoveryOpeningCostWattDays; } }
        public double NativeEnergyDrawnWattDays { get { return nativeEnergyDrawnWattDays; } }
        public bool HasNativeEnergyDebitFault { get { return nativeEnergyDebit != null && !nativeEnergyDebit.Acknowledged; } }
        public string NativeDebitOperationId { get { return nativeEnergyDebit?.OperationId; } }
        public float NativeDebitRequestedWattDays { get { return nativeEnergyDebit == null ? 0f : nativeEnergyDebit.Requested; } }
        public float NativeDebitObservedWattDays { get { return nativeEnergyDebit == null ? 0f : nativeEnergyDebit.Observed; } }
        public string NativeBindingFailureKey
        {
            get
            {
                string failure = NativePhysicalLinkFailure();
                if (failure != null) { return failure; }
                // A thrown cutoff is reported ahead of the generic power failure for the same
                // reason the tick checks it first: the player needs to know the switch is the
                // reason, not a fault somewhere in the wiring.
                if (KillSwitchThrown) { return "RR_NativeGate_KillSwitchThrown"; }
                // A lapsed assembly blocks the next opening. It never closes one already
                // running: ending an opening for a bookkeeping reason would strand whoever
                // is on the far side, and the return window is for real emergencies.
                if (ServiceLapsed) { return "RR_NativeGate_ServiceLapsed"; }
                if (HasNativeEnergyDebitFault) { return "RR_NativeGate_EnergyDebitFault"; }
                if (!NativePowerConnected()) { return "RR_NativeGate_Disconnected"; }
                if (!NativeElectricalAvailable() || !IsConsolePowered(nativeConsole) ||
                    (powerTrader != null && !powerTrader.PowerOn))
                { return "RR_NativeGate_PowerUnavailable"; }
                return null;
            }
        }

        private CompPowerBattery NativeBatteryComp
        { get { return nativeBattery == null || nativeBattery.Destroyed ? null : nativeBattery.TryGetComp<CompPowerBattery>(); } }
        private float NativeStoredEnergy
        {
            get
            {
                CompPowerBattery battery = NativeBatteryComp;
                return battery == null || !FiniteNonnegative(battery.StoredEnergy) ? 0f : battery.StoredEnergy;
            }
        }
        private float NativeBatteryCapacity
        {
            get
            {
                CompPowerBattery battery = NativeBatteryComp;
                return battery == null || !FiniteNonnegative(battery.Props.storedEnergyMax) ? 0f : battery.Props.storedEnergyMax;
            }
        }
        private IntVec3 NativeEntryCell
        {
            get
            {
                if (!IsDesignated || !parent.Spawned || parent.Position != nativeBoundPosition) { return IntVec3.Invalid; }
                // Core changes a one-cell door's Rotation in DoorPreDraw. A camera draw must not
                // retarget or invalidate the saved expedition approach; use its bound orientation.
                Rot4 orientation = new Rot4(nativeBoundRotation);
                return nativeBoundPosition + (nativeOppositeEntrySide ? orientation.FacingCell : orientation.Opposite.FacingCell);
            }
        }
        private IntVec3 EntrySideCell(bool opposite)
        { return parent.Position + (opposite ? parent.Rotation.FacingCell : parent.Rotation.Opposite.FacingCell); }

        private RimroomsCampaignComponent NativeCampaign
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }

        /// <summary>
        /// Whether this thing is player-owned infrastructure standing **on the same map as the
        /// gate**, at a place the branch operates.
        ///
        /// **Arc 5's exit plan.** This used to require `parent.Map == campaign.Headquarters`, so a
        /// gate could only ever be designated at the headquarters and the arc's *"exit plan"* was
        /// unreachable however many sites a branch held. It now asks
        /// <see cref="RimroomsCampaignComponent.OperatesAt"/>: the headquarters, or a site on the
        /// books.
        ///
        /// **A Backrooms coordinate is still excluded**, because a coordinate can never be
        /// registered as a site. What is down there is a natural gate — no operator, no power, no
        /// address book — and invariant 12 keeps it that way without a second check to forget.
        ///
        /// **The `thing.Map == parent.Map` clause is untouched, and it is the good consequence.**
        /// A gate at a remote site needs its own console, its own bound battery and its own
        /// assembly bench **at that site**. You cannot run a gate at the far end of the world off
        /// the equipment in your headquarters, which is exactly what *"remote sites need people,
        /// supplies, signals, protection, and an exit plan"* is asking for.
        ///
        /// The name is kept. Eleven call sites read it as "the branch's own infrastructure, here",
        /// which is what it has always meant and still means; only the set of valid "here"s grew.
        /// </summary>
        private bool SameNativeHeadquartersThing(Thing thing)
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            return campaign != null && campaign.CanOperate && campaign.OperatesAt(parent.Map) &&
                parent.Spawned && parent.Faction == Faction.OfPlayer &&
                thing != null && !thing.Destroyed && thing.Spawned && thing.Map == parent.Map && thing.Faction == Faction.OfPlayer;
        }

        private static bool ExactProvider(Thing thing, string definition)
        { return thing != null && thing.def != null && thing.def.defName == definition; }

        /// <summary>
        /// A door this mod is prepared to operate as a gate.
        ///
        /// This used to name Core `Door` and `Autodoor` explicitly. It no longer needs to:
        /// the component is only ever attached by this mod's own patches, so **carrying the
        /// component is the allowlist**, and the patch file is where the supported providers
        /// are declared. What still has to be checked here is the shape, because the
        /// capability ladder is defined for four footprints and nothing else.
        /// </summary>
        /// <summary>
        /// Whether this door can be a gate at all.
        ///
        /// The footprint tested is the **run's**, not the def's, so three adjacent ordinary doors
        /// bound together are a legal 1x3 and any one of them alone is a legal 1x1. A door whose
        /// own def is already a legal shape stays legal with no run, which is every gate that has
        /// never been extended.
        ///
        /// An **extension** is deliberately still a provider by this test -- it is a door of a
        /// legal shape. What stops it being operated is `IsDesignated`, which refuses it outright.
        /// </summary>
        private bool NativeDoorProvider()
        {
            if (!(parent is Building_Door) || parent.def == null) { return false; }
            if (LegalGateFootprint(parent.def.size)) { return true; }
            CellRect run = RunRect;
            return run.Area > 0 && LegalGateFootprint(new IntVec2(run.Width, run.Height));
        }

        private bool HasUnresolvedNativeTrip()
        {
            RimroomsExpeditionComponent expeditions = Current.Game?.GetComponent<RimroomsExpeditionComponent>();
            return expeditions != null && expeditions.Records.Any(r => r != null && r.Gate == parent && !r.Closed);
        }

        /// <summary>Validate every new link before mutating. Binding never grants material work or charge.</summary>
        public CompanyActionResult BindNativeInfrastructure(Thing console, Thing battery, Thing assemblyBench,
            bool oppositeEntrySide = false)
        {
            if (!NativeDoorProvider()) { return RefuseNative("UnsupportedProvider"); }
            if (nativeBindingSchema != 1) { return RefuseNative("UnknownSchema"); }
            if (IsOpening) { return RefuseNative("ActiveCannotRebind"); }
            // Owner direction 2026-09-29: "gate doors expansions can NOT be done on a
            // working gate". A ramp is the gate working, so it counts.
            if (IsSpinningUp) { return RefuseNative("ActiveCannotRebind"); }
            if (HasNativeEnergyDebitFault) { return RefuseNative("EnergyDebitFault"); }
            if (!SameNativeHeadquartersThing(console) || !SameNativeHeadquartersThing(battery) ||
                !SameNativeHeadquartersThing(assemblyBench)) { return RefuseNative("HeadquartersRequired"); }
            if (!string.IsNullOrEmpty(nativeBranchId) && nativeBranchId != NativeCampaign.BranchId)
            { return RefuseNative("HeadquartersRequired"); }
            if (!ExactProvider(console, "CommsConsole") || !(console is Building_CommsConsole) ||
                !ExactProvider(battery, "Battery") || battery.TryGetComp<CompPowerBattery>() == null ||
                !ExactProvider(assemblyBench, "TableMachining") || !(assemblyBench is Building_WorkTable))
            { return RefuseNative("UnsupportedProvider"); }

            // **`returnReserveCapacityWattDays` wired in 0.11.5-dev** as the thing its name always
            // read like: the smallest reserve a gate will accept. It had been declared and read by
            // nothing, which made it a job nobody finished rather than a value nobody wanted.
            //
            // A battery too small to hold an emergency return is not a reserve, and binding one
            // would produce a gate that looks complete and strands the first crew through it. The
            // refusal happens here, at the moment somebody chooses the battery, rather than as a
            // surprise at the threshold.
            CompPowerBattery reserve = battery.TryGetComp<CompPowerBattery>();
            if (reserve.Props == null || !FiniteNonnegative(reserve.Props.storedEnergyMax) ||
                reserve.Props.storedEnergyMax < GateProps.returnReserveCapacityWattDays)
            { return RefuseNative("ReserveTooSmall"); }
            IntVec3 entry = EntrySideCell(oppositeEntrySide);
            if (!entry.InBounds(parent.Map) || !entry.Standable(parent.Map)) { return RefuseNative("EntryBlocked"); }
            if (HasUnresolvedNativeTrip() && (nativeOppositeEntrySide != oppositeEntrySide ||
                nativeBoundPosition != parent.Position || nativeBoundRotation != parent.Rotation.AsInt))
            { return RefuseNative("EntryLocked"); }
            CompRimroomsGateConsole station = console.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGateConsole workshop = assemblyBench.TryGetComp<CompRimroomsGateConsole>();
            if (station == null || workshop == null || !station.CanBindToGate(parent) || !workshop.CanBindToGate(parent))
            { return RefuseNative("ProviderAlreadyBound"); }
            foreach (Building building in parent.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGate other = building.TryGetComp<CompRimroomsGate>();
                if (other != null && other != this && other.nativeDesignated &&
                    (other.nativeBattery == battery || other.nativeConsole == console || other.nativeAssemblyBench == assemblyBench))
                { return RefuseNative("ProviderAlreadyBound"); }
            }
            CompRimroomsGateConsole oldStation = nativeConsole?.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGateConsole oldWorkshop = nativeAssemblyBench?.TryGetComp<CompRimroomsGateConsole>();
            if (station.HasAssemblyJob || workshop.HasAssemblyJob ||
                (oldStation != null && oldStation.HasAssemblyJob) || (oldWorkshop != null && oldWorkshop.HasAssemblyJob))
            { return RefuseNative("AssemblyInProgress"); }
            if (nativeDesignated && nativeConsole == console && nativeBattery == battery &&
                nativeAssemblyBench == assemblyBench && nativeOppositeEntrySide == oppositeEntrySide &&
                nativeBoundPosition == parent.Position && nativeBoundRotation == parent.Rotation.AsInt &&
                station.LinkedGate == parent && workshop.LinkedGate == parent)
            {
                // The same explicit action may repair a missing bill after an interrupted UI operation.
                return EnsureNativeAssemblyBill(workshop, true);
            }

            // New providers are linked before old providers are detached; every method is a synchronous local mutation.
            bool stationWasLinked = station.LinkedGate == parent;
            bool workshopWasLinked = workshop.LinkedGate == parent;
            bool oldStationCleared = false;
            bool oldWorkshopCleared = false;
            try
            {
                if (!station.BindToGate(parent) || !workshop.BindToGate(parent))
                { throw new InvalidOperationException("Native provider refused a preflighted gate binding."); }
                if (oldStation != null && oldStation != station && oldStation.LinkedGate == parent)
                {
                    oldStationCleared = oldStation.ClearNativeBinding(parent);
                    if (!oldStationCleared) { throw new InvalidOperationException("Prior console refused unlink."); }
                }
                if (oldWorkshop != null && oldWorkshop != workshop && oldWorkshop.LinkedGate == parent)
                {
                    oldWorkshopCleared = oldWorkshop.ClearNativeBinding(parent);
                    if (!oldWorkshopCleared) { throw new InvalidOperationException("Prior workshop refused unlink."); }
                }
            }
            catch (Exception exception)
            {
                if (!stationWasLinked && station.LinkedGate == parent) { station.ClearNativeBinding(parent); }
                if (!workshopWasLinked && workshop.LinkedGate == parent) { workshop.ClearNativeBinding(parent); }
                if (oldStationCleared) { oldStation.BindToGate(parent); }
                if (oldWorkshopCleared) { oldWorkshop.BindToGate(parent); }
                Log.Error("[Rimrooms][Gate] Native binding interrupted; existing gate state retained: " + exception);
                return RefuseNative("BindingInterrupted");
            }
            nativeConsole = console;
            nativeBattery = battery;
            nativeAssemblyBench = assemblyBench;
            nativeBranchId = NativeCampaign.BranchId;
            nativeBoundPosition = parent.Position;
            nativeBoundRotation = parent.Rotation.AsInt;
            nativeOppositeEntrySide = oppositeEntrySide;
            nativeDesignated = true;
            calibrated = false;
            stablePowerTicks = 0;
            // The door is a gate from this moment, so it should look like one from this moment.
            // Core caches a thing's coloured graphic, and this is the one call that drops that
            // cache and redraws the cell.
            if (parent.Spawned) { parent.Notify_ColorChanged(); }
            return EnsureNativeAssemblyBill(workshop, false);
        }

        public CompanyActionResult ClearNativeBinding()
        {
            if (nativeBindingSchema != 1) { return RefuseNative("UnknownSchema"); }
            if (IsOpening || IsSpinningUp || HasUnresolvedNativeTrip()) { return RefuseNative("ActiveCannotRebind"); }
            if (HasNativeEnergyDebitFault) { return RefuseNative("EnergyDebitFault"); }
            if (!nativeDesignated) { return CompanyActionResult.Existing(); }
            CompRimroomsGateConsole station = nativeConsole?.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGateConsole workshop = nativeAssemblyBench?.TryGetComp<CompRimroomsGateConsole>();
            if ((station != null && station.HasAssemblyJob) || (workshop != null && workshop.HasAssemblyJob))
            { return RefuseNative("AssemblyInProgress"); }
            if (station != null && station.LinkedGate == parent && !station.ClearNativeBinding(parent))
            { return RefuseNative("BindingInterrupted"); }
            if (workshop != null && workshop.LinkedGate == parent && !workshop.ClearNativeBinding(parent))
            {
                if (station != null) { station.BindToGate(parent); }
                return RefuseNative("BindingInterrupted");
            }
            nativeDesignated = false;
            nativeConsole = null;
            nativeBattery = null;
            nativeAssemblyBench = null;
            assignedOperator = null;
            calibrated = false;
            stablePowerTicks = 0;
            // Released, so it is an ordinary door again and must read as one immediately.
            if (parent.Spawned) { parent.Notify_ColorChanged(); }
            // Retain paid assembly, branch provenance, bound position and all closed operation receipts.
            return CompanyActionResult.Applied();
        }

        private string NativePhysicalLinkFailure()
        {
            string failure = NativeIdentityLinkFailure();
            if (failure != null) { return failure; }
            if (!NativeEntryCell.IsValid || !NativeEntryCell.InBounds(parent.Map) || !NativeEntryCell.Standable(parent.Map))
            { return "RR_NativeGate_EntryBlocked"; }
            return null;
        }

        private string NativeIdentityLinkFailure()
        {
            if (!NativeDoorProvider()) { return "RR_NativeGate_UnsupportedProvider"; }
            if (nativeBindingSchema != 1) { return "RR_NativeGate_UnknownSchema"; }
            if (!nativeDesignated) { return "RR_NativeGate_NotBound"; }
            if (NativeCampaign == null || nativeBranchId != NativeCampaign.BranchId ||
                !SameNativeHeadquartersThing(nativeConsole) || !SameNativeHeadquartersThing(nativeBattery) ||
                !SameNativeHeadquartersThing(nativeAssemblyBench)) { return "RR_NativeGate_LinkMissing"; }
            if (!ExactProvider(nativeConsole, "CommsConsole") || !ExactProvider(nativeBattery, "Battery") ||
                !ExactProvider(nativeAssemblyBench, "TableMachining") || NativeBatteryComp == null ||
                nativeConsole.TryGetComp<CompRimroomsGateConsole>()?.LinkedGate != parent ||
                nativeAssemblyBench.TryGetComp<CompRimroomsGateConsole>()?.LinkedGate != parent)
            { return "RR_NativeGate_LinkMissing"; }
            return null;
        }

        /// <summary>
        /// What the gate's own circuit is **generating** right now, in watts.
        ///
        /// Only what is actually producing: a generator that is switched off, broken down or out
        /// of fuel contributes nothing, which is the entire point of asking. Stored charge is
        /// deliberately not counted — a battery is not supply, it is a buffer, and the owner's
        /// answer names delivery: *"the gate refuses to open unless its circuit can deliver this
        /// much power"*.
        /// </summary>
        private float NativeGenerationWatts()
        {
            CompPowerBattery battery = NativeBatteryComp;
            PowerNet net = battery == null ? null : battery.PowerNet;
            if (net == null) { return 0f; }
            float total = 0f;
            List<CompPowerTrader> traders = net.powerComps;
            for (int index = 0; index < traders.Count; index++)
            {
                CompPowerTrader trader = traders[index];
                if (trader == null || !trader.PowerOn) { continue; }
                float output = trader.PowerOutput;
                if (output > 0f && !float.IsNaN(output) && !float.IsInfinity(output)) { total += output; }
            }
            return total;
        }

        private bool NativePowerConnected()
        {
            CompPowerBattery battery = NativeBatteryComp;
            CompPowerTrader consolePower = nativeConsole?.TryGetComp<CompPowerTrader>();
            if (battery == null || battery.PowerNet == null || consolePower == null || consolePower.PowerNet != battery.PowerNet)
            { return false; }
            return NativeThresholdConnected();
        }

        private bool NativeThresholdConnected()
        {
            CompPowerBattery battery = NativeBatteryComp;
            if (battery == null || battery.PowerNet == null) { return false; }
            if (ExactProvider(parent, "Autodoor"))
            { return powerTrader != null && powerTrader.PowerNet == battery.PowerNet; }
            // A manual door has no trader. Require an actual live transmitter under its threshold.
            return parent.Position.GetThingList(parent.Map).Any(t =>
            {
                CompPower transmitter = t.TryGetComp<CompPower>();
                return transmitter != null && transmitter.TransmitsPowerNow && transmitter.PowerNet == battery.PowerNet;
            });
        }

        private bool NativeElectricalAvailable()
        {
            CompPowerBattery battery = NativeBatteryComp;
            return battery != null && !battery.StunnedByEMP && !nativeBattery.IsBrokenDown() && !parent.IsBrokenDown() &&
                FlickUtility.WantsToBeOn(parent) && FlickUtility.WantsToBeOn(nativeBattery) &&
                !parent.Map.gameConditionManager.ElectricityDisabled(parent.Map);
        }

        private bool BeginNativeTick()
        {
            if (!NativeDoorProvider()) { return false; }
            if (!nativeDesignated && !IsOpening) { return false; }
            int now = Find.TickManager.TicksGame;
            if (nativeLastProcessedTick == now) { return false; }
            nativeLastProcessedTick = now;
            return true;
        }

        /// <summary>
        /// The standing cost of keeping a designated gate, charged while it is closed. While it
        /// is open the opening draw is charged instead, so the two never stack.
        ///
        /// **`idlePowerDrawWatts` wired in 0.11.5-dev.** It had been declared and read by nothing
        /// since the prop was written, which made it a job nobody finished rather than a value
        /// nobody wanted. Owner direction, verbatim: *"make sure shit isnt unused it was put there
        /// for a reason"*.
        ///
        /// **Never takes the reserve below what an emergency return costs.** That floor is the
        /// difference between a cost and a trap: a player who designates a gate and walks away
        /// should come back to a flat battery, not to a crew that cannot be recovered.
        /// </summary>
        private void SpendIdleDrawTick()
        {
            if (IsOpening || !IsDesignated) { return; }
            // Through the property, never the raw prop: it is the one place research is applied,
            // so what the gate reports drawing and what it actually takes can never diverge.
            float cost = IdlePowerDrawWatts * CompPower.WattsToWattDaysPerTick;
            if (!(cost > 0f) || float.IsNaN(cost) || float.IsInfinity(cost)) { return; }
            CompPowerBattery battery = NativeBatteryComp;
            if (battery == null) { return; }
            if (NativeStoredEnergy - cost < GateProps.emergencyReturnCostWattDays) { return; }
            battery.DrawPower(cost);
        }

        private bool SpendNativeOpeningTick()
        {
            float cost = OpeningPowerDrawWatts * CompPower.WattsToWattDaysPerTick;
            if (NativeStoredEnergy < cost + GateProps.emergencyReturnCostWattDays) { return false; }
            return TrySpendNativeEnergy(cost, false, NativeOpeningDebitId("tick:" + Find.TickManager.TicksGame));
        }

        private string NativeOpeningDebitId(string suffix)
        { return CurrentOpeningId + ":" + nativeOpeningSequence + ":" + suffix; }

        private bool NativeEmergencyCircuitAvailable()
        {
            return NativeDoorProvider() && IsDesignated && NativeCampaign != null && nativeBranchId == NativeCampaign.BranchId &&
                SameNativeHeadquartersThing(nativeBattery) && ExactProvider(nativeBattery, "Battery") &&
                NativeEntryCell.IsValid && NativeEntryCell.InBounds(parent.Map) && NativeEntryCell.Standable(parent.Map) &&
                NativeThresholdConnected() && NativeElectricalAvailable();
        }

        private bool TrySpendNativeEnergy(float amount, bool emergency, string operationId)
        {
            if (!FiniteNonnegative(amount) || amount <= 0f || HasNativeEnergyDebitFault) { return false; }
            if (emergency ? !NativeEmergencyCircuitAvailable() : NativeBindingFailureKey != null) { return false; }
            float paid = 0f;
            if (nativeEnergyDebit != null)
            {
                if (nativeEnergyDebit.OperationId == operationId)
                {
                    if (nativeEnergyDebit.Requested != amount || !FiniteNonnegative(nativeEnergyDebit.Observed)) { return false; }
                    paid = nativeEnergyDebit.Observed;
                }
                else { ArchiveNativeDebit(); }
            }
            float remaining = Math.Max(0f, amount - paid);
            if (remaining <= NativeDebitTolerance(amount)) { ArchiveNativeDebit(); return true; }
            CompPowerBattery battery = NativeBatteryComp;
            if (battery == null || !FiniteNonnegative(battery.StoredEnergy) || battery.StoredEnergy < remaining) { return false; }
            float before = battery.StoredEnergy;
            Exception interrupted = null;
            try { battery.DrawPower(remaining); }
            catch (Exception exception) { interrupted = exception; }
            float observed = before - battery.StoredEnergy;
            bool finiteObserved = FiniteNonnegative(observed);
            if (finiteObserved) { nativeEnergyDrawnWattDays += observed; }
            if (interrupted != null || !finiteObserved || Math.Abs(observed - remaining) > NativeDebitTolerance(before))
            {
                nativeEnergyDebit = new NativeEnergyDebitFault
                {
                    OperationId = operationId, Requested = amount,
                    Observed = finiteObserved ? paid + observed : float.NaN, Acknowledged = false,
                    Tick = Find.TickManager.TicksGame, Battery = nativeBattery
                };
                Log.Warning("[Rimrooms][Gate] Native battery debit requires review; requested " + amount +
                    " Wd, observed " + nativeEnergyDebit.Observed + " Wd, operation " + operationId +
                    (interrupted == null ? "." : ": " + interrupted.Message));
                return false;
            }
            if (nativeEnergyDebit != null) { nativeEnergyDebit.Observed = paid + observed; }
            ArchiveNativeDebit();
            return true;
        }

        // Core stores float energy: accept representational rounding, never a material partial withdrawal.
        private static float NativeDebitTolerance(float magnitude)
        { return Math.Max(0.00001f, Math.Abs(magnitude) * 0.0000002f); }

        public CompanyActionResult AcknowledgeNativeEnergyDebit()
        {
            if (nativeBindingSchema != 1) { return RefuseNative("UnknownSchema"); }
            if (NativeCampaign == null || !NativeCampaign.CanOperate ||
                nativeBranchId != NativeCampaign.BranchId) { return RefuseNative("HeadquartersRequired"); }
            if (nativeEnergyDebit == null || nativeEnergyDebit.Acknowledged) { return CompanyActionResult.Existing(); }
            nativeEnergyDebit.Acknowledged = true;
            // No refill/refund. A retry of the same payment can debit only its unobserved remainder.
            // A later different operation archives this observed loss without crediting it to the new operation.
            return CompanyActionResult.Applied();
        }

        private void ArchiveNativeDebit()
        {
            if (nativeEnergyDebit == null) { return; }
            nativeDebitHistory.Add(nativeEnergyDebit);
            nativeEnergyDebit = null;
            while (nativeDebitHistory.Count > 32) { nativeDebitHistory.RemoveAt(0); }
        }

        private CompanyActionResult EnsureNativeAssemblyBill(CompRimroomsGateConsole workshop, bool existing)
        {
            try
            {
                // **THE BILL IS THE PLAYER'S.** This called `EnsureAssemblyBill`, which added
                // an unsuspended production bill the instant a door was commissioned, so the
                // gate assembled itself with nothing connected and no mission begun. The recipe
                // is on the machining table's own list; the player queues it when they are ready.
                workshop.SyncAssemblyBill();
                if (assemblyComplete) { workshop.MarkAssemblyBillComplete(); }
                return existing ? CompanyActionResult.Existing() : CompanyActionResult.Applied();
            }
            catch (Exception exception)
            {
                Log.Error("[Rimrooms][Gate] Native links retained; explicitly rebind the same installation to retry bill setup: " + exception);
                return RefuseNative("BindingInterrupted");
            }
        }

        private void ExposeNativeBinding()
        {
            Scribe_Values.Look(ref nativeBindingSchema, "rr_nativeGateSchema", 1, true);
            Scribe_Values.Look(ref nativeDesignated, "rr_nativeGateDesignated", false);
            Scribe_Values.Look(ref nativeBranchId, "rr_nativeGateBranch");
            Scribe_References.Look(ref nativeConsole, "rr_nativeGateConsole");
            Scribe_References.Look(ref nativeBattery, "rr_nativeGateBattery");
            Scribe_References.Look(ref nativeAssemblyBench, "rr_nativeGateAssemblyBench");
            Scribe_Values.Look(ref nativeOppositeEntrySide, "rr_nativeGateOppositeSide", false);
            Scribe_Values.Look(ref nativeBoundPosition, "rr_nativeGatePosition", IntVec3.Invalid);
            Scribe_Values.Look(ref nativeBoundRotation, "rr_nativeGateRotation", 0);
            Scribe_Values.Look(ref nativeLastProcessedTick, "rr_nativeGateLastTick", -1);
            Scribe_Values.Look(ref nativeEnergyDrawnWattDays, "rr_nativeGateEnergyDrawn", 0d);
            Scribe_Values.Look(ref nativeOpeningSequence, "rr_nativeGateOpeningSequence", 0);
            Scribe_Deep.Look(ref nativeEnergyDebit, "rr_nativeGateDebitFault");
            Scribe_Collections.Look(ref nativeDebitHistory, "rr_nativeGateDebitHistory", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                nativeDebitHistory = nativeDebitHistory ?? new List<NativeEnergyDebitFault>();
                while (nativeDebitHistory.Count > 32) { nativeDebitHistory.RemoveAt(0); }
            }
        }

        private static bool FiniteNonnegative(float value)
        { return !float.IsNaN(value) && !float.IsInfinity(value) && value >= 0f; }
        private static CompanyActionResult RefuseNative(string suffix)
        { return CompanyActionResult.Refused("RR_NativeGate_" + suffix); }
    }

    public sealed class NativeEnergyDebitFault : IExposable
    {
        public string OperationId;
        public float Requested;
        public float Observed;
        public bool Acknowledged;
        public int Tick;
        public Thing Battery;
        public void ExposeData()
        {
            Scribe_Values.Look(ref OperationId, "operationId");
            Scribe_Values.Look(ref Requested, "requested", 0f);
            Scribe_Values.Look(ref Observed, "observed", 0f);
            Scribe_Values.Look(ref Acknowledged, "acknowledged", false);
            Scribe_Values.Look(ref Tick, "tick", 0);
            Scribe_References.Look(ref Battery, "battery");
        }
    }
}
