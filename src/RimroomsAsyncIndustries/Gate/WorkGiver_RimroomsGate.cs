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

    /// <summary>
    /// Sends a qualified staff member to take a gate console when nobody is holding the window.
    ///
    /// **This is the half of operator relief that makes it automatic.** Owner, 2026-10-06: *"he can
    /// leave when another pawn hops on the other comms console toggled to gate contrtrols"*. Four
    /// bindable stations and a station-based hold make a hand-off *possible*; without a work giver
    /// the hop has to be ordered by hand every time, and a player micromanaging a relay has not
    /// been relieved of anything.
    ///
    /// **Nothing in this mod staffed a console as ordinary work before.** The only route was
    /// `assignedOperator.jobs.TryTakeOrderedJob(job, JobTag.Misc)` -- a forced job on one named
    /// pawn -- which is why there was no hand-off anywhere: a second colonist was never offered the
    /// post, so they could never take it.
    ///
    /// ## IT FINDS NOTHING ALMOST ALWAYS, AND THAT IS THE DESIGN
    ///
    /// `ReliefWanted` is false unless the gate is designated, **actually holding a connection**,
    /// not in emergency, not killed, and currently unattended. A closed gate wants nobody, so in a
    /// colony between expeditions this giver costs one boolean per console and offers no work at
    /// all. That is the same discipline `WorkGiver_RRReconditionGate` states for itself: *"the
    /// owner's direction was that pawns must not always be doing this."*
    ///
    /// **And it is ordinary work with an ordinary priority.** It competes with cooking and hauling
    /// like anything else, so a branch that assigns nobody to it still loses windows -- which is a
    /// decision the player made rather than a defect. The pawn is never trapped either:
    /// `GateWatch.MustLeave` is an absolute floor inside the job itself, asked before any posture.
    /// </summary>
    public sealed class WorkGiver_RRStaffGateConsole : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        { get { return ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial); } }

        /// <summary>
        /// Every station of every gate that currently wants somebody.
        ///
        /// **Enumerated from the gate outward rather than from consoles inward.** A relief station
        /// is an equipment link, so a console does not know which gate it relieves; the gate does.
        /// Asking the console would mean re-deriving the link in the opposite direction, and the
        /// gate's own `BoundConsoles` is already the single answer to *where can this be held from*.
        /// </summary>
        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            if (pawn == null || pawn.Map == null) { yield break; }
            foreach (Building building in pawn.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGate gate = building.TryGetComp<CompRimroomsGate>();
                if (gate == null || !gate.ReliefWanted) { continue; }
                foreach (Thing station in gate.BoundConsoles)
                {
                    if (station != null) { yield return station; }
                }
            }
        }

        /// <summary>
        /// The gate this station can hold a window for, or null.
        ///
        /// A station may be the gate's own console or one of its relief links, so both routes are
        /// tried. Resolved per call rather than cached: a link can be made or broken between ticks.
        /// </summary>
        private static CompRimroomsGate GateWanting(Thing station)
        {
            if (station == null || station.Map == null) { return null; }
            CompRimroomsGateConsole bound = station.TryGetComp<CompRimroomsGateConsole>();
            CompRimroomsGate direct = bound == null ? null : bound.Gate;
            if (direct != null && direct.ReliefWanted) { return direct; }
            foreach (Building building in station.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGate gate = building.TryGetComp<CompRimroomsGate>();
                if (gate == null || !gate.ReliefWanted) { continue; }
                foreach (Thing candidate in gate.BoundConsoles)
                {
                    if (candidate == station) { return gate; }
                }
            }
            return null;
        }

        private Job FindStaffingJob(Pawn pawn, Thing thing, bool forced)
        {
            CompRimroomsGate gate = GateWanting(thing);
            if (gate == null || !gate.QualifiedToStaff(pawn)) { return null; }
            // The pawn has to be able to get there and sit there. `CanReserveSittableOrSpot` is
            // what stops two colonists being sent to the same chair, which on four stations is the
            // difference between relief and a traffic jam.
            if (!pawn.CanReserveAndReach(thing, PathEndMode.InteractionCell, Danger.Some, 1, -1,
                    null, forced)
                || !pawn.CanReserveSittableOrSpot(thing.InteractionCell, forced))
            { return null; }
            // **Asked before the post is offered, not only inside the job.** A pawn who is starving
            // or bleeding out would take the post, fail out of it on the first tick, and be offered
            // it again -- a loop that looks like a pawn twitching at a console. The job's own floor
            // stays exactly where it is; this stops the offer being made in the first place.
            if (GateWatch.MustLeave(pawn)
                || GateWatch.Releases(pawn, gate.WatchPosture))
            { return null; }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail("RR_OperateGate");
            return definition == null ? null : JobMaker.MakeJob(definition, thing);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return FindStaffingJob(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return FindStaffingJob(pawn, t, forced); }
    }
}
