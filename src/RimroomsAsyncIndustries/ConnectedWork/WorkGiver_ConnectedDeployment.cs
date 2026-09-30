using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// How travel-to-work reaches a pawn: as an ordinary WorkGiver, inside Core's own
    /// <c>JobGiver_Work</c>, in that pawn's own priority and schedule order. Nothing here
    /// pushes a job at anybody and nothing is ever marked player-forced.
    ///
    /// The one job this giver ever hands out is a crossing. Once the worker has arrived
    /// it hands out nothing at all, and Core's own work giver for that work type picks
    /// the work up locally. That is the entire point of the shape: the work is done by
    /// the game's own code, on the map it belongs to, with the game's own reservations.
    ///
    /// Registered twice, like every carry family, because starting and continuing need
    /// opposite priorities:
    ///
    /// * a **continuation** giver, above the local giver for its work type, so a worker
    ///   partway to a gate is not turned around by work that appeared at home while it
    ///   walked;
    /// * a **planning** giver, below *every* local giver in its work type, so crossing a
    ///   gate to work only ever happens when there is nothing of that kind to do on this
    ///   side at all.
    /// </summary>
    public abstract class WorkGiver_ConnectedDeployment : WorkGiver
    {
        protected abstract string ProviderId { get; }

        /// <summary>True for the high-priority half that only continues committed trips.</summary>
        protected abstract bool ContinueOnly { get; }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            RimroomsConnectedWorkComponent work = Work();
            if (work == null || !work.CanOperate || pawn == null || !pawn.Spawned) { return true; }
            ConnectedDeploymentProvider provider = ConnectedDeploymentProviders.Get(ProviderId);
            if (provider == null) { return true; }
            ConnectedDeploymentIntent deployment = work.ActiveDeploymentFor(pawn);
            if (ContinueOnly)
            { return deployment == null || deployment.ProviderId != ProviderId; }
            // One commitment per worker, across both record kinds.
            if (deployment != null || work.ActiveIntentFor(pawn) != null) { return true; }
            if (!work.MayPlanFor(pawn) || !provider.WorkerEligible(pawn)) { return true; }
            // Nothing to plan against until this branch actually remembers a gate.
            RimroomsPortalNetwork network = Network();
            return network == null || network.HasStateFault || network.Connections.Count == 0;
        }

        public override Job NonScanJob(Pawn pawn)
        {
            RimroomsConnectedWorkComponent work = Work();
            ConnectedDeploymentProvider provider = ConnectedDeploymentProviders.Get(ProviderId);
            RimroomsPortalCrossingService crossings = Crossings();
            if (work == null || !work.CanOperate || provider == null || crossings == null ||
                crossings.StateFaultKey != null || pawn == null || !pawn.Spawned)
            { return null; }
            // The gate rule, asked on every path into this layer and not only at the
            // threshold: a colonist may decide to cross to work, nothing else may decide
            // anything about a gate.
            if (PortalTraversalPolicy.TravellerFailureKey(pawn) != null) { return null; }
            // Someone held inside an unresolved crossing belongs to the crossing service
            // until its receipt is reconciled. Never hand them a job.
            if (crossings.HasUnresolvedCrossing(pawn)) { return null; }
            // The one legitimate moment this worker's allowed area on this map is
            // observable is while it is standing on it. Write it down every pass.
            work.ObserveAreaHere(pawn);

            ConnectedDeploymentIntent deployment = work.ActiveDeploymentFor(pawn);
            if (deployment != null)
            {
                if (!ContinueOnly || deployment.ProviderId != ProviderId) { return null; }
                return Continue(deployment, provider, pawn, work);
            }
            if (ContinueOnly || !work.MayPlanFor(pawn)) { return null; }
            if (work.ActiveIntentFor(pawn) != null) { return null; }
            if (!provider.WorkerEligible(pawn)) { return null; }
            work.NotePlanningPass(pawn);
            deployment = Plan(provider, pawn, work);
            return deployment == null ? null : Continue(deployment, provider, pawn, work);
        }

        /// <summary>
        /// Look for a connected map that holds work of this kind, and open a deployment
        /// for the first one found. Bounded: a fixed number of connected maps from a
        /// rotating start, and a bounded candidate window inside each.
        /// </summary>
        private ConnectedDeploymentIntent Plan(ConnectedDeploymentProvider provider, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            RimroomsCampaignComponent campaign = Campaign();
            if (campaign == null || !campaign.CanOperate || pawn.Map == null ||
                !campaign.OwnsMap(pawn.Map))
            { return null; }

            // Never send someone through a gate while the same kind of work is waiting on
            // this side. The local giver for this work type does sit above this one, but
            // Core's JobGiver_Work walks every giver in priority order calling NonScanJob
            // *before* that giver's scan, and a higher-priority scanner only wins once it
            // has actually found a target. So "is there local work" has to be asked here
            // outright; it cannot be inferred from the priority number.
            if (provider.HasWorkHere(pawn)) { return null; }

            List<Map> connected = ConnectedWorkScan.ConnectedMaps(campaign, pawn.Map, pawn);
            for (int index = 0; index < connected.Count; index++)
            {
                Map other = connected[index];
                // A place that turned this worker away recently is left alone for a while.
                if (work.DestinationRecentlyRefused(pawn, other)) { continue; }
                PortalRouteStep step;
                bool pending;
                if (!work.Routes.TryNextStep(pawn.Map, other, out step, out pending)) { continue; }
                // If we have ever seen that this worker's allowed area excludes where it
                // would arrive, the trip is pointless before it starts.
                if (step != null && step.Destination != null &&
                    !work.ObservedAreaAllows(pawn, step.Destination.Map, step.Destination.ApproachCell))
                { continue; }
                if (!provider.HasCandidateWork(other, pawn, work)) { continue; }
                ConnectedDeploymentIntent opened = work.OpenDeployment(provider, pawn, other, step);
                if (opened != null) { return opened; }
            }
            return null;
        }

        /// <summary>
        /// One segment of the deployment, chosen from its phase and the worker's actual
        /// current map. Nothing is stored about "which step comes next", so a reload, an
        /// interruption or an unexpected location all resolve here.
        /// </summary>
        private Job Continue(ConnectedDeploymentIntent deployment, ConnectedDeploymentProvider provider,
            Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            string blocking = work.LiveFailureKey(deployment);
            if (blocking != null)
            {
                work.Close(deployment, RimroomsConnectedWorkComponent.DeploymentPhaseFor(blocking), blocking);
                return null;
            }
            if (pawn.Map != deployment.DestinationMap)
            { return CrossToward(deployment, pawn, work); }

            // Arrived. The definitive question, asked of the map the worker is standing
            // on, where every native check finally means what it says.
            if (!provider.HasWorkHere(pawn))
            {
                if (deployment.Phase == ConnectedDeploymentPhase.Travelling)
                {
                    // We crossed for this and there is nothing to do after all. Remember
                    // the map for a while so the next pass does not repeat the walk.
                    work.NoteDestinationRefused(pawn, pawn.Map);
                    work.Close(deployment, ConnectedDeploymentPhase.Cancelled,
                        "RR_ConnectedWork_NoWorkOnArrival");
                    return null;
                }
                // The work here is done. A finished deployment, and deliberately no
                // refusal recorded: coming back when there is more to do is correct.
                work.Close(deployment, ConnectedDeploymentPhase.Completed, null);
                return null;
            }

            // There is work here, and Core's own giver for it is already scanning this
            // map in this pawn's own priority order. Issue nothing: holding the record is
            // the whole contribution, and it is what stops this worker being planned into
            // a trip back across the gate while a frame in front of it is unfinished.
            //
            // The worker is never dragged home. When the work runs out the record simply
            // closes and the person is free, standing where it stands, with its own needs
            // and whatever local work it finds — which is exactly what the portal
            // contract says about anyone who crossed legitimately.
            work.NoteArrival(deployment);
            return null;
        }

        /// <summary>
        /// One hop toward the destination, through the single shared crossing
        /// implementation. What is specific to a deployment is the ending: running out of
        /// attempts has cost a walk and nothing else, because nothing is being carried.
        /// </summary>
        private Job CrossToward(ConnectedDeploymentIntent deployment, Pawn pawn,
            RimroomsConnectedWorkComponent work)
        {
            Map destination = deployment.DestinationMap;
            if (deployment.CrossAttempts >= RimroomsConnectedWorkComponent.MaximumCrossAttempts)
            {
                work.NoteDestinationRefused(pawn, destination);
                work.Close(deployment, ConnectedDeploymentPhase.Failed, "RR_ConnectedWork_RouteExhausted");
                return null;
            }
            Job job;
            ConnectedCrossingOutcome outcome = ConnectedCrossing.StepToward(pawn, destination, work, out job);
            if (outcome == ConnectedCrossingOutcome.NoRoute)
            {
                work.Close(deployment, ConnectedDeploymentPhase.Cancelled, "RR_ConnectedWork_NoRoute");
                return null;
            }
            if (outcome != ConnectedCrossingOutcome.Step) { return null; }
            work.NoteCrossAttempt(deployment);
            return job;
        }

        private static RimroomsConnectedWorkComponent Work()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsConnectedWorkComponent>(); }
        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }
        private static RimroomsPortalCrossingService Crossings()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalCrossingService>(); }
    }

    /// <summary>
    /// Sends a builder through a gate to finish a frame that already has its material.
    /// Sits below every one of Core's own construction givers, so a builder only ever
    /// crosses when there is nothing constructive left to do on this side.
    /// </summary>
    public sealed class WorkGiver_ConnectedConstructionFinishing : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.ConstructionFinishing; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>
    /// Walks a builder the rest of the way to a site it was already sent to, then gets
    /// out of the way. Sits above Core's own frame finishing so a worker partway to a
    /// gate is not turned around by a frame that appeared at home while it walked.
    /// </summary>
    public sealed class WorkGiver_ConnectedConstructionFinishingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.ConstructionFinishing; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>
    /// Sends a researcher through a gate to a bench on the other side. Sits below every one
    /// of Core's own research givers, so a researcher only crosses when there is nothing to
    /// research on this side.
    /// </summary>
    public sealed class WorkGiver_ConnectedResearch : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId { get { return ConnectedDeploymentProviders.Research; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>
    /// Walks a researcher the rest of the way to a bench it was already sent to, then gets
    /// out of the way so whatever research giver is active there does the work.
    /// </summary>
    public sealed class WorkGiver_ConnectedResearchContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId { get { return ConnectedDeploymentProviders.Research; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a doctor through a gate to a patient who stays where they are.</summary>
    public sealed class WorkGiver_ConnectedTending : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId { get { return ConnectedDeploymentProviders.Tending; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks a doctor the rest of the way to a patient, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedTendingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId { get { return ConnectedDeploymentProviders.Tending; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends someone through a gate to feed a patient who cannot feed themselves.</summary>
    public sealed class WorkGiver_ConnectedFeeding : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.PatientFeeding; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks a feeder the rest of the way to a patient, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedFeedingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.PatientFeeding; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>
    /// Sends somebody through a gate to put a downed person into a bed on that same map,
    /// rather than hauling them home first. The counterpart of the casualty family, not a
    /// duplicate of it.
    /// </summary>
    public sealed class WorkGiver_ConnectedRescueInPlace : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.RescueInPlace; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks a rescuer the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedRescueInPlaceContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.RescueInPlace; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do cleaning work over there.</summary>
    public sealed class WorkGiver_ConnectedCleaning : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Cleaning; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedCleaningContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Cleaning; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do repair work over there.</summary>
    public sealed class WorkGiver_ConnectedRepair : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Repair; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedRepairContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Repair; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do firefighting work over there.</summary>
    public sealed class WorkGiver_ConnectedFirefighting : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Firefighting; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedFirefightingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Firefighting; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do designated mining work over there.</summary>
    public sealed class WorkGiver_ConnectedMining : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Mining; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedMiningContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Mining; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do designated hunting work over there.</summary>
    public sealed class WorkGiver_ConnectedHunting : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Hunting; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedHuntingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Hunting; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do designated plantcutting work over there.</summary>
    public sealed class WorkGiver_ConnectedPlantCutting : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.PlantCutting; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedPlantCuttingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.PlantCutting; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to do designated growing work over there.</summary>
    public sealed class WorkGiver_ConnectedGrowing : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Growing; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedGrowingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Growing; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to warden work over there.</summary>
    public sealed class WorkGiver_ConnectedWarden : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Warden; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedWardenContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Warden; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to childcare work over there.</summary>
    public sealed class WorkGiver_ConnectedChildcare : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Childcare; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedChildcareContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Childcare; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    /// <summary>Sends a worker through a gate to animalhandling work over there.</summary>
    public sealed class WorkGiver_ConnectedHandling : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.AnimalHandling; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    /// <summary>Walks that worker the rest of the way, then gets out of the way.</summary>
    public sealed class WorkGiver_ConnectedHandlingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.AnimalHandling; } }
        protected override bool ContinueOnly { get { return true; } }
    }
    // Bill work: one giver pair per work type, because Core itself distinguishes them.
    // `WorkGiver_DoBill.StartOrResumeBillJob` compares a recipe's `requiredGiverWorkType`
    // against `def.workType`, and a bench belongs to a work type only through its
    // `WorkGiverDef.fixedBillGiverDefs`. See `BillWorkProvider` for the whole argument.

    public sealed class WorkGiver_ConnectedBillWorkCooking : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkCooking; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkCookingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkCooking; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkCrafting : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkCrafting; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkCraftingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkCrafting; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkSmithing : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkSmithing; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkSmithingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkSmithing; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkTailoring : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkTailoring; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkTailoringContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkTailoring; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkArt : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkArt; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedBillWorkArtContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BillWorkArt; } }
        protected override bool ContinueOnly { get { return true; } }
    }


    public sealed class WorkGiver_ConnectedDarkStudy : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.DarkStudy; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedDarkStudyContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.DarkStudy; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedHaulingUpkeep : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.HaulingUpkeep; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedHaulingUpkeepContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.HaulingUpkeep; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedMachineLoading : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.MachineLoading; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedMachineLoadingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.MachineLoading; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedPainting : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Painting; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedPaintingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Painting; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedRoofWork : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.RoofWork; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedRoofWorkContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.RoofWork; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedBasicWorker : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BasicWorker; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedBasicWorkerContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.BasicWorker; } }
        protected override bool ContinueOnly { get { return true; } }
    }

    public sealed class WorkGiver_ConnectedFishing : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Fishing; } }
        protected override bool ContinueOnly { get { return false; } }
    }

    public sealed class WorkGiver_ConnectedFishingContinue : WorkGiver_ConnectedDeployment
    {
        protected override string ProviderId
        { get { return ConnectedDeploymentProviders.Fishing; } }
        protected override bool ContinueOnly { get { return true; } }
    }
}
