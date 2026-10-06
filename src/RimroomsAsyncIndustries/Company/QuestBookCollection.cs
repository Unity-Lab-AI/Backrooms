using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The company collects a finished book out of a beacon's radius.
    ///
    /// **Owner's fork answer, 2026-10-06**, asked how a finished book physically returns: **beacon
    /// radius pickup**, over a courier and over a dispatch through the gate.
    ///
    /// ## It costs nothing new, which is why it was the recommended option
    ///
    /// It reuses the contract `ValuablesExchange` and Core's own `OrbitalTradeBeacon` already
    /// have — *what is in the circle is what is on the table* — so a player learns no new idea and
    /// Core already draws the radius. **And the facility now ships eight beacons** where the owner
    /// placed them, so the delivery surface was already on the map before this existed.
    ///
    /// ## The two routes it was chosen over, and why each was worse
    ///
    /// **A courier** would have put the timing in the corporation's hands, so a player with a green
    /// light waits on something they cannot push. **A dispatch through the gate** would have cost a
    /// gate window, which is the mod's only scarce clock — paperwork would then compete with
    /// expeditions for it, and §1.1 exists to stop exactly that kind of creep.
    ///
    /// ## Three properties that follow from using a radius
    ///
    /// * **The player controls the timing.** A finished book may sit on a shelf indefinitely.
    ///   **§1.1 binds: there is no deadline on a write-up, ever.**
    /// * **It cannot pay twice.** Settlement runs through `PostTransaction` on the request's own
    ///   existing operation id, which is idempotent by construction.
    /// * **A book inside a radius by accident is still a choice the player made**, the same as
    ///   anything else left in a trade beacon's circle — and the collection letter names every quest
    ///   that went, so it is never silent.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Books collected, as a record rather than a limit.
        ///
        /// Saved because it is a thing that happened to the branch; nothing reads it as a cap.
        /// </summary>
        private int questBooksCollected;

        internal void ExposeQuestBookCollection()
        {
            Scribe_Values.Look(ref questBooksCollected, "rr_questBooksCollected", 0);
        }

        /// <summary>How many finished books the corporation has collected from this branch.</summary>
        public int QuestBooksCollected { get { return questBooksCollected; } }

        /// <summary>
        /// Collect every green book sitting in a designated beacon's radius.
        ///
        /// **A batch, in one pass, with one letter.** The owner's own model is a collection rather
        /// than a series of pickups, and three books hauled into a circle should go together.
        /// </summary>
        internal void TickQuestBookCollection()
        {
            if (!corporationContact || !CanOperate) { return; }
            Map map = headquarters;
            if (map == null || !Find.Maps.Contains(map)) { return; }

            var collected = new List<string>();
            IReadOnlyList<RequestRecord> line = Requests;
            if (line == null) { return; }
            for (int index = 0; index < line.Count; index++)
            {
                RequestRecord request = line[index];
                if (request == null || request.Status != RequestStatus.Accepted) { continue; }
                // **The light is the gate, and it is asked rather than re-derived.** `LightFor`
                // already decides whether the paperwork is complete, the book exists, agrees and is
                // in custody. Re-testing those four conditions here would be a second derivation of
                // the one question this whole subsystem is about.
                if (LightFor(request) != QuestLight.Green) { continue; }
                Thing book = BookFor(request);
                if (book == null || book.Map != map) { continue; }
                if (!InAnyCreditBeaconRadius(book)) { continue; }
                try
                {
                    if (CollectQuestBook(request, book)) { collected.Add(QuestLabel(request)); }
                }
                catch (Exception error)
                {
                    // Left for the next sweep. The book is still green and still in the radius, so
                    // the condition that brought it here is unchanged.
                    Log.Warning("[Rimrooms] quest book collection could not complete for "
                        + request.Id + ": " + error);
                }
            }
            if (collected.Count == 0) { return; }
            Find.LetterStack.ReceiveLetter(
                "RR_QuestBookCollected_Title".Translate(),
                "RR_QuestBookCollected_Body".Translate(CompanyName, collected.Count,
                    string.Join(", ", collected.ToArray())),
                LetterDefOf.PositiveEvent);
        }

        /// <summary>
        /// Whether this thing is inside the radius of a beacon the player designated for credit.
        ///
        /// **Asked of the designation rather than of every trade beacon on the map.** A player who
        /// has not designated a beacon has not asked the company to collect anything, and an
        /// undesignated trade beacon must keep behaving exactly as it always has — which is the same
        /// dormant-until-designated rule every other comp this mod patches on already follows.
        /// </summary>
        private bool InAnyCreditBeaconRadius(Thing item)
        {
            if (item == null || !item.Spawned || item.Map == null) { return false; }
            List<Building> buildings = item.Map.listerBuildings.allBuildingsColonist;
            for (int index = 0; index < buildings.Count; index++)
            {
                Building building = buildings[index];
                if (building == null || building.Destroyed) { continue; }
                Economy.CompRimroomsCreditBeacon beacon =
                    building.TryGetComp<Economy.CompRimroomsCreditBeacon>();
                if (beacon == null || !beacon.Designated) { continue; }
                if (item.Position.InHorDistOf(building.Position, beacon.Radius)) { return true; }
            }
            return false;
        }

        /// <summary>
        /// Settle the quest and take the book.
        ///
        /// **The payment is the request's own, through its own operation id**, so collecting a book
        /// twice — a sweep that overlaps, a save reloaded mid-pass — pays once. That idempotence is
        /// not added here; it is `PostTransaction`'s, and asking it is how this stays honest.
        ///
        /// **The book is destroyed rather than teleported.** It has gone to the corporation, and a
        /// book that vanishes from the map while the ledger says it was received is the truthful
        /// model. Keeping it would mean a branch holding a deliverable it had already been paid for.
        /// </summary>
        private bool CollectQuestBook(RequestRecord request, Thing book)
        {
            RimroomsRequestDef definition = request.Definition;
            long payment = definition == null ? 0L : definition.paymentUsd;
            string operationId = request.Id + ":paperwork-return";
            if (payment > 0L)
            {
                CompanyActionResult posted = PostTransaction(operationId, payment,
                    "RR_Ledger_PaperworkReturn", request.Id);
                // **A refused payment does not take the book.** The player would otherwise lose the
                // deliverable and the money, and the next sweep can try again with it still green.
                if (!posted.Success) { return false; }
            }
            // Cleared so the book is no longer anybody's deliverable before it stops existing. A
            // stamp left on a destroyed thing is harmless, but a stamp cleared first means nothing
            // can ever find a half-collected book.
            CompRouteEvidence stamp = book.TryGetComp<CompRouteEvidence>();
            if (stamp != null) { stamp.ClearQuestStamp(); }
            book.Destroy(DestroyMode.Vanish);
            questBooksCollected++;
            RecordEvent("RR_Event_QuestBookCollected", request.Id, payment.ToString("N0"));
            return true;
        }

        /// <summary>The quest's own label for a letter, or its id when the def is gone.</summary>
        private static string QuestLabel(RequestRecord request)
        {
            RimroomsRequestDef definition = request == null ? null : request.Definition;
            return definition == null
                ? (request == null ? "?" : request.Id)
                : definition.LabelCap.ToString();
        }
    }
}
