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
        /// What each site adds to the daily overhead, as a share of the branch's base overhead.
        ///
        /// **A ratio and not a number, deliberately.** Async Industries runs on $25,000 a day of
        /// overhead and the Store on $1,500; one absolute surcharge would be a rounding error for
        /// one and ruinous for the other. A quarter of base overhead per site means the cost of
        /// holding a place is always proportionate to the operation holding it, and every start
        /// tunes it for free by tuning the number it already had.
        /// </summary>
        internal const int RemoteSiteOverheadDivisor = 4;

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
                long each = dailyOverheadUsd / RemoteSiteOverheadDivisor;
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
            if (remoteSites.Count >= MaximumRemoteSites)
            { return CompanyActionResult.Refused("RR_Site_TooMany"); }

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
