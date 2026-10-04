using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What happens to a branch's places when it stops paying for them.
    ///
    /// **Owner direction, verbatim:** *"Add space leasing/claiming with cost, boundaries, term,
    /// access/security requirements, maintenance, renewal, eviction, and exit/abandonment
    /// consequences"*. Cost, boundaries, access requirements, maintenance and the exit
    /// consequences all shipped. **Renewal and eviction are here. Term is refused, and that is
    /// the interesting part.**
    ///
    /// ## TERM IS SUPERSEDED BY §1.1, AND IS NOT BUILT
    ///
    /// `docs/CAMPAIGN_CHART.md` §1.1 is absolute and checker-enforced: *"A gate's connection has
    /// a duration. **Nothing else in this mod has a duration.**"* The owner's words behind it were
    /// *"nothing ever ever have time restripctions but the gate"*, and the section says in so
    /// many words what that forbids: **no expiry on a mission, quest, offer, contract, quote or
    /// trade**, and *"no countdown on anything a player is asked to do"*.
    ///
    /// A lease term is a countdown on a thing the player is asked to maintain. **So there is no
    /// term, there will not be one, and this is where that is recorded** — the same way the chart
    /// records *"timed distortion investigations"* from four prep documents as **superseded**
    /// rather than quietly dropping them. A row asking for something a LAW forbids is answered by
    /// saying so, not by building a smaller version of it.
    ///
    /// ## Eviction is a consequence, not a clock, and that is what makes it allowed
    ///
    /// §1.1 permits the gate's window precisely because *"it is the consequence of things the
    /// player controls"* — power, tech, maintenance, workforce — and every one of those is
    /// *"a thing the player can see, understand and act on"*. Eviction is built to that same
    /// test: a site goes **only** because the branch did not pay for it, the unpaid bill is on
    /// the ledger where the player can read it, paying clears it, and nothing is ever taken from
    /// a branch that is paying its way.
    ///
    /// **No time passing ever evicts anybody.** A branch that keeps paying keeps its places for
    /// ever.
    ///
    /// ## Renewal costs nothing, because a fee for recovering is the same trap
    ///
    /// *"A release fee must never be added — a cost for changing your mind is the same trap in a
    /// different coat"* is on the owner's own row, and `ReleaseRemoteSite` already honours it.
    /// Re-registering an evicted place is the same shape: the branch has already been punished by
    /// losing the place and by owing the money. **Charging again for the recovery would be
    /// charging twice for one mistake.** So renewal is the ordinary registration, refused only
    /// while the arrears that caused the eviction are still outstanding — which is a condition
    /// the player clears by paying, not by waiting.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How many operating days of unpaid site bills the corporation tolerates.
        ///
        /// Three, and deliberately more than one: a branch that is briefly short should not lose
        /// a place over a single bad day, and the player needs enough warning on the ledger to
        /// act. The arrears event already fires on the first missed payment.
        /// </summary>
        internal const int ArrearsBeforeEviction = 3;

        /// <summary>
        /// Unpaid obligations the branch owes for the places it runs.
        ///
        /// Counted by reason rather than by amount, so the count means *days missed* and nothing
        /// else. Containment is excluded on purpose: failing to pay for containment loses the
        /// money, not the sites.
        /// </summary>
        public int SiteArrearsCount
        {
            get
            {
                if (obligations == null) { return 0; }
                return obligations.Count(obligation => obligation != null && !obligation.paid
                    && obligation.reasonKey == "RR_Ledger_RemoteSites");
            }
        }

        /// <summary>Whether the branch is far enough behind for the corporation to act.</summary>
        public bool FacingEviction
        {
            get { return SiteArrearsCount >= ArrearsBeforeEviction && LiveRemoteSiteCount > 0; }
        }

        /// <summary>
        /// Takes one place off the branch, if it has stopped paying for its places.
        ///
        /// **One, not all of them, and the most recently acquired one.** Taking everything at
        /// once would turn a cash-flow problem into a campaign-ending event with no step in
        /// between, and the newest place is the one the branch had least reason to be holding —
        /// so the branch keeps the site it has run longest, which is the one its operation is
        /// actually built around.
        ///
        /// Returns whether anything was taken, so the caller does not have to ask twice.
        /// </summary>
        internal bool EvictOnePlace()
        {
            if (!CanOperate || !FacingEviction) { return false; }
            RemoteSiteRecord newest = null;
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record == null || !record.Live) { continue; }
                if (newest == null || record.registeredTick > newest.registeredTick)
                { newest = record; }
            }
            if (newest == null) { return false; }

            string id = newest.id;
            string label = newest.label;
            remoteSites.Remove(newest);
            // Recorded as an eviction rather than as a release: the branch did not choose this,
            // and a history that cannot tell the two apart is a history that lies about what
            // happened.
            RecordEvent("RR_Event_RemoteSiteEvicted", id, label ?? "");
            Find.LetterStack.ReceiveLetter(
                "RR_Site_EvictedLabel".Translate(),
                "RR_Site_EvictedText".Translate(label ?? id, SiteArrearsCount.ToString()),
                LetterDefOf.NegativeEvent);
            return true;
        }

        /// <summary>
        /// Why a place cannot be put back on the books right now, or null.
        ///
        /// **This is renewal**, and it is the ordinary registration with one extra condition:
        /// clear what is owed first. A branch that re-registered a place while still in arrears
        /// would be adding a bill it has already proved it cannot pay, and the corporation
        /// declining that is the only reading that makes sense from either side.
        /// </summary>
        public string RenewalFailureKey()
        {
            return SiteArrearsCount > 0 ? "RR_Site_ArrearsOutstanding" : null;
        }
    }
}
