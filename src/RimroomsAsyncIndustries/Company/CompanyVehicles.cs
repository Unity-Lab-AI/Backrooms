using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// **Company vehicles and gravships, mapped onto what the providers already do.**
    ///
    /// Nothing here is a vehicle system. Every action hands the player to the provider's own
    /// surface, or refuses with a reason, and the package still loads, runs and saves with every
    /// provider absent: there is no compile-time reference to Vehicle Framework, Vanilla Vehicles
    /// Expanded or either gravship chapter.
    ///
    /// | Promised action | Native behaviour it maps to | When it is refused |
    /// |---|---|---|
    /// | Load a company vehicle as a cargo carrier | Vehicle Framework's own `Vehicles.Dialog_LoadCargo(VehiclePawn)` | framework absent, vehicle not ours or not on a company map, dialog type missing |
    /// | Send vehicles out to a company site | The vanilla caravan dialog, which Vehicle Framework itself patches to take vehicles | framework absent, map not a company surface map |
    /// | Drive a vehicle through the gate | **Nothing.** Vehicle Framework has no map-portal path: its assembly names no `MapPortal` type and a vehicle is not a pawn the portal's own loading accepts | always |
    /// | Launch a gravship from a company site | Odyssey's own grav engine, selected so its launch gizmo is in front of the player | Odyssey absent, map is a pocket map (a Backrooms space), no engine on the map |
    ///
    /// Vanilla Vehicles Expanded and both gravship chapters add content to those two native
    /// systems and expose no launch, cargo or mission API of their own, so they need no branch
    /// here; their presence is reported by <see cref="Core.InstalledIntegrations"/>.
    ///
    /// Type lookup is by full name through `GenTypes`, cached once per type, and a type that is
    /// not found is the refusal rather than an exception.
    /// </summary>
    public static class CompanyVehicles
    {
        private const int VehicleFrameworkRow = 11;
        private const string VehiclePawnTypeName = "Vehicles.VehiclePawn";
        private const string LoadCargoDialogTypeName = "Vehicles.Dialog_LoadCargo";

        private static bool typesResolved;
        private static Type vehiclePawnType;
        private static Type loadCargoDialogType;

        private static void ResolveTypes()
        {
            if (typesResolved) { return; }
            typesResolved = true;
            try
            {
                vehiclePawnType = GenTypes.GetTypeInAnyAssembly(VehiclePawnTypeName);
                loadCargoDialogType = GenTypes.GetTypeInAnyAssembly(LoadCargoDialogTypeName);
            }
            catch (Exception exception)
            {
                vehiclePawnType = null;
                loadCargoDialogType = null;
                Log.Warning("[Rimrooms] Vehicle Framework types could not be resolved: " + exception.Message);
            }
        }

        /// <summary>Whether Vehicle Framework is loaded and its vehicle type was found.</summary>
        public static bool FrameworkAvailable
        {
            get
            {
                if (!Core.InstalledIntegrations.ActiveRow(VehicleFrameworkRow)) { return false; }
                ResolveTypes();
                return vehiclePawnType != null;
            }
        }

        /// <summary>Whether a pawn is one of the framework's vehicles. False with it absent.</summary>
        public static bool IsVehicle(Pawn pawn)
        {
            if (pawn == null || !FrameworkAvailable) { return false; }
            return vehiclePawnType.IsInstanceOfType(pawn);
        }

        /// <summary>
        /// The player's own vehicles standing on one map, in load-id order so the list does not
        /// reshuffle between frames. Empty with the framework absent.
        /// </summary>
        public static List<Pawn> VehiclesOn(Map map)
        {
            var found = new List<Pawn>();
            if (map == null || !FrameworkAvailable) { return found; }
            IReadOnlyList<Pawn> spawned = map.mapPawns.AllPawnsSpawned;
            for (int index = 0; index < spawned.Count; index++)
            {
                Pawn pawn = spawned[index];
                if (pawn != null && pawn.Faction == Faction.OfPlayer && vehiclePawnType.IsInstanceOfType(pawn))
                { found.Add(pawn); }
            }
            found.Sort((left, right) => string.CompareOrdinal(left.ThingID, right.ThingID));
            return found;
        }

        /// <summary>Mass a vehicle is already carrying, by the game's own inventory reckoning.</summary>
        public static float CarriedMass(Pawn vehicle)
        {
            return vehicle == null ? 0f : MassUtility.InventoryMass(vehicle);
        }

        /// <summary>
        /// A company surface map: the headquarters, or any player home that is not a pocket map.
        /// Backrooms spaces are pocket maps; vehicles and gravships stay out of them.
        /// </summary>
        public static bool IsCompanySurface(RimroomsCampaignComponent campaign, Map map)
        {
            if (campaign == null || !campaign.CanOperate || map == null || map.IsPocketMap) { return false; }
            return map == campaign.Headquarters || map.IsPlayerHome;
        }

        /// <summary>Opens the framework's own cargo dialog for one company vehicle.</summary>
        public static CompanyActionResult OpenCargo(RimroomsCampaignComponent campaign, Pawn vehicle)
        {
            if (!FrameworkAvailable) { return CompanyActionResult.Refused("RR_Vehicle_FrameworkAbsent"); }
            if (vehicle == null || vehicle.Destroyed || !vehicle.Spawned || !IsVehicle(vehicle) ||
                vehicle.Faction != Faction.OfPlayer)
            { return CompanyActionResult.Refused("RR_Vehicle_NotCompanyVehicle"); }
            if (!IsCompanySurface(campaign, vehicle.Map)) { return CompanyActionResult.Refused("RR_Vehicle_NotCompanyMap"); }
            if (loadCargoDialogType == null || !typeof(Window).IsAssignableFrom(loadCargoDialogType))
            { return CompanyActionResult.Refused("RR_Vehicle_CargoDialogMissing"); }
            Window dialog;
            try { dialog = Activator.CreateInstance(loadCargoDialogType, vehicle) as Window; }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms] Vehicle Framework cargo dialog refused to open: " + exception.Message);
                return CompanyActionResult.Refused("RR_Vehicle_CargoDialogMissing");
            }
            if (dialog == null) { return CompanyActionResult.Refused("RR_Vehicle_CargoDialogMissing"); }
            Find.WindowStack.Add(dialog);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Opens the vanilla caravan dialog for a company map. Vehicle Framework patches that
        /// dialog itself to list vehicles, so this is the framework's own formation path.
        /// </summary>
        public static CompanyActionResult OpenCaravanFormation(RimroomsCampaignComponent campaign, Map map)
        {
            if (!FrameworkAvailable) { return CompanyActionResult.Refused("RR_Vehicle_FrameworkAbsent"); }
            if (!IsCompanySurface(campaign, map)) { return CompanyActionResult.Refused("RR_Vehicle_NotCompanyMap"); }
            if (VehiclesOn(map).Count == 0) { return CompanyActionResult.Refused("RR_Vehicle_NoneHere"); }
            Find.WindowStack.Add(new Dialog_FormCaravan(map));
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Always refused, with the reason. The gate is entered on foot: Vehicle Framework has
        /// no portal path, and inventing one would mean moving a vehicle through a map portal
        /// that never loads one.
        /// </summary>
        public static CompanyActionResult ThroughGate()
        {
            return CompanyActionResult.Refused(FrameworkAvailable
                ? "RR_Vehicle_GateRefused" : "RR_Vehicle_FrameworkAbsent");
        }

        /// <summary>The first spawned grav engine on a map, or null.</summary>
        public static Building_GravEngine GravEngineOn(Map map)
        {
            if (map == null || !ModsConfig.OdysseyActive) { return null; }
            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            for (int index = 0; index < buildings.Count; index++)
            {
                if (buildings[index] is Building_GravEngine engine && engine.Spawned) { return engine; }
            }
            return null;
        }

        /// <summary>
        /// Puts the grav engine on a company site in front of the player, selected, so the launch
        /// is Odyssey's own gizmo with every one of its own checks. Nothing here launches.
        /// </summary>
        public static CompanyActionResult SelectGravEngine(RimroomsCampaignComponent campaign, Map map)
        {
            if (!ModsConfig.OdysseyActive) { return CompanyActionResult.Refused("RR_Gravship_OdysseyAbsent"); }
            if (map != null && map.IsPocketMap) { return CompanyActionResult.Refused("RR_Gravship_PocketMap"); }
            if (!IsCompanySurface(campaign, map)) { return CompanyActionResult.Refused("RR_Vehicle_NotCompanyMap"); }
            Building_GravEngine engine = GravEngineOn(map);
            if (engine == null) { return CompanyActionResult.Refused("RR_Gravship_NoEngine"); }
            CameraJumper.TryJumpAndSelect(engine);
            return CompanyActionResult.Applied();
        }
    }
}
