using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// A place the branch runs that is not its headquarters.
    ///
    /// **Arc 5, "Build beyond headquarters"**, from `CAMPAIGN_CONTENT_CATALOG.md`:
    ///
    /// > *"Remote sites need people, supplies, signals, protection, and an exit plan... **A remote
    /// > base is a costly responsibility rather than free map ownership.**"*
    ///
    /// That last sentence is the whole design, and it decides the shape: **registration is the
    /// act, and the bill is the consequence.** A map the player happens to hold is not a branch
    /// site until somebody puts it on the books, and once it is on the books it costs every day
    /// until it comes off.
    /// </summary>
    public sealed class RemoteSiteRecord : IExposable
    {
        internal string id;
        internal MapParent site;
        internal string label;
        internal int registeredTick;

        public string Id { get { return id; } }
        public MapParent Site { get { return site; } }
        public int RegisteredTick { get { return registeredTick; } }

        /// <summary>What to call it. The world object's own name, or the saved one if it is gone.</summary>
        public string Label
        {
            get
            {
                if (site != null && !string.IsNullOrEmpty(site.LabelCap)) { return site.LabelCap; }
                return string.IsNullOrEmpty(label) ? id : label;
            }
        }

        /// <summary>
        /// Whether the site is somewhere the branch can actually reach right now.
        ///
        /// Checked live rather than trusted from the record, for the same reason every other
        /// live check in this mod is: a world object can be destroyed, a map can be abandoned,
        /// and a record that outlived its place should stop counting rather than wait for
        /// somebody to notice.
        /// </summary>
        public bool Live
        {
            get
            {
                return site != null && !site.Destroyed && site.HasMap && site.Map != null &&
                    Find.Maps.Contains(site.Map);
            }
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_References.Look(ref site, "rr_site");
            Scribe_Values.Look(ref label, "rr_label");
            Scribe_Values.Look(ref registeredTick, "rr_registeredTick");
        }
    }

    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How many sites a branch may hold beyond its headquarters.
        ///
        /// A cap rather than a limit on ambition: it bounds the saved list and the daily billing
        /// loop, both of which are walked every operating day. Eight is well past what the
        /// arc's *"costly responsibility"* economy makes comfortable, so a player meets the bill
        /// long before they meet this.
        /// </summary>
        internal const int MaximumRemoteSites = 8;

        /// <summary>
        /// What the cap becomes once a branch has earned the room for more.
        ///
        /// **Tier 3 is "remote operations: support more than one site".** At 0.12.5-dev this
        /// branch had nothing to move, because remote sites did not exist yet; arc 5 wrote them.
        /// The unlock is observable in the one place a player already reads the cap — the Sites
        /// pane says *"3 of 8"*, and afterwards it says *"3 of 12"* — and in the refusal
        /// `RR_Site_TooMany` stopping.
        /// </summary>
        internal const int ExpandedRemoteSites = 12;

        /// <summary>
        /// What each site adds to the daily overhead, as a share of the branch's base overhead.
        ///
        /// **A ratio and not a number, deliberately.** Async Industries runs on $25,000 a day of
        /// overhead and the Store on $1,500; one absolute surcharge would be a rounding error for
        /// one and ruinous for the other. A quarter of base overhead per site means the cost of
        /// holding a place is always proportionate to the operation holding it, and every start
        /// tunes it for free by tuning the number it already had.
        /// </summary>
        internal const int RemoteSiteOverheadDivisor = 4;

        /// <summary>
        /// A better divisor: each site costs a sixth of base overhead instead of a quarter.
        ///
        /// **Commerce tier 3.** A ratio rather than an absolute, for the same reason the base
        /// divisor is one: Async Industries runs on $25,000 a day of overhead and the Store on
        /// $1,500, so one flat discount would be a rounding error for one and transformative for
        /// the other. Observable on the Sites pane, which already prints the daily figure.
        /// </summary>
        internal const int EfficientRemoteSiteOverheadDivisor = 6;

        /// <summary>
        /// How many sites this branch may hold, which a completed project raises.
        ///
        /// **One method, both readers.** The service refusal and the Sites pane readout both come
        /// through here, so the number a player is shown and the number that refuses them can
        /// never disagree -- the same discipline as the gate's idle draw.
        /// </summary>
        public int RemoteSiteCap
        {
            get
            {
                return HasCapability("RR_Cap_SiteNetwork") ? ExpandedRemoteSites : MaximumRemoteSites;
            }
        }

        /// <summary>The divisor in force, which a completed project improves.</summary>
        private int OverheadDivisorInForce
        {
            get
            {
                return HasCapability("RR_Cap_SiteEfficiency")
                    ? EfficientRemoteSiteOverheadDivisor : RemoteSiteOverheadDivisor;
            }
        }

        private List<RemoteSiteRecord> remoteSites = new List<RemoteSiteRecord>();

        internal void ExposeRemoteSites()
        {
            Scribe_Collections.Look(ref remoteSites, "rr_remoteSites", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && remoteSites == null)
            { remoteSites = new List<RemoteSiteRecord>(); }
        }

        public IReadOnlyList<RemoteSiteRecord> RemoteSites { get { return remoteSites; } }

        /// <summary>Sites currently reachable. The bill is charged on these, never on a lost one.</summary>
        public int LiveRemoteSiteCount
        {
            get { return remoteSites.Count(record => record != null && record.Live); }
        }

        /// <summary>
        /// What holding the branch's sites adds to a day's overhead.
        ///
        /// Zero for a branch with none, which is every branch at the start of every scenario. That
        /// is the honest answer and it is why this is worth having: **free map ownership is the
        /// thing the arc says must not exist**, so the moment a player takes a second place the
        /// number stops being zero.
        /// </summary>
        public long DailyRemoteSiteOverheadUsd
        {
            get
            {
                if (dailyOverheadUsd <= 0) { return 0L; }
                long each = dailyOverheadUsd / OverheadDivisorInForce;
                if (each <= 0L) { return 0L; }
                return each * LiveRemoteSiteCount;
            }
        }

        /// <summary>
        /// Put a map on the books as a branch site.
        ///
        /// ## What may be registered, and what may not
        ///
        /// **Not the headquarters.** It is already the branch's own place and already billed.
        ///
        /// **Not a Backrooms coordinate.** A coordinate is a destination, not a base: it is
        /// reached through a gate, it is not the player's to keep, and charging rent on one would
        /// be wrong on its own terms. This is the distinction that made the naive version of this
        /// feature compute a surcharge of zero and call it progress.
        ///
        /// **Only a place the player already holds.** Nothing here acquires anything. RimWorld
        /// already lets a colony settle a second tile, and this mod's own topology already lets a
        /// crew come out of the Backrooms somewhere else. **Acquisition is the game's; recognition
        /// is ours.** A mod that invented its own settling would be fighting Core for no reason.
        /// </summary>
        public CompanyActionResult RegisterRemoteSite(Map map)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            if (map == null || !Find.Maps.Contains(map))
            { return CompanyActionResult.Refused("RR_Site_MapUnavailable"); }
            if (map == headquarters) { return CompanyActionResult.Refused("RR_Site_IsHeadquarters"); }
            if (map.Parent is RimroomsDestinationMapParent)
            { return CompanyActionResult.Refused("RR_Site_CoordinateNotASite"); }
            MapParent parent = map.Parent;
            if (parent == null || parent.Destroyed || parent.Faction != Faction.OfPlayer)
            { return CompanyActionResult.Refused("RR_Site_NotYours"); }

            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord existing = remoteSites[index];
                if (existing != null && existing.site == parent) { return CompanyActionResult.Existing(); }
            }
            if (remoteSites.Count >= RemoteSiteCap)
            { return CompanyActionResult.Refused("RR_Site_TooMany"); }
            // **RENEWAL.** Owner's row: *"...maintenance, renewal, eviction..."*. Putting a place
            // back on the books is the ordinary registration -- there is no renewal fee, for the
            // same reason there is no release fee: *"a cost for changing your mind is the same
            // trap in a different coat"*, and a branch that has lost a place and still owes for
            // it has already paid twice. The one condition is that what is owed is cleared
            // first, which the player does by paying rather than by waiting.
            string arrears = RenewalFailureKey();
            if (arrears != null) { return CompanyActionResult.Refused(arrears); }

            string id = branchId + ":site:" + parent.ID;
            remoteSites.Add(new RemoteSiteRecord
            {
                id = id,
                site = parent,
                label = parent.LabelCap,
                registeredTick = Find.TickManager.TicksGame,
            });
            RecordEvent("RR_Event_RemoteSiteRegistered", id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Take a site off the books.
        ///
        /// **No penalty and no notice period.** Nothing in this mod has a deadline but the gate
        /// (`docs/CAMPAIGN_CHART.md` §1.1), and a release fee would be a deadline's cousin: a cost
        /// for changing your mind. The bill simply stops on the next operating day.
        ///
        /// The map is not touched. Releasing a site says the branch no longer runs it, not that
        /// the colony there stops existing — that is the player's business and RimWorld's.
        /// </summary>
        public CompanyActionResult ReleaseRemoteSite(string id)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record == null || record.id != id) { continue; }
                remoteSites.RemoveAt(index);
                RecordEvent("RR_Event_RemoteSiteReleased", id);
                return CompanyActionResult.Applied();
            }
            return CompanyActionResult.Refused("RR_Site_NotRegistered");
        }

        /// <summary>
        /// Whether the parent corporation will deliver a shipment to this map.
        ///
        /// **Arc 5 names "company-to-site logistics"**, and procurement had the headquarters
        /// written into it in seven places. The headquarters, or any site on the books that the
        /// branch can currently reach — and nowhere else, because a supplier will not unload into
        /// a place the branch has not accepted responsibility for.
        ///
        /// A Backrooms coordinate is excluded by construction: it can never be registered, so it
        /// can never be a delivery address. Which is correct — a supplier does not drive into a
        /// hole in the world.
        /// </summary>
        public bool CanReceiveDeliveryAt(Map map) { return IsBranchPlace(map); }

        /// <summary>
        /// Whether the branch **operates** here: whether it may build and run a facility on this
        /// map, which arc 5 calls the site's *"exit plan"* — a gate of its own.
        ///
        /// **A separate question from <see cref="CanReceiveDeliveryAt"/> that currently has the
        /// same answer.** Both delegate to one place-set so they cannot drift while they agree,
        /// and they are named apart because they are not the same thing: a site could one day be
        /// too remote for a supplier and still perfectly fine to build a gate on, and at that
        /// point one predicate would be wrong for one of them.
        /// </summary>
        public bool OperatesAt(Map map) { return IsBranchPlace(map); }

        /// <summary>
        /// The headquarters, or a site on the books the branch can currently reach.
        ///
        /// **A Backrooms coordinate is excluded by construction**, because it can never be
        /// registered — which is what keeps a designated gate out of a coordinate without a
        /// second check to forget. Invariant 12: what is down there is a natural gate, with no
        /// operator, no power and no address book, and it is not the company's doing.
        /// </summary>
        private bool IsBranchPlace(Map map)
        {
            if (map == null || !Find.Maps.Contains(map)) { return false; }
            if (headquarters == map) { return true; }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record != null && record.Live && record.site == map.Parent) { return true; }
            }
            return false;
        }

        /// <summary>
        /// Whether anybody the branch employs is actually standing at this place.
        ///
        /// **Arc 5: *"remote sites need people"*.** A site with nobody at it is a line on a
        /// ledger, and the consequence is that a shipment bound for it **waits** — a supplier
        /// does not unload into an empty field with nobody to sign for it.
        ///
        /// **Employed, alive, and present.** Not downed: somebody unconscious on the floor cannot
        /// take delivery of anything, and pretending otherwise would make the rule a formality.
        /// A prisoner or a slave is not staff and never counted.
        ///
        /// Checked live. A site is staffed when people are there and unstaffed the moment they
        /// leave, which is the honest reading of *"needs people"* and needs no assignment to
        /// maintain, no record to go stale and nothing for the player to remember to update.
        /// </summary>
        public bool IsSiteStaffed(Map map)
        {
            if (map == null) { return false; }
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn pawn = member.pawn;
                if (pawn == null || pawn.Dead || pawn.Destroyed || !pawn.Spawned) { continue; }
                if (pawn.Map != map || pawn.Downed) { continue; }
                if (pawn.IsPrisoner || pawn.IsSlave) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Whether a shipment may actually be unloaded here **now**.
        ///
        /// Distinct from <see cref="CanReceiveDeliveryAt"/> on purpose, and the split is the whole
        /// design of this piece:
        ///
        /// * **The address** is acceptable if the place is on the books. A player may order ahead
        ///   while the crew is still walking there, which is what anybody would actually do.
        /// * **The arrival** needs somebody present. The shipment waits, the cargo stays held and
        ///   the payment stays recorded — nothing is lost and the fix is obvious.
        ///
        /// Gating the order instead would have punished planning, and gating nothing would have
        /// made *"remote sites need people"* a sentence in a document.
        ///
        /// **The headquarters is never held to this.** A branch with nobody alive at home has a
        /// bigger problem, and the clean-up team already owns it.
        /// </summary>
        public bool CanUnloadAt(Map map)
        {
            if (!CanReceiveDeliveryAt(map)) { return false; }
            if (map == headquarters) { return true; }
            // **Logistics tier 3: RR_Cap_UnattendedDelivery.** Arc 5 established that a shipment
            // to an empty site waits, because a supplier does not unload into a field with nobody
            // to sign for it. This is the branch earning the right to be trusted with a drop: the
            // arrangement is on file, the site is on the books, and the crate is left.
            //
            // The rule it relaxes is kept everywhere else. A place that is NOT on the books still
            // refuses, above, and that is the clause that matters.
            if (HasCapability("RR_Cap_UnattendedDelivery")) { return true; }
            return IsSiteStaffed(map);
        }

        /// <summary>Somewhere a shipment may be sent, for a menu. Headquarters first.</summary>
        public List<Map> DeliveryDestinations()
        {
            List<Map> destinations = new List<Map>();
            if (headquarters != null && Find.Maps.Contains(headquarters)) { destinations.Add(headquarters); }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record == null || !record.Live || record.site.Map == null) { continue; }
                if (!destinations.Contains(record.site.Map)) { destinations.Add(record.site.Map); }
            }
            return destinations;
        }

        /// <summary>Whether this map is a registered site. The third clause of <c>OwnsMap</c>.</summary>
        internal bool IsRegisteredRemoteSite(Map map)
        {
            if (map == null || map.Parent == null) { return false; }
            for (int index = 0; index < remoteSites.Count; index++)
            {
                RemoteSiteRecord record = remoteSites[index];
                if (record != null && record.site == map.Parent) { return true; }
            }
            return false;
        }
    }
}
