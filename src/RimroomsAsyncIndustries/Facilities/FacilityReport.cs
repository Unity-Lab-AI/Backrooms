using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Facilities
{
    /// <summary>RR-FAC: classification is presentation data, never a capability grant.</summary>
    public sealed class RimroomsFacilityCategoryDef : Def
    {
        public List<string> buildingDefNames = new List<string>();
        public bool includePowerSources;

        /// <summary>
        /// Match anything that can hold a contained subject, by **capability** rather than by
        /// name: any building carrying `CompEntityHolder`, plus any bed Core classifies as a
        /// prisoner bed.
        ///
        /// Named defs were the first design and were wrong twice over. `HoldingPlatform` is an
        /// Anomaly defName, so a `<li>` naming it would be read by `check-dlc-gating.py` as an
        /// ungated expansion reference; and a named list covers no modded holder. Matching the
        /// comp covers a modded holder for free, needs no gate at all because
        /// `CompEntityHolder` lives in the always-present base assembly, and on an install
        /// without Anomaly simply matches nothing.
        ///
        /// Prisoner beds are in because containment is not an Anomaly-only idea in this mod: a
        /// branch holding somebody it brought back is a branch with a containment problem, and
        /// on a Core-only install that is the only kind there is.
        /// </summary>
        public bool includeContainment;

        public int displayOrder;

        public bool Matches(Building building)
        {
            if (defName == "RR_Facility_Machine")
            {
                Gate.CompRimroomsGate gate = building.TryGetComp<Gate.CompRimroomsGate>();
                Gate.CompRimroomsGateConsole console = building.TryGetComp<Gate.CompRimroomsGateConsole>();
                if ((gate != null && gate.IsDesignated) || (console != null && console.Gate != null)) { return true; }
            }
            if (includeContainment)
            {
                if (building.TryGetComp<CompEntityHolder>() != null) { return true; }
                var bed = building as Building_Bed;
                if (bed != null && bed.ForPrisoners) { return true; }
            }
            return (buildingDefNames != null && buildingDefNames.Contains(building.def.defName)) || (includePowerSources &&
                (building.TryGetComp<CompPowerPlant>() != null || building.TryGetComp<CompPowerBattery>() != null));
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (buildingDefNames == null || buildingDefNames.Any(string.IsNullOrWhiteSpace))
            { yield return "Facility classification contains an empty building name."; }
        }
    }

    public sealed class FacilityBuildingObservation
    {
        public Building Building;
        public string Label;
        public string CategoryId;
        public string RoomLabel;
        public int RoomCells;
        public int UnroofedCells;
        public bool Outdoors;
        public float Temperature;
        public bool HasRoom;
        public bool? PowerOn;
        public bool? InteractionCellClear;
        public int HitPoints;
        public int MaxHitPoints;
        public string BedTypeKey;
        public int BedSlots;
        public int BedOwners;
        public int BedOccupants;
    }

    /// <summary>Transient HQ observations. No room references, grants, or background ticking.</summary>
    public sealed class FacilityReport
    {
        public Map Map { get; private set; }
        public int CapturedTick { get; private set; } = -1;
        public readonly List<FacilityBuildingObservation> Buildings = new List<FacilityBuildingObservation>();
        public readonly List<string> StaffWithoutOwnedBeds = new List<string>();
        public readonly List<string> StaffNeedingCare = new List<string>();
        public int OrdinaryBedSlots { get; private set; }
        public int OrdinaryBedOwners { get; private set; }
        public int OrdinaryBedOccupants { get; private set; }
        public int MedicalSlots { get; private set; }
        public int OtherBedSlots { get; private set; }
        public int RefreshErrors { get; private set; }

        public static bool Available(Map map)
        { return map != null && Find.Maps != null && Find.Maps.Contains(map); }

        public void RefreshIfNeeded(RimroomsCampaignComponent campaign, bool force = false)
        {
            Map target = campaign.Headquarters;
            int now = Find.TickManager.TicksGame;
            if (!force && target == Map && CapturedTick >= 0 && now >= CapturedTick && now - CapturedTick < 250)
            { return; }
            using (Core.RimroomsDiagnostics.Measure("facilities-summary")) { Capture(campaign, target, now); }
        }

        private void Capture(RimroomsCampaignComponent campaign, Map map, int now)
        {
            Map = map;
            CapturedTick = now;
            Buildings.Clear();
            StaffWithoutOwnedBeds.Clear();
            StaffNeedingCare.Clear();
            OrdinaryBedSlots = OrdinaryBedOwners = OrdinaryBedOccupants = MedicalSlots = OtherBedSlots = RefreshErrors = 0;
            if (!Available(map)) { return; }
            List<RimroomsFacilityCategoryDef> categories = DefDatabase<RimroomsFacilityCategoryDef>.AllDefsListForReading
                .OrderBy(d => d.displayOrder).ThenBy(d => d.defName, StringComparer.Ordinal).ToList();
            foreach (Building building in map.listerBuildings.allBuildingsColonist.ToList())
            {
                if (!Inspectable(building, map)) { continue; }
                try
                {
                    var row = new FacilityBuildingObservation { Building = building, Label = building.LabelCap.ToString(),
                        CategoryId = categories.FirstOrDefault(c => c.Matches(building))?.defName,
                        HitPoints = building.HitPoints, MaxHitPoints = building.MaxHitPoints };
                    Room room = building.GetRoom();
                    if (room != null && !room.Dereferenced)
                    {
                        row.HasRoom = true;
                        row.RoomLabel = room.GetRoomRoleLabel();
                        row.RoomCells = room.CellCount;
                        row.UnroofedCells = room.OpenRoofCount;
                        row.Outdoors = room.UsesOutdoorTemperature;
                        row.Temperature = room.Temperature;
                    }
                    CompPowerTrader power = building.TryGetComp<CompPowerTrader>();
                    if (power != null) { row.PowerOn = power.PowerOn; }
                    if (building.def.hasInteractionCell)
                    {
                        IntVec3 cell = building.InteractionCell;
                        row.InteractionCellClear = cell.InBounds(map) && cell.Standable(map) && !cell.Fogged(map);
                    }
                    Building_Bed bed = building as Building_Bed;
                    if (bed != null) { CaptureBed(row, bed); }
                    Buildings.Add(row);
                }
                catch (Exception)
                {
                    // A modded furniture getter may fail; retain other observations and disclose the gap.
                    RefreshErrors++;
                }
            }
            Buildings.Sort((a, b) => string.Compare(a.Label, b.Label, StringComparison.CurrentCulture));
            foreach (StaffRecord staff in campaign.Staff.Where(s => s.Employed))
            {
                Pawn pawn = staff.Pawn;
                if (pawn == null || pawn.Dead || pawn.Destroyed) { continue; }
                if (pawn.ownership?.OwnedBed == null) { StaffWithoutOwnedBeds.Add(staff.Name); }
                if (pawn.Downed || pawn.health?.hediffSet?.HasNaturallyHealingInjury() == true)
                { StaffNeedingCare.Add(staff.Name); }
            }
        }

        private void CaptureBed(FacilityBuildingObservation row, Building_Bed bed)
        {
            row.BedSlots = bed.SleepingSlotsCount;
            row.BedOwners = bed.OwnersForReading.Count;
            row.BedOccupants = bed.CurOccupants.Count(p => p != null);
            bool humanlike = bed.def.building != null && bed.def.building.bed_humanlike;
            bool knownQuarters = row.CategoryId == "RR_Facility_Quarters";
            if (humanlike && bed.Medical)
            { row.BedTypeKey = "RR_Fac_MedicalBed"; row.CategoryId = "RR_Facility_Medical"; MedicalSlots += row.BedSlots; }
            else if (!humanlike) { row.BedTypeKey = "RR_Fac_AnimalBed"; OtherBedSlots += row.BedSlots; }
            else if (bed.ForHumanBabies) { row.BedTypeKey = "RR_Fac_BabyBed"; OtherBedSlots += row.BedSlots; }
            else if (bed.ForPrisoners) { row.BedTypeKey = "RR_Fac_PrisonerBed"; OtherBedSlots += row.BedSlots; }
            else if (bed.ForSlaves) { row.BedTypeKey = "RR_Fac_SlaveBed"; OtherBedSlots += row.BedSlots; }
            else if (bed.ForColonists && knownQuarters)
            {
                row.BedTypeKey = "RR_Fac_OrdinaryBed";
                OrdinaryBedSlots += row.BedSlots;
                OrdinaryBedOwners += row.BedOwners;
                OrdinaryBedOccupants += row.BedOccupants;
            }
            else { row.BedTypeKey = "RR_Fac_SpecialBed"; OtherBedSlots += row.BedSlots; }
        }

        public static bool Inspectable(Building building, Map map)
        {
            return Available(map) && building != null && !building.Destroyed && building.Spawned &&
                building.Map == map && building.Faction == Faction.OfPlayer && !building.Position.Fogged(map);
        }
    }
}
