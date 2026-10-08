using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// Sends exploring pawns from room to room until the coordinate is written up.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"the pawns will go room to room exploring the maze
    /// of the map attempting to explore the seed completely until toggled off or completed with a pop
    /// notice "PAwn radioed in exploration complete" or something appropriate"*, and *"survey should
    /// go hand in hand with the auto explore and person has task to write in journal when exploring
    /// each room for like 20 seconds"*.
    ///
    /// ## Completion is a real state, not a guess
    ///
    /// **Every room the planner authored has been entered**, read off the room records. **Not every
    /// cell unfogged** — a sealed pocket behind unmined rock would make completion unreachable and the
    /// notice would never fire, and `SealedFamily` vaults exist precisely so some rooms have no door.
    /// The room records already enumerate what a coordinate *has*, so they are the only honest
    /// denominator.
    ///
    /// **And a sealed vault is excluded for the same reason it is excluded from the layout check** —
    /// it has no links, it is reached by mining, and demanding it would make every coordinate holding
    /// one permanently incomplete. That rule is `room.Links.Count == 0`, tested the same way and for
    /// the same reason as `ValidatePlacedLayoutCore`, which is the defect that killed the owner's solo
    /// start when the two disagreed.
    ///
    /// ## It never issues a second job to a busy pawn
    ///
    /// The only thing this does is hand an **idle** explorer its next room. A pawn already writing one
    /// up is left alone, which is what makes the twenty seconds mean twenty seconds rather than a
    /// restart every tick.
    /// </summary>
    public sealed class ExplorationMapComponent : MapComponent
    {
        /// <summary>
        /// How often an idle explorer is given its next room. **Once a game-second.**
        ///
        /// Nothing here is urgent: a pawn that waits a second between rooms is invisible next to the
        /// twenty seconds they spend writing, and a scan every tick would be real cost for an answer
        /// that changes when somebody finishes a room.
        /// </summary>
        private const int Interval = 60;

        public ExplorationMapComponent(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager == null || Find.TickManager.TicksGame % Interval != 0) { return; }
            // Only ever a coordinate. There is nothing to explore in a colony and no room records to
            // explore it against.
            if (!(map.Parent is RimroomsDestinationMapParent)) { return; }
            FirstSliceSiteComponent site = map.GetComponent<FirstSliceSiteComponent>();
            CoordinateRecord coordinate = site == null ? null : site.Coordinate;
            if (coordinate == null || coordinate.Rooms == null || coordinate.Rooms.Count == 0) { return; }

            IReadOnlyList<Pawn> pawns = map.mapPawns.FreeColonistsSpawned;
            for (int index = 0; index < pawns.Count; index++)
            {
                Pawn pawn = pawns[index];
                CompRimroomsExplorer explorer = pawn == null
                    ? null : pawn.TryGetComp<CompRimroomsExplorer>();
                if (explorer == null || !explorer.Exploring) { continue; }

                if (Complete(coordinate))
                {
                    // Reported once per pawn per coordinate, then the order releases itself: the
                    // owner's words are "until toggled off or completed", so completion is one of the
                    // two ways it ends rather than a state the player has to notice and clear.
                    if (!explorer.ReportedComplete)
                    {
                        explorer.NoteReportedComplete();
                        Announce(pawn, coordinate);
                    }
                    explorer.StopExploring();
                    continue;
                }

                // Busy pawns are left alone. This is what makes twenty seconds mean twenty seconds.
                if (pawn.CurJobDef != null && pawn.CurJobDef.defName == "RR_ExploreRoom") { continue; }
                if (pawn.Downed || pawn.InMentalState) { continue; }
                // **No book, no exploring, and the pawn is told rather than left standing.** The
                // survey is written into the record book; without one this would be a colonist
                // walking a maze to no effect, which is the exact shape of defect the owner reported
                // when pawns ran across a coordinate to plant a flower.
                if (!FirstSliceSiteComponent.CarriesRecordBook(pawn))
                {
                    explorer.StopExploring();
                    Messages.Message("RR_Explore_NoBook".Translate(pawn.LabelShortCap),
                        pawn, MessageTypeDefOf.RejectInput, false);
                    continue;
                }
                IssueNextRoom(pawn, coordinate);
            }
        }

        /// <summary>
        /// Whether every room that can be walked into has been written up.
        ///
        /// **PUBLIC AND STATIC BECAUSE TWO PLACES ASK IT, AND THEY DISAGREED FOR ONE BUILD.** The
        /// survey write-up's `SurveyComplete` precondition tested `room.Surveyed` on **every** room,
        /// which on any coordinate holding a sealed vault could never be true -- so the write-up this
        /// whole feature exists to unlock would have been permanently unwritable, and nothing would
        /// have said why. Caught by writing the second rule down beside the first.
        ///
        /// **Linkless rooms are excluded, exactly as the layout validator excludes them.** A sealed
        /// vault is authored with no doors on purpose and is reached by mining; counting it would make
        /// a coordinate that contains one permanently unfinished. The two places that ask this
        /// question now ask it the same way, which is the lesson the solo-start failure taught.
        /// </summary>
        public static bool Complete(CoordinateRecord coordinate)
        {
            for (int index = 0; index < coordinate.Rooms.Count; index++)
            {
                RoomRecord room = coordinate.Rooms[index];
                if (room == null) { continue; }
                if (room.Links == null || room.Links.Count == 0) { continue; }
                if (!room.Surveyed) { return false; }
            }
            return true;
        }

        /// <summary>
        /// Send the pawn to the nearest room it has not written up.
        ///
        /// Nearest by squared distance from where they stand, so a pawn works outward through the maze
        /// rather than crossing it and coming back. Ties break on room index, so the same situation
        /// resolves the same way on a reloaded save.
        /// </summary>
        private void IssueNextRoom(Pawn pawn, CoordinateRecord coordinate)
        {
            JobDef explore = DefDatabase<JobDef>.GetNamedSilentFail("RR_ExploreRoom");
            if (explore == null) { return; }
            RoomRecord best = null;
            IntVec3 bestCell = IntVec3.Invalid;
            int bestDistance = int.MaxValue;
            for (int index = 0; index < coordinate.Rooms.Count; index++)
            {
                RoomRecord room = coordinate.Rooms[index];
                if (room == null || room.Surveyed) { continue; }
                if (room.Links == null || room.Links.Count == 0) { continue; }
                IntVec3 cell = ReachableCellIn(pawn, room);
                if (!cell.IsValid) { continue; }
                int distance = pawn.Position.DistanceToSquared(cell);
                if (distance > bestDistance) { continue; }
                if (distance == bestDistance && best != null && room.Index >= best.Index) { continue; }
                best = room;
                bestCell = cell;
                bestDistance = distance;
            }
            // Nothing reachable and not yet complete means the rest is behind rock or a locked door.
            // Silence is right: the player can see where their pawn stopped, and the toggle is still
            // on so progress resumes the moment they open a way through.
            if (best == null || !bestCell.IsValid) { return; }
            Job job = JobMaker.MakeJob(explore, bestCell);
            pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
        }

        /// <summary>
        /// A cell in this room the pawn can actually stand on and reach.
        ///
        /// Walked from the centre outward in the rectangle's own order, so the target is stable across
        /// reloads, and **reachability is checked here rather than discovered on arrival** — a room
        /// whose only way in is unmined rock must not be chosen, or the pawn would path nowhere and
        /// the component would hand them the same room for ever.
        /// </summary>
        private IntVec3 ReachableCellIn(Pawn pawn, RoomRecord room)
        {
            CellRect bounds = room.Bounds;
            IntVec3 centre = bounds.CenterCell;
            if (Suitable(pawn, centre)) { return centre; }
            foreach (IntVec3 cell in bounds.Cells)
            {
                if (Suitable(pawn, cell)) { return cell; }
            }
            return IntVec3.Invalid;
        }

        private bool Suitable(Pawn pawn, IntVec3 cell)
        {
            return cell.IsValid && cell.InBounds(map) && cell.Standable(map)
                && pawn.CanReach(cell, PathEndMode.OnCell, Danger.Some);
        }

        /// <summary>
        /// The owner's own notice: *"PAwn radioed in exploration complete"*.
        ///
        /// A letter rather than a message, because it is the end of a job the player set in motion and
        /// may well have walked away from — a message that fades after four seconds would be missed by
        /// exactly the player this feature is for.
        /// </summary>
        private void Announce(Pawn pawn, CoordinateRecord coordinate)
        {
            Find.LetterStack.ReceiveLetter(
                "RR_Explore_CompleteTitle".Translate(),
                "RR_Explore_CompleteBody".Translate(pawn.LabelShortCap, coordinate.Label),
                LetterDefOf.PositiveEvent, new TargetInfo(pawn.Position, map));
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign != null && campaign.CanOperate)
            { campaign.RecordEvent("RR_Event_ExplorationComplete", coordinate.Id, coordinate.Label); }
        }
    }
}
