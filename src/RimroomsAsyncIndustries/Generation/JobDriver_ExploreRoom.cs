using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Walk into a room and write it into the journal.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"survey should go hand in hand with the auto
    /// explore and person has task to write in journal when exploring each room for like 20
    /// seconds"*.
    ///
    /// ## The survey IS the journal task, which is a change of cause and not of effect
    ///
    /// `FirstSliceSiteComponent` has always marked a room surveyed when somebody carrying a record
    /// book stood in it. That stays. What the owner's direction adds is that an **explorer** does not
    /// get it for free by walking through: they stop, and they write, and the writing is what
    /// produces the survey. So this job's one derivation of *mark it* is
    /// <see cref="FirstSliceSiteComponent.MarkRoomSurveyed"/> — the same method, the same event line,
    /// the same field observation.
    ///
    /// ## Twenty seconds, and the number is the owner's
    ///
    /// <see cref="RoomSurveyTicks"/> is 1,200 ticks: at RimWorld's 60 ticks a second that is **twenty
    /// seconds of real time at normal speed**, which is what *"for like 20 seconds"* says. Long enough
    /// that a player watches it happen and a maze is a real undertaking; short enough that a
    /// seven-room coordinate is minutes rather than an evening.
    ///
    /// ## The book is required, and that is the point of having one
    ///
    /// No book, no job. The record book is what a survey is written *into*, so an explorer without one
    /// is a colonist on a walk. This is the same condition the walk-through already applies, asked of
    /// one pawn instead of the whole crew because this pawn is the one doing the writing.
    ///
    /// ## And the pawn is never trapped
    ///
    /// `GateWatch.MustLeave` in the `FailOn` and again every tick, exactly as at the gate console and
    /// the records desk. Exploring is an order, not a sentence.
    /// </summary>
    public sealed class JobDriver_RRExploreRoom : JobDriver
    {
        /// <summary>
        /// How long writing one room up takes.
        ///
        /// **1,200 ticks = twenty seconds at normal speed**, which is the owner's own figure. Stated
        /// as ticks rather than seconds because that is what the game counts, and the conversion is
        /// written here so nobody has to rediscover it.
        /// </summary>
        public const int RoomSurveyTicks = 1200;

        private int written;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref written, "rr_roomSurveyProgress", 0);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed) { return true; }

        /// <summary>The room this job is writing up, resolved from where the pawn is standing.</summary>
        private RoomRecord TargetRoom
        {
            get
            {
                FirstSliceSiteComponent site = pawn.Map == null
                    ? null : pawn.Map.GetComponent<FirstSliceSiteComponent>();
                return site == null ? null : site.RoomAt(job.targetA.Cell);
            }
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnBurningImmobile(TargetIndex.A);
            // The floor, before anything. One derivation with the console and the desk.
            this.FailOn(() => GateWatch.MustLeave(pawn));
            // Toggled off mid-walk means stop walking. The order is the player's and so is the
            // cancellation, which is what makes it behave like drafting.
            this.FailOn(() =>
            {
                CompRimroomsExplorer explorer = pawn.TryGetComp<CompRimroomsExplorer>();
                return explorer == null || !explorer.Exploring;
            });
            // **No book, no survey.** Asked here as well as in the component that issues the job,
            // because a pawn can be relieved of the book between the order and the arrival.
            this.FailOn(() => !FirstSliceSiteComponent.CarriesRecordBook(pawn));

            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);

            Toil write = ToilMaker.MakeToil("RR_ExploreRoomWrite");
            write.initAction = delegate
            {
                // Already written up by somebody else while this pawn walked. Not a failure: the
                // component will hand them the next room on its following tick.
                RoomRecord room = TargetRoom;
                if (room == null || room.Surveyed) { EndJobWith(JobCondition.Succeeded); }
            };
            write.tickAction = delegate
            {
                if (GateWatch.MustLeave(pawn))
                { EndJobWith(JobCondition.InterruptForced); return; }
                RoomRecord room = TargetRoom;
                if (room == null) { EndJobWith(JobCondition.Incompletable); return; }
                if (room.Surveyed) { EndJobWith(JobCondition.Succeeded); return; }

                written++;
                // Intellectual, like every other writing job in this mod, and a small amount: the
                // work is observation rather than analysis.
                if (pawn.skills != null) { pawn.skills.Learn(SkillDefOf.Intellectual, 0.04f); }
                if (written < RoomSurveyTicks) { return; }

                FirstSliceSiteComponent site = pawn.Map == null
                    ? null : pawn.Map.GetComponent<FirstSliceSiteComponent>();
                if (site != null) { site.MarkRoomSurveyed(room, pawn); }
                ReadyForNextToil();
            };
            write.defaultCompleteMode = ToilCompleteMode.Never;
            write.WithProgressBar(TargetIndex.A, () => (float)written / RoomSurveyTicks);
            write.activeSkill = () => SkillDefOf.Intellectual;
            yield return write;
        }
    }
}
