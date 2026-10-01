using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimroomsAsyncIndustries.Gate;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    public sealed partial class MainTabWindow_Operations
    {
        private Thing nativeBindingGate;
        private Thing nativeConsoleChoice;
        private Thing nativeBatteryChoice;
        private Thing nativeAssemblyBenchChoice;
        private bool nativeOppositeEntrySideChoice;

        private void DrawNativeGateBinding(Listing_Standard listing, RimroomsCampaignComponent campaign)
        {
            listing.Label("RR_NativeGate_Heading".Translate());
            listing.Label("RR_NativeGate_Explanation".Translate());
            if (campaign?.HasBranch == true && campaign.Headquarters != null)
            { listing.Label("RR_NativeGate_HQContext".Translate(campaign.BranchId, campaign.Headquarters.uniqueID)); }

            RimroomsExpeditionComponent expeditions = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsExpeditionComponent>();
            ExpeditionRecord activeRun = expeditions == null ? null : expeditions.Active;
            CompRimroomsGate gate = null;

            if (activeRun != null)
            {
                Thing recordedGate = activeRun.Gate;
                gate = recordedGate == null ? null : recordedGate.TryGetComp<CompRimroomsGate>();
                if (gate == null)
                {
                    listing.Label("RR_NativeGate_RecordedGateUnavailable".Translate(activeRun.ExpeditionId));
                    listing.GapLine();
                    return;
                }

                selectedGate = recordedGate;
                SetNativeBindingTarget(gate, gate.IsOpening);
                listing.Label("RR_NativeGate_RecordedRunGate".Translate(activeRun.ExpeditionId,
                    recordedGate.LabelCap, recordedGate.Position));
            }
            else
            {
                if (campaign == null || campaign.Headquarters == null)
                {
                    listing.Label("RR_NativeGate_NoHeadquarters".Translate());
                    listing.GapLine();
                    return;
                }

                if (listing.ButtonText("RR_NativeGate_SelectDoor".Translate())) { OpenNativeDoorMenu(campaign); }
                gate = CurrentGate(campaign);
                if (gate == null)
                {
                    listing.Label("RR_NativeGate_NoSelectedGate".Translate());
                    listing.Label("RR_NativeGate_AvailableDoorCount".Translate(AvailableNativeDoors(campaign).Count()));
                    listing.GapLine();
                    return;
                }
                SetNativeBindingTarget(gate);
                listing.Label("RR_NativeGate_SelectedDoor".Translate(gate.parent.LabelCap,
                    gate.parent.def.defName, gate.parent.Position));
            }

            if (gate.parent.Spawned && listing.ButtonText("RR_NativeGate_InspectGate".Translate()))
            { CameraJumper.TryJumpAndSelect(gate.parent); }
            DrawNativeRoleChoice(listing, "RR_NativeGate_ConsoleRole", "RR_NativeGate_ChooseConsole",
                nativeConsoleChoice, AvailableNativeConsoles(campaign));
            DrawNativeRoleChoice(listing, "RR_NativeGate_BatteryRole", "RR_NativeGate_ChooseBattery",
                nativeBatteryChoice, AvailableNativeBatteries(campaign));
            DrawNativeRoleChoice(listing, "RR_NativeGate_AssemblyBenchRole", "RR_NativeGate_ChooseAssemblyBench",
                nativeAssemblyBenchChoice, AvailableNativeAssemblyBenches(campaign));

            bool sameGateHasOpenRun = activeRun != null && activeRun.Gate == gate.parent;
            if (sameGateHasOpenRun)
            {
                nativeOppositeEntrySideChoice = gate.OppositeEntrySide;
                listing.Label("RR_NativeGate_EntrySideLocked".Translate(
                    (gate.OppositeEntrySide ? "RR_NativeGate_OppositeSide" : "RR_NativeGate_StandardSide").Translate()));
            }
            else
            {
                listing.CheckboxLabeled("RR_NativeGate_OppositeEntrySide".Translate(), ref nativeOppositeEntrySideChoice);
            }

            listing.Label(gate.IsDesignated ? "RR_NativeGate_Designated".Translate() : "RR_NativeGate_NotDesignated".Translate());
            if (gate.Console != null)
            {
                listing.Label("RR_NativeGate_LinkedConsole".Translate(gate.Console.LabelCap, gate.Console.Position));
                if (gate.Console.Spawned && listing.ButtonText("RR_NativeGate_InspectConsole".Translate()))
                { CameraJumper.TryJumpAndSelect(gate.Console); }
            }
            if (gate.LinkedBattery != null)
            {
                listing.Label("RR_NativeGate_LinkedBattery".Translate(gate.LinkedBattery.LabelCap, gate.LinkedBattery.Position));
                if (gate.LinkedBattery.Spawned && listing.ButtonText("RR_NativeGate_InspectBattery".Translate()))
                { CameraJumper.TryJumpAndSelect(gate.LinkedBattery); }
            }
            if (gate.AssemblyBench != null)
            {
                listing.Label("RR_NativeGate_LinkedAssemblyBench".Translate(gate.AssemblyBench.LabelCap, gate.AssemblyBench.Position));
                if (gate.AssemblyBench.Spawned && listing.ButtonText("RR_NativeGate_InspectAssemblyBench".Translate()))
                { CameraJumper.TryJumpAndSelect(gate.AssemblyBench); }
            }

            string inspect = gate.CompInspectStringExtra();
            if (!string.IsNullOrEmpty(inspect)) { listing.Label(inspect); }
            listing.Label("RR_NativeGate_SharedBatteryWarning".Translate());
            listing.Label("RR_NativeGate_DoorStateExplanation".Translate());
            if (gate.HasNativeEnergyDebitFault)
            {
                listing.Label("RR_NativeGate_DebitFaultDetails".Translate(gate.NativeDebitOperationId ?? "?",
                    gate.NativeDebitRequestedWattDays.ToString("F4"), gate.NativeDebitObservedWattDays.ToString("F4")));
                listing.Label("RR_NativeGate_DebitFaultExplanation".Translate());
                if (listing.ButtonText("RR_NativeGate_AcknowledgeDebit".Translate()))
                { ShowResult(gate.AcknowledgeNativeEnergyDebit()); }
            }
            if (gate.NativeBindingFailureKey != null) { listing.Label(gate.NativeBindingFailureKey.Translate()); }

            if (!gate.IsOpening && nativeConsoleChoice != null && nativeBatteryChoice != null && nativeAssemblyBenchChoice != null &&
                listing.ButtonText((gate.IsDesignated ? "RR_NativeGate_SaveBinding" : "RR_NativeGate_DesignateGate").Translate()))
            {
                ShowResult(gate.BindNativeInfrastructure(nativeConsoleChoice, nativeBatteryChoice,
                    nativeAssemblyBenchChoice, nativeOppositeEntrySideChoice));
            }
            else if (gate.IsOpening)
            {
                listing.Label("RR_NativeGate_OpeningCannotRebind".Translate());
            }

            if (activeRun == null && gate.IsDesignated && listing.ButtonText("RR_NativeGate_ClearBinding".Translate()))
            { ShowResult(gate.ClearNativeBinding()); }
            listing.GapLine();
        }

        private void SetNativeBindingTarget(CompRimroomsGate gate, bool refreshSavedLinks = false)
        {
            if (gate == null || (nativeBindingGate == gate.parent && !refreshSavedLinks)) { return; }
            nativeBindingGate = gate.parent;
            nativeConsoleChoice = gate.Console;
            nativeBatteryChoice = gate.LinkedBattery;
            nativeAssemblyBenchChoice = gate.AssemblyBench;
            nativeOppositeEntrySideChoice = gate.OppositeEntrySide;
        }

        private static IEnumerable<Building_Door> AvailableNativeDoors(RimroomsCampaignComponent campaign)
        {
            if (campaign?.Headquarters == null) { return Enumerable.Empty<Building_Door>(); }
            return campaign.Headquarters.listerBuildings.allBuildingsColonist.OfType<Building_Door>()
                .Where(door => door != null && door.Spawned && door.Map == campaign.Headquarters &&
                    door.Faction == Faction.OfPlayer && (door.def.defName == "Door" || door.def.defName == "Autodoor") &&
                    door.TryGetComp<CompRimroomsGate>() != null)
                .OrderBy(door => door.def.defName).ThenBy(door => door.Position.x).ThenBy(door => door.Position.z)
                .ThenBy(door => door.thingIDNumber).ToList();
        }

        internal static IEnumerable<Thing> AvailableNativeConsoles(RimroomsCampaignComponent campaign)
        {
            return AvailableNativeBuildings(campaign, "CommsConsole")
                .Where(thing => thing is Building_CommsConsole && thing.TryGetComp<CompRimroomsGateConsole>() != null);
        }

        internal static IEnumerable<Thing> AvailableNativeBatteries(RimroomsCampaignComponent campaign)
        {
            return AvailableNativeBuildings(campaign, "Battery")
                .Where(thing => thing.TryGetComp<CompPowerBattery>() != null);
        }

        internal static IEnumerable<Thing> AvailableNativeAssemblyBenches(RimroomsCampaignComponent campaign)
        {
            return AvailableNativeBuildings(campaign, "TableMachining")
                .Where(thing => thing is Building_WorkTable && thing.TryGetComp<CompRimroomsGateConsole>() != null);
        }

        /// <summary>
        /// The one candidate of a kind, or null when there is none or more than one.
        ///
        /// **The door toggle's whole contract.** A branch with exactly one console, one battery
        /// and one machining table -- which is every start this mod ships -- can be switched on
        /// from the door. Anything ambiguous is refused by name and chosen in this pane instead,
        /// because picking one of several on the player's behalf is a decision, not a shortcut.
        /// </summary>
        internal static Thing SoleCandidate(IEnumerable<Thing> candidates)
        {
            Thing only = null;
            foreach (Thing candidate in candidates)
            {
                if (only != null) { return null; }
                only = candidate;
            }
            return only;
        }

        private static IEnumerable<Thing> AvailableNativeBuildings(RimroomsCampaignComponent campaign, string defName)
        {
            if (campaign?.Headquarters == null) { return Enumerable.Empty<Thing>(); }
            return campaign.Headquarters.listerBuildings.allBuildingsColonist
                .Where(building => building != null && building.Spawned && building.Map == campaign.Headquarters &&
                    building.Faction == Faction.OfPlayer && building.def.defName == defName)
                .OrderBy(building => building.Position.x).ThenBy(building => building.Position.z)
                .ThenBy(building => building.thingIDNumber).Cast<Thing>().ToList();
        }

        private void OpenNativeDoorMenu(RimroomsCampaignComponent campaign)
        {
            List<FloatMenuOption> options = AvailableNativeDoors(campaign).Select(door =>
            {
                Building_Door captured = door;
                return new FloatMenuOption("RR_NativeGate_DoorOption".Translate(captured.LabelCap,
                    captured.def.defName, captured.Position), delegate
                {
                    selectedGate = captured;
                    SetNativeBindingTarget(captured.TryGetComp<CompRimroomsGate>());
                });
            }).ToList();
            if (options.Count == 0)
            {
                Messages.Message("RR_NativeGate_NoDoorCandidates".Translate(), MessageTypeDefOf.RejectInput, false);
                return;
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        private void DrawNativeRoleChoice(Listing_Standard listing, string roleKey, string chooseKey,
            Thing choice, IEnumerable<Thing> candidates)
        {
            string value = choice == null ? "RR_NativeGate_Unselected".Translate().ToString()
                : "RR_NativeGate_RoleValue".Translate(choice.LabelCap, choice.def.defName, choice.Position).ToString();
            listing.Label(roleKey.Translate(value));
            if (listing.ButtonText(chooseKey.Translate())) { OpenNativeRoleMenu(chooseKey, candidates, SetRoleChoiceAction(chooseKey)); }
            if (choice != null && choice.Spawned && listing.ButtonText("RR_NativeGate_InspectRole".Translate(choice.LabelCap)))
            { CameraJumper.TryJumpAndSelect(choice); }
        }

        private Action<Thing> SetRoleChoiceAction(string roleKey)
        {
            if (roleKey == "RR_NativeGate_ChooseConsole") { return thing => nativeConsoleChoice = thing; }
            if (roleKey == "RR_NativeGate_ChooseBattery") { return thing => nativeBatteryChoice = thing; }
            return thing => nativeAssemblyBenchChoice = thing;
        }

        private static void OpenNativeRoleMenu(string roleKey, IEnumerable<Thing> candidates, Action<Thing> select)
        {
            List<FloatMenuOption> options = candidates.Select(candidate =>
            {
                Thing captured = candidate;
                return new FloatMenuOption("RR_NativeGate_RoleOption".Translate(captured.LabelCap,
                    captured.def.defName, captured.Position), delegate { select(captured); });
            }).ToList();
            if (options.Count == 0)
            {
                Messages.Message("RR_NativeGate_NoRoleCandidates".Translate(roleKey.Translate()), MessageTypeDefOf.RejectInput, false);
                return;
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }
    }
}
