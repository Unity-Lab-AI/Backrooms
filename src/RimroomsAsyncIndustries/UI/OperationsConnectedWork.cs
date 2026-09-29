using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.ConnectedWork;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// Shows the cross-gate work trips currently under way. This exists for the same
    /// reason the unresolved-crossing list does: saved state that moves the player's
    /// people and goods must never be invisible. A trip listed here names who is on
    /// it, what object it is for, and which way it is going.
    /// </summary>
    public sealed partial class MainTabWindow_Operations
    {
        private void DrawConnectedWork(Listing_Standard listing)
        {
            RimroomsConnectedWorkComponent work = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsConnectedWorkComponent>();
            if (work == null) { return; }
            listing.Label("RR_ConnectedWork_Heading".Translate());
            if (work.StateFaultKey != null)
            {
                listing.Label(work.StateFaultKey.Translate());
                return;
            }
            if (!work.CanOperate)
            {
                listing.Label("RR_ConnectedWork_Unavailable".Translate());
                return;
            }
            List<ConnectedWorkIntent> live = work.Intents
                .Where(intent => intent != null && intent.IsLive)
                .OrderBy(intent => intent.Id)
                .ToList();
            List<ConnectedDeploymentIntent> deployed = work.Deployments
                .Where(deployment => deployment != null && deployment.IsLive)
                .OrderBy(deployment => deployment.Id)
                .ToList();
            if (live.Count == 0 && deployed.Count == 0)
            {
                listing.Label("RR_ConnectedWork_None".Translate());
                return;
            }
            DrawDeployments(listing, deployed);
            if (live.Count == 0) { return; }
            listing.Label("RR_ConnectedWork_Active".Translate(live.Count));
            foreach (ConnectedWorkIntent intent in live)
            {
                bool carrying = intent.Phase == ConnectedWorkPhase.Carrying;
                Thing subject = carrying ? intent.Cargo : intent.SourceThing;
                string stage = (carrying
                    ? "RR_ConnectedWork_StageCarrying" : "RR_ConnectedWork_StageCollecting").Translate().ToString();
                listing.Label("RR_ConnectedWork_Line".Translate(
                    intent.Pawn == null ? "RR_ConnectedWork_UnknownWorker".Translate().ToString()
                        : intent.Pawn.LabelShortCap.ToString(),
                    subject == null ? "RR_ConnectedWork_UnknownObject".Translate().ToString()
                        : subject.LabelCap.ToString(),
                    MapLabel(intent.FetchMap),
                    MapLabel(intent.StoreMap),
                    stage));
            }
        }

        /// <summary>
        /// The people this company has sent to work somewhere else. Listed separately from
        /// the carry trips above because they are a different thing and reading them as
        /// hauling would be misleading: nobody here is bringing anything back. The line
        /// says who, what work justified it, where, and whether they are still walking.
        /// </summary>
        private static void DrawDeployments(Listing_Standard listing,
            List<ConnectedDeploymentIntent> deployed)
        {
            if (deployed.Count == 0) { return; }
            listing.Label("RR_ConnectedWork_Deployed".Translate(deployed.Count));
            foreach (ConnectedDeploymentIntent deployment in deployed)
            {
                ConnectedDeploymentProvider provider =
                    ConnectedDeploymentProviders.Get(deployment.ProviderId);
                string stage = (deployment.Phase == ConnectedDeploymentPhase.Deployed
                    ? "RR_ConnectedWork_StageWorking"
                    : "RR_ConnectedWork_StageTravelling").Translate().ToString();
                listing.Label("RR_ConnectedWork_DeployLine".Translate(
                    deployment.Pawn == null ? "RR_ConnectedWork_UnknownWorker".Translate().ToString()
                        : deployment.Pawn.LabelShortCap.ToString(),
                    provider == null ? "RR_ConnectedWork_UnknownWork".Translate().ToString()
                        : provider.LabelKey.Translate().ToString(),
                    MapLabel(deployment.DestinationMap),
                    stage));
            }
        }

        private static string MapLabel(Map map)
        {
            if (map == null) { return "RR_ConnectedWork_UnknownPlace".Translate().ToString(); }
            return map.Parent == null || string.IsNullOrEmpty(map.Parent.Label)
                ? "RR_ConnectedWork_UnknownPlace".Translate().ToString() : map.Parent.Label;
        }
    }
}
