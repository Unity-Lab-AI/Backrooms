using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The four things a branch can decide to do with what it brought back, other than sell it.
    ///
    /// **Owner direction, verbatim:** *"Make sale/study/use/contain/release/recruit/detain/transfer
    /// choices visible with financial, staff, faction, legal-in-world, trust, and security
    /// consequences"*.
    ///
    /// Sale shipped through the valuables exchange, study through analysis, recruit through
    /// hiring. **Contain, release and transfer did not exist**, and `detain` is on
    /// `CompRimroomsSurvivor` because it belongs to a person rather than to a record.
    ///
    /// ## Each one has a consequence a player can feel, which is the whole row
    ///
    /// A choice with no consequence is a label. So:
    ///
    /// | Choice | What it actually costs or buys |
    /// |---|---|
    /// | **Contain** | A **daily charge, forever**, on its own ledger line. Keeps the thing and keeps it out of the exchange. |
    /// | **Release** | Pays nothing and closes the record. The thing is not there any more. |
    /// | **Transfer** | Pays **less than the exchange would** and the thing is gone. What it buys is the corporation having it. |
    ///
    /// The containment charge is modelled on `DailyRemoteSiteOverheadUsd` deliberately, down to
    /// having **its own obligation line rather than being folded into overhead** — the same
    /// reasoning: *"so the player can see on the ledger what the places are costing them and
    /// decide whether to keep them"*. A branch that contains everything it finds should be able
    /// to watch itself going broke and know why.
    ///
    /// ## Transfer pays less than sale, and that is the point
    ///
    /// If transfer paid the same, it would be sale with extra words. It pays
    /// <see cref="TransferRate"/> of the exchange's ordinary rate, so choosing it is choosing to
    /// take less — which only makes sense when the player wants the thing off the branch's books
    /// without putting it on the open market. That is the *legal-in-world* consequence the row
    /// asks for, expressed as a price rather than as a paragraph.
    ///
    /// ## No release fee, ever
    ///
    /// The queue row on leasing states it and it applies here: *"A release fee must never be
    /// added — a cost for changing your mind is the same trap in a different coat."* Releasing
    /// something costs nothing. It simply pays nothing either.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// Share of the branch's daily overhead each contained record costs, as a divisor.
        ///
        /// Twenty, so a branch with a typical overhead pays a small amount per item and a branch
        /// hoarding twenty of them is paying a second overhead. Deliberately derived from the
        /// branch's own overhead rather than a flat figure, exactly like the remote-site share:
        /// a figure in credits would be meaningless across the five scenario budgets.
        /// </summary>
        private const long ContainmentOverheadDivisor = 20L;

        /// <summary>What a transfer pays, against what the exchange would have paid.</summary>
        public const float TransferRate = 0.6f;

        /// <summary>Every record the branch is currently holding in containment.</summary>
        public IEnumerable<EvidenceRecord> ContainedRecords()
        {
            return evidence.Where(record => record != null
                && record.Disposition == EvidenceDisposition.Contained);
        }

        /// <summary>
        /// What containment costs the branch per day.
        ///
        /// Zero for a branch containing nothing, which is every branch until somebody decides to
        /// contain something — the same shape as `DailyRemoteSiteOverheadUsd` and for the same
        /// reason: a line that is always zero teaches the player nothing.
        /// </summary>
        public long DailyContainmentUsd
        {
            get
            {
                if (dailyOverheadUsd <= 0) { return 0L; }
                long each = dailyOverheadUsd / ContainmentOverheadDivisor;
                if (each <= 0L) { return 0L; }
                return each * ContainedRecords().Count();
            }
        }

        /// <summary>
        /// Why a disposition cannot be decided for this record, or null if it can.
        ///
        /// Split from the action for the reason every other check in this mod is: a candidate
        /// test and a definitive action are two different questions, and merging them hides
        /// which one failed.
        /// </summary>
        public string DispositionFailureKey(EvidenceRecord record)
        {
            if (!CanOperate) { return stateFaultKey ?? "RR_Disposition_Inactive"; }
            if (record == null || !evidence.Contains(record))
            { return "RR_Disposition_RecordUnavailable"; }
            // **The branch has to actually have the thing.** A record that is still out there, or
            // one somebody lost, is not something anybody can decide the fate of.
            if (record.Status != EvidenceStatus.Secured && record.Status != EvidenceStatus.Analyzed)
            { return "RR_Disposition_NotRecovered"; }
            if (record.Disposition != EvidenceDisposition.None)
            { return "RR_Disposition_AlreadyDecided"; }
            return null;
        }

        /// <summary>
        /// Keeps the thing, secured, off the market — and starts paying for it every day.
        ///
        /// Nothing is destroyed and nothing is paid out. The consequence is entirely the standing
        /// charge, which is what makes containment a decision rather than a default.
        /// </summary>
        public CompanyActionResult ContainRecord(EvidenceRecord record)
        {
            string failure = DispositionFailureKey(record);
            if (failure != null) { return CompanyActionResult.Refused(failure); }
            record.MarkDisposition(EvidenceDisposition.Contained, Find.TickManager.TicksGame);
            RecordEvent("RR_Event_RecordContained", record.Id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Puts it back. Pays nothing, costs nothing, and closes the record.
        ///
        /// **The item is destroyed rather than left standing**, because "released" has to mean
        /// the thing is not here any more — a record marked released with the book still sitting
        /// on the shelf would be a lie the player could see. Destroyed only when the branch
        /// physically holds it; a record whose item reference has already gone is simply marked.
        /// </summary>
        public CompanyActionResult ReleaseRecord(EvidenceRecord record)
        {
            string failure = DispositionFailureKey(record);
            if (failure != null) { return CompanyActionResult.Refused(failure); }
            DisposeOfItem(record);
            record.MarkDisposition(EvidenceDisposition.Released, Find.TickManager.TicksGame);
            RecordEvent("RR_Event_RecordReleased", record.Id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Destroys it. The owner's *"destruction choice"*.
        ///
        /// **The one disposition that needs nothing.** Containment needs money every day,
        /// transfer needs the corporation on the line, and release needs the thing to have
        /// somewhere to go back to. Destroying needs none of those, which is why a branch that
        /// has run out of options still has this one — and why it had to exist separately from
        /// release rather than being folded into it.
        ///
        /// **It is also the only disposition that may be taken on a contained record**, through
        /// <see cref="DestroyFromContainment"/>. A branch that contained something and then found
        /// it could not afford to keep doing so must have a way out that is not an exploit, and
        /// paying nothing for it is not an exploit.
        /// </summary>
        public CompanyActionResult DestroyRecord(EvidenceRecord record)
        {
            string failure = DispositionFailureKey(record);
            if (failure != null) { return CompanyActionResult.Refused(failure); }
            DisposeOfItem(record);
            record.MarkDisposition(EvidenceDisposition.Destroyed, Find.TickManager.TicksGame);
            RecordEvent("RR_Event_RecordDestroyed", record.Id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Destroys something the branch had already decided to contain.
        ///
        /// **The one exception to dispositions being one-way**, and it is a deliberate one. A
        /// containment charge runs every day forever; without a way out, a player who contained
        /// something early and then needed the money would be paying for a decision they made
        /// before they understood the cost. That is the same trap *"a release fee must never be
        /// added"* exists to refuse, in the other direction.
        ///
        /// It moves `Contained` to `Destroyed` rather than back to `None`, because the thing
        /// still has to go somewhere and un-deciding is what would make the consequences
        /// meaningless. **And it pays nothing**, which is why it cannot be used to launder a
        /// contained record into money: the only way to be paid is to have chosen transfer or the
        /// exchange in the first place.
        /// </summary>
        public CompanyActionResult DestroyFromContainment(EvidenceRecord record)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Disposition_Inactive"); }
            if (record == null || !evidence.Contains(record))
            { return CompanyActionResult.Refused("RR_Disposition_RecordUnavailable"); }
            if (record.Disposition != EvidenceDisposition.Contained)
            { return CompanyActionResult.Refused("RR_Disposition_NotContained"); }
            DisposeOfItem(record);
            record.MarkDisposition(EvidenceDisposition.Destroyed, Find.TickManager.TicksGame);
            RecordEvent("RR_Event_RecordDestroyed", record.Id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Hands it to the parent corporation, for less than the exchange would have paid.
        ///
        /// **Requires the branch to be in contact**, which is the one refusal here that is about
        /// the fiction as much as the mechanism: there is nobody to hand it to otherwise. That
        /// contact state already exists and is already surfaced on the console.
        /// </summary>
        public CompanyActionResult TransferRecord(EvidenceRecord record)
        {
            string failure = DispositionFailureKey(record);
            if (failure != null) { return CompanyActionResult.Refused(failure); }
            if (!CorporationContact) { return CompanyActionResult.Refused("RR_Disposition_NoContact"); }

            long paid = TransferValueOf(record);
            if (paid > 0L)
            {
                CompanyActionResult posted = PostTransaction("rr_transfer:" + record.Id, paid,
                    "RR_Ledger_RecordTransfer", record.Id);
                // A refused posting leaves the record undecided rather than transferring it for
                // nothing. The thing is only handed over once the money is on the books.
                if (!posted.Success) { return posted; }
            }
            DisposeOfItem(record);
            record.MarkDisposition(EvidenceDisposition.Transferred, Find.TickManager.TicksGame);
            RecordEvent("RR_Event_RecordTransferred", record.Id, paid.ToString("N0"));
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// What the corporation pays for a record, which is deliberately less than its worth.
        ///
        /// Read off the thing's own market value through Core's `MarketValue`, so a mod item is
        /// valued by whatever the game says it is worth and nothing here keeps a price list.
        /// Zero when the record has no item left to value, and a transfer then simply pays
        /// nothing rather than being refused — the corporation still takes the paperwork.
        /// </summary>
        public long TransferValueOf(EvidenceRecord record)
        {
            Thing item = record == null ? null : record.Item;
            if (item == null || item.Destroyed) { return 0L; }
            // **Confidence moves the price, which is what makes the score load-bearing rather
            // than a readout.** The corporation pays more for a finding the branch can stand
            // behind than for a book somebody carried out of a room, and the owner's row pairs
            // *confidence* with *value* on one line for exactly that reason.
            float value = item.MarketValue * item.stackCount * OrdinaryExchangeRate * TransferRate
                * ConfidenceValueFactor(record);
            return value <= 0f ? 0L : (long)value;
        }

        /// <summary>
        /// Removes the physical thing a decided record referred to, if the branch still has it.
        ///
        /// Shared by release and transfer because both mean *it is not here any more*, and two
        /// copies of that would be two chances to leave an item standing behind a record that
        /// says it is gone.
        /// </summary>
        private static void DisposeOfItem(EvidenceRecord record)
        {
            Thing item = record == null ? null : record.Item;
            if (item == null || item.Destroyed) { return; }
            item.Destroy(DestroyMode.Vanish);
        }

        /// <summary>
        /// Containment's own line on the daily bill.
        ///
        /// Called from the operating-cost tick beside payroll, overhead and remote sites.
        /// </summary>
        internal void AddContainmentObligation(string dayId, int dueTick)
        {
            ReconcileContainedCustody();
            AddObligation(dayId + ":containment", "RR_Ledger_Containment",
                DailyContainmentUsd, dueTick);
        }
        /// <summary>
        /// Ends containment for every record whose thing the branch no longer holds, so the
        /// daily charge stops with it.
        ///
        /// Containment only bills while the branch keeps the thing. A thing destroyed by any
        /// route -- fire, a raid, a mod, a trader taking it -- leaves the record contained and
        /// billing for nothing unless this runs. Run before each day's charge is raised. Lost
        /// custody is read conservatively: only a destroyed thing, or one now held by another
        /// faction's pawn, a passing ship or a settlement's stock, counts as gone.
        /// </summary>
        internal void ReconcileContainedCustody()
        {
            List<EvidenceRecord> contained = ContainedRecords().ToList();
            for (int index = 0; index < contained.Count; index++)
            {
                EvidenceRecord record = contained[index];
                if (StillHeldByBranch(record.Item)) { continue; }
                record.MarkDisposition(EvidenceDisposition.Destroyed, Find.TickManager.TicksGame);
                RecordEvent("RR_Event_ContainmentEnded", record.Id);
            }
        }

        private static bool StillHeldByBranch(Thing item)
        {
            if (item == null || item.Destroyed) { return false; }
            for (IThingHolder holder = item.ParentHolder; holder != null; holder = holder.ParentHolder)
            {
                Pawn pawn = holder as Pawn;
                if (pawn != null && pawn.Faction != Faction.OfPlayer && !pawn.IsPrisonerOfColony) { return false; }
                if (holder is PassingShip) { return false; }
                RimWorld.Planet.Settlement settlement = holder as RimWorld.Planet.Settlement;
                if (settlement != null && settlement.Faction != Faction.OfPlayer) { return false; }
                if (holder is Map) { return true; }
            }
            return true;
        }
    }
}
