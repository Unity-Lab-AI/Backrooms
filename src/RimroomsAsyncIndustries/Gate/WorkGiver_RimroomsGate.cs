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

    /// <summary>
    /// Offers reconditioning as ordinary work, and only inside the band where it is wanted.
    ///
    /// `ServiceWanted` is false across the whole dead zone, so in a well-kept room this giver
    /// finds nothing for long stretches and costs one boolean per console. That is the point:
    /// the owner's direction was that pawns must not always be doing this.
    /// </summary>
    public sealed class WorkGiver_RRReconditionGate : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        { get { return ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial); } }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            if (pawn == null || pawn.Map == null) { yield break; }
            foreach (Building building in pawn.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGateConsole console = building.TryGetComp<CompRimroomsGateConsole>();
                CompRimroomsGate gate = console == null ? null : console.Gate;
                if (gate != null && gate.Console == building && gate.ServiceWanted) { yield return building; }
            }
        }

        private Job FindReconditionJob(Pawn pawn, Thing thing, bool forced)
        {
            CompRimroomsGateConsole console = thing == null ? null : thing.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate gate = console == null ? null : console.Gate;
            if (gate == null || gate.Console != thing || !gate.CanRecondition(pawn) ||
                !pawn.CanReserveAndReach(thing, PathEndMode.InteractionCell, Danger.Some, 1, -1, null, forced) ||
                !pawn.CanReserveSittableOrSpot(thing.InteractionCell, forced))
            { return null; }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail("RR_ReconditionGate");
            return definition == null ? null : JobMaker.MakeJob(definition, thing);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return FindReconditionJob(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return FindReconditionJob(pawn, t, forced); }
    }

}
