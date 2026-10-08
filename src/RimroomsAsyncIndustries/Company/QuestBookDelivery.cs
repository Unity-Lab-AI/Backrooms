using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// A book arrives for each accepted quest that wants paperwork.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"and the seend new journals after each quest
    /// finished/ starting new quests/missions, its almost like every book recieved needs to be tuned
    /// to or capable of listing the current quests its needed for that has been acceptred, with
    /// ability to accept more than one quests at a time"*.
    ///
    /// ## One delivery mechanism in this mod, not two
    ///
    /// This uses the **same** `DropPodUtility.DropThingsNear` call and the **same** relief drop cell
    /// `RecordBookDelivery` already uses, and marks the book company-issued at creation exactly as
    /// that route does. A second drop implementation would be a second place to fix the next time a
    /// drop lands somewhere wrong.
    ///
    /// ## Why it is driven by the record rather than fired at acceptance
    ///
    /// `AcceptRequest` could have dropped a book inline, and that would have been one line. It is
    /// here instead, on the company's own tick, asking *does every quest that wants paperwork have a
    /// book* — because **the condition is the thing that matters, not the moment.** A quest accepted
    /// while the drop failed, a book burned a week later, a save loaded from before this existed:
    /// each is a branch holding an obligation with no deliverable, and each is fixed by the same
    /// question being asked again. Firing at acceptance would have handled exactly one of the three.
    ///
    /// **It is not a tap.** A quest gets a book when it has none; `BookFor` is what decides, and a
    /// book already stamped for that quest is the answer. So the player cannot farm books by
    /// cancelling and re-accepting, and the corporation does not send a second one for a book
    /// somebody left on a shelf.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>How many quest books the corporation has sent. A record, never a limit.</summary>
        private int questBookDeliveries;

        internal void ExposeQuestBookDelivery()
        {
            Scribe_Values.Look(ref questBookDeliveries, "rr_questBookDeliveries", 0);
        }

        /// <summary>How many quest books this branch has been sent.</summary>
        public int QuestBookDeliveries { get { return questBookDeliveries; } }

        /// <summary>
        /// Checked on the company's cadence. Cheap in almost every call: a status comparison per
        /// quest, and the book scan only for a quest that actually wants paperwork.
        /// </summary>
        internal void TickQuestBookDelivery()
        {
            if (!corporationContact) { return; }
            Map map = headquarters;
            if (map == null || !Find.Maps.Contains(map)) { return; }
            ThingDef book = Expedition.ExpeditionCargo.RecordBookDef;
            // A null def means Core's book is missing or our comp never attached. Sending nothing is
            // right: a delivery of an unresolvable item is a letter about a crate that is not there.
            if (book == null) { return; }
            IReadOnlyList<RequestRecord> line = Requests;
            if (line == null) { return; }
            for (int index = 0; index < line.Count; index++)
            {
                RequestRecord request = line[index];
                if (request == null || request.Status != RequestStatus.Accepted) { continue; }
                // No paperwork, no deliverable, no book. Most quests are this.
                if (WriteUpsWanted(request).Count == 0) { continue; }
                if (BookFor(request) != null) { continue; }
                try { DeliverQuestBook(map, book, request); }
                catch (Exception error)
                {
                    // The condition stays true, so the next company tick tries again rather than
                    // leaving a branch unable to report with no way to find out why.
                    Log.Warning("[Rimrooms] quest book delivery could not complete for "
                        + request.Id + ": " + error);
                }
                // **One per tick, deliberately.** Accepting four quests at once should land four
                // pods over four company ticks rather than one crate holding four books, because a
                // book is bound to its quest and a player sorting a stack of identical-looking books
                // out of one pile is the opposite of helpful.
                return;
            }
        }

        private void DeliverQuestBook(Map map, ThingDef book, RequestRecord request)
        {
            Thing made = ThingMaker.MakeThing(book);
            if (made == null) { return; }
            CompRouteEvidence issued = made.TryGetComp<CompRouteEvidence>();
            // Marked and stamped before it is dropped. **Stamped at a tally of zero on purpose:**
            // the book is bound to the quest from the moment it exists, so `BookFor` can find it and
            // nothing has to go scanning for an unbound book to adopt later. The count rises as
            // paperwork is filed, through the one writer.
            if (issued != null)
            {
                issued.MarkCompanyIssued();
                issued.StampForQuest(request.Id, request.WriteUpsFiled.Count);
            }

            IntVec3 centre = ReliefDropCell(map);
            questBookDeliveries++;
            DropPodUtility.DropThingsNear(centre, map, new List<Thing> { made }, 110, false, false,
                true, forbid: false);

            RimroomsRequestDef definition = request.Definition;
            RecordEvent("RR_Event_QuestBookDelivery", request.Id,
                definition == null ? request.Id : definition.LabelCap.ToString());
            Find.LetterStack.ReceiveLetter(
                "RR_QuestBook_Title".Translate(),
                "RR_QuestBook_Body".Translate(CompanyName,
                    definition == null ? request.Id : definition.LabelCap.ToString()),
                LetterDefOf.PositiveEvent, new TargetInfo(centre, map));
        }
    }
}
