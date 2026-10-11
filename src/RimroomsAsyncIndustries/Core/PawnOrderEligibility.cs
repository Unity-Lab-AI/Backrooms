using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>
    /// Whether code that was not asked by the player may hand a pawn an ordered job right now.
    ///
    /// An ordered job replaces whatever the pawn is doing, so anything this package issues on its own
    /// (exploration walks, setup helpers) has to leave alone a pawn the player drafted or ordered, a pawn
    /// that cannot act, and a pawn that is about to go and eat or sleep.
    /// </summary>
    internal static class PawnOrderEligibility
    {
        public static bool FreeForAutonomousOrders(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.InMentalState || pawn.Drafted)
            {
                return false;
            }

            if (pawn.jobs == null) return false;
            if (pawn.CurJob != null && pawn.CurJob.playerForced) return false;
            if (pawn.jobs.jobQueue != null && pawn.jobs.jobQueue.AnyPlayerForced) return false;

            if (pawn.needs != null)
            {
                if (pawn.needs.food != null && pawn.needs.food.CurCategory >= HungerCategory.Hungry) return false;
                if (pawn.needs.rest != null && pawn.needs.rest.CurCategory >= RestCategory.VeryTired) return false;
            }

            return true;
        }
    }
}
