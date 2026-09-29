using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Gate
{
    public sealed class WorkGiver_RRCalibrateGate : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        {
            get { return ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial); }
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            if (pawn == null || pawn.Map == null) { yield break; }
            foreach (Building building in pawn.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGateConsole console = building.TryGetComp<CompRimroomsGateConsole>();
                CompRimroomsGate gate = console == null ? null : console.Gate;
                if (gate != null && gate.Console == building) { yield return building; }
            }
        }

        private Job FindCalibrationJob(Pawn pawn, Thing thing, bool forced)
        {
            CompRimroomsGateConsole console = thing == null ? null : thing.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate gate = console == null ? null : console.Gate;
            if (gate == null || gate.Console != thing || !gate.CanCalibrate(pawn) || !pawn.CanReserveAndReach(thing, PathEndMode.InteractionCell,
                Danger.Some, 1, -1, null, forced) || !pawn.CanReserveSittableOrSpot(thing.InteractionCell, forced))
            { return null; }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail("RR_CalibrateGate");
            return definition == null ? null : JobMaker.MakeJob(definition, thing);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return FindCalibrationJob(pawn, t, forced) != null;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return FindCalibrationJob(pawn, t, forced);
        }
    }

    public sealed class CompProperties_RimroomsGateCutoff : CompProperties
    {
        public CompProperties_RimroomsGateCutoff() { compClass = typeof(CompRimroomsGateCutoff); }
    }

    public sealed class CompRimroomsGateCutoff : ThingComp
    {
        private CompRimroomsGate Gate
        {
            get
            {
                if (!parent.Spawned || parent.Map == null) { return null; }
                ThingDef gateDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_MachineGate");
                if (gateDef == null) { return null; }
                Thing gate = parent.Map.listerBuildings.AllBuildingsColonistOfDef(gateDef)
                    .OrderBy(t => t.Position.DistanceToSquared(parent.Position)).FirstOrDefault();
                return gate == null ? null : gate.TryGetComp<CompRimroomsGate>();
            }
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            if (parent.Faction != Faction.OfPlayer) { yield break; }
            yield return new Command_Action
            {
                defaultLabel = "RR_Gate_EmergencyCutoffLabel".Translate(),
                defaultDesc = "RR_Gate_EmergencyCutoffDesc".Translate(),
                icon = ContentFinder<Texture2D>.Get("Buildings/Gate/RR_EmergencyCutoff", true),
                action = TriggerCutoff
            };
        }

        public override string CompInspectStringExtra()
        {
            CompRimroomsGate gate = Gate;
            return gate == null ? "RR_Gate_NoMachineLinked".Translate().ToString()
                : gate.IsEmergency ? "RR_Gate_CutoffEmergencyActive".Translate(gate.FailureKey.Translate()).ToString()
                : "RR_Gate_CutoffReady".Translate().ToString();
        }

        private void TriggerCutoff()
        {
            CompRimroomsGate gate = Gate;
            CompanyActionResult result = gate == null ? CompanyActionResult.Refused("RR_Gate_NoMachineLinked")
                : gate.TriggerEmergencyCutoff();
            if (!result.Success)
            { Messages.Message(result.MessageKey.Translate(), parent, MessageTypeDefOf.RejectInput, false); }
        }
    }
}
