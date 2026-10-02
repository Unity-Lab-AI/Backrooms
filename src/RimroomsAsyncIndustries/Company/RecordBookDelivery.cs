using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The corporation sends a record book to a branch that has built a gate and has none.
    ///
    /// **Owner direction, 2026-10-01, verbatim:** *"make sure the other scenerios properly get the
    /// book in a drop when they need it and start the quest to go through their built gate"*.
    ///
    /// ## Why this has to exist at all
    ///
    /// `ExpeditionCargo.RecordBooksRequired` is one `TextBook`, and **no start except the
    /// laboratory ships one.** The Store spawns 27 fixtures and no book; the solo start spawns
    /// nothing at all. So a player who builds a gate from nothing hits
    /// `RR_Exp_MissingRecordBook` on their first dispatch with no idea what a record book is or
    /// where one comes from.
    ///
    /// The owner found exactly that on the laboratory start, which shipped no book either:
    /// *"if i use approach gate and dispach to coordinate it says no book, i have no books"*.
    /// The laboratory start now carries two. **This is the answer for the starts that cannot.**
    ///
    /// ## Deterministic, not an incident
    ///
    /// Same reasoning as the clean-up team: *"a promise must not be at the mercy of a dice
    /// roll"*. A player who has built and calibrated a gate has met the condition, so the book
    /// arrives. The storyteller-paced courier in `RimroomsIncidents` still exists and still
    /// brings the ordinary crate; it is not the thing that unblocks a first expedition.
    ///
    /// ## When it fires, and why each condition is there
    ///
    /// | Condition | Why |
    /// |---|---|
    /// | in corporation contact | *"clena up tema is only once u are in communication and working with the corporation"*. Nothing arrives from a corporation that has not heard of this branch |
    /// | a designated, calibrated gate | the player has done the work this is a reward for. Before that a book is a mystery item with no use |
    /// | **no book anywhere on any owned map** | the corporation does not send a second one. A branch that has a book, or made one, or bought one, gets nothing |
    ///
    /// **It can fire more than once, and that is deliberate.** Burn the book, lose it in a
    /// coordinate, leave it on a crew who did not come back — and the branch is blocked again
    /// through no fault it can fix. The no-book-anywhere test is what stops it being a tap: it
    /// cannot send a second while the first still exists.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How many books come in a delivery. **Two**, the same as the laboratory start ships:
        /// one to take into the field and one in reserve, because a branch that loses its only
        /// book is blocked until it makes another.
        /// </summary>
        private const int RecordBookDeliveryCount = 2;

        /// <summary>How many books the corporation has sent. A record, never a limit.</summary>
        private int recordBookDeliveries;

        /// <summary>When the last one arrived. History, not a countdown.</summary>
        private int lastRecordBookDeliveryTick = -1;

        internal void ExposeRecordBookDelivery()
        {
            Scribe_Values.Look(ref recordBookDeliveries, "rr_recordBookDeliveries", 0);
            Scribe_Values.Look(ref lastRecordBookDeliveryTick, "rr_lastRecordBookDeliveryTick", -1);
        }

        /// <summary>How many record books the corporation has sent this branch.</summary>
        public int RecordBookDeliveries { get { return recordBookDeliveries; } }

        /// <summary>
        /// Whether this branch has a gate it has actually finished.
        ///
        /// **Calibrated, not merely designated.** A designated door is a decision; a calibrated
        /// one is a machine that will open. Sending the book at designation would put it in a
        /// player's lap before they had anything to use it on.
        /// </summary>
        private bool HasFinishedGate()
        {
            List<Map> maps = Find.Maps;
            if (maps == null) { return false; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map.listerBuildings == null || !OwnsMap(map)) { continue; }
                List<Building> buildings = map.listerBuildings.allBuildingsColonist;
                for (int item = 0; item < buildings.Count; item++)
                {
                    Building building = buildings[item];
                    if (building == null || building.Destroyed) { continue; }
                    Gate.CompRimroomsGate gate = building.TryGetComp<Gate.CompRimroomsGate>();
                    if (gate != null && gate.IsDesignated && gate.Calibrated) { return true; }
                }
            }
            return false;
        }

        /// <summary>
        /// Whether a record book exists anywhere this branch can reach — on a floor, in a shelf,
        /// in somebody's pack, on either side of a connection.
        ///
        /// **Resolved through `ExpeditionCargo.RecordBookDef`**, never by name, so the one
        /// question *is this the thing a dispatch will accept* has a single answer. Asking by
        /// def name here and by comp there is how a branch ends up holding a book the dispatch
        /// refuses.
        /// </summary>
        private bool AnyRecordBookHeld(ThingDef book)
        {
            if (book == null) { return true; }
            List<Map> maps = Find.Maps;
            if (maps == null) { return false; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || !OwnsMap(map)) { continue; }
                if (map.listerThings != null
                    && map.listerThings.ThingsOfDef(book).Count > 0)
                { return true; }
                // A book in a pack is a book the branch has. `AllPawnsSpawned` covers the crew
                // standing on either side of an open connection, because both maps are owned.
                if (map.mapPawns == null) { continue; }
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int item = 0; item < pawns.Count; item++)
                {
                    Pawn pawn = pawns[item];
                    if (pawn == null || pawn.inventory == null
                        || pawn.inventory.innerContainer == null)
                    { continue; }
                    if (pawn.inventory.innerContainer.Contains(book)) { return true; }
                }
            }
            return false;
        }

        /// <summary>
        /// Checked on the company's own cadence. Cheap in almost every call: a bool, then a
        /// scan that stops at the first book.
        /// </summary>
        internal void TickRecordBookDelivery()
        {
            if (!corporationContact) { return; }
            Map map = headquarters;
            if (map == null || !Find.Maps.Contains(map)) { return; }
            ThingDef book = Expedition.ExpeditionCargo.RecordBookDef;
            // A null def means Core's book is missing or our comp never attached. Sending
            // nothing is right: a delivery of an unresolvable item is a letter about a crate
            // that is not there.
            if (book == null) { return; }
            if (!HasFinishedGate()) { return; }
            if (AnyRecordBookHeld(book)) { return; }
            try { DeliverRecordBooks(map, book); }
            catch (Exception error)
            {
                // The condition stays true, so the next company tick tries again rather than
                // leaving a branch unable to dispatch with no way to find out why.
                Log.Warning("[Rimrooms] record book delivery could not complete: " + error);
            }
        }

        private void DeliverRecordBooks(Map map, ThingDef book)
        {
            var payload = new List<Thing>();
            for (int index = 0; index < RecordBookDeliveryCount; index++)
            {
                Thing made = ThingMaker.MakeThing(book);
                if (made != null) { payload.Add(made); }
            }
            // Nothing was made, so nothing is recorded and the next tick tries again. A letter
            // announcing an empty crate is worse than silence.
            if (payload.Count == 0) { return; }

            IntVec3 centre = ReliefDropCell(map);
            recordBookDeliveries++;
            lastRecordBookDeliveryTick = Find.TickManager.TicksGame;

            DropPodUtility.DropThingsNear(centre, map, payload, 110, false, false, true,
                forbid: false);

            RecordEvent("RR_Event_RecordBookDelivery", BranchId);
            Find.LetterStack.ReceiveLetter(
                "RR_BookDrop_Title".Translate(),
                "RR_BookDrop_Body".Translate(CompanyName, payload.Count),
                LetterDefOf.PositiveEvent, new TargetInfo(centre, map));
        }
    }
}
