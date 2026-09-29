using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork.Providers
{
    /// <summary>
    /// A builder crossing a gate to finish a frame that already has all its material.
    ///
    /// This is the other half of construction across a gate. The supply family carries
    /// real steel through to a real frame; this one sends the person, because a frame
    /// whose material is all delivered does not need anything carried to it — it needs
    /// somebody to stand next to it and build.
    ///
    /// Nothing about construction is reimplemented here, not even the job. On arrival
    /// Core's own <c>WorkGiver_ConstructFinishFrames</c> is already scanning that map in
    /// this pawn's own priority order and will pick the frame up itself, with its own
    /// reservation, its own blocking-thing handling and its own toils. This provider
    /// only answers whether going there is justified.
    ///
    /// The division of the eligibility rules follows Core's own
    /// <c>GenConstruct.CanConstruct</c> exactly, split by what each rule reads:
    ///
    /// * Facts about the frame and the pawn's own skills, ideo and work settings are
    ///   map-independent or are facts about the frame's *own* map, so they are fair to
    ///   ask about a map nobody is standing on.
    /// * <c>CanTouchTargetFromValidCell</c> and <c>CanReserveAndReach</c> read the
    ///   worker's map, its regions and its reservation manager. They are asked only on
    ///   arrival, through Core's own <c>CanConstruct</c>, never remotely.
    /// </summary>
    public sealed class ConstructionFinishingProvider : ConnectedDeploymentProvider
    {
        /// <summary>How many frames one remote candidate pass may look at.</summary>
        private const int MaximumFramesPerMap = 24;

        public override string ProviderId
        { get { return ConnectedDeploymentProviders.ConstructionFinishing; } }

        public override int ProviderVersion { get { return 1; } }

        public override string LabelKey { get { return "RR_ConnectedWork_FinishingLabel"; } }

        public override WorkTypeDef WorkType
        { get { return DefDatabase<WorkTypeDef>.GetNamedSilentFail("Construction"); } }

        public override bool WorkerEligible(Pawn pawn)
        {
            WorkTypeDef workType = WorkType;
            if (pawn == null || workType == null) { return false; }
            // The player's own work assignment is respected exactly as Core respects it.
            // Nothing here is ever forced, so a colonist with construction switched off
            // is never sent to build, on this map or any other.
            if (pawn.WorkTypeIsDisabled(workType)) { return false; }
            return pawn.workSettings != null && pawn.workSettings.WorkIsActive(workType);
        }

        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            List<Thing> frames = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame);
            if (frames.Count == 0) { return false; }
            // A rotating window, never a prefix: a long frame queue must not starve its
            // own tail, and several connected maps may be open at once.
            int windowStart = ConnectedWorkScan.WindowStart(frames.Count, MaximumFramesPerMap, pawn);
            int examined = 0;
            for (int position = windowStart; position < frames.Count; position++)
            {
                if (examined >= MaximumFramesPerMap) { break; }
                examined++;
                if (CandidateFrame(frames[position] as Frame, pawn, map, work)) { return true; }
            }
            return false;
        }

        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            List<Thing> frames = pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame);
            for (int index = 0; index < frames.Count; index++)
            {
                var frame = frames[index] as Frame;
                if (frame == null || frame.Destroyed || !frame.Spawned) { continue; }
                if (frame.Faction != pawn.Faction) { continue; }
                // Material still owed is the supply family's business, not this one's.
                if (!frame.IsCompleted() || frame.WorkLeft <= 0f) { continue; }
                if (frame.Position.Fogged(frame.Map)) { continue; }
                // Core's own scanner framework filters forbidden things before ever
                // calling its giver, so CanConstruct does not check it. Asked here.
                if (frame.IsForbidden(pawn)) { continue; }
                // The definitive half, and Core's own: reachability, a valid cell to
                // stand in, blocking things, burning, skills, ideo and reservations.
                if (!GenConstruct.CanConstruct(frame, pawn, true, false)) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether this frame on this explicit map is worth crossing a gate for. Every
        /// rule below reads either the frame, the frame's own map, or the pawn's own
        /// skills and beliefs. None of them reads the worker's map, regions, reachability
        /// or reservations, because the worker is not there yet.
        /// </summary>
        private static bool CandidateFrame(Frame frame, Pawn pawn, Map map,
            RimroomsConnectedWorkComponent work)
        {
            if (frame == null || frame.Destroyed || !frame.Spawned || frame.Map != map)
            { return false; }
            // Core's own first test in WorkGiver_ConstructFinishFrames.
            if (frame.Faction != pawn.Faction) { return false; }
            if (!frame.IsCompleted() || frame.WorkLeft <= 0f) { return false; }
            if (frame.IsBurning()) { return false; }
            // The faction form of the forbidden check, not the pawn form: the pawn form
            // consults its allowed area in its current map, which is the wrong map here.
            if (frame.IsForbidden(Faction.OfPlayer)) { return false; }
            if (frame.Position.Fogged(map)) { return false; }
            // A frame with something in its footprint needs that cleared first, which is
            // its own local job. Sending someone across a gate to discover it is a
            // wasted walk, so a blocked frame is not a candidate. This reads the frame's
            // own map and compares identity only, so it is fair to ask remotely.
            if (GenConstruct.FirstBlockingThing(frame, pawn) != null) { return false; }
            if (!SkillsAllow(frame, pawn)) { return false; }
            if (pawn.Ideo != null && !pawn.Ideo.MembersCanBuild(frame)) { return false; }
            // What we last saw of this worker's allowed area over there. An unobserved
            // map reads unrestricted, which is Core's own answer for a map no area was
            // ever set on. The per-pawn truth is rechecked on arrival regardless.
            return work.ObservedAreaAllows(pawn, map, frame.Position);
        }

        /// <summary>
        /// The skill prerequisites Core checks, read from the same places Core reads
        /// them. Map-independent, so it is safe before the worker travels — and worth
        /// asking early, because a builder who cannot legally build this thing would
        /// otherwise walk through a gate to be refused on arrival.
        /// </summary>
        private static bool SkillsAllow(Frame frame, Pawn pawn)
        {
            if (pawn.skills == null) { return true; }
            if (pawn.skills.GetSkill(SkillDefOf.Construction).Level <
                frame.def.constructionSkillPrerequisite)
            { return false; }
            return pawn.skills.GetSkill(SkillDefOf.Artistic).Level >=
                frame.def.artisticSkillPrerequisite;
        }
    }
}
